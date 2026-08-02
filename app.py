"""banksys_szai4 Streamlit 入口:侧边栏导航(数据分析 / 在线预测)。

数据分析页(US-2,核心逻辑 analysis.py)、在线预测页(US-4,核心逻辑 ml/predict.py)均已实现;
界面中文化(US-5)由 labels.py 字典提供「英文取值 + 中文显示」。
"""

import streamlit as st

import analysis
import labels
from ml import predict as predict_ml
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
        # 中文显示 + 英文取值:过滤逻辑仍用英文列名(US-5)
        cat_col = st.selectbox(
            "类别特征",
            CATEGORICAL_FEATURES,
            format_func=lambda col: labels.FEATURE_LABELS[col],
            key="analysis_cat_col",
        )
        cat_options = sorted(df[cat_col].dropna().unique())
        cat_values = st.multiselect(
            f"{labels.FEATURE_LABELS[cat_col]} 取值",
            cat_options,
            default=cat_options,
            format_func=labels.option_label,
            key="cat_values",
        )
    with right:
        num_col = st.selectbox(
            "数值特征",
            NUMERIC_FEATURES,
            format_func=lambda col: labels.FEATURE_LABELS[col],
            key="analysis_num_col",
        )
        num_min, num_max = float(df[num_col].min()), float(df[num_col].max())
        num_range = st.slider(
            f"{labels.FEATURE_LABELS[num_col]} 范围",
            num_min,
            num_max,
            (num_min, num_max),
            key="num_range",
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
    st.subheader(f"{labels.FEATURE_LABELS[cat_col]} 各取值认购占比")
    st.plotly_chart(analysis.make_category_target_bar(filtered, cat_col), use_container_width=True)
    st.subheader(f"{labels.FEATURE_LABELS[num_col]} 分布")
    st.plotly_chart(analysis.make_numeric_hist(filtered, num_col), use_container_width=True)

    st.subheader("数据预览")
    display_columns = {**labels.FEATURE_LABELS, **labels.EXTRA_COLUMN_LABELS}
    st.dataframe(filtered.head(100).rename(columns=display_columns))


def render_prediction_page() -> None:
    """在线预测页(US-4):点选输入 21 特征,预测是否认购(逻辑见 ml/predict.py)。"""
    st.header("🔮 在线预测")
    df = _load_train()
    options = predict_ml.load_category_options(df)
    numeric_ranges = predict_ml.load_numeric_ranges(df)

    try:
        model = predict_ml.load_model()
    except FileNotFoundError as exc:
        st.error(str(exc))
        return

    st.subheader("客户信息输入")
    sample: dict = {}
    with st.form("prediction_form"):
        columns = st.columns(2)
        for i, col in enumerate(CATEGORICAL_FEATURES):
            with columns[i % 2]:
                # 中文显示 + 英文取值:模型输入不变,仅界面翻译(US-5)
                sample[col] = st.selectbox(
                    labels.FEATURE_LABELS[col],
                    options[col],
                    format_func=labels.option_label,
                    key=f"cat_{col}",
                )
        for i, col in enumerate(NUMERIC_FEATURES):
            with columns[i % 2]:
                lo, hi = numeric_ranges[col]
                sample[col] = st.number_input(
                    labels.FEATURE_LABELS[col],
                    min_value=lo,
                    max_value=hi,
                    value=(lo + hi) / 2,
                    key=f"num_{col}",
                )
        submitted = st.form_submit_button("预测是否认购")

    if submitted:
        result = predict_ml.predict_one(sample, options, numeric_ranges, model=model)
        for warning in result["warnings"]:
            st.warning(warning)
        if result["errors"]:
            st.error("输入有误,请修正: " + " ; ".join(result["errors"]))
            return
        verdict = "会认购 ✅" if result["subscribe"] == "yes" else "不会认购 ❌"
        st.success(f"预测结果:{verdict}")
        st.metric("认购概率", f"{result['proba']:.2%}")
        st.caption("模型:随机森林 RF-100(holdout AUC 0.893,阈值 0.5)")


page = st.sidebar.radio("页面", ["📊 数据分析", "🔮 在线预测"])
if page == "📊 数据分析":
    render_analysis_page()
else:
    render_prediction_page()
