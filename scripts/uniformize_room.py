#!/usr/bin/env python3

import csv
import sys
from collections import defaultdict

if len(sys.argv) != 2:
    print("Usage: python uniformize_room.py <input_file.csv>")
    sys.exit(1)

input_file = sys.argv[1]
output_file = sys.argv[1]

FIXED_HEADERS = [ "TIME","PARTICIPANT_ID","NUM_PARTICIPANTS","SENT_RTT","SENT_BITRATE","SENT_FPS" ]
PARTICIPANTS_HEADER = ["BITRATE", "RTT", "FPS"]

# 1. Lire toutes les lignes et collecter tous les participants uniques
rows = []
with open(input_file, newline='', encoding='utf-8') as csvfile:
    reader = csv.reader(csvfile)
    for row in reader:
        rows.append(row)

# 2. Identifier les participants initiaux
initial_participants = []
# print(rows[0])
for i  in range(len(FIXED_HEADERS), len(rows[0]), len(PARTICIPANTS_HEADER)):
    participant_header = rows[0][i]
    split_header = participant_header.split('_')
    participant_id = split_header[0]
    initial_participants.append(participant_id)

# print(f"Participants initiaux identifiés : {initial_participants}")

# 3. Identifier les nouveaux participants
new_participants = []
PARTICIPANT_ID = FIXED_HEADERS.index("PARTICIPANT_ID")

for row in rows[1:]:
    participant = row[PARTICIPANT_ID]
    if participant not in initial_participants and not any(participant == p[1] for p in new_participants):
        timestamp = row[0]
        new_participants.append((timestamp, participant))

# print(f"Nouveaux participants identifiés : {new_participants}")

# 4. Add new participants to the header
new_participant_headers = []
for _, participant in new_participants:
    for header in PARTICIPANTS_HEADER:
        new_participant_headers.append(f"{participant}_{header}")

rows[0].extend(new_participant_headers)

# 5. Réécrire le fichier CSV avec les nouveaux participants
num_participants = len(initial_participants) + len(new_participants)
NUM_PARTICIPANTS_INDEX = FIXED_HEADERS.index("NUM_PARTICIPANTS")

for row in rows[1:]:
    # replace empty strings by 0
    for i in range(len(row)):
        if row[i] == '':
            row[i] = '0'

    for _, participant in new_participants:
        # Initialize new participant fields with empty strings
        # row[NUM_PARTICIPANTS_INDEX] = str(num_participants)
        column_to_add =  len(rows[0]) - len(row)
        row.extend([''] * column_to_add)

# 6. Write the updated rows to the output file
with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerows(rows)

print(f"Fichier uniformisé écrit dans {output_file}")