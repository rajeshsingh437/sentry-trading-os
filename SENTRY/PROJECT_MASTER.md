# PROJECT_MASTER.md
### SENTRY — Trading Operating System (Python Rebuild)
*(Project renamed from "TOS Professional Edition" / "TOS v2" to **SENTRY** — it watches every fill, flags impulse trades, and guards discipline.)*

**Read this file FIRST, in every new session, before writing or changing anything.**

---

## 0. How To Use This File (for any AI agent — Claude, ChatGPT, Gemini)

1. Read this entire file before touching code.
2. Read `TLE_Trade_Object_and_Lifecycle_Specification_v1_1.md` — it is **FROZEN**. Do not add, remove, or redesign fields in it. If you think a change is needed, write it into `PROPOSED_CHANGES_v1.2.md` instead and keep building against v1.1.
3. Check the **Work Log** (Section 10) to see exactly what was last done and what's next.
4. **Plan First** — before writing/modifying code, write out your step-by-step plan in the chat, in plain English, for Rajesh to read. He has zero coding background — do not ask him to edit code by hand.
5. **Flag & Improve** — at every step, call out bugs, risks, over-trading triggers, or better approaches you notice in the current module.
6. **Full code blocks only** — never say "change line 42." Always give the complete, drop-in file.
7. **End every session** with exact terminal commands to commit to GitHub (template in Section 11).
8. Update the Work Log (Section 10) before ending the session, so the next AI/session can continue with zero re-explaining.
9. **Prefer command-line/terminal instructions over manual UI steps**, wherever a command-line equivalent exists — creating files, creating folders, editing config, git operations, installing packages/extensions, all go through the terminal. Reserve click-through UI steps only for actions with no CLI equivalent (e.g. installing VS Code/Python itself the first time, or GitHub website actions like creating a new empty repo).
10. **Every file's content is delivered as a single complete, copy-paste-ready code block** — never described in prose, never inline mid-sentence, and never as a partial diff.

---

## 1. Motto & Philosophy

**Motto:** *"Survive, Compound, and Stay Disciplined."*

This is not a P&L tracker. It is Rajesh's **second brain for disciplined execution** — a system that:
- Cannot be lied to (every trade is logged, planned or not).
- Makes impulse trades visible immediately, not at month-end.
- Separates **Process Score** from **Outcome Score** — a profitable impulsive trade is a bad trade; a disciplined loss is a good trade.
- Compounds capital in a risk-of-ruin-aware way, not a get-rich-quick way.

Core operating principles (carried over from TOS v1/v2, do not dilute):
- **Longevity First** — capital preservation beats any single trade.
- **Process Over Result** — the plan and its execution are graded independently of P&L.
- **Detach From Single Trades** — no single trade should be able to meaningfully hurt the account or the trader's head.
- **Focus on Horizons** — risk-adjusted compounding over years, not days.

---

## 2. User Profile & Non-Negotiable Constraints

- **User:** Rajesh — discretionary Nifty 50 options trader (buy-side CE/PE long setups), full-time trader, decade of technical skill, struggles specifically with **discipline in execution**, not analysis.
- **No programming background.** Every deliverable must be a complete file he can paste into VS Code and run — never a diff, never "add this line."
- **Budget: strictly free tools.** No paid APIs, no paid hosting, no paid libraries unless a free tier genuinely covers his usage.
- **Timeline:** 2 weeks for a working v1.
- **Distribution requirement (critical, sets the whole architecture):** the finished app must run as a **portable desktop app (.exe-style)** that works on *any* Windows laptop/PC he switches to — not tied to one machine, no server to maintain, no cloud dependency required to function day-to-day.
- **Broker:** Flattrade.
- Works across Claude, ChatGPT, and Gemini in different sessions — hence this file's existence.

---

## 3. Technology Stack Decision — and why

This is a **change from the earlier direction** on this project. Earlier sessions had started a browser-based "TOS Professional Edition" in React/TypeScript/Vite. **That direction is superseded by this document.** Reason for the flag: two live parallel builds (React/TS repo vs. this Python rebuild) will fragment effort and confuse future AI sessions — going forward, **this Python stack is the single source of truth** unless Rajesh explicitly says otherwise in an update to this file.

| Layer | Choice | Why |
|---|---|---|
| Language | **Python 3.11+** | Explicitly requested; huge free ecosystem; one language for UI glue, data, and broker API. |
| Desktop UI shell | **pywebview** | Renders HTML/CSS/JS (his existing TOS v2 dashboard) inside a native desktop window, backed by Python. This means the rich dashboard he already designed and iterated on is **reused, not rebuilt** — every panel/id in `TOS_v2_dashboard_12.html` becomes a view fed by Python instead of by browser-only JS/localStorage. |
| Local database | **SQLite** (via Python's built-in `sqlite3`) | Single file, zero server, travels with the app folder — matches the "any laptop" requirement. No cloud DB needed. |
| Packaging | **PyInstaller (`--onefile`)** | Produces a single `.exe` on Windows that bundles Python + all libraries. Copy the `.exe` + its data folder to a new laptop and it runs — nothing to install. |
| Broker integration | **Flattrade REST API** (official developer API, free) | Real username/password login into a broker platform is blocked by 2FA — not feasible or safe. Flattrade's API key + API secret flow is the correct "Tier 1" per the fallback plan below. |
| Version control | **GitHub** (free, private repo recommended) | Already Rajesh's stated workflow. |

**Flag for Rajesh:** pywebview + PyInstaller together is the most reliable free path to "one .exe that runs anywhere," but Windows Defender/SmartScreen sometimes flags unsigned PyInstaller executables on a new machine the first time. This is normal for indie/unsigned apps — click "More info → Run anyway." We are not going to pay for a code-signing certificate under the free-tools constraint; flagging this now so it isn't a surprise in week 2.

---

## 3.1 VS Code Environment Setup (do this once, before Phase 2)

Two real issues came up during Phase 1 setup — a stray `bash` command dropped Rajesh into WSL/Linux by accident, and every `git commit` printed CRLF/LF line-ending warnings. Both are fixed permanently by the workspace config below, committed once to the repo.

**Recommended extensions** — run in the VS Code terminal (PowerShell):

```bash
code --install-extension ms-python.python
code --install-extension ms-python.vscode-pylance
```

(If `code` isn't recognized, install manually instead: Extensions icon in the left sidebar → search "Python" by Microsoft → Install. Pylance installs automatically alongside it.)

**Workspace settings** — pins the terminal to PowerShell (prevents the accidental-bash issue) and points VS Code at the project's virtual environment automatically:

```bash
mkdir .vscode
@'
{
  "python.defaultInterpreterPath": "${workspaceFolder}/venv/Scripts/python.exe",
  "terminal.integrated.defaultProfile.windows": "PowerShell",
  "files.eol": "\n",
  "editor.formatOnSave": true,
  "files.autoSave": "onFocusChange"
}
'@ | Out-File -FilePath ".vscode\settings.json" -Encoding utf8
```

**Line-ending fix** — tells Git to normalize line endings consistently, so the CRLF/LF warning on every commit stops permanently:

```bash
@'
* text=auto eol=lf
'@ | Out-File -FilePath ".gitattributes" -Encoding utf8
```

**Commit both:**

```bash
git add .vscode .gitattributes
git commit -m "Add VS Code workspace settings and .gitattributes to fix terminal/line-ending issues"
git push
```

**One habit going forward:** if a VS Code terminal tab ever shows a shell name other than `powershell` in the small dropdown (top-right of the terminal panel, e.g. it says `bash` or `wsl` or `Ubuntu`), close that tab and open a fresh terminal — don't type commands into it.

---

## 4. Broker Integration Strategy (3-Tier, per Project Goal doc)

### Tier 1 — Flattrade REST API (build this first)
- Rajesh generates an **API Key + API Secret** from Flattrade's developer portal (not his login password).
- Python backend polls positions/order book on an interval and cross-checks every filled order against that day's **pre-approved Trade Plans** (Section 5 below).
- Any fill with no matching Trade Plan → immediate high-priority alert:
  **"UNPLANNED IMPULSE TRADE DETECTED: SURVIVE & STAY DISCIPLINED."**
- This is the guardrail Rajesh cannot talk himself out of — it's automatic, not something he has to remember to check.

### Tier 2 — Contract Note / Trade-History CSV upload (fallback, build second)
- If live polling has issues on a given day, Rajesh drops the day's contract note (PDF) or trade-history CSV into an `uploads/` folder.
- App parses it, fills in trades + exact brokerage/taxes/net P&L, and still cross-checks timestamps against pre-planned setups. Post-trade rather than real-time, but still can't hide a mistake.

### Tier 3 — Auto-email reader (later, optional)
- A background script checks an isolated inbox for Flattrade's official trade-execution alert emails and updates the journal near-real-time without manual work.

**Build order:** Tier 2 (CSV/contract-note parser) is actually the fastest to get *something* real flowing into the journal in week 1, even before the live API polling is fully wired — recommend building Tier 2 first as the reliability floor, then layering Tier 1 on top. Flag this as a sequencing improvement over the doc's stated order.

---

## 5. Data Model — The Trade Object

**Do not restate or redesign this here.** The single source of truth is:
`TLE_Trade_Object_and_Lifecycle_Specification_v1_1.md` — **Status: FROZEN v1.1**

Every AI session must implement against that file exactly as written:
- 11 sections: Identity, Instrument, Planning, Readiness, Execution, Trade Management, Exit, Review, Psychology, Learning, Attachments.
- Full lifecycle: `Draft → Planned → Ready → Triggered → (Invalidated | Skipped | Active) → Scaling → Completed → AwaitingReview → Reviewed → Archived.`
- Two independent scores per trade: **Process Score** (0–100, from Review section) and **Outcome Score** (P&L, R-Multiple, Return %, Win/Loss/Breakeven).
- Cross-section validation rules (Section "Cross-Section Validation" in the TLE doc) must be enforced in code before any lifecycle transition, not just at final save.

**Storage approach (revised in Phase 2 — see Work Log for the reasoning):** two layers, not one.

- **Layer A — generic key/value store (built in Phase 2):** the dashboard already manages its own state through ~15 separate localStorage keys (journal, trade plans, checklists, capital plan, filters, factors, etc.). Rather than rebuild all of that against a rigid schema, `storage.py` gives every localStorage key a permanent row in a SQLite `kv_store` table (`key`, `value` as JSON text, `updated_at`). A small patch at the top of `dashboard/index.html`'s `<head>` mirrors every `localStorage.setItem`/`removeItem` call into this table via the Python bridge, and a new `dashboard/boot.html` hydrates localStorage from it on startup before the real dashboard loads. This is zero-risk to the existing 5000+ lines of dashboard logic and immediately solves the "survives a laptop switch" requirement for the *entire* app, not just trades.
- **Layer B — structured `trades` table (planned for Phase 3):** once the Trade Journal is wired up directly, trade records get *additionally* parsed out of the journal's JSON blob into their own table with real columns (`trade_id`, `status`, `symbol`, `realised_pnl`, `process_score`, etc.) matching the frozen TLE spec, so Analytics, the Edge Drift Monitor, and the Rule Engine can query fast instead of parsing JSON blobs at runtime. Layer A remains the source of truth for everything else.

---

## 6. UI Migration Map — TOS v2 HTML → Python-backed Desktop App

`TOS_v2_dashboard_12.html` is **not thrown away** — its 11 views become the 11 views of the new app, now reading/writing real data through Python instead of only browser localStorage. Nothing in this list gets dropped:

| Existing view (`id=`) | Becomes | Data source |
|---|---|---|
| `view-home` | Home / Pre-Market Regime, Mission Principles, Today's Readiness, Equity Curve, Alerts, Calendar Heatmap, EOD checklist | Live from `trades` table + market snapshot |
| `view-decision` | GO/NO-GO Decision Engine, A+ Setup Reference, Trade Plan Capture | Readiness checklist engine (TLE Section 4) |
| `view-risk` | Position Size Calculator, Loss-Streak Breaker, Drawdown Limits, Capital Build-up Plans, Risk-of-Ruin estimate | Capital plan module ([[capital-planning]] "Bold Guarded" preset: ~3% risk/trade, 1% floor after losses/drawdown) |
| `view-journal` | Log a Trade (full journal form, scale-out legs, MAE/MFE, screenshots) | `trades` table, Execution/Exit/Trade Management sections |
| `view-session` | Pre-Open Checklist, Hourly Check-In, Cost of Mistakes Log | New `session_checkins` + `cost_log` tables |
| `view-analytics` | Advanced metrics (Sharpe, Sortino, SQN, Profit Factor, Expectancy), R-distribution, breakdowns by strategy/emotion/day/time/setup/market/readiness, Edge Drift Monitor, Process Adherence Trend, Focus & Distraction, Cost of Mistakes analytics | Computed from `trades` + `session_checkins` + `cost_log` |
| `view-psychology` | Psychology Score, Emotion Frequency, Performance Bell Curve (A/B/C game), Mood/Confidence/Process-Adherence over time, A/B/C Game Self-Check | TLE Section 9 (Psychology) per trade + daily self-check table |
| `view-discipline` | If-Then Implementation Intentions, 60-Second Reset (box breathing), Daily Discipline Log, Weekly Accountability Review | New `if_then_rules`, `discipline_log`, `weekly_review` tables |
| `view-news` | Market Ticker, Regime Score Inputs, Upcoming Events, Live News Feed, Curated Reference Notes | Free market-data source (see Section 7 flag) |
| `view-reports` | Generate/print report (PDF via browser print) | pywebview supports print-to-PDF; keep this mechanism |
| `view-rulebook` | Core Principles, Risk Rules, Color System, Phase Roadmap, Daily Workflow, Rule Engine (auto-enforced) | Rule Engine reads `trades` + capital plan live, same as before |

**Flag for Rajesh:** the old dashboard used `localStorage` for persistence, which is browser-only and not portable. The Python rebuild's whole point is to replace that with SQLite so your data survives a laptop change — this is a real upgrade, not just a re-skin.

---

## 7. Free Market-Data Flag

`view-news`/`view-home` previously auto-fetched VIX/USD-INR/Crude. Under the strict free-tools constraint, we need a genuinely free, no-key-required (or free-tier-with-signup) data source for these — this has to be evaluated and picked in Phase 6, not assumed. Flagging now so it isn't a silent gap: worst case, this panel falls back to Rajesh's manual entry (the dashboard already has an "Enter manually" mode — keep that as the guaranteed-working path).

---

## 8. Module Roadmap

- **Module 1: Trade Journal & Broker Integration** *(current focus)*
- **Module 2: Pre-Trade Plan Checker & Guardrails** (Readiness/Decision Engine, Capital Plan, Rule Engine)
- **Module 3: Behavioral Analysis & Impulse Red-Flag Engine** (Psychology, Discipline, Cost-of-Mistakes)
- **Module 4: Analytics & Equity Curve Dashboard**
- **Module 5: Packaging & Distribution** (PyInstaller `.exe`, portable data folder)

---

## 9. Step-by-Step Build SOP (phase order for any AI session to follow)

> Each phase below ends with: working code delivered as full files, a plain-English explanation of what it does, and GitHub commit instructions. No phase should require Rajesh to hand-edit code.

**Phase 0 — Environment Setup**
Install Python 3.11+, VS Code, Git. Create project folder + GitHub repo. Give Rajesh the exact `pip install` command block for all dependencies used in Phase 1 (pywebview first; add others as each phase needs them).

**Phase 1 — Skeleton App**
A minimal pywebview window that loads a copy of `TOS_v2_dashboard_12.html` from disk, with a tiny Python `Api` class exposed to JS (pywebview's `js_api` bridge) proving two-way communication (e.g. Python returns "Hello from Python" into a dashboard field). Confirms the whole shell works before any real logic goes in.

**Phase 2 — Durable Storage Layer (DONE — see Work Log)**
Generic key/value SQLite store (`storage.py`, `kv_store` table) mirroring every localStorage key the dashboard already uses, via a small persistence patch in `dashboard/index.html`'s `<head>` and a new `dashboard/boot.html` that hydrates localStorage from SQLite on startup. Zero changes to existing dashboard logic. Solves cross-machine durability for the whole app immediately. Structured `trades` table (Layer B, Section 5) deferred into Phase 3 alongside Journal wiring, where it's needed anyway.

**Phase 3 — Structured Trades Table (DONE — see Work Log)**
The dashboard's existing "Log a Trade" form already worked and already got durably saved by Phase 2 (it writes to localStorage key `tos_journal_trades_v2`, one of the keys Phase 2 mirrors). What Phase 3 added: every time that key is saved, `storage.py` also parses the JSON array into a proper structured `trades` SQL table (real columns: date, instrument, pnl, r_multiple, result, etc.) plus a `get_trade_stats()` function (win rate, expectancy, profit factor, avg R) exposed to JS as `Api.get_trade_stats()`. No dashboard HTML/JS was touched — this is a pure Python-side addition. Sets up fast querying for Analytics/Edge Drift Monitor/Rule Engine in later phases.

**Phase 4 — Broker Integration Tier 2 (contract-note/CSV parser)**
Parse Flattrade's exported trade history/contract note into Trade Objects (fills into Execution/Exit), matched against that day's Trade Plans. This is the reliability floor per Section 4.

**Phase 5 — Broker Integration Tier 1 (live Flattrade API polling)**
Poll positions/orders on an interval; raise the impulse-trade alert the moment an unplanned fill appears.

**Phase 6 — Decision Engine, Risk Engine, Capital Plan**
Port the ten-item weighted Readiness checklist, Position Size Calculator, Loss-Streak Breaker, Drawdown Limits, and the "Bold Guarded" capital build-up plan (~3% risk/trade, 1% floor after losses/drawdown from peak equity) into live Python logic feeding `view-decision`/`view-risk`.

**Phase 7 — Rule Engine & Discipline Module**
Auto-enforced rules (news-day mode, loss-streak stop, etc.), If-Then implementation intentions, Daily Discipline Log, Weekly Accountability Review, 60-second box-breathing reset.

**Phase 8 — Psychology Module**
Per-trade Psychology fields (TLE Section 9), daily A/B/C Game Self-Check, Psychology Score, mood/confidence/process trend charts.

**Phase 9 — Analytics Suite**
Sharpe/Sortino/SQN/Profit Factor/Expectancy, all the breakdown panels, Edge Drift Monitor, Process Adherence Trend, Cost-of-Mistakes analytics.

**Phase 10 — Reports**
Print/Save-as-PDF report generation (reuse pywebview's print capability).

**Phase 11 — Packaging**
PyInstaller `--onefile` build; verify the resulting `.exe` + data folder runs correctly when copied to a *different* machine (this is the actual acceptance test for the "any laptop" requirement — not just "it built without errors").

**Phase 12 — Handoff Documentation**
A short "how to move to a new laptop" note (copy folder, run exe, data comes with it) and a "how to back up your data" note (the SQLite file + attachments folder).

---

## 10. Work Log (update this every session — most recent entry on top)

> Format: Date · What was done · What's next · Anything flagged

- **[Insert Date]** · **Extended the risk % warning to Trade Plan Capture.** Added a Qty (lots) field to the Trade Plan form (it didn't have one before), and the same live risk banner now appears there too — identical thresholds and colours as the Journal, so a plan gets flagged *before* the trade is even taken, not just after. Refactored the risk-banner logic into one shared function (`renderRiskBanner`) used by both forms, so the two can never drift out of sync. Plan's `qty` is now saved with the plan and carried through automatically when "Send to Journal" is used (the Journal's Qty field and risk banner both populate from the plan). Open Plans list now also shows Qty. Removed a leftover duplicate `journalLotSize()` function from the previous edit in the same session. Verified with `node --check` — no syntax errors — before handoff. · **Flagged (carried over):** parallel React/TS repo should be paused/archived; free market-data source for VIX/USD-INR/Crude not yet chosen (Section 7); PyInstaller SmartScreen warning expected at Phase 11, not a bug.

- **[Insert Date]** · **Phase 3 built: structured trades table.** Extended `storage.py` with a `trades` SQL table (real columns: date, instrument, strike, entry/exit/stop/target, pnl, r_multiple, result, confidence, emotion, tags, etc.) that auto-rebuilds every time the journal (`tos_journal_trades_v2`) is saved — hooked directly into the existing `set_item`/`remove_item` functions from Phase 2, so no dashboard HTML/JS changes were needed at all. Added `get_trade_stats()` (win rate, expectancy, profit factor, avg R) and exposed it as `Api.get_trade_stats()` in `main.py`, ready for Analytics to call directly in a later phase instead of parsing JSON. Verified end-to-end in a standalone test before handoff (two sample trades in → both `kv_store` and `trades` table populated correctly, stats computed correctly: 50% win rate, +0.42R expectancy, 2.67 profit factor). **Also confirmed:** because the journal was already one of the Phase 2 mirrored keys, real trades logged through the existing "Log a Trade" form were *already* durably saved and *already* feeding the Home Dashboard KPI cards before this phase started — Phase 3 only added the structured-table layer underneath, nothing user-facing changed. **Verified working by Rajesh:** logged 6 real trades, dashboard and journal table both reflecting them correctly. · **Flagged (carried over):** parallel React/TS repo should be paused/archived; free market-data source for VIX/USD-INR/Crude not yet chosen (Section 7); PyInstaller SmartScreen warning expected at Phase 11, not a bug.
- **[Insert Date]** · Project Master file created; Python + pywebview + SQLite + PyInstaller stack decided; Flattrade confirmed as broker; earlier React/TS "TOS Professional Edition" direction superseded by this document · **Next:** Phase 0 (environment setup) and Phase 1 (skeleton pywebview app) · **Flagged:** parallel React/TS repo exists and should be paused/archived to avoid split effort; free market-data source for VIX/USD-INR/Crude not yet chosen (Section 7).

---

## 11. Session-End GitHub Commit Template

Every AI session ends with this block, filled in with the actual files touched:

```bash
cd path/to/your/project-folder
git add .
git commit -m "Phase X: <one-line description of what changed>"
git push
```

If this is the very first commit of the whole project:

```bash
cd path/to/your/project-folder
git init
git add .
git commit -m "Initial commit: PROJECT_MASTER.md and TLE spec"
git branch -M main
git remote add origin https://github.com/<your-username>/<repo-name>.git
git push -u origin main
```

---

## 12. Freeze Rules (inherited from the TLE spec — apply project-wide)

- `TLE_Trade_Object_and_Lifecycle_Specification_v1_1.md` is FROZEN. No additions, deletions, or redesign during implementation.
- This `PROJECT_MASTER.md` file, by contrast, is a **living document** — update the Work Log and any decision sections every session so the philosophy and status stay current for whichever AI opens it next.
- Any proposed change to the Trade Object spec goes into a separate `PROPOSED_CHANGES_v1.2.md`, discussed only after the current implementation milestone is complete.
