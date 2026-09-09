from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))

from canonical_self_audit import indexed_paths  # noqa: E402


def test_indexed_paths_only_accept_existing_tracked_files():
    text = "| `alpha.md` | Exists |\n| `missing.md` | Exists |\n| `https://example.com` | Link |"
    assert indexed_paths(text, {"alpha.md", "other.md"}) == {"alpha.md"}


def test_backup_tree_is_classified_as_hygiene():
    from canonical_self_audit import backup_files

    files = {".patch_backup_20260909/a.md", "README.md", "05_runtime/a.py"}
    assert backup_files(files) == {".patch_backup_20260909/a.md"}
