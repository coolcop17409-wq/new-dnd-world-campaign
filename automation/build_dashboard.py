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
 m=re.search(r"CAMPAIGN_STATE\\s*[—–-]\\s*DAY\\s+(\\d+)",p.read_text(encoding="utf-8")[:2000],re.I) if p.exists() else None
 return int(m.group(1)) if m else None
def character(group, name, sheet):
 rows=table(CSV/group/sheet)
 fields={}
 for r in rows[:8]:
  for i in range(0,len(r)-1,2):
   if r[i].strip() and r[i+1].strip():
    fields[r[i].strip().lower()]=r[i+1].strip()
 resource_rows=[]
 for i,r in enumerate(rows):
  if r and r[0].strip().upper()=="RESOURCE":
   for item in rows[i+1:]:
    if not item or not item[0].strip(): break
    if item[0].strip().upper() in {"ABILITY","SKILL","FEATURE"}: break
    resource_rows.append({"name":item[0].strip(),"current":item[1].strip() if len(item)>1 else "","max":item[2].strip() if len(item)>2 else "","recovery":item[3].strip() if len(item)>3 else ""})
   break
 return {"name":name,"level":fields.get("level"),"hp":fields.get("current hp"),"max_hp":fields.get("max hp"),"ac":fields.get("ac"),"initiative":fields.get("initiative"),"speed":fields.get("speed"),"resources":resource_rows}
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
  if q in {"","0","0.0"}:continue
  out.append({"item":r[item].strip(),"qty":q,"holder":r[holder].strip() if holder is not None and holder<len(r) else "","detail":r[detail].strip()[:180] if detail is not None and detail<len(r) else ""})
 return out
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
 payload={
  "generated_from":"staging snapshots; Drive remains authoritative",
  "campaign_day":campaign_day(),
  "estate_status":estate.get("status"),
  "estates":estate.get("estates",{}),
  "party":[character("v","Valenthia","v-character.csv"),character("cirren","Cirren","cirren-character.csv"),character("fenar","Fenar","fenar-character.csv")],
  "inventory":{"Valenthia":inventory("v","v-inventory.csv"),"Cirren":inventory("cirren","cirren-inventory.csv"),"Fenar":inventory("fenar","fenar-inventory.csv")},
  "magic_shop_lots":shops()
 }
 OUT.parent.mkdir(parents=True,exist_ok=True)
 OUT.write_text(json.dumps(payload,ensure_ascii=False,indent=2)+"\\n",encoding="utf-8")
 print(f"Built {OUT}")
if __name__=="__main__":main()
