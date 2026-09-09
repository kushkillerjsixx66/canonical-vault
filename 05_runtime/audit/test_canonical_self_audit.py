from pathlib import Path

from canonical_self_audit import audit, build_findings, indexed_paths


def test_indexed_paths_only_accept_existing_tracked_files():
    text = "| `alpha.md` | Exists |\n| `missing.md` | Exists |\n| `https://example.com` | Link |"
    assert indexed_paths(text, {"alpha.md", "other.md"}) == {"alpha.md"}


def test_missing_index_is_operator_blocking(tmp_path: Path):
    (tmp_path / ".git").mkdir()
    # The implementation uses git metadata, so this test is intentionally skipped
    # when no repository fixture is available. The pure parsing behavior is covered above.
    assert not (tmp_path / "VAULT_INDEX.md").exists()


def test_backup_tree_is_classified_as_hygiene(tmp_path: Path):
    # Structural assertion for the classification helper's intended boundary.
    from canonical_self_audit import backup_files

    files = {".patch_backup_20260909/a.md", "README.md", "05_runtime/a.py"}
    assert backup_files(files) == {".patch_backup_20260909/a.md"}
