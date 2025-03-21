#!/bin/bash
# filepath: vm-memory-monitor/monitor_cgroup_memory.sh

OUTPUT_FILE="cgroup_memory_stats.csv"
CGROUP_BASE="/sys/fs/cgroup/machine.slice"
VM_SCOPE_SUFFIX="medooze.scope"
POLL_INTERVAL=1000000 # Intervalle en microsecondes (1ms)

# Vérifier que inotify-tools est installé
if ! command -v inotifywait &> /dev/null; then
    echo "Erreur : inotifywait (inotify-tools) n'est pas installé. Installez-le avec : sudo apt install inotify-tools"
    exit 1
fi

# Écrire l'en-tête du fichier CSV
echo "timestamp,memory_current" > $OUTPUT_FILE

echo "En attente de la création du dossier cgroup pour la VM..."

# Attendre passivement que le dossier cgroup soit créé
VM_CGROUP_PATH=""
while [ -z "$VM_CGROUP_PATH" ]; do
    NEW_PATH=$(inotifywait -e create --format '%w%f' "$CGROUP_BASE" 2>/dev/null)
    if [[ "$NEW_PATH" == *"$VM_SCOPE_SUFFIX" ]]; then
        VM_CGROUP_PATH="$NEW_PATH"
        echo "Dossier cgroup trouvé : $VM_CGROUP_PATH"
    fi
done

echo "Début de la surveillance de la mémoire..."

# Boucle pour surveiller memory.current
while true; do
    if [ -f "$VM_CGROUP_PATH/memory.current" ]; then
        TIMESTAMP=$(date +%s%3N) # Timestamp en millisecondes
        MEMORY_CURRENT=$(cat "$VM_CGROUP_PATH/memory.current")
        echo "$TIMESTAMP,$MEMORY_CURRENT" >> $OUTPUT_FILE
    else
        echo "Fichier memory.current introuvable. Arrêt du script."
        break
    fi
    sleep $(echo "$POLL_INTERVAL / 1000000" | bc -l)
done