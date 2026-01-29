from auto_reference_generator.reference_generator import ReferenceGenerator
import argparse, os, logging, inspect
import importlib.metadata
from auto_reference_generator.common import running_time
from datetime import datetime

logger = logging.getLogger(__name__)

def create_parser():
    parser = argparse.ArgumentParser(prog="Auto_Reference_Generator", description = "Auto Reference Generator for Digital Cataloguing")
    parser.add_argument("-v", "--version", action = 'version', version = '%(prog)s {version}'.format(version = importlib.metadata.version("auto_reference_generator")),
                        help = "See version information, then exit")
    parser.add_argument('root', nargs = '?', default = os.getcwd(),
                        help = "The root directory to create references for")
    refgroup = parser.add_argument_group('Reference Options','Options for reference generation')
    refgroup.add_argument("-p", "--prefix", required = False, nargs = '?',
                        help = "Set a prefix to append onto generated references")
    refgroup.add_argument("-s", "--suffix", required = False, nargs = '?',
                        help = "Set a suffix to append onto generated references")
    refgroup.add_argument("--suffix-option", required = False, choices= ['apply_to_files','apply_to_folders','apply_to_both'], default = 'apply_to_files',
                        help = "Set whether to apply the suffix to files, folders or both when generating references")
    refgroup.add_argument("-acc", "--accession", required = False, choices = ['dir', 'file', 'all'], default = None, type = str.lower,
                        help="Sets the program to create an accession listing - IE a running number of the files.")
    refgroup.add_argument("-accp", "--acc-prefix", required = False, nargs = '?',
                        help = "Sets the Prefix for Accession Mode")
    refgroup.add_argument("-l", "--level-limit", required = False, nargs = '?', type = int,
                        help = "Set a level limit to generate references to")
    refgroup.add_argument("-str", "--start-ref", required = False, nargs = '?', default = 1, type = int,
                        help = "Set the starting reference number. Won't affect sub-folders/files")
    refgroup.add_argument("-dlm", "--delimiter", required = False, nargs= '?', type = str,
                        help = "Set the delimiter to use between levels")
    refgroup.add_argument("--remove-empty", required = False, action = 'store_true',
                        help = "Sets the Program to remove any Empty Directory and Log removals to a text file")
    refgroup.add_argument("--disable-empty-export", required = False, action = 'store_false',
                        help = "Sets the program to not export a log of removed empty directories, by default will export, this flag disables that")
    refgroup.add_argument("-hid","--hidden", required = False , action = 'store_true', default = False,
                        help = "Set to include hidden files/folders in the listing")
    refgroup.add_argument("-fx", "--fixity", required = False, nargs = '?', const = "SHA-1", default = None, choices = ['MD5', 'SHA-1', 'SHA1', 'SHA-256'], type = fixity_helper,
                        help = "Set to generate fixities, specify Algorithm to use (default SHA-1)")
    refgroup.add_argument("--sort-by", required=False, nargs = '?', default = 'folders_first', choices = ['folders_first','alphabetical'], type=str.lower,
                        help = "Set the sorting method, 'folders_first' sorts folders first then files alphabetically; 'alphabetically' sorts alphabetically (ignoring folder distinction)")


    outputgroup = parser.add_argument_group('Output Options','Options for outputting the generated references')
    outputgroup.add_argument("-o", "--output", required = False, nargs = '?',
                        help = "Set the output directory for the created spreadsheet")
    outputgroup.add_argument("--disable-meta-dir", required = False, action = 'store_false', default = True,
                        help = "Set to disable creating a 'meta' file for spreadsheet; can be used in combination with output")
    outputgroup.add_argument("-skp","--skip", required = False, action = 'store_true', default = False,
                        help = "Set to skip creating references, will generate a spreadsheet listing")
    outputgroup.add_argument("-fmt", "--output-format", required = False, default = "xlsx", choices = ['xlsx', 'csv', 'json', 'ods', 'xml', 'dict'],
                        help = "Set to set output format. Note ods requires odfpy; xml requires lxml; dict requires pandas, please install via pip if needed")
    outputgroup.add_argument("--options-file", required = False, nargs = '?', default = os.path.join(os.path.dirname(__file__),'options','options.properties'),
                        help = "Set the options file to use, to override output column headers and other options")
    outputgroup.add_argument("--log-level", required=False, nargs='?', choices=['DEBUG','INFO','WARNING','ERROR'], default=None, type=str.upper,
                        help="Set the logging level (default: WARNING)")
    outputgroup.add_argument("--log-file", required=False, nargs='?', default=None,
                        help="Optional path to write logs to a file (default: stdout)")
    
    keywordsgroup = parser.add_argument_group('Keyword Options','Options for using keywords in reference generation')
    keywordsgroup.add_argument("-key","--keywords", nargs = '*', default = None,
                        help = "Set to replace reference numbers with given Keywords for folders (only Folders atm). Can be a list of keywords or a JSON file mapping folder names to keywords.")
    keywordsgroup.add_argument("--keywords-case-sensitivity", required = False, action = 'store_false', default = True,
                        help = "Set to change case keyword matching sensitivity. By default keyword matching is insensitive")
    keywordsgroup.add_argument("-keym","--keywords-mode", nargs = '?', const = "initialise", choices = ['initialise','firstletters','from_json'], default = 'initialise',
                        help = "Set to alternate keyword mode: 'initialise' will use initials of words; 'firstletters' will use the first letters of the string; 'from_json' will use a JSON file mapping names to keywords")
    keywordsgroup.add_argument("--keywords-retain-order", required = False, default = False, action = 'store_true', 
                        help = "Set when using keywords to continue reference numbering. If not used keywords don't 'count' to reference numbering, e.g. if using initials 'Project Alpha' -> 'PA' then the next folder/file will be '1' not '2'")
    keywordsgroup.add_argument("--keywords-abbreviation-number", required = False, nargs='?', default = 3, type = int,
                        help = "Set to set the number of letters to abbreviate for 'firstletters' mode, does not impact 'initialise' mode.")
    return parser

def run_cli():
    parser = create_parser()
    args = parser.parse_args()
    # Configure logging early so other modules inherit the settings
    try:
        log_level = getattr(logging, args.log_level.upper()) if args.log_level else logging.INFO
    except Exception:
        log_level = logging.INFO
    log_format = '%(asctime)s %(levelname)-8s [%(name)s] %(message)s'
    if args.log_file:
        logging.basicConfig(level=log_level, filename=args.log_file, filemode='a', format=log_format)
    else:
        logging.basicConfig(level=log_level, format=log_format)
    logger.debug(f'Logging configured (level={logging.getLevelName(log_level)}, file={args.log_file or "stdout"})')
    
    if not os.path.exists(args.root):
        logger.error(f'Please ensure that root is a valid folder: {args.root}.'
                     '\nIf on Windows ensure that path does not end in \\" or \\\' as this causes a conflict for Command Line')
        raise FileNotFoundError(f'Please ensure that root is a valid folder: {args.root}.'
                     '\nIf on Windows ensure that path does not end in \\" or \\\' as this causes a conflict for Command Line')
    if isinstance(args.root, str):
        args.root = args.root.strip("\"").rstrip("\\")
        logger.info(f'Root path is set to: {args.root}')

    if args.remove_empty:
        logger.warning(inspect.cleandoc("\n***WARNING***" \
                                "\nYou have enabled the remove empty folders functionality of the program. " \
                                "This action will remove all empty folders." \
                                "\nThis process will permanently delete all empty folders, with no way recover the items." \
                                "\n***"))
        i = input(inspect.cleandoc("Please type Y if you wish to proceed, otherwise the program will close: "))
        if not i.lower() == "y":
            logger.info("Y not typed, safetly aborted...")
            raise SystemExit()
        else:
            logger.info("Confirmation recieved proceeding to remove empty folders...")

    if not args.output:
        args.output = os.path.abspath(args.root)
        logger.info(f'Output path defaulting to root directory: {args.output}')
    else:
        args.output = os.path.abspath(args.output)
        logger.info(f'Output path set to: {args.output}')
    if args.acc_prefix and not args.accession:
        logger.warning(f'Accession prefix set but accession mode not set, ignoring accession prefix')

    if args.keywords and args.keywords_mode == 'from_json' and len(args.keywords) != 1:
        logger.error(f'When using keywords mode "from_json" only a single JSON file can be provided as keywords')
        raise ValueError(f'When using keywords mode "from_json" only a single JSON file can be provided as keywords')
    
    if args.keywords and args.keywords_mode is None:
        args.keywords_mode = 'initialise'
        logger.info(f'Keywords provided but no keywords mode set, defaulting to "initialise"')

    sort_key = None
    if args.sort_by:
        if args.sort_by == "folders_first":
            logger.debug(f'Sorting by folders first')
            sort_key = lambda x: (os.path.isfile(x), str.casefold(x))
        elif args.sort_by == "alphabetical":
            logger.debug(f'Sorting alphabetically')
            sort_key = str.casefold

    start_time = datetime.now()
    ReferenceGenerator(args.root, 
                            output_path = args.output, 
                            prefix = args.prefix, 
                            accprefix = args.acc_prefix,
                            suffix = args.suffix,
                            suffix_options = args.suffix_option,
                            level_limit = args.level_limit,
                            fixity = args.fixity, 
                            empty_flag = args.remove_empty, 
                            empty_export_flag = args.disable_empty_export, 
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
                            options_file = args.options_file).main()
    logger.info(f"Run Complete! Ran for: {running_time(start_time)}")    

def fixity_helper(x: str):
    x = x.upper()
    if x == 'SHA1':
        x = 'SHA-1'
    if x == 'SHA256':
        x = 'SHA-256'
    if x == 'SHA512':
        x = 'SHA-512'
    return x.upper()

if __name__ == "__main__":
    try:
        run_cli()
    except KeyboardInterrupt:
        logger.warning("Process interrupted by user, exiting...")