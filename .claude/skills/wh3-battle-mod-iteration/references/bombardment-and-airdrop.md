# Bombardment and air-drop abilities

Topical depth for the typed bombardment family and the self-centred air-drop ("on top of") abilities.

## Counting the family

- Typed set: `unit_abilities.type = wh_type_bombardment` - 131 keys game-wide.
- Narrow to unit-side carriers: a `source_type` in the unit-side set AND a real
  `unit_special_abilities` row -> 58.
- Remove army-bar junctions (`army_spec`) -> **55 wheel-visible**.
- The last step is where a hand count drifts: subtracting the obvious army ability but keeping the
  two cataclysm/army twins of another lands one or two high. State the definition with every count.
- Rows vs entries vs keys: "N implemented" counts KEYS. An ability carried by several keys (base +
  DLC/quest twin) inflates the key count relative to entries, so a remainder computed from an entry
  count is wrong by exactly the twin keys.

## Grant sources worth knowing

- **Call of Tor** - Oath-Brothers of Tor (War Bear Riders ROR): bound, self-centred
  (`ai_usage = aoe_centred_on_self`), unlimited uses.
- **Undeath from Above** - the Deck Droppers unit set (Deck Droppers, Bombers, Handgunners, Salt Lord
  Scuttlers), all flying.
- **Bubonic Broadside** - army-bar only: no unit, lord, item or mount junction anywhere in the data.
- **Warp Lightning Rod** - NO carrier junction at all. It is a campaign mutation grant (Clan Moulder
  Lobotomy augmentation), not a default unit ability. A missing junction is therefore not proof an
  ability is unreachable; ask the user before filing it as impossible.
- **Nan-Gau Grenades** - Empress Crowmen (Onyx Crowmen ROR), flying, 2 uses / 60 s, 10 m, air-only.

## What an air-drop row actually is

- All target flags false, `effect_range 0`, `targetting_aoe = wh_abilities_bomb_drop` (or
  `_small_drop`), `ai_usage = always_use_only_land`.
- Restriction flags carry the real gating: `grounded` (must be airborne; cannot be used landed) and,
  on some rows, `engaged_in_melee`.
- The blast radius is NOT in the extracted tables. Any underfoot test therefore uses a constant or a
  radii sum, stated as such.
- Not every self-centred damage row is a drop: Searing Torrent is a 10 m self-nova on ground disc
  cavalry whose `engaged_in_melee` flag is a RECHARGE restriction (melee is never required, only
  excluded). It can still ride the same trigger, with that noted in the comment.

## The overlap test (replacing edge-to-edge)

`unit_distance` measures bounding-box edge to edge. With large formations two units can have box
edges 0.5 m apart while their centres are 15 m apart, so a small metre bound fires with nothing
underneath - the reported "released too soon". Use instead:

1. Read both positions as `battle_vector` and take `get_x()` / `get_y()` only. Ignoring z is
deliberate: a flier's altitude would make every drop read far away.
2. Threshold = `(caster_radius + enemy_radius) * fraction` when a radius/footprint read exists
   (fraction below 1 so the enemy is under the formation, not touching its edge); otherwise ONE
   documented constant standing in for the formation footprint.
3. Log centre distance and threshold on every decision and on the pre-cast re-check, so a field
   report can be answered from the log rather than inferred from where the rocks landed.
4. Fail closed when an infantry or flying read raises.

A user-chosen bound (e.g. a 1 m test value) overrides the 70% rule on purpose: keep it as one named
constant, exempt the evaluator from the range map by identity check, and label it a test value in the
comment, the release note and the sheet.

## Members (the eleven)

Death from Above, Drop Rocks, Drop Sphere, Fire Bombs, Gyrobomber Bomb, Sky-Junk Bomb,
Skyhammer Bomb, Wake of Fire, Searing Torrent, Nan-Gau Grenades, Undeath from Above.

Air-gated where the row declares `grounded` or every carrier flies; two documented exceptions are the
ground Tiktaq'to variant of Drop Sphere and Searing Torrent (ground carrier).
