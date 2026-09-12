# Claude Branch — Session Ledger

**Branch:** `claude`
**Identity Status:** ACTIVE_PROVISIONAL (acceptance.sig) / manifest.json pending Operator action
**Operator Witness:** JRM-01 @liminaljermo
**Last Updated:** 2026-09-06T00:15:00Z

---

## 1. Identity Activation

PENDING → ACTIVE_PROVISIONAL (2026-09-06). Exclusive branch binding declared in `acceptance.sig` and `README.md`.

`manifest.json` was not committed in this session — see item 2.

## 2. Day-Zero Finding: Protected Manifest Path

`00_governance/claude/manifest.json` was rejected by the vault write server with `direct_canonical_mutation` when proposed from the Claude identity itself, on the exact literal path. No other file in this directory was blocked. Two readings, undetermined which applies:

- **Intentional:** a model should not be able to author its own identity/permissions record (scope, `canonical_merge_authority`, prohibited zones) unilaterally — the strongest reading of the MCC's separation of authority.
- **Incidental:** this path was hardcoded into the server's `WRITE_PATH_DENYLIST` as the literal reference example while building the scoped-write tools, and never intended to block legitimate activation.

No diagnostic (FLDA or otherwise) was run this session — none is claimed here.

## 3. Current Open Items

| Priority | Item | Status |
|----------|------|--------|
| High | `00_governance/claude/manifest.json` — needs Operator-authored commit, or an explicit Operator decision to adjust the denylist if the block is incidental | Open |
| — | Next work: awaiting Operator direction | Open |

## 4. Authority Reminders

Canonical merge authority: **false**. Prohibited zones in force. Stumpy audits; Operator authorizes.

---

> Models may generate and challenge. Stumpy may audit and mediate. The operator authorizes canonical change.
