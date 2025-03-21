#!/usr/bin/python3

import csv
import sys
from matplotlib import pyplot as plt

plt.rc('font', size=22)          # controls default text sizes
plt.rc('axes', titlesize=26)     # fontsize of the axes title
plt.rc('axes', labelsize=26)    # fontsize of the x and y labels
plt.rc('legend', fontsize=24)    # legend fontsize

px = 1 / plt.rcParams['figure.dpi']  # pixel in inches
LINEWIDTH = 4

INDEX = 0
COLOR = 1
PROCESS = 2
LABEL = 3
UNIT = 4
NAME = 5

ANCHOR=[(0,0), (1,1), (0,1), (0,0), (1,0), (1,0.5), (0,0.5), (1,0.5), (0,0), (0,0), (0,0)]

# Headers basés sur cgroup_headers
headers = {
    'TIME': [0, None, lambda x: float(x) / 1000., "time", "(s)", "Time"],
    'ANON': [1, 'b', lambda x: float(x) / (1024 * 1024), "Memory", "(MiB)", "Anonymous Memory"],
    'FILE': [2, 'm', lambda x: float(x) / (1024 * 1024), "Memory", "(MiB)", "File Cache"],
    'KERNEL': [3, 'k', lambda x: float(x) / (1024 * 1024), "Memory", "(MiB)", "Kernel Memory"],
    'KERNEL_STACK': [4, 'g', lambda x: float(x) / (1024 * 1024), "Memory", "(MiB)", "Kernel Stack"],
    'PAGETABLES': [5, 'r', lambda x: float(x) / (1024 * 1024), "Memory", "(MiB)", "Page Tables"],
    'SEC_PAGETABLES': [6, 'c', lambda x: float(x) / (1024 * 1024), "Memory", "(MiB)", "Secondary Page Tables"],
    'PERCPU': [7, 'y', lambda x: float(x) / (1024 * 1024), "Memory", "(MiB)", "Per-CPU Memory"],
    'SOCK': [8, 'darkRed', lambda x: float(x) / (1024 * 1024), "Memory", "(MiB)", "Socket Memory"],
    'VMALLOC': [9, 'purple', lambda x: float(x) / (1024 * 1024), "Memory", "(MiB)", "VMalloc Memory"],
    'SHMEM': [10, 'orange', lambda x: float(x) / (1024 * 1024), "Memory", "(MiB)", "Shared Memory"],
    'ZSWAP': [11, 'pink', lambda x: float(x) / (1024 * 1024), "Memory", "(MiB)", "ZSwap"],
    'ZSWAPPED': [12, 'brown', lambda x: float(x) / (1024 * 1024), "Memory", "(MiB)", "ZSwapped"],
    'FILE_MAPPED': [13, 'cyan', lambda x: float(x) / (1024 * 1024), "Memory", "(MiB)", "File Mapped"],
    'FILE_DIRTY': [14, 'lime', lambda x: float(x) / (1024 * 1024), "Memory", "(MiB)", "File Dirty"],
    'FILE_WRITEBACK': [15, 'teal', lambda x: float(x) / (1024 * 1024), "Memory", "(MiB)", "File Writeback"],
    'SWAPCACHED': [16, 'gold', lambda x: float(x) / (1024 * 1024), "Memory", "(MiB)", "Swap Cached"],
    'ANON_THP': [17, 'navy', lambda x: float(x) / (1024 * 1024), "Memory", "(MiB)", "Anonymous THP"],
    'FILE_THP': [18, 'olive', lambda x: float(x) / (1024 * 1024), "Memory", "(MiB)", "File THP"],
    'SHMEM_THP': [19, 'maroon', lambda x: float(x) / (1024 * 1024), "Memory", "(MiB)", "Shared Memory THP"],
    'INACTIVE_ANON': [20, 'darkGreen', lambda x: float(x) / (1024 * 1024), "Memory", "(MiB)", "Inactive Anonymous"],
    'ACTIVE_ANON': [21, 'darkBlue', lambda x: float(x) / (1024 * 1024), "Memory", "(MiB)", "Active Anonymous"],
    'INACTIVE_FILE': [22, 'darkCyan', lambda x: float(x) / (1024 * 1024), "Memory", "(MiB)", "Inactive File"],
    'ACTIVE_FILE': [23, 'darkMagenta', lambda x: float(x) / (1024 * 1024), "Memory", "(MiB)", "Active File"],
    'UNEVICTABLE': [24, 'black', lambda x: float(x) / (1024 * 1024), "Memory", "(MiB)", "Unevictable"],
    'SLAB_RECLAIMABLE': [25, 'gray', lambda x: float(x) / (1024 * 1024), "Memory", "(MiB)", "Slab Reclaimable"],
    'SLAB_UNRECLAIMABLE': [26, 'silver', lambda x: float(x) / (1024 * 1024), "Memory", "(MiB)", "Slab Unreclaimable"],
    'SLAB': [27, 'lightBlue', lambda x: float(x) / (1024 * 1024), "Memory", "(MiB)", "Slab"],
    'WORKINGSET_REFAULT_ANON': [28, 'lightGreen', lambda x: float(x), "Count", "", "Working Set Refault Anon"],
    'WORKINGSET_REFAULT_FILE': [29, 'lightRed', lambda x: float(x), "Count", "", "Working Set Refault File"],
    'WORKINGSET_ACTIVATE_ANON': [30, 'darkOrange', lambda x: float(x), "Count", "", "Working Set Activate Anon"],
    'WORKINGSET_ACTIVATE_FILE': [31, 'darkPurple', lambda x: float(x), "Count", "", "Working Set Activate File"],
    'WORKINGSET_RESTORE_ANON': [32, 'darkGray', lambda x: float(x), "Count", "", "Working Set Restore Anon"],
    'WORKINGSET_RESTORE_FILE': [33, 'lightGray', lambda x: float(x), "Count", "", "Working Set Restore File"],
    'WORKINGSET_NODERECLAIM': [34, 'gold', lambda x: float(x), "Count", "", "Working Set No Reclaim"],
    'PGDEMOTE_KSWAPD': [35, 'pink', lambda x: float(x), "Count", "", "Page Demote KSWAPD"],
    'PGDEMOTE_DIRECT': [36, 'brown', lambda x: float(x), "Count", "", "Page Demote Direct"],
    'PGDEMOTE_KHUGEPAGED': [37, 'cyan', lambda x: float(x), "Count", "", "Page Demote KHugePaged"],
    'PGPROMOTE_SUCCESS': [38, 'lime', lambda x: float(x), "Count", "", "Page Promote Success"],
    'PGSCAN': [39, 'teal', lambda x: float(x), "Count", "", "Page Scan"],
    'PGSTEAL': [40, 'navy', lambda x: float(x), "Count", "", "Page Steal"],
    'PGSCAN_KSWAPD': [41, 'olive', lambda x: float(x), "Count", "", "Page Scan KSWAPD"],
    'PGSCAN_DIRECT': [42, 'maroon', lambda x: float(x), "Count", "", "Page Scan Direct"],
    'PGSCAN_KHUGEPAGED': [43, 'darkGreen', lambda x: float(x), "Count", "", "Page Scan KHugePaged"],
    'PGSTEAL_KSWAPD': [44, 'darkBlue', lambda x: float(x), "Count", "", "Page Steal KSWAPD"],
    'PGSTEAL_DIRECT': [45, 'darkCyan', lambda x: float(x), "Count", "", "Page Steal Direct"],
    'PGSTEAL_KHUGEPAGED': [46, 'darkMagenta', lambda x: float(x), "Count", "", "Page Steal KHugePaged"],
    'PGFAULT': [47, 'black', lambda x: float(x), "Count", "", "Page Faults"],
    'PGMAJFAULT': [48, 'gray', lambda x: float(x), "Count", "", "Major Page Faults"],
    'PGREFILL': [49, 'silver', lambda x: float(x), "Count", "", "Page Refill"],
    'PGACTIVATE': [50, 'lightBlue', lambda x: float(x), "Count", "", "Page Activate"],
    'PGDEACTIVATE': [51, 'lightGreen', lambda x: float(x), "Count", "", "Page Deactivate"],
    'PGLAZYFREE': [52, 'lightRed', lambda x: float(x), "Count", "", "Lazy Free"],
    'PGLAZYFREED': [53, 'darkOrange', lambda x: float(x), "Count", "", "Lazy Freed"],
    'SWPIN_ZERO': [54, 'darkPurple', lambda x: float(x), "Count", "", "Swap In Zero"],
    'SWPOUT_ZERO': [55, 'darkGray', lambda x: float(x), "Count", "", "Swap Out Zero"],
    'ZSWPIN': [56, 'gold', lambda x: float(x), "Count", "", "ZSwap In"],
    'ZSWPOUT': [57, 'pink', lambda x: float(x), "Count", "", "ZSwap Out"],
    'ZSWPWB': [58, 'brown', lambda x: float(x), "Count", "", "ZSwap Writeback"],
    'THP_FAULT_ALLOC': [59, 'cyan', lambda x: float(x), "Count", "", "THP Fault Alloc"],
    'THP_COLLAPSE_ALLOC': [60, 'lime', lambda x: float(x), "Count", "", "THP Collapse Alloc"],
    'THP_SWPOUT': [61, 'teal', lambda x: float(x), "Count", "", "THP Swap Out"],
    'THP_SWPOUT_FALLBACK': [62, 'navy', lambda x: float(x), "Count", "", "THP Swap Out Fallback"],
    'NUMA_PAGES_MIGRATED': [63, 'olive', lambda x: float(x), "Count", "", "NUMA Pages Migrated"],
    'NUMA_PTE_UPDATES': [64, 'maroon', lambda x: float(x), "Count", "", "NUMA PTE Updates"],
    'NUMA_HINT_FAULTS': [65, 'darkGreen', lambda x: float(x), "Count", "", "NUMA Hint Faults"],
    'RAM_USAGE': [66, 'blue', lambda x: float(x), "Memory", "(MiB)", "Memory Current"],
    'SWAP_USAGE': [67, 'red', lambda x: float(x), "Memory", "(MiB)", "Swap Current"],
    'MAXRAM': [68, 'green', lambda x: float(x), "Memory", "(MiB)", "Memory Max"],
    'PRESSURE_AVG10': [69, 'purple', lambda x: float(x), "Pressure", "(PSI)", "Pressure Avg10"],
    'SUMMED_MEMORY': [70, 'purple', lambda x: float(x) / (1024 * 1024), "Memory", "(MiB)", "Summed Memory"],
}

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

def plot_yy(ax, lines, header, x_axis_values, w, style, color, label):
    # get the correct index in the csv array
    y_idx = header[INDEX]
    # get corresponding values
    y_axis_value = [ header[PROCESS](line[y_idx]) if len(line) > y_idx else 0 for line in lines ]
    # plot y values in function of x values on the plot
    ax.plot(x_axis_values[w[0]:w[1]], y_axis_value[w[0]:w[1]], color=color, label=label, linewidth=LINEWIDTH, linestyle=style)

def plot_y(ax, lines, header, x_axis_values, window, style, filename, multiple_on_y, twin):
    color = header[COLOR]
    label = header[NAME]

    plot_yy(ax, lines, header, x_axis_values, window, style, color, label)

def save(filenames, x_axis, y_axis, y2_axis, show, res):
    # ext = "png"
    ext = "png"

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
            dest_path[-1] = "plot_{}x{}x{}_{}_{}.{}".format(x_axis, y_axis[0],y2_axis[0], res[0]//res[1], 1, ext)
        else:
            dest_path[-1] = "plot_{}x{}_{}_{}.{}".format(x_axis, y_axis[0], res[0]//res[1], 1, ext)

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

def plot(filenames, x_axis, y_axis, y2_axis, window, show, res, location):
    # create figure with specified ratio
    fig,ax = plt.subplots(figsize=(res[0]*px, res[1]*px))
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

    multiple_on_y = len(y_axis) > 1 or len(y2_axis) > 1

        # iterate through all specified file ot combine them on one fig
    for filename in filenames:
        # open the csv average file
        lines = open_csv(filename) 

        # get x axis values
        x_axis_idx = headers[x_axis][INDEX]
        x_axis_values = [ headers[x_axis][PROCESS](line[x_axis_idx]) for line in lines ]

        # find start and end index of the specified window
        window_index = find_window_index(x_axis_values, window)
        # Substract the start window value to all values to start at 0
        x_axis_values = [ x - x_axis_values[window_index[0]] for x in x_axis_values ]
 
        # plot on primary vertical axis
        for y in y_axis:
            plot_y(ax, lines, headers[y], x_axis_values, window_index, '-', filename if len(filenames) > 1 else None, multiple_on_y, twin)

        # plot on secondary vertical axis
        for y in y2_axis:
            plot_y(bx, lines, headers[y], x_axis_values, window_index, 'dotted', filename if len(filenames) > 1 else None, multiple_on_y, twin)

    # add legend to the figure
    fig.legend(loc=location, bbox_to_anchor=ANCHOR[location], bbox_transform=ax.transAxes)

    # save fig
    save(filenames, x_axis, y_axis, y2_axis, show, res)

    # free figure
    plt.close()

if __name__ == "__main__":
    x_axis = None
    y_axis = []
    y2_axis = []
    show = False

    window = None
    location = 1 # legend at upper right by default

    num_required_args = 4

    if len(sys.argv) >= num_required_args:
        filenames = sys.argv[1].split(',')
        # indicator = sys.argv[2].split(',')
        x_axis = sys.argv[2]
        y_axis = sys.argv[3].split(',')
    
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
            else:
                y2_axis = sys.argv[i].split(',')
    else:
        print("Usage : {} <file> <avg|1stq|median|3rdq|min|max> <key_x_axis> <key1_y_axis[,k2,...,kn]> [keys_y2_axis]".format(sys.arvg[0]))
        exit(1)

    print(x_axis, y_axis, y2_axis, window)

    # check if specified metrics actually exists
    is_valid = check_args([x_axis, *y_axis, *y2_axis])
    # otherwise exit program
    if not is_valid:
        print("You specified a column not valid")
        exit(1)

    plot(filenames, x_axis, y_axis, y2_axis, window, show, (1920,960), location) # ratio 2:1
    # plot(filenames, x_axis, y_axis, y2_axis, window, indicator, show, (1024,1024), location) # ratio 1:1