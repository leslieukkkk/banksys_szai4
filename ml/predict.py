"""在线预测逻辑(US-4):加载模型、输入校验、单条预测。

类别选项与数值范围从训练数据动态生成(见 standards/01 US-4 技术备注),
避免线上选项与训练分布漂移;预测复用训练 pipeline,保证特征一致。
"""

import numbers
from pathlib import Path

import joblib
import numpy as np
import pandas as pd

from labels import FEATURE_LABELS
from ml.preprocessing import CATEGORICAL_FEATURES, NUMERIC_FEATURES
from ml.train import FEATURES, MODEL_PATH

THRESHOLD = 0.5


def load_model(path: Path = MODEL_PATH):
    """加载训练好的 pipeline;文件缺失时给出可操作提示(US-4 AC3)。"""
    if not path.exists():
        raise FileNotFoundError(f"模型文件不存在: {path} —— 请先运行 python -m ml.train 生成模型")
    return joblib.load(path)


def load_category_options(df: pd.DataFrame) -> dict[str, list[str]]:
    """从训练数据提取各类别特征的允许取值(排序),供下拉控件使用。"""
    return {col: sorted(df[col].dropna().unique().tolist()) for col in CATEGORICAL_FEATURES}


def load_numeric_ranges(df: pd.DataFrame) -> dict[str, tuple[float, float]]:
    """从训练数据提取数值特征取值范围,供输入控件上下界与校验使用。"""
    return {col: (float(df[col].min()), float(df[col].max())) for col in NUMERIC_FEATURES}


def validate_input(
    sample: dict,
    options: dict[str, list[str]],
    numeric_ranges: dict[str, tuple[float, float]],
) -> tuple[list[str], list[str]]:
    """校验单条输入;返回 (errors, warnings),errors 非空则阻止预测(US-4 AC4)。"""
    errors: list[str] = []
    warnings: list[str] = []
    for col in CATEGORICAL_FEATURES:
        value = sample.get(col)
        if value is None or str(value).strip() == "":
            errors.append(f"{FEATURE_LABELS[col]}({col}): 必填")
        elif value not in options[col]:
            errors.append(f"{FEATURE_LABELS[col]}({col}): 取值 '{value}' 不在训练数据取值范围内")
    for col in NUMERIC_FEATURES:
        value = sample.get(col)
        if value is None:
            errors.append(f"{FEATURE_LABELS[col]}({col}): 必填")
            continue
        if not isinstance(value, numbers.Real) or not np.isfinite(value):
            errors.append(f"{FEATURE_LABELS[col]}({col}): 必须为有效数字")
            continue
        lo, hi = numeric_ranges[col]
        if not lo <= value <= hi:
            warnings.append(
                f"{FEATURE_LABELS[col]}({col}): {value} 超出训练数据范围"
                f" [{lo:.1f}, {hi:.1f}],预测结果仅供参考"
            )
    return errors, warnings


def predict_one(
    sample: dict,
    options: dict[str, list[str]],
    numeric_ranges: dict[str, tuple[float, float]],
    model=None,
    threshold: float = THRESHOLD,
) -> dict:
    """校验并预测单条输入;返回 {proba, subscribe, errors, warnings}。

    类别新值由预处理 OneHotEncoder(handle_unknown="ignore")兜底,不会崩溃。
    """
    errors, warnings = validate_input(sample, options, numeric_ranges)
    if errors:
        return {"proba": None, "subscribe": None, "errors": errors, "warnings": warnings}
    if model is None:
        model = load_model()
    row = pd.DataFrame([sample])[FEATURES]
    proba = float(model.predict_proba(row)[0, 1])
    return {
        "proba": proba,
        "subscribe": "yes" if proba >= threshold else "no",
        "errors": [],
        "warnings": warnings,
    }
