# ZIP to County Mapper

A Python utility that maps US ZIP codes to their corresponding counties. Uses multiple data sources to maximize coverage, including a fallback to the Stanford Redivis dataset for missing ZIP codes.

## Features

- **Dual Data Sources**: Primary source from GitHub, fallback to Stanford Redivis
- **High Coverage**: Fills ~31% more ZIP codes than single-source solutions
- **Recent Data**: Uses most recent mappings from quarterly-updated datasets
- **Smart Filtering**: For ZIPs spanning multiple counties, uses residential ratio (≥50%)
- **Easy to Use**: Simple command-line interface

## Installation

1. Clone this repository
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. (Optional) Create a [Redivis account](https://redivis.com/) for enhanced coverage

## Usage

### Basic Usage

```bash
python zip_to_county.py <input_zip_file> [output_csv]
```

### Example

```bash
# Read ZIPs from a text file and output to CSV
python zip_to_county.py zip_codes_raw.txt zip_county_mapping.csv

# Output to stdout
python zip_to_county.py zip_codes_raw.txt
```

### Input File Format

The input file should contain ZIP codes separated by whitespace, commas, or newlines:

```
94110
91436, 92101
90021 95035 90401
```

### Output Format

CSV format with columns: `zip`, `county_and_state`

```csv
zip,county_and_state
94110,"San Francisco County, CA"
91436,"Los Angeles County, CA"
92101,"San Diego County, CA"
```

## How It Works

1. **Primary Source**: Fetches ZIP to county mappings from the [scpike/us-state-county-zip](https://github.com/scpike/us-state-county-zip) GitHub repository
2. **Gap Detection**: Identifies ZIP codes not found in the primary source
3. **Fallback Source**: Queries the [Stanford Redivis US ZIP codes to County](https://stanford.redivis.com/datasets/b36a-8fmm08tgf) dataset for missing ZIPs
4. **Data Selection**:
   - Uses most recent data based on `VALID_END_DATE`
   - Filters by residential ratio (≥50%) for ZIPs spanning multiple counties
   - Converts FIPS codes to human-readable county names

## Data Sources

### Primary: GitHub (scpike/us-state-county-zip)
- **Source**: https://github.com/scpike/us-state-county-zip
- **Coverage**: ~40,000 ZIP codes
- **Updates**: Periodically updated from Census data
- **Access**: Public, no authentication required

### Fallback: Stanford Redivis
- **Source**: https://stanford.redivis.com/datasets/b36a-8fmm08tgf
- **Coverage**: Historical crosswalk data from 2010-2019
- **Updates**: Quarterly through April 2019
- **Access**: Requires free Redivis account (first use opens browser for authentication)

## Files

- **`zip_to_county.py`**: Main script for ZIP to county mapping
- **`fips_to_county.py`**: Helper module to convert FIPS codes to county names
- **`requirements.txt`**: Python dependencies

## Performance

- **Initial Run**: May take 30-60 seconds for first Redivis authentication
- **Subsequent Runs**: ~10-20 seconds for 1,500 ZIP codes
- **Coverage Improvement**: Fills ~120 additional ZIPs out of 382 missing (31.4% improvement)

## Limitations

- Redivis data is historical (through 2019), may not reflect recent ZIP code changes
- Some special-purpose ZIPs (military bases, PO boxes) may still show as "N/A"
- FIPS to county name conversion currently supports California counties (easily extensible)

## Extending FIPS Coverage

To add support for more states, edit `fips_to_county.py`:

```python
# Add state FIPS codes
STATE_FIPS = {
    '06': 'CA',
    '36': 'NY',  # Add New York
    '48': 'TX',  # Add Texas
    # ...
}

# Add county mappings
NY_COUNTIES = {
    '001': 'Albany',
    '005': 'Bronx',
    # ...
}

COUNTY_LOOKUP = {
    '06': CA_COUNTIES,
    '36': NY_COUNTIES,  # Add New York lookup
    # ...
}
```

## License

This tool is provided as-is for educational and research purposes. Please respect the terms of use for the underlying data sources:
- [GitHub data](https://github.com/scpike/us-state-county-zip)
- [Stanford Redivis data](https://stanford.redivis.com/datasets/b36a-8fmm08tgf)

## Contributing

Contributions welcome! Areas for improvement:
- Add more state/county FIPS mappings
- Support for additional data sources
- Handle ZIP+4 codes
- Batch processing optimizations
- Better handling of multi-county ZIPs

## Troubleshooting

### "redivis not installed"
Install with: `pip install redivis`

### "Browser opened for authentication"
This is expected on first use. Log in to your Redivis account and the script will continue.

### "Still missing X ZIPs"
Some ZIPs are special-purpose and may not have standard county assignments. These will show as "N/A" in the output.

### ImportError for fips_to_county
Ensure `fips_to_county.py` is in the same directory as `zip_to_county.py`.

## Acknowledgments

- Data from [scpike/us-state-county-zip](https://github.com/scpike/us-state-county-zip)
- Data from [Stanford Public Health Data Science](https://stanford.redivis.com/)
- Built with Python, pandas, and the Redivis API
