# 计划：运营（顶层组 Owner）从 ops.html 拆出独立页

> 状态：plan-mode 草案，待批准。本计划**覆盖 spec `2026-09-10-tutorials-ia-rework-design.md` line 27「运营人员不新造页，卡片指 ops.html#gov，长大再拆」**——现据账号边界（运维=root/实例管理员，运营=顶层组 Owner）提前执行该拆分。

## 0. 决策与依据（已与用户确认）

- 4a（一次性建立：建组树/仓库/保护分支/看板/需求流配置）**归运营**：顶层组 Owner 用 Owner token 即可建子组、建仓、设保护分支、配看板，无需 root（root 只用于创建顶层组 intel_excavator 本身，那是运维的交接步）。
- 故 4a + 4b 整体迁 governance.html；ops.html 只留"建实例 + 建顶层组 + 授权 Owner 给项目负责人"的交接步。
- 内容纪律：事实性内容**只搬不改**，从现 ops.html 4a/4b 搬迁并按运营口吻重排，引用同一套 §/ADR 锚点，**不引入新事实**（承袭 spec line 70 口径）。

## 1. 新建 `docs/tutorials/governance.html`（运营 / 顶层组 Owner）

页型套现教程房风（CSS 复制 developer.html），check.py 登记页型 `governance`（见 §3）。

**骨架（h2）**：你是谁 → 你能做什么 / 不能做什么 → 治理主线 → 持续治理 → 红线清单 → 延伸阅读。

- **hero**：crumb `← 返回角色导航`→index.html；h1「运营上手指南」；tagline「搭并治组树——子组 · 授权 · 里程碑」；badge「顶层组 Owner」。
- **你是谁**：你是拿着顶层组 intel_excavator 的项目负责人（顶层组 Owner）。运维把实例与顶层组建好、把你设为 Owner 后，组树之下都归你。与运维（root）的边界：你治组树（建子组/仓库/保护分支/看板、授权变更、里程碑），不碰实例（起栈/改 compose/DB 直改/开号封禁是运维的，见 ops.html）。若你兼平台维护人，实例侧读 ops.html。
- **能做 / 不能做**（新写小表）：
  - ✅ 建子组与仓库、配保护分支、配组看板、授权变更（Owner token）、里程碑命名归组、需求流收口配置
  - ❌ 起栈/改 compose、root 改密/DB 直改、开号封禁（运维，见 ops.html）；改 CI 宪法模板（走 platform 组 MR，见 platform.html）；直接 push main
- **治理主线：搭起组树**（4a 重排为运营步骤，素材逐条来自 ops.html 4a）：
  1. 建组树（ADR-0003）：顶层组=项目，子组=产品域 `firmware/autonomy/vehicle/cloud/app/platform`，子组内建仓；`platform/` 是宪法组。UI 建组或 API `POST /api/v4/groups`。图 `assets/03-groups.png`。
  2. 配权限（ADR-0004/0005）：三级授权表（Guest/Reporter 只读 · Developer push+MR · Maintainer 合 MR+保护分支=每仓 1–2 名 Owner）；顶层 Owner 由项目负责人持有。注意**账号由运维开**（关注册，见 ops.html §6.1），权限你授——账号 ≠ 权限。
  3. 建仓与保护分支（ADR-0006）：子组内建仓、每仓指定一名 Owner；trunk-based（main 常绿 + 短命特性分支 + MR 合入）；保护分支禁直接 push；发布周期长的留 `release/x.y`；入库门槛——用途说不清的代码不入库。图 `assets/10-protect.png`。
  4. 需求流与看板（ADR-0015–0017）：建 `intake` 收口仓库承接需求/现场问题；标签分诊、里程碑归组、跨仓 transfer 走原生；组看板配六状态列。**坑位**：组看板懒创建，配置前须先浏览器访问过看板页。图 `assets/41-group-board.png`。
  5. CI 宪法（指针，不展开）：`platform/ci-templates` 由 platform 组 Maintainer 维护（见 platform.html）；你需确保下游仓库 `.gitlab-ci.yml` 以 `include: project:` 引用通用层——**未 include 通用层的流水线 MR 不予合入**（制度 + 自检双保险）。
- **持续治理**（4b 扩写，素材来自 ops.html 4b + §5.2/§5.5 尾注）：
  - 授权变更一律走 API 并留存脚本日志——**免费版无审计能力，脚本是唯一留痕**
  - 新产品域 = 新子组：按产品域建组，团队重组不动组树
  - 里程碑命名如「固件 v2.3·2026Q4」，版本节点跨仓库生效。图 `assets/42-milestone-progress.png`。
- **红线清单**：
  - 🚫 授权变更不留痕＝没发生（免费版无审计，API 脚本是唯一留痕）
  - 🚫 组树按产品域、不按团队（团队重组不动组树）
  - 🚫 未 include 通用层的流水线 MR 不予合入
- **延伸阅读**：design §4.1（组树）/§4.3（权限）/§6.2（CI）= docs/design/2026-08-31-excavator-code-management-design.md；需求流设计 = docs/design/2026-09-03-requirement-flow-design.md；ADR-0003/0004/0005/0006/0015/0016/0017 = docs/adr/；→ ops.html（建实例+顶层组+授权）；→ platform.html（CI 宪法）；→ owner.html（域级分诊与发布）；→ submitter.html（提单与看板追进度）。
- **footer**：注明本页为 ops.html「组织与治理」章拆出（spec line 27「长大再拆」本次执行），设计文档同 ops.html。

## 2. 改 `docs/tutorials/ops.html`（瘦身为实例管理员/纯运维）

- **hero**：不变（h1 运维上手指南、tagline 起栈·开号·封禁·备份、badge 实例管理员）。
- **你是谁**（line 72）：删去「若你是拿着顶层组的运营（项目负责人），直接从 #gov 进入」分叉句；改为纯运维定位，末尾加一句"组树搭建与持续治理由顶层 Owner 完成，见 governance.html"。
- **实施主线 第 4 步**（line 136–174，id=gov）：4a/4b 整体迁出。改写为运维交接步：
  - h3 改「建顶层组与授权交接」（保留 `id="gov"`，无活链入但保留无害）。
  - 内容：用 admin token 建顶层组 intel_excavator（UI 或 `POST /api/v4/groups`）；把项目负责人设为顶层组 Owner；**此后组树/仓库/保护分支/看板/需求流配置与持续治理转交运营，见 governance.html**。
  - 删除现 4a（5.1–5.5）与 4b 全部内容。
- **第 5 步 转入日常**（line 177–178）：桥接段微调，把"日常动作"指向保留的查阅区（架构表/日常运维/原型复现/已知坑位），不动其它。
- **查阅：已知坑位**（line 347）：`凡脚本化操作（含 4a 的 API 批量建组树）` → 改指 `含 governance.html 的 API 批量建组树`（4a 已迁出，原指失效）。
- **查阅：架构与组件表 / 日常运维 / 原型复现 / 红线 / 延伸**：均不动（运维/实例领域）。
- **footer**：补一行 sibling 指向 governance.html。

## 3. 改 `docs/tutorials/index.html`（运营卡改指）

- 运营人员卡（line 87）：`href="ops.html#gov"` → `href="governance.html"`。文案/badge 不动（"组树 · 授权 · 里程碑"仍准）。
- 其余不动（通用入门已是极简两步、术语速查重排均为本会话外已落定）。

## 4. 改 `docs/tutorials/check.py`（登记新页型）

- `SKELETON` 增 `"governance": ["你是谁", "能做", "治理", "红线", "延伸"]`（h2 文案含"治理主线""持续治理"均命中"治理"片段）。
- `pagetype()` 现逻辑 `name.replace(".html","")` 已产出 `"governance"`，无需改。
- 图片下限：governance 非-index/ops，须 ≥2 图——本计划 4 张（03/10/41/42），满足。

## 5. 联动核查（边改边查）

- **README.md**（line 11 现合指 ops.html）：裂成两行——「平台运维」→ `docs/tutorials/ops.html`（建实例 + 日常运维查阅）；「运营（顶层 Owner）」→ `docs/tutorials/governance.html`（搭并治组树）。line 10（团队成员→index）与 line 19（三轨角色教程）不动；九卡不变仍是 9 卡。
- **compose 注释**：spec line 84 指 `#arch`/`#run`，不涉 #gov，**无需改**。
- **入链 grep**：`grep -rn "ops.html#gov\|#gov" docs/` 须只剩 archival（specs/plans）+ ops.html 自身 `id="gov"`；活链仅原 index.html:87（本次改走）。

## 6. 验收

1. `cd docs/tutorials && python3 check.py index.html developer.html owner.html viewer.html platform.html field-engineer.html submitter.html ops.html governance.html` 全绿（9 页）。
2. `grep -rn "ops.html#gov" docs/tutorials/` 仅 ops.html 自身无（运营卡已走 governance.html）；`grep -rn "governance.html" docs/tutorials/` 命中 index 运营卡 + ops 你是谁/footer 两处指向。
3. ops.html SKELETON 仍全（你是谁/能做/实施主线/查阅/红线/延伸）；step4 已瘦身为交接步、4a/4b 内容不再出现。
4. governance.html 事实性内容与 ops.html 原 4a/4b 一致（§/ADR 锚点齐全），无新事实。
5. assets 引用全部存在（03/10/41/42 均在 assets/）。

## 7. 不做（out of scope）

- platform.html / owner.html / submitter.html / viewer.html / developer.html / field-engineer.html 内容不动。
- 通用入门、术语速查不动。
- ops.html 查阅层（架构表/日常运维/原型复现/已知坑位）事实不动；红线/延伸基本不动。
- 提交留待用户确认后（依用户全局规则：commit 前展示内容等确认）。
