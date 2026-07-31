# Tag System, ABC Scoring Rules & Trading References

**This file is self-contained.** Anyone can copy just this file and apply it —
it doesn't depend on the rest of the SENTRY project. Source: Rajesh's own
notes (`#TAGS.txt`), transcribed and organized, not reinterpreted.

---

## 1. Tag Types & Naming Convention

Every tag typed into the Tag widget follows one of three shapes:

### A. Scored behavior tags — `NAME-DIM-SCORE`
For anything being rated on intensity, 1–10. `DIM` is a single letter:
- **T** = Tactical (execution — what you actually did in the trade)
- **M** = Mental (psychological/emotional state)

`SCORE` is 1–10. **The meaning of the number depends on which game it's
measured against** (see Section 2) — a 10 is not always bad or always good.

Examples from the source notes:
```
FOMO-T-10
Bias-T-8
Trading Bias-T-8
FOL-T-10
Lack of Focus-M-10
```

### B. Glossary tags — `#CODE-G`
Reference/definitional tags — not scored, not behavior-graded. A glossary
entry, not a live behavior flag.
```
#OU-G
#OD-G
```

### C. Plain tags — `#CODE`
Context or setup tags with no score and no grading — market/session
descriptors. These match the existing trading shorthand glossary
(`TAGS_GLOSSARY.md` in the SENTRY project — BO, Deeppb, TR, TTR, etc.):
```
#TTR, #TR, #2LR
```

**Where tags live:** the Tag widget only — one input, used everywhere in the
system. During a live trade there's no time to type much, so typing just the
short code (e.g. `FOL`) should be enough to log it and immediately show its
corrective-step popup.

---

## 2. ABC Game Scoring Rules

Ratings are 1–10, but **the number's meaning is relative to the game it's
currently measured in**:

| Game | What 10 means | What low means |
|---|---|---|
| C-Game | 10 = huge red flag (worst) | — |
| B-Game | 10 = ideal | 5 and below = getting poor |
| A-Game | 10 = perfect | — |

**Sticky C-Game tags:** FOL, LPT, and Trading Bias specifically stay
classified as C-Game **unless** the score is 3-and-below for 3 consecutive
months.

### Promotion / demotion rules (rolling windows)

**Monthly:**
- In C-Game: if the regular (i.e. typical/average) rating is below 5 for a
  month → moves to B-Game the following month.
- In B-Game: if regular rating is below 5 for a month → moves back to
  C-Game the following month.
- In B-Game: if regular rating is above 5 for a month → moves up to
  A-Game the following month.
- In A-Game: if rating falls below 5 for a month → moves down to B-Game.

**Weekly (faster-moving overrides):**
- In B-Game: a single week rated 1 → drops straight to C-Game.
- In B-Game: a single week rated 10 → jumps straight to A-Game.
- In A-Game: a single week rated 5-or-below → drops to B-Game.

**Status in the SENTRY app (as of this writing): these rolling promotion/
demotion rules are documented here but not yet automated** — the app
currently logs each tag's raw score and dimension, and applies a simple,
clearly-provisional per-entry bucket estimate (see the project's
`PROJECT_MASTER.md` Work Log for exact behavior) while the full
monthly/weekly rolling engine described above is designed properly. Rajesh
has said he'll share more complete rules — this section should be the
reference once that engine gets built, not re-derived from scratch.

**Open questions worth resolving when the full engine gets built** (Claude's
input, as asked for):
- What counts as "regular" — a simple average over the window, a median, or
  something else (e.g. mode, or "most days")?
- What happens with sparse data — a tag only logged twice in a month?
- Do monthly windows reset on the calendar month, or roll on a trailing
  30-day basis?
- When a monthly rule and a weekly rule would fire in the same period and
  disagree, which wins?

---

## 3. Ideas for Making Tags More Automated & Interactive

Requested input on this — a few directions worth considering, not yet built:

- **Keyword search across the whole app.** Since tags are meant to be usable
  "everywhere," a single search box that finds every trade, note, or session
  entry referencing a given tag would make the tag system much more useful
  than logging alone — turns tags into a real index, not just a diary.
- **Tag-to-rule association.** Rajesh's own example: typing `#TTR` should
  automatically surface whatever rule or danger is associated with a Tight
  Trading Range day — not just log the tag. This is a natural extension of
  the nudge system already built (today: one fixed nudge message per tag) —
  the next step is letting a tag reference *multiple* associated things
  (a day-type classification, a session rule, a danger flag) and surface all
  of them, not just one string.
  - A tag's day-level tags could also cross-relate into a trading calendar or Journal Timeline — logically each “day” could carry compound tags (e.g., NTD, TTR, RISK-ON), and its own summary.
- **Weekly/monthly tag dashboards.** Once the scoring rules above are
  automated, a per-tag trend view (this week vs last week, this month vs
  last) would make the promotion/demotion rules visible rather than
  invisible background math — worth pairing with the existing Bell Curve.
- **Auto-suggested tags from context.** Later, once broker/terminal
  integration exists, some tags (TTR, expiry-day caution, VIX-based
  caution) could be suggested automatically instead of requiring manual
  entry — reducing the "no time to type" problem even further during a live
  trade.

---

## 4. Reference & Readings — Trading Style and Psychology Base

This is the standing reference base for Rajesh's trading style and the
psychology framework behind this whole project. Any corrective advice,
research, or suggestion inside SENTRY should draw on this foundation, not
generic trading content.

### Trading style: Price Action (Al Brooks method)
Book list:
- *Reading Price Charts Bar by Bar* — reading individual price bars
- *Trading Price Action Trends* — understanding, entering, and managing trends
- *Trading Price Action Trading Ranges* — trading sideways markets and breakouts
- *Trading Price Action Reversals* — mechanics and identification of reversals
- https://www.brookstradingcourse.com/price-action-trading-books/

Simplified-version blog reference:
- https://ninetrans.blogspot.com/

### Trading Psychology
- https://tradertom.com/
- *Best Loser Wins* (book)
- https://jaredtendler.com/ — *The Mental Game of Trading* (book)
- Dr. David Paul — https://www.londoninvestorshow.com/david-paul-lis2019 ,
  https://www.youtube.com/playlist?list=PLVUeLwMIiPzDN2fAUo6PX-opolQ_5dDU7
- Steve Ward — https://tradeatyourbest.com/about-steve/
- Daniel Kahneman — *Thinking, Fast and Slow*; *The Halo Effect*
- Annie Duke — *Thinking in Bets*; https://www.youtube.com/watch?v=sYVYa13190E

---

*If sharing just this file with someone else, or reapplying it fresh to a new
system: Sections 1–2 define the tag/scoring language, Section 3 is open
design thinking (not settled behavior), and Section 4 is the philosophical
base everything else should be checked against.*
