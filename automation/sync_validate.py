#!/usr/bin/env python3
"""Read-only scoped preflight. Diagnostics are administration, never campaign events."""
from __future__ import annotations
import argparse, csv, hashlib, json, re, sys
from decimal import Decimal, InvalidOperation
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from automation import build_dashboard as dashboard, tracker_validate as tracker
from automation.build_play_packet import active_checkpoint, latest_recent_event_id
from automation.handoffs.validate import check as handoff_check
CHAR = 'data/characters/events.csv'
SHOP = 'trackers/csv/magic-shops/events.csv'
CHAR_HEADER = ['event_id','campaign_day','owner','record_type','target','delta','absolute_value','evidence','status']
SHOP_HEADER = ['Event ID','Campaign day','Settlement','Dealer','Lot','Event','Units changed','Hold expiry / delivery day','Terms or note','Quality requested / lots shown','Next check day','Status / outcome']

def finding(code, path, message, event_id=''):
    return dict(code=code, path=path, event_id=event_id, message=message)

def read_csv(root, path, header=None):
    findings=[]; result=[]
    try:
        with (root/path).open(encoding='utf-8-sig',newline='') as f:
            rows=list(csv.reader(f,strict=True))
        if not rows or (header is not None and rows[0]!=header):
            return [],[finding('csv.header',path,'Unexpected CSV header')]
        for number,row in enumerate(rows[1:],2):
            if not row or not any(row): continue
            if len(row)!=len(rows[0]):
                findings.append(finding('csv.width',path,f'Row {number}: expected {len(rows[0])} columns, got {len(row)}',row[0]))
            else: result.append(dict(zip(rows[0],row)))
    except (OSError,csv.Error) as exc:
        findings.append(finding('csv.read',path,str(exc)))
    return result,findings

def character_schema(events):
    errors=[]; seen=set()
    for e in events:
        eid=e['event_id']; issues=[]
        if not eid or not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_./:-]*',eid): issues.append('invalid stable event ID')
        if eid in seen: issues.append('duplicate event ID')
        seen.add(eid)
        if e['owner'] not in tracker.CHARACTERS: issues.append('unknown character owner')
        if not e['campaign_day'].isdigit(): issues.append('campaign day must be a nonnegative integer')
        if e['record_type'] not in {'stat','resource','currency','inventory','inventory_create'}: issues.append('unsupported character record type (shop rows belong in Magic Shops Events)')
        if not e['target'].strip() or not e['evidence'].strip(): issues.append('target and evidence required')
        if e['status']!='posted': issues.append('only accepted posted changes belong in the journal')
        if bool(e['delta'])==bool(e['absolute_value']): issues.append('exactly one delta or absolute_value required')
        for key in ('delta','absolute_value'):
            if e[key]:
                try:
                    n=Decimal(e[key])
                    if not n.is_finite() or n!=n.to_integral_value(): raise InvalidOperation
                except InvalidOperation: issues.append(f'{key} must be a finite integer')
        if e['record_type']=='inventory_create':
            try:
                m=json.loads(e['evidence'])
                if not isinstance(m,dict) or not all(isinstance(m.get(k),str) and m[k].strip() for k in ('source_event','holder','detail')): raise ValueError
            except (ValueError,TypeError): issues.append('inventory_create needs source_event, holder, detail JSON evidence')
        if issues: errors.append(finding('character.schema',CHAR,'; '.join(issues),eid))
    return errors

def characters(root, final=False):
    events, errors=read_csv(root,CHAR,CHAR_HEADER)
    errors+=character_schema(events)
    if errors: return errors
    try:
        with patch.object(dashboard,'ROOT',root),patch.object(dashboard,'CSV',root/'trackers/csv'),patch.object(tracker,'CSV',root/'trackers/csv'):
            issues=[]
            for name,(group,sheet,inv) in tracker.CHARACTERS.items(): tracker.character_check(name,group,sheet,inv,issues)
            errors += [finding('character.baseline','trackers/csv',m) for m in issues]
            payload={'party':[dashboard.character(g,n,c,i) for n,(g,c,i) in tracker.CHARACTERS.items()],
                     'inventory':{n:dashboard.inventory(g,i) for n,(g,c,i) in tracker.CHARACTERS.items()}}
            if final: payload['campaign_day']=dashboard.campaign_day()
            dashboard.apply_character_events(payload)
    except (ValueError,KeyError,TypeError,OSError,IndexError) as exc:
        errors.append(finding('character.overlay',CHAR,str(exc)))
    return errors

def shops(root):
    errors=[]
    for file,keys in [('dealers.csv',['Settlement','Dealer']),('stock.csv',['Settlement','Dealer','Lot']),('events.csv',['Event ID'])]:
        path='trackers/csv/magic-shops/'+file
        records,issues=read_csv(root,path,SHOP_HEADER if file=='events.csv' else None);errors+=issues
        seen=set()
        for e in records:
            key=tuple(e.get(k,'') for k in keys)
            if not all(key) or key in seen: errors.append(finding('shop.identity',path,f'Missing or duplicate key {key}',e.get('Event ID','')))
            seen.add(key)
            qkey='Units on hand' if file=='stock.csv' else 'Units changed' if file=='events.csv' else None
            if qkey:
                try:
                    q=Decimal(e[qkey])
                    if not q.is_finite() or q!=q.to_integral_value() or (file=='stock.csv' and q<0): raise InvalidOperation
                except (InvalidOperation,KeyError): errors.append(finding('shop.quantity',path,f'Invalid {qkey} for {key}',e.get('Event ID','')))
    return errors

def linked_transactions(root, links):
    """Batch metadata describes required legs; owning journals remain sole authorities."""
    cs,errors=read_csv(root,CHAR,CHAR_HEADER); ss,more=read_csv(root,SHOP,SHOP_HEADER);errors+=more
    for link in links:
        try:
            sale=[e for e in ss if e['Event ID']==link['sale_id']]
            debit=[e for e in cs if e['event_id']==link['currency_id']]
            item=[e for e in cs if e['event_id']==link['inventory_id']]
            assert len(sale)==len(debit)==len(item)==1,'each linked leg must exist exactly once'
            sale,debit,item=sale[0],debit[0],item[0]
            assert sale['Event'].upper().startswith('SALE'),'market leg must be a sale'
            assert debit['record_type']=='currency' and debit['target']=='purse_cp','debit belongs in Character Events'
            assert int(debit['delta'])==-int(link['price_cp']) and int(link['price_cp'])>0,'incorrect currency debit'
            assert item['record_type']=='inventory_create' and item['target']==link['item'],'personal inventory creation required'
            assert int(item['absolute_value'])==int(link['quantity'])==-int(sale['Units changed']),'quantities must match'
            assert debit['owner']==item['owner']==link['owner'],'wrong owner'
            assert debit['campaign_day']==item['campaign_day']==sale['Campaign day'],'inconsistent transaction day'
            assert link['sale_id'] in debit['evidence'] and json.loads(item['evidence'])['source_event']==link['sale_id'],'missing cross-leg source evidence'
        except (AssertionError,KeyError,ValueError,TypeError) as exc:
            errors.append(finding('transaction.legs',CHAR,str(exc),link.get('sale_id','unknown')))
    return errors

def checkpoint(root, final):
    path='campaign/continuity/campaign-state.md'
    try:
        _,state=active_checkpoint((root/path).read_text())
        latest=latest_recent_event_id((root/'campaign/continuity/session-log.md').read_text())
        if latest not in state:
            if not final: return [],['Owning session log precedes final checkpoint; generated views held.']
            return [finding('checkpoint.latest',path,f'Newest accepted event {latest} absent from final checkpoint',latest)],[]
        return [],[]
    except (ValueError,OSError) as exc: return [finding('checkpoint.format',path,str(exc))],[]

def validate(root=ROOT, scope='characters', phase='owners', links=None):
    errors=[]; notes=[]
    if scope in ('characters','final'): errors+=characters(root,phase=='final' or scope=='final')
    if scope=='shops': errors+=shops(root)
    if scope in ('checkpoint','final'):
        e,n=checkpoint(root,phase=='final' or scope=='final');errors+=e;notes+=n
    if scope=='handoffs': errors += [finding('handoff.schema','automation/handoffs',m) for m in handoff_check(root/'automation/handoffs')]
    if links: errors+=linked_transactions(root,links)
    paths=sorted({e['path'] for e in errors})
    return dict(schema_version=1,status='FAIL' if errors else 'PENDING_CHECKPOINT' if notes else 'PASS',scope=scope,phase=phase,findings=errors,notes=notes,affected_files=paths,
                source_hashes={p:hashlib.sha256((root/p).read_bytes()).hexdigest() for p in paths if (root/p).is_file()})

def main():
    p=argparse.ArgumentParser();p.add_argument('--root',type=Path,default=ROOT);p.add_argument('--scope',choices=['characters','shops','checkpoint','final','handoffs'],required=True);p.add_argument('--phase',choices=['owners','final'],default='owners');p.add_argument('--links',type=Path);p.add_argument('--report',type=Path,default=Path('reports/sync-diagnostic.json'));a=p.parse_args()
    result=validate(a.root,a.scope,a.phase,json.loads(a.links.read_text()) if a.links else None)
    a.report.parent.mkdir(parents=True,exist_ok=True);a.report.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2));return bool(result['findings'])
if __name__=='__main__':sys.exit(main())
