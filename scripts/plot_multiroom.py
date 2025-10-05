#!/usr/bin/env python3

import pandas as pd
import matplotlib.pyplot as plt
import sys
import os
import re

plt.rcParams.update({
    "font.size": 20
})

if len(sys.argv) < 2:
    print("Usage: python plot_multiroom.py <csv_file1> <csv_file2> ...")
    sys.exit(1)

csv_files = sys.argv[1:]
room_names = [re.match(r'(room\d+)', os.path.basename(f)).group(1) for f in csv_files]

metrics = [
    ("SENT_BITRATE", "Débit émetteur (kbps)"),
    ("SENT_RTT", "RTT (ms)"),
    ("SENT_FPS", "FPS émetteur"),
    ("RECEIVED_BITRATE_MEAN", "Débit moyen reçu (kbps)"),
    ("RECEIVED_FPS_MEAN", "FPS moyen reçu"),
]

# Prépare les données par room
room_data = {}
for csv_file, room_name in zip(csv_files, room_names):
    df = pd.read_csv(csv_file)
    recv_cols = [col for col in df.columns if re.match(r'participant-\d+_BITRATE', col)]
    recv_fps_cols = [col for col in df.columns if re.match(r'participant-\d+_FPS', col)]
    df["TIME"] = df["TIME"] / 1000
    for col in df.columns:
        if col not in ["TIME", "PARTICIPANT_ID"]:
            df[col] = pd.to_numeric(df[col], errors="coerce")
            df.loc[df[col] < 0, col] = 0
            df[col] = df[col].fillna(0)
    # Moyenne des colonnes reçues
    if recv_cols:
        df["RECEIVED_BITRATE_MEAN"] = df[recv_cols].mean(axis=1)
    if recv_fps_cols:
        df["RECEIVED_FPS_MEAN"] = df[recv_fps_cols].mean(axis=1)
    # Moyenne par timestamp pour chaque métrique
    room_data[room_name] = {}
    for metric, _ in metrics:
        if metric in df.columns:
            room_data[room_name][metric] = df.groupby("TIME")[metric].mean()

# Pour chaque métrique, scatter les moyennes de chaque room et plot la moyenne des moyennes
for metric, ylabel in metrics:
    plt.figure()
    all_times = sorted(set().union(*[room_data[room][metric].index for room in room_data if metric in room_data[room]]))
    # Interpoler les moyennes sur tous les timestamps pour chaque room
    interpolated = []
    for room in room_data:
        if metric in room_data[room]:
            series = room_data[room][metric].reindex(all_times).interpolate()
            plt.scatter(series.index, series.values, s=15, alpha=0.7, label=room)
            interpolated.append(series.values)
    # Moyenne des moyennes, en ignorant les NaN (rooms non actives)
    if interpolated:
        df_interp = pd.DataFrame(interpolated).T  # shape: (len(all_times), n_rooms)
        mean_of_means = df_interp.mean(axis=1, skipna=True)
        plt.plot(all_times, mean_of_means, color='black', linewidth=2, label="Moyenne")
    plt.xlabel("Temps (s)")
    plt.ylabel(ylabel)
    plt.legend(markerscale=2, fontsize=10)
    plt.tight_layout()
    plt.savefig(f"multiroom_{metric.lower()}.pdf")
    plt.close()