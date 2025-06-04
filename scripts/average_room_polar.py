#!/usr/bin/python3

import os
import glob
import polars as pl
from datetime import datetime

def process_folder(folder_path, output_file):
    csv_files = glob.glob(os.path.join(folder_path, "*.csv"))
    dfs = []
    for f in csv_files:
        try:
            df = pl.read_csv(f)
            if 'TIME' in df.columns and 'PARTICIPANT_ID' in df.columns:
                dfs.append(df)
            else:
                print(f"Skipping {f}: missing TIME or PARTICIPANT_ID columns.")
        except Exception as e:
            print(f"Error reading {f}: {e}")

    # Nettoie les colonnes (enlève les espaces, etc.)
    for i, df in enumerate(dfs):
        df = df.rename({c: c.strip() for c in df.columns})
        dfs[i] = df

    # Fusionne sur TIME et PARTICIPANT_ID
    merged = dfs[0]
    for i, df in enumerate(dfs[1:], start=1):
        merged = merged.join(df, on=['TIME', 'PARTICIPANT_ID'], how='inner', suffix=f'_dup{i}')

    # Pour chaque colonne numérique, calcule la moyenne des colonnes dupliquées
    result = merged.select(['TIME', 'PARTICIPANT_ID'])
    base_cols = [col for col in dfs[0].columns if col not in ['TIME', 'PARTICIPANT_ID']]
    for col in base_cols:
        # Récupère toutes les colonnes correspondantes (col, col_dup1, col_dup2, etc.)
        col_versions = [c for c in merged.columns if c == col or c.startswith(f"{col}_dup")]
        # Calcule la moyenne ligne par ligne
        result = result.with_columns(
            pl.mean_horizontal([merged[c].cast(pl.Float64) for c in col_versions]).alias(col)
        )

    # Réordonne les colonnes comme à l'origine
    result = result.select(['TIME', 'PARTICIPANT_ID'] + base_cols)
    result.write_csv(output_file)

if __name__ == "__main__":
    dir_name = os.path.basename(os.getcwd())
    date_str = datetime.today().strftime('%Y-%m-%d-%H-%M-%S')
    out_filename = f"{dir_name}_{date_str}_average_polar.csv"
    process_folder(os.getcwd(), out_filename)