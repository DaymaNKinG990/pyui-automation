import pytest
import numpy as np
from pyui_automation.core.utils import retry, ensure_dir, get_temp_path, save_image, load_image, compare_images

def test_retry_success_on_first_try():
    calls = []
    @retry(attempts=3, delay=0)
    def func():
        calls.append(1)
        return 42
    assert func() == 42
    assert len(calls) == 1

def test_retry_success_on_second_try():
    calls = []
    @retry(attempts=3, delay=0)
    def func():
        if not calls:
            calls.append(1)
            raise ValueError('fail')
        return 99
    assert func() == 99
    assert len(calls) == 1

def test_retry_raises_on_all_failures():
    @retry(attempts=2, delay=0, exceptions=(ValueError,))
    def func():
        raise ValueError('fail')
    with pytest.raises(ValueError):
        func()

def test_ensure_dir_creates(tmp_path):
    d = tmp_path / 'newdir'
    assert not d.exists()
    res = ensure_dir(d)
    assert d.exists()
    assert res == d

def test_ensure_dir_existing(tmp_path):
    d = tmp_path
    res = ensure_dir(d)
    assert res == d

def test_get_temp_path_unique():
    p1 = get_temp_path()
    p2 = get_temp_path()
    assert p1 != p2

def test_get_temp_path_with_suffix():
    p = get_temp_path('.txt')
    assert p.suffix == '.txt'

def test_save_and_load_image(tmp_path):
    arr = np.ones((10, 10, 3), dtype=np.uint8) * 255
    f = tmp_path / 'img.png'
    save_image(arr, str(f))
    loaded = load_image(str(f))
    assert loaded is not None
    assert loaded.shape[0] == 10

def test_load_image_nonexistent():
    assert load_image('nonexistent_file.png') is None

def test_compare_images_equal():
    arr = np.ones((5, 5, 3), dtype=np.uint8) * 100
    assert compare_images(arr, arr.copy(), threshold=0.9) is True

def test_compare_images_different_shape():
    arr1 = np.ones((5, 5, 3), dtype=np.uint8)
    arr2 = np.ones((6, 5, 3), dtype=np.uint8)
    assert compare_images(arr1, arr2) is False

def test_compare_images_below_threshold():
    arr1 = np.zeros((5, 5, 3), dtype=np.uint8)
    arr2 = np.ones((5, 5, 3), dtype=np.uint8) * 255
    assert compare_images(arr1, arr2, threshold=0.99) is False 

def test_save_image_invalid_type(tmp_path):
    with pytest.raises(Exception):
        save_image('not_an_array', str(tmp_path / 'img.png'))

def test_compare_images_invalid_type():
    arr = np.ones((5, 5, 3), dtype=np.uint8)
    with pytest.raises(Exception):
        compare_images(arr, 'not_an_array')
    with pytest.raises(Exception):
        compare_images('not_an_array', arr)

def test_retry_invalid_attempts():
    with pytest.raises(Exception):
        @retry(attempts=0)
        def func():
            return 1
        func()

def test_ensure_dir_invalid_type():
    with pytest.raises(Exception):
        ensure_dir('not_a_path')

def test_get_temp_path_invalid_suffix():
    with pytest.raises(Exception):
        get_temp_path(123) 