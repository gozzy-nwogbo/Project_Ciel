# Skill: invoice-organizer

Organize invoices and receipts for tax prep, bookkeeping, and expense reporting by extracting metadata, renaming consistently, and generating summaries.
Trigger phrases: "organize my invoices", "sort receipts for tax", "rename my invoices", "expense report prep", "invoice summary".
Output artifact: organized invoice folder with `invoice-log.csv` and summary markdown at target directory.

---

# Invoice Organizer

Organizes invoices and receipts for tax prep, bookkeeping, and expense reporting.

## When to Use

- Tax season and you have a folder of receipts/invoices
- Expense report preparation
- Monthly bookkeeping
- Organizing vendor invoices for accounts payable
- Cleaning up a downloads folder full of PDF receipts

## Process

### Step 1: Inventory

```bash
# Find all likely invoice files
find ~/Downloads -name "*.pdf" -o -name "*.jpg" -o -name "*.png" | grep -iE "invoice|receipt|bill|order"

# Or list everything in a target folder
ls -la ~/invoices-messy/
```

### Step 2: Extract Information

For each document, extract:
- **Vendor/Payee name**
- **Invoice date**
- **Invoice number** (if present)
- **Amount**
- **Category** (software, travel, office, meals, etc.)

Use a log file to track:
```bash
echo "vendor,date,amount,category,original_filename,new_filename" > invoice-log.csv
```

### Step 3: Rename Files

Consistent naming convention:
```
YYYY-MM-DD_[Vendor]_[Amount]_[InvoiceNumber].pdf
```

Examples:
```
2025-02-15_AWS_$142.30_INV-2025-0215.pdf
2025-02-10_Adobe_$54.99_CC-2025-02.pdf
2025-01-28_WeWork_$800.00_WW-JAN2025.pdf
```

Python snippet for batch renaming:
```python
import os
from pathlib import Path

def rename_invoice(folder, old_name, vendor, date, amount, inv_num=""):
    old_path = Path(folder) / old_name
    ext = old_path.suffix
    inv_part = f"_{inv_num}" if inv_num else ""
    new_name = f"{date}_{vendor}_{amount}{inv_part}{ext}"
    new_path = Path(folder) / new_name
    os.rename(old_path, new_path)
    return new_name
```

### Step 4: Organize into Folders

```
invoices/
├── 2025/
│   ├── Q1/
│   │   ├── software/
│   │   ├── travel/
│   │   ├── office/
│   │   └── other/
│   └── Q2/
├── 2024/
└── _review/    <- unclear items to manually check
```

### Step 5: Generate Summary

Produce a CSV or markdown summary:

```markdown
## Invoice Summary -- Q1 2025

| Date | Vendor | Amount | Category |
|------|--------|--------|----------|
| 2025-01-05 | AWS | $134.22 | Software |
| 2025-01-10 | Notion | $16.00 | Software |
| 2025-02-14 | Delta | $420.00 | Travel |

**Total**: $570.22
**By Category**: Software $150.22 / Travel $420.00
```

## Categories (standard)

- `software` -- SaaS subscriptions, cloud services
- `hardware` -- computers, peripherals, equipment
- `travel` -- flights, hotels, transportation
- `meals` -- business meals and entertainment
- `office` -- supplies, furniture
- `professional-services` -- contractors, consultants
- `utilities` -- internet, phone
- `marketing` -- ads, design services
- `other` -- everything else

## Tips

- When a vendor name is unclear, use the domain from the email (e.g., `stripe.com` -> `Stripe`)
- If an amount is unclear, mark it `$?` and add to `_review/`
- Keep originals until tax filing is complete
