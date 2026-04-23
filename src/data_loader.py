# src/data_loader.py
"""
data loader model
response for the data loader from multi-format files
"""

import pandas as pd
import os

def load_data(filepath):
    """load data"""
    print(f"📂 load data: {filepath}")
    
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"data file not exist: {filepath}")
    
    # read methods based on the extend fiel name
    if filepath.endswith('.csv'):
        df = _load_csv(filepath)
    elif filepath.endswith('.xlsx') or filepath.endswith('.xls'):
        df = pd.read_excel(filepath)
        print("✅ read Excel file")
    else:
        raise ValueError("unsupported format, please use CSV orExcel")
    
    print(f"✅ successfully load {len(df)} line data")
    print(f"📊 column data: {', '.join(df.columns.tolist())}")
    
    return df

def _load_csv(filepath):
    """load csv file, auto detect the separator"""
    try:
        # fill the separator
        df = pd.read_csv(filepath, sep='\t')
        print("✅ use tab delimiters")
        return df
    except:
        try:
            # try comma separation
            df = pd.read_csv(filepath)
            print("✅ use comma separation")
            return df
        except Exception as e:
            # auto detect
            with open(filepath, 'r') as f:
                first_line = f.readline()
                if '\t' in first_line:
                    df = pd.read_csv(filepath, sep='\t')
                    print("✅ auto detect tab delimiters")
                    return df
                else:
                    df = pd.read_csv(filepath)
                    print("✅ auto detect comma separation")
                    return df