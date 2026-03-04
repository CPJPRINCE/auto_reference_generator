import hashlib
import tempfile
from auto_reference_generator.hash import HashGenerator


def test_hash_generator_sha1(tmp_path):
    content = b"hello world" * 10
    file_path = tmp_path / "sample.bin"
    file_path.write_bytes(content)

    hg = HashGenerator()  # default SHA-1
    digest = hg.hash_generator(str(file_path))

    expected = hashlib.sha1(content).hexdigest().upper()
    assert digest == expected


def test_hash_generator_md5(tmp_path):
    content = b"another test content"
    file_path = tmp_path / "sample2.bin"
    file_path.write_bytes(content)

    hg = HashGenerator(algorithm="MD5")
    digest = hg.hash_generator(str(file_path))

    expected = hashlib.md5(content).hexdigest().upper()
    assert digest == expected


def test_hash_generator_multithreaded_sha1(tmp_path):
    contents = {
        "a.bin": b"file-a" * 100,
        "b.bin": b"file-b" * 200,
        "c.bin": b"file-c" * 300,
    }
    paths = []
    for name, data in contents.items():
        file_path = tmp_path / name
        file_path.write_bytes(data)
        paths.append(str(file_path))

    hg = HashGenerator(algorithm="SHA-1")
    single = {p: hg.hash_generator(p) for p in paths}
    multi = hg.hash_generator_multithread(paths, max_workers = 2)

    assert single == multi
