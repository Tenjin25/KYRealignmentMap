"""
Extract 2022 KY U.S. Senate county totals from the certified image-only PDF via OCR.

Input:
  data/1.17.2023 Certified General Election Results.pdf

Output:
  data/20221108__ky__general__county.csv (U.S. Senate rows replaced)
"""

from pathlib import Path
import io
import re
import difflib
import pandas as pd
import fitz
import pytesseract
from PIL import Image


BASE = Path(__file__).resolve().parent.parent
PDF_PATH = BASE / "data" / "1.17.2023 Certified General Election Results.pdf"
COUNTY_LOOKUP = BASE / "data" / "county_name_lookup.csv"
OUT_CSV = BASE / "data" / "20221108__ky__general__county.csv"
TESSERACT_EXE = r"C:\Program Files\Tesseract-OCR\tesseract.exe"


def normalize_county_key(text: str) -> str:
    value = re.sub(r"[^A-Za-z0-9 .-]", "", str(text or ""))
    value = re.sub(r"\s+", " ", value).strip().upper()
    return value


def clean_num(token: str) -> int:
    t = str(token or "").strip()
    # OCR often uses O/o/°/C/l for 0/1.
    t = t.replace("O", "0").replace("o", "0").replace("°", "0")
    t = t.replace("I", "1").replace("l", "1").replace(")", "0").replace("(", "0")
    t = re.sub(r"[^0-9]", "", t)
    return int(t) if t else 0


def load_counties():
    df = pd.read_csv(COUNTY_LOOKUP, dtype=str).fillna("")
    counties = sorted(df["county_name"].dropna().astype(str).str.strip().unique())
    return counties


def parse_senate_pages() -> pd.DataFrame:
    pytesseract.pytesseract.tesseract_cmd = TESSERACT_EXE
    counties = load_counties()
    county_keys = {normalize_county_key(c): c for c in counties}
    extracted: dict[str, tuple[int, int, int, int]] = {}

    doc = fitz.open(PDF_PATH)
    # Senate county table spans pages 2..6 (1-indexed) in this certified PDF.
    senate_pages = [1, 2, 3, 4, 5]  # zero-indexed

    for p in senate_pages:
        page = doc.load_page(p)
        pix = page.get_pixmap(matrix=fitz.Matrix(2.5, 2.5), alpha=False)
        img = Image.open(io.BytesIO(pix.tobytes("png")))

        # Run two OCR passes; second pass helps recover lines missed in first.
        texts = [
            pytesseract.image_to_string(img, config="--oem 3 --psm 6"),
            pytesseract.image_to_string(img, config="--oem 3 --psm 4"),
        ]

        for text in texts:
            for raw in text.splitlines():
                line = re.sub(r"\s+", " ", raw).strip()
                if not line:
                    continue
                if "Total Votes" in line or "Totalvotes" in line:
                    continue

                tokens = line.split()
                numeric_idx = []
                for i, tok in enumerate(tokens):
                    if re.search(r"\d", tok):
                        numeric_idx.append(i)
                if len(numeric_idx) < 2:
                    continue

                first_num_idx = numeric_idx[0]
                county_guess = " ".join(tokens[:first_num_idx]).strip()
                county_guess = county_guess.replace("Peny", "Perry")
                county_guess = re.sub(r"^[^A-Za-z]+", "", county_guess)
                county_guess = re.sub(r"[^A-Za-z .'\-]+$", "", county_guess)
                if not county_guess:
                    continue

                county_key = normalize_county_key(county_guess)
                county = county_keys.get(county_key)
                if not county:
                    close = difflib.get_close_matches(county_guess, counties, n=1, cutoff=0.78)
                    county = close[0] if close else None
                if not county:
                    continue

                nums = [clean_num(tokens[i]) for i in numeric_idx[:4]]
                if len(nums) < 2:
                    continue
                rep = nums[0]
                dem = nums[1]
                w1 = nums[2] if len(nums) > 2 else 0
                w2 = nums[3] if len(nums) > 3 else 0
                # Keep the version with the larger 2-party sum if OCR differs.
                cur = extracted.get(county)
                if cur is None or (rep + dem) > (cur[0] + cur[1]):
                    extracted[county] = (rep, dem, w1, w2)

    if len(extracted) < 110:
        raise RuntimeError(f"OCR parse too sparse: only {len(extracted)} counties extracted")

    # Fill any missing counties with zeros (rare OCR misses), but keep explicit record.
    missing = [c for c in counties if c not in extracted]
    if missing:
        print(f"Warning: missing counties after OCR parse: {missing}")
        for c in missing:
            extracted[c] = (0, 0, 0, 0)

    rows = []
    for county in counties:
        rep, dem, w1, w2 = extracted[county]
        rows.extend(
            [
                {
                    "year": 2022,
                    "county": county,
                    "office": "United States Senator",
                    "district": "",
                    "candidate": "Rand PAUL",
                    "party": "REP",
                    "votes": rep,
                },
                {
                    "year": 2022,
                    "county": county,
                    "office": "United States Senator",
                    "district": "",
                    "candidate": "Charles BOOKER",
                    "party": "DEM",
                    "votes": dem,
                },
                {
                    "year": 2022,
                    "county": county,
                    "office": "United States Senator",
                    "district": "",
                    "candidate": "Charles Lee THOMASON",
                    "party": "W",
                    "votes": w1,
                },
                {
                    "year": 2022,
                    "county": county,
                    "office": "United States Senator",
                    "district": "",
                    "candidate": "Billy Ray WILSON",
                    "party": "W",
                    "votes": w2,
                },
            ]
        )

    return pd.DataFrame(rows)


def merge_into_county_csv(senate_df: pd.DataFrame):
    if OUT_CSV.exists():
        base = pd.read_csv(OUT_CSV, dtype=str).fillna("")
    else:
        base = pd.DataFrame()

    if not base.empty:
        for col in ["year", "county", "office", "district", "candidate", "party", "votes"]:
            if col not in base.columns:
                base[col] = ""

        mask_senate = (
            base["year"].astype(str).str.strip().eq("2022")
            & base["office"].astype(str).str.contains("senator", case=False, na=False)
        )
        base = base[~mask_senate].copy()

    senate_df = senate_df.copy()
    for col in [
        "election_day",
        "absentee",
        "av_counting_boards",
        "early_voting",
        "mail",
        "provisional",
        "pre_process_absentee",
    ]:
        senate_df[col] = ""

    ordered = [
        "year",
        "county",
        "office",
        "district",
        "candidate",
        "party",
        "votes",
        "election_day",
        "absentee",
        "av_counting_boards",
        "early_voting",
        "mail",
        "provisional",
        "pre_process_absentee",
    ]

    for col in ordered:
        if col not in base.columns:
            base[col] = ""

    merged = pd.concat([base[ordered], senate_df[ordered]], ignore_index=True)
    merged["votes"] = pd.to_numeric(merged["votes"], errors="coerce").fillna(0).astype(int)
    merged.to_csv(OUT_CSV, index=False)
    print(f"Updated {OUT_CSV} with OCR-certified 2022 Senate rows ({len(senate_df)} rows).")


def main():
    if not PDF_PATH.exists():
        raise SystemExit(f"Missing PDF: {PDF_PATH}")
    if not Path(TESSERACT_EXE).exists():
        raise SystemExit(f"Tesseract not found: {TESSERACT_EXE}")

    senate_df = parse_senate_pages()
    print(
        "Extracted counties:",
        senate_df["county"].nunique(),
        "rows:",
        len(senate_df),
    )
    merge_into_county_csv(senate_df)


if __name__ == "__main__":
    main()
