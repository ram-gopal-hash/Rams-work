"""
bess_builder.py — G2G Kaamyabi BESS pricing model builder
==========================================================
Solves the operating-lease rental and the storage-PPA tariff that hit a target
post-tax equity IRR, then writes a 9-sheet Excel workbook.

USAGE
    1. Edit the BASE dict and the VALUE-STACK inputs to match the deal.
    2. Set OUT to the target path.
    3. python3 bess_builder.py
    4. ALWAYS recalculate afterwards (formulas are written, not evaluated):
         python3 recalc.py <OUT> 120   (bundled beside this file — portable)
       Then read back the Summary recon checks — all six must read OK.

DESIGN NOTES (read before editing)
    * Tolling structure: charging energy is the CUSTOMER's cost. Charging source does
      not touch G2G's IRR — it drives the customer's ceiling and the achievable cycles.
    * Everything downstream of an input must be a live Excel formula. Python solves only
      what a solver is genuinely needed for (the two prices and the static grids).
    * Years beyond the tenure toggle are masked to zero by an explicit `flag` row.
      The working-capital delta MUST be multiplied by that flag, or Year 6 of a 5-year
      deal releases the Year-5 debtors a second time and IRR reads ~19.2% instead of 18%.
      Recon check #4 exists to catch exactly this.
    * Note text must never begin with "=" or "@" — Excel parses it as a formula.

Requires: openpyxl, numpy
"""

# ═══ SECTION 1 — PRICING ENGINE ═══

import numpy as np

BASE = dict(
    supply_cost   = 87.1298,
    capex_adder   = 0.12,          # raised from 0.10 per review discussion
    kwh_nameplate = 522.0,
    dod           = 0.90,
    availability  = 0.95,
    cycle_life    = 8000.0,
    fade_total    = 0.30,
    cycles_day    = 1.0,
    days          = 365.0,
    tenure        = 5,             # 5 / 7 / 10
    max_debt_yrs  = 7,             # lender cap on BESS
    debt_pct      = 0.70,
    int_rate      = 0.105,
    dep_rate      = 0.15,
    tax_rate      = 0.2517,
    om_y13        = 3.76895,
    om_y45        = 2.93141,
    wty610_total  = 10.05054,      # REbuffr Y6-10 extended warranty, 5-yr block
    ins_rate      = 0.0035,
    debtor_days   = 30.0,
    tv5           = 0.25,          # gross TV % — 5-yr exit (warranty netted separately)
    tv7           = 0.15,
    tv10          = 0.075,
    hurdle        = 0.18,
    rte           = 0.86,
)

def irr(cfs):
    cfs = np.array(cfs, dtype=float)
    for g in [0.15, 0.18, 0.10, 0.25, 0.05, 0.35, 0.5, 0.02]:
        r = g
        for _ in range(2000):
            t  = np.arange(len(cfs))
            f  = np.sum(cfs / (1 + r) ** t)
            fp = np.sum(-t * cfs / (1 + r) ** (t + 1))
            if abs(fp) < 1e-15: break
            rn = r - f / fp
            if abs(rn - r) < 1e-10:
                if -0.9 < rn < 10: return rn
                break
            r = rn
    return None

def amort(debt, rate, yrs):
    rm, nm = rate / 12, yrs * 12
    pmt = debt * rm / (1 - (1 + rm) ** (-nm))
    bal = debt; mi, mp = [], []
    for _ in range(nm):
        i = bal * rm; pr = pmt - i
        mi.append(i); mp.append(pr); bal -= pr
    return ([sum(mi[y*12:(y+1)*12]) for y in range(yrs)],
            [sum(mp[y*12:(y+1)*12]) for y in range(yrs)], pmt)

def om_year(p, yr):
    if yr <= 3: return p["om_y13"]
    if yr <= 5: return p["om_y45"]
    return p["wty610_total"] / 5.0

def tv_amount(p):
    T = p["tenure"]; capex = p["supply_cost"] * (1 + p["capex_adder"])
    tvp = {5: p["tv5"], 7: p["tv7"], 10: p["tv10"]}[T]
    return capex * tvp - (p["wty610_total"] if T == 5 else 0.0)

def discharged_kwh(p, yr):
    cyc_yr  = p["cycles_day"] * p["days"]
    fade_yr = p["fade_total"] / p["cycle_life"] * cyc_yr
    return p["kwh_nameplate"] * p["dod"] * p["availability"] * cyc_yr * (1 - fade_yr * (yr - 0.5))

def equity_cfs(price, mode, p):
    T      = p["tenure"]
    capex  = p["supply_cost"] * (1 + p["capex_adder"])
    debt   = capex * p["debt_pct"]; equity = capex - debt
    dy_    = min(T, p["max_debt_yrs"])
    ai, ap, _ = amort(debt, p["int_rate"], dy_)
    cfs = [-equity]; wdv = capex; bf = 0.0; prev_dbt = 0.0
    for yr in range(1, T + 1):
        rev = price * 12 if mode == "lease" else price * discharged_kwh(p, yr) / 100000.0
        ebitda = rev - om_year(p, yr) - p["ins_rate"] * capex
        iy = ai[yr-1] if yr <= dy_ else 0.0
        py = ap[yr-1] if yr <= dy_ else 0.0
        dep = wdv * p["dep_rate"]; wdv -= dep
        pbt = ebitda - iy - dep
        taxable = max(0.0, pbt - bf); bf = max(0.0, bf - pbt)
        tax = taxable * p["tax_rate"]
        dbt = rev * p["debtor_days"] / 365.0
        cf = ebitda - tax - iy - py - (dbt - prev_dbt); prev_dbt = dbt
        if yr == T:
            tv = tv_amount(p)
            cf += tv - max(0.0, tv - wdv) * p["tax_rate"] + dbt
        cfs.append(cf)
    return cfs

def solve_price(mode, p, lo, hi):
    for _ in range(80):
        mid = (lo + hi) / 2
        r = irr(equity_cfs(mid, mode, p))
        if r is None or r < p["hurdle"]: lo = mid
        else: hi = mid
    return (lo + hi) / 2

def metrics(price, mode, p):
    T = p["tenure"]; capex = p["supply_cost"] * (1 + p["capex_adder"])
    debt = capex * p["debt_pct"]; dy_ = min(T, p["max_debt_yrs"])
    ai, ap, _ = amort(debt, p["int_rate"], dy_)
    cfs = equity_cfs(price, mode, p); r = irr(cfs)
    dscrs = []; wdv = capex; bf = 0.0
    for yr in range(1, dy_ + 1):
        rev = price * 12 if mode == "lease" else price * discharged_kwh(p, yr) / 100000.0
        ebitda = rev - om_year(p, yr) - p["ins_rate"] * capex
        dep = wdv * p["dep_rate"]; wdv -= dep
        pbt = ebitda - ai[yr-1] - dep
        taxable = max(0.0, pbt - bf); bf = max(0.0, bf - pbt)
        tax = taxable * p["tax_rate"]
        dscrs.append((ebitda - tax) / (ai[yr-1] + ap[yr-1]))
    return dict(irr=r, cfs=cfs, capex=capex, debt=debt, equity=capex-debt,
                dscrs=dscrs, min_dscr=min(dscrs), avg_dscr=sum(dscrs)/len(dscrs),
                y1_rev=(price*12 if mode == "lease" else price*discharged_kwh(p,1)/100000.0),
                tv=tv_amount(p))

def value_stack(p, vp):
    """vp: surplus_kwh_day, solar_opp, offpeak, peak, dg, dg_share, min_saving."""
    disc_day = p["kwh_nameplate"] * p["dod"] * p["availability"] * p["cycles_day"] * (1 - p["fade_total"]/p["cycle_life"]*p["cycles_day"]*p["days"]*0.5)
    chg_day  = disc_day / p["rte"]
    sol_used = min(vp["surplus_kwh_day"], chg_day)
    grid     = chg_day - sol_used
    chg_cost_day = sol_used * vp["solar_opp"] + grid * vp["offpeak"]
    chg_per_disc = chg_cost_day / disc_day
    value    = vp["dg_share"] * vp["dg"] + (1 - vp["dg_share"]) * vp["peak"]
    net      = value - chg_per_disc
    ceiling  = net * (1 - vp["min_saving"])
    return dict(disc_day=disc_day, chg_day=chg_day, sol_used=sol_used, grid=grid,
                chg_per_disc=chg_per_disc, value=value, net=net, ceiling=ceiling,
                annual_kwh=disc_day * p["days"])

# ═══ SECTION 2 — WORKBOOK BUILDER ═══

from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

OUT = "/mnt/user-data/outputs/PROJECT_BESS_PricingModel_v1.0.xlsx"   # <-- set per deal
NY = 10  # model horizon columns

# solve prices per tenure
SOLVED = {}
for T in (5, 7, 10):
    p = dict(BASE, tenure=T)
    SOLVED[T] = dict(
        lease=round(solve_price("lease", p, 0.3, 8.0), 4),
        ppa=round(solve_price("ppa", p, 2.0, 60.0), 4))
    SOLVED[T]["ml"] = metrics(SOLVED[T]["lease"], "lease", p)
    SOLVED[T]["mp"] = metrics(SOLVED[T]["ppa"], "ppa", p)
LEASE, PPA = SOLVED[5]["lease"], SOLVED[5]["ppa"]

DARK="1F4E79"; SBLUE="BDD7EE"; WH="FFFFFF"; YEL="FFFF00"
NL='#,##0.00;(#,##0.00);"-"'; N0='#,##0;(#,##0);"-"'
P1='0.0%;(0.0%);"-"'; P2='0.00%'; X2='0.00"x"'; R2='0.00'
def F(b=False,s=9,c="000000",i=False): return Font(name="Arial",bold=b,size=s,color=c,italic=i)
def FILL(c): return PatternFill("solid",fgColor=c)
def ALN(h="left",v="center",w=False): return Alignment(horizontal=h,vertical=v,wrap_text=w)
def BDR():
    t=Side(style="thin",color="CCCCCC"); return Border(left=t,right=t,top=t,bottom=t)
def title(ws,r,t,span):
    c=ws.cell(r,1,t); c.font=F(True,13,WH); c.fill=FILL(DARK); c.alignment=ALN()
    ws.merge_cells(start_row=r,start_column=1,end_row=r,end_column=span); ws.row_dimensions[r].height=30
def sub(ws,r,t,span):
    c=ws.cell(r,1,t); c.font=F(False,9,"595959",i=True); c.alignment=ALN()
    ws.merge_cells(start_row=r,start_column=1,end_row=r,end_column=span)
def sec(ws,r,t,span):
    c=ws.cell(r,1,t); c.font=F(True,10,DARK); c.fill=FILL(SBLUE); c.alignment=ALN()
    ws.merge_cells(start_row=r,start_column=1,end_row=r,end_column=span); ws.row_dimensions[r].height=18
def lbl(ws,r,c,v,b=False,ind=0):
    ce=ws.cell(r,c,("    "*ind)+str(v)); ce.font=F(b); ce.border=BDR(); ce.alignment=ALN(); return ce
def val(ws,r,c,v,fmt=NL,kind="formula",b=False,fill=None):
    col={"input":"0000FF","formula":"000000","link":"008000","static":"7030A0"}[kind]
    ce=ws.cell(r,c,v); ce.font=F(b,9,col); ce.border=BDR(); ce.alignment=ALN("right"); ce.number_format=fmt
    if fill: ce.fill=FILL(fill)
    return ce
def note(ws,r,c,v,span=None):
    ce=ws.cell(r,c,v); ce.font=F(False,8,"595959",i=True); ce.alignment=ALN(w=True); ce.border=BDR()
    if span: ws.merge_cells(start_row=r,start_column=c,end_row=r,end_column=span)
def hdr(ws,r,c,v,fmt=None):
    ce=ws.cell(r,c,v); ce.font=F(True,9,WH); ce.fill=FILL(DARK); ce.alignment=ALN("center",w=True); ce.border=BDR()
    if fmt: ce.number_format=fmt

wb=Workbook(); wb.remove(wb.active)

# ══ ASSUMPTIONS ═══════════════════════════════════════════════
ws=wb.create_sheet("Assumptions"); ws.sheet_view.showGridLines=False
for col,w in {"A":2,"B":46,"C":13,"D":11,"E":64}.items(): ws.column_dimensions[col].width=w
title(ws,1,"BESS PRICING MODEL v1.1 — 250 kW / 522 kWh, Sangli MH  |  Lease vs PPA  |  5/7/10-yr tenure toggle",5)
sub(ws,2,"Rs. Lakhs unless stated | Blue = input | Black = formula | Yellow = key lever | Purple (other sheets) = static Python-solved | REbuffr quote 08-07-2026",5)
A={}; r=4
def arow(key,label,v,fmt=NL,kind="input",unit="Rs L",nt="",fill=None):
    global r
    lbl(ws,r,2,label); val(ws,r,3,v,fmt,kind,fill=fill)
    ce=ws.cell(r,4,unit); ce.font=F(False,8,"666666"); ce.border=BDR(); ce.alignment=ALN("center")
    note(ws,r,5,nt); ws.row_dimensions[r].height=24
    A[key]=r; r+=1

sec(ws,r,"A.  CAPITAL COST",5); r+=1
arow("supply","BESS supply cost (ex-works, ex-GST)",BASE["supply_cost"],NL,"input","Rs L",
     "REbuffr ₹87,12,980 incl. 5-yr defect warranty, EMS, spares. USD/INR 94 basis — see Negotiation Points on FX cap.")
arow("adder","Client-scope capex adder",BASE["capex_adder"],P1,"input","% of supply",
     "Raised to 12% (~₹10.5 L) after peer-model review flagged ₹10-15 L range. Freight, civil, HT breaker, cabling, crane. Replace with actual quotes.",fill=YEL)
arow("capex","Total project capex (ex-GST)",f"=C{A['supply']}*(1+C{A['adder']})",NL,"formula","Rs L","Financing and depreciation base.")
arow("gst","GST on capex (memo)",0.18,P1,"input","%","ITC assumed creditable — G2G makes taxable supplies @18%. Confirm with CA.")

sec(ws,r,"B.  TECHNICAL",5); r+=1
arow("kwh","Nameplate energy",522,N0,"input","kWh","Liquid-cooled LFP.")
arow("kw","PCS rating",250,N0,"input","kW","3P3W 415 Vac at 50 degC. Used for the power feasibility checks on Value Stack.")
arow("chgwin","Charging window length",8,N0,"input","hours","Solar hours available for charging (e.g. 09:00-17:00 = 8). Drives the charge-power check.")
arow("diswin","Discharge window length",7,N0,"input","hours","Hours over which the battery discharges (e.g. evening peak 17:00-24:00 = 7).")
arow("dod","Depth of discharge",BASE["dod"],P1,"input","%","")
arow("avail","Availability",BASE["availability"],P1,"input","%","REbuffr guarantees only 95%; negotiating 96-97% would flow straight to revenue — see Negotiation Points.")
arow("cyclife","Cycle life to 70% SOH",8000,N0,"input","cycles","")
arow("fade","Capacity fade over cycle life",BASE["fade_total"],P1,"input","%","")
arow("cyc","Cycles per day",BASE["cycles_day"],R2,"input","cyc/day","Drives PPA revenue AND the customer value stack. Toggle 1.0-2.0.",fill=YEL)
arow("days","Operating days per year",365,N0,"input","days","")
arow("fadeyr","Annual SOH fade",f"=C{A['fade']}/C{A['cyclife']}*C{A['cyc']}*C{A['days']}",P2,"formula","%/yr","")
arow("rte","Round-trip efficiency",BASE["rte"],P1,"input","%",
     "AC-to-AC incl. chiller aux load. NOT guaranteed by REbuffr — demand ≥86% guarantee with LDs (Negotiation Points #3). Feeds Value Stack charging cost.")

sec(ws,r,"C.  CONTRACT — TENURE TOGGLE",5); r+=1
arow("tenure","Contract tenure  ►  SET 5, 7 OR 10",5,N0,"input","years",
     "MASTER TOGGLE. All sheets recalc. Solved prices below are per-tenure — pick the matching pair from Scenario Comparison.",fill=YEL)
arow("maxdebt","Max debt tenure (lender cap)",BASE["max_debt_yrs"],N0,"input","years","Lenders unlikely to exceed 7 yrs on BESS today.")
arow("debtyrs","Debt tenure (applied)",f"=MIN(C{A['tenure']},C{A['maxdebt']})",N0,"formula","years","10-yr contract runs deleveraged in Y8-10.")
arow("dd","Debtor days",30,N0,"input","days","")

sec(ws,r,"D.  FINANCING",5); r+=1
arow("dpct","Debt share",BASE["debt_pct"],P1,"input","%","")
arow("debt","Debt amount",f"=C{A['capex']}*C{A['dpct']}",NL,"formula","Rs L","")
arow("equity","Equity amount",f"=C{A['capex']}-C{A['debt']}",NL,"formula","Rs L","")
arow("int","Interest rate",BASE["int_rate"],P2,"input","% p.a.","Confirm with lender; BESS may price 50-150bps over solar.")

sec(ws,r,"E.  OPERATING COSTS",5); r+=1
arow("om13","O&M / warranty — Years 1-3",BASE["om_y13"],NL,"input","Rs L/yr","REbuffr ₹3,76,895 — per-year vs lump-sum ambiguity. CONFIRM (Negotiation #5).")
arow("om45","O&M / warranty — Years 4-5",BASE["om_y45"],NL,"input","Rs L/yr","REbuffr ₹2,93,141 — same ambiguity.")
arow("wty","Extended warranty Y6-10 (total)",BASE["wty610_total"],NL,"input","Rs L","REbuffr ₹10,05,054 for the 5-yr block. Netted off 5-yr TV; expensed p.a. for 7/10-yr tenures.")
arow("wtyann","  — annualised (Y6+)",f"=C{A['wty']}/5",NL,"formula","Rs L/yr","Amortised evenly — smoother DSCR than Y6 lump, same NPV.")
arow("ins","Insurance",BASE["ins_rate"],P2,"input","% capex/yr","")

sec(ws,r,"F.  TAX & DEPRECIATION",5); r+=1
arow("dep","Depreciation rate (WDV)",BASE["dep_rate"],P1,"input","%","15% standalone P&M. 40% only if capitalised in integrated solar+storage — CA opinion. Toggle to test.",fill=YEL)
arow("tax","Income tax rate",BASE["tax_rate"],P2,"input","%","115BAA.")

sec(ws,r,"G.  TERMINAL VALUE — per tenure (edit when better data available)",5); r+=1
arow("tv5","TV % — 5-yr exit (gross)",BASE["tv5"],P1,"input","% capex","~93% SOH at exit. Buyer inherits Y6-10 warranty → netted below.")
arow("tv7","TV % — 7-yr exit",BASE["tv7"],P1,"input","% capex","~90% SOH @1 cyc/day.")
arow("tv10","TV % — 10-yr exit",BASE["tv10"],P1,"input","% capex","~86% SOH @1 cyc; ~73% @2 cyc (91% of warranty life used — see Scenario Comparison).")
arow("tvpct","TV % applied (per toggle)",f"=IF(C{A['tenure']}=5,C{A['tv5']},IF(C{A['tenure']}=7,C{A['tv7']},C{A['tv10']}))",P1,"formula","% capex","")
arow("tv","TV amount (net)",f"=C{A['capex']}*C{A['tvpct']}-IF(C{A['tenure']}=5,C{A['wty']},0)",NL,"formula","Rs L",
     "5-yr: gross TV less Y6-10 warranty the buyer inherits. Underwrite contractually: fixed-price buyout / renewal option.")

sec(ws,r,"H.  RETURN TARGET & SOLVED PRICES (5-yr base — see Scenario Comparison for 7/10)",5); r+=1
arow("hurdle","Target post-tax equity IRR",BASE["hurdle"],P1,"input","%","")
arow("lease","OPTION A — Lease rental (solved, 5-yr)",LEASE,NL,"input","Rs L/month",
     f"₹{LEASE*100000:,.0f}/month + GST, flat, full-service. If toggling tenure, paste the matching price from Scenario Comparison to re-check 18%.",fill=YEL)
arow("ppa","OPTION B — Storage tariff (solved, 5-yr)",PPA,R2,"input","Rs/kWh",
     "At 1 cyc/day. Pair with take-or-pay floor of 90% of contracted cycles.",fill=YEL)

sec(ws,r,"I.  CUSTOMER VALUE STACK INPUTS",5); r+=1
arow("surplus","Solar surplus available for charging",450,N0,"input","kWh/day",
     "YOUR INPUT — monsoon-adjusted annual average from load study. 530 kWp vs 400 kW demand suggests 350-600 kWh/day seasonal. Refine with load-profile model later.",fill=YEL)
arow("regime","Export regime (1=Curtailed 2=Net-meter 3=Banking 4=RESCO PPA)",4,N0,"input","choice",
     "Sets the opportunity cost of a solar-surplus kWh — the only number the regime changes.",fill=YEL)
arow("rc1","  Regime 1 — Curtailed / export-blocked",0.00,R2,"input","Rs/kWh","Surplus otherwise stranded — battery rescues it free.")
arow("rc2","  Regime 2 — Net metering (export credit forgone)",3.30,R2,"input","Rs/kWh","MSEDCL solar compensation ~₹3-3.5. Verify current order.")
arow("rc3","  Regime 3 — Banking (banked value forgone)",3.50,R2,"input","Rs/kWh","Peak-hour banking withdrawal restricted — verify.")
arow("rc4","  Regime 4 — RESCO PPA (customer pays tariff anyway)",4.50,R2,"input","Rs/kWh","Kaamyabi solar PPA tariff — units consumed by battery are billed like any other.")
arow("solopp","Solar opportunity cost (applied)",f"=CHOOSE(C{A['regime']},C{A['rc1']},C{A['rc2']},C{A['rc3']},C{A['rc4']})",R2,"formula","Rs/kWh","")
arow("gridbase","MSEDCL base energy charge (HT industrial)",7.30,R2,"input","Rs/kWh",
     "VERIFY from customer's bill / MERC MYT order FY26-30. Category-specific.")
arow("peaksur","Peak surcharge (17:00-24:00)",0.25,P1,"input","%","Current MERC order: +25% for HT/LT industrial & commercial.")
arow("oprebate","Off-peak rebate (solar hours 09:00-17:00)",0.25,P1,"input","%","Off-peak is now DAYTIME — grid top-up charging happens in the same window as solar surplus.")
arow("peak","Peak rate (computed)",f"=C{A['gridbase']}*(1+C{A['peaksur']})",R2,"formula","Rs/kWh","")
arow("offpeak","Off-peak rate (computed)",f"=C{A['gridbase']}*(1-C{A['oprebate']})",R2,"formula","Rs/kWh","Grid top-up charging cost.")
arow("dg","DG generation cost displaced",25.0,R2,"input","Rs/kWh","Diesel ~₹92/L ÷ 3.6 kWh/L + O&M. Verify from fuel logs.")
arow("dgshare","Discharge to DG offset (share)",0.60,P1,"input","%","Balance goes to evening peak-shaving. Site-specific — from outage history.",fill=YEL)
arow("minsave","Customer minimum saving (marketable ceiling)",0.20,P1,"input","%",
     "Ceiling = customer net value × (1 − this). Change case-by-case as agreed.",fill=YEL)
arow("ktariff","Kaamyabi solar PPA tariff (bundled memo)",4.50,R2,"input","Rs/kWh","For the two-revenue-streams memo on Value Stack.")

# ══ DEBT SCHEDULE (10 cols, dynamic debt tenure) ═══════════════
ws=wb.create_sheet("Debt Schedule"); ws.sheet_view.showGridLines=False
ws.column_dimensions["A"].width=2; ws.column_dimensions["B"].width=28
for i in range(NY): ws.column_dimensions[get_column_letter(3+i)].width=11
title(ws,1,"TERM DEBT — MONTHLY EMI, ANNUAL SUMMARY  (Rs. Lakhs)  |  tenure = MIN(contract, 7)",12)
sub(ws,2,"Zero beyond debt tenure. 10-yr contracts run deleveraged in Years 8-10.",12)
hdr(ws,4,2,"Year")
for y in range(1,NY+1): hdr(ws,4,2+y,y,N0)
DS={"open":5,"int":6,"prin":7,"close":8}
lbl(ws,5,2,"Opening balance",True); lbl(ws,6,2,"Interest"); lbl(ws,7,2,"Principal repaid"); lbl(ws,8,2,"Closing balance",True)
for y in range(1,NY+1):
    c,pc=get_column_letter(2+y),get_column_letter(1+y)
    val(ws,5,2+y,f"=Assumptions!$C${A['debt']}" if y==1 else f"={pc}8",NL,"link" if y==1 else "formula",b=True)
    val(ws,6,2+y,f"=IF({c}$4<=Assumptions!$C${A['debtyrs']},-CUMIPMT(Assumptions!$C${A['int']}/12,Assumptions!$C${A['debtyrs']}*12,Assumptions!$C${A['debt']},{(y-1)*12+1},{y*12},0),0)",NL)
    val(ws,7,2+y,f"=IF({c}$4<=Assumptions!$C${A['debtyrs']},-CUMPRINC(Assumptions!$C${A['int']}/12,Assumptions!$C${A['debtyrs']}*12,Assumptions!$C${A['debt']},{(y-1)*12+1},{y*12},0),0)",NL)
    val(ws,8,2+y,f"={c}5-{c}7",NL,b=True)

# ══ MODEL SHEETS (10 cols, tenure-masked) ═════════════════════
def build_model(name,mode):
    ws=wb.create_sheet(name); ws.sheet_view.showGridLines=False
    ws.column_dimensions["A"].width=2; ws.column_dimensions["B"].width=42; ws.column_dimensions["C"].width=11
    for i in range(NY): ws.column_dimensions[get_column_letter(4+i)].width=11
    ttl=("OPTION A — OPERATING LEASE (full-service, flat monthly rental)" if mode=="lease"
         else "OPTION B — STORAGE PPA (Rs/kWh on discharged energy)")
    title(ws,1,f"{ttl}  |  Rs. Lakhs  |  years beyond tenure toggle auto-zero",13)
    sub(ws,2,"Fully live — Assumptions drive everything. Yellow IRR cell is the pricing check.",13)
    hdr(ws,3,2,"Particulars"); hdr(ws,3,3,"Year 0")
    for y in range(1,NY+1): hdr(ws,3,3+y,y,N0)
    cols=[get_column_letter(4+i) for i in range(NY)]
    r=4; RR={}
    def R(tag,label,fn,fmt=NL,b=False,kind="formula",y0=None,ind=0):
        nonlocal r
        lbl(ws,r,2,label,b,ind)
        if y0 is not None: val(ws,r,3,y0,fmt,"link",b)
        else:
            ce=ws.cell(r,3,None); ce.border=BDR()
        for i,c in enumerate(cols): val(ws,r,4+i,fn(c,i+1),fmt,kind,b)
        RR[tag]=r; r+=1
    def S(t):
        nonlocal r; sec(ws,r,t,13); r+=1

    S("TENURE MASK & ENERGY")
    R("flag","Year active (1 within tenure, else 0)",lambda c,y:f"=IF({c}$3<=Assumptions!$C${A['tenure']},1,0)",N0)
    R("cyc","Cycles per year",lambda c,y:f"=Assumptions!$C${A['cyc']}*Assumptions!$C${A['days']}*{c}{RR['flag']}",N0)
    R("soh","Average SOH in year",lambda c,y:f"=1-Assumptions!$C${A['fadeyr']}*({c}$3-0.5)",P1)
    R("kwh","Discharged energy billed (kWh)",lambda c,y:f"=Assumptions!$C${A['kwh']}*Assumptions!$C${A['dod']}*Assumptions!$C${A['avail']}*{c}{RR['cyc']}*{c}{RR['soh']}",N0,True)

    S("REVENUE & OPERATING COSTS")
    if mode=="lease":
        R("rev","Lease rental income (flat)",lambda c,y:f"=Assumptions!$C${A['lease']}*12*{c}{RR['flag']}",NL,True)
    else:
        R("rev","Storage tariff revenue",lambda c,y:f"=Assumptions!$C${A['ppa']}*{c}{RR['kwh']}/100000",NL,True)
    R("om","O&M / extended warranty",lambda c,y:f"=IF({c}{RR['flag']}=0,0,IF({c}$3<=3,Assumptions!$C${A['om13']},IF({c}$3<=5,Assumptions!$C${A['om45']},Assumptions!$C${A['wtyann']})))",NL,ind=1)
    R("ins","Insurance",lambda c,y:f"=Assumptions!$C${A['ins']}*Assumptions!$C${A['capex']}*{c}{RR['flag']}",NL,ind=1)
    R("ebd","EBITDA",lambda c,y:f"={c}{RR['rev']}-{c}{RR['om']}-{c}{RR['ins']}",NL,True)

    S("DEBT SERVICE")
    R("int","Interest",lambda c,y:f"='Debt Schedule'!{get_column_letter(2+y)}{DS['int']}",NL,kind="link")
    R("pri","Principal",lambda c,y:f"='Debt Schedule'!{get_column_letter(2+y)}{DS['prin']}",NL,kind="link")

    S("DEPRECIATION (WDV) & TAX — loss carry-forward")
    R("wop","Opening WDV",lambda c,y:(f"=Assumptions!$C${A['capex']}" if y==1 else f"={get_column_letter(2+y)}{r+2}"),NL)
    R("dep","Depreciation",lambda c,y:f"={c}{RR['wop']}*Assumptions!$C${A['dep']}*{c}{RR['flag']}",NL)
    R("wcl","Closing WDV",lambda c,y:f"={c}{RR['wop']}-{c}{RR['dep']}",NL)
    R("pbt","Profit before tax",lambda c,y:f"={c}{RR['ebd']}-{c}{RR['int']}-{c}{RR['dep']}",NL,True)
    R("bfo","Loss b/f (opening)",lambda c,y:("=0" if y==1 else f"={get_column_letter(2+y)}{r+2}"),NL,ind=1)
    R("txb","Taxable income",lambda c,y:f"=MAX(0,{c}{RR['pbt']}-{c}{RR['bfo']})",NL,ind=1)
    R("bfc","Loss c/f (closing)",lambda c,y:f"=MAX(0,{c}{RR['bfo']}-{c}{RR['pbt']})",NL,ind=1)
    R("tax","Income tax",lambda c,y:f"={c}{RR['txb']}*Assumptions!$C${A['tax']}",NL)

    S("WORKING CAPITAL & TERMINAL VALUE")
    R("dbt","Trade debtors (closing)",lambda c,y:f"={c}{RR['rev']}*Assumptions!$C${A['dd']}/365",NL)
    R("dwc","Increase in working capital",lambda c,y:(f"={c}{RR['dbt']}*{c}{RR['flag']}" if y==1 else f"=({c}{RR['dbt']}-{get_column_letter(2+y)}{RR['dbt']})*{c}{RR['flag']}"),NL)
    R("tv","Terminal value (net, at tenure end)",lambda c,y:f"=IF({c}$3=Assumptions!$C${A['tenure']},Assumptions!$C${A['tv']},0)",NL)
    R("tvt","Tax on terminal value",lambda c,y:f"=IF({c}$3=Assumptions!$C${A['tenure']},MAX(0,{c}{RR['tv']}-{c}{RR['wcl']})*Assumptions!$C${A['tax']},0)",NL,ind=1)

    S("EQUITY CASH FLOW & RETURNS")
    R("cf","Post-tax equity cash flow",
      lambda c,y:f"={c}{RR['ebd']}-{c}{RR['tax']}-{c}{RR['int']}-{c}{RR['pri']}-{c}{RR['dwc']}+{c}{RR['tv']}-{c}{RR['tvt']}+IF({c}$3=Assumptions!$C${A['tenure']},{c}{RR['dbt']},0)",
      NL,True,y0=f"=-Assumptions!$C${A['equity']}")
    R("cum","Cumulative equity cash flow",lambda c,y:(f"=C{RR['cf']}+D{RR['cf']}" if y==1 else f"={get_column_letter(2+y)}{r}+{c}{RR['cf']}"),NL,y0=f"=-Assumptions!$C${A['equity']}")
    lbl(ws,r,2,"Post-tax equity IRR",True)
    val(ws,r,3,f"=IRR(C{RR['cf']}:M{RR['cf']})",P2,"formula",True,fill=YEL)
    RR["irr"]=r; r+=1
    R("dscr","DSCR  [(EBITDA − tax) / debt service]",lambda c,y:f"=IF({c}{RR['int']}+{c}{RR['pri']}<=0,\"\",({c}{RR['ebd']}-{c}{RR['tax']})/({c}{RR['int']}+{c}{RR['pri']}))",X2)
    return RR

RL=build_model("Lease Model","lease")
RP=build_model("PPA Model","ppa")

# ══ CUSTOMER VALUE STACK (live) ═══════════════════════════════
ws=wb.create_sheet("Value Stack",1); ws.sheet_view.showGridLines=False
for col,w in {"A":2,"B":46,"C":14,"D":11,"E":62}.items(): ws.column_dimensions[col].width=w
title(ws,1,"CUSTOMER VALUE STACK — regime-agnostic  |  Y1 basis, per day unless stated",5)
sub(ws,2,"Fully live: change surplus, regime, cycles, ToD rates or DG share on Assumptions and this recalculates. Purple = static Python-solved floor prices.",5)
r=4; V={}
def vrow(key,label,f,fmt=R2,kind="formula",unit="",nt="",b=False,fill=None):
    global r
    lbl(ws,r,2,label,b); val(ws,r,3,f,fmt,kind,b,fill=fill)
    ce=ws.cell(r,4,unit); ce.font=F(False,8,"666666"); ce.border=BDR(); ce.alignment=ALN("center")
    note(ws,r,5,nt); ws.row_dimensions[r].height=22
    V[key]=r; r+=1

sec(ws,r,"A.  CHARGING WATERFALL (solar surplus first, off-peak grid top-up)",5); r+=1
vrow("disc","Daily discharge target",f"=Assumptions!C{A['kwh']}*Assumptions!C{A['dod']}*Assumptions!C{A['avail']}*Assumptions!C{A['cyc']}*(1-Assumptions!C{A['fadeyr']}*0.5)",R2,"formula","kWh/day","Y1 average SOH basis.")
vrow("chg","Charging energy required",f"=C{V['disc']}/Assumptions!C{A['rte']}",R2,"formula","kWh/day","Discharge ÷ RTE — why the RTE guarantee matters commercially.")
vrow("sol","Solar surplus used",f"=MIN(Assumptions!C{A['surplus']},C{V['chg']})",R2,"formula","kWh/day","Cheaper lane fills first.")
vrow("grid","Grid top-up (off-peak, solar hours)",f"=C{V['chg']}-C{V['sol']}",R2,"formula","kWh/day","MSEDCL off-peak window is now 09:00-17:00 — same window as surplus.")
vrow("solsh","Solar share of charging",f"=C{V['sol']}/C{V['chg']}",P1,"formula","%","")
vrow("chgcost","Charging cost per discharged kWh",f"=(C{V['sol']}*Assumptions!C{A['solopp']}+C{V['grid']}*Assumptions!C{A['offpeak']})/C{V['disc']}",R2,"formula","Rs/kWh","Blended, grossed up for RTE losses.",True)

sec(ws,r,"B.  DISCHARGE VALUE",5); r+=1
vrow("dval","Blended avoided cost",f"=Assumptions!C{A['dgshare']}*Assumptions!C{A['dg']}+(1-Assumptions!C{A['dgshare']})*Assumptions!C{A['peak']}",R2,"formula","Rs/kWh","DG-offset share × ₹25 + peak-shave share × peak rate.",True)
vrow("net","Customer net value per discharged kWh",f"=C{V['dval']}-C{V['chgcost']}",R2,"formula","Rs/kWh","What storage is worth to them, gross of our price.",True)

sec(ws,r,"C.  PRICING CORRIDOR — PPA (Rs/kWh discharged)",5); r+=1
vrow("ceil","CEILING — max marketable price",f"=C{V['net']}*(1-Assumptions!C{A['minsave']})",R2,"formula","Rs/kWh","Net value less the customer's minimum saving.",True,fill=YEL)
vrow("floor","FLOOR — our 18% IRR price",f"=Assumptions!C{A['ppa']}",R2,"link","Rs/kWh","Solved on PPA Model at current toggle settings.",True,fill=YEL)
vrow("corr","Corridor (ceiling − floor)",f"=C{V['ceil']}-C{V['floor']}",R2,"formula","Rs/kWh","",True)
vrow("stat","Deal status",f'=IF(C{V["corr"]}>=0,"DEAL SPACE — price inside corridor","UNDERWATER — need more cycles / DG share / tenure")',"@","formula","","",True)

sec(ws,r,"D.  CORRIDOR — LEASE EQUIVALENT (Rs Lakhs/month)",5); r+=1
vrow("akwh","Annual discharged energy (Y1)",f"=C{V['disc']}*Assumptions!C{A['days']}",N0,"formula","kWh/yr","")
vrow("lceil","Lease ceiling",f"=C{V['ceil']}*C{V['akwh']}/12/100000",NL,"formula","Rs L/mo","Same ceiling expressed as flat rental.")
vrow("lfloor","Lease floor (our 18%)",f"=Assumptions!C{A['lease']}",NL,"link","Rs L/mo","")
vrow("lcorr","Corridor",f"=C{V['lceil']}-C{V['lfloor']}",NL,"formula","Rs L/mo","",True)

sec(ws,r,"E.  CORRIDOR vs CYCLES — floor is static (Python-solved), ceiling recalculates live",5); r+=1
hdr(ws,r,2,"Cycles/day"); cyc_axis=[1.00,1.25,1.50,1.75,2.00]
for j,cy in enumerate(cyc_axis): hdr(ws,r,3+j,cy,R2)
r+=1
lbl(ws,r,2,"FLOOR — PPA @18% IRR (static, 5-yr)")
floor_vals={}
for j,cy in enumerate(cyc_axis):
    fv=round(solve_price("ppa",dict(BASE,cycles_day=cy),2.0,60.0),2)
    floor_vals[cy]=fv
    val(ws,r,3+j,fv,R2,"static")
r+=1
lbl(ws,r,2,"CEILING — live at each cycle level")
ceil_row=r
for j,cy in enumerate(cyc_axis):
    # live ceiling with cycles overridden: recompute disc/chg/mix inline
    d=f"(Assumptions!$C${A['kwh']}*Assumptions!$C${A['dod']}*Assumptions!$C${A['avail']}*{cy}*(1-Assumptions!$C${A['fade']}/Assumptions!$C${A['cyclife']}*{cy}*Assumptions!$C${A['days']}*0.5))"
    ch=f"({d}/Assumptions!$C${A['rte']})"
    so=f"MIN(Assumptions!$C${A['surplus']},{ch})"
    gr=f"({ch}-{so})"
    cc=f"(({so}*Assumptions!$C${A['solopp']}+{gr}*Assumptions!$C${A['offpeak']})/{d})"
    f=f"=(Assumptions!$C${A['dgshare']}*Assumptions!$C${A['dg']}+(1-Assumptions!$C${A['dgshare']})*Assumptions!$C${A['peak']}-{cc})*(1-Assumptions!$C${A['minsave']})"
    val(ws,r,3+j,f,R2)
r+=1
lbl(ws,r,2,"Corridor (ceiling − floor)",True)
for j,cy in enumerate(cyc_axis):
    c=get_column_letter(3+j)
    ce=ws.cell(r,3+j,f"={c}{ceil_row}-{floor_vals[cy]}"); ce.border=BDR(); ce.alignment=ALN("right"); ce.number_format=R2
    ce.font=F(True,9)
r+=1
note(ws,r,2,"The corridor typically opens between 1.5 and 2.0 cycles/day — more cycles cut our floor faster than they erode the customer's charging economics. This row is the dispatch case to engineer with the customer.",5); r+=2

sec(ws,r,"F.  PHYSICAL FEASIBILITY — can the hardware actually do this?",5); r+=1
vrow("reqname","Required nameplate for assumed cycles",f"=C{V['disc']}/(Assumptions!C{A['dod']}*Assumptions!C{A['avail']})",R2,"formula","kWh",
     "Daily discharge / (DoD x availability). A battery delivers only ~85.5% of nameplate per fill.",True)
vrow("insname","Nameplate installed",f"=Assumptions!C{A['kwh']}",R2,"link","kWh","")
vrow("sizechk","CHECK — battery large enough?",f'=IF(Assumptions!C{A["kwh"]}>=C{V["reqname"]}-0.5,"OK","TOO SMALL — need "&TEXT(C{V["reqname"]},"#,##0")&" kWh")',"@","formula","",
     "Annual-energy models produce cycle counts a single battery cannot physically deliver. This catches it.",True)
vrow("gridecon","Grid top-up cost to deliver 1 kWh",f"=Assumptions!C{A['offpeak']}/Assumptions!C{A['rte']}",R2,"formula","Rs/kWh",
     "Off-peak rate grossed up for RTE losses.")
vrow("gridchk","CHECK — is grid top-up economic?",f'=IF(C{V["gridecon"]}<C{V["dval"]}*0.6,"YES — a 2nd charging window exists, >1 cycle/day reachable","NO — solar-only charging, cycles capped at ~1.0/day")',"@","formula","",
     "Decides whether the cycles lever exists at this site. If NO, do not carry over sensitivity conclusions that assume 1.5-2 cycles.",True)
vrow("cycchk","CHECK — one-charging-window rule",f'=IF(OR(Assumptions!C{A["cyc"]}<=1.0001,C{V["gridecon"]}<C{V["dval"]}*0.6),"OK","INFEASIBLE — "&TEXT(Assumptions!C{A["cyc"]},"0.00")&" cyc/day needs a 2nd charging window")',"@","formula","",
     "One sun per day = one charging window. Exception: genuine discharge demand inside the charging window (daytime DG offset).",True)
vrow("chgpwr","Charge power required (average)",f"=C{V['chg']}/Assumptions!C{A['chgwin']}",R2,"formula","kW","Solar surplus is a bell curve — midday peak can exceed this average and clip the PCS.")
vrow("dispwr","Discharge power required (average)",f"=C{V['disc']}/Assumptions!C{A['diswin']}",R2,"formula","kW","")
vrow("pwrchk","CHECK — PCS rating adequate?",f'=IF(AND(C{V["chgpwr"]}<=Assumptions!C{A["kw"]},C{V["dispwr"]}<=Assumptions!C{A["kw"]}),"OK on average — verify peak against hourly profile","UNDERSIZED — PCS "&Assumptions!C{A["kw"]}&" kW")',"@","formula","",
     "Averages only. Annual totals cannot answer whether midday surplus clips the PCS — needs the hourly generation profile.",True)

sec(ws,r,"G.  KAAMYABI BUNDLED VIEW (internal memo — solar is ours)",5); r+=1
vrow("skwh","Solar kWh sold to battery per year",f"=C{V['sol']}*Assumptions!C{A['days']}",N0,"formula","kWh/yr","Every charging electron is solar-PPA revenue to G2G.")
vrow("srev","Solar revenue on battery charging",f"=C{V['skwh']}*Assumptions!C{A['ktariff']}/100000",NL,"formula","Rs L/yr","")
vrow("strev","Storage revenue (PPA at floor)",f"=C{V['floor']}*C{V['akwh']}/100000",NL,"formula","Rs L/yr","")
vrow("comb","Combined G2G revenue per year",f"=C{V['srev']}+C{V['strev']}",NL,"formula","Rs L/yr",
     "Two revenue streams on the same electron. Gives room to concede on storage price and recover on solar volume — do NOT show this sheet section to the customer.",True)

# ══ SCENARIO COMPARISON (static) ══════════════════════════════
ws=wb.create_sheet("Scenario Comparison"); ws.sheet_view.showGridLines=False
for col,w in {"A":2,"B":40,"C":16,"D":16,"E":16,"F":50}.items(): ws.column_dimensions[col].width=w
title(ws,1,"TENURE SCENARIOS — 5 / 7 / 10 YEARS  (all solved to 18.00% post-tax equity IRR)",6)
sub(ws,2,"STATIC Python-solved (purple). The live model follows the tenure toggle on Assumptions — paste the matching price there to verify. Base: 1 cyc/day, 12% adder, 15% WDV.",6)
r=4
hdr(ws,r,2,"Metric"); hdr(ws,r,3,"5-year"); hdr(ws,r,4,"7-year"); hdr(ws,r,5,"10-year"); hdr(ws,r,6,"Notes")
r+=1
def scomp(label,vals,fmt=NL,nt="",b=False):
    global r
    lbl(ws,r,2,label,b)
    for j,v in enumerate(vals): val(ws,r,3+j,v,fmt,"static",b)
    note(ws,r,6,nt); ws.row_dimensions[r].height=22
    r+=1
S5,S7,S10=SOLVED[5],SOLVED[7],SOLVED[10]
scomp("Lease rental (Rs L/month)",[S5["lease"],S7["lease"],S10["lease"]],NL,"Falls with tenure — longer amortisation beats lower TV. A sales lever for longer lock-ins.",True)
scomp("  = per month",[f"₹{S5['lease']*1e5:,.0f}",f"₹{S7['lease']*1e5:,.0f}",f"₹{S10['lease']*1e5:,.0f}"],"@","")
scomp("PPA tariff (Rs/kWh @ 1 cyc/day)",[S5["ppa"],S7["ppa"],S10["ppa"]],R2,"",True)
scomp("Lease: min DSCR",[S5["ml"]["min_dscr"],S7["ml"]["min_dscr"],S10["ml"]["min_dscr"]],X2,"10-yr min is Y1 (7-yr debt on lower rental); Y8-10 deleveraged.")
scomp("Lease: avg DSCR (debt yrs)",[S5["ml"]["avg_dscr"],S7["ml"]["avg_dscr"],S10["ml"]["avg_dscr"]],X2,"")
scomp("PPA: min DSCR",[S5["mp"]["min_dscr"],S7["mp"]["min_dscr"],S10["mp"]["min_dscr"]],X2,"")
scomp("Terminal value — net (Rs L)",[S5["ml"]["tv"],S7["ml"]["tv"],S10["ml"]["tv"]],NL,"5-yr: 25% gross less ₹10.05 L Y6-10 warranty buyer inherits. 7-yr: 15%. 10-yr: 7.5%. All editable on Assumptions.")
scomp("Y6-10 warranty treatment",["Netted off TV","Opex ₹2.01 L/yr (Y6-7)","Opex ₹2.01 L/yr (Y6-10)"],"@","")
scomp("Debt tenure (yrs)",[5,7,7],N0,"Lender cap 7 yrs on BESS assumed.")
scomp("Cycles used @ 1 cyc/day",[1825,2555,3650],N0,"vs 8,000-cycle warranty budget.")
scomp("  — % of cycle budget",[0.228,0.319,0.456],P1,"At 2 cyc/day the 10-yr case uses 91% of budget — no augmentation capex modelled; cap cycles contractually or price augmentation.")
scomp("End-of-tenure SOH @ 1 cyc/day",[0.932,0.904,0.863],P1,"Supports the TV assumptions.")

# ══ SENSITIVITY (static, 5-yr base) ═══════════════════════════
ws=wb.create_sheet("Sensitivity"); ws.sheet_view.showGridLines=False
ws.column_dimensions["A"].width=2; ws.column_dimensions["B"].width=26
for i in range(7): ws.column_dimensions[get_column_letter(3+i)].width=12
title(ws,1,"SENSITIVITY — REQUIRED PRICE FOR 18% POST-TAX EQUITY IRR  (5-yr tenure)",9)
sub(ws,2,"STATIC Python-solved (purple values) — re-run solver after changing Assumptions. Blue cell = base case.",9)
def heat(ws,r,c,v,fmt,base=False,lo=None,hi=None):
    ce=ws.cell(r,c,v); ce.border=BDR(); ce.alignment=ALN("center"); ce.number_format=fmt
    if base: ce.fill=FILL("4472C4"); ce.font=F(True,9,WH)
    else:
        ce.font=F(False,9,"7030A0")
        if lo is not None and hi>lo:
            t=max(0.0,min(1.0,(v-lo)/(hi-lo)))
            ce.fill=FILL(["C6EFCE","E2EFDA","FFF2CC","FCE4D6","F8CBAD"][min(4,int(t*5))])
r=4
tvax=[0.15,0.20,0.25,0.30,0.35]; cycax=[1.00,1.25,1.50,1.75,2.00]; addax=[0.06,0.09,0.12,0.15,0.18]
sec(ws,r,"T1 — PPA TARIFF (Rs/kWh)  |  Cycles/day × 5-yr gross TV %",9); r+=1
hdr(ws,r,2,"Cycles ↓ / TV % →")
for j,tv in enumerate(tvax): hdr(ws,r,3+j,tv,P1)
r+=1
t1={ (cy,tv): solve_price("ppa",dict(BASE,cycles_day=cy,tv5=tv),2.0,60.0) for cy in cycax for tv in tvax }
lo,hi=min(t1.values()),max(t1.values())
for cy in cycax:
    lbl(ws,r,2,f"{cy:.2f} cyc/day",b=(cy==1.0))
    for j,tv in enumerate(tvax):
        heat(ws,r,3+j,round(t1[(cy,tv)],2),R2,base=(cy==1.0 and abs(tv-0.25)<1e-9),lo=lo,hi=hi)
    r+=1
r+=1
sec(ws,r,"T2 — LEASE RENTAL (Rs L/month)  |  Capex adder × 5-yr gross TV %",9); r+=1
hdr(ws,r,2,"Adder ↓ / TV % →")
for j,tv in enumerate(tvax): hdr(ws,r,3+j,tv,P1)
r+=1
t2={ (ad,tv): solve_price("lease",dict(BASE,capex_adder=ad,tv5=tv),0.3,8.0) for ad in addax for tv in tvax }
lo,hi=min(t2.values()),max(t2.values())
for ad in addax:
    lbl(ws,r,2,f"+{ad:.0%} capex adder",b=(abs(ad-0.12)<1e-9))
    for j,tv in enumerate(tvax):
        heat(ws,r,3+j,round(t2[(ad,tv)],3),NL,base=(abs(ad-0.12)<1e-9 and abs(tv-0.25)<1e-9),lo=lo,hi=hi)
    r+=1
r+=1
sec(ws,r,"T3 — DEPRECIATION & INTEREST SCENARIOS (static)",9); r+=1
hdr(ws,r,2,"Scenario"); hdr(ws,r,3,"Lease Rs L/mo"); hdr(ws,r,4,"PPA Rs/kWh"); r+=1
for nm,pp in [("Base (15% WDV, 10.5%)",dict(BASE)),
              ("Dep 40% WDV (if solar-integrated, CA sign-off)",dict(BASE,dep_rate=0.40)),
              ("Interest 12.0% (BESS premium pricing)",dict(BASE,int_rate=0.12)),
              ("Interest 9.5% (priority-sector style)",dict(BASE,int_rate=0.095))]:
    lbl(ws,r,2,nm)
    val(ws,r,3,round(solve_price("lease",pp,0.3,8.0),3),NL,"static")
    val(ws,r,4,round(solve_price("ppa",pp,2.0,60.0),2),R2,"static")
    r+=1
note(ws,r,2,"Interest sensitivity matters — BESS has no established priority-sector track; lock the rate before quoting the customer.",9)

# ══ NEGOTIATION POINTS (static) ═══════════════════════════════
ws=wb.create_sheet("Negotiation Points"); ws.sheet_view.showGridLines=False
for col,w in {"A":2,"B":18,"C":34,"D":30,"E":40,"F":24}.items(): ws.column_dimensions[col].width=w
title(ws,1,"REbuffr NEGOTIATION POINTS — each ask protects a model input",6)
sub(ws,2,"Benchmarks corrected and verified Jul-2026. Sequence: settle these before quoting the customer — several move the price.",6)
r=4
hdr(ws,r,2,"Clause"); hdr(ws,r,3,"REbuffr position"); hdr(ws,r,4,"Industry benchmark"); hdr(ws,r,5,"Our ask"); hdr(ws,r,6,"Model cell protected")
r+=1
for row in [
    ("Price","₹87.13 L ex-works = ~₹16,700/kWh","₹16,000–21,000/kWh for ~500 kWh integrated C&I","Accept base price; spend negotiation capital on the clauses below","Assumptions C5 (supply)"),
    ("FX / lithium peg","USD/INR 94 + lithium spot, repriced at proposal date; 7-day validity","Fixed INR or ±2.5% ceiling cap","Fixed INR for 30 days, or hard cap ±2.5%; mirror any residual pass-through in customer contract","Supply cost stability"),
    ("RTE guarantee","Not stated anywhere in proposal","85–88% AC-to-AC guaranteed at PCC incl. chiller/aux load","Written ≥86% RTE guarantee with LDs; below 86% our customer's charging cost rises and PPA competitiveness erodes","Assumptions RTE (0.86) — feeds Value Stack charging cost"),
    ("Uptime & restoration","95% uptime; 24h response; 96h full restoration; 15 days/yr breakdown allowance","96–98% uptime; 48h max restoration for C&I","96% uptime, 48h restoration on critical faults, partial-load discharge % defined in writing; LDs pass-through to customer availability commitment","Assumptions availability (0.95) — 1% uptime ≈ 1% revenue on PPA"),
    ("O&M pricing","'1 years ₹3,76,895' (Y1-3); '4 years ₹2,93,141' (Y4-5) — internally inconsistent","2.0–3.5% of capex p.a. all-in","Written confirmation: per-year or lump-sum; itemise what 'spares included' covers (cells vs BMS vs PCS modules)","Assumptions O&M rows — ~₹0.14 L/mo of lease price"),
    ("Y6-10 warranty","₹10,05,054 for 5-yr block; must opt in within 3 months of delivery","Standard extended-warranty windows 6-12 months","Extend opt-in window to 12 months (we may not have chosen tenure by month 3); confirm transferability to asset buyer","TV netting (5-yr) / Y6+ opex (7/10-yr)"),
    ("Payment terms","30/20/30/15/5 with 3% PBG for 1 yr","10% retention or 5-10% PBG until PR test","5% PBG through defect-warranty year 1 + performance ratio acceptance test at commissioning","Capex phasing / construction risk"),
    ("Delivery","1-6 weeks from PO/advance/drawings — unusually fast","8-16 weeks typical for containerised imports","Reconfirm in writing with LDs for delay; back-to-back our customer COD commitment","Project timeline"),
    ("Site readiness penalty","₹7,500/engineer/day if site not ready","Standard","Fine — but define 'site ready' checklist at PO to avoid disputes","Allied capex contingency"),
]:
    for j,cellv in enumerate(row):
        ce=ws.cell(r,2+j,cellv); ce.font=F(j==0,9,"7F3F00" if j==4 else "000000"); ce.border=BDR(); ce.alignment=ALN(w=True)
    ws.row_dimensions[r].height=44
    r+=1

# ══ SUMMARY ═══════════════════════════════════════════════════
ws=wb.create_sheet("Summary",0); ws.sheet_view.showGridLines=False
for col,w in {"A":2,"B":44,"C":17,"D":17,"E":17,"F":48}.items(): ws.column_dimensions[col].width=w
title(ws,1,"PRICING SUMMARY v1.1 — 250 kW / 522 kWh BESS, Sangli  |  18% Post-Tax Equity IRR",6)
sub(ws,2,"Tenure toggle on Assumptions drives all live sheets. Static Python-solved values in purple.",6)
r=4
sec(ws,r,"SOLVED PRICES BY TENURE (static)  — live model currently reflects the Assumptions toggle",6); r+=1
hdr(ws,r,2,"Metric"); hdr(ws,r,3,"5-yr"); hdr(ws,r,4,"7-yr"); hdr(ws,r,5,"10-yr"); hdr(ws,r,6,"Notes"); r+=1
for label,vals,fmt,nt in [
    ("Lease (Rs L/month)",[S5["lease"],S7["lease"],S10["lease"]],NL,"Flat, full-service, + GST"),
    ("PPA (Rs/kWh @ 1 cyc/day)",[S5["ppa"],S7["ppa"],S10["ppa"]],R2,"+ GST; take-or-pay ≥90% of cycles"),
    ("Min DSCR (lease)",[S5["ml"]["min_dscr"],S7["ml"]["min_dscr"],S10["ml"]["min_dscr"]],X2,"Debt capped at 7 yrs")]:
    lbl(ws,r,2,label,True)
    for j,v in enumerate(vals): val(ws,r,3+j,v,fmt,"static",True)
    note(ws,r,6,nt); r+=1

sec(ws,r,"LIVE MODEL STATE (follows Assumptions toggle)",6); r+=1
def live(label,f,fmt,nt="",b=False,fill=None):
    global r
    lbl(ws,r,2,label,b); val(ws,r,3,f,fmt,"link",b,fill=fill)
    note(ws,r,6,nt); ws.merge_cells(start_row=r,start_column=4,end_row=r,end_column=5)
    r+=1
live("Tenure selected",f"=Assumptions!C{A['tenure']}",N0,"Master toggle.",True,YEL)
live("Lease IRR (live)",f"='Lease Model'!C{RL['irr']}",P2,"Reads 18.00% when price input matches the tenure's solved price.",True)
live("PPA IRR (live)",f"='PPA Model'!C{RP['irr']}",P2,"",True)
live("Capex (ex-GST)",f"=Assumptions!C{A['capex']}",NL,"₹87.13 L supply + 12% adder.")
live("Equity | Debt",f"=Assumptions!C{A['equity']}",NL,"Debt = capex − equity; see Debt Schedule.")
live("Terminal value (net, per toggle)",f"=Assumptions!C{A['tv']}",NL,"5-yr nets off Y6-10 warranty.")

sec(ws,r,"PRICING CORRIDOR (live — from Value Stack)",6); r+=1
live("Customer ceiling — PPA (Rs/kWh)",f"='Value Stack'!C{V['ceil']}",R2,"Net avoided cost × (1 − min saving).",True,YEL)
live("Our floor — PPA (Rs/kWh)",f"='Value Stack'!C{V['floor']}",R2,"18% IRR price.",True,YEL)
live("Corridor",f"='Value Stack'!C{V['corr']}",R2,"NEGATIVE at 1 cyc/day — corridor opens at 1.5-2 cycles or higher DG share. See Value Stack section E.",True)
live("Deal status",f"='Value Stack'!C{V['stat']}","@","",True)

sec(ws,r,"PHYSICAL FEASIBILITY (live — from Value Stack section F)",6); r+=1
live("Battery large enough for assumed cycles?",f"='Value Stack'!C{V['sizechk']}","@",
     "Required nameplate = daily discharge / (DoD x availability).",True)
live("Is grid top-up economic at this site?",f"='Value Stack'!C{V['gridchk']}","@",
     "If NO, cycles are capped near 1.0/day and the cycles lever does not exist here.",True)
live("One-charging-window rule",f"='Value Stack'!C{V['cycchk']}","@",
     "One sun per day = one charging window unless there is discharge demand within it.",True)
live("PCS rating adequate?",f"='Value Stack'!C{V['pwrchk']}","@",
     "Average basis — peak needs the hourly profile.",True)

sec(ws,r,"RECONCILIATION CHECKS (live)",6); r+=1
def chk(label,f,nt=""):
    global r
    lbl(ws,r,2,label)
    ce=ws.cell(r,3,f); ce.font=F(True); ce.border=BDR(); ce.alignment=ALN("center")
    note(ws,r,6,nt); r+=1
chk("Lease IRR = 18.0% target",f'=IF(ABS(\'Lease Model\'!C{RL["irr"]}-Assumptions!C{A["hurdle"]})<0.0005,"OK","CHECK")',"Fails by design if tenure toggled without pasting matching price.")
chk("PPA IRR = 18.0% target",f'=IF(ABS(\'PPA Model\'!C{RP["irr"]}-Assumptions!C{A["hurdle"]})<0.0005,"OK","CHECK")')
chk("Debt amortised by debt tenure",f'=IF(ABS(SUMPRODUCT((\'Debt Schedule\'!C4:L4<=Assumptions!C{A["debtyrs"]})*\'Debt Schedule\'!C{DS["prin"]}:L{DS["prin"]})-Assumptions!C{A["debt"]})<0.005,"OK","CHECK")')
chk("No cash flows beyond tenure (lease)",f'=IF(ABS(SUMPRODUCT((\'Lease Model\'!D3:M3>Assumptions!C{A["tenure"]})*\'Lease Model\'!D{RL["cf"]}:M{RL["cf"]}))<0.000001,"OK","CHECK")')
chk("No cash flows beyond tenure (PPA)",f'=IF(ABS(SUMPRODUCT((\'PPA Model\'!D3:M3>Assumptions!C{A["tenure"]})*\'PPA Model\'!D{RP["cf"]}:M{RP["cf"]}))<0.000001,"OK","CHECK")')
chk("Charging waterfall balances",f'=IF(ABS(\'Value Stack\'!C{V["sol"]}+\'Value Stack\'!C{V["grid"]}-\'Value Stack\'!C{V["chg"]})<0.001,"OK","CHECK")')

sec(ws,r,"FLAGS — RESOLVE BEFORE QUOTING",6); r+=1
for fl in [
    "1. At 1 cycle/day the deal is UNDERWATER (ceiling ~₹10.6 vs floor ₹20.5). The corridor opens at 1.5-2 cycles with meaningful DG-offset share — engineer the dispatch case with the customer FIRST; it decides whether this deal exists.",
    "2. O&M per-year vs lump-sum ambiguity unresolved (Negotiation #5) — worth ~₹0.14 L/mo.",
    "3. Depreciation at 15% WDV; 40% needs CA sign-off on solar-integration capitalisation (worth ~₹0.14 L/mo — Sensitivity T3).",
    "4. No RTE guarantee and 96h restoration in REbuffr terms — both erode the value stack; see Negotiation Points before PO.",
    "5. Capex adder 12% is still an estimate; get civil/HT/freight quotes (Sensitivity T2 spans 6-18%).",
    "6. TV parameters (25/15/7.5%) are judgement calls, editable on Assumptions — underwrite via customer buyout/renewal clause.",
    "7. MSEDCL ToD inputs set per MERC MYT order FY26-30 structure (off-peak = solar hours 9-17h, peak 17-24h +25%); VERIFY the customer's category and base energy charge from their actual bill.",
    "8. If tenure is toggled, paste the matching solved price from Scenario Comparison into Assumptions H — the IRR check will confirm.",
    "9. For discussion — requires professional review (tax, legal, lender, Ind AS 116 lease classification) before commitment.",
]:
    ce=ws.cell(r,2,fl); ce.font=F(False,9,"7F3F00"); ce.alignment=ALN(w=True); ce.border=BDR()
    ws.merge_cells(start_row=r,start_column=2,end_row=r,end_column=6)
    ws.row_dimensions[r].height=30
    r+=1

wb.save(OUT)
print(f"saved {OUT}")
for T in (5,7,10):
    print(f"T={T}: lease {SOLVED[T]['lease']} | ppa {SOLVED[T]['ppa']}")
