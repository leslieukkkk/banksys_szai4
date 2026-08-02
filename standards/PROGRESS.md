# PROGRESS · banksys_szai4 〔本项目活记忆 · 状态机〕

> **作用**:这是项目的"存档点"。任意 AI、任意重启会话,读它即可知道当前做到哪、下一步做什么、踩过什么坑。
> **更新时机**:每完成一个有意义步骤、每次会话结束前。
> **格式要求**:时间倒序,最新在上;短、准、可接力。

---

## 当前状态 (最后更新: 2026-08-02 · by AI)

- **阶段**:`US-2 开发完成,待 PR(六步流程第④步)`
- **上一步完成**:`feature/6-data-analysis` 开发完成 —— analysis.py 纯逻辑(过滤/聚合/3 种图表)+ app.py 导航重构 + 22 个测试;本地自检全绿(覆盖率 98%);streamlit 真跑冒烟通过(health `ok` / 首页 200)。
- **下一步 (TODO 第一条)**:✋等确认门 4 → 提交 push → PR(closes #6)。
- **阻塞项**:无(等人类确认)

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
- [x] 第⑤步 PR #2(https://github.com/leslieukkkk/banksys_szai4/pull/2)CI 全绿,人类已合并
- [x] 第⑥步 CD 首次失败 → fix/1-cd-healthcheck-wait 修复(等待就绪循环,PR #3)合并后 CD 重跑成功:健康检查 `ok`,部署成功 http://<服务器>:8888
- [x] US-3 离线训练(issue #4 / PR #5):已合并上线,RF-100 AUC=0.8929,镜像构建时训练
- [~] US-2 数据分析页(issue #6 / feature/6-data-analysis):开发完成待 PR
- [ ] 后续 US-4(在线预测),新分支 + PR
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
| 2026-08-02 | 基线模型选随机森林 RF-100(对比:LR AUC=0.807 距 0.80 门禁余量仅 0.007;RF-100 AUC=0.893,余量 0.09) | 门禁余量要留足,防 CI/服务器环境差异导致门禁误红;RF-100 训练耗时可接受 |
| 2026-08-02 | 页面结构:单 `app.py` + 侧边栏 radio 导航;分析逻辑抽到 `analysis.py` 纯函数 | AppTest 可整体驱动;过滤/聚合/图表不依赖 Streamlit 即可单测(US-2 AC6) |

---

## 已知坑 (GOTCHAS)

- 现象:CD 健康检查失败,日志 `curl: (56) Recv failure: Connection reset by peer`,容器显示 `Up Less than a second`。
  根因:Streamlit 首启需导入 pandas/pyarrow 等依赖,服务就绪可达十几秒;立即 curl 收到 connection reset(exit 56,curl 默认不重试)。
  解决:deploy.sh 改为等待就绪循环(20 次 × 3s,`curl -fsS` 成功后退出)。
  验证:fix/1-cd-healthcheck-wait 合并后 CD 重跑(待验证)。
- 现象:plotly `px.bar(color=...)` 会按 color 取值拆成多条 trace,`fig.data[0]` 只含单个类别,测试断言 `len(fig.data)==1` 失败。
  根因:plotly express 的 color 参数是分组语义,不是"填色"语义。
  解决:不需要分组配色时不传 color;测试里按实际 trace 结构断言。
  验证:22 passed。
- 现象:`conda run python -m ml.train` 崩溃 `UnicodeEncodeError: 'gbk' codec can't encode '�'`,pytest 却全绿。
  根因:Windows 控制台 GBK 编码,脚本 print 含中文(规范 05 §7 预置坑;pytest 捕获输出会掩盖,必须真跑一次脚本)。
  解决:ml/train.py 的 print 全部改纯 ASCII,并加注释说明。
  验证:真跑 `python -m ml.train` 输出正常。
- 预置约束:Streamlit 不支持自定义 HTTP 路由,**健康检查必须用官方 `/_stcore/health` 端点**,不能用 `/health`。

---

## 里程碑 (DONE)

- [x] US-1 初始化工程化与 CI/CD:六步流程完整跑通(建仓→分支→模块开发→本地自检→PR→人工合并→CD 部署),服务在主机 8888 运行,`/_stcore/health` 返回 `ok`
- [x] US-3 离线训练与模型产物:`python -m ml.train` 闭环(模型+评估报告+test 预测文件),RF-100 holdout AUC=0.8929,门禁 0.80 通过;镜像构建时训练,模型随镜像上线
