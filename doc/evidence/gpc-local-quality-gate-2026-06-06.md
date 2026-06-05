# GlobalCloud GPC 本地质量门禁证据

日期：2026-06-06

## 已执行门禁

| 门禁 | 命令 | 当前结果 |
|---|---|---|
| 工作树 | `git status --short --branch` | 提交后复跑应为干净工作树 |
| 健康检查 | `.venv311/bin/python tools/gpc_health_check.py --json` | `local_health_score=100`，`production_readiness_score=100` |
| Python 编译 | `.venv311/bin/python -m py_compile ...` | 通过 |
| 单元测试 | `.venv311/bin/python -m unittest discover -s tests -p 'test_*.py' -v` | `11/11 OK` |
| Node 依赖 | `npm ci` | Playwright 依赖可从本仓库 lockfile 安装 |
| 浏览器脚本语法 | `npm test` | 通过 |
| 认证后台 HTTP smoke | `.venv311/bin/python tools/gpc_authenticated_backend_smoke.py --config .runtime/gpc-odoo.conf --database GCGPC --base-url http://127.0.0.1:8069` | 通过，9 个后台入口无失败 |
| 核心业务 smoke | `.venv311/bin/python tools/gpc_core_flow_smoke.py --config .runtime/gpc-odoo.conf --database GCGPC --base-url http://127.0.0.1:8069 --report-json doc/evidence/gpc-core-flow-smoke.json --report-md doc/evidence/gpc-core-flow-smoke.md` | 通过 |
| 核心 smoke 覆盖率 | `.venv311/bin/coverage report -m tools/gpc_core_flow_smoke.py` | `99%` |
| 浏览器表单 E2E | `node tools/gpc_browser_form_e2e.cjs --base-url http://127.0.0.1:8069 --report-json doc/evidence/gpc-browser-form-e2e.json --report-md doc/evidence/gpc-browser-form-e2e.md --screenshot doc/evidence/gpc-browser-form-e2e.png` | 通过 |

## 当前限制

- 远端 GitHub Actions 未实际运行；当前为本地等价门禁。
- 浏览器表单 E2E 已标准化到本仓库 `package.json/package-lock.json`，本地复跑来源为 `/Users/lujunxiang/Projects/GlobalCloud GPC/node_modules/playwright/index.js`；正式远端验证仍需要推送到可执行远端。

## 结论

本地质量门禁已覆盖安装后运行健康、单元测试、核心业务 ORM 流程、认证后台入口、真实浏览器表单路径和覆盖率证据。
