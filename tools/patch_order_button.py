"""Round 21: patch the component the engine actually named, and declare the property.

The log identified the button: id='button_order1', under sa_dial > button_parent, defined in
hud_battle.twui.xml with callback_id="BattleSpecialAbilityButton" (the engine's own click->use).

Two insertions into that ONE component, both literal:
  1. <userproperties>: declare zz_rclick = "0"   (vanilla reads properties that layouts declare -
     e.g. wh3_dlc23_labour_move.lua reads "faction_id"/"treasury_cost" off buttons, so this is the
     game's own UI->script handshake, not an invention)
  2. <callbackwithcontextlist>: ContextCommandRightClick -> self.SetProperty("zz_rclick", "1")
     (the callback CA uses 115 times across 23 components, including on ability components)
"""
import re
from pathlib import Path

SRC = Path(r"C:\Users\vlady\Desktop\WH3_mod\mod_source")
REL = "ui/battle ui/hud_battle.twui.xml"
VANILLA = Path(r"C:\Users\vlady\AppData\Local\Temp\wh3_layouts") / REL

text = VANILLA.read_text(encoding="utf-8", errors="replace")
before = len(text)

m = re.search(r"\n\t\t<button_order1\r?\n(.*?)\n\t\t</button_order1>", text, re.S)
assert m, "button_order1 component not found in hud_battle"
body = m.group(1)
assert 'callback_id="BattleSpecialAbilityButton"' in body, "not the ability button component"

CB = ('\t\t\t\t<callback_with_context\n'
      '\t\t\t\t\tcallback_id="ContextCommandRightClick"\n'
      '\t\t\t\t\tcontext_object_id="CcoStaticObject"\n'
      '\t\t\t\t\tcontext_function_id="self.SetProperty(&quot;zz_rclick&quot;, &quot;1&quot;)"/>\n'
      '\t\t\t\t<callback_with_context\n'
      '\t\t\t\t\tcallback_id="ContextCommandLeftClick"\n'
      '\t\t\t\t\tcontext_object_id="CcoStaticObject"\n'
      '\t\t\t\t\tcontext_function_id="self.SetProperty(&quot;zz_lclick&quot;, &quot;1&quot;)"/>\n')

assert body.count("</callbackwithcontextlist>") == 1
new_body = body.replace("</callbackwithcontextlist>", CB + "\t\t\t</callbackwithcontextlist>", 1)

UP = ('\t\t\t\t<property\n'
      '\t\t\t\t\tname="zz_rclick"\n'
      '\t\t\t\t\tvalue="0"/>\n'
      '\t\t\t\t<property\n'
      '\t\t\t\t\tname="zz_lclick"\n'
      '\t\t\t\t\tvalue="0"/>\n')
if "<userproperties>" in new_body:
    new_body = new_body.replace("<userproperties>", "<userproperties>\n" + UP, 1)
else:
    new_body = new_body.rstrip() + "\n\t\t\t<userproperties>\n" + UP + "\t\t\t</userproperties>"
    print("   (no userproperties block existed - one was added)")

text = text[:m.start(1)] + new_body + text[m.end(1):]
dst = SRC / REL
with open(dst, "w", encoding="utf-8", newline="") as fh:
    fh.write(text)

n_cmd = text.count("ContextCommandRightClick")
n_prop = text.count('name="zz_rclick"')
n_engine = text.count("BattleSpecialAbilityButton")
print(f"{REL}")
print(f"   size: {before} -> {len(text)} chars  (+{len(text)-before})")
print(f"   ContextCommandRightClick in file: {n_cmd} (want 1)")
print(f"   zz_rclick declarations          : {n_prop} (want 1)")
print(f"   engine's own ability callback   : {n_engine} (must stay)")

m = re.search(r"\n\t\t<button_order1\r?\n(.*?)\n\t\t</button_order1>", text, re.S)
print("\n   the parts that matter now:")
for line in m.group(0).splitlines():
    s = line.strip()
    if any(k in s for k in ("callback_id", "callbackwithcontext", "userproperties", "zz_rclick",
                            "<property", "value=\"0\"", "<button_order1", "ContextCommand")):
        print("      ", s[:130])
