#!/usr/bin/python3

import csv
import sys
from matplotlib import pyplot as plt

import scienceplots

plt.style.use(['science','ieee'])

plt.rcParams.update({
    "font.size": 10
})

# plt.rc('font', size=40)          # controls default text sizes
# plt.rc('axes', titlesize=44)     # fontsize of the axes title
# plt.rc('axes', labelsize=44)    # fontsize of the x and y labels
# # plt.rc('xtick', labelsize=SMALL_SIZE)    # fontsize of the tick labels
# # plt.rc('ytick', labelsize=SMALL_SIZE)    # fontsize of the tick labels
# plt.rc('legend', fontsize=42)    # legend fontsize
# # plt.rc('figure', titlesize=BIGGER_SIZE)  # fontsize of the figure title

# px = 1 / plt.rcParams['figure.dpi']  # pixel in inches
LINEWIDTH=4

INDEX=0
COLOR=1
PROCESS=2
LABEL=3
UNIT=4
NAME=5

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

headers = {
    'TIME': [0, None, lambda x: float(x) / 1000., "time", "(s)", "Time"],
    'MEMORY_USED': [1, 'b', lambda x: float(x), "Memory", "(MiB)", "cgroup current memory"],
    'MEMORY_FREE': [2, 'm', lambda x: float(x), "Memory", "(MiB)", "cgroup current free memory"],
    'MEMORY_MAX': [3, 'k', lambda x: float(x), "Memory", "(MiB)", "cgroup max memory"],
    'SWAP': [4, 'g', lambda x: float(x), "Memory", "(MiB)", "cgroup current swap usage"],
    'CGROUP_CACHE': [5, 'y', lambda x: float(x) / 1024 / 1024, "Memory", "(MiB)", "cgroup cache"],
    'CGROUP_SWAPPABLE': [6, 'c', lambda x: float(x) / 1024 / 1024, "Memory", "(MiB)", "cgroupe swappable"],
    'MEMORY_PRESSURE_AVG10': [7, 'darkRed', lambda x: float(x), "Pressure Stall Information", "(PSI)", "Memory pressure"],
    'MEMORY_PRESSURE_AVG60': [8],
    'MEMORY_PRESSURE_AVG300': [9],
    'MEMORY_PRESSURE_TOTAL': [10],
    'VIRSH_ACTUAL': [11, 'k', lambda x: float(x) / 1024., "Memory", "(MiB)", "VM allocated memory"],
    'VIRSH_UNUSED': [12, 'tomato', lambda x: float(x) / 1024., "Memory", "(MiB)", "VM unused memory"],
    'VIRSH_USABLE': [13, 'm', lambda x: float(x) / 1024., "Memory", "(MiB)", "Guest free memory"],
    'VIRSH_AVAILABLE': [14, 'g', lambda x: float(x) / 1024., "Memory", "(MiB)", "Guest vRAM"],
    'VIRSH_SWAP_IN': [15, '', lambda x: float(x) / 1024., "Memory", "(MiB)", "VM swap in"],
    'VIRSH_SWAP_OUT': [16, 'r', lambda x: float(x) / 1024., "Memory", "(MiB)", "Guest swap"],
    'VIRSH_MINOR_FAULT': [17],
    'VIRSH_MAJOR_FAULT': [18],
    'PUBLISHER_BITRATE': [19, 'b', lambda x: sliding_window(x, s_windows["publisher_bitrate"]), "Bitrate", "(kbps)", "publisher bitrate"],
    'PUBLISHER_FPS': [20, 'r', lambda x: sliding_window(x, s_windows["publisher_fps"]), "FPS", "", "publisher fps"],
    'PUBLISHER_RES': [21],
    'PUBLISHER_RTT': [22, 'r', lambda x: float(x), "Delay", "(ms)", "publisher rtt"],
    'CONNECTION_STATE': [23],
    'VIEWER_COUNT': [24, 'y', lambda x: float(x), "Viewer Count", "", "Viewer count"],
    'VM_MEMORY_USAGE': [25, 'midnightBlue', lambda x: float(x), "Memory", "(MiB)", "Guest used memory"],
    'VM_MEMORY_FREE': [26, 'tomato', lambda x: float(x), "Memory", "(MiB)", "VM current free memory"],
    'VM_CPU_USAGE': [27, 'b', lambda x: max(0, float(x) * 100), "CPU", "(%)", "VM cpu usage"],
    'VM_FREE_TOTAL': [28, 'purple', lambda x: float(x), "Memory", "(MiB)", "VM free total"], 
    'VM_FREE_USED': [29, 'orange', lambda x: float(x), "Memory", "(MiB)", "VM free used"], 
    'VM_FREE_BUFCACHE': [30, 'cyan', lambda x: float(x), "Memory", "(MiB)", "VM free buff/cache"],
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
    'VIEWER_TARGET': [44, 'k', lambda x: float(x), "Bitrate", "(kbps)", "viewer encoder target"],
    'VIEWER_BITRATE': [45, 'g', lambda x: sliding_window(x, s_windows["viewer_bitrate"]), "Bitrate", "(kbps)", "viewer received bitrate"],
    'VIEWER_RTT': [46],
    'VIEWER_DELAY': [47, 'm', lambda x: float(x), "Delay", "(ms)", "End to end delay"],
    'VIEWER_FPS': [48, 'm', lambda x: sliding_window(x, s_windows["viewer_fps"]), "FPS", "", "viewer received FPS"],
    'VIEWER_RID_H': [49, 'g', lambda x: float(x), "RID Count", "", "simulcast high layer"],
    'VIEWER_RID_M': [50, 'b', lambda x: float(x), "RID Count", "", "simulcast medium layer"],
    'VIEWER_RID_L': [51, 'r', lambda x: float(x), "RID Count", "", "simulcast low layer"],
}

indicators = ["avg", "1stq", "median", "3rdq", "min", "max"]
indicators_color = ['b', 'y', 'r', 'c', 'g', 'k']

def check_args(axis):
    for name in axis:
        if not name in headers:
            print(name)
            return False
    return True


def open_csv(filename):
     with open(filename, 'r') as csv_file:
        lines = [ line for line in csv.reader(csv_file, delimiter=',') ] # read file
        lines.pop(0) # remove headers
        return lines
     
     return None

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


def go_annotate(ax):
    # Annotate the figure with background colors for different phases
    phases = [
        {"start": 0, "end": 60, "color": "lightgray", "label": "No viewer"},
        {"start": 60, "end": 120, "color": "lightblue", "label": "20 viewers"},
        {"start": 120, "end": 180, "color": "lightgreen", "label": "40 viewers"},
        {"start": 180, "end": 240, "color": "yellow", "label": "60 viewers"},
        {"start": 240, "end": 720, "color": "orange", "label": "80 viewers"},
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
        ax.plot(x_axis_values[w[0]:w[1]], y_axis_value[w[0]:w[1]], color=color, label=label, linestyle=style)
        # ax.plot(x_axis_values[w[0]:w[1]], y_axis_value[w[0]:w[1]], label=label)
    else:
        for ind in indicator:
            y_idx = get_index(header[INDEX], ind)
            y_axis_value = [ header[PROCESS](line[y_idx]) if len(line) > y_idx else 0 for line in lines ]
            # ax.plot(x_axis_values[w[0]:w[1]], y_axis_value[w[0]:w[1]], color=indicators_color[indicators.index(ind)], label=ind, linewidth=LINEWIDTH)
            ax.plot(x_axis_values[w[0]:w[1]], y_axis_value[w[0]:w[1]], label=ind)

def plot_y(ax, lines, header, indicator, x_axis_values, window, style, filename, multiple_on_y, twin):
    color = header[COLOR]
    label = header[NAME]

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

def save(filenames, x_axis, y_axis, y2_axis, indicator, show, res):
    # ext = "png"
    ext = "pdf"

    if show:
        # show the figure in a window a asked
        plt.show()
    else:
        # Save the figure in pdf format otherwise

        # get the path of the csv file to save the figure in same directory
        # in case of multiple, consider the first one as destinatino path
        dest_path = filenames[0].split('/')
        
        # if there was more than one file plotted, save the fig in the directory above
        if len(filenames) > 1:
            dest_path.pop()

        if len(y2_axis):
            # Add the metrics shown in the secondary axis to the fig filename if there was any
            dest_path[-1] = "plot_{}x{}x{}_{}_{}_{}.{}".format(x_axis, y_axis[0],y2_axis[0], "-".join(indicator), res[0]//res[1], 1, ext)
        else:
            dest_path[-1] = "plot_{}x{}_{}_{}_{}.{}".format(x_axis, y_axis[0], "-".join(indicator), res[0]//res[1], 1, ext)

        plt.savefig("/".join(dest_path), format=ext)

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

def plot(filenames, x_axis, y_axis, y2_axis, window, indicator, show, res, location, legend_col, annotate = False):
    # create figure with specified ratio
    # fig,ax = plt.subplots(figsize=(res[0], res[1]))
    fig,ax = plt.subplots()
    # set label for figure
    ax.set_xlabel("{} {}".format(headers[x_axis][LABEL], headers[x_axis][UNIT]))
    label_ind = LABEL if len(filenames) == 1 or len(y_axis) > 1 else NAME
    ax.set_ylabel("{} {}".format(headers[y_axis[0]][label_ind], headers[y_axis[0]][UNIT]))
    bx = None # no secondary axis by default
    twin = False

    # create a secondary axis if smothing is asked to be plot on it
    if len(y2_axis) > 0:
        bx = ax.twinx()
        bx.set_ylabel("{} {}".format(headers[y2_axis[0]][label_ind], headers[y2_axis[0]][UNIT]))
        twin = True

    # Set a title in case we are comparing indicators    
    if len(indicator) > 1:
            ax.set_title(y_axis[0])

    multiple_on_y = len(y_axis) > 1 or len(y2_axis) > 1

        # iterate through all specified file ot combine them on one fig
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
 
        # plot on primary vertical axis
        for y in y_axis:
            plot_y(ax, lines, headers[y], indicator, x_axis_values, window_index, '-', filename if len(filenames) > 1 else None, multiple_on_y, twin)

        # plot on secondary vertical axis
        for y in y2_axis:
            plot_y(bx, lines, headers[y], indicator, x_axis_values, window_index, 'dotted', filename if len(filenames) > 1 else None, multiple_on_y, twin)

    # view window
    # if window:
    #     ax.set_xlim(window[0], window[1])
    #     if bx:
    #         bx.set_xlim(window[0], window[1])

    if annotate:
        go_annotate(ax)
        # ax.legend()

    # add legend to the figure
    fig.legend(loc=location, bbox_to_anchor=ANCHOR[location], bbox_transform=ax.transAxes, ncol=legend_col)
    # fig.legend(ncol=2)

    # save fig
    save(filenames, x_axis, y_axis, y2_axis, indicator, show, res)

    # free figure
    plt.close()

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
        print("Usage : {} <file> <avg|1stq|median|3rdq|min|max> <key_x_axis> <key1_y_axis[,k2,...,kn]> [keys_y2_axis]".format(sys.arvg[0]))
        exit(1)

    print(x_axis, y_axis, y2_axis, window)

    # check if specified indicators are valid
    for i in indicator:
        if not i in indicators:
            print("You specifed an invalid indicator")

    # check if specified metrics actually exists
    is_valid = check_args([x_axis, *y_axis, *y2_axis])
    # otherwise exit program
    if not is_valid:
        print("You specified a column not valid")
        exit(1)

    # plot(filenames, x_axis, y_axis, y2_axis, window, indicator, show, (1920,960), location, legend_col) # ratio 2:1
    plot(filenames, x_axis, y_axis, y2_axis, window, indicator, show, (1024,1024), location, legend_col, annotate) # ratio 1:1
