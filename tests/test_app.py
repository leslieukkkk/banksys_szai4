"""Streamlit 应用冒烟测试(US-1 占位首页 → US-2 导航 → US-4 预测表单)。"""

import numpy as np
from streamlit.testing.v1 import AppTest

from ml import predict
from ml.preprocessing import CATEGORICAL_FEATURES, NUMERIC_FEATURES


class FakePipeline:
    """固定概率的假 pipeline,避免测试依赖真实模型文件(CI 中模型未训练)。"""

    def predict_proba(self, X):
        return np.array([[0.7, 0.3]])


def test_app_renders_title():
    # Arrange / Act: AppTest 在进程中完整执行 app.py
    at = AppTest.from_file("app.py").run()

    # Assert
    assert not at.exception
    assert at.title[0].value == "🏦 banksys_szai4 · 银行营销认购预测"


def test_app_analysis_page_is_default():
    at = AppTest.from_file("app.py").run()

    assert at.sidebar.radio[0].label == "页面"
    assert at.sidebar.radio[0].value == "📊 数据分析"
    assert at.header[0].value == "📊 数据分析"
    # 概览指标渲染(US-2 AC1)
    assert len(at.metric) == 4
    # 界面中文化(US-5):特征选择器显示中文,取值仍为英文列名
    assert at.selectbox(key="analysis_cat_col").label == "类别特征"
    assert at.selectbox(key="analysis_cat_col").value == "job"
    assert at.selectbox(key="analysis_num_col").value == "age"


def test_app_prediction_page_renders_full_form(monkeypatch):
    # 模型缺失时页面给出提示而不是崩溃(US-4 AC3)
    monkeypatch.setattr(predict, "load_model", lambda: FakePipeline())

    at = AppTest.from_file("app.py").run()
    at.sidebar.radio[0].set_value("🔮 在线预测").run()

    assert not at.exception
    assert at.header[0].value == "🔮 在线预测"
    # 21 个特征控件 + 提交按钮(US-4 AC1)
    assert len(at.selectbox) == len(CATEGORICAL_FEATURES)
    assert len(at.number_input) == len(NUMERIC_FEATURES)
    assert len(at.button) == 1
    # 界面中文化(US-5 AC1/AC2):标签为中文,取值仍为英文
    assert at.selectbox(key="cat_job").label == "职业"
    assert at.selectbox(key="cat_job").value == "admin."
    assert at.number_input(key="num_age").label == "年龄"


def test_app_prediction_missing_model_shows_hint(monkeypatch):
    def raise_missing():
        raise FileNotFoundError("模型文件不存在 —— 请先运行 python -m ml.train 生成模型")

    monkeypatch.setattr(predict, "load_model", raise_missing)

    at = AppTest.from_file("app.py").run()
    at.sidebar.radio[0].set_value("🔮 在线预测").run()

    assert not at.exception
    assert "python -m ml.train" in str(at.error[0].value)


def test_app_prediction_submit_shows_result(monkeypatch):
    monkeypatch.setattr(predict, "load_model", lambda: FakePipeline())

    at = AppTest.from_file("app.py").run()
    at.sidebar.radio[0].set_value("🔮 在线预测").run()
    at.button[0].click().run()

    assert not at.exception
    # FakePipeline 概率 0.3 < 0.5 → 不会认购
    assert "不会认购" in str(at.success[0].value)
    assert at.metric[0].label == "认购概率"
