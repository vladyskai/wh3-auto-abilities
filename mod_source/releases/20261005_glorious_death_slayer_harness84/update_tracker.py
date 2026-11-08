# -*- coding: utf-8 -*-
"""Fix 3: mark the untestable block-2 entries in the tracker + add a header note.

Anchored per ENTRY (the entry header is unique), so the many identical
"approved (in-melee self)" Decision lines are never edited out of place.
"""
import io, re, hashlib

P = r"C:/Users/vlady/Desktop/WH3_mod/docs/WH3_ability_tracker.md"
s = io.open(P, encoding="utf-8").read()
orig_len = len(s)

NOTE = (
"**Update 2026-10-05 (field-test follow-up — two corrections + field-test status):** the block-2 field test produced two corrections, both implemented and shipped (harness84: 2039 checks green):\n"
"- **Glorious Death** — the candidate set is **SLAYER UNITS ONLY** (not \"any friendly unit\"). It fires when a Slayer unit is in melee: a Slayer **ally** is preferred (the lowest-health one); otherwise the **owner itself** casts on self only if the owner is a Slayer and in melee; otherwise silent. A **non-Slayer ally is never targeted** (the old any-in-melee-ally fallback is removed). \"Slayer\" is decided by a list of **land_units type keys derived from the game's own data** (`land_units.loc.tsv`: every unit key whose own key contains `slayer`/`doomseeker`, exact whole-key equality only — e.g. `wh_main_dwf_inf_slayers`, `wh2_dlc10_dwf_inf_giant_slayers`, `wh3_dlc25_dwf_cha_daemon_slayer`, `wh3_dlc25_dwf_inf_doomseekers`).\n"
"- **Ghoul King of Ushoran** — the 80%-re-arm **hysteresis is REMOVED** (a unit under sustained damage may never climb back above 80%, which would disarm the trigger for good); the rule is plain own health ≤ 75%, limited only by the readiness gate + the engine cooldown + the rejection-informed back-off.\n"
"\n"
"**Field-test status of block 2 (read the entries below).** Only **Glorious Death** could be field-tested (the user owns that DLC and fielded it); it was tested and its trigger was corrected above. The entries marked `pending test (DLC unavailable)` are implemented but need a hero/item the user cannot field in skirmish-vs-AI (the user named **Fangspike** and **Eagle-Feather Torc** as item-gated). Entries marked `pending test (not yet field-tested)` are implemented but were not reached in the test battle (ownership of the needed DLC is not assumed). **All of these remain implemented and shipping** — they are awaiting a test opportunity, not unimplemented.\n"
)
anchor_hdr = "Harness83: 1962 checks green.\n\n**Legend — Status column:**"
assert s.count(anchor_hdr) == 1
s = s.replace(anchor_hdr, "Harness83: 1962 checks green.\n\n" + NOTE + "\n**Legend — Status column:**", 1)

leg_old = "- `redesigned` — user-approved with a different trigger than the melee default (see the item's decision note); implement with the stated redesigned activation.\n"
assert s.count(leg_old) == 1
leg_new = (leg_old
    + "- `pending test (DLC unavailable)` — implemented, but the ability needs a hero/item from a DLC the user does not own, so it cannot be fielded in skirmish-vs-AI; awaiting a test opportunity.\n"
    + "- `pending test (not yet field-tested)` — implemented, but not reached/verified in a field battle yet (ownership of the needed DLC is not assumed); awaiting a test opportunity.\n")
s = s.replace(leg_old, leg_new, 1)

SIMPLE_DEC = ("- Decision: **pending test (not yet field-tested)** — implemented (in-melee self); the block-2 "
              "field test could not reach it (no DLC ownership assumed) — awaiting a test opportunity.")

def entry_span(text, name):
    m = re.search(r"\*\*\d+\. " + re.escape(name) + r"\*\*", text)
    assert m is not None, "no header: " + name
    i = m.start()
    j = text.find("\n**", m.end())
    assert j > i, "no end: " + name
    return i, j

def replace_decision(chunk, newline):
    k = chunk.index("- Decision:")
    e = chunk.index("\n", k)
    return chunk[:k] + newline + chunk[e:]

def append_decision(chunk, suffix):
    k = chunk.index("- Decision:")
    e = chunk.index("\n", k)
    return chunk[:e] + suffix + chunk[e:]

def edit(text, name, fn):
    i, j = entry_span(text, name)
    return text[:i] + fn(text[i:j]) + text[j:]

SIMPLE_NAMES = [
    "Dolorous Blade", "Dragon Spear", "Dreaded Duellist", "Dwarf Gouger", "Enrage", "Entice",
    "Everyone Has Their Price", "Evisceration", "Eye for an Eye", "Eye Gouger", "Eye of the Storm",
    "Faith's Bastion", "Fangsword of Eltharion", "Feint & Riposte", "Filth Mace", "Fluid Injection!",
    "Fury of the Blood God", "Fury of the Land", "Fury of Ursun", "Ghal Maraz", "Giant Leap", "Gitsnik",
    "Gotrek's Doom", "Grand Shield of Faith", "Great Gutgouger", "Halo of Maidenly Wrath",
    "Hammer-axe of Skoll",
]
assert len(SIMPLE_NAMES) == 27, len(SIMPLE_NAMES)

# 27 simple entries -> pending test (not yet field-tested)
for nm in SIMPLE_NAMES:
    s = edit(s, nm, lambda c: replace_decision(c, SIMPLE_DEC))

# the two named item-gated entries -> pending test (DLC unavailable); the
# redesigned note is kept and the status is appended.
s = edit(s, "Eagle-Feather Torc", lambda c: append_decision(c,
    " · **pending test (DLC unavailable)** — the torc is a DLC27 item the user cannot field."))
s = edit(s, "Fangspike", lambda c: append_decision(c,
    " · **pending test (DLC unavailable)** — the fangspike is a DLC26 item the user cannot field."))
s = edit(s, "Foe-Seeker", lambda c: append_decision(c,
    " · **pending test (not yet field-tested)** — Krell is a character the user did not field."))
s = edit(s, "Ghoul King of Ushoran", lambda c: append_decision(c,
    "; the interim 80%-re-arm hysteresis was REMOVED (2026-10-05) — plain own health ≤ 75%."
    " · **pending test (not yet field-tested)** — a WH2-DLC hero; not yet field-tested."))
s = edit(s, "Glorious Death", lambda c: append_decision(c,
    " CORRECTED after the field test (2026-10-05): SLAYER UNITS ONLY — a Slayer ally preferred,"
    " else self only when the owner itself is a Slayer and in melee, else silent; a non-Slayer ally"
    " is never targeted. Slayer-ness = the derived land_units type-key list. **Field-tested (DLC25).**"))

io.open(P, "w", encoding="utf-8", newline="").write(s)
print("tracker updated: %d -> %d bytes" % (orig_len, len(s)))
print("pending (not yet field-tested) occurrences:", s.count("pending test (not yet field-tested)"))
print("pending (DLC unavailable) occurrences   :", s.count("pending test (DLC unavailable)"))
print("sha256", hashlib.sha256(s.encode("utf-8")).hexdigest()[:32])
