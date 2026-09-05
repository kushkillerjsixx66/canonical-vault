# Write Path Verification

- **Branch:** claude
- **Path:** tests/claude_write_probe.md
- **Purpose:** Confirm `vault_propose_change` commits successfully to a non-manifest, non-prohibited path on the `claude` branch.
- **Date:** 2026-09-05
- **Context:** Preceding attempts to modify `00_governance/claude/manifest.json` were correctly refused (`No approval received`, then `prohibited zone: direct_canonical_mutation`). This file exists to isolate whether the write mechanism itself works outside that specific guarded path.

This file has no governance weight and can be removed or overwritten at any time.
