import csv
import io
import re
import sys
import urllib.request
from pathlib import Path

try:
    import redivis
    from fips_to_county import fips_to_county_state
    REDIVIS_AVAILABLE = True
except ImportError:
    REDIVIS_AVAILABLE = False

DATA_URL = "https://raw.githubusercontent.com/scpike/us-state-county-zip/refs/heads/master/geo-data.csv"


def load_zip_list(zip_file: Path) -> list[str]:
    content = zip_file.read_text(encoding="utf-8")
    # Split on any whitespace or commas
    return [z for z in re.split(r"[,\s]+", content) if z]


def fetch_zip_data(url: str = DATA_URL) -> dict[str, set[str]]:
    """Fetch ZIP to county mapping from GitHub source."""
    with urllib.request.urlopen(url, timeout=60) as resp:
        raw = resp.read().decode("utf-8", errors="ignore")
    reader = csv.DictReader(io.StringIO(raw))
    mapping: dict[str, set[str]] = {}
    for row in reader:
        zipcode = row["zipcode"].zfill(5)
        county = row["county"].strip()
        state = row["state_abbr"].strip()
        if not county or not state:
            continue
        mapping.setdefault(zipcode, set()).add(f"{county} County, {state}")
    return mapping


def fetch_redivis_data(zip_codes: list[str]) -> dict[str, set[str]]:
    """
    Fetch ZIP to county mapping from Stanford Redivis for specific ZIPs.
    Returns the most recent mapping for each ZIP code.

    Args:
        zip_codes: List of 5-digit ZIP codes as strings

    Returns:
        Dict mapping ZIP codes to sets of county names
    """
    if not REDIVIS_AVAILABLE:
        return {}

    try:
        # Convert ZIP codes to integers for the query
        zip_ints = ", ".join(zip_codes)

        # Query Redivis
        organization = redivis.organization("StanfordPHS")
        dataset = organization.dataset("us_zip_codes_to_county:b36a")

        query = f"""
            SELECT ZIP, COUNTY, RES_RATIO, VALID_END_DATE
            FROM `us_zip_codes_to_county:1ph7`
            WHERE ZIP IN ({zip_ints})
            ORDER BY ZIP, VALID_END_DATE DESC
        """

        df = dataset.query(query).to_pandas_dataframe()

        # Group by ZIP and get the most recent entry (or all if multiple counties)
        mapping: dict[str, set[str]] = {}
        for zip_code in zip_codes:
            zip_int = int(zip_code)
            zip_data = df[df['ZIP'] == zip_int]

            if zip_data.empty:
                continue

            # Get the most recent date
            most_recent = zip_data['VALID_END_DATE'].max()
            recent_data = zip_data[zip_data['VALID_END_DATE'] == most_recent]

            # Add all counties from the most recent period
            # (some ZIPs span multiple counties)
            counties = set()
            for _, row in recent_data.iterrows():
                county_name = fips_to_county_state(row['COUNTY'])
                # Only include if RES_RATIO > 0.5 (majority of addresses)
                if row['RES_RATIO'] >= 0.5:
                    counties.add(county_name)

            if counties:
                mapping[zip_code] = counties

        return mapping

    except Exception as e:
        print(f"Warning: Failed to fetch from Redivis: {e}", file=sys.stderr)
        return {}


def build_rows(zip_codes: list[str], mapping: dict[str, set[str]]):
    rows = [("zip", "county_and_state")]
    for z in zip_codes:
        counties = mapping.get(z)
        rows.append((z, "; ".join(sorted(counties)) if counties else "N/A"))
    return rows


def write_rows(rows: list[tuple[str, str]], output_path: Path | None):
    target = sys.stdout if output_path is None else output_path.open(
        "w", encoding="utf-8", newline=""
    )
    try:
        writer = csv.writer(target)
        writer.writerows(rows)
    finally:
        if target is not sys.stdout:
            target.close()


def main(args: list[str]):
    if not args:
        raise SystemExit("Usage: python zip_to_county.py <zip_file> [output_csv]")
    zip_file = Path(args[0])
    zips = load_zip_list(zip_file)

    # Fetch primary data source
    print("Fetching ZIP data from GitHub...", file=sys.stderr)
    mapping = fetch_zip_data()

    # Find missing ZIPs
    missing_zips = [z for z in zips if z not in mapping]

    # Try to fill missing ZIPs with Redivis if available
    if missing_zips and REDIVIS_AVAILABLE:
        print(
            f"Found {len(missing_zips)} missing ZIPs. Querying Redivis...",
            file=sys.stderr,
        )
        redivis_mapping = fetch_redivis_data(missing_zips)
        mapping.update(redivis_mapping)

        still_missing = [z for z in missing_zips if z not in mapping]
        filled = len(missing_zips) - len(still_missing)
        if filled > 0:
            print(f"Redivis filled {filled} missing ZIPs.", file=sys.stderr)
        if still_missing:
            print(
                f"Still missing {len(still_missing)} ZIPs: {', '.join(still_missing[:10])}{'...' if len(still_missing) > 10 else ''}",
                file=sys.stderr,
            )
    elif missing_zips:
        print(
            f"Found {len(missing_zips)} missing ZIPs (Redivis not available).",
            file=sys.stderr,
        )

    rows = build_rows(zips, mapping)
    output_path = Path(args[1]) if len(args) > 1 else None
    write_rows(rows, output_path)


if __name__ == "__main__":
    main(sys.argv[1:])
