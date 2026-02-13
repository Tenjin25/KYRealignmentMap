# Quick Start: Processing Kentucky Election PDFs

## The Reality Check

**Bad news:** Your PDFs are too complex for 100% automated extraction.  
**Good news:** You can get 90% there with automation + 10% manual cleanup.

## The Workflow That Actually Works

### Step 1: Extract Structure (2 minutes)

```powershell
# This gets you counties + vote numbers
py scripts\ky_specific_pdf_parser.py "data\2024 General Election Certification as Amended on December 9th 2024.pdf"
```

**What this produces:**
- ✅ All counties extracted
- ✅ Vote numbers extracted
- ❌ Generic candidate names ("Candidate 1", "Candidate 2")
- ❌ Missing party/office info

### Step 2: Export to Excel for Editing (1 minute)

```powershell
# Convert CSV to Excel for easy editing
py -c "import pandas as pd; df = pd.read_csv('data/20241105__ky__general__county.csv'); df.to_excel('data/20241105_EDIT_ME.xlsx', index=False)"
```

### Step 3: Manual Corrections (15-30 minutes)

1. Open `data/20241105_EDIT_ME.xlsx` in Excel
2. Open the PDF side-by-side
3. Replace generic names with real ones:
   - "Candidate 1" → Look at PDF, see it's the first candidate
   - For 2024 Presidential: "Donald J. Trump"
   - "Candidate 2" → "Kamala D. Harris"
   - etc.
4. Fill in the `party` column: REP, DEM, LIB, IND, etc.
5. Fill in the `office` column: "President", "U.S. Senate", etc.
6. **Pro tip:** Use Excel's Find & Replace to change all "Candidate 1" at once

### Step 4: Convert Back to CSV (1 minute)

```powershell
py -c "import pandas as pd; df = pd.read_excel('data/20241105_EDIT_ME.xlsx'); df.to_csv('data/20241105__ky__general__county.csv', index=False)"
```

### Step 5: Validate (1 minute)

```powershell
py scripts\validate_extraction.py "data\20241105__ky__general__county.csv"
```

## Time Investment

- **Fully automated:** 3 minutes, but 60% accuracy (unusable)
- **Hybrid workflow:** 20-35 minutes, 95%+ accuracy ✅
- **Pure manual entry:** 2-3 hours, 100% accuracy (overkill)

## Alternative: Use Your TXT Files!

For years 2002-2008, you already have .txt files that are WAY easier to parse:

```powershell
# Check what you have
ls data\*.txt

# These are much better than PDFs!
# Want me to create a TXT parser?
```

## What About Other PDFs?

**Process each PDF based on year:**

| Year | Method | Notes |
|------|--------|-------|
| 2002-2008 | **Use .txt files** | Much easier than PDFs |
| 2010-2011 | Hybrid (PDF → Excel → Fix) | Similar format |
| 2012-2016 | Hybrid | Multiple races |
| 2019-2024 | Hybrid | Most complex |

## Quick Commands Reference

```powershell
# Extract from PDF
py scripts\ky_specific_pdf_parser.py "data\FILENAME.pdf"

# CSV to Excel
py -c "import pandas as pd; pd.read_csv('file.csv').to_excel('file.xlsx', index=False)"

# Excel to CSV
py -c "import pandas as pd; pd.read_excel('file.xlsx').to_csv('file.csv', index=False)"

# Validate
py scripts\validate_extraction.py "data\file.csv"
```

## Need More Help?

Tell me:
1. **Which year** you want to process
2. **Which race** (President, Senate, etc.)
3. Do you want me to **create a better extraction script** for that specific PDF?

The key insight: **Don't fight the PDFs. Work with them.**
