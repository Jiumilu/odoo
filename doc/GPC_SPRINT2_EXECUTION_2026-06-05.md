# GlobalCloud GPC 第二轮执行记录

日期：2026-06-05

## 1. 本轮目标

- 关闭核心业务流程未闭环问题。
- 补测试报告和覆盖率基线。
- 修复关键中文错误提示。
- 修复中文业务环境默认时区。

## 2. 关键动作

- 安装核心业务模块：`contacts`、`crm`、`sale_management`、`purchase`、`stock`、`mrp`、`project`。
- 新增核心流程 smoke 脚本：`tools/gpc_core_flow_smoke.py`。
- 生成核心流程证据：`doc/evidence/gpc-core-flow-smoke.json`、`doc/evidence/gpc-core-flow-smoke.md`。
- 新增覆盖率基线：`doc/evidence/gpc-coverage.txt`、`doc/evidence/gpc-coverage.json`。
- 增强 `tools/gpc_reverse_proxy.py`，对 JSON 错误做中文化和 traceback 脱敏。
- 统一用户语言和时区：`zh_CN`、`Asia/Shanghai`。

## 3. 核心流程结果

| 流程 | 结果 | 状态变化 |
|---|---|---|
| 联系人 CRUD | 通过 | 创建联系人，更新电话、语言和时区 |
| CRM 机会 | 通过 | `New` -> `Won` |
| 销售订单 | 通过 | `draft` -> `sale`，生成 1 条出库 |
| 采购订单 | 通过 | `draft` -> `purchase`，生成 1 条入库 |
| 项目任务 | 通过 | 创建项目和任务，任务进入阶段 |

## 4. 验证命令

```bash
.venv311/bin/python tools/gpc_core_flow_smoke.py --config .runtime/gpc-odoo.conf --database GCGPC --base-url http://127.0.0.1:8069 --report-json doc/evidence/gpc-core-flow-smoke.json --report-md doc/evidence/gpc-core-flow-smoke.md
.venv311/bin/coverage run --include='*/tools/gpc_core_flow_smoke.py' tools/gpc_core_flow_smoke.py --config .runtime/gpc-odoo.conf --database GCGPC --base-url http://127.0.0.1:8069
.venv311/bin/coverage report -m tools/gpc_core_flow_smoke.py
.venv311/bin/python tools/gpc_health_check.py --json
```

## 5. 结论

第二轮后五项等权平均分复评为 `93/100`。该结论依赖当前数据库状态、当前运行服务和当前证据文件。
