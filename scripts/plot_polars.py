import polars as pl
import matplotlib.pyplot as plt
import scienceplots

# TODO: set csv unit in yaml and compute in funciton of axis unit.

# Post-processing function
def process_metric(column, operations):
    for operation in operations:
        for op,args in operation.items():
            if op == "slide-window":
                column = column.rolling_mean(args)
        # Add other operations if needed
    return column

# Function to rename duplicated indicators for each metric
def resolve_column_names(df, config):
    """
    Resolves the issue of duplicated column names in Polars by assigning unique names
    to columns based on the metric and indicator. Assumes indicators have the same order for all metrics.

    Args:
        df (pl.DataFrame): Polars DataFrame loaded from CSV.
        config (dict): Dictionary containing plot configurations.

    Returns:
        pl.DataFrame: DataFrame with renamed columns.
    """
    indicators = ["1stQ", "Median", "3rdQ", "Min", "Max"]
    renamed_columns = []  # Store new column names
    current_metric = None  # Keep track of current metric while renaming

    for col in df.columns:
        # If the column name matches the name of a metric, update "current_metric"
        if not any([ind in col for ind in indicators]):
            current_metric = col
            renamed_columns.append(col)  # Keep metric names unchanged
        else:
            # Handle indicators (renamed as METRIC_INDICATOR)
            indicator_idx = len(renamed_columns)
            indicator = indicators[indicator_idx % len(indicators)]
            renamed_columns.append(f"{current_metric}_{indicator.lower()}")

    # Rename columns in the DataFrame
    df.columns = renamed_columns
    return df

def handle_missing_values(df, fill_value=0):
    """
    Handles missing values (None/NaN) in a DataFrame by filling them with a specific value.
    Args:
        df (pl.DataFrame): The input DataFrame.
        fill_value (float or int): The value to replace None/NaN values with (default: 0).
    Returns:
        pl.DataFrame: The DataFrame with missing values handled.
    """
    return df.fill_null(fill_value)


# Plotting function
def plot_metrics(config, column_labels):
    """
    Plot metrics as specified in the config and column labels.

    Args:
        config (dict): Dictionary containing plot configurations.
        column_labels (dict): Dictionary mapping column names to labels in English and French.
    """
    plt.style.use("ieee")
    plt.figure(figsize=config.get("figsize", (10, 6)))

    # Determine language for labels (default: "en")
    lang = config.get("lang", "en")

    # Manage global indicators if specified
    indicators = config.get("indicators", ["avg"])  # Default to 'avg' if no indicators provided

    for file in config["files"]:
        df = pl.read_csv(file)
        df = resolve_column_names(df, config)

        # # Post-process specified columns
        post_processing = config.get("process", {})
        # for column, operations in post_processing.items():
        #     if column in df.columns:
        #         df = df.with_columns(process_metric(df[column], operations).alias(column))

        # X-axis configuration
        x_metric = config['x']
        x_data = df[x_metric]
        x_label = config.get("xlabel", column_labels.get(x_metric, {}).get(lang, x_metric))
        plt.xlabel(x_label)

        # Process Y-axis metrics
        y_metrics = config.get("y", [])
        for metric in y_metrics:
            for indicator in indicators:
                y_column_name = metric if indicator == "avg" else f"{metric}_{indicator}"
                if y_column_name in df.columns:
                    y_data = df[y_column_name].cast(pl.Float64, strict=False)
                    y_data = handle_missing_values(y_data)

                    if metric in post_processing:
                        y_data = process_metric(y_data, post_processing[metric])

                    y_label = column_labels.get(metric, {}).get(lang, metric)
                    label = f"{y_label} - {indicator}"
                    plt.plot(x_data, y_data, label=label)

        # Process secondary Y-axis metrics (if specified)
        if "y2" in config:
            ax2 = plt.gca().twinx()
            y2_metrics = config["y2"]
            for metric in y2_metrics:
                for indicator in indicators:
                    y2_column_name = metric if indicator == "avg" else f"{metric}_{indicator}"
                    if y2_column_name in df.columns:
                        y2_data = df[y2_column_name].cast(pl.Float64, strict=False)
                        y2_data = handle_missing_values(y2_data)
                        y2_label = column_labels.get(metric, {}).get(lang, metric)
                        label = f"{y2_label} - {indicator}"
                        ax2.plot(x_data, y2_data, label=label, linestyle="--", alpha=config.get("transparency", 0.5))

    # Set x and y limits
    if "xlim" in config:
        plt.xlim(config["xlim"][0], config["xlim"][1])
    if "ylim" in config:
        plt.ylim(config["ylim"][0], config["ylim"][1])
    if "y2lim" in config and "y2" in config:
        ax2.set_ylim(config["y2lim"][0], config["y2lim"][1])

    # Customizing Legend
    loc = config.get("loc", 0)
    leg_col = config.get("leg_col", 1)
    plt.legend(loc=loc, ncol=leg_col)

    # Custom titles
    if "title" in config:
        plt.title(config["title"])

    # Save the output file
    output_file = config.get("name", "plot")
    ext = config.get("format", "pdf")
    plt.savefig(f"{config.get('out-dir', '.')}/{output_file}.{ext}")


def process_and_plot(settings):
    plot_metrics(settings, {})
