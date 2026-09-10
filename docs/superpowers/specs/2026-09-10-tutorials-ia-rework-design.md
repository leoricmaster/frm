# 教程信息架构重构（三轨导航 · ops 教程化 · 驻场降级）— 设计

- 日期：2026-09-10
- 状态：v2 修订，待通盘终审
- 决策人：lancer
- v2 变更：治理章双视角切分（§2/§4）、index 卡片文案全量钉死（§3）、实施顺序（§5）、验收收紧（§7）

## 1. 背景与问题

教程侧与运维手册侧各有一个结构问题，且互为补位：

1. **index 六卡平铺无分组**：开发/仓库Owner/只读/平台/驻场/提单人同级并列，角色多了不好扫，也分不出"活动域"。
2. **运维轨没有教程页**：`gitlab-ops.md`（昨日刚按 spec 重构为实施与运维手册）受众就是运维与顶层 Owner，形态却是 md——宽表、无导航、mermaid 依赖 GitLab 渲染。它有教程的一半基因（§2–5 线性实施），也有手册的一半（§1 准绳表、§6 日常运维、附录查阅）。
3. **驻场不是角色**：field-engineer.html:67 自证「在公司里是 Developer，到了现场账号降为 Guest」——是部署情境，不是权限集，占角色卡位混淆口径。
4. 尾巴：README:11 仍指向已改名的 `gitlab-repro.md`；工作区有一笔未提交改动删了 ops 手册的「受众」行。

## 2. 已确认决策

| 决策点 | 结论 |
|---|---|
| index 导航 | **三轨**：日常运维 / 代码交付 / 需求管理；通用入门与术语速查置顶/置底不动 |
| gitlab-ops.md 去向 | **转 HTML 教程页 `docs/tutorials/ops.html`**，`docs/ops/` 目录撤销；按读法分层：线性实施主线 + 查阅层 |
| 架构图 | mermaid → **内嵌 SVG**（自包含纪律，check.py 禁外部资源） |
| 治理章切分 | 实施主线第 4 步定名**「组织与治理」（id=gov）**，内分 **4a 一次性建立 / 4b 持续治理**两小节；运营卡锚指 `#gov` |
| 驻场 | **降级为场景**：field-engineer.html 保留为场景篇（红线级内容不动），index 撤卡，developer.html 内链 |
| 平台工程 | **一页两轨挂链**：代码交付轨正卡 + 日常运维轨副卡（同一 platform.html），不拆页 |
| 运营人员（顶层 Owner） | **不新造页**，卡片指 `ops.html#gov`，长大再拆 |
| 运维/运营命名 | **保轨名「日常运维」**，卡面 badge 钉 GitLab 映射（实例管理员 / 顶层组 Owner） |
| 需求管理两角色 | 两卡共用 submitter.html，h2 加显式 id（flow-a / flow-b）作锚点，暂不拆页 |

## 3. index.html 目标布局

三轨各一 `<h2>`（h2「角色导航」取消），卡片沿用现样式；副卡加「⇄」角标注明正卡所在轨。卡片文案全量：

| 轨 | 卡片文案（标题 ｜ 一句话 ｜ 关键词行） | 链接 | badge |
|---|---|---|---|
| 日常运维 | 运维人员 ｜ 把平台从零搭起来并看住的人 ｜ 起栈 · 开号 · 备份 | ops.html | 实例管理员 |
| 日常运维 | 运营人员 ｜ 拿着顶层组的项目负责人 ｜ 组树 · 授权 · 里程碑 | ops.html#gov | 顶层组 Owner |
| 日常运维 | 平台工程 ⇄ ｜ 同一页的另一半：runner · 镜像库 · 对象存储 ｜ 基础设施视角 | platform.html | platform 组 Maintainer |
| 代码交付 | 开发工程师 ｜ 写代码的人（出差驻场？看场景篇） ｜ 分支 · MR · 等CI绿 | developer.html | Developer 30 |
| 代码交付 | 仓库 Owner ｜ 守门与发布的人 ｜ 评审 · tag · Release · 分诊 | owner.html | Maintainer 40 |
| 代码交付 | 只读协作者 ｜ 只看不动代码的人 ｜ 项目页 · 制品下载 | viewer.html | Guest 10 |
| 代码交付 | 平台工程 ｜ 管 CI 宪法与制品基础设施的人 ｜ 宪法 · 模板 · 传播 | platform.html | platform 组 Maintainer |
| 需求管理 | 需求提出人 ｜ 提需求、报缺陷的人 ｜ 模板建单 · 追进度 | submitter.html#flow-a | 提单人 Guest |
| 需求管理 | 需求管理者 ｜ 盯进度、主持例会的人 ｜ 看板三屏 · 里程碑 | submitter.html#flow-b | 管理者 Reporter |

- 分诊动作归域 Owner（术语表现状），仓库 Owner 卡关键词已含「分诊」，不向需求轨复制内容。

## 4. ops.html 页骨架（教程房风适配）

CSS 复制现教程房风，新增 details/summary 折叠样式（查阅层用）。结构镜像教程页「你是谁 → 能做/不能做 → 典型任务流 → 自救 → 红线 → 延伸」，任务流位换为「实施主线 + 查阅层」。

| 区块（h2） | 内容来源（现 gitlab-ops.md） |
|---|---|
| 你是谁 | 受众行以教程口吻恢复落位（即工作区删掉的那行）；badge「实例管理员」；一句话点明双读者——实施期的运维，与长期治理的顶层 Owner（见 #gov） |
| 能做 / 不能做 | 新写小表：起栈 / Runner 注册 / 开号 / 封禁 / 备份 ✅；业务代码 / 模板内容 ❌（链 platform 教程） |
| 实施主线：五步把平台建起来 | 五个 .step 块，见下 |
| ↳ 第 1 步 部署准备 | 现 §2（主机 / 镜像预拉 / 端口 / 凭据表） |
| ↳ 第 2 步 起栈与就绪（id=run） | 现 §3，含 Runner 注册四小步与 GID 坑位 |
| ↳ 第 3 步 首启初始化 | 现 §4（root 改密 / 核对注册关 / 关 Web IDE 回退；seed-once 原则集中一条） |
| ↳ 第 4 步 组织与治理（id=gov） | 章首**双视角导语**：实施的人按 4a 建一遍；治理的人（顶层 Owner）从 4b 起长期在此活动。**4a 一次性建立**＝现 §5.1–5.5（组树 / 三级权限 / 仓库与保护分支 / CI 模板 / 需求流配置）；**4b 持续治理**＝从 §5.2 尾注与 §6 提炼：授权变更一律 API 留痕、新增产品域子组、里程碑命名口径、顶层 Owner 兼任平台维护人 |
| ↳ 第 5 步 转入日常 | 桥接段：链查阅层各区 |
| 查阅：架构与组件表（id=arch） | 现 §1 全部；mermaid → 内嵌 SVG；「本表是准绳」原则原样保留 |
| 查阅：日常运维 | 现 §6 三小节（开账号 / 封禁回收 / 备份恢复） |
| 查阅：原型复现 | 附录 A（A–Z 段表），details 折叠 |
| 查阅：已知坑位 | 附录 B，指向验证结论 §3 |
| 红线清单 | 提炼 4 条：未演练的备份＝没有备份 / 组件表是准绳（改 yml 先对表）/ 原型口令仅限原型栈 / seed-once（改设置直改 DB，不改 compose） |
| 延伸阅读 | design / adr / 验证结论锚点列表 |

- 事实性内容以昨日 v1 为基线只搬不改；新增文字仅两处——「能做/不能做」小表与 4b 持续治理小节（≤10 行，素材取自现 §5.2/§5.5/§6 已有口径，不引入新事实）。
- h1「运维上手指南」，tagline「从零实施五步 + 日常运维查阅——起栈、开号、封禁、备份」。
- 关键区块显式 id：`gov` / `arch` / `run`（compose 两处注释将指 arch 与 run，见 §5）。

## 5. 驻场降级与联动改动

| 文件 | 改动 |
|---|---|
| field-engineer.html | h1 改「驻场场景篇」；badge 改「场景 · 出场前 Developer / 现场 Guest」；「你是谁」段首加「这不是独立角色——你是身处驻场情境的开发工程师」+ 返 developer 链；任务流/红线不动 |
| developer.html | 典型任务流后加小节「出差驻场？」链接卡 → field-engineer.html |
| index.html | 撤驻场角色卡，三轨九卡落位 |
| submitter.html | 两个任务流 h2 加显式 id：flow-a / flow-b |
| check.py | SKELETON：index 改 [`通用入门`,`术语速查`,`日常运维`,`代码交付`,`需求管理`]；新增 `ops`: [`你是谁`,`能做`,`实施主线`,`查阅`,`红线`,`延伸`]；field 页型沿用；图片下限对 ops 页豁免（SVG 内嵌不计 img） |
| README.md | 阅读地图行改指 `docs/tutorials/ops.html`；「六角色」表述改三轨；目录树移除 ops/ |
| gitlab-compose-test/docker-compose.yml | 两处注释改指新锚：25 行（§1 组件表）→ `docs/tutorials/ops.html#arch`；77 行（§3 Runner 注册）→ `docs/tutorials/ops.html#run` |
| docs/ops/gitlab-ops.md | 删除（内容已迁）；md→html 全文重写断 `--follow` 相似度，接受，页脚注明前身与 spec 溯源 |

实施顺序：ops.html（内容迁移 + SVG）→ index 三轨 → field/developer 场景链 → submitter 加 id → check.py 页型 → README / compose 收尾。

## 6. 边界（不做）

- submitter 拆页、platform 拆页（均为已拍板的"暂不"）。
- ops 事实性内容只搬不改（新增文字限 §4 所列两处）；发现的事实错误另行走修。
- 通用入门、术语速查内容不动（仅布局归位）。
- 教程页视觉不新设计，沿用现房风。

## 7. 验收标准

1. `check.py` 对 8 页（index / developer / owner / viewer / platform / field / submitter / ops）全绿。
2. index 三轨 9 卡，无驻场角色卡；全部链接含锚点可达；developer↔field 双向链路通。
3. ops.html：无外部资源引用；架构 SVG 与 compose 实况一一对应（承袭昨日验收 #2 口径）；「示例值」标注、seed-once 原则、准绳原则齐全；受众定位恢复；#gov 章双视角导语与 4a/4b 切分在位。
4. 仓内 grep `gitlab-ops|gitlab-repro` 除 specs 目录存档（含本 spec）外零残留；`docs/ops/` 目录不存在。
5. 工作区遗留的受众行删除并入本次变更，不留孤立改动。
