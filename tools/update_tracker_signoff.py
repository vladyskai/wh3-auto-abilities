#!/usr/bin/env python3
"""Tracker edits for the sign-off pass (binary read/write - the file is LF).

1. Three new update paragraphs after the harness-116 entry: 117 (centre distance
   back, edge measurement retired), 118 (the wait deleted), and the sign-off
   pass itself (full suite + workbook v18).
2. One SIGN-OFF DECISIONS paragraph: the bombardment logic stays as it is
   ("I find it satisfying right now"), and the Hecleas review outcome with the
   two things the user chose not to pursue.
3. The 19 air-drop rows in §3a get the rule in force prepended to their rule
   cell, with the round 114-116 text explicitly marked SUPERSEDED (history kept).
4. The 30 enemy_ground_melee_infantry rows and the 6 melee_skip_commanders rows
   get the user's bombardment decision appended to their last cell.
5. The §3b friendly-fire block gets the Hecleas note (no friendly-fire veto).
"""
import hashlib

P = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_ability_tracker.md"
raw = open(P, "rb").read()
assert raw.count(b"\r") == 0, "the tracker must stay LF"
s = raw.decode("utf-8")
before = hashlib.md5(raw).hexdigest()
lines = s.split("\n")
print("lines before:", len(lines), "md5:", before)

UPDATES = [
    # ------------------------------------------------------------------ 117
    "**Update 2026-10-18 (harness 117 - THE AIR DROP IS THE CENTRE DISTANCE AGAIN; THE EDGE MEASUREMENT "
    "IS RETIRED).** Light iteration cycle (the air-drop harness sections only; no workbook, no full "
    "suite - the cycle the user approved for tuning rounds). **THE RULING**, after testing round 116: "
    "*\"I tried it. Let's keep the distance to center\"*. **THE MEASUREMENT IS REPLACED, not retuned:** "
    "`battle_unit:unit_distance` is EDGE-TO-EDGE on bounding BOXES (`battle_unit.lua:160`), so a wide "
    "flying formation beside a wide infantry block reads a fraction of a metre while the two CENTRES "
    "are 15 m apart - the old rule could fire with nothing underneath, which is the report that "
    "started the sequence. The decision is now **`FOURTH.AIR_DROP_CENTER_M = 6.0` on the HORIZONTAL "
    "CENTRE-TO-CENTRE distance** (`battle_unit:position()` x/z, `battle_vector:distance_xz` with a "
    "`sqrt(dx^2+dz^2)` fallback, every read fail-closed). `AIR_DROP_EDGE_M` is deleted; nothing else "
    "in the file used it. The measured delay of round 116 was KEPT at this point. **Counts unchanged:** "
    "689 entries / 742 keys / 46 evaluators, `air_drop_on_infantry` 12 / 19. Harness 117 (light, "
    "`H117_LIGHT=1`): **1,828 checks / 0 failures**; installed pack md5 "
    "`516b16aaa33d26abede8738c4447ffbe`. Round doc `docs/WH3_round117_airdrop_centredist.md`.",
    # ------------------------------------------------------------------ 118
    "**Update 2026-10-18 (harness 118 - THE DELAY IS GONE; THE 6 m CENTRE STAYS).** Light cycle again. "
    "**THE RULING**, verbatim: *\"I tried it. Let's keep the distance to center and remove the delay we "
    "had completely.\"* **DELETED** (whole-file grep first, caller audit in the round doc): "
    "`AIR_DROP_DWELL_MID_S`, `AIR_DROP_DWELL_SWING_S`, `AIR_DROP_MIN_CONTACT_S`, the pair row "
    "(`FOURTH.ad_pair` and its helpers), the purge hook and its only call site, the velocity rebuild "
    "(`ad_enemy_velocity` and the raw-read body), the projection, the dynamic delay, the "
    "short-crossing fallback and every dwell / hold / separation / cosine log line - including the "
    "raw movement + heading read-verification block, which existed only to check the cosine. **KEPT:** "
    "the centre measurement (`ad_centre_gap`), the candidate filter (ALIVE, `number_of_men_alive() > "
    "`AIR_DROP_MIN_MEN` 10, **no infantry filter**), the 0.2 s fast pass with its 30 m near gate, "
    "`POLL_MS` 250, `air_only` / `no_melee`, the self-centred cast on the OWNER, every fail-closed "
    "read, the gates and the pre-cast re-check - which now re-measures the CENTRE on fresh handles. "
    "The trigger fires on **the evaluation that first measures a centre inside 6 m**: nothing is "
    "stamped, nothing is timed, nothing is re-measured inside a contact. **Counts unchanged:** 689 / "
    "742 / 46, `air_drop_on_infantry` 12 / 19. Harness 118 (light, `H118_LIGHT=1`): **1,586 checks / 0 "
    "failures**; red control 80. Installed pack md5 `2f215bc4c35845452103327fb62ba554`. Round doc "
    "`docs/WH3_round118_airdrop_nodelay.md`. **The workbook was not touched in either round** (the "
    "approved light cycle), so v17 still described round 116's measured delay until the sign-off pass "
    "below reconciled it.",
    # -------------------------------------------------------------- sign-off
    "**Update 2026-10-18 (SIGN-OFF PASS - harness 119: THE FULL SUITE, HEAVY MODE, AND WORKBOOK v18).** "
    "The user said *\"Update the spreadsheet\"* - the agreed sign-off point - so the light cycle ended: "
    "the FULL suite was run against the shipped source and the master workbook was regenerated. "
    "**FULL SUITE: 4,777 checks / 0 failures** (harness 119 = harness 118 plus five pin edits; run "
    "twice, byte-identical). **harness 118's own full run found 5 failures, ALL ONE STALE PIN and "
    "nothing else:** harness 93's hand-kept mirror of `FOURTH.TRIGGER_TIP` still carried round 116's "
    "wording for `air_drop_on_infantry` - byte-equal to the PRE-118 snapshot (`docs/backups/round118/"
    "pre118_*.lua`), which is how the diagnosis was proved - so `0q live`, `0q ann`, `D2`, `D3a` and "
    "the h93 headline failed while the SOURCE was right (12 unmatched entries, all `air_drop_on_infantry`). "
    "No real regression from rounds 117/118 and **no failure outside the air-drop family**. The four "
    "air-drop suite-boundary pins the light cycle had left as floors are now EXACT: h114 4614, h115 "
    "4686, h116 4702, h117 4718; light mode still runs green (1,586 / 0) because its floors are kept. "
    "**WORKBOOK v18:** `docs/WH3_abilities_master_v18_2026-10-18.xlsx` (+ `.ods`) - all 19 air-drop "
    "rows rewritten in columns 19 and 22 to the centre rule, every reference to the removed machinery "
    "gone; Definitions sections 12/13/14 retitled RETIRED with one reason each, sections 8-11 given "
    "their reason too, and a new section 15 stating the rule in force with `AIR_DROP_CENTER_M = 6.0` "
    "as the single knob and the full retired list; Numbers reconciled with the arithmetic stated "
    "(1,799 = 1,141 + 658; 689 entries / 742 keys / 46 evaluators; 741 implemented rows + 1 key with "
    "no inventory row = 742); v1-v17 byte-unchanged. **NO SOURCE CHANGE AND NO REBUILD** - the "
    "installed pack was already the round-118 build (`2f215bc4c35845452103327fb62ba554`). Full record: "
    "`docs/WH3_signoff_full_suite_v18.md`.",
]

DECISIONS = (
    "**SIGN-OFF DECISIONS (2026-10-18) - TWO THINGS CLOSED, ONE REVIEW FILED, NOTHING PENDING.** "
    "**(1) THE BOMBARDMENT LOGIC IS FINAL FOR NOW.** The user's ruling, verbatim: *\"I find it "
    "satisfying right now\"*. The `enemy_ground_melee_infantry` and `melee_skip_commanders` families "
    "are to be **left exactly as they are** and are **not to be re-litigated** (no retune, no new "
    "trigger proposal, no questionnaire). Each implemented bombardment row carries this note inline; it "
    "is a decision, not a pending question. **(2) THE HECLEAS MOD REVIEW - `docs/WH3_hecleas_mod_review.md`.** "
    "The review examined the Hecleas battle mod for anything reusable: **the BATTLE AI CLAIM RESOLVES "
    "TO A WEIGHTS TABLE, not scripted ability logic** - it weights how the AI values targets and "
    "abilities and carries **no reusable per-ability trigger scripting** this mod could adopt, so "
    "nothing was ported. **THE USER CHOSE NOT TO PURSUE, at this time:** (a) the **FRIENDLY-FIRE "
    "VETO** - an engine-side or script-side check that would let an area ability refuse a cast whose "
    "blast would catch friendly units; and (b) the **REINFORCEMENT ENUMERATOR** - a read for units "
    "arriving as reinforcements. Neither is scheduled, neither changes the wheel scope, and the §3b "
    "friendly-fire block therefore stays `proposed (FF)` / excluded exactly as it is - the veto is not "
    "the reason those rows are off, and building it later would not switch them on by itself."
)

AIRDROP_NOTE = (
    "**ROUND 118 (2026-10-18) - THE RULE IN FORCE, as reconciled in workbook v18: fire when the "
    "nearest ALIVE enemy with more than 10 models has a HORIZONTAL CENTRE-TO-CENTRE distance under "
    "`FOURTH.AIR_DROP_CENTER_M = 6.0 m`, on that same evaluation - no wait, no pacing of any kind, no "
    "motion prediction, no fallback path. The candidate rule is unchanged: alive, more than 10 models, "
    "no infantry filter. THE TEXT THAT FOLLOWS IS HISTORY (rounds 114-116) AND IS SUPERSEDED; the "
    "authoritative per-row rule is the Trigger column of `docs/WH3_abilities_master_v18_2026-10-18.xlsx` "
    "and Definitions section 15 of that workbook.** "
)

BOMB_NOTE = (" · **USER DECISION 2026-10-18: leave this trigger as it is** (*\"I find it satisfying "
             "right now\"*) - recorded so it is not re-litigated.")

HECLEAS_NOTE = (
    "> **HECLEAS REVIEW OUTCOME (2026-10-18) - the friendly-fire veto is NOT being pursued.** "
    "`docs/WH3_hecleas_mod_review.md` found that the Hecleas mod's BATTLE AI claim is a **weights "
    "table** with **no reusable ability scripting**, so nothing was adopted from it. The user also "
    "chose, at this time, **not** to build a friendly-fire veto (an area cast refusing to fire when "
    "the blast would catch friendly units) and **not** to build the reinforcement enumerator. This "
    "block therefore stays `proposed (FF)` / excluded exactly as it is - the missing veto is not what "
    "keeps these rows off, and adding one later would not switch them on by itself."
)

# --------------------------------------------------------------------- insert
idx = None
for i, l in enumerate(lines):
    if l.startswith("**Update 2026-10-18 (harness 116") and "0c489c2438cf9acc98730bff1b0df52b" in l:
        idx = i
assert idx is not None, "the harness-116 update paragraph was not found"
new = []
for t in UPDATES:
    new.append("")
    new.append(t)
new.append("")
new.append(DECISIONS)
lines[idx + 1:idx + 1] = new
print("inserted %d paragraphs after line %d" % (len(new), idx + 1))

# §3b header -> the Hecleas note
j = next(i for i, l in enumerate(lines) if l.startswith("### 3b. Friendly-fire-flagged"))
lines[j + 1:j + 1] = ["", HECLEAS_NOTE]
print("Hecleas note added after the §3b header (line %d)" % (j + 1))

# the 19 air-drop rows: prepend the rule in force, mark the rest HISTORY
n_air = 0
for i, l in enumerate(lines):
    if "| air_drop_on_infantry |" in l:
        k = l.index("| air_drop_on_infantry |") + len("| air_drop_on_infantry |")
        lines[i] = l[:k] + " " + AIRDROP_NOTE + l[k:]
        n_air += 1
print("air-drop rows annotated:", n_air)

# the bombardment rows: append the decision to the row's last cell
n_bom = 0
for i, l in enumerate(lines):
    if ("| enemy_ground_melee_infantry |" in l or "| melee_skip_commanders |" in l) and l.rstrip().endswith("|"):
        body = l.rstrip()
        last = body.rindex("|")
        lines[i] = body[:last] + BOMB_NOTE + " |" + body[last + 1:]
        n_bom += 1
print("bombardment rows annotated:", n_bom)

out = "\n".join(lines).encode("utf-8")
assert out.count(b"\r") == 0
open(P, "wb").write(out)
print("lines after:", len(lines), "md5:", hashlib.md5(out).hexdigest())
