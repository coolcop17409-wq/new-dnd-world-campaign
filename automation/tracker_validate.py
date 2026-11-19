#!/usr/bin/env python3
"""Validate staging character, inventory, estate event, and magic-shop records."""
from __future__ import annotations
import csv,json
from decimal import Decimal,InvalidOperation
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
CSV=ROOT/"trackers"/"csv"
REPORT=ROOT/"reports"/"tracker-validation.json"
CHARACTERS={"Valenthia":("v","v-character.csv","v-inventory.csv"),"Cirren":("cirren","cirren-character.csv","cirren-inventory.csv"),"Fenar":("fenar","fenar-character.csv","fenar-inventory.csv")}
def rows(path):
 with path.open(encoding="utf-8-sig",newline="") as f:return list(csv.reader(f))
def num(v,context,findings):
 try:return Decimal(str(v).strip().replace(",",""))
 except (InvalidOperation,ValueError):
  findings.append(f"{context}: expected a numeric value, got {v!r}")
  return None
def character_check(name,group,sheet,inventory,findings):
 data=rows(CSV/group/sheet)
 values={}
 for row in data[:8]:
  for i in range(0,len(row)-1,2):
   if row[i].strip() and row[i+1].strip(): values[row[i].strip().lower()]=row[i+1].strip()
 hp=num(values.get("current hp",""),f"{name} current HP",findings)
 max_hp=num(values.get("max hp",""),f"{name} maximum HP",findings)
 if hp is not None and max_hp is not None and (hp<0 or hp>max_hp):findings.append(f"{name}: HP {hp} is outside 0–{max_hp}.")
 resources={}
 for i,row in enumerate(data):
  if row and row[0].strip().upper()=="RESOURCE":
   for item in data[i+1:]:
    if not item or not item[0].strip():break
    key=item[0].strip()
    if key.upper().startswith(("ATTACKS","ABILITY SCORES","FEATURES","SKILLS")):break
    if len(item)<3 or not item[1].strip() or not item[2].strip():continue
    cur=num(item[1],f"{name} resource {key} current",findings)
    maximum=num(item[2],f"{name} resource {key} maximum",findings)
    if cur is not None and maximum is not None and (cur<0 or cur>maximum):findings.append(f"{name}: {key} {cur}/{maximum} is outside its allowed range.")
    if key.lower() in resources:findings.append(f"{name}: duplicate resource row {key}.")
    resources[key.lower()]=True
   break
 items=rows(CSV/group/inventory)
 hi=next((i for i,r in enumerate(items) if r and r[0].strip().upper()=="ITEM"),None)
 if hi is None:
  findings.append(f"{name}: inventory header not found.")
 else:
  qtyi=next((i for i,x in enumerate(items[hi]) if x.strip().lower() in {"qty","quantity"}),None)
  for r in items[hi+1:]:
   if not r:break
   if not r[0].strip() or qtyi is None or qtyi>=len(r):continue
   q=num(r[qtyi],f"{name} inventory {r[0].strip()} quantity",findings)
   if q is not None and q<0:findings.append(f"{name}: {r[0].strip()} has negative quantity {q}.")
def main():
 findings=[]
 for name,(group,char,inventory) in CHARACTERS.items():character_check(name,group,char,inventory,findings)
 # Actual character changes require unique IDs and evidence; unresolved plans cannot post.
 ep=ROOT/"data"/"characters"/"events.csv"
 if ep.exists():
  with ep.open(encoding="utf-8-sig",newline="") as f:events=list(csv.DictReader(f))
  ids=set()
  for e in events:
   if not any(str(v or "").strip() for v in e.values()):continue
   eid=(e.get("event_id") or "").strip()
   if not eid:findings.append("Character event without event_id.");continue
   if eid in ids:findings.append(f"Duplicate character event ID {eid}.")
   ids.add(eid)
   if (e.get("status") or "").strip().lower()!="posted":findings.append(f"{eid}: only posted actual changes can affect character state.")
   if not (e.get("evidence") or "").strip():findings.append(f"{eid}: missing evidence/source.")
   if not (e.get("campaign_day") or "").strip():findings.append(f"{eid}: missing campaign day.")
   if (e.get("delta") or "").strip() and (e.get("absolute_value") or "").strip():findings.append(f"{eid}: use either delta or absolute_value, not both.")
 # Existing magic-shop CSVs are state tables plus an event log; validate identity and quantity only.
 shops=CSV/"magic-shops"
 def unique_keys(filename,header_key_names,label):
  data=rows(shops/filename)
  h=[x.strip().lower() for x in data[0]]
  indexes=[h.index(x) for x in header_key_names]
  seen=set()
  for row in data[1:]:
   if not row or not row[0].strip():continue
   key=tuple(row[i].strip() if i<len(row) else "" for i in indexes)
   if key in seen:findings.append(f"Magic Shops {label}: duplicate key {key}.")
   seen.add(key)
 unique_keys("dealers.csv",["settlement","dealer"],"dealer")
 unique_keys("stock.csv",["settlement","dealer","lot"],"stock lot")
 unique_keys("events.csv",["event id"],"event ID")
 stock=rows(shops/"stock.csv")
 sh=[x.strip().lower() for x in stock[0]]
 qi=sh.index("units on hand")
 for row in stock[1:]:
  if not row or not row[0].strip():continue
  q=num(row[qi],f"Magic Shops {row[0]} / {row[2]} quantity",findings)
  if q is not None and q<0:findings.append(f"Magic Shops {row[0]} / {row[2]} has negative stock.")
 result={"status":"PASS" if not findings else "CHECK","findings":findings,"characters_checked":list(CHARACTERS),"shop_lots_checked":len(stock)-1,"character_events_checked":len(ids) if ep.exists() else 0}
 REPORT.parent.mkdir(parents=True,exist_ok=True);REPORT.write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
 print(json.dumps(result,indent=2))
 return 1 if findings else 0
if __name__=="__main__":raise SystemExit(main())
