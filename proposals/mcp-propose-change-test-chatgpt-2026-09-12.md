# MCP Propose-Change Test: ChatGPT Branch

**Date:** 2026-09-12
**Purpose:** Verify that the Canonical Vault MCP write path can create a governed proposal on the `chatgpt` branch without mutating `main`.

## Change

This is a deliberately non-canonical test artifact. Its presence is intended to verify that the MCP proposal interface accepts `chatgpt` as a governed model-specific write branch.

## Governance boundary

- Target branch: `chatgpt`
- Canonical branch: `main`
- This artifact does not modify constitutional, legal, or manifest paths.
- No merge is authorized by this proposal.
- Human approval remains required before canonical integration.

## Expected lifecycle

`MCP proposal → chatgpt branch commit → PR → human review/approval → merge`
