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

df = df[["TIME", "PARTICIPANT_ID", "NUM_PARTICIPANTS", "SENT_BITRATE", "SENT_RTT", "SENT_FPS"] + [col for col in df.columns if re.match(r'participant-\d+_BITRATE', col)] +  [col for col in df.columns if re.match(r'participant-\d+_FPS', col)]]

# Convertir le timestamp en secondes
df["TIME"] = df["TIME"] / 1000

df["SENT_BITRATE"] = pd.to_numeric(df["SENT_BITRATE"], errors="coerce")
df.loc[df["SENT_BITRATE"] < 0, "SENT_BITRATE"] = 0
df["SENT_BITRATE"] = df["SENT_BITRATE"].fillna(0)

print(df["SENT_BITRATE"].head(20))
print(df["SENT_BITRATE"].dtype)
print(df["SENT_BITRATE"].min(), df["SENT_BITRATE"].max())

# --- FIGURE 1 : SENT_BITRATE ---
for pid, group in df.groupby("PARTICIPANT_ID"):
    plt.scatter(group["TIME"], group["SENT_BITRATE"], s=10, alpha=0.5, label=pid)

mean_bitrate = df.groupby("TIME")["SENT_BITRATE"].mean().clip(lower=0)
print(mean_bitrate)
plt.plot(mean_bitrate.index, mean_bitrate.values, color='black', linewidth=2, label="Moyenne")

plt.xlabel("Timestamp (s)")
plt.ylabel("Sent Bitrate (kbps)")
plt.title("Sent Bitrate par participant et moyenne")
# plt.legend(markerscale=2, fontsize=8)
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
# plt.legend(markerscale=2, fontsize=8)
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
    plt.plot(mean_received.index, mean_received.values, color='black', linewidth=2, label="Moyenne globale")
    plt.xlabel("Timestamp (s)")
    plt.ylabel("Mean Received Bitrate (kbps)")
    plt.title("Bitrate moyen reçu par participant et moyenne globale")
    # plt.legend(markerscale=2, fontsize=8)
    plt.tight_layout()
    img_file_recv = os.path.join(outdir, os.path.splitext(os.path.basename(csv_file))[0] + "_mean_received_bitrate.png")
    plt.savefig(img_file_recv)
    plt.close()


# --- FIGURE 4 : SENT_FPS ---
plt.figure()
for pid, group in df.groupby("PARTICIPANT_ID"):
    if "SENT_FPS" in group:
        plt.scatter(group["TIME"], group["SENT_FPS"], s=10, alpha=0.5, label=pid)

mean_fps = df.groupby("TIME")["SENT_FPS"].mean()
plt.plot(mean_fps.index, mean_fps.values, color='blue', linewidth=2, label="Moyenne")

plt.xlabel("Timestamp (s)")
plt.ylabel("Sent FPS")
plt.title("Sent FPS par participant et moyenne")
plt.tight_layout()
img_file_fps = os.path.join(outdir, os.path.splitext(os.path.basename(csv_file))[0] + "_sent_fps.png")
plt.savefig(img_file_fps)
plt.close()

# --- FIGURE 5 : RECEIVED FPS (MOYENNE) ---
recv_fps_cols = [col for col in df.columns if re.match(r'participant-\d+_FPS', col)]
if recv_fps_cols:
    df["RECEIVED_FPS_MEAN"] = df[recv_fps_cols].mean(axis=1)
    plt.figure()
    for pid, group in df.groupby("PARTICIPANT_ID"):
        plt.scatter(group["TIME"], group["RECEIVED_FPS_MEAN"], s=10, alpha=0.5, label=pid)
    mean_received_fps = df.groupby("TIME")["RECEIVED_FPS_MEAN"].mean()
    plt.plot(mean_received_fps.index, mean_received_fps.values, color='purple', linewidth=2, label="Moyenne globale")
    plt.xlabel("Timestamp (s)")
    plt.ylabel("Mean Received FPS")
    plt.title("FPS moyen reçu par participant et moyenne globale")
    plt.tight_layout()
    img_file_recv_fps = os.path.join(outdir, os.path.splitext(os.path.basename(csv_file))[0] + "_mean_received_fps.png")
    plt.savefig(img_file_recv_fps)
    plt.close()

# --- FIGURE 6 : Nombre de senders par timestamp ---
plt.figure()
senders_per_time = df.groupby("TIME")["SENT_BITRATE"].apply(lambda x: ((x != 0) & (x != '') & (~pd.isna(x)) & (x.astype(float) > 0)).sum())
num_participants_per_time = df.groupby("TIME")["NUM_PARTICIPANTS"].first()

plt.plot(senders_per_time.index, senders_per_time.values, label="Senders actifs", marker='o')
plt.plot(num_participants_per_time.index, num_participants_per_time.values, label="Participants théoriques", linestyle='--')
plt.xlabel("Timestamp (s)")
plt.ylabel("Nombre de senders")
plt.title("Nombre de senders actifs vs théorique par timestamp")
plt.legend()
plt.tight_layout()
img_file_senders = os.path.join(outdir, os.path.splitext(os.path.basename(csv_file))[0] + "_senders_count.png")
plt.savefig(img_file_senders)
plt.close()

# --- FIGURE 7 : Nombre de viewers reçus ---
recv_cols = [col for col in df.columns if re.match(r'participant-\d+_BITRATE', col)]
if recv_cols:
    # Nombre de viewers reçus par ligne (participant à un timestamp)
    viewers_received_per_row = df[recv_cols].apply(lambda row: ((row != 0) & (row != '') & (~pd.isna(row)) & (row.astype(float) > 0)).sum(), axis=1)
    df["VIEWERS_RECEIVED_COUNT"] = viewers_received_per_row

    # Moyenne du nombre de viewers reçus par participant pour chaque timestamp
    mean_viewers_per_time = df.groupby("TIME")["VIEWERS_RECEIVED_COUNT"].mean()
    # Total de viewers reçus pour chaque timestamp
    total_viewers_per_time = df.groupby("TIME")["VIEWERS_RECEIVED_COUNT"].sum()
    # Nombre de participants théorique
    num_participants_per_time = df.groupby("TIME")["NUM_PARTICIPANTS"].first()
    # Nombre de viewers théoriques par participant
    viewers_theo_per_participant = num_participants_per_time - 1
    # Nombre de viewers théoriques total
    viewers_theo_total = num_participants_per_time * viewers_theo_per_participant

    fig, ax1 = plt.subplots(figsize=(10, 5))
    ax1.plot(mean_viewers_per_time.index, mean_viewers_per_time.values, label="Moyenne viewers reçus/participant", marker='o', color='tab:blue')
    ax1.plot(viewers_theo_per_participant.index, viewers_theo_per_participant.values, label="Viewers théoriques/participant", linestyle='--', color='tab:cyan')
    ax1.set_ylabel("Moyenne viewers reçus/participant", color='tab:blue')
    ax1.tick_params(axis='y', labelcolor='tab:blue')
    ax1.set_xlabel("Timestamp (s)")

    ax2 = ax1.twinx()
    ax2.plot(total_viewers_per_time.index, total_viewers_per_time.values, label="Total viewers reçus", marker='x', color='tab:orange')
    ax2.plot(viewers_theo_total.index, viewers_theo_total.values, label="Total viewers théoriques", linestyle='--', color='tab:red')
    ax2.set_ylabel("Total viewers reçus / théoriques", color='tab:orange')
    ax2.tick_params(axis='y', labelcolor='tab:orange')

    fig.suptitle("Viewers reçus par timestamp")
    fig.tight_layout()
    fig.legend(loc="upper left", bbox_to_anchor=(0.1,0.9))
    img_file_viewers = os.path.join(outdir, os.path.splitext(os.path.basename(csv_file))[0] + "_viewers_count.png")
    plt.savefig(img_file_viewers)
    plt.close()

    # without théorique
    fig, ax1 = plt.subplots(figsize=(10, 5))
    ax1.plot(mean_viewers_per_time.index, mean_viewers_per_time.values, label="Moyenne viewers reçus/participant", marker='o', color='tab:blue')
    ax1.set_ylabel("Moyenne viewers reçus/participant", color='tab:blue')
    ax1.tick_params(axis='y', labelcolor='tab:blue')
    ax1.set_xlabel("Timestamp (s)")

    ax2 = ax1.twinx()
    ax2.plot(total_viewers_per_time.index, total_viewers_per_time.values, label="Total viewers reçus", marker='x', color='tab:orange')
    ax2.set_ylabel("Total viewers reçus", color='tab:orange')
    ax2.tick_params(axis='y', labelcolor='tab:orange')

    fig.suptitle("Viewers reçus par timestamp (sans théorique)")
    fig.tight_layout()
    fig.legend(loc="upper left", bbox_to_anchor=(0.1,0.9))
    img_file_viewers_simple = os.path.join(outdir, os.path.splitext(os.path.basename(csv_file))[0] + "_viewers_count_simple.png")
    plt.savefig(img_file_viewers_simple)
    plt.close()