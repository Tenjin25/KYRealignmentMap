"""
Extract 2022 PDF using EasyOCR (pure Python OCR).
No external Tesseract needed!
"""

import sys
from pathlib import Path

print("=" * 80)
print("2022 PDF OCR EXTRACTION - EasyOCR")
print("=" * 80)

pdf_path = Path("data/2022 Certified General Election Results.pdf")

print("\nStep 1: Installing EasyOCR (first time only, ~200MB download)...")
try:
    import easyocr
    print("  ✓ EasyOCR already available")
except ImportError:
    print("  Installing easyocr...")
    import subprocess
    result = subprocess.run(
        [sys.executable, '-m', 'pip', 'install', 'easyocr', '-q'],
        capture_output=True,
        text=True
    )
    if result.returncode == 0:
        print("  ✓ EasyOCR installed")
    else:
        print(f"  ✗ Installation failed: {result.stderr}")
        sys.exit(1)

# Now import
import easyocr
from pdf2image import convert_from_path
import pandas as pd
import re

print("\nStep 2: Converting PDF to images...")
print("  (This will take a while for 258 pages...)")

try:
    # Convert only first 5 pages as a test
    print("  Testing with first 5 pages...")
    images = convert_from_path(str(pdf_path), first_page=1, last_page=5, dpi=150)
    print(f"  ✓ Converted {len(images)} pages to images")
    
    print("\nStep 3: Running OCR on images...")
    print("  Initializing OCR reader...")
    reader = easyocr.Reader(['en'], gpu=False)  # CPU mode
    
    all_text = []
    for i, image in enumerate(images, 1):
        print(f"  Processing page {i}...", end=" ", flush=True)
        results = reader.readtext(image)
        
        # Extract text from results
        page_text = '\n'.join([text[1] for text in results])
        all_text.append(page_text)
        
        # Count counties found
        counties_found = len([t for t in page_text.split('\n') if 'County' in t or any(c in t for c in 
            ['Adair', 'Allen', 'Anderson', 'Ballard', 'Barren', 'Bath', 'Bell', 'Boone'])])
        
        print(f"✓ ({len(page_text)} chars)")
    
    combined_text = '\n'.join(all_text)
    
    print(f"\n  ✓ OCR complete!")
    print(f"\n  Total text extracted: {len(combined_text)} characters")
    print(f"\n  First 1000 characters:\n{combined_text[:1000]}")
    
    # Look for Kentucky counties
    ky_counties = ['Adair', 'Allen', 'Anderson', 'Ballard', 'Barren', 'Bath', 'Bell', 'Boone',
                   'Bourbon', 'Boyd', 'Boyle']
    
    found_counties = [c for c in ky_counties if c in combined_text]
    print(f"\n  Kentucky counties found: {len(found_counties)}")
    if found_counties:
        print(f"    Examples: {', '.join(found_counties[:5])}")
    
    # Save sample
    with open('ocr_sample_2022.txt', 'w', encoding='utf-8') as f:
        f.write(combined_text)
    print(f"\n  ✓ Saved OCR sample to: ocr_sample_2022.txt")
    
    print("\n" + "=" * 80)
    print("ASSESSMENT")
    print("=" * 80)
    
    if len(found_counties) > 0 and len(combined_text) > 5000:
        print("✓ OCR working reasonably well!")
        print(f"  Found {len(found_counties)} Kentucky counties in text")
        print(f"  Would recommend: Continue OCR on all pages")
        print(f"  Time estimate: 30-60 minutes for full PDF")
    else:
        print("✗ OCR quality is poor")
        print("  Recommendation: Use manual data entry or find alternative source")
    
except Exception as e:
    print(f"\n✗ Error during OCR: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 80)
print("NEXT STEPS")
print("=" * 80)
print("""
If OCR looks good:
  1. Run full OCR on all 258 pages (will take 1-2 hours)
  2. Parse results to extract county/candidate/vote data
  3. Manual verification of extracted data

If OCR looks poor:
  1. Email elections@ky.gov requesting CSV
  2. Check if alternative data source exists
  3. Consider using 2020 presidential + state-level extrapolation
""")
