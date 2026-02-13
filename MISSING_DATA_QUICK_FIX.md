# Missing Data - Quick Action Plan

## Your Situation
- ✅ You have data for 13 years of elections
- ❌ Missing: 2019, 2022, 2010 off-year, 2011 off-year (4 years)
- These are scanned PDFs that can't be automatically extracted

## Fastest Solution: Find Existing Data

### Action 1: Check GitHub (2 minutes)
Open in browser: https://github.com/openelections/openelections-data-ky

Look for CSV files for 2019, 2022, 2010, 2011
- If they exist → Download and copy to your data/ folder → Done!
- If not → Continue to Action 2

### Action 2: Check State Website (5 minutes)  
Kentucky Secretary of State: https://elections.ky.gov/results-and-data/

Look for downloadable Excel/CSV files for these years
- If found → Download and copy to data/ folder → Done!
- If not → Continue to Action 3

### Action 3: Try Dave Leip's Atlas (5 minutes)
https://uselectionatlas.org/

- Go to Kentucky
- Look for election years you're missing
- May have county-level results you can copy

### Action 4: Email State (if all above fail)
Send email to: elections@ky.gov
Subject: "CSV Export Request - 2019, 2022, 2010, 2011 General Election Results"

Many states keep CSV files ready to share but don't publish them prominently.

---

## If All Else Fails: OCR Route

### Prerequisites (one-time setup)
1. Install Tesseract OCR: 
   - Download from https://github.com/UB-Mannheim/tesseract/wiki
   - Install with defaults
   - Verify: `tesseract --version`

2. You already have Python packages installed

### Then run OCR:
```powershell
# Test on a few pages first
py scripts\ocr_ky_extractor.py "data\2019 General Certified Results.pdf" --pages 1-5

# If that works, extract all
py scripts\ocr_ky_extractor.py "data\2019 General Certified Results.pdf"
```

### Then manually fix:
1. Export OCR result to Excel
2. Compare with PDF side-by-side  
3. Fix candidate names
4. Fix vote numbers (some OCR errors are common)
5. Save as CSV

Time: 1-2 hours per year including setup & verification

---

## My Recommendation

**Try this order:**
1. ✅ Check OpenElections GitHub (2 min) 
2. ✅ Check Kentucky Secretary of State (5 min)
3. ✅ Email them if not found (2 min, but wait for response)
4. ⏳ Try online PDF converters (10 min, test 1 page)
5. ❌ Install Tesseract OCR (last resort, more complex)

**Chances are very good the data exists already!** Election data is often transcribed by volunteer projects. Start with GitHub/OpenElections.

---

## What You Have Now

Already extracted and ready to use:
- 2002, 2003, 2004, 2007, 2008, 2010 Senate, 2012, 
- 2014, 2015, 2016, 2020, 2023, 2024

That's 13 years! Adding these 4 would give you 17+ comprehensive years of Kentucky election data.

