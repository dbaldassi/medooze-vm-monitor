#!/usr/bin/python3

import sys
from matplotlib import pyplot as plt
import matplotlib
import polars as pl

import scienceplots

plt.style.use(['science','ieee'])

plt.rcParams.update({
    "font.size": 18
})

plt.rcParams['axes.prop_cycle'] = matplotlib.cycler('linestyle', ['-', '--', ':', '-.'])

# px = 1 / plt.rcParams['figure.dpi']  # pixel in inches
LINEWIDTH=3

# Language translations
TRANSLATIONS = {
    'fr': {
        'TIME': {'label': 'Temps', 'unit': '(s)', 'name': 'Temps'},
        'MEMORY': {'label': 'Mémoire', 'unit': '(MiB)'},
        'BITRATE': {'label': 'Débit', 'unit': '(kbps)'},
        'FPS': {'label': 'FPS', 'unit': ''},
        'DELAY': {'label': 'Délai', 'unit': '(ms)'},
        'CPU': {'label': 'CPU', 'unit': '(%)'},
        'PRESSURE': {'label': 'Pressure Stall Information', 'unit': '(PSI)'},
        'VIEWER_COUNT': {'label': 'Nombre de récepteurs', 'unit': ''},
        'RID_COUNT': {'label': 'RID Count', 'unit': ''},
        'no_viewers': 'Pas de récepteurs',
        'viewers': 'récepteurs',
    },
    'en': {
        'TIME': {'label': 'Time', 'unit': '(s)', 'name': 'Time'},
        'MEMORY': {'label': 'Memory', 'unit': '(MiB)'},
        'BITRATE': {'label': 'Bitrate', 'unit': '(kbps)'},
        'FPS': {'label': 'FPS', 'unit': ''},
        'DELAY': {'label': 'Delay', 'unit': '(ms)'},
        'CPU': {'label': 'CPU', 'unit': '(%)'},
        'PRESSURE': {'label': 'Pressure Stall Information', 'unit': '(PSI)'},
        'VIEWER_COUNT': {'label': 'Viewer count', 'unit': ''},
        'RID_COUNT': {'label': 'RID Count', 'unit': ''},
        'no_viewers': 'No viewers',
        'viewers': 'viewers',
    }
}

# Column metadata structure indices
INDEX = 0
COLOR = 1
PROCESS = 2
LABEL_KEY = 3  # Key to look up in translations
NAME_KEY = 4   # Specific name key in translations

# color used when combining exp
method_color = {
    "ballooning" : 'b',
    "cgroup-max" : 'r',
    "cgroup-reclaim" : 'g'
}

method_style = {
    "ballooning" : '--',
    "cgroup-max" : '-',
    "cgroup-reclaim" : 'dotted'
}

ANCHOR=[(0,0), (1,1), (0,1), (0,0), (1,0), (1,0.5), (0,0.5), (1,0.5), (0.5,1), (0,0), (0.5,1), (0,2)]

# plt.rcParams["figure.figsize"] = (20,3)

s_windows = {
    "publisher_bitrate": [],
    "viewer_bitrate": [],
    "publisher_fps": [],
    "viewer_fps": [],
}

def sliding_window(x, w):
    window_len = 10

    w.append(float(x))

    if len(w) >= window_len:
        w.pop(0)

    return sum(w) / len(w)

# Column metadata: [index, color, process_function, label_key, name_key]
# label_key and name_key are used to look up translations
def get_column_metadata(lang='fr'):
    """Returns column metadata with translations for the specified language."""
    t = TRANSLATIONS.get(lang, TRANSLATIONS['fr'])
    
    return {
        'TIME': [0, None, lambda x: float(x) / 1000., 'TIME', 'TIME'],
        'MEMORY_USED': [1, 'b', lambda x: float(x), 'MEMORY', 'cgroup_memory'],
        'MEMORY_FREE': [2, 'm', lambda x: float(x), 'MEMORY', 'cgroup_free_memory'],
        'MEMORY_MAX': [3, 'k', lambda x: float(x), 'MEMORY', 'cgroup_max_memory'],
        'SWAP': [4, 'r', lambda x: float(x), 'MEMORY', 'host_swap'],
        'CGROUP_CACHE': [5, 'y', lambda x: float(x) / 1024 / 1024, 'MEMORY', 'cgroup_cache'],
        'CGROUP_SWAPPABLE': [6, 'c', lambda x: float(x) / 1024 / 1024, 'MEMORY', 'cgroup_swappable'],
        'MEMORY_PRESSURE_AVG10': [7, 'darkRed', lambda x: float(x), 'PRESSURE', 'memory_pressure'],
        'MEMORY_PRESSURE_AVG60': [8],
        'MEMORY_PRESSURE_AVG300': [9],
        'MEMORY_PRESSURE_TOTAL': [10],
        'VIRSH_ACTUAL': [11, 'k', lambda x: float(x) / 1024., 'MEMORY', 'vm_allocated_memory' if lang == 'en' else 'vm_allocated_memory_fr'],
        'VIRSH_UNUSED': [12, 'tomato', lambda x: float(x) / 1024., 'MEMORY', 'vm_unused_memory' if lang == 'en' else 'vm_unused_memory_fr'],
        'VIRSH_USABLE': [13, 'm', lambda x: float(x) / 1024., 'MEMORY', 'guest_free_memory' if lang == 'en' else 'guest_free_memory_fr'],
        'VIRSH_AVAILABLE': [14, 'g', lambda x: float(x) / 1024., 'MEMORY', 'guest_vram' if lang == 'en' else 'guest_capacity'],
        'VIRSH_SWAP_IN': [15, '', lambda x: float(x) / 1024., 'MEMORY', 'vm_swap_in'],
        'VIRSH_SWAP_OUT': [16, 'r', lambda x: float(x) / 1024., 'MEMORY', 'guest_swap' if lang == 'en' else 'guest_swap_fr'],
        'VIRSH_MINOR_FAULT': [17],
        'VIRSH_MAJOR_FAULT': [18],
        'PUBLISHER_BITRATE': [19, 'b', lambda x: sliding_window(x, s_windows["publisher_bitrate"]), 'BITRATE', 'publisher_bitrate' if lang == 'en' else 'publisher_bitrate_fr'],
        'PUBLISHER_FPS': [20, 'r', lambda x: sliding_window(x, s_windows["publisher_fps"]), 'FPS', 'publisher_fps' if lang == 'en' else 'publisher_fps_fr'],
        'PUBLISHER_RES': [21],
        'PUBLISHER_RTT': [22, 'r', lambda x: float(x), 'DELAY', 'publisher_rtt' if lang == 'en' else 'publisher_rtt_fr'],
        'CONNECTION_STATE': [23],
        'VIEWER_COUNT': [24, 'y', lambda x: float(x), 'VIEWER_COUNT', 'viewer_count' if lang == 'en' else 'viewer_count_fr'],
        'VM_MEMORY_USAGE': [25, 'midnightBlue', lambda x: float(x), 'MEMORY', 'guest_memory' if lang == 'en' else 'guest_memory_fr'],
        'VM_MEMORY_FREE': [26, 'tomato', lambda x: float(x), 'MEMORY', 'vm_free_memory'],
        'VM_CPU_USAGE': [27, 'b', lambda x: max(0, float(x) * 100), 'CPU', 'vm_cpu_usage' if lang == 'en' else 'vm_cpu_usage_fr'],
        'VM_FREE_TOTAL': [28, 'purple', lambda x: float(x), 'MEMORY', 'vm_free_total'], 
        'VM_FREE_USED': [29, 'orange', lambda x: float(x), 'MEMORY', 'vm_free_used'], 
        'VM_FREE_BUFCACHE': [30, 'cyan', lambda x: float(x), 'MEMORY', 'vm_free_bufcache'],
        'MEDOOZE_INCOMING_LOST': [31],
        'MEDOOZE_INCOMING_DROP': [32],
        'MEDOOZE_INCOMING_BITRATE': [33],
        'MEDOOZE_INCOMING_NACK': [34],
        'MEDOOZE_INCOMING_PLI': [35],
        'RX_PACKET': [36],
        'RX_DROPPED': [37],
        'RX_ERRORS': [38],
        'RX_MISSED': [39],
        'TX_PACKET': [40],
        'TX_DROPPED': [41],
        'TX_ERRORS': [42],
        'TX_MISSED': [43],
        'VIEWER_TARGET': [44, 'k', lambda x: float(x), 'BITRATE', 'viewer_encoder_target'],
        'VIEWER_BITRATE': [45, 'g', lambda x: sliding_window(x, s_windows["viewer_bitrate"]), 'BITRATE', 'viewer_received_bitrate' if lang == 'en' else 'viewer_received_bitrate_fr'],
        'VIEWER_RTT': [46],
        'VIEWER_DELAY': [47, 'm', lambda x: float(x), 'DELAY', 'end_to_end_delay' if lang == 'en' else 'end_to_end_delay_fr'],
        'VIEWER_FPS': [48, 'm', lambda x: sliding_window(x, s_windows["viewer_fps"]), 'FPS', 'viewer_received_fps' if lang == 'en' else 'viewer_received_fps_fr'],
        'VIEWER_RID_H': [49, 'g', lambda x: float(x), 'RID_COUNT', 'simulcast_high_layer' if lang == 'en' else 'simulcast_high_layer_fr'],
        'VIEWER_RID_M': [50, 'b', lambda x: float(x), 'RID_COUNT', 'simulcast_medium_layer' if lang == 'en' else 'simulcast_medium_layer_fr'],
        'VIEWER_RID_L': [51, 'r', lambda x: float(x), 'RID_COUNT', 'simulcast_low_layer' if lang == 'en' else 'simulcast_low_layer_fr'],
    }

# Specific name translations
NAME_TRANSLATIONS = {
    'fr': {
        'cgroup_memory': "Mémoire allouée à la VM",
        'cgroup_free_memory': "cgroup mémoire libre",
        'cgroup_max_memory': "cgroup memory.max",
        'host_swap': "Swap hôte",
        'cgroup_cache': "cgroup cache",
        'cgroup_swappable': "cgroupe swappable",
        'memory_pressure': "Memory pressure",
        'vm_allocated_memory_fr': "Mémoire allouée à la VM",
        'vm_unused_memory_fr': "Mémoire inutilisée de la VM",
        'guest_free_memory_fr': "Mémoire libre de l'invité",
        'guest_capacity': "Capacité de l'invité",
        'vm_swap_in': "VM swap in",
        'guest_swap_fr': "Swap de l'invité",
        'publisher_bitrate_fr': "Débit émetteur",
        'publisher_fps_fr': "FPS émetteur",
        'publisher_rtt_fr': "RTT émetteur",
        'viewer_count_fr': "Nombre de récepteurs",
        'guest_memory_fr': "Mémoire utilisée par l'invité",
        'vm_free_memory': "VM current free memory",
        'vm_cpu_usage_fr': "Utilisation CPU (VM)",
        'vm_free_total': "VM free total",
        'vm_free_used': "VM free used",
        'vm_free_bufcache': "VM free buff/cache",
        'viewer_encoder_target': "viewer encoder target",
        'viewer_received_bitrate_fr': "Débit récepteurs",
        'end_to_end_delay_fr': "Délai bout à bout",
        'viewer_received_fps_fr': "FPS récepteurs",
        'simulcast_high_layer_fr': "simulcast couche haute",
        'simulcast_medium_layer_fr': "simulcast couche moyenne",
        'simulcast_low_layer_fr': "simulcast couche basse",
    },
    'en': {
        'cgroup_memory': "cgroup memory",
        'cgroup_free_memory': "cgroup current free memory",
        'cgroup_max_memory': "cgroup max memory",
        'host_swap': "cgroup swap",
        'cgroup_cache': "cgroup cache",
        'cgroup_swappable': "cgroupe swappable",
        'memory_pressure': "Memory pressure",
        'vm_allocated_memory': "VM allocated memory",
        'vm_unused_memory': "VM unused memory",
        'guest_free_memory': "Guest free memory",
        'guest_vram': "Guest vRAM",
        'vm_swap_in': "VM swap in",
        'guest_swap': "Guest swap",
        'publisher_bitrate': "publisher bitrate",
        'publisher_fps': "publisher fps",
        'publisher_rtt': "publisher rtt",
        'viewer_count': "Viewer count",
        'guest_memory': "Guest memory",
        'vm_free_memory': "VM current free memory",
        'vm_cpu_usage': "VM cpu usage",
        'vm_free_total': "VM free total",
        'vm_free_used': "VM free used",
        'vm_free_bufcache': "VM free buff/cache",
        'viewer_encoder_target': "viewer encoder target",
        'viewer_received_bitrate': "viewer received bitrate",
        'end_to_end_delay': "End to end delay",
        'viewer_received_fps': "viewer received FPS",
        'simulcast_high_layer': "simulcast high layer",
        'simulcast_medium_layer': "simulcast medium layer",
        'simulcast_low_layer': "simulcast low layer",
    }
}

def get_label_and_unit(column_name, metadata, lang):
    """Get label and unit for a column based on language."""
    t = TRANSLATIONS.get(lang, TRANSLATIONS['fr'])
    if len(metadata) > LABEL_KEY:
        label_key = metadata[LABEL_KEY]
        if label_key in t:
            return t[label_key]['label'], t[label_key]['unit']
    return "", ""

def get_column_name(column_name, metadata, lang):
    """Get the display name for a column based on language."""
    name_t = NAME_TRANSLATIONS.get(lang, NAME_TRANSLATIONS['fr'])
    if len(metadata) > NAME_KEY:
        name_key = metadata[NAME_KEY]
        if name_key in name_t:
            return name_t[name_key]
    return column_name

indicators = ["avg", "1stq", "median", "3rdq", "min", "max"]
indicators_color = ['b', 'y', 'r', 'c', 'g', 'k']

def check_args(axis, headers):
    for name in axis:
        if not name in headers:
            print(name)
            return False
    return True

def open_csv_polars(filename):
    """Open CSV file using Polars."""
    return pl.read_csv(filename)

def open_csv(filename):
    """Open CSV file and return as list of lists for compatibility."""
    df = pl.read_csv(filename)
    # Convert to list of lists (excluding headers)
    return df.to_numpy().tolist()

def get_index(idx, indicator):
    # Average has 6 columns for the same stat, one per indicator, which average, median, quartile ...
    # tis function returns the correct index in the file
    indicator_idx = indicators.index(indicator)
    return idx * len(indicators) + indicator_idx

def get_method(filename):
    name = filename.split('/')[-1]

    print(name)
    if "ballooning" in name:
        return "ballooning"
    elif "cgroups-max" in name or "cgroup-max" in name:
        return "cgroup-max"
    elif "cgroup-reclaim" in name or "cgroups-reclaim" in name:
        return "cgroup-reclaim"
    
    return None

def create_figure(settings):
    """Create a matplotlib figure with settings configuration."""
    figsize = settings.get("figsize", (5, 5))
    transparency = settings.get("transparency", True)
    
    fig, ax = plt.subplots(figsize=figsize)
    if transparency:
        fig.patch.set_alpha(0.0)
        ax.set_facecolor('none')
    
    return fig, ax


def go_annotate(ax, lang='fr'):
    """Annotate the figure with background colors for different phases."""
    t = TRANSLATIONS.get(lang, TRANSLATIONS['fr'])
    
    if lang == 'fr':
        phases = [
            {"start": 0, "end": 60, "color": "lightgray", "label": t['no_viewers']},
            {"start": 60, "end": 120, "color": "lightblue", "label": f"20 {t['viewers']}"},
            {"start": 120, "end": 180, "color": "lightgreen", "label": f"40 {t['viewers']}"},
            {"start": 180, "end": 240, "color": "yellow", "label": f"60 {t['viewers']}"},
            {"start": 240, "end": 720, "color": "orange", "label": f"80 {t['viewers']}"},
            {"start": 720, "end": 920, "color": "lightgray", "label": None },
            {"start": 920, "end": 980, "color": "lightgreen", "label": None },
            {"start": 980, "end": None, "color": "orange", "label": None },
        ]
    else:  # English
        phases = [
            {"start": 0, "end": 60, "color": "lightgray", "label": t['no_viewers']},
            {"start": 60, "end": 120, "color": "lightblue", "label": f"20 {t['viewers']}"},
            {"start": 120, "end": 180, "color": "lightgreen", "label": f"40 {t['viewers']}"},
            {"start": 180, "end": 240, "color": "yellow", "label": f"60 {t['viewers']}"},
            {"start": 240, "end": 720, "color": "orange", "label": f"80 {t['viewers']}"},
            {"start": 720, "end": 920, "color": "lightgray", "label": None },
            {"start": 920, "end": 980, "color": "lightgreen", "label": None },
            {"start": 980, "end": None, "color": "orange", "label": None },
        ]

    for phase in phases:
        ax.axvspan(
            phase["start"],
            phase["end"] if phase["end"] is not None else ax.get_xlim()[1],
            color=phase["color"],
            alpha=0.3,
            label=phase["label"]
        )
    

def plot_yy(ax, lines, header, indicator, x_axis_values, w, style, color, label):
    if len(indicator) == 1: # only one indicator asked, for instance only the average
        # get the correct index in the csv array
        y_idx = get_index(header[INDEX], indicator[0])
        # get corresponding values
        y_axis_value = [ header[PROCESS](line[y_idx]) if len(line) > y_idx else 0 for line in lines ]
        # plot y values in function of x values on the plot
        if y_axis_value[w[0]] == 0:
            w[0] += 1

        ax.plot(x_axis_values[w[0]:w[1]], y_axis_value[w[0]:w[1]], color=color, label=label, linestyle=style, linewidth=LINEWIDTH)
        
    else:
        for ind in indicator:
            y_idx = get_index(header[INDEX], ind)
            y_axis_value = [ header[PROCESS](line[y_idx]) if len(line) > y_idx else 0 for line in lines ]
            ax.plot(x_axis_values[w[0]:w[1]], y_axis_value[w[0]:w[1]], label=ind)

colors = matplotlib.cm.get_cmap('tab10').colors
c = [1,0]
def plot_y(ax, lines, header, indicator, x_axis_values, window, style, filename, multiple_on_y, twin, lang):
    color = header[COLOR]
    label = get_column_name(None, header, lang)

    if filename:
        method = get_method(filename)

        if multiple_on_y:
            style = method_style[method]
            label = "{} ({})".format(label, method)
        else:
            color = method_color[method]

            if twin:
                label = "{} ({})".format(label, method)
            else:
                label = method
        

    plot_yy(ax, lines, header, indicator, x_axis_values, window, style, color, label)

def save(settings, x_axis, y_axis, y2_axis, indicator):
    """Save the figure using settings configuration."""
    img_format = settings.get("format", "pdf")
    img_name = settings.get("name", None)
    show = settings.get("show", False)
    filenames = settings.get("files", [])

    if show:
        # show the figure in a window as asked
        plt.show()
    else:
        # Save the figure otherwise
        if img_name:
            # Use the name from settings
            dest_path = filenames[0].split('/')
            dest_path[-1] = f"{img_name}.{img_format}"
        else:
            # Generate name from metrics (backward compatibility)
            dest_path = filenames[0].split('/')
            
            # if there was more than one file plotted, save the fig in the directory above
            if len(filenames) > 1:
                dest_path.pop()

            if len(y2_axis):
                # Add the metrics shown in the secondary axis to the fig filename if there was any
                dest_path[-1] = "plot_{}x{}x{}_{}_{}_{}.{}".format(x_axis, y_axis[0],y2_axis[0], "-".join(indicator), 1, 1, img_format)
            else:
                dest_path[-1] = "plot_{}x{}_{}_{}_{}.{}".format(x_axis, y_axis[0], "-".join(indicator), 1, 1, img_format)

        transparency = settings.get("transparency", True)
        plt.savefig("/".join(dest_path), format=img_format, transparent=transparency)

def find_window_index(values, window):
    window_index = [0, len(values)]
    if not window:
        return window_index

    ind = 0
    while ind < len(values) and values[ind] < window[0]:
        ind += 1

    window_index[0] = ind if ind < len(values) else 0

    while ind < len(values) and values[ind] < window[1]:
        ind += 1
    
    window_index[1] = ind
    print(window_index)

    return window_index

def plot(settings, x_axis, y_axis, y2_axis, window, indicator, annotate=False):
    """Main plotting function using settings object."""
    filenames = settings.get("files", [])
    location = settings.get("location", settings.get("loc", 1))
    legend_col = settings.get("leg_col", 1)
    lang = settings.get("lang", "fr")
    
    # Get headers with language support
    headers = get_column_metadata(lang)
    
    # create figure with settings
    fig, ax = create_figure(settings)
    
    # set label for figure
    label, unit = get_label_and_unit(x_axis, headers[x_axis], lang)
    ax.set_xlabel(f"{label} {unit}")
    
    label_ind = LABEL_KEY if len(filenames) == 1 or len(y_axis) > 1 else NAME_KEY
    if label_ind == LABEL_KEY:
        label, unit = get_label_and_unit(y_axis[0], headers[y_axis[0]], lang)
    else:
        label = get_column_name(y_axis[0], headers[y_axis[0]], lang)
        _, unit = get_label_and_unit(y_axis[0], headers[y_axis[0]], lang)
    ax.set_ylabel(f"{label} {unit}")
    
    bx = None # no secondary axis by default
    twin = False

    # create a secondary axis if something is asked to be plot on it
    if len(y2_axis) > 0:
        bx = ax.twinx()
        if label_ind == LABEL_KEY:
            label, unit = get_label_and_unit(y2_axis[0], headers[y2_axis[0]], lang)
        else:
            label = get_column_name(y2_axis[0], headers[y2_axis[0]], lang)
            _, unit = get_label_and_unit(y2_axis[0], headers[y2_axis[0]], lang)
        bx.set_ylabel(f"{label} {unit}")
        if settings.get("transparency", True):
            bx.set_facecolor('none')
        twin = True

    # Set a title in case we are comparing indicators    
    if len(indicator) > 1:
            ax.set_title(y_axis[0])

    multiple_on_y = len(y_axis) > 1 or len(y2_axis) > 1

    # iterate through all specified file to combine them on one fig
    for filename in filenames:
        # open the csv average file
        lines = open_csv(filename) 

        # get x axis values
        x_axis_idx = get_index(headers[x_axis][INDEX], indicator[0])
        x_axis_values = [ headers[x_axis][PROCESS](line[x_axis_idx]) for line in lines ]

        # find start and end index of the specified window
        window_index = find_window_index(x_axis_values, window)
        # Substract the start window value to all values to start at 0
        x_axis_values = [ x - x_axis_values[window_index[0]] for x in x_axis_values ]
 
        style = None
        if len(y2_axis) > 0:
            style = '-'

        # plot on primary vertical axis
        for y in y_axis:
            plot_y(ax, lines, headers[y], indicator, x_axis_values, window_index, None, filename if len(filenames) > 1 else None, multiple_on_y, twin, lang)

        # plot on secondary vertical axis
        for y in y2_axis:
            plot_y(bx, lines, headers[y], indicator, x_axis_values, window_index, None, filename if len(filenames) > 1 else None, multiple_on_y, twin, lang)

    if annotate:
        go_annotate(ax, lang)

    ax.set_xlim([0,400])
    ax.set_ylim([0,2500])
    
    # add legend to the figure
    leg = fig.legend(loc='center left', bbox_to_anchor=(1., 0.5),  bbox_transform=ax.transAxes, frameon=True)
    if leg:
        leg.get_frame().set_alpha(0.0)

    # save fig
    save(settings, x_axis, y_axis, y2_axis, indicator)

    # free figure
    plt.close()

import math

def plot_delta(settings, x_axis, y_axis, window, indicator, annotate=False):
    """
    Crée une figure 16:9 avec un sous-plot par métrique de y_axis.
    Le premier fichier sert de baseline. On trace (fichier_i - baseline).
    """
    filenames = settings.get("files", [])
    show = settings.get("show", False)
    lang = settings.get("lang", "fr")
    
    # Get headers with language support
    headers = get_column_metadata(lang)
    
    if len(filenames) < 2:
        print("Besoin d'au moins 2 fichiers pour un delta plot.")
        return
    if len(indicator) == 0:
        print("Besoin d'au moins un indicateur.")
        return
    if len(indicator) > 1:
        print("plot_delta: seul indicator[0] est utilisé.")
    ind = indicator[0]

    # Lecture de tous les fichiers
    all_lines = [open_csv(f) for f in filenames]

    # Préparation axe X depuis le baseline
    baseline_lines = all_lines[0]
    x_axis_idx = get_index(headers[x_axis][INDEX], ind)
    x_axis_values_full = [headers[x_axis][PROCESS](line[x_axis_idx]) for line in baseline_lines]

    # Fenêtre
    window_index = find_window_index(x_axis_values_full, window)
    x0 = x_axis_values_full[window_index[0]]
    x_axis_values = [x - x0 for x in x_axis_values_full[window_index[0]:window_index[1]]]

    # Figure with custom size or default 16:9
    figsize = settings.get("figsize", (16, 9))
    transparency = settings.get("transparency", True)
    
    fig, axes = plt.subplots(len(y_axis), 1, figsize=figsize, sharex=True)
    if transparency:
        fig.patch.set_alpha(0.0)

    if len(y_axis) == 1:
        axes = [axes]

    for ax in axes:
        if transparency:
            ax.set_facecolor('none')

    # Méthodes (couleurs / styles)
    methods = [get_method(f) for f in filenames[1:]]
    # Palette fallback
    palette = ['b', 'r', 'g', 'm', 'c', 'y', 'k']

    for mi, metric in enumerate(y_axis):
        ax = axes[mi]
        ax.set_xlim([0,1200])
        header = headers[metric]
        y_idx_base = get_index(header[INDEX], ind)
        baseline_series_full = [
            header[PROCESS](line[y_idx_base]) if len(line) > y_idx_base else 0
            for line in baseline_lines
        ]
        baseline_series = baseline_series_full[window_index[0]:window_index[1]]

        # Plot delta pour chaque fichier (saut baseline)
        for fi, lines in enumerate(all_lines[1:], start=1):
            y_idx = get_index(header[INDEX], ind)
            series_full = [
                header[PROCESS](line[y_idx]) if len(line) > y_idx else 0
                for line in lines
            ]
            series = series_full[window_index[0]:window_index[1]]
            # Alignement longueur min
            mlen = min(len(series), len(baseline_series), len(x_axis_values))
            delta = [series[i] - baseline_series[i] for i in range(mlen)]
            method = methods[fi - 1]
            color = method_color.get(method, palette[(fi - 1) % len(palette)])
            label = filenames[fi].split('/')[-1]
            if 'balloon' in label:
                label = 'ballooning'
            elif 'cgroup' in label:
                label = 'cgroups'
            ax.plot(x_axis_values[:mlen], delta, alpha=0.7, color=color, label=label)

        # Ligne horizontale zéro
        ax.axhline(0, color='black', linestyle='--', linewidth=1)

        # Labels
        label, unit = get_label_and_unit(metric, header, lang)
        ax.set_ylabel(f"{label} {unit}")
        col_name = get_column_name(metric, header, lang)
        ax.set_title(f"{col_name}")

        if annotate:
            go_annotate(ax, lang)

    label, unit = get_label_and_unit(x_axis, headers[x_axis], lang)
    axes[-1].set_xlabel(f"{label} {unit}")

    # Aligne proprement tous les ylabels (nécessite matplotlib >=3.4)
    fig.align_ylabels(axes)

    # Légende consolidée
    handles, labels = axes[0].get_legend_handles_labels()
    if handles:
        leg = fig.legend(handles, labels, loc='center left', bbox_to_anchor=(1.02, 0.5), frameon=True)
        if leg:
            leg.get_frame().set_alpha(0.0)

    # Sauvegarde / affichage
    img_format = settings.get("format", "pdf")
    if show:
        plt.show()
    else:
        img_name = settings.get("name", None)
        if img_name:
            dest_path = filenames[0].split('/')
            dest_path[-1] = f"{img_name}.{img_format}"
        else:
            dest_path = filenames[0].split('/')
            dest_path[-1] = "delta_{}x{}_{}.{}".format(
                x_axis,
                "-".join(y_axis),
                ind,
                img_format
            )
        plt.savefig("/".join(dest_path), format=img_format, bbox_inches='tight', transparent=transparency)

    plt.close(fig)

"""
Arguments:
    - settings (dict): Settings dictionary containing:
        - files (list): List of input CSV files.
        - indicator (list): List of indicators (e.g., 'avg', 'median', '1stq', etc.).
        - x (str): Name of the key for the X-axis.
        - y (list): List of names of the keys for the Y-axis.
        - y2 (list, optional): List of names of the keys for Y2-axis (dual axis), default: None.
        - window (list, optional): Sliding window [start, end] with two integers, default: None.
        - location (int, optional): Legend location in the graph, default: 1 (upper-right corner).
        - leg_col (int, optional): Number of columns in the legend, default: 1.
        - annotate (bool, optional): Whether to add annotations to the points, default: False.
        - show (bool, optional): Whether to display the graph after generation, default: False.
        - lang (str, optional): Language for labels ('fr' or 'en'), default: 'fr'.
        - format (str, optional): Image format ('pdf' or 'png'), default: 'pdf'.
        - name (str, optional): Output filename (without extension), default: auto-generated.
        - figsize (tuple, optional): Figure size (width, height), default: (5, 5).
        - transparency (bool, optional): Whether to use transparent background, default: True.
        - delta (bool, optional): Whether to plot delta, default: False.
Returns:
    - None
"""
def process_and_plot(settings):
    filenames = settings.get("files", [])
    indicator = settings.get("indicator", [])
    x_axis = settings.get("x")
    y_axis = settings.get("y", [])
    y2_axis = settings.get("y2", [])
    window = settings.get("window")
    annotate = settings.get("annotate", False)
    delta = settings.get("delta", False)
    lang = settings.get("lang", "fr")

    # Get headers with language support
    headers = get_column_metadata(lang)

    print(delta)
    # Valider les indicateurs fournis
    for i in indicator:
        if not i in indicators:
            raise ValueError(f"[ERREUR] Specified indicator not valid : '{i}'")

    # Valider les axes X et Y (et Y2 si fourni)
    is_valid = check_args([x_axis, *y_axis, *(y2_axis or [])], headers)
    if not is_valid:
        raise ValueError(f"[ERREUR] Specified column not valid : {x_axis}, {y_axis}, {y2_axis}")

    if delta:
        plot_delta(settings, x_axis, y_axis, window, indicator, annotate)
    else:
        plot(settings, x_axis, y_axis, y2_axis, window, indicator, annotate)

if __name__ == "__main__":
    x_axis = None
    y_axis = []
    y2_axis = []
    show = False

    window = None
    location = 1 # legend at upper right by default

    num_required_args = 5
    legend_col = 1 # default number of columns in the legend

    annotate = False

    if len(sys.argv) >= num_required_args:
        filenames = sys.argv[1].split(',')
        indicator = sys.argv[2].split(',')
        x_axis = sys.argv[3]
        y_axis = sys.argv[4].split(',')
    
        for i in range(num_required_args, len(sys.argv)):
            if sys.argv[i] == "show":
                show = True
            elif sys.argv[i][0] == "[":
                window = sys.argv[i][1:len(sys.argv[i])-1].split(',')
                window = [int(i) for i in window] # convert to int
            elif sys.argv[i].startswith("loc="):
                split = sys.argv[i].split('=')
                print(split[1], type(split[1]))
                location = int(split[1])
            elif  sys.argv[i].startswith("leg_col="):
                split = sys.argv[i].split('=')
                print(split[1], type(split[1]))
                legend_col = int(split[1])
            elif sys.argv[i] == "annotate":
                annotate = True
            else:
                y2_axis = sys.argv[i].split(',')
    else:
        print("Usage : {} <file> <avg|1stq|median|3rdq|min|max> <key_x_axis> <key1_y_axis[,k2,...,kn]> [keys_y2_axis]".format(sys.argv[0]))
        exit(1)

    print(x_axis, y_axis, y2_axis, window)

    # Build settings dictionary for backward compatibility
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
        "lang": "fr",  # default language
        "format": "pdf",  # default format
        "transparency": True,  # default transparency
        "figsize": (5, 5),  # default figure size
    }

    # check if specified indicators are valid
    for i in indicator:
        if not i in indicators:
            print("You specified an invalid indicator")
            exit(1)

    # Get headers with default language
    headers = get_column_metadata(settings["lang"])

    # check if specified metrics actually exists
    is_valid = check_args([x_axis, *y_axis, *y2_axis], headers)
    # otherwise exit program
    if not is_valid:
        print("You specified a column not valid")
        exit(1)

    # Use process_and_plot for consistency
    process_and_plot(settings)
