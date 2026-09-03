# 教程同步三阶段（需求流）Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 按需求流设计 §8 交付物收尾教程——新增第 6 篇《需求提出人与管理者》、小幅扩展 developer/field-engineer 两篇、回收 dev1 遗留 token，全部复用三阶段验证截图 32–43（不补拍）。

**Architecture:** 文档为主的计划：先改两个 spec（需求流 §4.1 打标回写 + 教程 spec 六篇化），再一个独立活实例 API 任务回收 token，然后三个 HTML 任务（新篇 + 两处扩展）逐任务提交，最后全站 footer 三阶段化 + 全量自检。教程内容全部锚定 test-plan §9.2 已验证路径与截图。

**Tech Stack:** 静态 HTML（内联 CSS、无 JS）+ GitLab API v4（curl）+ check.py 静态自检。

**依据：**
- 设计：`docs/superpowers/specs/2026-09-03-requirement-flow-design.md` §8 交付物（教程三项）
- 验证证据：`docs/superpowers/specs/2026-08-31-excavator-prototype-test-plan.md` §9.2/§9.3
- 教程 spec：`docs/superpowers/specs/2026-08-31-role-tutorials-design.md`
- 前例：`docs/superpowers/plans/2026-09-01-tutorials-phase2-sync.md`（同套路：先 spec 后教程、截图复用、逐图核对）

## Global Constraints

- 教程 HTML 双击即开：全中文、内联 CSS、无 JS、无外部资源（check.py 强制，违规即 FAIL）
- 教程不臆造：每条新增操作/规则必须能回溯 test-plan §9.2 验证项或需求流设计 §4–§7；分诊/排期/合码的操作细节不写进第 6 篇（提单人视角只讲"单的去向"）
- 图注逐字对齐：每张新引入截图必须用 Read 查看原图，图注与图中可见状态逐字一致；不一致时**改图注、不改图、不重拍**（phase-1 终审 a9781ca 同款要求）
- 截图只复用不补拍：本计划引入 9 张（32/33/34/36/37/39/41/42/43）；35/38/40 不复用（38 有图文已知分歧 test-plan 9.3-7）
- 工作直接在 main、不推远端（用户既定选择）；提交用 conventional 前缀
- GitLab API base `http://10.66.35.35:8081/api/v4`；root PAT 从 `docs/superpowers/plans/2026-09-03-requirement-flow-phase3.md` 提取，**必须 `tail -1`**（行 13 有截断版）：
  `T=$(grep -oP 'T=glpat-\S+' docs/superpowers/plans/2026-09-03-requirement-flow-phase3.md | tail -1 | cut -d= -f2)`
- **PAT 不写进任何将提交的文件**（含本计划后续修改、提交信息、test-plan 记档）
- shell 变量跨 Bash 调用不保留：每个 Step 自带 `$T` 提取或重 export
- 三阶段截图已核实为真实 PNG（1440×900 逻辑尺寸，浏览器 2x 缩放实际 2880×1800 左右）；33 显示 @guest1 的单带 `状态::待受理` 标签、41 显示看板六列（待受理/已排期/开发中/待验证/已关闭/已拒绝）——图注以此为基准

---

### Task 1: Spec 先行——需求流 §4.1/§4.2 打标回写 + 教程 spec 六篇化

**Files:**
- Modify: `docs/superpowers/specs/2026-09-03-requirement-flow-design.md`（§4.1 一处、§4.2 一处）
- Modify: `docs/superpowers/specs/2026-08-31-role-tutorials-design.md`（素材行/§1/§2/§5/§6/§8 共十处）

**Interfaces:**
- Consumes: test-plan 9.3-1（Guest 无打标权限偏差）、9.3-7（38 图文分歧）
- Produces: 教程 spec §5.6 submitter 大纲与 §6 截图分配行——Task 3/4/5 据此实现；需求流设计 §4.1 打标规则——Task 3 的 submitter.html"不能打标"表述与图 33/34 图注依据

- [ ] **Step 1: 需求流设计 §4.1 来源打标回写（9.3-1）**

`2026-09-03-requirement-flow-design.md` 第 41 行，old → new：

```markdown
- **来源打标**：建单时选 `来源::集团 / 市场 / 客户 / 现场 / 内部` scoped 标签，将来统计需求来源构成有数据可依。
```
改为：
```markdown
- **来源打标**：提单人不打标——Guest 无 label 权限（三阶段实测，test-plan 9.3-1），`来源::集团 / 市场 / 客户 / 现场 / 内部` 由分诊人在分诊时代打，将来统计需求来源构成有数据可依。
```

- [ ] **Step 2: 需求流设计 §4.2 分诊动作补打标**

第 48 行，old → new：

```markdown
- 动作三个：**移交**（move 到对应域仓库，评论与链接全保留）／**打回**（信息不足退回补充）／**婉拒**（重复或超范围，说明理由关闭）；
```
改为：
```markdown
- 动作三个：**移交**（move 到对应域仓库，评论与链接全保留）／**打回**（信息不足退回补充）／**婉拒**（重复或超范围，说明理由关闭）；分诊时代打 `来源::`/`状态::` 标签（Guest 无打标权限，§4.1）；
```

- [ ] **Step 3: 教程 spec 素材行**

`2026-08-31-role-tutorials-design.md` 第 6 行，old → new：

```markdown
- 素材：一阶段 20 张 + 二阶段 11 张（21–31）原型截图，均复用验证证据、不补拍；二阶段截图于 2026-09-01 验证（test-plan §8）后纳入
```
改为：
```markdown
- 素材：一阶段 20 张 + 二阶段 11 张（21–31）+ 三阶段 9 张复用（32–43 中选 9）原型截图，均复用验证证据、不补拍；二阶段截图于 2026-09-01 验证（test-plan §8）、三阶段于 2026-09-03 验证（test-plan §9）后纳入
```

- [ ] **Step 4: 教程 spec §1 六篇化**

第 10 行 `为五类角色各写一份自包含 HTML 入门教程，外加一个角色导航索引页。` 改为 `为六类角色各写一份自包含 HTML 入门教程（五类代码侧 + 需求侧"需求提出人与管理者"），外加一个角色导航索引页。`

文件树（第 13–21 行）中 `├── field-engineer.html     # 驻场工程师（离线工作流）` 之后插入一行：
```
├── submitter.html         # 需求提出人与管理者（提单 + 看板视角，三阶段新增）
```
并把 `└── assets/                 # 20 张截图的副本（复制，非软链）` 改为 `└── assets/                 # 截图的副本（复制，非软链）`。

- [ ] **Step 5: 教程 spec §2 决策表**

`| 交付形态 | 5 个独立 HTML + 1 个索引页 |` 改为 `| 交付形态 | 6 个独立 HTML + 1 个索引页 |`

- [ ] **Step 6: 教程 spec §5.1/§5.5 大纲补三阶段条目**

§5.1 developer 大纲末尾（第 66 行 `- 红线：不上明文密钥…` 之前）插入：
```markdown
- 三阶段扩展（提单/关联单号）：MR 描述写 `Closes #单号` + 选里程碑，模板四项自查 checklist；红线"无单不开发"（需求流 §7.1）；用图 36（三阶段）
```
§5.5 field-engineer 大纲末尾（第 104 行 `- 红线：改动不以 commit 回中心仓…` 之前）插入：
```markdown
- 三阶段扩展（manifest 建缺陷单）：现场缺陷回受理台按缺陷模板建单、manifest 整段粘贴进专区——后方三跳回溯（需求流 §5.2）；用图 39（三阶段）
```

- [ ] **Step 7: 教程 spec 新增 §5.6 submitter 大纲、原 §5.6 index 改 §5.7**

在第 105 行 `### 5.6 index.html — 角色导航 + 通用入门` 之前插入新节（index 节标题号改为 5.7）：
```markdown
### 5.6 submitter.html — 需求提出人与管理者（三阶段新增）

（本节 § 指向《产研需求流设计》2026-09-03）

- 双读者：提单人（市场/客服/集团接口人，Guest 10，只提单不管代码）+ 管理者（Reporter 20，例会看板投屏）
- 任务流 A 提一张单：受理台选模板 → 填三段拿单号 → 等分诊（移交/打回/婉拒；标签由分诊代打）→ 合入自动关单不用催
- 任务流 B 例会三屏：组看板状态列 → 里程碑过滤与完成度 → 受理台积压
- 用图：32-intake-template-form、33-intake-issue-filed、34-issue-transferred、37-issue-auto-closed（提单线）；41-group-board、42-milestone-progress、43-intake-backlog（管理线）
- 🔍 为什么只进一个口（§4.1）／为什么验收标准必填（§7.3）／为什么 3 日 SLA（§4.2）／为什么不用催（§5.1）／例会只看板（§6）
- 自救：单被打回 / 单被婉拒 / 找不到入口 / 查历史单进度
- 红线：群里口头提需求不算数、不贴客户商务细节（§7.3）、管理者不绕过分诊派活（§4.4）
```

- [ ] **Step 8: 教程 spec §6 截图分配表**

第 116 行统计行末尾追加（括号内）：`三阶段复用 9 张（32/33/34/36/37/39/41/42/43）；35/40 叙事由文字承载不复用，38-release-milestone 因图文已知分歧（test-plan 9.3-7）不复用。`

表格末尾（第 130 行后）追加四行：
```markdown
| 32-intake-template-form, 33-intake-issue-filed, 34-issue-transferred, 37-issue-auto-closed | submitter 提单线（三阶段） |
| 41-group-board, 42-milestone-progress, 43-intake-backlog | submitter 管理线（三阶段） |
| 36-mr-closes-issue | developer 关联单号（三阶段） |
| 39-defect-manifest | field-engineer 现场缺陷提单（三阶段） |
```

- [ ] **Step 9: 教程 spec §8 YAGNI 追加两条**

末尾追加：
```markdown
- 第 6 篇不写成需求管理手册——分诊/排期/合码操作属 Owner/developer 教程与设计文档范畴，提单人视角只讲"单的去向"
- 不复用 35/38/40 三阶段截图（打回婉拒以文字承载、38 图文已知分歧 test-plan 9.3-7、40 反向三跳细节回溯 test-plan §9）
```

- [ ] **Step 10: 核对与提交**

Run: `git diff --stat` 应显示仅 2 个 spec 文件变更；人工复查上述 10 处全部落位。

```bash
git add docs/superpowers/specs/2026-09-03-requirement-flow-design.md docs/superpowers/specs/2026-08-31-role-tutorials-design.md
git commit -m "docs(specs): 教程spec六篇化+需求流§4.1打标回写（9.3-1采纳）"
```

---

### Task 2: 遗留收口——回收 dev1-ci/dev1-push token（id 3/4）并记档

**Files:**
- Modify: `docs/superpowers/specs/2026-08-31-excavator-prototype-test-plan.md`（§9.3 追加第 9 条）

**Interfaces:**
- Consumes: root PAT（phase3 计划行 36，`tail -1` 提取）；三阶段收口报告"范围外观察"记录（.superpowers/sdd/final-fix-report.md）
- Produces: 实例上 dev1 名下无 active PAT；test-plan 9.3-9 记档条目（Task 6 全量自检不再涉及）

背景：两枚 token 为一阶段预置，仓库内无引用（本地 firmware-repo/intake-repo/perception-repo 均非 git 仓库、无 credential helper；项目/组/实例三级 CI 变量均为空——Task 执行时复核）。

- [ ] **Step 1: 安全前置复核（三级 CI 变量为空 + token 现状）**

```bash
cd /home/lancer/projects/frm
T=$(grep -oP 'T=glpat-\S+' docs/superpowers/plans/2026-09-03-requirement-flow-phase3.md | tail -1 | cut -d= -f2)
G=http://10.66.35.35:8081/api/v4
curl -s -H "PRIVATE-TOKEN: $T" "$G/user" | python3 -c 'import json,sys;print(json.load(sys.stdin)["username"])'
```
Expected: `root`

```bash
T=$(grep -oP 'T=glpat-\S+' docs/superpowers/plans/2026-09-03-requirement-flow-phase3.md | tail -1 | cut -d= -f2)
G=http://10.66.35.35:8081/api/v4
for u in projects/2/variables groups/2/variables admin/ci/variables; do curl -s -H "PRIVATE-TOKEN: $T" "$G/$u"; echo " <- $u"; done
```
Expected: 三行均 `[] <- …`（无任何 CI 变量引用这两枚 token）

```bash
T=$(grep -oP 'T=glpat-\S+' docs/superpowers/plans/2026-09-03-requirement-flow-phase3.md | tail -1 | cut -d= -f2)
curl -s -H "PRIVATE-TOKEN: $T" "http://10.66.35.35:8081/api/v4/personal_access_tokens?user_id=2" \
 | python3 -c 'import json,sys;[print(t["id"],t["name"],"active="+str(t["active"])) for t in json.load(sys.stdin)]'
```
Expected: `3 dev1-ci active=True`、`4 dev1-push active=True`（5/12/14 已 revoked）

- [ ] **Step 2: 回收（DELETE；9.3-4 记录本实例 PUT 404、DELETE 204）**

```bash
T=$(grep -oP 'T=glpat-\S+' docs/superpowers/plans/2026-09-03-requirement-flow-phase3.md | tail -1 | cut -d= -f2)
G=http://10.66.35.35:8081/api/v4
curl -s -o /dev/null -w '%{http_code}\n' -H "PRIVATE-TOKEN: $T" -X DELETE "$G/personal_access_tokens/3"
curl -s -o /dev/null -w '%{http_code}\n' -H "PRIVATE-TOKEN: $T" -X DELETE "$G/personal_access_tokens/4"
```
Expected: 两行均 `204`（若 202/404，停下按 9.3-4 排查，勿盲试 PUT）

- [ ] **Step 3: 复核无残留**

重跑 Step 1 第三条命令。Expected: `3 dev1-ci active=False`、`4 dev1-push active=False`（其余不变）。

- [ ] **Step 4: test-plan §9.3 追加第 9 条**

`2026-08-31-excavator-prototype-test-plan.md` §9.3 第 8 条之后追加：
```markdown
9. **dev1 名下基础设施 token 回收**：`dev1-ci`/`dev1-push`（id 3/4，一阶段预置）经查三级 CI 变量、本地仓库均无引用，已于三阶段教程收尾时 DELETE 回收（204×2，复核 revoked）——遗留 active PAT 清零（root 工作 PAT 见三阶段计划，2026-10-01 到期）。
```

- [ ] **Step 5: 提交**

```bash
git add docs/superpowers/specs/2026-08-31-excavator-prototype-test-plan.md
git commit -m "chore(instance): 回收dev1-ci/dev1-push遗留token（id 3/4）——test-plan 9.3-9记档"
```

---

### Task 3: 新建第 6 篇 submitter.html + index 接入 + check.py 骨架 + 7 张截图

**Files:**
- Create: `docs/tutorials/submitter.html`
- Modify: `docs/tutorials/index.html`（卡片/术语/入口框/footer）
- Modify: `docs/tutorials/check.py`（SKELETON 加 submitter 行）
- Create: `docs/tutorials/assets/` 下复制 7 张：`32-intake-template-form.png`、`33-intake-issue-filed.png`、`34-issue-transferred.png`、`37-issue-auto-closed.png`、`41-group-board.png`、`42-milestone-progress.png`、`43-intake-backlog.png`

**Interfaces:**
- Consumes: Task 1 的 spec §5.6 大纲；截图源 `gitlab-compose-test/screenshots/`
- Produces: `submitter.html`（Task 6 全量自检对象之一）；`assets/3x/4x` 系列图（Task 4/5 各自复制 36/39，不与本任务重叠）

- [ ] **Step 1: 复制截图并核验为真实 PNG**

```bash
cd /home/lancer/projects/frm
for n in 32-intake-template-form 33-intake-issue-filed 34-issue-transferred 37-issue-auto-closed 41-group-board 42-milestone-progress 43-intake-backlog; do
  cp "gitlab-compose-test/screenshots/$n.png" docs/tutorials/assets/
done
file docs/tutorials/assets/3*.png docs/tutorials/assets/4*.png
```
Expected: 每行含 `PNG image data`（共 7 行，无 38）

- [ ] **Step 2: 逐张 Read 核对图注基准**

用 Read 依次查看 7 张新图（源目录即可），记录每张实际可见状态。已核基准：
- 33：受理台 issue 列表，@guest1 的单带 `状态::待受理` 标签、过滤器 Label=待受理
- 41：组看板六列——待受理(2)/已排期(1)/开发中(1)/待验证(1)/已关闭(2)/已拒绝(1)
- 其余 5 张按 test-plan §9.2 描述写图注，Read 后若与下文图注有出入，**改图注**。

- [ ] **Step 3: 写 submitter.html**

骨架：`<!DOCTYPE html>` 到 `</head>`（第 1–52 行）从 `field-engineer.html` **逐字节复制**（含全部内联 CSS），`<title>` 改为 `需求提出人与管理者 · 挖机代码管理上手指南`。body 完整内容如下：

```html
<body>

<header class="hero">
  <div class="wrap">
    <p class="crumb"><a href="index.html">← 返回角色导航</a></p>
    <h1>需求提出人与管理者上手指南</h1>
    <p class="tagline">有需求提单、有缺陷贴 manifest；例会看板投屏——全程不碰代码</p>
    <span class="badge">提单人 Guest 10 · 管理者 Reporter 20</span>
  </div>
</header>

<div class="wrap">

<h2>你是谁</h2>
<p>这篇教程服务两类人，共用一个入口：</p>
<p><b>需求提出人</b>——市场、客服、集团接口人、现场反馈汇集者。你在 GitLab 里是 <b>Guest（10）</b>：唯一日常操作就是在<b>受理台</b>（excavator/intake 仓库）提单，提完等分诊。不需要知道代码住在哪个仓库，也不需要任何代码权限。</p>
<p><b>管理者</b>——带团队看进度的人。你是 <b>Reporter（20）</b>：不写代码，周例会打开组看板和里程碑页投屏，回答"需求到哪了、卡在哪"。</p>

<h2>你能做什么 / 不能做什么</h2>
<table>
  <tr><th>能 ✅</th><th>不能 ❌</th></tr>
  <tr><td>在受理台按模板建单（需求 / 缺陷 / 任务）</td><td>改任何代码仓库（无权限，也不需要）</td></tr>
  <tr><td>给自己的单补评论、补信息</td><td>打标签、改看板配置（标签由分诊代打，配置平台组管）</td></tr>
  <tr><td>看组看板、里程碑完成度（例会投屏）</td><td>在群里口头提需求代替提单（制度：一概"请提单"）</td></tr>
</table>

<h2>典型任务流 A：提一张单（需求提出人）</h2>

<div class="step">
  <span class="no">1</span><h3>进受理台，选模板</h3>
  <p>左侧 Groups → excavator → <b>intake</b>（受理台）仓库 → Issues → New issue。三个模板三选一：<b>需求</b>（背景 / 目标 / 验收标准）、<b>缺陷</b>（现象 / 复现 / 影响范围 / 机器 manifest 粘贴区）、<b>任务</b>（技术改进类）。</p>
  <figure class="shot">
    <img src="assets/32-intake-template-form.png" alt="受理台建单页，需求模板表单">
    <figcaption>受理台建单 ｜ 三模板三选一——需求 / 缺陷 / 任务</figcaption>
  </figure>
  <div class="box why">
    <b>🔍 为什么所有需求只进一个口？</b>
    来源再多（集团 / 市场 / 客户 / 现场 / 内部）都走同一张模板进来，分诊人才能在 3 个工作日内给你答复；散在群消息里的需求没人接、也没人记得住（设计 §4.1）。
  </div>
</div>

<div class="step">
  <span class="no">2</span><h3>填完三段，提交拿单号</h3>
  <p>模板三段里<b>验收标准必填</b>，写"怎么算做完"——最好是可检查的样子（如"怠速下驾驶室振动位移 ≤ X mm"）。提交后拿到 <b>#单号</b>，这是你后续追问进度的唯一凭证。</p>
  <figure class="shot">
    <img src="assets/33-intake-issue-filed.png" alt="受理台 issue 列表，guest1 提的需求单带待受理标签">
    <figcaption>受理台列表 ｜ @guest1 的需求单已进「待受理」队列——所有来源唯一进料口</figcaption>
  </figure>
  <div class="box why">
    <b>🔍 为什么验收标准空泛会被打回？</b>
    单据质量靠两道兜底：模板示例给"好单"的样子 + 分诊打回机制（设计 §7.3）。"优化一下体验"这种单没人知道做完没做完。
  </div>
</div>

<div class="step">
  <span class="no">3</span><h3>等分诊：看单去哪了</h3>
  <p>3 个工作日内，分诊人（域 Owner 兼任）会做三件事之一：<b>移交</b>（单搬到对应产品域仓库、进排期）、<b>打回</b>（信息不足，退回你补）、<b>婉拒</b>（重复或超范围，说明理由关闭）。<code>来源::</code>/<code>状态::</code> 标签由分诊人代打——Guest 无打标权限（三阶段实测）。</p>
  <figure class="shot">
    <img src="assets/34-issue-transferred.png" alt="分诊移交后的需求单，已进域仓库并排期">
    <figcaption>分诊移交后 ｜ 单已 move 到 firmware 域仓库、状态 已排期、进里程碑</figcaption>
  </figure>
  <div class="box why">
    <b>🔍 为什么强调 3 日内分诊？</b>
    入口响应速度决定大家愿不愿意提单——这是口头文化能否被替代的胜负手（设计 §4.2）。分诊堵没堵，管理者一眼能看（见任务流 B 第 3 步）。
  </div>
</div>

<div class="step">
  <span class="no">4</span><h3>怎么知道做完了：不用催</h3>
  <p>开发在 MR 描述里写 <code>Closes #单号</code>，代码评审合入的那一刻，你的单<b>自动关闭</b>、自动记录合入 commit——哪个版本收了你这单，点开单就能看到。</p>
  <figure class="shot">
    <img src="assets/37-issue-auto-closed.png" alt="MR 合入后自动关闭的需求单，带合入 commit 记录">
    <figcaption>合入自动关单 ｜ MR 合入后单自动关闭、合入 commit 自动记录（155ms）</figcaption>
  </figure>
  <div class="box why">
    <b>🔍 为什么不用发消息催进度？</b>
    追溯链由系统自动生成，不靠人事后补录（设计 §5.1）：单的状态就是进度，催问的答案都在单上。需要外部验收的单（台架 / 现场确认）合入后进"待验证"，验收人通过后手关（§4.3）。
  </div>
</div>

<h2>典型任务流 B：例会看板三屏（管理者）</h2>

<div class="step">
  <span class="no">1</span><h3>组看板：一屏看全域状态</h3>
  <p>Groups → excavator → Issues → <b>Board</b>。列就是状态（待受理 → 已排期 → 开发中 → 待验证 → 已关闭 …），卡片在哪一列，活在哪一步。</p>
  <figure class="shot">
    <img src="assets/41-group-board.png" alt="excavator 组看板，列为待受理/已排期/开发中/待验证/已关闭/已拒绝">
    <figcaption>组看板 ｜ 列=状态——待受理/已排期/开发中/待验证/已关闭/已拒绝，一屏看全域</figcaption>
  </figure>
</div>

<div class="step">
  <span class="no">2</span><h3>里程碑过滤与完成度</h3>
  <p>看板按里程碑过滤（里程碑 = 版本节点，如"固件 v0.9"），或直接打开里程碑页：完成度<b>按单数给百分比</b> + 已关/未关清单——例会投这一屏。</p>
  <figure class="shot">
    <img src="assets/42-milestone-progress.png" alt="里程碑详情页，按单数显示完成度百分比与清单">
    <figcaption>里程碑完成度 ｜ CE 按单数给百分比 + 已关/未关清单——例会投屏</figcaption>
  </figure>
  <div class="box why">
    <b>🔍 例会只看板、不念稿</b>
    "待验证挂了一周的单"自动成为议程（设计 §6）。不做工时、不做燃尽——版本制交付，看单数就够了。
  </div>
</div>

<div class="step">
  <span class="no">3</span><h3>受理台积压：分诊堵没堵</h3>
  <p>进 intake 仓库，Issues 按 <b>待受理</b> 过滤——待受理堆着多少单，分诊有没有堵，一眼可见。积压超一周，例会点名。</p>
  <figure class="shot">
    <img src="assets/43-intake-backlog.png" alt="受理台按待受理标签过滤的积压视图">
    <figcaption>受理台积压 ｜ 按 待受理 过滤——分诊堵没堵一眼可见</figcaption>
  </figure>
  <div class="box why">
    <b>🔍 为什么管理者要盯受理台？</b>
    提单人的意愿是这条流程的命脉，而意愿取决于响应速度（设计 §10）——积压视图就是分诊健康的仪表盘。
  </div>
</div>

<h2>常见报错自救</h2>
<div class="box tip">
  <b>💡 我的单被打回了</b>
  不是拒绝：分诊人在评论里说明了缺什么，把信息补在评论区即可，单会重新进入分诊。
</div>
<div class="box tip">
  <b>💡 我的单被婉拒了</b>
  看关闭理由：重复（原单链接就在理由里）、超范围（找对口团队）。不认可可找域 Owner 申诉。
</div>
<div class="box tip">
  <b>💡 找不到提单入口</b>
  Groups → excavator → intake，或直接收藏受理台地址。所有来源都从这里进，别把需求发给个人。
</div>
<div class="box tip">
  <b>💡 想知道"我之前提的那单做到哪了"</b>
  打开单看状态列位置；已关闭的单里挂着合入 commit 与所属里程碑，哪次发布收的一查便知。
</div>

<h2>红线清单</h2>
<div class="box danger">
  <b>🚫 群里 / 口头提需求不算数</b>
  体系只认板上的单——群消息一概回"请提单"（设计 §7.3）。口头文化是这条流程唯一的对手。
</div>
<div class="box danger">
  <b>🚫 单里不贴客户商务 / 合同细节</b>
  需求说清楚就行，商务条款不进工单系统——DLP 意识延伸到需求侧（设计 §7.3）。
</div>
<div class="box danger">
  <b>🚫 管理者不绕过分诊直接派活</b>
  排期是域 Owner 把单拖进里程碑（设计 §4.4），不是领导打招呼——绕过受理台的活没有追溯链。
</div>

<h2>延伸阅读</h2>
<p>设计文档（docs/superpowers/specs/2026-09-03-requirement-flow-design.md）：</p>
<ul>
  <li>§4.1 统一受理台 / §4.2 分诊值班 / §4.3 状态机</li>
  <li>§5 追溯闭环（正向 Closes 关单 / 反向 manifest 三跳）</li>
  <li>§6 进度可视化 / §7.3 防滥用边界</li>
</ul>
<p>原型验收（docs/superpowers/specs/2026-08-31-excavator-prototype-test-plan.md）：</p>
<ul>
  <li>§9 三阶段验证结果（四场景证据链，截图 32–43）</li>
</ul>

<footer>挖机项目代码管理体系 · 教程基于 2026-08-31 / 09-01 / 09-03 三阶段本地原型实例截图 · 设计文档：docs/superpowers/specs/2026-09-03-requirement-flow-design.md</footer>

</div>
</body>
</html>
```

（注：设计 § 指向《产研需求流设计》。）写完后按 Step 2 的核对结果修正图注。

- [ ] **Step 4: check.py 加 submitter 骨架**

`check.py` SKELETON 字典 `"field"` 行之后插入：
```python
    "submitter":     ["你是谁", "能做", "任务流", "自救", "红线", "延伸"],
```

- [ ] **Step 5: index.html 接入第 6 篇**

四处修改：
1. 角色导航 `<a class="card" href="field-engineer.html">…</a>` 之后追加：
```html
  <a class="card" href="submitter.html">
    <b>需求提出人与管理者</b>
    <p>提需求看进度的人</p>
    <span class="badge">提单人 Guest / 管理者 Reporter</span>
    <p>提单 · 看板 · 里程碑</p>
  </a>
```
2. 「产物去哪了」figure 29（MinIO 三桶）之后、`<h2>术语速查</h2>` 之前插入：
```html
<div class="box why">
  <b>🔍 有需求 / 缺陷要提？（三阶段新增）</b>
  全部来源只进一个口——受理台（excavator/intake）按模板建单，3 个工作日内分诊；进度看组看板与里程碑。见<b><a href="submitter.html">需求提出人与管理者</a></b>教程。
</div>
```
3. 术语速查表 `<tr><td>DLP …</tr>` 之后追加五行：
```html
  <tr><td>受理台（intake）</td><td>所有需求 / 缺陷的唯一进料口仓库：按模板建单，3 日内分诊</td></tr>
  <tr><td>分诊</td><td>域 Owner 把单移交 / 打回 / 婉拒，并代打来源与状态标签</td></tr>
  <tr><td>状态:: / 来源:: 标签</td><td>形如"状态::待受理"的全组统一标签——看板列就来自它</td></tr>
  <tr><td>里程碑</td><td>版本节点（如"固件 v2.3·2026Q4"），进度按单数百分比看</td></tr>
  <tr><td>Closes #单号</td><td>写在 MR 描述里的关单指令：代码合入那一刻，单自动关闭</td></tr>
```
4. footer 改为：
```html
<footer>挖机项目代码管理体系 · 教程基于 2026-08-31 / 09-01 / 09-03 三阶段本地原型实例截图 · 设计文档：docs/superpowers/specs/2026-08-31-excavator-code-management-design.md / 2026-09-03-requirement-flow-design.md</footer>
```

- [ ] **Step 6: 自检**

```bash
cd /home/lancer/projects/frm && python3 docs/tutorials/check.py submitter.html index.html
```
Expected: 两行 `[OK]`（submitter 7 imgs, skeleton ✓；index skeleton ✓）

- [ ] **Step 7: 提交**

```bash
git add docs/tutorials/submitter.html docs/tutorials/index.html docs/tutorials/check.py docs/tutorials/assets/32-intake-template-form.png docs/tutorials/assets/33-intake-issue-filed.png docs/tutorials/assets/34-issue-transferred.png docs/tutorials/assets/37-issue-auto-closed.png docs/tutorials/assets/41-group-board.png docs/tutorials/assets/42-milestone-progress.png docs/tutorials/assets/43-intake-backlog.png
git commit -m "feat(tutorials): 第6篇《需求提出人与管理者》——提单+看板双视角，复用三阶段截图7张"
```

---

### Task 4: developer.html 扩展——提单/关联单号 + 无单不开发红线（图 36）

**Files:**
- Modify: `docs/tutorials/developer.html`（步骤 4 内插入、红线清单首项、延伸阅读、footer）
- Create: `docs/tutorials/assets/36-mr-closes-issue.png`（复制）

**Interfaces:**
- Consumes: Task 1 spec §5.1 三阶段条目；test-plan §9.2「MR Closes 自动关单」验证项
- Produces: 无下游依赖（Task 6 全量自检对象）

- [ ] **Step 1: 复制并核对图 36**

```bash
cp /home/lancer/projects/frm/gitlab-compose-test/screenshots/36-mr-closes-issue.png /home/lancer/projects/frm/docs/tutorials/assets/
```
Read 该图，确认 MR 描述含 `Closes #` 字样与里程碑选中状态，按实际修正 Step 2 图注中的单号。

- [ ] **Step 2: 步骤 4「建 MR」内插入关联单号内容**

在 `<figure class="shot">…08-mr-list…</figure>` 与既有「为什么必须走 MR」why 框之间插入：
```html
  <p>从三阶段起，描述里再加两件：<b>关联单号</b>（默认写 <code>Closes #单号</code>——合入即自动关单；需外部验收的单只写 <code>#单号</code> 引用，不写 Closes）与<b>选定里程碑</b>。仓库的 MR 模板已带四项自查 checklist：☑ 关联单号 ☑ 里程碑 ☑ CI 全绿 ☑ 自测通过。</p>
  <figure class="shot">
    <img src="assets/36-mr-closes-issue.png" alt="MR 描述写 Closes 关联需求单并选定里程碑">
    <figcaption>MR 关联单号 ｜ 描述写 Closes #单号 + 选定里程碑——合入即自动关单</figcaption>
  </figure>
  <div class="box why">
    <b>🔍 无单不开发（三无制度第一条）</b>
    任何改动（需求、缺陷、现场修复）先有单，commit 必须能追到一张 issue（需求流设计 §7.1）。你自己发现的 bug / 技术改进？先去受理台（excavator/intake）提缺陷 / 任务单，再开工——MR 描述里的 Closes 就是把"做了什么"和"为什么做"焊在一起的焊点（需求流设计 §5.1）。
  </div>
```

- [ ] **Step 3: 红线清单加首项**

`<h2>红线清单</h2>` 之后第一个 danger 框之前插入：
```html
<div class="box danger">
  <b>🚫 无单不开发</b>
  任何改动先有单（需求 / 缺陷 / 任务），MR 必须关联单号——追不到单的改动不合入（需求流设计 §7.1 三无制度）。
</div>
```

- [ ] **Step 4: 延伸阅读 + footer**

延伸阅读 `</ul>` 之后追加：
```html
<p>需求流设计（docs/superpowers/specs/2026-09-03-requirement-flow-design.md）：</p>
<ul>
  <li>§4.3 关单双路径 / §5.1 MR 关联与 checklist</li>
</ul>
```
footer 中 `2026-08-31 / 09-01 两阶段` → `2026-08-31 / 09-01 / 09-03 三阶段`。

- [ ] **Step 5: 自检 + 提交**

```bash
cd /home/lancer/projects/frm && python3 docs/tutorials/check.py developer.html
```
Expected: `[OK] developer.html — 5 imgs, skeleton ✓`

```bash
git add docs/tutorials/developer.html docs/tutorials/assets/36-mr-closes-issue.png
git commit -m "feat(tutorials): developer扩展提单/关联单号——无单不开发红线+图36"
```

---

### Task 5: field-engineer.html 扩展——manifest 建缺陷单 + 反向三跳（图 39）

**Files:**
- Modify: `docs/tutorials/field-engineer.html`（步骤 2 后插 2b、自救框补句、延伸阅读、footer）
- Create: `docs/tutorials/assets/39-defect-manifest.png`（复制）

**Interfaces:**
- Consumes: Task 1 spec §5.5 三阶段条目；test-plan §9.2「反向三跳」「外部验收路径（缺陷单 待验证）」验证项
- Produces: 无下游依赖（Task 6 全量自检对象）

- [ ] **Step 1: 复制并核对图 39**

```bash
cp /home/lancer/projects/frm/gitlab-compose-test/screenshots/39-defect-manifest.png /home/lancer/projects/frm/docs/tutorials/assets/
```
Read 该图：确认缺陷单含 manifest 粘贴内容、状态标签为 `状态::待验证`，按实际微调 Step 2 图注。

- [ ] **Step 2: 步骤 2「现场场景一」之后插入步骤 2b**

在场景一 why 框（`</div>` 结束「为什么现场永远不编译」）之后、场景二 `<div class="step">` 之前插入：
```html
<div class="step">
  <span class="no">2b</span><h3>现场机器出问题：用 manifest 建缺陷单</h3>
  <p>确认是缺陷？回受理台（excavator/intake）用<b>缺陷模板</b>建单：现象 / 复现 / 影响范围照模板填，把读出的 manifest.json <b>整段粘进模板的 manifest 粘贴区</b>。</p>
  <figure class="shot">
    <img src="assets/39-defect-manifest.png" alt="受理台的缺陷单，manifest 粘贴进模板专区，状态待验证">
    <figcaption>缺陷单（待验证）｜ manifest 粘贴进模板专区——修复合入后单进待验证，等你现场验收再关</figcaption>
  </figure>
  <div class="box why">
    <b>🔍 为什么贴 manifest，而不是口头说版本？</b>
    manifest 内嵌 commit：后方从你贴的这段出发，commit → 合入 MR → 需求单<b>三跳回溯</b>全自动——"这个行为是哪次需求引入的"一查便知（需求流设计 §5.2）。你现场补的 MR 也挂这张缺陷单，改动天然有单。
  </div>
</div>
```

- [ ] **Step 3: 自救框补一句**

「💡 机器上版本不明，刷什么？」框末尾追加一句：
```html
  查明版本后若确认是缺陷，就地按 2b 用 manifest 建缺陷单。
```

- [ ] **Step 4: 延伸阅读 + footer**

延伸阅读 `</ul>` 之后（原型验收段之前）追加：
```html
<p>需求流设计（docs/superpowers/specs/2026-09-03-requirement-flow-design.md）：</p>
<ul>
  <li>§5.2 反向追溯链（manifest → commit → MR → 需求单）</li>
</ul>
```
footer 中 `2026-08-31 / 09-01 两阶段` → `2026-08-31 / 09-01 / 09-03 三阶段`。

- [ ] **Step 5: 自检 + 提交**

```bash
cd /home/lancer/projects/frm && python3 docs/tutorials/check.py field-engineer.html
```
Expected: `[OK] field-engineer.html — 5 imgs, skeleton ✓`

```bash
git add docs/tutorials/field-engineer.html docs/tutorials/assets/39-defect-manifest.png
git commit -m "feat(tutorials): field-engineer扩展manifest建缺陷单——反向三跳+图39"
```

---

### Task 6: 收尾——剩余 footer 三阶段化 + 全量自检

**Files:**
- Modify: `docs/tutorials/viewer.html`、`docs/tutorials/owner.html`、`docs/tutorials/platform.html`（各仅 footer 一行）

**Interfaces:**
- Consumes: Task 3/4/5 产出的 7 个页面与 9 张新图
- Produces: 全套教程三阶段一致状态（验收门）

- [ ] **Step 1: 三个 footer 统一**

viewer/owner/platform 三页 footer 中 `2026-08-31 / 09-01 两阶段` → `2026-08-31 / 09-01 / 09-03 三阶段`（设计文档指向保持各自不变）。

- [ ] **Step 2: 全量自检**

```bash
cd /home/lancer/projects/frm && python3 docs/tutorials/check.py index.html developer.html owner.html viewer.html platform.html field-engineer.html submitter.html
```
Expected: 7 行全 `[OK]`

```bash
grep -c '两阶段' docs/tutorials/*.html; ls docs/tutorials/assets/ | grep -cE '^(32|33|34|36|37|39|41|42|43)-'
```
Expected: 第一命令各文件 0；第二命令 9

- [ ] **Step 3: 逐图终核（抽三张）**

Read `assets/34-issue-transferred.png`、`assets/37-issue-auto-closed.png`、`assets/42-milestone-progress.png`，确认图注与图内状态一致（有出入改图注）。

- [ ] **Step 4: 提交**

```bash
git add docs/tutorials/viewer.html docs/tutorials/owner.html docs/tutorials/platform.html
git commit -m "docs(tutorials): 全站footer三阶段化+全量自检通过（7页/9图）"
```

---

## 不做（YAGNI 边界）

- 不补拍新截图（只复用 32–43 中的 9 张）
- 不扩 owner.html（分诊/排期操作）——设计 §8 交付物清单只有第 6 篇 + developer/field 两处扩展；分诊细节归设计文档
- 不使用 35/38/40（文字承载 / 图文分歧 9.3-7 / 细节回溯 test-plan）
- 不动 root PAT（实例管理工作凭据，2026-10-01 自动作废；已在提交历史中，不扩散也不清洗）
- 不推远端（用户既定选择）
