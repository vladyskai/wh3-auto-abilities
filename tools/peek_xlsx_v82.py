#!/usr/bin/env python3
"""Read-only: print the workbook v82 rows (and Cards rows) of the keys given on the command line."""
import sys

import openpyxl

SRC = r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_abilities_master_v82_2026-11-22.xlsx"


def main():
    keys = sys.argv[1:]
    wb = openpyxl.load_workbook(SRC, read_only=True)
    for r, row in enumerate(wb["Abilities"].iter_rows(values_only=True, min_row=2), start=2):
        k = str(row[2]).split(";")[0].strip()
        if k in keys:
            print("ROW", r, k)
            for c in (17, 19, 20, 21):
                print("   col", c + 1, "=", row[c])
    for r, row in enumerate(wb["Cards"].iter_rows(values_only=True, min_row=2), start=2):
        if any(k in str(row[3]) for k in keys):
            print("CARD", r, row)
    nm = wb["Numbers"]
    for r, row in enumerate(nm.iter_rows(values_only=True), start=1):
        if row[1] in ("enemy_wave", "enemy_wander", "enemy_ground_melee") or r in (7, 42):
            print("NUM", r, row[:5])
    wb.close()


if __name__ == "__main__":
    main()
