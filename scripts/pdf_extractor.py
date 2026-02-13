"""
Simple PDF extractor for Kentucky election results.
Converts PDFs to OpenElections CSV format with improved robustness.

Usage:
    py scripts/pdf_extractor.py "data/2020 General Election Results.pdf"
    py scripts/pdf_extractor.py --all  # Process all PDFs
    py scripts/pdf_extractor.py -v <file>  # Verbose mode
"""

import sys
import os
from pathlib import Path
import re
import logging

try:
    import tabula
    import pandas as pd
    TABULA_AVAILABLE = True
except ImportError:
    TABULA_AVAILABLE = False
    print("Error: tabula-py required. Install with: pip install tabula-py pandas")
    sys.exit(1)

# Try to import utilities from pdf_utils
try:
    from pdf_utils import (
        clean_candidate_name, clean_county_name, clean_votes,
        extract_party, get_election_date, validate_extraction_result,
        merge_duplicate_results
    )
    UTILS_AVAILABLE = True
except ImportError:
    UTILS_AVAILABLE = False
    print("Warning: pdf_utils not available. Using basic functions.")

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


def extract_year(filename):
    """Extract year from filename."""
    match = re.search(r'(20\d{2})', filename)
    return match.group(1) if match else None


# Define basic functions if utilities not available
if not UTILS_AVAILABLE:
    def clean_candidate_name(name):
        """Clean up candidate names."""
        if not name or str(name).lower() in ['nan', 'none', 'total', 'votes', 'statewide']:
            return None
        name = str(name).strip()
        name = ' '.join(name.split())
        if name.isdigit() or len(name) < 2:
            return None
        return name

    def clean_county_name(county):
        """Clean county names."""
        if not county or str(county).lower() in ['nan', 'none', 'total', 'statewide', 'totals']:
            return None
        return str(county).strip().title()

    def clean_votes(votes):
        """Convert votes to integer."""
        try:
            if pd.isna(votes):
                return 0
            return int(float(str(votes).replace(',', '').strip()))
        except:
            return 0

    def extract_party(text):
        """Extract party from text."""
        party_patterns = {
            'REP': ['REP', 'Republican', '(R)', 'GOP'],
            'DEM': ['DEM', 'Democratic', 'Democrat', '(D)'],
            'LIB': ['LIB', 'Libertarian', '(L)'],
            'IND': ['IND', 'Independent', '(I)'],
            'GRN': ['GRN', 'Green', '(G)'],
            'CON': ['CON', 'Constitution'],
        }
        
        text_upper = str(text).upper()
        for party_code, patterns in party_patterns.items():
            for pattern in patterns:
                if pattern.upper() in text_upper:
                    return party_code
        return ''

    def get_election_date(year):
        """Get election date."""
        dates = {
            '2010': '20101102', '2011': '20111108', '2012': '20121106',
            '2014': '20141104', '2015': '20151103', '2016': '20161108',
            '2019': '20191105', '2020': '20201103', '2022': '20221108',
            '2023': '20231107', '2024': '20241105', '2025': '20251104'
        }
        return dates.get(year, f"{year}1106")

    def validate_extraction_result(df):
        """Basic validation."""
        if df.empty:
            return False, ["No data extracted"]
        warnings = []
        if len(df) < 10:
            warnings.append(f"Few rows: {len(df)}")
        return len(df) > 0, warnings

    def merge_duplicate_results(df):
        """Basic deduplication."""
        if df.empty:
            return df
        group_cols = [c for c in ['county', 'candidate', 'party'] if c in df.columns]
        if group_cols:
            return df.groupby(group_cols, dropna=False, as_index=False).agg({'votes': 'sum'})
        return df


def parse_pdf_simple(pdf_path):
    """
    Parse PDF using tabula with multiple fallback strategies.
    """
    logger.info(f"Extracting tables from: {pdf_path}")
    
    year = extract_year(os.path.basename(pdf_path))
    results = []
    
    try:
        # Try different extraction strategies
        strategies = [
            ('Lattice', {'lattice': True, 'pages': 'all', 'multiple_tables': True}),
            ('Stream', {'stream': True, 'pages': 'all', 'multiple_tables': True, 'guess': False}),
            ('Auto', {'pages': 'all', 'multiple_tables': True, 'guess': True}),
        ]
        
        tables = None
        successful_strategy = None
        
        for strategy_name, strategy_params in strategies:
            try:
                logger.info(f"  Trying {strategy_name} strategy...")
                tables = tabula.read_pdf(pdf_path, **strategy_params)
                if tables and len(tables) > 0 and not tables[0].empty:
                    logger.info(f"  ✓ {strategy_name} found {len(tables)} tables")
                    successful_strategy = strategy_name
                    break
            except Exception as e:
                logger.debug(f"  {strategy_name} strategy failed: {e}")
                continue
        
        if not tables:
            logger.error("  ✗ No tables extracted by any strategy")
            return []
        
        # Process each table
        for table_idx, df in enumerate(tables):
            if df is None or df.empty:
                continue
            
            logger.info(f"  Processing table {table_idx + 1}: {df.shape[0]} rows × {df.shape[1]} cols")
            
            # Assume first column is county, rest are candidates
            counties_col = df.columns[0]
            
            for col in df.columns[1:]:
                candidate_name = clean_candidate_name(col)
                if not candidate_name:
                    continue
                
                party = extract_party(col)
                
                # Extract votes for each county
                for idx, row in df.iterrows():
                    county = clean_county_name(row[counties_col])
                    if not county:
                        continue
                    
                    votes = clean_votes(row[col])
                    
                    results.append({
                        'county': county,
                        'office': '',
                        'district': '',
                        'candidate': candidate_name,
                        'party': party,
                        'votes': votes,
                        'election_day': '',
                        'absentee': '',
                        'av_counting_boards': '',
                        'early_voting': '',
                        'mail': '',
                        'provisional': '',
                        'pre_process_absentee': ''
                    })
        
        logger.info(f"  Extracted {len(results)} data rows")
        
        # Validate extraction
        if results:
            df_validate = pd.DataFrame(results)
            is_valid, warnings = validate_extraction_result(df_validate)
            if warnings:
                logger.warning("  Extraction warnings:")
                for warning in warnings:
                    logger.warning(f"    - {warning}")
        
    except Exception as e:
        logger.error(f"  ✗ Error: {e}")
        if logger.level == logging.DEBUG:
            import traceback
            traceback.print_exc()
    
    return results


def save_to_openelections(results, year, output_dir='data'):
    """Save results to OpenElections format CSV."""
    if not results:
        logger.warning("No data to save")
        return None
    
    df = pd.DataFrame(results)
    
    # Merge duplicates
    df = merge_duplicate_results(df)
    
    # Get proper election date
    election_date = get_election_date(year)
    output_filename = f"{election_date}__ky__general__county.csv"
    output_path = Path(output_dir) / output_filename
    
    # Ensure columns are in correct order
    column_order = [
        'county', 'office', 'district', 'candidate', 'party', 'votes',
        'election_day', 'absentee', 'av_counting_boards', 'early_voting',
        'mail', 'provisional', 'pre_process_absentee'
    ]
    
    df = df[column_order]
    
    # Save to CSV
    df.to_csv(output_path, index=False)
    
    logger.info(f"\n✓ Saved: {output_path}")
    logger.info(f"  Records: {len(df)}")
    if 'county' in df.columns:
        logger.info(f"  Counties: {df['county'].nunique()}")
    if 'candidate' in df.columns:
        logger.info(f"  Candidates: {df['candidate'].nunique()}")
    logger.info(f"  Total votes: {df['votes'].sum():,}")
    
    # Show preview
    print("\nPreview (first 10 rows):")
    print(df.head(10).to_string(index=False))
    
    return output_path


def main():
    """Main function."""
    import argparse
    
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('pdf_path', nargs='?', help='Path to PDF file to process')
    parser.add_argument('--all', action='store_true', help='Process all PDFs in data/ directory')
    parser.add_argument('-v', '--verbose', action='store_true', help='Enable verbose output')
    args = parser.parse_args()
    
    if args.verbose:
        logger.setLevel(logging.DEBUG)
    
    data_dir = Path('data')
    
    # Get PDF files to process
    if args.all:
        pdf_files = list(data_dir.glob('*.pdf'))
    elif args.pdf_path:
        pdf_files = [Path(args.pdf_path)]
    else:
        # Default: process all PDFs
        pdf_files = list(data_dir.glob('*.pdf'))
    
    if not pdf_files:
        logger.error("No PDF files found")
        return
    
    logger.info(f"Found {len(pdf_files)} PDF file(s)\n")
    logger.info("=" * 70)
    
    success_count = 0
    for pdf_path in pdf_files:
        logger.info(f"\n{pdf_path.name}")
        logger.info("-" * 70)
        
        year = extract_year(pdf_path.name)
        if not year:
            logger.warning(f"  Could not extract year from filename: {pdf_path.name}")
            year = "unknown"
        
        # Extract data
        results = parse_pdf_simple(str(pdf_path))
        
        if results:
            # Save to CSV
            output_path = save_to_openelections(results, year)
            if output_path:
                success_count += 1
        else:
            logger.error(f"  ✗ No data extracted from {pdf_path.name}")
    
    logger.info("\n" + "=" * 70)
    logger.info(f"Completed: {success_count}/{len(pdf_files)} files processed successfully")
    logger.info("=" * 70)
    
    if success_count < len(pdf_files):
        logger.info("\nTip: For better extraction, try using scripts/robust_pdf_extractor.py")


if __name__ == '__main__':
    main()
