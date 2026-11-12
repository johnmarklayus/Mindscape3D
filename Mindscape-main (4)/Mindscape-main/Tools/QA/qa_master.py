"""MindScape QA master workbook (Documents/Reports/MindScape QA Master.xlsx).

One workbook for every QA report: each report is its own sheet of test cases, and the Masterlist sheet is rebuilt
from whatever report sheets exist. Testers only type on the report sheets (Status, Tester, Date tested, notes), so
rebuilding the Masterlist never loses their work, and re-adding a report that already exists keeps its sheet as is.

    from qa_master import add_report, rebuild_masterlist, save
    wb = load()
    add_report(wb, "Sheet name", "Report title", "Scope", [("ID", "Test case", "Preconditions", "Steps", "Expected"), ...])
    rebuild_masterlist(wb); save(wb)
"""
import os
from openpyxl import Workbook, load_workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.worksheet.datavalidation import DataValidation
from openpyxl.formatting.rule import CellIsRule
from openpyxl.worksheet.hyperlink import Hyperlink

PATH = os.path.join(os.path.dirname(__file__), "..", "..", "Documents", "Reports", "MindScape QA Master.xlsx")
F = "Arial"
thin = Side(style="thin", color="BFBFBF"); BORDER = Border(left=thin, right=thin, top=thin, bottom=thin)
HEAD = PatternFill("solid", fgColor="2F3E46"); YELLOW = PatternFill("solid", fgColor="FFF2CC")
STATUSES = ["Pass", "Fail", "Blocked", "Not run"]
COLORS = {"Pass": "C6EFCE", "Fail": "FFC7CE", "Blocked": "FFEB9C"}
HDR = 6          # header row on each report sheet
SPARE = 30       # extra rows the formulas and the Status dropdown cover, for cases added by hand
COLUMNS = ["ID", "Test case", "Preconditions", "Steps", "Expected result", "Status", "Tester", "Date tested", "Actual result / notes"]
WIDTHS = [8, 30, 30, 45, 60, 11, 14, 13, 34]
SKIP = {"Masterlist", "_Template"}


def load():
    return load_workbook(PATH) if os.path.exists(PATH) else Workbook()


def save(wb):
    wb.save(PATH)
    return os.path.abspath(PATH)


def _header(ws, row, names):
    for i, h in enumerate(names, 1):
        c = ws.cell(row=row, column=i, value=h)
        c.font = Font(name=F, bold=True, color="FFFFFF"); c.fill = HEAD; c.border = BORDER
        c.alignment = Alignment(wrap_text=True, vertical="center")


def _status_rules(ws, rng):
    dv = DataValidation(type="list", formula1='"' + ",".join(STATUSES) + '"', allow_blank=True)
    ws.add_data_validation(dv); dv.add(rng)
    for st, col in COLORS.items():
        ws.conditional_formatting.add(rng, CellIsRule(operator="equal", formula=[f'"{st}"'], fill=PatternFill("solid", fgColor=col)))


def add_report(wb, name, title, scope, cases):
    """Adds a report sheet (before _Template). An existing sheet of that name is left untouched."""
    if name in wb.sheetnames:
        return wb[name]
    index = wb.sheetnames.index("_Template") if "_Template" in wb.sheetnames else len(wb.sheetnames)
    ws = wb.create_sheet(name, index)
    ws["A1"] = title; ws["A1"].font = Font(name=F, size=14, bold=True)
    ws["A2"] = "Scope: " + scope
    ws["A3"] = "Build / version tested:"; ws["C3"].fill = YELLOW; ws["C3"].font = Font(name=F, size=10)
    ws["A4"] = "Fill in only the yellow cells. Status is a dropdown: Pass, Fail, Blocked, Not run. The Masterlist updates by itself."
    for c in ("A2", "A3", "A4"):
        ws[c].font = Font(name=F, size=10, italic=c != "A3", bold=c == "A3")
    ws["A5"] = "← Back to Masterlist"; ws["A5"].hyperlink = Hyperlink(ref="A5", location="'Masterlist'!A1")
    ws["A5"].font = Font(name=F, size=10, color="0563C1", underline="single")
    _header(ws, HDR, COLUMNS)
    for r, (cid, case, pre, steps, expected) in enumerate(cases, HDR + 1):
        for i, v in enumerate([cid, case, pre, steps, expected, "Not run", "", "", ""], 1):
            c = ws.cell(row=r, column=i, value=v)
            c.font = Font(name=F, size=10); c.border = BORDER; c.alignment = Alignment(wrap_text=True, vertical="top")
            if i >= 6: c.fill = YELLOW
            if i == 8: c.number_format = "yyyy-mm-dd"
    last = HDR + max(len(cases), 1)
    _status_rules(ws, f"F{HDR+1}:F{last+SPARE}")
    for col, w in zip("ABCDEFGHI", WIDTHS):
        ws.column_dimensions[col].width = w
    ws.freeze_panes = f"C{HDR+1}"
    return ws


def _reports(wb):
    out = []
    for ws in wb.worksheets:
        if ws.title in SKIP or ws.cell(row=HDR, column=1).value != "ID":
            continue
        rows = [r for r in range(HDR + 1, ws.max_row + 1) if ws.cell(row=r, column=1).value]
        out.append((ws.title, ws["A1"].value or ws.title, rows))
    return out


def rebuild_masterlist(wb):
    """Recreates the Masterlist from every report sheet (it holds formulas only, so nothing typed is lost)."""
    if "Masterlist" in wb.sheetnames:
        del wb["Masterlist"]
    if "Sheet" in wb.sheetnames and wb["Sheet"].max_row == 1:
        del wb["Sheet"]
    ml = wb.create_sheet("Masterlist", 0)
    wb.active = 0
    ml["A1"] = "MindScape 3D · QA Masterlist"; ml["A1"].font = Font(name=F, size=16, bold=True)
    ml["A2"] = ("One workbook for every QA report. Each report has its own sheet; this page shows the status of all of them. "
                "Statuses here are formulas: change them on the report sheets, not here.")
    ml["A2"].font = Font(name=F, size=10, italic=True)
    ml["A4"] = "Reports"; ml["A4"].font = Font(name=F, size=12, bold=True)
    _header(ml, 5, ["Sheet", "Report", "Cases", "Pass", "Fail", "Blocked", "Not run", "Pass rate", "Report status"])
    reports = _reports(wb)
    r = 6
    for name, title, rows in reports:
        end = (rows[-1] if rows else HDR + 1) + SPARE
        rng = f"'{name}'!$F${HDR+1}:$F${end}"
        ml.cell(row=r, column=1, value=name).hyperlink = Hyperlink(ref=f"A{r}", location=f"'{name}'!A1")
        ml.cell(row=r, column=1).font = Font(name=F, size=10, color="0563C1", underline="single")
        ml.cell(row=r, column=2, value=title)
        ml.cell(row=r, column=3, value=f"=COUNTA('{name}'!$A${HDR+1}:$A${end})")
        for j, st in enumerate(STATUSES, 4):
            ml.cell(row=r, column=j, value=f'=COUNTIF({rng},"{st}")')
        ml.cell(row=r, column=8, value=f"=IF(C{r}=0,0,D{r}/C{r})").number_format = "0%"
        ml.cell(row=r, column=9, value=f'=IF(C{r}=0,"No cases",IF(E{r}>0,"Fail",IF(F{r}>0,"Blocked",IF(D{r}=C{r},"Pass",IF(G{r}=C{r},"Not started","In progress")))))')
        for j in range(1, 10):
            c = ml.cell(row=r, column=j); c.border = BORDER
            if j != 1: c.font = Font(name=F, size=10)
        r += 1
    tot = r
    ml.cell(row=tot, column=2, value="All reports").font = Font(name=F, size=10, bold=True)
    for j, col in zip(range(3, 8), "CDEFG"):
        ml.cell(row=tot, column=j, value=f"=SUM({col}6:{col}{tot-1})").font = Font(name=F, size=10, bold=True)
    ml.cell(row=tot, column=8, value=f"=IF(C{tot}=0,0,D{tot}/C{tot})").number_format = "0%"
    ml.cell(row=tot, column=8).font = Font(name=F, size=10, bold=True)
    for j in range(1, 10):
        ml.cell(row=tot, column=j).border = BORDER
    for st, col in {"Pass": "C6EFCE", "Fail": "FFC7CE", "Blocked": "FFEB9C", "In progress": "DDEBF7"}.items():
        ml.conditional_formatting.add(f"I6:I{max(6, tot-1)}", CellIsRule(operator="equal", formula=[f'"{st}"'], fill=PatternFill("solid", fgColor=col)))

    start = tot + 3
    ml.cell(row=start - 1, column=1, value="All test cases").font = Font(name=F, size=12, bold=True)
    _header(ml, start, ["ID", "Report (sheet)", "Test case", "Status", "Tester", "Date tested", "Notes"])
    r = start + 1
    for name, title, rows in reports:
        for src in rows:
            ml.cell(row=r, column=1, value=f"='{name}'!A{src}").hyperlink = Hyperlink(ref=f"A{r}", location=f"'{name}'!A{src}")
            ml.cell(row=r, column=1).font = Font(name=F, size=10, color="0563C1", underline="single")
            ml.cell(row=r, column=2, value=name)
            ml.cell(row=r, column=3, value=f"='{name}'!B{src}")
            ml.cell(row=r, column=4, value=f"='{name}'!F{src}")
            for j, col in ((5, "G"), (6, "H"), (7, "I")):
                ml.cell(row=r, column=j, value=f"=IF('{name}'!{col}{src}=\"\",\"\",'{name}'!{col}{src})")
            ml.cell(row=r, column=6).number_format = "yyyy-mm-dd"
            for j in range(1, 8):
                c = ml.cell(row=r, column=j); c.border = BORDER; c.alignment = Alignment(wrap_text=True, vertical="top")
                if j != 1: c.font = Font(name=F, size=10)
            r += 1
    for st, col in COLORS.items():
        ml.conditional_formatting.add(f"D{start+1}:D{max(start+1, r-1)}", CellIsRule(operator="equal", formula=[f'"{st}"'], fill=PatternFill("solid", fgColor=col)))
    for col, w in zip("ABCDEFG", [14, 42, 40, 11, 12, 12, 40]):
        ml.column_dimensions[col].width = w
    ml.freeze_panes = "A6"
    return ml
