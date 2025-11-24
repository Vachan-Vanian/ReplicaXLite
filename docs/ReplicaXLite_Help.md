# ReplicaXLite User Manual

## Table of Contents
1. [Introduction](#introduction)
2. [Getting Started](#getting-started)
3. [User Interface Overview](#user-interface-overview)
4. [Project Management](#project-management)
5. [View Controls](#view-controls)
6. [3D Interactor](#3d-interactor)
7. [FEM Setup](#fem-setup)
8. [Tools](#tools)
9. [Integrated Console - Full Program Control](#integrated-console---full-program-control)
10. [Settings](#settings)
11. [Keyboard Shortcuts Reference](#keyboard-shortcuts-reference)
12. [Support and Contact](#support-and-contact)

---

## Introduction

**ReplicaXLite** is a finite element toolkit for creating, analyzing, and monitoring 3D structural models. Built with PySide6 and PyVista, it provides an intuitive graphical interface for structural engineering workflows.

### Key Features
- Interactive 3D visualization of structural models
- Comprehensive FEM (Finite Element Method) model setup
- **Integrated Jupyter Console with full program control**
- Multiple view modes and camera controls
- Tools for sensor data, unit conversion, and OpenSees integration
- Project-based workflow with save/load functionality
- Rich media support (plots, HTML, LaTeX in console)
- Python scripting for automation and custom workflows

---

## Getting Started

### Launching the Application
Run ReplicaXLite from your terminal or command line. The application will display a splash screen while loading.

### Minimum Requirements
- Minimum window size: 1280 x 720 pixels
- Default window size: 1536 x 864 pixels

### First Launch
When you first open ReplicaXLite, you'll see:
- Window title showing version and "No project is opened"
- Empty 3D visualization area with coordinate axes
- Status bar at the bottom
- Menu bar with Project, View, Interactor, Tools, and Info menus
- Console with welcome banner and quick start guide

---

## User Interface Overview

### Main Window Layout

The ReplicaXLite interface consists of three main panels arranged horizontally:

#### 1. Left Panel: Project File Viewer
- Displays project structure and files
- Navigate through your project components
- Tree-view organization

#### 2. Center Panel: Split into Two Sections

**Top Section - 3D Interactor:**
- Interactive 3D visualization area
- Shows coordinate axes (X, Y, Z)
- Main workspace for viewing and manipulating models
- PyVista-based rendering

**Bottom Section - FEM Tables:**
Tabbed interface containing:
- **Materials**: Define material properties
- **Sections**: 
  - Elastic sections
  - Fiber sections (with Section, Rebar Points, Rebar Lines, Rebar Circles sub-tabs)
- **Nodes**:
  - Coordinates: Node position definitions
  - Constraints: Boundary conditions
  - Restraints: Rigid Diaphragms, Rigid Links, Equal DOFs
  - Masses: Nodal mass definitions
  - Loads: Applied nodal loads
- **Elements**: Beam Integrations, Connections, Loads
- **Time Series**: Time-dependent functions
- **Patterns**: Load pattern definitions
- **Analyses**: Analysis configuration
- **Sensors**: Sensor placement and setup

#### 3. Right Panel: Console
- **Jupyter-based interactive console**
- Full Python environment
- Execute commands and scripts
- View output and messages
- Rich media display (plots, HTML, LaTeX)
- Direct application control

### Status Bar
Located at the bottom of the window, the status bar displays:
- Current operation status
- Messages and notifications
- Application state information

---

## Project Management

Access project operations through the **Project** menu or keyboard shortcuts.

### Creating a New Project
- **Menu**: Project → New
- **Shortcut**: `Ctrl+N`
- Creates a fresh project workspace
- Warning: Unsaved changes in current project will be lost

### Opening an Existing Project
- **Menu**: Project → Open
- **Shortcut**: `Ctrl+O`
- Opens a file dialog to select a project file
- Loads all project data and settings

### Saving Your Project
- **Menu**: Project → Save
- **Shortcut**: `Ctrl+S`
- Saves current project state
- Preserves all model data, settings, and configurations

### Closing a Project
- **Menu**: Project → Close
- Closes the current project
- Returns to empty workspace state

### Settings
- **Menu**: Project → Settings
- Opens the Settings Editor dialog
- Configure application preferences and defaults
- Changes are saved and applied immediately

### Exiting the Application
- **Menu**: Project → Exit
- Closes ReplicaXLite
- Confirmation dialog appears to prevent accidental data loss
- Warning: "Close the application? Unsaved changes will be lost!"

---

## View Controls

ReplicaXLite provides extensive camera and view controls for 3D model visualization.

### Standard Views

#### Isometric View
- **Menu**: View → Isometric
- **Shortcut**: `Ctrl+0`
- Default 3D perspective view

#### Orthogonal Plane Views

**Positive Direction Views:**
- **Plane YZ | +X**: View → Plane YZ | +X, Shortcut: `Ctrl+1`
- **Plane XZ | +Y**: View → Plane XZ | +Y, Shortcut: `Ctrl+2`
- **Plane XY | +Z**: View → Plane XY | +Z, Shortcut: `Ctrl+3`

**Negative Direction Views:**
- **Plane YZ | -X**: View → Plane YZ | -X, Shortcut: `Ctrl+Alt+1`
- **Plane XZ | -Y**: View → Plane XZ | -Y, Shortcut: `Ctrl+Alt+2`
- **Plane XY | -Z**: View → Plane XY | -Z, Shortcut: `Ctrl+Alt+3`

### Camera Rotation

Rotate the view around global axes:

**X-Axis Rotation:**
- **Rotate X+**: Shortcut: `Alt+1`
- **Rotate X-**: Shortcut: `Alt+4`

**Y-Axis Rotation:**
- **Rotate Y+**: Shortcut: `Alt+2`
- **Rotate Y-**: Shortcut: `Alt+5`

**Z-Axis Rotation:**
- **Rotate Z+**: Shortcut: `Alt+3`
- **Rotate Z-**: Shortcut: `Alt+6`

Rotation angles are configurable in Settings under Interactor preferences.

### Camera Movement

Pan the camera in global coordinate directions:

**X-Direction:**
- **Move X+**: Shortcut: `Ctrl+Up`
- **Move X-**: Shortcut: `Ctrl+Down`

**Y-Direction:**
- **Move Y+**: Shortcut: `Ctrl+Right`
- **Move Y-**: Shortcut: `Ctrl+Left`

**Z-Direction:**
- **Move Z+**: Shortcut: `Alt+Up`
- **Move Z-**: Shortcut: `Alt+Down`

Movement step distances are configurable in Settings.

### Projection Modes

#### Toggle Perspective/Orthogonal
- **Menu**: View → Toggle Perspective/Orthogonal
- **Shortcut**: `Ctrl+8`
- Switch between perspective (3D depth) and orthogonal (parallel) projection

#### Toggle Full Screen Mode
- **Menu**: View → Toggle Full Screen Mode
- **Shortcut**: `Shift+F`
- Maximize visualization area
- Press again to return to normal view

### Display Modes

Control how the model is rendered:

#### Surface with Edges
- **Menu**: View → Surface with Edges
- **Shortcut**: `Ctrl+4`
- Shows solid surfaces with visible element edges

#### Surface without Edges
- **Menu**: View → Surface without Edges
- **Shortcut**: `Ctrl+5`
- Shows only solid surfaces (cleaner appearance)

#### Wireframe
- **Menu**: View → Wireframe
- **Shortcut**: `Ctrl+6`
- Shows only element edges (transparent surfaces)

---

## 3D Interactor

The Interactor menu provides tools for displaying and managing content in the 3D visualization area.

### Display/Update Model
- **Menu**: Interactor → Display/Update Model
- Renders or refreshes the current structural model in the 3D view
- Use after making changes to model geometry or properties

### Clear Displayed Model
- **Menu**: Interactor → Clear Displayed Model
- Removes the structural model from view
- Other objects (spheres, annotations) remain visible

### Clear ALL
- **Menu**: Interactor → Clear ALL
- Removes all content from the 3D interactor
- Complete reset of the visualization area

### Add Sphere
- **Menu**: Interactor → Add Sphere
- Adds a sphere object to the 3D scene
- Useful for marking points of interest or reference locations

### Screenshot
- **Menu**: Interactor → Screenshot
- **Shortcut**: `Ctrl+P`
- Captures the current 3D view as an image
- Settings available for:
  - Transparent background (on/off)
  - Image scale factor

---

## FEM Setup

The FEM (Finite Element Method) setup interface allows you to define all components of your structural model through tabbed tables.

### Materials Tab
Define material properties for your structural elements:
- Material identification
- Mechanical properties
- Constitutive models

### Sections Tab

#### Elastic Sections
- Define elastic section properties
- Cross-sectional characteristics
- Standard section types

#### Fiber Sections
Advanced section modeling with four sub-tabs:
1. **Section**: Main fiber section definition
2. **Rebar Points**: Individual reinforcement bar locations
3. **Rebar Lines**: Linear reinforcement patterns
4. **Rebar Circles**: Circular reinforcement patterns

### Nodes Tab

#### Coordinates
- Define node positions in 3D space
- X, Y, Z coordinate specification
- Node identification and labeling

#### Constraints
- Apply boundary conditions
- Fixed, pinned, or roller supports
- Custom constraint definitions

#### Restraints
Three types of restraints available:
1. **Rigid Diaphragms**: Enforce in-plane rigidity
2. **Rigid Links**: Connect nodes with rigid elements
3. **Equal DOFs**: Enforce equal degrees of freedom between nodes

#### Masses
- Assign lumped masses to nodes
- Mass values for dynamic analysis

#### Loads
- Define nodal loads
- Force and moment applications
- Load combinations

### Elements Tab

#### Beam Integrations
- Define integration schemes for beam elements
- Gauss-Lobatto, Legendre, etc.

#### Connections
- Element connectivity definitions
- Node-to-node relationships

#### Loads
- Distributed element loads
- Uniform and varying load patterns

### Time Series Tab
- Define time-dependent functions
- Load time histories
- Ground motion records

### Patterns Tab
- Load pattern definitions
- Static and dynamic load cases
- Pattern combinations

### Analyses Tab
- Configure analysis parameters
- Static, dynamic, or nonlinear analysis
- Solution algorithms and convergence criteria

### Sensors Tab
- Define sensor locations
- Monitor structural response
- Data collection setup

---

## Tools

ReplicaXLite includes several utility tools accessible from the Tools menu.

### Sensor Data Reader
- **Menu**: Tools → Sensor Data Reader
- Import and visualize sensor data
- Process measurement time histories
- Data analysis and visualization

### Unit Converter
- **Menu**: Tools → Unit Converter
- Convert between different unit systems
- Common engineering units
- SI, Imperial, and custom conversions

### OpenSees Recorder Reader
- **Menu**: Tools → OpenSees Recorder Reader
- Read output files from OpenSees analyses
- Import recorder data
- Visualization and post-processing

### Color Picker
- **Menu**: Tools → Color Picker
- Select colors for visualization
- Customize element and component colors
- RGB/Hex color selection

### Time History Data
- **Menu**: Tools → Time History Data
- Manage time history datasets
- Import/export capabilities
- Time series visualization

---

## Integrated Console - Full Program Control

The **Jupyter Console** is one of ReplicaXLite's most powerful features, giving you complete programmatic access to every aspect of the application.

### What Makes It Powerful

This isn't a basic Python interpreter - it's a full Jupyter kernel with:
- **Complete access to the application** through the `app` variable
- **Rich media display** (plots, HTML, LaTeX, images)
- **IPython magic commands** for advanced workflows
- **Asynchronous execution** for long-running tasks
- **File operations** built into the toolbar
- **Tab completion** and **help system**
- **Syntax highlighting** with Monokai theme

### Console Toolbar

Located at the top of the console panel:

- **📂 Open**: Load Python script into console (doesn't execute automatically)
- **💾 Save**: Save console history to current file
- **💾 Save As**: Save console history to new file
- **🗑️ Clear**: Clear console output

### Welcome Banner

When the console loads, you'll see:
- Quick start guide
- Example code snippets
- List of available features
- Tips for usage

### Getting Started

The console automatically loads with:
- Common imports: `numpy`, `matplotlib`, `pandas`
- The `app` object pointing to your ReplicaXLite instance
- Rich display formatters enabled
- Matplotlib configured for inline plotting at 150 DPI

### Direct Application Control

**Access everything in the application:**

```python
# Main application object
app                             # ReplicaXLite main window

# Core components
app.settings                    # All settings (live dictionary)
app.model                       # Your structural models (dictionary)
app.interactor                  # 3D PyVista viewer widget

# Managers - full control of all features
app.manage_interactor          # Control visualization
app.manage_fem_table           # Access FEM tables
app.manage_project             # Project operations
app.manage_tools               # Access all tools
app.manage_settings            # Settings editor

# UI Components
app.main_notebook              # Main tab widget
app.fem_table_tabs             # FEM table tabs (nested dict)
app.project_file_viewer        # Project tree viewer
app.console_manager            # Console manager itself
```

### Practical Examples

**Modify settings programmatically:**
```python
# Change rotation angle for X-axis
app.settings['interactor']['rotation_angle_deg_x'] = 15

# Change camera movement step size
app.settings['interactor']['distance_step_z'] = 100

# View all interactor settings
print(app.settings['interactor'])
```

**Control the 3D viewer:**
```python
# Switch between standard views
app.interactor.view_isometric()
app.interactor.view_xy()
app.interactor.view_yz()

# Clear the display
app.manage_interactor.interactor.clear()

# Add objects to the scene
app.manage_interactor.add_sphere()

# Take a screenshot programmatically
app.manage_interactor.take_screenshot(
    None,  # filename (None = auto-generate)
    transparent_background=True,
    scale=2  # Higher resolution
)
```

**Access your structural models:**
```python
# List all loaded models
print(app.model.keys())

# Access a specific model
if 'my_bridge' in app.model:
    bridge = app.model['my_bridge']
    # Now you have full access to the StructuralModel object
    # Inspect nodes, elements, materials, etc.

# Check if any models are loaded
if app.model:
    print(f"Loaded models: {len(app.model)}")
else:
    print("No models loaded")
```

### Rich Media Display

**High-quality matplotlib plots:**
```python
import matplotlib.pyplot as plt
import numpy as np

# Create data
x = np.linspace(0, 10, 100)
y = np.sin(x)

# Plot inline at 150 DPI
plt.figure(figsize=(8, 4))
plt.plot(x, y, linewidth=2)
plt.title('Inline Plot at High Resolution')
plt.xlabel('X axis')
plt.ylabel('Y axis')
plt.grid(True, alpha=0.3)
plt.show()
```

**Display custom HTML:**
```python
from IPython.display import HTML, display

html_content = '''
<div style="background-color:#f0f0f0; padding:20px; 
            border-radius:5px; border:2px solid #0066cc;">
    <h2 style="color:#0066cc;">Custom HTML Display</h2>
    <p>You can render <b>any HTML content</b> directly!</p>
    <ul>
        <li>Tables</li>
        <li>Images</li>
        <li>Formatted text</li>
    </ul>
</div>
'''
display(HTML(html_content))
```

**Display LaTeX equations:**
```python
from IPython.display import Latex, display

# Single equation
display(Latex(r'$\sigma = E \cdot \epsilon$'))

# Multiple equations
display(Latex(r'''
$$M = \int_{A} y \cdot \sigma \, dA$$
$$I = \int_{A} y^2 \, dA$$
'''))
```

**Pretty print Pandas DataFrames:**
```python
import pandas as pd

# Create sample data
data = pd.DataFrame({
    'Node': [1, 2, 3, 4],
    'X': [0.0, 5.0, 10.0, 15.0],
    'Y': [0.0, 0.0, 0.0, 0.0],
    'Z': [0.0, 5.0, 10.0, 15.0]
})

# Display with automatic formatting
display(data)
```

### IPython Magic Commands

Magic commands provide powerful functionality:

```python
# Timing and performance
%timeit [x**2 for x in range(1000)]
%time long_operation()

# Variable inspection
%who                           # List variables
%whos                          # Detailed variable list
%who_ls                        # Return list of variables

# System commands
%pwd                           # Current directory
%cd /path/to/dir              # Change directory
%ls                            # List directory contents

# History
%history                       # All command history
%history -n 1-10              # Lines 1-10 with numbers
%history -g pattern           # Search history

# Namespace management
%reset                         # Clear all variables
%reset -f                      # Force reset without confirmation
%reset_selective pattern       # Reset specific variables

# Other useful magics
%matplotlib inline             # Configure matplotlib
%quickref                      # Quick reference guide
%lsmagic                       # List all magic commands
```

**Practical magic examples:**
```python
# Measure performance
%timeit app.interactor.view_isometric()

# See what variables exist
%whos

# View recent commands
%history -n -5  # Last 5 commands
```

### Asynchronous Execution

For long-running operations that would freeze the GUI, use `run_async()`:

```python
import time

def long_calculation():
    """Simulate a long-running task"""
    for i in range(100):
        print(f"Processing step {i}/100")
        time.sleep(0.1)  # Simulate work
    return "Calculation complete!"

# Run without freezing the GUI
run_async(long_calculation)
```

**The output appears in real-time in the console while the GUI remains fully responsive!**

**Async with parameters:**
```python
def process_data(data_size, delay):
    total = 0
    for i in range(data_size):
        print(f"Processing item {i+1}/{data_size}")
        total += i * i
        time.sleep(delay)
    return f"Total: {total}"

# Run with arguments
run_async(process_data, 50, 0.05)
```

### Workflow Automation

Create reusable scripts for common tasks:

**Example - Batch model setup:**
```python
def setup_standard_materials():
    """Setup common structural materials"""
    materials = {
        'concrete_c30': {'E': 30e9, 'nu': 0.2},
        'steel_s355': {'E': 210e9, 'nu': 0.3},
        'steel_rebar': {'E': 200e9, 'nu': 0.3}
    }
    
    for name, props in materials.items():
        print(f"Adding material: {name}")
        # Add to your model here
    
    print("✓ Standard materials configured")

# Run it
setup_standard_materials()
```

**Example - Data analysis workflow:**
```python
import pandas as pd
import matplotlib.pyplot as plt

def analyze_results(filename):
    """Analyze structural analysis results"""
    # Load results
    results = pd.read_csv(filename)
    
    # Statistical summary
    print(results.describe())
    
    # Find critical values
    max_disp = results['displacement'].max()
    max_stress = results['stress'].max()
    
    print(f"\nMaximum displacement: {max_disp:.3f}")
    print(f"Maximum stress: {max_stress:.3f}")
    
    # Plot results
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4))
    
    ax1.plot(results['time'], results['displacement'])
    ax1.set_title('Displacement vs Time')
    ax1.grid(True)
    
    ax2.plot(results['time'], results['stress'])
    ax2.set_title('Stress vs Time')
    ax2.grid(True)
    
    plt.tight_layout()
    plt.show()

# Use it
# analyze_results('analysis_output.csv')
```

### Help System

Get help on any object:

```python
# Quick help
app?                           # Overview of app object
app.interactor?                # Help on interactor

# Detailed help with source code
app??                          # Full source
app.settings??                 # View settings structure

# Help on modules
import numpy as np
np.array?                      # Help on numpy arrays

# Python built-in help
help(app)
help(app.manage_interactor)
```

### Tab Completion

Press **Tab** at any time to:
- Complete variable names
- See available methods and attributes
- Browse object properties
- Complete file paths

```python
app.in[TAB]                    # Shows: interactor, etc.
app.settings['in[TAB]          # Shows available keys
app.manage_[TAB]               # Shows all managers
```

### Console File Operations

**Open a Python script:**
1. Click **📂 Open** in the toolbar
2. Select your `.py` file
3. Code loads into the console (not executed)
4. Press `Shift+Enter` to execute

**Save your work:**
1. Click **💾 Save** (or **Save As**)
2. Console history is saved to a `.py` file
3. Magic commands are automatically prefixed with `%`
4. File can be loaded and executed later

**Clear output:**
- Click **🗑️ Clear** to clear console output
- Variables remain in memory
- Use `%reset` to clear variables

### Tips for Power Users

1. **Save workflows**: Use Save button to export console history as reusable `.py` files
2. **Keyboard shortcuts**: 
   - `Shift+Enter`: Execute and move to next line
   - `Ctrl+C`: Interrupt execution
   - `Up/Down arrows`: Navigate command history
   - `Tab`: Auto-complete
3. **Explore internals**: Everything is accessible - try `dir(app)` to see all attributes
4. **Batch operations**: Write functions for repetitive tasks
5. **Integration**: Combine console commands with GUI operations seamlessly
6. **Custom modules**: Import your own Python modules for specialized analysis

### Console Reset

If you need a fresh start:
```python
# Clear all variables
%reset -f
```

The console will automatically:
- Reinitialize the environment
- Restore the `app` reference
- Re-import standard libraries
- Reset execution counter to `In[1]`

### Advanced: Multithreading Safety

⚠️ **Important**: When using `run_async()`, do not call GUI methods directly from the worker function. GUI updates must happen in the main thread. The output (via `print()`) is automatically routed to the console safely.

---

## Settings

Access the Settings Editor through **Project → Settings**. Configure application behavior and default values.

### Settings Editor Interface

The Settings Editor provides a structured interface to modify application preferences. Changes are saved immediately and persist across sessions.

### Key Settings Categories

#### Unit System
- Select base unit system (SI, Imperial, etc.)
- Configure conversion factors
- Affects all numerical inputs and displays throughout the application

#### Interactor Settings

**Rotation Angles:**
- `rotation_angle_deg_x`: Rotation increment for X-axis (degrees)
- `rotation_angle_deg_y`: Rotation increment for Y-axis (degrees)
- `rotation_angle_deg_z`: Rotation increment for Z-axis (degrees)

**Camera Movement:**
- `distance_step_x`: Movement step size for X direction
- `distance_step_y`: Movement step size for Y direction
- `distance_step_z`: Movement step size for Z direction

**Screenshot Options:**
- `transparent_background`: Enable/disable transparent background
- `scale`: Resolution multiplier for screenshots (1, 2, 3, etc.)

### Settings in Console

You can also modify settings directly through the console:

```python
# View current settings
print(app.settings)

# View specific category
print(app.settings['interactor'])

# Modify settings
app.settings['interactor']['rotation_angle_deg_x'] = 10
app.settings['interactor']['scale'] = 3
```

### Settings Persistence
- Settings are automatically saved when you close the Settings Editor
- Settings are stored in the application configuration
- Changes apply immediately
- Settings are restored on application restart

---

## Keyboard Shortcuts Reference

### Project Management
| Action | Shortcut |
|--------|----------|
| New Project | `Ctrl+N` |
| Open Project | `Ctrl+O` |
| Save Project | `Ctrl+S` |

### Standard Views
| Action | Shortcut |
|--------|----------|
| Isometric View | `Ctrl+0` |
| Plane YZ \| +X | `Ctrl+1` |
| Plane XZ \| +Y | `Ctrl+2` |
| Plane XY \| +Z | `Ctrl+3` |
| Plane YZ \| -X | `Ctrl+Alt+1` |
| Plane XZ \| -Y | `Ctrl+Alt+2` |
| Plane XY \| -Z | `Ctrl+Alt+3` |

### Display Modes
| Action | Shortcut |
|--------|----------|
| Surface with Edges | `Ctrl+4` |
| Surface without Edges | `Ctrl+5` |
| Wireframe | `Ctrl+6` |
| Toggle Perspective/Ortho | `Ctrl+8` |
| Toggle Full Screen | `Shift+F` |

### Camera Rotation
| Action | Shortcut |
|--------|----------|
| Rotate X+ | `Alt+1` |
| Rotate Y+ | `Alt+2` |
| Rotate Z+ | `Alt+3` |
| Rotate X- | `Alt+4` |
| Rotate Y- | `Alt+5` |
| Rotate Z- | `Alt+6` |

### Camera Movement
| Action | Shortcut |
|--------|----------|
| Move X+ | `Ctrl+Up` |
| Move X- | `Ctrl+Down` |
| Move Y+ | `Ctrl+Right` |
| Move Y- | `Ctrl+Left` |
| Move Z+ | `Alt+Up` |
| Move Z- | `Alt+Down` |

### Interactor
| Action | Shortcut |
|--------|----------|
| Screenshot | `Ctrl+P` |

### Console Shortcuts
| Action | Shortcut |
|--------|----------|
| Execute Line | `Shift+Enter` |
| Interrupt Execution | `Ctrl+C` |
| Auto-complete | `Tab` |
| Previous Command | `Up Arrow` |
| Next Command | `Down Arrow` |

---

### Getting Help

1. **In-Application Help**: 
   - Use the console help system: `app?`, `help(app)`
   - View this manual
   - Explore example code in the console welcome banner

2. **Bug Reports**: 
   - Contact the developer via email
   - Include version information from window title
   - Describe steps to reproduce the issue

3. **Feature Requests**:
   - Email suggestions to the developer
   - Describe your use case and workflow

---

## Integration with External Tools

**Export data:**
```python
import pandas as pd

# Collect data from your model
data = {
    'node': [1, 2, 3],
    'x': [0, 5, 10],
    'displacement': [0.0, 2.5, 5.0]
}

df = pd.DataFrame(data)
df.to_csv('results.csv', index=False)
print("✓ Data exported to results.csv")
```

**Import data:**
```python
import numpy as np

# Load ground motion
acceleration = np.loadtxt('ground_motion.txt')
print(f"Loaded {len(acceleration)} data points")

# Apply to model
# ...
```

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