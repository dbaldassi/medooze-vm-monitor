import os
import glob
import csv

def uniformize_csv(file_path, out_path, model_ids):
    with open(file_path, newline='') as f_in:
        reader = csv.reader(f_in)
        header = next(reader)
        rows = list(reader)

    # Trouve tous les participants dans le header
    participant_cols = [col for col in header if "participant-" in col]
    found_ids = sorted(set(int(col.split('-')[1].split('_')[0]) for col in participant_cols))
    id_map = {old: new for old, new in zip(found_ids, model_ids)}

    # Remplace dans le header
    new_header = []
    for col in header:
        if "participant-" in col:
            parts = col.split('-')
            num = int(parts[1].split('_')[0])
            suffix = col.split('_', 1)[1]
            new_col = f"participant-{id_map[num]}_{suffix}"
            new_header.append(new_col)
        else:
            new_header.append(col)

    # Remplace dans la colonne PARTICIPANT_ID
    pid_idx = header.index("PARTICIPANT_ID")
    new_rows = []
    for row in rows:
        parts = row[pid_idx].split('-')
        pid = int(parts[1])
        if pid in id_map:
            row[pid_idx] = f"participant-{id_map[pid]}"
        new_rows.append(row)

    # Écrit le nouveau fichier
    with open(out_path, "w", newline='') as f_out:
        writer = csv.writer(f_out)
        writer.writerow(new_header)
        writer.writerows(new_rows)

if __name__ == "__main__":
    # Modèle de participants : 1 à 10
    model_ids = list(range(1, 11))
    for file_path in glob.glob("*_average.csv"):
        out_path = file_path.replace(".csv", "_uniform.csv")
        uniformize_csv(file_path, out_path, model_ids)
        print(f"Fichier traité : {file_path} → {out_path}")
