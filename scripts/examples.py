"""
Example script showing how to convert various Kentucky election files 
to OpenElections CSV format.

Usage:
    py scripts/examples.py
"""

from convert_to_openelections import OpenElectionsFormatter
from pathlib import Path

def main():
    # Initialize the formatter
    formatter = OpenElectionsFormatter(output_dir='data')
    
    # Define the conversions to perform
    conversions = [
        {
            'name': '2002 General Election',
            'input': 'data/2002statebycounty.txt',
            'date': '20021105',  # First Tuesday after first Monday in November 2002
            'type': 'general',
            'level': 'county'
        },
        {
            'name': '2003 General Election',
            'input': 'data/2003statewidebycounty.txt',
            'date': '20031104',
            'type': 'general',
            'level': 'county'
        },
        {
            'name': '2004 General Election',
            'input': 'data/2004statebyCOUNTY.txt',
            'date': '20041102',
            'type': 'general',
            'level': 'county'
        },
        {
            'name': '2007 General Election',
            'input': 'data/2007statewidebyCOUNTY.txt',
            'date': '20071106',
            'type': 'general',
            'level': 'county'
        },
        {
            'name': '2008 General Election',
            'input': 'data/STATEwide by candidate by county gen 08.txt',
            'date': '20081104',
            'type': 'general',
            'level': 'county'
        },
    ]
    
    print("=" * 70)
    print("OpenElections Format Converter - Batch Conversion")
    print("=" * 70)
    print()
    
    successful = 0
    failed = 0
    
    for conversion in conversions:
        print(f"Converting: {conversion['name']}")
        print(f"  Input:  {conversion['input']}")
        
        # Check if input file exists
        if not Path(conversion['input']).exists():
            print(f"  ⚠ SKIPPED: File not found")
            print()
            failed += 1
            continue
        
        try:
            formatter.convert_file(
                input_file=conversion['input'],
                election_date=conversion['date'],
                election_type=conversion['type'],
                level=conversion['level']
            )
            print(f"  ✓ SUCCESS")
            successful += 1
        except Exception as e:
            print(f"  ✗ ERROR: {e}")
            failed += 1
        
        print()
    
    print("=" * 70)
    print(f"Summary: {successful} successful, {failed} failed/skipped")
    print("=" * 70)
    

if __name__ == '__main__':
    main()
