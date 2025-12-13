"""
Auto Reference Generator tool

This tool is utilised to recursively generator reference codes, following an ISAD(G) convention, for a given directory / folder to an Excel or CSV spreadsheet.

It is compatible with Windows, MacOS and Linux Operating Systems.

author: Christopher Prince
license: Apache License 2.0"
"""

from auto_reference_generator.common import *
from auto_reference_generator.hash import *
import os, time, datetime
import pandas as pd
import configparser
from typing import Optional, Union

class ReferenceGenerator():
    """
    A Tool for generating archival references for any given directory for use by Digital Archivists.
    Will turn the hierarchy of a folder into and return the results as spreadsheet (or other output).

    :param root: the root directory to generate references for. Subsequent directories and files will be included.
    :param output_path: set the output path for the generated spreadsheet.
    :param prefix: set a prefix to append to generated references
    :param accprefix: set a prefix to append to generated accession references
    :param suffix: set a suffix to append to generated references
    :param suffix_options: set whether to apply the suffix to files, folders or both
    :param start_ref: set the starting reference, only affects first instance
    :param fixity: set whether to generate fixities
    :param empty_flag: set whether to delete and log empty directories
    :param skip_flag: set whether to skip reference generation (outputs set data)
    :param accession_flag: set whether to generate accession reference (running number)
    :param meta_dir_flag: set whether to generate a 'meta' dir for output
    :param hidden_flag: set to include hidden files/directories
    :param output_format: set to specify output format [xlsx, csv, ods, xml, json, dict] are supported, may require additional modules.
    :param delimiter: set delimiter for generated references
    :param keywords: set to replace numbers in reference with alphabetical characters, specified in list
    :param keywords_mode: set to specify keywords mode [initialise, firstletters] 
    :param keywords_retain_order: set to continue counting reference, if keyword is used, skips numbers if not
    :param sort_key: set the sort key, can be any valid function for sorted
    :param keywords_abbreviation: set int for number of characters to abbreviate to for keywords mode
    :param keywords_case_sensitivity: set to change case sensitivity for keyword matching
    :param options_file: set an options file to adjust field parameters
    """
    def __init__(self, 
                 root: str, 
                 output_path: str = os.getcwd(), 
                 prefix: Optional[str] = None,
                 suffix: Optional[str] = None,
                 suffix_options: Optional[str] = 'apply_to_files',
                 level_limit: Optional[int] = None,
                 accprefix: Optional[str] = None, 
                 start_ref: int = 1, 
                 fixity: Optional[str] = None, 
                 empty_flag: bool = False, 
                 skip_flag: bool = False, 
                 accession_flag: Optional[str] = None, 
                 meta_dir_flag: bool = True, 
                 hidden_flag: bool = False, 
                 output_format: str = "xlsx",
                 delimiter: str = "/",
                 keywords: Union[list,str,None] = None,
                 keywords_mode: Optional[str] = None,
                 keywords_retain_order: bool = False,
                 keywords_case_sensitivity: Optional[bool] = True,
                 sort_key = lambda x: (os.path.isfile(x), str.casefold(x)),
                 keywords_abbreviation_number: Optional[int] = None,
                 options_file: str = os.path.join(os.path.dirname(__file__),'options','options.properties')
                 ) -> None:

        self.root = os.path.abspath(root)
        self.root_level = self.root.count(os.sep)
        self.root_path = os.path.dirname(self.root)
        self.output_path = output_path
        self.output_format = output_format
        self.prefix = prefix
        self.suffix = suffix
        self.suffix_options = suffix_options
        self.level_limit = level_limit
        self.start_ref = start_ref
        self.fixity = fixity
        self.delimiter = delimiter
        if self.delimiter is None:
            self.delimiter_flag = False
            self.delimiter = "/"
        else:
            self.delimiter_flag = True
        self.keywords_list = keywords
        self.keywords_mode = keywords_mode
        self.keywords_retain_order = keywords_retain_order
        self.keywords_case_sensitivity = keywords_case_sensitivity
        self.sort_key = sort_key
        self.keywords_abbreviation_number = keywords_abbreviation_number

        self.accession_count = start_ref
        if accprefix:
            self.accession_prefix = accprefix
        else:
            self.accession_prefix = prefix

        self.reference_list = []
        self.record_list = []
        self.empty_list = []
        self.accession_list = []

        self.meta_dir_flag = meta_dir_flag
        self.accession_flag = accession_flag
        self.empty_flag = empty_flag
        self.skip_flag = skip_flag
        self.hidden_flag = hidden_flag

        if options_file is None:
            options_file = os.path.join(os.path.dirname(__file__),'options','options.properties')
        self.parse_config(options_file=os.path.abspath(options_file))
        self.start_time = datetime.datetime.now()

    def parse_config(self, options_file = os.path.join('options','options.properties')) -> None:
        config = configparser.ConfigParser()
        config.read(options_file, encoding='utf-8')
        global INDEX_FIELD
        INDEX_FIELD = config['options']['INDEX_FIELD']
        global PATH_FIELD
        PATH_FIELD = config['options']['PATH_FIELD']
        global RELATIVE_FIELD
        RELATIVE_FIELD = config['options']['RELATIVE_FIELD']
        global PARENT_FIELD
        PARENT_FIELD = config['options']['PARENT_FIELD']
        global PARENT_REF
        PARENT_REF = config['options']['PARENT_REF']
        global REFERENCE_FIELD
        REFERENCE_FIELD = config['options']['REFERENCE_FIELD']
        global ACCESSION_FIELD
        ACCESSION_FIELD = config['options']['ACCESSION_FIELD']
        global REF_SECTION
        REF_SECTION = config['options']['REF_SECTION']
        global LEVEL_FIELD
        LEVEL_FIELD = config['options']['LEVEL_FIELD']
        global BASENAME_FIELD
        BASENAME_FIELD = config['options']['BASENAME_FIELD']
        global EXTENSION_FIELD
        EXTENSION_FIELD = config['options']['EXTENSION_FIELD']
        global ATTRIBUTE_FIELD
        ATTRIBUTE_FIELD = config['options']['ATTRIBUTE_FIELD']
        global SIZE_FIELD
        SIZE_FIELD = config['options']['SIZE_FIELD']
        global CREATEDATE_FIELD
        CREATEDATE_FIELD = config['options']['CREATEDATE_FIELD']
        global MODDATE_FIELD
        MODDATE_FIELD = config['options']['MODDATE_FIELD']        
        global ACCESSDATE_FIELD
        ACCESSDATE_FIELD = config['options']['ACCESSDATE_FIELD']
        global OUTPUTSUFFIX
        OUTPUTSUFFIX = config['options']['OUTPUTSUFFIX']
        global METAFOLDER
        METAFOLDER = config['options']['METAFOLDER']
        global EMPTYDIRSREMOVED
        EMPTYDIRSREMOVED = config['options']['EMPTYSUFFIX']
        global ACCDELIMTER
        ACCDELIMTER = config['options']['ACCDELIMTER']

    def remove_empty_directories(self) -> None:
        """
        Remove empty directories with a warning.
        """
        confirm_delete = input('\n***WARNING*** \
                               \n\nYou have selected the Remove Empty Folders Option. \
                               \nThis process is NOT reversible! \
                               \n\nPlease confirm this by typing: "Y" \
                               \nTyping any other character will abort the program... \
                               \n\nPlease confirm your choice: ')
        if confirm_delete.lower() != "y":
            print('Aborting...')
            time.sleep(1)
            raise SystemExit()
        empty_dirs = []
        for dirpath, dirnames, filenames in os.walk(self.root, topdown = False):
            if not any((dirnames, filenames)):
                empty_dirs.append(dirpath)
                try:
                    os.rmdir(dirpath)
                    print(f'Removed Directory: {dirpath}')
                except OSError as e:
                    print(f"Error removing directory '{dirpath}': {e}")
        if empty_dirs:
            output_txt = define_output_file(self.output_path, self.root, METAFOLDER, self.meta_dir_flag, 
                                            output_suffix = EMPTYDIRSREMOVED, output_format = "txt")
            export_list_txt(empty_dirs, output_txt)
        else:
            print('No directories removed!')

    def filter_directories(self, directory, sort_key = lambda x: (os.path.isfile(x), str.casefold(x))) -> list:
        """
        Sorts the list alphabetically and filters out certain files.
        """
        try:
            if self.hidden_flag is False:
                list_directories = sorted([win_256_check(os.path.join(directory, f.name)) for f in os.scandir(directory)
                                        if not f.name.startswith('.')
                                        and filter_win_hidden(win_256_check(os.path.join(directory, f.name))) is False
                                        and f.name != METAFOLDER
                                        and f.name != os.path.basename(__file__)],
                                        key = sort_key)
            elif self.hidden_flag is True:
                list_directories = sorted([os.path.join(directory, f.name) for f in os.scandir(directory) \
                                        if f.name != METAFOLDER \
                                        and f.name != os.path.basename(__file__)],
                                        key = sort_key)
            else:
                list_directories = []
            return list_directories
        except Exception:
            print('Failed to Filter')
            raise SystemError()

    def parse_directory_dict(self, file_path: str, level: int, ref: Union[str,int]) -> dict:
        """
        Parses directory / file data into a dict which is then appended to a list
        """
        try:
            if file_path.startswith(u'\\\\?\\'):
                parse_path = file_path.replace(u'\\\\?\\', "")
            else: 
                parse_path = file_path
            file_stats = os.stat(file_path)
            if self.accession_flag is not None:
                if self.delimiter_flag is False:
                    self.delimiter = ACCDELIMTER
                acc_ref = self.accession_running_number(parse_path, self.delimiter)
                self.accession_list.append(acc_ref)
            if os.path.isdir(file_path):
                file_type = "Dir"
            else:
                file_type = "File"
            class_dict = {
                        PATH_FIELD: str(os.path.abspath(parse_path)),
                        RELATIVE_FIELD: str(parse_path).replace(self.root_path, ""), 
                        BASENAME_FIELD: os.path.splitext(os.path.basename(file_path))[0], 
                        EXTENSION_FIELD: os.path.splitext(file_path)[1], 
                        PARENT_FIELD: os.path.abspath(os.path.join(os.path.abspath(parse_path), os.pardir)), 
                        ATTRIBUTE_FIELD: file_type, 
                        SIZE_FIELD: file_stats.st_size, 
                        CREATEDATE_FIELD: datetime.datetime.fromtimestamp(file_stats.st_ctime), 
                        MODDATE_FIELD: datetime.datetime.fromtimestamp(file_stats.st_mtime), 
                        ACCESSDATE_FIELD: datetime.datetime.fromtimestamp(file_stats.st_atime), 
                        LEVEL_FIELD: level, 
                        REF_SECTION: ref}
            
            if self.fixity and not os.path.isdir(file_path):
                hash = HashGenerator(self.fixity).hash_generator(file_path)
                class_dict.update({"Algorithm": self.fixity, "Hash": hash})
            self.record_list.append(class_dict)
            return class_dict
        except:
            print('Failed to Parse')
            raise SystemError()


    def list_directories(self, directory: str, ref: Union[str,int] = 1) -> None:
        """
        Generates a list of directories. Also calculates level and a running reference number.
        """            
        ref = int(ref)
        pref = None
        list_directory = self.filter_directories(directory, sort_key = self.sort_key)
        try:
            if directory.startswith(u'\\\\?\\'):
                level = directory.replace(u'\\\\?\\', "").count(os.sep) - self.root_level + 1
            else:
                level = directory.count(os.sep) - self.root_level + 1
            for file_path in list_directory:
                file_name = win_file_split(file_path)
                #Keyword Replacement
                if self.keywords_list is not None:
                    # Case Sensitivity Check
                    if self.keywords_case_sensitivity is True:
                        keyword_file_name = file_name.upper()
                    elif self.keywords_case_sensitivity is False:
                        keyword_file_name = file_name
                    else:
                        keyword_file_name = file_name
                    if len(self.keywords_list) == 0 and os.path.isdir(file_path):
                        if self.keywords_retain_order is False:
                            pref = ref - 1
                        elif self.keywords_retain_order is True:
                            pref = ref
                        ref = str(keyword_replace(keyword_file_name, mode=self.keywords_mode, abbreviation_number=self.keywords_abbreviation_number))
                    elif any(keyword_file_name in keyword.upper() for keyword in self.keywords_list) and os.path.isdir(file_path):
                        if self.keywords_retain_order is False:
                            pref = ref - 1
                        elif self.keywords_retain_order is True:
                            pref = ref
                        ref = str(keyword_replace(keyword_file_name, mode=self.keywords_mode, abbreviation_number=self.keywords_abbreviation_number))
                    elif self.keywords_mode == "from_json" and os.path.isdir(file_path):
                        try:
                            os.path.exists(os.path.abspath(self.keywords_list[0]))
                        except Exception as e:
                            print('Error accessing JSON file, please check path.')
                        import json
                        with open(os.path.abspath(self.keywords_list[0])) as file:
                            keyword_dict = json.load(file)
                        if not isinstance(keyword_dict, dict):
                            print('Keywords JSON file is not a valid dictionary.')
                            raise SystemExit()
                        if self.keywords_case_sensitivity is True:
                            keyword_dict = {k.upper(): v for k, v in keyword_dict.items()}
                        if any(keyword_file_name in keyword for keyword in keyword_dict.keys()) and os.path.isdir(file_path):
                            if self.keywords_retain_order is False:
                                pref = ref - 1
                            elif self.keywords_retain_order is True:
                                pref = ref
                            ref = str(keyword_dict.get(keyword_file_name))
                    else:
                        pass
                #Suffix Addition
                if self.suffix is not None:
                    if self.suffix_options == 'apply_to_files' and os.path.isfile(file_path):
                        ref = str(ref) + str(self.suffix)
                    elif self.suffix_options == 'apply_to_folders' and os.path.isdir(file_path):
                        ref = str(ref) + str(self.suffix)
                    elif self.suffix_options == 'apply_to_both':
                        ref = str(ref) + str(self.suffix)
                    else:
                        pass
                if self.level_limit is not None and level > self.level_limit:
                    self.parse_directory_dict(file_path, level, ref='')
                else:
                    self.parse_directory_dict(file_path, level, ref)
                #Suffix Removal for next reference increment
                if self.suffix is not None:
                    if self.suffix_options == 'apply_to_files' and os.path.isfile(file_path):
                        ref = str(ref).replace(str(self.suffix), "")
                    elif self.suffix_options == 'apply_to_folders' and os.path.isdir(file_path):
                        ref = str(ref).replace(str(self.suffix), "")
                    elif self.suffix_options == 'apply_to_both':
                        ref = str(ref).replace(str(self.suffix), "")
                # prefer explicit None check - pref may be 0 which is a valid value
                if pref is not None:
                    ref = int(pref) + 1
                    pref = None
                else:
                    ref = int(ref) + 1
                if os.path.isdir(file_path):
                    self.list_directories(file_path, ref = 1)
        except Exception:
            print("Error occurred for directory/file: {}".format(list_directory))
            raise SystemError()

    def init_dataframe(self) -> pd.DataFrame:
        """
        Lists the directories and forms dicts from the above two functions.
        Looks up and pulls through the Parent row's data to the Child Row.
        Merges the dataframe on itself, Parent is merged 'left' on FullName to pull through the Parent's data
        (lookup is based on File Path's), and unnecessary data is dropped.
        Any errors are turned to 0 and the result are based on the reference loop initialisation.
        """
        self.parse_directory_dict(file_path = self.root, level = 0, ref = 0)
        self.list_directories(self.root, self.start_ref)
        self.df = pd.DataFrame(self.record_list).copy()
        
        merged = self.df.merge(self.df[[INDEX_FIELD, REF_SECTION]], how = 'left', left_on = PARENT_FIELD, 
                                right_on = INDEX_FIELD, suffixes=('_x', '_y'))
        parent_col = f'{REF_SECTION}_y'
        parent_series = (pd.to_numeric(merged[parent_col], errors='coerce').fillna(0).astype(int).astype(str))

        merged = merged.drop(columns=[f'{INDEX_FIELD}_y'])  
        merged = merged.rename(columns={f'{REF_SECTION}_x': REF_SECTION, parent_col: PARENT_REF, f'{INDEX_FIELD}_x': INDEX_FIELD})
        merged[PARENT_REF] = parent_series.astype(str)
        self.df = merged
        # old method - resulted in dtype warning
        # self.df = self.df.merge(self.df[[INDEX_FIELD, REF_SECTION]], how = 'left', left_on = PARENT_FIELD, 
        #                        right_on = INDEX_FIELD)
        #self.df = self.df.drop([f'{INDEX_FIELD}_y'], axis = 1)
        #self.df = self.df.rename(columns = {f'{REF_SECTION}_x': REF_SECTION, f'{REF_SECTION}_y': PARENT_REF, 
        #                                  f'{INDEX_FIELD}_x': INDEX_FIELD})
        #self.df.loc[:, PARENT_REF] = self.df[PARENT_REF].fillna(0)
        #self.df.loc[:, PARENT_REF] = self.df.astype({PARENT_REF: str})
        self.df.index.name = "Index"
        self.list_loop = self.df[[REF_SECTION, PARENT_FIELD, LEVEL_FIELD]].values.tolist()
        if self.skip_flag:
            pass
        else:
            self.init_reference_loop()
        return self.df

    def init_reference_loop(self) -> pd.DataFrame:
        """
        Initialises the Reference loop. Sets some of the pre-variables necessary for the loop.
        """
        c = 0
        tot = len(self.list_loop)
        for ref, parent, level in self.list_loop:
            c += 1
            print(f"Generating Auto Reference for: {c} / {tot}", end = "\r")
            self.reference_loop(ref = ref, parent = parent, track = 1, level = level, delimiter = self.delimiter)

        self.df.loc[:, REFERENCE_FIELD] = self.reference_list
        if self.accession_flag is not None:
            self.df.loc[:, ACCESSION_FIELD] = self.accession_list
        return self.df

    def reference_loop(self, ref: str, parent: str, track: int, level: int, new_ref: Optional[str] = None, delimiter: str = "/") -> None:
        """
        The Reference loop works upwards, running an "index lookup" against the parent folder until it reaches the top.

        ref is the reference section derived from the list in the list_directories function. [Stays Constant]
        PARENT is the parent folder of the child. [Varies]
        TRACK is an iteration tracker to distinguish between first and later iterations. [Varies]
        LEVEL is the level of the folder, 0 being the root. [Stays Constant]

        new_ref is the archive reference constructed during this loop.

        To do this, the reference loop works upwards, running an "index lookup" against the parent folder until it reaches the top.
        1) To start, the reference loop indexes from the dataframe established by listing the directories.
        2) The index compares FullName against the Parent (So acting on the Basis of File Path's)
        3) If the index fails / is 0, then the top has been reached.
        4) In that event if LEVEL is also 0 IE the top-most item is being looked at (normally the first thing). new_ref is set to ref
        5) Otherwise the top-most level has been reached and, new_ref is simply new_ref.
        6) If the index does matches, then top level has not yet been reached. In this case we also account for the PARENT's Reference, to avoid an error at the 2nd to top layer.
        7) parent_ref is looked up, by Indexing the Dataframe. Then if parent_ref is 0, IE we're on the 2nd top layer. We check the TRACK.
        8) If TRACK is 1, IE the first iteration on the 2nd layer, new_ref is just ref.
        9) If TRACK isn't 1, IE subsequent iterations on the 2nd layer, new_ref is just itself.
        10) If parent_ref isn't 0, then we concatenate the parent_ref with either ref or new_ref.
        11) If TRACK is 1, new_ref is parent_ref + ref.
        12) If TRACK isn't 1, new_ref is parent_ref + new_ref.
        13) At the end of the process the PARENT of the current folder is looked up and sub_parent replace's the PARENT variable. TRACK is also advanced.
        14) Then the function is then called upon recursively. In this way the loop will work through until it reaches the top.
        15) This is only called upon if the index does not fail. If it does fail, then the top-level is reached and the loop escaped.
        16) As this is acting within the Loop from the init stage, this will operate on all files within a list.
        """
        try:
            idx = self.df.loc[self.df[INDEX_FIELD] == parent,INDEX_FIELD].index
            if idx.size == 0:
                if level == 0:
                    new_ref = str(ref)
                    if self.prefix:
                        new_ref = str(self.prefix)
                else:
                    new_ref = str(new_ref)
                    if self.prefix:
                        new_ref = str(self.prefix) + delimiter + str(new_ref)
                self.reference_list.append(new_ref)
            else:
                parent_ref = self.df.loc[idx, REF_SECTION].item()
                if parent_ref == 0:
                    if track == 1:
                        new_ref = str(ref)
                    else:
                        new_ref = str(new_ref)
                else:
                    if track == 1:
                        if ref == '':
                            new_ref = str(parent_ref)
                        else:
                            new_ref = str(parent_ref) + delimiter + str(ref)
                    else:
                        if ref == '' and parent_ref == '':
                            pass
                        else:
                            new_ref = str(parent_ref) + delimiter + str(new_ref)
                parent = self.df.loc[idx,PARENT_FIELD].item()
                track = track + 1
                self.reference_loop(ref, parent, track, level, new_ref, delimiter=delimiter)

        except Exception as e:
            print('Error in Reference Loop.')
            print(e)
            raise SystemError()
            pass

    def accession_running_number(self, file_path: str, delimiter: str = "-") -> Union[int,str,None]:
        """
        Generates a Running Number / Accession Code, can be set to 3 different "modes", counting Files, Directories or Both
        """
        if self.accession_flag is not None:
            if self.accession_flag.lower() == "file":
                if os.path.isdir(file_path):
                    if self.accession_prefix is not None:
                        accession_ref = self.accession_prefix + delimiter + "Dir"
                    else:
                        accession_ref = "Dir"
                else:
                    if self.accession_prefix is not None:
                        accession_ref = self.accession_prefix + delimiter + str(self.accession_count)
                    else:
                        accession_ref = self.accession_count
                    self.accession_count += 1
            elif self.accession_flag.lower() == "dir":
                if os.path.isdir(file_path):
                    if self.accession_prefix is not None:
                        accession_ref = self.accession_prefix + delimiter + str(self.accession_count)
                    else:
                        accession_ref = self.accession_count
                    self.accession_count += 1
                else:
                    if self.accession_prefix is not None:
                        accession_ref = self.accession_prefix + delimiter + "File"
                    else:
                        accession_ref = "File"
            elif self.accession_flag.lower() == "all":
                if self.accession_prefix:
                    accession_ref = self.accession_prefix + delimiter + str(self.accession_count)
                else:
                    accession_ref = self.accession_count
                self.accession_count += 1
            else:
                accession_ref = None
        else:
            accession_ref = None
        return accession_ref

    def main(self) -> Optional[list]:
        """
        Runs Program :)
        """
        if self.empty_flag:
            self.remove_empty_directories()
        self.init_dataframe()
        output_file = define_output_file(self.output_path, self.root, meta_dir_flag = self.meta_dir_flag, 
                                         output_suffix = OUTPUTSUFFIX ,output_format = self.output_format)
        if self.output_format == "xlsx":
            export_xl(df = self.df, output_filename = output_file)
        elif self.output_format == "csv":
            export_csv(df = self.df, output_filename = output_file)
        elif self.output_format == "ods":
            export_ods(df = self.df, output_filename = output_file)
        elif self.output_format == "json":
            export_json(df = self.df, output_filename = output_file)
        elif self.output_format == "xml":
            export_xml(df = self.df, output_filename = output_file)
        elif self.output_format == "dict":
            return export_dict(df = self.df)
        print_running_time(self.start_time)
