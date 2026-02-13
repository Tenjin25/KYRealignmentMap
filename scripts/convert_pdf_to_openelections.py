"""
Convert Kentucky election PDF files to OpenElections CSV format.

This script uses tabula to extract tables from PDF files and converts them
to the OpenElections format.

Usage:
    py scripts/convert_pdf_to_openelections.py <pdf_file> <election_date> [level]
    
Example:
    py scripts/convert_pdf_to_openelections.py "data/2012genresults.pdf" 20121106 county
"""

import sys
import os
from pathlib import Path

# Add tools directory to path to import pdf_to_csv
sys.path.insert(0, str(Path(__file__).parent.parent / 'tools'))

try:
    import tabula
    import pandas as pd
except ImportError:
    print("Error: Required libraries not installed.")
    print("Install with: pip install tabula-py pandas")
    sys.exit(1)

try:
    from pdf_to_csv import parse_ky_pdf_tabula, clean_value
except ImportError:
    print("Error: Could not import tools/pdf_to_csv.py")
    sys.exit(1)


def pdf_to_openelections(pdf_path: str, election_date: str, level: str = 'county'):
    """
    Convert a Kentucky election PDF to OpenElections format.
    
    Args:
        pdf_path: Path to the PDF file
        election_date: Date in YYYYMMDD format
        level: 'county' or 'precinct'
    """
    print(f"Converting: {pdf_path}")
    print(f"Election date: {election_date}")
    print(f"Level: {level}")
    print()
    
    # Use the existing parser from tools/pdf_to_csv.py
    print("Extracting data using tabula...")
    df = parse_ky_pdf_tabula(pdf_path)
    
    if df.empty:
        print("⚠ No data extracted. The PDF may have a complex layout.")
        print("   Try manually reviewing the PDF structure.")
        return False
    
    print(f"Extracted {len(df)} rows of data")
    print()
    
    # Convert to OpenElections format
    output_filename = f"{election_date}__ky__general__{level}.csv"
    output_path = Path('data') / output_filename
    
    # The OpenElections format requires specific columns
    required_columns = [
        'county', 'office', 'district', 'candidate', 'party', 'votes',
        'election_day', 'absentee', 'av_counting_boards', 'early_voting',
        'mail', 'provisional', 'pre_process_absentee'
    ]
    
    if level == 'precinct':
        required_columns.insert(1, 'precinct')
    
    # Ensure all required columns exist
    for col in required_columns:
        if col not in df.columns:
            df[col] = ''  # Add missing columns
    
    # Select and reorder columns
    output_df = df[required_columns]
    
    # Save to CSV
    output_df.to_csv(output_path, index=False)
    
    print(f"✓ Created: {output_path}")
    print(f"  {len(output_df)} rows")
    
    # Show a preview
    print("\nPreview (first 5 rows):")
    print(output_df.head().to_string(index=False))
    
    return True


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        return
    
    pdf_file = sys.argv[1]
    election_date = sys.argv[2]
    level = sys.argv[3] if len(sys.argv) > 3 else 'county'
    
    # Validate inputs
    if not Path(pdf_file).exists():
        print(f"Error: File not found: {pdf_file}")
        return
    
    if len(election_date) != 8 or not election_date.isdigit():
        print(f"Error: Invalid date format. Expected YYYYMMDD, got: {election_date}")
        return
    
    if level not in ['county', 'precinct']:
        print(f"Error: Invalid level. Expected 'county' or 'precinct', got: {level}")
        return
    
    success = pdf_to_openelections(pdf_file, election_date, level)
    
    if not success:
        print("\nNote: PDF extraction can be tricky. For complex PDFs:")
        print("  1. Try opening the PDF and checking its structure")
        print("  2. Use tools/pdf_to_csv.py directly for more control")
        print("  3. Consider manual extraction to Excel/CSV first")


if __name__ == '__main__':
    main()
