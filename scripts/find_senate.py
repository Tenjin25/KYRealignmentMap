import pdfplumber
import sys

pdf_path = sys.argv[1] if len(sys.argv) > 1 else "data/2016 General Election Results.pdf"

pdf = pdfplumber.open(pdf_path)

print(f'Searching {pdf_path}...\n')

for i in range(len(pdf.pages)):
    text = pdf.pages[i].extract_text() or ''
    lower_text = text.lower()
    
    # Look for senate
    if 'senator' in lower_text or 'senate' in lower_text:
        lines = text.split('\n')
        senate_lines = [l.strip() for l in lines if 'senat' in l.lower() and l.strip()]
        
        if senate_lines:
            print(f'Page {i+1}:')
            for line in senate_lines[:8]:
                print(f'  {line}')
            
            # Show first data line
            for line in lines:
                if 'Adair' in line:
                    print(f'  First data: {line.strip()[:100]}')
                    break
            print()

pdf.close()
