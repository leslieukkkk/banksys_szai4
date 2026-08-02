"""特征工程与预处理:训练与预测共用,保证在线/离线特征一致(见 standards/01 US-3/US-4)。"""

import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler

# 特征列定义(与 data/train.csv 列名一致)
NUMERIC_FEATURES = [
    "age",
    "duration",
    "campaign",
    "pdays",
    "previous",
    "emp_var_rate",
    "cons_price_index",
    "cons_conf_index",
    "lending_rate3m",
    "nr_employed",
]
CATEGORICAL_FEATURES = [
    "job",
    "marital",
    "education",
    "default",
    "housing",
    "loan",
    "contact",
    "month",
    "day_of_week",
    "poutcome",
]
TARGET = "subscribe"
ID_COLUMN = "id"


def load_data(path: str) -> pd.DataFrame:
    """加载训练 CSV,校验必要列存在;缺失列直接报错便于定位。"""
    df = pd.read_csv(path)
    expected = set(NUMERIC_FEATURES + CATEGORICAL_FEATURES + [TARGET])
    missing = expected - set(df.columns)
    if missing:
        raise ValueError(f"数据缺少列: {sorted(missing)}")
    return df


def build_preprocessor() -> ColumnTransformer:
    """数值列标准化 + 类别列 one-hot(未知类别忽略,防线上输入新值崩溃)。"""
    return ColumnTransformer(
        [
            ("num", StandardScaler(), NUMERIC_FEATURES),
            (
                "cat",
                OneHotEncoder(handle_unknown="ignore", sparse_output=False),
                CATEGORICAL_FEATURES,
            ),
        ]
    )
