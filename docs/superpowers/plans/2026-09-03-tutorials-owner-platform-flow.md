# owner/platform 需求流职责补全 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 补全 owner.html 与 platform.html 在需求流侧的职责缺口——域 Owner 的分诊三动作 + 排期 + 合码核需求流 checklist，平台工程师的标签字典/看板配置 MR 管控。

**Architecture:** 两处 HTML 扩展，复用已有三阶段截图（34/42/43），无新截图、无 spec 改动、无新文件。owner.html 在现有「典型任务流：一次发布的全流程」之前插入新 h2 节「典型任务流：分诊与排期」（3 步骤卡片），合码步骤补需求流 checklist 核对，延伸阅读 + 红线各补需求流条目。platform.html 在红线清单前插入新 h2 节「典型任务流：纳管需求流配置」（标签字典 + 看板配置 + issue 模板），延伸阅读补需求流设计段。

**Tech Stack:** 静态 HTML（内联 CSS、无 JS）+ check.py 静态自检。

**依据：**
- 设计：`docs/superpowers/specs/2026-09-03-requirement-flow-design.md` §4.2（分诊值班）、§4.4（排期）、§5.1（合码 checklist）、§7.1（三无制度）、§7.2（角色增量职责）
- 截图：34-issue-transferred、42-milestone-progress、43-intake-backlog（已在 assets/，三阶段 Task 3 复制）

## Global Constraints

- 教程 HTML：全中文、内联 CSS、无 JS、无外部资源（check.py 强制）
- 截图只复用不补拍：34/42/43 已在 assets/（submitter.html 也用这三张，跨页复用符合自包含原则）
- 不改 spec、不改 check.py、不改 index.html（index 已在 Task 3 接入需求流入口框 + 术语速查，不重复）
- 插入位置精确：owner 在 h2「典型任务流：一次发布的全流程」之前插新 h2；platform 在 h2「常见报错自救」之前插新 h2
- commit message 用 conventional 前缀
- 工作直接在 main、不推远端

---

### Task 1: owner.html 扩展——分诊与排期 + 合码核 checklist + 红线/延伸

**Files:**
- Modify: `docs/tutorials/owner.html`

**Interfaces:**
- Consumes: 设计 §4.2/§4.4/§5.1/§7.1；截图 34/42/43（已在 assets/）
- Produces: owner.html 骨架不变（check.py SKELETON 已含 owner），新增内容不破坏既有片段匹配

- [ ] **Step 1: 在 h2「典型任务流：一次发布的全流程」之前插入新 h2 节**

在第 76 行 `<h2>典型任务流：一次发布的全流程</h2>` 之前插入：

```html
<h2>典型任务流：分诊与排期（需求流）</h2>
<p>三阶段起，你不只是代码守门人——你还是这个域的<b>分诊人</b>（§4.2）。提单人在受理台（excavator/intake）提的单，先到你手里过一道：3 个工作日内决定它的去向。</p>

<div class="step">
  <span class="no">1</span><h3>分诊：三选一</h3>
  <p>打开受理台（excavator/intake）的 Issues 列表，按 <b>待受理</b> 过滤——这些单等着你处理。对每张单做三件事之一：</p>
  <ul>
    <li><b>移交</b>——单属于你管的域？把它 move 到你的域仓库，评论与链接全保留。同时代打 <code>来源::</code> 和 <code>状态::已排期</code> 标签（提单人是 Guest，没有打标权限，标签由你代打，§4.1）。</li>
    <li><b>打回</b>——验收标准空泛、信息不够？退回提单人补充，在评论里写明缺什么。</li>
    <li><b>婉拒</b>——重复提了、或超出本域范围？说明理由、关闭。</li>
  </ul>
  <div class="box why">
    <b>🔍 为什么 3 日内必须分诊？</b>
    入口响应速度决定大家愿不愿意提单——这是口头文化能否被替代的胜负手（§4.2）。堵没堵，看受理台积压（见管理者教程的积压视图）。
  </div>
</div>

<div class="step">
  <span class="no">2</span><h3>排期：拖里程碑</h3>
  <p>移交到域仓库的单默认进 <b>已排期</b>。排期 = 把单拖进版本里程碑（如"固件 v0.9"），进里程碑即排上日程。里程碑 = 版本节点，跨仓库生效（§4.4）。</p>
  <figure class="shot">
    <img src="assets/42-milestone-progress.png" alt="里程碑详情页，按单数显示完成度百分比与已关/未关清单">
    <figcaption>里程碑页 ｜ 进了里程碑的单在这里——按单数给完成度，不做工时与燃尽</figcaption>
  </figure>
  <div class="box why">
    <b>🔍 为什么不做工时统计？</b>
    版本制交付、节点驱动，不做固定迭代、不搞工时——看单数百分比就够了，里程碑清单就是发布清单（§4.4）。
  </div>
</div>

<div class="step">
  <span class="no">3</span><h3>合码前：核需求流 checklist</h3>
  <p>Developer 提 MR 时，描述里应该带着四项自查 checklist。你合码前除了看代码 diff 和 CI 绿，还要核这四项（§5.1）：</p>
  <ul>
    <li>☑ <b>关联需求单号</b>——写了 <code>Closes #单号</code>（默认路径：合入即自动关单）还是只引用 <code>#单号</code>（需外部验收：合入后进待验证，你来手关）</li>
    <li>☑ <b>选定里程碑</b>——这个版本要收的需求</li>
    <li>☑ <b>CI 全绿</b></li>
    <li>☑ <b>自测通过</b></li>
  </ul>
  <div class="box why">
    <b>🔍 无单不开发（三无制度第一条，§7.1）</b>
    任何改动（需求、缺陷、现场修复）先有单，commit 必须能追到一张 issue——追不到单的 MR 不合入。这是需求流与代码流之间的焊点。
  </div>
</div>
```

- [ ] **Step 2: 红线清单补需求流条目**

在 `<h2>红线清单</h2>` 后第一个 danger 框（「不合没有任何评审记录的"自己批自己"」）之前插入：

```html
<div class="box danger">
  <b>🚫 无单不开发——不合入追不到单的 MR</b>
  MR 必须关联需求单号（Closes 或引用），追不到单的改动不合入（需求流设计 §7.1 三无制度）。
</div>
<div class="box danger">
  <b>🚫 无里程碑不发布——tag/Release 必须挂里程碑</b>
  发版前确认 tag 所属里程碑已选定——无里程碑的版本不算数（需求流设计 §7.1）。
</div>
```

- [ ] **Step 3: 延伸阅读补需求流设计段**

在现有 `</ul>`（代码管理设计文档段）之后追加：

```html
<p>需求流设计（docs/superpowers/specs/2026-09-03-requirement-flow-design.md）：</p>
<ul>
  <li>§4.2 分诊值班 / §4.4 版本节奏（排期与里程碑）</li>
  <li>§5.1 MR 关联与 checklist / §7.1 三无制度</li>
</ul>
```

- [ ] **Step 4: 自检 + 提交**

```bash
cd /home/lancer/projects/frm && python3 docs/tutorials/check.py owner.html
```
Expected: `[OK] owner.html — 6 imgs, skeleton ✓`（原 4 图 + 新增 42 = 5 图… 实际看 owner 已有 14/16/17/27 四张，加 42 = 5 图）

```bash
git add docs/tutorials/owner.html
git commit -m "feat(tutorials): owner扩展分诊与排期——需求流checklist+三无红线+图42"
```

---

### Task 2: platform.html 扩展——标签字典/看板配置/模板 MR 管控

**Files:**
- Modify: `docs/tutorials/platform.html`

**Interfaces:**
- Consumes: 设计 §7.2（平台工程师增量职责）、§4.1（受理台与标签）、§4.3（状态机 7 状态 scoped 标签）；截图 43（已在 assets/）
- Produces: platform.html 骨架不变

- [ ] **Step 1: 在 h2「常见报错自救」之前插入新 h2 节**

在第 182 行 `<h2>常见报错自救</h2>` 之前插入：

```html
<h2>典型任务流：纳管需求流配置（三阶段新增）</h2>
<p>三阶段引入了需求流——受理台、scoped 标签字典、组看板、issue 模板——这些配置的版本化管护也在你手上（§7.2）。所有需求流配置都在 <code>platform/</code> 仓库里走 MR，与 ci-templates 同级管理：新增一个标签也走 MR，防止标签蔓延失控。</p>

<div class="step">
  <span class="no">1</span><h3>scoped 标签字典</h3>
  <p>全组统一的两套 scoped 标签在 <code>platform/</code> 仓库版本化（§4.3）：</p>
  <ul>
    <li><b>状态::</b>——7 个：待受理 / 已排期 / 开发中 / 待验证 / 已关闭 / 已拒绝 / 暂缓。一个不多一个不少——看板列就是这 7 个状态。</li>
    <li><b>来源::</b>——5 个：集团 / 市场 / 客户 / 现场 / 内部。统计需求来源构成有数据可依。</li>
  </ul>
  <p>新增或改名一个标签 = 改 <code>platform/</code> 里的标签字典文件 → MR 评审 → 合入。不走 MR 直接在 GitLab 界面加标签 = 绕过版本化，不允许。</p>
  <div class="box why">
    <b>🔍 为什么标签也走 MR？</b>
    标签是看板列、是统计维度、是例会议程——一个人随手加一个标签，看板就多一列、统计就对不齐。版本化让标签变更可追溯、可评审（§7.2）。
  </div>
</div>

<div class="step">
  <span class="no">2</span><h3>组看板与里程碑配置</h3>
  <p>组级看板的列配置（7 状态列）和组级里程碑（版本节点）都在 <code>platform/</code> 里管。看板是懒创建的——首次浏览器访问后 API 才能加列，这个坑三阶段实测踩过（test-plan 9.1）。里程碑命名规范如 <code>固件 v0.9·三阶段原型</code>，跨仓库生效。</p>
  <div class="box why">
    <b>🔍 为什么看板列 = 状态标签？</b>
    看板列不是自由配置的——它直接映射 7 个 scoped 状态标签。改列 = 改标签字典 = 走 MR（§4.3 / §6）。
  </div>
</div>

<div class="step">
  <span class="no">3</span><h3>issue 模板与 MR 模板</h3>
  <p>受理台的三个 issue 模板（需求 / 缺陷 / 任务）和各域仓库的 MR 模板（含需求流四项 checklist）都在 <code>platform/</code> 版本化。改模板 = 改所有人的提单/建 MR 体验，必须走 MR 评审——与改 ci-templates 同理。</p>
  <div class="box why">
    <b>🔍 为什么模板也在 platform/？</b>
    模板是流程的入口——模板改一行，所有人的提单/建 MR 行为就变了。与 ci-templates 同理，集中版本化、走 MR 评审、防止各域各搞一套（§7.2）。
  </div>
</div>
```

- [ ] **Step 2: 红线清单补需求流配置条目**

在 `<h2>红线清单</h2>` 后第一个 danger 框之前插入：

```html
<div class="box danger">
  <b>🚫 标签/看板/模板不在 GitLab 界面直接改——走 platform/ MR</b>
  直接在 GitLab 界面加标签、改看板列、改模板 = 绕过版本化，不可追溯、不可评审（需求流设计 §7.2）。
</div>
```

- [ ] **Step 3: 延伸阅读补需求流设计段**

在现有 `</ul>`（代码管理设计段 + 原型验收段）之后追加：

```html
<p>需求流设计（docs/superpowers/specs/2026-09-03-requirement-flow-design.md）：</p>
<ul>
  <li>§4.3 状态机与 scoped 标签 / §7.2 角色与配置归属</li>
  <li>§6 进度可视化（看板与里程碑）</li>
</ul>
```

- [ ] **Step 4: 自检 + 提交**

```bash
cd /home/lancer/projects/frm && python3 docs/tutorials/check.py platform.html
```
Expected: `[OK] platform.html — 6 imgs, skeleton ✓`（原 5 图不变，新节无图——43 积压图已有在 submitter 用，这里不重复以免失焦）

```bash
git add docs/tutorials/platform.html
git commit -m "feat(tutorials): platform扩展纳管需求流配置——标签字典/看板/模板MR管控"
```

---

### Task 3: 收尾——全量自检 + 逐图终核

**Files:**
- Modify: 无（仅验证）

- [ ] **Step 1: 全量自检**

```bash
cd /home/lancer/projects/frm && python3 docs/tutorials/check.py index.html developer.html owner.html viewer.html platform.html field-engineer.html submitter.html
```
Expected: 7 行全 `[OK]`

- [ ] **Step 2: 逐图终核（抽 2 张）**

Read `assets/42-milestone-progress.png`（owner 新引入），确认图注与图内状态一致。

- [ ] **Step 3: 确认无残留**

```bash
grep -c '两阶段' docs/tutorials/*.html; grep -rn '分诊\|排期\|标签字典' docs/tutorials/owner.html docs/tutorials/platform.html | wc -l
```
Expected: 第一命令各文件 0；第二命令 ≥6（owner 分诊/排期 ≥3 处 + platform 标签字典/看板/模板 ≥3 处）

---

## 不做（YAGNI 边界）

- 不改 spec（需求流设计 §7.2 已定义角色增量职责，教程只是实现侧补全）
- 不改 check.py（owner/platform 骨架已在 SKELETON 里，新增 h2 不破坏片段匹配）
- 不改 index.html（需求流入口框 + 术语速查已在 Task 3 接入）
- 不补拍新截图（34/42/43 已在 assets/，跨页复用）
- platform 新节不加图（标签字典/看板配置操作是平台组内部 MR 流程，与既有 ci-templates MR 流程同模式，文字承载即可——避免图过多失焦）
