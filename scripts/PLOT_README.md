# Plot Script Improvements

## Overview

The `scripts/plot.py` script has been refactored to provide a cleaner, more maintainable, and more flexible plotting system.

## Key Improvements

### 1. Polars Integration
- **Before**: Manual CSV parsing using Python's csv module
- **After**: Using Polars library for efficient CSV processing
- **Benefit**: Faster, more reliable CSV reading with better memory management

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

### 4. Dynamic Column Detection
- **Before**: Hardcoded column names and indices in large dictionary
- **After**: Column metadata generated dynamically with language support
- **Benefit**: Easier to maintain and extend

### 5. Figure Creation Function
New `create_figure(settings)` function handles figure creation with:
- Custom size from `settings.figsize`
- Transparency from `settings.transparency`

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

### Old Code
```python
plot(
    filenames,
    x_axis,
    y_axis,
    y2_axis,
    window,
    indicator,
    show,
    (1024, 1024),  # resolution
    location,
    legend_col,
    annotate
)
```

### New Code
```python
settings = {
    "files": filenames,
    "x": x_axis,
    "y": y_axis,
    "y2": y2_axis,
    "window": window,
    "indicator": indicator,
    "show": show,
    "figsize": (10, 10),  # size instead of resolution
    "location": location,
    "leg_col": legend_col,
    "annotate": annotate,
    "lang": "fr",  # NEW: choose language
    "format": "pdf",  # NEW: choose format
    "name": "output",  # NEW: custom name
    "transparency": True,  # NEW: transparency
}

process_and_plot(settings)
```

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
