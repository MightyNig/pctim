# verify_receipt.py v0.1.2
"""
Independent verifier for the PCTIM proof artifact.

Validates TWO layers:
1. PCTIMCore receipt_hash for every full boundary receipt.
2. Runner log_hash for every execution-log entry.

The JSONL artifact contains the complete receipt, so receipt_hash is not
treated as display-only metadata.
"""

import hashlib
import json
import os
import sys

RECEIPTS_PATH = os.path.join(os.path.dirname(__file__), "pctim_proof_receipts.jsonl")


def canonical_without_receipt_hash(receipt: dict) -> str:
    fields = {k: v for k, v in receipt.items() if k != "receipt_hash"}
    return json.dumps(fields, sort_keys=True, separators=(",", ":"))


def recompute_receipt_hash(receipt: dict) -> str:
    return hashlib.sha256(
        canonical_without_receipt_hash(receipt).encode("utf-8")
    ).hexdigest()


def canonical_log_record(entry: dict) -> dict:
    return {
        "test_id": entry["test_id"],
        "test_name": entry["test_name"],
        "core_receipt": entry["core_receipt"],
    }


def recompute_log_hash(entry: dict) -> str:
    canonical = json.dumps(
        canonical_log_record(entry),
        sort_keys=True,
        separators=(",", ":"),
    )
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def main() -> int:
    print("=" * 60)
    print("PCTIM PROOF VERIFIER v0.1.2")
    print("=" * 60)

    if not os.path.exists(RECEIPTS_PATH):
        print(f"\n[FAIL] Artifact not found: {RECEIPTS_PATH}")
        sys.exit(1)

    with open(RECEIPTS_PATH, "r", encoding="utf-8") as f:
        lines = [line.strip() for line in f if line.strip()]

    if not lines:
        print("\n[FAIL] Artifact is empty.")
        sys.exit(1)

    failures = []
    seen_ids = set()

    print(f"\nArtifact : {os.path.basename(RECEIPTS_PATH)}")
    print(f"Entries  : {len(lines)}")
    print("\nValidating full receipt_hash and log_hash commitments...\n")

    for idx, line in enumerate(lines, start=1):
        try:
            entry = json.loads(line)
            required = {"test_id", "test_name", "core_receipt", "log_hash"}
            if not required.issubset(entry):
                raise ValueError("missing required fields")

            test_id = entry["test_id"]
            if test_id in seen_ids and test_id not in {"13A", "13B"}:
                raise ValueError(f"duplicate test_id: {test_id}")
            seen_ids.add(test_id)

            receipt = entry["core_receipt"]
            stored_receipt_hash = receipt.get("receipt_hash")
            if not stored_receipt_hash:
                raise ValueError("missing core receipt_hash")

            recomputed_receipt = recompute_receipt_hash(receipt)
            receipt_ok = stored_receipt_hash == recomputed_receipt

            recomputed_log = recompute_log_hash(entry)
            log_ok = entry["log_hash"] == recomputed_log

            if receipt_ok and log_ok:
                print(
                    f"PASS [{test_id:>3}] "
                    f"receipt_hash={stored_receipt_hash[:16]}... "
                    f"log_hash={entry['log_hash'][:16]}..."
                )
            else:
                print(f"FAIL [{test_id:>3}]")
                if not receipt_ok:
                    print(
                        f"  receipt_hash stored     : {stored_receipt_hash}\n"
                        f"  receipt_hash recomputed  : {recomputed_receipt}"
                    )
                if not log_ok:
                    print(
                        f"  log_hash stored          : {entry['log_hash']}\n"
                        f"  log_hash recomputed      : {recomputed_log}"
                    )
                failures.append((idx, test_id))

        except (json.JSONDecodeError, KeyError, TypeError, ValueError) as exc:
            print(f"FAIL [line {idx}] malformed artifact: {exc}")
            failures.append((idx, f"line-{idx}"))

    print("\n" + "=" * 60)
    if failures:
        print(f"VERIFICATION RESULT: FAILED ({len(failures)} failure(s))")
        for idx, ident in failures:
            print(f"  - {ident} at line {idx}")
        print("=" * 60)
        return 1

    print(f"VERIFICATION RESULT: PASSED")
    print(f"All {len(lines)} entries passed both cryptographic checks.")
    print("=" * 60)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
