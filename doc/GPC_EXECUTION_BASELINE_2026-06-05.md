# GlobalCloud GPC 执行基线

基线版本：GPC-BL-2026-06-05-01
结论日期：2026-06-05
项目路径：/Users/lujunxiang/Projects/GlobalCloud GPC
当前分支：19.0
当前状态：需专项修复

## 1. 横向评分总表

| 项目 | 当前总分 | 健康度 | 功能完整性 | 软件测试 | 中文化 | 治理成熟度 | 当前状态 | P0 数量 | P1 数量 | 最大风险 | 建议动作 |
|---|---:|---:|---:|---:|---:|---:|---|---:|---:|---|---|
| GlobalCloud GPC | 65 | 81 | 58 | 62 | 76 | 48 | 需专项修复 | 3 | 5 | 核心业务流程未闭环，测试证明力不足，交付治理缺失 | 第一轮只修 P0/P1，不新增业务功能 |

## 2. 评分校准

| 维度 | 分数 | 证据来源 | 校准结论 |
|---|---:|---|---|
| 健康度 | 81 | git 状态、端口监听、健康脚本、HTTP/websocket 探针、依赖检查 | 证据充分。本地运行态已健康，但生产交付链路仍不完整 |
| 功能完整性 | 58 | 数据库模块状态、页面验证、API 探针、功能矩阵 | 证据充分。没有把源码存在误判为业务完成 |
| 软件测试 | 62 | 测试资产盘点、Odoo 最小测试运行、CI/coverage 缺失检查 | 证据充分。没有把测试文件数量误判为测试充分 |
| 中文化 | 76 | zh_CN PO 统计、msgfmt、页面抽查、错误提示探针、README 检查 | 证据充分。覆盖高，但错误提示/文档/模板残留明显 |
| 治理成熟度 | 48 | release.py、README、.github、交付物和风险文档检查 | 证据充分。治理文档和上线管理条件不足 |

## 3. 最终处置决策

项目分类：C 类，专项修复后再开发。

硬结论：GlobalCloud GPC 当前不建议上线，也不建议继续堆新增业务功能；原因是核心业务流程未闭环、测试证明力不足、交付治理缺失。下一阶段只允许关闭 P0/P1 风险，完成第一轮复评后再决定是否恢复功能开发。

## 4. 阶段门槛

### 继续开发门槛

- 能安装、能启动、能通过健康检查。
- 无 P0。
- 核心功能矩阵明确，区分已安装、未安装、不可安装、不可验证。
- 最小测试命令可运行。

当前判断：部分满足，P0 未清零。

### 交付准备门槛

- 核心流程闭环。
- P0/P1 清零。
- CI 可自动运行健康检查和最小测试。
- 中文用户主路径可用。
- README、部署、运维、回滚、风险台账完整。

当前判断：不满足。

### 上线门槛

- build/test/lint 或等价质量门禁通过。
- 核心 E2E 或 smoke test 通过。
- 权限、数据、异常场景验证通过。
- 回滚方案、备份恢复、监控告警明确。
- 版本和风险记录完整。

当前判断：不满足。

## 5. 第一轮修复冲刺目标

周期：1-2 周

目标：

- P0 清零。
- P1 至少关闭 3 项。
- 建立 CI 最小质量门禁。
- 完成 3 条核心业务流程 smoke test 定义和至少 1 条实际闭环验证。
- 形成中文 README、部署说明、运维说明、风险台账初版。
- 复评五项中变化项，并更新本基线。

## 6. 复评机制

每轮修复后必须回跑以下检查：

```text
git status --short --branch
.venv311/bin/python -m pip check
.venv311/bin/python -m py_compile tools/gpc_health_check.py tools/gpc_reverse_proxy.py tools/complete_zh_cn_i18n.py
git diff --check
find addons odoo/addons -path '*/i18n/zh_CN.po' -print0 | xargs -0 -n 1 msgfmt --check -o /tmp/gpc_i18n_check.mo
.venv311/bin/python odoo-bin -c .runtime/gpc-odoo.conf -d GCGPC --test-enable --test-tags ':TestSelector.test_selector_parser' --stop-after-init --workers=0 --max-cron-threads=0 --http-port=18091 --log-level=test
tools/gpc_health_check.py --json
```

复评输出必须包含：

- 修复前分数。
- 修复后分数。
- 已关闭风险。
- 新发现风险。
- 状态变化。
- 下一步动作。

