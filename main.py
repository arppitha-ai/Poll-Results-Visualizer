"""Run the full pipeline:  data -> clean -> analyse -> charts -> insights.

Usage:
    python main.py                         # synthetic data + everything
    python main.py --input my_poll.csv     # your own CSV (e.g. Google Forms export)
"""
import argparse

import pandas as pd

from src import analysis as A
from src import config as C
from src.cleaning import clean_poll_data
from src.generate_data import generate_poll_data
from src.insights import generate_insights, save_report
from src.visualize import save_all


def main():
    ap = argparse.ArgumentParser(description="Poll Results Visualizer")
    ap.add_argument("--input", help="path to a raw poll CSV (skips data generation)")
    ap.add_argument("--n", type=int, default=600, help="synthetic respondents")
    ap.add_argument("--seed", type=int, default=42)
    args = ap.parse_args()
    C.DATA_DIR.mkdir(exist_ok=True)
    C.OUTPUT_DIR.mkdir(exist_ok=True)

    if args.input:
        raw = pd.read_csv(args.input)
        print(f"[1/6] Loaded {len(raw)} rows from {args.input}")
    else:
        raw = generate_poll_data(args.n, args.seed)
        raw.to_csv(C.RAW_CSV, index=False)
        print(f"[1/6] Generated {len(raw)} synthetic rows -> {C.RAW_CSV}")
    print(raw.head(), "\n")

    df, log = clean_poll_data(raw)
    df.to_csv(C.CLEAN_CSV, index=False)
    print("[2/6] Cleaning log:", log, f"\n      saved -> {C.CLEAN_CSV}\n")

    vs = A.vote_share(df)
    vs.to_csv(C.OUTPUT_DIR / "vote_share.csv")
    A.crosstab_pct(df, C.REGION).to_csv(C.OUTPUT_DIR / "region_vs_option_pct.csv")
    A.crosstab_pct(df, C.AGE).to_csv(C.OUTPUT_DIR / "age_vs_option_pct.csv")
    A.rating_by(df, C.TOOL).to_csv(C.OUTPUT_DIR / "rating_by_option.csv")
    print("[3/6] Vote share summary:\n", vs, "\n")
    print("      Leader by region:\n", A.leader_by_group(df, C.REGION), "\n")

    paths = save_all(df)
    print(f"[4/6] Saved {len(paths)} charts -> {C.IMAGE_DIR}")

    print("[5/6] Key insights:")
    for i, line in enumerate(generate_insights(df), 1):
        print(f"   {i}. {line}")
    print(f"      report -> {save_report(df)}")

    print("\n[6/6] Done. Launch the dashboard with:  streamlit run app.py")


if __name__ == "__main__":
    main()
