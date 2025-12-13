"""
Common Tools used in both Opex Manifest and Auto Reference modules.

author: Christopher Prince
license: Apache License 2.0"
"""

import os, time, sys, stat
import datetime
import pandas as pd
from typing import Optional

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
    except PermissionError as e:
        print(e)
        print('Waiting 10 Seconds to try again...')
        time.sleep(10)
        export_list_txt(txt_list, output_filename)
    finally:
        print(f"Saved to: {output_filename}")

def export_csv(df: pd.DataFrame, output_filename: str):
    try:
        df['Archive_Reference'] = df['Archive_Reference'].astype('string')
        df.to_csv(output_filename,sep = ",",encoding = "utf-8")
    except ModuleNotFoundError:
        print('Pandas Module not found, cannot export to csv, please install via: pip install pandas')
    except PermissionError as e:
        print(e)
        print('Waiting 10 Seconds to try again...')
        time.sleep(10)
        export_csv(df,output_filename)
    print(f"Saved to: {output_filename}")

def export_json(df: pd.DataFrame, output_filename: str):
    try:
        df.to_json(output_filename,orient='index', indent=4)
    except ModuleNotFoundError:
        print('Pandas Module not found, cannot export to json, please install via: pip install pandas')
        raise SystemExit()
    except PermissionError as e:
        print(e)
        print('Waiting 10 Seconds to try again...')
        time.sleep(10)
        export_json(df, output_filename)
    print(f"Saved to: {output_filename}")

def export_xml(df: pd.DataFrame, output_filename: str):
    try:
        df.to_xml(output_filename)
    except ModuleNotFoundError:
        print('lxml Module not found, cannot export to xml, please install via: pip install lxml')
        raise SystemExit()
    except PermissionError as e:
        print(e)
        print('Waiting 10 Seconds to try again...')
        time.sleep(10)
        export_xml(df, output_filename)
    print(f"Saved to: {output_filename}")

def export_xl(df: pd.DataFrame, output_filename: str):
    try:
        with pd.ExcelWriter(output_filename,mode = 'w') as writer:
            df.to_excel(writer)
    except ModuleNotFoundError:
        print('openpyxl Module not found, cannot export to xlsx, please install via: pip install openpyxl')
        raise SystemExit()
    except PermissionError as e:
        print(e)
        print('Waiting 10 Seconds to try again...')
        time.sleep(10)
        export_xl(df,output_filename)
    print(f"Saved to: {output_filename}")

def export_ods(df: pd.DataFrame, output_filename: str):
    try:
        with pd.ExcelWriter(output_filename,engine='odf',mode = 'w') as writer:
            df.to_excel(writer)
    except ModuleNotFoundError:
        print('odfpy Module not found, cannot export to ods, please install via: pip install odfpy')
        raise SystemExit()
    except PermissionError as e:
        print(e)
        print('Waiting 10 Seconds to try again...')
        time.sleep(10)
        export_xl(df,output_filename)
    print(f"Saved to: {output_filename}")

def export_dict(df: pd.DataFrame):
    try:
        return df.to_dict('records')
    except ModuleNotFoundError:
        print('Pandas Module not found, cannot export to dict, please install via: pip install pandas')
        raise SystemExit()

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

def keyword_replace(text: str, mode: Optional[str] = "initialise", keyword_dict: Optional[dict] = None, abbreviation_number: Optional[int] = None) -> str:
    text = text.translate(str.maketrans('','',r"""!"#$%&'()*+,-./:;<=>?@[\]^_`{|}~"""))
    if mode == "initialise":
        if len(text.split(" ")) > 1:
            if abbreviation_number is None:
                abbreviation_number = -1
            return "".join([x[0] for x in text.upper().split(" ", abbreviation_number)])
        else:
            if abbreviation_number is None:
                abbreviation_number = 3
            return text[0:abbreviation_number].upper().replace(' ','')
    elif mode == "firstletters":
        if abbreviation_number is None:
            abbreviation_number = 3
        return text[0:abbreviation_number].upper().replace(' ','')
    else:
        print('Invalid keyword mode')
        raise SystemExit()
    
def print_running_time(start_time):
    print(f'Running time: {datetime.datetime.now() - start_time}')