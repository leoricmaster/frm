# 文档梳理清理与主文档精炼 实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 按已确认规格（`docs/superpowers/specs/2026-09-07-doc-cleanup-design.md`）清除 8 个过程文档、设计迁入 `docs/design/`、建根 README 与验证结论页，随后对主文档逐个评审精炼。

**Architecture:** 两阶段。阶段一为机械化重组（删/迁/改引用/新页/README，两个 commit）；阶段二为交互式精炼（逐文档评审报告 → 用户逐处确认 → 修改，按文档分 commit）。所有引用修复以全库 grep 为准（全集已穷尽列出，比规格 §3.3 示例表更全）。

**Tech Stack:** Markdown/HTML 文档、git（mv 保留历史）、`docs/tutorials/check.py`（教程静态自检）。

## Global Constraints

- **提交须用户确认**（用户 2026-09-07 指令，优先于一切流程模板）：每个 Commit 步骤 = 先展示改动摘要（`git status --short` + `git diff --stat`）→ 等用户明确同意 → 再 `git commit`。用户未确认前不得提交。
- 提交信息：中文、conventional 前缀、末尾 `Co-Authored-By: Claude Code <noreply@anthropic.com>`。
- 设计文档移动一律 `git mv`（保留历史）；过程文档删除用 `git rm`。
- 教程页只改文字引用与正文表述，**不动 CSS/结构**；每轮改动后 `check.py` 7 页须全 OK。
- 阶段二精炼**不擅自砍内容**：评审报告 → 用户确认 → 改；未获确认的项保持原样。
- 本计划与设计文档（2026-09-07-doc-cleanup-*）自身在全部完成后的收尾任务中删除。

---

### Task 1: 蒸馏验证结论页（新文件，本任务不提交）

**Files:**
- Create: `docs/design/2026-09-07-prototype-verification.md`

**Interfaces:**
- Produces: 验证结论页路径 `docs/design/2026-09-07-prototype-verification.md` 及其章节编号（§1 矩阵 / §2 角色模拟 / §3 实测事实 / §4 不覆盖项 / §5 证据位置）——Task 3 的全部引用改写、Task 5 README、教程延伸阅读均指向这些编号。

- [ ] **Step 1: 写入全文**

内容如下（从 test-plan §5/§7/§8/§9 蒸馏，矩阵行数 8+9+10，实测事实 12 条）：

```markdown
# 原型验证结论（三阶段）

- 日期：2026-09-07（蒸馏自 2026-08-31 / 09-01 / 09-03 三阶段验证记录，原稿见 git 历史 `docs/superpowers/specs/2026-08-31-excavator-prototype-test-plan.md`）
- 状态：三阶段全部通过
- 依据：docs/design/ 三份设计文档；证据截图 01–43 存 `gitlab-compose-test/screenshots/`

## 1. 三阶段验证矩阵

### 阶段一 · 平台与权限（2026-08-31）

| 验证项 | 设计章节 | 结果 |
|---|---|---|
| GitLab 部署与登录 | §8 阶段1 | ✅ |
| excavator 组结构（顶层+6子组） | §4.1 | ✅ |
| 三级权限模型 | §4.3 | ✅ |
| 保护分支禁直推 main | §4.2 | ✅ |
| MR 创建与评审 | §4.2/§3.2 | ✅ |
| 示例流水线全绿（include 通用层） | §6.2/§8 | ✅ |
| 制品追溯 manifest | §6.3 | ✅ |
| 界面可用性（截图 01–13） | §3.2 | ✅ |

### 阶段二 · 制品通道（2026-09-01）

| 验证项 | 设计章节 | 结果 |
|---|---|---|
| MinIO 三桶初始化 | §6.4 | ✅ |
| 大文件指针 + CI 取数校验（sha256） | §6.4 | ✅ |
| 现场投放区 write-only 回传 | §7.2 | ✅ |
| 投放区归档 | §7.2 | ✅ |
| 训练产物入库 + manifest 指针 | §6.3/§6.4 | ✅ |
| CI 凭据受保护 + 打码 | §6.5 | ✅ |
| Harbor 直推（build→push→pull） | §5.3/§6.4 | ✅ |
| Harbor 代理缓存拓扑 | §5.3 | ✅ |
| compose 全家 healthy（~15 服务） | — | ✅ |

### 阶段三 · 需求流（2026-09-03）

| 验证项 | 设计章节 | 结果 |
|---|---|---|
| Guest 按模板建单 | §4.1 | ✅ |
| 分诊三动作（移交/打回/婉拒） | §4.2 | ✅ |
| 里程碑排期 | §4.4 | ✅ |
| MR Closes 自动关单 | §5.1 | ✅ |
| tag/Release 挂里程碑 + manifest 资产 | §5.1 | ✅ |
| 反向三跳（manifest→commit→MR→单） | §5.2 | ✅ |
| 外部验收路径（缺陷单 待验证） | §4.3 | ✅ |
| 组看板状态列 | §6 | ✅ |
| 里程碑完成度（CE 按单数） | §6 | ✅ |
| 受理台积压视图 | §6 | ✅ |

## 2. 角色模拟验收（阶段一第二轮）

五类角色以真实身份（impersonation）走完典型工作流，全部通过：

| 角色 | 关键结论 |
|---|---|
| 开发工程师 dev1 | 直推 main 被拒；MR 全流程成立；CI 由红修绿 |
| 仓库 Owner maint1 | 评审/合入/打 tag/手动晋升/建 Release；**manifest.commit = main HEAD = tag commit = MR 合入 commit 四方一致** |
| 只读协作者 guest1 | Release 下载制品 ✅、clone 403 ✅；⚠️ 可读 CI job 日志（见 §3-3） |
| 平台工程 plat1 | 域 Maintainer 推 platform 仓库被 403——宪法变更权不扩散；模板变更下游零改动自动传播 |
| 驻场工程师（离线流） | 出场打包/现场核对/应急 24h 补 MR 全闭环 |

## 3. 关键实测事实（设计规则依赖的边界）

1. **通用层模板须对全体开发者可读**：dev1 在 platform 组无角色 → include 解析失败、流水线 0 job。修复：全员加 platform 组 Reporter(20)。正式实施固化进建组脚本。
2. **include ≠ 继承**：下游须 `extends: .firmware-template` 模板变更才传播；"不 include/不 extends 通用层的流水线不予合入"写进 MR 检查单。
3. **Guest 可读 CI job 日志**（CE 默认）：敏感变量全部设 Protected 缓解（仅受保护分支流水线可见）。
4. **include 在 pipeline 创建时快照解析，retry 不重解析**：模板热修后须触发新流水线验证。
5. **域 Maintainer 推 platform 仓库被 403**：权限分离按设计意图成立。
6. **Harbor 独立 compose**（非并入主 compose）：配置源 `harbor.yml` 入库即可复现，生成 compose 不入库（含随机密钥）。
7. **MinIO 拒 HTTP Basic（400）**：CI 的 curl 须 `--aws-sigv4` 签名（runner 内 curl 8.5.0 支持）。
8. **Harbor proxy 上游实测用 `docker.1ms.run`**（比预估的 hub.rat.dev 稳定）。
9. **Guest 无 label 权限**：来源/状态标签由分诊人代打（已回写需求流设计 §4.1，比"建单时选来源"更稳）。
10. **image-build 须 `only:[main,tags]`**：否则 MR 流水线因缺受保护变量必红；且 tag 须先过 `POST /protected_tags` 保护才可见受保护变量。
11. **组看板懒创建**：首次浏览器访问后 API 才能加列。
12. **root PAT 无 sudo 作用域**：扮演非 root 用户改用"管理员代建用户 PAT、用毕吊销"（作者身份保真）。

## 4. 不覆盖项（留正式实施）

- 谈判依赖项：DLP 两区模型（§5，需集团产品名）、VPN 场景（§7.4）、HIL 台架（§6.1）；
Harbor TLS/多租户/漏洞扫描、MinIO 分布式与备份策略、Nexus、GPU 真实训练（原型只验证拓扑与集成方式）。
- LDAP 真实域账号分诊轮值、`platform/` 标签字典 MR 管控实战、周例会看板纪律、四产品域并行、外部工具（禅道等）导出迁移。

## 5. 证据位置

- `gitlab-compose-test/screenshots/`：01–13 阶段一部署与权限，14–20 阶段一角色流，21–31 阶段二制品通道，32–43 阶段三需求流；
- 教程引用子集在 `docs/tutorials/assets/`；实例侧留档（intake 模板、firmware 示例等）在 `gitlab-compose-test/<repo名>/`。
```

- [ ] **Step 2: 自检**

Run: `grep -c '^| ' docs/design/2026-09-07-prototype-verification.md`
Expected: ≥ 33（8+9+10 矩阵行 + 5 角色行 + 表头行）

---

### Task 2: 删除过程文档与迁移设计文档（本任务不提交）

**Files:**
- Delete: `docs/superpowers/plans/2026-08-31-role-tutorials.md`、`2026-09-01-harbor-minio-phase2.md`、`2026-09-01-tutorials-phase2-sync.md`、`2026-09-03-requirement-flow-phase3.md`、`2026-09-03-tutorials-owner-platform-flow.md`、`2026-09-03-tutorials-phase3-sync.md`（均在该目录下）
- Delete: `docs/superpowers/specs/2026-08-31-excavator-prototype-test-plan.md`、`docs/superpowers/specs/2026-08-31-role-tutorials-design.md`
- Move: `docs/superpowers/specs/2026-08-31-excavator-code-management-design.md`、`2026-09-01-harbor-minio-phase2-design.md`、`2026-09-03-requirement-flow-design.md` → `docs/design/`（同名）

**Interfaces:**
- Consumes: Task 1 已建 `docs/design/`（目录已存在）。
- Produces: `docs/design/` 下三份设计文档——Task 3 全部相对链接的目标路径。

- [ ] **Step 1: git rm 8 个过程文件**

```bash
git rm docs/superpowers/plans/2026-08-31-role-tutorials.md \
       docs/superpowers/plans/2026-09-01-harbor-minio-phase2.md \
       docs/superpowers/plans/2026-09-01-tutorials-phase2-sync.md \
       docs/superpowers/plans/2026-09-03-requirement-flow-phase3.md \
       docs/superpowers/plans/2026-09-03-tutorials-owner-platform-flow.md \
       docs/superpowers/plans/2026-09-03-tutorials-phase3-sync.md \
       docs/superpowers/specs/2026-08-31-excavator-prototype-test-plan.md \
       docs/superpowers/specs/2026-08-31-role-tutorials-design.md
```

- [ ] **Step 2: git mv 三份设计**

```bash
git mv docs/superpowers/specs/2026-08-31-excavator-code-management-design.md docs/design/
git mv docs/superpowers/specs/2026-09-01-harbor-minio-phase2-design.md docs/design/
git mv docs/superpowers/specs/2026-09-03-requirement-flow-design.md docs/design/
```

- [ ] **Step 3: 验证**

Run: `git status --short && ls docs/design/`
Expected: 8 行 `D `、3 行 `R `（旧→新路径）、`?? docs/design/2026-09-07-prototype-verification.md`；design 目录含 4 个文件；`docs/superpowers/` 仅剩 specs 下 2026-09-07-doc-cleanup-design.md 与 plans 下本计划。

---

### Task 3: 引用修复（全集，本任务不提交）

**Files:**
- Modify: `docs/adr/` 全部 21 个 md（20 ADR + README）
- Modify: `docs/design/2026-09-01-harbor-minio-phase2-design.md`（6 处）、`docs/design/2026-09-03-requirement-flow-design.md`（2 处）
- Modify: `docs/tutorials/` 7 个 html（路径文本 + 小节指称）
- Modify: `gitlab-compose-test/docker-compose.yml:2`（注释）

**Interfaces:**
- Consumes: Task 1 的验证结论页章节编号（§1–§5）；Task 2 的新路径 `docs/design/`。

- [ ] **Step 1: ADR 19 个文件统一替换**

对以下 19 个文件（**不含 0019**，其 Step 2 单独处理；不含 README，其 Step 3 处理）各执行一次 `Edit replace_all`：
`0001 / 0002 / 0003 / 0004 / 0005 / 0006 / 0007 / 0008 / 0009 / 0010 / 0011 / 0012 / 0013 / 0014 / 0015 / 0016 / 0017 / 0018 / 0020`

old: `../superpowers/specs/`  new: `../design/`

- [ ] **Step 2: ADR-0019 特殊处理（先于任何统一替换）**

Edit 1（来源行）：
old: `- 来源：[原型验证计划](../superpowers/specs/2026-08-31-excavator-prototype-test-plan.md)、[Harbor/MinIO 二阶段设计 §2](../superpowers/specs/2026-09-01-harbor-minio-phase2-design.md)、[角色教程设计](../superpowers/specs/2026-08-31-role-tutorials-design.md)`
new: `- 来源：[原型验证结论](../design/2026-09-07-prototype-verification.md)、[Harbor/MinIO 二阶段设计 §2](../design/2026-09-01-harbor-minio-phase2-design.md)`

Edit 2（决策正文）：
old: `证据（截图、job 日志）编号入档，test-plan 表格化逐项 ✅；`
new: `证据（截图、job 日志）编号入档，验证结论页表格化逐项 ✅；`

- [ ] **Step 3: ADR README 决策来源 3 链**

old: `../superpowers/specs/`  new: `../design/`（replace_all，3 处）

- [ ] **Step 4: Harbor/MinIO 设计 6 处**

| 行 | old | new |
|---|---|---|
| 5 | `[原型验证计划](./2026-08-31-excavator-prototype-test-plan.md) §0"Harbor/MinIO ⏸ 第二阶段"` | `[原型验证结论](./2026-09-07-prototype-verification.md) §0 所引设计初版（Harbor/MinIO 二阶段前为 ⏸）` |
| 23 | `跑通 + 截图入档 + test-plan 更新` | `跑通 + 截图入档 + 验证结论页更新` |
| 77 | `记录"代理拓扑成立、上游连通性受本机环境限制"入 test-plan` | `记录"代理拓扑成立、上游连通性受本机环境限制"入验证结论页` |
| 79 | `兜底恢复命令写入 test-plan` | `兜底恢复命令写入验证结论页` |
| 92 | `test-plan 新增"第二阶段验证结果"章节` | `验证结论页收录第二阶段结果` |
| 100 | `5. test-plan 更新、提交。` | `5. 验证结论页更新、提交。` |

- [ ] **Step 5: 需求流设计 2 处**

| 行 | old | new |
|---|---|---|
| 41 | `Guest 无 label 权限（三阶段实测，test-plan 9.3-1）` | `Guest 无 label 权限（三阶段实测，验证结论 §3-9）` |
| 145 | `- test-plan 新增"第三阶段验证结果"章节；` | `- 验证结果入档（原型验证结论 §1 阶段三）；` |

- [ ] **Step 6: 教程 7 页路径与指称**

统一规则（各页 replace_all）：`docs/superpowers/specs/2026-08-31-excavator-code-management-design.md` → `docs/design/2026-08-31-excavator-code-management-design.md`；`docs/superpowers/specs/2026-09-03-requirement-flow-design.md` → `docs/design/2026-09-03-requirement-flow-design.md`；`docs/superpowers/specs/2026-08-31-excavator-prototype-test-plan.md` → `docs/design/2026-09-07-prototype-verification.md`。

路径替换后，各页"原型验收"清单项指称修正（新页无旧节号）：

| 页 | old 清单项 | new 清单项 |
|---|---|---|
| viewer | `§7.2 逐角色模拟验收——驻场工程师取制品走的就是你这条同款通道` | `§2 角色模拟验收——驻场工程师取制品走的就是你这条同款通道` |
| viewer | `§8 第二阶段验证结果（Harbor/MinIO 接入）` | `§1 阶段二矩阵（Harbor/MinIO 接入）` |
| field-engineer | `§7.3 闭环实测（应急改动 24h 补 MR）` | `§2 角色模拟验收·驻场（应急改动 24h 补 MR 闭环）` |
| field-engineer | `§8.2 现场投放区 write-only 回传（二阶段验证）` | `§1 阶段二矩阵（现场投放区 write-only 回传）` |
| submitter | `§9 三阶段验证结果（四场景证据链，截图 32–43）` | `§1 阶段三矩阵（四场景证据链，截图 32–43）` |
| platform | `§7.3 全部五条实测发现` | `§3 实测事实（阶段一全部五条）` |
| platform | `§8 第二阶段验证结果（Harbor/MinIO 九项全 ✅）` | `§1 阶段二矩阵（Harbor/MinIO 九项全 ✅）` |

platform.html 正文 1 处：
old: `这个坑三阶段实测踩过（test-plan 9.1）`
new: `这个坑三阶段实测踩过（验证结论 §3-11）`

- [ ] **Step 7: docker-compose.yml 注释**

old: `# 对应设计文档：docs/superpowers/specs/2026-08-31-excavator-code-management-design.md`
new: `# 对应设计文档：docs/design/2026-08-31-excavator-code-management-design.md`

- [ ] **Step 8: 全库复核**

Run: `grep -rn 'superpowers' docs/adr docs/design docs/tutorials gitlab-compose-test/docker-compose.yml | grep -v '2026-09-07-doc-cleanup\|git 历史'`
Expected: 无输出（验证结论页头部"原稿见 git 历史"一句含 superpowers 字样，属有意保留的出处注记，用 `git 历史` 过滤）。

---

### Task 4: 回归验证 + commit ①（删+迁+修链）

- [ ] **Step 1: 教程自检**

Run: `python3 docs/tutorials/check.py index.html developer.html owner.html viewer.html platform.html field-engineer.html submitter.html`（在仓库根执行；check.py 以脚本所在目录为基准解析文件名，不依赖 cwd）
Expected: 7 行 `[OK]`，退出码 0。

- [ ] **Step 2: 展示并求确认**

向用户展示 `git status --short` 与 `git diff --stat`（8 删 + 3 迁 + 21 ADR + 2 设计 + 7 教程 + 1 compose）。**等待明确同意**。

- [ ] **Step 3: 提交（获确认后）**

```bash
git add docs/adr docs/tutorials gitlab-compose-test/docker-compose.yml \
       docs/design/2026-08-31-excavator-code-management-design.md \
       docs/design/2026-09-01-harbor-minio-phase2-design.md \
       docs/design/2026-09-03-requirement-flow-design.md \
       docs/superpowers/plans/2026-09-07-doc-cleanup.md
git commit -m "docs: 过程文档清理与设计归位——删8过程文件，设计迁入docs/design，全库引用改指

Co-Authored-By: Claude Code <noreply@anthropic.com>"
```

add 范围说明：**不含**验证结论页（untracked，随 commit ② 入库，①②相邻落地无长期悬空）；**含**本计划文件（否则 Task 9 的 `git rm` 对未跟踪文件必失败）。

---

### Task 5: 根 README + commit ②

**Files:**
- Create: `README.md`（仓库根）
- Add: `docs/design/2026-09-07-prototype-verification.md`（Task 1 产物）

- [ ] **Step 1: 写入 README 全文**

````markdown
# 智能挖机 · 统一代码管理体系

50+ 人多团队（固件 / 算法 / 车载 / 云端 / App）的代码托管、CI/CD、制品与需求流体系。平台为自建 GitLab CE 一体化，已在本地原型上三阶段实证；设计在与集团 DLP / VPN 管理框架共存的前提下自洽可独立落地，并预留向集团设施迁移的接口。

## 阅读地图

| 你是谁 | 读什么 |
|---|---|
| 评审者 / 干系人 | `docs/design/` 三份设计（决策事实来源）→ `docs/adr/` 20 条决策记录 → `docs/design/2026-09-07-prototype-verification.md` 验证结论 |
| 团队成员（任一角色） | `docs/tutorials/index.html`——按角色 5–10 分钟上手 |
| 平台运维 / 复现环境 | `gitlab-compose-test/`（compose 栈 + 截图脚本 + 证据 01–43） |

## 目录

```
docs/
├── design/       三份设计文档 + 原型验证结论（本体系的事实来源）
├── adr/          20 条架构决策记录 + 索引（含否决备选与重开条件）
└── tutorials/    六角色上手教程（HTML，含截图）
gitlab-compose-test/  本地原型环境：compose 栈、示例仓库、截图证据
```

## 原型环境速览

GitLab CE 19.3.1 @ http://10.66.35.35:8081（docker compose 栈，含 Runner / MinIO / Harbor）。教程截图与验证证据均出自该实例；凭据不入库。
````

- [ ] **Step 2: 链接存在性验证**

Run: `test -f docs/design/2026-09-07-prototype-verification.md && test -f docs/tutorials/index.html && test -f docs/adr/README.md && echo OK`
Expected: `OK`

- [ ] **Step 3: 展示并求确认 → 提交（获确认后）**

```bash
git add README.md docs/design/2026-09-07-prototype-verification.md
git commit -m "docs: 新增根README阅读地图+原型验证结论页（三阶段矩阵/12条实测事实/不覆盖项）

Co-Authored-By: Claude Code <noreply@anthropic.com>"
```

---

### Task 6: 精炼 · 三份设计文档（交互式）

**Files:**
- Modify（经确认后）: `docs/design/` 三份设计

**Interfaces:**
- Consumes: Task 4 后的重组完成态。
- Produces: 每份文档一份经用户确认的精炼结果；commit ③a/③b/③c。

- [ ] **Step 1: 逐份评审报告（会话内呈现，不入库）**

对每份设计按三维度出发现清单，格式：

```
### <文档名>（现 N 行 → 预计 M 行）
| # | 位置 | 类型(删/并/改写) | 发现 | 处置建议 |
```

审查重点：背景铺垫是否可压（读者=发起人+内部）；同一规则是否在多节重复；表格与正文信息是否重复；交叉引用编号是否与现结构一致；被验证结论页接管的细节（实测过程类）是否可瘦身。

- [ ] **Step 2: 用户逐处确认**（可整体接受 / 逐条勾选 / 否决）

- [ ] **Step 3: 执行修改**（仅动获确认项）

- [ ] **Step 4: 展示 diff → 确认 → commit**（每份一个 commit，信息如 `docs(design): 统一管理体系精炼——背景压缩/重复合并（N→M行）`）

---

### Task 7: 精炼 · ADR 21 文件（交互式）

- [ ] **Step 1: 全量通读 20 ADR + 索引，出汇总评审报告**（ADR 较新，预期发现少——如实报"无需改动"也是合法结论，不硬凑发现）

报告格式（每文件一小节，汇总放同一份报告）：

```
### ADR-00NN（现 N 行）
| # | 位置 | 类型(删/并/改写) | 发现 | 处置建议 |
```

重点：六节结构完整性；一句话决策与正文是否一致；来源链接有效性（应为 `../design/`）；索引表与各 ADR 标题/状态是否一致。

- [ ] **Step 2: 用户确认 → 修改 → 展示 diff → 确认 → 单个 commit**

---

### Task 8: 精炼 · 教程 7 页（交互式，只内容不动样式）

- [ ] **Step 1: 逐页评审报告**（重点：延伸阅读指称与新版文档结构一致；步骤冗余；页间重复段落是否该收敛为链接；红线/提示框是否被正文重复）

- [ ] **Step 2: 用户确认 → 修改**

- [ ] **Step 3: 回归**

Run: `python3 docs/tutorials/check.py index.html developer.html owner.html viewer.html platform.html field-engineer.html submitter.html`
Expected: 7 行 `[OK]`

- [ ] **Step 4: 展示 diff → 确认 → 单个 commit**

---

### Task 9: 收尾自清与完成判定

- [ ] **Step 1: 完成判定复核**

Run: `grep -rn 'superpowers\|test-plan\|role-tutorials' README.md docs/ gitlab-compose-test/docker-compose.yml | grep -v 'git 历史\|2026-09-07-doc-cleanup'`
Expected: 无输出（两个 2026-09-07 工作文件此时仍在库，Step 2 自清后即彻底归零，过滤项对应规格 §7 的豁免）。
Run: `python3 docs/tutorials/check.py index.html developer.html owner.html viewer.html platform.html field-engineer.html submitter.html`
Expected: 全 OK。
确认：三份设计、ADR、教程各有一份经确认的精炼结果。

- [ ] **Step 2: 自清（过程文档不留）**

```bash
git rm docs/superpowers/specs/2026-09-07-doc-cleanup-design.md docs/superpowers/plans/2026-09-07-doc-cleanup.md
```

- [ ] **Step 3: 展示 → 确认 → 最终 commit**

```bash
git commit -m "docs: 文档梳理完成——清理本次工作设计/计划（过程文档不留，成果为重组后的docs结构与精炼后的主文档）

Co-Authored-By: Claude Code <noreply@anthropic.com>"
```

- [ ] **Step 4: 提示用户**：plans 里明文 PAT 已退出 HEAD，git 历史仍在——建议在实例上作废该 root PAT（规格 §3.4，超出文档范围）。
