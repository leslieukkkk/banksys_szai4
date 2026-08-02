"""labels 中文字典单元测试(US-5)。"""

import labels
from ml.preprocessing import CATEGORICAL_FEATURES, NUMERIC_FEATURES


def _has_cjk(text: str) -> bool:
    return any("一" <= ch <= "鿿" for ch in text)


def test_all_features_have_chinese_labels():
    expected = set(NUMERIC_FEATURES + CATEGORICAL_FEATURES)
    assert expected <= set(labels.FEATURE_LABELS)
    # 每个字段名都含中文字符,防止漏翻译
    assert all(_has_cjk(label) for label in labels.FEATURE_LABELS.values())


def test_option_label_translates_known_values():
    assert labels.option_label("admin.") == "行政"
    assert labels.option_label("university.degree") == "大学"
    assert labels.option_label("jan") == "1月"
    assert labels.option_label("mon") == "周一"
    assert labels.option_label("no") == "无"
    assert labels.option_label("success") == "上次成功"


def test_option_label_passthrough_unknown_value():
    # 未收录的取值原样返回,防显示缺失
    assert labels.option_label("not-a-real-job") == "not-a-real-job"


def test_target_and_extra_column_labels():
    assert labels.TARGET_LABELS == {"no": "未认购", "yes": "认购"}
    assert labels.EXTRA_COLUMN_LABELS == {"subscribe": "是否认购", "id": "编号"}
