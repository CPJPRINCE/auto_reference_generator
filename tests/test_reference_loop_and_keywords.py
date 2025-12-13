import os
import json
import pandas as pd
from auto_reference_generator.reference_generator import ReferenceGenerator


def test_reference_loop_prefix_and_parent_concat():
    rg = ReferenceGenerator('.', prefix='PFX')

    # Case 1: parent not found and level == 0 -> should append prefix
    rg.reference_list = []
    # ensure df exists (empty) so lookup will work
    import pandas as pd
    rg.df = pd.DataFrame(columns=['FullName', 'Ref_Section', 'Parent'])
    rg.reference_loop(ref='1', parent='/no-such-parent', track=1, level=0)
    assert rg.reference_list[-1] == 'PFX'

    # Case 2: parent exists with REF_SECTION and should produce parent_ref + ref when track==1
    # Build a minimal dataframe representing the parent record
    df = pd.DataFrame([
        {'FullName': '/parent', 'Ref_Section': 10, 'Parent': '/grandparent'}
    ])
    rg.df = df
    rg.reference_list = []
    rg.reference_loop(ref='3', parent='/parent', track=1, level=1)
    # Because level > 0 and prefix is set, the final new_ref is prefixed
    assert rg.reference_list[-1] == 'PFX/10/3'


def test_keywords_initialise_and_from_json(tmp_path):
    # Build directory structure
    root = tmp_path / 'kwroot'
    root.mkdir()
    kwdir = root / 'John Smith'
    kwdir.mkdir()
    child = kwdir / 'child.txt'
    child.write_text('x')

    # initialise mode with explicit keyword matching the dirname
    rg1 = ReferenceGenerator(str(root), keywords=['JOHN SMITH'], keywords_mode='initialise')
    df1 = rg1.init_dataframe()

    # find the row for the kwdir and child
    row_dir = df1.loc[df1['FullName'] == str(kwdir)].iloc[0]
    row_child = df1.loc[df1['FullName'] == str(child)].iloc[0]

    # keyword_replace('John Smith', mode='initialise') -> 'JS'
    assert str(row_dir['Ref_Section']) == 'JS'
    assert str(row_child['Archive_Reference']).startswith('JS/')

    # from_json mode
    mapping = {'JOHN SMITH': 'JSM'}
    json_file = tmp_path / 'kw.json'
    json_file.write_text(json.dumps(mapping))

    rg2 = ReferenceGenerator(str(root), keywords=[str(json_file)], keywords_mode='from_json')
    df2 = rg2.init_dataframe()

    row_dir2 = df2.loc[df2['FullName'] == str(kwdir)].iloc[0]
    row_child2 = df2.loc[df2['FullName'] == str(child)].iloc[0]

    assert str(row_dir2['Ref_Section']) == 'JSM'
    assert str(row_child2['Archive_Reference']).startswith('JSM/')


def test_reference_loop_custom_delimiter_and_suffix():
    # Setup ReferenceGenerator without prefix so output is predictable
    rg = ReferenceGenerator('.', prefix=None)
    import pandas as pd
    # parent exists with Ref_Section 10
    rg.df = pd.DataFrame([
        {'FullName': '/parent', 'Ref_Section': 10, 'Parent': '/grandparent'}
    ])
    rg.reference_list = []

    # Test custom delimiter
    rg.reference_loop(ref='3', parent='/parent', track=1, level=1, delimiter='.')
    assert rg.reference_list[-1] == '10.3'

    # Test suffix preserved when in ref string
    rg.reference_list = []
    rg.reference_loop(ref='1_SFX', parent='/parent', track=1, level=1, delimiter='/')
    assert rg.reference_list[-1] == '10/1_SFX'

    # Test track != 1 uses new_ref concatenation and keeps suffix
    rg.reference_list = []
    rg.reference_loop(ref='', parent='/parent', track=2, level=2, new_ref='1_SFX', delimiter='-')
    # parent_ref=10, new_ref should become '10-1_SFX'
    assert rg.reference_list[-1] == '10-1_SFX'
