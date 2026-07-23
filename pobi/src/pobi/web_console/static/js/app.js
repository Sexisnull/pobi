"use strict";

/* ------------------------------------------------------------------ *
 * Pobi Web Console — frontend controller
 * ------------------------------------------------------------------ */

/* ---------------- i18n ---------------- */
const I18N = {
  en: {},
  zh: {
    "Dashboard": "仪表盘",
    "New Scan": "新建扫描",
    "Monitor": "监控",
    "Results": "结果",
    "Settings": "设置",
    "Audit": "审计",
    "connecting…": "连接中…",
    "operator:": "操作者：",
    "Pobi // Web Console": "Pobi // 网页控制台",
    "SIMULATION": "模拟模式",
    "DAEMON": "守护模式",
    "OFFLINE": "离线",
    "live": "在线",
    "daemon linked": "已连接守护进程",
    "no daemon": "未连接守护进程",
    "Autonomous penetration testing control plane. Target:": "自主渗透测试控制台。目标：",
    "Component health": "组件健康",
    "Recent activity": "近期活动",
    "Mode": "模式",
    "Components": "组件",
    "Live clients": "在线客户端",
    "Approval mode": "审批模式",
    "ON": "开",
    "OFF": "关",
    "Quick action": "快速操作",
    "+ Launch scan": "＋ 发起扫描",
    "No component data": "无组件数据",
    "No activity yet": "暂无活动",
    "Configure an autonomous engagement. The agent plans, exploits and self-validates.": "配置一次自主渗透任务。智能体将自主规划、利用并自我验证。",
    "1 · Preset workflow": "1 · 预设工作流",
    "2 · Target & scope": "2 · 目标与范围",
    "Target URL": "目标地址",
    "Scope notes (optional)": "范围说明（可选）",
    "e.g. only /api/* and the login flow; do not touch /admin except read-only": "例如：仅 /api/* 与登录流程；除只读外不要触碰 /admin",
    "3 · Agent & model": "3 · 智能体与模型",
    "Agent strategy": "智能体策略",
    "LLM model": "大模型",
    "4 · Guardrails": "4 · 护栏",
    "Max depth:": "最大深度：",
    "Min confidence:": "最小置信度：",
    "Require operator approval before intrusive actions": "在执行侵入性操作前需操作者审批",
    "Launch scan ▶": "发起扫描 ▶",
    "Launching…": "启动中…",
    "Launch failed: ": "启动失败：",
    "Run a full autonomous penetration test.": "执行一次完整的自主渗透测试。",
    "session": "会话",
    "running": "运行中",
    "■ Interrupt": "■ 中断",
    "Agent confidence": "智能体置信度",
    "Live event feed": "实时事件流",
    "Task tree": "任务树",
    "Session state": "会话状态",
    "loading…": "加载中…",
    "APPROVAL REQUIRED": "需要审批",
    "✓ Approve": "✓ 批准",
    "✕ Deny": "✕ 拒绝",
    "Interrupt this scan?": "确定要中断本次扫描吗？",
    "◉ Live monitor": "◉ 实时监控",
    "Findings": "发现",
    "Execution log": "执行日志",
    "No validated findings yet. Run a scan or wait for self-validation.": "暂无经过验证的发现。请运行扫描或等待自我验证。",
    "Severity": "严重度",
    "Title": "标题",
    "Endpoint": "端点",
    "Conf.": "置信度",
    "no execution events captured": "未捕获任何执行事件",
    "Component health and agent guardrails.": "组件健康与智能体护栏。",
    "↻ Re-init components": "↻ 重新初始化组件",
    "Validation config": "验证配置",
    "Max retries:": "最大重试次数：",
    "Require validation token": "需要验证令牌",
    "Strict mode": "严格模式",
    "Save validation": "保存验证配置",
    "LLM provider": "大模型提供方",
    "Provider": "提供方",
    "Model name": "模型名称",
    "Save LLM": "保存大模型",
    "When enabled, intrusive agent actions require operator sign-off via the Monitor.": "启用后，智能体的侵入性操作需操作者在监控页确认。",
    "Require approval for intrusive actions": "对侵入性操作要求审批",
    "Save": "保存",
    "no data": "无数据",
    "Validation config saved": "验证配置已保存",
    "LLM provider saved": "大模型已保存",
    "Approval mode saved": "审批模式已保存",
    "Components re-initializing": "组件正在重新初始化",
    "Authorization trail of every privileged action taken through the console.": "通过控制台执行的每个特权操作的授权记录。",
    "Time": "时间",
    "Operator": "操作者",
    "Action": "操作",
    "Target": "目标",
    "Decision": "决策",
    "Detail": "详情",
    "No audit entries": "暂无审计记录",
    "Unknown view": "未知视图",
    "History": "历史任务",
    "Vulnerabilities": "漏洞",
    "Token Usage": "Token 使用量",
    "Reports": "报告",
    "Severity summary": "严重度汇总",
    "Critical": "严重",
    "High": "高危",
    "Medium": "中危",
    "Low": "低危",
    "Info": "信息",
    "No sessions yet. Launch a scan to populate history.": "暂无任务，发起一次扫描后将出现在此处。",
    "Session": "会话",
    "Target": "目标",
    "Status": "状态",
    "Findings": "发现",
    "Duration": "耗时(秒)",
    "Created": "创建时间",
    "Tokens": "Token 数",
    "Cost": "花费",
    "View": "查看",
    "Report": "报告",
    "Monitor": "监控",
    "Total prompt tokens": "提示词总 Token",
    "Total completion tokens": "生成总 Token",
    "Total tokens": "总 Token",
    "Estimated cost (USD)": "预计花费(美元)",
    "Usage by phase": "各阶段用量",
    "Per-session usage": "各会话用量",
    "All findings across sessions": "跨会话的全部发现",
    "Select a session": "选择一个会话",
    "Pick a completed session to view its report": "选择一个已完成会话以查看报告",
    "Download Markdown": "下载 Markdown",
    "Download JSON": "下载 JSON",
    "Report for": "报告：",
    "No report available for this session": "该会话暂无报告",
    "Confidence": "置信度",
    "All past and running scan sessions.": "所有历史与进行中的扫描会话。",
    "Cost incurred by LLM calls across autonomous scans.": "自主扫描中由大模型调用产生的花费。",
    "View a security assessment report and download it.": "查看安全评估报告并下载。",
    "All findings aggregated across sessions.": "跨会话汇总的所有发现。"
  },
};
let lang = (function () {
  try { return localStorage.getItem("pobi.lang") || "en"; } catch (e) { return "en"; }
})();
function t(s) { return (I18N[lang] && I18N[lang][s]) || s; }
function setLang(l) {
  lang = l;
  try { localStorage.setItem("pobi.lang", l); } catch (e) {}
  document.documentElement.lang = (l === "zh" ? "zh-CN" : "en");
  document.querySelectorAll(".lang-btn").forEach((b) => b.classList.toggle("active", b.dataset.lang === l));
  localizeStatic();
  renderTopbar();
  router();
}
function localizeStatic() {
  document.querySelectorAll("[data-i18n]").forEach((el) => { el.textContent = t(el.dataset.i18n); });
}

const state = {
  mode: "connecting",
  connected: false,
  subscribers: 0,
  approvalMode: false,
  currentSession: null,
  currentAgent: null,
  confidence: 0,
  events: [],
  sessionEvents: {},      // session_id -> [events]
  approvals: {},          // request_id -> event
  feedEl: null,
};

const TARGET_DEFAULT = "http://127.0.0.1:8005";

/* ---------------- API helpers ---------------- */
async function api(method, path, body) {
  const opts = { method, headers: { "Content-Type": "application/json" } };
  if (body !== undefined) opts.body = JSON.stringify(body);
  const res = await fetch(path, opts);
  if (!res.ok) {
    let detail = res.statusText;
    try { detail = (await res.json()).detail || detail; } catch (_) {}
    throw new Error(detail);
  }
  return res.status === 204 ? null : res.json();
}

function fmtTime(ts) {
  const d = ts != null ? new Date(ts * 1000) : new Date();
  return d.toLocaleTimeString([], { hour12: false });
}

/* ---------------- Event stream ---------------- */
function connectEvents() {
  const es = new EventSource("/api/events");
  es.addEventListener("ready", (e) => {
    const d = JSON.parse(e.data);
    state.mode = d.mode;
    state.connected = d.connected;
    state.subscribers = d.subscribers || 0;
    renderTopbar();
  });
  es.onmessage = (e) => {
    let ev;
    try { ev = JSON.parse(e.data); } catch (_) { return; }
    if (ev.type === undefined && ev.mode !== undefined) return;
    pushEvent(ev);
    if (state.route === "live") paintLiveEvent(ev);
  };
  es.onerror = () => { /* auto-reconnect by browser */ };
}

function pushEvent(ev) {
  if (!ev || !ev.type) return;
  updateLiveState(ev);
  state.events.unshift(ev);
  if (state.events.length > 600) state.events.pop();
  if (ev.session_id) {
    const arr = state.sessionEvents[ev.session_id] || (state.sessionEvents[ev.session_id] = []);
    arr.unshift(ev);
    if (arr.length > 1000) arr.pop();
  }
  // confidence
  if (ev.type === "confidence_update" && ev.data && ev.data.new_confidence != null) {
    state.confidence = ev.data.new_confidence;
    updateConfidenceBar();
  }
  // approvals
  if (ev.type === "approval_required" && ev.data && ev.data.request_id) {
    state.approvals[ev.data.request_id] = ev;
    if (currentRoute() === "monitor") renderApprovals();
  }
  if (ev.type === "approval_granted" || ev.type === "approval_denied") {
    if (ev.data && ev.data.request_id) delete state.approvals[ev.data.request_id];
    if (currentRoute() === "monitor") renderApprovals();
  }
  // live feed
  if (state.feedEl && (!state.currentSession || ev.session_id === state.currentSession)) {
    appendFeedLine(state.feedEl, ev);
  }
}

/* ---------------- Topbar / connection ---------------- */
function renderTopbar() {
  const modeEl = document.getElementById("modeBadge");
  modeEl.textContent = t(state.mode === "simulation" ? "SIMULATION" : (state.mode === "daemon" ? "DAEMON" : "OFFLINE"));
  modeEl.style.color = state.mode === "simulation" ? "var(--warn)" : (state.mode === "daemon" ? "var(--good)" : "var(--bad)");
  document.getElementById("subsBadge").textContent = state.subscribers + " " + t("live");
  const conn = document.getElementById("connDot");
  conn.className = "conn " + (state.connected ? "ok" : "err");
  conn.querySelector("#connText").textContent = state.connected ? t("daemon linked") : t("no daemon");
}

/* ---------------- Router ---------------- */
function parseHash() {
  const raw = location.hash.replace(/^#/, "") || "dashboard";
  const [route, q] = raw.split("?");
  const params = {};
  if (q) q.split("&").forEach((kv) => { const [k, v] = kv.split("="); params[k] = decodeURIComponent(v || ""); });
  return { route, params };
}
function currentRoute() { return parseHash().route; }

const TITLES = { dashboard: "Dashboard", scan: "New Scan", monitor: "Monitor", results: "Results", history: "History", vulns: "Vulnerabilities", tokens: "Token Usage", reports: "Reports", settings: "Settings", audit: "Audit" };

async function router() {
  const { route, params } = parseHash();
  document.querySelectorAll(".nav-item").forEach((n) => n.classList.toggle("active", n.dataset.route === route));
  document.getElementById("crumb").textContent = t(TITLES[route]) || route;
  state.feedEl = null;
  const view = document.getElementById("view");
  if (route === "scan" && params.session) { /* came back after launch */ }
  state.currentSession = params.session || null;
  state.currentAgent = params.agent || null;
  if (!(state.sessionEvents[params.session])) state.sessionEvents[params.session] = state.sessionEvents[params.session] || [];

  view.innerHTML = "";
  if (route === "dashboard") return renderDashboard(view);
  if (route === "scan") return renderScan(view, params);
  if (route === "monitor") return renderMonitor(view, params);
  if (route === "live") return renderLive(view, params);
  if (route === "agents") return renderAgents(view, params);
  if (route === "validation") return renderValidation(view, params);
  if (route === "scope") return renderScope(view, params);
  if (route === "plan") return renderPlan(view, params);
  if (route === "results") return renderResults(view, params);
  if (route === "history") return renderHistory(view, params);
  if (route === "vulns") return renderVulnerabilities(view, params);
  if (route === "tokens") return renderTokens(view, params);
  if (route === "reports") return renderReports(view, params);
  if (route === "settings") return renderSettings(view);
  if (route === "audit") return renderAudit(view);
  view.innerHTML = `<p class='empty'>${t("Unknown view")}</p>`;
}

window.addEventListener("hashchange", router);

/* ---------------- Dashboard ---------------- */
async function renderDashboard(view) {
  view.innerHTML = `
    <h1 class="page">${t("Dashboard")}</h1>
    <p class="page-sub">${t("Autonomous penetration testing control plane. Target:")} <span class="mono">${TARGET_DEFAULT}</span></p>
    <div class="grid cards" id="dashCards"></div>
    <div class="grid" style="grid-template-columns: 1.4fr 1fr; margin-top:16px">
      <div class="panel"><h2>${t("Component health")}</h2><div id="compGrid" class="grid cards"></div></div>
      <div class="panel"><h2>${t("Recent activity")}</h2><div id="recentAud" class="kv"></div></div>
    </div>`;
  const cards = document.getElementById("dashCards");
  const status = await safe(() => api("GET", "/api/status"), {});
  const health = await safe(() => api("GET", "/api/health"), { overall_success: false, components: {} });
  const aud = await safe(() => api("GET", "/api/audit?limit=6"), []);

  const comps = normalizeComponents(health.components);
  const okCount = comps.filter((c) => c.status === "healthy").length;
  cards.innerHTML = `
    ${statCard(t("Mode"), (state.mode || "—").toUpperCase(), state.mode === "simulation" ? "warn" : "good")}
    ${statCard(t("Components"), `${okCount}/${comps.length || 0}`, okCount ? "good" : "bad")}
    ${statCard(t("Live clients"), String(state.subscribers), "")}
    ${statCard(t("Approval mode"), status.approval_mode ? t("ON") : t("OFF"), status.approval_mode ? "warn" : "")}
    <div class="panel stat" style="grid-column: span 1"><div class="k">${t("Quick action")}</div>
      <button class="btn primary" onclick="location.hash='#scan'">${t("+ Launch scan")}</button></div>`;

  const cg = document.getElementById("compGrid");
  cg.innerHTML = comps.map(renderComponentCard).join("") || `<p class="empty">${t("No component data")}</p>`;

  const ra = document.getElementById("recentAud");
  ra.innerHTML = (aud || []).map((a) => `<div><span class="key">${fmtTime(a.ts)}</span><span>${a.action}<span class="muted"> · ${a.actor}</span></span></div>`).join("") || `<p class="empty">${t("No activity yet")}</p>`;
}

/* ---------------- Preflight (env self-check) ---------------- */
async function renderPreflight() {
  const body = document.getElementById("pfBody");
  if (!body) return;
  const pf = await safe(() => api("GET", "/api/preflight"), { checks: [], can_scan: false });
  const statusBadge = pf.can_scan
    ? `<span class="tag good">${t("Ready to scan")}</span>`
    : `<span class="tag bad">${t("Setup needed")}</span>`;
  body.innerHTML = `
    <div style="display:flex;align-items:center;gap:10px;margin-bottom:12px">
      ${statusBadge}
      <span class="muted">${t("Capabilities:")}
        HTTP ${pf.capabilities?.http_layer ? "✓" : "×"} ·
        Shell ${pf.capabilities?.shell_tools ? "✓" : "×"} ·
        WASM ${pf.capabilities?.wasm_python ? "✓" : "×"}
      </span>
    </div>
    <div class="pf-checks">${(pf.checks || []).map(renderPreflightCheck).join("")}</div>
    ${pf.can_scan ? `<a class="btn primary" style="margin-top:12px" href="#scan">${t("Start a scan →")}</a>` : ""}
  `;
  bindPreflightActions();
}

function renderPreflightCheck(c) {
  const icon = { ok: "✅", warn: "⚠️", error: "❌" }[c.status] || "•";
  const actions = (c.actions || []).map((a) => {
    if (a.kind === "api") {
      return `<button class="btn small" data-pf-api data-method="${a.method}" data-path="${a.path}">${a.label}</button>`;
    }
    if (a.kind === "link") {
      return `<a class="btn ghost small" href="${a.href}" target="_blank" rel="noreferrer noopener">${a.label} ↗</a>`;
    }
    if (a.kind === "route") {
      return `<a class="btn ghost small" href="${a.hash}">${a.label}</a>`;
    }
    return "";
  }).join(" ");
  return `
    <div class="pf-check pf-${c.status}">
      <div class="pf-title">${icon} <b>${c.label}</b> <span class="muted"> — ${c.detail || ""}</span></div>
      ${c.impact ? `<div class="pf-impact muted">${c.impact}</div>` : ""}
      ${actions ? `<div class="pf-actions">${actions}</div>` : ""}
    </div>`;
}

function bindPreflightActions() {
  document.querySelectorAll("#preflight [data-pf-api]").forEach((btn) => {
    btn.onclick = async () => {
      const original = btn.textContent;
      btn.disabled = true;
      btn.textContent = t("Running…");
      const r = await safe(() => api(btn.dataset.method, btn.dataset.path), { ok: false, detail: t("request failed") });
      if (r.ok) {
        toast(`✅ ${r.detail || t("Done")}`);
      } else {
        toast(`❌ [${r.error_type || "err"}] ${r.detail || t("Failed")}`);
      }
      btn.disabled = false;
      btn.textContent = original;
      renderPreflight();
    };
  });
}

/* Render Preflight in Settings with auto-fix buttons for unhealthy items */
function renderPreflightWithFixes(pf) {
  const body = document.getElementById("pfBody");
  if (!body) return;
  if (!pf || !pf.checks) { body.innerHTML = `<p class="muted">${t("No preflight data")}</p>`; return; }
  const statusBadge = pf.can_scan
    ? `<span class="tag good">${t("Ready to scan")}</span>`
    : `<span class="tag bad">${t("Setup needed")}</span>`;
  body.innerHTML = `
    <div style="display:flex;align-items:center;gap:10px;margin-bottom:12px">
      ${statusBadge}
      <span class="muted">${t("Capabilities:")}
        HTTP ${pf.capabilities?.http_layer ? "✓" : "×"} ·
        Shell ${pf.capabilities?.shell_tools ? "✓" : "×"} ·
        WASM ${pf.capabilities?.wasm_python ? "✓" : "×"}
      </span>
    </div>
    <div class="pf-checks">${pf.checks.map(renderPreflightCheckWithFix).join("")}</div>
  `;
  /* Bind fix buttons */
  body.querySelectorAll("[data-pf-fix]").forEach((btn) => {
    btn.onclick = async () => {
      const original = btn.innerHTML;
      btn.disabled = true;
      btn.innerHTML = `<span class="spin">⏳</span> ${t("Fixing…")}`;
      const r = await safe(() => api(btn.dataset.method || "POST", btn.dataset.path), { ok: false, detail: t("request failed") });
      if (r.ok) {
        toast(`✅ ${r.detail || t("Fixed! Please refresh.")}`);
        btn.innerHTML = `✅ ${t("Fixed")}`;
        btn.className = "btn small good";
        setTimeout(() => router(), 1500);
      } else {
        toast(`❌ [${r.error_type || "err"}] ${r.detail || t("Failed")}`);
        btn.disabled = false;
        btn.innerHTML = original;
      }
    };
  });
}

/* Render a single preflight check item with fix button (used in Settings) */
function renderPreflightCheckWithFix(c) {
  const icon = { ok: "✅", warn: "⚠️", error: "❌" }[c.status] || "•";
  let fixBtn = "";
  if (c.status !== "ok" && c.actions && c.actions.length) {
    /* Use the first API action as auto-fix */
    const fixAction = c.actions.find((a) => a.kind === "api") || c.actions[0];
    if (fixAction.kind === "api") {
      fixBtn = `<button class="btn small primary" data-pf-fix data-method="${fixAction.method}" data-path="${fixAction.path}">🔧 ${fixAction.label || t("Auto-fix")}</button>`;
    } else if (fixAction.kind === "link") {
      fixBtn = `<a class="btn ghost small" href="${fixAction.href}" target="_blank" rel="noreferrer noopener">${fixAction.label} ↗</a>`;
    } else if (fixAction.kind === "route") {
      fixBtn = `<a class="btn ghost small" href="${fixAction.hash}">${fixAction.label}</a>`;
    }
  }
  return `
    <div class="pf-check pf-${c.status}">
      <div class="pf-title">${icon} <b>${c.label}</b> <span class="muted"> — ${c.detail || ""}</span></div>
      ${c.impact ? `<div class="pf-impact muted">${c.impact}</div>` : ""}
      ${fixBtn ? `<div class="pf-actions" style="margin-top:6px">${fixBtn}</div>` : ""}
    </div>`;
}

function statCard(k, v, cls) {
  const color = cls === "good" ? "var(--good)" : cls === "warn" ? "var(--warn)" : cls === "bad" ? "var(--bad)" : "var(--text)";
  return `<div class="panel stat"><div class="k">${k}</div><div class="v" style="color:${color}">${v}</div></div>`;
}
function tag(cls, text) { return `<span class="tag ${cls}">${text}</span>`; }

// Map every upstream status vocabulary to the canonical dashboard set:
//   "healthy" (ok) | "warn" | "error" (failed / bad)
// The preflight layer reports "ok"/"warn"/"error"; the daemon reports
// "healthy"/"warn"/"error"; legacy simulator responses used "simulated".
// Without this, "ok" fell through to the "bad" branch and every healthy
// component was shown as an error.
function _normStatus(s) {
  const v = String(s == null ? "" : s).toLowerCase();
  if (["ok", "healthy", "simulated", "pass", "passed", "true"].includes(v)) return "healthy";
  if (["warn", "warning"].includes(v)) return "warn";
  return "error";
}

// Normalize the /api/health `components` field into a list of
// {id,label,status,detail} so both the dashboard and settings views can render
// it identically. Handles the legacy dict-shaped response too.
function normalizeComponents(raw) {
  if (Array.isArray(raw)) return raw.map((c) => ({ ...c, status: _normStatus(c && c.status) }));
  if (raw && typeof raw === "object") {
    return Object.entries(raw).map(([k, v]) => ({
      id: k, label: k,
      status: _normStatus(v),
      detail: String(v),
    }));
  }
  return [];
}

function renderComponentCard(c) {
  const cls = c.status === "healthy" ? "good" : c.status === "warn" ? "warn" : "bad";
  return `<div class="panel stat"><div class="k">${esc(c.label || c.id)}</div>
    <div class="v" style="font-size:14px">${tag(cls, c.status)}</div>
    ${c.detail ? `<div class="muted" style="font-size:11px;margin-top:4px">${esc(c.detail)}</div>` : ""}</div>`;
}

function renderComponentRow(c) {
  const cls = c.status === "healthy" ? "good" : c.status === "warn" ? "warn" : "bad";
  return `<div><span class="key">${esc(c.label || c.id)}</span><span>${tag(cls, c.status)}${c.detail ? ` <span class="muted">${esc(c.detail)}</span>` : ""}</span></div>`;
}

function stCls(s) { return ({ running: "warn", completed: "good", aborted: "bad", idle: "", unknown: "" })[(s || "").toLowerCase()] || ""; }
function sevCls(s) { return ({ critical: "bad", high: "bad", medium: "warn", low: "good", info: "" })[(s || "").toLowerCase()] || ""; }
function fmtNum(n) { return (n || 0).toLocaleString("en-US"); }
async function safe(fn, fallback) { try { return await fn(); } catch (e) { return fallback; } }

/* ---------------- New Scan ---------------- */
async function renderScan(view, params) {
  const presets = await safe(() => api("GET", "/api/presets"), []);
  const models = await safe(() => api("GET", "/api/models"), { providers: {} });
  const llm = await safe(() => api("GET", "/api/llm"), { provider: "openai", model_name: "gpt-4o" });

  const provOpts = Object.entries(models.providers || {}).map(([p, ms]) =>
    `<optgroup label="${p}">${ms.map((m) => `<option ${m === llm.model_name ? "selected" : ""}>${m}</option>`).join("")}</optgroup>`).join("");

  view.innerHTML = `
    <h1 class="page">${t("New Scan")}</h1>
    <p class="page-sub">${t("Configure an autonomous engagement. The agent plans, exploits and self-validates.")}</p>
    <div class="panel" style="max-width:920px">
      <h2>${t("1 · Preset workflow")}</h2>
      <div class="presets" id="presets"></div>
      <h2 style="margin-top:22px">${t("2 · Target & scope")}</h2>
      <label class="field"><span>${t("Target URL")}</span><input id="fTarget" class="mono" value="${TARGET_DEFAULT}"></label>
      <label class="field"><span>${t("Scope notes (optional)")}</span><textarea id="fScope" placeholder="${t("e.g. only /api/* and the login flow; do not touch /admin except read-only")}"></textarea></label>
      <h2>${t("3 · Agent & model")}</h2>
      <div class="row">
        <label class="field" style="flex:1"><span>${t("Agent strategy")}</span>
          <select id="fAgent"><option value="router_agent" selected>router_agent (planner + workers)</option></select></label>
        <label class="field" style="flex:1"><span>${t("LLM model")}</span><select id="fModel">${provOpts || `<option>${llm.model_name}</option>`}</select></label>
      </div>
      ${params && params.plan ? `<div class="plan-chip"><span class="k">已挂载作战计划</span> <span class="mono">${esc(params.plan)}</span> <button class="btn ghost sm" id="clearPlan">清除</button></div>` : ""}
      <h2>${t("4 · Guardrails")}</h2>
      <div class="row">
        <label class="field" style="flex:1"><span>${t("Max depth:")} <b id="depthVal">5</b></span>
          <div class="range"><input id="fDepth" type="range" min="1" max="8" value="5"></div></label>
        <label class="field" style="flex:1"><span>${t("Min confidence:")} <b id="confVal">0.6</b></span>
          <div class="range"><input id="fConf" type="range" min="0" max="1" step="0.05" value="0.6"></div></label>
      </div>
      <label class="field"><span><input type="checkbox" id="fApproval" style="width:auto;margin-right:8px">${t("Require operator approval before intrusive actions")}</span></label>
      <div class="section-head" style="margin-top:10px">
        <span class="muted" id="promptPrev"></span>
        <button class="btn primary" id="launchBtn">${t("Launch scan ▶")}</button>
      </div>
    </div>`;

  const pbox = document.getElementById("presets");
  let selectedPreset = null;
  pbox.innerHTML = presets.map((p) => `
    <div class="preset" data-id="${p.id}">
      <div class="pname"><span style="color:${p.color}">●</span>${p.name}</div>
      <div class="pdesc">${p.description}</div>
    </div>`).join("");
  pbox.querySelectorAll(".preset").forEach((el) => el.onclick = () => {
    pbox.querySelectorAll(".preset").forEach((x) => x.classList.remove("sel"));
    el.classList.add("sel");
    selectedPreset = presets.find((p) => p.id === el.dataset.id);
    document.getElementById("fDepth").value = selectedPreset.max_depth;
    document.getElementById("depthVal").textContent = selectedPreset.max_depth;
    document.getElementById("promptPrev").textContent = selectedPreset.prompt.slice(0, 90) + "…";
  });

  const depth = document.getElementById("fDepth"), conf = document.getElementById("fConf");
  depth.oninput = () => document.getElementById("depthVal").textContent = depth.value;
  conf.oninput = () => document.getElementById("confVal").textContent = conf.value;

  document.getElementById("launchBtn").onclick = async () => {
    const target = document.getElementById("fTarget").value.trim();
    const depthV = parseInt(depth.value, 10);
    const confV = parseFloat(conf.value);
    const prompt = selectedPreset ? selectedPreset.prompt : document.getElementById("fScope").value || "Run a full autonomous penetration test.";
    const approval = document.getElementById("fApproval").checked;
    const btn = document.getElementById("launchBtn");
    btn.disabled = true; btn.textContent = t("Checking LLM…");

    // Gate: LLM must be configured AND reachable before we hand a task to the daemon.
    const guard = await verifyLLMOrBanner();
    if (!guard.ok) {
      btn.disabled = false;
      btn.textContent = t("Launch scan ▶");
      return;
    }

    btn.textContent = t("Launching…");
    try {
      // approval mode
      await api("POST", "/api/approval-mode", { enabled: approval });
      const ag = await api("POST", "/api/agents", { target, provider: llm.provider, model_name: document.getElementById("fModel").value });
      const agentId = ag.agent_id;
      const scanPayload = {
        agent_id: agentId, target, prompt, max_depth: depthV,
        validation_config: { min_confidence: confV },
      };
      if (params && params.plan) scanPayload.plan_id = params.plan;
      const scan = await api("POST", "/api/scans", scanPayload);
      location.hash = `#monitor?session=${encodeURIComponent(scan.session_id)}&agent=${encodeURIComponent(agentId)}`;
    } catch (e) {
      alert(t("Launch failed: ") + e.message);
      btn.disabled = false; btn.textContent = t("Launch scan ▶");
    }
  };
  if (params && params.plan) {
    const cp = document.getElementById("clearPlan");
    if (cp) cp.onclick = () => { location.hash = "#scan"; };
  }
}

/* ---------------- Monitor ---------------- */
function renderMonitor(view, params) {
  const session = params.session;
  const agent = params.agent;
  state.currentSession = session || null;
  state.sessionEvents[session] = state.sessionEvents[session] || [];
  state.confidence = 0;

  view.innerHTML = `
    <div class="section-head">
      <div><h1 class="page" style="margin:0">${t("Monitor")}</h1>
      <p class="page-sub" style="margin:2px 0 0">${t("session")} <span class="mono">${session || "—"}</span></p></div>
      <div class="pill-row">
        <span class="badge" id="runStatus">${t("running")}</span>
        <button class="btn danger" id="intrBtn">${t("■ Interrupt")}</button>
      </div>
    </div>
    <div class="conf-wrap">
      <div class="muted" style="font-size:12px;margin-bottom:6px">${t("Agent confidence")}</div>
      <div class="conf-bar"><div class="conf-fill" id="confFill"></div></div>
    </div>
    <div class="split">
      <div>
        <div class="panel" style="padding:0;overflow:hidden"><h2 style="padding:14px 14px 0">${t("Live event feed")}</h2>
          <div class="feed" id="feed"></div></div>
        <div id="approvals" style="margin-top:16px"></div>
      </div>
      <div>
        <div class="panel"><h2>${t("Task tree")}</h2><div class="tree" id="tree"><p class="empty">${t("loading…")}</p></div></div>
        <div class="panel" style="margin-top:16px"><h2>${t("Session state")}</h2><div class="kv" id="sessState"></div></div>
      </div>
    </div>`;

  state.feedEl = document.getElementById("feed");
  // replay already-captured events for this session
  (state.sessionEvents[session] || []).slice().reverse().forEach((ev) => appendFeedLine(state.feedEl, ev));
  updateConfidenceBar();
  renderApprovals();

  // poll task tree + session state
  const tick = async () => {
    if (currentRoute() !== "monitor") { clearInterval(window.__monTick); return; }
    const snap = await safe(() => api("GET", `/api/sessions/${session}`), null);
    renderSessionState(snap);
    const tasks = await safe(() => api("GET", `/api/agents/${agent}/tasks`), null);
    renderTree(tasks);
    if (snap && (snap.status === "completed" || snap.status === "aborted")) {
      document.getElementById("runStatus").textContent = snap.status;
      document.getElementById("runStatus").className = "badge " + (snap.status === "completed" ? "good" : "bad");
    }
  };
  tick();
  window.__monTick = setInterval(tick, 2500);

  document.getElementById("intrBtn").onclick = async () => {
    if (!confirm(t("Interrupt this scan?"))) return;
    await safe(() => api("POST", `/api/scans/${session}/interrupt`, { reason: "operator" }), null);
  };
}

function appendFeedLine(feed, ev) {
  if (!feed) return;
  const line = document.createElement("div");
  line.className = "line";
  line.innerHTML = `<span class="ts">${fmtTime()}</span><span class="et">${ev.type}</span><span class="ev">${summarize(ev)}</span>`;
  feed.prepend(line);
  while (feed.childElementCount > 400) feed.lastChild.remove();
}
function summarize(ev) {
  const d = ev.data || {};
  if (d.description) return esc(d.description);
  if (d.task) return esc(d.task) + (d.status ? ` [${d.status}]` : "");
  if (d.tool_name) return `${esc(d.tool_name)} ${esc(JSON.stringify(d.tool_args || ""))}`;
  if (d.title) return esc(d.title);
  if (d.action) return `${esc(d.action)} → ${esc(d.target_endpoint || "")}`;
  return esc(JSON.stringify(d).slice(0, 80));
}
function esc(s) { return String(s).replace(/[&<>]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;" }[c])); }

function updateConfidenceBar() {
  const fill = document.getElementById("confFill");
  if (fill) fill.style.width = Math.round(state.confidence * 100) + "%";
}

function renderApprovals() {
  const box = document.getElementById("approvals");
  if (!box) return;
  const ids = Object.keys(state.approvals);
  if (!ids.length) { box.innerHTML = ""; return; }
  box.innerHTML = ids.map((id) => {
    const ev = state.approvals[id]; const d = ev.data || {};
    return `<div class="approval"><div class="muted" style="font-size:11px;letter-spacing:.5px">${t("APPROVAL REQUIRED")}</div>
      <div style="font-weight:700;margin-top:4px">${esc(d.tool_name || "")}</div>
      <div class="desc">${esc(d.description || "")}<br><span class="mono">${esc(JSON.stringify(d.tool_args || {}))}</span></div>
      <div class="pill-row">
        <button class="btn primary" onclick="decideApproval('${id}', true)">${t("✓ Approve")}</button>
        <button class="btn danger" onclick="decideApproval('${id}', false)">${t("✕ Deny")}</button>
      </div></div>`;
  }).join("");
}
window.decideApproval = async function (requestId, approved) {
  await safe(() => api("POST", "/api/approve", { request_id: requestId, approved }), null);
  delete state.approvals[requestId];
  renderApprovals();
};

function renderTree(tasks) {
  const el = document.getElementById("tree");
  if (!el) return;
  if (!tasks) { el.innerHTML = `<p class="empty">${t("no data")}</p>`; return; }
  el.innerHTML = renderTreeNode(tasks);
}
function renderTreeNode(node, depth = 0) {
  if (Array.isArray(node)) return node.map((n) => renderTreeNode(n, depth)).join("");
  if (!node || typeof node !== "object") return "";
  const status = node.status ? ` <span class="tag">${node.status}</span>` : "";
  const label = node.task || node.name || node.phase || node.type || JSON.stringify(node).slice(0, 40);
  const children = node.children ? renderTreeNode(node.children, depth + 1) : "";
  return `<div class="node">${esc(label)}${status}</div>${children}`;
}
function renderSessionState(snap) {
  const el = document.getElementById("sessState");
  if (!el || !snap) return;
  const rows = [
    ["status", snap.status],
    ["target", snap.target],
    ["agent", snap.agent_id],
    ["confidence", snap.confidence != null ? snap.confidence : (state.confidence || 0)],
    ["findings", (snap.findings || []).length],
    ["duration", snap.duration != null ? snap.duration + "s" : "—"],
  ];
  el.innerHTML = rows.map(([k, v]) => `<div><span class="key">${k}</span><span>${esc(v)}</span></div>`).join("");
}

/* ---------------- Results ---------------- */
async function renderResults(view, params) {
  const session = params.session;
  const agent = params.agent;
  view.innerHTML = `
    <div class="section-head"><div><h1 class="page" style="margin:0">${t("Results")}</h1>
      <p class="page-sub" style="margin:2px 0 0">${t("session")} <span class="mono">${session || "—"}</span></p></div>
      <button class="btn" onclick="location.hash='#monitor?session=${encodeURIComponent(session || "")}&agent=${encodeURIComponent(agent || "")}'">${t("◉ Live monitor")}</button></div>
    <div class="grid" style="grid-template-columns: 1.3fr 1fr">
      <div class="panel"><h2>${t("Findings")}</h2><div id="findings"><p class="empty">${t("loading…")}</p></div></div>
      <div class="panel"><h2>${t("Execution log")}</h2><div class="feed" id="resFeed" style="height:420px"></div></div>
    </div>`;

  const snap = await safe(() => api("GET", `/api/sessions/${session}`), null);
  const findings = (snap && snap.findings) || [];
  const fEl = document.getElementById("findings");
  if (!findings.length) {
    fEl.innerHTML = `<p class="empty">${t("No validated findings yet. Run a scan or wait for self-validation.")}</p>`;
  } else {
    fEl.innerHTML = `<table><thead><tr><th>${t("Severity")}</th><th>${t("Title")}</th><th>${t("Endpoint")}</th><th>${t("Conf.")}</th></tr></thead><tbody>` +
      findings.map((f) => `<tr>
        <td class="sev-${f.severity}">${f.severity.toUpperCase()}</td>
        <td>${esc(f.title)}</td>
        <td class="mono">${esc(f.endpoint || "")}</td>
        <td>${f.confidence != null ? Math.round(f.confidence * 100) + "%" : "—"}</td></tr>
        <tr><td colspan="4" class="muted" style="font-family:var(--mono);font-size:12px;border:none">${esc(f.evidence || "")}</td></tr>`).join("") + `</tbody></table>`;
  }
  const feed = document.getElementById("resFeed");
  (state.sessionEvents[session] || []).slice().reverse().forEach((ev) => {
    if (["execution_record", "validation_result", "tool_call_start", "confidence_update"].includes(ev.type)) appendFeedLine(feed, ev);
  });
  if (!feed.childElementCount) feed.innerHTML = `<p class="empty">${t("no execution events captured")}</p>`;
}

/* ---------------- Settings ---------------- */
async function renderSettings(view) {
  const health = await safe(() => api("GET", "/api/health"), { components: {} });
  const pf = await safe(() => api("GET", "/api/preflight"), { checks: [], setup_needed: false });
  const val = await safe(() => api("GET", "/api/validation"), { min_confidence: 0.6, max_retries: 3, require_validation_token: true, strict_mode: false });
  const llm = await safe(() => api("GET", "/api/llm"), { provider: "openai", model_name: "gpt-4o" });
  const am = await safe(() => api("GET", "/api/approval-mode"), { approval_mode: false });
  state.approvalMode = !!am.approval_mode;

  const comps = normalizeComponents(health.components);
  view.innerHTML = `
    <h1 class="page">${t("Settings")}</h1>
    <p class="page-sub">${t("Component health and agent guardrails.")}</p>
    <div class="grid" style="grid-template-columns: 1fr 1fr">
      <div class="panel"><h2>${t("Component health")}</h2>
        <div class="kv">${comps.map(renderComponentRow).join("") || `<p class="empty">${t("no data")}</p>`}</div>
        <button class="btn" id="initBtn" style="margin-top:12px">${t("↻ Re-init components")}</button>
      </div>
      <div class="panel"><h2>${t("Validation config")}</h2>
        <label class="field"><span>${t("Min confidence:")} <b id="vc">${val.min_confidence}</b></span>
          <div class="range"><input id="vConf" type="range" min="0" max="1" step="0.05" value="${val.min_confidence}"></div></label>
        <label class="field"><span>${t("Max retries:")} <b id="vr">${val.max_retries}</b></span>
          <div class="range"><input id="vRet" type="range" min="0" max="10" value="${val.max_retries}"></div></label>
        <label class="field"><span><input type="checkbox" id="vTok" ${val.require_validation_token ? "checked" : ""} style="width:auto;margin-right:8px">${t("Require validation token")}</span></label>
        <label class="field"><span><input type="checkbox" id="vStrict" ${val.strict_mode ? "checked" : ""} style="width:auto;margin-right:8px">${t("Strict mode")}</span></label>
        <button class="btn primary" id="saveVal">${t("Save validation")}</button>
      </div>
      <div class="panel"><h2>${t("LLM provider")}</h2>
        <label class="field"><span>${t("Provider")}</span><input id="llmP" class="mono" value="${llm.provider || ""}"></label>
        <label class="field"><span>${t("Model name")}</span><input id="llmM" class="mono" value="${llm.model_name || llm.model || ""}"></label>
        <label class="field"><span>${t("API key")}</span><input id="llmK" type="password" class="mono" placeholder="sk-... (leave blank to reuse saved)"></label>
        <label class="field"><span>${t("Base URL (optional)")}</span><input id="llmB" class="mono" placeholder="https://..."></label>
        <div style="display:flex;gap:8px;flex-wrap:wrap">
          <button class="btn" id="testLlm">${t("Test connection")}</button>
          <button class="btn primary" id="saveLlm">${t("Save LLM")}</button>
        </div>
        <div id="llmTestResult" class="pf-check" style="display:none;margin-top:12px"></div>
      </div>
      <div class="panel"><h2>${t("Approval mode")}</h2>
        <p class="muted" style="font-size:12px">${t("When enabled, intrusive agent actions require operator sign-off via the Monitor.")}</p>
        <label class="field"><span><input type="checkbox" id="amChk" ${state.approvalMode ? "checked" : ""} style="width:auto;margin-right:8px">${t("Require approval for intrusive actions")}</span></label>
        <button class="btn primary" id="saveAm">${t("Save")}</button>
      </div>
    </div>
    <div class="panel" style="margin-top:16px"><h2>${t("Environment preflight")} ${pf.setup_needed ? `<span class="badge warn">${t("Setup needed")}</span>` : ""}</h2><div id="pfBody"></div></div>`;

  document.getElementById("vConf").oninput = (e) => document.getElementById("vc").textContent = e.target.value;
  document.getElementById("vRet").oninput = (e) => document.getElementById("vr").textContent = e.target.value;
  document.getElementById("saveVal").onclick = async () => {
    await safe(() => api("POST", "/api/validation", {
      min_confidence: parseFloat(document.getElementById("vConf").value),
      max_retries: parseInt(document.getElementById("vRet").value, 10),
      require_validation_token: document.getElementById("vTok").checked,
      strict_mode: document.getElementById("vStrict").checked,
    }), null);
    toast(t("Validation config saved"));
  };
  document.getElementById("saveLlm").onclick = async () => {
    const payload = {
      provider: document.getElementById("llmP").value,
      model_name: document.getElementById("llmM").value,
    };
    const apiKey = document.getElementById("llmK").value;
    const baseUrl = document.getElementById("llmB").value;
    if (apiKey) payload.api_key = apiKey;
    if (baseUrl) payload.base_url = baseUrl;
    await safe(() => api("POST", "/api/llm", payload), null);
    toast(t("LLM provider saved"));
  };
  document.getElementById("testLlm").onclick = async () => {
    const box = document.getElementById("llmTestResult");
    box.style.display = "block";
    box.className = "pf-check pf-warn";
    box.innerHTML = `⏳ ${t("Testing...")}`;
    const payload = {
      provider: document.getElementById("llmP").value,
      model_name: document.getElementById("llmM").value,
      api_key: document.getElementById("llmK").value || null,
      base_url: document.getElementById("llmB").value || null,
    };
    const r = await safe(() => api("POST", "/api/llm/test", payload), { ok: false, error_type: "network", detail: "request failed" });
    if (r.ok) {
      box.className = "pf-check pf-ok";
      box.innerHTML = `✅ ${t("Connected")} — ${r.detail || ""} <span class="muted">(${r.latency_ms}ms)</span>`;
    } else {
      const safeDetail = String(r.detail || "").replace(/</g, "&lt;").replace(/>/g, "&gt;");
      box.className = "pf-check pf-error";
      box.innerHTML = `❌ ${t("Failed")} [${r.error_type || "err"}] — <span class="mono">${safeDetail}</span>`;
    }
  };
  document.getElementById("saveAm").onclick = async () => {
    await safe(() => api("POST", "/api/approval-mode", { enabled: document.getElementById("amChk").checked }), null);
    toast(t("Approval mode saved"));
  };
  document.getElementById("initBtn").onclick = async () => {
    await safe(() => api("POST", "/api/init"), null);
    toast(t("Components re-initializing"));
    setTimeout(router, 1200);
  };
  /* Render Environment Preflight with fix buttons */
  renderPreflightWithFixes(pf);
}

/* ---------------- Audit ---------------- */
async function renderAudit(view) {
  const rows = await safe(() => api("GET", "/api/audit?limit=200"), []);
  view.innerHTML = `
    <h1 class="page">${t("Audit")}</h1>
    <p class="page-sub">${t("Authorization trail of every privileged action taken through the console.")}</p>
    <div class="panel" style="padding:0;overflow:hidden">
      <table><thead><tr><th>${t("Time")}</th><th>${t("Operator")}</th><th>${t("Action")}</th><th>${t("Target")}</th><th>${t("Decision")}</th><th>${t("Detail")}</th></tr></thead>
      <tbody id="audBody"></tbody></table></div>`;
  const body = document.getElementById("audBody");
  body.innerHTML = (rows || []).map((a) => `<tr>
    <td class="mono">${fmtTime(a.ts)}</td>
    <td>${esc(a.actor)}</td>
    <td>${esc(a.action)}</td>
    <td class="mono">${esc(a.target || "—")}</td>
    <td>${a.decision ? tag(a.decision === "granted" || a.decision === "launched" || a.decision === "enabled" ? "good" : a.decision === "denied" || a.decision === "disabled" ? "bad" : "warn", a.decision) : "—"}</td>
    <td class="muted">${esc(a.detail || "")}</td></tr>`).join("") || `<tr><td colspan="6" class="empty">${t("No audit entries")}</td></tr>`;
}

/* ---------------- Persistent top banner ---------------- */
// Persistent, dismissable banner at the top of the app for blocking-issue
// callouts (missing LLM, connectivity failure). Multiple banners stack.
function banner({ id, level, message, actionLabel, actionHref, actionOnClick }) {
  let host = document.getElementById("bannerHost");
  if (!host) {
    host = document.createElement("div");
    host.id = "bannerHost";
    host.style.cssText = "position:fixed;top:0;left:232px;right:0;z-index:60;display:flex;flex-direction:column;gap:0";
    document.body.appendChild(host);
  }
  const bid = id || `b-${Math.random().toString(36).slice(2, 8)}`;
  const existing = document.getElementById(bid);
  if (existing) existing.remove();

  const colors = {
    error: "background:#4a1d1d;border-bottom:1px solid #7a2b2b;color:#ffdada",
    warn:  "background:#4a3a1d;border-bottom:1px solid #7a5b2b;color:#ffeeb8",
    info:  "background:#1d2a4a;border-bottom:1px solid #2b447a;color:#dae4ff",
  };
  const style = colors[level] || colors.info;
  const b = document.createElement("div");
  b.id = bid;
  b.style.cssText = `${style};padding:10px 18px;display:flex;align-items:center;justify-content:space-between;font-size:13px`;
  const icon = { error: "❌", warn: "⚠️", info: "ℹ️" }[level] || "•";
  const actionBtn = actionLabel
    ? `<button class="btn small" style="margin-left:10px" data-bnr-action>${actionLabel}</button>`
    : "";
  b.innerHTML = `
    <span>${icon} ${message}</span>
    <span>${actionBtn}
      <button class="btn small ghost" style="margin-left:6px" data-bnr-close>${t("Dismiss")}</button>
    </span>`;
  host.appendChild(b);
  b.querySelector("[data-bnr-close]").onclick = () => b.remove();
  const actEl = b.querySelector("[data-bnr-action]");
  if (actEl) {
    actEl.onclick = () => {
      if (actionOnClick) actionOnClick();
      if (actionHref) location.hash = actionHref;
    };
  }
  return b;
}

function dismissBanner(id) {
  const el = document.getElementById(id);
  if (el) el.remove();
}

/* ---------------- LLM guardrail (used before scan launch and on startup) ---------------- */
// Returns { configured, connected, detail }. Never throws.
async function checkLLMReady() {
  const pf = await safe(() => api("GET", "/api/preflight"), null);
  if (!pf) return { configured: false, connected: false, detail: "preflight request failed" };
  const llmCheck = (pf.checks || []).find((c) => c.id === "llm");
  if (!llmCheck || llmCheck.status === "error") {
    return { configured: false, connected: false, detail: llmCheck?.detail || "not configured" };
  }
  // Configured — now check connectivity with saved credentials.
  const llm = await safe(() => api("GET", "/api/llm"), null);
  if (!llm || !llm.provider) return { configured: false, connected: false, detail: "provider missing" };
  const r = await safe(
    () => api("POST", "/api/llm/test", {
      provider: llm.provider,
      model_name: llm.model_name || llm.model,
    }),
    { ok: false, error_type: "network", detail: "test request failed" },
  );
  return {
    configured: true,
    connected: !!r.ok,
    detail: r.ok ? `${r.detail || ""} (${r.latency_ms || "?"}ms)` : `[${r.error_type || "err"}] ${r.detail || ""}`,
  };
}

async function verifyLLMOrBanner() {
  const s = await checkLLMReady();
  if (!s.configured) {
    banner({
      id: "llm-missing",
      level: "error",
      message: t("LLM not configured — scans are disabled until an LLM provider is set."),
      actionLabel: t("Configure LLM"),
      actionHref: "#settings",
    });
    return { ok: false, reason: "not_configured", detail: s.detail };
  }
  if (!s.connected) {
    banner({
      id: "llm-unreachable",
      level: "error",
      message: t("LLM connectivity test failed: ") + s.detail,
      actionLabel: t("Open LLM settings"),
      actionHref: "#settings",
    });
    return { ok: false, reason: "unreachable", detail: s.detail };
  }
  dismissBanner("llm-missing");
  dismissBanner("llm-unreachable");
  return { ok: true };
}


/* ---------------- History ---------------- */
async function renderHistory(view, params) {
  view.innerHTML = `
    <h1 class="page">${t("History")}</h1>
    <p class="page-sub">${t("All past and running scan sessions.")}</p>
    <div class="panel" style="padding:0;overflow:hidden"><div id="histBody"></div></div>`;
  const body = document.getElementById("histBody");
  body.innerHTML = `<p class="empty">${t("loading…")}</p>`;
  const rows = await safe(() => api("GET", "/api/sessions"), []);
  if (!rows || !rows.length) {
    body.innerHTML = `<p class="empty">${t("No sessions yet. Launch a scan to populate history.")}</p>`;
    return;
  }
  const trs = rows.map((r) => {
    const sid = r.session_id || "";
    const agent = r.agent_id ? `&agent=${encodeURIComponent(r.agent_id)}` : "";
    const st = r.status || "unknown";
    return `<tr>
      <td class="mono">${esc((sid || "").slice(0, 12))}</td>
      <td>${esc(r.target || "")}</td>
      <td>${tag(stCls(st), st)}</td>
      <td>${r.findings || 0}</td>
      <td>${r.duration != null ? r.duration + "s" : "—"}</td>
      <td>${r.created_at ? fmtTime(r.created_at) : "—"}</td>
      <td>${fmtNum(r.total_tokens)}</td>
      <td class="row-actions">
        <a class="btn-mini" href="#results?session=${encodeURIComponent(sid)}">${t("View")}</a>
        <a class="btn-mini" href="#reports?session=${encodeURIComponent(sid)}">${t("Report")}</a>
        <a class="btn-mini" href="#monitor?session=${encodeURIComponent(sid)}${agent}">${t("Monitor")}</a>
      </td></tr>`;
  }).join("");
  body.innerHTML = `<table><thead><tr>
    <th>${t("Session")}</th><th>${t("Target")}</th><th>${t("Status")}</th><th>${t("Findings")}</th>
    <th>${t("Duration")}</th><th>${t("Created")}</th><th>${t("Tokens")}</th><th></th>
  </tr></thead><tbody>${trs}</tbody></table>`;
}

/* ---------------- Vulnerabilities ---------------- */
async function renderVulnerabilities(view, params) {
  view.innerHTML = `
    <h1 class="page">${t("Vulnerabilities")}</h1>
    <p class="page-sub">${t("All findings aggregated across sessions.")}</p>
    <div id="vulnSummary"></div>
    <div class="panel" style="padding:0;overflow:hidden;margin-top:16px"><div id="vulnBody"></div></div>`;
  const sessions = await safe(() => api("GET", "/api/sessions"), []);
  const findings = [];
  (sessions || []).forEach((s) => (s.findings || []).forEach((f) => findings.push(Object.assign({}, f, { _session: s.session_id }))));
  const summary = document.getElementById("vulnSummary");
  const order = { critical: 0, high: 1, medium: 2, low: 3, info: 4 };
  const counts = {};
  findings.forEach((f) => { const k = (f.severity || "low").toLowerCase(); counts[k] = (counts[k] || 0) + 1; });
  summary.innerHTML = `<div class="section-label">${t("Severity summary")}</div><div class="grid cards">` +
    ["critical", "high", "medium", "low", "info"].map((s) => statCard(t(s.charAt(0).toUpperCase() + s.slice(1)), String(counts[s] || 0), sevCls(s))).join("") + `</div>`;
  const body = document.getElementById("vulnBody");
  if (!findings.length) { body.innerHTML = `<p class="empty">${t("No vulnerabilities found")}</p>`; return; }
  const trs = findings.sort((a, b) => (order[(a.severity || "low").toLowerCase()] || 9) - (order[(b.severity || "low").toLowerCase()] || 9)).map((f) => {
    const sid = f._session || "";
    return `<tr>
      <td>${tag(sevCls(f.severity), f.severity)}</td>
      <td>${esc(f.title || "")}</td>
      <td class="mono">${esc(f.endpoint || "")}</td>
      <td>${f.confidence != null ? Math.round(f.confidence * 100) + "%" : "—"}</td>
      <td><a class="btn-mini" href="#results?session=${encodeURIComponent(sid)}">${esc((sid || "").slice(0, 12))}</a></td></tr>`;
  }).join("");
  body.innerHTML = `<div class="section-label">${t("All findings across sessions")}</div>
    <table><thead><tr><th>${t("Severity")}</th><th>${t("Title")}</th><th>${t("Endpoint")}</th><th>${t("Conf.")}</th><th>${t("Session")}</th></tr></thead>
    <tbody>${trs}</tbody></table>`;
}

/* ---------------- Token Usage ---------------- */
async function renderTokens(view, params) {
  const sessionId = params && params.session;
  view.innerHTML = `
    <h1 class="page">${t("Token Usage")}</h1>
    <p class="page-sub">${t("Cost incurred by LLM calls across autonomous scans.")}</p>
    <div class="grid cards" id="tokCards"></div>
    <div class="panel" style="margin-top:16px"><h2>${t("Usage by phase")}</h2><div id="tokPhase"></div></div>
    <div class="panel" style="margin-top:16px"><h2>${t("Per-session usage")}</h2><div id="tokPer"></div></div>`;
  const agg = await safe(() => api("GET", "/api/tokens"), null);
  const cards = document.getElementById("tokCards");
  if (agg) {
    cards.innerHTML = statCard(t("Total prompt tokens"), fmtNum(agg.total_prompt_tokens), "") +
      statCard(t("Total completion tokens"), fmtNum(agg.total_completion_tokens), "") +
      statCard(t("Total tokens"), fmtNum(agg.total_tokens), "") +
      statCard(t("Estimated cost (USD)"), "$" + (agg.total_cost_usd != null ? agg.total_cost_usd.toFixed(2) : "0.00"), "");
  }
  let byPhase = (agg && agg.by_phase) || {};
  let phaseTitle = t("Usage by phase");
  if (sessionId) {
    const st = await safe(() => api("GET", `/api/sessions/${encodeURIComponent(sessionId)}/tokens`), null);
    if (st) { byPhase = st.by_phase || {}; phaseTitle = t("Usage by phase") + " · " + esc(sessionId.slice(0, 12)); }
  }
  const phaseEl = document.getElementById("tokPhase");
  const phases = Object.entries(byPhase);
  if (phases.length) {
    const max = Math.max.apply(null, phases.map((p) => p[1].total_tokens || 0).concat([1]));
    phaseEl.innerHTML = phases.map(([name, p]) => {
      const w = Math.round(100 * (p.total_tokens || 0) / max);
      return `<div class="bar-row"><div class="bar-label">${esc(name)}</div>
        <div class="bar-track"><div class="bar-fill" style="width:${w}%"></div></div>
        <div class="bar-val">${fmtNum(p.total_tokens || 0)} · $${(p.cost_usd || 0).toFixed(2)}</div></div>`;
    }).join("");
  } else { phaseEl.innerHTML = `<p class="empty">${t("no data")}</p>`; }
  const perEl = document.getElementById("tokPer");
  const per = (agg && agg.per_session) || [];
  if (per.length) {
    perEl.innerHTML = `<table><thead><tr><th>${t("Session")}</th><th>${t("Target")}</th><th>${t("Tokens")}</th><th>${t("Cost")}</th></tr></thead><tbody>` +
      per.map((r) => `<tr>
        <td><a class="btn-mini" href="#tokens?session=${encodeURIComponent(r.session_id || "")}">${esc((r.session_id || "").slice(0, 12))}</a></td>
        <td>${esc(r.target || "")}</td>
        <td>${fmtNum(r.total_tokens || 0)}</td>
        <td>$${(r.cost_usd != null ? r.cost_usd : 0).toFixed(2)}</td></tr>`).join("") + `</tbody></table>`;
  } else { perEl.innerHTML = `<p class="empty">${t("no data")}</p>`; }
}

/* ---------------- Reports ---------------- */
async function renderReports(view, params) {
  const sessionId = params && params.session;
  view.innerHTML = `
    <h1 class="page">${t("Reports")}</h1>
    <p class="page-sub">${t("View a security assessment report and download it.")}</p>
    <div id="repBody"></div>`;
  const body = document.getElementById("repBody");
  if (!sessionId) {
    const sessions = await safe(() => api("GET", "/api/sessions"), []);
    if (!sessions || !sessions.length) { body.innerHTML = `<p class="empty">${t("No sessions yet. Launch a scan to populate history.")}</p>`; return; }
    const cards = sessions.map((s) => `<a class="report-pick" href="#reports?session=${encodeURIComponent(s.session_id)}">
        <div style="font-weight:800">${esc((s.session_id || "").slice(0, 12))}</div>
        <div class="muted">${esc(s.target || "")} · ${tag(stCls(s.status || "unknown"), s.status || "unknown")}</div></a>`).join("");
    body.innerHTML = `<div class="section-label">${t("Select a session")}</div>
      <p class="muted">${t("Pick a completed session to view its report")}</p>
      <div class="report-picker">${cards}</div>`;
    return;
  }
  const report = await safe(() => api("GET", `/api/sessions/${encodeURIComponent(sessionId)}/report`), null);
  if (!report) { body.innerHTML = `<p class="empty">${t("No report available for this session")}</p>`; return; }
  const tok = report.tokens || {};
  const fhtml = (report.findings && report.findings.length) ? report.findings.map((f) => `
      <li class="finding-item">${tag(sevCls(f.severity), f.severity)} <strong>${esc(f.title || "")}</strong>
        <div class="muted">${esc(f.endpoint || "")} · ${t("Confidence")}: ${f.confidence != null ? Math.round(f.confidence * 100) + "%" : "—"}</div>
        <div class="evidence">${esc(f.evidence || "")}</div></li>`).join("")
    : `<li class="muted">${t("No vulnerabilities found")}</li>`;
  body.innerHTML = `
    <div class="report-toolbar">
      <span class="muted">${t("Report for")} <code>${esc((report.session_id || "").slice(0, 12))}</code> · ${esc(report.target || "")}</span>
      <span>
        <a class="btn-mini" href="/api/sessions/${encodeURIComponent(sessionId)}/report/download?format=markdown" download>${t("Download Markdown")}</a>
        <a class="btn-mini" href="/api/sessions/${encodeURIComponent(sessionId)}/report/download?format=json" download>${t("Download JSON")}</a>
      </span>
    </div>
    <div class="report-meta">
      <span>${t("Status")}: ${tag(stCls(report.status || "unknown"), report.status || "unknown")}</span>
      <span>${t("Confidence")}: ${report.confidence != null ? report.confidence : "—"}</span>
      <span>${t("Duration")}: ${report.duration != null ? report.duration + "s" : "—"}</span>
      <span>${t("Tokens")}: ${fmtNum(tok.total_tokens)} · $${(tok.cost_usd || 0).toFixed(2)}</span>
    </div>
    <div class="section-label">${t("Findings")}</div>
    <ul class="finding-list">${fhtml}</ul>`;
}

/* ---------------- Boot ---------------- */
connectEvents();
localizeStatic();
document.querySelectorAll(".lang-btn").forEach((b) => b.classList.toggle("active", b.dataset.lang === lang));
renderTopbar();
router();

// NOTE: The "LLM not configured" reminder is intentionally NOT shown on load.
// It only surfaces when the user actually starts a task (see the launch gate in
// renderScan, which calls verifyLLMOrBanner()), so the banner is no longer a
// persistent, always-on notice.

// Close the mobile sidebar whenever a nav item is activated.
document.querySelectorAll(".nav-item").forEach((el) =>
  el.addEventListener("click", () => document.querySelector(".app").classList.remove("nav-open")));

/* ===========================================================================
   Live — real-time agent operations board
   =========================================================================== */
const KNOWN_AGENTS = ["router_agent", "recon_agent", "exploit_agent", "memory",
  "judge", "webapp_analyzer", "authenticator", "requester", "shell", "python_interpreter"];
const liveState = {
  running: false, sessionId: null,
  agents: {}, tasks: {}, findings: [], events: [],
  kpis: { events: 0, tasksDone: 0, findings: 0, confidence: 0, tokens: 0, cost: 0 },
};
function ensureAgentsInit() {
  KNOWN_AGENTS.forEach((n) => {
    if (!liveState.agents[n]) liveState.agents[n] = { name: n, status: "idle", phase: "", task: "", tool: "", confidence: 0, lastTs: 0 };
  });
}
function truncateStr(s, n) { s = String(s == null ? "" : s); return s.length > n ? s.slice(0, n - 1) + "…" : s; }
function setTxt(id, v) { const e = document.getElementById(id); if (e) e.textContent = v; }
function cssId(s) { return String(s).replace(/[^a-zA-Z0-9_-]/g, "_"); }
function toast(msg, kind) {
  let t = document.getElementById("toast");
  if (!t) { t = document.createElement("div"); t.id = "toast"; t.className = "toast"; document.body.appendChild(t); }
  t.textContent = msg; t.className = "toast show " + (kind || "good");
  clearTimeout(t._tm); t._tm = setTimeout(() => { t.className = "toast " + (kind || "good"); }, 2800);
}

function updateLiveState(ev) {
  const d = ev.data || {};
  const a = d.agent_name || d.agent_id || null;
  if (a && !liveState.agents[a]) liveState.agents[a] = { name: a, status: "idle", phase: "", task: "", tool: "", confidence: 0, lastTs: 0 };
  liveState.events.unshift(ev);
  if (liveState.events.length > 300) liveState.events.pop();
  liveState.kpis.events++;
  switch (ev.type) {
    case "agent_start":
      liveState.running = true; liveState.sessionId = ev.session_id || liveState.sessionId;
      if (liveState.agents.router_agent) liveState.agents.router_agent.status = "thinking";
      break;
    case "agent_step":
      if (a) { liveState.agents[a].status = "thinking"; liveState.agents[a].phase = d.phase || ""; liveState.agents[a].lastTs = ev.ts || Date.now() / 1000; }
      break;
    case "task_created":
      if (d.task_id) liveState.tasks[d.task_id] = { task: d.task, status: "pending", agent: a, sev: d.severity };
      if (a) { liveState.agents[a].status = "working"; liveState.agents[a].task = d.task || ""; }
      break;
    case "tool_call_start":
      if (a) { liveState.agents[a].status = "executing"; liveState.agents[a].tool = d.tool_name || ""; }
      break;
    case "execution_record":
      if (a) liveState.agents[a].status = "working";
      break;
    case "confidence_update":
      if (a && d.new_confidence != null) { liveState.agents[a].confidence = d.new_confidence; liveState.kpis.confidence = Math.max(liveState.kpis.confidence, d.new_confidence); }
      break;
    case "task_status_changed":
      if (d.task_id && liveState.tasks[d.task_id]) liveState.tasks[d.task_id].status = d.status;
      if (d.status === "completed") { liveState.kpis.tasksDone++; if (a) liveState.agents[a].status = "idle"; }
      break;
    case "validation_result":
      if (d.valid) { liveState.kpis.findings++; liveState.findings.unshift({ task: d.task, severity: d.severity || "medium", ts: ev.ts || Date.now() / 1000 }); }
      break;
    case "token_usage":
      if (d.total_tokens != null) liveState.kpis.tokens = d.total_tokens;
      if (d.cost_usd != null) liveState.kpis.cost = d.cost_usd;
      break;
    case "session_end":
      liveState.running = false;
      Object.values(liveState.agents).forEach((x) => (x.status = "idle"));
      break;
  }
}

const RIVER_ICON = {
  agent_start: "▶", agent_step: "▸", task_created: "✚", tool_call_start: "⚙",
  execution_record: "↻", confidence_update: "◈", task_status_changed: "✔",
  validation_result: "★", token_usage: "∑", session_end: "■", approval_required: "⚠",
};

function allAgentNames() {
  const set = new Set(KNOWN_AGENTS);
  Object.keys(liveState.agents).forEach((n) => set.add(n));
  return [...set];
}
function orbsHTML() {
  return allAgentNames().map((n) => {
    const st = (liveState.agents[n] && liveState.agents[n].status) || "idle";
    return `<div class="agent-orb status-${st}" id="orb-${cssId(n)}">
      <div class="orb-ring"><span class="orb-dot"></span></div>
      <div class="orb-name">${esc(n)}</div>
      <div class="orb-task" id="orbtask-${cssId(n)}"></div>
      <div class="orb-tool" id="orbtool-${cssId(n)}"></div>
    </div>`;
  }).join("");
}
function updateOrb(name) {
  const ag = liveState.agents[name]; if (!ag) return;
  const orb = document.getElementById("orb-" + cssId(name));
  if (!orb) return;
  orb.className = "agent-orb status-" + ag.status;
  const t = document.getElementById("orbtask-" + cssId(name));
  const tl = document.getElementById("orbtool-" + cssId(name));
  if (t) t.textContent = ag.task ? truncateStr(ag.task, 40) : "";
  if (tl) tl.textContent = ag.tool ? "⚙ " + ag.tool : "";
}
function updateKpis() {
  const k = liveState.kpis;
  setTxt("kpi-active", Object.values(liveState.agents).filter((x) => x.status !== "idle").length);
  setTxt("kpi-tasks", k.tasksDone);
  setTxt("kpi-find", k.findings);
  setTxt("kpi-conf", (k.confidence * 100).toFixed(0) + "%");
  setTxt("kpi-tok", (k.tokens || 0).toLocaleString());
  setTxt("kpi-cost", "$" + (k.cost || 0).toFixed(4));
  const st = document.getElementById("liveStatus");
  if (st) st.innerHTML = liveState.running ? `<span class="pill run">● LIVE</span>` : `<span class="pill idle">○ IDLE</span>`;
  const sess = document.getElementById("liveSession");
  if (sess) sess.textContent = liveState.sessionId ? "#" + String(liveState.sessionId).slice(0, 8) : "";
}
function prependRiver(ev, silent) {
  const river = document.getElementById("liveRiver"); if (!river) return;
  const line = document.createElement("div");
  line.className = "river-line type-" + ev.type;
  const d = ev.data || {};
  const label = d.task || d.agent_name || d.agent_id || d.tool_name || "";
  line.innerHTML = `<span class="river-ico">${RIVER_ICON[ev.type] || "•"}</span>` +
    `<span class="river-time">${fmtTime(ev.ts)}</span>` +
    `<span class="river-type">${esc(ev.type)}</span>` +
    `<span class="river-msg">${esc(String(label))}</span>`;
  river.prepend(line);
  while (river.children.length > 120) river.removeChild(river.lastChild);
}
function flashFinding(f) {
  const box = document.getElementById("liveFindings"); if (!box) return;
  const chip = document.createElement("div");
  chip.className = "finding-chip sev-" + (f.severity || "medium");
  chip.innerHTML = `<span class="fsev">${esc(f.severity || "medium")}</span><span class="fmsg">${esc(truncateStr(f.task || "finding", 64))}</span>`;
  box.prepend(chip);
  requestAnimationFrame(() => chip.classList.add("show"));
  while (box.children.length > 12) box.removeChild(box.lastChild);
  const c = document.getElementById("liveFindCount"); if (c) c.textContent = liveState.kpis.findings;
}

async function renderLive(view, params) {
  state.route = "live";
  let seed = KNOWN_AGENTS.slice();
  try {
    const r = await api("GET", "/api/agents/templates");
    seed = Array.from(new Set([...KNOWN_AGENTS, ...(r.agents || []).map((a) => a.name)]));
  } catch (_) {}
  seed.forEach((n) => { if (!liveState.agents[n]) liveState.agents[n] = { name: n, status: "idle", phase: "", task: "", tool: "", confidence: 0, lastTs: 0 }; });
  view.innerHTML = `
    <div class="live-wrap">
      <div class="live-head">
        <div class="live-title">⚡ 实时 Agent 作战台 <span class="live-session" id="liveSession"></span></div>
        <div class="live-status" id="liveStatus"></div>
      </div>
      <div class="live-kpis" id="liveKpis">
        ${["active", "tasks", "find", "conf", "tok", "cost"].map((k) => `<div class="kpi-card kpi-${k}"><div class="kpi-val" id="kpi-${k}">0</div><div class="kpi-label">${k === "active" ? "活跃智能体" : k === "tasks" ? "已完成任务" : k === "find" ? "命中发现" : k === "conf" ? "平均置信度" : k === "tok" ? "Token" : "成本"}</div></div>`).join("")}
      </div>
      <div class="live-grid">
        <div class="live-orbs" id="liveOrbs">${orbsHTML()}</div>
        <div class="live-side">
          <div class="panel-title">🎯 最新发现 <span class="badge ghost" id="liveFindCount">0</span></div>
          <div class="findings-ticker" id="liveFindings"></div>
          <div class="panel-title">🌊 事件流</div>
          <div class="event-river" id="liveRiver"></div>
        </div>
      </div>
    </div>`;
  paintLiveFull();
  liveState.events.slice(0, 60).reverse().forEach((ev) => prependRiver(ev, true));
  liveState.findings.slice(0, 12).forEach((f) => flashFinding(f));
}
function paintLiveFull() {
  allAgentNames().forEach(updateOrb);
  updateKpis();
}
function paintLiveEvent(ev) {
  const d = ev.data || {};
  const a = d.agent_name || d.agent_id || null;
  if (a) updateOrb(a);
  updateKpis();
  prependRiver(ev, false);
  if (ev.type === "validation_result" && d.valid) flashFinding({ task: d.task, severity: d.severity || "medium", ts: ev.ts || Date.now() / 1000 });
}

/* ===========================================================================
   Agents — view / edit prompt templates
   =========================================================================== */
async function renderAgents(view, params) {
  state.route = "agents";
  view.innerHTML = `<div class="section-head"><h2>⌬ Agent 管理</h2>
    <p class="muted">查看并编辑各智能体的系统提示词（<code>.jinja2</code> 模板）。保存将写回 pobi_prompts 模板文件，运行中的 agent 下次渲染即生效。</p></div>
    <div class="agent-grid" id="agentGrid"><div class="loading">加载中…</div></div>`;
  let list = [];
  try {
    const r = await api("GET", "/api/agents/templates");
    list = r.agents || [];
  } catch (e) {
    view.querySelector("#agentGrid").innerHTML = `<div class="err">加载失败: ${esc(e.message)}</div>`;
    return;
  }
  const grid = view.querySelector("#agentGrid");
  if (!list.length) { grid.innerHTML = `<div class="muted">未找到提示词模板。</div>`; return; }
  grid.innerHTML = list.map((a) => `<div class="agent-card">
     <div class="ac-name">${esc(a.name)}</div>
     <div class="ac-role">${esc(a.role || "")}</div>
     <div class="ac-desc">${esc(truncateStr(a.description || "", 100))}</div>
     <div class="ac-meta"><span class="badge ghost">${a.bytes}B</span><span class="badge ${a.writable ? "good" : "warn"}">${a.writable ? "可写" : "只读"}</span><span class="badge ghost">${a.override ? "override" : "package"}</span></div>
     <button class="btn" data-edit="${esc(a.name)}">编辑提示词 ✎</button>
   </div>`).join("");
  grid.querySelectorAll("[data-edit]").forEach((b) => (b.onclick = () => openPromptEditor(b.getAttribute("data-edit"), view)));
}
async function openPromptEditor(name, view) {
  let overlay = document.getElementById("promptOverlay");
  if (!overlay) { overlay = el("div", "overlay"); overlay.id = "promptOverlay"; document.body.appendChild(overlay); }
  overlay.innerHTML = `<div class="modal prompt-modal">
    <div class="modal-head"><span>✎ 编辑提示词 · ${esc(name)}</span><button class="x" id="promptClose">✕</button></div>
    <textarea class="code-editor" id="promptText" spellcheck="false">加载中…</textarea>
    <div class="modal-foot"><span class="hint" id="promptHint"></span><span class="spacer"></span>
      <button class="btn ghost" id="promptCancel">取消</button>
      <button class="btn primary" id="promptSave">保存并同步 ⤓</button></div>
  </div>`;
  overlay.classList.add("show");
  document.getElementById("promptClose").onclick = closePromptEditor;
  document.getElementById("promptCancel").onclick = closePromptEditor;
  try {
    const r = await api("GET", "/api/agents/templates/" + encodeURIComponent(name));
    document.getElementById("promptText").value = r.content;
    document.getElementById("promptHint").textContent = "路径: " + (r.path || "");
  } catch (e) {
    document.getElementById("promptText").value = "";
    document.getElementById("promptHint").textContent = "加载失败: " + e.message;
  }
  document.getElementById("promptSave").onclick = async () => {
    const content = document.getElementById("promptText").value;
    const btn = document.getElementById("promptSave"); btn.disabled = true; btn.textContent = "保存中…";
    try {
      const res = await api("PUT", "/api/agents/templates/" + encodeURIComponent(name), { content });
      document.getElementById("promptHint").textContent = "已同步 ✓ " + (res.path || "") + (res.stored === "override" ? " (override)" : "");
      toast("提示词已保存并同步到后端", "good");
    } catch (e) {
      document.getElementById("promptHint").textContent = "保存失败: " + e.message;
      toast("保存失败: " + e.message, "bad");
    } finally { btn.disabled = false; btn.textContent = "保存并同步 ⤓"; }
  };
}
function closePromptEditor() { const o = document.getElementById("promptOverlay"); if (o) o.classList.remove("show"); }

/* ===========================================================================
   Validation — strategy config (sync to backend YAML)
   =========================================================================== */
async function renderValidation(view, params) {
  state.route = "validation";
  view.innerHTML = `<div class="section-head"><h2>✓ 验证策略配置</h2>
    <p class="muted">定义「怎样算成功」的策略（flag / judge）。保存将写入 <code>~/.cache/pobi/validation.yaml</code>，运行时被后端加载 —— 即「同步到后端」。</p></div>
    <div class="val-wrap" id="valWrap"><div class="loading">加载中…</div></div>`;
  let cfg;
  try { cfg = await api("GET", "/api/validation-config"); }
  catch (e) { view.querySelector("#valWrap").innerHTML = `<div class="err">加载失败: ${esc(e.message)}</div>`; return; }
  const wrap = view.querySelector("#valWrap");
  wrap.innerHTML = `
    <div class="val-form">
      <div class="field"><label>validation_format</label><input id="valFmt" value="${esc(cfg.validation_format || "")}" placeholder="如 ###RESULT###... 或留空"></div>
      <div class="field"><label>validation_type</label><select id="valType"><option value="">（未指定）</option><option value="flag">flag</option><option value="judge">judge</option></select></div>
      <div class="strategies">
        <div class="strat-head"><span>策略列表</span><button class="btn ghost" id="addStrat">+ 添加策略</button></div>
        <div id="stratList"></div>
      </div>
      <div class="modal-foot"><span class="hint">保存后写入 validation.yaml（后端运行时加载）</span><span class="spacer"></span>
        <button class="btn ghost" id="valReset">重置默认</button>
        <button class="btn primary" id="valSave">保存并同步到后端 ⤓</button></div>
    </div>`;
  document.getElementById("valType").value = cfg.validation_type || "";
  const stratList = document.getElementById("stratList");
  function drawStrats() {
    stratList.innerHTML = (cfg.strategies || []).map((s, i) => {
      const name = s.name || "flag";
      return `<div class="strategy-row" data-i="${i}">
        <select class="sname"><option value="flag" ${name === "flag" ? "selected" : ""}>flag</option><option value="judge" ${name === "judge" ? "selected" : ""}>judge</option></select>
        <input class="spattern" placeholder="pattern（flag 用，正则）" value="${esc(s.pattern || "")}">
        <input class="stype" placeholder="validation_type" value="${esc(s.validation_type || "")}">
        <input class="sformat" placeholder="validation_format" value="${esc(s.validation_format || "")}">
        <button class="x" data-del="${i}">✕</button>
      </div>`;
    }).join("") || `<div class="muted">（暂无策略）</div>`;
    stratList.querySelectorAll("[data-del]").forEach((b) => (b.onclick = () => { cfg.strategies.splice(+b.getAttribute("data-del"), 1); drawStrats(); }));
  }
  drawStrats();
  document.getElementById("addStrat").onclick = () => { cfg.strategies.push({ name: "flag", pattern: "", validation_type: "", validation_format: "" }); drawStrats(); };
  document.getElementById("valReset").onclick = () => {
    cfg = { strategies: [{ name: "flag" }, { name: "judge" }], validation_format: null, validation_type: null };
    document.getElementById("valFmt").value = ""; document.getElementById("valType").value = ""; drawStrats();
  };
  document.getElementById("valSave").onclick = async () => {
    cfg.validation_format = document.getElementById("valFmt").value || null;
    cfg.validation_type = document.getElementById("valType").value || null;
    cfg.strategies = (cfg.strategies || []).map((s, i) => {
      const row = stratList.querySelector(`[data-i="${i}"]`); if (!row) return s;
      return { name: row.querySelector(".sname").value, pattern: row.querySelector(".spattern").value || null, validation_type: row.querySelector(".stype").value || null, validation_format: row.querySelector(".sformat").value || null };
    });
    const btn = document.getElementById("valSave"); btn.disabled = true; btn.textContent = "保存中…";
    try { await api("POST", "/api/validation-config", cfg); toast("验证策略已同步到后端 ✓", "good"); }
    catch (e) { toast("保存失败: " + e.message, "bad"); }
    finally { btn.disabled = false; btn.textContent = "保存并同步到后端 ⤓"; }
  };
}

/* ---------------- Scope (authorization gate) ---------------- */
async function renderScope(view, params) {
  state.route = "scope";
  view.innerHTML = `<h1 class="page">授权范围 (Scope)</h1>
    <p class="page-sub">配置授权范围。开启后，agent 的所有出网请求（HTTP / 浏览器）都会被强制校验，越界目标会被硬中止并记录到审计日志。关闭时网关为空操作，不影响现有流程。</p>
    <div class="grid">
      <div class="panel">
        <h2>范围授权设置</h2>
        <div class="row"><div class="field"><div class="k">启用范围授权</div><div class="h">开启后仅允许访问授权范围内的目标（默认关闭）</div></div>
          <div class="field"><label class="switch"><input type="checkbox" id="scEnabled"><span>启用（开启后仅允许访问授权范围内目标）</span></label></div></div>
        <div class="row"><div class="field"><div class="k">根域名（单）</div><div class="h">如 example.com，允许该域名及其所有子域名</div></div>
          <div class="field"><input type="text" id="scRootSingle" placeholder="example.com"></div></div>
        <div class="row"><div class="field"><div class="k">根域名列表</div><div class="h">每行一个，允许其所有子域名</div></div>
          <div class="field"><textarea id="scRootList" rows="3" placeholder="a.com&#10;b.com"></textarea></div></div>
        <div class="row"><div class="field"><div class="k">域名（单）</div><div class="h">精确匹配，不含子域名</div></div>
          <div class="field"><input type="text" id="scDomainSingle" placeholder="app.example.com"></div></div>
        <div class="row"><div class="field"><div class="k">域名列表</div><div class="h">每行一个，精确匹配</div></div>
          <div class="field"><textarea id="scDomainList" rows="3" placeholder="api.example.com&#10;admin.example.com"></textarea></div></div>
        <div class="row"><div class="field"><div class="k">IP 或 IP 列表</div><div class="h">支持单个 IP 或 CIDR，每行一个</div></div>
          <div class="field"><textarea id="scIps" rows="3" placeholder="10.0.0.5&#10;192.168.1.0/24"></textarea></div></div>
        <div class="row"><div class="field"><div class="k">排除列表 (out-of-scope)</div><div class="h">显式排除，优先级最高（域名 / IP / CIDR）</div></div>
          <div class="field"><textarea id="scExclude" rows="2" placeholder="intranet.example.com&#10;127.0.0.1"></textarea></div></div>
        <div class="row"><div class="field"><div class="k">速率上限 (max QPS)</div></div>
          <div class="field"><input type="number" id="scQps" min="1" value="10"></div></div>
        <div class="row"><div class="field"><div class="k">单次响应体积上限 (bytes)</div></div>
          <div class="field"><input type="number" id="scBytes" min="1024" value="5000000"></div></div>
        <div class="row-actions"><button class="btn primary" id="scSave">保存范围配置</button></div>
      </div>
      <div class="panel">
        <h2>规则测试</h2>
        <p class="muted" style="font-size:12.5px;margin-top:-6px;">保存前用样本目标验证匹配逻辑（排除优先、根域名含子域、域名精确、IP/CIDR 匹配）。</p>
        <div class="field"><input type="text" id="scTestTarget" placeholder="https://sub.example.com/path"></div>
        <button class="btn" id="scTest" style="margin-top:10px;">测试匹配</button>
        <div id="scTestResult" style="margin-top:12px;"></div>
      </div>
    </div>`;

  let cfg;
  try { cfg = await api("GET", "/api/scope-config"); }
  catch (e) { toast("加载范围配置失败: " + e.message, "bad"); cfg = {}; }
  cfg = cfg || {};
  document.getElementById("scEnabled").checked = !!cfg.enabled;
  document.getElementById("scQps").value = cfg.max_qps != null ? cfg.max_qps : 10;
  document.getElementById("scBytes").value = cfg.max_bytes != null ? cfg.max_bytes : 5000000;
  document.getElementById("scRootSingle").value = (cfg.root_domains && cfg.root_domains[0]) || "";
  document.getElementById("scRootList").value = ((cfg.root_domains || []).slice(1)).join("\n");
  document.getElementById("scDomainSingle").value = (cfg.domains && cfg.domains[0]) || "";
  document.getElementById("scDomainList").value = ((cfg.domains || []).slice(1)).join("\n");
  document.getElementById("scIps").value = (cfg.ips || []).join("\n");
  document.getElementById("scExclude").value = (cfg.out_of_scope || []).join("\n");

  const collect = (id) => document.getElementById(id).value.split(/\r?\n|,/).map((s) => s.trim()).filter(Boolean);
  const build = () => {
    const root = collect("scRootList");
    const rs = document.getElementById("scRootSingle").value.trim();
    if (rs && !root.includes(rs)) root.unshift(rs);
    const dom = collect("scDomainList");
    const ds = document.getElementById("scDomainSingle").value.trim();
    if (ds && !dom.includes(ds)) dom.unshift(ds);
    return {
      enabled: document.getElementById("scEnabled").checked,
      root_domains: root,
      domains: dom,
      ips: collect("scIps"),
      out_of_scope: collect("scExclude"),
      max_qps: parseInt(document.getElementById("scQps").value) || 10,
      max_bytes: parseInt(document.getElementById("scBytes").value) || 5000000,
    };
  };

  document.getElementById("scSave").onclick = async () => {
    const btn = document.getElementById("scSave"); btn.disabled = true; btn.textContent = "保存中…";
    try { await api("POST", "/api/scope-config", build()); toast("范围配置已保存 ✓", "good"); }
    catch (e) { toast("保存失败: " + e.message, "bad"); }
    finally { btn.disabled = false; btn.textContent = "保存范围配置"; }
  };

  document.getElementById("scTest").onclick = async () => {
    const target = document.getElementById("scTestTarget").value.trim();
    if (!target) { toast("请输入测试目标", "warn"); return; }
    const box = document.getElementById("scTestResult");
    box.innerHTML = `<div class="muted">测试中…</div>`;
    try {
      const r = await api("POST", "/api/scope-config/test", { ...build(), target });
      box.innerHTML = `<div class="finding-chip ${r.allowed ? "sev-low" : "sev-high"}">
        <span class="fsev">${r.allowed ? "ALLOW" : "BLOCK"}</span>
        <span class="fmsg">${esc(target)}</span>
        <span class="fconf">${esc(r.reason)}</span></div>`;
    } catch (e) { box.innerHTML = `<div class="err">测试失败: ${esc(e.message)}</div>`; }
  };
}

/* ---------------- Plan Mode ---------------- */
async function renderPlan(view, params) {
  state.route = "plan";
  let plan = null;

  const plans = await safe(() => api("GET", "/api/plans"), []);

  view.innerHTML = `<h1 class="page">作战计划 (Plan Mode)</h1>
    <p class="page-sub">在执行前审阅、修剪与批准任务树。审批后的计划即为执行时运行的任务树，可存为 JSON 复用。</p>
    <div class="grid" style="grid-template-columns: 300px 1fr; gap:16px; align-items:start">
      <div class="panel">
        <h2>已保存计划</h2>
        <div id="planList" class="plan-list"></div>
        <button class="btn" id="planNew" style="margin-top:10px;width:100%">＋ 从模板新建</button>
      </div>
      <div class="panel" id="editor">
        <p class="empty">从左侧选择计划，或点“从模板新建”生成草稿。</p>
      </div>
    </div>`;

  const listEl = document.getElementById("planList");
  const editorEl = document.getElementById("editor");

  function findNode(nodes, id) {
    for (const n of (nodes || [])) {
      if (n.id === id) return n;
      const f = findNode(n.children, id);
      if (f) return f;
    }
    return null;
  }

  function treeHTML(nodes) {
    if (!nodes || !nodes.length) return `<p class="muted" style="font-size:12px">（空）</p>`;
    return `<ul class="ptree">` + nodes.map((n) => {
      const st = n.status || "pending";
      const conf = Math.round((n.confidence_score != null ? n.confidence_score : 0.6) * 100);
      const pruned = st === "pruned";
      return `<li class="pnode ${pruned ? "pruned" : ""}">
        <div class="prow">
          <span class="ptask">${esc(n.task)}</span>
          <span class="pconf">${conf}%</span>
          <span class="tag ${st === "approved" ? "good" : st === "pruned" ? "bad" : ""}">${st}</span>
          <span class="pacts">
            <button class="btn ghost sm" data-act="approve" data-id="${esc(n.id)}">批准</button>
            <button class="btn ghost sm" data-act="prune" data-id="${esc(n.id)}">${pruned ? "恢复" : "修剪"}</button>
            <button class="btn ghost sm" data-act="edit" data-id="${esc(n.id)}">编辑</button>
            <button class="btn ghost sm" data-act="conf" data-id="${esc(n.id)}">置信</button>
            <button class="btn ghost sm" data-act="addchild" data-id="${esc(n.id)}">＋子</button>
          </span>
        </div>
        ${treeHTML(n.children)}
      </li>`;
    }).join("") + `</ul>`;
  }

  function renderList() {
    if (!plans.length) { listEl.innerHTML = `<p class="muted" style="font-size:12px">尚无保存的计划</p>`; return; }
    listEl.innerHTML = plans.map((p) => `
      <div class="plan-item ${plan && plan.plan_id === p.plan_id ? "sel" : ""}" data-id="${esc(p.plan_id)}">
        <div class="pn">${esc(p.name)}</div>
        <div class="pm">${esc(p.target || "")} · ${p.root_count} 根 · ${p.approved ? '<span class="tag good">已批准</span>' : '<span class="tag">草稿</span>'}</div>
      </div>`).join("");
    listEl.querySelectorAll(".plan-item").forEach((el) => el.onclick = async () => {
      try { plan = await api("GET", "/api/plans/" + el.dataset.id); renderEditor(); renderList(); }
      catch (e) { toast("加载计划失败: " + e.message, "bad"); }
    });
  }

  document.getElementById("planNew").onclick = async () => {
    const target = prompt("目标 URL（用于计划模板）", TARGET_DEFAULT);
    if (target === null) return;
    const promptText = prompt("计划提示词（描述目标 / 范围）", "Run a full autonomous penetration test.");
    try {
      plan = await api("POST", "/api/plans/generate", { target: target || "", prompt: promptText || "" });
      renderEditor(); renderList();
    } catch (e) { toast("生成草稿失败: " + e.message, "bad"); }
  };

  function renderEditor() {
    if (!plan) { editorEl.innerHTML = `<p class="empty">从左侧选择计划，或点“从模板新建”生成草稿。</p>`; return; }
    editorEl.innerHTML = `
      <div class="section-head">
        <h2 style="margin:0">编辑计划</h2>
        <span class="pill-row">
          ${plan.approved ? '<span class="tag good">已批准</span>' : '<span class="tag">草稿</span>'}
          <button class="btn primary" id="plSave">保存</button>
          <button class="btn" id="plApprove">批准计划</button>
          <button class="btn" id="plApply">应用到扫描 →</button>
          <button class="btn danger" id="plDelete">删除</button>
        </span>
      </div>
      <div class="row">
        <label class="field" style="flex:1"><span>计划名称</span><input id="plName" value="${esc(plan.name || "")}"></label>
        <label class="field" style="flex:1"><span>目标</span><input id="plTarget" class="mono" value="${esc(plan.target || "")}"></label>
      </div>
      <label class="field"><span>提示词</span><textarea id="plPrompt">${esc(plan.prompt || "")}</textarea></label>
      <div class="row-actions"><button class="btn" id="plAddRoot">＋ 添加根任务</button></div>
      <h3 style="margin:14px 0 6px">任务树</h3>
      <div id="plTree"></div>`;
    const treeEl = document.getElementById("plTree");
    const draw = () => { treeEl.innerHTML = treeHTML(plan.nodes || []); bindTree(); };
    function bindTree() {
      treeEl.querySelectorAll("button[data-act]").forEach((btn) => {
        btn.onclick = () => {
          const id = btn.dataset.id; const act = btn.dataset.act;
          const node = findNode(plan.nodes || [], id);
          if (!node) return;
          if (act === "approve") node.status = "approved";
          else if (act === "prune") node.status = node.status === "pruned" ? "pending" : "pruned";
          else if (act === "addchild") {
            node.children = node.children || [];
            node.children.push({ id: "node-" + Math.random().toString(16).slice(2, 8), task: "新子任务", status: "pending", confidence_score: 0.6, children: [] });
          }
          else if (act === "edit") { const v = prompt("编辑任务描述", node.task); if (v != null && v.trim()) node.task = v.trim(); }
          else if (act === "conf") { const v = prompt("置信度 0-1", String(node.confidence_score)); const f = parseFloat(v); if (!isNaN(f)) node.confidence_score = Math.max(0, Math.min(1, f)); }
          draw();
        };
      });
    }
    draw();
    document.getElementById("plAddRoot").onclick = () => {
      plan.nodes = plan.nodes || [];
      plan.nodes.push({ id: "node-" + Math.random().toString(16).slice(2, 8), task: "新根任务", status: "pending", confidence_score: 0.6, children: [] });
      draw();
    };
    document.getElementById("plSave").onclick = async () => {
      plan.name = document.getElementById("plName").value.trim() || "Untitled plan";
      plan.target = document.getElementById("plTarget").value.trim();
      plan.prompt = document.getElementById("plPrompt").value;
      const btn = document.getElementById("plSave"); btn.disabled = true; btn.textContent = "保存中…";
      try {
        const saved = await api("POST", "/api/plans", plan);
        plan = saved;
        const meta = { plan_id: saved.plan_id, name: saved.name, target: saved.target, approved: saved.approved, root_count: (saved.nodes || []).length, updated_at: saved.updated_at };
        const idx = plans.findIndex((p) => p.plan_id === saved.plan_id);
        if (idx >= 0) plans[idx] = meta; else plans.unshift(meta);
        toast("计划已保存 ✓", "good"); renderList();
      } catch (e) { toast("保存失败: " + e.message, "bad"); }
      finally { btn.disabled = false; btn.textContent = "保存"; }
    };
    document.getElementById("plApprove").onclick = async () => {
      try { const r = await api("POST", "/api/plans/" + plan.plan_id + "/approve"); plan = r; toast("计划已批准 ✓", "good"); renderList(); renderEditor(); }
      catch (e) { toast("批准失败: " + e.message, "bad"); }
    };
    document.getElementById("plDelete").onclick = async () => {
      if (!confirm("确认删除该计划？")) return;
      try { await api("DELETE", "/api/plans/" + plan.plan_id); plans = plans.filter((p) => p.plan_id !== plan.plan_id); plan = null; renderList(); renderEditor(); toast("已删除", "good"); }
      catch (e) { toast("删除失败: " + e.message, "bad"); }
    };
    document.getElementById("plApply").onclick = () => {
      location.hash = "#scan?plan=" + encodeURIComponent(plan.plan_id);
    };
  }

  renderList();
}
