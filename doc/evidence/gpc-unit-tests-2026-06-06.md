# GlobalCloud GPC 本地工具单元测试证据

日期：2026-06-06

## 执行命令

```bash
.venv311/bin/python -m unittest discover -s tests -p 'test_*.py' -v
```

## 执行结果

```text
test_http_probe_success_and_http_error (test_gpc_tools.CoreFlowSmokeTests.test_http_probe_success_and_http_error) ... ok
test_markdown_report_contains_flow_evidence (test_gpc_tools.CoreFlowSmokeTests.test_markdown_report_contains_flow_evidence) ... ok
test_html_and_headers_are_localized (test_gpc_tools.ReverseProxyLocalizationTests.test_html_and_headers_are_localized) ... ok
test_known_json_error_is_localized (test_gpc_tools.ReverseProxyLocalizationTests.test_known_json_error_is_localized) ... ok
test_non_error_json_passes_through (test_gpc_tools.ReverseProxyLocalizationTests.test_non_error_json_passes_through) ... ok
test_runtime_replacements_cover_brand_and_contacts (test_gpc_tools.RuntimeLocalizationTests.test_runtime_replacements_cover_brand_and_contacts) ... ok
test_authenticated_backend_markdown_report (test_gpc_tools.AuthenticatedBackendSmokeTests.test_authenticated_backend_markdown_report) ... ok
test_extract_csrf_token (test_gpc_tools.AuthenticatedBackendSmokeTests.test_extract_csrf_token) ... ok

Ran 8 tests in 0.005s

OK
```

## 覆盖内容

| 测试对象 | 覆盖点 | 证明力 |
|---|---|---|
| `tools/gpc_reverse_proxy.py` | 普通 JSON 透传、JSON 错误中文化、HTML 品牌/错误页替换、响应头修正 | 防止代理再次吞掉 `/website/translations` 等正常 JSON |
| `tools/gpc_apply_runtime_localization.py` | 旧品牌、测试邮箱、电话替换规则 | 防止具体邮箱被通用域名规则提前覆盖 |
| `tools/gpc_core_flow_smoke.py` | HTTP 成功/错误探针、Markdown 报告生成 | 防止 smoke 证据生成格式回退 |
| `tools/gpc_authenticated_backend_smoke.py` | CSRF token 提取、登录态后台报告生成 | 防止认证后台 smoke 登录流程和报告格式回退 |

## 结论

本轮新增测试能证明本地质量工具的关键转换逻辑稳定，但它不等同于完整业务 E2E 测试。业务闭环仍以 `doc/evidence/gpc-core-flow-smoke.md` 和浏览器登录态入口证据为准。
