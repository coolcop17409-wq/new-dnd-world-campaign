"""Validate immutable accepted-play envelopes. Never adjudicates or writes owners."""
import json
import re
import sys
from pathlib import PurePosixPath

PREFIXES = ('campaign/continuity/', 'data/characters/', 'data/estate/',
            'trackers/csv/', 'world/politics/', 'prep/dm-only/')

def validate(batch):
    errors = []
    if not isinstance(batch, dict):
        return ['batch must be an object']
    rid = batch.get('request_id', '')
    if not isinstance(rid, str) or not re.fullmatch(r'PLAY-[A-Z0-9-]+', rid):
        errors.append('invalid stable request_id')
    if batch.get('schema_version') != 1 or batch.get('mode') not in ('accepted_play', 'smoke_test'):
        errors.append('unsupported schema or mode')
    for field in ('base_commit', 'source_checkpoint', 'destination_checkpoint', 'source_evidence', 'pending_action'):
        if not isinstance(batch.get(field), str) or not batch[field].strip():
            errors.append('missing ' + field)
    if not re.fullmatch('[0-9a-f]{40}', str(batch.get('base_commit', ''))):
        errors.append('base_commit must be exact SHA')
    deps = batch.get('depends_on')
    if not isinstance(deps, list) or any(not isinstance(x, str) or not re.fullmatch(r'PLAY-[A-Z0-9-]+', x) or x == rid for x in deps):
        errors.append('invalid dependencies')
    events = batch.get('events')
    if not isinstance(events, list):
        return errors + ['events must be a list']
    if batch.get('mode') == 'smoke_test':
        if events or batch.get('source_checkpoint') != batch.get('destination_checkpoint'):
            errors.append('smoke test must have no events or checkpoint change')
    elif not events:
        errors.append('accepted_play requires events')
    seen = set()
    for event in events:
        if not isinstance(event, dict):
            errors.append('event must be object'); continue
        eid = event.get('event_id')
        if not isinstance(eid, str) or not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_.:/-]*', eid):
            errors.append('invalid event ID')
        elif eid in seen:
            errors.append('duplicate event ID')
        else:
            seen.add(eid)
        if event.get('accepted') is not True:
            errors.append('unaccepted event')
        for field in ('evidence', 'before', 'after'):
            if not isinstance(event.get(field), str) or not event[field].strip():
                errors.append('missing exact event ' + field)
        paths = event.get('owner_paths')
        if not isinstance(paths, list) or not paths:
            errors.append('missing owner paths'); continue
        for path in paths:
            if not isinstance(path, str) or '..' in PurePosixPath(path).parts or not path.startswith(PREFIXES) or '\\' in path:
                errors.append('invalid owner path')
    return errors

if __name__ == '__main__':
    with open(sys.argv[1], encoding='utf-8') as f:
        errors = validate(json.load(f))
    print(json.dumps({'status': 'FAIL' if errors else 'PASS', 'findings': errors}))
    sys.exit(bool(errors))
