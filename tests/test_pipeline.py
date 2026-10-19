import pandas as pd

from src import analysis as A
from src import config as C
from src.cleaning import clean_poll_data
from src.generate_data import generate_poll_data


def _clean():
    return clean_poll_data(generate_poll_data(300, seed=1))


def test_cleaning_removes_duplicates_and_invalid_ratings():
    df, log = _clean()
    assert log["duplicates_removed"] > 0
    assert df[C.RATING].between(1, 5).all()
    assert not df.duplicated().any()


def test_tool_names_standardised():
    df, _ = _clean()
    assert set(df[C.TOOL]) <= set(C.TOOLS) | {"Other"}


def test_vote_share_sums_to_100():
    df, _ = _clean()
    assert abs(A.vote_share(df)["Share %"].sum() - 100) < 0.5


def test_crosstab_rows_sum_to_100():
    df, _ = _clean()
    assert (A.crosstab_pct(df, C.REGION).sum(axis=1).round(0) == 100).all()


def test_pipeline_is_reproducible():
    pd.testing.assert_frame_equal(generate_poll_data(100, 5), generate_poll_data(100, 5))
