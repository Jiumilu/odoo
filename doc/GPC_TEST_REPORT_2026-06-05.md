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
| 覆盖率基线 | `coverage run ... tools/gpc_core_flow_smoke.py` | 已建立 |

## 2. 当前通过证据

- 依赖一致性：`No broken requirements found.`
- Odoo test runner：`0 failed, 0 error(s) of 1 tests`
- 核心业务 smoke：`doc/evidence/gpc-core-flow-smoke.json` 中 `ok=true`
- 核心业务流程覆盖：联系人、CRM 机会、销售订单、采购订单、项目任务
- 覆盖率基线：`doc/evidence/gpc-coverage.txt` 显示 `tools/gpc_core_flow_smoke.py` 覆盖率 `87%`

## 3. 剩余限制

- 当前覆盖率优先覆盖本地工具和 smoke 执行链路，尚未覆盖全部 Odoo 上游模块。
- 尚未建立浏览器 E2E 自动化登录和后台点击流。
- 外部集成如邮件、短信、Outlook/Gmail、Recaptcha 仍未做真实连通测试。

## 4. 结论

测试证明力已经从“只有零散命令”提升为“CI、smoke、测试报告、覆盖率基线”组合。当前测试可支持继续开发和交付准备复评，但上线前仍应补充浏览器 E2E、权限矩阵测试和外部集成测试。
