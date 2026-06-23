"""
register_libraries.lym의 순수 Python 유틸리티 함수 단위 테스트.
pya 없이 실행 가능한 로직만 테스트한다.
"""
import os
import pytest

from lib_utils import (
    find_repo_root,
    get_layout_files,
    is_lfs_pointer,
    LFS_POINTER_MAX_BYTES,
)


class TestFindRepoRoot:
    def test_finds_root_from_child_dir(self, tmp_path):
        repo = tmp_path / "myrepo"
        repo.mkdir()
        (repo / ".git").mkdir()
        child = repo / "macros"
        child.mkdir()
        fake_file = child / "macro.lym"
        fake_file.write_text("content")

        result = find_repo_root(str(fake_file))
        assert result == str(repo)

    def test_returns_none_when_no_git_dir(self, tmp_path):
        fake_file = tmp_path / "somefile.py"
        fake_file.write_text("content")
        result = find_repo_root(str(fake_file))
        assert result is None

    def test_finds_root_from_deeply_nested_file(self, tmp_path):
        repo = tmp_path / "repo"
        repo.mkdir()
        (repo / ".git").mkdir()
        deep = repo / "a" / "b" / "c"
        deep.mkdir(parents=True)
        fake_file = deep / "file.py"
        fake_file.write_text("x")

        result = find_repo_root(str(fake_file))
        assert result == str(repo)


class TestIsLfsPointer:
    def test_small_file_is_lfs_pointer(self, tmp_path):
        f = tmp_path / "pointer.oas"
        f.write_text("version https://git-lfs.github.com/spec/v1\noid sha256:abc\nsize 12345\n")
        assert is_lfs_pointer(str(f)) is True

    def test_large_file_is_not_lfs_pointer(self, tmp_path):
        f = tmp_path / "real.oas"
        f.write_bytes(b"\x00" * 300)
        assert is_lfs_pointer(str(f)) is False

    def test_boundary_one_below_is_pointer(self, tmp_path):
        f = tmp_path / "boundary.oas"
        f.write_bytes(b"\x00" * (LFS_POINTER_MAX_BYTES - 1))
        assert is_lfs_pointer(str(f)) is True

    def test_boundary_at_threshold_is_not_pointer(self, tmp_path):
        f = tmp_path / "boundary2.oas"
        f.write_bytes(b"\x00" * LFS_POINTER_MAX_BYTES)
        assert is_lfs_pointer(str(f)) is False


class TestGetLayoutFiles:
    def test_returns_oas_files(self, tmp_path):
        (tmp_path / "a.oas").write_bytes(b"\x00" * 300)
        (tmp_path / "b.oas").write_bytes(b"\x00" * 300)
        result = get_layout_files(str(tmp_path))
        names = [os.path.basename(f) for f in result]
        assert "a.oas" in names
        assert "b.oas" in names

    def test_oas_takes_priority_over_gds_same_name(self, tmp_path):
        (tmp_path / "chip.oas").write_bytes(b"\x00" * 300)
        (tmp_path / "chip.gds").write_bytes(b"\x00" * 300)
        result = get_layout_files(str(tmp_path))
        names = [os.path.basename(f) for f in result]
        assert "chip.oas" in names
        assert "chip.gds" not in names

    def test_gds_included_when_no_oas_collision(self, tmp_path):
        (tmp_path / "a.oas").write_bytes(b"\x00" * 300)
        (tmp_path / "b.gds").write_bytes(b"\x00" * 300)
        result = get_layout_files(str(tmp_path))
        names = [os.path.basename(f) for f in result]
        assert "a.oas" in names
        assert "b.gds" in names

    def test_empty_dir_returns_empty_list(self, tmp_path):
        result = get_layout_files(str(tmp_path))
        assert result == []

    def test_nonexistent_dir_returns_empty_list(self):
        result = get_layout_files("/nonexistent/path/layouts")
        assert result == []
