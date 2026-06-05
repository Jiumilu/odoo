# GlobalCloud GPC 浏览器表单级 E2E 报告

执行时间戳：`2026-06-05T23:03:04.469Z`
基础地址：`http://127.0.0.1:8069`
测试联系人：`GPC Browser Form E2E 20260605230242`
总体结果：`通过`

| 步骤 | 结果 | 证据 |
|---|---|---|
| login | 通过 | `{"name":"login","ok":true,"url":"http://127.0.0.1:8069/odoo/discuss","title":"讨论"}` |
| open_contacts | 通过 | `{"name":"open_contacts","ok":true,"url":"http://127.0.0.1:8069/odoo/contacts","title":"联系人"}` |
| fill_contact_form | 通过 | `{"name":"fill_contact_form","ok":true,"contactName":"GPC Browser Form E2E 20260605230242","email":"browser-form-e2e@gc-gpc.example.com","phone":"13900000002"}` |
| save_contact | 通过 | `{"name":"save_contact","ok":true,"url":"http://127.0.0.1:8069/odoo/contacts/102","title":"GPC Browser Form E2E 20260605230242","recordId":102,"hasContactName":true,"savedRecord":{"id":102,"name":"GPC Browser Form E2E 20260605230242","email":"browser-form-e2e@gc-gpc.example.com","phone":"13900000002"}}` |
| search_contact | 通过 | `{"name":"search_contact","ok":true,"url":"http://127.0.0.1:8069/odoo/contacts","title":"联系人","hasContactName":true,"visibleHasLegacyBrand":false}` |
