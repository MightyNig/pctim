import time
import json
import sys
import os
import io

# Explicitly add the 'src' directory to Python's module search path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))

from pctim_core import PCTIMCore

# Force UTF-8 encoding for standard output (Fixes Windows file redirection)
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def print_receipt(title, receipt):
    print(f"\n{'='*60}\n🚀 SCENARIO: {title}\n{'='*60}")
    if receipt["status"] == "BIND_SUCCESS":
        print("✅ RESULT: BIND_SUCCESS")
    else:
        print(f"🚫 RESULT: {receipt['status']}")
    
    print("🧾 BOUNDARY RECEIPT:")
    print(json.dumps(receipt, indent=2))
    
    pre = receipt["pre_effect_counter"]
    post = receipt["post_effect_counter"]
    if pre == post:
        print(f"🛡️  EFFECT SINK: Blocked. Counter remained at {post}.")
    else:
        print(f"⚡ EFFECT SINK: Mutated. Counter advanced {pre} -> {post}.")

def build_payload(core, nonce, step_type, state_data):
    return {
        "nonce": nonce,
        "step_type": step_type,
        "state_data": state_data,
        "authority": "AUTH_123",
        "scope": "SCOPE_A",
        "custodian": "CUST_A",
        "predecessor_hash": core.current_lineage_hash
    }

def main():
    print("STARTING PCTIM PROOF CARRIER v0.1.2...\n")

    # 01. BASELINE / VALID BIND
    core = PCTIMCore()
    p1 = build_payload(core, "tx-001", "INITIALIZATION", "STATE_1")
    r1 = core.execute_point_call(p1)
    print_receipt("01: Baseline / Valid Bind", r1)

    # 02. CONTINUITY / VALID PREDECESSOR
    p2 = build_payload(core, "tx-002", "CONTINUATION", "STATE_2")
    r2 = core.execute_point_call(p2)
    print_receipt("02: Continuity / Valid Predecessor", r2)

    # 03. AUTHORITY REVOCATION (True Mid-Flight Mutation)
    p3 = build_payload(core, "tx-003", "CONTINUATION", "STATE_3")
    core.active_authority = "REVOKED_AUTH" # Mutate system mid-flight
    r3 = core.execute_point_call(p3)
    print_receipt("03: Authority Revocation Mid-Flight", r3)

    # 04. FAIL-CLOSED LOCK PERSISTENCE
    p4 = build_payload(core, "tx-004", "CONTINUATION", "STATE_4")
    p4["authority"] = "REVOKED_AUTH" # Match authority to bypass check, test lock
    r4 = core.execute_point_call(p4)
    print_receipt("04: Fail-Closed Lock Persistence", r4)

    # 05. STALE CONTINUATION (True Post-Establishment Decay)
    core2 = PCTIMCore(temporal_window_ns=200_000_000)
    p_valid1 = build_payload(core2, "tx-s1", "INITIALIZATION", "STATE_1")
    core2.execute_point_call(p_valid1)
    
    p_stale = build_payload(core2, "tx-s2", "CONTINUATION", "STATE_2")
    time.sleep(0.3) # Wait 300ms AFTER valid initialization
    r_stale = core2.execute_point_call(p_stale)
    print_receipt("05: Stale Continuation", r_stale)

    # 06. LINEAGE MUTATION
    core3 = PCTIMCore()
    p_lineage = build_payload(core3, "tx-l1", "INITIALIZATION", "STATE_1")
    p_lineage["predecessor_hash"] = "forged_hash_xyz"
    r_lineage = core3.execute_point_call(p_lineage)
    print_receipt("06: Lineage Mutation", r_lineage)

    # 07. SCOPE MUTATION (True Mid-Flight Mutation)
    core4 = PCTIMCore()
    p_scope1 = build_payload(core4, "tx-sc1", "INITIALIZATION", "STATE_1")
    core4.execute_point_call(p_scope1)
    
    p_scope2 = build_payload(core4, "tx-sc2", "CONTINUATION", "STATE_2")
    core4.active_scope = "SCOPE_B" # System scope changes mid-flight
    r_scope = core4.execute_point_call(p_scope2)
    print_receipt("07: Scope Mutation", r_scope)

    # 08. CUSTODY MUTATION (True Mid-Flight Mutation)
    core5 = PCTIMCore()
    p_cust1 = build_payload(core5, "tx-cu1", "INITIALIZATION", "STATE_1")
    core5.execute_point_call(p_cust1)
    
    p_cust2 = build_payload(core5, "tx-cu2", "CONTINUATION", "STATE_2")
    core5.active_custodian = "CUST_B" # System custody changes mid-flight
    r_custody = core5.execute_point_call(p_cust2)
    print_receipt("08: Custody Mutation", r_custody)

    # 09. REPLAY ATTACK
    core6 = PCTIMCore()
    p_replay = build_payload(core6, "tx-rep1", "INITIALIZATION", "STATE_1")
    core6.execute_point_call(p_replay)
    r_replay = core6.execute_point_call(p_replay) # Resubmit exact same call
    print_receipt("09: Replay Attack", r_replay)

    # 10. DIRECT EFFECT ATTEMPT (Consequence Bypass)
    core7 = PCTIMCore()
    p_direct = build_payload(core7, "tx-dir1", "CONTINUATION", "STATE_1")
    r_direct = core7.attempt_direct_consequence(p_direct)
    print_receipt("10: Alternate Route / Direct Effect Attempt", r_direct)

    # 11. NO_BIND → CONSEQUENCE ATTEMPT (Refusal-after-Refusal)
    core8 = PCTIMCore()
    p_valid_init = build_payload(core8, "tx-nb1", "INITIALIZATION", "STATE_1")
    core8.execute_point_call(p_valid_init)
    
    # 1. Mutate authority to trigger NO_BIND
    p_invalid_cont = build_payload(core8, "tx-nb2", "CONTINUATION", "STATE_2")
    core8.active_authority = "REVOKED_AUTH"
    r_nobind = core8.execute_point_call(p_invalid_cont)
    print_receipt("11A: Trigger NO_BIND (Authority Revoked)", r_nobind)
    
    # 2. Attacker ignores the NO_BIND and attempts to force the consequence anyway
    r_force = core8.attempt_direct_consequence(p_invalid_cont)
    print_receipt("11B: NO_BIND -> Attempt Direct Consequence", r_force)

if __name__ == "__main__":
    main()