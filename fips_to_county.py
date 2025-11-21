#!/usr/bin/env python3
"""
Helper module to convert FIPS county codes to county names.
FIPS codes are 5-digit codes where first 2 digits are state, last 3 are county.
"""

# State FIPS codes
STATE_FIPS = {
    '06': 'CA',
    '36': 'NY',
    '48': 'TX',
    # Add more as needed
}

# County FIPS lookup (state_fips -> {county_fips -> county_name})
# California counties
CA_COUNTIES = {
    '001': 'Alameda',
    '013': 'Contra Costa',
    '019': 'Fresno',
    '029': 'Kern',
    '037': 'Los Angeles',
    '041': 'Marin',
    '053': 'Monterey',
    '055': 'Napa',
    '059': 'Orange',
    '061': 'Placer',
    '065': 'Riverside',
    '067': 'Sacramento',
    '071': 'San Bernardino',
    '073': 'San Diego',
    '075': 'San Francisco',
    '077': 'San Joaquin',
    '079': 'San Luis Obispo',
    '081': 'San Mateo',
    '083': 'Santa Barbara',
    '085': 'Santa Clara',
    '087': 'Santa Cruz',
    '095': 'Solano',
    '097': 'Sonoma',
    '099': 'Stanislaus',
    '107': 'Tulare',
    '111': 'Ventura',
    '113': 'Yolo',
}

COUNTY_LOOKUP = {
    '06': CA_COUNTIES,
}


def fips_to_county_state(fips_code: str | int) -> str:
    """
    Convert a 5-digit FIPS code to 'County Name, ST' format.

    Args:
        fips_code: 5-digit FIPS code (e.g., '06037' or 6037)

    Returns:
        County and state string (e.g., 'Los Angeles County, CA')
        or 'Unknown County (FIPS: xxxxx)' if not found
    """
    fips_str = str(fips_code).zfill(5)
    state_fips = fips_str[:2]
    county_fips = fips_str[2:]

    state_abbr = STATE_FIPS.get(state_fips)
    if not state_abbr:
        return f'Unknown County (FIPS: {fips_str})'

    counties = COUNTY_LOOKUP.get(state_fips, {})
    county_name = counties.get(county_fips)

    if not county_name:
        return f'Unknown County (FIPS: {fips_str})'

    return f'{county_name} County, {state_abbr}'


if __name__ == '__main__':
    # Test with some examples
    test_codes = [6037, 6071, 6085, 6095, 6107, 6111]
    for code in test_codes:
        print(f'{code} -> {fips_to_county_state(code)}')
