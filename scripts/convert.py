"""
Command-line utility to convert election files to OpenElections format.

Usage:
    py scripts/convert.py <input_file> <election_date> [election_type] [level]
    
Examples:
    py scripts/convert.py data/2002statebycounty.txt 20021105
    py scripts/convert.py data/my_election.txt 20200303 primary county
    
Arguments:
    input_file     : Path to the input file
    election_date  : Date in YYYYMMDD format (e.g., 20021105)
    election_type  : Optional. 'general', 'primary', 'special' (default: general)
    level          : Optional. 'county' or 'precinct' (default: county)
"""

import sys
from pathlib import Path
from convert_to_openelections import OpenElectionsFormatter


def print_usage():
    """Print usage information."""
    print(__doc__)


def main():
    # Check for help flag
    if len(sys.argv) < 2 or sys.argv[1] in ['-h', '--help', 'help']:
        print_usage()
        return
    
    # Parse arguments
    if len(sys.argv) < 3:
        print("Error: Missing required arguments")
        print()
        print_usage()
        return
    
    input_file = sys.argv[1]
    election_date = sys.argv[2]
    election_type = sys.argv[3] if len(sys.argv) > 3 else 'general'
    level = sys.argv[4] if len(sys.argv) > 4 else 'county'
    
    # Validate date format
    if len(election_date) != 8 or not election_date.isdigit():
        print(f"Error: Invalid date format '{election_date}'. Expected YYYYMMDD (e.g., 20021105)")
        return
    
    # Validate election type
    if election_type not in ['general', 'primary', 'special', 'runoff']:
        print(f"Error: Invalid election type '{election_type}'.")
        print("Valid types: general, primary, special, runoff")
        return
    
    # Validate level
    if level not in ['county', 'precinct']:
        print(f"Error: Invalid level '{level}'.")
        print("Valid levels: county, precinct")
        return
    
    # Check if input file exists
    if not Path(input_file).exists():
        print(f"Error: File not found: {input_file}")
        return
    
    # Perform conversion
    print(f"Converting {input_file}...")
    print(f"  Date: {election_date}")
    print(f"  Type: {election_type}")
    print(f"  Level: {level}")
    print()
    
    try:
        formatter = OpenElectionsFormatter(output_dir='data')
        formatter.convert_file(
            input_file=input_file,
            election_date=election_date,
            election_type=election_type,
            level=level
        )
        print()
        print("✓ Conversion complete!")
    except Exception as e:
        print(f"✗ Error during conversion: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == '__main__':
    sys.exit(main() or 0)
