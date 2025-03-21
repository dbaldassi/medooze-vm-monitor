#!/bin/bash
# filepath: /Users/david/Documents/remote-vm-monitor/monitor_vm_memory.sh

# Nom de la VM
VM_NAME="medooze"

# Fichier de sortie pour les statistiques mémoire
OUTPUT_FILE="vm_memory_stats.csv"

# Durée de la surveillance en secondes
DURATION=60

# Intervalle entre chaque collecte de données (en secondes)
INTERVAL=1

# Vérifier si la VM existe
if ! virsh dominfo "$VM_NAME" &>/dev/null; then
    echo "Erreur : La VM '$VM_NAME' n'existe pas."
    exit 1
fi

# Démarrer la VM si elle n'est pas déjà en cours d'exécution
if ! virsh list --state-running | grep -q "$VM_NAME"; then
    echo "Démarrage de la VM '$VM_NAME'..."
    virsh start "$VM_NAME"
fi

# Écrire l'en-tête du fichier CSV
echo "timestamp,actual,swap_in,swap_out,unused,available,usable" > "$OUTPUT_FILE"

# Calculer l'heure de fin
END_TIME=$(( $(date +%s) + DURATION ))

echo "Surveillance de la mémoire de la VM '$VM_NAME' pendant $DURATION secondes..."

# Boucle pour collecter les statistiques mémoire
while [ $(date +%s) -lt $END_TIME ]; do
    TIMESTAMP=$(date +%s) # Timestamp en secondes

    # Collecter les statistiques mémoire avec virsh dommemstat
    MEM_STATS=$(virsh dommemstat "$VM_NAME" 2>/dev/null)

    # Extraire les valeurs des statistiques
    ACTUAL=$(echo "$MEM_STATS" | awk '/actual/ {print $2}')
    SWAP_IN=$(echo "$MEM_STATS" | awk '/swap_in/ {print $2}')
    SWAP_OUT=$(echo "$MEM_STATS" | awk '/swap_out/ {print $2}')
    UNUSED=$(echo "$MEM_STATS" | awk '/unused/ {print $2}')
    AVAILABLE=$(echo "$MEM_STATS" | awk '/available/ {print $2}')
    USABLE=$(echo "$MEM_STATS" | awk '/usable/ {print $2}')

    # Écrire les données dans le fichier CSV
    echo "$TIMESTAMP,$ACTUAL,$SWAP_IN,$SWAP_OUT,$UNUSED,$AVAILABLE,$USABLE" >> "$OUTPUT_FILE"

    # Attendre avant la prochaine collecte
    sleep "$INTERVAL"
done

echo "Surveillance terminée. Les données sont enregistrées dans '$OUTPUT_FILE'."