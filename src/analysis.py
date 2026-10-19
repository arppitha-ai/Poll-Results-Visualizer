"""Core analysis functions - each returns a DataFrame/Series you can print or plot."""
import numpy as np
import pandas as pd

from . import config as C
from .text_utils import top_words


def vote_share(df: pd.DataFrame, col: str = C.TOOL) -> pd.DataFrame:
    counts = df[col].value_counts()
    out = pd.DataFrame({"Votes": counts, "Share %": (counts / counts.sum() * 100).round(1)})
    out.index.name = col
    return out


def margin_of_error(share_pct: float, n: int, z: float = 1.96) -> float:
    p = share_pct / 100
    return round(z * np.sqrt(p * (1 - p) / n) * 100, 1)


def rating_summary(df: pd.DataFrame) -> dict:
    r = df[C.RATING]
    return {"mean": round(r.mean(), 2), "median": float(r.median()), "std": round(r.std(), 2),
            "pct_satisfied": round((r >= 4).mean() * 100, 1),
            "pct_dissatisfied": round((r <= 2).mean() * 100, 1)}


def rating_by(df: pd.DataFrame, by: str) -> pd.DataFrame:
    out = df.groupby(by)[C.RATING].agg(["mean", "count"]).round(2)
    return out.rename(columns={"mean": "Avg Rating", "count": "Responses"}).sort_values("Avg Rating", ascending=False)


def crosstab_pct(df: pd.DataFrame, group: str, col: str = C.TOOL) -> pd.DataFrame:
    d = df[df[group] != "Unknown"]
    return (pd.crosstab(d[group], d[col], normalize="index") * 100).round(1)


def leader_by_group(df: pd.DataFrame, group: str) -> pd.DataFrame:
    ct = crosstab_pct(df, group)
    return pd.DataFrame({"Leading Option": ct.idxmax(axis=1), "Share %": ct.max(axis=1)})


def recommend_share(df: pd.DataFrame) -> pd.DataFrame:
    return vote_share(df[df[C.RECOMMEND] != "Unknown"], C.RECOMMEND)


def daily_trend(df: pd.DataFrame) -> pd.DataFrame:
    daily = df.groupby("Date").size().rename("Responses").to_frame()
    daily["7-day avg"] = daily["Responses"].rolling(7, min_periods=1).mean().round(1)
    return daily


def sentiment_share(df: pd.DataFrame) -> pd.DataFrame:
    return vote_share(df, "Sentiment")


def keywords(df: pd.DataFrame, n: int = 15) -> list[tuple[str, int]]:
    return top_words(df[C.FEEDBACK], n)
