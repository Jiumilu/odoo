#!/usr/bin/env python3
"""Apply idempotent runtime localization defaults for GlobalCloud GPC."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

REPLACEMENTS = {
    "OdooBot": "GlobalCloud GPC 助手",
    "odoobot@example.com": "bot@gc-gpc.example.com",
    "info@yourcompany.example.com": "service@gc-gpc.example.com",
    "info@globalcloud-gpc.example.com": "service@gc-gpc.example.com",
    "vauxoo@yourcompany.example.com": "partner@gc-gpc.example.com",
    "vauxoo@globalcloud-gpc.example.com": "partner@gc-gpc.example.com",
    "chicago@yourcompany.com": "branch@gc-gpc.example.com",
    "chicago@globalcloud-gpc.com": "branch@gc-gpc.example.com",
    "YourCompany": "GlobalCloud GPC",
    "yourcompany": "globalcloud-gpc",
    "公司 name": "GlobalCloud GPC",
    "+1 555-555-5556": "18607163009",
    "+1 312 349 3030": "18607163009",
}


def replace_text(value: Any) -> tuple[Any, bool]:
    if not isinstance(value, str):
        return value, False
    updated = value
    for old, new in REPLACEMENTS.items():
        updated = updated.replace(old, new)
    return updated, updated != value


def replace_jsonb_column(cr, table: str, column: str) -> int:
    from psycopg2 import sql

    changed = 0
    for old, new in REPLACEMENTS.items():
        cr.execute(
            sql.SQL("UPDATE {} SET {} = replace({}::text, %s, %s)::jsonb WHERE {}::text LIKE %s").format(
                sql.Identifier(table),
                sql.Identifier(column),
                sql.Identifier(column),
                sql.Identifier(column),
            ),
            (old, new, f"%{old}%"),
        )
        changed += cr.rowcount
    return changed


def has_model(env, model_name: str) -> bool:
    return model_name in env.registry.models


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default=".runtime/gpc-odoo.conf")
    parser.add_argument("--database", default="GCGPC")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    import odoo
    from odoo import api
    from odoo.modules.registry import Registry
    from odoo.tools import config

    config.parse_config(["-c", args.config, "-d", args.database, "--log-level=warn"])
    del odoo

    evidence: dict[str, Any] = {
        "views": [],
        "mail_templates": [],
        "partners": [],
        "companies": [],
        "websites": [],
        "discuss_channels": [],
        "mail_messages": [],
        "skipped_models": [],
    }
    with Registry(args.database).cursor() as cr:
        env = api.Environment(cr, api.SUPERUSER_ID, {"active_test": False})

        for view in env["ir.ui.view"].search([]):
            new_arch, changed = replace_text(view.arch_db)
            if changed:
                view.write({"arch_db": new_arch})
                evidence["views"].append({"id": view.id, "key": view.key, "name": view.name})

        if has_model(env, "mail.template"):
            for template in env["mail.template"].search([]):
                updates = {}
                new_body, body_changed = replace_text(template.body_html)
                if body_changed:
                    updates["body_html"] = new_body
                new_subject, subject_changed = replace_text(template.subject)
                if subject_changed:
                    updates["subject"] = new_subject
                if updates:
                    template.write(updates)
                    evidence["mail_templates"].append({"id": template.id, "name": template.name})
        else:
            evidence["skipped_models"].append("mail.template")

        for partner in env["res.partner"].search([]):
            updates = {}
            for field in ("name", "email", "phone", "website"):
                if field in partner._fields:
                    new_value, changed = replace_text(partner[field])
                    if changed:
                        updates[field] = new_value
            if updates:
                partner.write(updates)
                evidence["partners"].append({"id": partner.id, "updates": updates})

        for company in env["res.company"].search([], order="id"):
            updates = {}
            for field in ("email", "phone", "website"):
                if field in company._fields:
                    new_value, changed = replace_text(company[field])
                    if changed:
                        updates[field] = new_value
            if updates:
                company.write(updates)
                evidence["companies"].append({"id": company.id, "name": company.name, "updates": updates})

        if has_model(env, "discuss.channel"):
            for channel in env["discuss.channel"].search([]):
                new_name, changed = replace_text(channel.name)
                if changed:
                    channel.write({"name": new_name})
                    evidence["discuss_channels"].append({"id": channel.id, "updates": {"name": new_name}})
        else:
            evidence["skipped_models"].append("discuss.channel")

        if has_model(env, "mail.message"):
            for message in env["mail.message"].search([]):
                updates = {}
                for field in ("subject", "body"):
                    if field in message._fields:
                        new_value, changed = replace_text(message[field])
                        if changed:
                            updates[field] = new_value
                if updates:
                    message.write(updates)
                    evidence["mail_messages"].append({"id": message.id, "updates": sorted(updates)})
        else:
            evidence["skipped_models"].append("mail.message")

        if has_model(env, "website"):
            for website in env["website"].search([]):
                updates = {}
                new_name, changed = replace_text(website.name)
                if changed or website.name != "绿色供应链公共服务平台":
                    updates["name"] = "绿色供应链公共服务平台"
                if updates:
                    website.write(updates)
                    evidence["websites"].append({"id": website.id, "updates": updates})
        else:
            evidence["skipped_models"].append("website")

        evidence["jsonb_replacements"] = {
            "ir_ui_view.arch_db": replace_jsonb_column(cr, "ir_ui_view", "arch_db"),
        }
        if has_model(env, "mail.template"):
            evidence["jsonb_replacements"].update(
                {
                    "mail_template.name": replace_jsonb_column(cr, "mail_template", "name"),
                    "mail_template.subject": replace_jsonb_column(cr, "mail_template", "subject"),
                    "mail_template.body_html": replace_jsonb_column(cr, "mail_template", "body_html"),
                }
            )

        cr.commit()

    print(json.dumps(evidence, ensure_ascii=False, indent=2) if args.json else evidence)
    return 0


if __name__ == "__main__":
    sys.exit(main())
