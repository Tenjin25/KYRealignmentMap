import pdfplumber

pdf = pdfplumber.open('data/Certification of Election Results for 2023 General Election Final.pdf')

races = {
    'Governor': 1,
    'Secretary of State': 8, 
    'Attorney General': 14,
    'Auditor': 20,
    'Treasurer': 26,
    'Ag Commissioner': 32
}

for race, page_num in races.items():
    text = pdf.pages[page_num].extract_text()
    lines = text.split('\n')
    
    print(f'\n=== {race} (Page {page_num+1}) ===')
    for line in lines[:15]:
        print(line)
    print()
    
    # Show first data line
    for line in lines:
        if 'Adair' in line:
            print(f'Data format: {line}')
            break

pdf.close()
