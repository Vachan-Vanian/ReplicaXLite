# ReplicaXLite StructuralAPI - User Manual

Version 1.0 | Copyright © 2024-2025 Vachan Vanian

---

## Table of Contents

1. [Introduction](#1-introduction)
2. [Installation](#2-installation)
3. [Basic Concepts](#3-basic-concepts)
4. [Quick Start Guide](#4-quick-start-guide)
5. [Model Geometry](#5-model-geometry)
6. [Material and Section Properties](#6-material-and-section-properties)
7. [Constraints](#7-constraints)
8. [Loading](#8-loading)
9. [Analysis](#9-analysis)
10. [Visualization](#10-visualization)
11. [Import/Export](#11-importexport)
12. [Advanced Features](#12-advanced-features)
13. [Best Practices](#13-best-practices)
14. [Troubleshooting](#14-troubleshooting)

---

## 1. Introduction

### 1.1 What is ReplicaXLite StructuralAPI?

ReplicaXLite StructuralAPI is a Python-based finite element toolkit designed for creating, analyzing, and monitoring 3D structural models. Built on top of OpenSeesPy and opstool, it provides a high-level, object-oriented interface that simplifies the process of structural analysis while maintaining the power and flexibility of OpenSees.

### 1.2 Key Features

- **Intuitive API**: Object-oriented design with clear method names
- **Delayed Execution**: Build your model without immediately creating OpenSees objects
- **Comprehensive Analysis**: Modeal, Gravity, Static, Pushover and Dynamic Time History analyses
- **Visualization**: Integrated visualization using opstool and PyVista
- **Import/Export**: DXF file support for CAD integration
- **Smart Analysis**: Automatic convergence strategies for difficult analyses
- **Modular Design**: Separated concerns for geometry, properties, constraints, and loading

### 1.3 System Requirements

- Python 3.11 or higher
- OpenSeesPy
- opstool
- NumPy
- PyVista
- ezdxf
- tqdm

---

## 2. Installation

```
see README.md
```

### 2.2 Project Structure

```
project/
├── StructuralAPI/
│   ├── __init__.py
│   ├── p000_utility.py
│   ├── p001_material.py
│   ├── p002_section.py
│   ├── p003_node.py
│   ├── p004_element.py
│   ├── p005_constraint.py
│   ├── p006_time_series.py
│   ├── p007_load.py
│   └── p008_structural_model/
│       ├── __init__.py
│       ├── p008_00_structural_model.py
│       ├── p008_01_model_geometry.py
│       ├── p008_02_model_properties.py
│       ├── p008_03_model_constraints.py
│       ├── p008_04_model_loading.py
│       ├── p008_05_model_analysis.py
│       ├── p008_06_model_visualization.py
│       └── p008_07_model_io.py
└── your_analysis_script.py
```

### 2.3 Basic Import

```python
from replicaxlite import StructuralModel
```

---

## 3. Basic Concepts

### 3.1 Model Organization

The `StructuralModel` class serves as the central hub, with specialized managers:

- **geometry**: Manages nodes and elements
- **properties**: Manages materials, sections, and beam integrations
- **constraints**: Manages boundary conditions and multi-point constraints
- **loading**: Manages time series and load patterns
- **analysis**: Manages analysis execution
- **visualization**: Manages model and results visualization
- **io**: Manages import/export operations

### 3.2 Delayed Execution Pattern

ReplicaXLite StructuralAPI uses a delayed execution pattern:

1. **Build Phase**: Create model components (nodes, elements, etc.)
2. **Model Building**: Call `build_model()` to create the OpenSees model
3. **Analysis Phase**: Run analyses
4. **Post-Processing**: Visualize results

```python
model = StructuralModel()

# Build phase - no OpenSees objects created yet
model.geometry.create_node(1, 0, 0, 0)
model.geometry.create_element(...)

# Model building - OpenSees model is created
model.build_model()

# Analysis phase
model.analysis.run_static_analysis(...)
```

### 3.3 Element Types

Elements are categorized by `StructuralElement` enum:
- `column`: Vertical structural members
- `beam`: Horizontal structural members
- `wall`: Shear wall elements
- `slab`: Floor slab elements
- `truss`: Truss elements
- `tree`: Special elements (e.g., for tree structures)
- `infill`: Infill panel elements
- `general`: General-purpose elements

### 3.4 Coordinate System

- **Global axes**: X (horizontal), Y (horizontal), Z (vertical)
- **DOF numbering**: 1=X, 2=Y, 3=Z, 4=RX, 5=RY, 6=RZ
- **Element local axes**: Automatically calculated based on element orientation

---

## 4. Quick Start Guide

### 4.1 Simple Frame Example

```python
from replicaxlite import StructuralModel

# Create model
model = StructuralModel("SimpleFrame")

# Create material
model.properties.create_uniaxial_material(
    tag=1,
    name="Steel01",
    material_type="Steel01",
    material_args={"Fy": 355e6, "E0": 200e9, "b": 0.01}
)

# Create elastic section
model.properties.create_elastic_section(
    tag=1,
    name="Column_Section",
    structural_element_type="column",
    section_shape="rectangle",
    shape_params={"width": 0.3, "height": 0.3},
    E_mod=30e9,
    G_mod=12e9
)

# Create beam integration
model.properties.create_beam_integration(
    tag=1,
    integration_type="Lobatto",
    structural_element_use="column",
    section_tag=1,
    num_points=5
)

# Create nodes
model.geometry.create_node(1, 0, 0, 0)
model.geometry.create_node(2, 0, 0, 3)
model.geometry.create_node(3, 4, 0, 3)
model.geometry.create_node(4, 4, 0, 0)

# Create elements
model.geometry.create_element(
    tag=1,
    start_node=1,
    end_node=2,
    element_type="column",
    section_name="Column_Section",
    integration_tag=1
)

# Create constraints (fixed base)
model.constraints.create_constraint(1, 1, 1, 1, 1, 1, 1)
model.constraints.create_constraint(4, 1, 1, 1, 1, 1, 1)

# Create load pattern
ts = model.loading.create_constant_time_series(tag=1)
pattern = model.loading.create_load_pattern(tag=1, time_series=ts)
pattern.add_node_load(2, fx=10000)  # 10kN lateral load

# Build model
model.build_model()

# Run analysis
odb = model.analysis.run_static_analysis(
    load_pattern_tag=1,
    n_steps=10,
    output_odb_tag="static"
)

# Visualize results
model.visualization.visualize_deformation(odb_tag="static")
```

---

## 5. Model Geometry

### 5.1 Creating Nodes

#### Basic Node Creation

```python
# Create node with tag and coordinates
node = model.geometry.create_node(
    tag=1,           # Node ID
    x=0.0,           # X coordinate
    y=0.0,           # Y coordinate  
    z=0.0            # Z coordinate
)
```

#### Adding Mass to Nodes

```python
node.add_mass(
    mass_x=1000,     # Translational mass in X
    mass_y=1000,     # Translational mass in Y
    mass_z=1000,     # Translational mass in Z
    mass_rx=0,       # Rotational mass about X
    mass_ry=0,       # Rotational mass about Y
    mass_rz=0        # Rotational mass about Z
)
```

### 5.2 Creating Elements

#### BeamColumn Elements

```python
# Create a beam-column element
element = model.geometry.create_element(
    tag=1,
    start_node=1,
    end_node=2,
    element_type="column",              # or "beam", "wall", etc.
    section_name="Column_Section",
    element_class="forceBeamColumn",    # or "dispBeamColumn", "elasticBeamColumn"
    integration_tag=1,
    element_args={}                      # Optional: additional arguments
)
```

#### General Elements (Advanced)

```python
# Create any OpenSees element type
element = model.geometry.create_general_element(
    tag=100,
    start_node=1,
    end_node=2,
    element_type="truss",               # OpenSees element type
    structural_element_type="truss",    # For model organization
    element_args={
        "A": 0.01,                      # Cross-sectional area
        "mat": 1                        # Material tag
    }
)
```

#### Line Elements (Geometric Only)

```python
# Create geometric line without structural properties
line = model.geometry.create_line_element(
    tag=1,
    start_node=1,
    end_node=2,
    element_type="beam"
)

# Later, convert to structural element
model.geometry.convert_line_elements(
    section_mapping={"beam": "Beam_Section"},
    element_class="forceBeamColumn"
)
```

### 5.3 Automatic Grid Generation

```python
# Create 3D grid structure
stats = model.geometry.create_grid(
    x_coords=[0, 4, 8],          # Grid lines in X
    y_coords=[0, 5, 10],         # Grid lines in Y
    z_coords=[0, 3, 6, 9],       # Grid lines in Z (floors)
    create_columns=True,
    create_beams=True,
    column_type="column",
    beam_x_type="beam_x",
    beam_y_type="beam_y"
)

print(f"Created {stats['nodes_created']} nodes")
print(f"Created {stats['elements_created']} elements")
```

### 5.4 Model Transformations

```python
# Translate entire structure
model.geometry.translate_structure(dx=5, dy=0, dz=0)

# Rotate about Z axis
model.geometry.rotate_structure_about_z(
    angle_degrees=45,
    center_x=0,
    center_y=0
)
```

### 5.5 Element Subdivision

```python
# Subdivide an element into smaller segments
new_element_ids = model.geometry.subdivide_element(
    element_id=1,
    num_segments=4
)
```

### 5.6 Model Queries

```python
# Find node at coordinates
node = model.geometry.find_node(x=0, y=0, z=3, tolerance=0.01)

# Get elements by type
columns = model.geometry.get_elements_by_group("column")
beams = model.geometry.get_elements_by_group("beam")

# Get elements by floor
floor_elements = model.geometry.get_elements_by_floor(3.0)

# Check for issues
free_nodes = model.geometry.check_free_nodes()
duplicates = model.geometry.check_duplicate_nodes()
duplicate_elements = model.geometry.check_duplicate_elements()
```

---

## 6. Material and Section Properties

### 6.1 Materials

#### Creating Uniaxial Materials

```python
# Steel material
model.properties.create_uniaxial_material(
    tag=1,
    name="Steel_Grade60",
    material_type="Steel01",
    material_args={
        "Fy": 420e6,        # Yield strength (Pa)
        "E0": 200e9,        # Elastic modulus (Pa)
        "b": 0.01           # Strain hardening ratio
    }
)

# Concrete material
model.properties.create_uniaxial_material(
    tag=2,
    name="Concrete_C30",
    material_type="Concrete01",
    material_args={
        "fpc": -30e6,       # Compressive strength (Pa)
        "epsc0": -0.002,    # Strain at peak stress
        "fpcu": -6e6,       # Crushing strength
        "epsU": -0.005      # Ultimate strain
    }
)
```

### 6.2 Sections

#### Elastic Sections

```python
# Rectangular section
model.properties.create_elastic_section(
    tag=1,
    name="Column_300x300",
    structural_element_type="column",
    section_shape="rectangle",
    shape_params={"width": 0.3, "height": 0.3},
    E_mod=30e9,
    G_mod=12e9,
    rotate_angle=0,
    section_shear=False
)

# I-section
model.properties.create_elastic_section(
    tag=2,
    name="I_Beam",
    structural_element_type="beam",
    section_shape="i_section",
    shape_params={
        "width": 0.2,
        "height": 0.4,
        "flange_thickness": 0.02,
        "web_thickness": 0.01
    },
    E_mod=200e9,
    G_mod=80e9
)

# Circular section
model.properties.create_elastic_section(
    tag=3,
    name="Circular_Column",
    structural_element_type="column",
    section_shape="circular",
    shape_params={"radius": 0.15, "num_points": 32},
    E_mod=30e9,
    G_mod=12e9
)

# User-defined section
model.properties.create_elastic_section(
    tag=4,
    name="Custom_Section",
    structural_element_type="beam",
    section_shape="user_section",
    shape_params={
        "outline_points": [
            [0, 0], [0.3, 0], [0.3, 0.4], 
            [0.2, 0.4], [0.2, 0.1], [0, 0.1], [0, 0]
        ],
        "hole_points": [
            [[0.1, 0.05], [0.15, 0.05], [0.15, 0.08], [0.1, 0.08], [0.1, 0.05]]
        ]
    },
    E_mod=30e9,
    G_mod=12e9
)
```

#### Fiber Sections

```python
# Reinforced concrete column
rebar_points = {
    "corner_bars": {
        "points": [
            (0.05, 0.05), (0.25, 0.05),
            (0.25, 0.25), (0.05, 0.25)
        ],
        "dia": 0.020,           # 20mm bars
        "mat_tag": 1,           # Steel material
        "color": "#ff0000"
    }
}

rebar_lines = {
    "side_bars": {
        "points": [(0.05, 0.15), (0.25, 0.15)],
        "dia": 0.016,
        "n": 3,                 # 3 bars along line
        "mat_tag": 1,
        "color": "#ff0000"
    }
}

model.properties.create_fiber_section(
    tag=10,
    name="RC_Column_300x300",
    structural_element_type="column",
    section_shape="rectangle",
    shape_params={"width": 0.3, "height": 0.3},
    section_cover=0.04,         # 40mm cover
    cover_mat_tag=2,            # Concrete cover material
    core_mat_tag=3,             # Concrete core material
    rebar_points=rebar_points,
    rebar_lines=rebar_lines,
    G=12e9
)

# Visualize the section
section = model.properties.sections["RC_Column_300x300"]
section.visualize(fill=True, show_legend=True)
```

### 6.3 Beam Integration

#### Standard Integration Methods

```python
# Lobatto integration (most common)
integration = BeamIntegration.Lobatto(
    tag=1,
    sec_tag=1,
    num_points=5
)
model.properties.add_beam_integration(integration)

# Legendre integration
integration = BeamIntegration.Legendre(
    tag=2,
    sec_tag=1,
    num_points=5
)

# Newton-Cotes integration
integration = BeamIntegration.NewtonCotes(
    tag=3,
    sec_tag=1,
    num_points=5
)
```

#### Plastic Hinge Integration

```python
# Hinge at element ends with interior elastic region
integration = BeamIntegration.HingeRadau(
    tag=10,
    sec_i=10,           # Hinge section at node I
    lp_i=0.5,           # Plastic hinge length at I
    sec_j=10,           # Hinge section at node J
    lp_j=0.5,           # Plastic hinge length at J
    sec_e=1             # Elastic section for interior
)
model.properties.add_beam_integration(integration)
```

#### User-Defined Integration

```python
# Custom integration points
integration = BeamIntegration.UserDefined(
    tag=20,
    num_points=4,
    sec_tags=[1, 1, 1, 1],
    locs=[0.1, 0.3, 0.7, 0.9],
    wts=[0.25, 0.25, 0.25, 0.25]
)
```

---

## 7. Constraints

### 7.1 Single-Point Constraints (Boundary Conditions)

```python
# Fixed support (all DOFs constrained)
model.constraints.create_constraint(
    node_tag=1,
    dx=1, dy=1, dz=1,    # Translations fixed
    rx=1, ry=1, rz=1     # Rotations fixed
)

# Pinned support (translations fixed, rotations free)
model.constraints.create_constraint(
    node_tag=2,
    dx=1, dy=1, dz=1,
    rx=0, ry=0, rz=0
)

# Roller support (vertical translation fixed only)
model.constraints.create_constraint(
    node_tag=3,
    dx=0, dy=0, dz=1,
    rx=0, ry=0, rz=0
)
```

### 7.2 Multi-Point Constraints

#### EqualDOF Constraints

```python
# Couple specific DOFs between two nodes
model.constraints.create_equal_dof(
    retained_node=1,      # Master node
    constrained_node=2,   # Slave node
    dofs=[1, 2, 3]       # Couple X, Y, Z translations
)
```

#### Rigid Diaphragm

```python
# Create rigid floor diaphragm
floor_nodes = [10, 11, 12, 13, 14, 15]

model.constraints.create_rigid_diaphragm(
    direction=3,          # Rigid in XY plane (perpendicular to Z)
    master_node=10,       # Master node (typically at floor center)
    slave_nodes=floor_nodes[1:]
)
```

#### Rigid Link

```python
# Create rigid link between two nodes
model.constraints.create_rigid_link(
    link_type="beam",     # "bar" or "beam"
    master_node=1,
    slave_node=2
)
```

---

## 8. Loading

### 8.1 Time Series

#### Constant Time Series

```python
# Constant load factor
ts = model.loading.create_constant_time_series(
    tag=1,
    factor=1.0
)
```

#### Linear Time Series

```python
# Linearly varying load factor
ts = model.loading.create_linear_time_series(
    tag=2,
    factor=1.0
)
```

#### Path Time Series

```python
import numpy as np

# Define time history
time = np.linspace(0, 10, 1000)
values = np.sin(2 * np.pi * time)

ts = model.loading.create_path_time_series(
    tag=3,
    time=time.tolist(),
    values=values.tolist(),
    factor=1.0
)

# Or from file
ts = model.loading.create_path_time_series(
    tag=4,
    file_path="ground_motion.txt",
    dt=0.01,
    factor=9.81  # Scale to m/s²
)
```

### 8.2 Load Patterns

#### Plain Load Pattern

```python
# Create load pattern with time series
pattern = model.loading.create_load_pattern(
    tag=1,
    time_series=ts
)

# Add nodal loads
pattern.add_node_load(
    node_tag=10,
    fx=10000,    # Force in X (N)
    fy=0,
    fz=-50000,   # Force in Z (N)
    mx=0, my=0, mz=0
)

# Add uniform beam load
pattern.add_beam_uniform_load(
    element_tags=[1, 2, 3],
    Wz=-5000,    # Distributed load (N/m) in local z
    Wy=0         # Distributed load (N/m) in local y
)

# Add point load on beam
pattern.add_beam_point_load(
    element_tags=[4],
    Pz=-10000,   # Point load (N) in local z
    xL=0.5       # Location (0 to 1)
)
```

#### Uniform Excitation (Ground Motion)

```python
# Load ground motion data
import numpy as np

# Read acceleration time history
accel_data = np.loadtxt("earthquake.txt")
time = accel_data[:, 0]
accel = accel_data[:, 1]

# Create time series
accel_ts = model.loading.create_path_time_series(
    tag=100,
    time=time.tolist(),
    values=accel.tolist(),
    factor=1.0
)

# Create uniform excitation pattern
eq_pattern = model.loading.create_uniform_excitation_pattern(
    tag=100,
    direction=1,              # X direction
    time_series=accel_ts
)
```

#### Multiple Support Excitation

```python
# For differential support motion
ms_pattern = model.loading.create_multiple_support_pattern(tag=200)

# Define ground motion at support location 1
model.loading.add_plain_ground_motion(
    pattern=ms_pattern,
    gm_tag=1,
    accel_series_tag=100
)

# Define ground motion at support location 2
model.loading.add_plain_ground_motion(
    pattern=ms_pattern,
    gm_tag=2,
    accel_series_tag=101
)

# Apply imposed motions to support nodes
model.loading.add_imposed_motion(
    pattern=ms_pattern,
    node_tag=1,
    dof=1,           # X direction
    gm_tag=1
)

model.loading.add_imposed_motion(
    pattern=ms_pattern,
    node_tag=100,
    dof=1,
    gm_tag=2
)
```

### 8.3 Gravity Loads

```python
# Create gravity load pattern
gravity_ts = model.loading.create_constant_time_series(tag=1)
gravity_pattern = model.loading.create_load_pattern(tag=1, time_series=gravity_ts)

# Apply self-weight to elements as uniform loads
# Concrete density: 2400 kg/m³, g = 9.81 m/s²
# For 0.3m x 0.3m column: W = 2400 * 0.09 * 9.81 = 2119 N/m

gravity_pattern.add_beam_uniform_load(
    element_tags=[1, 2, 3, 4],  # All columns
    Wz=-2119,  # Negative for downward
    Wx=0
)
```

---

## 9. Analysis

### 9.1 Modal Analysis

```python
# Run eigenvalue analysis
modal_results = model.analysis.run_modal_analysis(
    num_modes=10,
    odb_tag="modal",
    solver="-genBandArpack"
)

# Access results
periods = modal_results["period"]
frequencies = modal_results["frequency"]
eigenvalues = modal_results["eigen_values"]

print(f"First period: {periods[0]:.3f} seconds")
print(f"Second period: {periods[1]:.3f} seconds")
```

### 9.2 Gravity Analysis

```python
# Run gravity analysis first (common practice)
gravity_odb = model.analysis.run_gravity_analysis(
    load_pattern_tag=1,
    n_steps=10,
    output_odb_tag="gravity",
    show_progress=True
)

# Model state is maintained for subsequent analyses
```

### 9.3 Static Analysis

```python
# Run static pushover or load case
static_odb = model.analysis.run_static_analysis(
    load_pattern_tag=2,
    n_steps=20,
    output_odb_tag="static",
    show_progress=True
)
```

### 9.4 Pushover Analysis

```python
# Define displacement protocol
target_displacement = [0.0, 0.01, 0.02, 0.03, 0.04, 0.05]

pushover_odb = model.analysis.run_pushover_analysis(
    load_pattern_tag=2,
    control_node=10,          # Node to control
    control_dof=1,            # X direction
    target_protocol=target_displacement,
    max_step=0.001,           # Maximum step size
    output_odb_tag="pushover"
)
```

### 9.5 Time History Analysis

```python
# Prepare time history data
time_history = {
    "time": time_array,
    "accel": accel_array
}

# Run time history analysis
th_odb = model.analysis.run_time_history_analysis(
    time_history=time_history,
    dt=0.01,                  # Time step
    n_steps=len(time_array),
    eigenvalues=modal_results["eigen_values"],  # From modal analysis
    damping_ratio=0.05,       # 5% damping
    odb_tag="timehistory",
    direction=1,              # X direction
    scale_factor=9.81,        # Scale to m/s²
    pattern_type="UniformExcitation"
)
```

### 9.6 Analysis with Custom Parameters

```python
# Custom analysis parameters
custom_params = {
    "system": "UmfPack",
    "constraints": "Transformation",
    "numberer": "RCM",
    "test_type": "EnergyIncr",
    "test_tolerance": 1.0e-6,
    "test_iterations": 50,
    "algorithm": "Newton"
}

odb = model.analysis.run_static_analysis(
    load_pattern_tag=1,
    n_steps=10,
    analysis_params=custom_params
)
```

### 9.7 Sequential Analysis Stages

```python
# Stage 1: Gravity
gravity_odb = model.analysis.run_gravity_analysis(
    load_pattern_tag=1,
    n_steps=10
)

# Stage 2: Modal analysis under gravity
modal_results = model.analysis.run_modal_analysis(num_modes=5)

# Stage 3: Time history
th_odb = model.analysis.run_time_history_analysis(
    time_history=earthquake_data,
    dt=0.01,
    n_steps=1000,
    eigenvalues=modal_results["eigen_values"],
    damping_ratio=0.05
)
```

---

## 10. Visualization

### 10.1 Model Visualization

```python
# Basic model visualization
fig = model.visualization.visualize_model(
    show_nodes=True,
    show_elements=True,
    show_local_axes=True,
    show_bc=True,
    cpos="iso"
)
```

### 10.2 Deformed Shape

```python
# Visualize deformed shape
fig = model.visualization.visualize_deformation(
    odb_tag="static",
    scale_factor=10.0,
    show_undeformed=True,
    resp_type="disp",
    resp_dof="UX,UY,UZ",
    slides=True
)
```

### 10.3 Section Forces

```python
# Visualize internal forces
force_figs = model.visualization.visualize_section_forces(
    odb_tag="static",
    section_forces=["N", "VY", "VZ", "T", "MY", "MZ"]
)

# Display individual force component
force_figs["MY"].show()  # Show bending moment about Y
```

### 10.4 Section Visualization

```python
# Visualize fiber section
section = model.properties.sections["RC_Column_300x300"]
fig = section.visualize(
    fill=True,
    show_legend=True,
    aspect_ratio=1.0
)
```

---

## 11. Import/Export

### 11.1 Exporting to DXF

```python
# Export model geometry to DXF
model.io.export_to_dxf("model_output.dxf")
```

### 11.2 Importing from DXF

```python
# Import model from DXF file
stats = model.io.import_from_dxf(
    filename="building_model.dxf",
    layer_mapping={
        "COLUMNS": "column",
        "BEAMS_X": "beam_x",
        "BEAMS_Y": "beam_y",
        "WALLS": "wall"
    },
    priorities=["X+", "Y+", "Z+"],  # Sort order
    start_id_nodes=1000,
    start_id_elements=2000,
    merge_nodes=True,
    remove_duplicates=True,
    remove_free_nodes=True
)

print(f"Imported {stats['nodes']} nodes")
print(f"Imported {stats['elements']} elements")

# Convert geometric lines to structural elements
model.geometry.convert_line_elements(
    section_mapping={
        "column": "Column_Section",
        "beam_x": "Beam_Section",
        "beam_y": "Beam_Section"
    },
    element_class="forceBeamColumn",
    integration_tag=1
)
```

---

## 12. Advanced Features

### 12.1 Direct OpenSees Command Execution

```python
# Execute OpenSees commands directly
result = model.execute_ops_command(
    "nodeCoord",
    101,
    auto_initialize=True
)

# With keyword arguments
model.execute_ops_command(
    "element",
    "zeroLength",
    1001, 10, 11,
    **{
        "-mat": [1, 2, 3],
        "-dir": [1, 2, 3],
        "-orient": [1, 0, 0, 0, 1, 0]
    },
    update_model_state=True
)
```

### 12.2 Force Release and Manual Updates

```python
# Release model for advanced modifications
model.force_release_model()

# Make modifications using OpenSees directly
# User is responsible for consistency

# Update specific components
model.user_update_materials()
model.user_update_sections()
model.user_update_elements()

# Or update everything
model.user_update_all()
```

### 12.3 Smart Analysis Parameters

```python
# Configure SmartAnalyze for difficult analyses
smart_params = {
    "testType": "EnergyIncr",
    "testTol": 1.0e-8,
    "testIterTimes": 50,
    "tryAddTestTimes": True,
    "testIterTimesMore": [100, 200],
    "tryAlterAlgoTypes": True,
    "algoTypes": [40, 10, 20, 30, 50, 60],
    "relaxation": 0.5,
    "minStep": 1.0e-6
}

pushover_odb = model.analysis.run_pushover_analysis(
    load_pattern_tag=2,
    control_node=10,
    control_dof=1,
    target_protocol=[0, 0.05],
    max_step=0.001,
    smart_analyze_params=smart_params
)
```

### 12.4 Multiple Support Excitation

```python
# For bridges, spatial variation of ground motion
support_nodes = [1, 2, 5, 10]

th_odb = model.analysis.run_time_history_analysis(
    time_history={"time": time, "accel": accel},
    dt=0.01,
    n_steps=1000,
    pattern_type="MultipleSupport",
    support_nodes=support_nodes,
    direction=1  # X direction
)
```

---

## 13. Best Practices

### 13.1 Model Organization

```python
# Use descriptive names
model.properties.create_elastic_section(
    tag=1,
    name="Exterior_Column_400x400",  # Clear description
    structural_element_type="column",
    ...
)

# Organize elements by groups
model.geometry.add_to_element_group(element_id=1, group_name="exterior_columns")
model.geometry.add_to_element_group(element_id=2, group_name="interior_columns")
```

### 13.2 Units

Always use consistent units throughout your model:

**Recommended: SI units (N, m, kg, s)**
- Forces: Newtons (N)
- Lengths: Meters (m)
- Stresses: Pascals (Pa) or N/m²
- Mass: kg
- Density: kg/m³
- Gravity: 9.81 m/s²

```python
# Example with clear units
E_concrete = 30e9  # Pa (30 GPa)
fy_steel = 420e6   # Pa (420 MPa)
column_width = 0.4  # m
beam_load = -12000  # N/m
gravity = 9.81      # m/s²
```

### 13.3 Analysis Workflow

```python
# 1. Build model
model.build_model()

# 2. Check model
free_nodes = model.geometry.check_free_nodes()
if free_nodes:
    print(f"Warning: {len(free_nodes)} free nodes found")

# 3. Run gravity (if needed)
gravity_odb = model.analysis.run_gravity_analysis(...)

# 4. Run modal analysis
modal_results = model.analysis.run_modal_analysis(...)

# 5. Run main analysis
main_odb = model.analysis.run_time_history_analysis(...)
```

### 13.4 Error Handling

```python
try:
    model.build_model()
except RuntimeError as e:
    print(f"Error building model: {e}")
    # Handle error

try:
    odb = model.analysis.run_static_analysis(...)
except Exception as e:
    print(f"Analysis failed: {e}")
    # Handle failure
```

---

## 14. Troubleshooting

### 14.1 Common Issues

#### Model Won't Build

**Problem**: RuntimeError when calling `build_model()`

**Solutions**:
- Check for unconverted line elements: `model.geometry.has_line_elements()`
- Verify all sections are defined
- Check material tags match section definitions
- Ensure beam integration tags are correct

#### Analysis Fails to Converge

**Problem**: Analysis returns negative result

**Solutions**:
```python
# Use more analysis steps
n_steps=100  # Instead of 10

# Adjust tolerances
analysis_params = {
    "test_tolerance": 1.0e-4,  # Relax tolerance
    "test_iterations": 100      # More iterations
}

# Use SmartAnalyze with more algorithms
smart_params = {
    "tryAlterAlgoTypes": True,
    "algoTypes": [40, 10, 20, 30, 50, 60]
}
```

#### Missing Mass for Dynamic Analysis

**Problem**: Modal analysis fails or produces zero frequencies

**Solution**:
```python
# Add mass to nodes
for node in model.geometry.nodes.values():
    node.add_mass(
        mass_x=1000,
        mass_y=1000,
        mass_z=1000
    )

# Rebuild model
model.build_model()
```

#### Visualization Issues

**Problem**: Empty or incorrect visualization

**Solutions**:
- Ensure model is built: `model.build_model()`
- Check odb_tag matches analysis output
- Verify analysis completed successfully

### 14.2 Performance Tips

```python
# Use efficient solvers for large models
analysis_params = {
    "system": "UmfPack",  # Fast sparse solver
    "numberer": "RCM"     # Reduce bandwidth
}

# Compress output data
odb.save_response(zlib=True)

# Limit output steps for large analyses
# Record every 10 steps instead of every step
```

### 14.3 Debugging

```python
# Enable verbose logging
model.params['verbose'] = True
model.params['debug'] = True

# Check model statistics
print(f"Nodes: {len(model.geometry.nodes)}")
print(f"Elements: {len(model.geometry.elements)}")
print(f"Materials: {len(model.properties.materials)}")
print(f"Sections: {len(model.properties.sections)}")

# Visualize before analysis
model.visualization.visualize_model()
```

---

## Appendix A: Complete Example - 3D Frame Building

```python
from replicaxlite import StructuralModel
import numpy as np

# Create model
model = StructuralModel("3D_Frame_Building")

# Define materials
model.properties.create_uniaxial_material(
    tag=1, name="Concrete", material_type="Concrete01",
    material_args={"fpc": -30e6, "epsc0": -0.002, 
                   "fpcu": -6e6, "epsU": -0.005}
)

model.properties.create_uniaxial_material(
    tag=2, name="Steel", material_type="Steel01",
    material_args={"Fy": 420e6, "E0": 200e9, "b": 0.01}
)

# Define sections
model.properties.create_fiber_section(
    tag=1, name="Column_500x500",
    structural_element_type="column",
    section_shape="rectangle",
    shape_params={"width": 0.5, "height": 0.5},
    section_cover=0.05,
    cover_mat_tag=1, core_mat_tag=1,
    rebar_points={
        "corners": {
            "points": [(0.08, 0.08), (0.42, 0.08),
                      (0.42, 0.42), (0.08, 0.42)],
            "dia": 0.025, "mat_tag": 2, "color": "#ff0000"
        }
    },
    G=12e9
)

model.properties.create_elastic_section(
    tag=2, name="Beam_300x600",
    structural_element_type="beam",
    section_shape="rectangle",
    shape_params={"width": 0.3, "height": 0.6},
    E_mod=30e9, G_mod=12e9
)

# Beam integration
integration = model.properties.create_beam_integration(
    tag=1, integration_type="Lobatto",
    structural_element_use="column",
    section_tag=1, num_points=5
)

# Create grid
model.geometry.create_grid(
    x_coords=[0, 5, 10],
    y_coords=[0, 5, 10],
    z_coords=[0, 3, 6, 9],
    create_columns=True,
    create_beams=True
)

# Convert to structural elements
model.geometry.convert_line_elements(
    section_mapping={
        "column": "Column_500x500",
        "beam_x": "Beam_300x600",
        "beam_y": "Beam_300x600"
    },
    integration_tag=1
)

# Fix base
for node in model.geometry.get_elements_by_floor(0.0):
    start_node = node.get_start_node()
    model.constraints.create_constraint(
        start_node.tag, 1, 1, 1, 1, 1, 1
    )

# Add mass
for node in model.geometry.nodes.values():
    if node.z > 0.1:  # Not base
        node.add_mass(5000, 5000, 5000, 0, 0, 0)

# Build model
model.build_model()

# Analyses
modal = model.analysis.run_modal_analysis(num_modes=5)
print(f"Periods: {modal['period']}")

# Visualize
model.visualization.visualize_model()
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