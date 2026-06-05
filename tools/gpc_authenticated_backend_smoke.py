#!/usr/bin/env python3
"""Authenticated backend HTTP smoke checks for GlobalCloud GPC."""

from __future__ import annotations

import argparse
import html
import http.cookiejar
import json
import re
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


BACKEND_ENTRIES = (
    ("discuss", "/odoo/discuss"),
    ("apps", "/odoo/apps"),
    ("contacts", "/odoo/contacts"),
    ("crm", "/odoo/crm"),
    ("sales", "/odoo/sales"),
    ("purchase", "/odoo/purchase"),
    ("inventory", "/odoo/inventory"),
    ("manufacturing", "/odoo/manufacturing"),
    ("project", "/odoo/project"),
)


def ensure_test_user(config_path: str, db_name: str, login: str, password: str) -> dict[str, Any]:
    import odoo
    from odoo import api
    from odoo.modules.registry import Registry
    from odoo.tools import config

    config.parse_config(["-c", config_path, "-d", db_name, "--log-level=warn"])
    del odoo

    group_xmlids = (
        "base.group_user",
        "base.group_system",
        "sales_team.group_sale_manager",
        "purchase.group_purchase_manager",
        "stock.group_stock_manager",
        "mrp.group_mrp_manager",
        "project.group_project_manager",
    )
    with Registry(db_name).cursor() as cr:
        env = api.Environment(cr, api.SUPERUSER_ID, {"active_test": False})
        groups = [env.ref(xmlid).id for xmlid in group_xmlids]
        user = env["res.users"].search([("login", "=", login)], limit=1)
        group_field = "groups_id" if "groups_id" in env["res.users"]._fields else "group_ids"
        values = {
            "name": "GlobalCloud GPC E2E User",
            "login": login,
            "email": login,
            "lang": "zh_CN",
            "tz": "Asia/Shanghai",
            "active": True,
            group_field: [(6, 0, groups)],
        }
        if user:
            user.write(values)
        else:
            user = env["res.users"].create(values)
        user.write({"password": password})
        cr.commit()
        return {"user_id": user.id, "login": login, "groups": list(group_xmlids)}


def open_text(opener: urllib.request.OpenerDirector, url: str, data: bytes | None = None, timeout: int = 15) -> tuple[str, str, int]:
    request = urllib.request.Request(url, data=data)
    if data is not None:
        request.add_header("Content-Type", "application/x-www-form-urlencoded")
    with opener.open(request, timeout=timeout) as response:
        return response.geturl(), response.read().decode("utf-8", "replace"), response.status


def extract_csrf_token(html_text: str) -> str:
    match = re.search(r'name=["\']csrf_token["\'][^>]*value=["\']([^"\']+)["\']', html_text)
    if not match:
        raise RuntimeError("csrf_token not found on login page")
    return html.unescape(match.group(1))


def run_backend_smoke(base_url: str, login: str, password: str) -> dict[str, Any]:
    base = base_url.rstrip("/")
    cookie_jar = http.cookiejar.CookieJar()
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cookie_jar))

    login_url, login_page, login_status = open_text(opener, base + "/web/login")
    csrf_token = extract_csrf_token(login_page)
    payload = urllib.parse.urlencode(
        {
            "csrf_token": csrf_token,
            "login": login,
            "password": password,
            "redirect": "/odoo/discuss",
        }
    ).encode()
    authenticated_url, authenticated_page, authenticated_status = open_text(opener, base + "/web/login", payload)
    authenticated = authenticated_status < 400 and "name=\"login\"" not in authenticated_page and "/web/login" not in authenticated_url

    entries: dict[str, Any] = {}
    for name, path in BACKEND_ENTRIES:
        started = time.time()
        try:
            final_url, body, status = open_text(opener, base + path)
            visible_text = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", body))
            entries[name] = {
                "ok": status < 400 and "name=\"login\"" not in body and "/web/login" not in final_url,
                "path": path,
                "status": status,
                "final_url": final_url,
                "bytes": len(body.encode()),
                "seconds": round(time.time() - started, 3),
                "has_webclient_asset": "web.assets_web" in body or "o_web_client" in body,
                "visible_has_legacy_brand": bool(re.search(r"\bOdoo\b", visible_text)),
            }
        except Exception as exc:
            entries[name] = {"ok": False, "path": path, "error": str(exc), "seconds": round(time.time() - started, 3)}

    return {
        "login_page": {"ok": login_status == 200, "url": login_url, "status": login_status},
        "authenticated": {"ok": authenticated, "url": authenticated_url, "status": authenticated_status},
        "entries": entries,
        "ok": authenticated and all(item.get("ok") and not item.get("visible_has_legacy_brand") for item in entries.values()),
    }


def markdown_report(result: dict[str, Any]) -> str:
    lines = [
        "# GlobalCloud GPC 登录态后台 HTTP Smoke 报告",
        "",
        f"执行时间戳：`{result['timestamp']}`",
        f"基础地址：`{result['base_url']}`",
        f"测试账号：`{result['test_user']['login']}`",
        f"总体结果：`{'通过' if result['ok'] else '失败'}`",
        "",
        "| 入口 | 结果 | HTTP 状态 | 最终 URL | 旧品牌残留 |",
        "|---|---|---:|---|---|",
    ]
    for name, entry in result["backend"]["entries"].items():
        lines.append(
            f"| {name} | {'通过' if entry.get('ok') else '失败'} | {entry.get('status')} | `{entry.get('final_url', '')}` | {'有' if entry.get('visible_has_legacy_brand') else '无'} |"
        )
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default=".runtime/gpc-odoo.conf")
    parser.add_argument("--database", default="GCGPC")
    parser.add_argument("--base-url", default="http://127.0.0.1:8069")
    parser.add_argument("--login", default="gpc.e2e@example.invalid")
    parser.add_argument("--password", default="GpcE2E-2026!")
    parser.add_argument("--report-json")
    parser.add_argument("--report-md")
    args = parser.parse_args()

    test_user = ensure_test_user(args.config, args.database, args.login, args.password)
    backend = run_backend_smoke(args.base_url, args.login, args.password)
    result = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "config": args.config,
        "database": args.database,
        "base_url": args.base_url.rstrip("/"),
        "test_user": test_user,
        "backend": backend,
        "ok": backend["ok"],
    }

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
