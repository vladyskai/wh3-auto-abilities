"""Independent verification of the CLEANED installed pack - no RPFM, no live
build session. Reads the installed .pack from the game folder as raw bytes:

  1) parses the PFH5 index and lists every entry;
  2) asserts the real (non-metadata) entry set is exactly the 5 ship files;
  3) byte-compares each entry's data slice against its source (sha256);
  4) raw-scans the whole pack for probe fragments / probe paths (must be absent);
  5) prints pack md5 + sha256 and compares dist/ against the installed file.
"""
import hashlib
import sys

sys.path.insert(0, r"C:/Users/vlady/Desktop/WH3_mod/tools")
from parse_pack_pfh5 import parse_bytes  # noqa: E402

GAME_PACK = r"C:/Program Files (x86)/Steam/steamapps/common/Total War WARHAMMER III/data/zz_test_deadly_onslaught.pack"
DIST_PACK = r"C:/Users/vlady/Desktop/WH3_mod/mod_source/dist/zz_test_deadly_onslaught.pack"
SRC_ROOT = r"C:/Users/vlady/Desktop/WH3_mod/mod_source"

EXPECTED = {
    "script/battle/mod/zz_test_deadly_onslaught.lua":
        SRC_ROOT + "/script/battle/mod/zz_test_deadly_onslaught.lua",
    "ui/templates/zz_auto_badge.twui.xml":
        SRC_ROOT + "/ui/templates/zz_auto_badge.twui.xml",
    "ui/zz_auto/auto_badge.png": SRC_ROOT + "/ui/zz_auto/auto_badge.png",
    "ui/zz_auto/blank.png": SRC_ROOT + "/ui/zz_auto/blank.png",
    "ui/common ui/special_ability_tooltip.twui.xml":
        SRC_ROOT + "/ui/common ui/special_ability_tooltip.twui.xml",
}

pack = open(GAME_PACK, "rb").read()
print("=" * 72)
print("INSTALLED PACK:", GAME_PACK)
print("size  :", len(pack))
print("md5   :", hashlib.md5(pack).hexdigest())
print("sha256:", hashlib.sha256(pack).hexdigest())
print("dist/ identical to installed:", open(DIST_PACK, "rb").read() == pack)
print("=" * 72)

entries = parse_bytes(pack)
reserved = [e for e in entries if e["path"].endswith(".rpfm_reserved")]
real = [e for e in entries if not e["path"].endswith(".rpfm_reserved")]
print(f"index entries: {len(entries)}   real files: {len(real)}   rpfm metadata: {len(reserved)}")
for e in entries:
    kind = "metadata" if e["path"].endswith(".rpfm_reserved") else "FILE"
    print(f"  [{kind:8s}] {e['size']:>9d}  flag={e['flag']}  @{e['offset']:>9d}  {e['path']}")

real_paths = sorted(e["path"] for e in real)
exp_paths = sorted(EXPECTED)
set_ok = real_paths == exp_paths
print("\nreal entry set == expected 5 files:", set_ok)
assert set_ok, f"{real_paths} != {exp_paths}"
assert not any("zz_probe" in e["path"] for e in entries), "a probe path is in the index!"

print("\nper-file byte-identity (data slice vs source):")
all_ok = True
for e in real:
    src = open(EXPECTED[e["path"]], "rb").read()
    slice_ = pack[e["offset"]: e["offset"] + e["size"]]
    ident = slice_ == src
    all_ok = all_ok and ident
    print(f"  {e['path']}")
    print(f"    slice {len(slice_):>7d} bytes sha256 {hashlib.sha256(slice_).hexdigest()}")
    print(f"    src   {len(src):>7d} bytes sha256 {hashlib.sha256(src).hexdigest()}")
    print(f"    IDENTICAL: {ident}")

print("\nprobe absence (raw byte scan of the whole installed pack):")
frags = [b"[zz_probe_ui_text]", b"zz_probe_ui_text_log.txt", b"[zz_probe_unit_reads]",
         b"zz_probe_unit_reads_log.txt", b"zz_probe_ui(", b"zz_probe_",
         b"zz_probe_ui_text.lua", b"zz_probe_unit_reads.lua"]
frag_ok = True
for f in frags:
    n = pack.count(f)
    frag_ok = frag_ok and n == 0
    print(f"  {f!r:42} count={n}")
print("all probe fragments absent:", frag_ok)

print("\nsanity: the shipped content IS present (counts > 0):")
for f in [b"zz_test_deadly_onslaught", b"foe_seeker", b"zz_auto_badge"]:
    print(f"  {f!r:32} count={pack.count(f)}")

verdict = (all_ok and frag_ok and set_ok)
print("\nRESULT:", "PASS" if verdict else "FAIL")
sys.exit(0 if verdict else 1)
