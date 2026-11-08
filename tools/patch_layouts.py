"""Build the UI-layout half of the mod.

Takes the vanilla layouts out of the extracted copy of ui3.pack and adds one
CA-documented callback to every component that draws a *unit ability icon*:

    <callback_with_context callback_id="ContextEventBroadcaster">
      <child_m_user_properties>
        <property name="rclick" value="zz_auto_rclick_..."/>
      </child_m_user_properties>
    </callback_with_context>

Why this is the right hook (all of it read off the engine's own files):

  * CA's UI callback documentation defines ContextEventBroadcaster as "On action
    specified by user property broadcasts the event specified (lclick, rclick,
    mouseon, mouseoff)" - rclick is a documented trigger, and vanilla layouts
    never use it, which is why right-clicking an ability icon has never done
    anything.
  * The ability buttons themselves were located from the engine's own script:
    lib_battle_ui.lua's highlight_unit_abilities() walks
    battle_orders/orders_parent/behaviour_parent, takes child 0 of each slot and
    reads InterfaceFunction("AbilityKeyForScript") to learn which ability a
    button shows.

Each component broadcasts a DIFFERENT event name on purpose: whichever one
actually fires tells us, from the mod's log, which component the button really
belongs to.
"""
import re
import shutil
import sys
from pathlib import Path

EXTRACTED = Path(r"C:\Users\vlady\AppData\Local\Temp\wh3_layouts")
SRC_ROOT = Path(r"C:\Users\vlady\Desktop\WH3_mod\mod_source")

# (layout path inside the pack, [(component id, event name), ...])
TARGETS = [
    ("ui/battle ui/hud_battle.twui.xml", [
        ("button_behaviour", "zz_auto_rclick_orders_bar"),
        ("template_ability", "zz_auto_rclick_hud_ability"),
        ("button_ability",   "zz_auto_rclick_button_ability"),
        ("button_spell",     "zz_auto_rclick_button_spell"),
    ]),
    ("ui/common ui/land_unit_card.twui.xml", [
        ("template_ability", "zz_auto_rclick_card_ability"),
    ]),
]

BLOCK = """\t\t\t\t<callback_with_context
\t\t\t\t\tcallback_id="ContextEventBroadcaster">
\t\t\t\t\t<child_m_user_properties>
\t\t\t\t\t\t<property
\t\t\t\t\t\t\tname="rclick"
\t\t\t\t\t\t\tvalue="{event}"/>
\t\t\t\t\t</child_m_user_properties>
\t\t\t\t</callback_with_context>
"""


def patch_layout(text: str, comp_id: str, event: str):
    """Insert the broadcaster into the first <callbackwithcontextlist> that
    belongs to the component with this id."""
    # find the component definition: a tag line whose id="..." matches
    pat = re.compile(r'\n\t\t<' + re.escape(comp_id) + r'\r?\n(.*?)\n\t\t</' + re.escape(comp_id) + r'>', re.S)
    m = pat.search(text)
    if not m:
        return text, "component not found"
    body = m.group(1)
    open_tag = "\n\t\t<" + comp_id
    if 'id="%s"' % comp_id not in body[:400]:
        return text, "found a block but its id header does not match"

    if "<callbackwithcontextlist>" in body:
        new_body = body.replace("<callbackwithcontextlist>",
                                "<callbackwithcontextlist>\n" + BLOCK.format(event=event).rstrip("\n"), 1)
        what = "into existing callbackwithcontextlist"
    elif "</callbacks_with_context>" in body:
        new_body = body.replace("</callbacks_with_context>",
                                BLOCK.format(event=event).rstrip("\n") + "\n\t\t\t\t</callbacks_with_context>", 1)
        what = "into existing callbacks_with_context"
    else:
        # no callback container yet: add one at the end of the component body
        new_body = body.rstrip() + "\n\t\t\t<callbackwithcontextlist>\n" + BLOCK.format(event=event).rstrip("\n") \
                   + "\n\t\t\t</callbackwithcontextlist>"
        what = "new callbackwithcontextlist added"

    start, end = m.start(1), m.end(1)
    return text[:start] + new_body + text[end:], what


def main():
    if not EXTRACTED.exists():
        sys.exit(f"no extracted layouts at {EXTRACTED}")
    for layout, comps in TARGETS:
        src = EXTRACTED / layout
        if not src.exists():
            print(f"!! missing {src}")
            continue
        text = src.read_text(encoding="utf-8", errors="replace")
        print(f"\n== {layout}  ({len(text)} chars)")
        for comp_id, event in comps:
            text, what = patch_layout(text, comp_id, event)
            print(f"   {comp_id:18} <- {event:32} {what}")
        dst = SRC_ROOT / layout
        dst.parent.mkdir(parents=True, exist_ok=True)
        # keep the engine's line endings
        dst.write_text(text, encoding="utf-8", newline="")
        print(f"   written: {dst}  ({len(text)} chars)")
        assert "zz_auto_rclick" in text, "no patch landed!"


if __name__ == "__main__":
    main()
