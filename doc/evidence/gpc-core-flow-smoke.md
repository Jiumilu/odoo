# GlobalCloud GPC 核心流程 Smoke Test 报告

执行时间戳：`2026-06-06T07:03:05+0800`
配置文件：`.runtime/gpc-odoo.conf`
数据库：`GCGPC`
基础地址：`http://127.0.0.1:8069`
总体结果：`通过`

## HTTP 入口

| 入口 | 结果 | HTTP 状态 | 证据 |
|---|---|---:|---|
| website_home | 通过 | 200 | `{"ok": true, "status": 200, "bytes": 21202, "seconds": 1.287}` |
| login | 通过 | 200 | `{"ok": true, "status": 200, "bytes": 20192, "seconds": 0.232}` |
| apps | 通过 | 200 | `{"ok": true, "status": 200, "bytes": 20239, "seconds": 0.102}` |

## ORM 核心流程

| 流程 | 结果 | 关键证据 |
|---|---|---|
| module_baseline | 通过 | `{"ok": true, "required": ["contacts", "crm", "sale_management", "purchase", "stock", "mrp", "project"], "installed": ["contacts", "crm", "mrp", "project", "purchase", "sale_management", "stock"], "missing": []}` |
| contact_crud | 通过 | `{"ok": true, "model": "res.partner", "record_id": 103, "created_name": "GPC Smoke Customer", "updated_phone": "13800000000", "lang": "zh_CN", "tz": "Asia/Shanghai"}` |
| crm_opportunity | 通过 | `{"ok": true, "model": "crm.lead", "record_id": 65, "before_stage": "New", "after_stage": "Won", "is_won": true}` |
| sales_order | 通过 | `{"ok": true, "model": "sale.order", "record_id": 47, "before_state": "draft", "after_state": "sale", "delivery_count": 1}` |
| purchase_order | 通过 | `{"ok": true, "model": "purchase.order", "record_id": 34, "before_state": "draft", "after_state": "purchase", "receipt_count": 1}` |
| stock_receipt_delivery | 通过 | `{"ok": true, "receipt_id": 109, "delivery_id": 110, "receipt_state": "done", "delivery_state": "done", "qty_after_receipt": 5.0, "qty_after_delivery": 3.0}` |
| manufacturing_order | 通过 | `{"ok": true, "production_id": 22, "states": ["draft", "confirmed", "progress", "done"], "raw_moves": 1, "finished_moves": 1, "qty_finished": 1.0}` |
| project_task | 通过 | `{"ok": true, "model": "project.task", "record_id": 97, "project_id": 28, "before_stage": false, "after_stage": "Inbox"}` |
| permission_boundary | 通过 | `{"ok": true, "admin_create_partner": true, "portal_sale_create": "AccessError", "public_sale_create": "AccessError", "expected_denial": "AccessError"}` |

说明：所有 ORM 写入都在同一事务内完成，脚本结束前执行 rollback，因此不会污染当前数据库。
