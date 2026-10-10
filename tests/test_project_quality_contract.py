from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


def test_quality_contract_files_exist():
    assert (REPO_ROOT / "Makefile").exists()
    assert (REPO_ROOT / ".github" / "workflows" / "ci.yml").exists()

    readme = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
    assert "make test" in readme
    assert "make lint" in readme
    assert "make ci" in readme

    makefile = (REPO_ROOT / "Makefile").read_text(encoding="utf-8")
    assert "lint:" in makefile
