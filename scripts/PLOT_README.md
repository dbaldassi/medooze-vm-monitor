# Plot Script Improvements

## Overview

The `scripts/plot.py` script has been refactored to provide a cleaner, more maintainable, and more flexible plotting system with extensive Polars integration.

## Key Improvements

### 1. Extensive Polars Integration
- **Before**: Manual CSV parsing, immediate conversion to lists, manual list comprehensions
- **After**: Polars DataFrames used throughout the entire pipeline with native column operations
- **Benefit**: Faster, more efficient data processing with cleaner code

**Details**:
- CSV files are loaded as Polars DataFrames and kept as DataFrames
- Column operations use Polars' optimized functions instead of Python loops
- Data transformations leverage Polars' `select()` and `map_elements()` capabilities
- No more manual index calculations - use column names directly

**Example**:
```python
# Before: Manual indexing and list comprehensions
lines = open_csv(filename)  # Returns list of lists
y_idx = get_index(header[INDEX], indicator[0])
y_values = [header[PROCESS](line[y_idx]) if len(line) > y_idx else 0 for line in lines]

# After: Polars column operations
df = open_csv(filename)  # Returns Polars DataFrame
y_series = apply_column_transform(df, column_name, indicator[0], header[PROCESS])
y_values = y_series.to_list()
```

### 2. Language Support
The script now supports multilingual labels (French and English).

**Configuration**: Use the `lang` parameter in settings:
- `"lang": "fr"` for French labels (default)
- `"lang": "en"` for English labels

**Example**:
```python
settings = {
    "lang": "fr",  # or "en"
    # ... other settings
}
```

### 3. Settings-Based Configuration
All plotting functions now use a unified `settings` dictionary instead of multiple parameters.

**Available Settings**:

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| `files` | list[str] | required | List of CSV file paths |
| `indicator` | list[str] | required | Indicators: 'avg', 'median', '1stq', '3rdq', 'min', 'max' |
| `x` | str | required | X-axis column name |
| `y` | list[str] | required | Y-axis column names |
| `y2` | list[str] | `[]` | Secondary Y-axis column names |
| `window` | list[int] | `None` | Time window [start, end] |
| `lang` | str | `"fr"` | Language: 'fr' or 'en' |
| `format` | str | `"pdf"` | Output format: 'pdf' or 'png' |
| `name` | str | auto-generated | Output filename (without extension) |
| `figsize` | tuple | `(5, 5)` | Figure size (width, height) in inches |
| `transparency` | bool | `True` | Transparent background |
| `annotate` | bool | `False` | Add phase annotations |
| `show` | bool | `False` | Display plot window |
| `location` | int | `1` | Legend location |
| `leg_col` | int | `1` | Number of legend columns |
| `delta` | bool | `False` | Plot delta between files |

### 4. Dynamic Column Detection with Polars
- **Before**: Hardcoded column names and indices in large dictionary
- **After**: Column metadata generated dynamically, accessed by name via Polars
- **Benefit**: Easier to maintain, extend, and understand

**Column Naming Convention**:
The script expects CSV columns to follow the pattern: `{METRIC}_{indicator}`
- Example: `TIME_median`, `VM_CPU_USAGE_avg`, `MEMORY_USED_1stq`
- Indicators: `avg`, `median`, `1stq`, `3rdq`, `min`, `max`

### 5. Simplified Plotting Functions
New helper functions for cleaner code:
- `get_column_name_with_indicator()`: Build column names from metric + indicator
- `apply_column_transform()`: Apply transformations using Polars operations
- Functions work directly with DataFrames instead of lists

### 5. Figure Creation Function
New `create_figure(settings)` function handles figure creation with:
- Custom size from `settings.figsize`
- Transparency from `settings.transparency`

## Internal Architecture

### Data Flow

```
CSV File → Polars DataFrame → Column Selection → Transformation → Plotting
```

**Key Functions**:

1. **`open_csv(filename)`**: Loads CSV as Polars DataFrame
2. **`get_column_name_with_indicator(column, indicator)`**: Builds column name (e.g., "TIME_median")
3. **`apply_column_transform(df, column, indicator, transform_func)`**: Applies transformation to a column using Polars
4. **`plot_yy(ax, df, column_name, header, ...)`**: Plots data using Polars Series
5. **`plot(settings, ...)`**: Main plotting orchestration with DataFrames

### Polars Operations Used

- `pl.read_csv()`: Fast CSV loading
- `pl.col().map_elements()`: Apply custom transformations
- `pl.Series()`: Efficient series operations for deltas
- `.to_list()`: Convert to list only when needed for matplotlib

## Usage Examples

### Basic Usage with Settings

```python
from plot import process_and_plot

settings = {
    "files": ["data/experiment_2025-01-01.csv"],
    "indicator": ["median"],
    "x": "TIME",
    "y": ["VM_CPU_USAGE", "VM_MEMORY_USAGE"],
    "lang": "fr",
    "format": "pdf",
    "name": "cpu_memory_plot",
    "figsize": (10, 6),
    "transparency": True,
}

process_and_plot(settings)
```

### Using Different Languages

```python
# French plot
settings_fr = {
    "files": ["data/results.csv"],
    "indicator": ["avg"],
    "x": "TIME",
    "y": ["PUBLISHER_BITRATE", "VIEWER_BITRATE"],
    "lang": "fr",  # French labels
    "format": "pdf",
    "name": "bitrate_fr",
}

# English plot
settings_en = {
    "files": ["data/results.csv"],
    "indicator": ["avg"],
    "x": "TIME",
    "y": ["PUBLISHER_BITRATE", "VIEWER_BITRATE"],
    "lang": "en",  # English labels
    "format": "png",
    "name": "bitrate_en",
}

process_and_plot(settings_fr)
process_and_plot(settings_en)
```

### Custom Figure Size and Format

```python
settings = {
    "files": ["data/memory_test.csv"],
    "indicator": ["median"],
    "x": "TIME",
    "y": ["MEMORY_USED", "SWAP"],
    "lang": "en",
    "format": "png",  # PNG format
    "name": "memory_comparison",
    "figsize": (12, 8),  # Custom size
    "transparency": False,  # Opaque background
}

process_and_plot(settings)
```

### Using with YAML Configuration

The script works seamlessly with `generate_figs.py` and YAML configuration files:

```yaml
global-settings:
  lang: en  # or fr
  format: pdf  # or png
  transparency: true
  figsize: [10, 6]

exps:
  my_experiment:
    figures:
      - name: cpu_usage
        protocol: plot
        files:
          - results/experiment_data.csv
        x: TIME
        y:
          - VM_CPU_USAGE
        lang: en
        format: png
```

## Migration Guide

### From Previous Version

**Old Code (list-based)**:
```python
lines = open_csv(filename)  # Returns list of lists
x_axis_idx = get_index(headers[x_axis][INDEX], indicator[0])
x_values = [headers[x_axis][PROCESS](line[x_axis_idx]) for line in lines]
```

**New Code (Polars-based)**:
```python
df = open_csv(filename)  # Returns Polars DataFrame
x_series = apply_column_transform(df, x_axis, indicator[0], headers[x_axis][PROCESS])
x_values = x_series.to_list()
```

### Benefits of Refactoring

1. **Cleaner Code**: No more manual indexing with `get_index()`
2. **Better Performance**: Polars optimized operations instead of Python loops
3. **Easier Debugging**: Column names instead of numeric indices
4. **More Maintainable**: Clear data flow with DataFrames
5. **Extensible**: Easy to add new transformations using Polars expressions

## Dependencies

Install required packages:
```bash
pip install -r requirements.txt
```

Required packages:
- polars >= 0.19.0
- matplotlib >= 3.5.0
- scienceplots >= 2.0.0
- pyyaml >= 6.0
- seaborn >= 0.12.0

## Backward Compatibility

The script maintains backward compatibility with command-line usage:

```bash
python plot.py file.csv median TIME VM_CPU_USAGE
```

The command-line interface automatically creates a settings dictionary with default values.
