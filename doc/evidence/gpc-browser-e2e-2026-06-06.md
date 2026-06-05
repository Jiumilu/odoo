# GlobalCloud GPC 浏览器 E2E 证据

日期：2026-06-06

验证工具：Codex in-app browser

## 1. 验证结果

| 页面 | URL | 标题 | 语言 | 品牌 | 旧品牌残留 | 电话 |
|---|---|---|---|---|---|---|
| 首页 | `http://127.0.0.1:8069/?fresh=20260606` | `Home | 绿色供应链公共服务平台` | `zh-CN` | `GlobalCloud GPC` / `绿色供应链公共服务平台` | 无 | `18607163009` |
| 登录页 | `http://127.0.0.1:8069/web/login?fresh=20260606` | `Login | 绿色供应链公共服务平台` | `zh-CN` | `GlobalCloud GPC` / `绿色供应链公共服务平台` | 无 | `18607163009` |
| 404 页 | `http://127.0.0.1:8069/non-existent-gpc-page?fresh=20260606` | `页面未找到 | 绿色供应链公共服务平台` | `zh-CN` | `GlobalCloud GPC` / `绿色供应链公共服务平台` | 无 | `18607163009` |

## 2. 浏览器读取证据

```json
[
  {
    "url": "http://127.0.0.1:8069/?fresh=20260606",
    "title": "Home | 绿色供应链公共服务平台",
    "lang": "zh-CN",
    "generator": "GlobalCloud GPC",
    "visibleHasLegacyBrand": false,
    "visibleHasChineseBrand": true,
    "visibleHasPhone": true
  },
  {
    "url": "http://127.0.0.1:8069/web/login?fresh=20260606",
    "title": "Login | 绿色供应链公共服务平台",
    "lang": "zh-CN",
    "generator": "GlobalCloud GPC",
    "visibleHasLegacyBrand": false,
    "visibleHasChineseBrand": true,
    "visibleHasPhone": true
  },
  {
    "url": "http://127.0.0.1:8069/non-existent-gpc-page?fresh=20260606",
    "title": "页面未找到 | 绿色供应链公共服务平台",
    "lang": "zh-CN",
    "generator": "GlobalCloud GPC",
    "visibleHasLegacyBrand": false,
    "visibleHasChineseBrand": true,
    "visibleHasPhone": true
  }
]
```

## 3. 结论

公开页面、登录页和错误页已经具备浏览器级中文化证据。登录后后台 E2E 仍需要可控测试账号或正式凭证才能覆盖。
