# PCTIM Proof Carrier v0.1.2

**Point-Call Temporal Integration Model — Bounded Mutation-Boundary Prototype**

## Overview

This repository provides a minimal, hardened test harness designed to evaluate bounded mutation-boundary behavior, state integrity, temporal continuity, and fail-closed persistence.

The carrier demonstrates deterministic refusal mechanics under controlled conditions while strictly isolating proprietary production substrates.

The published carrier exercises:
- lineage commitments across accepted transitions;
- a configured temporal decay window;
- live authority, scope, custody, and state checks;
- single-use nonce handling;
- fail-closed behavior after a boundary breach;
- an observable protected-effect surrogate; and
- refusal of direct attempts to bypass the logical effect gate.

## Information Boundary Policy

This repository exposes only the bounded public carrier and its verification artifacts.

All proprietary Klata Inc. commercial logic, UI telemetry layers, production deployment topology, private routing, private key hierarchies, and underlying PCTIM mathematical or kernel machinery are strictly withheld. 

> **Disclosure Principle:** This carrier demonstrates selected externally observable PCTIM behavior. It is not a complete disclosure or implementation of the PCTIM production system.

## Bounded Public Claim

The bounded claim tested by this carrier is:

> **A proposed point-call may reach the logical effect gate only when the published carrier conditions required for that call remain valid at the verification boundary.**

For the public carrier, a point-call is valid only when all tested boundary conditions pass simultaneously:

`Valid(Cᵢ) = Lineage ∧ Temporal ∧ Authority ∧ Scope ∧ Custody ∧ State ∧ Nonce`

Where:

- `Lineage` = cryptographic lineage continuity is unbroken;
- `Temporal` = the continuation remains inside the configured temporal window;
- `Authority` = the active authority condition is valid;
- `Scope` = the operation remains inside the active scope;
- `Custody` = the active custody condition is valid; and
- `Nonce` = the request has not already been consumed.

The bounded consequence property is:
`Valid(Cᵢ) = 1  ⇒  ProtectedEffect(Cᵢ) = 1`
`Valid(Cᵢ) = 0  ⇒  ProtectedEffect(Cᵢ) = 0`

The carrier therefore tests the strict boundary rule:
**NO_BIND → NO PROTECTED EFFECT**

## The Core Mechanism

Every continuation must satisfy the carrier's mandatory boundary conditions before a `BIND_SUCCESS` result can produce the protected-effect surrogate.

1. **Cryptographic Lineage Continuity:** Accepted transitions produce a canonical JSON SHA-256 commitment derived from the previous lineage commitment and the published transition fields. A predecessor mismatch breaks the established chain.
2. **Temporal Decay Window:** Continuations exceeding the configured nanosecond window are rejected as stale.
3. **Live Condition Validation:** The carrier evaluates authority, scope, custody, and active state dynamically mid-flight at the boundary.
4. **Single-Use Effect Gate:** A successful evaluation issues a single-use internal ticket to the logical effect gate. Direct bypass attempts with forged tickets are blocked.

## Protected-Effect Boundary

A refusal status alone is not treated as sufficient evidence of consequence prevention. The carrier therefore records `pre_effect_counter` and `post_effect_counter`. The tests programmatically assert whether an attempted consequence actually reaches the observable protected-effect surrogate.

## Test Matrix

The suite contains 13 bounded scenarios, with Scenario 13 containing two sequential execution phases (yielding 14 execution receipts).

| Scenario | Tested Condition / Mutation | Expected Outcome | Effect Status |
| :--- | :--- | :--- | :--- |
| **01. Baseline Bind** | Initial valid point-call | `BIND_SUCCESS` | Mutated |
| **02. Lineage Continuity** | Valid chained predecessor commitment | `BIND_SUCCESS` | Mutated |
| **03. Authority Mutation** | Active authority revoked mid-flight | `NO_BIND_REVOKED_AUTHORITY` | Blocked |
| **04. Lock Persistence** | Subsequent call after prior boundary breach | `SYSTEM_LOCKED` | Blocked |
| **05. Stale Continuation** | Temporal window exceeded after valid initialization | `NO_BIND_STALE_EVIDENCE` | Blocked |
| **06. Lineage Mutation** | Breaks an established continuation chain by mutating the predecessor | `NO_BIND_LINEAGE_BREACH` | Blocked |
| **07. Active State Mutation** | Active state drifts mid-flight | `NO_BIND_STATE_BREACH` | Blocked |
| **08. Scope Mutation** | Active scope changed mid-flight | `NO_BIND_SCOPE_BREACH` | Blocked |
| **09. Custody Mutation** | Active custodian changed mid-flight | `NO_BIND_CUSTODY_BREACH` | Blocked |
| **10. Replay Attack** | Previously consumed nonce resubmitted | `NO_BIND_REPLAY_ATTACK` | Blocked |
| **11. Alternate Route Dispatch** | Alternate routing path using `alternate_dispatch()` | `NO_BIND_REVOKED_AUTHORITY` | Blocked |
| **12. Direct Effect Bypass** | Direct invocation against the logical effect gate | `EFFECT_GATE_BLOCKED` | Blocked |
| **13A/B. Refusal-after-Refusal** | `NO_BIND` triggered, followed by direct consequence attempt | `NO_BIND → BLOCKED` | Blocked |

## Boundary Receipt Commitment (receipt_hash)

Each carrier execution produces a boundary receipt containing the test outcome. A cryptographic boundary commitment (`receipt_hash`) is generated over the full receipt payload by the core verifier. 

**Note:** `verify_receipt.py` independently parses the generated proof log, reconstructs the canonical receipt, and recomputes the true `receipt_hash` to prove receipt integrity. It also validates the runner's summary `log_hash`.

## Falsification Conditions

The bounded carrier claim is falsified within its stated scope if a published test demonstrates any of the following:

- an invalid call increases the protected-effect counter;
- a consumed nonce successfully produces another protected effect;
- a broken predecessor is accepted;
- a required authority mutation still permits the tested effect;
- a stale continuation still reaches the tested effect;
- a required scope or custody mutation is bypassed;
- a forged direct effect attempt increments the effect counter; or
- the published receipt cannot be independently reproduced and verified under the documented conditions.

## Local Reproduction

Clone the repository and run the carrier to generate the proof log artifact:

```bash
git clone [https://github.com/MightyNig/pctim.git](https://github.com/MightyNig/pctim.git)
cd pctim
python run_proof.py
python verify_receipt.py
```

The carrier run executes the published mutation suite and writes its proof log to:

```text
pctim_proof_receipts.txt
```

The independent verifier evaluates the integrity of the published receipt artifact separately from the main execution command.

Note on Determinism: The carrier guarantees deterministic behavioral outcomes (NO_BIND → BLOCKED). Because the temporal decay window evaluates live wall-clock nanoseconds, independent test executions will produce unique receipt bytes and cryptographic 
hashes. The public claim is strict behavioral reproducibility, not byte-identical cryptographic replay across independent runs.

## Project Structure

```text
pctim-proof-carrier/
├── src/
│   └── pctim_core.py            # Core PCTIM verifier & logical effect gate
├── run_proof.py                 # Master test suite runner
├── verify_receipt.py            # Independent receipt verification
├── pctim_proof_receipts.jsonl     # Generated proof log artifact
└── README.md                    # Orientation & scope specification
```

## Version Boundary

**PCTIM Proof Carrier v0.1.2** is a bounded mutation-boundary prototype.

It is intended to establish a small, runnable, reproducible, and falsifiable public proof surface for the selected PCTIM behaviors.

It does not constitute a complete disclosure or implementation of PCTIM.

**The carrier is the public proof surface. The production PCTIM kernel remains protected.**