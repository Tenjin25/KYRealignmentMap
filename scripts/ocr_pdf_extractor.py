"""
OCR-based PDF extraction for Kentucky election results.
Use this when PDFs are scanned images or standard extraction fails.

Requirements:
    pip install pytesseract pdf2image pillow
    
Also install Tesseract OCR:
    Windows: https://github.com/UB-Mannheim/tesseract/wiki
    Or: choco install tesseract

Usage:
    py scripts/ocr_pdf_extractor.py "data/2020 General Election.pdf"
"""

import sys
import re
from pathlib import Path
import pandas as pd
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

try:
    from pdf2image import convert_from_path
    import pytesseract
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False
    print("Error: OCR libraries not installed")
    print("Install with: pip install pytesseract pdf2image pillow")
    print("Also install Tesseract: https://github.com/UB-Mannheim/tesseract/wiki")
    sys.exit(1)

from pdf_utils import (
    KY_COUNTIES, clean_county_name, clean_votes, extract_party,
    get_election_date, validate_extraction_result, merge_duplicate_results,
    format_openelections_standard
)


def extract_with_ocr(pdf_path, start_page=1, end_page=None, dpi=300):
    """
    Extract text from PDF using OCR.
    
    Args:
        pdf_path: Path to PDF file
        start_page: First page to process (1-indexed)
        end_page: Last page to process (None = all pages)
        dpi: Resolution for image conversion (higher = better quality, slower)
    """
    logger.info(f"Converting PDF pages to images (DPI={dpi})...")
    
    try:
        # Convert PDF to images
        if end_page:
            images = convert_from_path(
                pdf_path, 
                dpi=dpi,
                first_page=start_page,
                last_page=end_page
            )
        else:
            images = convert_from_path(pdf_path, dpi=dpi, first_page=start_page)
        
        logger.info(f"  Converted {len(images)} pages")
        
        # Extract text from each image
        all_text = []
        for i, image in enumerate(images, start=start_page):
            logger.info(f"  OCR processing page {i}...")
            text = pytesseract.image_to_string(image)
            all_text.append(text)
        
        return "\n".join(all_text)
    
    except Exception as e:
        logger.error(f"OCR extraction failed: {e}")
        return ""


def parse_ocr_text(text):
    """
    Parse OCR text to extract election results.
    
    Looks for patterns like:
    County Name  Vote1  Vote2  Vote3
    """
    results = []
    
    lines = text.split('\n')
    
    for line in lines:
        # Look for lines that start with a county name followed by numbers
        # Pattern: County name, then multiple vote counts
        parts = line.split()
        
        if not parts:
            continue
        
        # Check if first word(s) could be a county
        potential_county = parts[0]
        
        # Try 2-word counties (e.g., "Mc Cracken")
        if len(parts) > 1 and parts[0].upper() in ['MC', 'LA']:
            potential_county = f"{parts[0]} {parts[1]}"
            remaining = parts[2:]
        else:
            remaining = parts[1:]
        
        # Check if it's a valid county
        county = clean_county_name(potential_county.replace('~', '').replace('|', ''))
        
        if not county:
            continue
        
        # Extract vote numbers from remaining text
        votes = []
        for part in remaining:
            # Clean common OCR errors
            part = part.replace('O', '0').replace('l', '1').replace('|', '1')
            
            if re.match(r'^[\d,]+$', part):
                vote_num = clean_votes(part)
                votes.append(vote_num)
        
        # Create result entries (we don't know candidate names from this method)
        for i, vote in enumerate(votes):
            results.append({
                'county': county,
                'candidate': f'Candidate {i+1}',
                'votes': vote
            })
    
    return results


def interactive_ocr_extraction(pdf_path):
    """
    Interactive OCR extraction - lets you specify pages and review results.
    """
    logger.info(f"\n{'='*70}")
    logger.info(f"Interactive OCR Extraction: {Path(pdf_path).name}")
    logger.info(f"{'='*70}\n")
    
    # Ask user which pages to process
    print("Which pages contain election results?")
    print("  Examples:")
    print("    1       - Just page 1")
    print("    1-5     - Pages 1 through 5")
    print("    all     - All pages (may be slow)")
    
    page_input = input("\nEnter pages: ").strip().lower()
    
    if page_input == 'all':
        start_page = 1
        end_page = None
    elif '-' in page_input:
        start, end = page_input.split('-')
        start_page = int(start)
        end_page = int(end)
    else:
        start_page = int(page_input)
        end_page = start_page
    
    # Extract with OCR
    text = extract_with_ocr(pdf_path, start_page, end_page)
    
    if not text:
        logger.error("No text extracted")
        return None
    
    # Save OCR text for review
    text_file = Path(pdf_path).stem + "_ocr.txt"
    with open(text_file, 'w', encoding='utf-8') as f:
        f.write(text)
    
    logger.info(f"\n✓ OCR text saved to: {text_file}")
    logger.info("  Review this file to see what was extracted")
    
    # Try to parse
    results = parse_ocr_text(text)
    
    if results:
        logger.info(f"\n  Parsed {len(results)} potential records")
        
        # Show preview
        df = pd.DataFrame(results)
        print("\nPreview of extracted data:")
        print(df.head(10))
        
        # Ask if user wants to save
        save = input("\nSave this extraction? (y/n): ").strip().lower()
        
        if save == 'y':
            return df
    else:
        logger.warning("Could not automatically parse OCR text")
        logger.info(f"Check {text_file} and extract data manually")
    
    return None


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('pdf_path', help='Path to PDF file')
    parser.add_argument('--pages', help='Pages to process (e.g., "1-10" or "all")')
    parser.add_argument('--dpi', type=int, default=300, help='Image resolution (default: 300)')
    parser.add_argument('--interactive', '-i', action='store_true', 
                       help='Interactive mode with prompts')
    
    args = parser.parse_args()
    
    if not OCR_AVAILABLE:
        logger.error("OCR libraries not available")
        return
    
    # Check Tesseract installation
    try:
        pytesseract.get_tesseract_version()
    except Exception:
        logger.error("Tesseract OCR not found!")
        logger.info("Install from: https://github.com/UB-Mannheim/tesseract/wiki")
        logger.info("Or with chocolatey: choco install tesseract")
        return
    
    if args.interactive:
        df = interactive_ocr_extraction(args.pdf_path)
    else:
        # Extract pages
        if args.pages:
            if args.pages.lower() == 'all':
                start_page, end_page = 1, None
            elif '-' in args.pages:
                start, end = args.pages.split('-')
                start_page, end_page = int(start), int(end)
            else:
                start_page = end_page = int(args.pages)
        else:
            start_page, end_page = 1, None
        
        text = extract_with_ocr(args.pdf_path, start_page, end_page, args.dpi)
        
        if text:
            # Save text
            text_file = Path(args.pdf_path).stem + "_ocr.txt"
            with open(text_file, 'w', encoding='utf-8') as f:
                f.write(text)
            logger.info(f"✓ OCR text saved to: {text_file}")
            
            # Try parsing
            results = parse_ocr_text(text)
            if results:
                df = pd.DataFrame(results)
                logger.info(f"Parsed {len(df)} records")
            else:
                df = None
        else:
            df = None
    
    if df is not None and not df.empty:
        # Save results
        year_match = re.search(r'(20\d{2})', Path(args.pdf_path).name)
        year = year_match.group(1) if year_match else "unknown"
        
        election_date = get_election_date(year)
        output_path = f"data/{election_date}__ky__general__county_ocr.csv"
        
        df = merge_duplicate_results(df)
        df = format_openelections_standard(df)
        df.to_csv(output_path, index=False)
        
        logger.info(f"\n✓ Saved to: {output_path}")
        logger.info("⚠️  Manual review required:")
        logger.info("  - Verify candidate names")
        logger.info("  - Check vote counts")
        logger.info("  - Fill in party/office information")


if __name__ == '__main__':
    main()
