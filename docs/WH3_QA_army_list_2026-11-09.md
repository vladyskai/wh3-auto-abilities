# QA army list for rounds 132 to 138 (2026-11-09)

**Purpose:** prove in a real battle the trigger paths shipped in rounds 132 to 138, which so far are proven only by
the harness. You build and fight the battles; I read the log afterwards. The installed pack is md5
`4d69206141c5d9eb89506fd0ed1064bd` (round 138).

**How it was built:**
- 99 abilities changed trigger or target filter since round 131 (the diff between the pre-round-132 source and today).
- Your battle logs show 231 abilities that have appeared on your wheels ("badge ...: shown"); 21 of the 99 are among
  them.
- The battles below cover every NEW code path at least once, preferring units you already field (mostly Empire).
- Units come from `land_units_to_unit_abilites_junctions`.
- I cannot see which items the custom-battle item lists offer. Items marked *(item)* need a check on the screen,
  with a fallback named.

## Battle 1: Empire (your own faction), vs Warriors of Chaos or Beastmen

Covers four trigger families. Arm each ability (badge **A**) before deployment ends.

| Unit | Ability to arm | Trigger (round) | What to do | Log line to look for |
|---|---|---|---|---|
| General of the Empire | Charmed Shield *(item; you used it before)* | melee or under fire (133) | let enemy missiles hit him before he is in melee | `the caster is under missile fire, cast on self` |
| General of the Empire (or any hero) | Potion of Speed *(item; if absent, skip: battle 3 covers charge-only)* | charge only (134) | order an ATTACK on an enemy 20 to 50 m away | `reason: charging (charge only)` |
| Huntsman General | Crown of Command *(item; you used it before)* | cast on the wavering ally (137) | let a cheap unit near him start wavering (outnumbered, flanked) | `wavering ally in range, cast on ally` |
| Witch Hunter | Slippery | charge, else melee (134) | order an attack from 20 to 50 m away | `reason: charging (gap=` |
| Handgunners, Swordsmen, Free Company | - | - | line and bait | - |

**The enemy army needs:**
- missile units (marauder horsemen with javelins, or Chaos Forsaken archers if Beastmen), so the General is shot;
- strong melee, so your cheap units waver;
- a Lord.

## Battle 2: Skaven, vs any melee-heavy army

Covers the new morale aura (round 137); Skaven waver often.

| Unit | Ability to arm | Trigger | What to do | Log line |
|---|---|---|---|---|
| Warlord | Rally! | caster or ally in the aura wavering (137) | keep him within about 20 m of Clanrats or Skavenslaves that are losing | `wavering aura:` |
| Grey Seer on Screaming Bell (plague variant) | Unholy Clamour | the same, whole army (137) | anywhere; it reacts to any wavering unit | `wavering aura: a friendly unit (...) is wavering, the whole army is covered` |
| Clanrats, Skavenslaves | - | - | they are the units that waver | - |

## Battle 3: Warriors of Chaos, vs Empire (with cavalry, a Steam Tank, Handgunners and a Lord)

| Unit | Ability to arm | Trigger | What to do | Log line |
|---|---|---|---|---|
| Hellcannon | Blooood! | charge only (134) | order it to ATTACK an enemy 20 to 50 m away | `charging (charge only)` |
| Hellcannon | Boom! | the unit shooting (132) | let it fire; it casts after its first shot plus half a reload | `the unit is shooting past its cast point` |
| Gutrot Spume | Tendrils of the Sea | enemy in melee, LARGE only (135) | get him next to the Steam Tank in melee; infantry in melee must NOT be picked | `target: '...steam_tank...'` |
| Chaos Warriors, Marauders | - | - | melee line | - |

## Battle 4 (short): Cathay, vs Empire with Handgunners

| Unit | Ability to arm | Trigger | What to do | Log line |
|---|---|---|---|---|
| Jet Lion | Missile Mirror | enemy missile unit shooting (138) | let the enemy Handgunners shoot at your line; keep the Jet Lion within about 140 m of them | `enemy missile unit shooting (targeting wh_main_emp_inf_handgunners` |

**The proof this battle exists for.** The mod has never read an enemy's ammunition. If the game refuses that read,
the log says `missile mirror: an enemy's ammo_left() cannot be read` once, and Missile Mirror never fires.

## Optional battle 5: Tomb Kings, vs Vampire Counts

- **Liche High Priest (Death), Eternal Gaze:** against an all-undead army it must NEVER fire (the not-undead filter,
  round 138).
- **Tomb King, Reanimate (wavering aura):** a risk. Tomb Kings units are undead and may never report "wavering" (they
  crumble instead). If Reanimate never fires, that is the likely reason, not a bug in the trigger.

## Already seen on your wheels (no extra unit needed)

Rune of Slowness and Sadistic Snare (the fast-enemy trigger), Headhunt (Lord/Hero filter), Entangle (not-flying
filter), Enchanted Metallurgy (shooting aura), and Acquiescence, Torment Blade, Virulent Contagion, The Hammer of
Karak Drazh, Frost Shard Glaive, Ravaging Swarm (enemy in melee). Any battle with those units also tests them.

## After the battles

Tell me which battles you fought. I will grep the log (never open it whole) for each line above, and report per
ability:
- it fired with the expected reason;
- it never fired (and why);
- or it fired wrongly.
