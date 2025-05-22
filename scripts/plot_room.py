#!/usr/bin/env python3

import pandas as pd
import matplotlib.pyplot as plt
import sys
import os
import re

if len(sys.argv) < 2:
    print("Usage: python plot_room.py <csv_file>")
    sys.exit(1)

csv_file = sys.argv[1]
outdir = os.path.dirname(os.path.abspath(csv_file))
df = pd.read_csv(csv_file)

df = df[["TIME", "PARTICIPANT_ID", "SENT_BITRATE", "SENT_RTT"] + [col for col in df.columns if re.match(r'participant-\d+_BITRATE', col)]]

# Convertir le timestamp en secondes
df["TIME"] = df["TIME"] / 1000

# --- FIGURE 1 : SENT_BITRATE ---
for pid, group in df.groupby("PARTICIPANT_ID"):
    plt.scatter(group["TIME"], group["SENT_BITRATE"], s=10, alpha=0.5, label=pid)

mean_bitrate = df.groupby("TIME")["SENT_BITRATE"].mean()
plt.plot(mean_bitrate.index, mean_bitrate.values, color='black', linewidth=2, label="Moyenne")

plt.xlabel("Timestamp (s)")
plt.ylabel("Sent Bitrate (kbps)")
plt.title("Sent Bitrate par participant et moyenne")
plt.legend(markerscale=2, fontsize=8)
plt.tight_layout()

img_file = os.path.join(outdir, os.path.splitext(os.path.basename(csv_file))[0] + "_sent_bitrate.png")
plt.savefig(img_file)
plt.close()

# --- FIGURE 2 : SENT_RTT ---
plt.figure()
for pid, group in df.groupby("PARTICIPANT_ID"):
    plt.scatter(group["TIME"], group["SENT_RTT"], s=10, alpha=0.5, label=pid)

mean_rtt = df.groupby("TIME")["SENT_RTT"].mean()
plt.plot(mean_rtt.index, mean_rtt.values, color='red', linewidth=2, label="Moyenne")

plt.xlabel("Timestamp (s)")
plt.ylabel("Sent RTT (ms)")
plt.title("Sent RTT par participant et moyenne")
plt.legend(markerscale=2, fontsize=8)
plt.tight_layout()

img_file_rtt = os.path.join(outdir, os.path.splitext(os.path.basename(csv_file))[0] + "_sent_rtt.png")
plt.savefig(img_file_rtt)
plt.close()

# --- FIGURE 3 : RECEIVED BITRATE (MOYENNE) ---
recv_cols = [col for col in df.columns if re.match(r'participant-\d+_BITRATE', col)]
if recv_cols:
    df["RECEIVED_BITRATE_MEAN"] = df[recv_cols].mean(axis=1)
    plt.figure()
    for pid, group in df.groupby("PARTICIPANT_ID"):
        plt.scatter(group["TIME"], group["RECEIVED_BITRATE_MEAN"], s=10, alpha=0.5, label=pid)
    mean_received = df.groupby("TIME")["RECEIVED_BITRATE_MEAN"].mean()
    plt.plot(mean_received.index, mean_received.values, color='green', linewidth=2, label="Moyenne globale")
    plt.xlabel("Timestamp (s)")
    plt.ylabel("Mean Received Bitrate (kbps)")
    plt.title("Bitrate moyen reçu par participant et moyenne globale")
    plt.legend(markerscale=2, fontsize=8)
    plt.tight_layout()
    img_file_recv = os.path.join(outdir, os.path.splitext(os.path.basename(csv_file))[0] + "_mean_received_bitrate.png")
    plt.savefig(img_file_recv)
    plt.close()