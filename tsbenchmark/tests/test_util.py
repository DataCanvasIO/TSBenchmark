from tsbenchmark.util import is_safe_dir_name


def test_is_safe_dir_name():
    assert is_safe_dir_name("abc")
    assert is_safe_dir_name("_abc")
    assert is_safe_dir_name("-abc_")
    assert is_safe_dir_name("123abc")
    assert is_safe_dir_name("_1-234_")

    assert not is_safe_dir_name("ab c123")
    assert not is_safe_dir_name("中abc")
    assert not is_safe_dir_name("$kss")
