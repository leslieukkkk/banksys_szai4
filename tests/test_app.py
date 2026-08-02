"""Streamlit 应用冒烟测试(US-1)。"""

from streamlit.testing.v1 import AppTest


def test_app_renders_without_error():
    # Arrange / Act: AppTest 在进程中完整执行 app.py
    at = AppTest.from_file("app.py").run()

    # Assert
    assert not at.exception
    assert at.title[0].value == "🏦 banksys_szai4 · 银行营销认购预测"
