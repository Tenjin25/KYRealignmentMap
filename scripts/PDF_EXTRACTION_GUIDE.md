# PDF Extraction Improvements for Kentucky Election Data

## Overview

This document describes the improvements made to PDF conversion scripts for extracting Kentucky election results from recent years. The enhanced scripts provide better error handling, validation, and multiple fallback strategies to ensure robust extraction.

## New Features

### 1. **Multiple Extraction Strategies**
- **Lattice Mode**: For PDFs with table borders
- **Stream Mode**: For PDFs without borders
- **Auto Mode**: Automatic table detection
- **PDFPlumber**: For complex layouts (optional)

### 2. **Comprehensive Validation**
- Validates extracted data for completeness
- Checks county coverage (Kentucky has 120 counties)
- Verifies candidate information
- Validates vote counts
- Provides warnings for potential issues

### 3. **Better Data Cleaning**
- Enhanced candidate name cleaning
- County name standardization with validation
- Party affiliation detection (REP, DEM, LIB, IND, GRN, CON, etc.)
- Robust vote count parsing

### 4. **Improved Error Handling**
- Graceful fallback between strategies
- Detailed logging at multiple levels
- Exception handling with informative messages
- Debug mode for troubleshooting

### 5. **Duplicate Handling**
- Automatic merging of duplicate entries
- Aggregation of votes by county/candidate/party

## Files

### Core Utilities
- **`scripts/pdf_utils.py`** - Common utilities for PDF processing
  - Party and office name mappings
  - Data cleaning functions
  - Validation functions
  - OpenElections format helpers

### Extraction Scripts

#### 1. `scripts/pdf_extractor.py` (Enhanced)
Simple extractor with improvements:
- Multiple fallback strategies
- Basic validation
- Better logging
- Works standalone or with utilities

**Usage:**
```bash
# Process a single PDF
python scripts/pdf_extractor.py "data/2024 General Election.pdf"

# Process all PDFs in data/
python scripts\pdf_extractor.py --all

# Verbose mode for debugging
python scripts/pdf_extractor.py -v "data/2024 General Election.pdf"
```

#### 2. `scripts/robust_pdf_extractor.py` (New)
Advanced extractor with maximum robustness:
- All extraction strategies with scoring
- Comprehensive validation
- Quality metrics
- Detailed reporting

**Usage:**
```bash
# Process a single PDF
python scripts/robust_pdf_extractor.py "data/2024 General Election.pdf"

# Process all PDFs
python scripts/robust_pdf_extractor.py --all

# Specify output directory
python scripts/robust_pdf_extractor.py --output-dir output/ "data/2024.pdf"

# Verbose mode
python scripts/robust_pdf_extractor.py -v "data/2024 General Election.pdf"
```

## Installation

### Required Packages
```bash
pip install pandas tabula-py
```

### Optional Packages (for better extraction)
```bash
# For PDFPlumber strategy
pip install pdfplumber pikepdf

# For OCR support (future enhancement)
pip install pytesseract pdf2image
```

### Java Requirement
Tabula-py requires Java. Install Java 8 or higher:
- Windows: https://www.java.com/download/
- Or use: `choco install openjdk` (with Chocolatey)

## Common Issues and Solutions

### Issue 1: No tables extracted

**Symptoms:**
- "No tables extracted by any strategy"
- Empty output file

**Solutions:**
1. Try verbose mode to see detailed logs:
   ```bash
   python scripts/robust_pdf_extractor.py -v "yourfile.pdf"
   ```

2. Check PDF structure:
   - Open PDF and verify it contains actual tables (not screenshots)
   - Check if tables have borders (use Lattice) or not (use Stream)

3. Install optional dependencies:
   ```bash
   pip install pdfplumber pikepdf
   ```

### Issue 2: Incomplete extraction

**Symptoms:**
- "Only X counties found" warning
- Missing candidates or incomplete data

**Solutions:**
1. Check validation warnings in output
2. Try robust_pdf_extractor.py instead of pdf_extractor.py
3. Examine PDF manually for:
   - Multiple tables spread across pages
   - Merged cells or complex formatting
   - Mixed data types in columns

### Issue 3: Wrong party affiliations

**Symptoms:**
- Party column empty or incorrect

**Solutions:**
1. Check if party info is in candidate name (e.g., "John Doe (R)")
2. Update party mappings in `pdf_utils.py`:
   ```python
   PARTY_MAPPINGS = {
       'REP': ['REP', 'REPUBLICAN', '(R)', 'R-'],
       # Add more patterns as needed
   }
   ```

### Issue 4: Duplicate entries

**Symptoms:**
- Same county/candidate appears multiple times
- Vote totals seem inflated

**Solutions:**
- The scripts automatically merge duplicates
- Check output for "Merged X rows into Y rows" message
- If still seeing duplicates, verify original PDF structure

## Validation Checklist

When processing a new PDF, verify:

1. **Row count**: Should have many rows (at least 100 for statewide race)
2. **County count**: Should have ~120 counties (Kentucky has 120)
3. **Candidate count**: At least 2 candidates per race
4. **Vote totals**: Should be reasonable numbers (not all zeros)
5. **Party coverage**: Major races should have REP and DEM candidates

## Manual Review Process

After extraction:

1. Open the generated CSV file
2. Spot check a few counties you're familiar with
3. Verify vote totals make sense
4. Check that party affiliations are correct
5. Ensure office/district fields are filled (may need manual entry)

## Performance Tips

### For Large PDFs:
1. Process one PDF at a time initially
2. Use verbose mode first to understand the structure
3. Once working, batch process with --all flag

### For Scanned PDFs (Images):
Current scripts don't support OCR. Options:
1. Find a text-based version of the PDF
2. Install OCR support (pytesseract + pdf2image)
3. Convert PDF pages to text first using external tools

## Example: Processing 2024 Results

```bash
# Step 1: Test with verbose mode
python scripts/robust_pdf_extractor.py -v "data/2024_general_results.pdf"

# Step 2: Review output and warnings
# - Check data/20241105__ky__general__county.csv
# - Read validation warnings

# Step 3: If successful, process remaining PDFs
python scripts/robust_pdf_extractor.py --all

# Step 4: Verify results
python tools/check_csv.py data/20241105__ky__general__county.csv
```

## Extending the Scripts

### Adding New Party Mappings

Edit `scripts/pdf_utils.py`:
```python
PARTY_MAPPINGS = {
    'REP': ['REP', 'REPUBLICAN', '(R)', 'GOP'],
    'DEM': ['DEM', 'DEMOCRATIC', '(D)'],
    # Add your new party
    'NEW': ['NEW', 'NEW PARTY', '(N)'],
}
```

### Adding New Office Types

Edit `scripts/pdf_utils.py`:
```python
OFFICE_MAPPINGS = {
    'President': ['PRESIDENT', 'PRES', 'PRESIDENTIAL'],
    # Add your new office
    'School Board': ['SCHOOL BOARD', 'BOARD OF EDUCATION'],
}
```

### Custom Extraction Strategy

In `scripts/robust_pdf_extractor.py`, add a new strategy class:
```python
class MyCustomStrategy(PDFExtractionStrategy):
    def __init__(self):
        super().__init__("My Custom Strategy")
    
    def extract(self, pdf_path: str) -> Tuple[pd.DataFrame, Dict]:
        # Your custom extraction logic
        results = []
        # ... process PDF ...
        return pd.DataFrame(results), {'strategy': self.name}
```

## Troubleshooting Steps

1. **Enable verbose logging:**
   ```bash
   python scripts/robust_pdf_extractor.py -v yourfile.pdf
   ```

2. **Check Java installation:**
   ```bash
   java -version
   ```

3. **Verify required packages:**
   ```bash
   python -c "import tabula; import pandas; print('OK')"
   ```

4. **Test with a known-good PDF:**
   - Use one of the older PDFs that worked before
   - If it fails, check your environment

5. **Examine raw PDF structure:**
   - Open PDF in a viewer
   - Try copying table data manually
   - If you can't copy it, PDF may be an image (needs OCR)

## Future Enhancements

Potential improvements for even more robustness:

1. **OCR Support**: Extract from scanned/image PDFs
2. **Machine Learning**: Train model to recognize table structures
3. **Office Detection**: Auto-detect office names from PDF content
4. **District Extraction**: Better pattern matching for districts
5. **Multi-format Support**: Handle Excel, Word documents
6. **Web scraping**: Download results directly from official sites
7. **Precinct-level**: Support precinct-level extraction
8. **Batch validation**: Compare against previous years for anomalies

## Support

For issues or questions:
1. Check this document first
2. Run with `-v` flag for detailed logs
3. Review the generated CSV for obvious issues
4. Check logs for specific error messages

## Best Practices

1. **Always backup**: Keep original PDFs safe
2. **Version control**: Track changes to extracted CSVs
3. **Document**: Note any manual corrections made
4. **Validate**: Always spot-check results
5. **Iterate**: Run multiple times with different strategies if needed
6. **Test early**: Don't wait until you have many PDFs to process

## Quick Reference

| Script | Best For | Speed | Complexity |
|--------|----------|-------|------------|
| `pdf_extractor.py` | Simple tables | Fast | Low |
| `robust_pdf_extractor.py` | Complex PDFs | Slower | High |
| `tools/pdf_to_csv.py` | Legacy support | Medium | Medium |

## Summary

The improved PDF extraction system provides:
- ✅ Multiple extraction strategies with automatic fallback
- ✅ Comprehensive validation and quality checks
- ✅ Better error handling and logging
- ✅ Enhanced data cleaning and standardization
- ✅ Duplicate detection and merging
- ✅ Verbose mode for debugging
- ✅ Standalone and utility-enhanced modes

Use `robust_pdf_extractor.py` for best results with recent year PDFs that may have complex formatting.
