# Pobi CLI

[![Discord](https://img.shields.io/badge/Discord-Pobi%20CLI-5865F2?logo=discord&logoColor=white)](https://discord.gg/zwUVa3E7KT)
[![Version](https://img.shields.io/badge/version-v0.1-blue.svg)](VERSION)

**基于反馈迭代的自主渗透测试 Agent**

在完整的 XBOW 验证基准上，使用 **Kimi K2.5** 取得约 **80%** 通过率，全量跑一次端到端约 **US$122**；架构与模型解耦，支持任意可部署 LLM。


> [!WARNING]
> **持续开发中**：核心功能可用，接口和交互仍在打磨。欢迎在 [issues](https://github.com/Sexisnull/pobi/issues) 反馈。

📄 [技术深入解读](https://xoxruns.medium.com/feedback-driven-iteration-and-fully-local-webapp-pentesting-ai-agent-achieving-78-on-xbow-199ef719bf01)

---

## 项目说明

Pobi CLI 是一个自主的 Web 应用渗透测试 Agent，采用反馈驱动迭代来适配利用策略。当标准工具失效时，它会自动生成 Python payload，观察响应，反复精调直到突破。

**核心特性：**
- **本地运行**：无云依赖，数据不外泄
- **模型无关**：兼容任意可部署的 LLM（通过 LiteLLM）
- **自研沙箱工具**：Playwright、Docker、WebAssembly
- **ADaPT 架构**：Supervisor + Subagent 层级
- **置信度决策**：<20% 放弃 / 20–60% 扩展 / 60–80% 精调 / >80% 验证

**架构一句话**：两阶段执行（侦察 → 利用），Supervisor 维护高层目标并派发给 Subagent（HTTP / Shell / Python 各司其职），Policy 根据置信度分数决定继续走哪条分支。当标准工具失败时，Agent 生成自定义脚本并根据观测反馈迭代——例如盲注 SQL 这类静态工具链得 0% 的场景。

**基准成绩**：XBOW 104 题验证集（黑盒模式，2026 年 1 月）
- XSS 91% · Business Logic 86% · SQLi 83% · IDOR 80%
- GraphQL / SSRF / NoSQL 注入 / HTTP 方法篡改 均 100%

---

## 快速开始

### 前置依赖
- [uv](https://docs.astral.sh/uv/)（推荐；`install.sh` 缺失时自动安装）
- Docker（沙箱扫描必需；`install.sh` 会检查并引导安装，并预拉取沙箱镜像）
- curl

### 安装

**方式 A — 仅用 uv（最简）**

```bash
git clone https://github.com/Sexisnull/pobi.git
cd pobi
uv sync                 # 安装 pobi 及 Web 依赖到 ./.venv
pobi-web-console        # 打开 http://localhost:8000
```

**方式 B — `./install.sh`（自动配置环境）**

安装脚本会创建隔离虚拟环境、把命令链接到 `~/.local/bin`，并帮你检查/配置运行时组件（Docker + 沙箱镜像、Playwright Chromium）：

```bash
./install.sh                  # 完整安装到 ~/.cache/pobi/venv
./install.sh --launch         # 装完立刻启动 Web Console
./install.sh --no-browser     # 跳过较大的 Playwright Chromium 下载
./install.sh --skip-docker    # 跳过 Docker 检查与镜像预拉取
```

若 `pobi` 命令找不到，把 `~/.local/bin` 加进 PATH：
```bash
export PATH="$HOME/.local/bin:$PATH"
```

### 运行

**Web Console（统一入口，推荐）**
```bash
pobi-web-console   # 打开 http://localhost:8000
```

**CLI 模式（可选）**
```bash
pobi --target "http://localhost:3000" --prompt "find SQL injection vulnerabilities"
```

### 使用前的配置
启动 Web Console 后，在 Settings 中配置：
- 至少一个**语义模型**（provider + API key + base_url，走你的供应商网关）；
- 一个**向量 / embedding 模型**（RAG 检索必需，维度需与索引一致）。

配置保存在 `~/.pobi/config.json`。沙箱镜像 `xoxruns/sandboxed_kali` 会在首次扫描时自动拉取（或由 `install.sh` 预拉取）。

### 命令

```
pobi
  --target, -t     目标 URL
  --prompt, -p     初始测试提示
  --mode,   -m     hacker（需批准）| yolo（全自主）
```

---

## Web Console

`pobi.web_console` 提供浏览器控制台：SSE 实时事件流、发起扫描、查看 findings、审计日志、敏感工具调用人工审批。守护进程不可达时自动降级为模拟模式，可离线体验 UI。

---

## 当前状态与路线图

### v0.1（当前稳定版）
- ✅ ADaPT 核心架构（Supervisor–Subagent）
- ✅ XBOW 基准评估（Kimi K2.5 ~80%）
- ✅ 自研沙箱工具（Playwright / Docker / WASM）
- ✅ LiteLLM 多模型支持
- ✅ 两阶段执行（侦察 + 利用）
- ✅ React/Ink CLI 界面 + Supervisor / YOLO 双模式
- ✅ Web Console 合入主包
- ✅ **授权范围闸门**：越界请求硬性中止 + 审计留证
- ✅ **Plan mode（`/plan`）**：执行前审阅/裁剪计划树

### 进行中（面向 v0.2）
- 🚧 代码库分析支持（白盒测试）
- 🚧 预设工作流（API 测试、Web 应用、认证绕过）
- 🚧 攻击链保存与重放
- 🚧 上下文压缩（减少冗余工具调用）
- 🚧 Secrets 管理改进
- 🚧 报告模板 `/report`

### 未来规划

按 **阻塞价值优先** 排序——先解决"没它就不能自称自主"的问题，再扩表面积。

**v0.2 — 硬化现有功能**（目标 Q3 2026）
- 上下文压缩：同分通过率下 token 降低 ≥30%
- Report v2：技术报告 + 高管摘要 + 机器可读（SARIF / JSON），每条发现附复现步骤与 CVSS
- 核心循环单测：ADaPT 分支、ValidationGate、scope gate 拒绝路径

**v0.3 — 从 Web 扩展到真正的渗透**（目标 Q4 2026）
- 侦察工具带（Docker 封装）：nmap / httpx / nuclei / ffuf / subfinder / whatweb 等，统一输出 schema
- 漏洞情报 RAG：nuclei-templates + exploit-db + CVE，指纹 → 模板/exploit 检索
- 持久 shell 会话：pty + session_id，支持后渗透
- WAF / 限流自适应 + payload 变异器
- 每 session 凭据/密钥仓库

**v0.4 — 后渗透与多目标**（目标 Q1 2027）
- 后渗透 Agent：本地枚举（LinPEAS/WinPEAS 清单）、凭据收集、内核 → exploit 检索
- Pivot：SSH/SOCKS 管理器，可达性图作为一等状态
- 多目标编排：目标图，A 拿到的凭据自动进入 B 的上下文
- 跨会话知识库：`assets` / `findings` / `credentials` / `attack_paths`

**v0.5 — 开源模型与对抗鲁棒性**（目标 Q2 2027）
- Qwen / Llama 蒸馏微调，目标 ≥75% XBOW，公开数据集与评估工具
- 对抗训练循环（WAF / 限流 / 蜜罐），规避与安全同时评分
- 白盒混合测试：tree-sitter + taint 分析喂给 planner

**v0.6 — 生产化**（目标 H2 2027）
- 会话时间线 UI、单步回放
- 多用户后端：AuthN/AuthZ、任务队列、产物存储
- 合规映射：OWASP ASVS / PCI-DSS / MITRE ATT&CK 覆盖矩阵
- 成本管控：run 级 / agent 级 token 与美元预算硬停

### 明确不做

- 物理 / 社工 / 钓鱼
- DoS / 压测 / 群发（scope gate 就是为了防这个）
- 恶意用户的检测规避
- v0.6 之前不做托管 SaaS——本地优先是特性，不是过渡阶段

**北极星**：把 Pobi 指向一个在授权范围内的资产，走开，回来看一份人类渗透测试师愿意签字的报告。

---

## 贡献

欢迎贡献：上下文优化算法、漏洞测试用例、开源权重微调、对抗测试场景。详见 [CONTRIBUTING.md](CONTRIBUTING.md)。

## 免责声明

**仅限授权安全测试。** 未授权测试违法。使用者自行负责合规与授权。

## 联系

- 📧 [yassine@straylabs.ai](mailto:yassine@straylabs.ai)
- 💬 Discord：xoxruns · [社区服](https://discord.gg/zwUVa3E7KT)
- 🐦 [@xoxruns](https://x.com/xoxruns)
