"""Build immutable play-sync requests exclusively from a pinned recovery journal."""
import argparse
import copy
import json
import re
from pathlib import Path
from automation.play_handoff import validate
from automation.recovery_journal import check, digest

PATH = 'automation/recovery/active.json'


def build(journal, request_id, journal_commit, prior_requests):
    check(journal)
    if not re.fullmatch('[0-9a-f]{40}', journal_commit):
        raise ValueError('journal commit must be an exact SHA')
    if not isinstance(prior_requests, list):
        raise ValueError('prior requests must be a complete reconciled list')
    posted, prior_ids = {}, set()
    for prior in prior_requests:
        if validate(prior) or prior.get('mode') != 'accepted_play':
            raise ValueError('invalid prior accepted-play request')
        rid = prior['request_id']
        if rid == request_id:
            raise ValueError('request ID already exists; reuse immutable transport')
        if rid in prior_ids:
            raise ValueError('duplicate prior request ID')
        prior_ids.add(rid)
        for event in prior['events']:
            eid = event['event_id']
            if eid in posted:
                raise ValueError('event assigned to multiple prior batches')
            posted[eid] = (event, rid)
    for before, after in zip(journal["entries"], journal["entries"][1:]):
        if before["destination_checkpoint"] != after["source_checkpoint"]:
            raise ValueError("journal checkpoint chain has a gap")
    selected, dependencies, mapped = [], set(), {}
    for entry in journal['entries']:
        overlaps = [e for e in entry['events'] if e['event_id'] in posted]
        if overlaps:
            if len(overlaps) != len(entry['events']):
                raise ValueError('partially queued entry requires reconciliation')
            owners = set()
            for event in overlaps:
                old, rid = posted[event['event_id']]
                if old != event:
                    raise ValueError('conflicting recorded event ID')
                owners.add(rid)
            if len(owners) != 1:
                raise ValueError('entry split across prior batches')
            if selected:
                raise ValueError('queued entries after unqueued entries; reconcile order')
            rid = owners.pop()
            mapped[entry['request_id']] = rid
            dependencies.add(rid)
        else:
            selected.append(entry)
    if not selected:
        raise ValueError('no unqueued entries; do not create a transport')
    selected_ids = {e['request_id'] for e in selected}
    seen = set()
    for i, entry in enumerate(selected):
        if i and entry['source_checkpoint'] != selected[i-1]['destination_checkpoint']:
            raise ValueError('checkpoint gap; do not infer missing play')
        for dep in entry['depends_on']:
            if dep in selected_ids:
                if dep not in seen:
                    raise ValueError('forward or cyclic recovery dependency')
            elif dep in mapped:
                dependencies.add(mapped[dep])
            elif dep in prior_ids:
                dependencies.add(dep)
            else:
                raise ValueError('unresolved dependency: ' + dep)
        seen.add(entry['request_id'])
    result = dict(schema_version=1, request_id=request_id, mode='accepted_play',
        base_commit=selected[0]['base_commit'],
        source_checkpoint=selected[0]['source_checkpoint'],
        destination_checkpoint=selected[-1]['destination_checkpoint'],
        source_evidence='\n\n'.join(e['request_id'] + '\n' + e['source_evidence'] for e in selected),
        pending_action=selected[-1]['pending_action'], depends_on=sorted(dependencies),
        events=copy.deepcopy([event for e in selected for event in e['events']]),
        recovery_entries={e['request_id']: digest(e) for e in selected},
        journal_source=dict(commit=journal_commit, path=PATH, digest=digest(journal)),
        prior_request_ids=sorted(prior_ids))
    errors = validate(result)
    if errors:
        raise ValueError(str(errors))
    return result


def verify(journal, request, prior_requests):
    source = request.get('journal_source', {})
    if source.get('path') != PATH or source.get('digest') != digest(journal):
        raise ValueError('pinned journal snapshot mismatch')
    rebuilt = build(journal, request['request_id'], source.get('commit', ''), prior_requests)
    if rebuilt != request:
        raise ValueError('request differs from journal-derived batch')
    return True


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('operation', choices=['build','verify'])
    p.add_argument('journal')
    p.add_argument('--prior-requests', required=True)
    p.add_argument('--request-id')
    p.add_argument('--journal-commit')
    p.add_argument('--request')
    a = p.parse_args()
    read = lambda path: json.loads(Path(path).read_text())
    try:
        journal, prior = read(a.journal), read(a.prior_requests)
        if a.operation == 'build':
            if not a.request_id or not a.journal_commit: p.error('request ID and journal commit required')
            result = build(journal, a.request_id, a.journal_commit, prior)
        else:
            if not a.request: p.error('--request required')
            verify(journal, read(a.request), prior)
            result = {'status': 'PASS'}
        print(json.dumps(result, indent=2, ensure_ascii=False))
    except (ValueError, KeyError, TypeError) as exc:
        p.exit(1, str(exc) + '\n')


if __name__ == '__main__':
    main()
