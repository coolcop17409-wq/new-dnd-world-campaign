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
def quantity_value(d):return d.quantize(Decimal("0.0001"),rounding=ROUND_HALF_UP)
def prerequisite_tasks():
 tasks={}
 for path in PROPERTY.glob("*-schedule.csv"):
  with path.open(encoding="utf-8-sig",newline="") as f:
   grid=list(csv.reader(f))
  hi=next((i for i,row in enumerate(grid) if row and norm(row[0]) in {"task id","task / settlement id"}),None)
  if hi is None:continue
  header=[norm(x) for x in grid[hi]]
  id_col=next((i for i,x in enumerate(header) if x in {"task id","task / settlement id"}),None)
  day_col=next((i for i,x in enumerate(header) if x=="actual day"),None)
  result_col=next((i for i,x in enumerate(header) if x=="result"),None)
  evidence_col=next((i for i,x in enumerate(header) if x in {"actual evidence","evidence / restriction","evidence / dependency"}),None)
  if None in (id_col,day_col,result_col):continue
  for row in grid[hi+1:]:
   if len(row)<=max(id_col,day_col,result_col):continue
   tid=row[id_col].strip()
   if not tid:continue
   tasks[tid]={"actual_day":row[day_col].strip(),"result":row[result_col].strip().lower(),
               "evidence":row[evidence_col].strip() if evidence_col is not None and len(row)>evidence_col else "",
               "source":path.name}
 # Live task outcomes overlay the immutable migrated schedule references.
 live_path=DATA/"operational-checkpoint.csv"
 if live_path.exists():
  for row in rows(live_path):
   if row.get("record_type")=="Prerequisite":
    tasks[row["record_id"]]={"actual_day":row.get("day", ""),"result":row.get("status", "").lower(),
                             "evidence":row.get("source_and_limits", ""),"source":str(live_path)}
 return tasks

def order_ledger_events(events):
 """Keep legacy order except explicit same-day dependencies, including prior tax adjustments.

 reference_id names a real event, never an instruction to bypass a balance check.
 This permits newly produced stock to be reserved and reconciled opening advances
 to be earned after their source correction without changing historical rows.
 """
 import heapq
 ordered=sorted(events,key=lambda r:(dec(r.get("effective_day","0")),r.get("event_type")=="retcon_adjustment"))
 by_id={r.get("event_id"):i for i,r in enumerate(ordered)}
 edges=defaultdict(list);degree=[0]*len(ordered)
 for i,r in enumerate(ordered):
  event_type=r.get("event_type","")
  before_tax=event_type=="tax_adjustment_before_event"
  if not before_tax and not event_type.endswith("_after_event"):continue
  anchor=r.get("reference_id","")
  if anchor not in by_id:raise ValueError(f"{r.get('event_id')}: missing posting predecessor {anchor}")
  j=by_id[anchor]
  if dec(ordered[j].get("effective_day","0"))!=dec(r.get("effective_day","0")):
   raise ValueError(f"{r.get('event_id')}: posting predecessor must share actual day")
  if before_tax:
   target=ordered[j]
   if (target.get("event_type")!="tax_adjustment" or not r.get("liability_id")
       or r.get("liability_id")!=target.get("liability_id") or r.get("estate")!=target.get("estate")):
    raise ValueError(f"{r.get('event_id')}: prior tax adjustment requires the same tax account and estate")
   edges[i].append(j);degree[j]+=1
  else:
   edges[j].append(i);degree[i]+=1
 heap=[i for i,n in enumerate(degree) if not n];heapq.heapify(heap);result=[]
 while heap:
  i=heapq.heappop(heap);result.append(ordered[i])
  for j in edges[i]:
   degree[j]-=1
   if not degree[j]:heapq.heappush(heap,j)
 if len(result)!=len(ordered):raise ValueError("cyclic explicit posting predecessors")
 return result

def authorized_retcon(row, manifests):
 """A signed correction must exactly match a resolved, player-authorized manifest."""
 if row.get("event_type") != "retcon_adjustment":return False
 entry=manifests.get(row.get("event_id", ""))
 return entry is not None and dict(row)==entry

def retcon_manifests():
 path=DATA/"operational-checkpoint.csv"
 if not path.exists():return {}
 records=rows(path);by_id={r["record_id"]:r for r in records};out={}
 for r in records:
  if r.get("record_type")!="Retrospective reconciliation" or r.get("status") not in {"Resolved","Verified"}:continue
  payload=json.loads(r["source_and_limits"]);authority=by_id.get(payload.get("authority"),{})
  if authority.get("record_type")!="Retcon authorization" or authority.get("status") not in {"PREPARED","RESOLVED","COMMITTED"}:continue
  for event in payload.get("economic_legs",[]):
   if event.get("reference_id")!=authority.get("record_id") or event.get("estate")!=r.get("estate") or event.get("effective_day")!=r.get("day"):continue
   if event["event_id"] in out:raise ValueError("duplicate manifested retcon leg "+event["event_id"])
   out[event["event_id"]]=event
 return out

def main():
 errors=[]
 retcon_rows=retcon_manifests()
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
 receivable_balance={};receivable_cut={}
 for row in rows(DATA/"opening-receivables.csv"):
  rid=(row.get("receivable_id") or "").strip();estate=(row.get("estate") or "").strip();amount=dec(row.get("opening_amount_gp","0"))
  if not rid:errors.append("opening receivable without a stable receivable ID");continue
  if rid in receivable_balance:errors.append(f"duplicate receivable ID {rid}")
  if estate not in ESTATES:errors.append(f"{rid}: unknown estate {estate}");continue
  if amount<0:errors.append(f"{rid}: negative opening receivable {amount}")
  receivable_balance[rid]={"estate":estate,"balance":amount};receivable_cut[rid]={"estate":estate,"balance":amount}
 inventory_balance={}
 for row in rows(DATA/"opening-inventory.csv"):
  iid=(row.get("inventory_id") or "").strip();estate=(row.get("estate") or "").strip();qty=dec(row.get("opening_quantity","0"))
  if not iid:errors.append("opening inventory without a stable inventory ID");continue
  if iid in inventory_balance:errors.append(f"duplicate opening inventory ID {iid}")
  if estate not in ESTATES:errors.append(f"{iid}: unknown estate {estate}");continue
  if qty<0:errors.append(f"{iid}: negative opening quantity {qty}")
  opening_cost=dec(row.get("opening_cost_gp","0"))
  if opening_cost<0:errors.append(f"{iid}: negative opening inventory cost {opening_cost}")
  reserved=dec(row.get("opening_reserved_quantity","0"));transit_qty=dec(row.get("opening_transit_quantity","0"));transit_cost=dec(row.get("opening_transit_cost_gp","0"))
  verification=(row.get("verification_status") or "unverified").strip().lower()
  if reserved<0 or reserved>qty:errors.append(f"{iid}: reserved quantity must be between zero and on-site book quantity")
  if transit_qty<0 or transit_cost<0:errors.append(f"{iid}: negative in-transit inventory")
  if verification not in {"verified","provisional","unverified"}:errors.append(f"{iid}: invalid verification_status {verification}")
  inventory_balance[iid]={"estate":estate,"quantity":qty,"reserved":reserved,"cost":opening_cost,"transit_quantity":transit_qty,"transit_cost":transit_cost,"verification":verification}
 cash_deltas_cut=defaultdict(Decimal);liability_deltas_cut=defaultdict(Decimal)
 cash_deltas_all=defaultdict(Decimal);liability_deltas_all=defaultdict(Decimal)
 receivable_deltas_cut=defaultdict(Decimal);receivable_deltas_all=defaultdict(Decimal)
 inventory_deltas_cut=defaultdict(Decimal);inventory_deltas_all=defaultdict(Decimal)
 inventory_reservations=defaultdict(Decimal);inventory_transit=defaultdict(Decimal)
 income_all=defaultdict(Decimal);expense_all=defaultdict(Decimal)
 ids=set();transfer_totals=defaultdict(Decimal);transfer_counts=defaultdict(int);parsed=0
 blocked={"forecast","planned","scheduled","pending","unconfirmed","estimate"}
 prerequisites=prerequisite_tasks()
 ledger_event_rows=rows(DATA/"events.csv")
 operation_report_path=ROOT/"reports"/"blackthorn-operations.json"
 if operation_report_path.exists():
  operation_report=json.loads(operation_report_path.read_text(encoding="utf-8"))
  addition_path=DATA/"blackthorn-operations-events.csv"
  with addition_path.open(encoding="utf-8-sig",newline="") as f:
   operation_ids=[(r.get("Event ID") or "").strip() for r in csv.DictReader(f) if (r.get("Event ID") or "").strip()]
  if operation_report.get("status")!="PASS":
   errors.append("Blackthorn operation report is not PASS; its ledger events were not applied")
  elif int(operation_report.get("checkpoint_day",-1))!=int(cutoff):
   errors.append("Blackthorn operation report checkpoint does not match estate ledger snapshot")
  elif operation_report.get("staging_event_ids",[])!=operation_ids:
   errors.append("Blackthorn operation report is stale against the current staged operation journal")
  else:
   ledger_event_rows.extend(operation_report.get("ledger_events",[]))
 # Retrospective net adjustments reconcile after all original/bridged activity on their recording day.
 ledger_event_rows=order_ledger_events(ledger_event_rows)
 for row in ledger_event_rows:
  eid=(row.get("event_id") or "").strip();estate=(row.get("estate") or "").strip()
  if not eid:errors.append("event without an event ID");continue
  if eid in ids:errors.append(f"duplicate event ID {eid}")
  ids.add(eid)
  if estate not in ESTATES:errors.append(f"{eid}: unknown estate {estate}");continue
  day=dec(row.get("effective_day","0"))
  in_snapshot = eid in meta["baseline_event_ids"] if "baseline_event_ids" in meta else day<=cutoff
  status=norm(row.get("status",""))
  cash_delta=dec(row.get("cash_delta_gp","0"))
  liability_delta=dec(row.get("liability_delta_gp","0"))
  income=dec(row.get("income_delta_gp","0"))
  expense=dec(row.get("expense_delta_gp","0"))
  quantity=dec(row.get("quantity_delta","0"))
  accepted=dec(row.get("accepted_quantity","0"))
  receivable_delta=dec(row.get("receivable_delta_gp","0"))
  inventory_cost=dec(row.get("inventory_cost_delta_gp","0"))
  reserved_delta=dec(row.get("reserved_quantity_delta","0"))
  transit_delta=dec(row.get("in_transit_quantity_delta","0"))
  transit_cost_delta=dec(row.get("in_transit_cost_delta_gp","0"))
  verification=(row.get("inventory_verification_status") or "").strip().lower()
  amount=dec(row.get("amount_gp","0"))
  inventory_financial=[quantity,inventory_cost,reserved_delta,transit_delta,transit_cost_delta,accepted]
  financial=[cash_delta,liability_delta,receivable_delta,income,expense,*inventory_financial]
  if status in blocked:
   if any(financial) or amount or verification:errors.append(f"{eid}: {status} event cannot post cash, liability, receivable, profit, inventory, verification, or shipment amounts")
   continue
  if (any(financial) or verification) and not (row.get("evidence") or "").strip():errors.append(f"{eid}: posted changes require evidence")
  if any(inventory_financial) and not (row.get("inventory_id") or "").strip():errors.append(f"{eid}: inventory quantity, reservation, transit, cost, or acceptance change requires inventory_id")
  if verification and (verification not in {"verified","provisional","unverified"} or not (row.get("inventory_id") or "").strip()):errors.append(f"{eid}: inventory verification update needs inventory_id and a supported status")
  if accepted and not ((row.get("shipment_id") or "").strip() or (row.get("reference_id") or "").strip()):errors.append(f"{eid}: accepted quantity requires a shipment_id or reference_id")
  if accepted<0:errors.append(f"{eid}: accepted_quantity cannot be negative")
  if (any(financial) or verification) and day==0:errors.append(f"{eid}: posted changes require an actual campaign day")
  is_retcon=authorized_retcon(row,retcon_rows)
  if (income<0 or expense<0) and not is_retcon:errors.append(f"{eid}: negative income/expense requires an exact authorized retrospective correction")
  if row.get("event_type")=="retcon_adjustment" and not is_retcon:errors.append(f"{eid}: retrospective correction does not match its resolved authorization manifest")
  event_type=norm(row.get("event_type",""))
  requires_gate=income>0 or any(token in event_type for token in ("shipment dispatch","shipment_dispatch","gate sale","gate_sale","service accept","service_accept"))
  if requires_gate:
   refs=[x.strip() for x in (row.get("prerequisite_ref") or "").replace(",", ";").split(";") if x.strip()]
   if not refs:errors.append(f"{eid}: earned income/service release requires prerequisite_ref task IDs")
   for ref in refs:
    gate=prerequisites.get(ref)
    if not gate:errors.append(f"{eid}: prerequisite {ref} is not in a property schedule")
    elif gate["result"] not in {"complete","pass","passed"} or not gate["actual_day"] or dec(gate["actual_day"])<=0 or dec(gate["actual_day"])>day or not gate["evidence"]:
     errors.append(f"{eid}: prerequisite {ref} is not evidenced complete/pass on or before Day {day}")
  if row.get("source_file","").strip() and amount!=0 and not any(financial):
   errors.append(f"{eid}: amount is not connected to a cash, liability, receivable, income, expense, inventory, or acceptance delta")
  cash_all[estate]+=cash_delta;cash_deltas_all[estate]+=cash_delta
  income_all[estate]+=income;expense_all[estate]+=expense
  if receivable_delta:
   rid=(row.get("receivable_id") or "").strip()
   if not rid:errors.append(f"{eid}: receivable change requires a receivable_id")
   else:
    if rid not in receivable_balance:
     if receivable_delta<0:errors.append(f"{eid}: cannot collect unknown receivable {rid}")
     else:receivable_balance[rid]={"estate":estate,"balance":Decimal(0)}
    if rid in receivable_balance:
     if receivable_balance[rid]["estate"]!=estate:errors.append(f"{eid}: receivable {rid} belongs to another estate")
     next_receivable=receivable_balance[rid]["balance"]+receivable_delta
     if next_receivable<0:errors.append(f"{eid}: collection exceeds receivable {rid} by {money(-next_receivable)} gp")
     receivable_balance[rid]["balance"]=next_receivable
    receivable_deltas_all[estate]+=receivable_delta
    if in_snapshot:
     if rid not in receivable_cut and receivable_delta<0:errors.append(f"{eid}: snapshot-cutoff collection exceeds unknown receivable {rid}")
     if rid not in receivable_cut:receivable_cut[rid]={"estate":estate,"balance":Decimal(0)}
     next_cut=receivable_cut[rid]["balance"]+receivable_delta
     if next_cut<0:errors.append(f"{eid}: snapshot-cutoff collection exceeds receivable {rid}")
     receivable_cut[rid]["balance"]=next_cut;receivable_deltas_cut[estate]+=receivable_delta
  iid=(row.get("inventory_id") or "").strip()
  if any(inventory_financial) or verification:
   if iid not in inventory_balance:
    if any(x<0 for x in [quantity,inventory_cost,reserved_delta,transit_delta,transit_cost_delta]):errors.append(f"{eid}: cannot reduce unregistered opening inventory {iid}")
    else:inventory_balance[iid]={"estate":estate,"quantity":Decimal(0),"reserved":Decimal(0),"cost":Decimal(0),"transit_quantity":Decimal(0),"transit_cost":Decimal(0),"verification":"unverified"}
   if iid in inventory_balance:
    stock=inventory_balance[iid]
    if stock["estate"]!=estate:errors.append(f"{eid}: inventory {iid} belongs to another estate")
    if stock["verification"]!="verified" and (quantity<0 or inventory_cost<0 or transit_delta<0 or transit_cost_delta<0):errors.append(f"{eid}: inventory {iid} is {stock['verification']}; verify its physical count before dispatch or release")
    next_qty=stock["quantity"]+quantity;next_cost=stock["cost"]+inventory_cost
    next_reserved=stock["reserved"]+reserved_delta
    next_transit=stock["transit_quantity"]+transit_delta;next_transit_cost=stock["transit_cost"]+transit_cost_delta
    if next_qty<0:errors.append(f"{eid}: inventory change exceeds available {iid} quantity by {money(-next_qty)}")
    if next_cost<0:errors.append(f"{eid}: inventory cost release exceeds recorded cost for {iid} by {money(-next_cost)} gp")
    if next_reserved<0 or next_reserved>next_qty:errors.append(f"{eid}: reservation for {iid} must remain between zero and on-site book quantity")
    if next_transit<0:errors.append(f"{eid}: in-transit quantity for {iid} cannot be negative")
    if next_transit_cost<0:errors.append(f"{eid}: in-transit cost for {iid} cannot be negative")
    stock.update({"quantity":next_qty,"cost":next_cost,"reserved":next_reserved,"transit_quantity":next_transit,"transit_cost":next_transit_cost})
    if verification:stock["verification"]=verification
    inventory_deltas_all[estate]+=quantity;inventory_reservations[estate]+=reserved_delta;inventory_transit[estate]+=transit_delta
    if in_snapshot:inventory_deltas_cut[estate]+=quantity
  if in_snapshot:
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
   if in_snapshot:
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
 for required in retcon_rows:
  if required not in ids:errors.append(f"missing manifested retrospective leg {required}")
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
  receivable_at_cut=sum((x["balance"] for x in receivable_cut.values() if x["estate"]==estate),Decimal(0))
  receivable_latest=sum((x["balance"] for x in receivable_balance.values() if x["estate"]==estate),Decimal(0))
  inventory_rows={k:v for k,v in inventory_balance.items() if v["estate"]==estate and any(v[key] for key in ("quantity","cost","reserved","transit_quantity","transit_cost"))}
  inventory_qty=sum((x["quantity"] for x in inventory_rows.values()),Decimal(0))
  inventory_cost=sum((x["cost"] for x in inventory_rows.values()),Decimal(0))
  inventory_available=sum((max(Decimal(0),x["quantity"]-x["reserved"]) if x["verification"]=="verified" else Decimal(0) for x in inventory_rows.values()),Decimal(0))
  inventory_transit_qty=sum((x["transit_quantity"] for x in inventory_rows.values()),Decimal(0))
  inventory_transit_cost=sum((x["transit_cost"] for x in inventory_rows.values()),Decimal(0))
  snapshot["estates"][estate]={
   "snapshot_cash_gp":str(money(cash_cut[estate])),"snapshot_liabilities_gp":str(money(liab_at_cut)),"snapshot_available_gp":str(available_cut),
   "projected_cash_gp":str(money(cash_all[estate])),"projected_liabilities_gp":str(money(liab_latest)),"projected_available_gp":str(available_latest),
   "cash_gp":str(money(cash_all[estate])),"liabilities_gp":str(money(liab_latest)),"available_gp":str(available_latest),
   "cash_after_snapshot_events_gp":str(money(cash_all[estate]-cash_cut[estate])),
   "snapshot_receivables_gp":str(money(receivable_at_cut)),
   "projected_receivables_gp":str(money(receivable_latest)),
   "receivables_gp":str(money(receivable_latest)),
   "receivable_events_after_snapshot_gp":str(money(receivable_latest-receivable_at_cut)),
   "actual_income_after_snapshot_gp":str(money(income_all[estate])),
   "actual_expense_after_snapshot_gp":str(money(expense_all[estate])),
   "inventory_quantity_delta_after_snapshot":str(quantity_value(inventory_deltas_all[estate]-inventory_deltas_cut[estate])),
   "inventory_reserved_delta_after_snapshot":str(quantity_value(inventory_reservations[estate])),
   "inventory_transit_quantity_delta_after_snapshot":str(quantity_value(inventory_transit[estate])),
   "inventory_book_quantity":str(quantity_value(inventory_qty)),
   "inventory_eligible_to_ship_quantity":str(quantity_value(inventory_available)),
   "inventory_on_site_cost_basis_gp":str(money(inventory_cost)),
   "inventory_in_transit_quantity":str(quantity_value(inventory_transit_qty)),
   "inventory_in_transit_cost_basis_gp":str(money(inventory_transit_cost)),
   "inventory_items":{k:{"book_quantity":str(quantity_value(v["quantity"])),"reserved_quantity":str(quantity_value(v["reserved"])),"unreserved_book_quantity":str(quantity_value(max(Decimal(0),v["quantity"]-v["reserved"]))),"in_transit_quantity":str(quantity_value(v["transit_quantity"])),"on_site_cost_basis_gp":str(money(v["cost"])),"in_transit_cost_basis_gp":str(money(v["transit_cost"])),"verification_status":v["verification"],"eligible_to_ship_quantity":str(quantity_value(max(Decimal(0),v["quantity"]-v["reserved"]) if v["verification"]=="verified" else Decimal(0)))} for k,v in inventory_rows.items()},
  }
  if cash_all[estate]<0:errors.append(f"{estate}: projected cash is negative")
 # A retrospective stock correction must reconcile to the active physical replay,
 # not merely to the superseded imported baseline. This also protects future runs.
 if operation_report_path.exists() and operation_report.get("status")=="PASS" and operation_report.get("superseded_interval"):
  bt=snapshot["estates"].get("Blackthorn",{})
  opening_grade_ids={r.get("item"):r.get("inventory_id") for r in rows(DATA/"opening-inventory.csv") if r.get("estate")=="Blackthorn"}
  for grade,expected in operation_report.get("on_site",{}).items():
   actual=bt.get("inventory_items",{}).get(opening_grade_ids.get(grade),{})
   if quantity_value(dec(actual.get("book_quantity",0)))!=quantity_value(dec(expected["quantity_t"])) or money(dec(actual.get("on_site_cost_basis_gp",0)))!=money(dec(expected["cost_gp"])):
    errors.append(f"Blackthorn {grade}: ledger differs from active retrospective stock replay")
  tq=sum((dec(v["quantity_t"]) for v in operation_report.get("in_transit",{}).values()),Decimal(0))
  tc=sum((dec(v["cost_gp"]) for v in operation_report.get("in_transit",{}).values()),Decimal(0))
  if quantity_value(dec(bt.get("inventory_in_transit_quantity",0)))!=quantity_value(tq) or money(dec(bt.get("inventory_in_transit_cost_basis_gp",0)))!=money(tc):errors.append("Blackthorn in-transit ledger differs from active retrospective replay")
 snapshot["accounting_coverage"]={}
 live_path=DATA/"operational-checkpoint.csv"
 if live_path.exists():
  for row in rows(live_path):
   if row.get("record_type")=="Posting coverage":
    snapshot["accounting_coverage"][row["estate"]]=json.loads(row["source_and_limits"])
 snapshot["income_expense_scope"]="Signed economic entries after imported opening, including any explicit retrospective corrections to earlier days. Resolved retrospective reconciliation manifests own actual service-day timelines; these entry totals are not a fresh tax period."
 snapshot["findings"]=errors
 if errors:snapshot["status"]="CHECK"
 REPORT.parent.mkdir(parents=True,exist_ok=True);REPORT.write_text(json.dumps(snapshot,indent=2)+"\n",encoding="utf-8")
 print(json.dumps(snapshot,indent=2))
 return 1 if errors else 0
if __name__=="__main__":raise SystemExit(main())

