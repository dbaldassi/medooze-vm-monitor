#!/usr/bin/python3

"""
Script de visualisation avec Polars et Matplotlib
Remplacement complet du script plot.py original sans backward compatibility
"""

import sys
import polars as pl
import matplotlib
matplotlib.use('Agg')  # Backend sans interface graphique
import matplotlib.pyplot as plt

# Configuration matplotlib - utiliser scienceplots si disponible et LaTeX aussi
try:
    import scienceplots
    plt.style.use(['science', 'ieee'])
except (ImportError, OSError, RuntimeError):
    # Fallback si scienceplots ou LaTeX n'est pas disponible
    print("Note: scienceplots ou LaTeX non disponible, utilisation du style par défaut")
    plt.rcParams.update({
        'text.usetex': False,  # Désactiver LaTeX
        'font.family': 'sans-serif',
    })
    
plt.rcParams.update({
    "font.size": 18,
    'text.usetex': False,  # S'assurer que LaTeX est désactivé
})
plt.rcParams['axes.prop_cycle'] = matplotlib.cycler('linestyle', ['-', '--', ':', '-.'])

LINEWIDTH = 3

# Configuration des couleurs et styles par méthode
method_color = {
    "ballooning": 'b',
    "cgroup-max": 'r',
    "cgroup-reclaim": 'g'
}

method_style = {
    "ballooning": '--',
    "cgroup-max": '-',
    "cgroup-reclaim": 'dotted'
}

# Configuration des métriques avec leurs propriétés
# Format: nom_colonne -> (couleur, label, unité, nom_complet, transformation)
METRICS_CONFIG = {
    'TIME': {'color': None, 'label': 'Temps', 'unit': '(s)', 'name': 'Temps', 'transform': lambda x: x / 1000.0},
    'MEMORY_USED': {'color': 'b', 'label': 'Mémoire', 'unit': '(MiB)', 'name': 'Mémoire allouée à la VM', 'transform': lambda x: x},
    'MEMORY_FREE': {'color': 'm', 'label': 'Memory', 'unit': '(MiB)', 'name': 'cgroup mémoire libre', 'transform': lambda x: x},
    'MEMORY_MAX': {'color': 'k', 'label': 'Memory', 'unit': '(MiB)', 'name': 'cgroup memory.max', 'transform': lambda x: x},
    'SWAP': {'color': 'r', 'label': 'Mémoire', 'unit': '(MiB)', 'name': 'Swap hôte', 'transform': lambda x: x},
    'CGROUP_CACHE': {'color': 'y', 'label': 'Memory', 'unit': '(MiB)', 'name': 'cgroup cache', 'transform': lambda x: x / 1024 / 1024},
    'CGROUP_SWAPPABLE': {'color': 'c', 'label': 'Memory', 'unit': '(MiB)', 'name': 'cgroup swappable', 'transform': lambda x: x / 1024 / 1024},
    'MEMORY_PRESSURE_AVG10': {'color': 'darkRed', 'label': 'Pressure Stall Information', 'unit': '(PSI)', 'name': 'Memory pressure', 'transform': lambda x: x},
    'VIRSH_ACTUAL': {'color': 'k', 'label': 'Memory', 'unit': '(MiB)', 'name': 'Mémoire allouée à la VM', 'transform': lambda x: x / 1024.0},
    'VIRSH_UNUSED': {'color': 'tomato', 'label': 'Memory', 'unit': '(MiB)', 'name': 'Mémoire inutilisée de la VM', 'transform': lambda x: x / 1024.0},
    'VIRSH_USABLE': {'color': 'm', 'label': 'Memory', 'unit': '(MiB)', 'name': 'Mémoire libre de l\'invité', 'transform': lambda x: x / 1024.0},
    'VIRSH_AVAILABLE': {'color': 'g', 'label': 'Mémoire', 'unit': '(MiB)', 'name': 'Capacité de l\'invité', 'transform': lambda x: x / 1024.0},
    'VIRSH_SWAP_IN': {'color': '', 'label': 'Memory', 'unit': '(MiB)', 'name': 'VM swap in', 'transform': lambda x: x / 1024.0},
    'VIRSH_SWAP_OUT': {'color': 'r', 'label': 'Mémoire', 'unit': '(MiB)', 'name': 'Swap de l\'invité', 'transform': lambda x: x / 1024.0},
    'PUBLISHER_BITRATE': {'color': 'b', 'label': 'Débit', 'unit': '(kbps)', 'name': 'Débit émetteur', 'transform': lambda x: x},
    'PUBLISHER_FPS': {'color': 'r', 'label': 'FPS', 'unit': '', 'name': 'FPS émetteur', 'transform': lambda x: x},
    'PUBLISHER_RTT': {'color': 'r', 'label': 'Délai', 'unit': '(ms)', 'name': 'RTT émetteur', 'transform': lambda x: x},
    'VIEWER_COUNT': {'color': 'y', 'label': 'Viewer Count', 'unit': '', 'name': 'Nombre de récepteurs', 'transform': lambda x: x},
    'VM_MEMORY_USAGE': {'color': 'midnightBlue', 'label': 'Mémoire', 'unit': '(MiB)', 'name': 'Mémoire utilisée par l\'invité', 'transform': lambda x: x},
    'VM_MEMORY_FREE': {'color': 'tomato', 'label': 'Memory', 'unit': '(MiB)', 'name': 'VM current free memory', 'transform': lambda x: x},
    'VM_CPU_USAGE': {'color': 'b', 'label': 'CPU', 'unit': '(%)', 'name': 'Utilisation CPU (VM)', 'transform': lambda x: pl.when(x * 100 > 0).then(x * 100).otherwise(0)},
    'VM_FREE_TOTAL': {'color': 'purple', 'label': 'Memory', 'unit': '(MiB)', 'name': 'VM free total', 'transform': lambda x: x},
    'VM_FREE_USED': {'color': 'orange', 'label': 'Memory', 'unit': '(MiB)', 'name': 'VM free used', 'transform': lambda x: x},
    'VM_FREE_BUFCACHE': {'color': 'cyan', 'label': 'Memory', 'unit': '(MiB)', 'name': 'VM free buff/cache', 'transform': lambda x: x},
    'VIEWER_TARGET': {'color': 'k', 'label': 'Débit', 'unit': '(kbps)', 'name': 'viewer encoder target', 'transform': lambda x: x},
    'VIEWER_BITRATE': {'color': 'g', 'label': 'Débit', 'unit': '(kbps)', 'name': 'Débit récepteurs', 'transform': lambda x: x},
    'VIEWER_DELAY': {'color': 'm', 'label': 'Délai', 'unit': '(ms)', 'name': 'Délai bout à bout', 'transform': lambda x: x},
    'VIEWER_FPS': {'color': 'm', 'label': 'FPS', 'unit': '', 'name': 'FPS récepteurs', 'transform': lambda x: x},
    'VIEWER_RID_H': {'color': 'g', 'label': 'RID Count', 'unit': '', 'name': 'simulcast couche haute', 'transform': lambda x: x},
    'VIEWER_RID_M': {'color': 'b', 'label': 'RID Count', 'unit': '', 'name': 'simulcast couche moyenne', 'transform': lambda x: x},
    'VIEWER_RID_L': {'color': 'r', 'label': 'RID Count', 'unit': '', 'name': 'simulcast couche basse', 'transform': lambda x: x},
}

# Indicateurs disponibles pour les statistiques agrégées
INDICATORS = ["avg", "1stq", "median", "3rdq", "min", "max"]


def load_csv_data(filename: str, indicator: str = "avg") -> pl.DataFrame:
    """
    Charge un fichier CSV avec gestion des indicateurs multiples
    
    Args:
        filename: Chemin vers le fichier CSV
        indicator: Indicateur à sélectionner (avg, median, etc.)
        
    Returns:
        DataFrame Polars avec les colonnes sélectionnées
    """
    # Lire le fichier CSV
    df = pl.read_csv(filename)
    
    # Si le fichier contient des colonnes avec indicateurs (ex: TIME_avg, TIME_median)
    # on sélectionne uniquement celles qui correspondent à l'indicateur demandé
    if any('_' in col for col in df.columns):
        # Extraire les colonnes qui correspondent à l'indicateur
        selected_cols = []
        col_mapping = {}
        
        for col in df.columns:
            if '_' in col:
                base_name, ind = col.rsplit('_', 1)
                if ind == indicator:
                    selected_cols.append(col)
                    col_mapping[col] = base_name
            else:
                selected_cols.append(col)
                col_mapping[col] = col
        
        df = df.select(selected_cols).rename(col_mapping)
    
    return df


def apply_transformations(df: pl.DataFrame, metrics: list[str]) -> pl.DataFrame:
    """
    Applique les transformations définies pour chaque métrique
    
    Args:
        df: DataFrame Polars
        metrics: Liste des métriques à transformer
        
    Returns:
        DataFrame avec les transformations appliquées
    """
    for metric in metrics:
        if metric in df.columns and metric in METRICS_CONFIG:
            transform = METRICS_CONFIG[metric]['transform']
            if callable(transform):
                try:
                    # Vérifier si c'est une expression Polars ou une fonction Python
                    df = df.with_columns(transform(pl.col(metric)).alias(metric))
                except (TypeError, AttributeError):
                    # Si c'est une fonction Python simple, utiliser map_elements
                    df = df.with_columns(pl.col(metric).map_elements(transform, return_dtype=pl.Float64).alias(metric))
    
    return df


def apply_rolling_window(df: pl.DataFrame, column: str, window_size: int = 10) -> pl.DataFrame:
    """
    Applique une fenêtre glissante (moyenne mobile) sur une colonne
    
    Args:
        df: DataFrame Polars
        column: Nom de la colonne
        window_size: Taille de la fenêtre
        
    Returns:
        DataFrame avec la colonne transformée
    """
    if column in df.columns:
        # Utiliser min_samples au lieu de min_periods (version récente de Polars)
        try:
            df = df.with_columns(
                pl.col(column).rolling_mean(window_size=window_size, min_samples=1).alias(column)
            )
        except TypeError:
            # Fallback pour les anciennes versions de Polars
            df = df.with_columns(
                pl.col(column).rolling_mean(window_size=window_size, min_periods=1).alias(column)
            )
    return df


def filter_time_window(df: pl.DataFrame, time_col: str, window: list[float] = None) -> pl.DataFrame:
    """
    Filtre le DataFrame selon une fenêtre temporelle
    
    Args:
        df: DataFrame Polars
        time_col: Nom de la colonne temporelle
        window: [début, fin] en secondes
        
    Returns:
        DataFrame filtré et avec temps normalisé à 0
    """
    if window is None or time_col not in df.columns:
        return df
    
    # Filtrer selon la fenêtre
    df_filtered = df.filter(
        (pl.col(time_col) >= window[0]) & (pl.col(time_col) <= window[1])
    )
    
    # Normaliser le temps pour commencer à 0
    if len(df_filtered) > 0:
        time_start = df_filtered[time_col][0]
        df_filtered = df_filtered.with_columns(
            (pl.col(time_col) - time_start).alias(time_col)
        )
    
    return df_filtered


def get_method_from_filename(filename: str) -> str:
    """
    Extrait le nom de la méthode depuis le nom du fichier
    
    Args:
        filename: Chemin du fichier
        
    Returns:
        Nom de la méthode ('ballooning', 'cgroup-max', 'cgroup-reclaim')
    """
    name = filename.split('/')[-1]
    
    if "ballooning" in name:
        return "ballooning"
    elif "cgroups-max" in name or "cgroup-max" in name:
        return "cgroup-max"
    elif "cgroup-reclaim" in name or "cgroups-reclaim" in name:
        return "cgroup-reclaim"
    
    return "unknown"


def add_phase_annotations(ax):
    """
    Ajoute des annotations colorées pour les différentes phases de l'expérience
    
    Args:
        ax: Axes matplotlib
    """
    phases = [
        {"start": 0, "end": 60, "color": "lightgray", "label": "Pas de récepteurs"},
        {"start": 60, "end": 120, "color": "lightblue", "label": "20 récepteurs"},
        {"start": 120, "end": 180, "color": "lightgreen", "label": "40 récepteurs"},
        {"start": 180, "end": 240, "color": "yellow", "label": "60 récepteurs"},
        {"start": 240, "end": 720, "color": "orange", "label": "80 récepteurs"},
        {"start": 720, "end": 920, "color": "lightgray", "label": None},
        {"start": 920, "end": 980, "color": "lightgreen", "label": None},
        {"start": 980, "end": None, "color": "orange", "label": None},
    ]

    for phase in phases:
        ax.axvspan(
            phase["start"],
            phase["end"] if phase["end"] is not None else ax.get_xlim()[1],
            color=phase["color"],
            alpha=0.3,
            label=phase["label"]
        )


def plot_standard(
    filenames: list[str],
    x_axis: str,
    y_axis: list[str],
    y2_axis: list[str] = None,
    window: list[float] = None,
    indicator: str = "avg",
    show: bool = False,
    annotate: bool = False,
    rolling_cols: list[str] = None
):
    """
    Crée un graphique standard avec un ou plusieurs fichiers CSV
    
    Args:
        filenames: Liste des fichiers CSV à tracer
        x_axis: Nom de la colonne pour l'axe X
        y_axis: Liste des colonnes pour l'axe Y primaire
        y2_axis: Liste des colonnes pour l'axe Y secondaire (optionnel)
        window: Fenêtre temporelle [début, fin]
        indicator: Indicateur statistique à utiliser
        show: Afficher le graphique au lieu de le sauvegarder
        annotate: Ajouter les annotations de phases
        rolling_cols: Colonnes sur lesquelles appliquer une fenêtre glissante
    """
    if y2_axis is None:
        y2_axis = []
    if rolling_cols is None:
        rolling_cols = []
    
    # Créer la figure
    fig, ax = plt.subplots(figsize=(5, 5))
    fig.patch.set_alpha(0.0)
    ax.set_facecolor('none')
    
    # Configurer l'axe Y secondaire si nécessaire
    bx = None
    if len(y2_axis) > 0:
        bx = ax.twinx()
        bx.set_facecolor('none')
    
    # Déterminer si on compare plusieurs fichiers ou plusieurs métriques
    multiple_files = len(filenames) > 1
    multiple_metrics = len(y_axis) > 1 or len(y2_axis) > 1
    
    # Tracer les données pour chaque fichier
    for filename in filenames:
        # Charger et préparer les données
        df = load_csv_data(filename, indicator)
        
        # Appliquer les transformations
        all_metrics = [x_axis] + y_axis + y2_axis
        df = apply_transformations(df, all_metrics)
        
        # Appliquer les fenêtres glissantes
        for col in rolling_cols:
            if col in df.columns:
                df = apply_rolling_window(df, col)
        
        # Filtrer selon la fenêtre temporelle
        df = filter_time_window(df, x_axis, window)
        
        # Extraire la méthode depuis le nom du fichier
        method = get_method_from_filename(filename) if multiple_files else None
        
        # Tracer les métriques Y primaires
        for y_metric in y_axis:
            if y_metric not in df.columns:
                continue
            
            config = METRICS_CONFIG.get(y_metric, {})
            color = config.get('color', 'b')
            label = config.get('name', y_metric)
            
            # Ajuster le style/couleur selon le contexte
            linestyle = '-'
            if multiple_files and method:
                if multiple_metrics:
                    linestyle = method_style.get(method, '-')
                    label = f"{label} ({method})"
                else:
                    color = method_color.get(method, color)
                    label = method
            
            # Tracer la courbe
            ax.plot(
                df[x_axis].to_numpy(),
                df[y_metric].to_numpy(),
                color=color,
                linestyle=linestyle,
                linewidth=LINEWIDTH,
                label=label
            )
        
        # Tracer les métriques Y secondaires
        if bx:
            for y_metric in y2_axis:
                if y_metric not in df.columns:
                    continue
                
                config = METRICS_CONFIG.get(y_metric, {})
                color = config.get('color', 'g')
                label = config.get('name', y_metric)
                
                # Ajuster selon le contexte
                linestyle = '-'
                if multiple_files and method:
                    if multiple_metrics:
                        linestyle = method_style.get(method, '-')
                        label = f"{label} ({method})"
                    else:
                        color = method_color.get(method, color)
                        label = method
                
                bx.plot(
                    df[x_axis].to_numpy(),
                    df[y_metric].to_numpy(),
                    color=color,
                    linestyle=linestyle,
                    linewidth=LINEWIDTH,
                    label=label
                )
    
    # Configurer les labels
    x_config = METRICS_CONFIG.get(x_axis, {})
    ax.set_xlabel(f"{x_config.get('label', x_axis)} {x_config.get('unit', '')}")
    
    y_config = METRICS_CONFIG.get(y_axis[0], {})
    label_type = 'name' if (not multiple_files or multiple_metrics) else 'label'
    ax.set_ylabel(f"{y_config.get(label_type, y_axis[0])} {y_config.get('unit', '')}")
    
    if bx and len(y2_axis) > 0:
        y2_config = METRICS_CONFIG.get(y2_axis[0], {})
        bx.set_ylabel(f"{y2_config.get(label_type, y2_axis[0])} {y2_config.get('unit', '')}")
    
    # Ajouter les annotations si demandé
    if annotate:
        add_phase_annotations(ax)
    
    # Configurer les limites des axes (peut être personnalisé si nécessaire)
    # Ces valeurs sont des valeurs par défaut raisonnables pour les expériences typiques
    # TODO: Rendre ces limites configurables ou les calculer dynamiquement
    ax.set_xlim([0, 400])
    ax.set_ylim([0, 2500])
    
    # Ajouter la légende
    leg = fig.legend(loc='center left', bbox_to_anchor=(1., 0.5), bbox_transform=ax.transAxes, frameon=True)
    if leg:
        leg.get_frame().set_alpha(0.0)
    
    # Sauvegarder ou afficher
    if show:
        plt.show()
    else:
        ext = "pdf"
        dest_path = filenames[0].split('/')
        
        if len(filenames) > 1:
            dest_path.pop()
        
        if len(y2_axis) > 0:
            dest_path[-1] = f"plot_{x_axis}x{y_axis[0]}x{y2_axis[0]}_{indicator}.{ext}"
        else:
            dest_path[-1] = f"plot_{x_axis}x{y_axis[0]}_{indicator}.{ext}"
        
        plt.savefig("/".join(dest_path), format=ext, transparent=True)
    
    plt.close()


def plot_delta(
    filenames: list[str],
    x_axis: str,
    y_axis: list[str],
    window: list[float] = None,
    indicator: str = "avg",
    show: bool = False,
    annotate: bool = False
):
    """
    Crée un graphique de différence (delta) entre fichiers
    Le premier fichier sert de baseline, les autres sont comparés à lui
    
    Args:
        filenames: Liste des fichiers CSV (le premier est la baseline)
        x_axis: Nom de la colonne pour l'axe X
        y_axis: Liste des colonnes pour les métriques à comparer
        window: Fenêtre temporelle [début, fin]
        indicator: Indicateur statistique à utiliser
        show: Afficher le graphique au lieu de le sauvegarder
        annotate: Ajouter les annotations de phases
    """
    if len(filenames) < 2:
        print("Erreur: plot_delta nécessite au moins 2 fichiers (baseline + comparaison)")
        return
    
    # Charger la baseline
    df_baseline = load_csv_data(filenames[0], indicator)
    all_metrics = [x_axis] + y_axis
    df_baseline = apply_transformations(df_baseline, all_metrics)
    df_baseline = filter_time_window(df_baseline, x_axis, window)
    
    # Créer la figure avec un subplot par métrique
    fig, axes = plt.subplots(len(y_axis), 1, figsize=(16, 9), sharex=True)
    fig.patch.set_alpha(0.0)
    
    if len(y_axis) == 1:
        axes = [axes]
    
    for ax in axes:
        ax.set_facecolor('none')
    
    # Tracer le delta pour chaque fichier comparé à la baseline
    for fi, filename in enumerate(filenames[1:], start=1):
        # Charger le fichier de comparaison
        df_compare = load_csv_data(filename, indicator)
        df_compare = apply_transformations(df_compare, all_metrics)
        df_compare = filter_time_window(df_compare, x_axis, window)
        
        # Obtenir la méthode pour le style
        method = get_method_from_filename(filename)
        color = method_color.get(method, 'b')
        
        # Label simplifié
        label = filename.split('/')[-1]
        if 'balloon' in label:
            label = 'ballooning'
        elif 'cgroup' in label:
            label = 'cgroups'
        
        # Tracer le delta pour chaque métrique
        for mi, metric in enumerate(y_axis):
            ax = axes[mi]
            
            if metric not in df_baseline.columns or metric not in df_compare.columns:
                continue
            
            # Calculer le delta avec Polars
            # Assurer que les DataFrames ont la même longueur
            min_len = min(len(df_baseline), len(df_compare))
            
            baseline_values = df_baseline[metric].head(min_len).to_numpy()
            compare_values = df_compare[metric].head(min_len).to_numpy()
            x_values = df_baseline[x_axis].head(min_len).to_numpy()
            
            delta = compare_values - baseline_values
            
            # Tracer le delta
            ax.plot(x_values, delta, color=color, alpha=0.7, label=label)
            
            # Ligne de référence zéro
            ax.axhline(0, color='black', linestyle='--', linewidth=1)
            
            # Labels
            config = METRICS_CONFIG.get(metric, {})
            ax.set_ylabel(f"{config.get('label', metric)} {config.get('unit', '')}")
            ax.set_title(f"{config.get('name', metric)}")
            
            if annotate:
                add_phase_annotations(ax)
            
            # Limite de l'axe X (peut être personnalisé si nécessaire)
            # TODO: Rendre configurable ou calculer dynamiquement
            ax.set_xlim([0, 1200])
    
    # Label de l'axe X sur le dernier subplot
    x_config = METRICS_CONFIG.get(x_axis, {})
    axes[-1].set_xlabel(f"{x_config.get('label', x_axis)} {x_config.get('unit', '')}")
    
    # Aligner les labels Y
    fig.align_ylabels(axes)
    
    # Légende consolidée
    handles, labels = axes[0].get_legend_handles_labels()
    if handles:
        leg = fig.legend(handles, labels, loc='center left', bbox_to_anchor=(1.02, 0.5), frameon=True)
        if leg:
            leg.get_frame().set_alpha(0.0)
    
    # Sauvegarder ou afficher
    ext = "pdf"
    if show:
        plt.show()
    else:
        dest_path = filenames[0].split('/')
        dest_path[-1] = f"delta_{x_axis}x{'-'.join(y_axis)}_{indicator}.{ext}"
        plt.savefig("/".join(dest_path), format=ext, bbox_inches='tight', transparent=True)
    
    plt.close(fig)


def process_and_plot(settings: dict):
    """
    Point d'entrée principal pour générer les graphiques
    
    Args:
        settings: Dictionnaire avec les paramètres de configuration:
            - files: Liste des fichiers CSV
            - indicator: Indicateur statistique ('avg', 'median', etc.)
            - x: Colonne pour l'axe X
            - y: Liste de colonnes pour l'axe Y
            - y2: Liste de colonnes pour l'axe Y secondaire (optionnel)
            - window: Fenêtre temporelle [début, fin] (optionnel)
            - location: Position de la légende (optionnel)
            - leg_col: Nombre de colonnes dans la légende (optionnel)
            - annotate: Ajouter les annotations (optionnel)
            - show: Afficher au lieu de sauvegarder (optionnel)
            - delta: Mode delta (optionnel)
            - rolling: Colonnes avec fenêtre glissante (optionnel)
    """
    filenames = settings.get("files", [])
    indicator = settings.get("indicator", "avg")
    x_axis = settings.get("x")
    y_axis = settings.get("y", [])
    y2_axis = settings.get("y2", [])
    window = settings.get("window")
    show = settings.get("show", False)
    delta = settings.get("delta", False)
    annotate = settings.get("annotate", False)
    rolling_cols = settings.get("rolling", [])
    
    # Validation
    if not filenames:
        raise ValueError("Aucun fichier spécifié")
    
    if indicator not in INDICATORS:
        raise ValueError(f"Indicateur invalide: {indicator}. Valeurs possibles: {INDICATORS}")
    
    all_metrics = [x_axis] + y_axis + (y2_axis or [])
    for metric in all_metrics:
        if metric not in METRICS_CONFIG:
            print(f"Avertissement: métrique inconnue '{metric}'")
    
    # Générer le graphique approprié
    if delta:
        plot_delta(filenames, x_axis, y_axis, window, indicator, show, annotate)
    else:
        plot_standard(filenames, x_axis, y_axis, y2_axis, window, indicator, show, annotate, rolling_cols)


if __name__ == "__main__":
    # Analyse des arguments en ligne de commande
    if len(sys.argv) < 5:
        print("Usage: {} <file1[,file2,...]> <indicator> <x_axis> <y_axis1[,y_axis2,...]> [y2_axis1[,y2_axis2,...]] [options]".format(sys.argv[0]))
        print("\nIndicateurs disponibles: " + ", ".join(INDICATORS))
        print("\nOptions:")
        print("  show              - Afficher le graphique au lieu de le sauvegarder")
        print("  [start,end]       - Fenêtre temporelle")
        print("  loc=N             - Position de la légende")
        print("  leg_col=N         - Nombre de colonnes dans la légende")
        print("  annotate          - Ajouter les annotations de phases")
        print("  delta             - Mode delta (comparaison à baseline)")
        sys.exit(1)
    
    # Parser les arguments
    filenames = sys.argv[1].split(',')
    indicator = sys.argv[2]
    x_axis = sys.argv[3]
    y_axis = sys.argv[4].split(',')
    
    # Options par défaut
    y2_axis = []
    show = False
    window = None
    location = 1
    legend_col = 1
    annotate = False
    delta_mode = False
    
    # Parser les options supplémentaires
    for i in range(5, len(sys.argv)):
        arg = sys.argv[i]
        
        if arg == "show":
            show = True
        elif arg == "annotate":
            annotate = True
        elif arg == "delta":
            delta_mode = True
        elif arg.startswith("[") and arg.endswith("]"):
            window_str = arg[1:-1].split(',')
            window = [float(x) for x in window_str]
        elif arg.startswith("loc="):
            location = int(arg.split('=')[1])
        elif arg.startswith("leg_col="):
            legend_col = int(arg.split('=')[1])
        elif ',' in arg:
            # Si ce n'est pas une option reconnue et contient des virgules, c'est probablement y2_axis
            y2_axis = arg.split(',')
    
    # Colonnes avec fenêtre glissante (bitrates et FPS)
    rolling_cols = ['PUBLISHER_BITRATE', 'VIEWER_BITRATE', 'PUBLISHER_FPS', 'VIEWER_FPS']
    
    # Appeler la fonction principale
    settings = {
        "files": filenames,
        "indicator": indicator,
        "x": x_axis,
        "y": y_axis,
        "y2": y2_axis,
        "window": window,
        "location": location,
        "leg_col": legend_col,
        "annotate": annotate,
        "show": show,
        "delta": delta_mode,
        "rolling": rolling_cols
    }
    
    process_and_plot(settings)
