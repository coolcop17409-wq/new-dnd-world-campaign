#!/usr/bin/env python3
"""Reconcile the staging event ledger to the imported Property workbook snapshot."""
from __future__ import annotations
import csv, json, re, sys
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/"data"/"estate"
PROPERTY=ROOT/"trackers"/"csv"/"property"
REPORT=ROOT/"reports"/"estate-ledger.json"
ESTATES={
 "Miregate":{"overview":"miregate-overview.csv","cash":["estate cash"],"available":["available after actual liabilities"],"liabilities":["payroll payable","recurring operations payable","incremental bills payable","rolling tax unpaid","customer advances"]},
 "Reedbed":{"overview":"reedbed-overview.csv","cash":["cash held"],"available":["available after liabilities"],"liabilities":["unpaid operating / capital","rolling tax unpaid","customer advances"]},
 "Old Distributary Fort":{"overview":"old-distributary-fort-overvie.csv","cash":["cash held"],"available":["available after liabilities"],"liabilities":["unpaid operating / capital","rolling tax unpaid","customer advances"]},
 "Blackthorn":{"overview":"blackthorn-overview.csv","cash":["cash gp"],"available":["available after actual liabilities"],"liabilities":["carrow unpaid gp","payroll payable gp","production / upkeep payable gp","incremental bills payable gp","rolling tax unpaid gp","customer advances gp"]},
}
def norm(s): return " ".join(s.strip().lower().replace("—","-").split())
def dec(s):
 s=(s or "").strip().replace(",","").replace("$","").replace("gp","").strip()
 if not s or s in {"-","–","—"}: return Decimal("0")
 if s.startswith("(") and s.endswith(")"): s="-"+s[1:-1]
 try: return Decimal(s)
 except InvalidOperation as e: raise ValueError(f"invalid amount {s!r}") from e
def rows(path):
 with path.open(encoding="utf-8-sig",newline="") as f: return list(csv.DictReader(f))
def label_value(path, aliases):
 with path.open(encoding="utf-8-sig",newline="") as f: data=list(csv.reader(f))
 wanted={norm(a) for a in aliases}
 for row in data:
  for i,cell in enumerate(row):
   if norm(cell) in wanted:
    for val in row[i+1:]:
     if val.strip(): return dec(val)
 raise ValueError(f"{path.name}: missing {aliases}")
def money(d): return d.quantize(Decimal("0.01"),rounding=ROUND_HALF_UP)
def main():
 errors=[]
 opening_rows=rows(DATA/"opening-balances.csv")
 openings={}
 for row in opening_rows:
  estate=row["estate"].strip()
  if estate in openings: errors.append(f"duplicate cash opening for {estate}")
  openings[estate]=dec(row["opening_cash_gp"])
 opening_liabilities=rows(DATA/"opening-liabilities.csv")
 liabilities={}
 liability_ids=set()
 for row in opening_liabilities:
  lid=row["liability_id"].strip()
  estate=row["estate"].strip()
  if not lid: errors.append("opening liability without a stable liability ID"); continue
  if lid in liability_ids: errors.append(f"duplicate liability ID {lid}")
  liability_ids.add(lid)
  if estate not in ESTATES: errors.append(f"{lid}: unknown estate {estate}"); continue
  amount=dec(row["opening_amount_gp"])
  if amount<0: errors.append(f"{lid}: negative opening liability {amount}")
  liabilities[estate]=liabilities.get(estate,Decimal(0))+amount
 events=rows(DATA/"events.csv")
 ids=set(); cash={e:openings.get(e,Decimal(0)) for e in ESTATES}
 deltas={e:Decimal(0) for e in ESTATES}
 liability_delta={e:Decimal(0) for e in ESTATES}
 parsed=[]
 blocked={"forecast","planned","scheduled","pending","unconfirmed","estimate"}
 for row in events:
  eid=row.get("event_id","").strip()
  estate=row.get("estate","").strip()
  if not eid: errors.append("event without an event ID"); continue
  if eid in ids: errors.append(f"duplicate event ID {eid}")
  ids.add(eid)
  if estate not in ESTATES: errors.append(f"{eid}: unknown estate {estate}"); continue
  status=norm(row.get("status",""))
  if status in blocked:
   if dec(row.get("cash_delta_gp","0")) or dec(row.get("liability_delta_gp","0")):
    errors.append(f"{eid}: {status} event cannot post a financial delta")
   continue
  cash_delta=dec(row.get("cash_delta_gp","0"))
  liability=dec(row.get("liability_delta_gp","0"))
  amount=dec(row.get("amount_gp","0"))
  # A cashbook-derived event must retain the exact displayed movement, including the sign.
  if row.get("source_file","").strip() and cash_delta==0 and amount!=0 and norm(row.get("event_type","")) not in {"noncash note"}:
   errors.append(f"{eid}: nonzero amount has zero cash delta; set cash delta explicitly for cash or accrue it as a liability event.")
  cash[estate]+=cash_delta
  deltas[estate]+=cash_delta
  liability_delta[estate]+=liability
  parsed.append((estate,eid,dec(row.get("effective_day","0")),cash_delta,liability))
 result={"status":"PASS","estates":{},"event_count":len(parsed),"event_ids_unique":len(ids)==len(parsed),"findings":[]}
 for estate,cfg in ESTATES.items():
  path=PROPERTY/cfg["overview"]
  summary_cash=label_value(path,cfg["cash"])
  summary_available=label_value(path,cfg["available"])
  expected_liabilities=sum((label_value(path,[a]) for a in cfg["liabilities"]),Decimal(0))
  calculated_liabilities=liabilities.get(estate,Decimal(0))+liability_delta[estate]
  available=money(cash[estate]-calculated_liabilities)
  if money(cash[estate])!=money(summary_cash):
   errors.append(f"{estate}: event ledger cash {money(cash[estate])} does not match overview {money(summary_cash)}")
  if money(calculated_liabilities)!=money(expected_liabilities):
   errors.append(f"{estate}: opening liability ledger {money(calculated_liabilities)} does not match overview {money(expected_liabilities)}")
  if available!=money(summary_available):
   errors.append(f"{estate}: ledger available {available} does not match overview {money(summary_available)}")
  result["estates"][estate]={
   "cash_gp":str(money(cash[estate])),"liabilities_gp":str(money(calculated_liabilities)),
   "available_gp":str(available),"snapshot_cash_gp":str(money(summary_cash)),
   "snapshot_liabilities_gp":str(money(expected_liabilities)),
   "snapshot_available_gp":str(money(summary_available)),
  }
  if money(cash[estate])<0: errors.append(f"{estate}: cash balance is negative")
 result["findings"]=errors
 if errors: result["status"]="CHECK"
 REPORT.parent.mkdir(parents=True,exist_ok=True)
 REPORT.write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
 print(json.dumps(result,indent=2))
 return 1 if errors else 0
if __name__=="__main__": raise SystemExit(main())
