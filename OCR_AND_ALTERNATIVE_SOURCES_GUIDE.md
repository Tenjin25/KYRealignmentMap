# OCR Setup & Alternative Data Sources Guide

## Status Summary

### ✅ What You Already Have
Data files exist for these years:
- 2002, 2003, 2004, 2007, 2008, 2010 (partial), 2012, 2014, 2015, 2016, 2020, 2023, 2024

### ❌ Missing Data (Must Extract or Find)
- **2019 General** - Scanned PDF (3 MB)
- **2022 General** - Scanned PDF (4 MB)
- **2010 Off-year** - Scanned PDF (5 MB)
- **2011 Off-year** - Scanned PDF (1 MB)

---

## Option 1: Find Alternative Data Sources (QUICKEST)

**Primary Source: OpenElections GitHub**
```
https://github.com/openelections/openelections-data-ky
```

Steps:
1. Visit the repository
2. Look for folders: `2019/`, `2022/`, `2010/`, `2011/`
3. If CSV files exist, download them
4. Copy to your `data/` folder

**Other Sources to Check:**
- Kentucky Secretary of State: https://elections.ky.gov/results-and-data/
- Dave Leip's Atlas: https://uselectionatlas.org/
- Ballotpedia: https://ballotpedia.org/Kentucky_elections
- Kentucky Data Portal: https://data.ky.gov/

**Email Option:**
Send email to Kentucky Secretary of State elections department asking for CSV exports of 2019, 2022, 2010, 2011 data. They often share these.

---

## Option 2: Set Up Local OCR (More Complex)

### Step 1: Install Tesseract OCR Engine

**Windows - Option A: Direct Download (Recommended)**
1. Go to: https://github.com/UB-Mannheim/tesseract/wiki
2. Download latest: `tesseract-ocr-w64-setup-v5.4.0.exe`
3. Run installer (next → next → finish, defaults are fine)
4. Verify installation:
   ```powershell
   tesseract --version
   ```

**Windows - Option B: Using Chocolatey (if you have admin)**
```powershell
choco install tesseract
```

**Windows - Option C: Using Scoop**
```powershell
scoop install tesseract
```

### Step 2: Extract OCR Data

Python packages already installed:
- ✓ pytesseract
- ✓ pdf2image
- ✓ pillow

**Usage:**
```powershell
# Extract first 10 pages with default quality
py scripts\ocr_ky_extractor.py "data\2019 General Certified Results.pdf" --pages 1-10

# Extract all pages with high quality (slower but more accurate)
py scripts\ocr_ky_extractor.py "data\2022 Certified General Election Results.pdf" --dpi 300

# Extract everything
py scripts\ocr_ky_extractor.py "data\2019 General Certified Results.pdf"
```

### Step 3: Manual Correction

OCR results are not perfect. You'll need to:
1. Export OCR output to CSV
2. Open in Excel
3. Compare with PDF and fix errors
4. Fix candidate names and party affiliations

---

## Recommended Workflow

### Fastest Path (Recommended):
1. **Check OpenElections GitHub first** (5 minutes)
   - If they have the data, you're done instantly
   
2. **If not found, try online sources** (15 minutes)
   - Dave Leip's Atlas
   - Ballotpedia
   - State website downloads
   
3. **Last resort: OCR** (1-2 hours including setup + manual corrections)
   - Only if other sources don't have the data
   - Requires Tesseract installation
   - Requires manual verification

### My Recommendation:
Start with **Option 1: Finding Alternative Data** before setting up OCR. The data was likely transcribed by election researchers and is probably available somewhere online.

---

## Quick Commands Reference

```powershell
# Check what years you're missing
py scripts\check_coverage.py

# See all recommended data sources
py scripts\find_data_sources.py

# (Once Tesseract is installed) Extract OCR data
py scripts\ocr_ky_extractor.py "data\2019 General Certified Results.pdf"
```

---

## Troubleshooting

**Problem:** "Tesseract not found"
**Solution:** Download and install from: https://github.com/UB-Mannheim/tesseract/wiki

**Problem:** OCR output has many errors
**Solution:** 
- Try with `--dpi 300` for higher quality
- Process fewer pages at a time
- Manually review results in Excel

**Problem:** No candidates/votes extracted
**Solution:** The OCR didn't work well. Try:
- Using --dpi 300 or 400
- May need to use manual copy-paste from PDF
- Or find alternative data source

---

## Files Created

- `scripts/ocr_ky_extractor.py` - OCR extraction tool
- `scripts/find_data_sources.py` - Alternative source finder
- `scripts/check_coverage.py` - See what data you have vs missing

---

## Priority List

**Easy (do first):**
1. Check OpenElections GitHub
2. Email Kentucky Secretary of State
3. Try Dave Leip's Atlas

**Medium (if above fails):**
4. Try online PDF converters (upload 1 page to test)

**Hard (only if necessary):**
5. Install Tesseract
6. Run OCR extraction
7. Manually correct results

