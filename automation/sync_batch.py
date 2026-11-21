"""Idempotent journal assembly helpers for prepublication callers (no network writes)."""
import csv, io

def append_once(text, event, header, id_column):
    """Exact retry is a no-op; conflicting stable ID and malformed input fail closed."""
    rows=list(csv.reader(io.StringIO(text),strict=True))
    if not rows or rows[0]!=header or any(len(r)!=len(header) for r in rows[1:]):raise ValueError('Malformed journal; no publication')
    if set(event)!=set(header) or not event[id_column]:raise ValueError('Event must match the owning schema and have a stable ID')
    matches=[dict(zip(header,r)) for r in rows[1:] if r[header.index(id_column)]==event[id_column]]
    if len(matches)>1:raise ValueError('Existing duplicate ID')
    if matches:
        if matches[0]!=event:raise ValueError('Stable ID conflict; preserve existing record and investigate')
        return text
    out=io.StringIO();w=csv.writer(out,lineterminator='\n');w.writerows(rows);w.writerow([event[k] for k in header]);return out.getvalue()

def require_head(expected, actual):
    if expected!=actual:raise ValueError('Concurrent source changed; reread affected owners before retry')
