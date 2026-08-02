"""banksys_szai4 Streamlit 入口:侧边栏导航(数据分析 / 在线预测)。

数据分析页(US-2)已实现,核心逻辑在 analysis.py;在线预测页(US-4)当前占位。
"""

import streamlit as st

import analysis
from ml.preprocessing import CATEGORICAL_FEATURES, NUMERIC_FEATURES

st.set_page_config(
    page_title="banksys_szai4 · 银行营销认购预测",
    page_icon="🏦",
    layout="wide",
)

st.title("🏦 banksys_szai4 · 银行营销认购预测")


@st.cache_data
def _load_train():
    return analysis.load_train()


def render_analysis_page() -> None:
    """数据分析页:概览 → 筛选联动 → 分布/交叉图表(过滤聚合逻辑见 analysis.py)。"""
    st.header("📊 数据分析")
    df = _load_train()

    stats = analysis.overview_stats(df)
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("总行数", f"{stats['rows']:,}")
    col2.metric("特征数", stats["features"])
    col3.metric("认购数", f"{stats['positives']:,}")
    col4.metric("认购率", f"{stats['positive_rate']:.1%}")

    st.subheader("筛选联动")
    left, right = st.columns(2)
    with left:
        cat_col = st.selectbox("类别特征", CATEGORICAL_FEATURES)
        cat_options = sorted(df[cat_col].dropna().unique())
        cat_values = st.multiselect(
            f"{cat_col} 取值", cat_options, default=cat_options, key="cat_values"
        )
    with right:
        num_col = st.selectbox("数值特征", NUMERIC_FEATURES)
        num_min, num_max = float(df[num_col].min()), float(df[num_col].max())
        num_range = st.slider(
            f"{num_col} 范围", num_min, num_max, (num_min, num_max), key="num_range"
        )

    filtered = analysis.filter_data(
        df,
        category_filters={cat_col: cat_values} if cat_values != cat_options else None,
        numeric_ranges={num_col: num_range} if num_range != (num_min, num_max) else None,
    )

    if filtered.empty:
        st.warning("当前筛选条件下没有数据,请放宽筛选条件。")
        return

    st.subheader("目标分布")
    st.plotly_chart(analysis.make_target_bar(filtered), use_container_width=True)
    st.subheader(f"{cat_col} 各取值认购占比")
    st.plotly_chart(analysis.make_category_target_bar(filtered, cat_col), use_container_width=True)
    st.subheader(f"{num_col} 分布")
    st.plotly_chart(analysis.make_numeric_hist(filtered, num_col), use_container_width=True)

    st.subheader("数据预览")
    st.dataframe(filtered.head(100))


def render_prediction_page() -> None:
    """在线预测页(US-4 实现,当前占位提示)。"""
    st.header("🔮 在线预测")
    st.info("在线预测功能开发中(US-4)。")


page = st.sidebar.radio("页面", ["📊 数据分析", "🔮 在线预测"])
if page == "📊 数据分析":
    render_analysis_page()
else:
    render_prediction_page()
