"""ml 模块单元测试(US-3):小样本保证快速稳定,固定种子可复现。"""

import json

import pandas as pd
import pytest

from ml import train
from ml.preprocessing import CATEGORICAL_FEATURES, NUMERIC_FEATURES, TARGET, load_data


@pytest.fixture(scope="module")
def sample_df() -> pd.DataFrame:
    """固定种子抽样 300 行,保证测试快速且可复现。"""
    return load_data(train.DATA_DIR / "train.csv").sample(300, random_state=42)


@pytest.fixture(scope="module")
def sample_test_df() -> pd.DataFrame:
    return pd.read_csv(train.DATA_DIR / "test.csv").head(50)


def test_load_data_has_all_expected_columns():
    df = load_data(train.DATA_DIR / "train.csv")
    expected = set(NUMERIC_FEATURES + CATEGORICAL_FEATURES + [TARGET])
    assert expected <= set(df.columns)


def test_load_data_missing_column_raises():
    with pytest.raises(ValueError, match="缺少列"):
        load_data(train.DATA_DIR / "test.csv")  # test.csv 无 subscribe 标签


def test_train_evaluate_returns_valid_metrics(sample_df):
    metrics, pipeline = train.train_evaluate(sample_df)

    assert 0.5 < metrics["auc"] <= 1.0
    assert 0.0 <= metrics["f1"] <= 1.0
    assert 0.0 < metrics["positive_rate"] < 1.0

    proba = pipeline.predict_proba(sample_df[train.FEATURES])[:, 1]
    assert ((proba >= 0) & (proba <= 1)).all()


def test_train_evaluate_reproducible_with_fixed_seed(sample_df):
    metrics_1, _ = train.train_evaluate(sample_df, seed=42)
    metrics_2, _ = train.train_evaluate(sample_df, seed=42)
    assert metrics_1["auc"] == metrics_2["auc"]


def test_predict_test_returns_id_and_subscribe(sample_df, sample_test_df):
    _, pipeline = train.train_evaluate(sample_df)
    predictions = train.predict_test(pipeline, sample_test_df)

    assert list(predictions.columns) == ["id", "subscribe"]
    assert len(predictions) == len(sample_test_df)
    assert set(predictions["subscribe"].unique()) <= {"yes", "no"}


def test_auc_gate_threshold():
    assert train.auc_passes({"auc": 0.80})
    assert train.auc_passes({"auc": 0.95})
    assert not train.auc_passes({"auc": 0.79})


def test_save_artifacts_writes_three_files(sample_df, sample_test_df, tmp_path):
    _, pipeline = train.train_evaluate(sample_df)
    metrics = {"auc": 0.90, "f1": 0.50, "positive_rate": 0.13}

    train.save_artifacts(
        pipeline,
        metrics,
        sample_test_df,
        model_path=tmp_path / "model.joblib",
        report_path=tmp_path / "eval_report.json",
        predictions_path=tmp_path / "test_predictions.csv",
    )

    assert (tmp_path / "model.joblib").exists()
    report = json.loads((tmp_path / "eval_report.json").read_text(encoding="utf-8"))
    assert report["auc"] == 0.90
    predictions = pd.read_csv(tmp_path / "test_predictions.csv")
    assert list(predictions.columns) == ["id", "subscribe"]
    assert len(predictions) == len(sample_test_df)


@pytest.mark.parametrize(("auc", "expected_exit"), [(0.90, 0), (0.50, 1)])
def test_main_exit_code_follows_auc_gate(monkeypatch, tmp_path, auc, expected_exit):
    # Given: 小样本数据 + 模拟评估结果(避免 main 内全量训练)
    sample = load_data(train.DATA_DIR / "train.csv").sample(300, random_state=42)
    sample.to_csv(tmp_path / "train.csv", index=False)
    pd.DataFrame({"id": [1, 2]}).to_csv(tmp_path / "test.csv", index=False)
    monkeypatch.setattr(train, "DATA_DIR", tmp_path)
    monkeypatch.setattr(train, "MODEL_PATH", tmp_path / "model.joblib")
    monkeypatch.setattr(train, "REPORT_PATH", tmp_path / "eval_report.json")
    monkeypatch.setattr(train, "PREDICTIONS_PATH", tmp_path / "test_predictions.csv")
    monkeypatch.setattr(
        train,
        "train_evaluate",
        lambda df, seed=42: ({"auc": auc, "f1": 0.50, "positive_rate": 0.13}, object()),
    )
    monkeypatch.setattr(
        train,
        "predict_test",
        lambda pipeline, df_test: pd.DataFrame({"id": [1, 2], "subscribe": ["no", "no"]}),
    )

    # When / Then: AUC 达标退出码 0,不达标非零(US-3 AC3)
    assert train.main() == expected_exit
