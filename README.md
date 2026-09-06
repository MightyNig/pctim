# PCTIM Proof Carrier v0.1.2

**Point-Call Temporal Integration Model — Bounded Mutation-Boundary Prototype**

## Overview

This repository provides a minimal, hardened test harness designed to evaluate bounded mutation-boundary behavior, state integrity, temporal continuity, and fail-closed persistence.

The carrier demonstrates deterministic refusal mechanics under controlled conditions while strictly isolating proprietary production substrates.

The published carrier exercises:

- lineage commitments across accepted transitions;
- a configured temporal decay window;
- live authority, scope, and custody checks;
- single-use nonce handling;
- fail-closed behavior after a boundary breach;
- an observable protected-effect surrogate; and
- refusal of direct attempts to bypass the effect gate.

## Information Boundary Policy

This repository exposes only the bounded public carrier and its verification artifacts.

All proprietary Klata Inc. commercial logic, UI telemetry layers, production deployment logic, private routing, and underlying PCTIM mathematical or kernel machinery are withheld.

The public implementation is intentionally limited to the behaviors required to reproduce the published test cases.

> **Disclosure Principle:** This carrier demonstrates selected externally observable PCTIM behavior. It is not a complete disclosure or implementation of the PCTIM production system.

## Bounded Public Claim

The bounded claim tested by this carrier is:

> **A proposed point-call may reach the protected-effect surrogate only when the published carrier conditions required for that call remain valid at the verification boundary.**

For the public carrier, a point-call is valid only when all tested boundary conditions pass simultaneously:

`Valid(Cᵢ) = Lineage ∧ Temporal ∧ Authority ∧ Scope ∧ Custody ∧ Nonce`

Where:

- `Lineage` = cryptographic lineage continuity is unbroken;
- `Temporal` = the continuation remains inside the configured temporal window;
- `Authority` = the active authority condition is valid;
- `Scope` = the operation remains inside the active scope;
- `Custody` = the active custody condition is valid; and
- `Nonce` = the request has not already been consumed.

The bounded consequence property is:

`Valid(Cᵢ) = 1  ⇒  ProtectedEffect(Cᵢ) = 1`

and:

`Valid(Cᵢ) = 0  ⇒  ProtectedEffect(Cᵢ) = 0`

The carrier therefore tests the strict boundary rule:

**NO_BIND → NO PROTECTED EFFECT**

This claim is limited to the published carrier implementation and test conditions.

## The Core Mechanism

PCTIM decouples proposed transaction sequences into strict **point-calls**.

Every continuation must satisfy the carrier's mandatory boundary conditions before a `BIND_SUCCESS` result can produce the protected-effect surrogate.

### 1. Cryptographic Lineage Continuity

Accepted transitions produce a commitment derived from the previous lineage commitment and the published transition fields.

For this public carrier, canonical JSON encoding followed by SHA-256 is used for the commitment:

`Oᵢ = H(Oᵢ₋₁ ∥ Stateᵢ ∥ Authorityᵢ ∥ Scopeᵢ ∥ Custodyᵢ ∥ Nonceᵢ)`

A predecessor mismatch produces `NO_BIND_LINEAGE_BREACH` and forces a fail-closed lockdown; no protected effect is produced.

The production PCTIM commitment construction and kernel implementation are not disclosed here.

### 2. Temporal Decay Window

Continuation calls are evaluated against the carrier's configured temporal window.

Where the elapsed interval exceeds the permitted window, the continuation is rejected as stale:

`NO_BIND_STALE_EVIDENCE`

and no protected effect is produced.

The carrier records temporal references using nanosecond-represented values. Effective clock resolution remains platform-dependent.

### 3. Live Authority, Scope & Custody Validation

The carrier evaluates authority, scope, and custody dynamically at the boundary rather than relying solely on initialization state.

A mutation of a required condition produces a corresponding `NO_BIND_*` refusal and prevents the tested protected effect.

### 4. Single-Use Effect Gate

A successful boundary evaluation issues a single-use internal gate ticket to the protected-effect gate.

The gate accepts only the valid ticket and consumes it after use.

A forged or otherwise invalid ticket is rejected:

`EFFECT_GATE_BLOCKED`

The effect counter provides an observable surrogate for whether the consequence boundary was crossed.

## Protected-Effect Boundary

A refusal status alone is not treated as sufficient evidence of consequence prevention.

The carrier therefore records:

```text
pre_effect_counter
post_effect_counter
```

For a successful baseline case:

```text
post_effect_counter = pre_effect_counter + 1
```

For a blocked case:

```text
post_effect_counter = pre_effect_counter
```

The direct consequence tests therefore determine whether an attempted consequence actually reaches the protected-effect surrogate rather than merely whether the verifier reports `NO_BIND`.

## Test Matrix

The carrier includes the following bounded mutation scenarios:

| Scenario | Tested Condition / Mutation | Expected Outcome | Effect Status |
| :--- | :--- | :--- | :--- |
| **01. Baseline Bind** | Initial valid point-call | `BIND_SUCCESS` | Mutated (`0 → 1`) |
| **02. Lineage Continuity** | Valid chained predecessor commitment | `BIND_SUCCESS` | Mutated (`1 → 2`) |
| **03. Authority Mutation** | Active authority revoked mid-flight | `NO_BIND_REVOKED_AUTHORITY` | Blocked |
| **04. Lock Persistence** | Subsequent call after prior boundary breach | `SYSTEM_LOCKED` | Blocked |
| **05. Stale Continuation** | Temporal window exceeded after valid initialization | `NO_BIND_STALE_EVIDENCE` | Blocked |
| **06. Lineage Mutation** | Forged predecessor commitment injected | `NO_BIND_LINEAGE_BREACH` | Blocked |
| **07. Scope Mutation** | Active scope changed mid-flight | `NO_BIND_SCOPE_BREACH` | Blocked |
| **08. Custody Mutation** | Active custodian changed mid-flight | `NO_BIND_CUSTODY_BREACH` | Blocked |
| **09. Replay Attack** | Previously consumed nonce resubmitted | `NO_BIND_REPLAY_ATTACK` | Blocked |
| **10. Direct Effect Bypass** | Forged ticket submitted directly to effect gate | `EFFECT_GATE_BLOCKED` | Blocked |
| **11A/B. Refusal-after-Refusal** | `NO_BIND` triggered, followed by direct consequence attempt | `NO_BIND → BLOCKED` | Blocked |

## Test Interpretation

The carrier is intended to be evaluated by separating:

1. the stated claim;
2. the executable artifact;
3. the mutation applied;
4. the observed result; and
5. the protected-effect outcome.

A repository description or status string is not, by itself, proof of the corresponding behavior.

The test evidence should therefore be derived from execution output, receipt contents, effect-counter state, and reproducibility under the published conditions.

## Receipt Integrity

Each carrier execution produces a boundary receipt containing the relevant public test outcome, including the nonce, status, reason, effect-counter state, and lineage commitment where applicable.

A receipt commitment is generated over the published receipt fields.

`verify_receipt.py` independently recomputes the published receipt commitment and reports whether the supplied receipt is internally consistent.

This receipt commitment is an integrity mechanism for the public artifact. It is not presented as a production signature scheme or as a complete PCTIM proof system.

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

Clone the repository, navigate into the project directory, run the carrier, and then independently verify the generated receipt material:

```bash
git clone https://github.com/MightyNig/pctim-proof-carrier.git
cd pctim-proof-carrier
python run_proof.py
python verify_receipt.py
```

The carrier run executes the published mutation suite and writes its proof log to:

```text
pctim_proof_receipts.txt
```

The independent verifier evaluates the integrity of the published receipt artifact separately from the main execution command.

## Project Structure

```text
pctim-proof-carrier/
├── src/
│   └── pctim_core.py            # Core PCTIM verifier & logical effect gate
├── tests/
├── run_proof.py                 # Master test suite runner
├── verify_receipt.py            # Independent receipt verification
├── pctim_proof_receipts.txt     # Generated proof log artifact
└── README.md                    # Orientation & scope specification
```

## Version Boundary

**PCTIM Proof Carrier v0.1.2** is a bounded mutation-boundary prototype.

It is intended to establish a small, runnable, reproducible, and falsifiable public proof surface for the selected PCTIM behaviors.

It does not constitute a complete disclosure or implementation of PCTIM.

**The carrier is the public proof surface. The production PCTIM kernel remains protected.**
