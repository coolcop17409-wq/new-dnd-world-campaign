#!/usr/bin/env python3
"""Build a read-only dashboard from staging tracker snapshots."""
from __future__ import annotations
import csv, json, re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
CSV=ROOT/"trackers"/"csv"
OUT=ROOT/"dashboard"/"dashboard.json"
def table(path):
 with path.open(encoding="utf-8-sig",newline="") as f: return list(csv.reader(f))
def campaign_day():
 p=ROOT/"campaign"/"continuity"/"campaign-state.md"
 m=re.search(r"CAMPAIGN_STATE\s*[—–-]\s*DAY\s+(\d+)",p.read_text(encoding="utf-8")[:2000],re.I) if p.exists() else None
 return int(m.group(1)) if m else None
def character(group, name, sheet, inventory_sheet):
 rows=table(CSV/group/sheet)
 fields={}
 for r in rows[:8]:
  for i in range(0,len(r)-1,2):
   if r[i].strip() and r[i+1].strip():
    fields[r[i].strip().lower()]=r[i+1].strip()
 if not fields.get("level") and len(rows)>1:
  match=re.search(r"\b(?:Cleric|Barbarian)\s*(\d+)",rows[1][0],re.I)
  if match: fields["level"]=match.group(1)
 resource_rows=[]
 for i,r in enumerate(rows):
  if r and r[0].strip().upper()=="RESOURCE":
   for item in rows[i+1:]:
    if not item or not item[0].strip(): break
    if item[0].strip().upper().startswith(("ATTACKS","ABILITY SCORES","FEATURES","SKILLS")): break
    if item[0].strip().upper() in {"ABILITY","SKILL","FEATURE"}: break
    resource_rows.append({"name":item[0].strip(),"current":item[1].strip() if len(item)>1 else "","max":item[2].strip() if len(item)>2 else "","recovery":item[3].strip() if len(item)>3 else ""})
   break
 inv=table(CSV/group/inventory_sheet)
 purse_row=next((r for r in inv if r and r[0].strip().lower()=="current campaign ledger (in custody)"),None)
 purse_cp=None
 if purse_row and len(purse_row)>=4:
  try:purse_cp=int(purse_row[1])*100+int(purse_row[2])*10+int(purse_row[3])
  except ValueError:pass
 return {"name":name,"level":fields.get("level"),"hp":fields.get("current hp"),"max_hp":fields.get("max hp"),"ac":fields.get("ac"),"initiative":fields.get("initiative"),"speed":fields.get("speed"),"resources":resource_rows,"purse_cp":purse_cp}
def inventory(group,sheet):
 rows=table(CSV/group/sheet)
 header_i=next((i for i,r in enumerate(rows) if r and r[0].strip().upper()=="ITEM"),None)
 if header_i is None:return []
 headers=[x.strip().lower() for x in rows[header_i]]
 def index(*names):
  return next((headers.index(n) for n in names if n in headers),None)
 item=index("item");qty=index("qty","quantity");holder=index("current holder");detail=index("detail / custody")
 out=[]
 for r in rows[header_i+1:]:
  if not r or item is None or item>=len(r) or not r[item].strip():continue
  q=r[qty].strip() if qty is not None and qty<len(r) else ""
  try:numeric_qty=float(q)
  except (TypeError,ValueError):continue
  if numeric_qty<=0:continue
  source_idx=index("source")
  source=r[source_idx].strip().lower() if source_idx is not None and source_idx<len(r) else ""
  detail_text=r[detail].strip() if detail is not None and detail<len(r) else ""
  holder_text=r[holder].strip() if holder is not None and holder<len(r) else ""
  if source in {"gp","sp","cp","currency","tracker"}:continue
  custody=(detail_text+" "+holder_text).lower()
  if any(flag in custody for flag in ("no longer carried","not carried","transferred to","sold to")):continue
  out.append({"item":r[item].strip(),"qty":q,"quantity_display":"Unlimited (not tracked)" if "unlimited" in detail_text.lower() else q,"holder":holder_text,"detail":detail_text[:180]})
 return out
def apply_character_events(payload):
 path=ROOT/"data"/"characters"/"events.csv"
 if not path.exists():return
 with path.open(encoding="utf-8-sig",newline="") as f: events=list(csv.DictReader(f))
 by_name={p["name"].lower():p for p in payload["party"]}
 for event in events:
  if not any((event.get(k,"").strip()) for k in ("event_id","campaign_day","target")):continue
  if event.get("status","").strip().lower()!="posted":raise ValueError(f"Character event {event.get('event_id')} is not posted; proposals do not affect the dashboard.")
  owner=event.get("owner","").strip().lower()
  person=by_name.get(owner)
  if not person:raise ValueError(f"Unknown character event owner: {owner}")
  kind=event.get("record_type","").strip().lower()
  target=event.get("target","").strip()
  if not target:raise ValueError(f"Character event {event.get('event_id')} has no target.")
  delta=event.get("delta","").strip()
  absolute=event.get("absolute_value","").strip()
  if delta and absolute:raise ValueError(f"Character event {event.get('event_id')} supplies both delta and absolute value.")
  if kind=="stat":
   key={"hp":"hp","max hp":"max_hp"}.get(target.lower())
   if not key:raise ValueError(f"Unsupported stat target {target!r}.")
   current=float(person[key] or 0)
   new=float(absolute) if absolute else current+float(delta or 0)
   person[key]=str(new)
  elif kind=="resource":
   matches=[x for x in person["resources"] if x["name"].strip().lower()==target.lower()]
   if len(matches)!=1:raise ValueError(f"Resource event {event.get('event_id')} target is missing or ambiguous: {target}.")
   current=float(matches[0]["current"] or 0)
   matches[0]["current"]=str(float(absolute) if absolute else current+float(delta or 0))
  elif kind=="currency":
   if target.lower()!="purse_cp":raise ValueError(f"Unsupported currency target {target!r}.")
   if person.get("purse_cp") is None:raise ValueError(f"{owner}: personal purse baseline is missing.")
   current=int(person["purse_cp"])
   person["purse_cp"]=int(absolute) if absolute else current+int(delta or 0)
   if person["purse_cp"]<0:raise ValueError(f"Character event {event.get('event_id')} makes the purse negative.")
  elif kind=="inventory":
   items=payload["inventory"].get(person["name"],[])
   matches=[x for x in items if x["item"].strip().lower()==target.lower()]
   if len(matches)!=1:raise ValueError(f"Inventory event {event.get('event_id')} target is missing or ambiguous: {target}.")
   if "unlimited" in matches[0].get("detail","").lower():raise ValueError(f"Inventory event {event.get('event_id')} cannot change a non-counted unlimited item.")
   current=float(matches[0]["qty"] or 0)
   matches[0]["qty"]=str(float(absolute) if absolute else current+float(delta or 0))
   matches[0]["quantity_display"]=matches[0]["qty"]
  else:raise ValueError(f"Unsupported character event type {kind!r}.")
  if kind=="stat" and key=="hp" and float(person["max_hp"] or 0) and float(person[key])>float(person["max_hp"]):raise ValueError(f"Character event {event.get('event_id')} exceeds maximum HP.")
  if kind=="resource":
   maximum=float(matches[0]["max"] or 0)
   if float(matches[0]["current"])<0 or (maximum and float(matches[0]["current"])>maximum):raise ValueError(f"Character event {event.get('event_id')} exceeds the resource range.")
  if kind=="inventory" and float(matches[0]["qty"])<0:raise ValueError(f"Character event {event.get('event_id')} makes inventory quantity negative.")
def shops():
 rows=table(CSV/"magic-shops"/"stock.csv")
 if not rows:return []
 h=[x.strip().lower() for x in rows[0]]
 def ix(*names):return next((h.index(n) for n in names if n in h),None)
 cols={"settlement":ix("settlement"),"dealer":ix("dealer"),"lot":ix("lot"),"qty":ix("units on hand"),"price":ix("gp per unit"),"status":ix("status"),"terms":ix("how ownership can change · dm preparation")}
 out=[]
 for r in rows[1:]:
  if not r or not r[0].strip():continue
  get=lambda k: r[cols[k]].strip() if cols[k] is not None and cols[k]<len(r) else ""
  try:q=float(get("qty") or 0)
  except ValueError:q=0
  if q>0:out.append({"settlement":get("settlement"),"dealer":get("dealer"),"lot":get("lot"),"qty":get("qty"),"price_gp":get("price"),"status":get("status"),"terms":get("terms")[:200]})
 return out
def main():
 estate=json.loads((ROOT/"reports"/"estate-ledger.json").read_text(encoding="utf-8"))
 validation_path=ROOT/"reports"/"tracker-validation.json"
 tracker_status=json.loads(validation_path.read_text(encoding="utf-8")).get("status","MISSING") if validation_path.exists() else "MISSING"
 payload={
  "generated_from":"staging snapshots; Drive remains authoritative",
  "campaign_day":campaign_day(),
  "estate_status":estate.get("status"),
  "tracker_status":tracker_status,
  "estates":estate.get("estates",{}),
  "party":[character("v","Valenthia","v-character.csv","v-inventory.csv"),character("cirren","Cirren","cirren-character.csv","cirren-inventory.csv"),character("fenar","Fenar","fenar-character.csv","fenar-inventory.csv")],
  "inventory":{"Valenthia":inventory("v","v-inventory.csv"),"Cirren":inventory("cirren","cirren-inventory.csv"),"Fenar":inventory("fenar","fenar-inventory.csv")},
  "magic_shop_lots":shops()
 }
 apply_character_events(payload)
 for person in payload["party"]:
  if person.get("purse_cp") is not None:
   gp,rem=divmod(person["purse_cp"],100);sp,cp=divmod(rem,10)
   person["purse"]={"gp":gp,"sp":sp,"cp":cp}
 OUT.parent.mkdir(parents=True,exist_ok=True)
 OUT.write_text(json.dumps(payload,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
 print(f"Built {OUT}")
if __name__=="__main__":main()
