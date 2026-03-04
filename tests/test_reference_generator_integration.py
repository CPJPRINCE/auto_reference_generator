import os
from auto_reference_generator.reference_generator import ReferenceGenerator


def _to_abs(p):
    return os.path.abspath(str(p))


def test_reference_generator_integration(tmp_path):
    """Create a small directory tree and assert Archive_Reference values."""
    root = tmp_path / "root"
    root.mkdir()

    # Top-level directories
    a = root / "A"
    a.mkdir()
    b = root / "B"
    b.mkdir()

    # Files in A
    a1 = a / "a1.txt"
    a1.write_text("a1")
    a2 = a / "a2.txt"
    a2.write_text("a2")

    # Nested in B
    b1 = b / "B1"
    b1.mkdir()
    b1f = b1 / "b1.txt"
    b1f.write_text("b1")

    # Root file
    rf = root / "rootfile.txt"
    rf.write_text("root")

    rg = ReferenceGenerator(str(root), output_format="dict", meta_dir_flag=False)
    records = rg.main()

    # Build lookup by FullName (PATH_FIELD = FullName) using normalized absolute paths
    lookup = {os.path.normpath(os.path.abspath(r['FullName'])): r for r in records}

    # Helper to get archive ref by absolute path
    def ref_for(p):
        return lookup[os.path.normpath(os.path.abspath(str(p)))]['Archive_Reference']

    # Root (initial parse used ref=0 and level=0) -> string '0'
    assert ref_for(root) == '0'

    # Top-level directories A and B should have refs '1' and '2' (order by name/scan order)
    assert ref_for(a) == '1'
    assert ref_for(b) == '2'

    # Files in A should be '1/1' and '1/2'
    assert ref_for(a1) == '1/1'
    assert ref_for(a2) == '1/2'

    # B1 (subdir of B) should be '2/1' and its file '2/1/1'
    assert ref_for(b1) == '2/1'
    assert ref_for(b1f) == '2/1/1'

    # Root file should be '3' because it comes after A and B in the top level
    assert ref_for(rf) == '3'
