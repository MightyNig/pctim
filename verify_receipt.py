import hashlib
import json
import os

def verify_all_receipts():
    receipts_path = "pctim_proof_receipts.txt"
    if not os.path.exists(receipts_path):
        print("FAIL: Receipt file not found.")
        return False

    with open(receipts_path, "r", encoding="utf-8") as f:
        lines = [line.strip() for line in f if line.strip()]

    all_passed = True
    for line in lines:
        parts = line.split(" | ")
        if len(parts) < 4:
            continue
            
        header_part = parts[0].strip()
        if ":" in header_part:
            sub_parts = header_part.split(":", 1)
            test_id = sub_parts[0].strip()
            test_name = sub_parts[1].strip()
        else:
            test_id = "00"
            test_name = header_part

        status = parts[1].replace("Status:", "").strip()
        counter_str = parts[2].replace("Counter:", "").strip()
        counter = int(counter_str) if counter_str.isdigit() else 0
        recorded_hash = parts[3].replace("Hash:", "").strip()

        # Exactly matches the canonical record structure hashed by run_proof.py
        record = {
            "test_id": test_id,
            "test_name": test_name,
            "status": status,
            "protected_effect_counter": counter,
            "details": status == "BIND_SUCCESS"
        }
        canonical = json.dumps(record, sort_keys=True)
        calculated_hash = hashlib.sha256(canonical.encode('utf-8')).hexdigest()[:16]

        if calculated_hash == recorded_hash:
            print(f"[VERIFIED] Test {test_id}: Hash match ({calculated_hash})")
        else:
            print(f"[FAILED] Test {test_id}: Hash mismatch! Recorded: {recorded_hash}, Calculated: {calculated_hash}")
            all_passed = False

    return all_passed

if __name__ == "__main__":
    success = verify_all_receipts()
    if success:
        print("\nRESULT: Independent Receipt Verification PASSED.")
    else:
        print("\nRESULT: Independent Receipt Verification FAILED.")