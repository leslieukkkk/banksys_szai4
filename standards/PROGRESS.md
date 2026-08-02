# PROGRESS · banksys_szai4 〔本项目活记忆 · 状态机〕

> **作用**:这是项目的"存档点"。任意 AI、任意重启会话,读它即可知道当前做到哪、下一步做什么、踩过什么坑。
> **更新时机**:每完成一个有意义步骤、每次会话结束前。
> **格式要求**:时间倒序,最新在上;短、准、可接力。

---

## 当前状态 (最后更新: 2026-08-02 · by AI)

- **阶段**:`初始化(六步流程第④步)`
- **上一步完成**:feature/1-project-init 模块 A(工程骨架)+ 模块 B(CI/CD 配置)开发完成;本地自检全绿(ruff format/check + pytest 1 passed + 覆盖率 100% ≥ 80% 门禁)。
- **下一步 (TODO 第一条)**:✋等确认门 4 → 提交 push → 创建 PR(closes #1)。
- **阻塞项**:无(等人类确认后进入第⑤步)

---

## 待办清单 (TODO,按优先级)

> 对应 06 六步流程:①建仓配 Secrets → ②开分支 → ③逐模块开发 → ④本地 CI 自检 → ⑤发 PR → ⑥人工合并 → CD

- [x] 读取 standards/README.md 与 00/01/PROGRESS/02~06
- [x] 确认技术选型:名称 `banksys_szai4`、scikit-learn、数据进 Git
- [x] 填写 `00-project-context.md`(项目身份/目录地图/占位符取值)
- [x] 填写 `01-requirements.md`(US-1~US-4 用户故事 + 验收标准)
- [x] 初始化本文件(PROGRESS 第一批 TODO)
- [x] 第①步 建仓:`gh repo create banksys_szai4`(https://github.com/leslieukkkk/banksys_szai4);人类已配置 Secrets(gh secret list 核对通过)
- [x] 第②步 从 main 开分支 `feature/1-project-init`(Issue #1 = US-1)
- [x] 第③步 模块 A:工程骨架(requirements/requirements-dev/pyproject/app.py/tests/test_app.py)
- [x] 第③步 模块 B:CI/CD(Dockerfile/deploy.sh/ci.yml/cd.yml/README)
- [x] 第④步 本地 CI 自检:ruff format --check ✅ / ruff check ✅ / pytest --cov --cov-fail-under=80 ✅(1 passed, 100%)
- [ ] 第⑤步 ✋确认后:git commit + push + `gh pr create`(closes #1),CI 复检,汇报后停下
- [ ] 第⑥步 人类合并 → CD 自动部署 → 汇报端口 8888 + `/_stcore/health` 结果
- [ ] 后续 US-3(离线训练)→ US-2(数据分析页)→ US-4(在线预测),每个新分支 + PR
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
