#!/usr/bin/env python3

import os
import re
import csv
import matplotlib
import matplotlib.pyplot as plt

import scienceplots

plt.style.use(['science','ieee'])

plt.rcParams.update({
    "font.size": 10
})

# colors = matplotlib.cm.get_cmap('Set2').colors
colors = ['#1b9e77', '#d95f02', '#7570b3', '#e7298a', '#66a61e', '#e6ab02', '#a6761d', '#666666']
plt.rcParams['axes.prop_cycle'] = matplotlib.cycler(color=colors)

# --- CONFIGURATION ---
INDICATOR = "avg"      # "avg", "median", etc.
# Y_HEADER = "VIRSH USABLE"
Y_HEADER = "PUBLISHER BITRATE"
X_HEADER = "TIME"

VAR_PARAM = "ki"       # "kp", "ki", ou "kd" (le paramètre à comparer)
FIXED_KP = 0.3         # valeur à fixer pour kp (si VAR_PARAM != "kp")
FIXED_KI = 0         # valeur à fixer pour ki (si VAR_PARAM != "ki")
FIXED_KD = 2        # valeur à fixer pour kd (si VAR_PARAM != "kd")

ROOT_DIR = "."

indicators = ["avg", "1stq", "median", "3rdq", "min", "max"]
def get_index(header_idx, indicator):
    indicator_idx = indicators.index(indicator)
    return header_idx * len(indicators) + indicator_idx

def extract_pid_params(dirname):
    m = re.match(r'balloon-pid-compare-([\d\.]+)-([\d\.]+)-([\d\.]+)', dirname)
    if m:
        return float(m.group(1)), float(m.group(2)), float(m.group(3))
    return None, None, None

# --- Filtrer les dossiers selon les paramètres ---
exp_dirs = []
for d in os.listdir(ROOT_DIR):
    # print(d, extract_pid_params(d))
    if re.match(r'balloon-pid-compare-\d+\.?\d*-\d+\.?\d*-\d+\.?\d*', d):
        # print("Dossier correspondant trouvé :", d)
        kp, ki, kd = extract_pid_params(d)
        if VAR_PARAM == "kp" and ki == FIXED_KI and kd == FIXED_KD:
            exp_dirs.append(d)
        elif VAR_PARAM == "ki" and kp == FIXED_KP and kd == FIXED_KD:
            exp_dirs.append(d)
        elif VAR_PARAM == "kd" and kp == FIXED_KP and ki == FIXED_KI:
            exp_dirs.append(d)

print("Expériences sélectionnées :", exp_dirs)

# --- Récupérer les fichiers CSV ---
csv_files = []
for d in exp_dirs:
    for f in os.listdir(os.path.join(ROOT_DIR, d)):
        if re.match(r".*_average_.*\.csv$", f):
            csv_files.append(os.path.join(ROOT_DIR, d, f))

print("CSV trouvés :", csv_files)

# --- Plot ---
# plt.figure(figsize=(12, 6))
# for csv_file in csv_files:
#     dirname = os.path.basename(os.path.dirname(csv_file))
#     kp, ki, kd = extract_pid_params(dirname)
#     if VAR_PARAM == "kp":
#         label = f"kp={kp}"
#     elif VAR_PARAM == "ki":
#         label = f"ki={ki}"
#     elif VAR_PARAM == "kd":
#         label = f"kd={kd}"

#     # Lire le CSV
#     with open(csv_file, 'r') as f:
#         reader = csv.reader(f)
#         headers = next(reader)
#         data = list(reader)

#     x_idx = headers.index(X_HEADER)
#     y_idx = headers.index(Y_HEADER)

#     x_col = x_idx + indicators.index(INDICATOR) # get_index(x_idx, INDICATOR)
#     y_col = y_idx + indicators.index(INDICATOR) # get_index(y_idx, INDICATOR)

#     x_vals = [float(row[x_col])/1000 for row in data if row[x_col] != '']
#     # y_vals = [float(row[y_col])/(1024*1024) for row in data if row[y_col] != '']
#     y_vals = [float(row[y_col]) for row in data if row[y_col] != '']

#     plt.plot(x_vals, y_vals, label=label)

# plt.xlabel(f"Temps (s)")
# plt.ylabel(f"Débit émetteur (kbps)")
# plt.legend()
# plt.tight_layout()
# plt.savefig(f"pid_compare_{VAR_PARAM}_{Y_HEADER}_{INDICATOR}.pdf")
# plt.close()
# print(f"Plot enregistré : pid_compare_{VAR_PARAM}_{Y_HEADER}_{INDICATOR}.pdf")

# --- Plot PUBLISHER BITRATE ---
for idx, csv_file in enumerate(csv_files):
    dirname = os.path.basename(os.path.dirname(csv_file))
    kp, ki, kd = extract_pid_params(dirname)
    label = f"{VAR_PARAM}={kp if VAR_PARAM=='kp' else ki if VAR_PARAM=='ki' else kd}"

    with open(csv_file, 'r') as f:
        reader = csv.reader(f)
        headers = next(reader)
        data = list(reader)

    x_idx = headers.index("TIME")
    y_idx = headers.index("PUBLISHER BITRATE")
    x_col = x_idx + indicators.index(INDICATOR)
    y_col = y_idx + indicators.index(INDICATOR)
    x_vals = [float(row[x_col])/1000 for row in data if row[x_col] != '']
    y_vals = [float(row[y_col]) for row in data if row[y_col] != '']

    plt.plot(x_vals, y_vals, label=label, color=colors[idx % len(colors)])

plt.xlabel("Temps (s)")
plt.ylabel("Débit émetteur (kbps)")
plt.legend()
plt.tight_layout()
plt.savefig(f"pid_compare_{VAR_PARAM}_PUBLISHER_BITRATE_{INDICATOR}.pdf")
plt.close()
print(f"Plot enregistré : pid_compare_{VAR_PARAM}_PUBLISHER_BITRATE_{INDICATOR}.pdf")

# --- Plot VIRSH USABLE + barre rouge ---
for idx, csv_file in enumerate(csv_files):
    dirname = os.path.basename(os.path.dirname(csv_file))
    kp, ki, kd = extract_pid_params(dirname)
    label = f"{VAR_PARAM}={kp if VAR_PARAM=='kp' else ki if VAR_PARAM=='ki' else kd}"

    with open(csv_file, 'r') as f:
        reader = csv.reader(f)
        headers = next(reader)
        data = list(reader)

    x_idx = headers.index("TIME")
    y_idx = headers.index("VIRSH USABLE")
    x_col = x_idx + indicators.index(INDICATOR)
    y_col = y_idx + indicators.index(INDICATOR)
    x_vals = [float(row[x_col])/1000 for row in data if row[x_col] != '']
    y_vals = [float(row[y_col])/(1024) for row in data if row[y_col] != '']

    plt.plot(x_vals, y_vals, label=label, color=colors[idx % len(colors)])

# if csv_files:
#     csv_file = csv_files[0]
#     dirname = os.path.basename(os.path.dirname(csv_file))
#     kp, ki, kd = extract_pid_params(dirname)
#     label_vm = f"Mémoire utilisée"

#     with open(csv_file, 'r') as f:
#         reader = csv.reader(f)
#         headers = next(reader)
#         data = list(reader)

#     x_idx = headers.index("TIME")
#     y_idx_vm = headers.index("VM MEMORY USAGE")
#     x_col = x_idx + indicators.index(INDICATOR)
#     y_col_vm = y_idx_vm + indicators.index(INDICATOR)
#     x_vals_vm = [float(row[x_col])/1000 for row in data if row[x_col] != '']
#     y_vals_vm = [float(row[y_col_vm]) for row in data if row[y_col_vm] != '']

#     plt.plot(x_vals_vm, y_vals_vm, label=label_vm, color='black', linestyle='dotted')

# Barre horizontale rouge à 200 MiB
plt.axhline(200, color='red', linestyle='--', linewidth=1, label='Target 200 MiB')

plt.xlabel("Temps (s)")
plt.ylabel("Mémoire libre (MiB)")
plt.legend()
plt.tight_layout()
plt.savefig(f"pid_compare_{VAR_PARAM}_VIRSH_USABLE_{INDICATOR}.pdf")
plt.close()
print(f"Plot enregistré : pid_compare_{VAR_PARAM}_VIRSH_USABLE_{INDICATOR}.pdf")

for idx, csv_file in enumerate(csv_files):
    dirname = os.path.basename(os.path.dirname(csv_file))
    kp, ki, kd = extract_pid_params(dirname)
    label = f"{VAR_PARAM}={kp if VAR_PARAM=='kp' else ki if VAR_PARAM=='ki' else kd}"

    with open(csv_file, 'r') as f:
        reader = csv.reader(f)
        headers = next(reader)
        data = list(reader)

    x_idx = headers.index("TIME")
    y_idx = headers.index("VM CPU USAGE")
    x_col = x_idx + indicators.index(INDICATOR)
    y_col = y_idx + indicators.index(INDICATOR)
    x_vals = [float(row[x_col])/1000 for row in data if row[x_col] != '']
    y_vals = [max(0, float(row[y_col]))*100 for row in data if row[y_col] != '']

    plt.plot(x_vals, y_vals, label=label, color=colors[idx % len(colors)])

plt.xlabel("Temps (s)")
plt.ylabel("CPU (\%)")
plt.legend()
plt.tight_layout()
plt.savefig(f"pid_compare_{VAR_PARAM}_VM_CPU_USAGE_{INDICATOR}.pdf")
plt.close()
print(f"Plot enregistré : pid_compare_{VAR_PARAM}_VM_CPU_USAGE_{INDICATOR}.pdf")