#!/bin/sh
# filepath: initramfs-monitor/monitor_memory.sh

OUTPUT_FILE="/memory_stats.csv"
DURATION=60 # Durée en secondes avant l'arrêt automatique

# Écrire l'en-tête du fichier CSV
echo "timestamp,total_memory,free_memory,used_memory" > $OUTPUT_FILE

# Calculer l'heure de fin
END_TIME=$(( $(date +%s) + DURATION ))

# Boucle pour collecter les statistiques jusqu'à la fin du délai
while [ $(date +%s) -lt $END_TIME ]; do
    # Récupérer les informations mémoire depuis /proc/meminfo
    TIMESTAMP=$(date +%s%3N) # Timestamp en millisecondes
    TOTAL_MEMORY=$(grep MemTotal /proc/meminfo | awk '{print $2}')
    FREE_MEMORY=$(grep MemFree /proc/meminfo | awk '{print $2}')
    USED_MEMORY=$((TOTAL_MEMORY - FREE_MEMORY))

    # Écrire les données dans le fichier CSV
    echo "$TIMESTAMP,$TOTAL_MEMORY,$FREE_MEMORY,$USED_MEMORY" >> $OUTPUT_FILE

    # Attendre 50ms
    usleep 50000
done

echo "Monitoring terminé après $DURATION secondes."