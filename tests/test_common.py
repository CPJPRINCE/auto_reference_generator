import os
import tempfile
from auto_reference_generator.common import define_output_file, keyword_replace


def test_define_output_file_creates_dirs(tmp_path):
    output_path = tmp_path / "out"
    base = tmp_path / "rootdir"
    base.mkdir()
    output_file = define_output_file(str(output_path), str(base), meta_dir_name="meta_test", meta_dir_flag=True, output_suffix="_SFX", output_format="csv")

    # dirs should be created and path should end with the basename + suffix + extension
    assert os.path.isdir(str(output_path / "meta_test"))
    assert output_file.endswith(os.path.basename(str(base)) + "_SFX.csv")


def test_keyword_replace_initialise_and_firstletters():
    text = "John Smith"
    assert keyword_replace(text, mode="initialise") == "JS"
    # abbreviation_number here controls split behavior, for 1 it still returns both initials
    assert keyword_replace(text, mode="initialise", abbreviation_number=1) == "JS"
    assert keyword_replace(text, mode="firstletters", abbreviation_number=3) == "JOH"
