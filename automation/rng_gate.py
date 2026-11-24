"""Structural dice-receipt gate; cannot authenticate external ChatGPT execution."""
import hashlib
import re

VOID_IDS = frozenset(("PLAY-REC-D308-PERYTON-R1-R2-DEFENSIVE-COUNTERATTACK-001","PLAY-REC-D308-PERYTON-R3-DEFENSIVE-DIVES-CIRREN-STABLE-001","PLAY-REC-D308-PERYTON-R4-DOUBLE-SNEAK-V-STABILIZED-001","PLAY-REC-D308-V-PERYTON-DEFENSIVE-PLAN-INITIATIVE-PENDING-001","PLAY-REC-D308-V-PSYCHIC-READY-RNG-CORRECTION-001"))

def reject_void(entry):
    if entry.get("request_id") in VOID_IDS:
        raise ValueError("Voided D308 fabricated-roll recovery: audit only")

def validate_rng(entry, path, raw, policy, seen_batches):
    reject_void(entry)
    if policy.get("version") != 1:
        raise ValueError("Unsupported RNG gate version")
    blob = raw.encode("utf-8")
    sha = hashlib.sha1(("blob "+str(len(blob))+"\0").encode()+blob).hexdigest()
    if path in policy.get("legacy_blobs", {}):
        if policy["legacy_blobs"][path] != sha:
            raise ValueError("Historical recovery blob differs from pinned original")
        return
    evidence = entry.get("rng_evidence")
    if not isinstance(evidence, dict):
        raise ValueError("Missing RNG evidence declaration")
    if evidence.get("status") == "no_rolls":
        if not isinstance(evidence.get("reason"), str) or not evidence["reason"].strip() or evidence.get("receipts"):
            raise ValueError("Invalid no-roll declaration")
        return
    receipts = evidence.get("receipts")
    if evidence.get("status") != "rolled" or not isinstance(receipts,list) or not receipts:
        raise ValueError("Missing raw RNG receipt")
    for receipt in receipts:
        if not isinstance(receipt,dict) or receipt.get("schema_version")!=1 or receipt.get("generator")!="python.secrets.randbelow":
            raise ValueError("Invalid RNG generator declaration")
        batch=receipt.get("batch_id")
        if not isinstance(batch,str) or not re.fullmatch("[0-9a-f]{32}",batch) or batch in seen_batches:
            raise ValueError("Missing, invalid or repeated RNG batch ID")
        seen_batches.add(batch)
        rolls=receipt.get("rolls")
        if not isinstance(rolls,list) or not rolls:
            raise ValueError("Empty RNG receipt")
        ids=set()
        for roll in rolls:
            if not isinstance(roll,dict):
                raise ValueError("Invalid roll")
            rid,sides,faces=roll.get("id"),roll.get("sides"),roll.get("faces")
            if not isinstance(rid,str) or not rid.strip() or rid in ids or type(sides) is not int or sides<2:
                raise ValueError("Invalid roll identity/die")
            if not isinstance(faces,list) or not faces or any(type(face) is not int or not 1<=face<=sides for face in faces):
                raise ValueError("Invalid raw die face")
            ids.add(rid)
