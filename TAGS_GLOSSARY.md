# SENTRY — Trading Shorthand & Tag Glossary

**Source:** Rajesh's own trading method (`TAG.txt`). This is the canonical
definition list — the in-app tag system (`PROJECT_MASTER.md` Section 13.2)
and the behavioral rules (Sections 13.1, 13.6) are both built against these
exact terms. Transcribed with only light formatting cleanup (obvious typos
fixed) — meaning preserved exactly as written. If any entry looks off,
correct it here directly rather than in code, since this file is the
single source of truth for the whole tag system.

---

## Setup Grades

| Grade | Meaning |
|---|---|
| A+ | Highest-probability setups |
| A | High-probability setups |
| B | Medium |
| C | Worst — associated with emotional or impulse trades |

---

## High-Probability Trend / Pullback Setups

| Tag | Meaning | Grade | Prob. | Context |
|---|---|---|---|---|
| BO | Breakout — high-probability setup in the right context & location | A+ | 60–70% | — |
| 1Pb / H1 / L1 | 1st pullback after a Breakout. If the BO was strong, this is a High-Probability Trade (HPT) | A | — | Trend |
| A2 / H2 (long) / L2 (short) | 1st 2-leg pullback in the direction of the trend (HPT) | A | 60% | Trend |
| 1st Deeppb | 1st deep pullback in an existing trend — one of the highest-probability setups, "bread and butter" | A+ | ~70% | Mostly trend, sometimes TR |
| Deeppb | Any 2nd/3rd-leg pullback setup in a trend | — | — | Trend |

## Trading-Range (TR) Setups

| Tag | Meaning | Grade | Prob. | Context |
|---|---|---|---|---|
| 2LR-DT / 2LR-FBO-DT / 2LR-FBO-DB-2LR | In a trading range only — HPT | A+ | 70% | TR |
| Rev. from 2nd Leg TCL | Reversal from the 2nd-leg trend channel line overshoot | A+ | — | TR / Trend |
| TCL O/S – W1Pb | Trend channel line overshoot — wedge 1st pullback | A+ | — | TR |

## Failure Setups

- Failure Deeppb
- Failure 2LR
- Failure Rev. from 2nd-leg TCL, turning into a Deeppb
- CT 2nd-leg (2–3 leg) failure around the EMA, or CT 2nd-leg failure generally

## Trend Resumption Setups

- FBO-DT-DB-2LR from MR in HPA price action, in a weak trend
- Deeppb
- DB–DB reversal from range / extreme low
- Reversal after a 2–3 leg move to a test of high/low in a weak trend

## Time-of-Day / Special Setups

| Tag | Meaning |
|---|---|
| Open | 9:20–10:00 window — A+ setup |
| EMA 5-15 Setup | Setup keyed off the 5 and 15 EMAs |
| FBO of the TL | Failed Breakout of the trend line |
| Rev. from H-L | Reversal from a high/low |

## Type of Day

- Soft Trend Day
- Hard Trend Day
- S&C (Spike & Channel)
- Trend Day
- Elastic Trend Day
- Trending Trading Range
- Big Range Day — Trend
- Big Range Day — TR
- VPA PA — Trend/TR day with vertical-move-type price action
- HPA PA — Trend/TR day with horizontal-move-type price action (weak)
- TR — Trading Range day
- Trend — Trend day
- Bear Leg in Bull — a bearish leg within a bull trend
- Bull Leg in Bear — a bullish leg within a bear trend
- Event Day
- 1st Day of the Series

## Gap Types

| Tag | Meaning |
|---|---|
| GU | Gap Up |
| BGUBR | Big Gap Up Beyond Range |
| BGDBR | Big Gap Down Beyond Range |
| SGUBR | Small Gap Up Beyond Range |
| SGUWR | Small Gap Up Within Range |
| SGDWR | Small Gap Down Within Range |
| SGDBR | Small Gap Down Beyond Range |

## Market Structure & Context Terms

| Tag | Meaning |
|---|---|
| TR | Trading Range |
| TTR | Tight Trading Range |
| NTD | No Trade Day |
| SOH | Sitting On Hands |
| LPT | Low-Probability Trade |
| FOL | Fear Of Loss |
| MR | Middle Range |
| LTR | Lower Trading Range |
| UTR | Upper Trading Range |
| W1Pb | Wedge, 1st Pullback |
| W / W-M | Wedge |
| TCL | Trend Channel Line (overshoot) |
| TL | Trend Line |
| 2nd Leg | 2nd-leg move within a TR or trend |
| S&C | Spike & Channel trend |
| DT | Double Top |
| DB | Double Bottom |
| CT | Counter Trend |
| Rev | Reversal |
| H / PH | High / Previous High |
| L / PL | Low / Previous Low |
| MExp. | Monthly Expiry |
| Exp | Expiry |
| HPT | High-Probability Trade |
| RBM | Range-Bound Market |
| EMA | Exponential Moving Average (default: 20) |

---

## Additional Confirmed Terms

| Tag | Meaning |
|---|---|
| SM | Social Media (used as a tag/flag — e.g. time spent on it, or a distraction source, per Section 13.9's distraction tracking) |
| PA exit | Exit based on market structure — at an obvious support/resistance zone, or on getting an opposite-side signal (not a fixed price target) |

---

## Behavioral & Session Rules (from Rajesh's notes — these drive live app logic, not just tags)

1. **In a TR, only focus on reversal from the obvious 2nd-leg move** — from the high/low, close to it, or a failed breakout (FBO) of the high/low. This is the only high-probability trade in that context.
2. **Post-14:15 (last hour):** the session check should always ask whether the read is resumption, reversal, or TTR.
3. **Most days, the goal is one good trade.** Look for more trades only on a confirmed trend day, only after the emotional score has improved, and even then only A+ setups — and only after a profitable day.
4. **TTR / small-range-day flag:** NIFTY's ATR, recently over 100, compressing to a 60–70 point range is a specific, concrete flag — must be surfaced as a reminder to be careful and mindful the moment it's detected.
5. **Session check cadence:** every hour, starting at 10:15, through 14:15.
6. **Trading beyond 2:30 PM is only allowed on a confirmed trend day.**

These six numbered rules are the concrete version of what Sections 13.1 and 13.6 of `PROJECT_MASTER.md` describe more generally — build against the specifics here, not the earlier looser language.
