# TLE – Trade Object & Trade Lifecycle Specification

**Status:** FROZEN v1.1

**Supersedes:** FROZEN v1.0

**Document Status:** Frozen for Implementation

**Rule:**
This document is the single source of truth for the Trade Lifecycle Engine (TLE).
No changes shall be made during implementation.
Any proposed changes shall be recorded separately and discussed only after
completion of the planned implementation milestone.

---

# Changelog: v1.0 → v1.1

All eight items proposed in `PROPOSED_CHANGES_v1.1.md` are adopted in full:

1. Every field now has a type, required/optional status, and validation rule.
2. New **Instrument** section (2) added — strike, expiry, option type, lot size,
   contract multiplier — referenced by Planning and Execution.
3. Execution and Exit changed from fixed Entry/Exit 1–4 fields to leg arrays.
4. Explicit boundary rule added between Execution and Trade Management.
5. Readiness checklist is now weighted, with a computed score and
   GO / CAUTION / STOP thresholds.
6. Lifecycle gains two branch states: **Invalidated** and **Skipped**.
7. Psychology fields are fixed to a 1–10 numeric scale (Emotion fields to a
   controlled label set) instead of free text.
8. Identity gains a `lifecycleHistory` array recording a timestamp on every
   lifecycle transition.

Section numbering has changed from v1.0 due to the new Instrument section.
See the mapping below if cross-referencing older notes:

| v1.0 section | v1.1 section |
|---|---|
| 1. Identity | 1. Identity |
| — | 2. Instrument (new) |
| 2. Planning | 3. Planning |
| 3. Readiness | 4. Readiness |
| 4. Execution | 5. Execution |
| 5. Trade Management | 6. Trade Management |
| 6. Exit | 7. Exit |
| 7. Review | 8. Review |
| 8. Psychology | 9. Psychology |
| 9. Learning | 10. Learning |
| 10. Attachments | 11. Attachments |

---

# Purpose

The Trade Lifecycle Engine (TLE) is the foundation of the Trading Operating System (TOS).

Every trade is represented as one complete lifecycle, beginning with an idea and ending with learning.

One Trade = One Trade ID.

---

# Trade Object

The Trade Object consists of the following logical sections.

---

# 1. Identity

Every trade must have a permanent identity.

Fields:

- **Trade ID** — string, required, immutable, unique. Recommended format:
  `TOS-YYYYMMDD-####`.
- **Created Date** — ISO 8601 timestamp, required. Must equal the first
  `lifecycleHistory` entry's timestamp.
- **Created By** — string, required.
- **Status** — enum, required. One of: `Draft`, `Planned`, `Ready`,
  `Triggered`, `Active`, `Scaling`, `Completed`, `Invalidated`, `Skipped`,
  `AwaitingReview`, `Reviewed`, `Archived`. Always derived from the most
  recent entry in `lifecycleHistory`, never set independently.
- **Version** — integer, required, starts at 1, increments by 1 on every
  edit to any section, monotonically increasing.
- **Tags** — string array, optional. Lowercase-kebab-case recommended.
- **Lifecycle History** — array of `{ status, timestamp }`, required,
  minimum one entry (the initial Draft), append-only, entries in ascending
  timestamp order. The gap between two consecutive entries is the time
  spent in that state (e.g. time between Ready and Triggered is decision
  latency).

Rules:

- Trade ID never changes.
- Every record references the Trade ID.
- One Trade = One Trade ID.
- `status` must always equal `lifecycleHistory[last].status`.

---

# 2. Instrument

Every trade must reference the specific contract being traded.

Fields:

- **Symbol** — string, required. e.g. `NIFTY`.
- **Instrument Type** — enum, required. `INDEX` or `STOCK`.
- **Option Type** — enum, required for options. `CE` or `PE`.
- **Strike Price** — number, required, > 0, must be a valid strike for the
  symbol/expiry.
- **Expiry Date** — ISO 8601 date, required, must be a valid weekly/monthly
  expiry for the symbol.
- **Lot Size** — number, required, > 0. Keep configurable since
  exchange-mandated lot sizes change periodically.
- **Contract Multiplier** — number, required, > 0. Usually 1 for index
  options.

Purpose:

Enables the Risk Engine to calculate premium outlay in INR and lets
Analytics slice performance by strike distance, days-to-expiry, or expiry
week.

---

# 3. Planning

Planning represents the reason for taking the trade.

Fields:

- **Instrument** — reference to Section 2, required before a trade can
  move from Draft to Planned.
- **Why this trade?** — string, required, non-empty.
- **What is the edge?** — string, required, non-empty. The specific,
  repeatable edge being exploited — not a restated thesis.
- **Strategy** — string, required. Named setup (e.g. "ORB Breakout").
  Recommend a controlled list once 10+ repeated setups exist, so Analytics
  can group by it reliably.
- **Timeframe** — enum, required. e.g. `Intraday`, `Swing`, `Positional`.
- **Expected Risk Reward** — number, required, > 0.
- **Maximum Risk** — number (INR), required, > 0. Should be checked
  against the capital plan's per-trade risk limit at save time.
- **Maximum Loss** — number (INR), required, > 0, should be ≥ Maximum Risk.
  Worst case if the stop fails entirely (gap/liquidity risk).
- **Position Size** — integer (lots), required, > 0, consistent with
  Capital Allocation and Instrument.Lot Size.
- **Capital Allocation** — number (INR), required, > 0.
- **Market Context** — string, optional but recommended. Feeds the Edge
  Drift Monitor.
- **Supporting Thesis** — string, optional.
- **Invalidation** — string, required, non-empty. The specific condition
  that proves the thesis wrong — this is what separates an Invalidated
  trade from a Triggered one in the Lifecycle.
- **Entry Trigger** — string, required, non-empty. The specific, observable
  condition that triggers entry — checked by the Readiness Engine at the
  Ready → Triggered transition.

Purpose:

This becomes the official Trading Plan.

---

# 4. Readiness

Readiness determines whether the trade should be executed.

Fields:

- **Checklist** — array of `{ label, weight, passed }`, required,
  non-empty. Weights across one checklist template sum to 100. Recommend
  reusing the existing TOS v2 ten-item weighted Decision Engine rather than
  maintaining two competing models.
- **Today's Mindset** — string, optional.
- **Revenge Trading Flag** — boolean, required. If `true`, forces the
  verdict to `STOP` regardless of computed score.
- **Score** — number, computed (never hand-edited), 0–100. Sum of `weight`
  for every checklist item where `passed = true`.
- **Verdict** — enum, computed. `GO` if score ≥ 80, `CAUTION` if score is
  50–79, `STOP` if score < 50 — or `STOP` unconditionally if Revenge
  Trading Flag is true.

Purpose:

This becomes the GO / CAUTION / STOP Engine.

---

# 5. Execution

Execution records every entry that fills the *original planned entry* —
not any add-on placed after the trade is already Active (see Section 6 for
that boundary).

Fields:

- **Entries** — array of legs `{ legId, price, quantity, timestamp,
  orderType }`, required, minimum 1 once status is Active or later.
- **Average Entry** — number, computed (quantity-weighted average of
  entries), never stored/hand-edited.
- **Slippage** — number (INR), computed where possible; manual override
  with a note allowed if the trigger price wasn't logged precisely enough.
- **Broker** — string, required, from a controlled list of the trader's
  brokers.
- **Execution Notes** — string, optional.

Purpose:

Represents actual order execution.

---

# 6. Trade Management

Trade Management records every modification made *after* the trade reaches
`Active`. A leg that fills the original planned entry belongs in Execution
(Section 5), never here — this is the explicit boundary rule adopted in
v1.1.

Fields, per event:

- **Event ID** — string, required, unique within the trade.
- **Timestamp** — ISO 8601, required, must be after Execution's last entry
  timestamp.
- **Type** — enum, required. `STOP_MOVED`, `PARTIAL_EXIT`, `SCALE_IN`,
  `SCALE_OUT`.
- **New Stop Price** — number, required only if Type is `STOP_MOVED`.
- **Quantity Change** — signed number, required if Type is
  `SCALE_IN`/`SCALE_OUT`/`PARTIAL_EXIT` (positive for scale-in, negative
  for scale-out/partial exit).
- **Price** — number, required if Type is
  `SCALE_IN`/`SCALE_OUT`/`PARTIAL_EXIT`, > 0.
- **Reason** — string, required, non-empty. Read by the Rule Engine and
  Review to detect plan deviation.
- **Emotion** — integer 1–10, required.
- **Confidence** — integer 1–10, required.

The section as a whole may be an empty array (many trades have no
post-entry modifications); if present, events must be in ascending
timestamp order.

Purpose:

Creates the complete Trade Timeline.

---

# 7. Exit

Exit records every closing transaction.

Fields:

- **Exits** — array of legs `{ legId, price, quantity, timestamp,
  orderType }`, required, minimum 1 once status is Completed. Combined
  exit quantity must equal combined Execution entry quantity plus net
  Trade Management scale-in/out — the position must fully close to zero.
- **Average Exit** — number, computed (quantity-weighted average of exits).
- **Realised P&L** — number (INR), computed:
  `(Average Exit − Average Entry) × Total Quantity × Lot Size × Contract Multiplier`.
- **R Multiple** — number, computed: `Realised P&L ÷ Planning.Maximum Risk`
  — always divided by *planned* risk, not actual risk taken, so oversizing
  stays visible in the number itself.
- **Exit Reason Category** — enum, required. `TARGET_HIT`, `STOP_HIT`,
  `INVALIDATION`, `TIME_STOP`, `DISCRETIONARY`, `OTHER`.
- **Exit Reason Note** — string, optional. Free-text detail alongside the
  category.

Purpose:

Represents trade completion.

---

# 8. Review

Trade Review evaluates process rather than financial outcome.

Fields — all required booleans, no partial/middle state:

- **Plan Followed** — did execution follow Planning.Entry Trigger exactly?
- **Discipline Maintained** — was the trade managed per plan, no impulsive
  changes?
- **Sizing Correct** — did Position Size match Planning?
- **Did Interfere** — did the trader manually interfere beyond the plan?
- **Exit Was Emotional** — was the exit driven by emotion rather than the
  planned exit condition?
- **Stop Respected** — was the planned stop respected, never moved further
  away?
- **Would Take Again** — would the trader take this exact setup again,
  independent of outcome?
- **Process Score** — number, computed, 0–100. Weighted sum of the seven
  booleans above (Did Interfere and Exit Was Emotional score when
  `false`). Initial proposed weights: Plan Followed 20, Discipline
  Maintained 20, Sizing Correct 15, Stop Respected 20, Did Interfere 10,
  Exit Was Emotional 10, Would Take Again 5 — revisit after 20–30 logged
  trades once real failure patterns are visible.

Principle:

Profit ≠ Good Trade

Loss ≠ Bad Trade

Process is evaluated independently.

---

# 9. Psychology

Psychology records the trader's emotional state.

Fields:

- **Emotion Before / During / After** — enum, required. One of: `Calm`,
  `Confident`, `Anxious`, `Frustrated`, `Euphoric`, `Fearful`, `Neutral`.
- **Confidence** — integer 1–10, required.
- **Stress** — integer 1–10, required.
- **Fear** — integer 1–10, required.
- **Greed** — integer 1–10, required.
- **Patience** — integer 1–10, required.
- **Distraction** — integer 1–10, required.

Purpose:

Creates long-term behavioural analytics.

Example:

Show every losing trade where Confidence exceeded 9/10.

---

# 10. Learning

Every trade must leave knowledge behind.

Fields:

- **Biggest Mistake** — string, optional, recommended when Process Score
  < 70.
- **Biggest Success** — string, optional.
- **Lesson Learned** — string, required, non-empty.
- **Rule Created** — reference `{ ruleId, label }`, optional. Structured
  rather than free text, so the Edge Drift Monitor can tally how often a
  specific rule is created or broken over time.
- **Rule Broken** — reference `{ ruleId, label }`, optional, generally
  populated when Review.Discipline Maintained is `false`.

Purpose:

Continuous improvement.

---

# 11. Attachments

Trade evidence.

Fields, per attachment:

- **Stage** — enum, required. `BeforeEntry`, `Entry`, `Management`,
  `Exit`, `Review`.
- **Type** — enum, required. `SCREENSHOT`, `VIDEO`, `CHART_MARKUP`.
- **URL** — string, required, must be a resolvable file reference.
- **Timestamp** — ISO 8601, required.
- **Caption** — string, optional.

---

# Trade Lifecycle

Every Trade progresses through the following lifecycle.

Draft

↓

Planned

↓

Ready

↓

Triggered → **Invalidated** (thesis broke before entry) or trade never
taken → **Skipped** (valid setup, not taken)

↓

Active

↓

Scaling

↓

Completed

↓

Awaiting Review

↓

Reviewed

↓

Archived

Both `Invalidated` and `Skipped` route to Awaiting Review the same as
Completed trades — a valid setup that was invalidated or skipped is still
a discipline signal worth reviewing.

Important Principle:

Completed ≠ Finished

A trade is complete only after review and learning have been captured.

---

# Three Core Questions

Every Trade must answer three questions.

## 1. Was it a good idea?

Planning

---

## 2. Was it executed well?

Execution

---

## 3. Did I learn something?

Review

These three evaluations are considered more important than the financial result alone.

---

# Why this Model

A properly defined Trade Object allows:

- Trading Journal
- Risk Manager
- Analytics
- AI Coach
- Reports

to operate from a single consistent data model.

Everything in TOS is built upon this foundation.

---

# Independent Scores

Every Trade maintains two separate scores.

## 1. Process Score (0–100)

Measures adherence to the trader's own process and discipline. Computed
per Section 8 above.

---

## 2. Outcome Score

Measures the financial result.

Includes:

- P&L (INR)
- R Multiple
- Return % (P&L ÷ Capital Allocation)
- Result: `WIN` / `LOSS` / `BREAKEVEN`

Process Score and Outcome Score are intentionally independent.

A profitable trade with poor discipline may receive:

High Outcome Score

Low Process Score

A losing trade executed perfectly may receive:

High Process Score

Low Outcome Score

---

# Cross-Section Validation

These rules can only be checked once the whole Trade Object is assembled,
and must be run before allowing any lifecycle transition (not only at
final save):

- Total exited quantity must equal total position quantity (Execution
  entries + net Trade Management scale-in/out) once status is Completed.
- Status of `Completed` or later requires an Exit record to be present.
- Status of `Reviewed` or `Archived` requires both Review and Learning to
  be populated.
- Top-level Process Score must exactly mirror Review.Process Score.
- Outcome Score must be present if and only if an Exit record is present.

---

# Freeze Rule

Status: FROZEN v1.1

No additions.

No deletions.

No redesign.

Implementation must follow this document exactly.

Future ideas shall be discussed only after completion of the
implementation milestone, and recorded separately (e.g.
`PROPOSED_CHANGES_v1.2.md`) rather than edited into this file.
