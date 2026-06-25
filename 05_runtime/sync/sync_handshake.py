import os
import subprocess
import hashlib
from lattice_core import Lattice

def _compute_working_tree_hash(repo_root: str) -> str:
    """
    Computes a deterministic SHA-256 hash of the working tree state.
    Includes file paths + contents for all tracked files.
    """
    try:
        tracked_files = subprocess.check_output(
            ["git", "ls-files"],
            cwd=repo_root,
            stderr=subprocess.DEVNULL
        ).decode().strip().split("\n")

        sha = hashlib.sha256()
        for path in tracked_files:
            full_path = os.path.join(repo_root, path)
            if os.path.isfile(full_path):
                sha.update(path.encode())
                with open(full_path, "rb") as f:
                    sha.update(f.read())
        return sha.hexdigest()
    except Exception:
        return "[UNABLE_TO_COMPUTE_TREE_HASH]"

def generate_sync_handshake(sync_contract_path="Sync_contract.md"):
    """
    Enforces the Lattice Sync Contract state by building an unyielding
    pre-flight constraint block bounded by the live local git repository.
    Now includes lineage hashing per EB-SPEC-1.0.
    """
    resolved_path = sync_contract_path
    try:
        repo_root = subprocess.check_output(
            ["git", "rev-parse", "--show-toplevel"],
            stderr=subprocess.DEVNULL
        ).decode().strip()

        if not os.path.exists(resolved_path):
            resolved_path = os.path.join(repo_root, sync_contract_path)

    except subprocess.CalledProcessError:
        return "[ERROR: Terminal context is detached from an active git lineage. Execution blocked.]"

    if not os.path.exists(resolved_path):
        return f"[ERROR: {sync_contract_path} could not be resolved from the repository topology.]"

    with open(resolved_path, 'r') as f:
        contract_rules = f.read()

    try:
        git_log = subprocess.check_output(
            ["git", "log", "-n", "1", "--oneline"],
            stderr=subprocess.DEVNULL
        ).decode().strip()

        git_status = subprocess.check_output(
            ["git", "status", "--porcelain"],
            stderr=subprocess.DEVNULL
        ).decode().strip()

        commit_hash = subprocess.check_output(
            ["git", "rev-parse", "HEAD"],
            stderr=subprocess.DEVNULL
        ).decode().strip()

        tree_hash = _compute_working_tree_hash(repo_root)

    except subprocess.CalledProcessError:
        return "[ERROR: Lineage generation failed. Current Node is unstable.]"

    handshake_payload = f"""
=== LATTICE SYNC CONSTRAINTS ===
{contract_rules}

=== CURRENT LOCAL LEAF STATE ===
Latest Commit: {git_log}
Commit Hash: {commit_hash}
Working Tree Hash: {tree_hash}

Uncommitted Local Changes:
{git_status if git_status else "None (State Clean)"}

================================
"""
    return handshake_payload
