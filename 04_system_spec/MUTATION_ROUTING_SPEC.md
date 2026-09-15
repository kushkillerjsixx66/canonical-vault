# Mutation Routing Specification

## Purpose
Define the governed path by which model-originated mutations enter the Canonical Vault.

## Constitutional Rule
Model-originated changes are never written directly to the canonical `main` branch. A mutation is proposed on an authorized model branch and then surfaced through a pull request for human/operator approval.

## Required Flow
1. Model identifies a proposed mutation.
2. Governance layer validates the requested mutation against branch, path, and authority constraints.
3. The proposal is committed to the authorized model branch.
4. A pull request is opened against `main`.
5. A human/operator reviews and approves or rejects the pull request.
6. Only the approved pull request may enter canonical state.

## Current MCP Contract
`vault_propose_change` creates a commit on a governed non-canonical branch. It does not merge to `main` and has no merge capability. `vault_open_pr` is the subsequent operation required to surface the proposal for approval.

## Branch Isolation
Each model should operate on its designated governed branch. The live MCP schema must enforce the intended model-to-branch mapping rather than relying solely on environment-variable configuration.

## Authority Boundary
The MCP server may create a proposal commit and open a pull request, but it must not autonomously merge the proposal into canonical state.

## Audit Requirements
Every mutation proposal should preserve:
- source branch
- target branch
- commit SHA
- pull request identifier
- proposer/model identity
- commit message
- affected path
- operator approval state

## Invariant
**No model-originated mutation becomes canonical without an explicit operator approval boundary.**
