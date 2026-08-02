"""离线训练脚本(US-3):一条命令完成训练、评估、导出。

用法:python -m ml.train
产出:
  models/model.joblib          训练好的 pipeline(预处理 + 分类器)
  models/eval_report.json      评估报告(holdout AUC/F1 等)
  models/test_predictions.csv  test.csv 预测结果(id, subscribe)
门禁:holdout AUC < 0.80 时以非零码退出(见 standards/00 质量门槛)。
"""

import json
import sys
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import f1_score, roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline

from ml.preprocessing import (
    CATEGORICAL_FEATURES,
    ID_COLUMN,
    NUMERIC_FEATURES,
    TARGET,
    build_preprocessor,
    load_data,
)

SEED = 42
MIN_AUC = 0.80

REPO_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = REPO_ROOT / "data"
MODEL_DIR = REPO_ROOT / "models"
MODEL_PATH = MODEL_DIR / "model.joblib"
REPORT_PATH = MODEL_DIR / "eval_report.json"
PREDICTIONS_PATH = MODEL_DIR / "test_predictions.csv"

FEATURES = NUMERIC_FEATURES + CATEGORICAL_FEATURES


def build_model() -> RandomForestClassifier:
    """基线模型:随机森林。对比实验:LR holdout AUC=0.807(距 0.80 门禁余量仅 0.007),
    RF-100 AUC≈0.89(余量 0.09),选 RF-100 兼顾指标与训练耗时;固定种子可复现。"""
    return RandomForestClassifier(n_estimators=100, random_state=SEED, n_jobs=-1)


def train_evaluate(df: pd.DataFrame, seed: int = SEED) -> tuple[dict, Pipeline]:
    """分层划分 holdout,训练 pipeline 并评估;返回 (指标字典, 拟合后的 pipeline)。"""
    X = df[FEATURES]
    y = df[TARGET].map({"yes": 1, "no": 0})
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, stratify=y, random_state=seed
    )
    pipeline = Pipeline([("pre", build_preprocessor()), ("clf", build_model())])
    pipeline.fit(X_train, y_train)
    y_proba = pipeline.predict_proba(X_test)[:, 1]
    y_pred = (y_proba >= 0.5).astype(int)
    metrics = {
        "auc": float(roc_auc_score(y_test, y_proba)),
        "f1": float(f1_score(y_test, y_pred)),
        "positive_rate": float(y.mean()),
    }
    return metrics, pipeline


def predict_test(pipeline: Pipeline, df_test: pd.DataFrame) -> pd.DataFrame:
    """对无标签打分集生成 (id, subscribe) 预测表。"""
    y_proba = pipeline.predict_proba(df_test[FEATURES])[:, 1]
    return pd.DataFrame(
        {
            ID_COLUMN: df_test[ID_COLUMN],
            "subscribe": np.where(y_proba >= 0.5, "yes", "no"),
        }
    )


def auc_passes(metrics: dict, min_auc: float = MIN_AUC) -> bool:
    """模型质量门禁:holdout AUC 是否达标(见 standards/00 第 4 节)。"""
    return metrics["auc"] >= min_auc


def save_artifacts(
    pipeline: Pipeline,
    metrics: dict,
    df_test: pd.DataFrame,
    *,
    model_path: Path = MODEL_PATH,
    report_path: Path = REPORT_PATH,
    predictions_path: Path = PREDICTIONS_PATH,
) -> None:
    """导出模型、评估报告与 test 预测文件(目录自动创建;路径可注入便于测试)。"""
    model_path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(pipeline, model_path)
    report_path.write_text(json.dumps(metrics, ensure_ascii=False, indent=2), encoding="utf-8")
    predict_test(pipeline, df_test).to_csv(predictions_path, index=False)


def main() -> int:
    # 注意:print 保持纯 ASCII —— Windows GBK 控制台会因中文输出崩溃(见 standards/05 排错表)
    print(f">> Loading training data: {DATA_DIR / 'train.csv'}")
    df = load_data(DATA_DIR / "train.csv")
    pos_rate = df[TARGET].value_counts(normalize=True)["yes"]
    print(f">> Samples: {len(df)} rows, positive rate {pos_rate:.3f}")

    metrics, pipeline = train_evaluate(df)
    print(f">> holdout AUC={metrics['auc']:.4f} F1={metrics['f1']:.4f}")

    save_artifacts(pipeline, metrics, pd.read_csv(DATA_DIR / "test.csv"))
    print(f">> Generated: {MODEL_PATH} / {REPORT_PATH} / {PREDICTIONS_PATH}")

    if not auc_passes(metrics):
        print(f">> Gate failed: AUC {metrics['auc']:.4f} < {MIN_AUC}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
