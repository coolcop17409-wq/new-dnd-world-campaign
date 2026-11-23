"""Build immutable play-sync requests exclusively from a pinned recovery journal."""
import argparse
import copy
import json
import re
from pathlib import Path
from automation.play_handoff import validate
from automation.recovery_journal import check, digest

PATH = 'automation/recovery/active.json'


def reconcile_supersessions(requests, supersessions, replacement=None):
    """Exclude only explicitly retired transports bound to exact immutable payloads.

    Callers must independently verify main receipts and absence of partial owner
    application. This offline check cannot certify remote publication.
    """
    by_id = {r['request_id']: r for r in requests}
    if len(by_id) != len(requests):
        raise ValueError('duplicate prior request ID')
    if replacement is not None:
        if replacement['request_id'] in by_id:
            raise ValueError('replacement already in prior requests')
        by_id[replacement['request_id']] = replacement
    retired = set()
    for receipt in supersessions or []:
        old_id, new_id = receipt.get('request_id'), receipt.get('superseded_by')
        if old_id in retired or old_id == new_id or old_id not in by_id or new_id not in by_id:
            raise ValueError('invalid supersession endpoints')
        old, new = by_id[old_id], by_id[new_id]
        if (validate(old) or validate(new) or old.get('mode') != 'accepted_play'
                or new.get('mode') != 'accepted_play'):
            raise ValueError('invalid supersession request')
        if (receipt.get('status') != 'superseded'
                or receipt.get('request_digest') != digest(old)
                or receipt.get('replacement_digest') != digest(new)
                or receipt.get('owners_unapplied_verified') is not True
                or receipt.get('applied_event_ids') != []
                or not re.fullmatch('[0-9a-f]{40}', str(receipt.get('verified_base_commit', '')))):
            raise ValueError('unverified supersession binding')
        new_events = {e['event_id']: e for e in new['events']}
        if any(new_events.get(e['event_id']) != e for e in old['events']):
            raise ValueError('replacement changes or omits retired events')
        retired.add(old_id)
    if any(r.get('superseded_by') in retired for r in supersessions or []):
        raise ValueError('chained or cyclic supersession needs reconciliation')
    if replacement is not None and replacement['request_id'] in retired:
        raise ValueError('retired request cannot be applied')
    return [r for r in requests if r['request_id'] not in retired]


def build(journal, request_id, journal_commit, prior_requests, supersessions=None):
    check(journal)
    if not re.fullmatch('[0-9a-f]{40}', journal_commit):
        raise ValueError('journal commit must be an exact SHA')
    if not isinstance(prior_requests, list):
        raise ValueError('prior requests must be a complete reconciled list')
    prior_requests = reconcile_supersessions(prior_requests, supersessions)
    # A verified, completed batch can already have had its original recovery
    # entries pruned from active.json. Keep an exact manifest-ID -> batch owner
    # mapping rather than requiring those old entries to be present again.
    posted, prior_ids, historical_recoveries = {}, set(), {}
    for prior in prior_requests:
        if validate(prior) or prior.get('mode') != 'accepted_play':
            raise ValueError('invalid prior accepted-play request')
        rid = prior['request_id']
        if rid == request_id:
            raise ValueError('request ID already exists; reuse immutable transport')
        if rid in prior_ids:
            raise ValueError('duplicate prior request ID')
        prior_ids.add(rid)
        manifest = prior.get('recovery_entries')
        if not isinstance(manifest, dict) or not manifest:
            raise ValueError('prior batch missing pinned recovery manifest')
        for recovery_id, pinned_digest in manifest.items():
            if (not isinstance(recovery_id, str)
                    or not re.fullmatch(r'PLAY-REC-[A-Za-z0-9_-]+', recovery_id)
                    or not isinstance(pinned_digest, str)
                    or not re.fullmatch(r'[0-9a-f]{64}', pinned_digest)):
                raise ValueError('invalid historical recovery manifest identity')
            if recovery_id in historical_recoveries:
                raise ValueError('recovery ID assigned to multiple prior batches')
            historical_recoveries[recovery_id] = rid
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
            elif dep in historical_recoveries:
                # The original recovery ID may no longer be in active.json
                # because a prior accepted batch was verified and pruned.
                dependencies.add(historical_recoveries[dep])
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


def verify(journal, request, prior_requests, supersessions=None):
    source = request.get('journal_source', {})
    if source.get('path') != PATH or source.get('digest') != digest(journal):
        raise ValueError('pinned journal snapshot mismatch')
    prior_requests = reconcile_supersessions(prior_requests, supersessions, request)
    rebuilt = build(journal, request['request_id'], source.get('commit', ''), prior_requests)
    if rebuilt != request:
        raise ValueError('request differs from journal-derived batch')
    return True


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('operation', choices=['build','verify'])
    p.add_argument('journal')
    p.add_argument('--prior-requests', required=True)
    p.add_argument('--supersessions', help='Verified main supersession receipts; never edit immutable requests')
    p.add_argument('--request-id')
    p.add_argument('--journal-commit')
    p.add_argument('--request')
    a = p.parse_args()
    read = lambda path: json.loads(Path(path).read_text())
    try:
        journal, prior = read(a.journal), read(a.prior_requests)
        if a.operation == 'build':
            if not a.request_id or not a.journal_commit: p.error('request ID and journal commit required')
            result = build(journal, a.request_id, a.journal_commit, prior, read(a.supersessions) if a.supersessions else None)
        else:
            if not a.request: p.error('--request required')
            verify(journal, read(a.request), prior, read(a.supersessions) if a.supersessions else None)
            result = {'status': 'PASS'}
        print(json.dumps(result, indent=2, ensure_ascii=False))
    except (ValueError, KeyError, TypeError) as exc:
        p.exit(1, str(exc) + '\n')


if __name__ == '__main__':
    main()
