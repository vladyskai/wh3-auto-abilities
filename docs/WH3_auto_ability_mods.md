# Total War: WARHAMMER III — mods that make battle abilities fire automatically

Research date: **26 September 2026**. Game status: **Update 9.0**, released 24 September 2026 (2 days before this research). Source: Steam Workshop (Steam's public `GetPublishedFileDetails` API for last-update timestamps and subscriber counts) plus Steam Workshop pages and Creative Assembly's 9.0 release notes.

## First, the thing that decides the answer

There are only **two ways** a mod can make your active abilities (the clickable icons on a lord/hero/unit card) fire without you clicking them:

1. **Conditional auto-activation** — the ability stays on the wheel but gains a built-in trigger: *when charging*, *when in melee*, *when health drops below 75%*, *on cooldown*, *when losing the melee*. A short list of games in the series do this; a mod has to repurpose a trigger the game already ships.[4]
2. **Turn the active ability into a passive** — no trigger, no toggle: the effect is simply on all the time, usually with its numbers cut so it is not blatantly overpowered. This is what the most popular and most-maintained mod does.[1]

A **third, different** approach is to hand the unit to the battle AI. The AI then casts and fires abilities for you, but you cannot say "only when charging" — you have given up control of that unit.[9]

Also worth knowing: vanilla WH3 has no auto-cast setting, and **Update 9.0 added none** — its release notes mention abilities in exactly 7 sentences, all of them individual bug fixes.[15]

## List A — conditional auto-activation mods (this is what you asked for)

| # | Mod | Author | What it actually does | Last updated | Subs | Maintained? |
|---|---|---|---|---|---|---|
| 1 | **Auto Abilities** [`id=3009989710`](https://steamcommunity.com/sharedfiles/filedetails/?id=3009989710) | Welter | Puts a real trigger on each active ability so it fires by itself. Triggers used: *Charging*, *In melee*, *On cooldown*, *Health below 75%*, *Below 50% HP*, *Losing melee combat*, *Morale wavering*. Does **not** change the abilities' numbers, duration or cooldown — only when they fire. Covers ~55 listed abilities and magic items. | **30 Jul 2023** | 518 | **No.** Author has moved on; on 22 Nov 2024 he wrote that a different mod "is superior to mine so I started using it. I also helped a bit in updating that mod" and linked mod #5.[4] |
| 2 | **Auto Abilities Foe Seeker** [`id=3012442892`](https://steamcommunity.com/sharedfiles/filedetails/?id=3012442892) | Welter | Companion to #1, standalone. Turns the *Foe Seeker* ability into a passive that **switches itself off below 75% health** (there was no good activation condition for it, and left on permanently it amounts to Perfect Vigour, which is too strong). | **30 Jul 2023** | 63 | **No.** Single-shot release the same day as the parent's last update.[5] |
| 3 | **Auto activation lite** [`id=2799569408`](https://steamcommunity.com/sharedfiles/filedetails/?id=2799569408) | (uncredited in page extract) | Narrow scope: only the active abilities granted by **magic items** equipped on lords/heroes. Character skills, unit abilities and bound spells are left vanilla. | **29 Jun 2023** | 50 | **No.** Over 3 years stale.[6] |
| 4 | **Permanent Active Skills** [`id=2869091770`](https://steamcommunity.com/sharedfiles/filedetails/?id=2869091770) | — | "No more clicking on skills all the time. Click once and it's permanently on." One toggle, whole battle, no conditions. | **4 Oct 2022** | 152 | **No.** Nearly 4 years stale, only 4 days after release.[7] |
| 5 | **Too Many Activatable Skills 8.x (SFO Safe)** [`id=2985359051`](https://steamcommunity.com/sharedfiles/filedetails/?id=2985359051) | Zach | Reduces every activatable ability's strength to **1/3** and makes it a **passive, permanently on**. No trigger, no toggle — the clicking disappears instead of being automated. Save-game and multiplayer safe (can be added/removed mid-campaign). SFO-compatible, which matters if you run overhaul mods. Title still says "8.x" but the mod was rebuilt from the ground up in Aug 2026 because the underlying data tables changed. | **20 Aug 2026** | 5,465 | **Best of the lot, but pre-9.0.** Author replying in the comments about the new patch: "I'll revisit this mod in a bit, but it should still be working in 9.0". One user disagrees: "im not sure if its working.. a ton of my activation skills came back" — another reports "seems to be working with 9.0". So: expected to work, author active, unconfirmed.[1] |
| 6 | **TMAS Remove AOE Visuals** [`id=3290510918`](https://steamcommunity.com/sharedfiles/filedetails/?id=3290510918) | Zach | Mod #5 minus the looping area-effect visuals, for people who found the permanently-on effects visually noisy. | **20 Aug 2026** | 421 | Same status as #5 — same author, same update day.[2] |
| 7 | **too many active skills** [`id=2875046977`](https://steamcommunity.com/sharedfiles/filedetails/?id=2875046977) | — | The 2022 Korean-language original that #5 is based on. Same idea, unmaintained. | **18 Nov 2022** | 35 | **Dead.** Effectively superseded by #5, which links back to it as "Original mod".[3] |

**Practical read:** if you want the behaviour today, mod **#5** is the only one with a live author. If you specifically want *conditional* activation ("fire when I charge", "fire below 75% HP") rather than "always on", your only options are **#1 + #2**, last touched July 2023.

## List B — mods that hand units to the AI (abilities fire automatically, but you don't choose the condition)

These are not ability-automation mods in the strict sense, but they produce the outcome you described — abilities get used without you clicking them — and every one of them is far more actively maintained than List A.

| Mod | Author | What it does | Last updated | Subs |
|---|---|---|---|---|
| [**AI Army Control**](https://steamcommunity.com/sharedfiles/filedetails/?id=3787823404) `id=3787823404` | — | Lets the AI take over selected units or your entire army in battle. Says it started from the AI General concept and was heavily reworked, leaning on the game's own native battle AI planner. | **15 Sep 2026** | 9,732 |
| [**AI General: Unified Tactics**](https://steamcommunity.com/sharedfiles/filedetails/?id=3727310475) `id=3727310475` | — | One button delegates your army (field, settlement, siege, ambush, reinforcement, quest battles). Explicitly "puts Lords and characters to work **casting spells and using special abilities**", plus fire discipline, skirmishing, artillery, and keeping the lord out of the first wave. Release TAC‑012.7.4. | **17 Sep 2026** | 3,838 |
| [**AI General Unified - Fixed**](https://steamcommunity.com/sharedfiles/filedetails/?id=3767196412) `id=3767196412` | — | Community fix/enhancement of the above (selection fixes etc.). Needs the original for install instructions. | **21 Jul 2026** | 272 |
| [**AI General 3**](https://steamcommunity.com/sharedfiles/filedetails/?id=2799316652) `id=2799316652` | — | The long-standing delegate-to-AI mod and the most-subscribed thing in this whole report. Page now leads with: "This mod likely still works even though I no longer update it… I no longer maintain WH3 mods, including this one." | **1 Sep 2026** | 99,377 |
| [**AI General Cycle Charge**](https://steamcommunity.com/sharedfiles/filedetails/?id=3789772045) `id=3789772045` | — | Pure Lua add-on that **requires AI General 3**; gives AI-controlled cavalry and chariots proper charge/disengage/recharge behaviour. | **29 Aug 2026** | 849 |
| [**TTW Auto Assist**](https://steamcommunity.com/sharedfiles/filedetails/?id=3769709545) `id=3769709545` | — | Lighter-weight: enables the **native battle AI for selected player units** via an Auto Assist button in the battle order bar. Selecting a unit pauses its AI. | **22 Jul 2026** | 298 |

**Companion worth knowing about:** [**More Ability and Spell Buttons**](https://steamcommunity.com/sharedfiles/filedetails/?id=3053402711) `id=3053402711` raises the UI cap to 18 ability buttons and 12 spell buttons. Relevant because the game hides any skill that has a passive trigger from the skill wheel[4] — with the automation mods installed you often want the remaining manual ones on screen. Last updated 3 Sep 2025, 25,620 subscribers.[14]

## Maintenance verdict

- **Criterion used:** does it run under Update 9.0 (24 Sept 2026)? The Workshop shows no hotfix wave from these authors in the 48 hours after 9.0 landed.
- **Nothing in the ability-automation category has been updated since 9.0 shipped.** The freshest is TMAS (#5, 20 Aug 2026), whose author is nonetheless present in his own comments fielding 9.0 reports.[1]
- **The conditional mods (#1–#4) are 2–4 years stale.** For database-edit mods that is less fatal than it sounds — they change rows in the game's data tables rather than hooking running code — but the same author's note that the tables shift between patches is exactly why Zach had to "rebuild the mod from the ground up" in August 2026.[1][4]
- **The AI-delegation mods (List B) are the actively maintained ones**, two of them touched within 10 days of this research, three within a fortnight.
- **No mod found gives you a configurable trigger editor** — you cannot map "ability X fires on condition Y" yourself. The available trigger list is fixed by the game engine. Welter, the author of the only true conditional mod, states this plainly: "we cannot create new trigger conditions, we have to use those already in the game", and warns the consequence — e.g. N'kari's and Skarbrand's charging attacks resolve *before* melee contact, so an "in melee" trigger misses them; "seems to be an animation issue for any Huge unit".[4]

## Search method (so you can judge coverage)

~30 keyword sweeps of the Steam Workshop browser (English: *auto abilities, automatic abilities, auto cast, automatic spell casting, ability automation, activate abilities automatically, too many active skills, active skills, toggle abilities, auto trigger, automatically use abilities, no micro, permanent active skills, smart cast, auto use items, one click abilities…*; plus Russian and Chinese terms: *авто способности, 自动激活技能, 自动施法*), filtered against 200+ distinct results. Non-English searches surfaced no additional mods in this category.

*Update timestamps and subscriber counts were read from Steam's public `ISteamRemoteStorage/GetPublishedFileDetails/v1` endpoint and the mod pages on 26 September 2026; Workshop "last updated" dates displayed on pages are relative and were resolved to absolute dates via that API.*

## Sources

[1] https://steamcommunity.com/sharedfiles/filedetails/?id=2985359051 — Steam Workshop: Too Many Activatable Skills 8.x (SFO Safe)
[2] https://steamcommunity.com/sharedfiles/filedetails/?id=3290510918 — Steam Workshop: TMAS Remove AOE Visuals
[3] https://steamcommunity.com/sharedfiles/filedetails/?id=2875046977 — Steam Workshop: too many active skills (2022 original)
[4] https://steamcommunity.com/sharedfiles/filedetails/?id=3009989710 — Steam Workshop: Auto Abilities (Welter)
[5] https://steamcommunity.com/sharedfiles/filedetails/?id=3012442892 — Steam Workshop: Auto Abilities Foe Seeker
[6] https://steamcommunity.com/sharedfiles/filedetails/?id=2799569408 — Steam Workshop: Auto activation lite
[7] https://steamcommunity.com/sharedfiles/filedetails/?id=2869091770 — Steam Workshop: Permanent Active Skills
[9] https://steamcommunity.com/sharedfiles/filedetails/?id=3727310475 — Steam Workshop: AI General: Unified Tactics
[14] https://steamcommunity.com/sharedfiles/filedetails/?id=3053402711 — Steam Workshop: More Ability and Spell Buttons
[15] https://community.creative-assembly.com/total-war/total-war-warhammer/blogs/110-total-war-warhammer-iii-update-9-0-release-notes — CA: Total War WARHAMMER III Update 9.0 Release Notes
