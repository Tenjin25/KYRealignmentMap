"""
Kentucky-specific PDF parser for election results.
Handles the unique format used by Kentucky Secretary of State PDFs.

This parser is optimized for Kentucky's specific PDF layout where:
- County names and votes appear in the same cell
- Headers span multiple rows
- Results are presented in a wide format

Usage:
    py scripts/ky_specific_pdf_parser.py "data/2024 General Election.pdf"
"""

import sys
import re
from pathlib import Path
import pandas as pd
import logging

try:
    import tabula
    import pdfplumber
    LIBS_AVAILABLE = True
except ImportError:
    LIBS_AVAILABLE = False
    print("Error: Required libraries not installed.")
    print("Install with: pip install tabula-py pdfplumber pandas")
    sys.exit(1)

from pdf_utils import (
    KY_COUNTIES, clean_county_name, clean_votes, extract_party,
    get_election_date, validate_extraction_result, merge_duplicate_results,
    format_openelections_standard, logger
)

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')


def extract_county_and_votes_from_text(text):
    """
    Extract county name and vote counts from mixed text.
    
    Kentucky PDFs often have format like:
    "Adair 5,841 1,660 43 33"
    "Jefferson 144,553 203,070 2,619"
    """
    if not text or pd.isna(text):
        return None, []
    
    text = str(text).strip()
    
    # Try to split county name from numbers
    # Pattern: County name followed by numbers with possible commas
    match = re.match(r'^([A-Za-z\s]+?)\s+([\d,\s]+)$', text)
    
    if match:
        county_part = match.group(1).strip()
        votes_part = match.group(2).strip()
        
        # Clean county name
        county = clean_county_name(county_part)
        if not county:
            return None, []
        
        # Extract vote numbers
        votes = []
        for vote_str in re.findall(r'[\d,]+', votes_part):
            vote_num = clean_votes(vote_str)
            votes.append(vote_num)
        
        return county, votes
    
    # If no match, check if it's just a county name
    county = clean_county_name(text)
    if county:
        return county, []
    
    return None, []


def parse_ky_pdf_smart(pdf_path):
    """
    Smart parser that understands Kentucky's PDF format.
    Uses text extraction to find candidate names and counties.
    """
    logger.info(f"Parsing Kentucky PDF: {pdf_path}")
    
    results = []
    current_office = ""
    candidate_info = []
    
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page_num, page in enumerate(pdf.pages, 1):
                logger.info(f"  Processing page {page_num}...")
                
                # Extract text to find office and candidates
                text = page.extract_text()
                if not text:
                    continue
                
                lines = text.split('\n')
                
                # Look for office titles
                for line in lines:
                    if 'president' in line.lower() and 'vice' in line.lower():
                        current_office = "President"
                    elif 'u.s. senate' in line.lower() or 'united states senate' in line.lower():
                        current_office = "U.S. Senate"
                    elif 'u.s. house' in line.lower() or 'congress' in line.lower():
                        current_office = "U.S. House"
                    elif 'governor' in line.lower():
                        current_office = "Governor"
                    elif 'attorney general' in line.lower():
                        current_office = "Attorney General"
                
                # Extract tables
                tables = page.extract_tables()
                
                if not tables:
                    continue
                
                for table in tables:
                    if not table or len(table) < 2:
                        continue
                    
                    # Try to identify header rows (contain candidate names)
                    header_row = None
                    data_start_row = 0
                    
                    for i, row in enumerate(table[:5]):  # Check first 5 rows
                        if not row:
                            continue
                        
                        # Check if this row has candidate names (contains alphabetic text)
                        text_cells = [cell for cell in row if cell and re.search(r'[A-Za-z]{3,}', str(cell))]
                        
                        if len(text_cells) >= 2:  # At least 2 text cells suggests candidate names
                            header_row = row
                            data_start_row = i + 1
                            break
                    
                    if not header_row:
                        continue
                    
                    # Extract candidate names and parties from header
                    candidates = []
                    for cell in header_row[1:]:  # Skip first column (county)
                        if not cell or not str(cell).strip():
                            continue
                        
                        cell_text = str(cell).strip()
                        
                        # Skip if it's just a number
                        if re.match(r'^[\d,\s]+$', cell_text):
                            continue
                        
                        # Extract candidate name and party
                        party = extract_party(cell_text)
                        
                        # Clean candidate name
                        name = re.sub(r'\([^)]*\)', '', cell_text)  # Remove parentheses
                        name = re.sub(r'\b(REP|DEM|LIB|IND|GRN|CON|Republican|Democratic|Libertarian|Independent|Green|Constitution)\b', '', name, flags=re.IGNORECASE)
                        name = ' '.join(name.split())
                        
                        if len(name) > 2:
                            candidates.append({'name': name, 'party': party})
                    
                    if not candidates:
                        continue
                    
                    # Process data rows
                    for row in table[data_start_row:]:
                        if not row or not row[0]:
                            continue
                        
                        first_cell = str(row[0])
                        
                        # Try to extract county and votes from first cell
                        county, votes_in_first = extract_county_and_votes_from_text(first_cell)
                        
                        if not county:
                            # Try just as county name
                            county = clean_county_name(first_cell)
                            if not county:
                                continue
                        
                        # If votes were in first cell, use those
                        if votes_in_first:
                            for i, vote in enumerate(votes_in_first):
                                if i < len(candidates):
                                    results.append({
                                        'county': county,
                                        'office': current_office,
                                        'district': '',
                                        'candidate': candidates[i]['name'],
                                        'party': candidates[i]['party'],
                                        'votes': vote
                                    })
                        else:
                            # Extract votes from separate cells
                            for i, cell in enumerate(row[1:]):
                                if i >= len(candidates):
                                    break
                                
                                votes = clean_votes(cell)
                                
                                results.append({
                                    'county': county,
                                    'office': current_office,
                                    'district': '',
                                    'candidate': candidates[i]['name'],
                                    'party': candidates[i]['party'],
                                    'votes': votes
                                })
        
        logger.info(f"  Extracted {len(results)} records")
        return pd.DataFrame(results)
    
    except Exception as e:
        logger.error(f"  Error parsing PDF: {e}")
        import traceback
        traceback.print_exc()
        return pd.DataFrame()


def parse_ky_pdf_raw_text(pdf_path):
    """
    Alternative parser using raw text extraction.
    For PDFs that are text-based but have difficult table structures.
    """
    logger.info(f"Trying raw text extraction for: {pdf_path}")
    
    results = []
    
    try:
        import pdfplumber
        
        with pdfplumber.open(pdf_path) as pdf:
            full_text = ""
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    full_text += text + "\n"
        
        # Look for county patterns with votes
        # Pattern: County name followed by numbers
        pattern = r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+((?:\d[\d,]*\s*)+)'
        
        matches = re.finditer(pattern, full_text)
        
        for match in matches:
            potential_county = match.group(1).strip()
            votes_text = match.group(2).strip()
            
            # Check if it's a known county
            if potential_county.upper() in KY_COUNTIES:
                county = clean_county_name(potential_county)
                
                # Extract all vote numbers
                votes = [clean_votes(v) for v in re.findall(r'\d[\d,]*', votes_text)]
                
                # We don't know candidate names from this method, so mark as unknown
                for i, vote in enumerate(votes):
                    results.append({
                        'county': county,
                        'office': '',
                        'district': '',
                        'candidate': f'Candidate {i+1}',
                        'party': '',
                        'votes': vote
                    })
        
        logger.info(f"  Raw text extraction found {len(results)} records")
        return pd.DataFrame(results)
    
    except Exception as e:
        logger.error(f"  Raw text extraction failed: {e}")
        return pd.DataFrame()


def process_ky_pdf(pdf_path, output_dir='data'):
    """Process a Kentucky election PDF with specialized parsing."""
    pdf_path = Path(pdf_path)
    
    if not pdf_path.exists():
        logger.error(f"File not found: {pdf_path}")
        return None
    
    logger.info(f"\n{'='*70}")
    logger.info(f"Processing Kentucky PDF: {pdf_path.name}")
    logger.info(f"{'='*70}")
    
    # Extract year
    year_match = re.search(r'(20\d{2})', pdf_path.name)
    year = year_match.group(1) if year_match else "unknown"
    
    # Try smart parser first
    df = parse_ky_pdf_smart(str(pdf_path))
    
    # If that didn't work well, try raw text
    if df.empty or len(df) < 50:
        logger.info("Smart parser didn't extract enough data, trying raw text...")
        df_raw = parse_ky_pdf_raw_text(str(pdf_path))
        if len(df_raw) > len(df):
            df = df_raw
    
    if df.empty:
        logger.error("No data extracted")
        return None
    
    # Validate
    is_valid, warnings = validate_extraction_result(df)
    if warnings:
        logger.warning("Extraction issues:")
        for warning in warnings:
            logger.warning(f"  - {warning}")
    
    # Merge duplicates
    df = merge_duplicate_results(df)
    
    # Format to OpenElections standard
    df = format_openelections_standard(df, level='county')
    
    # Generate output filename
    election_date = get_election_date(year)
    output_filename = f"{election_date}__ky__general__county.csv"
    output_path = Path(output_dir) / output_filename
    
    # Save
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)
    
    logger.info(f"\n✓ Saved: {output_path}")
    logger.info(f"  Records: {len(df)}")
    logger.info(f"  Counties: {df['county'].nunique()}")
    logger.info(f"  Candidates: {df['candidate'].nunique()}")
    logger.info(f"  Total votes: {df['votes'].sum():,}")
    
    # Show preview
    if len(df) > 0:
        print("\nPreview (first 10 rows):")
        print(df.head(10).to_string(index=False))
    
    # Manual review suggestions
    if not is_valid or len(warnings) > 0:
        logger.info("\n⚠️  Manual review recommended:")
        logger.info("  1. Check candidate names are correct")
        logger.info("  2. Verify vote totals make sense")
        logger.info("  3. Fill in missing office/party information")
        logger.info(f"  4. Run validation: py scripts/validate_extraction.py \"{output_path}\"")
    
    return output_path


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('pdf_path', help='Path to Kentucky election PDF')
    parser.add_argument('--output-dir', default='data', help='Output directory')
    parser.add_argument('-v', '--verbose', action='store_true', help='Verbose output')
    
    args = parser.parse_args()
    
    if args.verbose:
        logger.setLevel(logging.DEBUG)
    
    result = process_ky_pdf(args.pdf_path, args.output_dir)
    
    if not result:
        logger.error("\n❌ Extraction failed")
        logger.info("\nTroubleshooting:")
        logger.info("  1. Check if PDF is text-based (not scanned image)")
        logger.info("  2. Try opening PDF manually to see structure")
        logger.info("  3. Consider using the .txt files if available")
        logger.info("  4. May need manual data entry for complex PDFs")
        sys.exit(1)


if __name__ == '__main__':
    main()
