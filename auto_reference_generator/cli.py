from auto_reference_generator.reference_generator import ReferenceGenerator
import argparse, os
import importlib.metadata

def parse_args():
    parser = argparse.ArgumentParser(prog="Auto_Reference_Generator", description = "Auto Reference Generator for Digital Cataloguing")
    parser.add_argument('root', nargs = '?', default = os.getcwd(),
                        help = "The root directory to create references for")
    parser.add_argument("-p", "--prefix", required = False, nargs = '?',
                        help = "Set a prefix to append onto generated references")
    parser.add_argument("-s", "--suffix", required = False, nargs = '?',
                        help = "Set a suffix to append onto generated references")
    parser.add_argument("--suffix-option", required = False, choices= ['apply_to_files','apply_to_folders','apply_to_both'], default = 'apply_to_files',
                        help = "Set whether to apply the suffix to files, folders or both when generating references")
    parser.add_argument("--rm-empty", required = False, action = 'store_true',
                        help = "Sets the Program to remove any Empty Directory and Log removals to a text file")
    parser.add_argument("-acc", "--accession", required = False, choices = ['dir', 'file', 'all'], default = None, type = str.lower,
                        help="Sets the program to create an accession listing - IE a running number of the files.")
    parser.add_argument("-accp", "--acc-prefix", required = False, nargs = '?',
                        help = "Sets the Prefix for Accession Mode")
    parser.add_argument("-o", "--output", required = False, nargs = '?',
                        help = "Set the output directory for created spreadsheet")
    parser.add_argument("-l", "--level-limit", required = False, nargs = '?', type = int,
                        help = "Set a level limit to generate references to")
    parser.add_argument("-str", "--start-ref", required = False, nargs = '?', default = 1, type=int,
                        help = "Set the starting reference number. Won't affect sub-folders/files")
    parser.add_argument("-dlm", "--delimiter", required = False, nargs= '?', type = str,
                        help = "Set the delimiter to use between levels")
    parser.add_argument("--disable-meta-dir", required = False, action = 'store_false', default = True,
                        help = "Set to disable creating a 'meta' file for spreadsheet; can be used in combination with output")
    parser.add_argument("-skp","--skip", required = False, action = 'store_true', default = False,
                        help = "Set to skip creating references, will generate a spreadsheet listing")
    parser.add_argument("-hid","--hidden", required = False , action = 'store_true', default = False,
                        help = "Set to include hidden files/folders in the listing")
    parser.add_argument("-fmt", "--output-format", required = False, default = "xlsx", choices = ['xlsx', 'csv', 'json', 'ods', 'xml', 'dict'],
                        help = "Set to set output format. Note ods requires odfpy; xml requires lxml; dict requires pandas, please install via pip if needed")
    parser.add_argument("-fx", "--fixity", required = False, nargs = '?', const = "SHA-1", default = None, choices = ['MD5', 'SHA-1', 'SHA1', 'SHA-256','SHA256','SHA-512','SHA512'], type = str.upper,
                        help = "Set to generate fixities, specify Algorithm to use (default SHA-1)")
    parser.add_argument("-v", "--version", action = 'version', version = '%(prog)s {version}'.format(version = importlib.metadata.version("auto_reference_generator")),
                        help = "See version information, then exit")
    parser.add_argument("-key","--keywords", nargs = '*', default = None,
                        help = "Set to replace reference numbers with given Keywords for folders (only Folders atm). Can be a list of keywords or a JSON file mapping folder names to keywords.")
    parser.add_argument("--keywords-case-sensitivity", required = False, action = 'store_false', default = True,
                        help = "Set to change case keyword matching sensitivity. By default keyword matching is insensitive")
    parser.add_argument("-keym","--keywords-mode", nargs = '?', const = "initialise", choices = ['initialise','firstletters','from_json'], default = 'initialise',
                        help = "Set to alternate keyword mode: 'initialise' will use initials of words; 'firstletters' will use the first letters of the string; 'from_json' will use a JSON file mapping names to keywords")
    parser.add_argument("--keywords-retain-order", required = False, default = False, action = 'store_true', 
                        help = "Set when using keywords to continue reference numbering. If not used keywords don't 'count' to reference numbering, e.g. if using initials 'Project Alpha' -> 'PA' then the next folder/file will still be '001' not '003'")
    parser.add_argument("--keywords-abbreviation-number", required = False, nargs='+', default = None, type = int,
                        help = "Set to set the number of letters to abbreviate for 'firstletters' mode, does not impact 'initialise' mode.")
    parser.add_argument("--sort-by", required=False, nargs = '?', default = 'folders_first', choices = ['folders_first','alphabetical'], type=str.lower,
                        help = "Set the sorting method, 'folders_first' sorts folders first then files alphabetically; 'alphabetically' sorts alphabetically (ignoring folder distinction)")
    parser.add_argument("--options-file", required = False, nargs = '?', default = os.path.join(os.path.dirname(__file__),'options','options.properties'),
                        help = "Set the options file to use")
    parser.add_argument("--physical-mode-input", required = False, nargs = '?', default = None,
                        help="Set to conduct an Auto Generation of a Specify a path to a Spreadsheet")
    parser.add_argument("--spreadsheet-to-sort",required= False, nargs = '?',default= None,
                        help="Set to a path to a Spreadsheet containing an 'Archive_Reference' Column to sort the spreadsheet according to hierarchy")
    args = parser.parse_args()
    return args

def run_cli():
    args = parse_args()
    if isinstance(args.root, str):
        args.root = args.root.strip("\"").rstrip("\\")
    if not args.output:
        args.output = os.path.abspath(args.root)
        print(f'Output path defaulting to root directory: {args.output}')
    else:
        args.output = os.path.abspath(args.output)
        print(f'Output path set to: {args.output}')
    if args.acc_prefix and not args.accession:
        print(f'Accession Prefix set but Accession Mode not set, ignoring Accession Prefix')
    sort_key = None
    if args.sort_by:
        if args.sort_by == "folders_first":
            sort_key = lambda x: (os.path.isfile(x), str.casefold(x))
        elif args.sort_by == "alphabetical":
            sort_key = str.casefold

    ReferenceGenerator(args.root, 
                            output_path = args.output, 
                            prefix = args.prefix, 
                            accprefix = args.acc_prefix,
                            suffix = args.suffix,
                            suffix_options = args.suffix_option,
                            level_limit = args.level_limit,
                            fixity = args.fixity, 
                            empty_flag = args.rm_empty, 
                            accession_flag = args.accession, 
                            hidden_flag = args.hidden, 
                            start_ref = args.start_ref, 
                            meta_dir_flag = args.disable_meta_dir, 
                            skip_flag = args.skip, 
                            output_format = args.output_format,
                            keywords = args.keywords,
                            keywords_mode = args.keywords_mode,
                            keywords_retain_order = args.keywords_retain_order,
                            keywords_case_sensitivity= args.keywords_case_sensitivity,
                            sort_key = sort_key,
                            delimiter = args.delimiter,
                            keywords_abbreviation_number = args.keywords_abbreviation_number,
                            options_file = args.options_file,
                            physical_mode_input = args.physical_mode_input,
                            input_to_sort = args.spreadsheet_to_sort).main()
    print('Complete!')

if __name__ == "__main__":
    run_cli()