# ReplicaXSensorDataReader Analyzer - User Manual

## Table of Contents

1. [Introduction](#1-introduction)
2. [Getting Started](#2-getting-started)
3. [Main Window Overview](#3-main-window-overview)
4. [Loading and Managing Configurations](#4-loading-and-managing-configurations)
5. [Configuration Editor](#5-configuration-editor)
6. [Data Processing](#6-data-processing)
7. [Visualization](#7-visualization)
8. [Data Corrections](#8-data-corrections)
9. [Filter Comparison Tool](#9-filter-comparison-tool)
10. [Exporting Data](#10-exporting-data)
11. [Real-Time Updates](#11-real-time-updates)
12. [Tips and Best Practices](#12-tips-and-best-practices)
13. [Troubleshooting](#13-troubleshooting)

---

## 1. Introduction

### 1.1 What is ReplicaXSensorDataReader Analyzer?

ReplicaXSensorDataReader Analyzer is a graphical application designed for analyzing and processing sensor data from CSV files. The application provides comprehensive tools for:

- Loading and configuring sensor data files
- Applying various data corrections and filters
- Visualizing data in multiple formats
- Comparing different filter configurations
- Exporting processed data

### 1.2 Key Features

- **Flexible Configuration**: JSON-based configuration system
- **Multiple Data Corrections**: 11 different correction types
- **Advanced Filtering**: Support for various filter types (Butterworth, Chebyshev, FIR, Savitzky-Golay, etc.)
- **Filter Comparison**: Dedicated tool for comparing and ranking filter performance
- **Real-Time Updates**: Automatic data reloading and processing
- **Multiple Export Formats**: Export all data, selected sensors, or original format

---

## 2. Getting Started

### 2.1 Launching the Application

Run the application from the command line or by executing the main script. The main window will appear with the following sections:

- **Data Viewer Tab**: Main interface for data analysis
- **Configuration Editor Tab**: Direct JSON editing
- **Log Output**: Real-time feedback on operations

### 2.2 First Steps

1. **Load a Configuration**: Click "Load Configuration" or use File → Open Configuration (Ctrl+O)
2. **Review Settings**: Check the Configuration Summary panel
3. **Process Data**: Click "Process Data" or press F5
4. **View Results**: Explore the Combined Plot and Individual Plots tabs

---

## 3. Main Window Overview

### 3.1 Menu Bar

#### File Menu
- **Open Configuration** (Ctrl+O): Load a JSON configuration file
- **Save Configuration** (Ctrl+S): Save current configuration to JSON
- **Export Data**: Submenu with three export options
  - Export All Data
  - Export Selected Sensors
  - Export in Original Format
- **Exit** (Ctrl+Q): Close the application

#### Edit Menu
- **Edit Configuration**: Open the comprehensive configuration dialog
- **Data Correction Settings**: Jump directly to corrections tab
- **Units Settings**: Jump directly to units tab

#### Tools Menu
- **Process Data** (F5): Process/reprocess data with current settings
- **Filter Comparison**: Open the Filter Comparison Tool window
- **Clear Plots**: Remove all current visualizations
- **Reset Sensors** (Ctrl+R): Clear all data and reset the application state

#### Help Menu
- **About**: Display application information

### 3.2 Data Viewer Tab Layout

The Data Viewer is split into two main sections:

**Left Panel (Controls):**
- File Controls buttons
- Real-Time Update controls
- Configuration Summary display
- Sensor Selection checkboxes

**Right Panel (Visualization):**
- Combined Plot: All selected sensors overlaid
- Individual Plots: Separate subplot for each sensor

### 3.3 Log Output

The bottom section displays color-coded log messages:
- **INFO** (Magenta): General information
- **WARNING** (Orange): Warnings about potential issues
- **ERROR** (Red): Error messages
- **SUCCESS** (Green): Successful operations

---

## 4. Loading and Managing Configurations

### 4.1 Configuration File Structure

Configuration files are JSON format with the following main sections:

```json
{
  "file_path": "path/to/data.csv",
  "seperator": ",",
  "decimal": ".",
  "start_row": 1,
  "end_row": 1000,
  "dt": 0.001,
  "time_column": "A",
  "data_type": "Length",
  "input_units": {...},
  "output_units": {...},
  "data": {...},
  "data_name": {...},
  "data_correction": {...}
}
```

### 4.2 Loading a Configuration

**Method 1: File Dialog**
1. Click "Load Configuration" button
2. Navigate to your JSON file
3. Click "Open"

**Method 2: Menu Bar**
1. File → Open Configuration (Ctrl+O)
2. Select file and open

**Result:**
- Configuration Summary updates automatically
- Sensor Selection checkboxes populate
- Status bar shows loaded file path
- Process and Export buttons become enabled

### 4.3 Saving a Configuration

1. Make changes to your configuration
2. Click "Save Configuration" or File → Save Configuration (Ctrl+S)
3. Choose save location and filename
4. Click "Save"

**Note**: Configuration is saved in JSON format with proper indentation for readability.

---

## 5. Configuration Editor

### 5.1 Opening the Editor

**Access the editor through:**
- "Edit Configuration..." button in Data Viewer
- Edit → Edit Configuration from menu bar
- Direct tab access for specific sections (Corrections, Units)

### 5.2 Basic Settings Tab

Configure fundamental data file properties:

| Setting | Description | Example |
|---------|-------------|---------|
| **File Path** | Path to CSV data file | `/data/sensors.csv` |
| **Separator** | Column delimiter | `,` `;` `\t` ` ` `|` |
| **Decimal** | Decimal point character | `.` or `,` |
| **Start Row** | First row to read | `1` |
| **End Row** | Last row to read | `1000` |
| **Time Step (dt)** | Sampling interval (seconds) | `0.001` (1000 Hz) |
| **Time Column** | Column letter for time data | `A` |

**Tips:**
- Use "Browse..." to select files easily
- Start/End Row: Define the data range to process
- Time Step: Used if time column is empty or for resampling

### 5.3 Units Tab

Configure input and output units for proper data conversion:

**Data Type Selection:**
- Length, Velocity, Acceleration, Force, Pressure, Temperature, etc.

**Input Units:**
- Time unit (s, ms, μs, min, h, etc.)
- Data unit (depends on data type)

**Output Units:**
- Time unit for display and export
- Data unit for display and export

**Example Configuration:**
- Data Type: `Acceleration`
- Input: `g` (gravitational acceleration)
- Output: `m/s²` (meters per second squared)

### 5.4 Data Mapping Tab

Define which columns contain sensor data and their display names:

**Table Columns:**
1. **Original Name**: Internal identifier
2. **Column**: CSV column letter (A, B, C, etc.)
3. **Display Name**: Name shown in plots and exports

**Controls:**
- **Add Sensor**: Create a new sensor mapping
- **Remove Selected**: Delete selected sensor mapping

**Example:**
| Original Name | Column | Display Name |
|---------------|--------|--------------|
| sensor_1 | B | S1 |
| sensor_2 | C | North Wall |
| sensor_3 | D | Roof Center |

### 5.5 Data Corrections Tab

Configure the 11 data correction operations applied in numerical order:

#### Processing Order Note
**IMPORTANT**: Corrections are applied in the order listed (1→11). This order affects the final result.

---

#### 1. Trim Time Correction

Limit data to a specific time range.

- **Enable**: Checkbox to activate
- **Start Time**: Beginning of time range (s)
- **End Time**: End of time range (s)

**Use Case**: Remove initialization or shutdown periods.

---

#### 2. Resample Correction

Change the sampling rate of the data.

- **Enable**: Checkbox to activate
- **Rate (Hz)**: New sampling frequency
- **Method**: Interpolation method
  - `linear`: Linear interpolation
  - `cubic`: Cubic spline interpolation
  - `nearest`: Nearest neighbor

**Use Case**: Standardize sampling rates across different sensors or reduce data size.

---

#### 3. Shift Time Correction

Offset all time values by a constant amount.

- **Enable**: Checkbox to activate
- **Shift (s)**: Time offset (positive or negative)

**Use Case**: Synchronize data from multiple sources or align events.

---

#### 4. Zero Start Y Correction

Set the initial data value to zero by subtracting the average of initial points.

- **Enable**: Checkbox to activate
- **Points**: Number of initial points to average

**Use Case**: Remove DC offset or normalize to starting conditions.

---

#### 5. Reverse Y Correction

Multiply all data values by -1.

- **Enable**: Checkbox to activate

**Use Case**: Correct sensor polarity or orientation.

---

#### 6. Detrend Correction

Remove trend from data.

- **Enable**: Checkbox to activate
- **Type**: 
  - `linear`: Remove linear trend
  - `poly`: Remove polynomial trend
- **Degree**: Polynomial degree (only for poly type)

**Use Case**: Remove drift or long-term trends.

---

#### 7. Derivative Correction

Calculate the numerical derivative (rate of change).

- **Enable**: Checkbox to activate

**Use Case**: Convert displacement to velocity, or velocity to acceleration.

---

#### 8. Filter Correction

Apply a digital filter to the data.

- **Enable**: Checkbox to activate
- **Type**: Filter algorithm
  - `none`: No filtering
  - `butterworth`: Butterworth IIR filter
  - `chebyshev1`: Chebyshev Type I filter
  - `chebyshev2`: Chebyshev Type II filter
  - `elliptic`: Elliptic (Cauer) filter
  - `bessel`: Bessel filter
  - `fir`: Finite Impulse Response filter
  - `savgol`: Savitzky-Golay filter
  - `moving_avg`: Moving average filter
- **Parameters...**: Opens filter parameter dialog

**Filter Parameters Dialog:**

The parameters available depend on the selected filter type.

**For IIR Filters (Butterworth, Chebyshev, Elliptic, Bessel):**
- **Order**: Filter order (1-20)
- **Filter Mode**: 
  - `low`: Lowpass filter
  - `high`: Highpass filter
  - `band`: Bandpass filter
  - `bandstop`: Bandstop (notch) filter
- **Cutoff Frequency (Hz)**: For low/high pass
- **Low/High Cutoff (Hz)**: For band/bandstop filters
- **Zero-Phase Filtering**: Checkbox (eliminates phase distortion)

**Chebyshev Type I & Elliptic only:**
- **Passband Ripple (dB)**: Allowable ripple in passband (0.1-20)

**Chebyshev Type II & Elliptic only:**
- **Stopband Attenuation (dB)**: Minimum attenuation in stopband (10-120)

**For FIR Filter:**
- **Number of Taps**: Filter length (must be odd)
- **Window Type**: `hamming`, `hann`, `blackman`, `boxcar`, `kaiser`
- **Filter Mode**: low, high, band, bandstop
- **Cutoff Frequencies**: Same as IIR filters
- **Zero-Phase Filtering**: Checkbox

**For Savitzky-Golay Filter:**
- **Window Length**: Number of points (must be odd, ≥3)
- **Polynomial Order**: Degree of fitting polynomial (1-100)

**For Moving Average:**
- **Window Size**: Number of points to average (1-100000)

**Use Case**: Noise reduction, frequency band isolation, smoothing.

---

#### 9. Stretch Y Correction

Multiply all data values by a constant factor.

- **Enable**: Checkbox to activate
- **Factor**: Multiplication factor

**Use Case**: Apply calibration factors or scale adjustments.

---

#### 10. Normalize Correction

Scale data to range [0, 1] or [-1, 1].

- **Enable**: Checkbox to activate

**Use Case**: Compare sensors with different scales or units.

---

#### 11. Zero Start Time Correction

Subtract the first time value from all time points.

- **Enable**: Checkbox to activate

**Use Case**: Start time series from t=0.

---

### 5.6 Saving Configuration Changes

After making changes in any tab:

1. Click "Save Configuration" button at the bottom
2. Changes are immediately applied to the sensor data object
3. Configuration Summary updates automatically
4. Click "Process Data" to see the effects

---

## 6. Data Processing

### 6.1 Processing Workflow

1. **Load Configuration**: Ensure configuration is loaded
2. **Click Process Data**: Button in left panel or Tools → Process Data (F5)
3. **Monitor Log**: Watch Log Output for progress and any warnings
4. **View Results**: Check status bar for summary (e.g., "Processed 10000 data points for 5 sensors")

### 6.2 What Happens During Processing

The application performs the following steps:

1. **Load Raw Data**: Read CSV file according to configuration
2. **Apply Unit Conversions**: Convert from input units to output units
3. **Apply Corrections**: Execute enabled corrections in order (1→11)
4. **Update Display**: Refresh all plots and sensor selection
5. **Generate Log**: Display detailed processing information

### 6.3 Processing Status

**Status Bar Messages:**
- "Processing data..." - Operation in progress
- "Processed X data points for Y sensors" - Success
- "No configuration loaded" - Error, load config first
- "Failed to process data" - Error, check log for details

### 6.4 Reprocessing Data

You can reprocess data at any time:
- After changing corrections
- After modifying filter parameters
- After adjusting units
- To refresh from source file (if data has changed)

Simply click "Process Data" again. Previous results will be overwritten.

---

## 7. Visualization

### 7.1 Sensor Selection

**Checkbox Controls:**
- Each processed sensor has a checkbox in the left panel
- Check/uncheck to show/hide sensor in plots
- Changes update plots immediately

**Bulk Selection:**
- **Select All**: Check all sensors
- **Select None**: Uncheck all sensors

### 7.2 Combined Plot

**Features:**
- All selected sensors plotted on same axes
- Each sensor has unique color (automatically assigned)
- Legend shows sensor names
- Interactive matplotlib toolbar for zoom, pan, save

**Toolbar Functions:**
- **Home**: Reset view to original
- **Back/Forward**: Navigate zoom history
- **Pan**: Click and drag to move view
- **Zoom**: Click and drag rectangle to zoom
- **Configure**: Adjust subplot parameters
- **Save**: Export plot as image (PNG, PDF, SVG, etc.)

**Axes:**
- X-axis: Time (in configured output units)
- Y-axis: Data value (in configured output units)
- Title: "Combined Sensor Data"

### 7.3 Individual Plots

**Layout:**
- Grid arrangement (up to 4 rows)
- Each sensor in separate subplot
- Consistent colors with Combined Plot
- Shared toolbar for all plots

**Subplot Features:**
- **Title**: Sensor name (bold, in sensor color)
- **Statistics**: Min, Max, Mean values displayed in legend
- **Zero Line**: Horizontal line at y=0 (if data crosses zero)
- **Grid**: Major and minor grid lines
- **Auto-scaling**: Y-axis automatically scaled with 5% padding

**Enhanced Display:**
- Scientific notation for large/small numbers
- Professional styling with appropriate spacing
- Figure title shows data file name
- Synchronized axes for easy comparison

### 7.4 Plot Interactions

**Zoom:**
1. Click zoom button in toolbar
2. Click and drag to create zoom rectangle
3. Release to zoom in
4. Right-click to zoom out

**Pan:**
1. Click pan button in toolbar
2. Click and drag to move view
3. Works on both axes simultaneously

**Save Plot:**
1. Click save button in toolbar
2. Choose format (PNG recommended for screen, PDF for print)
3. Select location and filename
4. Click Save

---

## 8. Data Corrections

### 8.1 Recommended Correction Sequences

#### Sequence for Displacement Data

```
1. Trim Time → Remove unwanted time ranges
3. Shift Time → Synchronize with events
4. Zero Start Y → Remove initial offset
8. Filter → Remove noise (Butterworth lowpass)
11. Zero Start Time → Start from t=0
```

#### Sequence for Acceleration to Displacement

```
1. Trim Time → Define analysis window
4. Zero Start Y → Remove DC offset
6. Detrend → Remove any drift
8. Filter → Bandpass to isolate frequencies
7. Derivative → Integrate to velocity (run twice for displacement)
10. Normalize → Compare different sensors
```

### 8.2 Filter Selection Guide

| Filter Type | Best For | Advantages | Disadvantages |
|-------------|----------|------------|---------------|
| **Butterworth** | General purpose | Flat passband, smooth rolloff | Moderate rolloff |
| **Chebyshev I** | Sharp cutoff needed | Very steep rolloff | Passband ripple |
| **Chebyshev II** | Sharp cutoff with flat passband | Flat passband, steep rolloff | Stopband ripple |
| **Elliptic** | Sharpest cutoff | Steepest rolloff for given order | Ripple in both bands |
| **Bessel** | Preserve waveform | Linear phase, no overshoot | Gentle rolloff |
| **FIR** | Phase critical | Exact linear phase | Requires more taps |
| **Savitzky-Golay** | Smoothing with feature preservation | Preserves peaks and valleys | Not for frequency filtering |
| **Moving Average** | Simple smoothing | Fast, simple | Severe frequency distortion |

### 8.3 Filter Parameter Guidelines

**Cutoff Frequency Selection:**
- **Lowpass**: Set just above highest frequency of interest
- **Highpass**: Set just below lowest frequency of interest
- **Bandpass**: Set to bracket frequency range of interest
- **Rule of Thumb**: For noise removal, cutoff at 2-3× signal bandwidth

**Filter Order:**
- **Lower Order (2-4)**: Gentle rolloff, minimal phase distortion
- **Medium Order (4-8)**: Good balance for most applications
- **Higher Order (8-12)**: Sharp rolloff, but risk of instability

**Zero-Phase Filtering:**
- **Enabled**: No phase distortion (recommended for most cases)
- **Disabled**: Real-time applications, causal filtering needed
- **Note**: Zero-phase doubles the effective filter order

**Savitzky-Golay Parameters:**
- **Window Length**: Larger = more smoothing (must be odd)
- **Polynomial Order**: Usually 2-4; higher preserves peaks better
- **Rule**: Window length > polynomial order + 1

---

## 9. Filter Comparison Tool

### 9.1 Opening the Tool

Access through: **Tools → Filter Comparison**

**Prerequisites:**
- Configuration must be loaded
- Data must be processed (click Process Data first)

### 9.2 Tool Window Layout

**Left Panel (Configuration):**
- Sensor selection dropdown
- Ranking criteria with weights
- Filter configuration list
- Preset buttons

**Right Panel (Results):**
- Summary tab with rankings
- Metrics comparison table
- Frequency band analysis
- Time/frequency domain plots
- FFT analysis
- Peak preservation analysis

### 9.3 Configuring a Comparison

#### Step 1: Select Sensor
Choose which sensor to analyze from dropdown menu.

#### Step 2: Set Ranking Criteria

Select metrics to use for ranking:

| Metric | Description | Goal | Weight |
|--------|-------------|------|--------|
| **RMSE** | Root Mean Square Error vs. original | Minimize | 0.1-10.0 |
| **MAE** | Mean Absolute Error vs. original | Minimize | 0.1-10.0 |
| **SNR (dB)** | Signal-to-Noise Ratio | Maximize | 0.1-10.0 |
| **Correlation** | Correlation with original signal | Maximize | 0.1-10.0 |
| **Energy Ratio** | Ratio of signal energies | Maximize | 0.1-10.0 |
| **Peak Preservation** | How well peaks are maintained | Maximize | 0.1-10.0 |

**Weight Guidelines:**
- Default: 1.0 for all selected metrics
- Higher weight = more importance in ranking
- Recommended: Check 3-4 metrics most relevant to your analysis

#### Step 3: Add Filter Configurations

**Manual Addition:**
1. Click "Add Filter" button
2. Enter descriptive name
3. Select filter type
4. Configure parameters
5. Click OK

**Using Presets:**

**"Add Common Filters"** - Adds a diverse set of filters:
- Butterworth LP 10Hz (4th order)
- Moving Average (window=11)
- Savitzky-Golay (window=21, poly=3)
- Chebyshev-I LP 10Hz (4th order)
- FIR LP 10Hz (101 taps, Hamming window)

**"Add Butterworth Variations"** - Adds Butterworth parameter sweep:
- Different orders: 2nd, 4th, 8th
- Different cutoffs: 5Hz, 10Hz, 20Hz
- Different types: Lowpass, Highpass, Bandpass (5-20Hz)

**Managing Filters:**
- **Edit Selected**: Modify parameters of selected filter
- **Remove Selected**: Delete selected filter
- **Clear All Filters**: Remove all configurations

**Minimum Requirement:** At least 2 filter configurations needed for comparison.

### 9.4 Running the Comparison

1. Ensure at least 2 filters are configured
2. Click "Run Comparison" (green button)
3. Wait for progress dialog
4. Results appear automatically in tabs

**Progress Steps:**
1. Analyzing filters... (10%)
2. Comparing filters... (50%)
3. Ranking filters... (70%)
4. Generating visualizations... (90%)
5. Updating display... (100%)

### 9.5 Understanding Results

#### Summary Tab

**Rankings Table:**
| Rank | Filter | Score |
|------|--------|-------|
| 1 | Best Filter | 0.9234 |
| 2 | Second Best | 0.8756 |
| ... | ... | ... |

- **Green background**: Best filter (Rank 1)
- **Yellow background**: Second best (Rank 2)
- **Scores**: Higher is better (0.0 - 1.0 scale)

#### Metrics Tab

Detailed comparison of time-domain metrics:

- **RMSE**: Lower values = closer to original (green if <1.0)
- **SNR (dB)**: Higher values = better quality (green if >40 dB)
- **Correlation**: Higher values = better match (green if >0.99)
- **Energy Ratio**: Closer to 1.0 = better preservation (green if 0.95-1.05)

**Color Coding:**
- Green text: Good performance
- Red text: Poor performance
- Green background: Best overall filter

#### Frequency Band Analysis Tab

Shows how each filter affects different frequency ranges:

- **Low Band Ratio**: Energy preservation in low frequencies
- **Mid Band Ratio**: Energy preservation in mid frequencies
- **High Band Ratio**: Energy preservation in high frequencies

**Interpretation:**
- Values near 1.0: Frequency band preserved
- Values near 0.0: Frequency band suppressed
- Use for understanding filter frequency selectivity

#### Time Domain Plot

Overlays all filtered signals with original:
- Original signal typically in one color
- Each filtered result in different color
- Legend identifies each filter
- Zoom to examine differences in detail

#### Frequency Domain Plot

Power spectral density comparison:
- Shows frequency content of each filtered signal
- Identify which frequencies are preserved/removed
- Useful for comparing lowpass/highpass characteristics

#### FFT Analysis Plot

Detailed frequency spectrum:
- Magnitude vs. frequency for each filter
- Direct comparison of frequency response
- Identify cutoff frequencies and rolloff characteristics

#### Peak Preservation Plot

Compares detection and preservation of peaks:
- Shows how well filters maintain important signal features
- Critical for applications where peaks represent events
- Overlay of original and filtered peak locations

### 9.6 Exporting Results

1. Review all results tabs
2. Click "Export Report" button
3. Select directory for output
4. Report includes:
   - HTML summary with rankings and metrics
   - All plots as high-resolution PNG files
   - CSV files with detailed metrics
   - JSON file with comparison configuration

**Output Structure:**
```
output_directory/
├── filter_comparison_report.html
├── time_domain_comparison.png
├── frequency_domain_comparison.png
├── fft_analysis.png
├── peak_preservation.png
├── metrics_comparison.csv
└── comparison_config.json
```

### 9.7 Filter Comparison Best Practices

**1. Start with Presets**
- Use "Add Common Filters" to get baseline comparison
- Add specific filters based on your requirements

**2. Systematic Parameter Variation**
- Vary one parameter at a time
- Use "Add Butterworth Variations" as template

**3. Appropriate Ranking Criteria**
- **For noise removal**: Enable RMSE, SNR, Correlation
- **For frequency isolation**: Enable Energy Ratio, Frequency Band metrics
- **For feature preservation**: Enable Peak Preservation, Correlation

**4. Interpret in Context**
- Best filter depends on your specific application
- Rank 1 is "best" by selected criteria only
- Review all plots, not just rankings

**5. Document Results**
- Export report for future reference
- Note which filter and parameters work best
- Use these settings in main configuration

---

## 10. Exporting Data

### 10.1 Export Options

Three export modes available:

#### 1. Export All Data

Exports all processed sensors to a single CSV file.

**File Structure:**
```
Time,Sensor1,Sensor2,Sensor3,...
0.000,0.123,0.456,0.789,...
0.001,0.124,0.457,0.790,...
...
```

**Use Case**: Complete dataset for external analysis.

#### 2. Export Selected Sensors

Exports only checked sensors to CSV.

**Dialog Options:**
- Checkbox list of all sensors
- Select All / Select None buttons
- Only checked sensors included in export

**Use Case**: Focus on specific sensors, reduce file size.

#### 3. Export in Original Format

Exports data matching the original CSV structure.

**Features:**
- Uses original column arrangement
- Includes original sensor names (or configured names)
- Maintains original separator and decimal characters
- Applies unit conversions and corrections

**Use Case**: Replace original data with processed version, maintain compatibility with other tools.

### 10.2 Export Configuration

**Common Options (all export modes):**

**Decimal Precision:**
- Range: 1-16 digits
- Default: 6 digits
- Higher precision for scientific applications

**Export Configuration File:**
- Checkbox option (checked by default)
- Saves JSON configuration alongside CSV
- Configuration file named: `<output_name>_config.json`
- Enables exact reproduction of processing

**Output Path:**
- Use "Browse..." to select location
- File extension: `.csv`
- Overwrites existing file (with confirmation)

### 10.3 Export Workflow

1. **Process Data First**: Ensure data is processed
2. **Select Export Type**: 
   - Click dropdown on "Export Data" button, OR
   - Use File → Export Data menu
3. **Configure Options**: 
   - In dialog, set precision
   - Select sensors (if Export Selected)
   - Choose export config option
4. **Choose Output Path**: Click "Browse..." and select location
5. **Click Export**: Data is written to file
6. **Verify Success**: Check log for confirmation message

### 10.4 Export Tips

**File Organization:**
```
project/
├── raw_data/
│   └── sensors_raw.csv
├── processed_data/
│   ├── sensors_processed.csv
│   └── sensors_processed_config.json
└── analysis/
    ├── selected_sensors.csv
    └── selected_sensors_config.json
```

**Best Practices:**
- Include date/time in filename: `sensors_2024-01-15_processed.csv`
- Always export configuration file for reproducibility
- Use appropriate precision (6-8 digits usually sufficient)
- Verify exported data in external tool before deleting originals

---

## 11. Real-Time Updates

### 11.1 Real-Time Update Feature

Automatically reloads and reprocesses data at regular intervals.

**Use Cases:**
- Monitoring live sensor feeds
- Watching data files that are being written
- Automatic refresh during long-term measurements

### 11.2 Activating Real-Time Updates

**Location**: Left panel under "Real-Time Update" group

**Controls:**
1. **Start/Stop Button**: Toggle real-time updates on/off
2. **Interval (s)**: Set update frequency (0.1 - 60.0 seconds)

**Activation Steps:**
1. Ensure configuration is loaded and data processed at least once
2. Set desired update interval (default: 1.0 second)
3. Click "Start Real-Time Update"
4. Button text changes to "Stop Real-Time Update"
5. Data reprocesses automatically at each interval

### 11.3 During Real-Time Updates

**What Happens:**
- Data file is reloaded from disk
- All corrections reapplied
- Plots automatically update
- Log shows each update cycle
- Status bar updates with new data point count

**Visual Feedback:**
- Button shows "Stop Real-Time Update" when active
- Log messages appear with each update
- Plots animate with new data

**Performance:**
- Update interval determines refresh rate
- Shorter intervals = more CPU usage
- Longer intervals = less responsive but lower overhead

### 11.4 Stopping Real-Time Updates

**Methods:**
1. Click "Stop Real-Time Update" button
2. Close the application
3. Load a new configuration (automatic stop)
4. Use Tools → Reset Sensors (automatic stop)

**Behavior After Stop:**
- Button returns to "Start Real-Time Update"
- Last processed data remains displayed
- Can restart at any time

### 11.5 Real-Time Update Best Practices

**Interval Selection:**
- **Fast updates (0.1-0.5s)**: Real-time monitoring, small files
- **Medium updates (1-5s)**: Standard monitoring, moderate files
- **Slow updates (10-60s)**: Long-term monitoring, large files

**System Considerations:**
- Large files + short interval = high CPU usage
- Multiple corrections + short interval = potential lag
- Monitor system performance and adjust accordingly

**Data File Requirements:**
- File must be accessible and unlocked
- Writing process should not lock file
- Consider using append-only writes to avoid conflicts

### 11.6 Troubleshooting Real-Time Updates

**Updates Not Reflecting Changes:**
- Ensure file is being updated on disk
- Check file timestamp changes
- Verify no file locking by other applications

**Performance Issues:**
- Increase update interval
- Reduce end_row in configuration
- Disable unnecessary corrections

**Errors During Updates:**
- Check log output for specific errors
- Verify file format hasn't changed
- Ensure file permissions allow reading

---

## 12. Tips and Best Practices

### 12.1 Configuration Management

**Version Control:**
- Save configuration with descriptive names: `sensor_analysis_v1.json`
- Document changes in commit messages or separate notes
- Keep backup copies of working configurations

**Configuration Templates:**
Create template configurations for common scenarios:
- `template_acceleration_analysis.json`
- `template_displacement_monitoring.json`
- `template_vibration_study.json`

**Parameter Documentation:**
Add comments to your external notes about:
- Why specific filter parameters were chosen
- Meaning of sensor names
- Expected data ranges
- Special conditions or events

### 12.2 Data Analysis Workflow

**Recommended Workflow:**

1. **Initial Exploration**
   - Load configuration with minimal corrections
   - Process and visualize raw data
   - Identify issues (noise, drift, offsets)

2. **Correction Development**
   - Enable corrections one at a time
   - Process after each addition
   - Verify expected behavior

3. **Filter Optimization**
   - Use Filter Comparison Tool
   - Test multiple filter configurations
   - Select best filter based on objective metrics

4. **Final Processing**
   - Apply optimal settings to all sensors
   - Export processed data
   - Save configuration for future reference

5. **Validation**
   - Verify exported data in external tool
   - Check critical values (peaks, means, etc.)
   - Confirm units are correct

### 12.3 Performance Optimization

**For Large Files:**
- Use start_row and end_row to limit data range
- Increase resample rate to reduce points
- Process in sections if necessary

**For Many Sensors:**
- Deselect unused sensors in visualization
- Export selected sensors only
- Use Individual Plots for detailed examination

**For Complex Corrections:**
- Disable corrections during exploration
- Enable only necessary corrections
- Use simpler filters when possible

### 12.4 Quality Assurance

**Pre-Processing Checks:**
- ✓ Correct separator and decimal settings
- ✓ Appropriate start/end rows
- ✓ Valid time column
- ✓ All sensor columns exist

**Post-Processing Validation:**
- ✓ Data range is reasonable
- ✓ No NaN or infinite values
- ✓ Filter removed noise without excessive smoothing
- ✓ Units are correct
- ✓ Time axis is continuous

**Before Export:**
- ✓ All corrections applied as intended
- ✓ Correct sensors selected
- ✓ Appropriate decimal precision
- ✓ Configuration file included
- ✓ Output filename is descriptive

---

## 13. Troubleshooting

### 13.1 Common Issues and Solutions

#### Issue: "No configuration loaded" Error

**Symptoms:**
- Cannot process data
- Export button disabled
- Empty sensor selection

**Solutions:**
1. Load a configuration file (File → Open Configuration)
2. Create new configuration (Edit → Edit Configuration)
3. Check that JSON file is valid format

---

#### Issue: "Failed to process data" Error

**Symptoms:**
- Error message in log
- No plots displayed
- Red error messages

**Possible Causes & Solutions:**

**Cause: File not found**
- Check file_path in configuration
- Verify file exists and is accessible
- Use absolute paths, not relative

**Cause: Incorrect separator or decimal**
- Verify separator matches CSV file (`,` `;` etc.)
- Check decimal character (`.` or `,`)
- Open CSV in text editor to confirm format

**Cause: Invalid column references**
- Ensure time_column exists (A, B, C, ...)
- Verify all sensor columns exist
- Check that start_row/end_row are valid

**Cause: Insufficient data points**
- Check that end_row > start_row
- Verify file has enough rows
- Reduce start_row or increase end_row

---

#### Issue: Filter Comparison Tool Won't Open

**Symptoms:**
- Menu option doesn't respond
- Warning: "No Data"

**Solutions:**
1. Load configuration first
2. Click "Process Data" button (F5)
3. Wait for processing to complete
4. Try opening filter comparison again

---

#### Issue: Real-Time Updates Not Working

**Symptoms:**
- Data doesn't refresh
- Button stuck in one state
- No log messages during updates

**Solutions:**
1. Stop and restart real-time updates
2. Verify file is being modified (check timestamp)
3. Ensure file is not locked by another program
4. Increase update interval
5. Check log for specific error messages

---

#### Issue: Plots Not Updating

**Symptoms:**
- Old data still displayed
- Sensor selection changes ignored
- Process Data doesn't refresh plots

**Solutions:**
1. Click "Clear Plots" (Tools menu)
2. Process data again (F5)
3. Restart application if persists
4. Check that sensors are selected (checkboxes)

---

#### Issue: Export Fails

**Symptoms:**
- "No Data" warning
- Cannot write to file error
- Missing output file

**Solutions:**

**No processed data:**
- Process data first (F5)
- Verify configuration loaded

**Write permission error:**
- Check output directory is writable
- Close file if open in another program
- Choose different output location

**Invalid path:**
- Use "Browse..." instead of typing
- Avoid special characters in filename
- Ensure directory exists

---

#### Issue: Incorrect Data Units

**Symptoms:**
- Values seem scaled wrong
- Units don't match expected
- Magnitude orders of magnitude off

**Solutions:**
1. Open Edit → Units Settings
2. Verify Data Type is correct
3. Check Input Units match source data
4. Confirm Output Units are desired
5. Reprocess data after corrections

---

#### Issue: Filter Parameters Not Saving

**Symptoms:**
- Parameters revert after closing dialog
- Filter doesn't apply correctly
- Unexpected filter behavior

**Solutions:**
1. Click "OK" in parameter dialog (not X button)
2. Verify "Enable" checkbox is checked
3. Save configuration after changes
4. Check parameters are valid for filter type
5. For band filters, ensure cutoff_low < cutoff_high

---

### 13.2 Log Interpretation

**Common Log Messages:**

| Message | Meaning | Action |
|---------|---------|--------|
| "Configuration loaded successfully" | Config OK | Proceed to processing |
| "Processing data..." | Operation started | Wait for completion |
| "Data processed successfully" | Success | View results |
| "File not found" | Path error | Check file_path |
| "Invalid configuration" | JSON error | Fix config format |
| "Warning: High filter order" | Potential instability | Reduce order or verify intent |
| "Applied correction: [name]" | Correction executed | Verify expected result |

### 13.3 Getting Help

**Before Reporting Issues:**

1. **Check Log Output**: Look for specific error messages
2. **Verify Configuration**: Ensure JSON is valid
3. **Test with Simple Config**: Isolate the problem
4. **Try Minimal Corrections**: Disable corrections one by one
5. **Export Configuration**: Save current settings for reference

**When Reporting Issues, Include:**
- Error messages from log (copy/paste)
- Configuration file (JSON)
- Sample of input data (first few rows)
- Steps to reproduce
- Expected vs. actual behavior

---

## Appendix A: Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| Ctrl+O | Open Configuration |
| Ctrl+S | Save Configuration |
| Ctrl+Q | Exit Application |
| F5 | Process Data |
| Ctrl+R | Reset Sensors |

---

## Appendix B: File Formats

### Configuration File (.json)

JSON format with the following structure:

```json
{
  "file_path": "string",
  "seperator": "string (1 char)",
  "decimal": "string (1 char)",
  "start_row": "integer",
  "end_row": "integer",
  "dt": "float",
  "time_column": "string",
  "data_type": "string",
  "input_units": {
    "time": "string",
    "data": "string"
  },
  "output_units": {
    "time": "string",
    "data": "string"
  },
  "data": {
    "sensor_id": "column_letter"
  },
  "data_name": {
    "sensor_id": "display_name"
  },
  "data_correction": {
    "trim_time": {...},
    "resample": {...},
    ...
  }
}
```

### Export CSV Format

**Export All Data / Selected Sensors:**
```csv
Time,Sensor1,Sensor2,...
0.000000,1.234567,2.345678,...
0.001000,1.234890,2.346789,...
...
```

**Export Original Format:**
Matches original CSV structure with processed values.

---

## Appendix C: Supported Units

### Time Units
s, ms, μs, ns, min, h, day, week, month, year

### Length Units
m, cm, mm, μm, nm, km, in, ft, yd, mi

### Velocity Units
m/s, cm/s, mm/s, km/h, mph, ft/s, knot

### Acceleration Units
m/s², cm/s², g, ft/s²

### Force Units
N, kN, MN, lbf, kip, dyn

### Pressure Units
Pa, kPa, MPa, GPa, bar, mbar, psi, ksi, atm, Torr, mmHg

### Temperature Units
°C, K, °F, °R

---

## Appendix D: Filter Comparison Metrics

### RMSE (Root Mean Square Error)
Measures average magnitude of error between filtered and original signal.

**Formula:** `sqrt(mean((y_filtered - y_original)²))`

**Interpretation:** Lower is better (closer to original)

### SNR (Signal-to-Noise Ratio)
Ratio of signal power to noise power, in decibels.

**Formula:** `10 * log10(signal_power / noise_power)`

**Interpretation:** Higher is better (more signal, less noise)

### Correlation
Pearson correlation coefficient between filtered and original.

**Range:** -1 to 1

**Interpretation:** Closer to 1 is better (perfect positive correlation)

### Energy Ratio
Ratio of filtered signal energy to original signal energy.

**Formula:** `sum(y_filtered²) / sum(y_original²)`

**Interpretation:** Closer to 1.0 is better (energy preserved)

### Peak Preservation
Measures how well filter maintains peak locations and magnitudes.

**Components:**
- Peak detection correlation
- Peak magnitude preservation
- Peak timing accuracy

**Interpretation:** Higher is better (peaks maintained)

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
