Auto Reference Generator - Portable Edition
=============================================

This is a standalone, portable distribution of Auto Reference Generator.

Installation
============

For Windows:
1. Extract the ZIP file to your desired location
2. Navigate to the auto_reference_generator folder
3. Run install.cmd (right-click and select "Run as Administrator")
4. Follow the on-screen instructions

After installation, you can use auto_reference_generator from any command prompt.

Usage
=====

Basic usage:
  auto_reference_generator /path/to/root -p PREFIX -o /path/to/output

For full options:
  auto_reference_generator --help

Examples
========

Generate references with a prefix:
  auto_reference_generator C:\MyFiles -p "DOC" -o C:\Output

Generate with CSV output:
  auto_reference_generator C:\MyFiles -fmt csv -o C:\Output

Generate with accession numbering:
  auto_reference_generator C:\MyFiles -acc both -accp "ACC" -o C:\Output

Uninstallation
==============

To uninstall from Windows:
1. Navigate to the auto_reference_generator folder
2. Run uninstall.cmd (right-click and select "Run as Administrator")
3. Follow the on-screen instructions

Support
=======

For more information, visit the project repository or consult the documentation.

This executable was built using Nuitka and includes all necessary dependencies.
No additional Python installation is required.
