"""
auto_classification_generator package definitions

Author: Christopher Prince
license: Apache License 2.0"
"""

from .common import define_output_file, \
                    keyword_replace, \
                    win_file_split, \
                    filter_win_hidden, \
                    path_check, \
                    running_time, \
                    win_256_check, \
                    export_csv, \
                    export_dict, \
                    export_json, \
                    export_list_txt, \
                    export_ods, \
                    export_xl, \
                    export_xml, \
                    suffix_addition, \
                    suffix_subtraction
from .referenceGen import ReferenceGenerator
from .cli import run_cli,create_parser
from importlib import metadata

__author__ = "Christopher Prince (c.pj.prince@gmail.com)"
__license__ = "Apache License Version 2.0"
__version__ = metadata.version("auto_reference_generator")
