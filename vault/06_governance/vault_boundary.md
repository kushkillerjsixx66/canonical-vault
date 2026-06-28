# Vault Governance Boundary
Version: 1.0
Status: Active
Operator: opID JRM‑01

## Purpose
Define the explicit governance boundary for the Vault subsystem to prevent altitude collapse, responsibility drift, and unauthorized domain expansion.

## Domain Responsibilities
- **Lineage — Preservation Only**  
  Vault records ancestry, versions, and drift states.  
  Vault does not interpret lineage.

- **Artifacts — Storage Only**  
  Vault stores modules, transforms, handlers, and CLI surfaces.  
  Vault does not generate or mutate artifacts.

- **Operator Identity — Record Only**  
  Vault maintains opID JRM‑01 and associated metadata.  
  Vault does not interpret operator intent or posture.

## Prohibitions
Vault must never:
- Allocate operator attention  
- Surface necessities (Pulse domain)  
- Evaluate decisions (Crossroad domain)  
- Detect drift (Sentinel domain)  
- Generate modules (Implementation seam)  
- Rewrite governance (Constitution layer)  
- Interpret operator intent (Operator seam)

## Interfaces
- **Read-only** to Pulse, Crossroad, Sentinel  
- **Write-only** from Implementation seam  
- **Operator writes** allowed only via explicit posture declaration

## Reversibility
All changes to this file must:
- Be operator‑initiated  
- Be lineage‑tracked  
- Preserve prior versions  
- Maintain strict reversibility

## Notes
This boundary prevents Vault from becoming a gravitational sink and ensures subsystem differentiation across the Lattice.
