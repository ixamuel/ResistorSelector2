import pandas as pd
import json
import os

def create_compact_json(xlsx_path, output_json):
    df = pd.read_excel(xlsx_path)
    df = df.fillna("")
    
    # Define column mapping based on the Excel headers
    # 'Products', 'Parts Number', 'Status', 'Series', 'Power Rating\n（W）', 'Chip Size (LxW(EIA))\n（ｍｍ）', 'Resistance Values\n（Ω）', 'Resistance Tolerance\n（%）', 'Packaging', 'T.C.R\n（×10⁻⁶/K）'
    
    mapping = {
        'Products': 'p',
        'Parts Number': 'pn',
        'Status': 's',
        'Series': 'se',
        'Power Rating\n（W）': 'pr',
        'Chip Size (LxW(EIA))\n（ｍｍ）': 'sz',
        'Resistance Values\n（Ω）': 'rv',
        'Resistance Tolerance\n（%）': 'rt',
        'Packaging': 'pk',
        'T.C.R\n（×10⁻⁶/K）': 'tc'
    }
    
    # Rename columns that exist in the dataframe
    actual_columns = df.columns.tolist()
    rename_dict = {}
    for col in actual_columns:
        if col in mapping:
            rename_dict[col] = mapping[col]
        else:
            # Fallback for slight variations in encoding or newlines
            clean_col = col.replace('\n', ' ').strip()
            for k, v in mapping.items():
                if k.replace('\n', ' ').strip() == clean_col:
                    rename_dict[col] = v
                    break
    
    df = df.rename(columns=rename_dict)
    
    # Keep only mapped columns that were found
    valid_mapped_cols = [c for c in rename_dict.values()]
    df = df[valid_mapped_cols]
    
    # Clean Resistance Values to float
    def clean_rv(val):
        if isinstance(val, (int, float)):
            return float(val)
        try:
            # Remove units or non-numeric if any (should be clean in XLSX though)
            return float(val)
        except:
            return 0.0

    df['rv'] = df['rv'].apply(clean_rv)
    
    # Create lookups for strings to reduce JSON size
    lookup_cols = ['p', 's', 'se', 'sz', 'rt', 'pk', 'tc', 'pr']
    lookups = {}
    
    for col in lookup_cols:
        if col in df.columns:
            # Sort lookups for consistency
            unique_vals = sorted(df[col].astype(str).unique().tolist())
            lookups[col_name_full(col)] = unique_vals
            # Create reverse mapping
            rl = {v: i for i, v in enumerate(unique_vals)}
            df[col] = df[col].astype(str).map(rl)

    # Convert to list of dicts
    data = df.to_dict(orient='records')
    
    final_obj = {
        'lookups': lookups,
        'resistors': data
    }
    
    # Create directory if doesn't exist
    os.makedirs(os.path.dirname(output_json), exist_ok=True)
    
    with open(output_json, 'w', encoding='utf-8') as f:
        json.dump(final_obj, f, separators=(',', ':'))

    print(f"Created {output_json}")
    print(f"Original Row count: {len(df)}")
    print(f"File size: {os.path.getsize(output_json) / 1024 / 1024:.2f} MB")

def col_name_full(short):
    m = {
        'p': 'products',
        's': 'status',
        'se': 'series',
        'sz': 'size',
        'rt': 'tolerance',
        'pk': 'packaging',
        'tc': 'tcr',
        'pr': 'power'
    }
    return m.get(short, short)

if __name__ == "__main__":
    xlsx = 'c:/Users/samue/Downloads/agrav - resistor/Resistors.xlsx'
    output = 'c:/Users/samue/Downloads/agrav - resistor/v2/resistors_compact.json'
    create_compact_json(xlsx, output)
