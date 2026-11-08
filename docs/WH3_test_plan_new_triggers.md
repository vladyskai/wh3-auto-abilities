# Test plan - the new auto-abilities (block 2)

This build adds **32 more abilities** to the auto-firing mod, and some of them
fire on **new conditions** (a broken barrier, low health, and so on). This page
tells you what to put on the field, what to do, and the exact line you should
see in the log. Print it and tick the boxes.

---

## 0. Before you start (do this once)

- The mod is already installed as a `.pack` in the game's `data` folder -
  nothing to copy.
- Launch the game and start **any custom/skirmish battle**.
- **Where the log is:** the file `zz_test_deadly_onslaught_log.txt`, in the game
  install folder **next to `Warhammer3.exe`** (i.e. `...\Total War WARHAMMER III\`).
  Open it with Notepad. Every battle appends a new block that starts with
  `======== new battle session ========`.
- **How to arm an ability:** click a unit's card to select it, then click the
  small **badge letter** that appears for that ability on the unit's ability
  dial. It flips **M -> A**. Only abilities showing **A** will auto-fire.
  (M = manual/off, A = automatic/on. All badges start at M.)
- **Only your own units are watched.** Enemy abilities are ignored.

Line shapes you will see in the log:

- An attempt: `ATTEMPT <ability> '<key>' on '<unit type>' ui id <id> | reason: <why> | armed=ON`
- A landed cast: `  perform_special_ability(key, unit) : ACCEPTED`
- A cooldown / "not allowed yet" refusal: `  perform_special_ability(key, unit) : REJECTED (on cooldown)`

(The reason text is what tells the new triggers apart - it is different for each
one on purpose.)

---

## 1. The five ORIGINAL abilities (one-battle regression list)

Field any army, arm these five badges, and check they still behave.

| Ability (badge marker) | Example unit that has it | Expected log line (the "reason" part) |
|---|---|---|
| **Deadly Onslaught** `onslaught` | Boris Todbringer | `reason: charging (gap=..m dist=..m eta=..s)` **or** `reason: in melee` |
| **Foe-Seeker** `foe_seeker` | Karl Franz / most lords | `reason: tired or worse (fatigue: tired)` (only once the unit is Tired+) |
| **Hammer of Sigmar** `hammer_of_sigmar` | an Empire Warrior Priest | `reason: in melee` |
| **Stand Your Ground** `stand_your_ground` | a lord that has the aura | `reason: in melee, morale below the wavering threshold` |
| **Blood Lust** `blood_lust` | a Vampire / Strigoi lord | `reason: in melee, morale not wavering` |

- [ ] All five badges appear (letter **M**) and flip to **A** when clicked.
- [ ] Each one fires with the reason shown above when its condition is met.
- [ ] A landed cast logs `perform_special_ability(key, unit) : ACCEPTED`.

---

## 2. The five NEW triggers

### 2a. Eagle-Feather Torc - fires when the barrier is BROKEN
- **Field:** any unit carrying the **Eagle-Feather Torc** item, or any unit with
  a **barrier** (e.g. a Tzeentch / Slaanesh / Kislev barrier unit).
- **Do:** let it take hits until the blue barrier bar is gone (barrier at 0).
- **Expect:** `reason: barrier broken (BarrierHp 0/120)` (the 120 is that unit's
  barrier maximum; it will show your unit's own numbers).
- [ ] Fires once the barrier is at 0.

### 2b. Fangspike - fires on the charge window OR in melee
- **Field:** a character carrying the **Fangspike** weapon.
- **Do:** charge it into an enemy (the charge window), then let it fight
  hand-to-hand.
- **Expect, charging:** `reason: charging (gap=..m dist=..m eta=..s)`
- **Expect, in melee:** `reason: in melee (charge or melee)`
- [ ] The charging line appears during the charge.
- [ ] The `in melee (charge or melee)` line appears once it is stuck in.
      (You will never see it say both at the same instant - only one of the two
      is chosen each time.)

### 2c. Summoned Foe-Seeker - Krell
- **Field:** **Krell**, summoned by **Heinrich Kemmler** (Kemmler summons Krell
  in battle).
- **Do:** wait until the summoned Krell is **Tired** or worse (a few minutes of
  fighting), then arm its Foe-Seeker badge.
- **Expect:** `reason: tired or worse (fatigue: tired)` - and it uses the **same
  badge** (`zz_auto_badge_fs`, the Foe-Seeker one) as any other Foe-Seeker unit.
  You do **not** get a second badge.
- [ ] Krell's Foe-Seeker fires on the tired rule using the normal Foe-Seeker badge.

### 2d. Ghoul King of Ushoran - fires at health <= 75%
- **Field:** a **Strigoi Vampire Lord** (the ghoul-king-flavoured vampire lord).
- **Do:** let it drop to about 75% health or below, then arm its badge.
- **Expect:** `reason: health 72% (<= 75%)` (the number is that unit's live
  health - it will show its own %).
- **Hysteresis (important):** it will **not** keep firing every couple of
  seconds while it stays low. After one cast it only re-arms once the unit climbs
  back **above 80%**. So: drop low -> one cast -> stays quiet while still low ->
  heal above 80% -> drop low again -> one cast.
- [ ] Fires when it drops to 75% or below.
- [ ] Stays quiet while it sits low (does not spam).
- [ ] Fires again only after it climbs above 80% and drops low again.

### 2e. Glorious Death - the FIRST ally-targeting ability
- **Field:** **Ungrim Ironfist** (or a **Daemon Slayer**), and make sure there is
  another **friendly unit in melee nearby** - ideally a cheap **Slayer** unit.
- **Do:** put Ungrim (or the Slayer) into hand-to-hand with a friendly unit also
  fighting.
- **Expect (ally chosen):** `reason: ally in melee (priority)` - the ability is
  cast on the **other** friendly unit in melee with the lowest health, **not** on
  Ungrim himself.
- **Expect (nobody else in melee):** `reason: self fallback (no other melee ally)`
  - then it targets Ungrim himself.
- **Note on refusals:** the mod cannot tell which units are "Slayer" units, so it
  offers the nearby in-melee ally and lets the game decide. If the game refuses
  (the ally is not a Slayer), you will see a `REJECTED` line and the mod backs
  off and retries later - that is expected and not a bug.
- [ ] With another in-melee friendly unit present: `reason: ally in melee (priority)`
      and the effect lands on the ally.
- [ ] With no other in-melee friend: `reason: self fallback (no other melee ally)`.

---

## 3. The 27 "simple" abilities (also new in this build)

These 27 fire on the same rule as Blood Lust: **while in melee, cast on self**.

They include (badge names in brackets): Dolorous Blade, Dragon Spear, Dreaded
Duelist, Dwarf Gouger, Enrage, Entice, Everyone Has Their Price, Evisceration,
Eye Jabber, Eye Gouger, Eye of the Storm, Faith's Bastion, Fangsword of
Eltharion, Feint and Reposte, Filth Mace, Fluid Injection, Gaze of Khorne, Fury
of the Land, Fury of Ursun, Ghal Maraz, Giant Leap, Gitsnik, Gotrek's Doom,
Shield of Faith (Upgraded), Great Gutgouger, Halo of Maidenly Wrath, Hammer-Axe
of Skoll.

- **Do:** put a unit that carries one of these **into hand-to-hand**, arm its
  badge, and wait one tick.
- **Expect:** `reason: in melee, morale not wavering`
  (or `reason: in melee (morale unreadable - plain in-melee fallback)` if the
  morale read cannot be taken).
- [ ] Pick two or three of them on units you actually field; each fires in melee
      with the reason above.
- [ ] A unit that owns none of these shows **no new badge** at all.

---

## 4. Negative checks (these must STAY SILENT)

Tick these - if any of them fires, something is wrong:

- [ ] **Barrier intact:** a torc/barrier unit that still has its barrier up does
      **not** log `barrier broken`.
- [ ] **Not charging and not in melee:** a Fangspike unit standing idle logs
      nothing for Fangspike.
- [ ] **Not tired yet:** a Foe-Seeker unit that is Fresh/Active (not Tired+)
      logs nothing for Foe-Seeker.
- [ ] **Health above 75%:** a Ghoul King unit above 75% logs no `health ...%` line.
- [ ] **No other melee ally:** Glorious Death says `self fallback`, never
      `ally in melee (priority)`.
- [ ] **Not in melee:** the 27 simple abilities do not fire for a unit that is
      not fighting.
- [ ] **Badge still M:** an ability you never clicked to **A** never fires
      (it stays off).

---

## 5. If something looks wrong

- Check the unit's badge is actually **A** (one click on the badge flips M/A).
- Check the log file is the one next to `Warhammer3.exe`, and look at the newest
  `======== new battle session ========` block.
- A `REJECTED (on cooldown)` line is normal - the game is refusing because the
  ability is already active/on cooldown; the mod retries later by itself.
- For Glorious Death, a `REJECTED` line usually means the ally it picked was not
  a Slayer unit - expected; the mod will try again.
