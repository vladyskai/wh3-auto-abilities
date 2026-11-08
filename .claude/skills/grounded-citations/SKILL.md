---
name: grounded-citations
description: "Ground answers and documents in cited, verifiable sources."
version: 1.2.0
author: Hermes Agent + Teknium
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [Research, Citations, Grounding, Sources, Web, Reports]
    category: research
    related_skills: [arxiv, pdf, reddit-reading, rss-feeds, youtube-content]
---

# Grounded Citations

Every claim taken from an outside source gets an inline numbered citation and a
`Sources:` list, Perplexity-style. A ledger script owns the `url → [n]` mapping
so the numbers and URLs come from retrieval, never from memory — the model only
ever emits small integers it was handed.

For high-stakes work the same ledger doubles as a fact-checking chain: verbatim
quotes are attached to each source (rejected unless they literally appear in
the fetched page text), claims from model knowledge are flagged `[unverified]`,
and `verify --evidence` fails any draft whose cited sources carry no evidence.

This skill covers answers in chat, written documents (markdown, PDF, docx,
slides), and research reports. It does not cover academic BibTeX pipelines —
for conference papers use the `arxiv` skill, which this skill
feeds (see `references/citation-formats.md`).

## When to Use

Use whenever an answer or artifact rests on information you fetched rather than
knew:

- Research, comparisons, news summaries, "what is the current state of X"
- Any deliverable you write to disk that quotes, paraphrases, or reports
  outside facts — reports, briefs, docs, decks, wiki pages
- Fact-finding where the user will want to check your work
- Multi-source synthesis where conflicting sources must be attributed

Skip inline citations when the retrieval is incidental to another task — a
quick syntax/version lookup mid-coding, casual conversation, creative writing.
Mention a URL only if the user would plausibly want the link.

## Prerequisites

None beyond the standard toolset. `scripts/sources.py` is stdlib-only Python 3.
Retrieval comes from whatever is configured: `web_search`, `web_extract`,
`browser_navigate`, or `terminal` (curl, CLIs).

Ledger location: `$HERMES_HOME/cache/citations/ledger.json` (profile-aware).
Override per task with `--ledger <path>` or `HERMES_CITATION_LEDGER`.

Domain notes live in `references/`: `references/switzerland-pension-and-tax.md`
carries the source map and the decision checks for Swiss pension, tax and
employment-benefit questions. `references/llm-cost-comparison.md` carries the
method for questions about what an AI subscription or API route costs, in
tokens and in dollars, and how two of them compare.

## How to Run

Resolve `$S` from the `skill_dir` field that `skill_view` returns for this
skill, never from a guessed path: the profile root differs per install
(`~/.hermes/skills/...` on a classic install, `%LOCALAPPDATA%\hermes\skills\...`
on a Windows profile, a plugin directory for a pinned copy). Pass the path to
native tools with forward slashes, since MSYS paths are not translated for them.

```bash
S=<skill_dir>/scripts/sources.py                   # e.g. C:/Users/<user>/AppData/Local/hermes/skills/research/grounded-citations/scripts/sources.py

python "$S" reset                                  # start a clean ledger
python "$S" add https://example.com/a --title "A"  # prints: [1]
python "$S" add https://example.com/b --title "B"  # prints: [2]
python "$S" list                                   # ledger table
python "$S" render                                 # Sources: block
python "$S" verify draft.md                        # catch bad citations
```

`add` is idempotent and URL-normalized: the same page always returns the same
id within a ledger, so ids stay stable across many search/extract rounds.

## Quick Reference

| Action | Command |
|---|---|
| Fresh ledger for a new task | `sources.py reset` |
| Register a source, get its id | `sources.py add <url> [--title T]` |
| Register several at once | `sources.py add <url1> <url2> ...` (no `--title` on a multi-URL call; loop one `add` per URL when each needs a title) |
| Register from JSON tool output | `sources.py ingest results.json` |
| Attach verbatim evidence to a source | `sources.py quote <id> --text "exact wording" --from page.txt` |
| Show ledger | `sources.py list [--json]` |
| Render the Sources block | `sources.py render [--style markdown\|plain\|footnotes\|bibtex\|evidence] [--only 1,3]` |
| Render only what a draft cites | `sources.py render --cited-in draft.md` |
| Rewrite a draft's Sources block in place | `sources.py render --replace-in draft.md` |
| Check a draft's citations | `sources.py verify draft.md [--strict] [--min-coverage 0.6] [--evidence]` |

## Procedure

① **Reset the ledger** at the start of a task that will produce a grounded
answer or document. Skip the reset when continuing work whose ids are already
in a draft — reusing the ledger keeps the numbering stable.

② **Register every source at retrieval time.** After each `web_search` /
`web_extract` / `browser_navigate` / fetch, pass the URLs to `sources.py add`
(or pipe the raw JSON through `sources.py ingest`). Do this *before* writing
prose. Registering later, from memory, is the failure mode this skill exists to
prevent. `--title` accepts only one URL, so a batch of 10+ pages is registered
with a shell loop (`for u in ...; do python "$S" add "$u" >/dev/null; done`),
which also keeps each returned id out of your context.

③ **Write cite-while-drafting.** Place the bracketed id(s) immediately after
each sentence the source supports:

```
Ice floats because it is less dense than liquid water.[1][2]
```

- No space before the bracket; each id in its own brackets.
- Max 3 ids per sentence. Cite per sentence, not one dump at the end.
- Only ids the ledger returned. Never invent an id or a URL.
- Claims from your own knowledge get no citation.
- Conflicting sources: present both readings, each with its own id.
- Quote exact figures, dates, and names as the source states them; flag gaps
  explicitly ("no source found for X") instead of smoothing them over.

④ **Append the Sources block** with `sources.py render --cited-in <draft>` so
the id → URL mapping is generated mechanically from the ledger, not retyped.
For non-markdown targets pick the matching `--style` and follow
`references/citation-formats.md` for placement (footnotes in docx, endnotes in
PDF/LaTeX, a Sources slide in decks, per-page source lists in wiki output).

⑤ **Verify before delivering** — `sources.py verify <draft>` exits non-zero on
unknown ids, on a Sources block that disagrees with the ledger, or (with
`--min-coverage`) on prose that is too thinly cited. Fix and re-run.

⑥ **Chat answers** follow the same steps with the draft in your reply: register
sources, cite inline, end with the rendered `Sources:` list. For a short answer
you may render the block from `sources.py render --only <ids>` instead of
writing to a file.

## Multi-Platform Sweeps

"What are people saying about X" / "research X across the web" is not one
`web_search`. Fan out across source types, collect in parallel, then synthesise
with every claim attributed to the platform it came from:

| Source type | Route | What it adds |
|---|---|---|
| Open web | `web_search` → `web_extract` | official docs, articles, announcements |
| Community discussion | `reddit-reading` (`search`, `thread`) | real user experience, complaints, workarounds |
| Blogs / releases / changelogs | `rss-feeds` (`read`, `discover`) | dated primary posts, version history |
| Video | `youtube-content` | walkthroughs, demos, talks |
| Code | `terminal` with `gh search repos` / `gh search issues` | implementations, open bugs |
| X/Twitter | `xurl` (needs API access) | announcements, developer chatter |

The `reddit-reading` and `rss-feeds` skills are optional. If absent, install with
`hermes skills install official/social-media/reddit-reading` or
`hermes skills install official/research/rss-feeds` before using them.

Register every URL from every route in the ledger as it arrives (step ②). Keep
opinion and measurement apart: a Reddit thread is evidence that users *report*
something, not that it is true; pair it with a primary source or label it as
sentiment. Report per-platform coverage gaps ("Reddit search returned nothing
newer than March") rather than silently narrowing to what worked.

## Fact-Checking Mode

For work where the reader must be able to check the chain — medical, legal,
financial, safety, disputed claims, or when the user asks for fact-checking —
upgrade from citations to evidence:

① **Attach a verbatim quote per source.** After extracting a page, save its
text to a file and attach the sentence(s) that carry each claim:

```bash
python "$S" quote 1 --text "Ice is about 9% less dense than liquid water." --from page1.txt
```

The quote is rejected unless it appears verbatim in the evidence text
(insensitive to whitespace, case, and markdown markup — inline links like
`_[ERAP1](https://…)_` in extracted text match the plain prose a reader sees),
so a paraphrase or misremembered figure cannot masquerade as evidence.
Copy-paste from the fetched text; never retype. Quote the sentence as the
reader sees it — the matcher sees through the extractor's markup for you, so
you don't have to reproduce link syntax or escaped asterisks in your quote.

② **Flag model-knowledge claims with `[unverified]`.** A load-bearing claim
you could not source gets an explicit marker instead of a citation:

```
The refactor likely predates the 2.0 release.[unverified]
```

`verify --min-coverage` counts `[unverified]` sentences as covered — the goal
is declared provenance for every claim, not a citation on every sentence.
If a key claim can be checked, check it; `[unverified]` is for what genuinely
cannot be, and a fact-check deliverable dominated by `[unverified]` markers
should say so in its summary.

③ **Cross-check disputed facts against a second independent source.** When two
sources disagree, cite both readings with their own ids and quotes, and say
which you weight and why. One source is reporting; two independent sources are
corroboration.

④ **Verify with the evidence gate and render the evidence block:**

```bash
python "$S" verify report.md --evidence --min-coverage 0.5
python "$S" render --style evidence --replace-in report.md
```

`--evidence` fails the draft if any cited source has no attached quote. The
`evidence` render style prints each source's quotes beneath its URL, so the
deliverable shows claim → source → exact supporting text with nothing taken on
faith. Use `--replace-in <draft>` to rewrite an existing Sources block in place
(idempotent — safe to re-run after attaching more quotes); `--cited-in` prints
to stdout instead. Both emit the heading `## Sources` (`--style plain` emits
`Sources:`).

**What `--min-coverage` counts.** Coverage is
`sentences with declared provenance / prose sentences`. A prose sentence is a
non-empty line fragment of 4+ words after the Sources block, headings (`#`),
table rows (`|`), and fenced code are dropped; blockquote markers are stripped.
Provenance is declared by either a `[n]` citation or an `[unverified]` marker,
so a sentence carrying both counts once. Run `verify` without a threshold first
and read the `info: stats:` line to see the counts before picking a number.

## Deliverable Packaging (this user)

- **Put the substance inline in the chat reply.** `MEDIA:` file cards do not
  open or download on his side; a file is a convenience copy, never the only
  carrier of the answer.
- **Also write the file to `Desktop\`**: the markdown source plus a
  print-friendly HTML built from that same markdown (headings, tables, lists,
  `**bold**`, linkified URLs, `@media print` rules). He prints and files these.
- **Generate the HTML mechanically from the finished markdown** so the two
  copies cannot drift, and render the Sources block into the markdown *before*
  converting.
- **Never use em dashes** in prose written for him: he reads them as
  AI-generated. Commas, colons, parentheses, full stops.
- **He is a careful reader without domain background.** Define each technical
  term in plain words at first use (TER, all-in fee, marginal tax rate,
  staggered withdrawal), keep sourced fact visibly separate from your own model
  or judgement, and say plainly what you could not verify.
- **When the recommendation turns on facts only he has** (employment status,
  intentions, risk tolerance, existing accounts), ask them in one batched
  `clarify` form of single-choice questions at the end of the research, then
  write the personalised closing section from the answers and update the files.

## Pitfalls

- **Registering after writing.** The ledger must be populated from tool output,
  not reconstructed from the draft — that reintroduces exactly the hallucinated
  -URL risk the numbering removes.
- **Renumbering mid-task.** Never hand-edit ids in a draft. Ids are ledger
  identities; if a draft cites `[4]`, `[4]` must stay that source. Run `reset`
  only between tasks.
- **Retyping URLs into the Sources block.** Always `render`. A hand-typed URL
  is an unverified claim.
- **Citing a search snippet as if you read the page.** A `web_search`
  description supports only what it literally says. Cite the extracted page
  when the claim needs the body — `web_extract` it first.
- **Over-citing.** Three ids on a sentence is the ceiling; a citation on every
  clause makes text unreadable and hides which source carries the load.
- **Citing the ledger in code/config artifacts.** Source comments belong in
  prose deliverables and doc headers, not inside generated code.
- **Parallel subagents.** Each subagent has its own working directory; point
  them all at one ledger with `--ledger` (or `HERMES_CITATION_LEDGER`) if their
  outputs get merged, otherwise their ids will collide.
- **Quoting from a snippet instead of the page.** Evidence quotes must come
  from the extracted page text, not a search-result description — `web_extract`
  first, save the text, then `quote --from` that file.
- **Paraphrasing into `quote --text`.** The verbatim check will reject it; the
  fix is to find the actual sentence, not to reword until something matches.
- **Using `[unverified]` as an escape hatch.** It marks the rare claim that
  genuinely cannot be sourced; if most sentences carry it, the task needed more
  retrieval, not more markers.
- **Hand-editing the Sources block.** Use `render --replace-in <draft>`; slicing
  the file yourself risks a stale or duplicated block that `verify` then flags.
- **Appending a section to a finished draft.** The Sources block is generated, so
  citations added in a later section never appear in it. Insert the section
  *above* the existing block, re-run `render --replace-in <draft>`, then
  `verify` again; skipping the re-render makes `verify` report the new ids as
  "cited but absent from the Sources block", which reads like a hallucination
  rather than a missing render.
- **Coverage collapses when the deliverable ends in advice.** A recommendation
  or "do this next" section carries judgement, not sourced claims, so adding one
  drops `--min-coverage` below a threshold that passed minutes earlier. Do not
  pad it with citations to game the gate: re-run `verify` without the threshold,
  confirm `citations OK`, and report the stats line honestly.
- **Regenerating a file this task already wrote.** `write_file` refuses to
  overwrite a file whose current content the task has not read, so the second
  conversion pass fails after the source markdown changed. Delete the derived
  artifact first (`rm -f out.html`) or read it, then write, then confirm the new
  byte count and grep for the section you just added.
- **Ranking fee-based products by their headline rate.** Rate cards hide whether
  the fund fee is bundled in and whether the fee applies to the cash part, so
  the cheapest advertised rate is often not the cheapest product. Cite a
  third-party cost simulation at a stated contribution and horizon alongside the
  rate table, and quote its assumptions.
- **Presenting your own arithmetic as a source.** A projection you calculated
  gets labelled as your model with its assumptions stated, never cited like a
  published figure.
- **Quoting a measured third-party figure as if it were a published one.**
  Log analyses, gateway telemetry and forum posts carry three things that
  vanish when you retell them: the unit of observation (one account, N
  accounts, a controlled test), the bound direction, and the price list of the
  day. One account's never-hit-cap best week is a floor on that account's cap,
  not the value a buyer receives; a promo-period figure is not the current
  level. State the N, the date and whether the number is a floor or a ceiling,
  or drop it to a range.
- **Ranking a flat-price plan against a metered service on the headline unit
  rate.** Total cost turns on the volume mix, not the unit price: for agent
  traffic, cached-input reads are the bulk of the tokens and the cheapest line
  on the bill. Price the same measured volume both ways before calling either
  cheaper, and name the volume at which the ranking flips.
- **Treating a rate card or plan limit as stable.** Vendors cut token rates and
  expire limit promotions without notice, so a figure is only true for the
  month it was priced. Re-fetch the current rates, say which month the
  comparison is priced at, and reprice the earlier measurement, since a cut of
  a third or more on the dominant token class moves the total by that much.

## Verification

```bash
python "$S" verify report.md --strict --min-coverage 0.5
```

Green means: every `[n]` in the draft exists in the ledger, the Sources block
lists exactly the cited ids with the ledger's URLs, and the cited share of
source-bearing sentences meets the threshold. Read the warnings even when the
exit code is 0 — uncited registered sources usually mean a claim lost its
attribution during editing.
