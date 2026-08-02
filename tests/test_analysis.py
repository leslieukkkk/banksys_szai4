"""analysis 模块单元测试(US-2):小样本保证快速稳定。"""

import pandas as pd
import pytest

import analysis
from ml.preprocessing import CATEGORICAL_FEATURES, NUMERIC_FEATURES, TARGET


@pytest.fixture(scope="module")
def df() -> pd.DataFrame:
    return analysis.load_train().sample(500, random_state=42)


def test_load_train_has_expected_columns():
    df = analysis.load_train()
    expected = set(NUMERIC_FEATURES + CATEGORICAL_FEATURES + [TARGET])
    assert expected <= set(df.columns)


def test_overview_stats(df):
    stats = analysis.overview_stats(df)
    assert stats["rows"] == len(df)
    assert stats["features"] == len(NUMERIC_FEATURES) + len(CATEGORICAL_FEATURES)
    assert stats["positives"] == int((df[TARGET] == "yes").sum())
    assert 0 < stats["positive_rate"] < 1


def test_filter_data_by_category(df):
    filtered = analysis.filter_data(df, category_filters={"job": ["admin."]})
    assert len(filtered) > 0
    assert (filtered["job"] == "admin.").all()


def test_filter_data_by_numeric_range(df):
    filtered = analysis.filter_data(df, numeric_ranges={"age": (25, 40)})
    assert len(filtered) > 0
    assert filtered["age"].between(25, 40).all()


def test_filter_data_combined_filters(df):
    filtered = analysis.filter_data(
        df,
        category_filters={"job": ["admin.", "services"]},
        numeric_ranges={"age": (25, 40)},
    )
    assert len(filtered) > 0
    assert filtered["job"].isin(["admin.", "services"]).all()
    assert filtered["age"].between(25, 40).all()


def test_filter_data_empty_values_mean_no_filter(df):
    assert len(analysis.filter_data(df, category_filters={"job": []})) == len(df)


def test_target_rate_by_category(df):
    rate = analysis.target_rate_by_category(df, "job")
    assert list(rate.columns) == ["job", "count", "subscribe_rate"]
    assert rate["subscribe_rate"].between(0, 1).all()
    assert rate["subscribe_rate"].is_monotonic_decreasing


def test_make_target_bar(df):
    fig = analysis.make_target_bar(df)
    assert len(fig.data) == 1
    assert set(fig.data[0].x) == {"no", "yes"}
    assert sum(fig.data[0].y) == len(df)


def test_make_category_target_bar(df):
    fig = analysis.make_category_target_bar(df, "job")
    assert len(fig.data) == 1
    assert len(fig.data[0].x) == df["job"].nunique()


def test_make_numeric_hist(df):
    fig = analysis.make_numeric_hist(df, "age")
    assert len(fig.data) == 1
    assert fig.data[0].type == "histogram"
