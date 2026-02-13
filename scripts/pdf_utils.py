"""
Enhanced PDF extraction utilities for Kentucky election results.
Provides robust extraction with validation, logging, and multiple fallback strategies.
"""

import re
import logging
from typing import Dict, List, Optional, Tuple
from pathlib import Path
import pandas as pd

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


# Comprehensive party mappings
PARTY_MAPPINGS = {
    'REP': ['REP', 'REPUBLICAN', 'REPUBLICANS', '(R)', 'R-', 'GOP'],
    'DEM': ['DEM', 'DEMOCRAT', 'DEMOCRATIC', 'DEMOCRATS', '(D)', 'D-'],
    'LIB': ['LIB', 'LIBERTARIAN', 'LIBERTARIANS', '(L)', 'L-'],
    'IND': ['IND', 'INDEPENDENT', 'INDEPENDENTS', '(I)', 'I-', 'NON-PARTISAN', 'NONPARTISAN'],
    'GRN': ['GRN', 'GREEN', 'GREENS', '(G)', 'G-'],
    'CON': ['CON', 'CONSTITUTION', 'CONSTITUTIONALIST', '(C)'],
    'REF': ['REF', 'REFORM', '(RF)'],
    'AME': ['AME', 'AMERICAN', 'AMERICAN PARTY'],
    'WRI': ['WRITE-IN', 'WRITE IN', 'WRITEIN', 'WRI'],
}

# Office name standardization
OFFICE_MAPPINGS = {
    'President': ['PRESIDENT', 'PRES ', 'PRESIDENTIAL'],
    'U.S. Senate': ['U.S. SENATE', 'US SENATE', 'UNITED STATES SENATE', 'SENATOR'],
    'U.S. House': ['U.S. HOUSE', 'US HOUSE', 'UNITED STATES HOUSE', 'CONGRESS', 'CONGRESSIONAL'],
    'Governor': ['GOVERNOR', 'GOV '],
    'Lieutenant Governor': ['LIEUTENANT GOVERNOR', 'LT. GOVERNOR', 'LT GOVERNOR', 'LIEUT GOVERNOR'],
    'Attorney General': ['ATTORNEY GENERAL', 'ATT\'Y GENERAL', 'ATTY GENERAL'],
    'Secretary of State': ['SECRETARY OF STATE', 'SEC OF STATE', 'SEC. OF STATE'],
    'State Treasurer': ['TREASURER', 'STATE TREASURER'],
    'State Auditor': ['AUDITOR', 'STATE AUDITOR'],
    'Commissioner of Agriculture': ['AGRICULTURE', 'COMMISSIONER OF AGRICULTURE', 'COMM OF AGRICULTURE'],
    'State Senate': ['STATE SENATE', 'KENTUCKY SENATE', 'KY SENATE'],
    'State House': ['STATE HOUSE', 'STATE REPRESENTATIVE', 'KENTUCKY HOUSE', 'KY HOUSE', 'REPRESENTATIVE'],
}

# Election date mapping (first Tuesday after first Monday in November)
ELECTION_DATES = {
    '2010': '20101102', '2011': '20111108', '2012': '20121106', '2013': '20131105',
    '2014': '20141104', '2015': '20151103', '2016': '20161108', '2017': '20171107',
    '2018': '20181106', '2019': '20191105', '2020': '20201103', '2021': '20211102',
    '2022': '20221108', '2023': '20231107', '2024': '20241105', '2025': '20251104',
    '2026': '20261103', '2027': '20271102', '2028': '20281107',
}

# Common Kentucky counties for validation
KY_COUNTIES = {
    'ADAIR', 'ALLEN', 'ANDERSON', 'BALLARD', 'BARREN', 'BATH', 'BELL', 'BOONE',
    'BOURBON', 'BOYD', 'BOYLE', 'BRACKEN', 'BREATHITT', 'BRECKINRIDGE', 'BULLITT',
    'BUTLER', 'CALDWELL', 'CALLOWAY', 'CAMPBELL', 'CARLISLE', 'CARROLL', 'CARTER',
    'CASEY', 'CHRISTIAN', 'CLARK', 'CLAY', 'CLINTON', 'CRITTENDEN', 'CUMBERLAND',
    'DAVIESS', 'EDMONSON', 'ELLIOTT', 'ESTILL', 'FAYETTE', 'FLEMING', 'FLOYD',
    'FRANKLIN', 'FULTON', 'GALLATIN', 'GARRARD', 'GRANT', 'GRAVES', 'GRAYSON',
    'GREEN', 'GREENUP', 'HANCOCK', 'HARDIN', 'HARLAN', 'HARRISON', 'HART',
    'HENDERSON', 'HENRY', 'HICKMAN', 'HOPKINS', 'JACKSON', 'JEFFERSON', 'JESSAMINE',
    'JOHNSON', 'KENTON', 'KNOTT', 'KNOX', 'LARUE', 'LAUREL', 'LAWRENCE', 'LEE',
    'LESLIE', 'LETCHER', 'LEWIS', 'LINCOLN', 'LIVINGSTON', 'LOGAN', 'LYON',
    'MADISON', 'MAGOFFIN', 'MARION', 'MARSHALL', 'MARTIN', 'MASON', 'MCCRACKEN',
    'MCCREARY', 'MCLEAN', 'MEADE', 'MENIFEE', 'MERCER', 'METCALFE', 'MONROE',
    'MONTGOMERY', 'MORGAN', 'MUHLENBERG', 'NELSON', 'NICHOLAS', 'OHIO', 'OLDHAM',
    'OWEN', 'OWSLEY', 'PENDLETON', 'PERRY', 'PIKE', 'POWELL', 'PULASKI',
    'ROBERTSON', 'ROCKCASTLE', 'ROWAN', 'RUSSELL', 'SCOTT', 'SHELBY', 'SIMPSON',
    'SPENCER', 'TAYLOR', 'TODD', 'TRIGG', 'TRIMBLE', 'UNION', 'WARREN',
    'WASHINGTON', 'WAYNE', 'WEBSTER', 'WHITLEY', 'WOLFE', 'WOODFORD'
}


def extract_year(filename: str) -> Optional[str]:
    """Extract 4-digit year from filename."""
    match = re.search(r'(20\d{2})', filename)
    return match.group(1) if match else None


def extract_party(text: str, strict: bool = False) -> str:
    """
    Extract party code from text with comprehensive pattern matching.
    
    Args:
        text: Text containing party information
        strict: If True, only return party if high confidence
        
    Returns:
        Party code (REP, DEM, etc.) or empty string
    """
    if not text or pd.isna(text):
        return ''
    
    text_upper = str(text).upper().strip()
    
    # Check exact matches first (highest confidence)
    for party_code, patterns in PARTY_MAPPINGS.items():
        for pattern in patterns:
            if pattern in text_upper:
                return party_code
    
    # If in strict mode and no match, return empty
    if strict:
        return ''
    
    # Try to extract from parentheses
    paren_match = re.search(r'\(([^)]+)\)', text_upper)
    if paren_match:
        content = paren_match.group(1)
        # Check again with extracted content
        for party_code, patterns in PARTY_MAPPINGS.items():
            if any(p in content for p in patterns):
                return party_code
    
    return ''


def standardize_office(office_text: str) -> str:
    """
    Standardize office names to consistent format.
    
    Args:
        office_text: Raw office name from PDF
        
    Returns:
        Standardized office name
    """
    if not office_text or pd.isna(office_text):
        return ''
    
    text_upper = str(office_text).upper().strip()
    
    for standard_name, patterns in OFFICE_MAPPINGS.items():
        for pattern in patterns:
            if pattern in text_upper:
                return standard_name
    
    # Return original if no match found
    return office_text.strip()


def extract_district(text: str) -> str:
    """
    Extract district number from text.
    
    Args:
        text: Text containing district information
        
    Returns:
        District number as string or empty string
    """
    if not text or pd.isna(text):
        return ''
    
    text_str = str(text)
    
    # Pattern: "1st District", "District 12", etc.
    patterns = [
        r'(\d+)(?:st|nd|rd|th)\s+(?:Congressional|Senatorial|Representative|Judicial)?\s*District',
        r'District\s+(\d+)',
        r'Dist\.?\s+(\d+)',
        r'#\s*(\d+)',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text_str, re.IGNORECASE)
        if match:
            return match.group(1)
    
    return ''


def clean_candidate_name(name: str) -> Optional[str]:
    """
    Clean and validate candidate names.
    
    Args:
        name: Raw candidate name
        
    Returns:
        Cleaned name or None if invalid
    """
    if not name or pd.isna(name):
        return None
    
    name_str = str(name).strip()
    
    # Skip totals and empty values
    if name_str.lower() in ['nan', 'none', 'total', 'totals', 'votes', 'statewide', '', 'yes', 'no']:
        return None
    
    # Skip if it's just numbers
    if re.match(r'^\d+$', name_str):
        return None
    
    # Skip if too short (but allow initials)
    if len(name_str) < 2:
        return None
    
    # Remove extra whitespace
    name_str = ' '.join(name_str.split())
    
    # Remove party affiliation in parentheses if present
    name_str = re.sub(r'\s*\([^)]*\)\s*$', '', name_str)
    
    # Remove trailing party indicators like " - R" or " REP"
    name_str = re.sub(r'\s*[-–]\s*(REP|DEM|LIB|IND|GRN|CON|R|D|L|I|G|C)$', '', name_str, flags=re.IGNORECASE)
    
    return name_str.strip() or None


def clean_county_name(county: str) -> Optional[str]:
    """
    Clean and validate county names.
    
    Args:
        county: Raw county name
        
    Returns:
        Cleaned county name or None if invalid
    """
    if not county or pd.isna(county):
        return None
    
    county_str = str(county).strip().upper()
    
    # Skip totals and other non-county entries
    skip_words = ['TOTAL', 'TOTALS', 'STATEWIDE', 'STATE TOTAL', 'GRAND TOTAL', 
                  'VOTES', 'YES', 'NO', 'SUMMARY', '']
    if county_str in skip_words:
        return None
    
    # Remove "County" suffix if present
    county_str = re.sub(r'\s+COUNTY$', '', county_str, flags=re.IGNORECASE)
    
    # Title case for output
    county_str = county_str.title()
    
    # Validate against known Kentucky counties
    if county_str.upper() not in KY_COUNTIES:
        logger.warning(f"Unrecognized county name: {county_str}")
    
    return county_str


def clean_votes(votes_value) -> int:
    """
    Convert votes to integer with robust error handling.
    
    Args:
        votes_value: Raw votes value (may be string, int, float, or None)
        
    Returns:
        Integer vote count
    """
    if votes_value is None or pd.isna(votes_value):
        return 0
    
    try:
        # Handle string values
        if isinstance(votes_value, str):
            # Remove commas, spaces, and other non-numeric characters
            cleaned = re.sub(r'[^\d.-]', '', votes_value)
            if not cleaned or cleaned == '-':
                return 0
            return int(float(cleaned))
        
        # Handle numeric values
        return int(float(votes_value))
    
    except (ValueError, TypeError):
        logger.debug(f"Could not convert votes value: {votes_value}")
        return 0


def validate_extraction_result(df: pd.DataFrame) -> Tuple[bool, List[str]]:
    """
    Validate extracted data for quality and completeness.
    
    Args:
        df: DataFrame with extracted election results
        
    Returns:
        Tuple of (is_valid, list_of_warnings)
    """
    warnings = []
    
    if df.empty:
        return False, ["No data extracted"]
    
    # Check for required columns
    required_cols = ['county', 'candidate', 'votes']
    missing_cols = [col for col in required_cols if col not in df.columns]
    if missing_cols:
        warnings.append(f"Missing required columns: {missing_cols}")
        return False, warnings
    
    # Check for minimum data
    if len(df) < 10:
        warnings.append(f"Very few rows extracted ({len(df)}). This may indicate incomplete extraction.")
    
    # Check county coverage (should have multiple counties)
    unique_counties = df['county'].dropna().nunique()
    if unique_counties < 10:
        warnings.append(f"Only {unique_counties} counties found. Kentucky has 120 counties.")
    
    # Check for candidates
    unique_candidates = df['candidate'].dropna().nunique()
    if unique_candidates < 2:
        warnings.append(f"Only {unique_candidates} candidate(s) found. Expected at least 2.")
    
    # Check for votes
    total_votes = df['votes'].sum()
    if total_votes == 0:
        warnings.append("Total votes sum to zero")
        return False, warnings
    
    # Check for party information
    if 'party' in df.columns:
        missing_party = df['party'].isna() | (df['party'] == '')
        if missing_party.sum() > len(df) * 0.5:
            warnings.append(f"{missing_party.sum()}/{len(df)} rows missing party information")
    
    # Check for suspicious patterns
    zero_votes = (df['votes'] == 0).sum()
    if zero_votes > len(df) * 0.3:
        warnings.append(f"{zero_votes}/{len(df)} rows have zero votes")
    
    # All checks passed (with possible warnings)
    is_valid = len([w for w in warnings if 'Missing' in w or 'zero' in w]) == 0
    
    return is_valid, warnings


def merge_duplicate_results(df: pd.DataFrame) -> pd.DataFrame:
    """
    Merge duplicate entries by summing votes.
    
    Args:
        df: DataFrame possibly containing duplicates
        
    Returns:
        DataFrame with duplicates merged
    """
    if df.empty:
        return df
    
    # Define grouping columns
    group_cols = ['county', 'office', 'district', 'candidate', 'party']
    
    # Only use columns that exist
    group_cols = [col for col in group_cols if col in df.columns]
    
    if not group_cols:
        return df
    
    # Convert votes to numeric
    df['votes'] = pd.to_numeric(df['votes'], errors='coerce').fillna(0).astype(int)
    
    # Group and sum votes
    result = df.groupby(group_cols, dropna=False, as_index=False).agg({'votes': 'sum'})
    
    # Add back any columns that weren't in group_cols
    for col in df.columns:
        if col not in result.columns and col != 'votes':
            result[col] = ''
    
    logger.info(f"Merged {len(df)} rows into {len(result)} rows")
    
    return result


def format_openelections_standard(df: pd.DataFrame, level: str = 'county') -> pd.DataFrame:
    """
    Format DataFrame to OpenElections standard format.
    
    Args:
        df: DataFrame with election results
        level: 'county' or 'precinct'
        
    Returns:
        Formatted DataFrame
    """
    if df.empty:
        return df
    
    # Define column order for county-level
    columns = [
        'county', 'office', 'district', 'candidate', 'party', 'votes',
        'election_day', 'absentee', 'av_counting_boards', 'early_voting',
        'mail', 'provisional', 'pre_process_absentee'
    ]
    
    # Add precinct column if needed
    if level == 'precinct':
        columns.insert(1, 'precinct')
    
    # Ensure all columns exist
    for col in columns:
        if col not in df.columns:
            df[col] = ''
    
    # Ensure votes is numeric
    df['votes'] = pd.to_numeric(df['votes'], errors='coerce').fillna(0).astype(int)
    
    # Select and reorder columns
    result = df[columns].copy()
    
    return result


def get_election_date(year: str) -> str:
    """Get election date in YYYYMMDD format."""
    return ELECTION_DATES.get(year, f"{year}1106")
