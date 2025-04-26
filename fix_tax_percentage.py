#!/usr/bin/env python3
# Fix the tax_rate to tax_percentage conversion in sales.py

import re

FILE_PATH = 'ui/sales.py'

with open(FILE_PATH, 'r') as file:
    content = file.read()

# Replace all occurrences of tax_rate with tax_percentage
pattern1 = r'item\.get\("tax_rate"'
replacement1 = r'item.get("tax_percentage"'

pattern2 = r'tax_rate = item\.get\("tax_rate"'
replacement2 = r'tax_rate = item.get("tax_percentage"'

modified_content = re.sub(pattern1, replacement1, content)
modified_content = re.sub(pattern2, replacement2, modified_content)

# Write the modified content back to the file
with open(FILE_PATH, 'w') as file:
    file.write(modified_content)

print("Replacements completed successfully")