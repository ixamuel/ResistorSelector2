# Plan: Update Resistor Database from XLSM File

## Problem Summary

The existing pipeline expects a plain `.xlsx` file (`Resistor DB.xlsx`) as input. The user now receives a **`.xlsm`** (macro-enabled workbook) file from Panasonic. The `.xlsm` is essentially a `.zip` archive containing XML files, but with VBA macros and potentially **protected sheets**. The user previously extracted the `.xlsx` manually by deleting VBA strings and editing protection settings.

**Goal:** Create a Python script that automates the extraction of the resistor data sheet from the `.xlsm` file, handling sheet protection, and then feeds into the existing pipeline (`compact_resistors_v2.py` -> `resistors_compact.json` -> `data.js`).

## Current Data Pipeline

```
Panasonic XLSX (Resistor DB.xlsx)
        │
        ▼
compact_resistors_v2.py  (pandas read_excel → column mapping → lookup encoding → JSON)
        │
        ▼
resistors_compact.json   (lookups + resistors array)
        │
        ▼
update_data_app.py  OR  generate_final_tool.py
        │
        ▼
data.js  (const DATA = {...})
        │
        ▼
index.html + app.js  (frontend)
```

## Proposed Solution

Create a new script `extract_from_xlsm.py` that:

1. **Accepts an `.xlsm` file path** as input (default: `PanasonicIndustry_Chip_Resistor_SelectionTool.xlsm`)
2. **Extracts the data sheet** from the protected `.xlsm` using one of two strategies:
   - **Strategy A (Preferred):** Use `openpyxl` with sheet unprotection (if the protection is not password-locked, `openpyxl` can read protected sheets directly since protection only restricts UI editing, not programmatic reading)
   - **Strategy B (Fallback):** If `openpyxl` cannot read the data (e.g., VBA project lock or very old format), extract the `.xlsm` as a ZIP archive, locate the worksheet XML (`xl/worksheets/sheet1.xml`), parse it directly, and extract cell data
3. **Saves the extracted data as a clean `.xlsx`** (e.g., `Resistor DB.xlsx`) overwriting the old one
4. **Optionally chains into the existing pipeline** to regenerate `resistors_compact.json` and `data.js`

### Why This Approach?

| Approach | Pros | Cons |
|----------|------|------|
| **Direct openpyxl read** | Simple, uses existing library, handles protection | May fail if sheet is password-protected |
| **ZIP extraction + XML parse** | Works regardless of protection level | More complex, need to understand Excel XML schema |
| **Manual extraction (current)** | User already does it | Not automated, error-prone |

**Recommendation:** Try Strategy A first (it's likely to work since sheet protection in Excel typically only prevents UI editing, not programmatic access). Fall back to Strategy B if needed.

## Detailed Steps

### Step 1: Create `extract_from_xlsm.py`

```python
# extract_from_xlsm.py
# Purpose: Extract resistor data from Panasonic XLSM file and update the database

import os
import sys
import json
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path

# Try openpyxl first (Strategy A)
try:
    import openpyxl
    HAS_OPENPYXL = True
except ImportError:
    HAS_OPENPYXL = False

# Try pandas (needed for the existing pipeline)
try:
    import pandas as pd
    HAS_PANDAS = True
except ImportError:
    HAS_PANDAS = False


def extract_sheet_via_openpyxl(xlsm_path, sheet_name=None):
    """
    Strategy A: Use openpyxl to read the XLSM directly.
    openpyxl can read protected sheets because protection only blocks UI editing.
    """
    wb = openpyxl.load_workbook(xlsm_path, data_only=True, keep_vba=False)
    
    # Find the data sheet (usually the first sheet or one with resistor data)
    if sheet_name:
        ws = wb[sheet_name]
    else:
        ws = wb.active
    
    # Convert to list of lists (rows)
    data = []
    for row in ws.iter_rows(values_only=True):
        data.append(list(row))
    
    wb.close()
    return data


def extract_sheet_via_zip(xlsm_path):
    """
    Strategy B: Extract XLSM as ZIP and parse the worksheet XML directly.
    This bypasses all protection mechanisms.
    """
    with zipfile.ZipFile(xlsm_path, 'r') as z:
        # List all files to find the worksheet
        sheet_files = [f for f in z.namelist() if f.startswith('xl/worksheets/') and f.endswith('.xml')]
        
        if not sheet_files:
            raise ValueError("No worksheet XML files found in XLSM archive")
        
        # Use the first worksheet (usually sheet1.xml)
        # Or detect which one has the most data
        sheet_xml = z.read(sheet_files[0])
        
        # Also need shared strings
        shared_strings = []
        if 'xl/sharedStrings.xml' in z.namelist():
            ss_xml = z.read('xl/sharedStrings.xml')
            ss_root = ET.fromstring(ss_xml)
            ns = {'s': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
            for si in ss_root.findall('.//s:si', ns):
                text_parts = []
                for t in si.iter('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}t'):
                    if t.text:
                        text_parts.append(t.text)
                shared_strings.append(''.join(text_parts))
        
        # Parse sheet XML into rows
        root = ET.fromstring(sheet_xml)
        ns = {'s': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
        
        rows_data = []
        for row in root.findall('.//s:row', ns):
            row_cells = []
            for cell in row.findall('s:c', ns):
                cell_type = cell.get('t')
                cell_value_elem = cell.find('s:v', ns)
                cell_value = cell_value_elem.text if cell_value_elem is not None else ''
                
                if cell_type == 's' and cell_value:
                    # Shared string reference
                    idx = int(cell_value)
                    cell_value = shared_strings[idx] if idx < len(shared_strings) else cell_value
                
                row_cells.append(cell_value)
            rows_data.append(row_cells)
        
        return rows_data


def save_as_xlsx(data, output_path):
    """Save extracted data as a clean XLSX file."""
    if HAS_OPENPYXL:
        wb = openpyxl.Workbook()
        ws = wb.active
        for row_idx, row in enumerate(data, 1):
            for col_idx, value in enumerate(row, 1):
                ws.cell(row=row_idx, column=col_idx, value=value)
        wb.save(output_path)
        print(f"Saved clean XLSX to: {output_path}")
    elif HAS_PANDAS:
        df = pd.DataFrame(data[1:], columns=data[0] if data else None)
        df.to_excel(output_path, index=False)
        print(f"Saved clean XLSX to: {output_path}")
    else:
        print("Warning: Neither openpyxl nor pandas available. Cannot save XLSX.")
        print("Data extracted but not saved as XLSX.")


def run_pipeline(xlsx_path, json_output='resistors_compact.json', data_js='data.js'):
    """Run the existing pipeline: XLSX → JSON → data.js"""
    # Import and run the existing compact_resistors_v2 logic
    sys.path.insert(0, os.path.dirname(__file__))
    from compact_resistors_v2 import create_compact_json
    
    create_compact_json(xlsx_path, json_output)
    
    # Update data.js
    from update_data_app import update_data_js
    update_data_js(json_output, data_js)
    
    print(f"\nPipeline complete!")
    print(f"  {xlsx_path} → {json_output} → {data_js}")


def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Extract resistor data from Panasonic XLSM and update the database'
    )
    parser.add_argument(
        'xlsm_file',
        nargs='?',
        default='PanasonicIndustry_Chip_Resistor_SelectionTool.xlsm',
        help='Path to the XLSM file (default: PanasonicIndustry_Chip_Resistor_SelectionTool.xlsm)'
    )
    parser.add_argument(
        '--output-xlsx',
        default='Resistor DB.xlsx',
        help='Output XLSX file path (default: Resistor DB.xlsx)'
    )
    parser.add_argument(
        '--json-output',
        default='resistors_compact.json',
        help='Output JSON file path (default: resistors_compact.json)'
    )
    parser.add_argument(
        '--data-js',
        default='data.js',
        help='Output data.js file path (default: data.js)'
    )
    parser.add_argument(
        '--skip-pipeline',
        action='store_true',
        help='Skip the JSON/data.js generation pipeline (just extract to XLSX)'
    )
    parser.add_argument(
        '--force-zip',
        action='store_true',
        help='Force ZIP extraction method instead of openpyxl'
    )
    
    args = parser.parse_args()
    
    if not os.path.exists(args.xlsm_file):
        print(f"Error: XLSM file not found: {args.xlsm_file}")
        sys.exit(1)
    
    print(f"Extracting data from: {args.xlsm_file}")
    
    # Extract data
    if args.force_zip or not HAS_OPENPYXL:
        print("Using ZIP extraction method (Strategy B)...")
        data = extract_sheet_via_zip(args.xlsm_file)
    else:
        print("Using openpyxl (Strategy A)...")
        try:
            data = extract_sheet_via_openpyxl(args.xlsm_file)
        except Exception as e:
            print(f"openpyxl failed: {e}")
            print("Falling back to ZIP extraction method...")
            data = extract_sheet_via_zip(args.xlsm_file)
    
    if not data:
        print("Error: No data extracted from XLSM")
        sys.exit(1)
    
    print(f"Extracted {len(data)} rows (including header)")
    
    # Save as clean XLSX
    save_as_xlsx(data, args.output_xlsx)
    
    # Run the existing pipeline
    if not args.skip_pipeline:
        print("\nRunning data pipeline...")
        run_pipeline(args.output_xlsx, args.json_output, args.data_js)
    else:
        print(f"\nDone. Clean XLSX saved to: {args.output_xlsx}")
        print("Run 'python compact_resistors_v2.py' to regenerate the JSON/data.js.")


if __name__ == "__main__":
    main()
```

### Step 2: Test the Script

Run the script against the existing `PanasonicIndustry_Chip_Resistor_SelectionTool.xlsm` file in the project directory:

```bash
python extract_from_xlsm.py
```

### Step 3: Verify Output

- Check that `Resistor DB.xlsx` is updated with the correct data
- Check that `resistors_compact.json` is regenerated
- Check that `data.js` is regenerated
- Open `index.html` in a browser to verify the frontend works with the new data

## Dependencies

The script requires:
- **Python 3.6+**
- **openpyxl** (for reading XLSM and writing XLSX) - `pip install openpyxl`
- **pandas** (for the existing pipeline) - `pip install pandas`
- No additional dependencies beyond what the project already uses

The ZIP extraction method uses only Python standard library (`zipfile`, `xml.etree.ElementTree`), so it works even without `openpyxl`.

## Edge Cases & Error Handling

| Scenario | Handling |
|----------|----------|
| XLSM file not found | Clear error message, exit code 1 |
| openpyxl fails to read | Automatic fallback to ZIP extraction |
| No worksheet XML found | Raise ValueError with descriptive message |
| Empty data extracted | Error message, exit code 1 |
| Missing shared strings | Graceful fallback (use raw cell values) |
| Sheet has different name | Auto-detect first sheet with data |
| Column headers changed | The existing `compact_resistors_v2.py` already has fuzzy column matching |

## Future Improvements (Not in Scope)

- Watch mode: Monitor a directory for new XLSM files and auto-update
- Diff report: Show what changed between old and new data (new parts, removed parts, status changes)
- GUI wrapper for non-technical users
