# Map probe, battle 1 (2026-11-13): findings

Battle: Empire against Vampire Counts, 40 units a side, map snapshots from 16 s to 230 s (108 snapshots, 8,640 rows),
log cut from byte 501,336,775 (`archive\logs\battle_20261113_map_probe1.txt`). No poll error.

1. **Every read answers on both sides** (position, bearing, width, men, health, value, class, visibility, melee,
   moving, flying; enemy routing), except `position_of_officer()`: 0% on both sides. `ordered_width()` works on enemies.
2. **Visibility works.** 101 enemy rows of LIVING units read `vis=0` (deployment and fog, up to 114 s); dead units
   also read `vis=0`.
3. **`strategic_value()` is a live value.** A full-strength unit reads close to its cost or above it (the War Wagon
   1,900 against a cost of 1,900; the Lahmian Lord 2,985 against 1,400, items and skills included). It drops as the unit
   loses men and health (correlation with cost 0.49, with cost x health 0.70), and a dead unit reads 0.
4. **The facing assumption is right.** Across 2,490 moves the travel direction was a median 8.6 deg from
   (sin b, cos b); 76% within 30 deg.
5. **`is_infantry()` and `unit_class()` are not an infantry test**: both call Fell Bats, Devils of Swartzhafen, the
   Varghulf and the Zombie Dragon infantry (`inf_mel`). The analyser now uses: infantry class AND not in the generated
   large set AND not flying AND at least 10 men.
6. **Dead units stay in both lists** with `men=0/...` and `sv=0`.
7. **Footprints:** ranked infantry depths look sane (Halberdiers 19 m wide x 16 m deep, zombies 31 x 14 m). Vehicles,
   cavalry and monsters are now taken as squares (the first pass gave land ships 575 m of depth).
8. **Blobs:**
   - The biggest one (172-190 s, about 790 enemy soldiers in a 20 m circle) was seven Vampire Counts infantry units
     mobbing one of our Flagellant units that had 11 of 120 men left. A blob trigger without the friendly check would
     have hit our own unit.
   - The best SAFE blobs (none of ours within R + 5 m) came while the enemy line advanced together: 96-108 s, 300-400
     zombies, skeletons and Sternsmen in a 15 m circle; at 230 s, 556 in a 20 m circle.

# Battlefield map probe report

Snapshots: 108; rows: 8640 (ours 4320, enemy 4320). Alliance read: 1.

## 1. Readability (share of rows where the read answered)

| Read | Ours | Enemy |
|---|---:|---:|
| x | 100% | 100% |
| ox | 0% | 0% |
| bearing | 100% | 100% |
| width | 100% | 100% |
| men_alive | 100% | 100% |
| hp | 100% | 100% |
| sv | 100% | 100% |
| inf | 100% | 100% |
| vis | 100% | 100% |
| melee | 100% | 100% |
| moving | 100% | 100% |
| fly | 100% | 100% |
| routing | 0% | 100% |

Enemy visibility values: {'1': 3880, '0': 440}.

## 2. Value: strategic_value() next to the game's cost

Rows with both: 8532. Correlation with cost: 0.49; with cost x health: 0.70.

| Unit type | Cost | strategic_value (min / max) |
|---|---:|---|
| wh3_dlc25_emp_veh_marienburg_land_ship_ror | 2500.0 | 0.5 / 2300.0 |
| wh3_dlc25_emp_veh_steam_tank_volley_gun | 2400.0 | 1.7 / 2560.0 |
| wh3_dlc25_emp_veh_marienburg_land_ship | 2100.0 | 14.3 / 2760.0 |
| wh3_dlc29_vmp_mon_zombie_dragon | 2000.0 | 7.2 / 2380.0 |
| wh2_dlc13_emp_veh_war_wagon_ror_0 | 1900.0 | 11.2 / 1900.0 |
| wh_dlc04_emp_cav_royal_altdorf_gryphites_0 | 1850.0 | 0.0 / 1850.0 |
| wh_dlc04_vmp_cav_chillgheists_0 | 1700.0 | 596.3 / 1900.0 |
| wh_dlc04_vmp_veh_claw_of_nagash_0 | 1700.0 | 2017.4 / 2470.0 |
| wh_dlc02_vmp_cav_blood_knights_0 | 1650.0 | 1326.6 / 1980.0 |
| wh3_main_vmp_blood_knights_sword_shield | 1550.0 | 612.4 / 1980.0 |
| wh_main_emp_cav_demigryph_knights_1 | 1500.0 | 78.4 / 1680.0 |
| wh2_dlc11_vmp_cha_bloodline_lahmian_lord_2 | 1400.0 | 1443.3 / 2985.0 |
| wh3_dlc29_vmp_cav_drakenhof_templars | 1400.0 | 2069.3 / 2180.0 |
| wh_main_vmp_cav_hexwraiths | 1400.0 | 0.0 / 1630.0 |
| wh_main_vmp_mon_varghulf | 1400.0 | 1266.6 / 1630.0 |
| wh3_dlc29_vmp_inf_lahmian_handmaidens_shadow | 1350.0 | 1302.2 / 1530.0 |
| wh_dlc03_emp_cha_wizard_beasts_3 | 1300.0 | 0.0 / 2520.0 |
| wh3_dlc29_vmp_inf_lahmian_handmaidens_death | 1300.0 | 983.8 / 1430.0 |
| wh_dlc04_vmp_cav_vereks_reavers_0 | 1300.0 | 1000.2 / 1370.0 |
| wh_dlc04_vmp_mon_devils_swartzhafen_0 | 1300.0 | 0.0 / 1300.0 |
| wh3_dlc25_emp_cav_knights_of_the_black_rose | 1250.0 | 0.0 / 1480.0 |
| wh3_dlc25_emp_inf_hochland_long_rifles_ror | 1200.0 | 0.0 / 1350.0 |
| wh2_pro08_neu_cha_gotrek | 1150.0 | 0.0 / 1875.0 |
| wh_dlc04_vmp_inf_sternsmen_0 | 1150.0 | 1211.7 / 1220.0 |
| wh3_dlc23_neu_cha_ulrika_warhorse | 1100.0 | 0.0 / 2920.0 |

## 3. Footprints (estimated depth; width is the engine's ordered width)

| Unit type | Side | Width m | Men | Est. depth m | How |
|---|---|---:|---:|---:|---|
| wh2_dlc13_emp_cha_huntsmarshal_0 | P | 2.0 | 1 | 2.0 | single |
| wh2_pro08_neu_cha_gotrek | P | 2.0 | 1 | 2.0 | single |
| wh_dlc03_emp_cha_wizard_beasts_3 | P | 2.4 | 1 | 2.4 | single |
| wh3_dlc23_neu_cha_ulrika | P | 2.0 | 1 | 2.0 | single |
| wh3_dlc23_neu_cha_ulrika_warhorse | P | 2.0 | 1 | 2.0 | single |
| wh_main_emp_inf_halberdiers | P | 19.1 | 120 | 16.0 | est |
| wh_dlc04_emp_inf_flagellants_0 | P | 20.5 | 120 | 17.0 | est |
| wh_dlc04_emp_inf_tattersouls_0 | P | 25.3 | 160 | 17.0 | est |
| wh_main_emp_inf_greatswords | P | 23.5 | 120 | 15.8 | est |
| wh_dlc04_emp_inf_free_company_militia_0 | P | 18.9 | 120 | 17.0 | est |
| wh_main_emp_inf_handgunners | P | 18.0 | 90 | 11.9 | est |
| wh_dlc04_emp_inf_stirlands_revenge_0 | P | 8.7 | 120 | 32.0 | est |
| wh2_dlc13_emp_inf_huntsmen_ror_0 | P | 26.3 | 90 | 21.6 | est |
| wh3_dlc25_emp_inf_hochland_long_rifles_ror | P | 18.8 | 32 | 11.2 | est |
| wh3_dlc25_emp_cav_knights_of_the_black_rose | P | 28.4 | 60 | 28.4 | square (not ranked infantry) |
| wh_main_emp_cav_demigryph_knights_1 | P | 27.0 | 32 | 27.0 | square (not ranked infantry) |
| wh_dlc04_emp_cav_royal_altdorf_gryphites_0 | P | 27.0 | 32 | 27.0 | square (not ranked infantry) |
| wh_main_emp_cav_outriders_0 | P | 25.4 | 60 | 25.4 | square (not ranked infantry) |
| wh_main_emp_cav_outriders_1 | P | 25.4 | 48 | 25.4 | square (not ranked infantry) |
| wh2_dlc13_emp_veh_war_wagon_ror_0 | P | 11.4 | 8 | 11.4 | square (not ranked infantry) |
| wh3_dlc25_emp_veh_marienburg_land_ship | P | 5.8 | 23 | 5.8 | square (not ranked infantry) |
| wh3_dlc25_emp_veh_steam_tank_volley_gun | P | 2.0 | 3 | 2.0 | single |
| wh3_dlc25_emp_veh_marienburg_land_ship_ror | P | 5.8 | 22 | 5.8 | square (not ranked infantry) |
| wh2_dlc11_vmp_cha_bloodline_lahmian_lord_2 | E | 2.0 | 1 | 2.0 | single |
| wh_main_vmp_cha_necromancer_0 | E | 2.0 | 1 | 2.0 | single |
| wh3_dlc29_vmp_cha_necromancer_undeath_barded_nightmare | E | 2.0 | 1 | 2.0 | single |
| wh_main_vmp_inf_zombie | E | 31.4 | 160 | 14.4 | est |
| wh_main_vmp_inf_skeleton_warriors_1 | E | 29.3 | 160 | 12.8 | est |
| wh3_dlc29_vmp_inf_spirit_host | E | 39.4 | 200 | 14.4 | est |
| wh_dlc04_vmp_inf_feasters_in_the_dusk_0 | E | 37.3 | 120 | 11.4 | est |
| wh_main_vmp_inf_cairn_wraiths | E | 42.0 | 60 | 9.4 | est |
| wh_main_vmp_inf_grave_guard_1 | E | 32.5 | 120 | 10.5 | est |
| wh_dlc04_vmp_inf_sternsmen_0 | E | 29.3 | 120 | 9.6 | est |
| wh3_dlc29_vmp_inf_lahmian_handmaidens_death | E | 31.4 | 32 | 10.0 | est |
| wh3_dlc29_vmp_inf_lahmian_handmaidens_shadow | E | 31.4 | 32 | 10.0 | est |
| wh_dlc04_vmp_cav_vereks_reavers_0 | E | 42.0 | 60 | 42.0 | square (not ranked infantry) |
| wh3_dlc29_vmp_cav_drakenhof_templars | E | 22.4 | 32 | 22.4 | square (not ranked infantry) |
| wh_main_vmp_cav_hexwraiths | E | 42.0 | 60 | 42.0 | square (not ranked infantry) |
| wh3_main_vmp_blood_knights_sword_shield | E | 42.0 | 60 | 42.0 | square (not ranked infantry) |
| wh_dlc02_vmp_cav_blood_knights_0 | E | 42.0 | 60 | 42.0 | square (not ranked infantry) |
| wh_dlc04_vmp_cav_chillgheists_0 | E | 42.0 | 60 | 42.0 | square (not ranked infantry) |
| wh_main_vmp_mon_fell_bats | E | 33.2 | 60 | 32.0 | est |
| wh_dlc04_vmp_mon_devils_swartzhafen_0 | E | 32.8 | 16 | 32.8 | square (not ranked infantry) |
| wh_main_vmp_mon_varghulf | E | 4.4 | 1 | 4.4 | single |
| wh3_dlc29_vmp_mon_zombie_dragon | E | 3.5 | 1 | 3.5 | single |
| wh_dlc04_vmp_veh_claw_of_nagash_0 | E | 2.0 | 18 | 2.0 | single |

## 4. Blobs: the best circle each snapshot (enemy infantry soldiers inside; ours within R + 5 m)

Bearing assumption: facing (sin b, cos b) on X/Z.

### Radius 10 m

| t (s) | Enemy soldiers inside | Units | Centre (x, z) | Ours near |
|---:|---:|---|---|---:|
| 186.0 | 456 | zombie(88), 1(82), host(106), 1(62), 0(96), death(8), death(14) | -167, -261 | 11 |
| 184.0 | 451 | zombie(88), 1(107), host(106), 1(29), 0(91), death(17), death(13) | -167, -260 | 10 |
| 178.0 | 433 | zombie(101), 1(70), host(79), 1(57), 0(86), death(19), death(22) | -169, -264 | 15 |
| 180.0 | 404 | zombie(82), 1(88), host(42), 1(67), 0(86), death(19), death(19) | -169, -264 | 15 |
| 176.0 | 404 | zombie(76), 1(95), host(72), 1(43), 0(91), death(8), death(19) | -168, -262 | 15 |
| 188.0 | 399 | zombie(88), 1(82), host(92), 1(29), 0(72), death(17), death(19) | -166, -266 | 10 |
| 210.0 | 396 | zombie(95), host(99), 1(77), 0(91), death(19), death(15) | -171, -268 | 2 |
| 208.0 | 394 | zombie(95), host(106), 1(86), 0(67), death(20), death(19) | -167, -266 | 2 |
| 220.0 | 391 | zombie(90), host(92), 1(96), 0(86), death(9), death(19) | -164, -270 | 2 |
| 212.0 | 376 | zombie(95), host(84), 1(77), 0(86), death(17), death(17) | -165, -267 | 2 |
| 214.0 | 371 | zombie(89), host(92), 1(72), 0(82), death(17), death(19) | -162, -270 | 2 |
| 174.0 | 369 | zombie(88), 1(82), host(58), 1(62), 0(67), death(6), death(5) | -169, -267 | 15 |
| 206.0 | 366 | zombie(88), host(99), 1(58), 0(82), death(20), death(19) | -167, -265 | 2 |
| 216.0 | 358 | zombie(95), host(99), 1(34), 0(91), death(20), death(19) | -163, -268 | 2 |
| 222.0 | 355 | zombie(90), host(99), 1(82), 0(72), death(13) | -168, -267 | 2 |

### Radius 15 m

| t (s) | Enemy soldiers inside | Units | Centre (x, z) | Ours near |
|---:|---:|---|---|---:|
| 184.0 | 719 | zombie(145), 1(152), host(141), 1(114), 0(120), death(27), death(20) | -170, -265 | 13 |
| 186.0 | 712 | zombie(158), 1(145), host(127), 1(114), 0(120), death(23), death(24) | -171, -265 | 11 |
| 188.0 | 677 | zombie(158), 1(107), host(134), 1(109), 0(120), death(23), death(26) | -170, -266 | 10 |
| 180.0 | 661 | zombie(126), 1(158), host(120), 1(76), 0(120), death(29), death(32) | -166, -260 | 15 |
| 178.0 | 650 | zombie(114), 1(145), host(143), 1(67), 0(120), death(29), death(32) | -165, -262 | 15 |
| 176.0 | 642 | zombie(120), 1(158), host(136), 1(67), 0(120), death(12), death(29) | -166, -260 | 15 |
| 174.0 | 618 | zombie(133), 1(158), host(130), 1(48), 0(120), death(3), death(26) | -166, -260 | 15 |
| 148.0 | 611 | zombie(140), 1(153), host(145), 1(38), 0(86), death(20), death(29) | -171, -262 | 32 |
| 210.0 | 603 | zombie(126), host(176), 1(120), 0(120), death(29), death(32) | -170, -268 | 2 |
| 220.0 | 601 | zombie(154), host(155), 1(120), 0(120), death(25), death(28) | -164, -269 | 2 |
| 208.0 | 598 | zombie(126), host(176), 1(120), 0(120), death(30), death(26) | -167, -266 | 2 |
| 146.0 | 595 | zombie(159), 1(159), host(123), 1(14), 0(101), death(17), death(22) | -175, -263 | 32 |
| 190.0 | 594 | zombie(158), 1(88), host(141), 1(62), 0(96), death(26), death(23) | -170, -270 | 10 |
| 150.0 | 593 | zombie(158), 1(158), host(80), 1(43), 0(106), death(23), death(26) | -176, -264 | 30 |
| 182.0 | 592 | zombie(145), 1(158), host(84), 1(48), 0(115), death(17), death(24) | -168, -264 | 15 |

### Radius 20 m

| t (s) | Enemy soldiers inside | Units | Centre (x, z) | Ours near |
|---:|---:|---|---|---:|
| 186.0 | 792 | zombie(158), 1(158), host(176), 1(119), 0(120), death(29), death(32) | -169, -266 | 11 |
| 184.0 | 789 | zombie(158), 1(158), host(176), 1(119), 0(120), death(29), death(29) | -168, -261 | 13 |
| 178.0 | 789 | zombie(158), 1(152), host(179), 1(119), 0(120), death(29), death(32) | -169, -262 | 15 |
| 188.0 | 787 | zombie(158), 1(158), host(176), 1(114), 0(120), death(29), death(32) | -168, -269 | 10 |
| 176.0 | 782 | zombie(158), 1(158), host(179), 1(114), 0(120), death(21), death(32) | -168, -262 | 15 |
| 190.0 | 781 | zombie(158), 1(152), host(176), 1(114), 0(120), death(29), death(32) | -169, -268 | 10 |
| 180.0 | 780 | zombie(158), 1(158), host(169), 1(114), 0(120), death(29), death(32) | -165, -262 | 15 |
| 174.0 | 777 | zombie(158), 1(158), host(181), 1(109), 0(120), death(19), death(32) | -169, -261 | 15 |
| 172.0 | 763 | zombie(158), 1(152), host(159), 1(119), 0(120), death(29), death(26) | -169, -264 | 15 |
| 196.0 | 750 | zombie(158), 1(133), host(169), 1(109), 0(120), death(29), death(32) | -166, -269 | 6 |
| 148.0 | 746 | zombie(159), 1(159), host(145), 1(115), 0(115), death(21), death(32) | -173, -266 | 32 |
| 182.0 | 745 | zombie(158), 1(158), host(148), 1(114), 0(120), death(21), death(26) | -171, -261 | 15 |
| 194.0 | 737 | zombie(158), 1(133), host(176), 1(90), 0(120), death(28), death(32) | -165, -268 | 7 |
| 152.0 | 735 | zombie(158), 1(158), host(138), 1(101), 0(120), death(29), death(32) | -170, -264 | 30 |
| 146.0 | 729 | zombie(159), 1(159), host(152), 1(101), 0(110), death(17), death(31) | -173, -267 | 32 |

### Radius 10 m - SAFE (none of ours within R + 5 m)

| t (s) | Enemy soldiers inside | Units | Centre (x, z) | Ours near |
|---:|---:|---|---|---:|
| 106.0 | 305 | zombie(90), 1(115), 0(96), death(5) | -187, -262 | 0 |
| 108.0 | 298 | zombie(96), 1(109), host(8), 0(82), death(3) | -186, -263 | 0 |
| 102.0 | 266 | zombie(90), 1(96), 0(77), death(3) | -190, -261 | 0 |
| 104.0 | 259 | zombie(83), 1(96), 0(77), death(3) | -190, -261 | 0 |
| 98.0 | 249 | zombie(77), 1(96), 0(72), death(5) | -193, -262 | 0 |
| 100.0 | 249 | zombie(70), 1(115), 0(62), death(1) | -192, -262 | 0 |
| 96.0 | 248 | zombie(83), 1(90), 0(72), death(3) | -195, -260 | 0 |
| 116.0 | 245 | zombie(83), 1(102), host(16), 0(43) | -187, -266 | 0 |
| 110.0 | 235 | zombie(96), 1(96), 0(43) | -187, -266 | 0 |
| 118.0 | 230 | zombie(90), 1(96), 0(43), death(1) | -186, -266 | 0 |
| 230.0 | 223 | zombie(96), host(106), 0(19), death(2) | -165, -268 | 0 |
| 228.0 | 220 | zombie(96), host(28), 0(82), death(2), death(12) | -154, -273 | 1 |
| 214.0 | 217 | zombie(25), host(70), 1(24), 0(62), death(20), death(15) | -155, -275 | 1 |
| 112.0 | 205 | zombie(96), 1(90), 0(19) | -185, -270 | 0 |
| 88.0 | 198 | zombie(96), 1(102) | -197, -268 | 0 |

### Radius 15 m - SAFE (none of ours within R + 5 m)

| t (s) | Enemy soldiers inside | Units | Centre (x, z) | Ours near |
|---:|---:|---|---|---:|
| 230.0 | 424 | zombie(128), host(176), 1(29), 0(77), death(15) | -165, -268 | 0 |
| 98.0 | 404 | zombie(154), 1(160), 0(82), death(9) | -192, -267 | 0 |
| 102.0 | 392 | zombie(147), 1(160), 0(82), death(3) | -192, -267 | 0 |
| 100.0 | 383 | zombie(154), 1(160), 0(67), death(2) | -193, -267 | 0 |
| 96.0 | 377 | zombie(154), 1(160), 0(58), death(6) | -194, -268 | 0 |
| 104.0 | 355 | zombie(122), 1(128), 0(96), death(9) | -190, -263 | 0 |
| 94.0 | 332 | zombie(147), 1(160), 0(24), death(1) | -196, -268 | 0 |
| 92.0 | 330 | zombie(160), 1(160), 0(10) | -198, -268 | 0 |
| 214.0 | 315 | zombie(25), 1(83), host(77), 1(24), 0(62), death(26), death(17) | -149, -276 | 1 |
| 88.0 | 315 | zombie(154), 1(160), death(1) | -199, -267 | 0 |
| 228.0 | 309 | zombie(96), 1(13), host(42), 0(101), death(25), death(32) | -149, -274 | 1 |
| 84.0 | 307 | zombie(147), 1(160) | -206, -267 | 0 |
| 226.0 | 307 | zombie(70), 1(58), host(49), 0(82), death(21), death(27) | -149, -272 | 1 |
| 82.0 | 275 | zombie(134), 1(141) | -211, -267 | 0 |
| 68.0 | 266 | zombie(160), 1(106) | -273, -268 | 0 |

### Radius 20 m - SAFE (none of ours within R + 5 m)

| t (s) | Enemy soldiers inside | Units | Centre (x, z) | Ours near |
|---:|---:|---|---|---:|
| 230.0 | 556 | zombie(160), host(176), 1(101), 0(96), death(24) | -168, -266 | 0 |
| 228.0 | 457 | zombie(109), 1(115), host(56), 0(115), death(30), death(32) | -144, -271 | 1 |
| 226.0 | 398 | zombie(77), 1(109), host(56), 0(96), death(31), death(29) | -145, -274 | 1 |
| 94.0 | 381 | zombie(160), 1(160), 0(58), death(3) | -198, -268 | 0 |
| 82.0 | 334 | zombie(160), 1(160), 0(14) | -211, -267 | 0 |
| 84.0 | 334 | zombie(160), 1(160), 0(14) | -206, -267 | 0 |
| 80.0 | 302 | zombie(141), 1(147), 0(14) | -213, -266 | 0 |
| 68.0 | 280 | zombie(160), 1(120) | -273, -268 | 0 |
| 70.0 | 280 | zombie(160), 1(120) | -267, -266 | 0 |
| 224.0 | 279 | zombie(19), 1(160), host(7), 0(48), death(31), death(14) | -140, -274 | 0 |
| 72.0 | 269 | zombie(154), 1(115) | -268, -271 | 0 |
| 66.0 | 262 | zombie(141), 1(6), 1(115) | -272, -261 | 0 |
| 218.0 | 262 | zombie(32), 1(83), host(49), 0(62), death(19), death(17) | -143, -278 | 1 |
| 48.0 | 240 | 1(120), 0(120) | -236, -194 | 0 |
| 222.0 | 237 | zombie(6), 1(154), host(14), 0(29), death(29), death(5) | -140, -277 | 0 |

