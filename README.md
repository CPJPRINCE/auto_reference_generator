# Auto Reference Generator

A small python programme to generate hieracrchical archival reference for files and directories and export the results to a spreadsheet.

Badges: PyPI | CI | Coverage | License

## Quick Start
Install:
```
pip install -U auto_reference_generator
```
Or download portable version.

Run:
```
auto_ref /path/to/root -p PREFIX -o /path/to/output
```

Generates a `meta/` folder with output `root_AutoRef.xlsx`

To use the portable version navigate to the Downloaded then run with:
```
.\auto_ref.exe .\path\to\root
```

## Version & Package info

Python Version:
Python Version 3.10+ is recommended. Earlier versions may work but are not tested.

Additional Packages:
- pandas (required)
- openpyxl (required - spreadsheet exports)
- pyodf (ods export)
- lxml (xml export)
- tqdm
To install:

```
pip install pandas openpyxl pyodf lxml tqdm
```
Portable version includes

## Why use this tool?

This tool is designed for archivist's cataloguing large amounts of Digital Records at a time.

It's platform independent tested functioning on Windows and Linux (untested on MacOS). 

## Features:

- Hierachical reference generation with customisatible (Prefixes/Suffixes/Delimiters/Starting ref).
- 'Level' identification and limiting.
- Keyword filtering - replacing Numericals with specified keywords (intials, first letter, JSON map)
- Logged removal of empty directories.
- An Accession / Running Number mode.
- Fixity Generation
- Exports: xslx (Default), csv, ods (requires pyodf), json or xml (requires lxml).
- Integration with Opex Manifest Generator [*\*Shameless Self promotion\**.](https://github.com/CPJPRINCE/opex_manifest_generator/)

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

These options can be combined in an.

## Output

Expected ouput is like so:

![SpreadPreview](assets/SpreadPreview.png)

This includes a preset of metadata:
Including: FullName, RelativeName, BaseName, Size, Modified, Ref_Section Level, Parent, Archive_Reference,

The reference will by default be generated to the `Archive_Reference` column:

![ReferencePreview](assets/ReferencesPreview.png)

## Structure of References

Usage with Prefix `ARC`.
```
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
```

Files and Folders can coexist at the same level. Without a prefix the root reference defaults to 0:

```
>Root                  0
--->Folder             1
------>Sub Folder      1/1
--------->File         1/1/1
--------->File2        1/1/2
------>File3           1/2

```
Prefixes can be set to any point in an Hierachy.

## Advanced Options

### Accession mode

An alternative method of code generation is based on an 'accession number'/running number pattern. Each file or folder will be given a running number regardless of depth.

Example output running Accession in "File" Mode:
```
> Root                 ACC-Dir
---> Folder 1          ACC-Dir
------> File 1         ACC-1
------> File 2         ACC-2
---> File 3            ACC-3
---> Folder 2          ACC-Dir
------> Sub-Folder     ACC-Dir
---------> File 4      ACC-4
```

To run:

`auto_ref "/path/to/root" -acc file -accp "ACC"`

The available modes are for `file, dir, all`. Output will be to an additiona `Accession_Reference` column

![AccessionPReview](assets/AccessionPreview.png)


### Clear Empty Directories

Running `auto_ref /path/to/root --remove-empty` automatically remove any empty directories. A plain text log of the removed directories will be saved to `meta/`.

### Fixity

To run a fixity and save to the output: `auto_ref /path/to/root -fx ALGORITHM` This will default to using the SHA-1 algorithm. MD5, SHA-1, SHA-256 and SHA-512 are supported. 

![HashPreview](assets/HashPreview.png)

### Level Limit

Set a level limit to stop generating referencing at: `auto_ref /path/to/root -l 5` will stop generating references 5 levels below root.

### Skip

If you want to generate a spreadsheet without a reference code you can run: `auto_ref /path/to/root --skip`

### Options File

You can customise the program by creating an 'options file' using the `--options-file` option. This allows for customisation of the column headers and the programs defaults.

Options given as:
```
[options]

INDEX_FIELD = FullName #Sets which field to use for index.

PATH_FIELD = FullName
RELATIVE_FIELD = RelativeName
PARENT_FIELD = Parent
PARENT_REF = Parent_Ref
REFERENCE_FIELD = Archive_Reference
REF_SECTION = Ref_Section
ACCESSION_FIELD = Accession_Reference
LEVEL_FIELD = Level
...
```

### Keywords

To use Keywords: `auto_ref /path/to/root -key Keyword1 Keyword2 Keyword3 ... -keym intialise` The keywords will replace the reference number to all matches of the keyword. The way the replacement is made is determined by the `-keym / --keyword-mode`.

Keyword Modes:
- `intialise` Uses the intials of the words. `Department of Justice` becomes `DOJ`. Singluar words use first x amount of letters.
- `firstletters` uses the first x amount of letters.`Department of Justices` becomes `DEP`.
- `from_json` can create a Python Dictionary in a JSON file and set KEYWORD to that file. Will replace all keys with given value. Run like so: `auto_ref /path/to/root -key /path/to/json.json`.
- JSON Dict written like so: `{'keyword':'value','keyword2','value2',...}` 

## Full Options:

(Note to self add in argparse to md...)

The below covers the full range of options. This may not be up to date.
For up to date options use the `-h` option to show dialog:

```
Options:
        -h,     --help          Show Help dialog                              

        -p,     --prefix        Replace Root 0 with specified prefix            [string]
                                Is added to all references

        -s      --suffix        Add a suffix to references                      [string]

        --suffix-options        Set whether to apply to files,                  {apply_to_files,apply_to_folders,
                                folders,or to all                               apply_to_all}
                                default is to apply_to_files.
        
        -l      --level-limit   Set whether to limit generation to              [int]
                                a specific level.
                                Note generated references may have
                                extra delimiter.

        -dlm    --delimiter     Set to change the default delimiter             [string]

        -acc,   --accession     Run in "Accession Mode", this will              {Dir,File,
                                generate a running number of either             All}
                                Files, directories, or Both                                                           
                                
        -accp,  --acc-prefix    Set the Prefix to append onto the running       [boolean]
                                number generated in "Accession Mode"
        
        -fx     --fixity        Generate fixity codes for files                 {MD5, SHA-1, 
                                                                                SHA-256, SHA-512}
        
        -hid    --hidden        Include Hidden directories and files in         [boolean]
                                generation.

        --remove-empty              Will remove all Empty Directories from          [boolean]
                                within a given folder, not including them
                                in the Reference Generation.
                                A simply Text list of removed folders is 
                                then generated to the output directory.
        
        -str,     --start-ref   Set the number to start the Reference           [int] 
                                generation from.
        
        -o,     --output        Set the directory to export the spreadsheet to. [string]      
        
        --disable-meta-dir      Set whether to generate a "meta" directory,     [boolean]
                                to export CSV / Excel file to.
                                Default behavior will be to create a directory,
                                using this option will disable it.      
        
        -skp    --skip          Skip running the Auto Reference process,   [boolean]
                                will generate a spreadsheet but not
                                an Archival Reference
        
        -fmt,   --format        Set export format. Will require                 {xlsx,csv,ods,dict,xml,json}
                                appropriate modules in Python.
                                ods - PyODF
                                xlsx - OpenPyXL
                                xml - lxml     
                                Defaults to xlsx.
        
        -key    --keywords      Set keywords to replace numericals with         [string|path]
                                alphanumerical characters
                                Can be single word or
                                list: 'written,like,this'
                                Or path to a JSON file containing a dict

                                Keywords only currently act upon folders
                                and not files.
        
        -keym   -keywords-mode  Set way to replace:                             {initialise,first_letters,from_json}
                                initialise: My New Folder > MNF
                                first_letters: My New Folder > MYF
                                from_json: Imports
                                Requires to have a Json file with a
                                dictionary of words to replace:
                                {'Word':'Replacement',
                                'SecondWord':'2ndReplacement}
        
        --keywords-retain-      Set whether to continue reference numbering     [bool]
        order                   If not used keywords don't 'count' towards
                                additional references. 
                                IE if the keyword you are replacing is 
                                be reference number: 2, this is moved
                                to what would originally be number 3.
                                Retaining the order means, this scheme is 
                                maintained: IE 3 is still 3, and 2 is skipped

        --keywords-case-        Set to enable case-sensitivity for keyword    [bool]
        sensitivity           matches. Default is cases are not sensitive.

        --keywords-abbreviation Set the number of characters to abbreviate to   [int]
        -number                 Only for first_letters mode.

        --sort-by               Set the sorting method: folders_first, sorts    [folders_first|alphabetically]
                                folders first. Alphabetically, you can guess.
                                Ignores folders.
                
                                
        
```

## Troubleshooting

- On Windows ensure that your root folder does not end in a `\`.
- The `meta/` folder will always be ignored.


## Future Developments

- ~~Level Limitations to allow for "group references"~~ - Added!
- ~~Generating reference's which use alphabetic characters~~ - Added!
- Physical Level

## Contributing

I welcome further contributions and feedback.
