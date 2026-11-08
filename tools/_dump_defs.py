
import openpyxl
p=r"C:\Users\vlady\Desktop\WH3_mod\docs\WH3_abilities_master_v18_2026-10-18.xlsx"
wb=openpyxl.load_workbook(p, data_only=True)
d=wb["Definitions"]
print("dims",d.max_row,d.max_column)
for r in range(1,70):
    vals=[d.cell(row=r,column=c).value for c in range(1,5)]
    if any(v not in (None,"") for v in vals):
        print(r," | ".join("" if v is None else str(v)[:130] for v in vals))
