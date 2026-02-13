"""
OCR scan specific pages to help find missing county vote counts.
"""

import pytesseract
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

import fitz
from PIL import Image

def scan_page(pdf_path, page_num):
    """Scan single page and show text."""
    doc = fitz.open(pdf_path)
    page = doc[page_num - 1]
    
    pix = page.get_pixmap(dpi=250)
    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
    
    text = pytesseract.image_to_string(img)
    doc.close()
    return text

pdf_path = "data/off2010gen.pdf"
missing = ['Caldwell', 'Casey', 'Greenup', 'Harlan', 'Woodford']

print("="*70)
print("Finding Missing Counties in OCR Text")
print("="*70)

# Scan pages 2-5 and search for missing counties
for page_num in range(2, 6):
    print(f"\n{'='*70}")
    print(f"Page {page_num}")
    print('='*70)
    
    text = scan_page(pdf_path, page_num)
    lines = text.split('\n')
    
    # Show lines that might contain missing counties
    for line in lines:
        line_lower = line.lower()
        for county in missing:
            if county.lower() in line_lower or county.lower()[:4] in line_lower:
                print(f"\nPossible {county}: {line}")
                break
