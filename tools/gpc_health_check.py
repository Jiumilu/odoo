#!/usr/bin/env python3
"""Read-only health score for the local GlobalCloud GPC Odoo checkout."""

from __future__ import annotations

import argparse
import configparser
import json
import os
import re
import subprocess
import sys
import time
import urllib.parse
import urllib.error
import urllib.request
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def run(cmd: list[str], *, timeout: int = 15, env: dict[str, str] | None = None) -> dict:
    started = time.time()
    try:
        proc = subprocess.run(
            cmd,
            cwd=ROOT,
            env={**os.environ, **(env or {})},
            text=True,
            capture_output=True,
            timeout=timeout,
            check=False,
        )
        return {
            "ok": proc.returncode == 0,
            "code": proc.returncode,
            "stdout": proc.stdout.strip(),
            "stderr": proc.stderr.strip(),
            "seconds": round(time.time() - started, 3),
        }
    except Exception as exc:  # pragma: no cover - used as diagnostic fallback
        return {"ok": False, "code": None, "stdout": "", "stderr": str(exc), "seconds": round(time.time() - started, 3)}


def http_probe(url: str, timeout: int = 10) -> dict:
    started = time.time()
    try:
        opener = urllib.request.build_opener(NoRedirectHandler)
        with opener.open(url, timeout=timeout) as response:
            body = response.read()
            return {"ok": True, "status": response.status, "seconds": round(time.time() - started, 3), "bytes": len(body)}
    except urllib.error.HTTPError as exc:
        return {
            "ok": 200 <= exc.code < 400,
            "status": exc.code,
            "location": exc.headers.get("Location"),
            "seconds": round(time.time() - started, 3),
            "bytes": 0,
        }
    except Exception as exc:
        return {"ok": False, "status": None, "error": str(exc), "seconds": round(time.time() - started, 3), "bytes": 0}


class NoRedirectHandler(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):  # noqa: D401
        return None


def read_config(path: Path) -> dict:
    parser = configparser.ConfigParser()
    parser.read(path)
    options = parser["options"] if parser.has_section("options") else {}
    return {key: str(options.get(key, "")).strip() for key in options}


def psql(config: dict, sql: str) -> dict:
    password = config.get("db_password", "")
    db_name = config.get("db_name", "GCGPC")
    cmd = ["docker", "exec", "-e", f"PGPASSWORD={password}", "gpc-postgres", "psql", "-U", config.get("db_user", "odoo"), "-d", db_name, "-Atc", sql]
    return run(cmd, timeout=20)


def int_from_result(result: dict, default: int = -1) -> int:
    try:
        return int(str(result.get("stdout", "")).splitlines()[-1])
    except Exception:
        return default


def git_dirty_counts() -> dict:
    status = run(["git", "status", "--porcelain=v1"], timeout=20)
    counts = {"i18n_po_paths": 0, "tools_paths": 0, "other_paths": 0, "total_paths": 0}
    for line in status.get("stdout", "").splitlines():
        if not line:
            continue
        path = line[3:] if len(line) > 3 else line
        counts["total_paths"] += 1
        if path.endswith("/i18n/zh_CN.po"):
            counts["i18n_po_paths"] += 1
        elif path.startswith("tools/") or path.startswith("config/"):
            counts["tools_paths"] += 1
        else:
            counts["other_paths"] += 1
    counts["ok"] = status["ok"]
    return counts


def listen_ports() -> dict:
    result = run(["lsof", "-nP", "-iTCP", "-sTCP:LISTEN"], timeout=10)
    listeners: dict[str, list[str]] = {}
    for line in result.get("stdout", "").splitlines()[1:]:
        parts = line.split()
        if len(parts) < 9:
            continue
        address = parts[-2] if parts[-1] == "(LISTEN)" else parts[-1]
        if ":" not in address:
            continue
        port = address.rsplit(":", 1)[-1]
        listeners.setdefault(port, []).append(" ".join(parts[:2] + [address]))
    return {"ok": result["ok"], "ports": listeners}


def score_item(points: int, ok: bool, label: str, evidence: dict | str, findings: list[dict]) -> int:
    if ok:
        return points
    findings.append({"label": label, "lost": points, "evidence": evidence})
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default=".runtime/gpc-odoo.conf")
    parser.add_argument("--base-url", default="http://127.0.0.1:8069")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    config_path = (ROOT / args.config).resolve()
    config = read_config(config_path)
    findings: list[dict] = []

    login = http_probe(args.base_url.rstrip("/") + "/web/login")
    apps = http_probe(args.base_url.rstrip("/") + "/odoo/apps")
    base = urllib.parse.urlparse(args.base_url)
    base_port = str(base.port or (443 if base.scheme == "https" else 80))
    ports = run(["docker", "ps", "--format", "{{.Names}}\t{{.Status}}\t{{.Ports}}"], timeout=10)
    port_line = next((line for line in ports["stdout"].splitlines() if line.startswith("gpc-postgres\t")), "")
    listeners = listen_ports()
    proc = run(["sh", "-c", "ps -axo pid,command | rg 'odoo-bin' | rg -v rg"], timeout=10)
    cmdline = proc["stdout"]

    db_ready = run(["docker", "exec", "gpc-postgres", "pg_isready", "-U", config.get("db_user", "odoo"), "-d", config.get("db_name", "GCGPC")], timeout=10)
    locks = int_from_result(psql(config, "select count(*) from pg_locks where not granted;"))
    long_queries = int_from_result(psql(config, "select count(*) from pg_stat_activity where datname=current_database() and state='active' and now()-query_start > interval '30 seconds';"))
    long_tx = int_from_result(psql(config, "select count(*) from pg_stat_activity where datname=current_database() and xact_start is not null and now()-xact_start > interval '5 minutes';"))
    pending_modules = int_from_result(psql(config, "select count(*) from ir_module_module where state in ('to install','to upgrade','to remove');"))
    cron_failures = int_from_result(psql(config, "select count(*) from ir_cron where coalesce(failure_count,0) > 0;"))

    pip_check = run([".venv311/bin/python", "-m", "pip", "check"], timeout=30)
    diff_check = run(["git", "diff", "--check"], timeout=30)
    msgfmt = run(["sh", "-c", "find addons odoo/addons -path '*/i18n/zh_CN.po' -print0 | xargs -0 -n 1 msgfmt --check -o /tmp/gpc_i18n_check.mo"], timeout=90)
    git_counts = git_dirty_counts()

    local = 0
    local += score_item(15, login.get("status") == 200, "login_http", login, findings)
    local += score_item(10, apps.get("status") in (200, 303), "apps_http", apps, findings)
    local += score_item(10, "127.0.0.1:54329->5432/tcp" in port_line, "postgres_local_bind", port_line, findings)
    local += score_item(10, db_ready["ok"], "postgres_ready", db_ready, findings)
    local += score_item(15, locks == 0 and long_queries == 0 and long_tx == 0, "database_runtime", {"locks": locks, "long_queries": long_queries, "long_transactions": long_tx}, findings)
    local += score_item(10, pending_modules == 0 and cron_failures == 0, "odoo_state", {"pending_modules": pending_modules, "cron_failures": cron_failures}, findings)
    local += score_item(10, "--dev" not in cmdline and "db_password" not in cmdline, "odoo_process_hardening", cmdline, findings)
    local += score_item(5, config.get("list_db", "").lower() == "false", "list_db_disabled", {"list_db": config.get("list_db")}, findings)
    local += score_item(5, pip_check["ok"], "python_dependencies", pip_check, findings)
    local += score_item(5, diff_check["ok"], "diff_whitespace", diff_check, findings)
    local += score_item(5, msgfmt["ok"], "zh_cn_po_syntax", {"ok": msgfmt["ok"], "stderr": msgfmt["stderr"][:500]}, findings)

    production_findings: list[dict] = []
    production = local
    production += score_item(0, config_path.exists() and config_path.stat().st_mode & 0o077 == 0, "private_config_permissions", oct(config_path.stat().st_mode & 0o777) if config_path.exists() else "missing", production_findings)
    if config.get("db_password") in {"", "odoo", "admin", "CHANGE_ME_STRONG_DATABASE_PASSWORD"}:
        production_findings.append({"label": "weak_db_password", "lost": 10, "evidence": "db_password is empty/default"})
        production -= 10
    if config.get("admin_passwd") in {"", "admin", "CHANGE_ME_STRONG_MASTER_PASSWORD"}:
        production_findings.append({"label": "weak_admin_passwd", "lost": 10, "evidence": "admin_passwd is empty/default"})
        production -= 10
    if git_counts["total_paths"] != 0:
        production_findings.append({"label": "dirty_worktree", "lost": 15, "evidence": git_counts})
        production -= 15
    if config.get("workers", "0") in {"0", ""}:
        production_findings.append({"label": "workers_not_enabled", "lost": 10, "evidence": {"workers": config.get("workers")}})
        production -= 10
    workers_enabled = config.get("workers", "0") not in {"0", ""}
    if workers_enabled and not config.get("gevent_port"):
        production_findings.append({"label": "gevent_port_not_configured", "lost": 5, "evidence": {"gevent_port": config.get("gevent_port")}})
        production -= 5
    if workers_enabled and config.get("http_port") == base_port:
        production_findings.append(
            {
                "label": "worker_http_port_exposed_directly",
                "lost": 5,
                "evidence": {"base_url_port": base_port, "http_port": config.get("http_port"), "expected": "reverse proxy in front of worker HTTP port"},
            }
        )
        production -= 5

    result = {
        "local_health_score": max(0, min(100, local)),
        "production_readiness_score": max(0, min(100, production)),
        "findings": findings,
        "production_findings": production_findings,
        "evidence": {
            "login": login,
            "apps": apps,
            "postgres_port": port_line,
            "listeners": listeners,
            "db": {"locks": locks, "long_queries": long_queries, "long_transactions": long_tx, "pending_modules": pending_modules, "cron_failures": cron_failures},
            "git": git_counts,
            "config": {
                "path": str(config_path),
                "list_db": config.get("list_db"),
                "workers": config.get("workers"),
                "gevent_port": config.get("gevent_port"),
                "http_interface": config.get("http_interface"),
                "http_port": config.get("http_port"),
                "db_host": config.get("db_host"),
                "db_port": config.get("db_port"),
            },
        },
    }
    print(json.dumps(result, ensure_ascii=False, indent=2) if args.json else result)
    return 0 if result["local_health_score"] == 100 and result["production_readiness_score"] == 100 else 1


if __name__ == "__main__":
    sys.exit(main())
