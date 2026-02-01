# Auto Reference Generator

A small python programme to generate hierarchical archival reference for files and directories and export the results to a spreadsheet.

[![Supported Versions](https://img.shields.io/pypi/pyversions/auto_reference_generator.svg)](https://pypi.org/project/auto_reference_generator)
[![CodeQL](https://github.com/CPJPRINCE/auto_reference_generator/actions/workflows/codeql.yml/badge.svg)](https://github.com/CPJPRINCE/auto_reference_generator/actions/workflows/codeql.yml)

## Table of Contents
- [Quick Start](#quick-start)
  - [Option 1: Using pip (Recommended for Python users / long-term usage)](#option-1-using-pip-recommended-for-python-users--long-term-usage)
  - [Option 2: Using Portable Executable (No Python Required)](#option-2-using-portable-executable-no-python-required)
  - [Output](#output)
- [Version & Package info](#version--package-info)
- [Why use this tool?](#why-use-this-tool)
- [Additional Features:](#additional-features)
- [Basic Usage / Examples](#basic-usage--examples)
- [Expected Spreadsheet](#expected-spreadsheet)
- [Structure of References](#structure-of-references)
- [Advanced Options](#advanced-options)
  - [Clear Empty Directories](#clear-empty-directories)
  - [Hash/Fixity Generation](#hashfixity-generation)
  - [Level Limit](#level-limit)
  - [Skip](#skip)
  - [Keywords](#keywords)
  - [Options File](#options-file)
  - [Accession mode](#accession-mode)
- [Full Options:](#full-options)
- [Troubleshooting](#troubleshooting)
- [Future Developments](#future-developments)
- [Contributing](#contributing)
- [Developers](#developers)


## Quick Start

### Option 1: Using pip (Recommended for Python users / long-term usage)
```bash
pip install -U auto_reference_generator
auto_ref /path/to/root -p PREFIX -o /path/to/output
```

### Option 2: Using Portable Executable (No Python Required)
Download the latest portable executable for your platform from [Releases](https://github.com/CPJPRINCE/auto_reference_generator/releases)

Extract and run:
```bash
# Windows
cd auto_ref\bin
.\auto_ref.cmd .\path\to\root -p PREFIX -o .\path\to\output

# Linux/macOS
./auto_ref /path/to/root -p PREFIX -o /path/to/output
```
On Windows you can also use the install.cmd with admin privileges to install and run the command without navigating to the .cmd directory (see Option 1 for use)

### Output
Generates a `meta` folder with output `root_AutoRef.xlsx` and a list of the generated reference hierarchy, alongside some metadata.

## Version & Package info

Python Version:
Python Version 3.10+ is recommended. Earlier versions may work but are not tested.

Additional Packages:
- pandas (required)
- openpyxl (required)
- pyodf (optional - ods export)
- lxml (optional - xml export)
- tqdm (required)

To install using Python:

```bash
pip install pandas openpyxl pyodf lxml tqdm
```

If using Python ensure it is added to Environment.

## Why use this tool?

This tool is designed for archivists cataloguing large amounts of Digital Records at a time.

Automated Generation of References saves time and effort compared to manually filling in vs.

Additional options expand upon this and allow insertion into existing hierarchies and reference systems.

## Additional Features:

- **Prefixes - allowing merging into existing hierarchies**
- **Suffixes**
- **Level identification and limiting**
- **Keyword assignment - replacing Numericals with specified keywords (initials, first letter, JSON map)**
- **Logged removal of empty directories**
- **Accession / Running Number mode**
- **Fixity Generation**
- **Export options include: xslx (Default), csv, ods, json or xml.**
- **Integration with Opex Manifest Generator [*\*Shameless Self promotion\**.](https://github.com/CPJPRINCE/opex_manifest_generator/)**

## Basic Usage / Examples

- Basic: `auto_ref /path/to/root`
- Prefix: `auto_ref /path/to/root -p PREFIX`
- Suffix: `auto_ref /path/to/root -s SUFFIX`
- Delimiter: `auto_ref /path/to/root -dlm "-"`
- Accession: `auto_ref /path/to/root -acc file`
- Fixity: `auto_ref /path/to/root -fx MD5`
- Format: `auto_ref /path/to/root -fmt csv`
- Remove Empty `auto_ref /path/to/root --remove-empty`
- Output: `auto_ref /path/to/root -o /path/to/output`
- Include Hidden: `auto_ref /path/to/root --hidden`

These options can be combined in a number of combinations.

## Expected Spreadsheet

The spreadsheet should output like so:

![SpreadPreview](assets/SpreadPreview.png)

This includes a preset of metadata:
Including: FullName, RelativeName, BaseName, Size, Modified, Ref_Section Level, Parent, Archive_Reference,

The reference will by default be generated to the `Archive_Reference` column:

![ReferencePreview](assets/ReferencesPreview.png)

## Structure of References

```
# Usage with Prefix `ARC`
auto_ref /path/to/root -p ARC

Folder                 Reference
>Root                  ARC
--->Folder 1           ARC/1
------>Sub Folder 1    ARC/1/1
--------->File 1       ARC/1/1/1
--------->File 2       ARC/1/1/2
------>Sub Folder 2    ARC/1/2
--------->File 3       ARC/1/2/1
--------->File 4       ARC/1/2/2
--->Folder 2           ARC/2
------>Sub Folder 3    ARC/2/1
--------->File 5       ARC/2/2
--->File 6             ARC/3
...

# Files and Folders can coexist at the same level. Without a prefix the root reference defaults to 0:
auto_ref /path/to/root

>Root                  0
--->Folder             1
------>Sub Folder      1/1
--------->File         1/1/1
--------->File2        1/1/2
------>File3           1/2
...

# Prefixes can also be set to integrate the folder into the existing hierarchy at any point.
auto_ref /path/to/root -p "ARC/1/2/3"

>Root                   ARC/1/2/3
--->Folder              ARC/1/2/3/1
------>File             ARC/1/2/3/1/1
------>File2            ARC/1/2/3/1/2
...

# Start Ref option will also set the starting number for first subfolder.
auto_ref /path/to/root -p "ARC/1/2/3" -s 5

>Root                   ARC/1/2/3
--->Folder              ARC/1/2/3/5
------>File             ARC/1/2/3/5/1
...

```
## Advanced Options

**Important notes**

- The term `meta` is hard coded to always be ignored for folders.
- A meta folder will always be generated unless using `--disable-meta-dir` option.
- **Both relative and absolute paths will work**

### Clear Empty Directories

```bash
# Will remove empty directories and generate a plain text log to the 'meta folder'. This is to prevent misleading references to nothing.
auto_ref /path/to/root --remove-empty
```

### Hash/Fixity Generation

```bash
# Will generate a SHA-1 fixity list alongside reference, in columns Hash and Algorithm
auto_ref /path/to/root -fx SHA-1

# MD5, SHA-1, SHA-256, SHA-512 supported.
```

![HashPreview](assets/HashPreview.png)

### Level Limit

```bash
# Sets a level-depth to stop generating referencing at. Example will stop generating 5 levels down from root.
auto_ref /path/to/root -l 5
```

### Skip

```bash
# Will skip reference generation if you just want a listing of files
auto_ref /path/to/root --skip
```

### Keywords

Keywords replace the numerical reference with a keyword that matches folder name.
```bash
# Replaces keywords "Department of Justice" & "Department of Finance" with intials of words IE DOJ, DOF.
auto_ref /path/to/root -key "Department of Justice" "Department of Finance"

# The keywords will replace the reference number to all matches of the keyword. The way the replacement is made is determined by the `-keym / --keyword-mode`.
```

Keyword Modes:

```bash
# intialise
# Uses the intials of the keywords in this example Department of Justice becomes DOJ. Singular words will use firstletters mode. Is the default mode.
auto_ref -key "Department of Justice" -keym initialise

# firstletters
# Use the first x letters of word. IE `Department of Justices` becomes `DEP`.
auto_ref -key "Department of Justice" -keym firstletters

# from_json
# Uses a Python Dictionary stored as a JSON file to set custom abbreviations.
auto_ref -key /path/to/keyword.json -keym from_json

# JSON formatted like:
{'keyword to replace':'value to replace with', 'keyword2':'value2'}
```

Additional Keyword Options:

```bash
--keywords-case-sensitivity # Sets make lookup case sensitive. Default is insensitive.
--keywords-abbreviation-number # Sets the number of letters to abbreviate firstletters mode to. Default is 3.
--keywords-retain-order # Sets whether reference generation will count replacements in its ordering.
                        # By default it will not count replacements.
                        # If a keyword replacement is made after reference number 1, the next reference number after the replacement will be: 2
                        # If this option is used the number will instead be 3.
```

### Options File

```bash
# Set a custom options file to customise default headers and some program defaults
auto_ref /path/to/root --options-file /path/to/options.properties
```

Default Options are:
```
[options]

INDEX_FIELD = FullName # Sets name to run indexing from

PATH_FIELD = FullName
RELATIVE_FIELD = RelativeName
PARENT_FIELD = Parent
PARENT_REF = Parent_Ref
REFERENCE_FIELD = Archive_Reference
REF_SECTION = Ref_Section
ACCESSION_FIELD = Accession_Reference
LEVEL_FIELD = Level
BASENAME_FIELD = BaseName
EXTENSION_FIELD = Extension
ATTRIBUTE_FIELD = Attributes
SIZE_FIELD = Size
CREATEDATE_FIELD = Create_Date
MODDATE_FIELD = Modified_Date
ACCESSDATE_FIELD = Access_Date

ALGORITHM_FIELD = Algorithm
HASH_FIELD = Hash

ACCDELIMTER = -
ACCFILE_KEYWORD = File
ACCDIR_KEYWORD = Dir
METAFOLDER = meta
OUTPUTSUFFIX = _AutoRef
EMPTYSUFFIX = _EmptyDirsRemoved
```

### Accession mode

An alternative method of code generation is based on an accession number / running number pattern. Each file or folder will be given a running number regardless of depth.

Example output running Accession in "file" Mode:
```
>Root                 ACC-Dir
---> Folder 1          ACC-Dir
------> File 1         ACC-1
------> File 2         ACC-2
---> File 3            ACC-3
---> Folder 2          ACC-Dir
------> Sub-Folder     ACC-Dir
---------> File 4      ACC-4
```

Examples:

```bash
# Run acc generation for files with Prefix "ACC" - numbers files
auto_ref /path/to/root -acc file -accp "ACC"`

# Run Accession generation for directories - numbers directories
auto_ref /path/to/root -acc dir -accp "ACC"`

# Run Accession generation for both - numbers both
auto_ref /path/to/root -acc both -accp "ACC"`
```

The output will be to an additional `Accession_Reference` column

![AccessionPReview](assets/AccessionPreview.png)

## Full Options:

The below covers the full range of options. Use the `-h` option to show this dialog:
<details>
<summary>
Full Options:
</summary>
<!-- argparse_to_md:auto_reference_generator:create_parser -->
Usage:
```
Auto_Reference_Generator [-h] [-v] [-p [PREFIX]] [-s [SUFFIX]]
                                    [--suffix-option {file,dir,both}] [-acc {file,dir,both}]
                                    [-accp [ACC_PREFIX]] [-l [LEVEL_LIMIT]] [-str [START_REF]]
                                    [-dlm [DELIMITER]] [--remove-empty] [--disable-empty-export]
                                    [-hid] [-fx [{MD5,SHA-1,SHA1,SHA-256}]]
                                    [--sort-by [{folders_first,alphabetical}]] [-o [OUTPUT]]
                                    [--disable-meta-dir] [-skp] [-fmt {xlsx,csv,json,ods,xml,dict}]
                                    [--options-file [OPTIONS_FILE]]
                                    [--log-level [{DEBUG,INFO,WARNING,ERROR}]]
                                    [--log-file [LOG_FILE]] [-key [KEYWORDS ...]]
                                    [--keywords-case-sensitivity]
                                    [-keym [{initialise,firstletters,from_json}]]
                                    [--keywords-retain-order]
                                    [--keywords-abbreviation-number [KEYWORDS_ABBREVIATION_NUMBER]]
                                    [root]
```
Auto Reference Generator for Digital Cataloguing

Positional arguments:
- `root`: The root directory to create references for

Optional arguments:
- `-v`, `--version`: See version information, then exit

Reference Options:
  Options for reference generation

- `-p [PREFIX]`, `--prefix [PREFIX]`: Set a prefix to append onto generated references
- `-s [SUFFIX]`, `--suffix [SUFFIX]`: Set a suffix to append onto generated references
- `--suffix-option {file`, `dir`, `both}`: Set whether to apply the suffix to files, folders or both when generating references
- `-acc {file`, `dir`, `both}`, `--accession {file`, `dir`, `both}`: Sets the program to create an accession listing - IE a running number of the files.
- `-accp [ACC_PREFIX]`, `--acc-prefix [ACC_PREFIX]`: Sets the Prefix for Accession Mode
- `-l [LEVEL_LIMIT]`, `--level-limit [LEVEL_LIMIT]`: Set a level limit to generate references to
- `-str [START_REF]`, `--start-ref [START_REF]`: Set the starting reference number. Won't affect sub-folders/files
- `-dlm [DELIMITER]`, `--delimiter [DELIMITER]`: Set the delimiter to use between levels
- `--remove-empty`: Sets the Program to remove any Empty Directory and Log removals to a text file
- `--disable-empty-export`: Sets the program to not export a log of removed empty directories, by default will export, this flag disables that
- `-hid`, `--hidden`: Set to include hidden files/folders in the listing
- `-fx [{MD5`, `SHA-1`, `SHA1`, `SHA-256}]`, `--fixity [{MD5`, `SHA-1`, `SHA1`, `SHA-256}]`: Set to generate fixities, specify Algorithm to use (default SHA-1)
- `--sort-by [{folders_first`, `alphabetical}]`: Set the sorting method, 'folders_first' sorts folders first then files alphabetically; 'alphabetically' sorts alphabetically (ignoring folder distinction)

Output Options:
  Options for outputting the generated references

- `-o [OUTPUT]`, `--output [OUTPUT]`: Set the output directory for the created spreadsheet
- `--disable-meta-dir`: Set to disable creating a 'meta' file for spreadsheet; can be used in combination with output
- `-skp`, `--skip`: Set to skip creating references, will generate a spreadsheet listing
- `-fmt {xlsx`, `csv`, `json`, `ods`, `xml`, `dict}`, `--output-format {xlsx`, `csv`, `json`, `ods`, `xml`, `dict}`: Set to set output format. ***Note ods requires odfpy; xml requires lxml; dict requires pandas, please install as needed***
- `--options-file [OPTIONS_FILE]`: Set the options file to use, to override output column headers and other options
- `--log-level [{DEBUG`, `INFO`, `WARNING`, `ERROR}]`: Set the logging level (default: WARNING)
- `--log-file [LOG_FILE]`: Optional path to write logs to a file (default: stdout)

Keyword Options:
  Options for using keywords in reference generation

- `-key [KEYWORDS ...]`, `--keywords [KEYWORDS ...]`: Set to replace reference numbers with given Keywords for folders (only Folders atm). Can be a list of keywords or a JSON file mapping folder names to keywords.
- `--keywords-case-sensitivity`: Set to change case keyword matching sensitivity. By default keyword matching is insensitive
- `-keym [{initialise`, `firstletters`, `from_json}]`, `--keywords-mode [{initialise`, `firstletters`, `from_json}]`: Set to alternate keyword mode: 'initialise' will use initials of words; 'firstletters' will use the first letters of the string; 'from_json' will use a JSON file mapping names to keywords
- `--keywords-retain-order`: Set when using keywords to continue reference numbering. If not used keywords don't 'count' to reference numbering, e.g. if using initials 'Project Alpha' -> 'PA' then the next folder/file will be '1' not '2'
- `--keywords-abbreviation-number [KEYWORDS_ABBREVIATION_NUMBER]`: Set to set the number of letters to abbreviate for 'firstletters' mode, does not impact 'initialise' mode.
<!-- argparse_to_md_end -->
</details>

## Troubleshooting

- On Windows ensure that when you enter the root folder it does not end in a `\`. This is slightly annoying as it adds it by default when tabbing.
- In the examples above I've used linux paths. If you're on Windows don't forget to change these to backslashes `\`

## Future Developments

- ~~Level Limitations to allow for "group references"~~ - Added!
- ~~Generating references which use alphabetic characters~~ - Added!
- A mode for Physical Cataloguing...

## Contributing

I welcome further contributions and feedback. If there any issues please raise them [here](https://github.com/CPJPRINCE/auto_reference_generator/issues).

## Developers

The program can be used as a python module like so.
```python
from auto_reference_generator import ReferenceGenerator

rg = ReferenceGenerator ("/path/to/root", prefix = "ARC", output_path = "/path/to/output")
```
