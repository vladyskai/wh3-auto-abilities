# Open points (working doc)

Started 2026-11-20, after round 182. A living list: add a line under **Ruling / notes** and I pick it up from the file on
disk. Closed items move to section 9 with the round that closed them.

| # | Open point | Status | Ruling / notes |
|---|---|---|---|
| 1 | **In-game test of rounds 176-182.** Nothing built since round 175 has been seen in a battle (Executioner, Land Mine, Surprise Squig!, the range fixes, the new ally and heal families, ...). The next battle log starts at byte 822,999,135. | DEFERRED | User 2026-11-20: "We'll do the in-game tests later". |
| 2 | **Enemy-charge detection test.** How well the charge read sees an enemy charge. Proposed test: Markus Wulfhart's Hunter's Snare (skill `wh2_dlc13_skill_emp_wulfhart_personal_5`) in a skirmish against the AI. | WAITING (user) | Goes with item 1. |
| 3 | **The 55 abilities shut by old rules** (19 "own-troop damage", 22 collection-time "unsuitable", 7 flanking / stealth, 5 mutual exclusivity, 2 bombardment), never ruled one by one. | DONE (rounds 183-186: 52 built, 12 closed; Warpstorm Scroll re-ruled in round 186) | `docs\WH3_rule_shut_review_2026-11-20.md` (user 2026-11-20: "Let's review those 55 abilities"). The live, commentable copy with a Ruling dropdown per row is the Claude Docs doc "Rule-shut abilities review" (https://claude.ai/artifact/HvLbtHifSNsbH8aeWcER5h); rulings are read from there. |
| 4 | **Your 9 "skipped (revisit)" abilities.** | DONE (round 185: all 9 built) | Same doc, section 7. |
| 5 | **Inventory loose ends.** Grombrindal Has No Fear and Scry Orb (castable, hidden under `source_type = passive`) need workbook rows; the five runes seen only on the spell bar (Breaking, Slowness, Speed, Negation, Oath and Steel) need a workbook status. | OPEN | Next sign-off round. |
| 6 | **Deferred by you (2026-11-01):** Silver Horn of Vengeance, Grombrindal Has No Fear. | DONE | Silver Horn built in round 185 (row 40, 'B'); Grombrindal Has No Fear still deferred. |
| 7 | **"A fast enemy nearby" does not check direction.** `fast_enemy_near` reads fast + moving + within 40 m; it does not check that the enemy is coming toward us (flagged in round 172). | NEEDS A RULING | |
| 8 | **Casting before the first shot.** The shooting triggers wait for the cast point (first shot + half a reload). Casting a shooting buff just before the first volley needs its own ruling. | NEEDS A RULING | |
| 9 | **Game rules the mod still ignores** (overnight audit, section 3): the target-morale rule of Transfix and Ghostly Howl; the "healing cap reached" rule; the ground-only / flying-only caster rules of Eye and Wrath of the Storm; the Moulder, Remouldered and Shock Collar unit sets. | OPEN | |
| 10 | **Feature ideas** (overnight audit, section 5, all optional): a "waiting for ..." line in each badge tooltip; an army-wide ALL button; an army-wide switch per ability; priority between competing abilities; learning the real recharge from the ability button; an end-of-battle summary; remembering arming across battles. | IDEAS | |
| 11 | **Stances.** Never automated for now (user 2026-11-01); a stance chooser is last priority. The 5 mutually exclusive abilities of the review (Zhangu War Drum, Festus) behave like stances. | PARKED | |
| 12 | **The charge hold uses the table recharge,** about 37 s too long in your campaign (you chose "selection fix only" on 2026-11-03; learning the recharge from the button was option a). | PARKED | Same as idea "learning the real recharge" in item 10. |

## Closed

(none yet)
