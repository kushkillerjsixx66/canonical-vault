# Lattice Transmission Protocol

**Version:** 0.1 — Technical Specification  
**Document ID:** LTP-0001  
**Vault Registry:** `VAULT://transmission-layer/LTP-0001/v0.1`  
**Status:** DRAFT — Canonical Review Pending

## Table of Contents

1. Purpose and Scope
2. Governance Foundation
3. Transmission Object Schema
4. Governance Envelope Format
5. Sigil Encoding Rules
6. Multi-Node Behavior
7. Integrity Fields
8. Fault Handling
9. Transmission Rules
10. Versioning
11. Node Responsibilities Matrix
12. Appendices

## 1. Purpose and Scope

### 1.1 Purpose

The Lattice Transmission Protocol (LTP) defines normative rules, formats, and behaviors governing transmission of governed objects between nodes in the Canonical Lattice Network. LTP ensures all transmissions preserve governance integrity, canonical invariants, sigil authenticity, and envelope fidelity across node boundaries.

### 1.2 Scope

LTP governs: Transmission Object (TO) construction and validation; Governance Envelope format and enforcement; Sigil encoding, carriage, and validation; canonical invariant preservation; multi-node routing; fault handling; node roles; and versioning.

LTP does not govern internal node logic, application-layer payload semantics, physical transport implementations, or Vault storage formats.

### 1.3 Normative References

- Canon Lattice Node Spec v0.2 (CLNS-0002)
- Canonical Sigil Grammar v1.0 (CSG-0001)
- Governance Envelope Specification v1.1 (GES-0003)
- Canonical Fault Classification Register v0.3 (CFCR-0004)
- RFC 2119 (keyword conventions: MUST, MUST NOT, SHOULD, MAY)

### 1.4 Defined Terms

## 2. Governance Foundation

### 2.1 Relationship to CLNS-0002

LTP is subordinate to CLNS-0002. All LTP behaviors are bounded by the invariants, node classifications, and governance rules of CLNS-0002. In cases of conflict, CLNS-0002 takes precedence.

### 2.2 Canonical Invariants Preserved by LTP

The following invariants are enforced by LTP across all transmission contexts. Any violation constitutes a canonical breach subject to fault handling per Section 8.

## 3. Transmission Object Schema

### 3.1 Top-Level Schema

```text
TransmissionObject {
  ltp_version:         String             // REQUIRED. MUST be "0.1".
  object_id:           UUID               // REQUIRED. Globally unique TO identifier.
  object_type:         Enum               // REQUIRED. See §3.2.
  governance_envelope: GovernanceEnvelope // REQUIRED. See §4.
  sigil_block:         SigilBlock         // REQUIRED. See §5.
  payload:              PayloadWrapper     // REQUIRED. See §3.3.
  integrity:            IntegrityBlock     // REQUIRED. See §7.
  relay_chain:          [RelayEntry]       // REQUIRED. Empty array if no relay. See §6.3.
  transmission_seal:    SealRecord         // REQUIRED. See §7.2.
  metadata:             TransmissionMeta   // REQUIRED. See §3.4.
}
```

### 3.2 Object Types

### 3.3 Payload Wrapper Schema

```text
PayloadWrapper {
  content_type:      String   // REQUIRED. MIME type or Lattice content type identifier.
  content_encoding:  Enum     // REQUIRED. Values: "raw", "base64", "lattice-encoded"
  content_hash:      String   // REQUIRED. SHA3-256 hash of raw payload content.
  content_length:    Integer  // REQUIRED. Byte length of payload.
  payload_body:      Bytes    // REQUIRED. Encoded payload content.
  payload_schema_id: String   // OPTIONAL. Reference to registered payload schema.
}
```

### 3.4 Transmission Metadata Schema

```text
TransmissionMeta {
  originating_node_id: String   // REQUIRED. Canonical node identifier.
  target_node_id:      String   // REQUIRED. Canonical node identifier.
  lattice_epoch:       Integer  // REQUIRED. Current Lattice Epoch at time of construction.
  canonical_nonce:     String   // REQUIRED. 256-bit hex nonce.
  genesis_hash:        String   // REQUIRED. Genesis Hash of the object's lineage.
  timestamp_utc:       ISO8601  // REQUIRED. UTC timestamp of TO construction.
  priority:            Enum     // REQUIRED. "CRITICAL", "HIGH", "NORMAL", or "LOW"
  ttl_epochs:          Integer  // REQUIRED. Epochs the TO remains valid. 0 = indefinite.
  tags:                [String] // OPTIONAL. Governance or routing tags.
}
```

## 4. Governance Envelope Format

### 4.1 Overview

The Governance Envelope is the authoritative governance record for a TO. It is sealed by the Originating Node and is immutable thereafter. Full compliance with GES-0003 is mandatory.

### 4.2 Schema

```text
GovernanceEnvelope {
  envelope_id:           UUID      // REQUIRED. Unique envelope identifier.
  governance_root:       String    // REQUIRED. E.g., "CLNS-0002".
  governance_version:    String    // REQUIRED. Version of the governing specification.
  envelope_spec:         String    // REQUIRED. E.g., "GES-0003".
  envelope_spec_version: String    // REQUIRED. Version of the envelope spec.
  canonical_authority:   String    // REQUIRED. Canonical authority node identifier.
  sigil_authority:       String    // REQUIRED. E.g., "LATTICE_CORE".
  governance_class:      Enum      // REQUIRED. Governance class per §3.2.
  invariants_asserted:   [String]  // REQUIRED. Invariants asserted as preserved.
  governance_lineage:    [String]  // REQUIRED. Ordered prior envelope IDs.
  sealed_at_epoch:       Integer   // REQUIRED. Lattice Epoch of sealing.
  sealed_at_utc:         ISO8601   // REQUIRED. UTC timestamp of sealing.
  envelope_hash:         String    // REQUIRED. SHA3-256 of canonical envelope fields.
  envelope_seal:         String    // REQUIRED. Ed25519 signature over envelope_hash.
}
```

### 4.3 Sealing Procedure

The Originating Node MUST follow this sequence exactly:

1. Populate all required envelope fields.
2. Serialize to canonical form (lexicographically ordered JSON, no whitespace).
3. Compute SHA3-256, excluding `envelope_hash` and `envelope_seal` fields.
4. Record hash in `envelope_hash`.
5. Sign `envelope_hash` with the Originating Node's Ed25519 private key.
6. Record hex-encoded signature in `envelope_seal`.

### 4.4 Envelope Validation

The Receiving Node MUST perform the following validation steps in order:

1. Verify `governance_root` references a valid governing specification.
2. Verify `envelope_spec` references a recognized envelope specification.
3. Verify `sigil_authority` is a recognized Sigil Authority.
4. Verify `invariants_asserted` covers INVARIANT 1 through INVARIANT 7.
5. Recompute and verify `envelope_hash`.
6. Verify `envelope_seal` against the Originating Node's registered public key.

Any failure MUST trigger fault handling per §8.

## 5. Sigil Encoding Rules

### 5.1 Overview

All sigils MUST conform to CSG-0001 and be carried within a well-formed Sigil Block. The Sigil Block is sealed by the Originating Node and is immutable for the lifetime of the TO.

### 5.2 Sigil Block Schema

```text
SigilBlock {
  sigil_block_id:   UUID         // REQUIRED. Unique Sigil Block identifier.
  sigil_authority:  String       // REQUIRED. Issuing Sigil Authority identifier.
  sigils:           [SigilEntry] // REQUIRED. Must contain at least one entry.
  sigil_block_hash: String       // REQUIRED. SHA3-256 over canonical sigil entries.
  sigil_block_seal: String       // REQUIRED. Sigil Authority's seal over sigil_block_hash.
}

SigilEntry {
  sigil_id:           String   // REQUIRED. Canonical sigil ID per CSG-0001.
  sigil_class:        Enum     // REQUIRED. "AUTHORITY","GOVERNANCE","ROUTING","DIAGNOSTIC","TEMPORAL"
  sigil_value:        String   // REQUIRED. Encoded per sigil_class.
  sigil_scope:        Enum     // REQUIRED. "OBJECT","ENVELOPE","PAYLOAD","NODE","EPOCH"
  sigil_issued_epoch: Integer  // REQUIRED. Epoch of issuance.
  sigil_expiry_epoch: Integer  // OPTIONAL. Epoch of expiry. Omit if non-expiring.
  sigil_chain:        [String] // OPTIONAL. Prior sigil IDs this sigil derives from.
}
```

### 5.3 Sigil Enforcement Rules

### 5.4 Sigil Classes

## 6. Multi-Node Behavior

### 6.1 Node Roles

### 6.2 Relay Chain Entry Schema

```text
RelayEntry {
  relay_node_id:    String  // REQUIRED. Canonical node identifier of Relay Node.
  relay_timestamp:  ISO8601 // REQUIRED. UTC timestamp of relay.
  relay_epoch:      Integer // REQUIRED. Lattice Epoch at relay.
  relay_entry_hash: String  // REQUIRED. SHA3-256 of this entry's canonical fields.
  relay_entry_seal: String  // REQUIRED. Relay Node's seal over relay_entry_hash.
}
```

### 6.3 Relay Chain Integrity Rules

## 7. Integrity Fields

### 7.1 IntegrityBlock Schema

```text
IntegrityBlock {
  payload_hash:      String // REQUIRED. SHA3-256 of raw payload body.
  envelope_hash_ref: String // REQUIRED. Mirrors GovernanceEnvelope.envelope_hash.
  sigil_hash_ref:    String // REQUIRED. Mirrors SigilBlock.sigil_block_hash.
  object_hash:       String // REQUIRED. SHA3-256 over (payload_hash + envelope_hash_ref
                            //            + sigil_hash_ref + canonical TransmissionMeta).
  hash_algorithm:    String // REQUIRED. MUST be "SHA3-256" for LTP v0.1.
}
```

### 7.2 Transmission Seal Schema

```text
SealRecord {
  seal_algorithm:     String  // REQUIRED. MUST be "Ed25519" for LTP v0.1.
  sealed_object_hash: String  // REQUIRED. MUST equal IntegrityBlock.object_hash.
  seal_value:         String  // REQUIRED. Hex-encoded Ed25519 signature.
  seal_key_id:        String  // REQUIRED. Key ID of Originating Node's signing key.
  seal_epoch:         Integer // REQUIRED. Lattice Epoch at sealing.
}
```

### 7.3 Integrity Verification Sequence

The Receiving Node MUST follow this sequence exactly, in order:

1. Verify `payload_hash` against received payload body.
2. Verify `envelope_hash_ref` matches `GovernanceEnvelope.envelope_hash`.
3. Verify `sigil_hash_ref` matches `SigilBlock.sigil_block_hash`.
4. Recompute and verify `object_hash`.
5. Verify `SealRecord.sealed_object_hash` equals `IntegrityBlock.object_hash`.
6. Verify `SealRecord.seal_value` using Originating Node's registered public key.

Any step failure MUST trigger §8 fault handling immediately.

## 8. Fault Handling

### 8.1 Fault Classification

### 8.2 Fault Report Schema

```text
FaultReport {
  fault_code:        String  // REQUIRED. Code per §8.1 and CFCR-0004.
  fault_class:       String  // REQUIRED. Fault class identifier.
  faulted_object_id: UUID    // REQUIRED. object_id of rejected TO.
  faulted_at_node:   String  // REQUIRED. Node ID of detecting node.
  faulted_at_epoch:  Integer // REQUIRED. Lattice Epoch at detection.
  faulted_at_utc:    ISO8601 // REQUIRED. UTC timestamp.
  fault_detail:      String  // REQUIRED. Human-readable description.
  fault_evidence:    Object  // OPTIONAL. Structured evidence (field, expected, received).
  fault_report_hash: String  // REQUIRED. SHA3-256 of canonical fault report.
  fault_report_seal: String  // REQUIRED. Detecting node's seal.
}
```

### 8.3 Fault Handling Procedure

1. Immediately cease processing of the faulted TO.
2. Construct a FaultReport per §8.2.
3. Transmit FaultReport to the Originating Node via a governance-acknowledged return path.
4. If detecting node is a Relay Node, also transmit to the upstream node.
5. Log fault to the node's local governance audit log.
6. CRITICAL faults: quarantine the faulted TO; MUST NOT discard pending governance review.
7. MEDIUM faults: MAY discard after transmitting the FaultReport.

### 8.4 No-Retry Policy

LTP v0.1 does not support retry of faulted transmissions. The Originating Node MUST construct a new TO with a new `object_id`, `canonical_nonce`, and updated `lattice_epoch`.

## 9. Transmission Rules

### 9.1 Construction Rules

### 9.2 Transmission Rules

### 9.3 Receipt Acknowledgment

Upon successful validation, the Receiving Node MUST transmit a GOVERNANCE_ASSERTION TO containing:

- Reference to the accepted `object_id`;
- Attestation of invariant satisfaction;
- Epoch and timestamp of acceptance;
- The Receiving Node's own Transmission Seal.

## 10. Versioning

### 10.1 Version Identification

LTP uses a MAJOR.MINOR scheme. Version 0.x releases are DRAFT and subject to breaking changes without prior notice. Version 1.0 and above are STABLE releases governed by a formal amendment process.

### 10.2 Backward Compatibility

Nodes MUST reject TOs with an unrecognized `ltp_version`.

LTP v0.1 TOs carry no forward compatibility guarantees.

Version negotiation is deferred to the transport or session layer.

### 10.3 Amendment Procedure

Amendments MUST:

- Be initiated as a canonical proposal to the Canonical Lattice Governance Body;
- Reference affected sections and invariants;
- Pass canonical review per CLNS-0002;
- Be published as a new versioned document in the Canonical Vault.

## 11. Node Responsibilities Matrix

## 12. Appendices

### Appendix A — Canonical Hash Construction Reference

Canonical serialization for hash computation MUST follow this procedure:

1. Sort all JSON keys lexicographically (Unicode code point order).
2. Remove all whitespace (spaces, newlines, tabs).
3. Encode strings as UTF-8.
4. Represent integers as JSON numbers with no leading zeros.
5. Hash the resulting byte sequence with SHA3-256.
6. Encode output as lowercase hexadecimal (64 characters).

**Example — Canonical TransmissionMeta serialization:**

```json
{"canonical_nonce":"a3f...","genesis_hash":"b7c...","lattice_epoch":1024,"originating_node_id":"NODE_ALPHA","priority":"NORMAL","target_node_id":"NODE_BETA","timestamp_utc":"2026-09-08T23:51:00Z","ttl_epochs":10}
```

### Appendix B — Sigil Encoding Quick Reference

### Appendix C — Fault Code Quick Reference

### Appendix D — Abbreviations

---

This document is a governed artifact of the Canonical Lattice Network. Reproduction, modification, or distribution outside of the Canonical Vault constitutes a canonical breach subject to governance enforcement under CLNS-0002.