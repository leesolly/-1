from pathlib import Path
from zipfile import ZipFile

from src.utils.archive import create_project_archive


def _build_sample_project(root: Path) -> Path:
    project_root = root / "sample"
    (project_root / "src").mkdir(parents=True)
    (project_root / "tests").mkdir()
    (project_root / ".git").mkdir()
    (project_root / "__pycache__").mkdir()
    (project_root / "src" / "main.py").write_text("print('hello')\n", encoding="utf-8")
    (project_root / "tests" / "test_sample.py").write_text(
        "def test_sample():\n    assert True\n", encoding="utf-8"
    )
    (project_root / "__pycache__" / "ignored.pyc").write_text("", encoding="utf-8")
    return project_root


def test_archive_includes_project_files(tmp_path: Path) -> None:
    project_root = _build_sample_project(tmp_path)
    archive_path = create_project_archive(project_root, filename="bundle.zip")
    assert archive_path.exists()
    assert archive_path.parent == project_root / "dist"
    with ZipFile(archive_path) as archive:
        names = set(archive.namelist())
    assert "src/main.py" in names
    assert "tests/test_sample.py" in names
    assert "__pycache__/ignored.pyc" not in names


def test_archive_can_skip_tests(tmp_path: Path) -> None:
    project_root = _build_sample_project(tmp_path)
    archive_path = create_project_archive(
        project_root,
        filename="bundle_without_tests.zip",
        include_tests=False,
    )
    with ZipFile(archive_path) as archive:
        assert not any(name.startswith("tests/") for name in archive.namelist())
