# 05_runtime  
*Governed execution layer of the Lattice*
## Lattice Runtime Adapter (Canonical)

All model calls must pass through `runtime/adapter/canonical_adapter.py`.

The runtime layer defines:

- scheduling  
- execution  
- drift monitoring  
- reversibility  
- envelope enforcement  
- lineage emission  

## Lattice Runtime Adapter (Canonical)

All model calls must pass through `runtime/adapter/canonical_adapter.py`.

- Input: `runtime/adapter/contracts/request_envelope.json`
- Output: `runtime/adapter/contracts/response_envelope.json`
- Governance: `runtime/governance/engine.py`
- Lineage: `lineage/` (to be wired)
- Evals: `evals/` (to be wired)
This layer ensures:

- safe execution  
- reversible operations  
- drift detectability  
- envelope compliance  
- lineage integrity  

It is the **execution engine** of the Lattice.
