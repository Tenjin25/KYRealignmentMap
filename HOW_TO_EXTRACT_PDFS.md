# How to Extract Kentucky Election PDFs - The Working Method

## The Problem
Kentucky PDFs have tables where candidates are COLUMNS and counties are ROWS. The columns are tightly spaced with no borders, so automated tools can't figure out where one candidate's votes end and another's begin.

## The Solution
Use `ky_text_extractor.py` - it reads the raw text line by line and extracts numbers in order. **You just need to tell it the candidate names in the correct order.**

## Step-by-Step Instructions

### 1. Open Your PDF
Open the PDF you want to extract in a PDF viewer (Adobe, browser, etc.)

### 2. Look at the Column Headers
Read the candidate names from LEFT to RIGHT across the page. Write them down.

### 3. Run the Extractor
```powershell
py scripts\ky_text_extractor.py "data\2024 General Election.pdf"
```

### 4. Enter the Candidates
The script will ask for each candidate. Enter them in the EXACT order they appear left to right.

Example for 2024 Presidential:
```
Candidate #1:
  Name: Donald Trump
  Party: REP
  Office [President]: President

Candidate #2:
  Name: Kamala Harris
  Party: DEM
  Office [President]: President

Candidate #3:
  Name: Robert Kennedy Jr
  Party: IND
  Office [President]: President

(etc... press Enter with blank name when done)
```

### 5. Check the Output
The script saves to `data/YYYYMMDD__ky__general__county.csv` and shows you:
- How many counties extracted
- Total votes
- Preview of data

## Example

```powershell
# For 2024 General
py scripts\ky_text_extractor.py "data\2024 General Election Certification as Amended on December 9th 2024.pdf"

# For 2022 General  
py scripts\ky_text_extractor.py "data\2022 Certified General Election Results.pdf"
```

## Common Party Abbreviations
- REP = Republican
- DEM = Democratic  
- LIB = Libertarian
- IND = Independent
- GRN = Green
- CON = Constitution
- WI = Write-In

## Tips

1. **Order matters!** Candidates must be entered in the same order as the PDF columns
2. **Count carefully** - make sure you don't skip a column
3. **Check the preview** - if numbers look wrong, you may have entered candidates in wrong order
4. **Minor candidates** - even candidates with few votes need to be entered if they have a column

## What Gets Extracted

- ✅ All 120 Kentucky counties
- ✅ Vote totals for each candidate in each county
- ✅ Correctly formatted for OpenElections

## If Something Goes Wrong

**Problem**: Wrong vote totals
**Solution**: You probably entered candidates in wrong order. Check the PDF column order again.

**Problem**: Not all counties extracted
**Solution**: Some pages might have different formatting. Check the output to see which counties are missing.

**Problem**: Too many/few candidates
**Solution**: Count the columns in the PDF carefully. Include ALL candidates even if some have zero votes.

## Time Required

- Looking at PDF and writing down candidates: 2 minutes
- Running script and entering names: 3 minutes  
- Checking output: 1 minute
- **Total: ~5-6 minutes per PDF**

Much faster than:
- ❌ Trying to fix automated extraction: hours
- ❌ Manual data entry: 2-3 hours
- ❌ Fighting with complex scripts: frustrating

##Why This Works

The Kentucky PDFs are laid out as text like this:
```
Adair 7,643 1,257 48 13 7 3 2 1 0 0 0
Allen 7,824 1,505 57 14 16 2 0 0 0 0 0
...
```

The script:
1. Finds lines starting with county names
2. Extracts all numbers from that line (in order)
3. Matches each number to the candidate you specified (in order)
4. Creates properly formatted CSV

Simple and effective!
