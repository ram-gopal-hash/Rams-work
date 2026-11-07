#!/usr/bin/env python3
"""
G2G Kaamyabi Solar Financial Model — Builder Template
======================================================
7-sheet structure: Assumptions / Debt / Depreciation / FinCal / Project Summary / BE_Solver / Scenarios
(the calling script adds a Verdict front sheet -- see SKILL.md)

v2.0 CHANGES -- all three mandatory patches from SKILL.md are APPLIED in this file:
  P1  Security deposit refund is a final-year OUTFLOW (was wrongly an inflow;
      latent while security_l = 0, which was true of both bundled examples).
  P2  deposit_in_equity toggle -- True = deposit is a zero-cost debt tranche that
      displaces promoter equity; False = deposit sits outside the equity base
      (single-sign-change comparator).
  P3  npv() / mirr() / sign_changes() helpers. Use mirr() whenever
      sign_changes(eq_cfs) > 1 -- plain IRR is invalid there.
  Scenarios now carries Tables 4-6: PPA tenure x tariff (Project IRR),
  tenure x tariff (Equity MIRR), tenure x capex (Project IRR).
All monetary values in Rs. Lakhs.

HOW TO USE THIS TEMPLATE
-------------------------
1. Replace the project parameter dict (p = { ... }) near line 17 with the new project's inputs.
2. Set output path at the bottom (build_workbook call).
3. Run: python3 <this_script>.py
4. The script computes everything in Python and writes all values — no Excel formulas needed.

STRUCTURE
---------
Line  17:  Project parameter dict (the only section you edit)
Line  79:  xirr()  — bisection IRR
Line  90:  compute() — full annual financial engine (DO NOT EDIT)
Line 245:  Style constants and helper functions
Line 294:  build_assumptions()
Line 400:  build_debt()
Line 440:  build_depreciation()
Line 507:  build_fincal()
Line 643:  build_summary()
Line 730:  build_be_solver()
Line 800:  build_scenarios()  — 3 heat map tables
Line 980:  build_workbook() — orchestrates all sheets
Line 1010: Entry point (edit project dict + output path here)
"""

import openpyxl
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils import get_column_letter

L = 100_000   # 1 Lakh

# ─── PROJECT PARAMETERS ───────────────────────────────────────────────────────
KB = {
    'name': 'Client A', 'structure': 'Rooftop RESCO',
    'client': 'Client A', 'location': 'Rajasthan',
    'bank': 'TBD', 'cod_fy': 'FY 2026-27',
    'dc_kw': 1000, 'ac_kwp': 750,
    'gen_per_kwp': 1306,          # kWh/kWp/yr (DC basis)
    'gen_y1': 1_306_000,          # kWh
    'deg_y2': 0.025, 'deg_y3': 0.007,
    'tariff': 4.40,               # Rs./kWh
    'ppa_yrs': 15,
    'epc_rate': 27_000,           # Rs./kW ex-GST
    'gst_rate': 0.089,
    'epc_ex_gst_l': 270.00,       # Rs. Lakhs
    'epc_incl_gst_l': 294.03,
    'equity_pct': 0.30, 'debt_pct': 0.70,
    'debt_yrs': 10, 'interest_rate': 0.10,
    'security_l': 0.0, 'return_deposit': 'No',
    'om_rate': 350, 'om_esc': 0.05,
    'insurance_pct': 0.007,
    'land_l': 0.0, 'land_esc': 0.05,
    'ad': 'Yes', 'it_dep': 0.40, 'book_dep': 0.20,
    'tax_rate': 0.2517, 'mat_rate': 0.156,
    'hurdle': 0.15, 'client_rating': 'BBB',
    'version': 'v1.0  |  Apr 2026', 'prep_by': 'G2G Finance Team',
    # Scenario ranges
    'scen_epc_min': 20_250, 'scen_epc_max': 33_750,   # 11 rows, step 1350
    'scen_units': [900,975,1050,1125,1200,1275,1306,1350,1425,1500,1575,1650],
    'scen_tariff': [3.20,3.50,3.80,4.10,4.40,4.70,5.00,5.30,5.60,5.90,6.20],
    'scen_rates': [0.08,0.085,0.09,0.095,0.10,0.105,0.11,0.115,0.12,0.125,0.13],
}
US = {
    'name': 'Client B', 'structure': 'Captive Ground Mounted',
    'client': 'Client B', 'location': 'Maharashtra',
    'bank': 'TBD', 'cod_fy': 'FY 2026-27',
    'dc_kw': 1000, 'ac_kwp': 700,
    'gen_per_kwp': 1450,
    'gen_y1': 1_450_000,
    'deg_y2': 0.025, 'deg_y3': 0.007,
    'tariff': 3.85,
    'ppa_yrs': 20,
    'epc_rate': 31_000,
    'gst_rate': 0.089,
    'epc_ex_gst_l': 310.00,
    'epc_incl_gst_l': 337.59,
    'equity_pct': 0.30, 'debt_pct': 0.70,
    'debt_yrs': 12, 'interest_rate': 0.10,
    'security_l': 0.0, 'return_deposit': 'No',
    'om_rate': 350, 'om_esc': 0.05,
    'insurance_pct': 0.007,
    'land_l': 1.25, 'land_esc': 0.05,  # Rs.50k/acre × 2.5 acres = Rs.1.25L
    'ad': 'Yes', 'it_dep': 0.40, 'book_dep': 0.20,
    'tax_rate': 0.2517, 'mat_rate': 0.156,
    'hurdle': 0.15, 'client_rating': 'BBB',
    'version': 'v1.0  |  Apr 2026', 'prep_by': 'G2G Finance Team',
    # Scenario ranges
    'scen_epc_min': 23_250, 'scen_epc_max': 38_750,   # 11 rows, step 1550
    'scen_units': [1050,1125,1200,1275,1350,1425,1450,1500,1575,1650,1725,1800],
    'scen_tariff': [2.85,3.10,3.35,3.60,3.85,4.10,4.35,4.60,4.85,5.10,5.35],
    'scen_rates': [0.08,0.085,0.09,0.095,0.10,0.105,0.11,0.115,0.12,0.125,0.13],
}

# ─── FINANCIAL ENGINE ─────────────────────────────────────────────────────────
def xirr(cfs):
    def npv(r): return sum(cf/(1+r)**t for t,cf in enumerate(cfs))
    lo, hi = -0.9999, 50.0
    if npv(lo)*npv(hi) > 0: return None
    for _ in range(4000):
        mid = (lo+hi)/2
        if abs(hi-lo) < 1e-10: break
        if npv(mid) > 0: lo = mid
        else: hi = mid
    return (lo+hi)/2

def npv(r, cfs):
    """Net present value of a cash-flow list (index 0 = year 0)."""
    return sum(x/(1+r)**t for t, x in enumerate(cfs))

def sign_changes(cfs):
    """Number of sign changes in a cash-flow stream. >1 means IRR is unreliable."""
    signs = [1 if x > 0 else (-1 if x < 0 else 0) for x in cfs if x != 0]
    return sum(1 for a, b in zip(signs, signs[1:]) if a != b)

def mirr(cfs, fin_rate=0.10, reinv_rate=0.08):
    """Modified IRR. USE THIS instead of xirr() whenever sign_changes(cfs) > 1
    -- e.g. when a client security deposit is refunded in the final year, which
    puts a second sign change in the equity stream and makes plain IRR
    multi-rooted (or unsolvable). Outflows discounted at fin_rate to t0,
    inflows compounded at reinv_rate to tn."""
    n = len(cfs) - 1
    pv_neg = sum(x/(1+fin_rate)**t   for t, x in enumerate(cfs) if x < 0)
    fv_pos = sum(x*(1+reinv_rate)**(n-t) for t, x in enumerate(cfs) if x > 0)
    if pv_neg == 0 or fv_pos <= 0:
        return None
    return (fv_pos / -pv_neg)**(1/n) - 1

def compute(p, tariff=None, gen_per_kwp=None, epc_rate=None, interest_rate=None):
    """Full model computation. Override params for scenario analysis."""
    tariff       = tariff       or p['tariff']
    gen_per_kwp  = gen_per_kwp  or p['gen_per_kwp']
    epc_rate_kw  = epc_rate     or p['epc_rate']
    rate         = interest_rate or p['interest_rate']

    epc_ex       = epc_rate_kw * p['dc_kw'] / L   # Rs. Lakhs
    loan         = epc_ex * p['debt_pct']
    equity       = epc_ex * p['equity_pct']
    dep_in_eq    = p.get('deposit_in_equity', True)
    net_equity   = equity - (p['security_l'] if dep_in_eq else 0.0)
    dt           = p['debt_yrs']
    n            = p['ppa_yrs']

    # Annual EMI (year-end)
    if dt > 0 and loan > 0:
        emi = loan * rate * (1+rate)**dt / ((1+rate)**dt - 1)
    else:
        emi = 0

    it_wdv = epc_ex
    bk_wdv = epc_ex
    debt   = loan
    loss_pool = 0.0   # accumulated unabsorbed dep (positive = pool available)
    mat_cr    = 0.0

    proj_cfs = [-epc_ex]
    eq_cfs   = [-net_equity]
    rows     = []
    gen_y1   = gen_per_kwp * p['dc_kw']   # kWh (may differ from base if scenario)

    for yr in range(1, n+1):
        # Generation
        if yr == 1:   gen_kwh = gen_y1
        elif yr == 2: gen_kwh = gen_y1 * (1 - p['deg_y2'])
        else:         gen_kwh = rows[-1]['gen_kwh'] * (1 - p['deg_y3'])

        # Revenue
        rev = gen_kwh * tariff / L

        # OpEx
        om  = p['ac_kwp'] * p['om_rate'] * (1+p['om_esc'])**(yr-1) / L
        ins = epc_ex * p['insurance_pct']
        lnd = p['land_l'] * (1+p['land_esc'])**(yr-1) if p['land_l'] > 0 else 0
        opex = om + ins + lnd
        ebitda = rev - opex

        # IT Depreciation (40% WDV)
        it_dep = it_wdv * p['it_dep']
        it_wdv2 = it_wdv - it_dep

        # Book Depreciation (20% WDV)
        bk_dep = bk_wdv * p['book_dep']
        bk_wdv2 = bk_wdv - bk_dep

        # Debt
        if yr <= dt and debt > 0.0001:
            interest  = debt * rate
            principal = emi - interest
            if principal > debt: principal = debt
            debt2 = debt - principal
            total_ds = interest + principal
        else:
            interest = principal = debt2 = total_ds = 0.0
        dscr = ebitda / total_ds if total_ds > 0 else None

        # IT PBT (before loss c/f)
        it_pbt_raw = rev - opex - interest - it_dep

        # Loss carry-forward
        if it_pbt_raw >= 0:
            loss_used = min(loss_pool, it_pbt_raw)
            it_taxable = it_pbt_raw - loss_used
            loss_pool2 = loss_pool - loss_used
        else:
            loss_used = 0.0
            it_taxable = 0.0
            loss_pool2 = loss_pool + (-it_pbt_raw)

        normal_tax = it_taxable * p['tax_rate']

        # Book PBT
        bk_pbt = rev - opex - interest - bk_dep
        mat_liab = max(0.0, bk_pbt * p['mat_rate'])

        # MAT vs Normal Tax
        if normal_tax >= mat_liab:
            excess = normal_tax - mat_liab
            mat_used = min(mat_cr, excess)
            actual_tax = normal_tax - mat_used
            mat_gen = 0.0
            mat_cr2 = mat_cr - mat_used
        else:
            actual_tax = mat_liab
            mat_gen = mat_liab - normal_tax
            mat_used = 0.0
            mat_cr2 = mat_cr + mat_gen

        pat = bk_pbt - actual_tax

        # Security deposit return
        # CORRECTED: refunding the client's deposit is a Year-n OUTFLOW.
        # Original template added it as an inflow (sign error; latent because
        # both reference projects had security_l = 0).
        extra = (-p['security_l'] if (yr == n and p['return_deposit'] == 'Yes' and dep_in_eq) else 0.0)

        fcf_proj = ebitda - actual_tax
        fcf_eq   = fcf_proj - total_ds + extra

        proj_cfs.append(fcf_proj)
        eq_cfs.append(fcf_eq)

        rows.append({
            'year': yr, 'gen_kwh': gen_kwh, 'rev': rev,
            'om': om, 'ins': ins, 'lnd': lnd, 'opex': opex,
            'ebitda': ebitda, 'ebitda_pct': ebitda/rev if rev else 0,
            'interest': interest, 'it_dep': it_dep,
            'it_pbt_raw': it_pbt_raw,
            'loss_bf': loss_pool, 'loss_used': loss_used, 'loss_cf': loss_pool2,
            'normal_tax': normal_tax,
            'bk_dep': bk_dep, 'bk_pbt': bk_pbt, 'mat_liab': mat_liab,
            'mat_cr_bf': mat_cr, 'mat_gen': mat_gen,
            'mat_used': mat_used, 'mat_cr_cf': mat_cr2,
            'actual_tax': actual_tax, 'pat': pat,
            'principal': principal, 'total_ds': total_ds,
            'fcf_proj': fcf_proj, 'fcf_eq': fcf_eq,
            'debt_open': debt, 'debt_close': debt2,
            'it_wdv_open': it_wdv, 'it_wdv_close': it_wdv2,
            'it_tax_shield': it_dep * p['tax_rate'],
            'bk_wdv_open': bk_wdv, 'bk_wdv_close': bk_wdv2,
            'bk_tax_shield': bk_dep * p['tax_rate'],
            'dscr': dscr,
            'cum_ecf': sum(r['fcf_eq'] for r in rows) + fcf_eq - net_equity,
        })

        it_wdv = it_wdv2; bk_wdv = bk_wdv2
        debt = debt2; loss_pool = loss_pool2; mat_cr = mat_cr2

    pirr = xirr(proj_cfs)
    eirr = xirr(eq_cfs)
    dscr_vals = [r['dscr'] for r in rows if r['dscr']]
    payback = None
    cum = 0
    for r in rows:
        cum += r['fcf_eq']
        if cum >= net_equity and payback is None:
            payback = r['year']

    return {
        'rows': rows, 'loan': loan, 'equity': equity,
        'net_equity': net_equity, 'emi': emi,
        'proj_irr': pirr, 'eq_irr': eirr,
        'min_dscr': min(dscr_vals) if dscr_vals else 0,
        'avg_dscr': sum(dscr_vals)/len(dscr_vals) if dscr_vals else 0,
        'payback': payback, 'proj_cfs': proj_cfs, 'eq_cfs': eq_cfs,
        'epc_ex': epc_rate_kw * p['dc_kw'] / L,
    }

# ─── STYLE HELPERS ────────────────────────────────────────────────────────────
DK   = "1F497D"   # dark blue header
MB   = "4472C4"   # medium blue section
LB   = "DCE6F1"   # light blue highlight
LG   = "F2F2F2"   # light grey
WH   = "FFFFFF"
BLK  = "000000"
BINP = "0000FF"   # blue input
GFOR = "00703C"   # green formula
GREY = "808080"

INR  = '#,##0.00;(#,##0.00);"-"'
INR0 = '#,##0;(#,##0);"-"'
PCT  = '0.00%;(0.00%);"-"'
PCT1 = '0.0%;(0.0%);"-"'
NUM  = '#,##0;(#,##0);"-"'
DSCR_F = '0.00"x";(0.00"x");"-"'

def sc(ws, r, c, val, fc=BLK, bold=False, bg=None, nf=None,
       ha='left', sz=10, italic=False, indent=0):
    cell = ws.cell(row=r, column=c)
    cell.value = val
    cell.font  = Font(name='Arial', size=sz, color=fc, bold=bold, italic=italic)
    cell.alignment = Alignment(horizontal=ha, vertical='center',
                                wrap_text=False, indent=indent)
    if bg: cell.fill = PatternFill('solid', start_color=bg)
    if nf: cell.number_format = nf
    return cell

def hdr(ws, r, c1, c2, title, bg=DK, sz=10):
    ws.row_dimensions[r].height = 18
    cell = sc(ws, r, c1, f'  {title}', fc=WH, bold=True, bg=bg, sz=sz)
    if c2 > c1:
        ws.merge_cells(start_row=r, start_column=c1, end_row=r, end_column=c2)
    return cell

def gap(ws, r, h=5):
    ws.row_dimensions[r].height = h

def title_row(ws, r, text, c1=1, c2=10, bg=DK, sz=13):
    ws.row_dimensions[r].height = 28
    cell = ws.cell(row=r, column=c1)
    cell.value = text
    cell.font  = Font(name='Arial', size=sz, bold=True, color=WH)
    cell.fill  = PatternFill('solid', start_color=bg)
    cell.alignment = Alignment(horizontal='left', vertical='center', indent=1)
    if c2 > c1:
        ws.merge_cells(start_row=r, start_column=c1, end_row=r, end_column=c2)

# ─── SHEET 1: ASSUMPTIONS ────────────────────────────────────────────────────
def build_assumptions(wb, p, comp):
    ws = wb.create_sheet('Assumptions')
    ws.column_dimensions['A'].width = 32
    ws.column_dimensions['B'].width = 24
    ws.column_dimensions['C'].width = 14
    ws.column_dimensions['D'].width = 18
    ws.column_dimensions['E'].width = 32

    n = p['ppa_yrs']
    title_row(ws, 1, f'{p["name"]}  —  ASSUMPTIONS  (Blue cells = input → all sheets update)', 1, 5)
    sc(ws, 2, 1, '  🔵 Blue = INPUT   |   🟢 Green = auto-calculated   |   Rs. Lakhs unless stated',
       fc='595959', italic=True, sz=9)
    ws.merge_cells('A2:E2')
    ws.row_dimensions[2].height = 14

    r = 3
    def inp(row, label, val, unit='', note=''):
        ws.row_dimensions[row].height = 16
        sc(ws, row, 1, f'  {label}', indent=1)
        sc(ws, row, 3, unit, fc='595959', italic=True, sz=9)
        sc(ws, row, 4, val, fc=BINP, bold=True, nf=None, ha='right')
        if note: sc(ws, row, 5, note, fc='595959', italic=True, sz=9)

    def calc(row, label, val, unit='', note='', nf=INR):
        ws.row_dimensions[row].height = 16
        sc(ws, row, 1, f'  {label}', indent=1)
        sc(ws, row, 3, unit, fc='595959', italic=True, sz=9)
        sc(ws, row, 4, val, fc=GFOR, nf=nf, ha='right')
        if note: sc(ws, row, 5, note, fc='595959', italic=True, sz=9)

    hdr(ws, r, 1, 5, 'A.  TECHNICAL PARAMETERS'); r+=1
    inp(r,'DC Capacity', p['dc_kw'], 'kW', 'Name-plate installed'); r+=1
    inp(r,'AC Capacity', p['ac_kwp'], 'kWp', 'Inverter AC output capacity'); r+=1
    inp(r,'Generation / kWp / yr (DC basis)', p['gen_per_kwp'], 'kWh/kWp',
        f'DC basis → {p["gen_y1"]:,} kWh total'); r+=1
    calc(r,'Year 1 Generation', p['gen_y1'], 'kWh', 'Auto: DC kW × gen/kWp', nf=NUM); r+=1
    inp(r,'Year 2 Degradation', p['deg_y2'], '% pa', '2.5% step-change'); r+=1
    inp(r,'Year 3+ Annual Degradation', p['deg_y3'], '% pa', '0.7% from Year 3 onwards'); r+=1
    gap(ws, r); r+=1

    hdr(ws, r, 1, 5, 'B.  REVENUE ASSUMPTIONS'); r+=1
    inp(r,'Electricity Tariff (PPA)', p['tariff'], 'Rs./kWh', 'Fixed for PPA term'); r+=1
    inp(r,'Tariff Escalation', 'Nil', '', 'Flat tariff — no escalation'); r+=1
    gap(ws, r); r+=1

    hdr(ws, r, 1, 5, 'C.  PROJECT TENURE  &  CAPITAL COST'); r+=1
    inp(r,'Project & PPA Tenure', p['ppa_yrs'], 'years', 'PPA term'); r+=1
    inp(r,'EPC Rate (ex-GST)', p['epc_rate'], 'Rs./kW', ''); r+=1
    inp(r,'GST Rate on EPC', p['gst_rate'], '%', f'Rs.{p["epc_incl_gst_l"]-p["epc_ex_gst_l"]:.2f}L GST'); r+=1
    calc(r,'EPC Total (incl. GST)', p['epc_incl_gst_l'], 'Rs. Lakhs',
         f'Rs.{p["epc_incl_gst_l"]:.2f}L total'); r+=1
    calc(r,'EPC ex-GST (dep & financing base)', p['epc_ex_gst_l'], 'Rs. Lakhs',
         'Base for debt, equity, depreciation'); r+=1
    gap(ws, r); r+=1

    hdr(ws, r, 1, 5, 'D.  FINANCING STRUCTURE'); r+=1
    inp(r,'Equity Share', p['equity_pct'], '%', 'Promoter contribution'); r+=1
    inp(r,'Loan Tenure', p['debt_yrs'], 'years', ''); r+=1
    inp(r,'Interest Rate', p['interest_rate'], '% pa', 'Fixed rate'); r+=1
    calc(r,'Equity Amount', comp['equity'], 'Rs. Lakhs', 'Auto: EPC ex-GST × equity%'); r+=1
    calc(r,'Debt Amount', comp['loan'], 'Rs. Lakhs', 'Auto: EPC ex-GST × debt%'); r+=1
    calc(r,'Annual Debt Service (EMI)', comp['emi'], 'Rs. Lakhs pa', 'Auto'); r+=1
    if p['security_l'] > 0:
        inp(r,'Security Deposit Recd.', p['security_l'], 'Rs. Lakhs', f'From {p["client"]} at COD'); r+=1
        inp(r,'Return Security at End', p['return_deposit'], '', ''); r+=1
    gap(ws, r); r+=1

    hdr(ws, r, 1, 5, 'E.  OPERATING COSTS  (Annual)'); r+=1
    inp(r,'O&M Rate (on AC capacity)', p['om_rate'], 'Rs/kWp/yr',
        f'Rs.{p["om_rate"]*p["ac_kwp"]/L:.2f}L base → +5% pa'); r+=1
    inp(r,'O&M Annual Escalation', p['om_esc'], '% pa', '5% default'); r+=1
    inp(r,'Insurance Rate', p['insurance_pct'], '% of EPC',
        f'Rs.{p["epc_ex_gst_l"]*p["insurance_pct"]:.2f}L pa'); r+=1
    if p['land_l'] > 0:
        inp(r,'Land Rental (base)', p['land_l'], 'Rs. Lakhs/yr',
            f'Rs.50k/acre × 2.5 acres → +5% pa'); r+=1
        inp(r,'Land Escalation', p['land_esc'], '% pa', ''); r+=1
    else:
        inp(r,'Land Rent', 0, 'Rs/ac/yr', 'Rooftop — nil'); r+=1
    gap(ws, r); r+=1

    hdr(ws, r, 1, 5, 'F.  DEPRECIATION,  TAX  &  RETURNS'); r+=1
    inp(r,'Accelerated Dep Claimed', p['ad'], 'Yes/No', 'IT Act Sec 32 — 40% WDV'); r+=1
    inp(r,'IT Depreciation Rate', p['it_dep'], '%', 'Auto from AD setting'); r+=1
    inp(r,'Book Depreciation Rate', p['book_dep'], '%', '20% WDV — for MAT'); r+=1
    inp(r,'Income Tax Rate', p['tax_rate'], '%', '25% + 4% cess'); r+=1
    inp(r,'MAT Rate', p['mat_rate'], '%', '15% + 4% cess'); r+=1
    inp(r,'Hurdle Rate (target)', p['hurdle'], '% pa', 'Target Equity IRR'); r+=1
    gap(ws, r); r+=1

    hdr(ws, r, 1, 5, 'G.  PROJECT IDENTITY'); r+=1
    for label, val in [
        ('SPV / Client', p['client']), ('Developer', 'G2G Solar / Kaamyabi'),
        ('Location', p['location']), ('Off-taker', f'{p["client"]}  |  {p["structure"]}'),
        ('Client Credit Rating', p['client_rating']),
        ('COD FY', p['cod_fy']), ('Install Type', p['structure']),
        ('Prep By', p['prep_by']), ('Version', p['version']),
    ]:
        ws.row_dimensions[r].height = 15
        sc(ws, r, 1, f'  {label}', indent=1)
        sc(ws, r, 4, val, ha='left')
        r += 1

    sc(ws, r+1, 1, '  🔵 Blue = INPUT  |  🟢 Green = auto-formula  |  Grey = info only',
       fc='595959', italic=True, sz=8)
    ws.merge_cells(f'A{r+1}:E{r+1}')

# ─── SHEET 2: DEBT ────────────────────────────────────────────────────────────
def build_debt(wb, p, comp):
    ws = wb.create_sheet('Debt')
    ws.column_dimensions['A'].width = 4
    for col, w in [('B',30),('C',16),('D',16),('E',16),('F',16),('G',16)]:
        ws.column_dimensions[col].width = w

    title_row(ws, 1, f'{p["name"]}  —  DEBT REPAYMENT SCHEDULE  (Rs. Lakhs)', 1, 7)
    sc(ws, 2, 2, f'Annual EMI  |  {p["debt_yrs"]}-year tenor  |  {p["interest_rate"]*100:.1f}% pa fixed',
       fc='595959', italic=True, sz=9)
    ws.merge_cells('B2:G2')
    ws.row_dimensions[2].height = 13

    # Summary
    for label, val, nf in [
        ('Loan Amount (Rs. Lakhs)', comp['loan'], INR),
        ('Loan Tenure (years)', p['debt_yrs'], '0'),
        ('Interest Rate (% pa)', p['interest_rate'], PCT),
        ('Annual Debt Service (EMI)', comp['emi'], INR),
    ]:
        sc(ws, ws.max_row+1, 2, label, fc='595959')
        c = ws.cell(row=ws.max_row, column=3)
        c.value = val; c.number_format = nf
        c.font = Font(name='Arial', size=10, bold=True, color=BINP)

    r = ws.max_row + 2
    for col, lbl in [(2,'Year'),(3,'Opening Bal.\n(Rs.L)'),(4,'Interest\n(Rs.L)'),
                     (5,'Principal\n(Rs.L)'),(6,'Int+Prin\n(Rs.L)'),(7,'Closing Bal.\n(Rs.L)')]:
        cell = sc(ws, r, col, lbl, fc=WH, bold=True, bg=DK, ha='center', sz=9)
        cell.alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)
    ws.row_dimensions[r].height = 28

    tot_i = tot_p = 0
    for row in comp['rows']:
        yr = row['year']
        if yr > p['debt_yrs']: break
        r += 1
        ws.row_dimensions[r].height = 16
        bg = LG if yr % 2 == 0 else None
        sc(ws, r, 2, yr, ha='center', bg=bg)
        sc(ws, r, 3, row['debt_open'], nf=INR, ha='right', bg=bg)
        sc(ws, r, 4, row['interest'],  nf=INR, ha='right', bg=bg)
        sc(ws, r, 5, row['principal'], nf=INR, ha='right', bg=bg)
        sc(ws, r, 6, row['total_ds'],  nf=INR, ha='right', bg=bg)
        sc(ws, r, 7, row['debt_close'],nf=INR, ha='right', bg=bg)
        tot_i += row['interest']; tot_p += row['principal']

    r += 1; ws.row_dimensions[r].height = 17
    for col, val in [(2,'TOTALS'),(3,comp['loan']),(4,tot_i),
                     (5,tot_p),(6,tot_i+tot_p),(7,0)]:
        sc(ws, r, col, val if isinstance(val,str) else val,
           fc=WH, bold=True, bg=DK,
           nf=INR if isinstance(val,float) else None, ha='center' if col==2 else 'right')

# ─── SHEET 3: DEPRECIATION ───────────────────────────────────────────────────
def build_depreciation(wb, p, comp):
    ws = wb.create_sheet('Depreciation')
    ws.column_dimensions['A'].width = 4
    for col, w in [('B',30),('C',16),('D',16),('E',16),('F',16),('G',16),('H',18)]:
        ws.column_dimensions[col].width = w

    title_row(ws, 1, f'{p["name"]}  —  DEPRECIATION SCHEDULE  (Rs. Lakhs)', 1, 8)
    sc(ws, 2, 2, f'Base = EPC ex-GST  |  IT dep {p["it_dep"]*100:.0f}% WDV (AD)  |  Book dep {p["book_dep"]*100:.0f}% WDV',
       fc='595959', italic=True, sz=9)
    ws.merge_cells('B2:H2'); ws.row_dimensions[2].height = 13

    for label, val, nf in [
        ('Dep Base (EPC ex-GST, Rs.L)', comp['epc_ex'], INR),
        ('IT Dep Rate (AD)',            p['it_dep'],    PCT),
        ('Book Dep Rate',               p['book_dep'],  PCT),
        ('Income Tax Rate',             p['tax_rate'],  PCT),
    ]:
        r2 = ws.max_row+1
        sc(ws, r2, 2, label, fc='595959')
        c = ws.cell(row=r2, column=3); c.value = val; c.number_format = nf
        c.font = Font(name='Arial', size=10, bold=True, color=BINP)

    r = ws.max_row + 2
    hdrs = ['Year','Opening WDV\n(Rs.L)','IT Dep\n(Rs.L)','Closing WDV\n(Rs.L)',
            'IT Tax Shield\n(Rs.L)','Book Dep\n(Rs.L)','Book Tax Shield\n(Rs.L)']
    for i, lbl in enumerate(hdrs):
        cell = sc(ws, r, i+2, lbl, fc=WH, bold=True, bg=DK, ha='center', sz=9)
        cell.alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)
    ws.row_dimensions[r].height = 28

    tot_itd = tot_btd = 0
    for row in comp['rows']:
        yr = row['year']
        r += 1; ws.row_dimensions[r].height = 16
        bg = LG if yr % 2 == 0 else None
        sc(ws, r, 2, yr,               ha='center', bg=bg)
        sc(ws, r, 3, row['it_wdv_open'],nf=INR, ha='right', bg=bg)
        sc(ws, r, 4, row['it_dep'],     nf=INR, ha='right', bg=bg)
        sc(ws, r, 5, row['it_wdv_close'],nf=INR,ha='right', bg=bg)
        sc(ws, r, 6, row['it_tax_shield'],nf=INR,ha='right',bg=bg)
        sc(ws, r, 7, row['bk_dep'],     nf=INR, ha='right', bg=bg)
        sc(ws, r, 8, row['bk_tax_shield'],nf=INR,ha='right',bg=bg)
        tot_itd += row['it_dep']; tot_btd += row['bk_dep']

    r += 1; ws.row_dimensions[r].height = 17
    for col, val in [(2,'TOTALS'),(4,tot_itd),(7,tot_btd)]:
        sc(ws, r, col, val if isinstance(val,str) else val,
           fc=WH, bold=True, bg=DK,
           nf=INR if isinstance(val,float) else None, ha='center' if col==2 else 'right')

# ─── SHEET 4: FINCAL ─────────────────────────────────────────────────────────
def build_fincal(wb, p, comp):
    ws = wb.create_sheet('FinCal')
    NCOLS = 30  # 30 metric columns (year as rows, metrics as columns)
    ws.column_dimensions['A'].width = 7   # Year label
    for i in range(2, NCOLS+1):
        ws.column_dimensions[get_column_letter(i)].width = 11

    n = p['ppa_yrs']

    title_row(ws, 1, f'{p["name"]}  —  FINANCIAL CALCULATIONS  ({n}-Year)  |  Rs. Lakhs', 1, NCOLS)
    sc(ws, 2, 1, 'AD depreciation  |  Tax loss carry-forward  |  MAT workings  |  Equity & Project IRR  |  DSCR',
       fc='595959', italic=True, sz=9)
    ws.merge_cells(f'A2:{get_column_letter(NCOLS)}2'); ws.row_dimensions[2].height = 13

    # ── column group headers ──
    # Col 1: Year | Cols 2-9: Income Statement | Cols 10-16: Tax Loss C/F
    # Cols 17-24: MAT Workings | Cols 25-30: Cash Flows & Returns
    r = 3; ws.row_dimensions[r].height = 17
    groups = [
        (0, 0, None, None),
        (1, 8, 'INCOME STATEMENT', MB),
        (9, 15, 'TAX LOSS  C/F', MB),
        (16, 23, 'MAT WORKINGS', MB),
        (24, 29, 'CASH FLOWS  &  RETURNS', MB),
    ]
    for c1_off, c2_off, title, bg in groups:
        if title:
            for col in range(c1_off+1, c2_off+2):
                ws.cell(row=r, column=col).fill = PatternFill('solid', start_color=bg)
            ws.merge_cells(start_row=r, start_column=c1_off+1,
                           end_row=r, end_column=c2_off+1)
            cell = ws.cell(row=r, column=c1_off+1)
            cell.value = title
            cell.font = Font(name='Arial', size=9, bold=True, color=WH)
            cell.alignment = Alignment(horizontal='center', vertical='center')

    # ── column labels ──
    r = 4; ws.row_dimensions[r].height = 40
    col_labels = [
        'Year', 'Generation\n(kWh)', 'Tariff\n(Rs/kWh)', 'Revenue\n(Rs.L)',
        'O&M\n(Rs.L)', 'Insurance\n(Rs.L)', 'Land\n(Rs.L)', 'Total OpEx\n(Rs.L)',
        'EBITDA\n(Rs.L)', 'Interest\n(Rs.L)', 'IT Dep\n(Rs.L)', 'IT PBT\n(Rs.L)',
        'Loss B/F\n(Rs.L)', 'Loss Used\n(Rs.L)', 'Loss C/F\n(Rs.L)', 'Normal Tax\n(Rs.L)',
        'Book Dep\n(Rs.L)', 'Book PBT\n(Rs.L)', 'MAT Liab\n(Rs.L)',
        'MAT Cr B/F', 'MAT Gen', 'MAT Used', 'MAT Cr C/F',
        'Actual Tax\n(Rs.L)', 'PAT\n(Rs.L)', 'Principal\n(Rs.L)',
        'Project CF\n(Rs.L)', 'Equity CF\n(Rs.L)', 'DSCR', 'Cum. ECF\n(Rs.L)',
    ]
    for i, lbl in enumerate(col_labels):
        cell = ws.cell(row=r, column=i+1)
        cell.value = lbl
        cell.font = Font(name='Arial', size=8, bold=True, color=WH)
        cell.fill = PatternFill('solid', start_color=DK)
        cell.alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)

    def data_row(ws_r, yr_label, vals, bg=None):
        ws.row_dimensions[ws_r].height = 16
        nfs = [None, NUM, INR, INR, INR, INR, INR, INR, INR, INR, INR, INR,
               INR, INR, INR, INR, INR, INR, INR, INR, INR, INR, INR, INR, INR,
               INR, INR, INR, DSCR_F, INR]
        for i, (v, nf) in enumerate(zip(vals, nfs)):
            cell = ws.cell(row=ws_r, column=i+1)
            cell.value = v
            cell.number_format = nf or 'General'
            cell.font = Font(name='Arial', size=9, color=BLK)
            cell.alignment = Alignment(horizontal='right' if i>0 else 'center', vertical='center')
            if bg: cell.fill = PatternFill('solid', start_color=bg)

    # Yr 0
    r = 5
    yr0 = ['Yr 0',0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
            -comp['epc_ex'],-comp['net_equity'],0,-comp['net_equity']]
    data_row(r, 'Yr 0', yr0, bg=LG)

    cum_ecf = -comp['net_equity']
    for row in comp['rows']:
        r += 1
        cum_ecf += row['fcf_eq']
        vals = [
            f'Yr {row["year"]}',
            row['gen_kwh'], p['tariff'], row['rev'],
            row['om'], row['ins'], row['lnd'], row['opex'],
            row['ebitda'], row['interest'], row['it_dep'], row['it_pbt_raw'],
            row['loss_bf'], row['loss_used'], row['loss_cf'], row['normal_tax'],
            row['bk_dep'], row['bk_pbt'], row['mat_liab'],
            row['mat_cr_bf'], row['mat_gen'], row['mat_used'], row['mat_cr_cf'],
            row['actual_tax'], row['pat'], row['principal'],
            row['fcf_proj'], row['fcf_eq'],
            row['dscr'], cum_ecf,
        ]
        bg = LG if row['year'] % 2 == 0 else None
        data_row(r, f'Yr {row["year"]}', vals, bg=bg)

    # Totals
    r += 1; ws.row_dimensions[r].height = 17
    rows = comp['rows']
    tot = ['TOTALS',
           None, None, sum(x['rev'] for x in rows),
           sum(x['om'] for x in rows), sum(x['ins'] for x in rows),
           sum(x['lnd'] for x in rows), sum(x['opex'] for x in rows),
           sum(x['ebitda'] for x in rows), sum(x['interest'] for x in rows),
           sum(x['it_dep'] for x in rows), None, None, None, None, None, None, None,
           None, None, None, None, None,
           sum(x['actual_tax'] for x in rows), None,
           sum(x['principal'] for x in rows),
           sum(x['fcf_proj'] for x in rows), sum(x['fcf_eq'] for x in rows),
           None, None]
    for i, v in enumerate(tot):
        cell = ws.cell(row=r, column=i+1)
        cell.value = v
        cell.font = Font(name='Arial', size=9, bold=True, color=WH)
        cell.fill = PatternFill('solid', start_color=DK)
        if isinstance(v, float):
            cell.number_format = INR
        cell.alignment = Alignment(horizontal='center' if i==0 else 'right', vertical='center')

    # IRR summary rows
    for lbl, val in [
        (f'PROJECT IRR  (EBITDA − Tax  |  {n}-year)', comp['proj_irr']),
        (f'EQUITY IRR  (After-tax, post-debt-service  |  {n}-year)', comp['eq_irr']),
    ]:
        r += 1; ws.row_dimensions[r].height = 18
        cell = ws.cell(row=r, column=1)
        cell.value = lbl
        cell.font = Font(name='Arial', size=10, bold=True, color=BLK)
        ws.merge_cells(start_row=r, start_column=1, end_row=r, end_column=27)
        vc = ws.cell(row=r, column=28)
        vc.value = val
        vc.number_format = PCT
        vc.font = Font(name='Arial', size=11, bold=True,
                       color='00703C' if (val or 0) >= p['hurdle'] else 'C00000')
        sc(ws, r, 29, '← live', fc='595959', italic=True, sz=8)

    ws.freeze_panes = ws.cell(row=5, column=3)

# ─── SHEET 5: PROJECT SUMMARY ─────────────────────────────────────────────────
def build_summary(wb, p, comp):
    ws = wb.create_sheet('Project Summary')
    ws.column_dimensions['A'].width = 30
    ws.column_dimensions['B'].width = 4
    ws.column_dimensions['C'].width = 4
    ws.column_dimensions['D'].width = 22
    ws.column_dimensions['E'].width = 28

    rows = comp['rows']
    n = p['ppa_yrs']

    title_row(ws, 1, f'{p["name"]}  —  {p["dc_kw"]} kW ROOFTOP SOLAR  |  PROJECT SUMMARY  |  LIVE', 1, 5)
    sub = (f'  EPC Rs.{p["epc_incl_gst_l"]:.2f}L incl.GST  |  Tariff Rs.{p["tariff"]}/kWh  |  '
           f'Debt 70% @ {p["interest_rate"]*100:.0f}% pa / {p["debt_yrs"]}yr  |  COD {p["cod_fy"]}')
    sc(ws, 2, 1, sub, fc='595959', italic=True, sz=9)
    ws.merge_cells('A2:E2'); ws.row_dimensions[2].height = 14

    r = 3
    def kv(row, label, val, nf=None, fc=BLK, bold=False, note=''):
        ws.row_dimensions[row].height = 16
        sc(ws, row, 1, f'  {label}', indent=1, bold=bold)
        cell = ws.cell(row=row, column=4)
        cell.value = val
        cell.font = Font(name='Arial', size=10, bold=bold, color=fc)
        cell.alignment = Alignment(horizontal='left', vertical='center')
        if nf: cell.number_format = nf
        if note: sc(ws, row, 5, note, fc='595959', italic=True, sz=9)

    hdr(ws, r, 1, 5, 'A.  PROJECT DETAILS'); r+=1
    for lbl, val in [
        ('Client / SPV', p['client']), ('Off-taker', f'{p["client"]}  ({p["structure"]})'),
        ('Location', p['location']), ('Type', p['structure']),
        ('COD', p['cod_fy']), ('PPA Tenure', f'{n} years'),
        ('Promoter', 'G2G Solar / Kaamyabi'), ('Lender', p['bank']),
        ('Client Credit Rating', p['client_rating']), ('Version', p['version']),
    ]:
        kv(r, lbl, val); r+=1

    hdr(ws, r, 1, 5, 'B.  TECHNICAL  &  GENERATION'); r+=1
    kv(r, 'DC Capacity', f'{p["dc_kw"]:,} kW'); r+=1
    kv(r, 'AC Capacity', f'{p["ac_kwp"]:,} kWp'); r+=1
    kv(r, 'Generation / kWp / yr', f'{p["gen_per_kwp"]:,} kWh'); r+=1
    kv(r, 'Year 1 Generation', rows[0]['gen_kwh'], nf='#,##0', note=f'{rows[0]["gen_kwh"]:,.0f} kWh'); r+=1
    kv(r, 'Year 1 Revenue', rows[0]['rev'], nf=INR, note='Rs. Lakhs'); r+=1
    kv(r, 'Year 1 EBITDA', rows[0]['ebitda'], nf=INR); r+=1
    kv(r, 'Year 1 EBITDA Margin', rows[0]['ebitda_pct'], nf=PCT1); r+=1

    hdr(ws, r, 1, 5, 'C.  CAPITAL COST  &  FINANCING'); r+=1
    kv(r, 'EPC ex-GST', p['epc_ex_gst_l'], nf=INR); r+=1
    kv(r, 'GST on EPC', p['epc_incl_gst_l']-p['epc_ex_gst_l'], nf=INR); r+=1
    kv(r, 'Total EPC (incl. GST)', p['epc_incl_gst_l'], nf=INR); r+=1
    kv(r, 'Equity (30%)', comp['equity'], nf=INR); r+=1
    if p['security_l']>0:
        kv(r, 'Security Deposit', p['security_l'], nf=INR, note=f'From {p["client"]}'); r+=1
        kv(r, 'Net Equity Outflow', comp['net_equity'], nf=INR, note='Equity − security'); r+=1
    kv(r, 'Debt (70%)', comp['loan'], nf=INR); r+=1
    kv(r, 'Interest Rate', p['interest_rate'], nf=PCT); r+=1
    kv(r, 'Loan Tenure', f'{p["debt_yrs"]} years'); r+=1
    kv(r, 'Annual Debt Service (EMI)', comp['emi'], nf=INR); r+=1
    kv(r, 'AD Dep Claimed', p['ad']); r+=1
    kv(r, 'IT Dep Rate', p['it_dep'], nf=PCT); r+=1

    hdr(ws, r, 1, 5, 'D.  FINANCIAL METRICS  ★  (live — update with assumptions)'); r+=1
    irr_color = '00703C' if (comp['eq_irr'] or 0) >= p['hurdle'] else 'C00000'
    kv(r, 'Project IRR', comp['proj_irr'], nf=PCT, fc='00703C', bold=True); r+=1
    kv(r, 'Equity IRR', comp['eq_irr'], nf=PCT, fc=irr_color, bold=True); r+=1
    kv(r, 'Hurdle Rate', p['hurdle'], nf=PCT); r+=1
    gap_val = (comp['eq_irr'] or 0) - p['hurdle']
    kv(r, 'IRR vs Hurdle  (+ = pass)', gap_val, nf=PCT,
       fc='00703C' if gap_val>=0 else 'C00000', bold=True); r+=1
    kv(r, 'Min DSCR (debt period)', comp['min_dscr'], nf=DSCR_F); r+=1
    kv(r, 'Avg DSCR (debt period)', comp['avg_dscr'], nf=DSCR_F); r+=1
    for yr_n, row in enumerate(rows, 1):
        if row['dscr']:
            kv(r, f'DSCR Year {yr_n}', row['dscr'], nf=DSCR_F); r+=1
        if yr_n >= p['debt_yrs']: break
    pb = comp['payback']
    kv(r, 'Equity Payback Period', f'{pb} years' if pb else 'Beyond horizon'); r+=1
    kv(r, 'Total Revenue (full term)', sum(x['rev'] for x in rows), nf=INR); r+=1
    kv(r, 'Total Tax Paid', sum(x['actual_tax'] for x in rows), nf=INR); r+=1
    kv(r, 'Total Interest Paid', sum(x['interest'] for x in rows), nf=INR); r+=1

    hdr(ws, r, 1, 5, 'E.  FLAGS  &  ECONOMICS NOTE'); r+=1
    eirr = comp['eq_irr'] or 0
    flags = []
    if eirr >= p['hurdle']:
        flags.append(f'  ✓  Equity IRR {eirr*100:.2f}%  vs Hurdle {p["hurdle"]*100:.0f}%  — ABOVE HURDLE')
    else:
        flags.append(f'  ⚠  Equity IRR {eirr*100:.2f}%  vs Hurdle {p["hurdle"]*100:.0f}%  — BELOW HURDLE')
    if comp['min_dscr'] < 1.25:
        flags.append(f'  ⚠  Min DSCR {comp["min_dscr"]:.2f}x  — BELOW 1.25x BANKABILITY THRESHOLD')
    else:
        flags.append(f'  ✓  Min DSCR {comp["min_dscr"]:.2f}x  — Above 1.25x threshold')
    if p['land_l'] > 0:
        flags.append(f'  ℹ  Land cost: Rs.{p["land_l"]:.2f}L pa  (Solapur Park — ground mount)')
    flags.append(f'  ℹ  AD dep (40% WDV) — tax loss c/f shelters early years from income tax')
    flags.append(f'  ℹ  MAT @ {p["mat_rate"]*100:.1f}% on book PBT applies during loss-c/f period')

    for flag in flags:
        ws.row_dimensions[r].height = 15
        fc = '00703C' if '✓' in flag else ('C00000' if '⚠' in flag else '595959')
        cell = ws.cell(row=r, column=1)
        cell.value = flag
        cell.font = Font(name='Arial', size=9, color=fc, italic=True)
        ws.merge_cells(f'A{r}:E{r}')
        r += 1

# ─── SHEET 6: BE_SOLVER ───────────────────────────────────────────────────────
def build_besolver(wb, p, comp):
    ws = wb.create_sheet('BE_Solver')
    ws.column_dimensions['A'].width = 4
    ws.column_dimensions['B'].width = 40
    ws.column_dimensions['C'].width = 20
    ws.column_dimensions['D'].width = 14

    title_row(ws, 1, f'{p["name"]}  —  BREAKEVEN TARIFF  |  Goal Seek: Set E7=0 by changing E4', 1, 5)
    sc(ws, 2, 2, 'All CF rows use live links. Only E4 (test tariff) is the variable.',
       fc='595959', italic=True, sz=9)
    ws.merge_cells('B2:E2'); ws.row_dimensions[2].height=13

    # Try to compute breakeven tariff via bisection
    def eq_irr_at_tariff(t):
        c = compute(p, tariff=t)
        return c['eq_irr'] or -99

    lo_t, hi_t = 0.5, 20.0
    # Find tariff where eq_irr = hurdle
    try:
        for _ in range(100):
            mid_t = (lo_t + hi_t) / 2
            if abs(hi_t - lo_t) < 0.0001: break
            if eq_irr_at_tariff(mid_t) < p['hurdle']: lo_t = mid_t
            else: hi_t = mid_t
        be_tariff = (lo_t + hi_t) / 2
        be_irr = eq_irr_at_tariff(be_tariff)
    except:
        be_tariff = p['tariff']
        be_irr = comp['eq_irr'] or 0

    r = 3
    for label, val, nf, note in [
        ('Test Tariff  (Rs./kWh)  ← Goal Seek target', be_tariff, INR, ''),
        ('Equity IRR at Test Tariff', be_irr, PCT, ''),
        ('Hurdle Rate', p['hurdle'], PCT, ''),
        ('Gap  (IRR − Hurdle)  ← Set to 0', be_irr - p['hurdle'], PCT, '← Goal Seek'),
    ]:
        r += 1; ws.row_dimensions[r].height = 17
        sc(ws, r, 2, label)
        sc(ws, r, 3, nf, fc='595959', sz=9)
        cell = ws.cell(row=r, column=4)
        cell.value = val; cell.number_format = nf
        cell.font = Font(name='Arial', size=11, bold=True,
                         color=BINP if 'Tariff' in label else
                               ('00703C' if val >= 0 else 'C00000'))
        if note: sc(ws, r, 5, note, fc='595959', italic=True, sz=9)

    r += 1
    tariff_gap = be_tariff - p['tariff']
    sc(ws, r, 2,
       f'  Breakeven Tariff = Rs.{be_tariff:.4f}/kWh  |  '
       f'Contract = Rs.{p["tariff"]}/kWh  |  Gap = Rs.{tariff_gap:+.4f}/kWh',
       fc='595959', italic=True, sz=9)
    ws.merge_cells(f'B{r}:E{r}'); ws.row_dimensions[r].height = 14

    sc(ws, r+1, 2, '  Note: Change cell D4 (test tariff) and observe D7 (Gap). Goal Seek: Data → What-If → Set D7=0, change D4.',
       fc='808080', italic=True, sz=8)
    ws.merge_cells(f'B{r+1}:E{r+1}'); ws.row_dimensions[r+1].height = 14

# ─── SHEET 7: SCENARIOS ───────────────────────────────────────────────────────
def irr_color(val):
    """Return (bg_hex, fg_hex, display_str) for an IRR value."""
    if val is None or val <= 0:
        return 'D3D3D3', '808080', 'neg'
    if val >= 0.30:   return '00B050', 'FFFFFF', f'{val*100:.1f}%'
    if val >= 0.25:   return '92D050', '000000', f'{val*100:.1f}%'
    if val >= 0.20:   return 'C6EFCE', '000000', f'{val*100:.1f}%'
    if val >= 0.15:   return 'E2EFDA', '000000', f'{val*100:.1f}%'
    if val >= 0.12:   return 'FFEB9C', '000000', f'{val*100:.1f}%'
    return 'FFC7CE', '000000', f'{val*100:.1f}%'

def heat_cell(ws, r, c, val, is_base=False):
    cell = ws.cell(row=r, column=c)
    if is_base:
        cell.value = f'{val*100:.1f}%  ★' if (val and val>0) else 'base'
        cell.font = Font(name='Arial', size=9, bold=True, color='FFFFFF')
        cell.fill = PatternFill('solid', start_color='4472C4')
    else:
        bg, fg, txt = irr_color(val)
        cell.value = txt
        cell.font = Font(name='Arial', size=9, bold=False, color=fg)
        cell.fill = PatternFill('solid', start_color=bg)
    cell.alignment = Alignment(horizontal='center', vertical='center')
    ws.row_dimensions[r].height = 15

def build_scenarios(wb, p):
    ws = wb.create_sheet('Scenarios')

    # EPC rows: 11 values
    epc_step = (p['scen_epc_max'] - p['scen_epc_min']) / 10
    epc_rows = [int(p['scen_epc_min'] + i*epc_step) for i in range(11)]
    units_cols = p['scen_units']        # 12 values
    tariff_cols = p['scen_tariff']      # 11 values
    rate_cols   = p['scen_rates']       # 11 values

    base_epc = p['epc_rate']
    base_u   = p['gen_per_kwp']
    base_t   = p['tariff']
    base_r   = p['interest_rate']

    # Column widths
    ws.column_dimensions['A'].width = 14
    for i in range(2, 20):
        ws.column_dimensions[get_column_letter(i)].width = 9

    title_row(ws, 1,
        f'SCENARIO ANALYSIS  —  SENSITIVITY HEAT MAPS  |  {p["name"]}', 1, 14)
    sc(ws, 2, 1,
       f'Base: EPC=Rs.{base_epc:,}/kW ex-GST  |  Tariff=Rs.{base_t}/kWh  |  '
       f'Units={base_u}/kWp  |  Eq={p["equity_pct"]*100:.0f}%  |  '
       f'Int={base_r*100:.1f}%  |  AD={p["it_dep"]*100:.0f}%  |  Apr-2026',
       fc='595959', italic=True, sz=9)
    ws.merge_cells('A2:N2'); ws.row_dimensions[2].height = 13

    # Legend
    r = 3; ws.row_dimensions[r].height = 16
    legends = [('≥30%','00B050','FFFFFF'), ('25–30%','92D050','000000'),
               ('20–25%','C6EFCE','000000'), ('15–20%','E2EFDA','000000'),
               ('12–15%','FFEB9C','000000'), ('<12%','FFC7CE','000000'),
               ('Base','4472C4','FFFFFF'), ('Neg/0','D3D3D3','808080')]
    for i, (lbl, bg, fg) in enumerate(legends):
        cell = ws.cell(row=r, column=i+1)
        cell.value = lbl
        cell.font = Font(name='Arial', size=9, bold=True, color=fg)
        cell.fill = PatternFill('solid', start_color=bg)
        cell.alignment = Alignment(horizontal='center', vertical='center')

    # ── TABLE 1: Equity IRR | EPC × Units ──
    r += 1; gap(ws, r); r += 1
    title_row(ws, r, f'TABLE 1  —  EQUITY IRR  |  EPC Rate (Rs./kW ex-GST)  ×  Units Generated (kWh/kWp/yr)',
              1, 14, bg=MB, sz=10)
    r += 1
    sc(ws, r, 1, f'EPC range Rs.{epc_rows[0]:,}–{epc_rows[-1]:,}/kW  |  '
                 f'Units range {units_cols[0]}–{units_cols[-1]}  |  Base: EPC={base_epc:,}, Units={base_u}',
       fc='595959', italic=True, sz=9)
    ws.merge_cells(f'A{r}:{get_column_letter(len(units_cols)+1)}{r}')
    ws.row_dimensions[r].height = 13

    r += 1; ws.row_dimensions[r].height = 18
    sc(ws, r, 1, 'EPC ↓  /  Units →', bold=True, bg=DK, fc=WH, ha='center')
    for j, u in enumerate(units_cols):
        cell = ws.cell(row=r, column=j+2)
        cell.value = u
        cell.font = Font(name='Arial', size=9, bold=True, color=WH)
        cell.fill = PatternFill('solid', start_color=DK)
        cell.alignment = Alignment(horizontal='center', vertical='center')

    print(f'  Building {p["name"]} Table 1 ({len(epc_rows)}×{len(units_cols)})...')
    for i, epc in enumerate(epc_rows):
        r += 1
        lbl_cell = ws.cell(row=r, column=1)
        lbl_cell.value = f'Rs.{epc:,}'
        lbl_cell.font  = Font(name='Arial', size=9, bold=True, color=WH)
        lbl_cell.fill  = PatternFill('solid', start_color=DK)
        lbl_cell.alignment = Alignment(horizontal='center', vertical='center')
        for j, u in enumerate(units_cols):
            res = compute(p, gen_per_kwp=u, epc_rate=epc)
            is_base = (epc == base_epc and u == base_u)
            heat_cell(ws, r, j+2, res['eq_irr'], is_base)

    # ── TABLE 2: Equity IRR | EPC × Interest Rate ──
    r += 2; gap(ws, r); r += 1
    title_row(ws, r, f'TABLE 2  —  EQUITY IRR  |  EPC Rate (Rs./kW ex-GST)  ×  Interest Rate (% pa)',
              1, 14, bg=MB, sz=10)
    r += 1
    sc(ws, r, 1, f'Interest steps 0.5%  |  Base: EPC={base_epc:,}, Rate={base_r*100:.1f}%',
       fc='595959', italic=True, sz=9)
    ws.merge_cells(f'A{r}:{get_column_letter(len(rate_cols)+1)}{r}')
    ws.row_dimensions[r].height = 13

    r += 1; ws.row_dimensions[r].height = 18
    sc(ws, r, 1, 'EPC ↓  /  Rate →', bold=True, bg=DK, fc=WH, ha='center')
    for j, rate in enumerate(rate_cols):
        cell = ws.cell(row=r, column=j+2)
        cell.value = f'{rate*100:.1f}%'
        cell.font = Font(name='Arial', size=9, bold=True, color=WH)
        cell.fill = PatternFill('solid', start_color=DK)
        cell.alignment = Alignment(horizontal='center', vertical='center')

    print(f'  Building {p["name"]} Table 2 ({len(epc_rows)}×{len(rate_cols)})...')
    for i, epc in enumerate(epc_rows):
        r += 1
        lbl_cell = ws.cell(row=r, column=1)
        lbl_cell.value = f'Rs.{epc:,}'
        lbl_cell.font  = Font(name='Arial', size=9, bold=True, color=WH)
        lbl_cell.fill  = PatternFill('solid', start_color=DK)
        lbl_cell.alignment = Alignment(horizontal='center', vertical='center')
        for j, rate in enumerate(rate_cols):
            res = compute(p, epc_rate=epc, interest_rate=rate)
            is_base = (epc == base_epc and abs(rate - base_r) < 0.001)
            heat_cell(ws, r, j+2, res['eq_irr'], is_base)

    # ── TABLE 3: Project IRR | Units × Tariff ──
    r += 2; gap(ws, r); r += 1
    title_row(ws, r, f'TABLE 3  —  PROJECT IRR  |  Units Generated (kWh/kWp/yr)  ×  Tariff (Rs./kWh)',
              1, 14, bg=MB, sz=10)
    r += 1
    sc(ws, r, 1, f'Tariff steps Rs.{tariff_cols[1]-tariff_cols[0]:.2f}/kWh  |  Base: Units={base_u}, Tariff=Rs.{base_t}',
       fc='595959', italic=True, sz=9)
    ws.merge_cells(f'A{r}:{get_column_letter(len(tariff_cols)+1)}{r}')
    ws.row_dimensions[r].height = 13

    r += 1; ws.row_dimensions[r].height = 18
    sc(ws, r, 1, 'Units ↓  /  Tariff →', bold=True, bg=DK, fc=WH, ha='center')
    for j, t in enumerate(tariff_cols):
        cell = ws.cell(row=r, column=j+2)
        cell.value = f'{t:.2f}'
        cell.font = Font(name='Arial', size=9, bold=True, color=WH)
        cell.fill = PatternFill('solid', start_color=DK)
        cell.alignment = Alignment(horizontal='center', vertical='center')

    print(f'  Building {p["name"]} Table 3 ({len(units_cols)}×{len(tariff_cols)})...')
    for i, u in enumerate(units_cols):
        r += 1
        lbl_cell = ws.cell(row=r, column=1)
        lbl_cell.value = u
        lbl_cell.font  = Font(name='Arial', size=9, bold=True, color=WH)
        lbl_cell.fill  = PatternFill('solid', start_color=DK)
        lbl_cell.alignment = Alignment(horizontal='center', vertical='center')
        for j, t in enumerate(tariff_cols):
            res = compute(p, gen_per_kwp=u, tariff=t)
            is_base = (u == base_u and abs(t - base_t) < 0.01)
            heat_cell(ws, r, j+2, res['proj_irr'], is_base)


    # ══ TENURE SENSITIVITY — TABLES 4-6 ═════════════════════════════════════
    # On short-tenure / free-handover deals these are the first tables Ram reads.
    # Read DOWN a column: what an extra PPA year buys at zero incremental capex.
    tenures = p.get('scen_tenures', [5, 6, 7, 8, 9, 10, 12, 15, 20, 25])
    r = ws.max_row + 3

    def _tenure_grid(r, title, sub, cols, colfmt, metric, base_col):
        title_row(ws, r, title, 1, 14, bg=MB, sz=10); r += 1
        sc(ws, r, 1, sub, fc='595959', italic=True, sz=9)
        ws.merge_cells(start_row=r, start_column=1, end_row=r, end_column=14); r += 1
        ws.row_dimensions[r].height = 20
        sc(ws, r, 1, 'PPA yrs ↓', fc=WH, bold=True, bg=DK, ha='center', sz=9)
        for j, v in enumerate(cols):
            sc(ws, r, j+2, colfmt(v), fc=WH, bold=True, bg=DK, ha='center', sz=9)
        r += 1
        for n in tenures:
            lc = ws.cell(row=r, column=1); lc.value = n
            lc.font = Font(name='Arial', size=9, bold=True, color=WH)
            lc.fill = PatternFill('solid', start_color=DK)
            lc.alignment = Alignment(horizontal='center', vertical='center')
            for j, v in enumerate(cols):
                is_base = (n == p['ppa_yrs'] and abs(v - base_col) < 0.01)
                heat_cell(ws, r, j+2, metric(n, v), is_base)
            r += 1
        return r + 2

    _ft = lambda v: f'{v:.2f}'
    _fe = lambda v: f'Rs.{v:,}'

    print(f'  Building {p["name"]} Table 4 (tenure × tariff, Project IRR)...')
    r = _tenure_grid(r,
        'TABLE 4  —  PROJECT IRR  |  PPA TENURE (yrs)  ×  TARIFF (Rs./kWh)',
        'Unlevered post-tax return on the full capitalised cost. Terminal value is nil in every cell.',
        tariff_cols, _ft,
        lambda n, v: compute(dict(p, ppa_yrs=n), tariff=v)['proj_irr'], base_t)

    print(f'  Building {p["name"]} Table 5 (tenure × tariff, Equity MIRR)...')
    r = _tenure_grid(r,
        'TABLE 5  —  EQUITY MIRR  |  PPA TENURE (yrs)  ×  TARIFF (Rs./kWh)',
        'MIRR, not IRR: a refunded security deposit adds a 2nd sign change, so plain IRR is multi-rooted. Finance 10%, reinvest 8%.',
        tariff_cols, _ft,
        lambda n, v: mirr(compute(dict(p, ppa_yrs=n), tariff=v)['eq_cfs']), base_t)

    print(f'  Building {p["name"]} Table 6 (tenure × capex, Project IRR)...')
    r = _tenure_grid(r,
        'TABLE 6  —  PROJECT IRR  |  PPA TENURE (yrs)  ×  EPC / CAPEX RATE (Rs./kW)',
        'Capex rate is the financing and depreciation base actually used (all-in where GST is capitalised).',
        epc_rows, _fe,
        lambda n, v: compute(dict(p, ppa_yrs=n), epc_rate=v)['proj_irr'], base_epc)

    sc(ws, r, 1, '  Bank debt is fully repaid at the end of the debt tenure, so every PPA year beyond that flows to equity unlevered. Extending tenure costs nothing — capex is sunk at Year 0.',
       fc='00703C', italic=True, sz=9)

# ─── BUILD ONE WORKBOOK ───────────────────────────────────────────────────────
def build_workbook(p, out_path):
    print(f'\nBuilding {p["name"]} model...')
    comp = compute(p)
    comp['eq_sign_changes'] = sign_changes(comp['eq_cfs'])
    comp['eq_mirr']         = mirr(comp['eq_cfs'])
    comp['eq_npv_hurdle']   = npv(p['hurdle'], comp['eq_cfs'])
    if comp['eq_sign_changes'] > 1:
        eq_txt = (f'Equity IRR: UNDEFINED (multi-rooted, '
                  f'{comp["eq_sign_changes"]} sign changes) -> '
                  f'MIRR {(comp["eq_mirr"] or 0)*100:.2f}%')
    else:
        eq_txt = f'Equity IRR: {(comp["eq_irr"] or 0)*100:.2f}%'
    print(f'  Project IRR: {(comp["proj_irr"] or 0)*100:.2f}%  |  '
          f'{eq_txt}  |  Min DSCR: {comp["min_dscr"]:.2f}x')

    # Inject epc_ex for depreciation base
    comp['epc_ex'] = p['epc_ex_gst_l']

    wb = Workbook()
    wb.remove(wb.active)

    print('  Building Assumptions...')
    build_assumptions(wb, p, comp)
    print('  Building Debt...')
    build_debt(wb, p, comp)
    print('  Building Depreciation...')
    build_depreciation(wb, p, comp)
    print('  Building FinCal...')
    build_fincal(wb, p, comp)
    print('  Building Project Summary...')
    build_summary(wb, p, comp)
    print('  Building BE_Solver...')
    build_besolver(wb, p, comp)
    print('  Building Scenarios (takes ~30s)...')
    build_scenarios(wb, p)

    wb.save(out_path)
    print(f'  Saved → {out_path}')
    return comp

# ─── MAIN ─────────────────────────────────────────────────────────────────────
if __name__ == '__main__':
    BASE = './output'

    kb_comp = build_workbook(KB, f'{BASE}/ClientA_Solar_Model_G2G.xlsx')
    us_comp = build_workbook(US, f'{BASE}/Client_B_Solar_Model_G2G.xlsx')

    print('\n── SUMMARY ──────────────────────────────────────────')
    for name, comp in [('Client A', kb_comp), ('Client B', us_comp)]:
        print(f'{name}:')
        print(f'  Project IRR : {(comp["proj_irr"] or 0)*100:.2f}%')
        print(f'  Equity IRR  : {(comp["eq_irr"] or 0)*100:.2f}%')
        print(f'  Min DSCR    : {comp["min_dscr"]:.2f}x')
        print(f'  Avg DSCR    : {comp["avg_dscr"]:.2f}x')
        print(f'  Payback     : {comp["payback"]} years' if comp["payback"] else '  Payback     : Beyond horizon')
