# GlobalCloud GPC 测试报告

日期：2026-06-05

## 1. 测试资产

| 类型 | 资产 | 状态 |
|---|---|---|
| 依赖一致性 | `python -m pip check` | 已运行 |
| 工具脚本编译 | `python -m py_compile tools/*.py` | 已运行 |
| 中文 PO 语法 | `msgfmt --check` | 已运行 |
| Odoo 官方 test runner | `:TestSelector.test_selector_parser` | 已运行 |
| 核心业务 smoke | `tools/gpc_core_flow_smoke.py` | 已运行 |
| 权限边界 smoke | `tools/gpc_core_flow_smoke.py` 中 `permission_boundary` | 已运行 |
| 浏览器 E2E | `doc/evidence/gpc-browser-e2e-2026-06-06.md` | 已运行 |
| 覆盖率基线 | `coverage run ... tools/gpc_core_flow_smoke.py` | 已建立 |

## 2. 当前通过证据

- 依赖一致性：`No broken requirements found.`
- Odoo test runner：`0 failed, 0 error(s) of 1 tests`
- 核心业务 smoke：`doc/evidence/gpc-core-flow-smoke.json` 中 `ok=true`
- 核心业务流程覆盖：联系人、CRM 机会、销售订单、采购订单、项目任务、权限边界
- 浏览器 E2E：公开首页、登录页、404 页可渲染，中文品牌可见，无 YourCompany/OdooBot/公司 name 可见残留
- 覆盖率基线：`doc/evidence/gpc-coverage.txt` 显示 `tools/gpc_core_flow_smoke.py` 覆盖率 `85%`

## 3. 剩余限制

- 当前覆盖率优先覆盖本地工具和 smoke 执行链路，尚未覆盖全部 Odoo 上游模块。
- 浏览器 E2E 已覆盖公开页面、登录页和 404 页，尚未覆盖登录后后台点击流。
- 外部集成如邮件、短信、Outlook/Gmail、Recaptcha 已明确为当前评分范围外；若进入上线评分，仍需真实或沙箱连通测试。

## 4. 结论

测试证明力已经从“只有零散命令”提升为“CI、smoke、权限边界、浏览器 E2E、测试报告、覆盖率基线”组合。当前测试可支持继续开发和交付准备复评，但上线前仍应补充登录后后台 E2E 和外部集成测试。
