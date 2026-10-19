"""Data cleaning & preprocessing for poll responses."""
import numpy as np
import pandas as pd

from . import config as C
from .text_utils import sentiment_label

TOOL_MAP = {"python": "Python", "py": "Python", "excel": "Excel", "ms excel": "Excel",
            "power bi": "Power BI", "powerbi": "Power BI", "power-bi": "Power BI",
            "tableau": "Tableau", "sql": "SQL", "r": "R"}
WORD_NUMBERS = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5}
YES_NO = {"yes": "Yes", "y": "Yes", "true": "Yes", "no": "No", "n": "No", "false": "No"}
GENDER_MAP = {"m": "Male", "male": "Male", "f": "Female", "female": "Female", "other": "Other"}


def _norm(series: pd.Series) -> pd.Series:
    """lower-case, trim and collapse repeated spaces (NaN stays NaN)."""
    return series.astype("string").str.strip().str.lower().str.replace(r"\s+", " ", regex=True)


def clean_poll_data(raw: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """Return (clean_df, log). `log` records what each step removed/fixed."""
    df = raw.rename(columns=C.COLUMN_ALIASES).copy()
    log = {"rows_raw": len(df)}

    df = df.drop_duplicates()
    log["duplicates_removed"] = log["rows_raw"] - len(df)

    df[C.TIMESTAMP] = pd.to_datetime(df[C.TIMESTAMP], errors="coerce")

    tool = _norm(df[C.TOOL])
    mapped = tool.map(TOOL_MAP)
    unknown = mapped.isna() & tool.notna()
    df[C.TOOL] = mapped.mask(unknown, "Other")
    log["unmapped_tools_set_to_Other"] = int(unknown.sum())

    df[C.RECOMMEND] = _norm(df[C.RECOMMEND]).map(YES_NO)
    df[C.GENDER] = _norm(df[C.GENDER]).map(GENDER_MAP)
    df[C.REGION] = df[C.REGION].astype("string").str.strip().str.title()
    df[C.AGE] = df[C.AGE].astype("string").str.strip()

    r = _norm(df[C.RATING]).replace(WORD_NUMBERS)
    r = pd.to_numeric(r, errors="coerce").astype(float)
    invalid = r.notna() & ~r.between(1, 5)
    r[invalid] = np.nan
    df[C.RATING] = r
    log["invalid_ratings_out_of_range"] = int(invalid.sum())

    before = len(df)
    df = df.dropna(subset=[C.TIMESTAMP, C.TOOL, C.RATING]).copy()
    log["rows_dropped_missing_critical"] = before - len(df)
    for col in (C.GENDER, C.REGION, C.AGE, C.RECOMMEND):
        df[col] = df[col].fillna("Unknown")
    df[C.FEEDBACK] = df[C.FEEDBACK].fillna("").astype(str).str.strip()

    df[C.RATING] = df[C.RATING].astype(int)
    df["Date"] = df[C.TIMESTAMP].dt.normalize()
    df["Feedback Length"] = df[C.FEEDBACK].str.len()
    df["Sentiment"] = df[C.FEEDBACK].map(sentiment_label).where(df[C.FEEDBACK] != "", "No comment")

    df = df.sort_values(C.TIMESTAMP).reset_index(drop=True)
    for col in (C.AGE, C.GENDER, C.REGION, C.TOOL, C.RECOMMEND):
        df[col] = df[col].astype(str)
    log["rows_clean"] = len(df)
    return df, log
