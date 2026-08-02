"""Streamlit 应用冒烟测试(US-1 占位首页 → US-2 导航重构)。"""

from streamlit.testing.v1 import AppTest


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


def test_app_switches_to_prediction_placeholder():
    at = AppTest.from_file("app.py").run()

    at.sidebar.radio[0].set_value("🔮 在线预测").run()

    assert not at.exception
    assert at.header[0].value == "🔮 在线预测"
    assert "开发中" in str(at.info[0].value)
