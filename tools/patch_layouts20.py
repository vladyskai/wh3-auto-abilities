"""Rebuild the two ability layouts from the pristine vanilla copies, inserting the
right-click command callback directly - no broadcaster, no regex over the whole file.

Round 20's first attempt used a regex anchored on ContextEventBroadcaster and ate 221 KB of the
unit card, because vanilla uses that callback too (the dev button's DevLevelUp broadcast), so the
match ran from vanilla's block to our inserted value. This version inserts a literal block into a
named component and nothing else.
"""
import re
from pathlib import Path

EXTRACTED = Path(r"C:\Users\vlady\AppData\Local\Temp\wh3_layouts")
SRC = Path(r"C:\Users\vlady\Desktop\WH3_mod\mod_source")

TARGETS = {
    "ui/battle ui/hud_battle.twui.xml": [
        "button_behaviour",      # the orders-bar behaviour button
        "template_ability",      # the battle HUD ability button
        "button_ability",
        "button_spell",
    ],
    "ui/common ui/land_unit_card.twui.xml": [
        "template_ability",      # the unit card's ability icon (the one the tooltip belongs to)
    ],
}

# One block for every component: a right-click sets a property on the component itself.
# This is the callback CA uses 115 times (including in battle), and the same
# self.SetProperty(...) expression the engine's own reinforcement button uses.
COMMAND = ('<callback_with_context\n'
           '\t\t\t\t\tcallback_id="ContextCommandRightClick"\n'
           '\t\t\t\t\tcontext_object_id="CcoStaticObject"\n'
           '\t\t\t\t\tcontext_function_id="self.SetProperty(&quot;zz_rclick&quot;, &quot;1&quot;)"/>')


def insert(text, comp_id):
    m = re.search(r'\n\t\t<' + re.escape(comp_id) + r'\r?\n(.*?)\n\t\t</' + re.escape(comp_id) + r'>', text, re.S)
    if not m:
        return text, "component not found"
    body = m.group(1)
    if 'id="%s"' % comp_id not in body[:400]:
        return text, "block found but its header does not match"

    if "<callbackwithcontextlist>" in body:
        new_body = body.replace("<callbackwithcontextlist>",
                                "<callbackwithcontextlist>\n\t\t\t\t" + COMMAND, 1)
        what = "into callbackwithcontextlist"
    else:
        new_body = body.rstrip() + "\n\t\t\t<callbackwithcontextlist>\n\t\t\t\t" + COMMAND \
                   + "\n\t\t\t</callbackwithcontextlist>"
        what = "new callbackwithcontextlist"
    return text[:m.start(1)] + new_body + text[m.end(1):], what


for rel, comps in TARGETS.items():
    vanilla = (EXTRACTED / rel).read_text(encoding="utf-8", errors="replace")
    text = vanilla
    print(f"\n== {rel}   (vanilla {len(vanilla)} chars)")
    for comp in comps:
        text, what = insert(text, comp)
        print(f"   {comp:18} <- ContextCommandRightClick   {what}")
        assert "ContextCommandRightClick" in text
    dst = SRC / rel
    dst.parent.mkdir(parents=True, exist_ok=True)
    with open(dst, "w", encoding="utf-8", newline="") as fh:
        fh.write(text)
    print(f"   written: {dst}  ({len(text)} chars)")
    print(f"   ContextCommandRightClick: {text.count('ContextCommandRightClick')}   "
          f"ContextEventBroadcaster: {text.count('ContextEventBroadcaster')} (vanilla's own, must stay)")
