# OpenElections Format Converter

This script converts Kentucky election data from various formats into the standardized OpenElections CSV format.

## OpenElections Format

The OpenElections project uses a standardized CSV format for election results:

### County-Level Format
```csv
county,office,district,candidate,party,votes,election_day,absentee,av_counting_boards,early_voting,mail,provisional,pre_process_absentee
```

### Precinct-Level Format
```csv
county,precinct,office,district,candidate,party,votes,election_day,absentee,av_counting_boards,early_voting,mail,provisional,pre_process_absentee
```

## Supported Input Formats

1. **Kentucky State Board of Elections Fixed-Width Format** (`*.txt`)
   - Candidates in rows, counties in columns
   - Examples: `2002statebycounty.txt`, `STATEwide by candidate by county gen 08.txt`

2. **PDF Files** (`*.pdf`) - Experimental
   - Uses tabula-py to extract tables from PDF documents
   - Requires: `pip install tabula-py pandas`
   - For complex PDFs, use `tools/pdf_to_csv.py` or `scripts/convert_pdf_to_openelections.py`

## Usage

### Basic Usage

```python
from convert_to_openelections import OpenElectionsFormatter

# Create formatter instance
formatter = OpenElectionsFormatter(output_dir='data')

# Convert a text file
formatter.convert_file(
    input_file='data/2002statebycounty.txt',
    election_date='20021105',  # YYYYMMDD format
    election_type='general',   # 'general', 'primary', 'special'
    level='county'             # 'county' or 'precinct'
)
```

### PDF Conversion

For PDF files, use the dedicated PDF converter:

```bash
py scripts/convert_pdf_to_openelections.py "data/2012genresults.pdf" 20121106 county
```

Or use the command-line tool with PDF support:

```bash
py scripts/convert.py "data/2012genresults.pdf" 20121106 general county
```

**Note:** PDF extraction requires tabula-py and can be unreliable for complex layouts. For best results with PDFs, consider using `tools/pdf_to_csv.py` directly.

### Batch Conversion

Convert multiple files at once:

```bash
py scripts/examples.py
```

This will convert all available old-format election files to OpenElections format.

### Individual File Conversion

```bash
py scripts/test_converter.py
```

## File Naming Convention

Output files follow the OpenElections naming convention:

```
YYYYMMDD__STATE__ELECTION_TYPE__LEVEL.csv
```

Examples:
- `20021105__ky__general__county.csv`
- `20081104__ky__general__county.csv`
- `20241105__ky__general__precinct.csv`

## Output

Converted files are saved to the `data/` directory with proper OpenElections formatting.

## Example

```python
# Convert 2002 general election data
formatter = OpenElectionsFormatter(output_dir='data')
formatter.convert_file(
    'data/2002statebycounty.txt',
    '20021105',
    'general',
    'county'
)
# Creates: data/20021105__ky__general__county.csv
```

## Available Scripts

### 1. `convert_to_openelections.py`
Main conversion library with the `OpenElectionsFormatter` class.

### 2. `convert.py` (Command-line tool)
Quick conversion of single files (TXT or PDF):
```bash
py scripts/convert.py data/election.txt 20021105 general county
py scripts/convert.py data/election.pdf 20121106 general county
```

### 3. `convert_pdf_to_openelections.py` (PDF-specific converter)
Dedicated PDF converter using the existing pdf_to_csv.py tools:
```bash
py scripts/convert_pdf_to_openelections.py "data/2012genresults.pdf" 20121106 county
```

### 4. `examples.py` (Batch conversion)
Converts all pre-configured old-format text files at once:
```bash
py scripts/examples.py
```

### 5. `test_converter.py` (Simple example)
Basic demonstration of converting one file.

## Converted Files

The following OpenElections-format files have been created:

| Year | Election | File | Status |
|------|----------|------|--------|
| 2000 | General  | `00Gen_Statewidebycounty.txt` | ✓ Source available (txt) |
| 2002 | General  | `20021105__ky__general__county.csv` | ✓ Converted |
| 2003 | General  | `2003statewidebycounty.txt` | ✓ Source available (txt) |
| 2004 | General  | `2004statebyCOUNTY.txt` | ✓ Source available (txt) |
| 2007 | General  | `2007statewidebyCOUNTY.txt` | ✓ Source available (txt) |
| 2008 | General  | `STATEwide by candidate by county gen 08.txt` | ✓ Source available (txt) |
| 2010 | General  | `off2010gen.pdf` | ⚠ PDF needs conversion |
| 2011 | General  | `off2011gen.pdf` | ⚠ PDF needs conversion |
| 2012 | General  | `2012genresults.pdf` | ⚠ PDF needs conversion |
| 2014 | General  | `2014 General Election Results.pdf` | ⚠ PDF needs conversion |
| 2015 | General  | `2015 General Election Results.pdf` | ⚠ PDF needs conversion |
| 2016 | General  | `2016 General Election Results.pdf` | ⚠ PDF needs conversion |
| 2019 | General  | `2019 General Certified Results.pdf` | ⚠ PDF needs conversion |
| 2020 | General  | `2020 General Election Results.pdf` | ⚠ PDF needs conversion |
| 2022 | General  | `2022 Certified General Election Results.pdf` | ⚠ PDF needs conversion |
| 2023 | General  | `Certification of Election Results for 2023 General Election Final.pdf` | ⚠ PDF needs conversion |
| 2024 | General  | `20241106__ky__general__county.csv` | ✓ Already in OpenElections format |
| 2024 | General  | `20241105__ky__general__precinct.csv` | ✓ Already in OpenElections format (precinct-level) |

### PDF Conversion TODO

The following PDFs need to be converted to OpenElections format:

```bash
# 2010 General
py scripts/convert_pdf_to_openelections.py "data/off2010gen.pdf" 20101102 county

# 2011 General  
py scripts/convert_pdf_to_openelections.py "data/off2011gen.pdf" 20111108 county

# 2012 General
py scripts/convert_pdf_to_openelections.py "data/2012genresults.pdf" 20121106 county

# 2014 General
py scripts/convert_pdf_to_openelections.py "data/2014 General Election Results.pdf" 20141104 county

# 2015 General
py scripts/convert_pdf_to_openelections.py "data/2015 General Election Results.pdf" 20151103 county

# 2016 General
py scripts/convert_pdf_to_openelections.py "data/2016 General Election Results.pdf" 20161108 county

# 2019 General
py scripts/convert_pdf_to_openelections.py "data/2019 General Certified Results.pdf" 20191105 county

# 2020 General
py scripts/convert_pdf_to_openelections.py "data/2020 General Election Results.pdf" 20201103 county

# 2022 General
py scripts/convert_pdf_to_openelections.py "data/2022 Certified General Election Results.pdf" 20221108 county

# 2023 General
py scripts/convert_pdf_to_openelections.py "data/Certification of Election Results for 2023 General Election Final.pdf" 20231107 county
```

## Requirements

- Python 3.7+
- No external dependencies (uses only standard library)

## Notes

- The script automatically expands county abbreviations (e.g., `ADAI` → `Adair`)
- Candidate names are extracted from the fixed-width format
- Empty vote breakdowns (election_day, absentee, etc.) are left blank when not available in source data
- PDF files in the `data/` directory may require additional processing using `tools/pdf_to_csv.py`
