"""界面中文字典(US-5):字段名与选项的显示翻译。

内部取值保持英文(模型 pipeline 使用),仅显示层中文化:
st.selectbox(format_func=labels.option_label) 实现「英文取值 + 中文显示」。
"""

# 21 个特征的显示名(列名 → 中文)
FEATURE_LABELS = {
    "age": "年龄",
    "job": "职业",
    "marital": "婚姻状况",
    "education": "教育程度",
    "default": "是否有信用违约",
    "housing": "是否有住房贷款",
    "loan": "是否有个人贷款",
    "contact": "联系方式",
    "month": "最近联系月份",
    "day_of_week": "最近联系星期",
    "duration": "通话时长(秒)",
    "campaign": "本次活动联系次数",
    "pdays": "距上次活动天数(999=从未联系)",
    "previous": "之前活动联系次数",
    "poutcome": "上次活动结果",
    "emp_var_rate": "就业率变动",
    "cons_price_index": "消费者价格指数(CPI)",
    "cons_conf_index": "消费者信心指数",
    "lending_rate3m": "3个月贷款利率",
    "nr_employed": "就业人数(千人)",
}

# 类别取值 → 中文(未收录的取值原样显示)
OPTION_LABELS = {
    "admin.": "行政",
    "blue-collar": "蓝领工人",
    "entrepreneur": "创业者",
    "housemaid": "家政",
    "management": "管理岗",
    "retired": "退休",
    "self-employed": "自由职业",
    "services": "服务业",
    "student": "学生",
    "technician": "技术员",
    "unemployed": "失业",
    "unknown": "未知",
    "divorced": "离异",
    "married": "已婚",
    "single": "未婚",
    "basic.4y": "小学(4年)",
    "basic.6y": "小学(6年)",
    "basic.9y": "初中(9年)",
    "high.school": "高中",
    "illiterate": "文盲",
    "professional.course": "职校",
    "university.degree": "大学",
    "no": "无",
    "yes": "有",
    "cellular": "手机",
    "telephone": "座机",
    "success": "上次成功",
    "failure": "上次失败",
    "nonexistent": "上次未联系",
    "jan": "1月",
    "feb": "2月",
    "mar": "3月",
    "apr": "4月",
    "may": "5月",
    "jun": "6月",
    "jul": "7月",
    "aug": "8月",
    "sep": "9月",
    "oct": "10月",
    "nov": "11月",
    "dec": "12月",
    "mon": "周一",
    "tue": "周二",
    "wed": "周三",
    "thu": "周四",
    "fri": "周五",
}


# 目标 subscribe 取值的显示名(数据分析页目标分布图刻度)
TARGET_LABELS = {"no": "未认购", "yes": "认购"}

# 数据预览表额外列名(不在 21 特征内)
EXTRA_COLUMN_LABELS = {"subscribe": "是否认购", "id": "编号"}


def option_label(value: str) -> str:
    """下拉选项显示名;未收录的取值原样返回(防新值导致显示缺失)。"""
    return OPTION_LABELS.get(value, value)
