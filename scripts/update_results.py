#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Doc ket qua pytest (report.xml) vao 3 file Excel theo mapping.
Khong bia: TC khong co trong mapping hoac khong xuat hien trong report.xml giu nguyen 'Chua chay'.

Dung:
  pytest --junitxml=report.xml -q
  python -X utf8 update_results.py
  # hoac: python -X utf8 update_results.py --junit report.xml --today 16/09/2026
"""
import argparse
import json
import pathlib
import xml.etree.ElementTree as ET
from datetime import datetime

try:
    from openpyxl import load_workbook
    from openpyxl.styles import Font
except ImportError:
    raise SystemExit("Thieu openpyxl. Cai: pip install openpyxl")

SCRIPTS = pathlib.Path(__file__).parent          # .../scripts
ROOT = SCRIPTS.parent                             # thu muc du an
DOCS = ROOT
JUNIT_DEFAULT = ROOT / "report.xml"
MAPPING_DEFAULT = SCRIPTS / "test_case_mapping.json"

# Excel targets: file -> list of (sheet, id_col, result_col, date_col, data_row_start)
# kiem tra tu build_test_artifacts.py
TARGETS = [
    (DOCS / "Unit Test Case_fixed.xlsx", [
        ("UT_Details", 1, 10, 11, 6),  # A=ID, J=Result, K=Date, data bat dau row 6
    ]),
    (DOCS / "IT_Test Case_fixed.xlsx", [
        ("Auth_DB", 1, 7, 8, 9),
        ("Product_DB", 1, 7, 8, 9),
        ("Cart_Checkout_DB", 1, 7, 8, 9),
        ("Order_Inventory_DB", 1, 7, 8, 9),
    ]),
    (DOCS / "ST_Test Case_fixed.xlsx", [
        ("E2E_Flows", 1, 7, 8, 9),
    ]),
]

BLUE = Font(name="Arial", size=10, color="0000FF")
BLACK = Font(name="Arial", size=10, color="000000")


def parse_junit(junit_path):
    """Tra ve dict nodeid -> status Pass/Fail/Skipped/Error.
    nodeid dang classname.name hoac filepath::name
    """
    tree = ET.parse(junit_path)
    root = tree.getroot()
    result = {}
    for tc in root.iter("testcase"):
        classname = tc.get("classname", "")
        name = tc.get("name", "")
        # 2 dang nodeid de match linh hoat
        key1 = f"{classname}::{name}" if classname else name
        key2 = name
        # filepath dang classname . . . co the map tu file
        # tim file tu classname neu co
        status = "Pass"
        if tc.find("failure") is not None or tc.find("error") is not None:
            status = "Fail"
        elif tc.find("skipped") is not None:
            status = "N/A"
        result[key1] = status
        result[key2] = status
        # them dang file::name neu doan duoc file
        # classname nhu tests.unit.test_utils -> tests/unit/test_utils.py
        if classname.startswith("tests."):
            file_guess = classname.replace(".", "/") + ".py" + "::" + name
            result[file_guess] = status
    return result


def resolve_tc_status(tc_id, nodeids, junit_map):
    """1 TC co the map nhieu pytest nodeid. Quy tac: co 1 Fail => Fail; tat ca Pass => Pass; toan Skip => N/A."""
    statuses = []
    for nid in nodeids:
        s = junit_map.get(nid)
        if s is None:
            # thu match theo ten ham cuoi
            short = nid.split("::")[-1]
            s = junit_map.get(short)
        if s is not None:
            statuses.append(s)
    if not statuses:
        return None  # chua chay / khong tim thay trong report
    if "Fail" in statuses:
        return "Fail"
    if all(s == "N/A" for s in statuses):
        return "N/A"
    if all(s == "Pass" for s in statuses):
        return "Pass"
    # con lai (lan lon) coi la Fail de khong che dau loi
    return "Fail" if "Fail" in statuses else "Pass"


def clean_id(raw):
    if raw is None:
        return ""
    s = str(raw).strip()
    # ID trong Excel co dang [UT-XXX-01] hoac UT-XXX-01
    s = s.strip("[]").strip()
    return s


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--junit", default=str(JUNIT_DEFAULT))
    ap.add_argument("--mapping", default=str(MAPPING_DEFAULT))
    ap.add_argument("--today", default=datetime.now().strftime("%d/%m/%Y"))
    ap.add_argument("--dry-run", action="store_true", help="Chi in ra, khong ghi Excel")
    args = ap.parse_args()

    junit_path = pathlib.Path(args.junit)
    mapping_path = pathlib.Path(args.mapping)
    if not junit_path.exists():
        raise SystemExit(f"Khong tim thay {junit_path}. Chay pytest --junitxml=report.xml truoc.")
    if not mapping_path.exists():
        raise SystemExit(f"Khong tim thay {mapping_path}")

    junit_map = parse_junit(junit_path)
    with open(mapping_path, encoding="utf-8") as f:
        mapping = json.load(f)
    # bo key _comment
    mapping = {k: v for k, v in mapping.items() if not k.startswith("_")}

    # tinh status cho tung TC
    tc_status = {}
    for tc_id, nodeids in mapping.items():
        st = resolve_tc_status(tc_id, nodeids, junit_map)
        if st is not None:
            tc_status[tc_id] = st

    print(f"JUnit: {len(junit_map)//2} testcase (da gom key phu)")
    print(f"Mapping: {len(mapping)} TC ID, resolve duoc {len(tc_status)} co ket qua trong report.xml")
    for k, v in sorted(tc_status.items()):
        print(f"  {k}: {v}")

    if args.dry_run:
        print("[dry-run] Khong ghi Excel.")
        return

    for file_path, sheets in TARGETS:
        if not file_path.exists():
            print(f"Bo qua (khong ton tai): {file_path.name}")
            continue
        wb = load_workbook(file_path)
        changed = 0
        for sheet_name, id_col, res_col, date_col, start_row in sheets:
            if sheet_name not in wb.sheetnames:
                print(f"  {file_path.name}: thieu sheet {sheet_name}")
                continue
            ws = wb[sheet_name]
            for r in range(start_row, ws.max_row + 1):
                raw = ws.cell(r, id_col).value
                cid = clean_id(raw)
                if not cid or cid.upper() in ("ID",):
                    continue
                # header row?
                if r == start_row - 1:
                    continue
                new_status = tc_status.get(cid)
                if new_status is None:
                    continue  # giu nguyen Chua chay
                c = ws.cell(r, res_col)
                c.value = new_status
                c.font = BLUE
                d = ws.cell(r, date_col)
                d.value = args.today
                d.font = BLUE
                changed += 1
        if changed:
            try:
                wb.calculation.fullCalcOnLoad = True
                wb.calculation.forceFullCalc = True
                wb.calculation.calcMode = "auto"
            except Exception:
                pass
            wb.save(file_path)
        print(f"{file_path.name}: cap nhat {changed} dong -> {args.today}")

    print("Xong. Mo Excel sheet Test Report de xem % tu dong nhay (Ctrl+Alt+F9 neu chua tinh).")


if __name__ == "__main__":
    main()
