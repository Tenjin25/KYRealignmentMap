# How to Scan and Extract Data from Kentucky Election PDFs

## Quick Answer
The **most practical approaches** for your Kentucky PDFs are:

1. **Use existing CSV/TXT files** (you already have many!)
2. **Manual entry with assistance** (most accurate for complex PDFs)  
3. **OCR for scanned PDFs** (if PDFs are images)
4. **Hybrid: Extract + Manual correction** (get structure, fix details)

---

## Method 1: Copy-Paste from PDF (Simplest) ✂️

**Best for:** Small datasets, one-off extractions

### Steps:
1. Open PDF in Adobe Reader or browser
2. Select table data with cursor
3. Copy (Ctrl+C)
4. Paste into Excel/Google Sheets
5. Clean up formatting
6. Save as CSV

**Pros:** No coding required, fast for small files  
**Cons:** Formatting issues, manual cleanup needed

### Try it now:
```bash
# Open a PDF
start "data/2020 General Election Results.pdf"
# Select and copy the data, paste into Excel
```

---

## Method 2: Use Tabula GUI (No Coding) 🖱️

**Best for:** PDFs with clear tables

### Setup:
1. Download Tabula from: https://tabula.technology/
2. Install and run (it opens in your browser)

### Steps:
1. Launch Tabula
2. Upload your PDF
3. Select table areas with mouse
4. Preview extraction
5. Export as CSV

**Pros:** Visual, no coding, works offline  
**Cons:** Still struggles with complex layouts

### Try it:
```bash
# Download from https://tabula.technology/
# Or install with chocolatey:
choco install tabula

# Then drag-drop your PDF into Tabula's web interface
```

---

## Method 3: OCR Extraction (For Scanned PDFs) 📸

**Best for:** PDFs that are images/scans

### Setup:
```bash
# Install OCR libraries
pip install pytesseract pdf2image pillow

# Install Tesseract engine
# Option A: Direct download
# Go to: https://github.com/UB-Mannheim/tesseract/wiki

# Option B: With Chocolatey
choco install tesseract

# Option C: With Scoop
scoop install tesseract
```

### Usage:
```bash
# Interactive mode (asks which pages to process)
py scripts/ocr_pdf_extractor.py -i "data/2020 General Election.pdf"

# Process specific pages
py scripts/ocr_pdf_extractor.py --pages 1-10 "data/2020 General Election.pdf"

# All pages with high quality
py scripts/ocr_pdf_extractor.py --pages all --dpi 400 "data/2020 General Election.pdf"
```

**Pros:** Works on image-based PDFs, automated  
**Cons:** Requires setup, OCR not 100% accurate

---

## Method 4: Online PDF Converters (Quick & Easy) 🌐

**Best for:** One-off conversions, no installation

### Recommended Services:
1. **Adobe Online Tools** (high quality)
   - https://www.adobe.com/acrobat/online/pdf-to-excel.html
   - Free for limited use

2. **ILovePDF**
   - https://www.ilovepdf.com/pdf_to_excel
   - Good for tables

3. **Zamzar**
   - https://www.zamzar.com/convert/pdf-to-csv/

### Steps:
1. Upload PDF to service
2. Select output format (Excel/CSV)
3. Download converted file
4. Clean up and verify data

**Pros:** No installation, quick  
**Cons:** Privacy concerns (uploading data), requires internet

---

## Method 5: Use Your Existing Tools (Recommended!) ✅

You already have working scripts! Use them as a **starting point**:

```bash
# Extract whatever you can
py scripts/robust_pdf_extractor.py "data/2020 General Election.pdf"

# This gives you:
# - County list
# - Some vote numbers
# - CSV structure

# Then manually correct:
# - Candidate names
# - Party affiliations
# - Verify vote counts
```

---

## Method 6: Manual Entry Template (Most Accurate) 📝

**Best for:** Critical accuracy, complex PDFs

I can create a spreadsheet template you fill in while viewing the PDF:

```bash
# Create template
py scripts/create_entry_template.py --year 2020 --race President

# This creates: 2020_president_entry_template.xlsx
# With:
# ✓ All 120 counties pre-filled
# ✓ Candidate name columns
# ✓ Validation rules
# ✓ Auto-calculated totals
```

### Workflow:
1. Open PDF on one screen
2. Open template on other screen
3. Enter numbers while viewing PDF
4. Template validates as you type
5. Export to OpenElections format

**Pros:** 100% accurate, validates as you go  
**Cons:** Time-consuming, manual work

---

## Method 7: Hybrid Approach (Recommended!) 🔄

**Combine automation with manual review:**

### Step 1: Auto-extract structure
```bash
py scripts/robust_pdf_extractor.py "data/2020 General Election.pdf"
# Gets: counties, some votes, basic structure
```

### Step 2: Export to Excel for editing
```python
import pandas as pd
df = pd.read_csv('data/20201103__ky__general__county.csv')
df.to_excel('data/20201103_for_editing.xlsx', index=False)
```

### Step 3: Manual corrections
- Open in Excel
- Fix candidate names (from "Candidate 1" to "Donald Trump")
- Add party affiliations
- Verify/correct vote counts
- Fill in office field

### Step 4: Convert back
```python
df = pd.read_excel('data/20201103_for_editing.xlsx')
df.to_csv('data/20201103__ky__general__county.csv', index=False)
```

### Step 5: Validate
```bash
py scripts/validate_extraction.py data/20201103__ky__general__county.csv
```

---

## Method 8: Use Your TXT Files! (BEST OPTION) 🎯

**You already have clean .txt files - use those!**

```bash
# Check what you have
ls data/*.txt

# Output shows:
# 00Gen_Statewidebycounty.txt
# 2002statebycounty.txt
# 2004statebyCOUNTY.txt
# 2007statewidebyCOUNTY.txt
# STATEwide by candidate by county gen 08.txt
```

These are **much easier to parse** than PDFs! Want me to create a txt-to-CSV converter?

---

## Practical Workflow for Your Project

### For PDFs You Have:

**2012, 2014, 2015, 2016 PDFs:**
```bash
# Try automated extraction
py scripts/robust_pdf_extractor.py --all

# Check results
py scripts/validate_extraction.py data/2012*.csv
py scripts/validate_extraction.py data/2014*.csv

# Manually correct in Excel
# Focus on: candidate names, party, office
```

**2019, 2020, 2022, 2023, 2024 PDFs:**
```bash
# These are more complex - use hybrid approach:

# 1. Get structure
py scripts/ky_specific_pdf_parser.py "data/2020 General Election.pdf"

# 2. Export to Excel
# 3. Open PDF side-by-side with Excel
# 4. Fill in correct candidate names
# 5. Verify vote totals
# 6. Save and validate
```

---

## Quick Comparison Table

| Method | Setup Time | Accuracy | Speed | Best For |
|--------|-----------|----------|-------|----------|
| Copy-Paste | 0 min | Medium | Fast | Small files |
| Tabula GUI | 5 min | Medium | Fast | Clear tables |
| Online Tools | 0 min | Medium | Fast | One-off tasks |
| OCR | 15 min | Low-Med | Slow | Scanned PDFs |
| Scripts (auto) | Done | Low-Med | Fast | Batch processing |
| Manual Entry | 5 min | High | Slow | Critical data |
| **Hybrid** | Done | **High** | Med | **Most PDFs** |
| **TXT Files** | 10 min | **High** | **Fast** | **Years with TXT** |

---

## My Recommendation for You

### Short-term (This Week):
1. **Use your TXT files** for 2002-2008 data
2. **Hybrid approach** for 2012-2024 PDFs:
   - Run scripts to get structure
   - Manual corrections in Excel
   - Validate results

### Setup Required:
```bash
# You already have these
pip install pandas tabula-py

# Optional (for OCR):
pip install pytesseract pdf2image
choco install tesseract
```

### Realistic Expectations:
- **Fully automated:** 60-70% accurate (needs review)
- **Hybrid approach:** 95%+ accurate (some manual work)
- **Manual entry:** 100% accurate (time-consuming)

---

## Need Help With Specific Method?

Tell me which approach you want to try:

**Option A:** "Create a TXT file parser" - for your existing .txt files  
**Option B:** "Show me the hybrid workflow" - step-by-step  
**Option C:** "Create entry template" - for manual data entry  
**Option D:** "Try different PDF tool" - test more extraction methods

Each method has trade-offs between:
- ⚡ **Speed** (how fast)
- 🎯 **Accuracy** (how correct)
- 💪 **Effort** (how much work)

What matters most for your project?
