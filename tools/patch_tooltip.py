"""Round 19 layout work.

1. The ability tooltip already ships a `label_right_click` component - CA's placeholder
   for exactly this hint ("Right click text that comes from db"), hidden for unit
   abilities because its visibility condition only holds in the spell-browser context,
   and filled with Loc("right_click_spell_browser"). Repurpose it: always visible, static
   English text. No new component, no new hierarchy entry, no localisation dependency.
2. Keep the rclick broadcaster insertions from round 17 (unchanged).
"""
import re
from pathlib import Path

EXTRACTED = Path(r"C:\Users\vlady\AppData\Local\Temp\wh3_layouts")
SRC_ROOT = Path(r"C:\Users\vlady\Desktop\WH3_mod\mod_source")
TOOLTIP = "ui/common ui/special_ability_tooltip.twui.xml"

HINT = "Right-click this ability to toggle automatic use (it then fires by itself on the charge)"


def patch_tooltip():
    text = (EXTRACTED / TOOLTIP).read_text(encoding="utf-8", errors="replace")
    before = text

    # (a) the visibility condition: make the line show for a normal unit ability tooltip
    old_vis = re.search(
        r'<callback_with_context\r?\n\t\t\t\t\tcallback_id="ContextVisibilitySetter"\r?\n'
        r'\t\t\t\t\tcontext_object_id="CcoUnitAbility"\r?\n'
        r'\t\t\t\t\tcontext_function_id="IsPassive == false &amp;&amp; &#10;IsContextValid\(AbilityGroupContext\).*?</callback_with_context>',
        text, re.S)
    assert old_vis, "visibility setter not found"
    text = text[:old_vis.start()] + (
        '<!-- Round 19: this line was hidden unless the tooltip belonged to the spell-browser\n'
        '\t\t\t\t     context, which no unit ability tooltip is. The visibility condition is dropped so\n'
        '\t\t\t\t     it always shows. -->') + text[old_vis.end():]

    # (b) the text: a static English line instead of the spell-browser loc lookup
    old_txt = re.search(
        r'<callback_with_context\r?\n\t\t\t\t\tcallback_id="ContextTextLabel"\r?\n'
        r'\t\t\t\t\tcontext_object_id="CcoStaticObject"\r?\n'
        r'\t\t\t\t\tcontext_function_id="Loc\(&quot;right_click_spell_browser&quot;\)"/>',
        text)
    assert old_txt, "text binding not found"
    text = text[:old_txt.start()] + (
        '<!-- Round 19: static hint for this mod, instead of Loc("right_click_spell_browser") -->'
        ) + text[old_txt.end():]

    # (c) the label's own placeholder text -> our hint
    old_ph = 'text="Right click text that comes from db"'
    assert text.count(old_ph) == 1, "placeholder text not found exactly once"
    text = text.replace(old_ph, 'text="%s"' % HINT, 1)

    assert text != before
    dst = SRC_ROOT / TOOLTIP
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_text(text, encoding="utf-8", newline="")
    print(f"{TOOLTIP}")
    print(f"   written: {dst} ({len(text)} chars)")
    print(f"   hint present: {HINT[:40]!r}...")
    print(f"   spell-browser loc binding gone: {'right_click_spell_browser' not in text}")


def main():
    patch_tooltip()


if __name__ == "__main__":
    main()
