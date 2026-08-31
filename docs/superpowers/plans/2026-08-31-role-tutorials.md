# 五角色 HTML 入门教程 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 按 `docs/superpowers/specs/2026-08-31-role-tutorials-design.md` 生成 6 个自包含 HTML 教程页（5 角色 + 索引）+ 20 张截图资产。

**Architecture:** 纯静态 HTML，每页内联同一套共享 CSS（无 JS、无外部资源、图片相对路径）。`check.py` 做结构化自检（图片引用存在、无外链资源、骨架齐全），每个任务产出后立即验证并提交。

**Tech Stack:** HTML5 + 内联 CSS；验证用 Python 3 标准库（html.parser）。

## Global Constraints

- 全中文；字体 stack 固定：`system-ui, "PingFang SC", "Microsoft YaHei", sans-serif`；正文 15px/1.7。
- 每页 `<html lang="zh-CN">`，`<meta charset="utf-8">`，`<title>` 格式：`角色名 · 挖机代码管理上手指南`。
- 图片一律相对路径 `assets/<原名>.png`（原文件名不改）。图片标签统一写法：
  `<figure class="shot"><img src="assets/xx-name.png" alt="描述"><figcaption>页面：… ｜ 看哪里：…</figcaption></figure>`
- 三种提示框 class 固定：`box why`（🔍 为什么，蓝）、`box danger`（⚠️ 红线，红）、`box tip`（💡 自救，黄）。
- 命令块：`<pre class="cmd"><code>…</code></pre>`，`$` 开头表示用户终端命令。
- 禁止出现任何 `http://`/`https://` 的资源引用（link/script/img src）；文内提及的 URL 一律是纯文本（延伸阅读只链仓库内相对文档 `../specs/…` 或不链）。
- 延伸阅读链接格式：指向 `../specs/2026-08-31-excavator-code-management-design.md` 的相应章节名（纯文本路径，不用 `<a href>` 也行，但用相对 `href` 是允许的例外——它不是外链）。
- 共享 CSS（每页 `<style>` 内**逐字**包含，不得改动——一致性靠复制维护）：

```css
:root{--ink:#1f2328;--mut:#656d76;--line:#d8dee4;--bg:#f6f8fa;
--blue:#0969da;--blue-bg:#ddf4ff;--red:#cf222e;--red-bg:#ffebe9;
--yel:#9a6700;--yel-bg:#fff8c5;--accent:#1f6feb}
*{box-sizing:border-box}
body{margin:0;color:var(--ink);font:15px/1.7 system-ui,"PingFang SC","Microsoft YaHei",sans-serif;background:#fff}
.wrap{max-width:880px;margin:0 auto;padding:0 20px 60px}
header.hero{background:linear-gradient(135deg,#0d2b45,#1f6feb);color:#fff;padding:34px 0 26px;margin-bottom:28px}
header.hero .wrap{padding-bottom:0}
.crumb{font-size:13px;opacity:.8;margin-bottom:10px}
.crumb a{color:#fff}
h1{font-size:26px;margin:0 0 6px}
.tagline{font-size:15px;opacity:.9;margin:0}
.badge{display:inline-block;background:rgba(255,255,255,.18);border:1px solid rgba(255,255,255,.45);
border-radius:99px;padding:2px 12px;font-size:13px;margin-top:10px}
h2{font-size:20px;border-left:4px solid var(--accent);padding-left:10px;margin:38px 0 14px}
h3{font-size:16px;margin:22px 0 8px}
table{border-collapse:collapse;width:100%;margin:12px 0;font-size:14px}
th,td{border:1px solid var(--line);padding:7px 10px;text-align:left;vertical-align:top}
th{background:var(--bg)}
.step{border:1px solid var(--line);border-radius:10px;padding:18px 20px;margin:16px 0;background:#fff}
.step .no{display:inline-block;background:var(--accent);color:#fff;border-radius:50%;
width:26px;height:26px;line-height:26px;text-align:center;font-weight:700;margin-right:8px}
.step h3{display:inline;margin:0}
.cmd{background:#0d1117;color:#e6edf3;border-radius:8px;padding:12px 14px;overflow-x:auto;
font:13px/1.6 ui-monospace,Consolas,monospace;margin:10px 0}
.cmd .c{color:#8b949e}
figure.shot{margin:14px 0}
figure.shot img{max-width:100%;border:1px solid var(--line);border-radius:8px;display:block}
figcaption{color:var(--mut);font-size:13px;margin-top:6px}
.box{border-radius:8px;padding:12px 16px;margin:14px 0;font-size:14px}
.box b{display:block;margin-bottom:4px}
.why{background:var(--blue-bg);border:1px solid #a5d8ff}
.why b{color:var(--blue)}
.danger{background:var(--red-bg);border:1px solid #ffc1c0}
.danger b{color:var(--red)}
.tip{background:var(--yel-bg);border:1px solid #ecdf95}
.tip b{color:var(--yel)}
.cards{display:grid;grid-template-columns:repeat(auto-fill,minmax(240px,1fr));gap:14px;margin:16px 0}
.card{border:1px solid var(--line);border-radius:10px;padding:16px;text-decoration:none;color:var(--ink)}
.card:hover{border-color:var(--accent);box-shadow:0 2px 8px rgba(31,111,235,.15)}
.card b{color:var(--accent)}
.ok{color:#1a7f37;font-weight:700}.no2{color:var(--red);font-weight:700}
footer{color:var(--mut);font-size:13px;border-top:1px solid var(--line);margin-top:48px;padding-top:14px}
@media print{header.hero{background:#0d2b45}.step,.box{break-inside:avoid}body{font-size:12px}}
```

- 共享页脚（每页 `</div>` 前，`<footer>` 内）：`挖机项目代码管理体系 · 教程基于 2026-08-31 本地原型实例截图 · 设计文档：docs/superpowers/specs/2026-08-31-excavator-code-management-design.md`
- 每个角色页 hero 面包屑：`<p class="crumb"><a href="index.html">← 返回角色导航</a></p>`

---

### Task 1: 资产复制与自检脚本

**Files:**
- Create: `docs/tutorials/assets/`（20 张 PNG 副本）
- Create: `docs/tutorials/check.py`

**Interfaces:**
- Produces: `check.py <file.html>...` —— 校验单/多个 HTML：退出码 0=通过；输出 `[OK] file — N imgs, skeleton ✓` 或 `[FAIL] file — 原因`。后续所有任务依赖它做验证。

- [ ] **Step 1: 建目录并复制截图**

```bash
mkdir -p docs/tutorials/assets
cp gitlab-compose-test/screenshots/*.png docs/tutorials/assets/
ls docs/tutorials/assets | wc -l   # 期望输出: 20
```

- [ ] **Step 2: 写自检脚本**

`docs/tutorials/check.py`（完整内容）：

```python
#!/usr/bin/env python3
"""教程静态自检：图片引用存在、无外部资源、骨架齐全。用法: check.py file.html ..."""
import re, sys, pathlib

BASE = pathlib.Path(__file__).parent
SKELETON = {  # 每类页必须包含的 <h2> 文案片段
    "index":  ["角色导航", "通用入门", "术语速查"],
    "developer":     ["你是谁", "能做", "任务流", "自救", "红线", "延伸"],
    "owner":         ["你是谁", "能做", "任务流", "自救", "红线", "延伸"],
    "viewer":        ["你是谁", "能做", "任务流", "自救", "红线", "延伸"],
    "platform":      ["你是谁", "能做", "任务流", "自救", "红线", "延伸"],
    "field":         ["你是谁", "能做", "任务流", "自救", "红线", "延伸"],
}
def pagetype(name):
    if name == "index.html": return "index"
    if name.startswith("field"): return "field"
    return name.replace(".html", "")

fails = 0
for arg in sys.argv[1:]:
    p = BASE / arg
    html = p.read_text(encoding="utf-8")
    errs = []
    for src in re.findall(r'(?:src|href)="([^"]+)"', html):
        if src.startswith(("http://", "https://", "//")):
            errs.append(f"外部资源引用: {src}")
        elif src.startswith(("assets/", "index.html")) and not (BASE / src).exists():
            errs.append(f"引用的文件不存在: {src}")
    pt = pagetype(p.name)
    for frag in SKELETON.get(pt, []):
        if frag not in html:
            errs.append(f"缺少骨架小节: {frag}")
    n_img = len(re.findall(r'<img ', html))
    if pt != "index" and n_img < 2:
        errs.append(f"图片过少({n_img}), 图文并茂要求 >=2")
    if errs:
        fails += 1
        print(f"[FAIL] {arg} — " + "; ".join(errs))
    else:
        print(f"[OK] {arg} — {n_img} imgs, skeleton ✓")
sys.exit(1 if fails else 0)
```

- [ ] **Step 3: 验证脚本对坏输入能报错（临时构造一个反例）**

```bash
cd docs/tutorials
printf '<html><body><img src="assets/nope.png"><a href="https://x.com/c.js">x</a></body></html>' > /tmp/bad.html
cp /tmp/bad.html bad.html && python3 check.py bad.html; echo "exit=$?"; rm bad.html
```

期望输出含 `[FAIL] bad.html — 引用的文件不存在: assets/nope.png; 外部资源引用: https://x.com/c.js`，且 `exit=1`。

- [ ] **Step 4: 提交**

```bash
git add docs/tutorials
git commit -m "feat(tutorials): 截图资产副本与教程自检脚本"
```

---

### Task 2: index.html — 角色导航 + 通用入门 + 术语速查

**Files:**
- Create: `docs/tutorials/index.html`

**Interfaces:**
- Consumes: Task 1 的 assets/ 与 check.py；Global Constraints 的共享 CSS。
- Produces: 5 张角色卡片分别链 `developer.html` `owner.html` `viewer.html` `platform.html` `field-engineer.html`（文件名固定，后续任务按此命名）。

- [ ] **Step 1: 写 index.html**

结构（完整骨架，共享 CSS 与页脚逐字嵌入）：

- hero：`<h1>挖机代码管理上手指南</h1>`，tagline：`我是谁？→ 点进对应角色，5–10 分钟即可上手日常操作`
- `<h2>角色导航</h2>`：`.cards` 内 5 张 `.card`，每张含角色名、一句定位、权限徽章、3 个关键词。文案：
  - **开发工程师** ｜ 写代码的人 ｜ Developer 30 ｜ 分支 · MR · 等CI绿
  - **仓库 Owner** ｜ 守门与发布的人 ｜ Maintainer 40 ｜ 评审 · tag · Release
  - **只读协作者** ｜ 只看不动代码的人 ｜ Guest 10 ｜ 项目页 · 制品下载
  - **平台工程** ｜ 管 CI 模板的人 ｜ platform 组 Maintainer ｜ 宪法 · 模板 · 传播
  - **驻场工程师** ｜ 出差在现场的人 ｜ 出场 Developer / 现场 Guest ｜ 离线 · 刷固件 · 补MR
- `<h2>通用入门</h2>`：所有角色共用的 4 个基本动作，各一图一步骤卡片（`.step` 复用）：
  1. 登录（`01-login.png`，图注：登录页 ｜ 账号找平台组开，域账号即登录账号）
  2. 找到自己的项目组（`04-group-tree.png`，图注：组结构树 ｜ excavator 下按产品域分 6 个子组）
  3. 看懂一条流水线（`07-ci-success.png`，图注：流水线详情 ｜ 绿=通过，红=失败，点开看日志）
  4. 看成员与权限（`12-members.png`，图注：项目成员页 ｜ 谁是 Owner 一目了然）
  - 另配 `02-dashboard.png`（图注：登录后的主面板 ｜ 左侧 Groups 快捷入口）、`06-pipelines.png`（图注：流水线列表 ｜ 每次 push 一条）穿插在步骤 2/3 卡片内
  - 每卡片后加一个 `.box why`：如"为什么按产品域分组，不按团队分组——团队会重组，产品域相对稳定（设计 §4.1）"
- `<h2>术语速查</h2>`：`<table>` 两列（术语/白话），行：
  - MR（Merge Request）｜ "请把我分支上的改动合进 main" 的申请，别人评审通过才算数
  - CI / 流水线 ｜ 服务器替你自动编译+测试；push 后自动跑，红了必须修
  - 保护分支 main ｜ 只能通过 MR 合入，谁都不能直接 push 的主干
  - tag / Release ｜ 给某个 commit 贴版本号（tag）；Release 是带附件的正式发布页
  - manifest.json ｜ 藏在制品里的"身份证"：哪个 commit、何时、哪台机器构建
  - ci-templates ｜ 全项目共用的 CI 模板仓库，规则改一处、全部仓库生效
- 页脚（共享）

- [ ] **Step 2: 自检**

```bash
cd docs/tutorials && python3 check.py index.html
```

期望：`[OK] index.html — 6 imgs, skeleton ✓`

- [ ] **Step 3: 浏览器目检（Playwright 截图回看）**

```bash
cd /home/lancer/projects/frm && python3 - <<'EOF'
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b = p.chromium.launch(executable_path='/usr/bin/google-chrome')
    pg = b.new_page(viewport={"width":1280,"height":900})
    pg.goto("file:///home/lancer/projects/frm/docs/tutorials/index.html")
    pg.screenshot(path="/tmp/tut-index.png", full_page=True)
    b.close()
EOF
```

然后 Read `/tmp/tut-index.png` 目检：卡片网格正常、图片显示、无横向滚动条。

- [ ] **Step 4: 提交**

```bash
git add docs/tutorials/index.html
git commit -m "feat(tutorials): 角色导航索引页（5卡片+通用入门+术语速查）"
```

---

### Task 3: developer.html — 开发工程师

**Files:**
- Create: `docs/tutorials/developer.html`

**Interfaces:**
- Consumes: 共享 CSS/页脚/面包屑；assets：`03-groups.png` `08-mr-list.png` `15-mr2-changes.png`。
- Produces: 无下游依赖。

- [ ] **Step 1: 写页面**（hero：开发工程师上手指南 ｜ Developer 30 徽章；面包屑回 index）

- `<h2>你是谁</h2>`：一段——本组开发成员；典型一天：拉代码→建分支→改码→push→建 MR→等 CI 绿。
- `<h2>你能做什么 / 不能做什么</h2>`：两列表格：
  | 能 ✅ | 不能 ❌ |
  | push 自己的特性分支 | 直接 push main（系统直接拒绝） |
  | 建 MR、评论、修改到通过 | 合入 MR（Owner 做） |
  | 触发并查看自己的流水线 | 改保护分支设置、改成员权限 |
- `<h2>典型任务流：一次改动的全流程</h2>`，6 个 `.step`：

  1. **找到并 clone 仓库** — `03-groups.png`（图注：组列表 ｜ excavator → firmware → 你的仓库）；命令：
     ```bash
     $ git clone http://gitlab.internal/excavator/firmware/hydraulic-controller.git
     $ cd hydraulic-controller
     ```
  2. **从最新 main 建特性分支** — 分支名规则 `feat/xxx` 或 `fix/xxx`；命令 `git checkout main && git pull && git checkout -b feat/pid-tune`；`.box why`：为什么短生命周期分支——main 常绿、小步快合，避免几个月合不回去（§4.2）。
  3. **改码 → commit → push** — 命令 `git add -A && git commit -m "feat: PID 参数整定"` `git push -u origin feat/pid-tune`；push 回显里的 GitLab 自动返回的建 MR 链接要点出来。
  4. **建 MR** — `08-mr-list.png`（图注：MR 列表 ｜ 左侧 Merge requests → New）；标题规范 + 描述里写"改了什么、为什么、怎么验证"；`.box why`：为什么必须 MR——代码进 main 的唯一通道是评审，禁止直推是系统强制的（§4.2）。
  5. **等 CI，读结果** — MR 页内嵌流水线；红了点开 job 看日志；`15-mr2-changes.png`（图注：MR 的 Changes 页 ｜ 评审者在这里逐行看你每一行改动）。
  6. **修到绿，等 Owner 合入** — push 新 commit 到同一分支，MR 自动更新。

- `<h2>常见报错自救</h2>`，3 个 `.box tip`（真实报错原文来自模拟验收 §7.2-A/7.3-1）：
  1. `remote: GitLab: You are not allowed to push code to protected branches.` → 你在推 main。回到自己的特性分支：`git switch -c feat/xxx` 再推。
  2. 流水线直接 failed 且 **0 个 job**，日志含 `Project 'excavator/platform/ci-templates' not found or access denied` → 你对 platform 组无读权限，找平台组加 Reporter（§7.3-1 已知问题）。
  3. 流水线红了怎么排查：job → Trace 看最后 30 行 → 本地复跑同命令 → `git commit --allow-empty -m "ci: retry"` 触发新流水线（注意：retry 不重新解析模板，改模板后必须触发新流水线）。
- `<h2>红线清单</h2>` `.box danger` ×3：不上传任何明文密钥/密码（CI 第一条 job 会跑 gitleaks 扫描，扫到即失败 §6.5）；不对共享分支用 `git push -f`；不在本机编"发布用"固件——发布产物只能来自 CI（§5.4）。
- `<h2>延伸阅读</h2>`：设计文档 §4.2 分支模型、§4.3 权限、§6.2 CI 三层（相对链接或纯文本路径）。

- [ ] **Step 2: 自检** `python3 check.py developer.html` → `[OK] … 3 imgs, skeleton ✓`
- [ ] **Step 3: 浏览器目检**（同 Task 2 Step 3，full_page 截 `/tmp/tut-dev.png` 后 Read 目检）
- [ ] **Step 4: 提交** `git add docs/tutorials/developer.html && git commit -m "feat(tutorials): 开发工程师教程"`

---

### Task 4: owner.html — 仓库 Owner

**Files:**
- Create: `docs/tutorials/owner.html`

**Interfaces:**
- Consumes: 共享 CSS/页脚/面包屑；assets：`14-mr2-merged.png` `16-release.png` `17-pipeline19.png`。
- Produces: 无下游依赖。

- [ ] **Step 1: 写页面**

- hero：仓库 Owner 上手指南 ｜ Maintainer 40；定位一句话：这个仓库的守门人和发布责任人（每仓库仅 1–2 人，§4.3）。
- 能/不能表：
  | 能 ✅ | 不能 ❌ |
  | approve 并合入 MR | 改 platform 组的 ci-templates（平台组自己管） |
  | 配保护分支、管成员 | 跳过评审合入自己的 MR（制度） |
  | 打 tag、批准晋升、建 Release | 在本机编发布产物 |
- 任务流 7 步：
  1. **评审 MR**：Changes 逐行看（图 `14-mr2-merged.png`，图注：MR 详情页 ｜ 顶部批准记录、中部流水线状态、合入信息）→ 有问题在行内评论；OK 则 **Approve**。
  2. **合入**：Merge 按钮合入即触发 main 流水线；`.box why`：为什么 Developer 不能自己合——评审与合入分离是代码质量的最低保障（§4.3）。
  3. **打 tag**：
     ```bash
     $ git checkout main && git pull
     $ git tag -a v0.2.0-field -m "现场验证版"
     $ git push origin v0.2.0-field
     ```
  4. **等 tag 流水线**：`17-pipeline19.png`（图注：tag 流水线 ｜ build 完成后 promote-release 处于 ⏸ 手动状态）。
  5. **手动批准晋升**：点 promote-release 的 ▶ Play——发布永远是人的决定，不是自动的（§6.3 `.box why`）。
  6. **建 Release**：Releases → New release 选 tag → 附上 `.bin` 与 `manifest.json`；`16-release.png`（图注：Release 页 ｜ 附件即驻场下载通道，Evidence 记录溯源）。
  7. **核对追溯链**（`.box why` 重点）：manifest.commit = main HEAD = tag commit = MR 合入 commit，四方一致才可放行（§6.3）；核对方法——Release 页 manifest 的 commit 字段 vs 仓库 main 页顶部 SHA。
- 自救 `.box tip` ×2：
  1. Merge 按钮灰着提示 conflicts → 本地 `git fetch && git checkout feat/xxx && git merge origin/main` 解决后 push，MR 自动更新。
  2. tag 打错了想删 → `git push origin :refs/tags/vX.Y.Z` + GitLab 页面删 tag；**已对外发布的 tag 不删，追加 `-fix` 新 tag**。
- 红线 `.box danger` ×3：不合没有任何评审记录的"自己批自己"；发布产物必须来自 CI 构建区，本机编译的版本永远不发给现场（§5.4）；tag 命名一旦对外，不复用不修改。
- 延伸阅读：§6.3 制品晋升与追溯、§4.3、§5.4。

- [ ] **Step 2: 自检** `python3 check.py owner.html` → OK
- [ ] **Step 3: 浏览器目检**（截图 `/tmp/tut-owner.png` 回看）
- [ ] **Step 4: 提交** `git commit -m "feat(tutorials): 仓库Owner教程（评审→tag→晋升→Release→追溯）"`

---

### Task 5: viewer.html — 只读协作者

**Files:**
- Create: `docs/tutorials/viewer.html`

**Interfaces:**
- Consumes: 共享 CSS/页尾/面包屑；assets：`05-project.png` `13-packages.png` `16-release.png`。
- Produces: 无下游依赖。

- [ ] **Step 1: 写页面**

- hero：只读协作者上手指南 ｜ Guest 10；定位：需要看项目状态、下载制品，但不动代码（跨组查阅/外部协作/测试同事）。
- 能/不能表（把"被拒"写成正常预期，来自 §7.2-C 实测）：
  | 能 ✅ | 不能（会收到 403/拒绝）❌ |
  | 看项目页、issue、Release、流水线状态 | `git clone`（403 not allowed to download code） |
  | 从 Release 下载 .bin 和 manifest.json | 看代码文件树、MR 列表（403） |
- 任务流 4 步：
  1. **找项目**：`05-project.png`（图注：项目主页 ｜ 无代码权时看到的是项目概览与活动）。
  2. **进 Releases 下载制品**：左侧 Deploy → Releases；`16-release.png`（图注：Release 页 ｜ Assets 里下载 .bin 与 manifest.json）。
  3. **核对 manifest**：打开 manifest.json 看 name/commit/build_time/runner 四个字段——"手上这个包是哪个版本、什么时候构建"一查即知（§6.3 `.box why`）。
  4. **（如需通用包）Package registry**：`13-packages.png`（图注：包仓库 ｜ Deploy → Package Registry）。
- `.box why` 放在能/不能表后：**看到 403 不是系统坏了，是权限边界在正常工作**（§4.3）——需要看代码时找仓库 Owner 加 Reporter，而不是想办法绕。
- 自救 `.box tip` ×2：clone 被拒 → 确认你要的是代码还是制品，制品走 Release 就够；Release 页没有附件 → 找 Owner 确认该版本是否已发布（未晋升的 tag 没有 Release）。
- 红线 `.box danger` ×1：下载的制品与 manifest 只在自己权限范围内使用，不转发给未授权人员。
- 延伸阅读：§4.3、§7.2（驻场同款通道）。

- [ ] **Step 2: 自检** `python3 check.py viewer.html` → OK
- [ ] **Step 3: 浏览器目检**
- [ ] **Step 4: 提交** `git commit -m "feat(tutorials): 只读协作者教程（浏览+制品下载+manifest核对）"`

---

### Task 6: platform.html — 平台工程

**Files:**
- Create: `docs/tutorials/platform.html`

**Interfaces:**
- Consumes: 共享 CSS/页尾/面包屑；assets：`11-ci-templates.png` `19-ci-mr.png` `18-job18-trace.png`。
- Produces: 无下游依赖。

- [ ] **Step 1: 写页面**

- hero：平台工程上手指南 ｜ platform 组 Maintainer；定位：管 `platform/ci-templates`——全项目 CI 规则的唯一来源，变更权只在本组（§4.3 实测：firmware Owner 推本仓库被 403 拒绝）。
- 能/不能表：
  | 能 ✅ | 不能 ❌ |
  | 改 ci-templates 并走 MR 合入 | 直接改业务仓库的代码 |
  | 管 runner 注册与标签 | 跳过 MR 直推 ci-templates 的 main |
  | 制定下游流水线准入规则 | 在业务仓库里单独给某个仓库开后门 |
- 任务流 5 步：
  1. **认识模板仓库**：`11-ci-templates.png`（图注：ci-templates 仓库 ｜ firmware/algo/vehicle/cloud 四套模板 + 规范文档）；`.box why`：为什么叫"宪法"——规则版本化、变更走 MR 评审，避免口头规矩（§4.1）。
  2. **改模板**：分支 → 修改 → push → MR；`19-ci-mr.png`（图注：模板变更 MR ｜ diff 即"法律条文"的修订记录）。
  3. **合入即全下游生效**：下游 `.gitlab-ci.yml` 里是 `include + extends`，模板改动无需任何下游仓库配合（§6.2）。
  4. **验证传播**：随便挑一个下游仓库触发新流水线 → 打开 build job；`18-job18-trace.png`（图注：下游 build job 的 Trace ｜ 出现模板新增的"产物为空，禁止发布"校验即证明传播成功）。
  5. **把规则写进准入**：下游流水线不 include 通用层的 MR 不予合入（§6.2 制度 + 自检双保险）。
- `.box why`（机制，必须讲透）：**include 在流水线创建时解析并快照**——retry 不重新解析；模板热修后必须触发**新**流水线验证，别盯着旧流水线 retry（§7.3-4 实测）。
- 自救 `.box tip` ×2：下游报 `ci-templates not found or access denied` → 检查该开发者是否在 platform 组有 Reporter（全员可读是硬规则，§7.3-1）；下游 job 用了自写 script 不吃模板更新 → 它只 include 没 extends，改成 `extends: .firmware-template`（§7.3-2）。
- 红线 `.box danger` ×3：模板改动必须自己先在测试仓库跑绿再合入（你影响的是所有仓库）；不给任何业务仓库绕过通用层的后门；runner 密钥/注册 token 不进仓库不进聊天工具。
- 延伸阅读：§6.2 三层模型、§6.1 Runner 池、7.3 全部五条实测发现。

- [ ] **Step 2: 自检** `python3 check.py platform.html` → OK
- [ ] **Step 3: 浏览器目检**
- [ ] **Step 4: 提交** `git commit -m "feat(tutorials): 平台工程教程（宪法变更→传播验证→快照机制）"`

---

### Task 7: field-engineer.html — 驻场工程师

**Files:**
- Create: `docs/tutorials/field-engineer.html`

**Interfaces:**
- Consumes: 共享 CSS/页尾/面包屑；assets：`16-release.png` `20-mr4-field.png`。
- Produces: 无下游依赖。

- [ ] **Step 1: 写页面**

- hero：驻场工程师上手指南 ｜ 出场前 Developer / 现场 Guest；定位：离线为基线、有网为加速——流程不赌现场有网（§7 开篇）。
- 能/不能表：
  | 能 ✅ | 不能 ❌ |
  | 出场前 clone 代码、下载已签名制品 | 现场编译正式版本 |
  | 现场本地 commit 改码验证 | 改动不留 commit（=违规） |
  | 应急刷本地临时包（须 24h 内补 MR） | 把临时包当工作方式 |
- 任务流 5 步：
  1. **出场前打包**（公司内）：`git pull` + 从 Release 下载本次任务相关已签名制品（`16-release.png` 图注同前）；按 `platform/` 仓库出场 checklist 核对：代码、制品、工具链版本、联系人（§7.1）。
  2. **现场通道一：调试/刷固件**：只刷预构建制品，刷前核对 manifest 四字段（§7.2）；`.box why`：为什么现场永远不编译——现场产物不可追溯，且编译环境不可控。
  3. **现场通道二：改码**：DLP 笔记本本地 `git commit`（哪怕没网）→ 有网即 push → MR → CI 出包 → 下载刷入；**改动必须以 commit 回中心仓**——防止代码重新散落回个人电脑（§7.2 硬规则）。
  4. **现场通道三：取数**：日志/传感器数据进 MinIO 投放区（能连则直传，否则回公司上传）；方向单一：数据向内流、代码向外只走 git（§7.2）。
  5. **应急兜底（§7.3）**：断网 + 机器急等 → 允许本地临时包先刷；回公司 **24 小时内**补 MR + 正式构建：`20-mr4-field.png`（图注：应急补单 MR ｜ commit message 注明"现场应急"，Owner 评审合入闭环）。
- `.box why`：临时包是救火用的，不是工作方式（§7.3 原话）——24h 补单制度就是"留应急缝，但缝有账可查"。
- 自救 `.box tip` ×2：现场没网改完码 → 改动已在本地 commit 就安全（不会丢），回网 `git push -u origin <分支>` 后建 MR；发现机器上版本不明 → 找到 manifest.json，四字段直接对出是哪个 commit 何时构建。
- 红线 `.box danger` ×3：改动不以 commit 回中心仓 = 按违规处理（§7.3）；应急临时包超 24h 不补 MR = 违规；现场数据不走私人网盘/U 盘乱拷，按 §7.4 集团外发策略走审批加密盘。
- 延伸阅读：§7 全节、§6.3 manifest、§5.3（驻场终端全量 DLP 的原因）。

- [ ] **Step 2: 自检** `python3 check.py field-engineer.html` → OK
- [ ] **Step 3: 浏览器目检**
- [ ] **Step 4: 提交** `git commit -m "feat(tutorials): 驻场工程师教程（三条通道+应急24h补单）"`

---

### Task 8: 整体验证与收尾

**Files:**
- Modify: `docs/superpowers/specs/2026-08-31-excavator-prototype-test-plan.md`（§6 截图清单后追加一句教程入口）

**Interfaces:**
- Consumes: 全部 6 页 + check.py。

- [ ] **Step 1: 全量自检**

```bash
cd docs/tutorials && python3 check.py *.html; echo "exit=$?"
```

期望：6 行 `[OK]`，exit=0。

- [ ] **Step 2: 全页渲染目检（一次截 6 张）**

Playwright 循环对 6 页各截 full_page 到 `/tmp/tut-*.png`，逐一 Read 目检：无破图、无横向滚动、打印预览（`page.emulate_media(media="print")` 后截图）不破版。

- [ ] **Step 3: 链接抽查**

`grep -o 'href="[a-z-]*\.html"' *.html | sort -u` 核对：所有互链文件都存在。

- [ ] **Step 4: 测试计划文档加教程入口**

在 prototype-test-plan.md §6 末尾追加一行：
`> 配套入门教程（按角色）：\`docs/tutorials/index.html\``

- [ ] **Step 5: 提交**

```bash
git add docs/tutorials docs/superpowers/specs/2026-08-31-excavator-prototype-test-plan.md
git commit -m "feat(tutorials): 五角色HTML教程完成（全量验证通过）"
```
