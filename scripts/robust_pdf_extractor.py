"""
Robust PDF extractor for Kentucky election results.
Uses multiple extraction strategies with fallbacks and extensive validation.

Usage:
    python scripts/robust_pdf_extractor.py "data/2024 General Election.pdf"
    python scripts/robust_pdf_extractor.py --all  # Process all PDFs in data/
"""

import sys
import os
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import logging

try:
    import pandas as pd
    import tabula
    TABULA_AVAILABLE = True
except ImportError:
    TABULA_AVAILABLE = False
    print("Error: Required packages not installed")
    print("Install with: pip install pandas tabula-py")
    sys.exit(1)

# Optional OCR support
try:
    import pdfplumber
    import pikepdf
    PDFPLUMBER_AVAILABLE = True
except ImportError:
    PDFPLUMBER_AVAILABLE = False

try:
    import pytesseract
    from pdf2image import convert_from_path
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False

# Import our utilities
from pdf_utils import (
    extract_year, extract_party, extract_district, standardize_office,
    clean_candidate_name, clean_county_name, clean_votes,
    validate_extraction_result, merge_duplicate_results,
    format_openelections_standard, get_election_date,
    logger
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


class PDFExtractionStrategy:
    """Base class for PDF extraction strategies."""
    
    def __init__(self, name: str):
        self.name = name
    
    def extract(self, pdf_path: str) -> Tuple[pd.DataFrame, Dict]:
        """
        Extract data from PDF.
        Returns: (DataFrame, metadata dict)
        """
        raise NotImplementedError
    
    def __str__(self):
        return self.name


class TabulaLatticeStrategy(PDFExtractionStrategy):
    """Extract using tabula with lattice mode (works for tables with borders)."""
    
    def __init__(self):
        super().__init__("Tabula Lattice")
    
    def extract(self, pdf_path: str) -> Tuple[pd.DataFrame, Dict]:
        logger.info(f"Trying {self.name} extraction...")
        
        results = []
        metadata = {'strategy': self.name, 'tables_found': 0}
        
        try:
            tables = tabula.read_pdf(
                pdf_path,
                pages='all',
                multiple_tables=True,
                lattice=True,
                pandas_options={'header': None}
            )
            
            metadata['tables_found'] = len(tables) if tables else 0
            
            if not tables:
                return pd.DataFrame(), metadata
            
            for table_idx, df in enumerate(tables):
                if df is None or df.empty or df.shape[1] < 2:
                    continue
                
                logger.debug(f"  Table {table_idx + 1}: {df.shape[0]} rows × {df.shape[1]} cols")
                
                # Try to identify header rows
                header_row_idx = 0
                for i in range(min(5, len(df))):
                    row = df.iloc[i]
                    # Header likely contains text like "County" or candidate names
                    if any(str(val).lower() in ['county', 'candidate', 'precinct'] for val in row):
                        header_row_idx = i
                        break
                
                # Set header and get data rows
                if header_row_idx > 0:
                    df.columns = df.iloc[header_row_idx]
                    df = df.iloc[header_row_idx + 1:].reset_index(drop=True)
                else:
                    # Use first row as header
                    df.columns = df.iloc[0]
                    df = df.iloc[1:].reset_index(drop=True)
                
                # Process each row
                county_col = df.columns[0]
                
                for _, row in df.iterrows():
                    county = clean_county_name(row[county_col])
                    if not county:
                        continue
                    
                    # Process each candidate column
                    for col in df.columns[1:]:
                        candidate = clean_candidate_name(col)
                        if not candidate:
                            continue
                        
                        party = extract_party(col)
                        votes = clean_votes(row[col])
                        
                        results.append({
                            'county': county,
                            'candidate': candidate,
                            'party': party,
                            'votes': votes,
                            'office': '',
                            'district': ''
                        })
            
            logger.info(f"  Extracted {len(results)} records")
            return pd.DataFrame(results), metadata
            
        except Exception as e:
            logger.error(f"  {self.name} failed: {e}")
            return pd.DataFrame(), metadata


class TabulaStreamStrategy(PDFExtractionStrategy):
    """Extract using tabula with stream mode (works for tables without borders)."""
    
    def __init__(self):
        super().__init__("Tabula Stream")
    
    def extract(self, pdf_path: str) -> Tuple[pd.DataFrame, Dict]:
        logger.info(f"Trying {self.name} extraction...")
        
        results = []
        metadata = {'strategy': self.name, 'tables_found': 0}
        
        try:
            tables = tabula.read_pdf(
                pdf_path,
                pages='all',
                multiple_tables=True,
                stream=True,
                guess=False,
                pandas_options={'header': None}
            )
            
            metadata['tables_found'] = len(tables) if tables else 0
            
            if not tables:
                return pd.DataFrame(), metadata
            
            for table_idx, df in enumerate(tables):
                if df is None or df.empty or df.shape[1] < 2:
                    continue
                
                logger.debug(f"  Table {table_idx + 1}: {df.shape[0]} rows × {df.shape[1]} cols")
                
                # Similar processing as lattice strategy
                df.columns = df.iloc[0]
                df = df.iloc[1:].reset_index(drop=True)
                
                county_col = df.columns[0]
                
                for _, row in df.iterrows():
                    county = clean_county_name(row[county_col])
                    if not county:
                        continue
                    
                    for col in df.columns[1:]:
                        candidate = clean_candidate_name(col)
                        if not candidate:
                            continue
                        
                        party = extract_party(col)
                        votes = clean_votes(row[col])
                        
                        results.append({
                            'county': county,
                            'candidate': candidate,
                            'party': party,
                            'votes': votes,
                            'office': '',
                            'district': ''
                        })
            
            logger.info(f"  Extracted {len(results)} records")
            return pd.DataFrame(results), metadata
            
        except Exception as e:
            logger.error(f"  {self.name} failed: {e}")
            return pd.DataFrame(), metadata


class PDFPlumberStrategy(PDFExtractionStrategy):
    """Extract using pdfplumber (good for complex layouts)."""
    
    def __init__(self):
        super().__init__("PDFPlumber")
    
    def extract(self, pdf_path: str) -> Tuple[pd.DataFrame, Dict]:
        if not PDFPLUMBER_AVAILABLE:
            logger.warning(f"  {self.name} not available (missing pdfplumber/pikepdf)")
            return pd.DataFrame(), {'strategy': self.name, 'available': False}
        
        logger.info(f"Trying {self.name} extraction...")
        
        results = []
        metadata = {'strategy': self.name, 'tables_found': 0}
        
        try:
            # Use pikepdf to repair/decrypt PDF if needed
            import io
            with pikepdf.open(pdf_path) as p:
                b = io.BytesIO()
                p.save(b)
                b.seek(0)
                
                with pdfplumber.open(b) as pdf:
                    for page_num, page in enumerate(pdf.pages):
                        tables = page.extract_tables()
                        
                        if not tables:
                            continue
                        
                        metadata['tables_found'] += len(tables)
                        
                        for table in tables:
                            if not table or len(table) < 2:
                                continue
                            
                            # Convert to DataFrame
                            df = pd.DataFrame(table[1:], columns=table[0])
                            
                            if df.empty or df.shape[1] < 2:
                                continue
                            
                            county_col = df.columns[0]
                            
                            for _, row in df.iterrows():
                                county = clean_county_name(row[county_col])
                                if not county:
                                    continue
                                
                                for col in df.columns[1:]:
                                    candidate = clean_candidate_name(col)
                                    if not candidate:
                                        continue
                                    
                                    party = extract_party(col)
                                    votes = clean_votes(row[col])
                                    
                                    results.append({
                                        'county': county,
                                        'candidate': candidate,
                                        'party': party,
                                        'votes': votes,
                                        'office': '',
                                        'district': ''
                                    })
            
            logger.info(f"  Extracted {len(results)} records")
            return pd.DataFrame(results), metadata
            
        except Exception as e:
            logger.error(f"  {self.name} failed: {e}")
            return pd.DataFrame(), metadata


class TabulaGuessStrategy(PDFExtractionStrategy):
    """Extract using tabula with automatic detection."""
    
    def __init__(self):
        super().__init__("Tabula Auto")
    
    def extract(self, pdf_path: str) -> Tuple[pd.DataFrame, Dict]:
        logger.info(f"Trying {self.name} extraction...")
        
        results = []
        metadata = {'strategy': self.name, 'tables_found': 0}
        
        try:
            tables = tabula.read_pdf(
                pdf_path,
                pages='all',
                multiple_tables=True,
                guess=True
            )
            
            metadata['tables_found'] = len(tables) if tables else 0
            
            if not tables:
                return pd.DataFrame(), metadata
            
            for df in tables:
                if df is None or df.empty:
                    continue
                
                # Assume first column is county, rest are candidates
                county_col = df.columns[0]
                
                for _, row in df.iterrows():
                    county = clean_county_name(row[county_col])
                    if not county:
                        continue
                    
                    for col in df.columns[1:]:
                        candidate = clean_candidate_name(col)
                        if not candidate:
                            continue
                        
                        party = extract_party(col)
                        votes = clean_votes(row[col])
                        
                        results.append({
                            'county': county,
                            'candidate': candidate,
                            'party': party,
                            'votes': votes,
                            'office': '',
                            'district': ''
                        })
            
            logger.info(f"  Extracted {len(results)} records")
            return pd.DataFrame(results), metadata
            
        except Exception as e:
            logger.error(f"  {self.name} failed: {e}")
            return pd.DataFrame(), metadata


def extract_with_fallback(pdf_path: str) -> Tuple[pd.DataFrame, Dict]:
    """
    Try multiple extraction strategies with fallback.
    Returns the best result based on validation.
    """
    strategies = [
        TabulaLatticeStrategy(),
        TabulaStreamStrategy(),
        TabulaGuessStrategy(),
    ]
    
    # Add PDFPlumber if available
    if PDFPLUMBER_AVAILABLE:
        strategies.append(PDFPlumberStrategy())
    
    best_result = pd.DataFrame()
    best_metadata = {}
    best_score = 0
    
    for strategy in strategies:
        try:
            df, metadata = strategy.extract(pdf_path)
            
            if df.empty:
                continue
            
            # Validate the result
            is_valid, warnings = validate_extraction_result(df)
            
            # Calculate a quality score
            score = len(df)
            if is_valid:
                score *= 2  # Bonus for passing validation
            
            # Penalize for warnings
            score -= len(warnings) * 10
            
            logger.info(f"  {strategy.name}: {len(df)} records, score={score}")
            for warning in warnings:
                logger.warning(f"    {warning}")
            
            # Keep best result
            if score > best_score:
                best_score = score
                best_result = df
                best_metadata = metadata
                best_metadata['warnings'] = warnings
                best_metadata['score'] = score
        
        except Exception as e:
            logger.error(f"  {strategy.name} failed with exception: {e}")
            continue
    
    if best_result.empty:
        logger.error("All extraction strategies failed")
    else:
        logger.info(f"Best result: {best_metadata.get('strategy', 'Unknown')} with {len(best_result)} records")
    
    return best_result, best_metadata


def process_pdf(pdf_path: str, output_dir: str = 'data') -> Optional[Path]:
    """
    Process a single PDF file with robust extraction.
    
    Args:
        pdf_path: Path to PDF file
        output_dir: Directory to save output CSV
        
    Returns:
        Path to output file or None if failed
    """
    pdf_path = Path(pdf_path)
    
    if not pdf_path.exists():
        logger.error(f"File not found: {pdf_path}")
        return None
    
    logger.info(f"\n{'='*70}")
    logger.info(f"Processing: {pdf_path.name}")
    logger.info(f"{'='*70}")
    
    # Extract year from filename
    year = extract_year(pdf_path.name)
    if not year:
        logger.warning("Could not extract year from filename")
        year = "unknown"
    
    # Extract data with fallback strategies
    df, metadata = extract_with_fallback(str(pdf_path))
    
    if df.empty:
        logger.error("No data extracted from PDF")
        return None
    
    # Add year to dataframe if we have it
    if 'year' not in df.columns:
        df['year'] = year
    
    # Merge duplicates
    df = merge_duplicate_results(df)
    
    # Format to OpenElections standard
    df = format_openelections_standard(df, level='county')
    
    # Generate output filename
    election_date = get_election_date(year)
    output_filename = f"{election_date}__ky__general__county.csv"
    output_path = Path(output_dir) / output_filename
    
    # Ensure output directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Save to CSV
    df.to_csv(output_path, index=False)
    
    logger.info(f"\n✓ Success!")
    logger.info(f"  Output: {output_path}")
    logger.info(f"  Records: {len(df)}")
    logger.info(f"  Counties: {df['county'].nunique()}")
    logger.info(f"  Candidates: {df['candidate'].nunique()}")
    logger.info(f"  Total votes: {df['votes'].sum():,}")
    
    # Show preview
    if len(df) > 0:
        logger.info("\nPreview (first 5 rows):")
        print(df.head(5).to_string(index=False))
    
    # Show warnings if any
    if metadata.get('warnings'):
        logger.info("\nWarnings:")
        for warning in metadata['warnings']:
            logger.warning(f"  {warning}")
    
    return output_path


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Robust PDF extractor for Kentucky election results'
    )
    parser.add_argument(
        'pdf_path',
        nargs='?',
        help='Path to PDF file to process'
    )
    parser.add_argument(
        '--all',
        action='store_true',
        help='Process all PDFs in data/ directory'
    )
    parser.add_argument(
        '--output-dir',
        default='data',
        help='Output directory (default: data/)'
    )
    parser.add_argument(
        '--verbose',
        '-v',
        action='store_true',
        help='Enable verbose logging'
    )
    
    args = parser.parse_args()
    
    if args.verbose:
        logger.setLevel(logging.DEBUG)
    
    # Determine which files to process
    if args.all:
        data_dir = Path('data')
        pdf_files = list(data_dir.glob('*.pdf'))
        
        if not pdf_files:
            logger.error(f"No PDF files found in {data_dir}")
            return
        
        logger.info(f"Found {len(pdf_files)} PDF file(s) to process\n")
    elif args.pdf_path:
        pdf_files = [Path(args.pdf_path)]
    else:
        parser.print_help()
        return
    
    # Process each file
    success_count = 0
    for pdf_path in pdf_files:
        try:
            result = process_pdf(pdf_path, args.output_dir)
            if result:
                success_count += 1
        except Exception as e:
            logger.error(f"Failed to process {pdf_path.name}: {e}")
            continue
    
    # Summary
    logger.info(f"\n{'='*70}")
    logger.info(f"Completed: {success_count}/{len(pdf_files)} files processed successfully")
    logger.info(f"{'='*70}")


if __name__ == '__main__':
    main()
