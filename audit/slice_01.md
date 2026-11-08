# Slice 01 audit - ABILITIES entries 1-58 (source order)

Counts: audited **58** | flagged **0** | clean **58**.

Source of truth for the entries: the `local ABILITIES = {` table in
`C:\Users\vlady\Desktop\WH3_mod\mod_source\script\battle\mod\zz_test_deadly_onslaught.lua`
(entries 1-58 in table order: `onslaught` .. `great_gutgouger`; 64 database keys in
total, counting the multi-key entries). Judged against the game's own ability data in
`%LOCALAPPDATA%\Temp\wh3\` (`unit_spec_abil.tsv` targeting/flags, `phase_junc.tsv` +
`phases.tsv` effect phases, `grouped2.json` effect-family/target classification,
`unit_abilities` / UI-effect localisation tables for names and effect bullets);
the tracker rows for all 64 keys were cross-checked and match.

## FLAGGED

None. Every one of the 58 entries was judged a confident YES on all three checks:
the cast target matches the game's declared targeting, the trigger fits the effect,
and the trigger rides only self-side engine reads that exist. Closest calls,
all examined and resolved as sound (kept clean on purpose):

- `evisceration`, `gaze_of_khorne`, `giant_leap` - the game declares self-centred
  damage bursts (`aoe_centred_on_self`, cast on self, `cant_move`); casting on self
  is the correct form and "in melee" is precisely the state where enemies stand
  inside the burst.
- `everyone_has_their_price` - a self-centred hex aura (`hex_melee_area_self`,
  the same spec shape as its 15 siblings: no target flags, `n_enemy=-1`, range 35);
  cast on self with an in-melee (enemy-present) trigger is the declared use.
- `stand_your_ground`, 2nd key `wh3_dlc24_character_abilities_tacticians_stand_your_ground` -
  the game declares `target_ground=true`; the mod casts it through its ground form
  (`perform_special_ability_ground`) at the unit's own position, a valid target
  (`min_range=0`, aura affects self + friends, range 35).
- `foe_seeker` - "tired" trigger; the ability's own phase data carries a fatigue
  recovery component (`fatigue_change_ratio=-0.01` on all three keys), the fatigue
  read (`battle_unit:fatigue_state`) exists and is implemented fail-closed, and the
  trigger was a recorded user decision.

No enemy-aimed entry (which the mod's reads cannot aim), no ally-unit-only-aimed
entry, no heal, no charge-only effect and no passive entry occurs in this slice -
the classes that would force a flag (not implementable reads, wrong cast target,
trigger/effect mismatch) are simply absent in entries 1-58.

## CLEAN

1. onslaught
2. foe_seeker
3. hammer_of_sigmar
4. stand_your_ground
5. blood_lust
6. aether_sword
7. apocalyptic_vision
8. armour_of_gazrakh
9. aura_of_quetzl
10. axe_of_dargo
11. axe_of_grom
12. axes_of_kadrin
13. azhags_ard_armour
14. ballet_of_blows
15. bear_fang_talisman
16. beastslaver
17. blade_of_bel_korhadris
18. blades_of_shang_yang
19. bloodstorm_blades
20. brass_body
21. change_or_die
22. claws_of_mourkain
23. cloak_of_mists_and_shadows
24. coat_in_blood
25. creature_killer
26. da_great_un_iz_ere
27. daemonblade
28. daemonshield
29. dagger_of_malice
30. dark_protection
31. darkwalker
32. deathbringer
33. strike_of_nehekhara
34. dolorous_blade
35. dragon_spear
36. dreaded_duelist
37. dwarf_gouger
38. enrage
39. entice
40. everyone_has_their_price
41. evisceration
42. eye_jabber
43. eye_gouger
44. eye_of_the_storm
45. faiths_bastion
46. fangsword_of_eltharion
47. feint_and_reposte
48. filth_mace
49. fluid_injection
50. gaze_of_khorne
51. fury_of_the_land
52. fury_of_ursun
53. ghal_maraz
54. giant_leap
55. gitsnik
56. gotrek_doom
57. shield_of_faith_upgraded
58. great_gutgouger
