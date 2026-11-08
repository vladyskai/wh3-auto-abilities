#!/usr/bin/env python3
"""Build docs/progress.html: where the mod stands, from the project's own records.

Sources (nothing typed by hand):
  * the newest master workbook (docs/WH3_abilities_master_v<N>_*.xlsx): the 1,123 in-wheel rows;
  * the tracker (docs/WH3_ability_tracker.md): the decision behind every row not implemented;
  * the mod's ABILITIES table: entries, keys and trigger families;
  * every battle log on this PC (grep for ATTEMPT ... ACCEPTED): which keys have fired in a real
    battle at least once (any build). The result is saved to docs/battle_seen_keys.json, so the page
    can be rebuilt on a machine without the logs (the logs are not in the repository).

Run:  uv run --with openpyxl python tools/make_progress_page.py
"""
import collections
import datetime
import glob
import html
import json
import os
import re
import subprocess
import sys

import openpyxl

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_ability_database as bd

ROOT = r"C:\Users\vlady\Desktop\WH3_mod"
DOCS = os.path.join(ROOT, "docs")
OUT = os.path.join(DOCS, "progress.html")
SEEN = os.path.join(DOCS, "battle_seen_keys.json")
GAME_LOG = r"C:\Program Files (x86)\Steam\steamapps\common\Total War WARHAMMER III\zz_test_deadly_onslaught_log.txt"


def newest_workbook():
    best = None
    for p in glob.glob(os.path.join(DOCS, "WH3_abilities_master_v*_*.xlsx")):
        m = re.search(r"_v(\d+)_", os.path.basename(p))
        if m and (best is None or int(m.group(1)) > best[0]):
            best = (int(m.group(1)), p)
    return best


def battle_seen():
    """Keys with an ACCEPTED cast in any battle log on this PC; falls back to the saved JSON."""
    logs = [GAME_LOG] + glob.glob(os.path.join(ROOT, "**", "*log*.txt"), recursive=True)
    logs = [p for p in logs if os.path.isfile(p) and os.path.getsize(p) > 0]
    if not logs:
        return json.load(open(SEEN, encoding="utf-8"))["accepted"], "saved list (no logs on this machine)"
    out = subprocess.run(["grep", "-h", "-a", "-E", r"\] ATTEMPT |: ACCEPTED|REJECTED"] + logs,
                         capture_output=True, text=True, encoding="utf-8", errors="replace").stdout
    att = re.compile(r"\] ATTEMPT \S+ '([^']+)'")
    cur, acc = None, set()
    for line in out.splitlines():
        m = att.search(line)
        if m:
            cur = m.group(1)
        elif cur and ": ACCEPTED" in line:
            acc.add(cur)
            cur = None
        elif cur and "REJECTED" in line:
            cur = None
    acc = sorted(acc)
    json.dump({"accepted": acc, "logs_read": len(logs),
               "made": datetime.date.today().isoformat()}, open(SEEN, "w", encoding="utf-8"), indent=0)
    return acc, "%d battle logs on this PC" % len(logs)


def group_of(status):
    s = status.lower()
    if s.startswith(("rejected", "skipped")) or "already rejected" in s or "family decision" in s:
        return "decided"
    return "open"


def open_kind(status, key):
    s = status
    if key in ("wh2_dlc11_hero_abilities_more_powder", "wh3_dlc25_abilities_restock_gunnery_school",
               "wh3_dlc27_character_abilities_master_of_mists", "wh3_dlc27_character_abilities_master_of_mists_custom",
               "wh3_dlc25_item_abilities_ominous_powder", "wh3_dlc29_unit_abilities_of_warp_and_ruin"):
        return "A. Shooting buffs and ammo refills"
    if "no enemy-unit read" in s or "explosive projectile" in s:
        return "B. Attacks cast at an enemy (magic missiles, bombs, breaths)"
    if any(t in s for t in ("no effect text", "ground-target-only", "enemy-ground placement", "auto: summon")):
        return "C. Other out-of-date exclusions"
    return "E. Self-centred explosions and whirlwinds (no change proposed)"


def main():
    ver, wbp = newest_workbook()
    ws = openpyxl.load_workbook(wbp, read_only=True)["Abilities"]
    trk = {r["key"]: r["status"] for r in bd.tracker_rows()}
    entries, _, _ = bd.mod_entries()
    fam = {k: e["trigger"] for e in entries for k in e["keys"]}
    seen, seen_src = battle_seen()
    seen = set(seen)

    rows = []
    for row in ws.iter_rows(min_row=2, values_only=True):
        if str(row[17]) != "IN-WHEEL":
            continue
        keys = [k.strip() for k in str(row[2]).split(";") if k.strip()]
        rows.append({"name": row[1], "keys": keys, "impl": str(row[19]), "status": trk.get(keys[0], "")})
    N = len(rows)
    impl = [r for r in rows if r["impl"] == "IMPLEMENTED"]
    proven = [r for r in impl if any(k in seen for k in r["keys"])]
    rest = [r for r in rows if r["impl"] != "IMPLEMENTED"]
    decided = [r for r in rest if group_of(r["status"]) == "decided"]
    opened = [r for r in rest if group_of(r["status"]) == "open"]
    assert len(proven) + (len(impl) - len(proven)) + len(decided) + len(opened) == N

    fams = collections.defaultdict(lambda: [0, 0, 0])
    for e in entries:
        f = fams[e["trigger"]]
        f[0] += 1
        f[1] += len(e["keys"])
        f[2] += sum(1 for k in e["keys"] if k in seen)
    kinds = collections.Counter(open_kind(r["status"], r["keys"][0]) for r in opened)
    dec_kinds = collections.Counter()
    for r in decided:
        s = r["status"]
        if "family decision" in s:
            dec_kinds["Friendly-fire and stealth families (your 2026-10-09 decision)"] += 1
        elif s.startswith("skipped"):
            dec_kinds["Skipped (stances, revisit later, unsuitable)"] += 1
        else:
            dec_kinds["Rejected (drawback, escape, friendly fire, other)"] += 1

    rounds = sorted(glob.glob(os.path.join(DOCS, "WH3_round1[2-9][0-9]_*.md")))[-6:]

    def pct(n):
        return 100.0 * n / N

    segs = [("proven", len(proven), "Automated, seen firing in a battle"),
            ("impl", len(impl) - len(proven), "Automated, not yet seen in a battle"),
            ("decided", len(decided), "Decided: not automated"),
            ("open", len(opened), "Still open")]
    bar = "".join('<div class="seg %s" style="width:%.3f%%" title="%s: %d"></div>' % (c, pct(n), html.escape(t), n)
                  for c, n, t in segs)
    legend = "".join('<li><span class="sw %s"></span>%s <b>%d</b> <span class="mut">(%.0f%%)</span></li>'
                     % (c, html.escape(t), n, pct(n)) for c, n, t in segs)
    famrows = "".join(
        '<tr><td><code>%s</code></td><td class="n">%d</td><td class="n">%d</td><td class="n">%d</td>'
        '<td class="hide-s"><div class="mini"><div style="width:%.1f%%"></div></div></td></tr>'
        % (html.escape(f), v[0], v[1], v[2], 100.0 * v[2] / v[1] if v[1] else 0)
        for f, v in sorted(fams.items(), key=lambda kv: (-kv[1][1], kv[0])))
    openrows = "".join('<tr><td>%s</td><td class="n">%d</td></tr>' % (html.escape(k), n)
                       for k, n in sorted(kinds.items()))
    decrows = "".join('<tr><td>%s</td><td class="n">%d</td></tr>' % (html.escape(k), n)
                      for k, n in sorted(dec_kinds.items()))
    roundrows = "".join('<li><a href="%s">%s</a></li>' % (os.path.basename(p),
                        html.escape(open(p, encoding="utf-8").readline().lstrip("# ").strip()))
                        for p in reversed(rounds))
    handled = len(impl) + len(decided)
    today = datetime.date.today().isoformat()

    page = """<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>WH3 Auto Abilities progress</title>
<style>
:root{--bg:#fbfaf7;--fg:#1d1c1a;--mut:#6b675f;--line:#e4e0d8;--card:#fff;
--proven:#2f7d4f;--impl:#8cc5a0;--decided:#b9b2a6;--open:#d9822b}
@media (prefers-color-scheme:dark){:root{--bg:#161513;--fg:#ece8e1;--mut:#a39d92;--line:#2e2b27;--card:#1f1d1a;
--proven:#4fae75;--impl:#2f6b48;--decided:#57524a;--open:#e0913f}}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--fg);font:15px/1.5 system-ui,Segoe UI,sans-serif}
main{max-width:980px;margin:0 auto;padding:24px 16px 48px}h1{font-size:26px;margin:0 0 4px}
h2{font-size:18px;margin:32px 0 10px}.mut{color:var(--mut)}code{font-size:13px;word-break:break-word;overflow-wrap:anywhere}
.big{display:flex;gap:16px;flex-wrap:wrap;margin:18px 0}.kpi{background:var(--card);border:1px solid var(--line);
border-radius:10px;padding:12px 16px;flex:1 1 200px}.kpi b{display:block;font-size:28px;line-height:1.2}
.bar{display:flex;height:28px;border-radius:8px;overflow:hidden;border:1px solid var(--line);margin:8px 0 10px}
.seg.proven,.sw.proven{background:var(--proven)}.seg.impl,.sw.impl{background:var(--impl)}
.seg.decided,.sw.decided{background:var(--decided)}.seg.open,.sw.open{background:var(--open)}
ul.legend{list-style:none;padding:0;margin:0;display:flex;flex-wrap:wrap;gap:6px 22px}
.sw{display:inline-block;width:12px;height:12px;border-radius:3px;margin-right:6px;vertical-align:-1px}
table{width:100%%;border-collapse:collapse;background:var(--card);border:1px solid var(--line);border-radius:10px;overflow:hidden}
th,td{padding:6px 10px;border-bottom:1px solid var(--line);text-align:left;vertical-align:middle}
th{font-size:13px;color:var(--mut);font-weight:600}.n{text-align:right;font-variant-numeric:tabular-nums}
.mini{height:8px;background:var(--line);border-radius:4px;overflow:hidden;min-width:80px}
.mini div{height:100%%;background:var(--proven)}.two{display:grid;grid-template-columns:1fr 1fr;gap:16px}
@media (max-width:700px){.two{grid-template-columns:1fr}.hide-s{display:none}}
.note{font-size:13px;color:var(--mut);margin-top:6px}
</style></head><body><main>
<h1>WH3 Auto Abilities: progress</h1>
<div class="mut">Built %(today)s from workbook v%(ver)d, the tracker, the mod's own table and %(seen_src)s.</div>
<div class="big">
<div class="kpi"><span class="mut">Abilities in the ability wheel</span><b>%(N)d</b></div>
<div class="kpi"><span class="mut">Handled (automated or decided)</span><b>%(handled_pct).0f%%</b><span class="mut">%(handled)d of %(N)d</span></div>
<div class="kpi"><span class="mut">Automated</span><b>%(nimpl)d</b><span class="mut">%(nfam)d trigger families</span></div>
<div class="kpi"><span class="mut">Seen firing in a battle</span><b>%(nproven)d</b><span class="mut">%(proven_pct).0f%% of the automated</span></div>
</div>
<div class="bar">%(bar)s</div>
<ul class="legend">%(legend)s</ul>
<p class="note">"Seen firing in a battle" means the game accepted a cast of that ability at least once in a real
battle on any build of the mod. It does not yet prove the current trigger, and an accepted cast can still be
dropped by the game. "Decided" means you ruled it out (rejected, skipped, or a family decision).</p>

<div class="two">
<div><h2>Still open (%(nopen)d)</h2><table><tr><th>Group</th><th class="n">Abilities</th></tr>%(openrows)s</table>
<p class="note">Groups from <a href="WH3_remaining_abilities_survey_2026-11-01.md">the survey</a>.</p></div>
<div><h2>Decided not to automate (%(ndec)d)</h2><table><tr><th>Why</th><th class="n">Abilities</th></tr>%(decrows)s</table></div>
</div>

<h2>Trigger families</h2>
<table><tr><th>Family</th><th class="n">Entries</th><th class="n">Keys</th><th class="n">Seen in battle</th><th class="hide-s"></th></tr>%(famrows)s</table>

<h2>Latest rounds</h2><ul>%(roundrows)s</ul>
</main></body></html>
""" % dict(today=today, ver=ver, seen_src=html.escape(seen_src), N=N, handled=handled,
           handled_pct=100.0 * handled / N, nimpl=len(impl), nfam=len(fams), nproven=len(proven),
           proven_pct=100.0 * len(proven) / len(impl), bar=bar, legend=legend, nopen=len(opened),
           openrows=openrows, ndec=len(decided), decrows=decrows, famrows=famrows, roundrows=roundrows)
    assert "\u2014" not in page
    open(OUT, "w", encoding="utf-8", newline="\n").write(page)
    print("wrote %s: %d in-wheel, %d automated (%d seen in battle), %d decided, %d open"
          % (OUT, N, len(impl), len(proven), len(decided), len(opened)))


if __name__ == "__main__":
    main()
