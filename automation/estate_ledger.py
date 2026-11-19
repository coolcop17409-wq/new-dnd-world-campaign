#!/usr/bin/env python3
"""Reconcile the staging event ledger to its dated Property workbook snapshot."""
from __future__ import annotations
import csv,json
from collections import defaultdict
from decimal import Decimal,InvalidOperation,ROUND_HALF_UP
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/"data"/"estate"
PROPERTY=ROOT/"trackers"/"csv"/"property"
REPORT=ROOT/"reports"/"estate-ledger.json"
ESTATES={
 "Miregate":{"overview":"miregate-overview.csv","cash":["estate cash"],"available":["available after actual liabilities"],"liabilities":["payroll payable","recurring operations payable","incremental bills payable","rolling tax unpaid","customer advances"]},
 "Reedbed":{"overview":"reedbed-overview.csv","cash":["cash held"],"available":["available after liabilities"],"liabilities":["unpaid operating / capital","rolling tax unpaid","customer advances"]},
 "Old Distributary Fort":{"overview":"old-distributary-fort-overview.csv","cash":["cash held"],"available":["available after liabilities"],"liabilities":["unpaid operating / capital","rolling tax unpaid","customer advances"]},
 "Blackthorn":{"overview":"blackthorn-overview.csv","cash":["cash gp"],"available":["available after actual liabilities"],"liabilities":["carrow unpaid gp","payroll payable gp","production / upkeep payable gp","incremental bills payable gp","rolling tax unpaid gp","customer advances gp"]},
}
def norm(s): return " ".join(str(s or "").strip().lower().replace("—","-").split())
def dec(s):
 s=str(s or "").strip().replace(",","").replace("$","").replace("gp","").strip()
 if not s or s in {"-","–","—"}:return Decimal("0")
 if s.startswith("(") and s.endswith(")"):s="-"+s[1:-1]
 try:return Decimal(s)
 except InvalidOperation as e:raise ValueError(f"invalid amount {s!r}") from e
def rows(path):
 with path.open(encoding="utf-8-sig",newline="") as f:return list(csv.DictReader(f))
def label_value(path,aliases,optional=False):
 with path.open(encoding="utf-8-sig",newline="") as f:data=list(csv.reader(f))
 wanted={norm(a) for a in aliases}
 for row in data:
  for i,cell in enumerate(row):
   if norm(cell) in wanted:
    for value in row[i+1:]:
     if value.strip():return dec(value)
 if optional:return Decimal(0)
 raise ValueError(f"{path.name}: missing {aliases}")
def money(d):return d.quantize(Decimal("0.01"),rounding=ROUND_HALF_UP)
def main():
 errors=[]
 meta=json.loads((DATA/"snapshot-meta.json").read_text(encoding="utf-8"))
 cutoff=Decimal(str(meta["snapshot_day"]))
 opening_cash={}
 for row in rows(DATA/"opening-balances.csv"):
  estate=row["estate"].strip()
  if estate in opening_cash:errors.append(f"duplicate cash opening for {estate}")
  opening_cash[estate]=dec(row["opening_cash_gp"])
 cash_all={estate:opening_cash.get(estate,Decimal(0)) for estate in ESTATES}
 cash_cut=dict(cash_all)
 liability_balance={}
 liability_cut={}
 for row in rows(DATA/"opening-liabilities.csv"):
  lid=row["liability_id"].strip();estate=row["estate"].strip();amount=dec(row["opening_amount_gp"])
  if not lid:errors.append("opening liability without a stable liability ID");continue
  if lid in liability_balance:errors.append(f"duplicate liability ID {lid}")
  if estate not in ESTATES:errors.append(f"{lid}: unknown estate {estate}");continue
  if amount<0:errors.append(f"{lid}: negative opening liability {amount}")
  liability_balance[lid]={"estate":estate,"balance":amount}
  liability_cut[lid]={"estate":estate,"balance":amount}
 cash_deltas_cut=defaultdict(Decimal);liability_deltas_cut=defaultdict(Decimal)
 cash_deltas_all=defaultdict(Decimal);liability_deltas_all=defaultdict(Decimal)
 ids=set();transfer_totals=defaultdict(Decimal);transfer_counts=defaultdict(int);parsed=0
 blocked={"forecast","planned","scheduled","pending","unconfirmed","estimate"}
 for row in rows(DATA/"events.csv"):
  eid=(row.get("event_id") or "").strip();estate=(row.get("estate") or "").strip()
  if not eid:errors.append("event without an event ID");continue
  if eid in ids:errors.append(f"duplicate event ID {eid}")
  ids.add(eid)
  if estate not in ESTATES:errors.append(f"{eid}: unknown estate {estate}");continue
  day=dec(row.get("effective_day","0"))
  status=norm(row.get("status",""))
  cash_delta=dec(row.get("cash_delta_gp","0"))
  liability_delta=dec(row.get("liability_delta_gp","0"))
  income=dec(row.get("income_delta_gp","0"))
  expense=dec(row.get("expense_delta_gp","0"))
  quantity=dec(row.get("quantity_delta","0"))
  accepted=dec(row.get("accepted_quantity","0"))
  amount=dec(row.get("amount_gp","0"))
  financial=[cash_delta,liability_delta,income,expense,quantity,accepted]
  if status in blocked:
   if any(financial) or amount:errors.append(f"{eid}: {status} event cannot post cash, liability, profit, inventory, or shipment amounts")
   continue
  if any(financial) and not (row.get("evidence") or "").strip():errors.append(f"{eid}: posted changes require evidence")
  if any(financial) and day==0:errors.append(f"{eid}: posted changes require an actual campaign day")
  if income<0 or expense<0:errors.append(f"{eid}: income and expense deltas must be nonnegative amounts")
  if row.get("source_file","").strip() and amount!=0 and not any(financial):
   errors.append(f"{eid}: amount is not connected to a cash, liability, income, expense, inventory, or acceptance delta")
  cash_all[estate]+=cash_delta;cash_deltas_all[estate]+=cash_delta
  if day<=cutoff:
   cash_cut[estate]+=cash_delta;cash_deltas_cut[estate]+=cash_delta
  lid=(row.get("liability_id") or "").strip()
  if liability_delta:
   if not lid:errors.append(f"{eid}: liability change requires a liability_id")
   else:
    if lid not in liability_balance:
     if liability_delta<0:errors.append(f"{eid}: cannot settle unknown liability {lid}")
     else:liability_balance[lid]={"estate":estate,"balance":Decimal(0)}
    if lid in liability_balance:
     if liability_balance[lid]["estate"]!=estate:errors.append(f"{eid}: liability {lid} belongs to another estate")
     next_amount=liability_balance[lid]["balance"]+liability_delta
     if next_amount<0:errors.append(f"{eid}: settlement exceeds liability {lid} by {money(-next_amount)} gp")
     liability_balance[lid]["balance"]=next_amount
   liability_deltas_all[estate]+=liability_delta
   if day<=cutoff:
    if lid and lid in liability_cut:
     next_cut=liability_cut[lid]["balance"]+liability_delta
     if next_cut<0:errors.append(f"{eid}: snapshot-cutoff settlement exceeds liability {lid}")
     liability_cut[lid]["balance"]=next_cut
    elif lid and liability_delta>0:
     liability_cut[lid]={"estate":estate,"balance":liability_delta}
    liability_deltas_cut[estate]+=liability_delta
  if "transfer" in norm(row.get("event_type","")):
   ref=(row.get("reference_id") or "").strip()
   if not ref:errors.append(f"{eid}: estate transfer needs a shared reference_id")
   else:transfer_totals[ref]+=cash_delta;transfer_counts[ref]+=1
  parsed+=1
 for ref,total in transfer_totals.items():
  if money(total)!=0:errors.append(f"transfer {ref}: paired cash legs net to {money(total)} gp, expected 0")
  if transfer_counts[ref]<2:errors.append(f"transfer {ref}: needs both source and destination cash legs")
 snapshot={"status":"PASS","cutoff_day":int(cutoff),"captured_date":meta.get("captured_date"),"event_count":parsed,"event_ids_unique":len(ids)==parsed,"estates":{},"findings":[]}
 for estate,cfg in ESTATES.items():
  path=PROPERTY/cfg["overview"]
  cash_expected=label_value(path,cfg["cash"])
  available_expected=label_value(path,cfg["available"])
  liabilities_expected=sum((label_value(path,[a],optional=True) for a in cfg["liabilities"]),Decimal(0))
  liab_at_cut=sum((x["balance"] for x in liability_cut.values() if x["estate"]==estate),Decimal(0))
  liab_latest=sum((x["balance"] for x in liability_balance.values() if x["estate"]==estate),Decimal(0))
  available_cut=money(cash_cut[estate]-liab_at_cut)
  available_latest=money(cash_all[estate]-liab_latest)
  if money(cash_cut[estate])!=money(cash_expected):errors.append(f"{estate}: ledger cash through Day {int(cutoff)} {money(cash_cut[estate])} does not match overview {money(cash_expected)}")
  if money(liab_at_cut)!=money(liabilities_expected):errors.append(f"{estate}: ledger liabilities through Day {int(cutoff)} {money(liab_at_cut)} do not match overview {money(liabilities_expected)}")
  if available_cut!=money(available_expected):errors.append(f"{estate}: available through Day {int(cutoff)} {available_cut} does not match overview {money(available_expected)}")
  snapshot["estates"][estate]={
   "snapshot_cash_gp":str(money(cash_cut[estate])),"snapshot_liabilities_gp":str(money(liab_at_cut)),"snapshot_available_gp":str(available_cut),
   "projected_cash_gp":str(money(cash_all[estate])),"projected_liabilities_gp":str(money(liab_latest)),"projected_available_gp":str(available_latest),
   "cash_gp":str(money(cash_all[estate])),"liabilities_gp":str(money(liab_latest)),"available_gp":str(available_latest),
   "cash_after_snapshot_events_gp":str(money(cash_all[estate]-cash_cut[estate])),
  }
  if cash_all[estate]<0:errors.append(f"{estate}: projected cash is negative")
 snapshot["findings"]=errors
 if errors:snapshot["status"]="CHECK"
 REPORT.parent.mkdir(parents=True,exist_ok=True);REPORT.write_text(json.dumps(snapshot,indent=2)+"\n",encoding="utf-8")
 print(json.dumps(snapshot,indent=2))
 return 1 if errors else 0
if __name__=="__main__":raise SystemExit(main())
