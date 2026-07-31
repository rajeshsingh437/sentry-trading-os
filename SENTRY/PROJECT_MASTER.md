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
11. **Any new feature idea gets weighed against the long-term goal before being built** — briefly state what it costs (build time, complexity, risk to existing logic) versus what it adds toward disciplined, risk-adjusted compounding, then keep or discard. Section 13 is a large backlog by design — it is not a queue to build in one pass; each item gets this evaluation when its turn comes up.

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
- **Zoom Out On Every Slip** — any mistake, tilt, or bad session gets reframed on a *minimum weekly* basis, not a single-trade basis. One trade never carries the weight of the whole story — survival and process do. This applies to how the app talks to Rajesh, and how any AI session talks to him too.

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

**Open tension — partially resolved, see below:** his later notes said "auto broker integration at the last stage." A follow-up made the actual intent much clearer: Rajesh does **not** want cloud/algo-style execution (no static IP, no auto-trading) — he wants a **local integration to an existing trading terminal already running on his machine**, reading trade book, order book, ticker, and (importantly) VIX/symbol data directly from it, in real time. This resolves *why* the earlier "last stage" phrasing was there — it was ruling out cloud/algo automation, not ruling out the local read-only guardrail Tier 1 was always meant to be. **Still open:** exactly *which* local terminal/mechanism (see clarifying questions logged in the Work Log — answers pending as of this note). Once that's answered, Tier 1 gets rewritten around whatever that local integration actually is, rather than assumed to be Flattrade's cloud REST API as originally drafted above.

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

## 7. Free Market-Data Flag — Partially Resolved

`view-news`/`view-home` previously auto-fetched VIX/USD-INR/Crude via a free proxy that was already failing in testing (see Phase 1 Work Log). Rajesh has since clarified: **VIX and symbol data should come from his local trading terminal** (same source as trade/order book, see Section 4/13.13) rather than an external API — that resolves VIX once terminal integration exists. **News stays external, by his explicit instruction** — needs its own free source, still to be picked. USD-INR/Crude weren't mentioned in the terminal-integration note — unclear if the local terminal covers those too, or if they still need a separate free external source. Confirm alongside the terminal-integration questions. Worst-case fallback either way: the dashboard's existing "Enter manually" mode.

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

- **[Insert Date]** · **Major tag system rebuild, driven by `#TAGS.txt` — read fully before any changes, per Rajesh's instruction.** (1) **New standalone file `TAG_SYSTEM_AND_REFERENCES.md`** — self-contained, shareable: the tag naming convention (scored `CODE-DIM-SCORE`, glossary `#CODE-G`, plain `#CODE`), the full ABC scoring/promotion/demotion rules (1–10 ratings, monthly + weekly rolling windows, sticky C-Game rule for FOL/LPT/Trading Bias), Claude's requested input on automating tags (keyword search, tag-to-rule association, weekly/monthly dashboards, auto-suggested tags), and the trading/psychology reference reading list (Al Brooks, Kahneman, Annie Duke, etc.) as the standing base for all coaching in this project. (2) **Tag input now supports the real convention**: `CODE` (default mapping), `CODE-A/B/C` (force a bucket), and `CODE-T-N`/`CODE-M-N` (scored, N=1–10, dimension T=Tactical/M=Mental) — verified against Rajesh's actual examples (FOL-T-10, Bias-T-8, SM-M-3, etc.) with a standalone Node dry-run before shipping. **Explicitly NOT built yet**: the full monthly/weekly rolling promotion/demotion engine from the rules — that needs real historical windows and more design clarity (open questions listed in the new reference file); what's built instead is a clearly-flagged provisional per-entry bucket estimate (score ≥7/4-6/≤3 mapped to C/B/A or A/B/C depending on the tag's polarity). Added a `polarity` field per tag (negative/positive, editable in Manage Tags) so scored entries land in a sane bucket — a high score on a positive tag like SOH should mean A-Game, not C. (3) **UI consolidation, per direct feedback**: removed the standalone floating Tag/Notes circular buttons entirely — both now live as buttons *inside* the nav sidebar (`.nav-tool-btn`, bottom section), so they respect the sidebar's own pin/auto-hide state instead of floating independently. Popovers still render as fixed-position panels (so they can escape the narrow collapsed rail) but now position dynamically via `getBoundingClientRect()` on whichever button opened them, rather than hardcoded coordinates. (4) **Sidebar smoothness fix**: collapsed width increased 56px→64px, transition duration increased with icon-specific sizing (16px→20px when collapsed) so the rail doesn't look cramped, added missing `transition` on the hover-expand state (previously snapped instantly, now animates). (5) **Notes widget restored as a plain scratchpad** — no tag parsing in it anymore (confirmed: "Tags will sit within the Tag widget only," per TAGS.txt) — just autosaving freeform text. (6) **ABC display correction** (from the immediately preceding session) carried forward unchanged — tags still land directly inside the real Mental/Tactical C/B/A columns, not a separate panel. Verified with `node --check` and a standalone regex dry-run against real TAGS.txt examples before handoff. **Next:** Rajesh tests the new Tag/Notes button placement and the scored-tag entry format; decide whether to prioritize the full rolling-window ABC engine next, or continue toward broker/terminal integration (still pending — Amibroker Python app mentioned but not yet shared). · **Flagged (carried over):** parallel React/TS repo should be paused/archived; news needs its own free external source (Section 7); PyInstaller SmartScreen warning expected at Phase 11.

- **[Insert Date]** · **Corrected ABC display placement — take 2, now integrated directly into the real grid.** Rajesh clarified the previous "Tag-Driven ABC Today" panel wasn't what he wanted: he wants live tags landing directly inside the actual Mental/Tactical C/B/A columns of the A/B/C Game Self-Check grid itself (the same 6-column layout already there), not a separate summary list. Removed that panel entirely (HTML, `renderTagAbcSummary()`, and its call). Instead, `renderAbcColumn()` now appends a small blank area at the bottom of each of the 6 columns that fills in real time with short-form entries (`HH:MM CODE`, e.g. `14:34 FOL`) as matching tags get logged — each entry lands in the exact column matching its dim+bucket. Added raw `abcDim`/`abcBucket` fields to each live-tag record (`commitTagLog`) so column-matching is exact, not string-parsed from the display label. This is a strict correction of last session's build, not an addition — the grid Rajesh referenced in his screenshot is now the single place ABC-tag activity shows up, alongside the pre-defined checklist items it's sitting next to. Verified with `node --check`. · **Flagged (carried over):** broker/terminal integration research still pending (Flattrade local option unconfirmed, Amibroker OLE/COM looks promising) — Rajesh mentioned a Python application related to his Amibroker setup he'll share next session; parallel React/TS repo should be paused/archived; news needs its own free external source (Section 7); PyInstaller SmartScreen warning expected at Phase 11, not a bug.

- **[Insert Date]** · **Moved ABC display to the right place.** Removed the ABC column from the Live Tag Log table (Session Checklists) — it was cluttering a table that isn't really about ABC. Added a new "Tag-Driven ABC Today" panel in the Psychology view, positioned directly below the Bell Curve (matching where the real A/B/C Game Self-Check reference already lives) — shows today's ABC-mapped tags with their bucket badges, so it's visible right next to the actual verdict/bell curve it's feeding, not buried in an unrelated table. Live Tag Log now shows Time/Tag/Note only. Verified with `node --check`. **Broker/terminal integration:** confirmed both Flattrade (trade book, order book, ticker) and Amibroker (VIX, symbol data) are in scope, different data from each — Rajesh doesn't know the technical integration path, so this needs research before any code, not a guess. Initial research done: Amibroker has a mature, well-documented OLE/COM automation interface (`Broker.Application` object) that's been used from Python via `pywin32`/`win32com` for years — reading quotes, symbol data, and (per its object model) potentially real-time data access; this looks like a strong, low-risk path for the Amibroker half. Flattrade's side still needs research (likely a cloud REST API per their developer docs, per the original Tier 1/2 plan in Section 4 — needs re-confirming whether they also expose anything locally). **Next session should continue this research** before writing any broker/terminal code. · **Flagged (carried over):** parallel React/TS repo should be paused/archived; news needs its own free external source (Section 7); PyInstaller SmartScreen warning expected at Phase 11, not a bug.

- **[Insert Date]** · **Built: collapsible/pinnable sidebar + Quick Notes hashtag capture.** (1) Sidebar now has a "📌 Pin sidebar" button at the bottom — pinned (default) keeps it always visible as before; unpinned collapses it to a 56px icon-only rail that expands on hover and overlays content rather than pushing it (Amibroker-style), matching Rajesh's reference screenshot. Preference persists (`tos_nav_pinned_v1`). (2) New "📝 Quick Notes" floating panel next to the tag button — a free-typing notepad where `#CODE` logs a tag using its own default ABC mapping, and `#CODE-A`/`#CODE-B`/`#CODE-C` forces that tag into a specific bucket for just that entry, exactly as requested. Parsing happens per-line the instant Enter is pressed (never rescans older lines, so editing earlier text can't accidentally re-log something). Refactored tag-logging into a shared `commitTagLog()` function so the popover buttons and the hashtag parser can never drift into two different behaviors. Content persists (`tos_quick_notes_v1`). **One judgment call flagged in the code:** forcing a bucket on a tag with no default ABC dimension (e.g. `#TTR-C`) defaults the dimension to 'tactical' since that's what most of Rajesh's original graded mistakes were — confirm if that default is wrong. Verified with `node --check` — no syntax errors. **Not addressed this session:** broker/local-terminal integration — see clarifying questions asked separately before any code gets written there, per Section 0 Rule 11 (this is a real architecture decision, not a guess-and-fix like the UI pieces above). · **Flagged (carried over):** parallel React/TS repo should be paused/archived; free market-data source for VIX/USD-INR/Crude superseded by Rajesh's local-terminal request — see Section 4/13.13 updates; PyInstaller SmartScreen warning expected at Phase 11, not a bug.

- **[Insert Date]** · **Section 13.2 upgraded to v2: editable tags + ABC Game auto-mapping.** Converted the fixed 7-tag list into a persisted, fully editable list (`tos_tag_defs_v1`) — new "+ Add / manage tags" link in the popover lets Rajesh add brand-new tags (code, label, nudge, optional ABC mapping) or delete any tag including the original 7. Core piece: tags can now carry an optional Mental/Tactical + A/B/C mapping, and logging a mapped tag pushes a synthetic entry into the *same* `state.abcChecked` array the manual A/B/C Game Self-Check grid already uses — confirmed by reading the existing code that `computeAbcVerdict()`, `computePsychologyScore()` (uses abcAdjust: -15 for C-game, +10 for A-game), `renderAlerts()`, and the bell curve (`state.abcHistory`) all already key off `state.abcChecked`, so this was reuse, not new parallel logic. Verified all four hooked-into function names exist in the file before wiring. Seeded a best-guess ABC mapping for the 4 behavioral tags (FOL/SM/LPT → C-game, SOH → A-game) matched against the closest existing checklist item text; left TTR/NTD/PA Exit unmapped since they're context/method, not behavior. Flagged clearly in 13.2 that the mapping is my judgment call, not something Rajesh stated — easy to change in-app. Live Tag Log table gained an ABC column. Verified with `node --check` — no syntax errors — before handoff. **Next:** Rajesh tests logging a mapped tag (e.g. FOL) and checks that Psychology view's verdict/score and the bell curve actually move — that's the real proof this works end to end. · **Flagged (carried over):** parallel React/TS repo should be paused/archived; free market-data source for VIX/USD-INR/Crude not yet chosen (Section 7); PyInstaller SmartScreen warning expected at Phase 11, not a bug; broker-integration sequencing tension (Section 4) still needs a direct conversation; "jump back into a trade after a break" leak point still has no tag name.

- **[Insert Date]** · **Built Section 13.2 v1: real-time tag system.** Added a floating "+" quick-tag button (bottom-left, fixed position, visible on every view — not buried in one screen, matching how it'd actually get used during a live session) that opens a popover with one-tap buttons for FOL, SM, TTR, NTD, SOH, LPT, and PA Exit. Tapping a tag logs it with a timestamp and an optional note, then shows a dismissible nudge box with that specific tag's corrective reminder (7-second auto-dismiss or manual close) — each tag has its own message, not a generic one. Added a "Live Tag Log" panel to Session Checklists showing today's entries with delete capability. Followed the exact same architectural pattern as the existing Cost of Mistakes Log (KEY constant, save/load/render functions) for consistency — `localStorage` key `tos_live_tags_v1`, durable automatically via Phase 2's persistence patch, no Python/storage.py changes needed. Nudge wording for all 7 tags is AI-drafted from `TAGS_GLOSSARY.md`'s definitions — flagged in Section 13.2 that this should get a look and possible rewrite in Rajesh's own voice. **Not built yet:** feeding tag history into a bell-curve/psychology score (deliberately deferred — that's Analytics-phase work, not v1). Verified with `node --check` — no syntax errors — before handoff. **Next:** Rajesh tests it live, decides if the 7-tag set and nudge wording feel right, or if the "jump back into a trade after a break" leak point (still unnamed) should get its own tag added. · **Flagged (carried over):** parallel React/TS repo should be paused/archived; free market-data source for VIX/USD-INR/Crude not yet chosen (Section 7); PyInstaller SmartScreen warning expected at Phase 11, not a bug; broker-integration sequencing tension (Section 4) still needs a direct conversation.

- **[Insert Date]** · **SM and PA exit confirmed by Rajesh directly** — SM = Social Media (distraction tag, ties into 13.9); PA exit = exit based on market structure (support/resistance zone or opposite-side signal), not a fixed target. Added both to `TAGS_GLOSSARY.md`, updated Section 13.16 to reflect the glossary is now fully resolved. The one remaining unnamed concept is the "jumping back into a trade after a break" leak point (13.6) — not a term Rajesh has given a tag for yet, separate from the glossary being complete. **No app code changes this session.** **Next:** Rajesh's call — tag system (13.2) can now be built against a fully-defined glossary, or continue the phase roadmap (Phase 4). · **Flagged (carried over):** parallel React/TS repo should be paused/archived; free market-data source for VIX/USD-INR/Crude not yet chosen (Section 7); PyInstaller SmartScreen warning expected at Phase 11, not a bug; broker-integration sequencing tension (Section 4) still needs a direct conversation.

- **[Insert Date]** · **Received and filed `TAG.txt` — the shorthand/tag glossary.** Created `TAGS_GLOSSARY.md` (new file, project root) as the canonical source for every setup name, grade, probability, context, type-of-day term, and gap-type term, plus six numbered behavioral/session rules. Updated `PROJECT_MASTER.md` to point at it: Section 13.16 now marks most terms resolved (only **SM** and **PA exit** remain genuinely unconfirmed); Section 13.1 gained the concrete hourly session-check cadence (10:15–14:15) and the post-14:15/TTR-flag specifics; Section 13.6 gained the real trading-window rule (no trades past 2:30 PM off a trend day) and the actual A+ setup list. **Corrected a mistake from the previous session:** Section 13.6 had guessed "LPT" was the tag for jumping back into a trade after a break — the glossary shows LPT actually means "Low-Probability Trade," unrelated. Fixed the text to say that specific leak point is still unnamed rather than leave the wrong guess in place. **No app code changes this session** — glossary filing only. **Next:** Rajesh's call — could start building the tag system (13.2) against the now-defined setup/context tags, or continue the phase roadmap (Phase 4). SM and PA exit still need confirming before any logic depends on them. · **Flagged (carried over):** parallel React/TS repo should be paused/archived; free market-data source for VIX/USD-INR/Crude not yet chosen (Section 7); PyInstaller SmartScreen warning expected at Phase 11, not a bug; broker-integration sequencing tension (Section 4) still needs a direct conversation.

- **[Insert Date]** · **Qty/risk-warning bug from previous session confirmed fixed** — was a stale `index.html` not fully replaced on Rajesh's machine, not a code issue; resolved by re-unzipping the full package. **Received and organized `TOS.docx`** — a large personal brain-dump of feature requirements — into new **Section 13: Behavioral Coaching & Real-Time Feedback Engine — Feature Backlog** (16 subsections: daily rhythm prompts, real-time tagging, risk-of-ruin/drawdown simulation, multi-leg scale-out automation, position sizing suggestions, setup discipline loop, streak detection, event/expiry awareness, distraction tracking, idea inbox, Amibroker screenshot integration, auto charges/taxes, broker roadmap refinement, English-writing coaching layer, a testing-phase data reset utility, and a glossary of undefined trading-jargon terms). Also added: a new governance rule (Section 0, Rule 11 — every new feature gets weighed against the long-term goal before being built, not built just because it's listed) and a new philosophy principle (Section 1 — "Zoom Out On Every Slip," reframing any mistake on a weekly basis, not a single-trade basis, sourced directly from Rajesh's own notes). Flagged rather than resolved: (1) several trading-jargon terms (SM, FOL, PA exit, TTR, NTD, SOH, LPT, BO-1Pb) are used in the source notes without definitions — listed in Section 13.16, need Rajesh's own definitions before logic can be built against them; (2) a real tension between Section 4's current broker build order and a new note saying "auto broker integration at the last stage" — flagged in Section 4, not resolved unilaterally, needs a direct conversation before Phase 4/5. **No code changes this session** — purely documentation/planning, per Rajesh's explicit request to organize and commit before building anything from this list. **Next:** Rajesh reviews Section 13, decides what (if anything) to prioritize next — could be a small piece (e.g. tag system for FOL/SM once defined) or continuing the existing phase roadmap (Phase 4 broker integration). · **Flagged (carried over):** parallel React/TS repo should be paused/archived; free market-data source for VIX/USD-INR/Crude not yet chosen (Section 7); PyInstaller SmartScreen warning expected at Phase 11, not a bug.

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

---

## 13. Behavioral Coaching & Real-Time Feedback Engine — Feature Backlog

Added from Rajesh's own notes (`TOS.docx`), organized into groups below. **This is a backlog, not a build queue** — see Section 0, Rule 11. Each item gets weighed against the long-term goal when its turn comes up, not built just because it's listed. Sequencing/prioritization is Rajesh's call; this section exists so nothing he asked for gets lost or half-remembered across sessions.

A general design thread running through nearly all of this: **the app should behave like an active coach, not a passive logbook** — asking questions at the right moments (pre-market, hourly, post-market), catching slips in real time via tags, and always re-anchoring back to the weekly/long-term picture rather than any single trade (see Section 1's new "Zoom Out On Every Slip" principle).

### 13.1 Daily Rhythm — Pre-Market / Hourly / Post-Market
- Opening the app in the morning should prompt a pre-market checklist and produce a score (this already exists in `view-home`'s Pre-Market Regime panel — extend it to *require* completion each morning rather than sit passively).
- Hourly check-in should ask a short set of questions and, if a slip pattern is detected, remind of the relevant pitfall. **Concrete cadence, per `TAGS_GLOSSARY.md` Rule 5:** every hour, starting at 10:15, through 14:15.
- **Post-14:15 (last hour), per Rule 2:** the check-in must specifically ask whether the read is resumption, reversal, or TTR — not the generic questions used earlier in the day.
- **TTR / small-range-day flag, per Rule 4:** when NIFTY's ATR compresses to a 60–70 point range (down from a recent baseline over 100), this is a specific, concrete trigger — surface it immediately as a "be careful and mindful" reminder, not just a passive stat.
- Post-market review should ask about process (not just outcome), and give an honest, critical, corrective reflection with a concrete plan for the next session. Feedback here should be precise about mistakes and improvements — not vague encouragement.

### 13.2 Real-Time In-Trade Tagging & Corrective Nudges — BUILT (v3, see Work Log — full convention now in `TAG_SYSTEM_AND_REFERENCES.md`)
- **One widget only, living in the sidebar** — "Tag" and "Notes" buttons inside the nav rail itself (not floating), so they collapse/expand with the sidebar's own pin/auto-hide state. Notes is a plain autosaving scratchpad with no tag parsing — tags only get created and logged through the Tag button, per direct instruction ("Tags will sit within the Tag widget only").
- **Full typed convention, matching `#TAGS.txt` exactly:** `CODE` (log with the tag's own default mapping, or none), `CODE-A/B/C` (force a bucket for this entry), `CODE-T-N`/`CODE-M-N` (scored 1–10, T=Tactical/M=Mental — the real convention from Rajesh's reference notes). Any code that doesn't exist yet is auto-created on the spot — typing *is* tag creation, no separate add-form needed. Tap buttons (one-tap logging for existing tags) still work alongside typing.
- **ABC mapping cascades into the real system**: a mapped tag pushes a synthetic entry into the same `state.abcChecked` array the manual Self-Check grid uses, so `computeAbcVerdict()`, `computePsychologyScore()`, Alerts, and the bell curve all update automatically — zero duplicate logic.
- **Scored entries (CODE-T-N) get a provisional per-entry bucket estimate** based on the tag's `polarity` (negative/positive, editable in Manage Tags — defaults negative for new tags) — **this is explicitly a placeholder**, not the real monthly/weekly rolling promotion/demotion engine described in `TAG_SYSTEM_AND_REFERENCES.md` Section 2, which needs real historical data and more design work before it can be automated correctly.
- **Tags show up directly inside the real Mental/Tactical C/B/A columns** of the A/B/C Game Self-Check grid (Psychology view) — a small area in each column fills in real time with short-form entries as matching tags land in that dim+bucket. Live Tag Log (Session Checklists) stays to Time/Tag/Note, for everything regardless of ABC mapping.
- Popovers position dynamically off the triggering button's actual screen position (`getBoundingClientRect()`), so they work correctly whether the sidebar is pinned, collapsed, or mid-hover.
- Pure `localStorage` (Layer A) — durable automatically via the Phase 2 persistence patch, no Python changes needed for any of this.

### 13.3 Capital, Risk-of-Ruin & Drawdown Simulation
- During the capital build-up phase (3% risk), simulate risk of ruin across consecutive losing streaks.
- Same simulation applies to **any** risk model and to actual live trades — how long the account survives at 30%, 50%, 70%, and full-blowup drawdown thresholds.
- This should run live against actual trades during an active drawdown phase, warning in real time and suggesting corrective measures (e.g. scale down) — not just as a static, one-time calculator (which is what the current `view-risk` Position Size Calculator does today).
- Whatever risk-per-trade style Rajesh selects in the Risk Engine should be simulated the same way — consecutive-loss and drawdown/blow-up behavior for that specific style, not a generic one-size model.

### 13.4 Multi-Leg Scale-Out Automation
- On a multi-lot entry: 1st exit at 2R, 2nd at 3R, 3rd at 4R, last lot on price action (Rajesh's own discretionary read of the tape).
- This should show live in both the Trade Plan and the Journal, not just get filled in after the fact.
- Once the first lot exits at 2R, the remaining lots' stop should move to breakeven and then trail to lock in profit.
- Longer-term: integrate with the broker terminal to make this scaling automatic rather than manually tracked. Explicitly **not** a near-term priority — noted for later once broker integration exists.

### 13.5 Position Sizing Suggestions
- Based on the current ledger (equity, recent drawdown, streak state), the app should proactively suggest the best position size for the next trade — not just calculate one on request.

### 13.6 Setup / Probability Discipline Loop
- Core idea: **one good trade** is the target on most days. Per `TAGS_GLOSSARY.md` Rule 3: look for more trades only on a confirmed trend day, only after the emotional score has improved, and even then only A+ setups — and only after a profitable day. Outside a strong trend day, each additional trade in a TR day carries a probability-drop reminder unless it's a genuine A+ setup.
- Exception: on a confirmed **strong (hard) trend day**, the app should force the opposite behavior — encourage more trades, bigger size, less hesitation. This is explicitly the *only* day to get aggressive.
- **A+ is now defined**, not a placeholder — see `TAGS_GLOSSARY.md`'s Setup tables (BO, 1st Deeppb, the TR-only 2LR/TCL setups, etc. are the actual A+ list). The existing A+ Setup Reference panel in `view-decision` should be built against these exact setups, not a generic "define your own" field.
- **Trading window rule, per Rule 6:** trading beyond 2:30 PM is only allowed on a confirmed trend day.
- **In a TR specifically, per Rule 1:** the only high-probability trade is a reversal from the obvious 2nd-leg move — from the high/low, close to it, or a failed breakout (FBO) of the high/low. Everything else in a TR is lower-probability by definition.
- Real-time reminder against jumping straight back into a trade right after a break — this leak point was described in the original notes but still has no confirmed tag name in `TAGS_GLOSSARY.md` (an earlier draft of this file incorrectly guessed "LPT" — LPT is actually "Low-Probability Trade," unrelated). This is the one remaining unnamed concept; everything else in the glossary is now fully resolved.

### 13.7 Streak & Session Pattern Detection
- A 2–5 day winning streak should raise an "overconfidence" flag/reminder about losing focus.
- A losing streak should raise a parallel flag for accumulated negative emotion and eroding confidence.
- The app should suggest relevant tags for different emotional states rather than leaving tagging fully manual.

### 13.8 Event & Expiry Awareness
- Extra caution flagged on expiry days — Tuesday for NIFTY, Thursday for SENSEX — and especially on monthly expiry.
- Extra caution whenever India VIX crosses above 20.
- Major macro events (RBI policy, Union Budget, etc.) get their own "event" tag; expiry days get their own "expiry" tag — both used to drive the extra-caution behavior above. (`view-news`'s Market Pulse strip already shows some of this — extend rather than replace.)

### 13.9 Time & Attention / Distraction Tracking
- Real-time tracking of time spent on Twitter, Telegram, or other identified "wanderer" apps during market hours, with a daily distraction score feeding into the same end-of-day bell curve as the psychology data.

### 13.10 Idea & Feedback Inbox
- A separate space to drop raw ideas as they occur, to be discussed/debated later, then explicitly kept or discarded — not mixed into the main workflow.
- Ties directly into Section 0 Rule 11: any proposed feature (from Rajesh or from an AI session) gets weighed against the long-term goal before being built, using this inbox as the holding area for anything not yet decided.

### 13.11 Chart/Screenshot Automation (Amibroker Integration)
- Investigate integrating with Amibroker so that when a trade is taken (detected via the terminal), a screenshot is captured automatically from Amibroker and attached to the Journal.
- Ideally both the futures chart and the relevant options chart get captured and tagged together; if only one is feasible, futures chart alone is an acceptable fallback.
- If a live API-level integration with Amibroker isn't realistic, a simpler fallback: a real-time snip/screenshot workflow that still lands directly in the Journal without extra manual steps.
- This is a nice-to-have, not core — flagged for evaluation once the Journal and broker integration are both solid (Section 0 Rule 11 applies directly here: real complexity, uncertain payoff, needs a deliberate yes/no when it comes up).

### 13.12 Auto Charges & Taxes Population
- For real-time/live trades, fetch correct brokerage and statutory charges (STT, exchange charges, GST, stamp duty, etc.) for the relevant segment and auto-populate them into the Journal.
- When a contract note is uploaded (Tier 2 broker integration), use the CN's actual figures instead of estimates.
- Auto-population applies to real/live trades and CN uploads — not to fully manual/backdated journal entries, where Rajesh is entering historical or hypothetical data himself.

### 13.13 Broker/Terminal Integration Roadmap — Clarified (no cloud, no algo, purely local)
- **Confirmed requirement:** local integration only. No static IP, no cloud dependency, no auto-execution/algo trading — Rajesh explicitly doesn't need that. He wants SENTRY to read from a trading terminal already running on his own machine: **trade book, order book, ticker (live price), VIX, and symbol data**, populated into the app in real time.
- **Still needs clarifying** (see clarifying questions, asked directly rather than assumed): which local terminal is the actual source — Flattrade's own desktop terminal, Amibroker (which Rajesh has and uses for charting, per his screenshot), or something else — and what mechanism it exposes for another app to read from it (a local API, a DDE/OLE interface, a database file, an export folder). The right build approach depends entirely on this answer; guessing wrong here wastes real effort, per Section 0 Rule 11.
- Multi-broker support and 2FA handling remain a later addition once one local integration is solid — unchanged from before.
- Section 4 has the fuller writeup and the resolved/still-open parts of the earlier "last stage" tension.

### 13.17 Pre-Market Ritual → Auto-Suggested Plan
- Indian market pre-market session closes at 9:08 AM. Once that closes, using whatever pre-market data is available (from the local terminal, once 13.13 is resolved), the app should move beyond just scoring the pre-market checklist (current `view-home` behavior) to actually **suggesting a plan for the day** — not just a readiness number.
- Depends on 13.13 being resolved first, since "pre-market data" here means real data pulled from the terminal, not manual entry.

### 13.14 Personal Growth Layer — Writing & English Coaching
- Rajesh is a non-native English speaker and wants subtle help improving his writing and phrasing over time — **not formal teaching, and not corrections that interrupt his flow.** He wants to learn through natural exposure, not be taught directly.
- This applies in two places: (1) as a general interaction style for any AI session working with him (already reflected in his stored preferences), and (2) potentially as a light in-app feature — e.g. the app gently suggesting a clearer word or phrasing when he writes journal notes, theses, or reviews, without ever feeling like a grammar-correction tool.
- Keep this understated in both contexts — the goal is confidence and natural improvement, never friction.

### 13.15 Testing-Phase Data Reset Utility
- While the app is still in active testing (current phase), saying "implement" a change should be able to refresh/reset all data cleanly.
- **Needs a real, safe implementation** before this becomes casual — a guarded "Reset all data (testing only)" action in Settings & Rulebook, behind an explicit confirmation, clearly separated from anything that could be mistaken for resetting real trading history once the app is in daily use. Do not wire a silent/automatic reset trigger — that's a serious foot-gun once real trades are being logged.

### 13.16 Glossary — Fully Resolved (see `TAGS_GLOSSARY.md`)
Rajesh filed a full glossary (`TAG.txt` → `TAGS_GLOSSARY.md` in the project root), and confirmed the last two open terms directly. **`TAGS_GLOSSARY.md` is now the canonical source** for every setup name, grade, context term, and the six numbered behavioral/session rules — the tag system (13.2) and the discipline loop (13.6) both build against it directly.

- **SM** = Social Media — used as a tag/flag (e.g. time spent on it, or a distraction source — ties into 13.9's distraction tracking).
- **PA exit** = exit based on market structure — an obvious support/resistance zone, or an opposite-side signal — not a fixed price target. Confirmed, not an inference anymore.

No unresolved terms remain. Any new shorthand introduced later should be added to `TAGS_GLOSSARY.md` directly, not guessed at here.

---
