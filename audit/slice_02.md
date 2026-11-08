# WH3 ability-logic audit — slice 02 of 10 (ABILITIES entries 59–116, source order)

Counts: **58 audited · 0 flagged · 58 clean.**

Source of truth for the entries: the `local ABILITIES = {` table in
`C:\Users\vlady\Desktop\WH3_mod\mod_source\script\battle\mod\zz_test_deadly_onslaught.lua`,
entries 59–116 in table order (`halo_of_maidenly_wrath` .. `ostland_runefang`; 58 entries,
one database key each). Judged against the game's own ability data in
`%LOCALAPPDATA%\Temp\wh3\`: `unit_spec_abil.tsv` (target flags, passive/cooldowns/`ai_usage`),
`phase_junc.tsv` + `phases.tsv` (per-phase targets, durations, damage/heal/imbuement/attribute
fields), the `uieff\` stat-effect / attribute-effect / UI-effect localisation tables,
`unit_abilities(.loc).tsv` (type + names), and the invalid-target / invalid-usage /
auto-deactivate flag tables. All 58 tracker rows were cross-checked and agree.

Trigger mix and cast targets: all 58 cast on the owner itself — 57 ride the default
`perform_special_ability(key, owner)` call (`cast_target` left nil), and `glorious_death`
writes the owner explicitly; no ground key and no ally-target writer occurs in this slice.
Triggers: 51× `melee_unwavering` (in melee, not routing/wavering, self-cast),
4× `charge_or_melee` (`fangspike`, `heart_piercing`, `horn_of_the_first_beast`,
`morglor_the_mangler`), 1× `ushoran_health` (`ghoul_king_of_ushoran`),
1× `barrier_broken` (`eagle_feather_torc`), 1× `glorious_death`.

## FLAGGED

None. Every one of the 58 entries was judged a confident YES on all three checks: the cast
target matches the game's declared targeting (every key in this slice carries NO unit- or
ground-target flags — `target_friends` / `target_enemies` / `target_ground` / `target_self`
all false in `unit_spec_abil`, none passive — so a cast on the owner is the game's own
activation), the trigger fits the effect, and every trigger rides only friendly-unit reads
that exist. Closest calls, all examined in detail and resolved as sound (kept clean on
purpose):

- `helm_of_discord`, `inevitable_horror`, `locus_of_beguilement`, `banespear`,
  `hochland_runefang`, `nordland_runefang` — enemy-facing effects (phases with
  `target_enemies=true`, range 35–55 m), but the ABILITY rows declare no target selection:
  all four target flags false, `n_enemy=-1`, `ai_usage` in the melee-area family
  (`hex_melee_area` / `hex_melee_area_self`; Nordland's row is tagged `augment_melee_self`
  while its phase is the enemy damage area). These are self-centred melee-area hexes — the
  same no-flag shape as `everyone_has_their_price`, which slice 01 examined and cleared.
  Casting on self is the only activation form the data allows, and "in melee" is precisely
  when the enemies stand inside the area (the declared `*_melee_area` use).
- `glorious_death` — cast always on the owner. The game's phase is a self-centred
  self+allies "Cannot Die" aura (40 s, 55 m, `always_affect_self=true`, attribute
  `cannot_die`, `ai_usage=augment_defense_melee_area`), restricted to Slayer targets
  (`unit_is_not_slayer` invalid-target flag — satisfied: both carriers,
  `wh3_dlc25_dwf_cha_daemon_slayer` and `wh_main_dwf_cha_ungrim_ironfist`, are in the mod's
  game-data-derived Slayer key list). Firing while a Slayer is in melee fits the ability's
  declared melee use; self-cast is the game's only activation (no aim flags).
- `eagle_feather_torc` — a barrier-replenish effect (`barrier_heal_amount 0.1` on 1 s ticks,
  10 s; UI text "Replenishes barrier points") fired exactly when the unit's barrier is
  broken. There is no melee gate in the evaluator; the reads ride the shipped
  `context_value` helper (fail-closed on unreadable), and the barrier-broken condition is a
  recorded user decision.
- `fangspike`, `heart_piercing`, `horn_of_the_first_beast`, `morglor_the_mangler` —
  charge-component effects (charge bonus ×1.2–1.4 plus damage/attack components) riding
  `charge_or_melee`, which INCLUDES the charge window (the project's own correct-trigger
  convention for charge effects); the melee arm still delivers the non-charge components.
- `halo_of_maidenly_wrath` — a self-centred explosion (`aoe_centred_on_self`,
  friendly-fire-safe; UI bullets "Explosion does not affect friendly troops"), cast on self
  with an in-melee trigger — the same resolution as the shipped `evisceration` /
  `gaze_of_khorne` class.
- Other single calls examined: `helm_of_many_eyes` — the key name says "passive" but the
  game row is an ACTIVE augment (`passive=false`, 22 s / 90 s, `ai_usage=augment_melee`,
  +54 melee defence), so cast-in-melee-on-self is its active form; `primal_roar` — grants
  Rampage! to self and allies alongside +40 MA / +20 physical resistance, the attribute the
  game itself classifies positive and the ability `augment_melee_area`;
  `mumbo_jumbo_chant` — the `cant_move` flag sits only on the chanting caster's phase (the
  standard chant/wind-up choreography) while the allies phase buffs those around it.

No enemy-aimed entry (which the mod's reads cannot aim), no ally-unit-only-aimed entry, no
ground-target entry, no heal behind a melee gate, no charge-only effect behind a melee-only
trigger, and no passive entry occurs in this slice — the classes that would force a flag are
simply absent in entries 59–116.

## CLEAN

Judged a confident yes on all three checks (all 58):

59. halo_of_maidenly_wrath
60. hammer_axe_of_skoll
61. eagle_feather_torc
62. fangspike
63. ghoul_king_of_ushoran
64. glorious_death
65. legbiter
66. hellfire_sword
67. helm_of_discord
68. helm_of_many_eyes
69. heroic_killing_blow_2
70. heroic_killing_blow_dlc07
71. heroic_killing_blow_main
72. hydra_blade
73. inevitable_horror
74. karaghul
75. killing_blow_1
76. killing_blow
77. liarsbane
78. lightning_reflexes
79. locus_of_beguilement
80. locus_of_grace
81. locus_of_wrath
82. lucky_banner
83. mace_of_ulumak
84. mananns_luck
85. master_of_the_skies
86. mimic_waaagh
87. mimic_grom_waaagh
88. monstrous_strength
89. mortal_blow
90. mortal_blow_upgraded
91. mumbo_jumbo_chant
92. strike_of_nagash
93. nurgles_favoured_son
94. opal_amulet
95. oracle_of_eternity
96. pendant_of_slaanesh
97. plaguefathers_oration
98. primal_roar
99. puncture
100. heart_piercing
101. horn_of_the_first_beast
102. morglor_the_mangler
103. banespear
104. black_axe_of_krell
105. black_lotus
106. blessed_blade_of_ptra
107. daemonic_strength
108. dark_venom
109. doom_glaive
110. dragons_fang
111. drakwald_runefang
112. elixir_of_damnation
113. hochland_runefang
114. nordland_runefang
115. ostermark_runefang
116. ostland_runefang
