# Vault Pipeline Index  
*Governed ingestion → transformation → Vault lifecycle engine*

The Vault Pipeline is the governed system that ingests raw capture, transforms it into structured artifacts, and hands it off to the Vault for commit → review → canonization.

This index provides a unified entry point into all pipeline documents.

---

## Core Documents

- **pipeline_model.yaml** — structural model of the pipeline  
- **pipeline_stages.md** — stage-by-stage execution model  
- **capture_contract.yaml** — rules for ingesting raw capture  
- **transformation_contract.yaml** — rules for structuring artifacts  
- **vault_handoff_contract.yaml** — rules for delivering artifacts to the Vault  
- **pipeline_constraints.yaml** — constraints on pipeline behavior  
- **pipeline_lifecycle.md** — lifecycle rules for pipeline execution  
- **pipeline_events.log** — lineage and event log  
- **README.md** — overview of the pipeline

---

## Pipeline Hierarchy

1. Capture Contract  
2. Transformation Contract  
3. Vault Handoff Contract  
4. Pipeline Constraints  
5. Pipeline Lifecycle  
6. Pipeline Model  

---

## Purpose

The Vault Pipeline ensures:

- governed ingestion  
- reversible transformation  
- drift detection  
- lineage integrity  
- safe Vault handoff  
- compliance with Ω‑13, Ω‑14, AMP, and invariants  

It is the **arterial system** of the Lattice.
