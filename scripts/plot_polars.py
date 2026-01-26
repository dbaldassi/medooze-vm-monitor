#!/usr/bin/python3

"""
Visualization script with Polars and Matplotlib
Complete rewrite of plot.py without backward compatibility

CSV Structure:
- No header row
- Each metric has 6 consecutive columns (one per indicator):
  Column order: avg, 1stq, median, 3rdq, min, max
- Example: TIME columns are at indices 0-5, MEMORY_USED at indices 6-11, etc.
"""

import sys
import polars as pl
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt

# Matplotlib configuration - use scienceplots if available
try:
    import scienceplots
    plt.style.use(['science', 'ieee'])
except (ImportError, OSError, RuntimeError):
    # Fallback if scienceplots or LaTeX is not available
    print("Note: scienceplots or LaTeX not available, using default style")
    plt.rcParams.update({
        'text.usetex': False,  # Disable LaTeX
        'font.family': 'sans-serif',
    })
    
plt.rcParams.update({
    "font.size": 18,
    'text.usetex': False,  # Ensure LaTeX is disabled
})
plt.rcParams['axes.prop_cycle'] = matplotlib.cycler('linestyle', ['-', '--', ':', '-.'])

LINEWIDTH = 3

# Color and style configuration per method
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

# Metric configuration with properties
# Index is the base column index (each metric has 6 columns for 6 indicators)
METRICS_CONFIG = {
    'TIME': {'index': 0, 'color': None, 'label': 'Time', 'unit': '(s)', 'name': 'Time'},
    'MEMORY_USED': {'index': 1, 'color': 'b', 'label': 'Memory', 'unit': '(MiB)', 'name': 'VM allocated memory'},
    'MEMORY_FREE': {'index': 2, 'color': 'm', 'label': 'Memory', 'unit': '(MiB)', 'name': 'cgroup free memory'},
    'MEMORY_MAX': {'index': 3, 'color': 'k', 'label': 'Memory', 'unit': '(MiB)', 'name': 'cgroup memory.max'},
    'SWAP': {'index': 4, 'color': 'r', 'label': 'Memory', 'unit': '(MiB)', 'name': 'Host swap'},
    'CGROUP_CACHE': {'index': 5, 'color': 'y', 'label': 'Memory', 'unit': '(MiB)', 'name': 'cgroup cache'},
    'CGROUP_SWAPPABLE': {'index': 6, 'color': 'c', 'label': 'Memory', 'unit': '(MiB)', 'name': 'cgroup swappable'},
    'MEMORY_PRESSURE_AVG10': {'index': 7, 'color': 'darkRed', 'label': 'Pressure Stall Information', 'unit': '(PSI)', 'name': 'Memory pressure'},
    'VIRSH_ACTUAL': {'index': 11, 'color': 'k', 'label': 'Memory', 'unit': '(MiB)', 'name': 'VM allocated memory'},
    'VIRSH_UNUSED': {'index': 12, 'color': 'tomato', 'label': 'Memory', 'unit': '(MiB)', 'name': 'VM unused memory'},
    'VIRSH_USABLE': {'index': 13, 'color': 'm', 'label': 'Memory', 'unit': '(MiB)', 'name': 'Guest free memory'},
    'VIRSH_AVAILABLE': {'index': 14, 'color': 'g', 'label': 'Memory', 'unit': '(MiB)', 'name': 'Guest capacity'},
    'VIRSH_SWAP_IN': {'index': 15, 'color': '', 'label': 'Memory', 'unit': '(MiB)', 'name': 'VM swap in'},
    'VIRSH_SWAP_OUT': {'index': 16, 'color': 'r', 'label': 'Memory', 'unit': '(MiB)', 'name': 'Guest swap'},
    'PUBLISHER_BITRATE': {'index': 19, 'color': 'b', 'label': 'Bitrate', 'unit': '(kbps)', 'name': 'Publisher bitrate'},
    'PUBLISHER_FPS': {'index': 20, 'color': 'r', 'label': 'FPS', 'unit': '', 'name': 'Publisher FPS'},
    'PUBLISHER_RTT': {'index': 22, 'color': 'r', 'label': 'Delay', 'unit': '(ms)', 'name': 'Publisher RTT'},
    'VIEWER_COUNT': {'index': 24, 'color': 'y', 'label': 'Viewer Count', 'unit': '', 'name': 'Viewer count'},
    'VM_MEMORY_USAGE': {'index': 25, 'color': 'midnightBlue', 'label': 'Memory', 'unit': '(MiB)', 'name': 'Guest memory'},
    'VM_MEMORY_FREE': {'index': 26, 'color': 'tomato', 'label': 'Memory', 'unit': '(MiB)', 'name': 'VM current free memory'},
    'VM_CPU_USAGE': {'index': 27, 'color': 'b', 'label': 'CPU', 'unit': '(%)', 'name': 'VM cpu usage'},
    'VM_FREE_TOTAL': {'index': 28, 'color': 'purple', 'label': 'Memory', 'unit': '(MiB)', 'name': 'VM free total'},
    'VM_FREE_USED': {'index': 29, 'color': 'orange', 'label': 'Memory', 'unit': '(MiB)', 'name': 'VM free used'},
    'VM_FREE_BUFCACHE': {'index': 30, 'color': 'cyan', 'label': 'Memory', 'unit': '(MiB)', 'name': 'VM free buff/cache'},
    'VIEWER_TARGET': {'index': 44, 'color': 'k', 'label': 'Bitrate', 'unit': '(kbps)', 'name': 'viewer encoder target'},
    'VIEWER_BITRATE': {'index': 45, 'color': 'g', 'label': 'Bitrate', 'unit': '(kbps)', 'name': 'Viewer received bitrate'},
    'VIEWER_DELAY': {'index': 47, 'color': 'm', 'label': 'Delay', 'unit': '(ms)', 'name': 'End to end delay'},
    'VIEWER_FPS': {'index': 48, 'color': 'm', 'label': 'FPS', 'unit': '', 'name': 'Viewer received FPS'},
    'VIEWER_RID_H': {'index': 49, 'color': 'g', 'label': 'RID Count', 'unit': '', 'name': 'simulcast high layer'},
    'VIEWER_RID_M': {'index': 50, 'color': 'b', 'label': 'RID Count', 'unit': '', 'name': 'simulcast medium layer'},
    'VIEWER_RID_L': {'index': 51, 'color': 'r', 'label': 'RID Count', 'unit': '', 'name': 'simulcast low layer'},
}

# Available indicators for aggregated statistics
INDICATORS = ["avg", "1stq", "median", "3rdq", "min", "max"]
INDICATORS_COLOR = ['b', 'y', 'r', 'c', 'g', 'k']


def get_column_index(metric_index: int, indicator: str) -> int:
    """
    Calculate the column index for a metric and indicator combination
    
    CSV structure: Each metric has 6 consecutive columns (one per indicator)
    Column order: avg, 1stq, median, 3rdq, min, max
    
    Args:
        metric_index: Base index of the metric in METRICS_CONFIG
        indicator: Indicator name (avg, 1stq, median, 3rdq, min, max)
        
    Returns:
        Actual column index in the CSV file
    """
    indicator_offset = INDICATORS.index(indicator)
    return metric_index * len(INDICATORS) + indicator_offset


def load_csv_data(filename: str, indicators: list[str]) -> pl.DataFrame:
    """
    Load CSV file with multiple indicator handling
    
    CSV structure: The file has no headers. Each metric has 6 consecutive columns,
    one for each indicator (avg, 1stq, median, 3rdq, min, max).
    
    Args:
        filename: Path to CSV file
        indicators: List of indicators to load (e.g., ['avg', 'median'])
        
    Returns:
        Polars DataFrame with columns named like METRIC_NAME_indicator
    """
    # Read CSV without headers
    df = pl.read_csv(filename, has_header=False)
    
    # Build a mapping of new column names to their source column indices
    column_mapping = {}
    
    for metric_name, config in METRICS_CONFIG.items():
        metric_idx = config['index']
        for indicator in indicators:
            col_idx = get_column_index(metric_idx, indicator)
            # Check if this column exists in the dataframe
            if col_idx < len(df.columns):
                old_col_name = df.columns[col_idx]
                new_col_name = f"{metric_name}_{indicator}"
                column_mapping[old_col_name] = new_col_name
    
    # Rename columns
    df = df.rename(column_mapping)
    
    # Select only the renamed columns
    selected_cols = list(column_mapping.values())
    df = df.select(selected_cols)
    
    return df


def apply_transformations(df: pl.DataFrame, metrics: list[str], indicators: list[str]) -> pl.DataFrame:
    """
    Apply transformations defined for each metric
    
    Transformations are hardcoded for performance (using native Polars expressions):
    - TIME: milliseconds to seconds (/ 1000.0)
    - VIRSH_*: KiB to MiB (/ 1024.0)
    - CGROUP_CACHE, CGROUP_SWAPPABLE: bytes to MiB (/ 1024.0 / 1024.0)
    - VM_CPU_USAGE: fraction to percentage (* 100.0)
    - Others: no transformation (identity)
    
    Args:
        df: Polars DataFrame
        metrics: List of metrics to transform
        indicators: List of indicators being used
        
    Returns:
        DataFrame with transformations applied
    """
    for metric in metrics:
        if metric not in METRICS_CONFIG:
            continue
        
        # Apply transformation to each indicator column for this metric
        for indicator in indicators:
            col_name = f"{metric}_{indicator}"
            if col_name not in df.columns:
                continue
            
            # Apply transformation based on metric type
            # Using native Polars expressions for optimal performance
            if metric == 'TIME':
                df = df.with_columns((pl.col(col_name) / 1000.0).alias(col_name))
            elif metric in ['VIRSH_ACTUAL', 'VIRSH_UNUSED', 'VIRSH_USABLE', 'VIRSH_AVAILABLE', 'VIRSH_SWAP_IN', 'VIRSH_SWAP_OUT']:
                df = df.with_columns((pl.col(col_name) / 1024.0).alias(col_name))
            elif metric in ['CGROUP_CACHE', 'CGROUP_SWAPPABLE']:
                df = df.with_columns((pl.col(col_name) / 1024.0 / 1024.0).alias(col_name))
            elif metric == 'VM_CPU_USAGE':
                df = df.with_columns((pl.col(col_name) * 100.0).alias(col_name))
            # For other metrics, no transformation needed (identity transform)
    
    return df


def apply_rolling_window(df: pl.DataFrame, column: str, indicators: list[str], window_size: int = 10) -> pl.DataFrame:
    """
    Apply rolling window (moving average) to column(s)
    
    Args:
        df: Polars DataFrame
        column: Base column name (without indicator suffix)
        indicators: List of indicators being used
        window_size: Window size
        
    Returns:
        DataFrame with transformed column(s)
    """
    for indicator in indicators:
        col_name = f"{column}_{indicator}"
        if col_name not in df.columns:
            continue
            
        # Use min_samples instead of min_periods (recent Polars version)
        try:
            df = df.with_columns(
                pl.col(col_name).rolling_mean(window_size=window_size, min_samples=1).alias(col_name)
            )
        except TypeError:
            # Fallback for older Polars versions
            df = df.with_columns(
                pl.col(col_name).rolling_mean(window_size=window_size, min_periods=1).alias(col_name)
            )
    return df


def filter_time_window(df: pl.DataFrame, time_col: str, indicators: list[str], window: list[float] = None) -> pl.DataFrame:
    """
    Filter DataFrame by time window
    
    Args:
        df: Polars DataFrame
        time_col: Name of time column (without indicator suffix)
        indicators: List of indicators being used
        window: [start, end] in seconds
        
    Returns:
        Filtered DataFrame with time normalized to 0
    """
    if window is None:
        return df
    
    # Use the first indicator's time column for filtering
    time_col_with_ind = f"{time_col}_{indicators[0]}"
    if time_col_with_ind not in df.columns:
        return df
    
    # Filter by window
    df_filtered = df.filter(
        (pl.col(time_col_with_ind) >= window[0]) & (pl.col(time_col_with_ind) <= window[1])
    )
    
    # Normalize time to start at 0 for all indicator columns
    if len(df_filtered) > 0:
        time_start = df_filtered[time_col_with_ind][0]
        for indicator in indicators:
            col_name = f"{time_col}_{indicator}"
            if col_name in df_filtered.columns:
                df_filtered = df_filtered.with_columns(
                    (pl.col(col_name) - time_start).alias(col_name)
                )
    
    return df_filtered


def get_method_from_filename(filename: str) -> str:
    """
    Extract method name from filename
    
    Args:
        filename: File path
        
    Returns:
        Method name ('ballooning', 'cgroup-max', 'cgroup-reclaim')
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
    Add colored annotations for different phases of the experiment
    
    Args:
        ax: Matplotlib axes
    """
    phases = [
        {"start": 0, "end": 60, "color": "lightgray", "label": "No viewers"},
        {"start": 60, "end": 120, "color": "lightblue", "label": "20 viewers"},
        {"start": 120, "end": 180, "color": "lightgreen", "label": "40 viewers"},
        {"start": 180, "end": 240, "color": "yellow", "label": "60 viewers"},
        {"start": 240, "end": 720, "color": "orange", "label": "80 viewers"},
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
    indicators: list[str] = None,
    show: bool = False,
    annotate: bool = False,
    rolling_cols: list[str] = None
):
    """
    Create a standard plot with one or more CSV files
    
    Args:
        filenames: List of CSV files to plot
        x_axis: Column name for X axis
        y_axis: List of columns for primary Y axis
        y2_axis: List of columns for secondary Y axis (optional)
        window: Time window [start, end]
        indicators: List of statistical indicators to use
        show: Show plot instead of saving
        annotate: Add phase annotations
        rolling_cols: Columns to apply rolling window
    """
    if y2_axis is None:
        y2_axis = []
    if rolling_cols is None:
        rolling_cols = []
    if indicators is None:
        indicators = ["avg"]
    
    # Create figure
    fig, ax = plt.subplots(figsize=(5, 5))
    fig.patch.set_alpha(0.0)
    ax.set_facecolor('none')
    
    # Configure secondary Y axis if needed
    bx = None
    if len(y2_axis) > 0:
        bx = ax.twinx()
        bx.set_facecolor('none')
    
    # Determine if comparing multiple files or metrics
    multiple_files = len(filenames) > 1
    multiple_metrics = len(y_axis) > 1 or len(y2_axis) > 1
    multiple_indicators = len(indicators) > 1
    
    # Plot data for each file
    for filename in filenames:
        # Load and prepare data
        df = load_csv_data(filename, indicators)
        
        # Apply transformations
        all_metrics = [x_axis] + y_axis + y2_axis
        df = apply_transformations(df, all_metrics, indicators)
        
        # Apply rolling windows
        for col in rolling_cols:
            df = apply_rolling_window(df, col, indicators)
        
        # Filter by time window
        df = filter_time_window(df, x_axis, indicators, window)
        
        # Extract method from filename for multi-file comparison
        method = get_method_from_filename(filename) if multiple_files else None
        
        # Plot primary Y metrics
        for y_metric in y_axis:
            config = METRICS_CONFIG.get(y_metric, {})
            color = config.get('color', 'b')
            base_label = config.get('name', y_metric)
            
            # Plot each indicator
            for ind_idx, indicator in enumerate(indicators):
                col_name = f"{y_metric}_{indicator}"
                if col_name not in df.columns:
                    continue
                
                # Adjust style/color based on context
                linestyle = '-'
                plot_color = color
                
                if multiple_indicators:
                    # When showing multiple indicators, use different colors per indicator
                    plot_color = INDICATORS_COLOR[INDICATORS.index(indicator)]
                    label = indicator if len(y_axis) == 1 else f"{base_label} ({indicator})"
                elif multiple_files and method:
                    if multiple_metrics:
                        linestyle = method_style.get(method, '-')
                        label = f"{base_label} ({method})"
                    else:
                        plot_color = method_color.get(method, color)
                        label = method
                else:
                    label = base_label
                
                # Get x values for this indicator
                x_col_name = f"{x_axis}_{indicator}"
                if x_col_name not in df.columns:
                    continue
                
                # Plot the curve
                ax.plot(
                    df[x_col_name].to_numpy(),
                    df[col_name].to_numpy(),
                    color=plot_color,
                    linestyle=linestyle,
                    linewidth=LINEWIDTH,
                    label=label
                )
        
        # Plot secondary Y metrics
        if bx:
            for y_metric in y2_axis:
                config = METRICS_CONFIG.get(y_metric, {})
                color = config.get('color', 'g')
                base_label = config.get('name', y_metric)
                
                # Plot each indicator
                for indicator in indicators:
                    col_name = f"{y_metric}_{indicator}"
                    if col_name not in df.columns:
                        continue
                    
                    # Adjust based on context
                    linestyle = '-'
                    plot_color = color
                    
                    if multiple_indicators:
                        plot_color = INDICATORS_COLOR[INDICATORS.index(indicator)]
                        label = indicator if len(y2_axis) == 1 else f"{base_label} ({indicator})"
                    elif multiple_files and method:
                        if multiple_metrics:
                            linestyle = method_style.get(method, '-')
                            label = f"{base_label} ({method})"
                        else:
                            plot_color = method_color.get(method, color)
                            label = method
                    else:
                        label = base_label
                    
                    x_col_name = f"{x_axis}_{indicator}"
                    if x_col_name not in df.columns:
                        continue
                    
                    bx.plot(
                        df[x_col_name].to_numpy(),
                        df[col_name].to_numpy(),
                        color=plot_color,
                        linestyle=linestyle,
                        linewidth=LINEWIDTH,
                        label=label
                    )
    
    # Configure labels
    x_config = METRICS_CONFIG.get(x_axis, {})
    ax.set_xlabel(f"{x_config.get('label', x_axis)} {x_config.get('unit', '')}")
    
    y_config = METRICS_CONFIG.get(y_axis[0], {})
    label_type = 'name' if (not multiple_files or multiple_metrics or multiple_indicators) else 'label'
    ax.set_ylabel(f"{y_config.get(label_type, y_axis[0])} {y_config.get('unit', '')}")
    
    if bx and len(y2_axis) > 0:
        y2_config = METRICS_CONFIG.get(y2_axis[0], {})
        bx.set_ylabel(f"{y2_config.get(label_type, y2_axis[0])} {y2_config.get('unit', '')}")
    
    # Add annotations if requested
    if annotate:
        add_phase_annotations(ax)
    
    # Configure axis limits (can be customized if needed)
    # TODO: Make these configurable or calculate dynamically
    ax.set_xlim([0, 400])
    ax.set_ylim([0, 2500])
    
    # Add legend
    leg = fig.legend(loc='center left', bbox_to_anchor=(1., 0.5), bbox_transform=ax.transAxes, frameon=True)
    if leg:
        leg.get_frame().set_alpha(0.0)
    
    # Save or show
    if show:
        plt.show()
    else:
        ext = "pdf"
        dest_path = filenames[0].split('/')
        
        if len(filenames) > 1:
            dest_path.pop()
        
        if len(y2_axis) > 0:
            dest_path[-1] = f"plot_{x_axis}x{y_axis[0]}x{y2_axis[0]}_{'-'.join(indicators)}.{ext}"
        else:
            dest_path[-1] = f"plot_{x_axis}x{y_axis[0]}_{'-'.join(indicators)}.{ext}"
        
        plt.savefig("/".join(dest_path), format=ext, transparent=True)
    
    plt.close()


def plot_delta(
    filenames: list[str],
    x_axis: str,
    y_axis: list[str],
    window: list[float] = None,
    indicators: list[str] = None,
    show: bool = False,
    annotate: bool = False
):
    """
    Create a delta plot comparing files to a baseline
    The first file serves as baseline, others are compared to it
    
    Args:
        filenames: List of CSV files (first is baseline)
        x_axis: Column name for X axis
        y_axis: List of columns for metrics to compare
        window: Time window [start, end]
        indicators: List of statistical indicators to use
        show: Show plot instead of saving
        annotate: Add phase annotations
    """
    if len(filenames) < 2:
        print("Error: plot_delta requires at least 2 files (baseline + comparison)")
        return
    
    if indicators is None:
        indicators = ["avg"]
    
    # Load baseline
    df_baseline = load_csv_data(filenames[0], indicators)
    all_metrics = [x_axis] + y_axis
    df_baseline = apply_transformations(df_baseline, all_metrics, indicators)
    df_baseline = filter_time_window(df_baseline, x_axis, indicators, window)
    
    # Create figure with one subplot per metric
    fig, axes = plt.subplots(len(y_axis), 1, figsize=(16, 9), sharex=True)
    fig.patch.set_alpha(0.0)
    
    if len(y_axis) == 1:
        axes = [axes]
    
    for ax in axes:
        ax.set_facecolor('none')
    
    # Plot delta for each comparison file
    for fi, filename in enumerate(filenames[1:], start=1):
        # Load comparison file
        df_compare = load_csv_data(filename, indicators)
        df_compare = apply_transformations(df_compare, all_metrics, indicators)
        df_compare = filter_time_window(df_compare, x_axis, indicators, window)
        
        # Get method for styling
        method = get_method_from_filename(filename)
        color = method_color.get(method, 'b')
        
        # Simplified label
        label = filename.split('/')[-1]
        if 'balloon' in label:
            label = 'ballooning'
        elif 'cgroup' in label:
            label = 'cgroups'
        
        # Plot delta for each metric
        for mi, metric in enumerate(y_axis):
            ax = axes[mi]
            
            # Plot delta for each indicator
            for indicator in indicators:
                col_name = f"{metric}_{indicator}"
                x_col_name = f"{x_axis}_{indicator}"
                
                if col_name not in df_baseline.columns or col_name not in df_compare.columns:
                    continue
                if x_col_name not in df_baseline.columns:
                    continue
                
                # Calculate delta
                min_len = min(len(df_baseline), len(df_compare))
                
                baseline_values = df_baseline[col_name].head(min_len).to_numpy()
                compare_values = df_compare[col_name].head(min_len).to_numpy()
                x_values = df_baseline[x_col_name].head(min_len).to_numpy()
                
                delta = compare_values - baseline_values
                
                # Create label
                plot_label = label if len(indicators) == 1 else f"{label} ({indicator})"
                plot_color = color if len(indicators) == 1 else INDICATORS_COLOR[INDICATORS.index(indicator)]
                
                # Plot delta
                ax.plot(x_values, delta, color=plot_color, alpha=0.7, label=plot_label)
            
            # Zero reference line
            ax.axhline(0, color='black', linestyle='--', linewidth=1)
            
            # Labels
            config = METRICS_CONFIG.get(metric, {})
            ax.set_ylabel(f"{config.get('label', metric)} {config.get('unit', '')}")
            ax.set_title(f"{config.get('name', metric)}")
            
            if annotate:
                add_phase_annotations(ax)
            
            # X-axis limit (TODO: make configurable)
            ax.set_xlim([0, 1200])
    
    # X axis label on last subplot
    x_config = METRICS_CONFIG.get(x_axis, {})
    axes[-1].set_xlabel(f"{x_config.get('label', x_axis)} {x_config.get('unit', '')}")
    
    # Align Y labels
    fig.align_ylabels(axes)
    
    # Consolidated legend
    handles, labels = axes[0].get_legend_handles_labels()
    if handles:
        leg = fig.legend(handles, labels, loc='center left', bbox_to_anchor=(1.02, 0.5), frameon=True)
        if leg:
            leg.get_frame().set_alpha(0.0)
    
    # Save or show
    ext = "pdf"
    if show:
        plt.show()
    else:
        dest_path = filenames[0].split('/')
        dest_path[-1] = f"delta_{x_axis}x{'-'.join(y_axis)}_{'-'.join(indicators)}.{ext}"
        plt.savefig("/".join(dest_path), format=ext, bbox_inches='tight', transparent=True)
    
    plt.close(fig)


def process_and_plot(settings: dict):
    """
    Main entry point for generating plots
    
    Args:
        settings: Configuration dictionary with parameters:
            - files: List of CSV files
            - indicator: List of statistical indicators (e.g., ['avg', 'median'])
            - x: Column for X axis
            - y: List of columns for Y axis
            - y2: List of columns for secondary Y axis (optional)
            - window: Time window [start, end] (optional)
            - location: Legend position (optional)
            - leg_col: Number of legend columns (optional)
            - annotate: Add annotations (optional)
            - show: Display instead of saving (optional)
            - delta: Delta mode (optional)
            - rolling: Columns with rolling window (optional)
    """
    filenames = settings.get("files", [])
    indicators = settings.get("indicator", ["avg"])
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
        raise ValueError("No files specified")
    
    # Ensure indicators is a list
    if isinstance(indicators, str):
        indicators = [indicators]
    
    for ind in indicators:
        if ind not in INDICATORS:
            raise ValueError(f"Invalid indicator: {ind}. Valid values: {INDICATORS}")
    
    all_metrics = [x_axis] + y_axis + (y2_axis or [])
    for metric in all_metrics:
        if metric not in METRICS_CONFIG:
            print(f"Warning: unknown metric '{metric}'")
    
    # Generate appropriate plot
    if delta:
        plot_delta(filenames, x_axis, y_axis, window, indicators, show, annotate)
    else:
        plot_standard(filenames, x_axis, y_axis, y2_axis, window, indicators, show, annotate, rolling_cols)


if __name__ == "__main__":
    # Parse command line arguments
    if len(sys.argv) < 5:
        print("Usage: {} <file1[,file2,...]> <indicator1[,indicator2,...]> <x_axis> <y_axis1[,y_axis2,...]> [y2_axis1[,y2_axis2,...]] [options]".format(sys.argv[0]))
        print("\nAvailable indicators: " + ", ".join(INDICATORS))
        print("\nOptions:")
        print("  show              - Display plot instead of saving")
        print("  [start,end]       - Time window")
        print("  loc=N             - Legend position")
        print("  leg_col=N         - Number of legend columns")
        print("  annotate          - Add phase annotations")
        print("  delta             - Delta mode (compare to baseline)")
        sys.exit(1)
    
    # Parse arguments
    filenames = sys.argv[1].split(',')
    indicators = sys.argv[2].split(',')
    x_axis = sys.argv[3]
    y_axis = sys.argv[4].split(',')
    
    # Default options
    y2_axis = []
    show = False
    window = None
    location = 1
    legend_col = 1
    annotate = False
    delta_mode = False
    
    # Parse additional options
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
            # If not a recognized option and contains commas, it's probably y2_axis
            y2_axis = arg.split(',')
    
    # Columns with rolling window (bitrates and FPS)
    rolling_cols = ['PUBLISHER_BITRATE', 'VIEWER_BITRATE', 'PUBLISHER_FPS', 'VIEWER_FPS']
    
    # Call main function
    settings = {
        "files": filenames,
        "indicator": indicators,
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
