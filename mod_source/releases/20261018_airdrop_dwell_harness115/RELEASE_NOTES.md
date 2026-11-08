# Round 115 — the air-drop trigger waits: a 1-second dwell, plus the short-crossing fallback

2026-10-18 · release `20261018_airdrop_dwell_harness115`
Installed pack md5 **`56ef53853b74e2ee9e07ac5e343ce78a`** (5 files, all byte-identical to source)
Round doc `docs/WH3_round115_airdrop_dwell.md` · spreadsheet `docs/WH3_abilities_master_v16_2026-10-18.xlsx`

---

## 1. The ruling

> "I mean the trigger fires too soon. So we need a delay of 1 second for the trigger."

Round 114 fired on the first reading under 0.10 m. Round 115 keeps that rule and makes it **last**:
a dwell on the **pair**, measured on the poll's clock. A dwell, not a lead.

## 2. The rule

```
candidate = alive and number_of_men_alive() > AIR_DROP_MIN_MEN (10)
valid     = its unit_distance() is readable
chosen    = the NEAREST valid candidate
UNDER     = unit_distance(caster, chosen) < AIR_DROP_EDGE_M (0.10 m)
FIRE      = the PAIR has been CONTINUOUSLY UNDER for AIR_DROP_DWELL_S (1.0 s)
            OR it separated after >= AIR_DROP_MIN_CONTACT_S (0.3 s) of contact
```

### Constants

| Constant | Ships as |
| --- | --- |
| `FOURTH.AIR_DROP_DWELL_S` (**new**) | `1.0` s |
| `FOURTH.AIR_DROP_MIN_CONTACT_S` (**new**) | `0.3` s |
| `AIR_DROP_EDGE_M` / `AIR_DROP_MIN_MEN` / `AIR_DROP_NEAR_M` / `AIR_DROP_FAST_S` | `0.1` / `10` / `30` / `0.2` (unchanged) |

### The dwell state

`FOURTH.ad_pair[caster ui id][enemy ui id] = { first = <poll tick> }` — nested, no composite string key,
**one** timestamp, no gap history and no velocity. Helpers, all fields on `FOURTH` (the chunk is at Lua's
200-local ceiling): `ad_pair_key`, `ad_pair_stamp`, `ad_pair_drop`, `ad_under`, `ad_event`,
`ad_purge_unit`, `ad_contact_clear`.

**The clock is `tick_count`** — the poll's own counter, `POLL_MS = 250 ms`. 1.0 s = the stamp plus four
further polls. The fast pass adds evaluations, never time. A missed poll can only make a pair wait
longer; nothing can fire early. The drop lands between **1.00 s and 1.25 s** after contact.

## 3. Behaviour

| Event | Result |
| --- | --- |
| first evaluation of a contact | stamp, **never fire** |
| still under, dwell not met | hold, log `dwell: under <t>s of 1.00s` |
| under for 1.00 s | **fire**, `dwell satisfied after 1.00s -> FIRING` |
| separates after >= 0.30 s | **fire on the separation**, `short crossing: under for <t>s (>= 0.30s)` |
| separates before 0.30 s | **cancel**, `dwell cancelled: separated after <t>s (gap <d>m …)` |
| re-contact | **fresh** dwell (the old stamp is dropped) |
| unit dropped | its pair rows are **purged** (caster slot or that one enemy row) |
| pre-cast re-check | re-validates models + alive, re-measures the gap, **re-verifies the dwell** |

The fallback is exempt from the gap test **by construction** (it fires on the separation evaluation);
the measured gap and the time held are logged so the exemption is visible, never hidden.

## 4. Kept exactly

The candidate filter, the nearest-by-`unit_distance` pick, `air_only` / `no_melee`, the self-centred cast
on the OWNER, every fail-closed read, the 0.2 s fast pass and the single `FOURTH.try_pair`
gate+cast path, `POLL_MS = 250`, the guard / charge / in-flight / per-unit serialisation gates, and the
tooltip mechanism (its air-drop sentence now states the 1-second hold).

Counts: **689 entries / 742 keys**, `air_drop_on_infantry` **12 / 19**, 46 evaluators — unchanged.

## 5. Harness 115

* **4,739 checks / 0 failures**, twice, byte-identical (`h115_run1.txt`, `h115_run2.txt`).
* Worlds A (1.0 s fires) · B (0.75 s → fallback only) · C (0.25 s → cancelled with its time) ·
  D (re-contact = fresh dwell) · E (first evaluation never fires; fast ticks add no time) ·
  F (re-check re-verifies the dwell and skips on gap drift) · G (purge by enemy and by caster) ·
  H (no double cast across fast ticks; one more only past the guard) · I (air-only still holds).
* Section-0 pins in both copies: both constants once, the nested state, the `tick_count` clock, the
  never-fires-first line, the fallback branch, the purge hook, the re-check gates, the family counts,
  the new tooltip; live-only `ad_tag` = 7 sites and the five dwell literals verbatim.
* **Red control** (round-114 build): **59 failures** — 56 in the new section plus the 3 designed text
  pins this round rebased (tooltip ×2, `ad_tag` count). No crash.
* **Supersessions** (count preserved): harness 114's 88 instant-fire world slots → N/A; round 107's
  S2a/S2b/S3a → N/A through a renamed check call; harness 93's TIP map rebased to the new sentence.

## 6. Build

```
source script/…         778,144 bytes
five files              all MATCHES SOURCE: True
round 114 + 115 gates   OK
built / installed md5   56ef53853b74e2ee9e07ac5e343ce78a   IDENTICAL True
independent reopen      of the installed pack: five files byte-identical
zz_probe_dist.pack      left installed (md5 d4e67cfb8bc562c7d6f0ff742909c13d, untouched)
```

## 7. Tuning (what to send back)

Every contact now logs its own time under. Send the `dwell …` lines for the ability that misbehaved:

* still too soon → `dwell satisfied after X.XXs` shows the hold; raise `AIR_DROP_DWELL_S` 1.0 → 1.5 → 2.0
* too late → lower `AIR_DROP_DWELL_S` 1.0 → 0.7 → 0.5 (keep it above `AIR_DROP_MIN_CONTACT_S`)
* quick passes missed → the `dwell cancelled: separated after X.XXs` lines name the time it *did* hold;
  lower `AIR_DROP_MIN_CONTACT_S` 0.3 → 0.2 → 0.1
* fallback firing when it should not → raise `AIR_DROP_MIN_CONTACT_S` 0.3 → 0.5 → 0.75

One constant per field test. `AIR_DROP_EDGE_M` has not changed and is not the knob for this round.
