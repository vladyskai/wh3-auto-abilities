"""The ONE place that says where the project's game-data extracts live.

Until 2026-11-01 the extracts sat in %LOCALAPPDATA%\\Temp\\wh3\\, and Windows Temp
cleanup emptied parts of it twice (the uieff\\ set, then wh3_layouts\\). They now
live inside the project, next to everything else that is archived:

    gamedata\\wh3\\                     the TSV extracts (regenerate: tools\\extract_gamedata.py)
    gamedata\\wh3\\uieff\\              the effect / ui-effect / stat-name extracts
    gamedata\\temp_snapshot_2026-11-01\\ the Temp copy as found on 2026-11-01 (frozen, never edited)

Every live tool imports its paths from here; nothing new may point at Temp.
"""
import os

ROOT = r"C:\Users\vlady\Desktop\WH3_mod"
GAMEDATA = os.path.join(ROOT, "gamedata", "wh3")
UIEFF = os.path.join(GAMEDATA, "uieff")
ARMY_SPEC = os.path.join(GAMEDATA, "army_spec.tsv")
UNIT_ABILITIES = os.path.join(GAMEDATA, "unit_abilities.tsv")
# forward-slash form, for Lua harnesses and the RPFM builders
GAMEDATA_FWD = GAMEDATA.replace("\\", "/")
ARMY_SPEC_FWD = ARMY_SPEC.replace("\\", "/")
GAME_DATA_DIR = r"C:/Program Files (x86)/Steam/steamapps/common/Total War WARHAMMER III/data"
