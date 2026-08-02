# PROGRESS · banksys_szai4 〔本项目活记忆 · 状态机〕

> **作用**:这是项目的"存档点"。任意 AI、任意重启会话,读它即可知道当前做到哪、下一步做什么、踩过什么坑。
> **更新时机**:每完成一个有意义步骤、每次会话结束前。
> **格式要求**:时间倒序,最新在上;短、准、可接力。

---

## 当前状态 (最后更新: 2026-08-02 · by AI)

- **阶段**:`初始化`
- **上一步完成**:读取 standards 全部文件;确认需求与技术选型(名称 `banksys_szai4` / Streamlit + scikit-learn / 端口 8888 / 数据进 Git);填写 `00-project-context.md`、`01-requirements.md`(US-1~US-4 带验收标准)。
- **下一步 (TODO 第一条)**:等人类确认文档 → 第①步建仓(gh repo create)+ 提示配置 Secrets(SSH 三件套)。
- **阻塞项**:无(等待人类确认文档与开始建仓)

---

## 待办清单 (TODO,按优先级)

> 对应 06 六步流程:①建仓配 Secrets → ②开分支 → ③逐模块开发 → ④本地 CI 自检 → ⑤发 PR → ⑥人工合并 → CD

- [x] 读取 standards/README.md 与 00/01/PROGRESS/02~06
- [x] 确认技术选型:名称 `banksys_szai4`、scikit-learn、数据进 Git
- [x] 填写 `00-project-context.md`(项目身份/目录地图/占位符取值)
- [x] 填写 `01-requirements.md`(US-1~US-4 用户故事 + 验收标准)
- [x] 初始化本文件(PROGRESS 第一批 TODO)
- [ ] ✋确认后:第①步 建仓 —— `git init` + `gh repo create banksys_szai4` + 提示配置 Secrets(`SSH_PRIVATE_KEY`/`SSH_HOST`/`SSH_USER`)
- [ ] 第②步 从 main 开分支 `feature/1-project-init`(工程骨架 + US-1)
- [ ] 第③步 模块 A:工程骨架(requirements/requirements-dev/Dockerfile/.gitignore/pyproject/README)
- [ ] 第③步 模块 B:数据层 + 离线训练(ml/preprocessing.py、ml/train.py)+ 测试
- [ ] 第③步 模块 C:Streamlit 数据分析页(app.py 页 1)+ 测试
- [ ] 第③步 模块 D:在线预测页(app.py 页 2)+ 测试
- [ ] 第④步 本地 CI 自检:ruff format/check + pytest + 覆盖率 ≥80% + 模型门禁 AUC ≥ 0.80
- [ ] 第⑤步 push + `gh pr create`(closes #1),CI 复检,汇报后停下
- [ ] 第⑥步 人类合并 → CD 自动部署 → 汇报端口 8888 + `/_stcore/health` 结果
- [ ] 会话结束前更新本文件

---

## 关键决策记录 (ADR)

| 日期 | 决策 | 理由 |
|---|---|---|
| 2026-08-02 | 仓库/镜像/容器名统一为 `banksys_szai4` | 用户指定,命名统一避免 CD 混乱 |
| 2026-08-02 | 机器学习库用 scikit-learn | 22.5k 行数据足够,无 GPU 需求,教学可复现 |
| 2026-08-02 | `data/`(train/test.csv,~3.7MB 公开数据)提交进 Git | 公开教学数据,CI/CD 无需额外下载,流水线最简单(规范 05 第 7 节允许) |
| 2026-08-02 | 模型产物 `models/` 不进 Git,Docker 构建时训练生成 | 产物可重复生成,镜像与模型绑定,杜绝陈旧模型 |
| 2026-08-02 | 主机端口固定 8888(不回退),容器内 8501 | 用户指定 8888;Streamlit 默认端口 8501 |
| 2026-08-02 | 健康检查用 `/_stcore/health` | Streamlit 无自定义路由,官方提供该健康端点,返回 `ok` |

---

## 已知坑 (GOTCHAS)

- 暂无真实故障;预置一条已知约束:Streamlit 不支持自定义 HTTP 路由,**健康检查必须用官方 `/_stcore/health` 端点**,不能用 `/health`。

---

## 里程碑 (DONE)

- [ ] <完成一项就勾选,写一句话说明结果>
