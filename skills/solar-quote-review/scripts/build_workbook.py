#!/usr/bin/env python3
"""Build the vendor-quote review workbook from a JSON spec.

Usage: python build_workbook.py spec.json output.xlsx
Then:  python <xlsx-skill>/scripts/recalc.py output.xlsx   (mandatory; must report zero errors)

Sheets: Summary | Quote | Tariff | Bills | Benchmark | Sizing | Payback | Assumptions
Conventions: Arial; blue = input, black = formula, green = cross-sheet link, yellow fill = key lever.
All money in Rs (not lakhs) so it reconciles to the bill and the quote to the rupee.
See assets/example_spec.json for the schema.
"""
import json
import sys

from openpyxl import Workbook
from openpyxl.comments import Comment
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

BLUE, BLACK, GREEN = "0000FF", "000000", "008000"
HDR_FILL = PatternFill("solid", fgColor="1F4E78")
KEY_FILL = PatternFill("solid", fgColor="FFFF00")
SUB_FILL = PatternFill("solid", fgColor="DDEBF7")
THIN = Side(style="thin", color="BFBFBF")
BOX = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)
RS = '#,##0;(#,##0);"-"'
RS2 = '#,##0.00;(#,##0.00);"-"'
PCT = '0.0%;(0.0%);"-"'
NUM1 = '#,##0.0;(#,##0.0);"-"'
NUM2 = '0.00'


def font(color=BLACK, bold=False, size=10, italic=False):
    return Font(name="Arial", color=color, bold=bold, size=size, italic=italic)


def put(ws, ref, value, color=BLACK, fmt=None, bold=False, fill=None, italic=False):
    c = ws[ref]
    c.value = value
    c.font = font(color, bold, italic=italic)
    c.border = BOX
    if fmt:
        c.number_format = fmt
    if fill:
        c.fill = fill
    return c


def note(ws, ref_, text):
    c = Comment(text, "solar-quote-review")
    c.width, c.height = 320, 140
    ws[ref_].comment = c


def title(ws, text, subtitle=None):
    ws["A1"].value = text
    ws["A1"].font = font(bold=True, size=13)
    if subtitle:
        ws["A2"].value = subtitle
        ws["A2"].font = font(italic=True, size=9)


def header(ws, row, labels, col=1):
    for i, lab in enumerate(labels):
        c = ws.cell(row=row, column=col + i, value=lab)
        c.font = Font(name="Arial", bold=True, color="FFFFFF", size=10)
        c.fill = HDR_FILL
        c.alignment = Alignment(wrap_text=True, vertical="center")
        c.border = BOX


def widths(ws, w):
    for i, x in enumerate(w, start=1):
        ws.column_dimensions[get_column_letter(i)].width = x


def slab_charge(units_ref, n):
    """Telescopic energy charge for units_ref against Tariff!A5:C(4+n). Top slab upper = 1E9."""
    last = 4 + n
    L, H, R = f"Tariff!$A$5:$A${last}", f"Tariff!$B$5:$B${last}", f"Tariff!$C$5:$C${last}"
    u = units_ref
    return f"=SUMPRODUCT(({u}>{L})*((({u}<{H})*{u}+({u}>={H})*{H})-{L})*{R})"


def build(spec, out):
    m, q, sysd = spec["meta"], spec["quote"], spec["system"]
    eco, load, neg = spec["economics"], spec["load"], spec["negotiation"]
    wb = Workbook()
    ref = {}

    # ---------------- Tariff ----------------
    t = wb.active
    t.title = "Tariff"
    title(t, f'Tariff: {spec["tariff"]["name"]}', f'Source: {spec["tariff"]["source"]}')
    header(t, 4, ["From (units)", "To (units)", "Rate (Rs/unit)", "Note"])
    slabs = spec["tariff"]["slabs"]
    for i, s in enumerate(slabs):
        r = 5 + i
        put(t, f"A{r}", s["lower"], BLUE, "#,##0")
        put(t, f"B{r}", s["upper"] if s["upper"] is not None else 1e9, BLUE, "#,##0")
        put(t, f"C{r}", s["rate"], BLUE, NUM2)
        put(t, f"D{r}", "Top slab: 1E9 = no upper limit" if s["upper"] is None else "", italic=True)
    nS = len(slabs)
    r = 6 + nS
    t[f"A{r}"].value = ("Energy charge is telescopic: each slab's rate applies only to units inside it. "
                        "Verify on Bills sheet: computed charge must match the bill to the rupee.")
    t[f"A{r}"].font = font(italic=True, size=9)
    widths(t, [14, 14, 16, 34])

    # ---------------- Quote ----------------
    qs = wb.create_sheet("Quote")
    title(qs, f'Quote review: {m["vendor"]}', f'Client: {m["client"]}  |  Review date: {m["review_date"]}')
    put(qs, "A4", "Quoted total incl. GST (Rs)", bold=True)
    put(qs, "B4", q["total_incl_gst"], BLUE, RS2, fill=KEY_FILL)
    ref["quote_total"] = "Quote!$B$4"

    header(qs, 6, ["Item", "Specification as quoted", "Qty"])
    r = 7
    for li in q["line_items"]:
        put(qs, f"A{r}", li["item"], BLUE)
        put(qs, f"B{r}", li["spec"], BLUE)
        put(qs, f"C{r}", li["qty"], BLUE)
        r += 1

    r += 1
    pay_hdr = r
    header(qs, r, ["Payment stage", "% (input)", "Computed Rs", "Stated Rs", "Diff Rs", "Before delivery? (1/0)"])
    r += 1
    p0 = r
    for p in q["payment"]:
        put(qs, f"A{r}", p["stage"], BLUE)
        put(qs, f"B{r}", p["pct"], BLUE, PCT)
        put(qs, f"C{r}", f"=B{r}*{ref['quote_total']}", fmt=RS2)
        put(qs, f"D{r}", p.get("stated_amount"), BLUE, RS2)
        put(qs, f"E{r}", f"=IF(D{r}=\"\",0,C{r}-D{r})", fmt=RS2)
        put(qs, f"F{r}", 1 if p["before_delivery"] else 0, BLUE, "0")
        r += 1
    p1 = r - 1
    put(qs, f"A{r}", "Total", bold=True)
    put(qs, f"B{r}", f"=SUM(B{p0}:B{p1})", fmt=PCT, bold=True)
    put(qs, f"C{r}", f"=SUM(C{p0}:C{p1})", fmt=RS2, bold=True)
    put(qs, f"D{r}", f"=SUM(D{p0}:D{p1})", fmt=RS2, bold=True)
    put(qs, f"E{r}", f"=SUM(E{p0}:E{p1})", fmt=RS2, bold=True)
    ref["pay_check"] = f"Quote!$B${r}"
    ref["pay_diff"] = f"Quote!$E${r}"
    r += 1
    put(qs, f"A{r}", "Money at risk before delivery (Rs)", bold=True)
    put(qs, f"C{r}", f"=SUMPRODUCT(C{p0}:C{p1},F{p0}:F{p1})", fmt=RS, bold=True, fill=KEY_FILL)
    ref["at_risk"] = f"Quote!$C${r}"
    r += 1
    put(qs, f"A{r}", "Share paid before delivery")
    put(qs, f"C{r}", f"=SUMPRODUCT(B{p0}:B{p1},F{p0}:F{p1})", fmt=PCT)
    ref["at_risk_pct"] = f"Quote!$C${r}"

    r += 2
    header(qs, r, ["Subsidy", "Rs", "Certainty"])
    r += 1
    s0 = r
    for s in q["subsidies"]:
        put(qs, f"A{r}", s["name"], BLUE)
        put(qs, f"B{r}", s["amount"], BLUE, RS)
        put(qs, f"C{r}", s["certainty"], BLUE)
        r += 1
    put(qs, f"A{r}", "Total subsidy", bold=True)
    put(qs, f"B{r}", f"=SUM(B{s0}:B{r-1})", fmt=RS, bold=True)
    ref["subsidy"] = f"Quote!$B${r}"
    r += 1
    put(qs, f"A{r}", "Net cost after subsidy (Rs)", bold=True)
    put(qs, f"B{r}", f"={ref['quote_total']}-{ref['subsidy']}", fmt=RS2, bold=True)
    ref["net_cost"] = f"Quote!$B${r}"
    widths(qs, [40, 42, 18, 16, 12, 18])

    # ---------------- Bills ----------------
    b = wb.create_sheet("Bills")
    title(b, "Client bill analysis", "Inputs from the DISCOM bills (blue). Computed charge must match the bill.")
    header(b, 4, ["Period", "Days", "Units", "kWh/day", "Avg load kW", "Energy charge (bill)",
                  "Energy charge (computed)", "Diff Rs", "Subsidy line", "Net payable",
                  "Max demand kW", "Sanctioned kW", "MD / sanctioned"])
    bills = spec["bills"]
    for i, bl in enumerate(bills):
        r = 5 + i
        put(b, f"A{r}", bl["period"], BLUE)
        put(b, f"B{r}", bl["days"], BLUE, "0")
        put(b, f"C{r}", bl["units"], BLUE, "#,##0")
        put(b, f"D{r}", f"=C{r}/B{r}", fmt=NUM1)
        put(b, f"E{r}", f"=D{r}/24", fmt=NUM2)
        put(b, f"F{r}", bl["energy_charge"], BLUE, RS2)
        put(b, f"G{r}", slab_charge(f"C{r}", nS), fmt=RS2)
        put(b, f"H{r}", f"=G{r}-F{r}", fmt=RS2, fill=KEY_FILL)
        put(b, f"I{r}", bl.get("subsidy_line", 0), BLUE, RS2)
        put(b, f"J{r}", bl.get("net_payable"), BLUE, RS)
        put(b, f"K{r}", bl["max_demand_kw"], BLUE, NUM2)
        put(b, f"L{r}", bl["sanctioned_kw"], BLUE, NUM2)
        put(b, f"M{r}", f"=K{r}/L{r}", fmt=PCT)
    b0, b1 = 5, 4 + len(bills)
    r = b1 + 2
    put(b, f"A{r}", "Peak max demand across bills (kW)", bold=True)
    put(b, f"C{r}", f"=MAX(K{b0}:K{b1})", fmt=NUM2, bold=True)
    ref["peak_md"] = f"Bills!$C${r}"
    r += 1
    put(b, f"A{r}", "Average kWh/day across bills", bold=True)
    put(b, f"C{r}", f"=SUM(C{b0}:C{b1})/SUM(B{b0}:B{b1})", fmt=NUM1, bold=True)
    ref["avg_kwh_day"] = f"Bills!$C${r}"
    r += 1
    put(b, f"A{r}", "Tariff check: max |diff| (Rs) - must be ~0", bold=True)
    put(b, f"C{r}", f"=MAX(MAX(H{b0}:H{b1}),-MIN(H{b0}:H{b1}))", fmt=RS2, bold=True, fill=KEY_FILL)
    ref["tariff_check"] = f"Bills!$C${r}"
    r += 1
    put(b, f"A{r}", "Sanctioned load (kW)")
    put(b, f"C{r}", f"=MAX(L{b0}:L{b1})", fmt=NUM2)
    ref["sanctioned"] = f"Bills!$C${r}"
    widths(b, [26, 7, 9, 9, 10, 15, 16, 10, 12, 12, 11, 11, 12])

    # ---------------- Benchmark ----------------
    bm = wb.create_sheet("Benchmark")
    title(bm, "Market benchmark: component build-up",
          "Ranges researched online at review date. Re-search every time; never reuse old figures.")
    header(bm, 4, ["Component", "Unit", "Qty", "Low rate", "High rate", "Low Rs", "High Rs", "Source / certainty"])
    benches = spec["benchmarks"]
    for i, x in enumerate(benches):
        r = 5 + i
        put(bm, f"A{r}", x["component"], BLUE)
        put(bm, f"B{r}", x["unit"], BLUE)
        put(bm, f"C{r}", x["qty"], BLUE, NUM2)
        put(bm, f"D{r}", x["low"], BLUE, RS)
        put(bm, f"E{r}", x["high"], BLUE, RS)
        put(bm, f"F{r}", f"=C{r}*D{r}", fmt=RS)
        put(bm, f"G{r}", f"=C{r}*E{r}", fmt=RS)
        put(bm, f"H{r}", x["source"], BLUE)
    k0, k1 = 5, 4 + len(benches)
    r = k1 + 1
    put(bm, f"A{r}", "Market range (Rs)", bold=True)
    put(bm, f"F{r}", f"=SUM(F{k0}:F{k1})", fmt=RS, bold=True)
    put(bm, f"G{r}", f"=SUM(G{k0}:G{k1})", fmt=RS, bold=True)
    ref["mkt_low"], ref["mkt_high"] = f"Benchmark!$F${r}", f"Benchmark!$G${r}"
    r += 1
    put(bm, f"A{r}", "Midpoint (Rs)")
    put(bm, f"G{r}", f"=AVERAGE({ref['mkt_low']},{ref['mkt_high']})", fmt=RS)
    ref["mkt_mid"] = f"Benchmark!$G${r}"
    r += 1
    put(bm, f"A{r}", "Vendor quote (Rs)")
    put(bm, f"G{r}", f"={ref['quote_total']}", GREEN, RS)
    r += 1
    put(bm, f"A{r}", "Quote vs top of range", bold=True)
    put(bm, f"G{r}", f"={ref['quote_total']}/{ref['mkt_high']}-1", fmt=PCT, bold=True, fill=KEY_FILL)
    ref["vs_high"] = f"Benchmark!$G${r}"
    r += 1
    put(bm, f"A{r}", "Quote vs midpoint", bold=True)
    put(bm, f"G{r}", f"={ref['quote_total']}/{ref['mkt_mid']}-1", fmt=PCT, bold=True)
    ref["vs_mid"] = f"Benchmark!$G${r}"
    cc = spec.get("catalogue_check")
    if cc:
        r += 2
        header(bm, r, ["Vendor catalogue cross-check", "", "", "", "", "Min Rs", "Max Rs", "How it works"])
        note(bm, f"A{r}",
             "Question: how much of the gap between the vendor's own nearest catalogue system and this "
             "quote is explained by the extra hardware, priced at market rates? Whatever is left is a "
             "premium the vendor cannot justify from its own price list.")
        r += 1
        put(bm, f"A{r}", cc["label"], BLUE)
        put(bm, f"F{r}", cc["price"], BLUE, RS)
        put(bm, f"G{r}", cc["price"], BLUE, RS)
        put(bm, f"H{r}", "Vendor's own list price for its nearest standard system", italic=True)
        c0 = r
        r += 1
        put(bm, f"A{r}", "Justified uplift for extra hardware", BLUE)
        put(bm, f"F{r}", cc["justified_uplift_low"], BLUE, RS)
        put(bm, f"G{r}", cc["justified_uplift_high"], BLUE, RS)
        put(bm, f"H{r}", cc["note"], BLUE)
        r += 1
        put(bm, f"A{r}", "Fair price on vendor's own pricing (catalogue + uplift)", bold=True)
        put(bm, f"F{r}", f"=F{c0}+F{c0+1}", fmt=RS, bold=True)
        put(bm, f"G{r}", f"=G{c0}+G{c0+1}", fmt=RS, bold=True)
        put(bm, f"H{r}", "Catalogue price + uplift, low and high", italic=True)
        fr = r
        r += 1
        put(bm, f"A{r}", "Vendor quote", bold=True)
        put(bm, f"F{r}", f"={ref['quote_total']}", GREEN, RS)
        put(bm, f"G{r}", f"={ref['quote_total']}", GREEN, RS)
        r += 1
        put(bm, f"A{r}", "Unexplained premium (min / max)", bold=True)
        put(bm, f"F{r}", f"=F{r-1}-G{fr}", fmt=RS, bold=True, fill=KEY_FILL)
        put(bm, f"G{r}", f"=G{r-1}-F{fr}", fmt=RS, bold=True, fill=KEY_FILL)
        put(bm, f"H{r}", "Min = quote - HIGH fair price; Max = quote - LOW fair price", italic=True)
        note(bm, f"F{r}",
             "Minimum premium: quote minus the HIGHEST fair price (vendor given full benefit of doubt).")
        note(bm, f"G{r}",
             "Maximum premium: quote minus the LOWEST fair price.")
        ref["prem_min"], ref["prem_max"] = f"Benchmark!$F${r}", f"Benchmark!$G${r}"
    widths(bm, [40, 10, 8, 11, 11, 13, 13, 52])

    # ---------------- Sizing ----------------
    sz = wb.create_sheet("Sizing")
    title(sz, "Technical sizing vs the client's bill")
    rows = [
        ("PV array (kWp)", sysd["pv_kwp"], BLUE, NUM2, "pv"),
        ("Inverter rating (kW)", sysd["inverter_kw"], BLUE, NUM2, "inv"),
        ("Phases", sysd["phases"], BLUE, "0", "ph"),
        ("Max single-phase output (kVA, datasheet)", sysd.get("max_single_phase_kva"), BLUE, NUM2, "sp"),
        ("Battery nameplate (kWh)", sysd["battery_kwh"], BLUE, NUM2, "batt"),
        ("Usable fraction", sysd["battery_usable_frac"], BLUE, PCT, "usable"),
        ("Backup load, low (kW)", load["backup_load_kw_low"], BLUE, NUM2, "bl_lo"),
        ("Backup load, high (kW)", load["backup_load_kw_high"], BLUE, NUM2, "bl_hi"),
        ("Generation (kWh/kWp/day)", eco["gen_kwh_per_kwp_day"], BLUE, NUM2, "yield"),
    ]
    header(sz, 4, ["Parameter", "Value", "Note"])
    r = 5
    for lab, val, col, fmt, key in rows:
        put(sz, f"A{r}", lab)
        put(sz, f"B{r}", val, col, fmt)
        ref[key] = f"Sizing!$B${r}"
        r += 1
    put(sz, f"C{5+6}", load.get("note", ""), BLUE)
    r += 1
    header(sz, r, ["Check", "Result", "Read"])
    r += 1
    checks = [
        ("Peak max demand from bills (kW)", f"={ref['peak_md']}", GREEN, NUM2, ""),
        ("Inverter / peak demand (x)", f"={ref['inv']}/{ref['peak_md']}", BLACK, "0.00\"x\"",
         ">1.5x: ask for a smaller-inverter price unless per-phase loading needs it"),
        ("Balanced per-phase capacity (kW)", f"={ref['inv']}/{ref['ph']}", BLACK, NUM2,
         "Split AC loads across phases"),
        ("PV / sanctioned load", f"={ref['pv']}/{ref['sanctioned']}", BLACK, PCT,
         ">100% usually needs load enhancement before net metering"),
        ("Usable battery (kWh)", f"={ref['batt']}*{ref['usable']}", BLACK, NUM2, ""),
        ("Runtime at average bill load (h)", f"={ref['batt']}*{ref['usable']}/({ref['avg_kwh_day']}/24)",
         BLACK, NUM1, "Whole-house average; evening peaks shorten it"),
        ("Runtime at backup load high (h)", f"={ref['batt']}*{ref['usable']}/{ref['bl_hi']}", BLACK, NUM1, ""),
        ("Runtime at backup load low (h)", f"={ref['batt']}*{ref['usable']}/{ref['bl_lo']}", BLACK, NUM1, ""),
        ("Daily PV generation (kWh)", f"={ref['pv']}*{ref['yield']}", BLACK, NUM1, ""),
        ("Daily generation / battery usable (x)", f"={ref['pv']}*{ref['yield']}/({ref['batt']}*{ref['usable']})",
         BLACK, "0.00\"x\"", ">=1x: array can refill battery on a normal day"),
        ("Daily generation / avg consumption", f"={ref['pv']}*{ref['yield']}/{ref['avg_kwh_day']}",
         BLACK, PCT, "Share of load the array can offset"),
    ]
    for lab, f, col, fmt, read in checks:
        put(sz, f"A{r}", lab)
        put(sz, f"B{r}", f, col, fmt)
        put(sz, f"C{r}", read, italic=True)
        if lab.startswith("Inverter /"):
            ref["inv_ratio"] = f"Sizing!$B${r}"
        if lab.startswith("Runtime at backup load high"):
            ref["rt_hi"] = f"Sizing!$B${r}"
        if lab.startswith("Runtime at backup load low"):
            ref["rt_lo"] = f"Sizing!$B${r}"
        r += 1
    widths(sz, [42, 14, 62])

    # ---------------- Payback ----------------
    pb = wb.create_sheet("Payback")
    title(pb, "Bill savings and payback",
          "Savings = energy charge before minus after, at telescopic slab rates. Ignores subsidy-line changes.")
    put(pb, "A4", "Cycles per year")
    put(pb, "B4", eco["cycles_per_year"], BLUE, "0")
    note(pb, "B4", "Number of bills per year. Bi-monthly billing (e.g. TNPDCL) = 6; monthly = 12. "
                   "Read 'Billing Cycle' on the client's bill.")
    put(pb, "A5", "Existing system output lost on replacement (kWh/day)")
    put(pb, "B5", eco.get("existing_system_kwh_day", 0), BLUE, NUM2)
    cols = [(bl["period"], f"=Bills!B{5+i}", f"=Bills!C{5+i}", GREEN) for i, bl in enumerate(bills)]
    cols += [(f"Scenario {u:,} units", eco["scenario_days"], u, BLUE) for u in eco["scenario_units"]]
    header(pb, 7, ["Line"] + [c[0] for c in cols])
    labels = ["Days", "Units consumed (grid, today)", "Existing system output lost", "New PV generation",
              "Net import after solar", "Energy charge today", "Energy charge after", "Saving per cycle",
              "Annualised (if every cycle like this)", "Net import <= 500? (cliff check)"]
    for i, lab in enumerate(labels):
        put(pb, f"A{8+i}", lab, bold=(i in (7, 8)))
    for j, (_, days, units, col) in enumerate(cols):
        cl = get_column_letter(2 + j)
        put(pb, f"{cl}8", days, col, "0")
        put(pb, f"{cl}9", units, col, "#,##0")
        put(pb, f"{cl}10", f"=$B$5*{cl}8", fmt="#,##0")
        put(pb, f"{cl}11", f"={ref['pv']}*{ref['yield']}*{cl}8", fmt="#,##0")
        put(pb, f"{cl}12", f"=MAX(0,{cl}9+{cl}10-{cl}11)", fmt="#,##0")
        put(pb, f"{cl}13", slab_charge(f"{cl}9", nS), fmt=RS)
        put(pb, f"{cl}14", slab_charge(f"{cl}12", nS), fmt=RS)
        put(pb, f"{cl}15", f"={cl}13-{cl}14", fmt=RS, bold=True)
        put(pb, f"{cl}16", f"={cl}15*$B$4", fmt=RS, bold=True)
        put(pb, f"{cl}17", f"=IF({cl}12<=500,\"YES - check free-unit rule\",\"no\")")
    note(pb, "A17", "Flag only, not valued. Tamil Nadu (from May 2026): <=500 units per bi-monthly bill "
                    "gets 200 free units, above 500 gets 100. If solar pulls net import under 500, savings "
                    "may be understated. Confirm with the DISCOM whether net-metered homes are billed on "
                    "net import and how free units are valued (the bill's 'Govt subsidy' line does not "
                    "equal free units x first-slab rate). Change the 500 threshold for other states.")
    lastc = get_column_letter(1 + len(cols))
    put(pb, "A19", "Annual saving, low (Rs)", bold=True)
    put(pb, "B19", f"=MIN(B16:{lastc}16)", fmt=RS, bold=True, fill=KEY_FILL)
    put(pb, "A20", "Annual saving, high (Rs)", bold=True)
    put(pb, "B20", f"=MAX(B16:{lastc}16)", fmt=RS, bold=True, fill=KEY_FILL)
    ref["sav_lo"], ref["sav_hi"] = "Payback!$B$19", "Payback!$B$20"
    header(pb, 22, ["Cost case", "Net cost Rs", "Payback yrs (high saving)", "Payback yrs (low saving)"])
    r = 23
    for cc_ in eco["cost_cases"]:
        put(pb, f"A{r}", cc_["label"], BLUE)
        put(pb, f"B{r}", cc_["cost"], BLUE, RS)
        put(pb, f"C{r}", f"=IFERROR(B{r}/$B$20,\"n/a\")", fmt=NUM1)
        put(pb, f"D{r}", f"=IFERROR(B{r}/$B$19,\"n/a\")", fmt=NUM1)
        r += 1
    ref["pb_first"] = "Payback!$C$23"
    ref["pb_first_lo"] = "Payback!$D$23"
    pb[f"A{r+1}"].value = ("Read: a hybrid + battery earns little extra under net metering; the backup "
                           "portion is outage insurance. Show solar-only payback separately in the memo.")
    pb[f"A{r+1}"].font = font(italic=True, size=9)
    widths(pb, [48] + [20] * len(cols))

    # ---------------- Assumptions ----------------
    a = wb.create_sheet("Assumptions")
    title(a, "Assumptions and certainty tags", "Plain = traced to a source; Likely = inferred; Assumed = chosen")
    header(a, 4, ["Tag", "Assumption", "Change if"])
    for i, x in enumerate(spec["assumptions"]):
        put(a, f"A{5+i}", x["tag"], BLUE)
        put(a, f"B{5+i}", x["item"], BLUE)
        put(a, f"C{5+i}", x["change_if"], BLUE)
    widths(a, [10, 80, 40])

    # ---------------- Summary (first tab) ----------------
    s = wb.create_sheet("Summary", 0)
    title(s, f'Vendor quote review: {m["client"]}',
          f'{m["vendor"]}  |  {m["review_date"]}  |  {m["version"]}  |  Requires professional review')
    put(s, "A4", "Decision", bold=True)
    put(s, "B4", m["decision"], BLUE, bold=True, fill=KEY_FILL)
    put(s, "A5", "Basis")
    put(s, "B5", m["decision_basis"], BLUE)
    lines = [
        ("Quoted price incl. GST (Rs)", f"={ref['quote_total']}", RS),
        ("Market range low (Rs)", f"={ref['mkt_low']}", RS),
        ("Market range high (Rs)", f"={ref['mkt_high']}", RS),
        ("Quote vs top of range", f"={ref['vs_high']}", PCT),
        ("Quote vs midpoint", f"={ref['vs_mid']}", PCT),
    ]
    if "prem_min" in ref:
        lines += [("Unexplained premium vs vendor catalogue, min (Rs)", f"={ref['prem_min']}", RS),
                  ("Unexplained premium vs vendor catalogue, max (Rs)", f"={ref['prem_max']}", RS)]
    lines += [
        ("Counter offer (Rs)", neg["counter"], RS),
        ("Walk-away above (Rs)", neg["walk_away"], RS),
        ("Money at risk before delivery (Rs)", f"={ref['at_risk']}", RS),
        ("Share paid before delivery", f"={ref['at_risk_pct']}", PCT),
        ("Subsidy assumed (Rs)", f"={ref['subsidy']}", RS),
        ("Annual bill saving, low (Rs)", f"={ref['sav_lo']}", RS),
        ("Annual bill saving, high (Rs)", f"={ref['sav_hi']}", RS),
        ("Payback on first cost case (yrs)", f"={ref['pb_first']}", NUM1),
        ("Payback on first cost case, low saving (yrs)", f"={ref['pb_first_lo']}", NUM1),
        ("Inverter / peak demand (x)", f"={ref['inv_ratio']}", "0.00\"x\""),
        ("Backup runtime at high backup load (h)", f"={ref['rt_hi']}", NUM1),
        ("Backup runtime at low backup load (h)", f"={ref['rt_lo']}", NUM1),
    ]
    header(s, 7, ["Metric", "Value"])
    r = 8
    for lab, f, fmt in lines:
        put(s, f"A{r}", lab)
        is_input = not (isinstance(f, str) and f.startswith("="))
        put(s, f"B{r}", f, BLUE if is_input else GREEN, fmt)
        r += 1
    r += 1
    header(s, r, ["Integrity checks", "Status"])
    r += 1
    put(s, f"A{r}", "Payment % sums to 100%")
    put(s, f"B{r}", f"=IF(ABS({ref['pay_check']}-1)<0.0001,\"OK\",\"CHECK\")")
    r += 1
    put(s, f"A{r}", "Tariff reproduces every bill within Rs 1")
    put(s, f"B{r}", f"=IF({ref['tariff_check']}<=1,\"OK\",\"CHECK - rates not verified\")")
    r += 1
    put(s, f"A{r}", "Quote arithmetic: stated vs computed payment amounts")
    put(s, f"B{r}", f"=IF(ABS({ref['pay_diff']})<=1,\"OK\",\"CHECK\")")
    widths(s, [46, 60])

    for ws in wb.worksheets:
        ws.sheet_view.showGridLines = False
        ws.freeze_panes = "A4" if ws.title != "Summary" else None
    wb.save(out)
    print(f"saved {out}")


if __name__ == "__main__":
    with open(sys.argv[1]) as f:
        build(json.load(f), sys.argv[2])
