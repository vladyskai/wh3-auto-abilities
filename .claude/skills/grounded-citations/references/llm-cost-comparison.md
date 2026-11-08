# LLM Cost Comparison: what a plan or an API route actually costs

For questions of the shape "how many tokens do I get for <plan>?", "is <subscription>
worth it?", "how does my current model stack up against <plan>?" and "what should I
pay for?". Two axes have to be answered separately: what the thing costs, and what
model quality you get for it. Collapsing them into one number is the failure mode.

## 1. Establish what the vendor publishes, and label the rest as measurement

| Vendor type | What is published | What is NOT published |
|---|---|---|
| Subscription plan (Claude Max, ChatGPT Pro) | prices, per-session multipliers against the base tier, the existence of a weekly cap, reset behaviour | any token count, and any multiplier for the weekly tier |
| First-party API (DeepSeek, OpenAI) | per-token rate card by token class, incl. cache-hit and cache-miss rates | nothing material |
| Reseller / aggregator (Nous Portal, OpenRouter) | catalog in/out prices per million, sometimes batch rates | often no cache-hit rate, so agent bills cannot be predicted from the catalog alone |

Rule: if the plan page says "5x the Pro allowance per session" and "a weekly limit
that applies across all models", then the 5x is per session only and the weekly tier
has no published multiplier. Third parties have measured both; treat their numbers as
measurements (see `grounded-citations` pitfalls on unit of observation and bounds).

## 2. Build a volume profile, never a single token number

Agent traffic is dominated by cached input, so "tokens" alone says nothing. A profile
has three lines per period:

- cache reads (the agent re-sending its own context on every step: 85 to 96% of volume
  in measured Claude Code workloads)
- uncached input (fresh context plus cache writes)
- output (the only line that scales with how much text is actually produced, and
  typically under 1% of volume)

Sources for a profile, best first: the user's own logs (`~/.claude/projects` JSONL for
Claude Code, ccusage, the harness's own session counters), then a published log-based
study, then a projection clearly labelled as one.

## 3. Price the identical profile on every route

Compute each route by multiplying each line by its own rate. Cache pricing decides the
answer: a route that does not discount cached input can cost several times a route that
does, at the same token volume. DeepSeek's cache-hit rate is 0.02x its cache-miss rate,
which is what makes the token-volume maths come out low at all.

Worked example, priced at the rates in force on 16 Oct 2026 for one measured heavy
week (1,768M cache reads, 218.5M uncached input, 12.5M output): DeepSeek V4.1 Flash
off-peak $45.58 and at peak $91.16; Opus 5.5 at list $1,478. Treat these as shape, not
as current numbers: re-fetch every rate before reusing any of it.

## 4. Convert time-of-day pricing into the user's local clock

Metered routes with peak/off-peak windows (DeepSeek: 01:00-04:00 and 06:00-10:00 UTC,
Mon-Fri) have to be restated in the user's timezone before they mean anything, and
weekend-wide discounts counted. In UTC+02:00 that peaks are 03:00-06:00 and 08:00-12:00
local, so every run after noon local, all night, and all weekend is half price: an
actionable scheduling fact, not a footnote.

## 5. Compare plan-against-metered at the same volume, then find the crossover

The interesting result is usually that they cost about the same at the plan's own
volume, because a subscription is sold well below its vendor's own list price. Both
sides of that must be stated: what the plan's usage is worth in API dollars, and what
the cheaper metered route charges for that same volume. Then give the volume at which
the ranking flips (subscription wins above roughly the plan fee's worth of metered
usage per month; metered wins below it, by a wide margin at light use).

## 6. Keep capability on its own axis

- Quote agentic benchmarks per version, never across versions, and name the harness:
  the same checkpoint moves several points between scaffolds, so a vendor's own harness
  score is not comparable to a third-party harness score.
- Vendor-reported and independently-run scores differ materially; give both.
- Cost per solved task from an independent evaluator is the one figure that combines
  the two axes, and it is a weaker claim than either.
- If the harness in play (Hermes) is absent from the scaffold tables, say that plainly
  instead of implying a number.

## 7. Sources to fetch, in order

| What | Where |
|---|---|
| Plan terms and limits | support.<vendor>.com help-centre articles, the plan pricing page |
| Limit-change history | vendor news/blog announcements (5-hour and weekly limit changes ship as separate posts) |
| Current API rate card | the vendor's own pricing page; check for a peak/off-peak schedule |
| Historical rates, for repricing an old measurement | the pydantic/genai-prices repo in GitHub (per-provider YAML with dated `constraint` blocks) |
| Reseller rates and credits | the aggregator's public model catalog page (Portal, OpenRouter) |
| Measured value of a subscription | log-based studies (finopsllm, wokey) and controlled tests (SemiAnalysis); forum posts are lower bounds |
| Capability | Artificial Analysis, Vals AI, the official Terminal-Bench board |

## 8. Deliverable shape (this user)

Inline tables in the chat reply, the same content written to `Desktop\<topic>.md`, no em
dashes, jargon glossed inline. Lead with the direct answer, then the tables, then the
correction or caveat the reader will otherwise find themselves, then sources. When a
figure gets challenged, re-derive it from the source text, state exactly what the source
says, and say which framing was wrong: quoting a floor as if it were a plan-level value
is the mistake to own, not the retrieval.
