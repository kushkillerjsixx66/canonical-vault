# Claude Branch — MCP Write Verification

**origin.model:** claude
**origin.branch:** claude
**origin.timestamp:** 2026-09-12T10:17:01-04:00
**lineage.transmission:** direct MCP call via `vault_propose_change`, explicit `branch="claude"` (not relying on server default)

## Purpose

Live diagnostic write, run at operator request in the course of investigating
branch-sovereignty behavior and a suspected PR-layer defect surfaced via the
ChatGPT connector (see: `vault_open_pr` resolving to `grok` on an unconfirmed
`head` argument).

## What this confirms

If this commit landed on `claude` (not `main`, not any other branch), it
verifies against the live deployment that:

- `vault_propose_change` correctly honors an explicit `branch` parameter
  rather than silently falling back to the server default (`grok`).
- Path/branch coherence held: this path is under `vault/claude/`, and the
  target branch is `claude` — matching, as required by the Model
  Contribution Contract.
- This deployment's `WRITE_BRANCH_ALLOWLIST` is unlocked (multi-model) at
  the time of this write, consistent with the schema Claude was served
  this session.

This artifact does not confirm anything about `vault_open_pr`'s branch
resolution — that requires a separate, explicit test of that tool.

**Canonical authority:** this branch is a controlled divergence surface.
This commit confers no canonical authority and requires `vault_open_pr` +
human merge review before any integration into `main`.
