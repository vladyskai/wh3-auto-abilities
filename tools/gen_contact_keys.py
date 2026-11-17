#!/usr/bin/env python3
"""Round 171: the CONTACT set, GENERATED from the game data (CLAUDE.md rule 4: never hand-typed).

User ruling 2026-11-17 (the score 1-2 review, row 21, Necrotic Phylactery: "do the contact effect list please"). The
phylactery makes our units ignore enemy contact effects (poison, sundered armour, blinded, flammable, ...); it pays only
while an enemy that APPLIES one is fighting us. A land unit is in the set when its melee blows carry a contact effect:
  * its primary melee weapon has a contact phase (land_units.primary_melee_weapon -> melee_weapons.contact_phase), or
  * one of its PASSIVE abilities imbues a contact effect (land_units_to_unit_abilites_junctions -> special ability
    phases -> phases.imbue_contact), e.g. poisoned attacks.
Missile contact effects are left out: the phylactery's trigger is a melee one.

  derive()  -> sorted land unit keys
  text(ks)  -> "key;key;..." (the one string embedded in the mod)
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gamedata_paths as GP  # noqa: E402


def tsv(name):
    with open(os.path.join(GP.GAMEDATA, name), encoding="utf-8-sig") as f:
        h = f.readline().rstrip("\n").split("\t")
        f.readline()
        for line in f:
            yield dict(zip(h, line.rstrip("\n").split("\t")))


def derive():
    mw = {r["key"]: r.get("contact_phase", "").strip() for r in tsv("melee_weapons.tsv")}
    imbue = {r["id"]: r.get("imbue_contact", "").strip() for r in tsv("phases.tsv")}
    passive = {r["key"] for r in tsv("unit_spec_abil.tsv") if r.get("passive") == "true"}
    abil_imbues = set()
    for r in tsv("phase_junc.tsv"):
        if r["special_ability"] in passive and imbue.get(r["phase"]):
            abil_imbues.add(r["special_ability"])
    out = set()
    for r in tsv("land_units.tsv"):
        if mw.get(r.get("primary_melee_weapon", ""), ""):
            out.add(r["key"])
    for r in tsv("land_abil.tsv"):
        if r["ability"] in abil_imbues:
            out.add(r["land_unit"])
    return sorted(out)


def text(ks):
    return ";".join(ks)


if __name__ == "__main__":
    ks = derive()
    lu = sum(1 for _ in tsv("land_units.tsv"))
    print(len(ks), "of", lu, "land units apply a melee contact effect")
    print([k for k in ks if "skv" in k][:8])
