"""
Common Tools used in both Opex Manifest and Auto Reference modules.

author: Christopher Prince
license: Apache License 2.0"
"""

import os, time, sys, stat, json, logging
import pandas as pd
from typing import Optional, Union
from datetime import datetime

logger = logging.getLogger(__name__)


def path_check(path: str):
    if os.path.exists(path):
        pass
    else:
        os.makedirs(path)

def define_output_file(output_path: str, output_name: str, meta_dir_name: str = 'meta', meta_dir_flag: Optional[bool] = True, output_suffix: Optional[str] = None, output_format: str = "xlsx"):
    path_check(output_path)
    if meta_dir_flag:
        path_check(os.path.join(output_path,meta_dir_name))
        if output_suffix is None:
            output_file = os.path.join(output_path,meta_dir_name,str(os.path.basename(output_name)) + "." + output_format)
        else:
            output_file = os.path.join(output_path,meta_dir_name,str(os.path.basename(output_name)) + output_suffix + "." + output_format)
    else:
        if output_suffix is None:
            output_file = os.path.join(output_path,str(os.path.basename(output_name)) + "." + output_format)
        else:
            output_file = os.path.join(output_path,str(os.path.basename(output_name)) + output_suffix + "." + output_format)
    return output_file

def export_list_txt(txt_list: list, output_filename: str):
    try: 
        with open(output_filename,'w') as writer:
            for line in txt_list:
                writer.write(f"{line}\n")
        logger.info(f"Saved file to: {output_filename}")
    except PermissionError as e:
        logger.warning(f'File {e} failed to open; waiting 10 seconds to try again...')
        time.sleep(10)
        export_list_txt(txt_list, output_filename)

def export_csv(df: pd.DataFrame, output_filename: str, sep: str = ",", index: bool = False):
    try:
        df.to_csv(output_filename,index = index, sep = sep, encoding = "utf-8")
        logger.info(f"Saved to: {output_filename}")    
    except ModuleNotFoundError:
        logger.warning('Pandas module not found, cannot export to csv. Please install via: pip install pandas')
    except PermissionError as e:
        logger.warning(f'File {e} failed to open; waiting 10 seconds to try again...')
        time.sleep(10)
        export_csv(df, output_filename, sep = sep, index = index)

def export_json(df: pd.DataFrame, output_filename: str, orient: str = 'index'):
    try:
        df.to_json(output_filename,orient=orient, indent=4)
        logger.info(f"Saved to: {output_filename}")    
    except ModuleNotFoundError:
        logger.warning('Pandas Module not found, cannot export to json. Please install via: pip install pandas')
        raise SystemExit()
    except PermissionError as e:
        logger.warning(f'File {e} failed to open; waiting 10 seconds to try again...')
        time.sleep(10)
        export_json(df, output_filename, orient = orient)

def export_xml(df: pd.DataFrame, output_filename: str, index: bool = False):
    try:
        df.to_xml(output_filename, index = index)
        logger.info(f"Saved to: {output_filename}")    
    except ModuleNotFoundError:
        logger.warning('lxml Module not found, cannot export to xml, please install via: pip install lxml')
        raise SystemExit()
    except PermissionError as e:
        logger.warning(f'File {e} failed to open; waiting 10 seconds to try again...')
        time.sleep(10)
        export_xml(df, output_filename, index = index)

def export_xl(df: pd.DataFrame, output_filename: str, index: bool = False):
    try:
        with pd.ExcelWriter(output_filename,mode = 'w') as writer:
            df.to_excel(writer, index = index)
        logger.info(f"Saved to: {output_filename}")    
    except ModuleNotFoundError:
        logger.warning('openpyxl Module not found, cannot export to xlsx, please install via: pip install openpyxl')
        raise SystemExit()
    except PermissionError as e:
        logger.warning(f'File {e} failed to open; waiting 10 seconds to try again...')
        time.sleep(10)
        export_xl(df,output_filename, index = index)

def export_ods(df: pd.DataFrame, output_filename: str, index: bool = False):
    try:
        with pd.ExcelWriter(output_filename,engine='odf',mode = 'w') as writer:
            df.to_excel(writer, index = index)
        logger.info(f"Saved to: {output_filename}")    
    except ModuleNotFoundError:
        logger.warning('odfpy Module not found, cannot export to ods, please install via: pip install odfpy')
        raise
    except PermissionError as e:
        logger.warning(f'File {e} failed to open; waiting 10 seconds to try again...')
        time.sleep(10)
        export_ods(df, output_filename, index = index)

def export_dict(df: pd.DataFrame):
    try:
        return df.to_dict('records')
    except ModuleNotFoundError:
        logger.warning('Pandas Module not found, cannot export to dict, please install via: pip install pandas')
        raise

def win_256_check(path: str):
    if len(path) > 255 and sys.platform == "win32":
        if path.startswith(u'\\\\?\\'):
            path = path
        else:
            path = u"\\\\?\\" + path
    return path

def win_file_split(path: str):
    if sys.platform == "win32":
        path = path.rsplit("\\",1)[-1]
    else:
        path = path.rsplit("/",1)[-1]
    return path

def filter_win_hidden(path: str):
    try:
        if bool(os.stat(path).st_file_attributes & stat.FILE_ATTRIBUTE_HIDDEN) is True:
            return True
        else:
            return False
    except:
        return False

def keyword_replace(keywords_list: Union[list, str], file_path: str, original_ref: str, keywords_mode: Optional[str] = "initialise", abbreviation_number: Optional[int] = None, keywords_case_sensitivity: Optional[bool] = False) -> str:
    file_name = win_file_split(file_path)
    if keywords_mode in ("initialise","firstletters"):
        if keywords_case_sensitivity is True:
            keywords_list = [keyword.upper() for keyword in keywords_list]
            file_name = file_name.upper()
        # If keywords_list is empty (but const is passed), applies to all directories or only those in list
        if (len(keywords_list) == 0 or any(file_name in keyword for keyword in keywords_list)) and os.path.isdir(file_path):
            replace_ref = file_name.translate(str.maketrans('','',r"""!"#$%&'()*+,-./:;<=>?@[\]^_`{|}~"""))
            if keywords_mode == "initialise":
                # If more than one word, take first letters
                if len(replace_ref.split(" ")) > 1:
                    if abbreviation_number is None:
                        abbreviation_number = -1
                    return "".join([x[0] for x in replace_ref.upper().split(" ", abbreviation_number)])
                # If single word, take first n letters
                else:
                    if abbreviation_number is None:
                        abbreviation_number = 3
                    return replace_ref[0:abbreviation_number].upper().replace(' ','')
            elif keywords_mode == "firstletters":
                if abbreviation_number is None:
                    abbreviation_number = 3
                return replace_ref[0:abbreviation_number].upper().replace(' ','')
        # If no match, return original ref
        else:
            return original_ref
    elif keywords_mode == "from_json":
        with open(os.path.abspath(keywords_list[0])) as file:
            keyword_dict = json.load(file)
            if not isinstance(keyword_dict, dict):
                logger.error('Keywords JSON file is not a valid dictionary.')
                raise ValueError('Keywords JSON file is not a valid dictionary.')
            if keywords_case_sensitivity is True:
                keyword_dict = {k.upper(): v for k, v in keyword_dict.items()}
                file_name = file_name.upper()
            if any(file_name in keyword for keyword in keyword_dict.keys()) and os.path.isdir(file_path):
                replace_ref = str(keyword_dict.get(file_name))
                return replace_ref
            else:
                return original_ref
    else:
        logger.error(f"Invalid keyword mode chosen {keywords_mode}, choose from ['firstletters','initialise','from_json']")
        raise ValueError(f"Invalid keyword mode chosen {keywords_mode}, choose from ['firstletters','initialise','from_json']")

def suffix_addition(file_path: str, ref: str, suffix: str, suffix_options: str = 'apply_to_files') -> str:
    if suffix_options == 'apply_to_files' and os.path.isfile(file_path):
        ref = str(ref) + str(suffix)
    elif suffix_options == 'apply_to_folders' and os.path.isdir(file_path):
        ref = str(ref) + str(suffix)
    elif suffix_options == 'apply_to_both':
        ref = str(ref) + str(suffix)
    else:
        pass
    return ref

def suffix_subtraction(file_path: str, ref: str, suffix: str, suffix_options: str = 'apply_to_files') -> str:
    if suffix_options == 'apply_to_files' and os.path.isfile(file_path):
        ref = str(ref).replace(str(suffix), "")
    elif suffix_options == 'apply_to_folders' and os.path.isdir(file_path):
        ref = str(ref).replace(str(suffix), "")
    elif suffix_options == 'apply_to_both':
        ref = str(ref).replace(str(suffix), "")
    else:
        pass
    return ref

def running_time(start_time):
    runningtime = datetime.now() - start_time
    return runningtime