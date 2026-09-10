# 教程信息架构重构实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 落地 spec `docs/superpowers/specs/2026-09-10-tutorials-ia-rework-design.md`（v2）：index 三轨九卡导航、gitlab-ops.md 教程化为 ops.html、驻场降级为场景篇、全仓引用收尾。

**Architecture:** 六个任务按依赖排布：两个独立小改（锚点、场景链）→ ops.html 主体 → index 三轨 → 收尾清引用 → 全量验收。每个任务自带 check.py / grep 自检，提交点全绿。

**Tech Stack:** 静态 HTML（教程房风：单文件自包含、无外部资源）、Python 自检脚本 `docs/tutorials/check.py`、git。

**本计划的表达约定（对 writing-plans「完整内容」的适配）：** 内容迁移类步骤 =「精确源 § 引用 + 迁移映射表 + 完整新文案」，不整页复述——源文件 `docs/ops/gitlab-ops.md` 是事实来源，DRY；所有**新增**文案（卡片、hero、能做/不能做、4b、红线、链接块）在计划中全量给出，逐字使用。

## Global Constraints

- 自包含纪律：所有页面禁止外部资源（`http://`/`https://`/`//` 开头的 src/href），check.py 会查。
- 事实内容只搬不改：ops.html 迁移内容以 `docs/ops/gitlab-ops.md` 现文为唯一基线；新增文字仅本计划全量给出的两处（能做/不能做表、4b 小节）加零星导语。
- 房风 CSS：复制 `docs/tutorials/developer.html` 第 6–51 行 `<style>` 块，仅允许追加 details/summary 折叠样式。
- 显式锚点集合：`gov` / `arch` / `run`（ops.html），`flow-a` / `flow-b`（submitter.html）。
- **房规：每个提交步骤执行前，先向用户展示 diff 概要，经确认再 commit**（可按任务攒批确认）。提交信息中文，尾行 `Co-Authored-By: Claude Code <noreply@anthropic.com>`。
- 每个任务收尾时 `check.py` 对其所涉页面必须全绿。

## 任务依赖

Task 1、Task 2 相互独立可并行；Task 3 依赖无（但产出被 4/5 消费）；Task 4 依赖 1+3；Task 5 依赖 4；Task 6 依赖全部。

---

### Task 1: submitter.html 两任务流加显式锚点

**Files:**
- Modify: `docs/tutorials/submitter.html`（79 行、133 行两处 h2）

**Interfaces:**
- Produces: 锚点 `submitter.html#flow-a`、`submitter.html#flow-b`（Task 4 的 index 需求管理两卡消费）

- [ ] **Step 1: 加两个 id**

```html
<!-- 79 行： -->
<h2 id="flow-a">典型任务流 A：提一张单（需求提出人）</h2>
<!-- 133 行： -->
<h2 id="flow-b">典型任务流 B：例会看板三屏（管理者）</h2>
```

- [ ] **Step 2: 自检**

Run: `python3 docs/tutorials/check.py submitter.html && grep -c 'id="flow-[ab]"' docs/tutorials/submitter.html`
Expected: `[OK] submitter.html — ... skeleton ✓`；grep 计数 `2`

- [ ] **Step 3: 提交（先过用户确认）**

```bash
git add docs/tutorials/submitter.html
git commit -m "docs(tutorials): submitter 两任务流加显式锚点 flow-a/flow-b"
```

---

### Task 2: 驻场降级为场景篇 + developer 双向链

**Files:**
- Modify: `docs/tutorials/field-engineer.html`（hero 三处 + 「你是谁」段首）
- Modify: `docs/tutorials/developer.html`（「常见报错自救」h2 前插入小节）

**Interfaces:**
- Produces: developer ↔ field-engineer 双向链（Task 6 验收消费）
- 注意: index 的驻场卡此任务暂不撤（Task 4 统一处理），中间态不破绿

- [ ] **Step 1: field-engineer.html hero 改造（三处 Edit）**

```html
<!-- 标题： -->
<h1>驻场场景篇</h1>
<!-- badge： -->
<span class="badge">场景 · 出场前 Developer / 现场 Guest</span>
<!-- 「你是谁」段首插入一句（保留原段其余文字不动）： -->
<p><b>这不是一个独立角色</b>——你就是身处驻场情境的<a href="developer.html">开发工程师</a>。你是这个项目的驻场工程师：在公司里是 <b>Developer</b>，到了现场账号降为 <b>Guest</b>……（后接原文）
```

- [ ] **Step 2: developer.html 插入场景入口（「常见报错自救」h2 之前）**

```html
<h2>出差驻场？</h2>
<div class="box tip">
  <b>💡 驻场场景篇</b>
  出差到现场（离线为基线、有网为加速）：刷固件核对 manifest、本地改码回补 MR、投放区取数、应急 24h 补单——见 <b><a href="field-engineer.html">驻场场景篇</a></b>。
</div>
```

- [ ] **Step 3: 自检**

Run: `python3 docs/tutorials/check.py developer.html field-engineer.html && grep -c 'field-engineer.html' docs/tutorials/developer.html && grep -c 'developer.html' docs/tutorials/field-engineer.html`
Expected: 两页 `[OK]`；两个 grep 计数各 `≥1`（双向链在位）

- [ ] **Step 4: 提交（先过用户确认）**

```bash
git add docs/tutorials/field-engineer.html docs/tutorials/developer.html
git commit -m "docs(tutorials): 驻场降级为场景篇，developer 增场景入口"
```

---

### Task 3: ops.html 全页（内容迁移 + SVG + check.py 页型）

**Files:**
- Create: `docs/tutorials/ops.html`
- Modify: `docs/tutorials/check.py`（SKELETON 加 ops 行；图片下限豁免 ops）

**Interfaces:**
- Produces: `ops.html` 含锚点 `#gov` / `#arch` / `#run`（Task 4 index 卡与 Task 5 compose 注释消费）
- Consumes: `docs/ops/gitlab-ops.md` 全文（迁移源）；`developer.html:6-51`（CSS）

- [ ] **Step 1: 读源**

Read `docs/ops/gitlab-ops.md`（190 行，全文）；Read `docs/tutorials/developer.html` 第 1–52 行（head + style 骨架）。

- [ ] **Step 2: 写 ops.html**

页面骨架 = developer.html 的 head/style/crumb-hero/wrap/footer 结构，`<title>运维 · 智能挖机代码管理上手指南</title>`。style 块原样复制，末尾追加：

```css
details{border:1px solid var(--line);border-radius:8px;margin:14px 0}
details summary{cursor:pointer;padding:10px 16px;font-weight:700;color:var(--accent)}
details[open] summary{border-bottom:1px solid var(--line)}
details .dbody{padding:4px 16px 12px}
```

内容区块按序组装（迁移规则：bash 块 → `<pre class="cmd">`；md 表格 → `<table>`；「> 为什么…」引注 → `<div class="box why">`；小节内步骤 → `<div class="step">`）：

| # | 区块（h2） | 内容 |
|---|---|---|
| 1 | hero | 下述新文案 A |
| 2 | 你是谁 | 下述新文案 A 的段落 |
| 3 | 你能做什么 / 不能做什么 | 下述新文案 B |
| 4 | 实施主线：五步把平台建起来 | 5 个 `.step`：①部署准备＝源 §2 ②起栈与就绪（**id=run**，step 的 h3 加 id）＝源 §3 含 Runner 注册 ③首启初始化＝源 §4 ④组织与治理（**id=gov**）＝新文案 C + 源 §5.1–5.5 ⑤转入日常＝桥接段（链 #arch 与查阅各区） |
| 5 | 查阅：架构与组件表（**id=arch**） | 源 §1：SVG（Step 3 画）+ 组件表 + 三条要点 + 准绳原则原句 |
| 6 | 查阅：日常运维 | 源 §6 三小节 |
| 7 | 查阅：原型复现 | 源附录 A，包 `<details><summary>展开附录 A：原型复现段表</summary><div class="dbody">…</div></details>` |
| 8 | 查阅：已知坑位 | 源附录 B |
| 9 | 红线清单 | 下述新文案 D |
| 10 | 延伸阅读 | 纯文本路径列表（房风：docs/ 路径不做链接）：设计 §7、ADR-0003/0004/0005/0006/0009/0010/0020/0021、验证结论 §3、原型验证结论 §5 |

**新文案 A（hero + 你是谁，逐字用）：**

```html
<header class="hero">
  <div class="wrap">
    <p class="crumb"><a href="index.html">← 返回角色导航</a></p>
    <h1>运维上手指南</h1>
    <p class="tagline">从零实施五步 + 日常运维查阅——起栈、开号、封禁、备份</p>
    <span class="badge">实例管理员</span>
  </div>
</header>
...
<h2>你是谁</h2>
<p>你是这套体系的平台运维：把已经设计好的方案<b>从零建起来</b>，然后<b>长期看住它</b>。实施期按「实施主线」五步走一遍；建成后日常动作在「查阅」区随手翻。不要求复刻原型测试环境——本文凡「示例值」（IP、端口、口令、组名、用户名）均来自原型验证环境，正式实施按实际替换。若你是拿着顶层组的<b>运营</b>（项目负责人），直接从 <a href="#gov">组织与治理</a> 进入。</p>
```

**新文案 B（能做/不能做，逐字用）：**

```html
<table>
  <tr><th>能 ✅</th><th>不能 ❌</th></tr>
  <tr><td>起栈、升组件（先对 <a href="#arch">组件表</a>）</td><td>改业务仓库代码（开发的事）</td></tr>
  <tr><td>注册 Runner、开账号、封禁回收</td><td>改 CI 模板与标签字典（走 platform 组 MR）</td></tr>
  <tr><td>备份、恢复演练</td><td>把原型口令带进正式环境</td></tr>
</table>
```

**新文案 C（#gov 章首双视角导语 + 4b，逐字用；导语后接源 §5.1–5.5 作 4a）：**

```html
<p>这一章两类人读：<b>实施的人</b>（运维）按 4a 从上到下建一遍；<b>治理的人</b>（顶层 Owner / 运营）建完之后从 4b 起长期在此活动。</p>
<h3>4a 一次性建立</h3>
（源 §5.1–5.5 原文迁入）
<h3>4b 持续治理</h3>
<ul>
<li>授权变更一律走 API 并留存脚本日志——免费版无审计，脚本是唯一留痕</li>
<li>新产品域 = 新子组：按产品域建组，团队重组不动组树（ADR-0003）</li>
<li>里程碑命名如「固件 v2.3·2026Q4」，版本节点跨仓库生效</li>
<li>顶层 Owner 由项目负责人持有、兼平台维护人——本页运维动作与治理动作在此人身上合一</li>
</ul>
```

**新文案 D（红线 4 条，逐字用）：**

```html
<div class="box danger"><b>🚫 未演练过的备份等于没有备份</b>恢复演练每半年一次（ADR-0020）。</div>
<div class="box danger"><b>🚫 组件表是准绳</b>改 yml 先对表；表要改先过设计文档。</div>
<div class="box danger"><b>🚫 原型口令仅限原型栈</b>正式实施 root 口令走凭证通道，首登即改。</div>
<div class="box danger"><b>🚫 实例运行过再改应用设置＝直改数据库</b>gitlab-rails runner 改 current_application_settings；改 compose 环境变量不再生效。</div>
```

页脚（溯源）：

```html
<footer>智能挖机项目代码管理体系 · 前身 docs/ops/gitlab-ops.md（2026-09-10 教程化，设计见 docs/superpowers/specs/2026-09-10-tutorials-ia-rework-design.md） · 设计文档：docs/design/2026-08-31-excavator-code-management-design.md</footer>
```

- [ ] **Step 3: 画内嵌 SVG（替换 mermaid）**

元素清单＝源 §1 的 mermaid 块（10 节点：DEV / GL / RU / MI / IN / DOCK / AD / RP / HB / BK；实线 6 边、虚线 4 边；端口标签 8081/8082/9002/9003/8084）。画法约束：`viewBox="0 0 900 420"`；宿主机 subgraph 画圆角矩形容器（`fill:#f6f8fa;stroke:#d8dee4`）；实线 `stroke:#1f6feb`、虚线 `stroke:#9a6700;stroke-dasharray:6 4`；节点文字 13px，与房风色板一致；纯内联，不引外部图。

- [ ] **Step 4: check.py 加 ops 页型**

```python
# SKELETON 字典追加一行：
    "ops":           ["你是谁", "能做", "实施主线", "查阅", "红线", "延伸"],
# 图片下限行改（pagetype 无需改，"ops.html"→"ops" 现逻辑已覆盖）：
    if pt not in ("index", "ops") and n_img < 2:
```

- [ ] **Step 5: 自检**

Run: `python3 docs/tutorials/check.py ops.html && grep -c 'id="gov"\|id="arch"\|id="run"' docs/tutorials/ops.html && grep -c 'http' docs/tutorials/ops.html || true`
Expected: `[OK] ops.html — ... skeleton ✓`；锚点计数 `3`；`http` 计数 `0`（无外部资源）

- [ ] **Step 6: 提交（先过用户确认）**

```bash
git add docs/tutorials/ops.html docs/tutorials/check.py
git commit -m "docs(tutorials): gitlab-ops 手册教程化为 ops.html（实施主线+查阅层+SVG）"
```

---

### Task 4: index.html 三轨九卡

**Files:**
- Modify: `docs/tutorials/index.html`（替换「角色导航」h2 + 六卡区块）
- Modify: `docs/tutorials/check.py`（SKELETON index 行）

**Interfaces:**
- Consumes: `ops.html`（Task 3 的 #gov）、`submitter.html`（Task 1 的 flow-a/flow-b）
- Produces: 三轨九卡布局（Task 5/6 消费）

- [ ] **Step 1: 替换导航区块（完整 HTML）**

删除现 `<h2>角色导航</h2>` 起至六卡 `</div>` 止，替换为：

```html
<h2>日常运维</h2>
<div class="cards">
  <a class="card" href="ops.html">
    <b>运维人员</b><p>把平台从零搭起来并看住的人</p>
    <span class="badge">实例管理员</span><p>起栈 · 开号 · 备份</p>
  </a>
  <a class="card" href="ops.html#gov">
    <b>运营人员</b><p>拿着顶层组的项目负责人</p>
    <span class="badge">顶层组 Owner</span><p>组树 · 授权 · 里程碑</p>
  </a>
  <a class="card" href="platform.html">
    <b>平台工程 ⇄</b><p>同一页的另一半：runner · 镜像库 · 对象存储</p>
    <span class="badge">platform 组 Maintainer</span><p>基础设施视角 · 正卡在代码交付</p>
  </a>
</div>
<h2>代码交付</h2>
<div class="cards">
  <a class="card" href="developer.html">
    <b>开发工程师</b><p>写代码的人（出差驻场？看场景篇）</p>
    <span class="badge">Developer 30</span><p>分支 · MR · 等CI绿</p>
  </a>
  <a class="card" href="owner.html">
    <b>仓库 Owner</b><p>守门与发布的人</p>
    <span class="badge">Maintainer 40</span><p>评审 · tag · Release · 分诊</p>
  </a>
  <a class="card" href="viewer.html">
    <b>只读协作者</b><p>只看不动代码的人</p>
    <span class="badge">Guest 10</span><p>项目页 · 制品下载</p>
  </a>
  <a class="card" href="platform.html">
    <b>平台工程</b><p>管 CI 宪法与制品基础设施的人</p>
    <span class="badge">platform 组 Maintainer</span><p>宪法 · 模板 · 传播</p>
  </a>
</div>
<h2>需求管理</h2>
<div class="cards">
  <a class="card" href="submitter.html#flow-a">
    <b>需求提出人</b><p>提需求、报缺陷的人</p>
    <span class="badge">提单人 Guest</span><p>模板建单 · 追进度</p>
  </a>
  <a class="card" href="submitter.html#flow-b">
    <b>需求管理者</b><p>盯进度、主持例会的人</p>
    <span class="badge">管理者 Reporter</span><p>看板三屏 · 里程碑</p>
  </a>
</div>
```

- [ ] **Step 2: check.py index 骨架改**

```python
    "index":  ["通用入门", "术语速查", "日常运维", "代码交付", "需求管理"],
```

- [ ] **Step 3: 自检**

Run: `python3 docs/tutorials/check.py index.html && grep -c 'class="card"' docs/tutorials/index.html && grep -c 'field-engineer.html' docs/tutorials/index.html || true`
Expected: `[OK] index.html — ...`；卡片计数 `9`；`field-engineer.html` 计数 `0`（驻场卡已撤）

- [ ] **Step 4: 提交（先过用户确认）**

```bash
git add docs/tutorials/index.html docs/tutorials/check.py
git commit -m "docs(tutorials): index 改三轨九卡导航"
```

---

### Task 5: 收尾——撤旧文件与旧引用

**Files:**
- Delete: `docs/ops/gitlab-ops.md`（目录随之撤销）
- Modify: `README.md`（阅读地图行 + 目录树）
- Modify: `gitlab-compose-test/docker-compose.yml`（25、77 两行注释）

**Interfaces:**
- Consumes: `ops.html#arch` / `#run`（Task 3）
- 注: 工作区那笔「受众行」未提交删除随本任务文件删除一并消解（spec 验收 #5）

- [ ] **Step 1: 删旧手册**

```bash
git rm docs/ops/gitlab-ops.md
rmdir docs/ops 2>/dev/null || true   # git rm 不保证清空目录，兜一手
```

- [ ] **Step 2: compose 两处注释改锚**

```yaml
# 25 行改为：
    # 组件表准绳见 docs/tutorials/ops.html#arch，原型机 62G/32C 富余不受影响
# 77 行改为：
    # 注册在 GitLab 就绪后进行（见 docs/tutorials/ops.html#run），此处先起容器
```

- [ ] **Step 3: README 三处**

阅读地图行（现 11 行）：

```markdown
| 平台运维 / 运营（顶层 Owner） | `docs/tutorials/ops.html`（实施五步 + 日常运维查阅）→ `gitlab-compose-test/`（compose 栈 + 截图脚本 + 证据 01–43） |
```

目录树：删除 `├── ops/` 行；`tutorials/` 行改为：

```markdown
└── tutorials/    三轨角色教程（HTML，含截图与运维手册）
```

- [ ] **Step 4: 自检**

Run: `grep -rn "gitlab-ops\|gitlab-repro" README.md docs/ gitlab-compose-test/docker-compose.yml | grep -v superpowers/specs || echo CLEAN; test ! -e docs/ops && echo NO-OPS-DIR`
Expected: `CLEAN`；`NO-OPS-DIR`

- [ ] **Step 5: 提交（先过用户确认）**

```bash
git add README.md gitlab-compose-test/docker-compose.yml
git commit -m "docs: 收尾——撤 docs/ops 与旧引用，compose/README 改指新锚"
```

---

### Task 6: 全量验收（无提交，纯检查）

**Files:** 无改动（发现问题回改对应任务文件并补提交）

- [ ] **Step 1: 八页全绿**

Run: `cd docs/tutorials && python3 check.py index.html developer.html owner.html viewer.html platform.html field-engineer.html submitter.html ops.html`
Expected: 8 行 `[OK]`

- [ ] **Step 2: 锚点与链路**

Run: `grep -o 'id="flow-a"\|id="flow-b"' docs/tutorials/submitter.html | sort | uniq -c; grep -c 'href="ops.html#gov"' docs/tutorials/index.html; grep -c '#arch\|#run' gitlab-compose-test/docker-compose.yml`
Expected: flow-a/flow-b 各 1；gov 卡 1；compose 两锚 2

- [ ] **Step 3: SVG 对表抽查**

对照 `gitlab-compose-test/docker-compose.yml` 服务与端口，核对 ops.html SVG：四容器名、8081/8082/9002/9003 端口、runner→docker.sock、minio-init 幂等边，一一在图。

- [ ] **Step 4: 对照 spec 验收 5 条逐条打勾**（spec §7），向用户报告验收单。
