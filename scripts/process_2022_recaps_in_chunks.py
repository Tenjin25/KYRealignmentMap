"""
Process 2022 SOS recap county PDFs in chunks and merge into a statewide county CSV.

Usage examples:
  py scripts/process_2022_recaps_in_chunks.py --start 0 --count 20
  py scripts/process_2022_recaps_in_chunks.py --start 20 --count 20
  py scripts/process_2022_recaps_in_chunks.py --merge-only
"""

from pathlib import Path
import argparse
import pandas as pd

from convert_pdf_to_openelections import (
    parse_sos_precinct_recap_pdf,
    canonicalize_county_name,
)


BASE_DIR = Path(__file__).resolve().parent.parent
RECAP_DIR = BASE_DIR / "data" / "2022_recaps"
CHUNK_DIR = BASE_DIR / "data" / "2022_recaps_chunks"
OUT_FILE = BASE_DIR / "data" / "20221108__ky__general__county.csv"
ELECTION_DATE = "20221108"


def list_pdfs():
    return sorted(RECAP_DIR.glob("*.pdf"), key=lambda p: p.name.lower())


def process_chunk(start: int, count: int):
    CHUNK_DIR.mkdir(parents=True, exist_ok=True)
    pdfs = list_pdfs()
    end = min(start + count, len(pdfs))
    if start >= len(pdfs):
        print(f"No files to process: start={start}, total={len(pdfs)}")
        return

    rows = []
    for idx, pdf in enumerate(pdfs[start:end], start=start):
        print(f"[{idx+1}/{len(pdfs)}] {pdf.name}")
        df = parse_sos_precinct_recap_pdf(str(pdf), ELECTION_DATE)
        if df.empty:
            continue
        df["county"] = df["county"].map(canonicalize_county_name)
        rows.append(df)

    if not rows:
        print("No rows extracted in this chunk.")
        return

    out = pd.concat(rows, ignore_index=True)
    out["votes"] = pd.to_numeric(out["votes"], errors="coerce").fillna(0).astype(int)
    out = (
        out.groupby(
            ["year", "county", "office", "district", "candidate", "party"],
            as_index=False,
            dropna=False,
        )["votes"]
        .sum()
    )

    chunk_file = CHUNK_DIR / f"chunk_{start:03d}_{end:03d}.csv"
    out.to_csv(chunk_file, index=False)
    print(f"Created {chunk_file} ({len(out)} rows)")


def merge_chunks():
    chunk_files = sorted(CHUNK_DIR.glob("chunk_*.csv"))
    if not chunk_files:
        raise SystemExit("No chunk CSV files found. Process at least one chunk first.")

    frames = [pd.read_csv(p, dtype={"district": "string"}).fillna("") for p in chunk_files]
    merged = pd.concat(frames, ignore_index=True)
    merged["votes"] = pd.to_numeric(merged["votes"], errors="coerce").fillna(0).astype(int)
    merged["year"] = 2022
    merged["county"] = merged["county"].map(canonicalize_county_name)

    merged = (
        merged.groupby(
            ["year", "county", "office", "district", "candidate", "party"],
            as_index=False,
            dropna=False,
        )["votes"]
        .sum()
    )

    for col in [
        "election_day",
        "absentee",
        "av_counting_boards",
        "early_voting",
        "mail",
        "provisional",
        "pre_process_absentee",
    ]:
        merged[col] = ""

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
    merged = merged[ordered].sort_values(["county", "office", "candidate", "party"])
    OUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    merged.to_csv(OUT_FILE, index=False)
    print(f"Created {OUT_FILE} ({len(merged)} rows) from {len(chunk_files)} chunks")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--start", type=int, default=0)
    parser.add_argument("--count", type=int, default=20)
    parser.add_argument("--merge-only", action="store_true")
    args = parser.parse_args()

    if args.merge_only:
        merge_chunks()
    else:
        process_chunk(args.start, args.count)


if __name__ == "__main__":
    main()
