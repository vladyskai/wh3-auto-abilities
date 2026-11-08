import os, csv, json
T = os.path.expandvars(r"%LOCALAPPDATA%\Temp\wh3")
def load(p):
    rows=[]
    with open(p,"r",encoding="utf-8-sig",newline="") as f:
        for r in csv.DictReader(f, delimiter="\t"):
            if r.get("key","").startswith("#"): continue
            rows.append(r)
    return rows
spec = {r["key"]:r for r in load(os.path.join(T,"unit_spec_abil.tsv"))}
uab  = {r["key"]:r for r in load(os.path.join(T,"unit_abilities.tsv"))}
KEYS = [
 "wh3_main_lord_abilities_nurgling_tide",
 "wh3_dlc26_lord_abilities_eye_of_khorne",
 "wh3_dlc29_spell_bound_the_dreaded_thirteenth",
 "wh3_dlc29_spell_bound_the_dreaded_thirteenth_1",
 "wh3_dlc29_spell_bound_the_dreaded_thirteenth_thanquol",
 "wh3_dlc29_spell_bound_the_dreaded_thirteenth_thanquol_1",
 "wh2_dlc16_lord_abilities_beast_pack",
 "wh2_dlc15_item_abilities_blacktoofs_conjuration",
 "wh2_dlc16_lord_abilities_call_to_gwindalor",
 "wh2_dlc16_spell_bound_vampires_lesser_raise_dead",
 "wh2_dlc17_spell_bound_savage_dominion",
 "wh3_dlc26_hero_abilities_savage_predators",
 "wh2_dlc16_hero_abilities_tide_of_death",
 "wh2_dlc16_hero_abilities_tide_of_pox",
 "wh3_main_item_abilities_zak_aloooog",
]
cols = ["target_ground","target_self","target_friends","target_enemies","target_intercept_range",
        "effect_range","affect_self","always_affect_self","spawned_unit","spawn_is_decoy","spawn_type",
        "num_uses","ai_usage","targetting_aoe","active_aoe","wind_up_time"]
for k in KEYS:
    s = spec.get(k); u = uab.get(k, {})
    print("="*100)
    print(k)
    if s is None:
        print("  NO unit_spec_abil row")
    else:
        print("  " + " | ".join("%s=%s"%(c, s.get(c,"")) for c in cols))
    print("  type=%s source_type=%s icon=%s hidden=%s" % (u.get("type"),u.get("source_type"),u.get("icon_name"),u.get("is_hidden_in_ui")))
