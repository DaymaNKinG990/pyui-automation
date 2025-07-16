from pathlib import Path
from pyui_automation.utils import file as file_utils

def test_ensure_dir_creates_and_returns(tmp_path):
    d = tmp_path / "subdir"
    result = file_utils.ensure_dir(d)
    assert result.exists() and result.is_dir()

def test_ensure_dir_existing(tmp_path):
    d = tmp_path / "existing"
    d.mkdir()
    result = file_utils.ensure_dir(d)
    assert result == d

def test_get_temp_dir_exists():
    temp_dir = file_utils.get_temp_dir()
    assert temp_dir.exists() and temp_dir.is_dir()

def test_get_temp_file_unique():
    f1 = file_utils.get_temp_file()
    f2 = file_utils.get_temp_file()
    assert f1 != f2
    assert isinstance(f1, Path)

def test_safe_remove_file(tmp_path):
    f = tmp_path / "f.txt"
    f.write_text("abc")
    assert file_utils.safe_remove(f) is True
    assert not f.exists()

def test_safe_remove_dir(tmp_path):
    d = tmp_path / "d"
    d.mkdir()
    (d / "f").write_text("x")
    assert file_utils.safe_remove(d) is True
    assert not d.exists()

def test_safe_remove_nonexistent(tmp_path):
    f = tmp_path / "nope.txt"
    assert file_utils.safe_remove(f) is False

def test_list_files_pattern(tmp_path):
    (tmp_path / "a.txt").write_text("1")
    (tmp_path / "b.log").write_text("2")
    files = file_utils.list_files(tmp_path, "*.txt")
    assert any(f.name == "a.txt" for f in files)
    assert all(isinstance(f, Path) for f in files)

def test_copy_file_success(tmp_path):
    src = tmp_path / "src.txt"
    dst = tmp_path / "dst.txt"
    src.write_text("data")
    assert file_utils.copy_file(src, dst) is True
    assert dst.read_text() == "data"

def test_copy_file_no_overwrite(tmp_path):
    src = tmp_path / "src.txt"
    dst = tmp_path / "dst.txt"
    src.write_text("data")
    dst.write_text("old")
    assert file_utils.copy_file(src, dst, overwrite=False) is False
    assert dst.read_text() == "old"

def test_copy_file_with_overwrite(tmp_path):
    src = tmp_path / "src.txt"
    dst = tmp_path / "dst.txt"
    src.write_text("data")
    dst.write_text("old")
    assert file_utils.copy_file(src, dst, overwrite=True) is True
    assert dst.read_text() == "data"

def test_copy_file_nonexistent_src(tmp_path):
    src = tmp_path / "no.txt"
    dst = tmp_path / "dst.txt"
    assert file_utils.copy_file(src, dst) is False

def test_move_file_success(tmp_path):
    src = tmp_path / "src.txt"
    dst = tmp_path / "dst.txt"
    src.write_text("data")
    assert file_utils.move_file(src, dst) is True
    assert dst.read_text() == "data"
    assert not src.exists()

def test_move_file_no_overwrite(tmp_path):
    src = tmp_path / "src.txt"
    dst = tmp_path / "dst.txt"
    src.write_text("data")
    dst.write_text("old")
    assert file_utils.move_file(src, dst, overwrite=False) is False
    assert src.exists() and dst.read_text() == "old"

def test_move_file_with_overwrite(tmp_path):
    src = tmp_path / "src.txt"
    dst = tmp_path / "dst.txt"
    src.write_text("data")
    dst.write_text("old")
    assert file_utils.move_file(src, dst, overwrite=True) is True
    assert dst.read_text() == "data"
    assert not src.exists()

def test_move_file_nonexistent_src(tmp_path):
    src = tmp_path / "no.txt"
    dst = tmp_path / "dst.txt"
    assert file_utils.move_file(src, dst) is False

def test_get_file_size_existing(tmp_path):
    f = tmp_path / "f.txt"
    f.write_text("abc")
    assert file_utils.get_file_size(f) == 3

def test_get_file_size_nonexistent(tmp_path):
    f = tmp_path / "no.txt"
    assert file_utils.get_file_size(f) is None

def test_is_file_empty_true(tmp_path):
    f = tmp_path / "empty.txt"
    f.write_text("")
    assert file_utils.is_file_empty(f) is True

def test_is_file_empty_false(tmp_path):
    f = tmp_path / "notempty.txt"
    f.write_text("abc")
    assert file_utils.is_file_empty(f) is False

def test_is_file_empty_nonexistent(tmp_path):
    f = tmp_path / "no.txt"
    assert file_utils.is_file_empty(f) is True 