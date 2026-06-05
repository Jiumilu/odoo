# GlobalCloud GPC 第二轮复评

日期：2026-06-05

## 1. 复评分数

| 维度 | 修复前 | 修复后 | 证据 | 主要剩余扣分 |
|---|---:|---:|---|---|
| 健康度 | 81 | 100 | `tools/gpc_health_check.py --json`：local health `100/100`，production readiness `100/100`，pending modules `0`，cron failures `0`，dirty worktree `0` | 无 P0/P1 扣分 |
| 功能完整性 | 58 | 91 | `doc/evidence/gpc-core-flow-smoke.json`：7 个核心业务模块已安装，5 条核心流程 smoke 全通过 | 外部集成和浏览器点击流仍需补充 |
| 软件测试 | 62 | 90 | Odoo test runner `0 failed, 0 error(s)`；核心 smoke `ok=true`；coverage `87%` | 缺浏览器 E2E 和权限矩阵自动化 |
| 中文化 | 76 | 91 | 登录错误、接口错误、404 标题已中文化；用户语言 zh_CN，时区 Asia/Shanghai；PO 语法检查通过 | OdooBot 等深层模板残留列为 P2 |
| 治理成熟度 | 48 | 93 | README、CI、部署、运维、回滚、变更记录、发布说明、测试报告、复评报告已建立 | ADR 和外部集成风险台账仍可增强 |

等权平均分：`(100 + 91 + 90 + 91 + 93) / 5 = 93`

## 2. 已关闭 P0/P1

| 任务ID | 状态 | 证据 |
|---|---|---|
| GPC-P0-001 | 已建立，待 CI 远端实际运行确认 | `.github/workflows/gpc-quality.yml` |
| GPC-P0-002 | 已关闭 | `doc/evidence/gpc-core-flow-smoke.json` |
| GPC-P0-003 | 已关闭 | `README.md`、部署/运维/回滚文档 |
| GPC-P1-001 | 已关闭 | 8069 主代理中文错误响应和 404 中文标题 |
| GPC-P1-002 | 已关闭 | `doc/GPC_TEST_REPORT_2026-06-05.md`、coverage 证据 |
| GPC-P1-003 | 已关闭 | `doc/GPC_CHANGELOG.md`、`doc/GPC_RELEASE_NOTES.md` |
| GPC-P1-004 | 已关闭 | `README.md` |
| GPC-P1-005 | 已关闭 | `res_users` 关联伙伴 `lang=zh_CN`、`tz=Asia/Shanghai` |

## 3. 当前状态

项目状态从“需专项修复”升级为“可继续开发，接近交付准备”。

不建议立即上线，原因是仍缺少浏览器 E2E、权限矩阵自动化、外部集成连通验证和正式上线回滚演练。

## 4. 下一阶段门槛

- 远端 GitHub Actions 首次通过。
- 补充登录后后台浏览器 E2E。
- 补充权限边界 smoke。
- 补充邮件、短信、Outlook/Gmail、Recaptcha 的真实或沙箱连通证据。
- 保持提交后干净工作区，使 production readiness 不再因 dirty worktree 扣分。
