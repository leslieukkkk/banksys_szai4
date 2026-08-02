"""数据分析页核心逻辑(US-2):纯函数、不依赖 Streamlit,便于单元测试(见 standards/01 US-2 AC6)。"""

from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from ml.preprocessing import CATEGORICAL_FEATURES, NUMERIC_FEATURES, TARGET, load_data

TRAIN_PATH = Path(__file__).resolve().parent / "data" / "train.csv"


def load_train(path: str | Path = TRAIN_PATH) -> pd.DataFrame:
    """加载训练数据(复用 ml.preprocessing 的列校验)。"""
    return load_data(path)


def overview_stats(df: pd.DataFrame) -> dict:
    """概览统计:行数、特征数、认购数、认购率。"""
    total = len(df)
    positives = int((df[TARGET] == "yes").sum())
    return {
        "rows": total,
        "features": len(NUMERIC_FEATURES) + len(CATEGORICAL_FEATURES),
        "positives": positives,
        "positive_rate": positives / total,
    }


def filter_data(
    df: pd.DataFrame,
    category_filters: dict[str, list[str]] | None = None,
    numeric_ranges: dict[str, tuple[float, float]] | None = None,
) -> pd.DataFrame:
    """按类别取值集合与数值区间过滤;空集合/None 表示不过滤该列。"""
    result = df
    for col, values in (category_filters or {}).items():
        if values:
            result = result[result[col].isin(values)]
    for col, (lo, hi) in (numeric_ranges or {}).items():
        result = result[(result[col] >= lo) & (result[col] <= hi)]
    return result


def target_rate_by_category(df: pd.DataFrame, col: str) -> pd.DataFrame:
    """单类别特征各取值的认购占比(降序),供交叉分析图使用。"""
    return (
        df.groupby(col)
        .agg(count=(TARGET, "count"), subscribe_rate=(TARGET, lambda s: (s == "yes").mean()))
        .sort_values("subscribe_rate", ascending=False)
        .reset_index()
    )


def make_target_bar(df: pd.DataFrame) -> go.Figure:
    """目标 yes/no 计数柱状图。"""
    counts = df[TARGET].value_counts().reindex(["no", "yes"]).fillna(0)
    return px.bar(
        x=counts.index,
        y=counts.values,
        labels={"x": TARGET, "y": "数量"},
        title=f"{TARGET} 分布(当前筛选)",
    )


def make_category_target_bar(df: pd.DataFrame, col: str) -> go.Figure:
    """单类别特征各取值认购占比柱状图。"""
    rate = target_rate_by_category(df, col)
    return px.bar(
        rate,
        x=col,
        y="subscribe_rate",
        labels={"subscribe_rate": "认购占比"},
        title=f"{col} 各取值认购占比(当前筛选)",
    )


def make_numeric_hist(df: pd.DataFrame, col: str) -> go.Figure:
    """数值特征分布直方图。"""
    return px.histogram(
        df,
        x=col,
        nbins=30,
        labels={col: col},
        title=f"{col} 分布(当前筛选)",
    )
