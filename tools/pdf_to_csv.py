import pdfplumber
import tabula
import pandas as pd
import os
import re
import pikepdf
import io

def clean_value(val):
    if val is None:
        return 0
    # Remove commas and non-numeric chars except decimals
    cleaned = re.sub(r'[^\d.]', '', str(val))
    try:
        return int(float(cleaned)) if cleaned else 0
    except ValueError:
        return 0

def parse_ky_pdf_tabula(pdf_path):
    """Try to extract tables using tabula-py. Return DataFrame or empty DataFrame on failure."""
    all_data = []
    year_match = re.search(r'(\d{4})', os.path.basename(pdf_path))
    year = year_match.group(1) if year_match else ""
    print(f"[tabula] Processing {pdf_path} (Year: {year})...")
    try:
        import tabula
        import numpy as np
        tables = tabula.read_pdf(pdf_path, pages='all', multiple_tables=True, lattice=True)
        for table in tables:
            if table is None or table.empty or table.shape[1] < 2:
                continue
            # Try to detect multi-row header: look for first few rows with many NaNs or non-numeric values
            header_rows = []
            data_start_idx = 0
            for i in range(min(3, len(table))):
                row = table.iloc[i]
                # Heuristic: header rows have few numeric values
                if sum([str(x).replace('.', '', 1).isdigit() for x in row]) < len(row) // 2:
                    header_rows.append(row)
                    data_start_idx = i + 1
                else:
                    break
            # Build column names from header rows
            if header_rows:
                colnames = []
                for col in range(table.shape[1]):
                    parts = [str(header_rows[r][col]).strip() for r in range(len(header_rows)) if str(header_rows[r][col]).strip() and str(header_rows[r][col]).lower() != 'nan']
                    colnames.append(' '.join(parts))
                table.columns = colnames
                table = table.iloc[data_start_idx:]
            header = table.columns.tolist()
            for idx, row in table.iterrows():
                county = str(row[header[0]]).strip()
                if not county or county.lower() in ['total', 'total votes', 'votes', 'yes', 'no']:
                    continue
                for col in header[1:]:
                    cand_name = str(col).strip()
                    party = ''
                    # Try to extract party from candidate name if present in parentheses or after dash
                    party_match = re.search(r'\(([^)]+)\)', cand_name)
                    if party_match:
                        party = party_match.group(1)
                        cand_name = cand_name.replace(f'({party})', '').strip()
                    elif '-' in cand_name:
                        parts = cand_name.split('-')
                        if len(parts) == 2:
                            cand_name, party = parts[0].strip(), parts[1].strip()
                    votes = row[col]
                    try:
                        votes = int(str(votes).replace(',', '').strip()) if votes and str(votes).strip() else 0
                    except Exception:
                        votes = 0
                    all_data.append({
                        'county': county,
                        'office': '',
                        'district': '',
                        'candidate': cand_name,
                        'party': party,
                        'votes': votes,
                        'year': year
                    })
    except Exception as e:
        print(f"[tabula] Error processing {pdf_path}: {e}")
    return pd.DataFrame(all_data)

def parse_ky_pdf(pdf_path):
    """Parse KY election PDFs using pdfplumber with pikepdf for repair."""
    all_data = []
    current_office = ""
    current_district = ""
    
    # Extract year from filename if possible
    year_match = re.search(r'(\d{4})', os.path.basename(pdf_path))
    year = year_match.group(1) if year_match else ""

    print(f"Processing {pdf_path} (Year: {year})...")

    # Use pikepdf to "repair" or decrypt the PDF in memory
    try:
        with pikepdf.open(pdf_path) as p:
            b = io.BytesIO()
            p.save(b)
            b.seek(0)
            
            with pdfplumber.open(b) as pdf:
                for page in pdf.pages:
                    text = page.extract_text()
                    if not text:
                        continue
                    
                    lines = text.split('\n')
                    
                    # Detect Office/District from text
                    for i, line in enumerate(lines):
                        if "For the office of" in line:
                            if i + 1 < len(lines):
                                current_office = lines[i+1].strip()
                            continue
                        
                        # Look for district patterns
                        dist_match = re.search(r'(\d+)(?:st|nd|rd|th)\s+(Congressional|Senatorial|Representative|Judicial)\s+District', line, re.IGNORECASE)
                        if dist_match:
                            current_district = dist_match.group(1)
                        elif "Congressional District" in line or "Senatorial District" in line or "Representative District" in line:
                            # Try to find a number in this line
                            num_match = re.search(r'(\d+)', line)
                            if num_match:
                                current_district = num_match.group(1)

                    tables = page.extract_tables()
                    if tables:
                        for table in tables:
                            if not table or len(table) < 2:
                                continue
                            
                            # Find row where county data starts
                            county_start_idx = -1
                            for i, row in enumerate(table):
                                if not row or len(row) < 2: continue
                                # Check if second col has a number and first col looks like a county
                                if row[1] and re.search(r'\d', str(row[1])):
                                    if str(row[0]).lower() not in ['total', 'total votes', 'votes', 'yes', 'no']:
                                        county_start_idx = i
                                        break
                            
                            if county_start_idx == -1:
                                continue
                            
                            # Extract candidates and parties from headers
                            header_rows = table[:county_start_idx]
                            num_cols = len(table[0])
                            candidates = []
                            parties = []
                            
                            party_keywords = ['REP', 'DEM', 'LIB', 'IND', 'GRN', 'CON', 'REF', 'Republican', 'Democratic', 'Libertarian']
                            
                            for c in range(1, num_cols):
                                col_header = " ".join([str(header[c]) for header in header_rows if header and c < len(header) and header[c]]).strip()
                                
                                party = ""
                                cand_name = col_header if col_header else f"Candidate_{c}"
                                
                                # Try to find party in header
                                for p_key in party_keywords:
                                    if p_key in col_header:
                                        party = p_key
                                        # Simple cleanup
                                        cand_name = col_header.replace(p_key, "").replace("Party", "").strip()
                                        break
                                
                                candidates.append(cand_name)
                                parties.append(party)
                            
                            for row in table[county_start_idx:]:
                                if not row or not row[0]: continue
                                county = str(row[0]).strip()
                                if county.lower() in ['total', 'total votes', 'votes']:
                                    continue
                                    
                                for i, (cand, party) in enumerate(zip(candidates, parties)):
                                    if i + 1 < len(row):
                                        votes = clean_value(row[i+1])
                                        if votes == 0 and not row[i+1]: continue
                                        
                                        all_data.append({
                                            'county': county,
                                            'office': current_office,
                                            'district': current_district,
                                            'candidate': cand,
                                            'party': party,
                                            'votes': votes,
                                            'year': year
                                        })
    except Exception as e:
        print(f"Error processing {pdf_path}: {e}")
                            
    return pd.DataFrame(all_data)

def format_openelections(df):
    if df.empty:
        return df

    # Target columns for county-level output (matching precinct CSV minus 'precinct')
    cols = [
        'county', 'office', 'district', 'candidate', 'party', 'votes',
        'election_day', 'absentee', 'av_counting_boards', 'early_voting', 'mail', 'provisional', 'pre_process_absentee'
    ]

    # Ensure all columns exist
    for col in cols:
        if col not in df.columns:
            df[col] = ""

    # Ensure 'year' column is filled with a single value if possible
    year_val = None
    if 'year' in df.columns:
        # Try to get the most common non-empty year value
        year_series = df['year'].replace('', pd.NA).dropna()
        if not year_series.empty:
            year_val = str(year_series.mode()[0])
        else:
            year_val = ''
        df['year'] = df['year'].replace('', year_val)
    else:
        year_val = ''
        df['year'] = year_val

    # Aggregate votes by county, office, district, candidate, party, year
    group_cols = ['county', 'office', 'district', 'candidate', 'party', 'year']
    df['votes'] = pd.to_numeric(df['votes'], errors='coerce').fillna(0).astype(int)
    agg_df = df.groupby(group_cols, dropna=False, as_index=False).agg({'votes': 'sum'})

    # Add blank columns for vote types
    for col in ['election_day', 'absentee', 'av_counting_boards', 'early_voting', 'mail', 'provisional', 'pre_process_absentee']:
        agg_df[col] = ""

    # Reorder columns
    return agg_df[cols], year_val

if __name__ == "__main__":
    import sys
    
    data_dir = "data"
    
    # If a specific PDF path is provided as argument, process only that file
    if len(sys.argv) > 1:
        files = [sys.argv[1]]
        # Extract just the filename if full path given
        files = [os.path.basename(f) if os.path.sep in f else f for f in files]
    else:
        # Otherwise process all PDFs in data directory
        files = [f for f in os.listdir(data_dir) if f.lower().endswith('.pdf')]

    # Election date mapping (first Tuesday after first Monday in November)
    election_dates = {
        '2010': '20101102',
        '2011': '20111108',
        '2012': '20121106',
        '2014': '20141104',
        '2015': '20151103',
        '2016': '20161108',
        '2019': '20191105',
        '2020': '20201103',
        '2022': '20221108',
        '2023': '20231107',
        '2024': '20241105',
    }

    for filename in files:
        pdf_path = os.path.join(data_dir, filename) if data_dir not in filename else filename
        
        # Try tabula first for better candidate extraction
        results = parse_ky_pdf_tabula(pdf_path)
        if results.empty:
            # Fallback to original method if tabula fails
            results = parse_ky_pdf(pdf_path)

        if not results.empty:
            oe_results, year_val = format_openelections(results)

            # Use extracted year for output filename with proper election date
            year = year_val if year_val else "unknown"
            election_date = election_dates.get(year, f"{year}1106")  # Default to Nov 6 if not in mapping
            output_name = f"{election_date}__ky__general__county.csv"
            output_path = os.path.join(data_dir, output_name)

            oe_results.to_csv(output_path, index=False)
            print(f"Saved {len(oe_results)} rows to {output_path}")
        else:
            print(f"No data found in {filename}")
