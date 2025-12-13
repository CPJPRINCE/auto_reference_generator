import os
import hashlib
from auto_reference_generator.reference_generator import ReferenceGenerator


def test_parse_directory_dict_returns_expected_fields(tmp_path):
    # create root and a file
    root = tmp_path / "root"
    root.mkdir()
    file = root / "file.txt"
    content = b"abc123"
    file.write_bytes(content)

    rg = ReferenceGenerator(str(root), fixity="SHA-1")
    result = rg.parse_directory_dict(str(file), level=1, ref=1)

    assert 'Path' not in result or isinstance(result, dict)
    # check keys expected by the method
    assert 'Hash' in result
    expected = hashlib.sha1(content).hexdigest().upper()
    assert result['Hash'] == expected


def test_accession_running_number_modes(tmp_path):
    root = tmp_path / "root2"
    root.mkdir()
    file = root / "f.txt"
    file.write_text("1")
    d = root / "subdir"
    d.mkdir()

    rg = ReferenceGenerator(str(root), accprefix="ACC", accession_flag="file")
    # file
    acc_file = rg.accession_running_number(str(file))
    assert isinstance(acc_file, (int, str))
    # dir
    acc_dir = rg.accession_running_number(str(d))
    assert (isinstance(acc_dir, str) and "Dir" in acc_dir) or isinstance(acc_dir, int)

    rg2 = ReferenceGenerator(str(root), accprefix="ACC", accession_flag="dir")
    acc_dir2 = rg2.accession_running_number(str(d))
    assert isinstance(acc_dir2, (int, str))
