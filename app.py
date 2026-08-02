"""banksys_szai4 Streamlit 入口。

US-1 阶段:占位首页,保证镜像可构建、健康端点 /_stcore/health 可用;
数据分析页与在线预测页在后续 feature 分支扩展(见 standards/01)。
"""

import streamlit as st

st.set_page_config(
    page_title="banksys_szai4 · 银行营销认购预测",
    page_icon="🏦",
    layout="wide",
)

st.title("🏦 banksys_szai4 · 银行营销认购预测")
st.caption("数据分析交互页 + 在线预测系统(Streamlit + scikit-learn)")
