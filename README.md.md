# PCTIM Proof Carrier v0.1.2
**Point-Call Temporal Integration Model — Bounded Mutation-Boundary Prototype**

## Overview
This repository provides a runnable, public-safe proof surface for the **Point-Call Temporal Integration Model (PCTIM)**.

The purpose of this carrier is to evaluate PCTIM's bounded failure behavior when a previously admissible point-call is subjected to deliberate temporal, lineage, authority, scope, custody, replay, and consequence-boundary mutations.

The carrier demonstrates:
- lineage commitments across accepted transitions;
- a configured temporal decay window;
- live authority, scope, and custody checks;
- single-use nonce handling;
- fail-closed behavior after a boundary breach;
- an observable protected-effect surrogate; and
- refusal of direct attempts to bypass the effect gate.

> **Scope & Access Boundary:** This public carrier exposes bounded execution behavior, integrity-committed boundary receipts, mutation cases, and failure assertions. It intentionally withholds the underlying mathematical substrate, production kernel mechanics, private condition construction, production key architecture, private routing, and deployment logic of PCTIM — while still providing 100% executable, falsifiable proof objects for every scenario in the test matrix.

> **Disclosure Principle:** The carrier demonstrates selected externally observable PCTIM behavior. It is not a complete disclosure or implementation of the PCTIM production system.

---

## Bounded Public Claim
The bounded claim tested by this carrier is:

> **A proposed point-call may reach the protected-effect surrogate only when the published carrier conditions required for that call remain valid at the verification boundary.**

For the carrier, a point-call is valid only when **all** individual boundary conditions pass simultaneously. In plain terms, if even a single condition fails, the entire check fails:

$$\text{Valid}(C_i) = \text{Lineage} \land \text{Temporal} \land \text{Authority} \land \text{Scope} \land \text{Custody} \land \text{Nonce}$$

where:
- `Lineage` = cryptographic lineage continuity is unbroken;
- `Temporal` = execution falls within the permitted time window;
- `Authority` = active authority token is valid and unrevoked;
- `Scope` = operation remains within the assigned scope;
- `Custody` = operational custody is verified; and
- `Nonce` = the request nonce has not been consumed (no replay).

The bounded consequence property is:

$$\text{Valid}(C_i) = 1 \implies \text{ProtectedEffect}(C_i) = 1$$

and:

$$\text{Valid}(C_i) = 0 \implies \text{ProtectedEffect}(C_i) = 0$$

The carrier therefore tests the strict boundary rule:

**NO_BIND → NO PROTECTED EFFECT**

---

## The Core Mechanism

PCTIM decouples proposed transaction sequences into strict **point-calls**. Every call must satisfy the carrier's mandatory boundary conditions before a `BIND_SUCCESS` result can produce the protected-effect surrogate.

### 1. Cryptographic Lineage Continuity
Accepted transitions produce a commitment derived from the previous lineage commitment and the transition fields. For this public carrier, the implementation uses canonical JSON encoding followed by SHA-256:

$$O_i = H(O_{i-1} \parallel \text{State}_i \parallel \text{Authority}_i \parallel \text{Scope}_i \parallel \text{Custody}_i \parallel \text{Nonce}_i)$$

A predecessor mismatch produces `NO_BIND_LINEAGE_BREACH` and forces a fail-closed lockdown — no protected effect is produced.

### 2. Temporal Decay Window
Continuation calls are evaluated against the carrier's configured, high-precision temporal window. Where the elapsed interval exceeds the permitted window, the continuation is rejected as stale (`NO_BIND_STALE_EVIDENCE`), and no protected effect is produced.

### 3. Live Authority, Scope & Custody Validation
The carrier evaluates authority, scope, and custody dynamically at the boundary — not just at initialization. A mutation of any required condition mid-flight produces a corresponding `NO_BIND_*` refusal and blocks the tested protected effect instantly.

### 4. Single-Use Effect Gate
A successful boundary evaluation issues a single-use internal gate ticket to the effect gate. The effect gate accepts only the valid ticket and consumes it after use; a forged or otherwise invalid ticket is rejected (`EFFECT_GATE_BLOCKED`). The effect counter provides an observable surrogate for whether the consequence boundary was crossed.

---

## Test Matrix
The carrier includes the following 11 bounded mutation scenarios:

| Scenario | Tested Condition / Mutation | Expected Outcome | Effect Status |
| :--- | :--- | :--- | :--- |
| **01. Baseline Bind** | Initial valid point-call | `BIND_SUCCESS` | Mutated ($0 \rightarrow 1$) |
| **02. Lineage Continuity** | Valid chained predecessor commitment | `BIND_SUCCESS` | Mutated ($1 \rightarrow 2$) |
| **03. Authority Mutation** | Active authority revoked mid-flight | `NO_BIND_REVOKED_AUTHORITY` | Blocked |
| **04. Lock Persistence** | Subsequent call after prior boundary breach | `SYSTEM_LOCKED` | Blocked |
| **05. Stale Continuation** | Temporal window exceeded after valid initialization | `NO_BIND_STALE_EVIDENCE` | Blocked |
| **06. Lineage Mutation** | Forged predecessor commitment injected | `NO_BIND_LINEAGE_BREACH` | Blocked |
| **07. Scope Mutation** | Active scope changed mid-flight | `NO_BIND_SCOPE_BREACH` | Blocked |
| **08. Custody Mutation** | Active custodian changed mid-flight | `NO_BIND_CUSTODY_BREACH` | Blocked |
| **09. Replay Attack** | Previously consumed nonce resubmitted | `NO_BIND_REPLAY_ATTACK` | Blocked |
| **10. Direct Effect Bypass** | Forged ticket submitted directly to effect gate | `EFFECT_GATE_BLOCKED` | Blocked |
| **11A/B. Refusal-after-Refusal** | `NO_BIND` triggered, followed by direct consequence attempt | `NO_BIND` $\rightarrow$ `BLOCKED` | Blocked |

---

## Project Structure
```text
pctim-proof-carrier/
├── src/
│   └── pctim_core.py            # Core PCTIM verifier & logical effect gate
├── tests/
├── run_proof.py                 # Master test suite runner (11 scenarios)
├── pctim_proof_receipts.txt     # Generated proof log artifact
└── README.md                    # Orientation & scope specification
```

---

## Running the Carrier
Clone the repository, navigate into the folder, and run the test suite:

```bash
git clone https://github.com/MightyNig/pctim-proof-carrier.git
cd pctim-proof-carrier
python run_proof.py
```

Running the suite executes all 11 scenarios in the test matrix above and writes a full proof log to `pctim_proof_receipts.txt`.