"""Pure recovery transforms. GitHub reads, owner verification and CAS belong to caller."""
import argparse
import copy
import hashlib
import json
import re
from pathlib import Path
from automation.play_handoff import validate


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode()).hexdigest()


def check(journal):
    if not isinstance(journal, dict) or journal.get('schema_version') != 1 or not isinstance(journal.get('entries'), list):
        raise ValueError('invalid recovery journal')
    ids, events = set(), set()
    for entry in journal['entries']:
        errors = validate(entry)
        if errors or entry.get('mode') != 'accepted_play':
            raise ValueError('invalid recovery entry: ' + str(errors))
        if entry['request_id'] in ids:
            raise ValueError('duplicate recovery ID')
        ids.add(entry['request_id'])
        for event in entry['events']:
            if event['event_id'] in events:
                raise ValueError('duplicate recovery event ID')
            events.add(event['event_id'])


def append(journal, entry):
    check(journal)
    result = copy.deepcopy(journal)
    for old in result['entries']:
        if old['request_id'] == entry.get('request_id'):
            if old == entry:
                return result
            raise ValueError('conflicting recovery ID; preserve original')
    result['entries'].append(copy.deepcopy(entry))
    check(result)
    return result


def prune(journal, request, receipt):
    """Remove exact fully verified entries only; never trust a list of IDs alone.

    Caller MUST first read the immutable request and central receipt from GitHub,
    verify owner/checkpoint commits and current owning evidence, then CAS output.
    This function checks evidence bindings, not remote truth or gameplay.
    """
    check(journal)
    if validate(request) or request.get('mode') != 'accepted_play':
        raise ValueError('invalid accepted-play request')
    if (receipt.get('status') != 'complete' or receipt.get('request_id') != request['request_id']
            or receipt.get('request_digest') != digest(request)
            or receipt.get('owners_verified') is not True):
        raise ValueError('missing verified complete receipt bound to request')
    for key in ('owner_commit', 'tested_commit'):
        if not re.fullmatch('[0-9a-f]{40}', str(receipt.get(key, ''))):
            raise ValueError('missing ' + key)
    if request['source_checkpoint'] != request['destination_checkpoint']:
        if not re.fullmatch('[0-9a-f]{40}', str(receipt.get('checkpoint_commit', ''))) or receipt.get('checkpoint_verified') is not True:
            raise ValueError('checkpoint not verified')
    tests = receipt.get('tests')
    if not isinstance(tests, list) or not tests or any(not isinstance(t, dict) or not t.get('command') or t.get('exit_code') != 0 for t in tests):
        raise ValueError('missing successful executed tests')
    refs = receipt.get('owner_refs')
    if not isinstance(refs, list) or not refs or any(not isinstance(r, str) or not r.strip() for r in refs):
        raise ValueError('missing owner references')
    manifest = request.get('recovery_entries')
    if not isinstance(manifest, dict) or not manifest or any(not re.fullmatch('[0-9a-f]{64}', str(v)) for v in manifest.values()):
        raise ValueError('missing exact recovery manifest')
    verified = receipt.get('verified_event_ids')
    if not isinstance(verified, list) or any(not isinstance(x, str) for x in verified):
        raise ValueError('missing verified event IDs')
    request_events = {e['event_id']: e for e in request['events']}
    keep = []
    for entry in journal['entries']:
        if entry['request_id'] not in manifest:
            keep.append(entry)
            continue
        if digest(entry) != manifest[entry['request_id']]:
            raise ValueError('recovery content differs from submitted snapshot')
        if any(e['event_id'] not in verified or request_events.get(e['event_id']) != e for e in entry['events']):
            raise ValueError('entry not fully applied and verified')
    return dict(schema_version=1, entries=copy.deepcopy(keep))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('operation', choices=['validate', 'append', 'prune', 'digest'])
    parser.add_argument('journal')
    parser.add_argument('--entry')
    parser.add_argument('--request')
    parser.add_argument('--receipt')
    args = parser.parse_args()
    read = lambda p: json.loads(Path(p).read_text())
    value = read(args.journal)
    try:
        if args.operation == 'digest':
            print(digest(value)); return
        if args.operation == 'validate':
            check(value); result = {'status': 'PASS'}
        elif args.operation == 'append':
            if not args.entry: parser.error('--entry required')
            result = append(value, read(args.entry))
        else:
            if not args.request or not args.receipt: parser.error('--request and --receipt required')
            result = prune(value, read(args.request), read(args.receipt))
        print(json.dumps(result, indent=2, ensure_ascii=False))
    except ValueError as exc:
        parser.exit(1, str(exc) + '\n')


if __name__ == '__main__':
    main()
