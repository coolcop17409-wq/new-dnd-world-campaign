"""Only an isolated integration test branch supplies this deliberately bad fixture."""
import json, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT))
from automation.sync_validate import read_csv, character_schema, CHAR_HEADER
PATH='automation/handoffs/sync-repair/fixtures/integration-character.csv'
if (ROOT/PATH).exists():
    events, errors=read_csv(ROOT,PATH,CHAR_HEADER)
    for error in character_schema(events):
        error['path']=PATH;errors.append(error)
    report={'schema_version':1,'scope':'synthetic','phase':'owners','status':'FAIL' if errors else 'PASS','findings':errors,'affected_files':[PATH] if errors else [],'notes':['Synthetic format-only fixture; no campaign event.']}
    (ROOT/'reports').mkdir(exist_ok=True);(ROOT/'reports/sync-diagnostic.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2));sys.exit(bool(errors))
print('No integration fixture in this branch; production records unchanged.')
