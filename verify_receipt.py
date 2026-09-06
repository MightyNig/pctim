# verify_receipt.py
import hashlib
import json
import os

def verify_all_receipts():
    receipts_path = "pctim_proof_receipts.txt"
    if not os.path.exists(receipts_path):
        print("FAIL: Receipt file not found.")
        return False

    # FIX 1: Enforce utf-8 encoding to match run_proof.py output
    with open(receipts_path, "r", encoding="utf-8") as f:
        lines = [line.strip() for line in f if line.strip()]

    all_passed = True
    for line in lines:
        parts = line.split(" | ")
        test_meta = parts[0].split("] ")
        test_id = test_meta[0].replace("[", "")
        test_name = test_meta[1]
        status = parts[1].replace("Status: ", "")
        counter = int(parts[2].replace("Counter: ", ""))
        recorded_hash = parts[3].replace("Hash: ", "")

        # FIX 2: Correctly map the 'details' boolean. 
        # run_proof.py sets details=True when pre != post (which happens on BIND_SUCCESS)
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