"""ml.predict 单元测试(US-4)。"""

import joblib
import numpy as np
import pandas as pd
import pytest

from ml import predict
from ml.preprocessing import CATEGORICAL_FEATURES, NUMERIC_FEATURES
from ml.train import FEATURES


@pytest.fixture(scope="module")
def data() -> tuple[pd.DataFrame, dict, dict]:
    df = pd.read_csv("data/train.csv").sample(300, random_state=42)
    return df, predict.load_category_options(df), predict.load_numeric_ranges(df)


def _valid_sample(df: pd.DataFrame) -> dict:
    row = df.iloc[0]
    return {col: row[col] for col in FEATURES}


def _mid_sample(options: dict, ranges: dict) -> dict:
    """构造所有特征合法的输入:类别取第一个合法值,数值取区间中值(避免越界警告干扰断言)。"""
    sample = {col: options[col][0] for col in CATEGORICAL_FEATURES}
    sample.update({col: (lo + hi) / 2 for col, (lo, hi) in ranges.items()})
    return sample


class FakeModel:
    """固定概率的假模型,用于阈值分支测试。"""

    def __init__(self, proba: float):
        self._proba = proba

    def predict_proba(self, X):
        return np.array([[1 - self._proba, self._proba]])


def test_load_model(tmp_path):
    path = tmp_path / "model.joblib"
    joblib.dump({"pipeline": True}, path)
    assert predict.load_model(path) == {"pipeline": True}


def test_load_model_missing_raises_with_hint(tmp_path):
    with pytest.raises(FileNotFoundError, match="python -m ml.train"):
        predict.load_model(tmp_path / "nope.joblib")


def test_load_category_options_keys_and_sorted(data):
    _, options, _ = data
    assert set(options) == set(CATEGORICAL_FEATURES)
    for values in options.values():
        assert values == sorted(values)


def test_load_numeric_ranges(data):
    _, _, numeric_ranges = data
    assert set(numeric_ranges) == set(NUMERIC_FEATURES)
    for lo, hi in numeric_ranges.values():
        assert lo <= hi


def test_validate_missing_category_is_error(data):
    _, options, ranges = data
    sample = {col: "x" for col in CATEGORICAL_FEATURES}
    sample.update({col: (lo + hi) / 2 for col, (lo, hi) in ranges.items()})
    errors, warnings = predict.validate_input(sample, options, ranges)
    assert len(errors) == len(CATEGORICAL_FEATURES)
    assert warnings == []


def test_validate_non_numeric_in_numeric_column_is_error(data):
    _, options, ranges = data
    sample = _mid_sample(options, ranges)
    sample["age"] = "abc"
    errors, warnings = predict.validate_input(sample, options, ranges)
    assert any("age" in e for e in errors)
    assert warnings == []


def test_validate_unknown_category_is_error(data):
    _, options, ranges = data
    sample = _mid_sample(options, ranges)
    sample["job"] = "not-a-real-job"
    errors, warnings = predict.validate_input(sample, options, ranges)
    assert any("job" in e for e in errors)
    assert warnings == []


def test_validate_missing_numeric_is_error(data):
    _, options, ranges = data
    sample = _mid_sample(options, ranges)
    sample["age"] = None
    errors, warnings = predict.validate_input(sample, options, ranges)
    assert any("age" in e for e in errors)
    assert warnings == []


def test_validate_out_of_range_numeric_warns_not_error(data):
    _, options, ranges = data
    sample = _mid_sample(options, ranges)
    lo, hi = ranges["age"]
    sample["age"] = hi + 100
    errors, warnings = predict.validate_input(sample, options, ranges)
    assert errors == []
    assert any("age" in w for w in warnings)


def test_validate_valid_input_returns_no_messages(data):
    df, options, ranges = data
    errors, warnings = predict.validate_input(_valid_sample(df), options, ranges)
    assert errors == []
    assert warnings == []


@pytest.mark.parametrize(("proba", "expected"), [(0.80, "yes"), (0.30, "no")])
def test_predict_one_threshold(data, proba, expected):
    df, options, ranges = data
    result = predict.predict_one(_valid_sample(df), options, ranges, model=FakeModel(proba))
    assert result["errors"] == []
    assert result["proba"] == pytest.approx(proba)
    assert result["subscribe"] == expected


def test_predict_one_errors_block_prediction(data):
    df, options, ranges = data
    sample = _valid_sample(df)
    sample["job"] = "not-a-real-job"
    result = predict.predict_one(sample, options, ranges, model=FakeModel(0.8))
    assert result["proba"] is None
    assert result["subscribe"] is None
    assert result["errors"]


def test_predict_one_with_real_model(data):
    """真实模型端到端:本地有产物则跑,CI 无产物自动跳过。"""
    df, options, ranges = data
    try:
        model = predict.load_model()
    except FileNotFoundError:
        pytest.skip("本地无模型文件(CI 未运行训练步骤)")
    result = predict.predict_one(_valid_sample(df), options, ranges, model=model)
    assert result["errors"] == []
    assert 0 <= result["proba"] <= 1
    assert result["subscribe"] in {"yes", "no"}
