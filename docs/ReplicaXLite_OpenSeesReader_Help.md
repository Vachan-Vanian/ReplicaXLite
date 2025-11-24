# ReplicaXRecorderReader User Manual

## Table of Contents
1. [Introduction](#introduction)
2. [Getting Started](#getting-started)
3. [User Interface Overview](#user-interface-overview)
4. [Working with Data Files](#working-with-data-files)
5. [Table Operations](#table-operations)
6. [Unit Management](#unit-management)
7. [Plot Configuration](#plot-configuration)
8. [Advanced Features](#advanced-features)
9. [Keyboard Shortcuts](#keyboard-shortcuts)
10. [Workflows and Examples](#workflows-and-examples)
11. [Troubleshooting](#troubleshooting)

---

## 1. Introduction

### About ReplicaXRecorderReader

ReplicaXRecorderReader is a specialized data analysis tool designed for finite element structural analysis results. It provides comprehensive capabilities for:

- Reading and displaying tabular recorder data (.out and .dat files)
- Managing unit conversions across different measurement systems
- Configuring and generating multiple plots with custom transformations
- Combining data from multiple analysis runs
- Saving and loading analysis configurations

### Key Features

- **Unit-aware data handling** with automatic conversion between unit systems
- **Flexible plotting** with data transformations, scaling, and filtering
- **Metadata persistence** through JSON configuration files
- **Batch operations** for combining multiple data files
- **Interactive tables** with copy/paste and keyboard shortcuts

---

## 2. Getting Started

### First Launch

When you first launch ReplicaXRecorderReader:

1. The application window opens with a status bar showing "No file opened"
2. All tabs except the menu bar are disabled until you open a file
3. The window is resizable (default: 1200×800 pixels)

### Opening Your First File

1. Click **File → Open File** or use the menu bar
2. Select a recorder file (`.out` or `.dat` format)
3. The application loads the data and enables all interface tabs
4. The status bar updates to show the current file path

**Supported File Formats:**
- `.out` files (OpenSees recorder output)
- `.dat` files (generic data files)
- Space-delimited numerical data

---

## 3. User Interface Overview

### Main Window Components

The application consists of five main tabs:

#### Tab 1: Table Data
Displays raw data as loaded from the file with default units. This is your original, unmodified dataset.

#### Tab 2: Plot Data
Shows the same data converted to plotting units as specified in Unit Management. Values are automatically recalculated when you change plot units.

#### Tab 3: Unit Management
Configure units for each column including:
- Column names
- Unit types (Length, Force, Stress, etc.)
- Default units (units in the original file)
- Plot units (units for display and plotting)

#### Tab 4: Set Plots
Define plot configurations including:
- Data columns for X and Y axes
- Row ranges to include
- Custom labels and titles
- Data transformations (scaling, offsets, thresholds)

#### Tab 5: Plots
Displays generated plots based on Set Plots configurations. Includes matplotlib navigation toolbar for zooming, panning, and saving.

### Status Bar

The status bar at the bottom displays the currently opened file path, helping you track which dataset you're working with.

---

## 4. Working with Data Files

### Opening Files

**Method 1: File Menu**
1. Navigate to **File → Open File**
2. Browse to your data file
3. Select and click Open

**Supported formats:** `.out`, `.dat`, or any space-delimited numerical file

**What happens on open:**
- Data is loaded into both Table Data and Plot Data tabs
- Default column headers are generated as "Column 1 [Unitless]", "Column 2 [Unitless]", etc.
- Unit Management table is populated with default settings
- One default plot configuration is created
- All plots are reset if a previous file was open

### Saving with Metadata

Metadata includes unit configurations and plot settings, saved as JSON alongside your data file.

**To save:**
1. Click **File → Save with Metadata**
2. A JSON file is created with the same name as your data file (e.g., `data.out` → `data.json`)

**Metadata contents:**
- Original data file name
- Unit management settings (column names, unit types, conversions)
- Plot configurations (axes, ranges, labels, transformations)

**Note:** You must have a file open to save metadata.

### Loading with Metadata

Restore both data and configuration from a previous session.

**To load:**
1. Click **File → Load with Metadata**
2. Select a JSON metadata file
3. The application automatically loads the corresponding data file
4. All unit and plot configurations are restored

**Requirements:**
- JSON file must be in the same directory as the data file
- The `data_file_name` field in JSON must match an existing file

---

## 5. Table Operations

### Keyboard Shortcuts

Both Table Data and Plot Data tabs support these shortcuts:

| Shortcut | Action |
|----------|--------|
| **Ctrl + +** | Add a single row after the current selection |
| **Ctrl + Shift + +** | Import multiple rows (prompts for count) |
| **Ctrl + -** | Remove the currently selected row |
| **Ctrl + Shift + -** | Remove all selected rows |
| **Ctrl + C** | Copy selection to clipboard |
| **Ctrl + V** | Paste from clipboard |
| **Delete** | Clear contents of selected cells |

### Selection Modes

**Single Cell:** Click on any cell to select it

**Multiple Rows:** 
- Click on row header to select entire row
- Shift + Click on another row header to select a range

**Multiple Columns:**
- Click on column header to select entire column
- Shift + Click on another column header to select a range

**Contiguous Block:**
- Click and drag across cells
- Or click first cell, then Shift + Click last cell

### Copy and Paste

**Copying:**
- Select cells, rows, or columns
- Press **Ctrl + C**
- Data is copied as tab-delimited text

**Pasting:**
- Click the top-left cell where you want to paste
- Press **Ctrl + V**
- Tab-delimited data is pasted, creating new cells if needed

**Compatibility:** Works with Excel, Google Sheets, and other spreadsheet applications.

### Adding Rows

**Add Single Row:**
1. Select a row (the new row will be inserted after it)
2. Press **Ctrl + +**
3. If no row is selected, the row is added at the end

**Import Multiple Rows:**
1. Press **Ctrl + Shift + +**
2. Enter the number of rows to add in the dialog
3. Rows are inserted after the current selection

### Removing Rows

**Remove Single Row:**
1. Select the row to remove
2. Press **Ctrl + -**

**Remove Multiple Rows:**
1. Select multiple rows using Shift + Click
2. Press **Ctrl + Shift + -**
3. All selected rows are removed at once

---

## 6. Unit Management

### Understanding the Unit System

The application distinguishes between:
- **Default Units:** The units in your original data file
- **Plot Units:** The units you want to use for visualization

Data values are stored in default units but displayed and plotted in plot units.

### Configuring Units

Navigate to the **Unit Management** tab to see four columns:

#### Column 1: Column Name
- Edit to change the display name
- Affects headers in all tabs
- Default format: "Column N"

#### Column 2: Unit Type
Dropdown menu with options:
- Unitless (no conversion)
- Length
- Force
- Stress
- Pressure
- Time
- Mass
- And other physical quantity types

#### Column 3: Default Units
- Specifies what units the data file contains
- Changes based on Unit Type selection
- Examples: meters, inches, kN, MPa

#### Column 4: Plot Units
- Specifies units for plotting and display
- Independent of default units
- Conversion happens automatically

### Unit Conversion

**How it works:**
1. Select Unit Type (e.g., "Length")
2. Set Default Units (e.g., "meters")
3. Set Plot Units (e.g., "inches")
4. Plot Data tab automatically shows converted values
5. Original data in Table Data tab remains unchanged

**Available conversions depend on the Unit Type selected.** The application uses the ReplicaXUnits system for accurate conversions.

### Editing Column Names

1. Click in the Column Name cell
2. Type the new name
3. Press Enter
4. Headers update immediately in all tabs

**Example:** Change "Column 1" to "Displacement" for clarity.

### Header Format

Headers display as: `[Column Name] [Units]`

**Examples:**
- "Displacement [inches]"
- "Force [kN]"
- "Time [seconds]"
- "Column 5 [Unitless]"

---

## 7. Plot Configuration

### Set Plots Tab

This tab defines all plots to be generated. Each row represents one plot.

### Plot Configuration Fields

#### X Data and Y Data (Columns 1-2)
Dropdown menus listing all available columns from your data table.
- Select which column provides X-axis data
- Select which column provides Y-axis data

#### Start Row and End Row (Columns 3-4)
Spinbox controls to define the data range:
- **Start Row:** First data row to include (0-indexed)
- **End Row:** Last data row to include
- Default: All rows (0 to maximum)

**Use case:** Focus on specific time ranges or load steps.

#### X Label, Y Label, Title (Columns 5-7)
Text fields for plot annotations:
- **X Label:** Horizontal axis label (defaults to column name)
- **Y Label:** Vertical axis label (defaults to column name)
- **Title:** Plot title (defaults to "Y Label vs X Label")

#### Zero Threshold (Columns 8-9)

**Apply Checkbox (Column 8):**
- When checked, applies zero threshold filtering

**Threshold Value (Column 9):**
- Numerical threshold value
- Any Y values with absolute value less than this become zero
- Range: 0 to 1
- Precision: 15 decimal places
- Default: 0.00000000001

**Use case:** Remove numerical noise or small oscillations from results.

#### X Scale and Y Scale (Columns 10-11)

Multiply data by these factors before plotting:
- Range: -1×10⁹ to 1×10⁹
- Precision: 6 decimal places
- Default: 1.0 (no scaling)

**Formula:** 
- X_plotted = X_data × X_scale
- Y_plotted = Y_data × Y_scale

**Use case:** Quick unit conversions or data normalization without changing unit settings.

#### X Add and Y Add (Columns 12-13)

Add constant offsets to data after scaling:
- Range: -1×10⁹ to 1×10⁹
- Precision: 6 decimal places
- Default: 0.0 (no offset)

**Formula:**
- X_plotted = (X_data × X_scale) + X_add
- Y_plotted = (Y_data × Y_scale) + Y_add

**Use case:** Shift data to start from zero or adjust reference points.

#### Transformations Display (Column 14)

**Show Checkbox:**
- When checked (default), transformation information appears in axis labels
- When unchecked, labels show only the basic column name and units

**Label format when shown:**
- Scale: "x2.0" means multiplied by 2
- Offset: "+5.0" or "-5.0" for additions
- Threshold: "(Zero < 1e-11)" when applied

**Example:** "Displacement [inches] (x0.5 +2.0)" indicates data was scaled by 0.5 and offset by 2.0.

### Managing Plot Configurations

#### Adding Plots

**Button:** Click "Add Plot" in the Set Plots tab

Each new plot row includes:
- All configuration widgets
- Dropdown menus populated with current columns
- Default values for numerical parameters

**Shortcut workflow:**
1. Click "Add Plot"
2. Select X and Y data columns
3. Adjust range, labels, and transformations
4. Click "Generate Plots"

#### Removing Plots

**Button:** Click "Remove Last Plot"

- Removes the bottom-most plot configuration
- Cannot remove the last remaining plot
- No confirmation dialog (action is immediate)

### Generating Plots

**Button:** Click "Generate Plots" to render all configured plots.

**What happens:**
1. All existing plots are cleared
2. Data is extracted for each plot configuration
3. Transformations are applied (scale, add, threshold)
4. Plots are arranged in an automatic grid layout
5. Results appear in the Plots tab

### Plot Grid Layout

The application automatically arranges multiple plots:

- **1-3 plots:** Single column, vertical arrangement
- **4-18 plots:** 3 rows, multiple columns
- **19+ plots:** Expanded grid (3 + multiples of 3 rows)

**Layout priority:** Fills vertically first, then horizontally.

---

## 8. Advanced Features

### Merge Files (Sum Values)

Combine multiple analysis runs by summing corresponding data values.

**Use case:** Superposition of load cases in structural analysis.

**Steps:**
1. Click **File → Merge Files (Sum Values)**
2. Select multiple data files to combine
3. Dialog asks: "Is the first column a time column?"
   - **Yes:** Time column is preserved, other columns are summed
   - **No:** All columns are summed element-wise
4. Files are validated for consistency:
   - If time column: Time values must match exactly
   - Unit metadata (if present) must be consistent
5. Choose save location for combined file
6. Combined data is saved with new JSON metadata

**Output:**
- New data file with summed values
- JSON file with:
  - List of original files
  - Combined unit management settings
  - Data file name

**Requirements:**
- All files must have the same number of rows
- All files must have the same number of columns
- If using time column: Time values must be identical across files

### Copy Metadata to Files

Replicate unit and plot configurations to multiple data files.

**Use case:** Apply the same analysis setup to multiple similar output files.

**Steps:**
1. Click **File → Copy Metadata to Files**
2. Select source JSON file (with desired settings)
3. Select target data files (`.out` or `.dat`)
4. Metadata is copied to each target:
   - If target has existing JSON, it's updated
   - If no JSON exists, a new one is created
   - `data_file_name` is updated for each file

**Preserved:**
- Unit management settings
- Plot configurations
- All other metadata fields

**Updated:**
- `data_file_name` field (matches each target file)

### Combine Selected Columns from Files

Create a new dataset by selecting specific columns from multiple files and merging them horizontally.

**Use case:** Compile results from different analyses into a single dataset.

**Steps:**
1. Click **File → Combine Selected Columns from Files**
2. Select multiple source data files
3. Column selection dialog appears with:
   - Grouped checkboxes by file
   - Column names from metadata or default names
4. Check desired columns from each file
5. Click OK
6. Choose save location
7. New file is created with selected columns side-by-side

**Column naming:**
- Format: `[FileName]_[ColumnName]`
- Example: "analysis1.out_Displacement"

**Output:**
- New data file with combined columns
- JSON metadata with:
  - Original file list
  - Unit information for selected columns
  - Generated column names

**Requirements:**
- All source files must have the same number of rows
- Column selection must include at least one column

---

## 9. Keyboard Shortcuts

### Global Shortcuts

Available in Table Data and Plot Data tabs:

| Shortcut | Action |
|----------|--------|
| **Ctrl + +** | Add single row after current selection |
| **Ctrl + Shift + +** | Import multiple rows (with prompt) |
| **Ctrl + -** | Remove current row |
| **Ctrl + Shift + -** | Remove all selected rows |
| **Ctrl + C** | Copy selection to clipboard |
| **Ctrl + V** | Paste from clipboard at current position |
| **Delete** | Clear contents of selected cells |

### Selection Shortcuts

| Shortcut | Action |
|----------|--------|
| **Click** | Select single cell |
| **Click + Drag** | Select rectangular range |
| **Shift + Click** | Extend selection to clicked cell |
| **Click Row Header** | Select entire row |
| **Click Column Header** | Select entire column |
| **Shift + Click Header** | Extend selection to multiple rows/columns |

### Tips for Efficient Use

1. **Rapid row addition:** Keep pressing Ctrl + + to add multiple rows quickly
2. **Bulk deletion:** Select multiple rows with Shift, then Ctrl + Shift + - to remove all at once
3. **Excel workflow:** Copy data from Excel (Ctrl + C), click target cell, paste (Ctrl + V)
4. **Clean up:** Select unwanted cells and press Delete to clear without removing rows

---

## 10. Workflows and Examples

### Workflow 1: Basic Analysis Setup

**Scenario:** You have a displacement recorder file and want to plot displacement vs. time.

1. **Open file:** File → Open File → Select your `.out` file
2. **Configure units:**
   - Go to Unit Management tab
   - Column 1: Rename to "Time", set to Time/seconds/seconds
   - Column 2: Rename to "Displacement", set to Length/meters/inches
3. **Verify conversion:** Check Plot Data tab to see displacement in inches
4. **Configure plot:**
   - Go to Set Plots tab
   - X Data: Time
   - Y Data: Displacement
   - X Label: "Time (seconds)"
   - Y Label: "Displacement (inches)"
   - Title: "Node Displacement History"
5. **Generate:** Click "Generate Plots"
6. **Save configuration:** File → Save with Metadata

### Workflow 2: Multi-Column Analysis

**Scenario:** Force-displacement curves for multiple nodes.

1. **Open file** with columns: Time, Node1_Disp, Node1_Force, Node2_Disp, Node2_Force
2. **Set up units:**
   - Time: seconds
   - Displacements: meters → inches
   - Forces: Newtons → kN
3. **Create multiple plots:**
   - Plot 1: Node1_Disp (X) vs Node1_Force (Y)
   - Plot 2: Node2_Disp (X) vs Node2_Force (Y)
   - Click "Add Plot" to create second plot
4. **Customize:**
   - Set appropriate labels for each plot
   - Apply different titles
5. **Generate plots:** See both force-displacement curves in grid layout
6. **Save:** File → Save with Metadata

### Workflow 3: Combining Load Cases

**Scenario:** Sum results from dead load and live load analyses.

1. **Prepare files:** 
   - `dead_load.out` (with JSON metadata)
   - `live_load.out` (with JSON metadata)
2. **Merge:** File → Merge Files (Sum Values)
3. **Select both files**
4. **Confirm:** "Is first column time?" → Yes
5. **Save as:** `combined_loads.out`
6. **Result:** 
   - Time column preserved
   - All other columns summed
   - Metadata merged into `combined_loads.json`
7. **Open and plot:** Load with Metadata to visualize combined response

### Workflow 4: Data Transformation

**Scenario:** Plot acceleration data with noise removal and unit conversion.

1. **Open acceleration file** (m/s²)
2. **Set up plot:**
   - Zero Threshold: Apply with value 0.001
   - Y Scale: 0.10197 (convert m/s² to g's)
   - X Add: 0.0
   - Y Add: 0.0
   - Show Transformations: Checked
3. **Labels:**
   - Y Label: "Acceleration"
   - Note: Label will show "(x0.10197) (Zero < 0.001)" automatically
4. **Generate plot:** Clean acceleration history in g's

### Workflow 5: Batch Processing

**Scenario:** Apply same plot setup to 10 similar analysis outputs.

1. **Create template:**
   - Open first file
   - Configure units and plots
   - File → Save with Metadata
2. **Copy to others:**
   - File → Copy Metadata to Files
   - Select the template JSON
   - Select all 10 target data files
   - Metadata copied to all
3. **Process each:**
   - File → Load with Metadata
   - Select each JSON file
   - Generate plots
   - Export as needed

### Workflow 6: Creating Comparison Datasets

**Scenario:** Compare specific results from multiple parameter studies.

1. **Collect files:** 
   - `param_1.out`
   - `param_2.out`
   - `param_3.out`
2. **Combine columns:** File → Combine Selected Columns from Files
3. **Select files:** All three parameter files
4. **Column selection dialog:**
   - From param_1.out: Check "Displacement" and "Force"
   - From param_2.out: Check "Displacement" and "Force"
   - From param_3.out: Check "Displacement" and "Force"
5. **Save as:** `comparison.out`
6. **Result columns:**
   - param_1.out_Displacement
   - param_1.out_Force
   - param_2.out_Displacement
   - param_2.out_Force
   - param_3.out_Displacement
   - param_3.out_Force
7. **Plot comparisons:** Create plots comparing displacement or force across parameters

---

## 11. Troubleshooting

### Problem: File Won't Open

**Symptoms:**
- Error message when opening file
- Application freezes during load

**Solutions:**
1. **Check file format:** Ensure data is space-delimited
2. **Verify numerical data:** All values must be convertible to float
3. **Check file permissions:** Ensure read access to the file
4. **Try smaller file:** Test with a subset to identify corruption

### Problem: Unit Conversion Not Working

**Symptoms:**
- Plot Data tab shows same values as Table Data
- Values don't change when changing plot units

**Solutions:**
1. **Check Unit Type:** Must be set to appropriate physical quantity (not "Unitless")
2. **Verify default units:** Must match the actual units in your file
3. **Different units required:** Plot units must differ from default units to see conversion
4. **Refresh:** Switch to another tab and back to Plot Data

### Problem: Plots Not Generating

**Symptoms:**
- Plots tab remains empty after clicking Generate Plots
- No error message appears

**Solutions:**
1. **Check row ranges:** Start Row must be ≤ End Row
2. **Verify data selection:** Ensure X and Y columns contain valid data
3. **Check for NaN:** Invalid transformations can produce NaN values
4. **Reset plots:** Open a new file to reset the plotting system

### Problem: Metadata Won't Load

**Symptoms:**
- Error when loading JSON file
- "Data file not found" message

**Solutions:**
1. **Check file location:** JSON and data file must be in same directory
2. **Verify data_file_name:** Field in JSON must match actual data filename
3. **Check JSON format:** Ensure valid JSON syntax (use a validator)
4. **Permissions:** Ensure read access to both JSON and data files

### Problem: Merge Files Fails

**Symptoms:**
- "Time values do not match" error
- "Unit information does not match" error

**Solutions:**
1. **Verify time columns:** If using time column, values must be identical
2. **Check dimensions:** All files must have same number of rows and columns
3. **Unit consistency:** Ensure all files have compatible unit metadata
4. **Try without time:** Answer "No" to time column question if time varies slightly

### Problem: Copy/Paste Not Working

**Symptoms:**
- Pasted data appears in wrong cells
- Data format is incorrect after paste

**Solutions:**
1. **Check delimiter:** Data should be tab-delimited
2. **Click target cell:** Click the top-left cell where paste should start
3. **Source format:** Ensure copying from compatible application
4. **Manual entry:** If problems persist, enter data manually

### Problem: Transformations Not Showing in Labels

**Symptoms:**
- Labels don't reflect scale, add, or threshold values

**Solutions:**
1. **Check "Show" checkbox:** In Set Plots tab, Column 14 must be checked
2. **Generate plots:** Changes only apply after clicking Generate Plots
3. **Non-default values:** Transformations only show if values differ from defaults (scale ≠ 1.0, add ≠ 0.0)

### Problem: Status Bar Not Updating

**Symptoms:**
- Status bar shows wrong file or "No file opened"

**Solutions:**
- This is cosmetic only and doesn't affect functionality
- Try reopening the file
- Check if the file was actually loaded (tabs should be enabled)

### Error Messages

**"No file is currently open. Please open a file first."**
- Action: Open a file before attempting to save metadata

**"JSON file does not contain data file information."**
- Action: Ensure JSON has `data_file_name` field

**"Corresponding data file not found."**
- Action: Move data file to same directory as JSON, or update JSON path

**"Unit information does not match other files."**
- Action: Verify unit configurations are consistent, or proceed without unit metadata

**"Time values do not match the first file."**
- Action: Ensure time columns are identical, or don't use time column option

---

## Appendix: Best Practices

### Data Management
1. **Keep JSON with data:** Always keep metadata files in the same directory as data files
2. **Use descriptive names:** Rename columns in Unit Management for clarity
3. **Save early, save often:** Use Save with Metadata after configuration changes
4. **Backup important configs:** Copy JSON files to preserve analysis setups

### Unit Configuration
1. **Set defaults correctly:** Default units must match your actual file units
2. **Consistent systems:** Use coherent unit systems within each analysis
3. **Document conversions:** Use descriptive column names to indicate final units
4. **Test conversions:** Verify a few values manually after unit changes

### Plotting Strategy
1. **Start simple:** Begin with basic plots, add transformations as needed
2. **Use transformations sparingly:** Prefer unit conversions over scaling when possible
3. **Label clearly:** Always provide meaningful axis labels and titles
4. **Grid layout:** Remember plots fill vertically first for better organization
5. **Zero threshold judiciously:** Too high removes real data, too low keeps noise

### File Combining
1. **Verify compatibility:** Check dimensions before merging files
2. **Consistent metadata:** Use Copy Metadata feature for uniform setups
3. **Name clearly:** Give combined files descriptive names indicating their source
4. **Document provenance:** JSON files automatically track original files

### Performance
1. **Large datasets:** Consider reducing data points for initial exploration
2. **Many plots:** Limit to 18 or fewer plots for optimal viewing
3. **Memory management:** Close and reopen application for very large files
4. **Plot refresh:** Plots regenerate from scratch each time (no incremental updates)

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