# MCP Propose-Change Test

**Date:** 2026-09-12
**Purpose:** Verify that the Canonical Vault MCP write path can create a governed proposal on the model-specific branch without mutating `main`.

## Change

This document is a deliberately non-canonical test artifact. Its presence demonstrates that `vault_propose_change` can append a commit to the governed proposal branch and that the resulting change can subsequently be exposed through a pull request for human review.

## Governance boundary

- Target branch: `claude`
- Canonical branch: `main`
- This artifact does not modify constitutional, legal, or manifest paths.
- No merge is authorized by this proposal.
- Human approval remains required before canonical integration.

## Expected lifecycle

`MCP proposal → governed branch commit → PR → human review/approval → merge`

This test intentionally validates the proposal boundary rather than canonical mutation.