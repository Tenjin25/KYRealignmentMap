import pdfplumber

pdf = pdfplumber.open('data/2015 General Election Results.pdf')

# Pages based on list_races output
races = {
    'Governor': 1,
    'Secretary of State': 7,
    'Attorney General': 12,
    'Auditor': 17,
    'Treasurer': 22,
    'Ag Commissioner': 27
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
            print(f'Data: {line}')
            break

pdf.close()
