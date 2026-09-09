# run_proof.py v0.1.2
# ============================================================
# PCTIM PROOF CARRIER
# Sys_ID: 1997 | Klata Inc. | Olamide Oduwole
#
# 13 bounded scenarios.
# Scenario 13 contains two sequential execution phases (13A and 13B).
# Total execution receipts: 14.
#
# The runner records the FULL boundary receipt plus a separate
# execution-log commitment. The verifier independently validates both.
# ============================================================

import hashlib
import io
import json
import os
import sys
import time
from typing import Callable, Dict, List

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "src")))

from pctim_core import PCTIMCore

if sys.stdout.encoding != "utf-8":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")


def assert_receipt(
    scenario_id: str,
    receipt: dict,
    expected_status: str,
    expect_effect_increment: bool = False,
) -> None:
    status = receipt.get("status", "UNKNOWN")
    pre = receipt.get("pre_effect_counter", 0)
    post = receipt.get("post_effect_counter", 0)
    failures = []

    if status != expected_status:
        failures.append(
            f"  Status  : expected '{expected_status}', got '{status}'"
        )

    if expect_effect_increment:
        if post != pre + 1:
            failures.append(
                f"  Effect  : expected {pre} -> {pre + 1}, got {pre} -> {post}"
            )
    elif post != pre:
        failures.append(
            f"  Effect  : expected no change ({pre}), got {pre} -> {post}"
        )

    if failures:
        print("\n" + "!" * 60)
        print(f"ASSERTION FAILURE — Scenario {scenario_id}")
        for line in failures:
            print(line)
        print("!" * 60)
        print("\nBOUNDED TEST SUITE FAILED\n")
        sys.exit(1)


def assert_setup(
    scenario_id: str,
    receipt: dict,
    expect_effect_increment: bool = True,
) -> None:
    """Assert every setup transition before using it as a precondition."""
    assert_receipt(
        scenario_id,
        receipt,
        "BIND_SUCCESS",
        expect_effect_increment=expect_effect_increment,
    )


def print_receipt(title: str, receipt: dict) -> None:
    print(f"\n{'=' * 60}\nSCENARIO: {title}\n{'=' * 60}")
    status = receipt.get("status", "UNKNOWN")
    print("RESULT:", status)
    print("BOUNDARY RECEIPT:")
    print(json.dumps(receipt, indent=2, sort_keys=True))
    pre = receipt.get("pre_effect_counter", 0)
    post = receipt.get("post_effect_counter", 0)
    if pre == post:
        print(f"EFFECT SINK: Blocked. Counter remained at {post}.")
    else:
        print(f"EFFECT SINK: Mutated. Counter advanced {pre} -> {post}.")


def split_title(title: str):
    if ":" in title:
        test_id, test_name = title.split(":", 1)
        return test_id.strip(), test_name.strip()
    return "00", title.strip()


def build_payload(core: PCTIMCore, nonce: str, step_type: str, state_data: str) -> dict:
    return {
        "nonce": nonce,
        "step_type": step_type,
        "state_data": state_data,
        "authority": "AUTH_123",
        "scope": "SCOPE_A",
        "custodian": "CUST_A",
        "predecessor_hash": core.current_lineage_hash,
    }


def canonical_log_record(test_id: str, test_name: str, receipt: dict) -> dict:
    return {
        "test_id": test_id,
        "test_name": test_name,
        "core_receipt": receipt,
    }


def log_hash_for(record: dict) -> str:
    canonical = json.dumps(record, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def main() -> None:
    print("STARTING PCTIM PROOF CARRIER v0.1.2")
    print("13 bounded scenarios.")
    print("Scenario 13 contains two sequential execution phases (13A and 13B).")
    print("Total execution receipts: 14.")

    receipts_path = os.path.join(os.path.dirname(__file__), "pctim_proof_receipts.jsonl")
    if os.path.exists(receipts_path):
        os.remove(receipts_path)

    logs: List[dict] = []
    assertion_count = 0

    def record_and_print(title: str, receipt: dict) -> None:
        nonlocal assertion_count
        print_receipt(title, receipt)

        test_id, test_name = split_title(title)
        core_receipt = json.loads(json.dumps(receipt, sort_keys=True))
        record = canonical_log_record(test_id, test_name, core_receipt)
        entry = {
            "test_id": test_id,
            "test_name": test_name,
            "core_receipt": core_receipt,
            "log_hash": log_hash_for(record),
        }
        logs.append(entry)

    def check(scenario_id, receipt, expected_status, expect_effect_increment=False):
        nonlocal assertion_count
        assert_receipt(
            scenario_id, receipt, expected_status,
            expect_effect_increment=expect_effect_increment
        )
        assertion_count += 1

    def setup(scenario_id, receipt):
        nonlocal assertion_count
        assert_setup(scenario_id, receipt, True)
        assertion_count += 1

    # 01. Baseline
    core = PCTIMCore()
    p1 = build_payload(core, "tx-001", "INITIALIZATION", "STATE_1")
    r1 = core.execute_point_call(p1)
    record_and_print("01: Baseline / Valid Bind", r1)
    check("01", r1, "BIND_SUCCESS", True)

    # 02. Valid continuation
    p2 = build_payload(core, "tx-002", "CONTINUATION", "STATE_1")
    r2 = core.execute_point_call(p2)
    record_and_print("02: Continuity / Valid Predecessor", r2)
    check("02", r2, "BIND_SUCCESS", True)

    # 03. Authority revoked mid-flight
    p3 = build_payload(core, "tx-003", "CONTINUATION", "STATE_1")
    core.active_authority = "REVOKED_AUTH"
    r3 = core.execute_point_call(p3)
    record_and_print("03: Authority Revocation Mid-Flight", r3)
    check("03", r3, "NO_BIND_REVOKED_AUTHORITY")

    # 04. Fail-closed persistence
    p4 = build_payload(core, "tx-004", "CONTINUATION", "STATE_1")
    r4 = core.execute_point_call(p4)
    record_and_print("04: Fail-Closed Lock Persistence", r4)
    check("04", r4, "SYSTEM_LOCKED")

    # 05. Stale continuation
    core2 = PCTIMCore(temporal_window_ns=200_000_000)
    r_s1 = core2.execute_point_call(
        build_payload(core2, "tx-s1", "INITIALIZATION", "STATE_1")
    )
    setup("05-setup", r_s1)
    p_stale = build_payload(core2, "tx-s2", "CONTINUATION", "STATE_1")
    time.sleep(0.3)
    r_stale = core2.execute_point_call(p_stale)
    record_and_print("05: Stale Continuation", r_stale)
    check("05", r_stale, "NO_BIND_STALE_EVIDENCE")

    # 06. Lineage mutation
    core3 = PCTIMCore()
    r_l1 = core3.execute_point_call(
        build_payload(core3, "tx-l1", "INITIALIZATION", "STATE_1")
    )
    setup("06-setup", r_l1)
    p_l2 = build_payload(core3, "tx-l2", "CONTINUATION", "STATE_1")
    p_l2["predecessor_hash"] = "forged_hash_xyz"
    r_lineage = core3.execute_point_call(p_l2)
    record_and_print("06: Lineage Mutation", r_lineage)
    check("06", r_lineage, "NO_BIND_LINEAGE_BREACH")

    # 07. Active state mutation
    core4 = PCTIMCore()
    r_st1 = core4.execute_point_call(
        build_payload(core4, "tx-st1", "INITIALIZATION", "STATE_1")
    )
    setup("07-setup", r_st1)
    p_st2 = build_payload(core4, "tx-st2", "CONTINUATION", "STATE_1")
    core4.active_state = "STATE_2"
    r_state = core4.execute_point_call(p_st2)
    record_and_print("07: Active State Mutation", r_state)
    check("07", r_state, "NO_BIND_STATE_BREACH")

    # 08. Scope mutation
    core5 = PCTIMCore()
    r_sc1 = core5.execute_point_call(
        build_payload(core5, "tx-sc1", "INITIALIZATION", "STATE_1")
    )
    setup("08-setup", r_sc1)
    p_sc2 = build_payload(core5, "tx-sc2", "CONTINUATION", "STATE_1")
    core5.active_scope = "SCOPE_B"
    r_scope = core5.execute_point_call(p_sc2)
    record_and_print("08: Scope Mutation", r_scope)
    check("08", r_scope, "NO_BIND_SCOPE_BREACH")

    # 09. Custody mutation
    core6 = PCTIMCore()
    r_cu1 = core6.execute_point_call(
        build_payload(core6, "tx-cu1", "INITIALIZATION", "STATE_1")
    )
    setup("09-setup", r_cu1)
    p_cu2 = build_payload(core6, "tx-cu2", "CONTINUATION", "STATE_1")
    core6.active_custodian = "CUST_B"
    r_custody = core6.execute_point_call(p_cu2)
    record_and_print("09: Custody Mutation", r_custody)
    check("09", r_custody, "NO_BIND_CUSTODY_BREACH")

    # 10. Replay attack
    core7 = PCTIMCore()
    p_replay = build_payload(core7, "tx-rep1", "INITIALIZATION", "STATE_1")
    r_rep1 = core7.execute_point_call(p_replay)
    setup("10-setup", r_rep1)
    r_replay = core7.execute_point_call(p_replay)
    record_and_print("10: Replay Attack", r_replay)
    check("10", r_replay, "NO_BIND_REPLAY_ATTACK")

    # 11. Alternate route
    core8 = PCTIMCore()
    r_rt1 = core8.execute_point_call(
        build_payload(core8, "tx-route-1", "INITIALIZATION", "STATE_1")
    )
    setup("11-setup", r_rt1)
    p_rt2 = build_payload(core8, "tx-route-2", "CONTINUATION", "STATE_1")
    core8.active_authority = "REVOKED_AUTH"
    r_route = core8.alternate_dispatch(p_rt2)
    record_and_print("11: Alternate Route Dispatch", r_route)
    check("11", r_route, "NO_BIND_REVOKED_AUTHORITY")

    # 12. Direct effect bypass attempt
    core9 = PCTIMCore()
    p_direct = build_payload(core9, "tx-dir1", "INITIALIZATION", "STATE_1")
    r_direct = core9.attempt_direct_consequence(p_direct)
    record_and_print("12: Direct Effect Bypass", r_direct)
    check("12", r_direct, "EFFECT_GATE_BLOCKED")

    # 13A/B. NO_BIND then consequence attempt
    core10 = PCTIMCore()
    r_nb_init = core10.execute_point_call(
        build_payload(core10, "tx-nb1", "INITIALIZATION", "STATE_1")
    )
    setup("13-setup", r_nb_init)
    p_nb_cont = build_payload(core10, "tx-nb2", "CONTINUATION", "STATE_1")
    core10.active_authority = "REVOKED_AUTH"
    r_nobind = core10.execute_point_call(p_nb_cont)
    record_and_print("13A: Trigger NO_BIND (Authority Revoked)", r_nobind)
    check("13A", r_nobind, "NO_BIND_REVOKED_AUTHORITY")

    r_force = core10.attempt_direct_consequence(p_nb_cont)
    record_and_print("13B: NO_BIND -> Attempt Direct Consequence", r_force)
    check("13B", r_force, "EFFECT_GATE_BLOCKED")

    expected_executions = 14
    if len(logs) != expected_executions:
        print(f"\nFAILED: expected {expected_executions} execution receipts, got {len(logs)}")
        sys.exit(1)

    with open(receipts_path, "w", encoding="utf-8") as f:
        for entry in logs:
            f.write(json.dumps(entry, sort_keys=True, separators=(",", ":")) + "\n")

    print("\n" + "=" * 60)
    print("PCTIM PROOF CARRIER v0.1.2")
    print("=" * 60)
    print(f"Test assertions    : {assertion_count}")
    print(f"Total scenarios    : 13")
    print(f"Total executions   : {len(logs)}")
    print(f"Successful binds   : {sum(1 for x in logs if x['core_receipt'].get('status') == 'BIND_SUCCESS')}")
    print(f"Blocked executions : {sum(1 for x in logs if x['core_receipt'].get('status') != 'BIND_SUCCESS')}")
    print(f"Receipt artifact   : {os.path.basename(receipts_path)}")
    print("\nRESULT:")
    print("BOUNDED TEST SUITE PASSED")
    print("=" * 60)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
