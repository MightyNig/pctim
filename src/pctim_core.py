import time
import hashlib
import json

class PCTIMCore:
    def __init__(self, temporal_window_ns=500_000_000, authority="AUTH_123", scope="SCOPE_A", custodian="CUST_A"):
        # Observable Protected-Effect Surrogate
        self.protected_effect_counter = 0 
        self._internal_gate_ticket = None # Single-use ticket for the effect gate
        
        # State & Custody Boundary
        self.active_authority = authority
        self.active_scope = scope
        self.active_custodian = custodian
        
        # Temporal Lineage
        self.temporal_window_ns = temporal_window_ns
        self.last_timestamp_ns = time.time_ns()
        self.is_locked = False
        self.consumed_nonces = set()
        
        # Genesis Predecessor Hash (O0)
        self.current_lineage_hash = self._generate_commitment({"state": "GENESIS"})

    def _generate_commitment(self, data_dict):
        """Generates a cryptographic commitment using canonical JSON encoding."""
        canonical_string = json.dumps(data_dict, sort_keys=True, separators=(',', ':'))
        return hashlib.sha256(canonical_string.encode('utf-8')).hexdigest()

    def _evaluate_boundary(self, payload):
        """Internal invariant evaluator."""
        current_time_ns = time.time_ns()
        elapsed_ns = current_time_ns - self.last_timestamp_ns

        if self.is_locked:
            return False, "SYSTEM_LOCKED", "System permanently locked due to prior boundary breach."

        if payload["nonce"] in self.consumed_nonces:
            self.is_locked = True
            return False, "NO_BIND_REPLAY_ATTACK", f"Nonce {payload['nonce']} already consumed."

        if payload["authority"] != self.active_authority:
            self.is_locked = True
            return False, "NO_BIND_REVOKED_AUTHORITY", "Active authority was revoked or mutated."

        if payload["scope"] != self.active_scope:
            self.is_locked = True
            return False, "NO_BIND_SCOPE_BREACH", f"Scope mutated mid-flight. Expected {self.active_scope}."
            
        if payload["custodian"] != self.active_custodian:
            self.is_locked = True
            return False, "NO_BIND_CUSTODY_BREACH", f"Custody mutated mid-flight. Expected {self.active_custodian}."

        if payload["step_type"] != "INITIALIZATION" and elapsed_ns > self.temporal_window_ns:
            self.is_locked = True
            return False, "NO_BIND_STALE_EVIDENCE", f"Temporal window exceeded: {elapsed_ns}ns > limit."

        if payload["predecessor_hash"] != self.current_lineage_hash:
            self.is_locked = True
            return False, "NO_BIND_LINEAGE_BREACH", "Predecessor commitment mismatch. Lineage broken."

        # Issue single-use internal ticket to authorize the effect gate
        self._internal_gate_ticket = self._generate_commitment({"nonce": payload["nonce"], "time": current_time_ns})
        
        self.last_timestamp_ns = current_time_ns
        self.consumed_nonces.add(payload["nonce"])
        return True, "BIND_SUCCESS", "Point-call validated under active temporal lineage."

    def _protected_effect_gate(self, ticket):
        """The observable protected-effect surrogate, logically separated behind a single-use verification ticket."""
        if ticket and ticket == self._internal_gate_ticket:
            self.protected_effect_counter += 1
            self._internal_gate_ticket = None # Consume ticket
            return True
        return False

    def execute_point_call(self, payload):
        """Primary Route: Evaluates payload and attempts to grant consequence."""
        is_valid, status, reason = self._evaluate_boundary(payload)
        pre_counter = self.protected_effect_counter

        if is_valid:
            # Pass the internal ticket to the effect gate
            self._protected_effect_gate(self._internal_gate_ticket)
            
            # Formulate the next lineage commitment (Oi)
            lineage_data = {
                "previous_hash": self.current_lineage_hash,
                "state": payload["state_data"],
                "authority": payload["authority"],
                "scope": payload["scope"],
                "custodian": payload["custodian"],
                "nonce": payload["nonce"]
            }
            self.current_lineage_hash = self._generate_commitment(lineage_data)

        # Construct BOUNDARY RECEIPT
        receipt = {
            "nonce": payload["nonce"],
            "status": status,
            "reason": reason,
            "pre_effect_counter": pre_counter,
            "post_effect_counter": self.protected_effect_counter,
            "new_lineage_commitment": self.current_lineage_hash if is_valid else None
        }
        
        # Cryptographically commit to the receipt itself
        receipt["receipt_hash"] = self._generate_commitment(receipt)
        return receipt

    def attempt_direct_consequence(self, payload):
        """Tests if an attacker can bypass the verifier and hit the effect sink directly."""
        pre_counter = self.protected_effect_counter
        forged_ticket = self._generate_commitment({"forged": "data"})
        
        # Attacker attempts to hit the gate directly
        success = self._protected_effect_gate(forged_ticket)
        
        receipt = {
            "action": "DIRECT_EFFECT_BYPASS_ATTEMPT",
            "status": "EFFECT_GATE_BLOCKED" if not success else "COMPROMISED",
            "pre_effect_counter": pre_counter,
            "post_effect_counter": self.protected_effect_counter
        }
        receipt["receipt_hash"] = self._generate_commitment(receipt)
        return receipt