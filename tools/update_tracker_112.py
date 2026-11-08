"""Round 112 tracker update - the enemy-side lead dial + the two log fixes.

1. All 19 air-drop rows: the round-111 parenthesis is replaced by the round-112
   text (the fourth dial, the four-dial defaults, the tuning guide, the log
   format).
2. The trigger-family glossary row for air_drop_on_infantry is brought to round
   112.
3. A new dated Update paragraph is inserted after the harness-111 update.
"""
import io

P = r"C:/Users/vlady/Desktop/WH3_mod/docs/WH3_ability_tracker.md"
s = io.open(P, encoding="utf-8", newline="").read()
assert "\r" not in s
before = s

START = "((**round 111: THE MOVING-CASTER DIALS**"
END = "**only** when the caster's velocity is non-zero)"
assert s.count(START) == 19, s.count(START)

NEW_ROW = (
    "((**round 112: THE ENEMY-SIDE DIAL - PARITY WITH THE CASTER** - the user's fifth air-drop "
    "report, verbatim: *\"when I selected the other 3 and just left them standing, the zombies "
    "passed below the Sky-junks and they didn't drop the bomb.\"* THE DIAGNOSIS "
    "(`docs/WH3_skyjunk_diagnosis.md`, pack `651f12e61284cae472bb06bf3a66b87d`): all four bombers "
    "were **armed**, **airborne** and **evaluated on every poll** (the same click, four `AUTO ... now "
    "ON` lines, no airborne hold, no gate), and the three that never fired had the enemy's centre "
    "carried `v_enemy * 1.5 s = 3.45 m` **PAST** the hoverer, so the **PROJECTED** gap bottomed in "
    "the **5-10 m** band and was **LARGEST exactly when the enemy was underneath** (about 5 m at the "
    "pass, 10 m one second later). The **ENEMY** therefore gets its own share of the fall time, "
    "exactly as the caster got one in round 111: "
    "`enemy(t) = enemy + v_enemy * FOURTH.AIR_DROP_DELAY_S * FOURTH.AIR_DROP_ENEMY_LEAD` with "
    "**`AIR_DROP_ENEMY_LEAD = 0.3`** shipped - **0.0** = the enemy's **CURRENT** position (the "
    "ordnance lands straight down on where it is), **1.0** = the round-110/111 full carry that "
    "produced those misses, **0.3** = 0.45 s (about 1.0 m at 2.3 m/s, not 3.45 m) because the release "
    "is not instantaneous but a full 1.5 s of enemy travel is far too much. It scales the enemy's "
    "velocity term **ONLY**: the caster's two dials (`AIR_DROP_CASTER_DELAY_S` **1.5 s** x "
    "`AIR_DROP_CASTER_LEAD` **0.5**), the **6 m** bound, `FOURTH.AIR_DROP_INHERIT = false`, "
    "`air_only` / `no_melee` per row, the self-centred cast on the OWNER, every fail-closed read and "
    "the re-projecting pre-cast re-check are **UNCHANGED** (the re-check calls the SAME helper, so "
    "it reads the SAME four dials). **THE FOUR DIALS - DEFAULTS THAT SHIP:** `AIR_DROP_DELAY_S = "
    "1.5 s` and `AIR_DROP_ENEMY_LEAD = 0.3` (the enemy's lead time and its share); "
    "`AIR_DROP_CASTER_DELAY_S = 1.5 s` and `AIR_DROP_CASTER_LEAD = 0.5` (the caster's). **TUNING "
    "GUIDE - ONE DIAL PER TEST:** the **enemy walks THROUGH underneath** while the caster **hovers** "
    "-> lower `AIR_DROP_ENEMY_LEAD` **0.3 -> 0.0**; the **caster chases a STANDING target** and "
    "fires **early** -> lower `AIR_DROP_CASTER_LEAD` **0.5 -> 0.3 -> 0.0** (and only then "
    "`AIR_DROP_CASTER_DELAY_S` **1.5 -> 1.0**); fires **late when both move** -> raise the lead of "
    "the body that was moving (`AIR_DROP_CASTER_LEAD` 0.5 -> 0.8 -> 1.0, `AIR_DROP_ENEMY_LEAD` 0.3 -> "
    "0.6 -> 1.0); still **early while STATIONARY** (both parked) -> lower `AIR_DROP_DELAY_S`, which "
    "shrinks both bodies. **THE LOG (two diagnostic fixes from the same investigation):** every "
    "air-drop line - decision, `watch:`, skip, pre-cast re-check - is prefixed with the unit's UI id "
    "(`[1003] sky_junk_bomb watch: ...`) because four IDENTICAL units made the last diagnosis a "
    "231 MB log dive, and every one of them prints **ALL FOUR** dials "
    "(`delay=1.50s enemy_lead=0.30 delay_caster=1.50s caster_lead=0.50`); the `watch:` line prints "
    "the **EXACT** distances below 15 m - the 6 m bound used to sit inside a 5 m band, so `~5m` "
    "covered 5.00-9.99 m and the one number needed to choose a bound was destroyed exactly where it "
    "mattered - and keeps the 5 m band above 15 m where the number is context only"
)

out = []
at = 0
while True:
    i = s.find(START, at)
    if i < 0:
        out.append(s[at:])
        break
    j = s.find(END, i)
    assert j > 0
    out.append(s[at:i])
    out.append(NEW_ROW)
    at = j + len(END)
s = "".join(out)
assert s.count("((**round 112: THE ENEMY-SIDE DIAL") == 19
assert s.count(START) == 0

# ---------------------------------------------------------------- glossary row
G1_OLD = "| `air_drop_on_infantry` | **rounds 110-111** - an enemy INFANTRY unit"
G1_NEW = "| `air_drop_on_infantry` | **rounds 110-112** - an enemy INFANTRY unit"
assert s.count(G1_OLD) == 1
s = s.replace(G1_OLD, G1_NEW)

G2_OLD = ("and the **ENEMY** by **`FOURTH.AIR_DROP_DELAY_S = 1.5 s`** in full (a TUNABLE constant - "
          "no row carries a fall time)")
G2_NEW = ("and the **ENEMY** by **`FOURTH.AIR_DROP_DELAY_S = 1.5 s` x `FOURTH.AIR_DROP_ENEMY_LEAD = "
          "0.3`** (a TUNABLE constant - no row carries a fall time; **0.0** = the enemy's CURRENT "
          "position, **1.0** = the old full carry)")
assert s.count(G2_OLD) == 1
s = s.replace(G2_OLD, G2_NEW)

G3_OLD = ("The log prints, per decision, the two caster dials (`from delay_caster=1.50s lead=0.50`, "
          "plus `moving caster: lead=0.50 of 1.50s` only when the caster is moving), the momentum "
          "mode, both bodies' current point + velocity + source + projected point, the PROJECTED and "
          "instant separations and the bound, plus a `watch:` band line naming the nearest infantry "
          "and both velocities when nothing qualifies.")
G3_NEW = ("The log prints, per decision, ALL FOUR dials "
          "(`delay=1.50s enemy_lead=0.30 delay_caster=1.50s caster_lead=0.50`, plus "
          "`moving caster: lead=0.50 of 1.50s` only when the caster is moving), the momentum mode, "
          "both bodies' current point + velocity + source + projected point, the PROJECTED and "
          "instant separations and the bound; **every** air-drop line carries the unit's ui id "
          "(`[1003] sky_junk_bomb watch: ...`), and the `watch:` line prints the **EXACT** "
          "distances below 15 m (5 m bands only above 15 m) so the deciding number is never hidden.")
assert s.count(G3_OLD) == 1
s = s.replace(G3_OLD, G3_NEW)

G4_OLD = ("**`AIR_DROP_CASTER_LEAD` 0.0 = the caster treated as stationary, 1.0 = the round-110 "
          "over-lead; TUNING ORDER: early while moving -> lower the lead 0.5 -> 0.3 -> 0.0 (then the "
          "caster delay 1.5 -> 1.0); early while stationary -> lower the shared `AIR_DROP_DELAY_S`; "
          "never fires while moving -> raise the lead 0.5 -> 0.8 -> 1.0. ONE dial per test.**")
G4_NEW = ("**THE FOUR DIALS AND WHAT EACH SYMPTOM MEANS: enemy walks THROUGH underneath while the "
          "caster hovers -> lower `AIR_DROP_ENEMY_LEAD` 0.3 -> 0.0; caster chases a standing target "
          "and fires early -> lower `AIR_DROP_CASTER_LEAD` 0.5 -> 0.3 -> 0.0, then "
          "`AIR_DROP_CASTER_DELAY_S` 1.5 -> 1.0; fires late when both move -> raise the lead of the "
          "body that was moving (caster 0.5 -> 0.8 -> 1.0 / enemy 0.3 -> 0.6 -> 1.0); still early "
          "while stationary -> lower the shared `AIR_DROP_DELAY_S`. ONE dial per test.**")
assert s.count(G4_OLD) == 1
s = s.replace(G4_OLD, G4_NEW)

# ------------------------------------------------------- the dated Update entry
ANCHOR = ("installed pack md5 `651f12e61284cae472bb06bf3a66b87d`; `zz_probe_dist.pack` left installed "
          "(md5 `d4e67cfb8bc562c7d6f0ff742909c13d`, untouched).\n")
assert s.count(ANCHOR) == 1

UPDATE = (
    "**Update 2026-10-24 (harness 112 - THE ENEMY-SIDE LEAD DIAL, AND THE TWO LOG FIXES).** One "
    "field report is **implemented and shipping**: the user's fifth air-drop test - *\"when I "
    "selected the other 3 and just left them standing, the zombies passed below the Sky-junks and "
    "they didn't drop the bomb.\"* **THE DIAGNOSIS, AS ARITHMETIC** "
    "(`docs/WH3_skyjunk_diagnosis.md`): four Sky-junks (ui ids 1002-1005) were **armed in one "
    "click**, **airborne all battle**, **evaluated on every poll** with **infantry candidates "
    "present**, and there was **no gate, no refusal, no airborne hold** - the rule's release test was "
    "simply never satisfied. For a **stationary** caster the enemy's centre was projected the **full "
    "1.5 s** ahead - `v_enemy * 1.5 s` = **3.45 m** at the zombie's 2.3 m/s - so the **PROJECTED** "
    "gap bottomed at about **5 m** (just outside the 6 m bound) and **GREW to 10 m** as the block "
    "went by: the number was largest exactly when the enemy was underneath. The 6 m bound and the "
    "caster's dials were not at fault; the **enemy's lead** was, and it had no dial. **THE FIX - THE "
    "FOURTH DIAL:** `enemy_projected = enemy + v_enemy * FOURTH.AIR_DROP_DELAY_S * "
    "FOURTH.AIR_DROP_ENEMY_LEAD`, shipped at **0.3**. `0.0` puts the impact on the enemy's **current** "
    "position; `1.0` is the old full carry; `0.3` is **0.45 s** - about **1.0 m** at 2.3 m/s instead "
    "of 3.45 m - because the release is not instantaneous but a full 1.5 s of enemy travel is far "
    "too much. **THE FOUR DIALS AND THEIR DEFAULTS:** `AIR_DROP_DELAY_S` **1.5 s** / "
    "`AIR_DROP_ENEMY_LEAD` **0.3** (enemy), `AIR_DROP_CASTER_DELAY_S` **1.5 s** / "
    "`AIR_DROP_CASTER_LEAD` **0.5** (caster); the bound stays **6 m**. **TUNING GUIDE - ONE DIAL PER "
    "TEST:** enemy walks THROUGH underneath while the caster hovers -> `AIR_DROP_ENEMY_LEAD` **0.3 -> "
    "0.0**; caster chases a standing target and fires early -> `AIR_DROP_CASTER_LEAD` **0.5 -> 0.3 -> "
    "0.0**, then `AIR_DROP_CASTER_DELAY_S` **1.5 -> 1.0**; fires late when both move -> raise the "
    "lead of the body that was moving (**0.5 -> 0.8 -> 1.0** / **0.3 -> 0.6 -> 1.0**); still early "
    "while stationary -> lower the shared `AIR_DROP_DELAY_S`. **THE TWO DIAGNOSTIC FIXES (why the "
    "last investigation cost a 231 MB log dive):** (a) the `watch:` line now prints the **EXACT** "
    "projected and instant distances below **15 m** - the old 5 m band was COARSER than the 6 m "
    "decision margin, so `~5m` covered 5.00-9.99 m and destroyed the one number a new bound needs; "
    "the 5 m band stays above 15 m; (b) **every** air-drop line - decision, `watch:`, skip, pre-cast "
    "- is prefixed with the unit's **ui id** (`[1003] sky_junk_bomb watch: ...`) because four "
    "identical `wh3_main_cth_veh_sky_junk_0` units made \"which of the four?\" unanswerable from the "
    "log; and every one of them prints **ALL FOUR** dials "
    "(`delay=1.50s enemy_lead=0.30 delay_caster=1.50s caster_lead=0.50`). **KEPT EXACTLY:** the "
    "caster's two dials, the shared `AIR_DROP_DELAY_S`, the 6 m bound, `AIR_DROP_INHERIT = false`, "
    "`air_only` / `no_melee`, the self-centred cast, every fail-closed read and the re-projecting "
    "pre-cast re-check (same helper => same four dials). **NO COUNTS MOVED:** 689 entries / 742 keys, "
    "`air_drop_on_infantry` **12 entries / 19 keys**, 46 evaluators - behaviour and observability "
    "only. Spreadsheet `docs/WH3_abilities_master_v13_2026-10-18.xlsx` (+ `.ods`; v13 supersedes "
    "v12; **v1-v12 byte-unchanged**); round doc "
    "`docs/WH3_round112_airdrop_enemylead.md`; harness 112: **4492 checks / 0 failures** (run twice, "
    "byte-identical), red control (the round-111 build) **31 failures, ALL in the new section**; "
    "installed pack md5 `237702987893b8837d2dbb5df05d566b`; `zz_probe_dist.pack` left installed "
    "(md5 `d4e67cfb8bc562c7d6f0ff742909c13d`, untouched).\n"
)
s = s.replace(ANCHOR, ANCHOR + UPDATE)

assert s != before
io.open(P, "w", encoding="utf-8", newline="\n").write(s)
print("tracker updated:", len(before), "->", len(s))
print("rows carrying the round-112 rule:", s.count("((**round 112: THE ENEMY-SIDE DIAL"))
print("update paragraph present:", s.count("harness 112 - THE ENEMY-SIDE LEAD DIAL"))
