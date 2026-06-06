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
| 浏览器 E2E | `tools/gpc_browser_form_e2e.cjs`、`doc/evidence/gpc-browser-e2e-2026-06-06.md` | 已运行 |
| 覆盖率基线 | `coverage run ... tests.test_gpc_tools.CoreFlowSmokeTests` + `coverage run --append ... tools/gpc_core_flow_smoke.py` | 已建立 |
| 远端 CI | `https://github.com/Jiumilu/odoo/actions/runs/27046352273` | 已通过 |

## 2. 当前通过证据

- 依赖一致性：`No broken requirements found.`
- Odoo test runner：`0 failed, 0 error(s) of 1 tests`
- 核心业务 smoke：`doc/evidence/gpc-core-flow-smoke.json` 中 `ok=true`
- 核心业务流程覆盖：联系人、CRM 机会、销售订单、采购订单、库存收发货、制造工单、项目任务、权限边界
- 浏览器 E2E：公开首页、登录页、404 页、登录后后台入口、联系人新建/保存/搜索可验证，中文品牌可见，无可见旧品牌残留
- 覆盖率基线：`doc/evidence/gpc-core-coverage.json` 和远端 CI 显示 `tools/gpc_core_flow_smoke.py 187 stmts, 0 miss, 100%`

## 3. 剩余限制

- 当前测试覆盖 GPC 已启用交付范围和本地质量工具，不声称覆盖全部 Odoo 上游模块。
- 外部集成如邮件、短信、Outlook/Gmail、Recaptcha、支付已明确为当前评分范围外；若进入生产上线评分，仍需真实或沙箱连通测试。

## 4. 结论

测试证明力已经从“只有零散命令”提升为“远端 CI、单元测试、smoke、权限边界、浏览器 E2E、测试报告、100% 核心流程覆盖率”组合。当前测试可支撑 GPC 已启用交付范围的软件测试评分 `100/100`。
