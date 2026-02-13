"""
OCR extraction for scanned Kentucky election PDFs.
Requires Tesseract OCR engine to be installed.
"""

import sys
import os
from pathlib import Path
import pandas as pd
from PIL import Image
import logging

# Check if pytesseract is available
try:
    import pytesseract
    from pdf2image import convert_from_path
except ImportError:
    print("Error: Required OCR packages not installed")
    print("Install with: pip install pytesseract pdf2image pillow")
    sys.exit(1)

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

# Kentucky counties for validation
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


def check_tesseract_installation():
    """Check if Tesseract OCR is installed."""
    try:
        tesseract_path = pytesseract.pytesseract.Tesseract().executable
        return True, tesseract_path
    except Exception:
        return False, None


def extract_text_from_pdf_ocr(pdf_path, pages=None, dpi=150):
    """
    Extract text from PDF using OCR.
    
    Args:
        pdf_path: Path to PDF file
        pages: List of page numbers to process (1-indexed), or None for all
        dpi: DPI for image conversion (higher = better quality, slower)
    
    Returns:
        Dictionary mapping page number to extracted text
    """
    logger.info(f"Converting PDF to images: {pdf_path}")
    
    try:
        # Convert PDF to images
        images = convert_from_path(pdf_path, dpi=dpi)
        
        if pages is not None:
            # Filter to requested pages
            images = [images[p-1] for p in pages if p <= len(images)]
        
        logger.info(f"Processing {len(images)} pages with OCR...")
        
        page_text = {}
        for i, image in enumerate(images, 1):
            logger.info(f"  OCR page {i}...")
            try:
                text = pytesseract.image_to_string(image)
                page_text[i] = text
            except Exception as e:
                logger.warning(f"  Error on page {i}: {e}")
                page_text[i] = ""
        
        return page_text
        
    except Exception as e:
        logger.error(f"Error converting PDF: {e}")
        raise


def extract_county_votes_from_text(text):
    """Extract county names and vote numbers from OCR'd text."""
    import re
    
    results = []
    lines = text.split('\n')
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        # Look for lines starting with county names
        for county in KY_COUNTIES:
            if line.lower().startswith(county.lower()):
                # Extract numbers from the line
                numbers = re.findall(r'\d+(?:,\d{3})*|\d+', line)
                
                if numbers:
                    votes = []
                    for num_str in numbers:
                        try:
                            votes.append(int(num_str.replace(',', '')))
                        except:
                            pass
                    
                    if votes:
                        results.append({
                            'county': county,
                            'line': line,
                            'votes': votes
                        })
                break
    
    return results


def main():
    """Main OCR extraction workflow."""
    
    # Check if Tesseract is installed
    is_installed, path = check_tesseract_installation()
    
    if not is_installed:
        print("\n" + "=" * 80)
        print("ERROR: Tesseract OCR is not installed")
        print("=" * 80)
        print("""
TO INSTALL TESSERACT ON WINDOWS:

Option 1: Download Installer
  1. Go to: https://github.com/UB-Mannheim/tesseract/wiki
  2. Click on latest.yml or releases
  3. Download: tesseract-ocr-w64-setup-v5.4.0.exe
  4. Run installer (default path is fine)
  5. Verify: tesseract --version

Option 2: Chocolatey (if you have admin rights)
  choco install tesseract

Option 3: Scoop
  scoop install tesseract

After installation, run this script again.
        """)
        return
    
    print(f"✓ Tesseract found at: {path}")
    print()
    
    # Get PDF file
    if len(sys.argv) < 2:
        print("Usage: python ocr_ky_extractor.py <pdf_path> [--pages 1-10] [--dpi 150]")
        print()
        print("Examples:")
        print("  python ocr_ky_extractor.py 'data/2019 General Certified Results.pdf'")
        print("  python ocr_ky_extractor.py 'data/2022.pdf' --pages 1-5")
        print("  python ocr_ky_extractor.py 'data/2022.pdf' --dpi 300")
        return
    
    pdf_path = Path(sys.argv[1])
    
    if not pdf_path.exists():
        print(f"Error: PDF not found: {pdf_path}")
        return
    
    # Parse options
    pages = None
    dpi = 150
    
    for i, arg in enumerate(sys.argv[2:]):
        if arg == '--pages' and i + 3 < len(sys.argv):
            page_spec = sys.argv[i + 3]
            if '-' in page_spec:
                start, end = map(int, page_spec.split('-'))
                pages = list(range(start, end + 1))
        elif arg == '--dpi' and i + 3 < len(sys.argv):
            dpi = int(sys.argv[i + 3])
    
    print(f"Extracting from: {pdf_path.name}")
    print(f"DPI: {dpi}")
    if pages:
        print(f"Pages: {pages}")
    print()
    
    # Extract text
    try:
        page_text = extract_text_from_pdf_ocr(str(pdf_path), pages=pages, dpi=dpi)
        
        # Combine all pages
        all_text = '\n'.join(page_text.values())
        
        # Extract counties and votes
        print("\nExtracting counties and votes...")
        results = extract_county_votes_from_text(all_text)
        
        print(f"Found {len(results)} county entries")
        
        for i, result in enumerate(results[:10]):
            print(f"  {result['county']}: {result['votes']}")
        
        if len(results) > 10:
            print(f"  ... and {len(results) - 10} more")
        
        print("\n✓ OCR extraction complete")
        print("Note: OCR results may contain errors. Manual review recommended.")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
