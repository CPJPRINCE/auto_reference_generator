# import os
# import pandas as pd
# from typing import Optional

# class PhysicalReferenceGenerator():
#     def __init__(self,
#                  physical_mode_input: Optional[str] = None,
#                 input_to_sort: Optional[str] = None):
#         self.physical_mode_input = physical_mode_input
#         self.input_to_sort = input_to_sort

#     def main(self) -> pd.DataFrame:
#             """
#             TEST USE ONLY - NOT FULLY IMPLEMENTED YET
#             Physical (catalogue spreadsheet) mode - reads an inventory and generates Archive_Reference
#             values from the physical Level definitions contained in `PHSYICAL_LEVEL_SEPERATORS` and the
#             `PHYSICAL_LEVEL_FIELD` within the spreadsheet. Uses the `prefix` property as the top-level
#             code by default (e.g. 'HS'). If no prefix is provided the first prefix-level Title will be used.
#             """
#             if self.physical_mode_input is None:
#                 raise ValueError('No physical_mode_input set')

#             # Read DataFrame from input
#             if self.physical_mode_input.endswith(('.xlsx', '.xls','.xlsm')):
#                 self.df = pd.read_excel(self.physical_mode_input)
#             elif self.physical_mode_input.endswith('.csv'):
#                 self.df = pd.read_csv(self.physical_mode_input)
#             elif self.physical_mode_input.endswith('.ods'):
#                 self.df = pd.read_excel(self.physical_mode_input,engine='odf')
#             else:
#                 raise ValueError('Unknown file type for physical_mode_input')

#             # Ensure index name is set consistently
#             self.df.index.name = 'Index'

#             # Get separators and item definitions from config
#             try:
#                 physical_separators = [x.strip().lower() for x in self.PHYSICAL_LEVEL_SEPERATORS.split(',')]
#             except Exception:
#                 physical_separators = []
#             try:
#                 physical_items = [x.strip().lower() for x in self.PHYSICAL_ITEM.split(',')]
#             except Exception:
#                 physical_items = []

#             # Determine the prefix-level index (prefer 'collection' if present)
#             if 'collection' in physical_separators:
#                 prefix_level_label = 'collection'
#                 prefix_index = physical_separators.index('collection')
#             elif len(physical_separators) > 0:
#                 prefix_level_label = physical_separators[0]
#                 prefix_index = 0
#             else:
#                 # fall back to the first level encountered
#                 prefix_level_label = None
#                 prefix_index = 0

#             # If no explicit prefix string provided, try to get from the first row that matches prefix level
#             prefix_value = self.prefix
#             if prefix_value is None and prefix_level_label is not None and self.PHYSICAL_LEVEL_FIELD in self.df.columns and 'Title' in self.df.columns:
#                 for _, row in self.df.iterrows():
#                     if isinstance(row[self.PHYSICAL_LEVEL_FIELD], str) and row[self.PHYSICAL_LEVEL_FIELD].strip().lower() == prefix_level_label:
#                         prefix_value = str(row['Title'])
#                         break

#             # counters for each recognised level + one for item-level beyond last
#             counters = [0] * (len(physical_separators) + 1)
#             references = []

#             # Iterate rows and build counters
#             level_list = self.df[self.PHYSICAL_LEVEL_FIELD].to_list()

#             for lvl in level_list:
#                 lvl_val = str(lvl).strip().lower()
#                 if lvl_val in physical_separators:
#                     lvl_idx = physical_separators.index(lvl_val)
#                 #elif lvl_val in physical_items:
#                 #    lvl_idx = len(physical_separators)
#                 else:
#                     # Non-recognised levels are treated as leaf item
#                     lvl_idx = len(physical_separators)

#                 # increment current level counter and reset deeper levels
#                 counters[lvl_idx] += 1
#                 for j in range(lvl_idx + 1, len(counters)):
#                     counters[j] = 0

#                 # Build reference string
#                 parts = []
#                 if prefix_value:
#                     parts.append(prefix_value)

#                 # include counters for levels that are non-zero beyond the prefix level
#                 for k in range(prefix_index + 1, len(counters)):
#                     if counters[k] > 0:
#                         parts.append(str(counters[k]))

#                 # If current row is at prefix level then return only prefix
#                 if prefix_value is not None and lvl_idx == prefix_index:
#                     ref_str = prefix_value
#                 else:
#                     ref_str = self.delimiter.join(parts) if len(parts) > 0 else ''
#                     if self.suffix:
#                         ref_str = ref_str + self.suffix

#                     # If there is no prefix and only a top-level counter, simply set count
#                     if not prefix_value and lvl_idx == prefix_index:
#                         ref_str = str(counters[lvl_idx])

#                 references.append(ref_str)

#             # Attach to DataFrame and return
#             self.df.loc[:, self.REFERENCE_FIELD] = references
#             return self.df

#         def sort_spreadsheet_by_reference(self,padding_width=5):
#             # Helper that returns a padded string for sorting
#             def _pad_reference_for_sort(val):
#                 # Handle NaN/None
#                 try:
#                     if pd.isna(val):
#                         return ""
#                 except Exception:
#                     # If pd.isna fails for some type, fall back to truthy test
#                     if val is None:
#                         return ""
#                 parts = str(val).split(self.delimiter)
#                 padded_parts = []
#                 for p in parts:
#                     # If the part is purely numeric, pad it; otherwise keep it as-is (but preserve original zfill behavior if desired)
#                     if p.isdigit():
#                         padded_parts.append(p.zfill(padding_width))
#                     else:
#                         # Keep alpha parts unchanged — this is more readable and behaves well for sorting
#                         padded_parts.append(p)
#                 return self.delimiter.join(padded_parts)

#             if self.input_to_sort.endswith(('.xlsx', '.xls','.xlsm')):
#                 self.df = pd.read_excel(self.input_to_sort)
#             elif self.input_to_sort.endswith('.csv'):
#                 self.df = pd.read_csv(self.input_to_sort)
#             elif self.input_to_sort.endswith('.ods'):
#                 self.df = pd.read_excel(self.input_to_sort,engine='odf')
#             else:
#                 raise ValueError('Unknown file type for physical_mode_input')

#             # Use the map result as the key to sort, which efficiently returns an array-like of padded keys
#             self.df = self.df.sort_values(by=self.REFERENCE_FIELD, key=lambda col: col.map(_pad_reference_for_sort))
#             return self.df