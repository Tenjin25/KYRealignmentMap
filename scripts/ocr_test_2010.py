"""
Extract 2010 Kentucky election results using OCR (scanned PDF).
"""

import sys
from pathlib import Path
import pandas as pd
import re

# Configure Tesseract path
import pytesseract
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

import fitz  # PyMuPDF
from PIL import Image
import io

KY_COUNTIES = [
    'Adair', 'Allen', 'Anderson', 'Ballard', 'Barren', 'Bath', 'Bell', 'Boone',
    'Bourbon', 'Boyd', 'Boyle', 'Bracken', 'Breathitt', 'Breckinridge', 'Bullitt',
    'Butler', 'Caldwell', 'Calloway', 'Campbell', 'Carlisle', 'Carroll', 'Carter',
    'Casey', 'Christian', 'Clark', 'Clay', 'Clinton', 'Crittenden', 'Cumberland',
    'Daviess', 'Edmonson', 'Elliott', 'Estill', 'Fayette', 'Fleming', 'Floyd',
    'Franklin', 'Fulton', 'Gallatin', 'Garrard', 'Grant', 'Graves', 'Grayson',
    'Green', 'Greenup', 'Hancock', 'Hardin', 'Harlan', 'Harrison', 'Hart',
    'Henderson', 'Henry', 'Hickman', 'Hopkins', 'Jackson', 'Jefferson', 'Jessamine',
    'Johnson', 'Kenton', 'Knott', 'Knox', 'Larue', 'Laurel', 'Lawrence', 'Lee',
    'Leslie', 'Letcher', 'Lewis', 'Lincoln', 'Livingston', 'Logan', 'Lyon',
    'Madison', 'Magoffin', 'Marion', 'Marshall', 'Martin', 'Mason', 'Mccracken',
    'Mccreary', 'Mclean', 'Meade', 'Menifee', 'Mercer', 'Metcalfe', 'Monroe',
    'Montgomery', 'Morgan', 'Muhlenberg', 'Nelson', 'Nicholas', 'Ohio', 'Oldham',
    'Owen', 'Owsley', 'Pendleton', 'Perry', 'Pike', 'Powell', 'Pulaski',
    'Robertson', 'Rockcastle', 'Rowan', 'Russell', 'Scott', 'Shelby', 'Simpson',
    'Spencer', 'Taylor', 'Todd', 'Trigg', 'Trimble', 'Union', 'Warren',
    'Washington', 'Wayne', 'Webster', 'Whitley', 'Wolfe', 'Woodford'
]


def extract_with_ocr(pdf_path, pages_to_scan=3):
    """Extract text from first few pages using OCR to identify race."""
    print(f"Converting PDF pages to images (scanning first {pages_to_scan} pages)...")
    
    doc = fitz.open(pdf_path)
    all_text = ""
    
    for page_num in range(min(pages_to_scan, len(doc))):
        print(f"  OCR processing page {page_num + 1}...")
        page = doc[page_num]
        
        # Render page to image
        pix = page.get_pixmap(dpi=200)
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        
        # OCR the image
        text = pytesseract.image_to_string(img)
        all_text += text + "\n"
    
    doc.close()
    return all_text


def main():
    pdf_path = "data/off2010gen.pdf"
    
    if len(sys.argv) > 1:
        pdf_path = sys.argv[1]
    
    if not Path(pdf_path).exists():
        print(f"❌ File not found: {pdf_path}")
        sys.exit(1)
    
    print("="*70)
    print("OCR-based Kentucky Election Extraction - 2010")
    print("="*70)
    print(f"\nPDF: {Path(pdf_path).name}")
    print("NOTE: OCR of scanned PDFs may take several minutes...\n")
    
    # Extract first few pages to identify race
    text = extract_with_ocr(pdf_path, pages_to_scan=3)
    
    print("\n" + "="*70)
    print("EXTRACTED TEXT (First 1000 chars):")
    print("="*70)
    print(text[:1000])
    
    # Check what race this is
    text_lower = text.lower()
    if 'senator' in text_lower and 'united states' in text_lower:
        print("\n✓ Found: US Senate race")
    elif 'governor' in text_lower:
        print("\n✓ Found: Governor race")
    elif 'president' in text_lower:
        print("\n✓ Found: Presidential race")
    else:
        print("\n⚠ Race type unclear from OCR text")
    
    print("\n" + "="*70)
    print("Next Step: Identify candidates and create full extractor")
    print("="*70)


if __name__ == '__main__':
    main()
