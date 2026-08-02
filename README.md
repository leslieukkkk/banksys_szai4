# banksys_szai4 · 银行营销认购预测 Web 应用

基于银行营销历史数据(UCI 公开教学数据)构建的 Streamlit 应用,包含:

- **数据分析交互页**:数据概览、分布探索、类别-目标交叉分析、筛选联动图表。
- **在线预测系统**:点选/下拉/数字输入客户信息,预测是否认购定期存款产品(离线训练 scikit-learn 模型)。

## 技术栈

Python 3.11 · Streamlit · scikit-learn · Plotly · pytest · ruff · Docker · GitHub Actions

## 目录结构

```text
banksys_szai4/
├── standards/                 # AI 项目记忆与通用规范(新会话先读 README)
├── data/                      # train.csv(22500 行,含标签)/ test.csv(7500 行,无标签)
├── ml/                        # 离线训练与预测代码(后续 feature 分支)
├── app.py                     # Streamlit 入口
├── models/                    # 训练产物(不进 Git,训练可重复生成)
├── tests/                     # 单元测试
├── requirements.txt           # 生产运行依赖
├── requirements-dev.txt       # 本地/CI 检查依赖
├── Dockerfile / deploy.sh     # 容器化与部署
└── .github/workflows/         # ci.yml / cd.yml
```

## 本地开发

```bash
# 1) 建环境(或复用已有 conda 环境)
conda create -y -n banksys_szai4 python=3.11
conda activate banksys_szai4

# 2) 装依赖(国内可用清华源)
pip install -r requirements-dev.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 3) 运行应用(http://localhost:8501)
streamlit run app.py

# 4) 离线训练(产出 models/model.joblib、eval_report.json、test_predictions.csv;
#    holdout AUC < 0.80 时以非零码退出)
python -m ml.train

# 5) 本地自检(提交前必须全绿)
ruff format --check .
ruff check .
pytest --cov --cov-fail-under=80
```

## CI/CD 流程(六步闭环)

```text
feature 分支 → PR → CI(格式/lint/测试/覆盖率 80%/docker build)
→ 人工 Review + 合并 main → CD(SSH 同步 → 构建 → 运行 → 健康检查)
```

- **CI**:PR 与 push main 时运行,红灯不合并。
- **CD**:合并 main 自动部署到服务器;公网端口首选 **8888**,被占用时在 **8888-8899** 区间自动顺延(共享服务器,**最终端口以 CD 日志为准**)。
- **健康检查**:`http://<服务器>:<端口>/_stcore/health`(Streamlit 官方端点,返回 `ok`)。
- **Secrets**(GitHub → Settings → Secrets and variables → Actions):
  `SSH_PRIVATE_KEY` / `SSH_HOST` / `SSH_USER`(密钥绝不进 Git)。
- 详细流程与标准见 [`standards/`](standards/README.md)。
