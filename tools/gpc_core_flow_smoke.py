#!/usr/bin/env python3
"""Transactional core-flow smoke checks for GlobalCloud GPC.

The script uses Odoo's own ORM and rolls back the transaction before exit.
It proves create/read/update/state-transition behavior without polluting the
local database.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
import urllib.error
import urllib.request
from datetime import date
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

REQUIRED_MODULES = ("contacts", "crm", "sale_management", "purchase", "stock", "mrp", "project")


def http_probe(url: str, timeout: int = 10) -> dict[str, Any]:
    started = time.time()
    try:
        with urllib.request.urlopen(url, timeout=timeout) as response:
            body = response.read()
            return {"ok": 200 <= response.status < 400, "status": response.status, "bytes": len(body), "seconds": round(time.time() - started, 3)}
    except urllib.error.HTTPError as exc:
        return {"ok": 200 <= exc.code < 400, "status": exc.code, "bytes": 0, "seconds": round(time.time() - started, 3)}
    except Exception as exc:
        return {"ok": False, "status": None, "error": str(exc), "bytes": 0, "seconds": round(time.time() - started, 3)}


def mark(ok: bool, evidence: dict[str, Any], error: str | None = None) -> dict[str, Any]:
    result = {"ok": ok, **evidence}
    if error:
        result["error"] = error
    return result


def run_orm_smoke(config_path: str, db_name: str) -> dict[str, Any]:
    import odoo
    from odoo import api
    from odoo.exceptions import AccessError
    from odoo.modules.registry import Registry
    from odoo.tools import config

    config.parse_config(["-c", config_path, "-d", db_name, "--log-level=warn"])
    del odoo  # imported for side effects and explicit dependency clarity

    flows: dict[str, Any] = {}
    with Registry(db_name).cursor() as cr:
        env = api.Environment(cr, api.SUPERUSER_ID, {})

        installed = set(env["ir.module.module"].search([("name", "in", REQUIRED_MODULES), ("state", "=", "installed")]).mapped("name"))
        missing = sorted(set(REQUIRED_MODULES) - installed)
        flows["module_baseline"] = mark(not missing, {"required": list(REQUIRED_MODULES), "installed": sorted(installed), "missing": missing})
        if missing:
            cr.rollback()
            return flows

        partner = env["res.partner"].create(
            {
                "name": "GPC Smoke Customer",
                "email": "gpc-smoke-customer@example.invalid",
                "lang": "zh_CN",
                "tz": "Asia/Shanghai",
            }
        )
        partner.write({"phone": "13800000000"})
        flows["contact_crud"] = mark(
            partner.exists() and partner.phone == "13800000000" and partner.lang == "zh_CN",
            {"model": "res.partner", "record_id": partner.id, "created_name": partner.name, "updated_phone": partner.phone, "lang": partner.lang, "tz": partner.tz},
        )

        try:
            lead = env["crm.lead"].create(
                {
                    "name": "GPC Smoke Opportunity",
                    "partner_id": partner.id,
                    "type": "opportunity",
                    "expected_revenue": 1000,
                }
            )
            before = lead.stage_id.name
            lead.action_set_won_rainbowman()
            flows["crm_opportunity"] = mark(
                bool(lead.stage_id.is_won),
                {"model": "crm.lead", "record_id": lead.id, "before_stage": before, "after_stage": lead.stage_id.name, "is_won": bool(lead.stage_id.is_won)},
            )
        except Exception as exc:
            flows["crm_opportunity"] = mark(False, {"model": "crm.lead"}, repr(exc))

        try:
            product = env["product.product"].create(
                {
                    "name": "GPC Smoke Product",
                    "type": "consu",
                    "list_price": 100,
                    "standard_price": 50,
                }
            )
            sale = env["sale.order"].create(
                {
                    "partner_id": partner.id,
                    "order_line": [(0, 0, {"product_id": product.id, "product_uom_qty": 2, "price_unit": 100})],
                }
            )
            before = sale.state
            sale.action_confirm()
            flows["sales_order"] = mark(
                sale.state == "sale" and len(sale.picking_ids) >= 1,
                {"model": "sale.order", "record_id": sale.id, "before_state": before, "after_state": sale.state, "delivery_count": len(sale.picking_ids)},
            )
        except Exception as exc:
            flows["sales_order"] = mark(False, {"model": "sale.order"}, repr(exc))

        try:
            vendor = env["res.partner"].create({"name": "GPC Smoke Vendor", "supplier_rank": 1})
            purchase = env["purchase.order"].create(
                {
                    "partner_id": vendor.id,
                    "order_line": [(0, 0, {"product_id": product.id, "product_qty": 3, "price_unit": 40, "date_planned": date.today()})],
                }
            )
            before = purchase.state
            purchase.button_confirm()
            flows["purchase_order"] = mark(
                purchase.state == "purchase" and len(purchase.picking_ids) >= 1,
                {"model": "purchase.order", "record_id": purchase.id, "before_state": before, "after_state": purchase.state, "receipt_count": len(purchase.picking_ids)},
            )
        except Exception as exc:
            flows["purchase_order"] = mark(False, {"model": "purchase.order"}, repr(exc))

        try:
            stock_location = env.ref("stock.stock_location_stock")
            customer_location = env.ref("stock.stock_location_customers")
            vendor_location = env.ref("stock.stock_location_suppliers")
            receipt_type = env.ref("stock.picking_type_in")
            delivery_type = env.ref("stock.picking_type_out")
            stock_product = env["product.product"].create({"name": "GPC Stock Smoke Product", "type": "consu", "is_storable": True})
            receipt = env["stock.picking"].create(
                {
                    "picking_type_id": receipt_type.id,
                    "location_id": vendor_location.id,
                    "location_dest_id": stock_location.id,
                    "move_ids": [
                        (
                            0,
                            0,
                            {
                                "description_picking": "GPC smoke receipt",
                                "product_id": stock_product.id,
                                "product_uom_qty": 5,
                                "product_uom": stock_product.uom_id.id,
                                "location_id": vendor_location.id,
                                "location_dest_id": stock_location.id,
                            },
                        )
                    ],
                }
            )
            receipt.action_confirm()
            receipt.action_assign()
            for move in receipt.move_ids:
                move.quantity = move.product_uom_qty
                move.picked = True
            receipt.button_validate()
            qty_after_receipt = env["stock.quant"]._get_available_quantity(stock_product, stock_location)

            delivery = env["stock.picking"].create(
                {
                    "picking_type_id": delivery_type.id,
                    "location_id": stock_location.id,
                    "location_dest_id": customer_location.id,
                    "move_ids": [
                        (
                            0,
                            0,
                            {
                                "description_picking": "GPC smoke delivery",
                                "product_id": stock_product.id,
                                "product_uom_qty": 2,
                                "product_uom": stock_product.uom_id.id,
                                "location_id": stock_location.id,
                                "location_dest_id": customer_location.id,
                            },
                        )
                    ],
                }
            )
            delivery.action_confirm()
            delivery.action_assign()
            for move in delivery.move_ids:
                move.quantity = move.product_uom_qty
                move.picked = True
            delivery.button_validate()
            qty_after_delivery = env["stock.quant"]._get_available_quantity(stock_product, stock_location)
            flows["stock_receipt_delivery"] = mark(
                receipt.state == "done" and delivery.state == "done" and qty_after_receipt == 5 and qty_after_delivery == 3,
                {
                    "receipt_id": receipt.id,
                    "delivery_id": delivery.id,
                    "receipt_state": receipt.state,
                    "delivery_state": delivery.state,
                    "qty_after_receipt": qty_after_receipt,
                    "qty_after_delivery": qty_after_delivery,
                },
            )
        except Exception as exc:
            flows["stock_receipt_delivery"] = mark(False, {"model": "stock.picking"}, repr(exc))

        try:
            stock_location = env.ref("stock.stock_location_stock")
            component = env["product.product"].create({"name": "GPC MRP Component", "type": "consu", "is_storable": True})
            finished = env["product.product"].create({"name": "GPC MRP Finished", "type": "consu", "is_storable": True})
            env["stock.quant"]._update_available_quantity(component, stock_location, 10)
            bom = env["mrp.bom"].create(
                {
                    "product_tmpl_id": finished.product_tmpl_id.id,
                    "product_qty": 1,
                    "product_uom_id": finished.uom_id.id,
                    "type": "normal",
                    "bom_line_ids": [(0, 0, {"product_id": component.id, "product_qty": 2, "product_uom_id": component.uom_id.id})],
                }
            )
            production = env["mrp.production"].create(
                {
                    "product_id": finished.id,
                    "product_qty": 1,
                    "product_uom_id": finished.uom_id.id,
                    "bom_id": bom.id,
                }
            )
            states = [production.state]
            production.action_confirm()
            states.append(production.state)
            production.move_raw_ids._action_assign()
            production.move_raw_ids.picked = True
            production.move_raw_ids._action_done()
            states.append(production.state)
            production.qty_producing = 1
            production.button_mark_done()
            states.append(production.state)
            qty_finished = env["stock.quant"]._get_available_quantity(finished, stock_location)
            flows["manufacturing_order"] = mark(
                production.state == "done" and production.move_raw_ids.state == "done" and production.move_finished_ids.state == "done" and qty_finished == 1,
                {
                    "production_id": production.id,
                    "states": states,
                    "raw_moves": len(production.move_raw_ids),
                    "finished_moves": len(production.move_finished_ids),
                    "qty_finished": qty_finished,
                },
            )
        except Exception as exc:
            flows["manufacturing_order"] = mark(False, {"model": "mrp.production"}, repr(exc))

        try:
            project = env["project.project"].create({"name": "GPC Smoke Project"})
            task = env["project.task"].create({"name": "GPC Smoke Task", "project_id": project.id})
            stages = env["project.task.type"].search([], limit=2)
            before = task.stage_id.name
            if len(stages) >= 2:
                task.write({"stage_id": stages[1].id})
            flows["project_task"] = mark(
                bool(task.exists() and task.project_id.id == project.id and task.stage_id),
                {"model": "project.task", "record_id": task.id, "project_id": project.id, "before_stage": before, "after_stage": task.stage_id.name},
            )
        except Exception as exc:
            flows["project_task"] = mark(False, {"model": "project.task"}, repr(exc))

        try:
            user_model = env["res.users"].with_context(active_test=False)
            admin = user_model.search([("login", "=", "gcgpc@csydsc.com")], limit=1) or env.ref("base.user_admin")
            public = env.ref("base.public_user")
            portal = user_model.search([("login", "=", "portal")], limit=1)
            portal_source = "existing"
            if not portal:
                portal_source = "created_for_smoke"
                group_field = "groups_id" if "groups_id" in env["res.users"]._fields else "group_ids"
                portal_partner = env["res.partner"].create({"name": "GPC Smoke Portal User", "email": "gpc-smoke-portal@example.invalid"})
                portal = env["res.users"].with_context(no_reset_password=True).create(
                    {
                        "name": "GPC Smoke Portal User",
                        "login": "gpc-smoke-portal@example.invalid",
                        "email": "gpc-smoke-portal@example.invalid",
                        "partner_id": portal_partner.id,
                        group_field: [(6, 0, [env.ref("base.group_portal").id])],
                    }
                )
            admin_partner = env(user=admin)["res.partner"].create({"name": "GPC Permission Smoke Customer"})
            denied: dict[str, str] = {}
            for login, user in (("portal", portal), ("public", public)):
                try:
                    env(user=user)["sale.order"].create({"partner_id": partner.id})
                    denied[login] = "unexpectedly_allowed"
                except Exception as exc:
                    denied[login] = type(exc).__name__
            flows["permission_boundary"] = mark(
                bool(admin_partner.id) and denied == {"portal": "AccessError", "public": "AccessError"},
                {
                    "admin_create_partner": bool(admin_partner.id),
                    "admin_login": admin.login,
                    "portal_login": portal.login,
                    "portal_source": portal_source,
                    "portal_sale_create": denied.get("portal"),
                    "public_login": public.login,
                    "public_sale_create": denied.get("public"),
                    "expected_denial": "AccessError",
                },
            )
        except AccessError as exc:
            flows["permission_boundary"] = mark(False, {"model": "res.users/sale.order"}, repr(exc))
        except Exception as exc:
            flows["permission_boundary"] = mark(False, {"model": "res.users/sale.order"}, repr(exc))

        cr.rollback()

    return flows


def markdown_report(result: dict[str, Any]) -> str:
    lines = [
        "# GlobalCloud GPC 核心流程 Smoke Test 报告",
        "",
        f"执行时间戳：`{result['timestamp']}`",
        f"配置文件：`{result['config']}`",
        f"数据库：`{result['database']}`",
        f"基础地址：`{result['base_url']}`",
        f"总体结果：`{'通过' if result['ok'] else '失败'}`",
        "",
        "## HTTP 入口",
        "",
        "| 入口 | 结果 | HTTP 状态 | 证据 |",
        "|---|---|---:|---|",
    ]
    for name, probe in result["http"].items():
        lines.append(f"| {name} | {'通过' if probe.get('ok') else '失败'} | {probe.get('status')} | `{json.dumps(probe, ensure_ascii=False)}` |")

    lines += [
        "",
        "## ORM 核心流程",
        "",
        "| 流程 | 结果 | 关键证据 |",
        "|---|---|---|",
    ]
    for name, flow in result["flows"].items():
        lines.append(f"| {name} | {'通过' if flow.get('ok') else '失败'} | `{json.dumps(flow, ensure_ascii=False, default=str)}` |")
    lines += [
        "",
        "说明：所有 ORM 写入都在同一事务内完成，脚本结束前执行 rollback，因此不会污染当前数据库。",
    ]
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default=".runtime/gpc-odoo.conf")
    parser.add_argument("--database", default="GCGPC")
    parser.add_argument("--base-url", default="http://127.0.0.1:8069")
    parser.add_argument("--report-json")
    parser.add_argument("--report-md")
    args = parser.parse_args()

    base = args.base_url.rstrip("/")
    result: dict[str, Any] = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "config": args.config,
        "database": args.database,
        "base_url": base,
        "http": {
            "website_home": http_probe(base + "/"),
            "login": http_probe(base + "/web/login"),
            "apps": http_probe(base + "/odoo/apps"),
        },
        "flows": run_orm_smoke(args.config, args.database),
    }
    result["ok"] = all(item.get("ok") for item in result["http"].values()) and all(item.get("ok") for item in result["flows"].values())

    if args.report_json:
        Path(args.report_json).parent.mkdir(parents=True, exist_ok=True)
        Path(args.report_json).write_text(json.dumps(result, ensure_ascii=False, indent=2, default=str) + "\n", encoding="utf-8")
    if args.report_md:
        Path(args.report_md).parent.mkdir(parents=True, exist_ok=True)
        Path(args.report_md).write_text(markdown_report(result), encoding="utf-8")

    print(json.dumps(result, ensure_ascii=False, indent=2, default=str))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
