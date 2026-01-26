# plot_polars.py - Script de visualisation avec Polars

Ce script est une réécriture complète de `plot.py` utilisant **Polars** pour la manipulation de données et **Matplotlib** pour la visualisation.

## Changements principaux

### Utilisation de Polars
- Remplacement de la lecture CSV manuelle par `pl.read_csv()`
- Utilisation des DataFrames Polars pour toutes les opérations sur les données
- Calculs effectués avec les opérations vectorisées de Polars au lieu de boucles Python
- Fenêtres glissantes implémentées avec `rolling_mean()` de Polars
- Filtrage et transformations avec l'API expressive de Polars

### Simplifications
- Structure du code plus claire et maintenable
- Gestion des erreurs améliorée
- Configuration des métriques centralisée dans `METRICS_CONFIG`
- Pas de backward compatibility avec l'ancien format

## Installation

```bash
pip install -r requirements.txt
```

### Dépendances
- polars >= 0.20.0
- matplotlib >= 3.7.0
- scienceplots >= 2.1.0 (optionnel, pour le style scientifique)
- numpy >= 1.24.0

**Note**: Le script fonctionne sans LaTeX. Si scienceplots ou LaTeX ne sont pas disponibles, le script utilise le style par défaut de matplotlib.

## Usage

### Syntaxe de base
```bash
./scripts/plot_polars.py <fichiers> <indicateur> <axe_x> <axes_y> [axes_y2] [options]
```

### Arguments
- `fichiers`: Liste de fichiers CSV séparés par des virgules
- `indicateur`: Indicateur statistique à utiliser (avg, median, 1stq, 3rdq, min, max)
- `axe_x`: Colonne pour l'axe X (généralement TIME)
- `axes_y`: Colonnes pour l'axe Y primaire (séparées par des virgules)
- `axes_y2`: Colonnes pour l'axe Y secondaire (optionnel)

### Options
- `show`: Afficher le graphique au lieu de le sauvegarder
- `[start,end]`: Fenêtre temporelle (ex: [60,300])
- `loc=N`: Position de la légende (0-11)
- `leg_col=N`: Nombre de colonnes dans la légende
- `annotate`: Ajouter les annotations de phases
- `delta`: Mode comparaison (delta par rapport au premier fichier)

## Exemples

### Graphique simple
```bash
# Tracer la mémoire utilisée en fonction du temps
./scripts/plot_polars.py data.csv avg TIME MEMORY_USED
```

### Graphique avec plusieurs métriques
```bash
# Tracer plusieurs métriques de mémoire
./scripts/plot_polars.py data.csv avg TIME MEMORY_USED,SWAP,VM_MEMORY_USAGE
```

### Graphique avec deux axes Y
```bash
# Mémoire sur axe Y primaire, pression mémoire sur axe Y secondaire
./scripts/plot_polars.py data.csv avg TIME MEMORY_USED,SWAP MEMORY_PRESSURE_AVG10
```

### Comparaison de plusieurs fichiers
```bash
# Comparer les résultats de différentes méthodes
./scripts/plot_polars.py file1.csv,file2.csv,file3.csv avg TIME MEMORY_USED
```

### Mode delta (différence)
```bash
# Comparer les fichiers en mode delta (premier fichier = baseline)
./scripts/plot_polars.py baseline.csv,test1.csv,test2.csv avg TIME MEMORY_USED delta
```

### Avec fenêtre temporelle et annotations
```bash
# Fenêtre de 60 à 720 secondes avec annotations des phases
./scripts/plot_polars.py data.csv avg TIME MEMORY_USED [60,720] annotate
```

## Format des données CSV

### Avec indicateurs multiples
Le script supporte les CSV avec plusieurs indicateurs par colonne:
```csv
TIME_avg,TIME_median,MEMORY_USED_avg,MEMORY_USED_median
0,0,1000,1050
1000,1000,1100,1150
```

Le script sélectionne automatiquement les colonnes correspondant à l'indicateur demandé et les renomme.

### CSV simple
Le script fonctionne aussi avec des CSV simples:
```csv
TIME,MEMORY_USED,SWAP
0,1000,100
1000,1100,110
```

## Métriques supportées

Le script reconnaît automatiquement les métriques suivantes et applique les transformations appropriées:

### Métriques de temps
- `TIME`: Temps (converti de ms en secondes)

### Métriques de mémoire
- `MEMORY_USED`: Mémoire allouée à la VM
- `MEMORY_FREE`: Mémoire libre du cgroup
- `MEMORY_MAX`: Limite max du cgroup
- `SWAP`: Swap utilisé
- `VM_MEMORY_USAGE`: Mémoire utilisée par l'invité
- `VM_MEMORY_FREE`: Mémoire libre de la VM
- `VIRSH_*`: Statistiques virsh (converties de KiB en MiB)

### Métriques de performance
- `PUBLISHER_BITRATE`: Débit émetteur (avec fenêtre glissante)
- `PUBLISHER_FPS`: FPS émetteur (avec fenêtre glissante)
- `PUBLISHER_RTT`: RTT émetteur
- `VIEWER_BITRATE`: Débit récepteurs (avec fenêtre glissante)
- `VIEWER_FPS`: FPS récepteurs (avec fenêtre glissante)
- `VIEWER_DELAY`: Délai bout à bout
- `VIEWER_COUNT`: Nombre de récepteurs

### Métriques CPU
- `VM_CPU_USAGE`: Utilisation CPU (convertie en pourcentage)

### Autres
- `MEMORY_PRESSURE_AVG10`: Pression mémoire
- `VIEWER_RID_*`: Layers simulcast

## Fonctionnalités Polars

### Fenêtres glissantes
Les colonnes suivantes utilisent automatiquement une fenêtre glissante de 10 points:
- `PUBLISHER_BITRATE`
- `VIEWER_BITRATE`
- `PUBLISHER_FPS`
- `VIEWER_FPS`

Implémenté avec `pl.col(column).rolling_mean(window_size=10, min_periods=1)`

### Filtrage temporel
Le filtrage par fenêtre temporelle est optimisé avec Polars:
```python
df.filter((pl.col(time_col) >= start) & (pl.col(time_col) <= end))
```

### Transformations
Les transformations de colonnes sont appliquées avec l'API Polars:
```python
df.with_columns(transform(pl.col(metric)).alias(metric))
```

## Différences avec plot.py original

1. **Pas de backward compatibility**: Le script n'essaie pas de reproduire exactement le comportement de l'ancien script
2. **API simplifiée**: Structure de code plus claire et pythonique
3. **Performance**: Utilisation de Polars pour des opérations vectorisées rapides
4. **Robustesse**: Meilleure gestion des erreurs et des cas limites
5. **LaTeX optionnel**: Fonctionne sans LaTeX (utilise le backend Agg de matplotlib)

## Notes techniques

### Backend matplotlib
Le script utilise le backend 'Agg' de matplotlib qui ne nécessite pas d'interface graphique et fonctionne sans LaTeX.

### Gestion des NaN
Polars gère naturellement les valeurs manquantes. Les fenêtres glissantes utilisent `min_periods=1` pour éviter les NaN au début.

### Performance
Grâce à Polars, le traitement de gros fichiers CSV est significativement plus rapide qu'avec le script original utilisant des boucles Python.

## Dépannage

### Erreur "Module not found: polars"
```bash
pip install polars
```

### Avertissements de police (font warnings)
Ces avertissements sont normaux et n'empêchent pas la génération des graphiques. Pour les éliminer, installez les polices Times:
```bash
sudo apt-get install fonts-liberation
```

### Erreur LaTeX
Si vous voyez une erreur concernant LaTeX, assurez-vous d'avoir la version la plus récente du script qui désactive LaTeX par défaut.

## Développement

### Ajouter une nouvelle métrique
Pour ajouter une métrique, ajoutez-la dans le dictionnaire `METRICS_CONFIG`:
```python
METRICS_CONFIG = {
    'MA_METRIQUE': {
        'color': 'b',
        'label': 'Mon Label',
        'unit': '(unité)',
        'name': 'Nom complet',
        'transform': lambda x: x * 2  # transformation optionnelle
    }
}
```

### Modifier les phases d'annotation
Modifiez la liste `phases` dans la fonction `add_phase_annotations()`.
