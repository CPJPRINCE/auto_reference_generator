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
