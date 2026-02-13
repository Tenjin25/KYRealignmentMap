import pdfplumber
import sys

pdf_path = sys.argv[1] if len(sys.argv) > 1 else "data/2024 General Election Certification as Amended on December 9th 2024.pdf"

pdf = pdfplumber.open(pdf_path)
print(f'Total pages: {len(pdf.pages)}')
print('\nRaces found:\n')

races_found = []
for i in range(len(pdf.pages)):
    text = pdf.pages[i].extract_text() or ''
    lines = text.split('\n')
    
    # Look for race titles in first 15 lines
    for line in lines[:15]:
        line_lower = line.lower().strip()
        
        # Check for specific offices
        if 'president and vice president' in line_lower:
            races_found.append(f'Page {i+1}: President and Vice President')
            break
        elif line_lower == 'governor':
            races_found.append(f'Page {i+1}: Governor')
            break
        elif 'attorney general' in line_lower and len(line) < 50:
            races_found.append(f'Page {i+1}: Attorney General')
            break
        elif 'secretary of state' in line_lower and len(line) < 50:
            races_found.append(f'Page {i+1}: Secretary of State')
            break
        elif 'state treasurer' in line_lower or line_lower == 'treasurer':
            races_found.append(f'Page {i+1}: State Treasurer')
            break
        elif 'auditor of public accounts' in line_lower or line_lower == 'auditor':
            races_found.append(f'Page {i+1}: Auditor of Public Accounts')
            break
        elif 'commissioner of agriculture' in line_lower:
            races_found.append(f'Page {i+1}: Commissioner of Agriculture')
            break
        elif 'united states senator' in line_lower:
            races_found.append(f'Page {i+1}: U.S. Senate')
            break
        elif 'united states representative' in line_lower:
            races_found.append(f'Page {i+1}: U.S. House')
            break

# Print unique races
for race in dict.fromkeys(races_found):
    print(race)

pdf.close()
