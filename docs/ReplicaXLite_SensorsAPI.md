# ReplicaXSensorDataReader - User Manual

## Table of Contents
1. [Overview](#overview)
2. [Installation & Setup](#installation--setup)
3. [Quick Start Guide](#quick-start-guide)
4. [Configuration Structure](#configuration-structure)
5. [Data Processing Workflow](#data-processing-workflow)
6. [Data Corrections](#data-corrections)
7. [Data Export](#data-export)
8. [Visualization](#visualization)
9. [Advanced Features](#advanced-features)
10. [Filter Comparison Tools](#filter-comparison-tools)
11. [Troubleshooting](#troubleshooting)
12. [API Reference](#api-reference)

---

## Overview

**ReplicaXSensorDataReader** is a comprehensive Python toolkit for reading, processing, analyzing, and visualizing sensor data from CSV files. It provides a flexible configuration-based approach to handle various data formats, apply corrections, perform unit conversions, and generate professional visualizations.

### Key Features
- **Flexible CSV Reading**: Support for various separators and decimal formats
- **Unit Conversion**: Automatic conversion between different unit systems
- **Data Corrections**: 11 types of corrections including filtering, detrending, integration, and more
- **Multiple Export Formats**: Export processed data in various CSV formats
- **Visualization Tools**: Built-in plotting capabilities with matplotlib
- **Filter Comparison**: Advanced tools for comparing and ranking different filters
- **Integration Analysis**: Calculate and visualize cumulative integrals of sensor data

---

## Installation & Setup

### Requirements
```python
import os
import csv
import datetime
import json
import numpy as np
from scipy import signal
from scipy.integrate import cumulative_trapezoid
from scipy import interpolate  # For advanced resampling
import matplotlib.pyplot as plt
```

### Basic Import
```python
from replicaxlite import ReplicaXSensorDataReader
```

---

## Quick Start Guide

### Example 1: Basic Usage with JSON Configuration

```python
# Create reader instance
reader = ReplicaXSensorDataReader()

# Load configuration from JSON file
reader.load_config_from_json('sensor_config.json')

# Access processed data
time, acceleration = reader.get_xy('Acceleration_1')

# Get summary statistics
summary = reader.get_summary()
print(summary)

# Export processed data
reader.export_to_csv('processed_data.csv')
```

### Example 2: Programmatic Configuration

```python
# Define configuration dictionary
config = {
    "file_path": "raw_data.csv",
    "seperator": ",",
    "decimal": ".",
    "start_row": 2,
    "end_row": 1000,
    "dt": 0.001,
    "time_column": "A",
    "data_type": "Acceleration",
    "input_units": {
        "time": "s",
        "data": "m/s^2"
    },
    "output_units": {
        "time": "s",
        "data": "g"
    },
    "data": {
        "ACC1": "B",
        "ACC2": "C"
    },
    "data_name": {
        "ACC1": "Acceleration_1",
        "ACC2": "Acceleration_2"
    },
    "data_correction": {
        "zero_start_time": {"process": True},
        "zero_start_y": {"process": True, "value": 100},
        "filter": {
            "process": True,
            "type": "butterworth",
            "params": {
                "order": 4,
                "btype": "low",
                "cutoff": 50
            }
        }
    }
}

# Create reader with configuration
reader = ReplicaXSensorDataReader(config)

# Or load configuration later
reader = ReplicaXSensorDataReader()
reader.load_config_from_dict(config)
```

---

## Configuration Structure

### Required Parameters

| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| `file_path` | string | Path to CSV file | `"data/sensors.csv"` |
| `seperator` | string | CSV column separator | `","` or `";"` |
| `decimal` | string | Decimal point character | `"."` or `","` |
| `start_row` | integer | First data row (Excel 1-based) | `2` |
| `end_row` | integer | Last data row (Excel 1-based) | `1000` |
| `dt` | float | Time step in seconds | `0.001` |
| `time_column` | string | Time column letter | `"A"` |
| `data_type` | string | Type of data | `"Acceleration"`, `"Force"`, etc. |
| `input_units` | dict | Input unit system | `{"time": "s", "data": "m/s^2"}` |
| `output_units` | dict | Output unit system | `{"time": "s", "data": "g"}` |
| `data` | dict | Column mapping | `{"ACC1": "B", "ACC2": "C"}` |
| `data_name` | dict | Display names | `{"ACC1": "Acceleration_1"}` |
| `data_correction` | dict | Correction settings | See [Data Corrections](#data-corrections) |

### Configuration Template

```json
{
    "file_path": "path/to/data.csv",
    "seperator": ",",
    "decimal": ".",
    "start_row": 2,
    "end_row": 1000,
    "dt": 0.001,
    "time_column": "A",
    "data_type": "Acceleration",
    "input_units": {
        "time": "s",
        "data": "m/s^2"
    },
    "output_units": {
        "time": "s",
        "data": "g"
    },
    "data": {
        "ACC1": "B",
        "ACC2": "C",
        "ACC3": "D"
    },
    "data_name": {
        "ACC1": "Sensor_1",
        "ACC2": "Sensor_2",
        "ACC3": "Sensor_3"
    },
    "data_correction": {
        "trim_time": {
            "process": false,
            "start_time": null,
            "end_time": null
        },
        "resample": {
            "process": false,
            "value": null,
            "method": "linear"
        },
        "shift_time": {
            "process": false,
            "value": null
        },
        "zero_start_y": {
            "process": false,
            "value": null
        },
        "reverse_y": {
            "process": false
        },
        "detrend": {
            "process": false,
            "type": "linear",
            "degree": 2
        },
        "derivative": {
            "process": false
        },
        "filter": {
            "process": false,
            "type": "none",
            "params": {}
        },
        "stretch_y": {
            "process": false,
            "value": null
        },
        "normilized": {
            "process": false
        },
        "zero_start_time": {
            "process": false
        }
    }
}
```

---

## Data Processing Workflow

### Processing Order

The corrections are applied in the following **strict order**:

1. **TRIM_TIME** - Select data range
2. **RESAMPLE** - Ensure uniform sampling
3. **SHIFT_TIME** - Apply time shift
4. **ZERO_START_Y** - Baseline correction
5. **REVERSE_Y** - Invert values
6. **DETREND** - Remove trend
7. **DERIVATIVE** - Calculate derivative
8. **FILTER** - Apply filtering
9. **STRETCH_Y** - Scale values
10. **NORMALIZE** - Normalize values
11. **ZERO_START_TIME** - Make time start at 0

### Excel Row/Column Reference

The API uses Excel-style references:
- **Rows**: 1-based indexing (Row 1 is the first row)
- **Columns**: Letter-based (A, B, C, ..., Z, AA, AB, ...)

```python
# Example: Reading data from Excel row 2-1000, columns A (time) and B-D (data)
config = {
    "start_row": 2,      # Excel row 2
    "end_row": 1000,     # Excel row 1000
    "time_column": "A",  # Column A
    "data": {
        "S1": "B",       # Column B
        "S2": "C",       # Column C
        "S3": "D"        # Column D
    }
}
```

---

## Data Corrections

### 1. Trim Time
Select a specific time range from the data while preserving dt.

```python
"trim_time": {
    "process": True,
    "start_time": 0.5,   # Start at 0.5 seconds
    "end_time": 10.0     # End at 10.0 seconds
}
```

**Notes:**
- Maintains uniform time spacing (dt)
- Useful for removing initial/final transients

### 2. Resample
Resample data to a uniform sampling rate.

```python
"resample": {
    "process": True,
    "value": 1000,           # Target sampling frequency in Hz
    "method": "linear"       # Interpolation method
}
```

**Available Methods:**
- `"linear"` - Linear interpolation (fastest)
- `"cubic"` - Cubic spline interpolation
- `"nearest"` - Nearest neighbor
- Other scipy.interpolate methods

**Notes:**
- Automatically updates `dt` in configuration
- Essential when combining data from different sources

### 3. Shift Time
Add or subtract a constant value to all time values.

```python
"shift_time": {
    "process": True,
    "value": -0.1        # Shift by -0.1 seconds
}
```

### 4. Zero Start Y
Remove DC offset by subtracting the average of the first n values.

```python
"zero_start_y": {
    "process": True,
    "value": 100         # Average first 100 points
}
```

**Notes:**
- Essential for removing sensor bias
- Use enough points to get stable average (typically 50-200)

### 5. Reverse Y
Multiply all values by -1 (invert signal).

```python
"reverse_y": {
    "process": True
}
```

**Use Cases:**
- Correct sensor orientation
- Match sign conventions

### 6. Detrend
Remove linear or polynomial trends from data.

```python
"detrend": {
    "process": True,
    "type": "linear",    # "linear" or "poly"
    "degree": 2          # Polynomial degree (for "poly" type)
}
```

**Types:**
- `"linear"` - Remove linear trend (drift)
- `"poly"` - Remove polynomial trend of specified degree

**Notes:**
- Applied using scipy.signal.detrend
- Useful for removing slow drifts

### 7. Derivative
Calculate numerical derivative using numpy.gradient.

```python
"derivative": {
    "process": True
}
```

**Notes:**
- Converts acceleration to velocity, velocity to displacement, etc.
- Uses central differences for better accuracy

### 8. Filter
Apply various digital filters to remove noise.

#### Butterworth Filter (Most Common)
```python
"filter": {
    "process": True,
    "type": "butterworth",
    "params": {
        "order": 4,              # Filter order
        "btype": "low",          # "low", "high", "band", "bandstop"
        "cutoff": 50,            # Cutoff frequency (Hz)
        "zero_phase": True       # Use filtfilt for zero-phase
    }
}
```

#### Band-Pass Filter
```python
"filter": {
    "process": True,
    "type": "butterworth",
    "params": {
        "order": 4,
        "btype": "band",
        "cutoff_low": 10,        # Lower cutoff (Hz)
        "cutoff_high": 100,      # Upper cutoff (Hz)
        "zero_phase": True
    }
}
```

#### Other IIR Filters
Available types: `"butterworth"`, `"chebyshev1"`, `"chebyshev2"`, `"elliptic"`, `"bessel"`

```python
# Chebyshev Type I (sharper rolloff, passband ripple)
"filter": {
    "process": True,
    "type": "chebyshev1",
    "params": {
        "order": 4,
        "btype": "low",
        "cutoff": 50,
        "rp": 1.0,               # Passband ripple (dB)
        "zero_phase": True
    }
}

# Elliptic (sharpest rolloff, both passband and stopband ripple)
"filter": {
    "process": True,
    "type": "elliptic",
    "params": {
        "order": 4,
        "btype": "low",
        "cutoff": 50,
        "rp": 1.0,               # Passband ripple (dB)
        "rs": 40.0,              # Stopband attenuation (dB)
        "zero_phase": True
    }
}
```

#### FIR Filter
```python
"filter": {
    "process": True,
    "type": "fir",
    "params": {
        "numtaps": 101,          # Number of filter taps (odd)
        "btype": "low",
        "cutoff": 50,
        "window": "hamming",     # Window function
        "zero_phase": True
    }
}
```

**Available Windows:** `"hamming"`, `"hanning"`, `"blackman"`, `"bartlett"`

#### Savitzky-Golay Filter (Smoothing)
```python
"filter": {
    "process": True,
    "type": "savgol",
    "params": {
        "window_length": 11,     # Must be odd
        "polyorder": 3           # Polynomial order
    }
}
```

#### Moving Average Filter
```python
"filter": {
    "process": True,
    "type": "moving_avg",
    "params": {
        "window_size": 11        # Window size
    }
}
```

### 9. Stretch Y
Multiply all values by a constant factor.

```python
"stretch_y": {
    "process": True,
    "value": 1.5         # Multiply by 1.5
}
```

### 10. Normalize
Divide all values by the maximum absolute value.

```python
"normilized": {
    "process": True
}
```

**Result:** All values will be in the range [-1, 1]

### 11. Zero Start Time
Shift time values so the first time point is exactly 0.

```python
"zero_start_time": {
    "process": True
}
```

---

## Data Export

### Export All Sensors

```python
# Export with default precision (14 decimal places)
reader.export_to_csv('output.csv')

# Export with custom precision and configuration file
reader.export_to_csv('output.csv', precision=6, export_config=True)
```

**Output:**
- `output.csv` - Processed data
- `output.json` - Updated configuration (if export_config=True)

### Export Selected Sensors

```python
# Export only specific sensors
selected = ['Acceleration_1', 'Acceleration_3']
reader.export_selected_sensors_to_csv(
    'selected_output.csv',
    sensor_names=selected,
    precision=10,
    export_config=True
)
```

### Export in Original Format

Replace data in the original CSV file structure:

```python
# Replace data in original file structure
reader.export_processed_data_in_original_format(
    'updated_original.csv',
    precision=14,
    export_config=True
)

# Or auto-generate filename (adds '_updated' suffix)
reader.export_processed_data_in_original_format()
```

**Notes:**
- Preserves header rows
- Maintains original column structure
- Truncates extra rows beyond processed data

---

## Visualization

### Basic Visualization

```python
# Simple plot
fig = reader.quick_visualize_sensor('Acceleration_1')
plt.show()

# Save plot
fig = reader.quick_visualize_sensor('Acceleration_1', save_path='plot.png')
```

### Advanced Visualization

```python
fig = reader.visualize_sensor(
    'Acceleration_1',
    title='Acceleration Time History',
    xlabel='Time (s)',
    ylabel='Acceleration (g)',
    figsize=(12, 6),
    plot_type='line',       # 'line' or 'scatter'
    colors='red',
    grid=True,
    legend=True,
    xlim=[0, 10],          # X-axis limits
    ylim=[-2, 2],          # Y-axis limits
    linewidth=2,           # Additional kwargs
    alpha=0.8
)
plt.show()
```

### Integration Visualization

```python
# Calculate and visualize integrals
fig = reader.visualize_integrals(
    'Acceleration_1',
    n=2,                   # Show up to 2nd integral
    initial=0.0
)
plt.show()
```

**Output:**
- Original signal
- 1st integral (velocity if input is acceleration)
- 2nd integral (displacement if input is acceleration)

---

## Advanced Features

### Adding Custom Sensors

**IMPORTANT:** Sensors can **only** be added when no data corrections are active.

```python
# Create time array and data
time, acc1 = reader.get_xy('Acceleration_1')
custom_data = acc1 * 2.0  # Example: scaled data

# Add new sensor
success = reader.add_sensor(
    name='Custom_Sensor',
    data=custom_data,
    column='E',            # Optional column letter
    no_override=True       # Prevent overwriting existing sensors
)

if success:
    # Now apply corrections to all sensors uniformly
    new_config = {
        "data_correction": {
            "filter": {
                "process": True,
                "type": "butterworth",
                "params": {"order": 4, "btype": "low", "cutoff": 50}
            }
        }
    }
    reader.update_config(new_config)
```

### Calculate Integrals

```python
# Get integrals programmatically
time, data, integrals = reader.calculate_integrals(
    'Acceleration_1',
    n=3,                   # Calculate up to 3rd integral
    initial=0.0
)

# Access individual integrals
velocity = integrals[0]        # 1st integral
displacement = integrals[1]    # 2nd integral
third_integral = integrals[2]  # 3rd integral
```

### Configuration Management

```python
# Export current configuration
config_dict = reader.export_config_to_dict()
reader.export_config_to_json('current_config.json')

# Update configuration
new_settings = {
    "data_correction": {
        "filter": {
            "process": True,
            "type": "butterworth",
            "params": {"order": 6, "btype": "low", "cutoff": 100}
        }
    }
}
reader.update_config(new_settings)

# Check processing log
reader.print_log()
```

### Get Sensor Information

```python
# List all available sensors
sensor_names = reader.get_sensor_names()
print(sensor_names)  # ['Acceleration_1', 'Acceleration_2', ...]

# Get summary statistics
summary = reader.get_summary()
for name, stats in summary.items():
    print(f"{name}:")
    print(f"  Original name: {stats['original_name']}")
    print(f"  First value: {stats['first_value']}")
    print(f"  Last value: {stats['last_value']}")
    print(f"  Min: {stats['min']}")
    print(f"  Max: {stats['max']}")

# Get specific sensor data
time, data = reader.get_xy('Acceleration_1')
```

---

## Filter Comparison Tools

### Compare Multiple Filters

```python
# Define filter configurations to compare
filter_configs = [
    {
        "name": "Butterworth 4th Order",
        "filter": {
            "type": "butterworth",
            "params": {
                "order": 4,
                "btype": "low",
                "cutoff": 50,
                "zero_phase": True
            }
        }
    },
    {
        "name": "Butterworth 6th Order",
        "filter": {
            "type": "butterworth",
            "params": {
                "order": 6,
                "btype": "low",
                "cutoff": 50,
                "zero_phase": True
            }
        }
    },
    {
        "name": "Savitzky-Golay",
        "filter": {
            "type": "savgol",
            "params": {
                "window_length": 21,
                "polyorder": 3
            }
        }
    },
    {
        "name": "FIR 101 Taps",
        "filter": {
            "type": "fir",
            "params": {
                "numtaps": 101,
                "btype": "low",
                "cutoff": 50,
                "window": "hamming",
                "zero_phase": True
            }
        }
    }
]

# Compare filters
results = reader.compare_filters(
    'Acceleration_1',
    filter_configs,
    reference_data=None,      # Use unfiltered data as reference
    num_dominant_peaks=5      # Identify top 5 frequency peaks
)
```

### Rank Filters

```python
# Define ranking criteria
ranking_criteria = {
    'rmse': {'weight': 2, 'goal': 'min'},         # Root mean square error
    'snr_db': {'weight': 1, 'goal': 'max'},       # Signal-to-noise ratio
    'correlation': {'weight': 1, 'goal': 'max'},  # Correlation with original
    'preservation_score': {'weight': 1, 'goal': 'max'}  # Peak preservation
}

# Rank filters
ranked_filters, scores = reader.rank_filters(results, ranking_criteria)

print("Filter Rankings:")
for i, filter_name in enumerate(ranked_filters, 1):
    print(f"{i}. {filter_name}: {scores[filter_name]:.4f}")
```

### Visualize Filter Comparison

```python
# Generate all comparison plots
figures = reader.visualize_filter_comparison(
    'Acceleration_1',
    results,
    output_dir='filter_comparison',
    plot_types=['time', 'frequency', 'fft', 'peaks', 'metrics']
)

# Display plots
for plot_type, fig in figures.items():
    plt.figure(fig.number)
    plt.show()
```

**Generated Plots:**
- **time**: Time domain comparison
- **frequency**: Frequency domain (Welch PSD) comparison
- **fft**: FFT magnitude spectrum with peak identification
- **peaks**: Peak preservation analysis
- **metrics**: Comparison of all metrics

### Generate Comprehensive Report

```python
# Generate HTML report with all plots and analyses
report_path = reader.generate_filter_report(
    'Acceleration_1',
    results,
    'filter_report',
    ranking_criteria=ranking_criteria
)

print(f"Report generated: {report_path}")
```

**Report Contents:**
- Filter rankings
- Time/frequency metrics comparison
- Frequency band analysis
- Dominant frequency preservation
- All visualization plots
- Individual filter details

### Understanding Filter Metrics

**Time Domain Metrics:**
- `mse`: Mean squared error
- `rmse`: Root mean squared error (lower is better)
- `mae`: Mean absolute error
- `max_abs_error`: Maximum absolute error
- `correlation`: Correlation coefficient (higher is better)
- `energy_ratio`: Ratio of filtered to original energy
- `snr_db`: Signal-to-noise ratio in dB (higher is better)

**Frequency Domain Metrics:**
- `low_band_ratio`: Power ratio in low frequency band (0-20 Hz)
- `mid_band_ratio`: Power ratio in mid frequency band (20-100 Hz)
- `high_band_ratio`: Power ratio in high frequency band (100+ Hz)

**Peak Preservation Metrics:**
- `preserved_peak_count`: Number of dominant peaks preserved
- `overall_preservation_score`: Combined score (0-1, higher is better)
- `peak_magnitude_ratios`: How well peak magnitudes are preserved
- `peak_frequency_shifts`: How much peak frequencies shifted

---

## Troubleshooting

### Common Errors

#### 1. "Required configuration parameter 'X' is missing"
**Solution:** Ensure all required parameters are in your configuration dictionary or JSON file.

#### 2. "Empty cell found at [Cell Reference]"
**Solution:** Check your CSV file for empty cells in the data range. Fill or remove empty cells.

#### 3. "Non-numeric data found at [Cell Reference]"
**Solution:** Ensure all data cells contain numeric values. Check for headers in the data range.

#### 4. "Data name 'X' not found in processed data"
**Solution:** Use `get_sensor_names()` to see available sensor names.

#### 5. "Cannot add sensor: data_correction is not empty"
**Solution:** Sensors can only be added when no corrections are active. Clear corrections first:
```python
config = reader.export_config_to_dict()
config["data_correction"] = {
    "trim_time": {"process": False},
    "resample": {"process": False},
    # ... set all to False
}
reader.update_config(config)
# Now add sensor
reader.add_sensor('New_Sensor', data)
```

### Debugging Tips

```python
# Check processing log
reader.print_log()

# Verify configuration
config = reader.export_config_to_dict()
print(json.dumps(config, indent=2))

# Check available sensors
print(reader.get_sensor_names())

# Verify data shape
time, data = reader.get_xy('Sensor_1')
print(f"Time points: {len(time)}")
print(f"Data points: {len(data)}")
print(f"Time range: {time[0]} to {time[-1]}")
```

---

## API Reference

### Class: ReplicaXSensorDataReader

#### Constructor
```python
ReplicaXSensorDataReader(config=None)
```

#### Configuration Methods
| Method | Description |
|--------|-------------|
| `load_config_from_json(json_file_path)` | Load configuration from JSON file |
| `load_config_from_dict(config_dict)` | Load configuration from dictionary |
| `export_config_to_json(json_file_path)` | Export configuration to JSON file |
| `export_config_to_dict()` | Export configuration as dictionary |
| `update_config(new_config)` | Update configuration and reprocess data |

#### Data Access Methods
| Method | Description |
|--------|-------------|
| `get_xy(data_name)` | Get time and data arrays for a sensor |
| `get_sensor_names()` | Get list of available sensor names |
| `get_summary()` | Get summary statistics for all sensors |

#### Data Processing Methods
| Method | Description |
|--------|-------------|
| `process_data()` | Process data with current configuration |
| `add_sensor(name, data, column, no_override)` | Add a custom sensor |

#### Export Methods
| Method | Description |
|--------|-------------|
| `export_to_csv(file_path, precision, export_config)` | Export all sensors |
| `export_selected_sensors_to_csv(file_path, sensor_names, precision, export_config)` | Export selected sensors |
| `export_processed_data_in_original_format(output_file_path, precision, export_config)` | Export in original format |

#### Visualization Methods
| Method | Description |
|--------|-------------|
| `visualize_sensor(sensor_name, **kwargs)` | Create customized plot |
| `quick_visualize_sensor(sensor_name, **kwargs)` | Quick plot with defaults |
| `visualize_integrals(sensor_name, n, initial)` | Visualize integrals |

#### Integration Methods
| Method | Description |
|--------|-------------|
| `calculate_integrals(sensor_name, n, initial)` | Calculate cumulative integrals |

#### Filter Comparison Methods
| Method | Description |
|--------|-------------|
| `compare_filters(sensor_name, filter_configs, reference_data, num_dominant_peaks)` | Compare multiple filters |
| `rank_filters(comparison_results, ranking_criteria)` | Rank filters by performance |
| `visualize_filter_comparison(sensor_name, comparison_results, output_dir, plot_types)` | Generate comparison plots |
| `generate_filter_report(sensor_name, comparison_results, output_dir, ranking_criteria)` | Generate HTML report |

#### Logging Methods
| Method | Description |
|--------|-------------|
| `print_log()` | Print processing log to console |
| `log_info(message)` | Add info message to log |
| `log_warning(message)` | Add warning to log |
| `log_error(message)` | Add error to log |

---

## Complete Example Workflow

```python
from replicaxlite import ReplicaXSensorDataReader
import matplotlib.pyplot as plt

# 1. Create reader and load configuration
reader = ReplicaXSensorDataReader()
reader.load_config_from_json('config.json')

# 2. Check available sensors
sensors = reader.get_sensor_names()
print(f"Available sensors: {sensors}")

# 3. Get summary statistics
summary = reader.get_summary()
for name, stats in summary.items():
    print(f"\n{name}:")
    print(f"  Range: [{stats['min']:.3f}, {stats['max']:.3f}]")

# 4. Apply additional corrections
new_config = {
    "data_correction": {
        "zero_start_time": {"process": True},
        "zero_start_y": {"process": True, "value": 100},
        "filter": {
            "process": True,
            "type": "butterworth",
            "params": {
                "order": 4,
                "btype": "low",
                "cutoff": 50,
                "zero_phase": True
            }
        }
    }
}
reader.update_config(new_config)

# 5. Visualize results
fig1 = reader.quick_visualize_sensor('Acceleration_1')
fig2 = reader.visualize_integrals('Acceleration_1', n=2)
plt.show()

# 6. Export processed data
reader.export_to_csv('processed_data.csv', precision=10, export_config=True)

# 7. Compare different filters
filter_configs = [
    {
        "name": "Butterworth 4th",
        "filter": {
            "type": "butterworth",
            "params": {"order": 4, "btype": "low", "cutoff": 50, "zero_phase": True}
        }
    },
    {
        "name": "Butterworth 6th",
        "filter": {
            "type": "butterworth",
            "params": {"order": 6, "btype": "low", "cutoff": 50, "zero_phase": True}
        }
    }
]

results = reader.compare_filters('Acceleration_1', filter_configs)
ranked, scores = reader.rank_filters(results)
reader.generate_filter_report('Acceleration_1', results, 'filter_report')

print(f"\nBest filter: {ranked[0]}")
reader.print_log()
```

---

## Appendix: License

```
ReplicaXLite - A finite element toolkit for creating, analyzing and monitoring 3D structural models
Copyright (C) 2024-2025 Vachan Vanian

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see <https://www.gnu.org/licenses/>.
```

---

**End of User Manual**