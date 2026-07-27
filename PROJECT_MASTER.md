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

**Storage approach:** store each Trade Object as a structured JSON document in a SQLite `trades` table (one row per Trade ID, JSON column for the full object, plus a handful of indexed columns — `trade_id`, `status`, `created_date`, `symbol`, `strategy`, `realised_pnl`, `process_score` — pulled out for fast filtering/analytics). This avoids fighting a rigid relational schema against a spec with nested arrays (checklist items, execution legs, lifecycle history), while still keeping the fields Analytics needs to slice fast as real columns.

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

**Phase 2 — Database Layer**
SQLite schema implementing the Trade Object (Section 5 above), created via a Python setup script. Include a small set of sample/dummy trades so later phases (Analytics, Journal) have something to render against immediately.

**Phase 3 — Trade Journal (manual entry first)**
Wire `view-journal`'s form to Python: save a Trade Object to SQLite through its lifecycle stages, enforcing the TLE cross-section validation rules before allowing a transition.

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

- **[Insert Date]** · Project renamed to **SENTRY**. Phase 0 (setup instructions) and Phase 1 (pywebview skeleton — `main.py`, `requirements.txt`, `dashboard/index.html`, `README_SETUP.md`) delivered as a ready-to-run folder · **Next:** Rajesh runs Phase 1 locally and confirms the window title changes to "SENTRY — Hello from Python — bridge is working!" then commits to GitHub per `README_SETUP.md`. Once confirmed, move to **Phase 2 — Database Layer** (SQLite schema for the Trade Object). · **Flagged:** parallel React/TS repo exists and should be paused/archived to avoid split effort; free market-data source for VIX/USD-INR/Crude not yet chosen (Section 7); PyInstaller packaging (Phase 11) may trigger a Windows SmartScreen warning on first run on a new machine — expected, not a bug, see Section 3.
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
