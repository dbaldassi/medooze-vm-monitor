#!/usr/bin/python3

import os
import glob
import pandas as pd
from datetime import datetime

def process_folder(folder_path, output_file):
    csv_files = glob.glob(os.path.join(folder_path, "*.csv"))
    # dfs = [pd.read_csv(f) for f in csv_files]
    dfs = []
    for f in csv_files:
        try:
            df = pd.read_csv(f, encoding='utf-8')
            if 'TIME' in df.columns and 'PARTICIPANT_ID' in df.columns:
                dfs.append(df)
            else:
                print(f"Skipping {f}: missing TIME or PARTICIPANT_ID columns.")
        except Exception as e:
            print(f"Error reading {f}: {e}")

    # Nettoie les colonnes (enlève les espaces, etc.)
    for i, df in enumerate(dfs):
        df.columns = [c.strip() for c in df.columns]
        dfs[i] = df

    # Fusionne sur TIME et PARTICIPANT_ID
    merged = dfs[0]
    for df in dfs[1:]:
        merged = pd.merge(
            merged, df, 
            on=['TIME', 'PARTICIPANT_ID'], 
            suffixes=(None, '_dup'), 
            how='inner'
        )

    # Pour chaque colonne numérique, calcule la moyenne des colonnes dupliquées
    result = merged[['TIME', 'PARTICIPANT_ID']].copy()
    base_cols = [col for col in dfs[0].columns if col not in ['TIME', 'PARTICIPANT_ID']]
    for col in base_cols:
        # Récupère toutes les colonnes correspondantes (col, col_dup, col_dup_dup, etc.)
        col_versions = [c for c in merged.columns if c.startswith(col)]
        result[col] = merged[col_versions].mean(axis=1)

    # Réordonne les colonnes comme à l'origine
    result = result[['TIME', 'PARTICIPANT_ID'] + base_cols]
    result.to_csv(output_file, index=False)

if __name__ == "__main__":
    dir_name = os.path.basename(os.getcwd())
    date_str = datetime.today().strftime('%Y-%m-%d-%H-%M-%S')
    out_filename = f"{dir_name}_{date_str}_average.csv"
    process_folder(os.getcwd(), out_filename)