# 智能挖机 · 统一代码管理体系

50+ 人多团队（固件 / 算法 / 车载 / 云端 / App）的代码托管、CI/CD、制品与需求流体系。平台为自建 GitLab（极狐发行版、免费版档）一体化，已在本地原型上三阶段实证；设计在与集团 DLP / VPN 管理框架共存的前提下自洽可独立落地，并预留向集团设施迁移的接口。

## 阅读地图

| 你是谁 | 读什么 |
|---|---|
| 评审者 / 干系人 | `docs/design/` 三份设计（决策事实来源）→ `docs/adr/` 21 条决策记录 → `docs/design/2026-09-07-prototype-verification.md` 验证结论 |
| 团队成员（任一角色） | `docs/tutorials/index.html`——按角色 5–10 分钟上手 |
| 平台运维 / 复现环境 | `docs/ops/gitlab-repro.md`（从零搭起、复刻终态、日常运维）→ `gitlab-compose-test/`（compose 栈 + 截图脚本 + 证据 01–43） |

## 目录

```
docs/
├── design/       三份设计文档 + 原型验证结论（本体系的事实来源）
├── adr/          21 条架构决策记录 + 索引（含否决备选与重开条件）
├── ops/          运维与复现手册（GitLab 从零搭起、日常运维）
└── tutorials/    六角色上手教程（HTML，含截图）
gitlab-compose-test/  本地原型环境：compose 栈、示例仓库、截图证据
```

## 原型环境速览

极狐 GitLab 19.3.1-jh.0（实测版本）@ http://10.66.35.35:8081（docker compose 栈，含 Runner / MinIO / Harbor）。教程截图与验证证据均出自该实例；原型一次性口令内嵌于 compose（仅限本测试栈，正式实施凭据另行管理）。
