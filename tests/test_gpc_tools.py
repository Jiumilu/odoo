from __future__ import annotations

import json
import unittest
from unittest import mock

from tools import gpc_apply_runtime_localization, gpc_authenticated_backend_smoke, gpc_core_flow_smoke, gpc_reverse_proxy


class ReverseProxyLocalizationTests(unittest.TestCase):
    def test_non_error_json_passes_through(self) -> None:
        body = json.dumps({"lang": "zh_CN", "modules": {"web": {}}}).encode()

        self.assertEqual(gpc_reverse_proxy.localize_json_error(body), body)

    def test_known_json_error_is_localized(self) -> None:
        payload = {
            "jsonrpc": "2.0",
            "error": {
                "message": "Odoo Server Error",
                "data": {"name": "odoo.http.SessionExpiredException", "message": "Session expired", "arguments": []},
            },
        }

        localized = json.loads(gpc_reverse_proxy.localize_json_error(json.dumps(payload).encode()).decode())

        self.assertEqual(localized["error"]["message"], "GlobalCloud GPC 错误提示")
        self.assertIn("会话已过期", localized["error"]["data"]["message"])
        self.assertEqual(localized["error"]["data"]["debug"], "")

    def test_html_and_headers_are_localized(self) -> None:
        raw = (
            b"HTTP/1.0 404 NOT FOUND\r\n"
            b"Content-Type: text/html; charset=utf-8\r\n"
            b"Content-Length: 43\r\n"
            b"\r\n"
            b"<title>Page Not Found</title>Powered by Odoo"
        )

        transformed = gpc_reverse_proxy.transform_response(raw).decode()

        self.assertIn("页面未找到", transformed)
        self.assertIn("由 GlobalCloud GPC 提供支持", transformed)
        self.assertNotIn("Content-Length: 43", transformed)


class RuntimeLocalizationTests(unittest.TestCase):
    def test_runtime_replacements_cover_brand_and_contacts(self) -> None:
        source = "OdooBot from YourCompany at info@yourcompany.example.com +1 555-555-5556"

        updated, changed = gpc_apply_runtime_localization.replace_text(source)

        self.assertTrue(changed)
        self.assertEqual(updated, "GlobalCloud GPC 助手 from GlobalCloud GPC at service@gc-gpc.example.com 18607163009")


class CoreFlowSmokeTests(unittest.TestCase):
    def test_http_probe_success_and_http_error(self) -> None:
        class Response:
            status = 200

            def __enter__(self):
                return self

            def __exit__(self, *args):
                return None

            def read(self):
                return b"ok"

        with mock.patch("urllib.request.urlopen", return_value=Response()):
            success = gpc_core_flow_smoke.http_probe("http://example.invalid")

        self.assertTrue(success["ok"])
        self.assertEqual(success["status"], 200)
        self.assertEqual(success["bytes"], 2)

        with mock.patch("urllib.request.urlopen", side_effect=gpc_core_flow_smoke.urllib.error.HTTPError("u", 404, "missing", {}, None)):
            failure = gpc_core_flow_smoke.http_probe("http://example.invalid")

        self.assertFalse(failure["ok"])
        self.assertEqual(failure["status"], 404)
        self.assertEqual(failure["bytes"], 0)

    def test_markdown_report_contains_flow_evidence(self) -> None:
        report = gpc_core_flow_smoke.markdown_report(
            {
                "timestamp": "2026-06-06T00:00:00+0800",
                "config": ".runtime/gpc-odoo.conf",
                "database": "GCGPC",
                "base_url": "http://127.0.0.1:8069",
                "ok": True,
                "http": {"login": {"ok": True, "status": 200, "bytes": 10}},
                "flows": {"contact_crud": {"ok": True, "model": "res.partner"}},
            }
        )

        self.assertIn("总体结果：`通过`", report)
        self.assertIn("contact_crud", report)
        self.assertIn("所有 ORM 写入", report)


class AuthenticatedBackendSmokeTests(unittest.TestCase):
    def test_extract_csrf_token(self) -> None:
        token = gpc_authenticated_backend_smoke.extract_csrf_token('<input name="csrf_token" value="abc&amp;123">')

        self.assertEqual(token, "abc&123")

    def test_authenticated_backend_markdown_report(self) -> None:
        report = gpc_authenticated_backend_smoke.markdown_report(
            {
                "timestamp": "2026-06-06T00:00:00+0800",
                "base_url": "http://127.0.0.1:8069",
                "test_user": {"login": "gpc.e2e@example.invalid"},
                "ok": True,
                "backend": {
                    "entries": {
                        "apps": {
                            "ok": True,
                            "status": 200,
                            "final_url": "http://127.0.0.1:8069/odoo/apps",
                            "visible_has_legacy_brand": False,
                        }
                    }
                },
            }
        )

        self.assertIn("总体结果：`通过`", report)
        self.assertIn("gpc.e2e@example.invalid", report)
        self.assertIn("apps", report)


if __name__ == "__main__":
    unittest.main()
