#!/usr/bin/env python3
# Fix the Decimal type handling error in sales.py

import re

FILE_PATH = 'ui/sales.py'

with open(FILE_PATH, 'r') as file:
    content = file.read()

# Replace the problematic lines
# Line 1062
pattern1 = r'discount_ratio = Decimal\(\'1\'\) - \(discount_amount / subtotal\) if subtotal > Decimal\(\'0\'\) else Decimal\(\'1\'\)'
replacement1 = r'discount_ratio = Decimal(\'1\') - (Decimal(str(discount_amount)) / Decimal(str(subtotal))) if subtotal > Decimal(\'0\') else Decimal(\'1\')'

# Line 2273 (similar pattern)
pattern2 = r'discount_ratio = Decimal\(\'1\'\) - \(discount_amount / subtotal\) if subtotal > Decimal\(\'0\'\) else Decimal\(\'1\'\)'
replacement2 = r'discount_ratio = Decimal(\'1\') - (Decimal(str(discount_amount)) / Decimal(str(subtotal))) if subtotal > Decimal(\'0\') else Decimal(\'1\')'

modified_content = content.replace(pattern1, replacement1)
modified_content = modified_content.replace(pattern2, replacement2)

# Write the modified content back to the file
with open(FILE_PATH, 'w') as file:
    file.write(modified_content)

print("Decimal error fixes completed successfully")