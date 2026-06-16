#!/bin/bash
# canonical-vault — GitHub init and push script
# Run from the directory CONTAINING canonical-vault/
# Usage: bash push.sh <github-username> [repo-name]

set -e

GITHUB_USER="${1:?Usage: bash push.sh <github-username> [repo-name]}"
REPO_NAME="${2:-canonical-vault}"
REPO_DIR="$(dirname "$0")"

echo "=== canonical-vault push ==="
echo "User: $GITHUB_USER"
echo "Repo: $REPO_NAME"
echo ""

cd "$REPO_DIR"

# Init
git init
git add .
git commit -m "init: canonical vault scaffold

- 00_governance: Constitution v1.1, Operator Manual v0.2
- 01_sovereignty: SICA-001
- 02_epistemic_substrate: Bilateralism & Truth Routing, Bilateral Runtime Patterns
- 03_vault_pipeline: Vault Chain Spec, Orchestration Contract Ω-11
- 04_system_spec: Lattice Unified Spec (root anchor, 2026-06-11)
- 05_runtime: lattice_runtime.py (source)
- 06_ip_legal: IP Attorney Brief (privileged)
- VAULT_INDEX.md, README.md"

# Create repo on GitHub (requires gh CLI authenticated)
echo ""
echo "Creating GitHub repo..."
gh repo create "$GITHUB_USER/$REPO_NAME" --private --source=. --remote=origin --push

echo ""
echo "Done. Repo live at: https://github.com/$GITHUB_USER/$REPO_NAME"
echo ""
echo "=== Pending (manual steps) ==="
echo "1. Download and unzip from Drive, place in 05_runtime/:"
echo "   - lattice_cli_project.zip  → 05_runtime/lattice_cli_project/"
echo "   - lattice_runtime_cli.zip  → 05_runtime/lattice_runtime_cli/"
echo "   - LMES_v1.1.zip            → 05_runtime/LMES_v1.1/"
echo ""
echo "2. Download binary files from Drive and commit:"
echo "   - 02_epistemic_substrate/Neuralese_Lexicon.docx"
echo "   - 02_epistemic_substrate/Empirical_Doctrine.pdf"
echo "   - 00_governance/playbook/Operator_Playbook_Omega-12.pdf"
echo "   - 04_system_spec/appendices/*.pdf"
echo "   - exports/SICA-001.pdf"
echo ""
echo "3. Pull remaining Drive docs not fetched (see VAULT_INDEX.md pending actions)"
