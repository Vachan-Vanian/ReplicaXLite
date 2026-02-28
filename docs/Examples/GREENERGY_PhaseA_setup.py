from replicaxlite import StructuralModel
import numpy as np
import opstool as opst

model = StructuralModel("Greenergy-PhaseA-Setup Units: (kN, KPa, m, tonne)")

# Create materials
# Steel from experimental results
steel_s500_mat = model.properties.create_uniaxial_material(tag=1, name='s500',
                                                           material_type='Steel02',
                                                           material_args={
                                                               'Fy': 564000,     
                                                               'E0': 195.2e6,    
                                                               'b': 0.01,
                                                               '*params': [18.5, 0.925, 0.15]
                                                           })

# Base beam
base_beam_cover_mat = model.properties.create_uniaxial_material(tag=2, name='base_beam_cover',
                                                            material_type='Concrete02',
                                                            material_args={
                                                                'fpc': -36760,    
                                                                'epsc0': -0.002,
                                                                'fpcu': -7350,    
                                                                'epsU': -0.0035, 
                                                                'lambda': 0.1,
                                                                'ft': 600,        
                                                                'Ets': 300000     
                                                            })

base_beam_core_mat = model.properties.create_uniaxial_material(tag=3, name='base_beam_core',
                                                            material_type='Concrete02',
                                                            material_args={
                                                                'fpc': -37760,     
                                                                'epsc0': -0.002,
                                                                'fpcu': -7350,     
                                                                'epsU': -0.004, 
                                                                'lambda': 0.1,
                                                                'ft': 680,         
                                                                'Ets': 340000      
                                                            })

# Column
column_cover_mat = model.properties.create_uniaxial_material(tag=4, name='column_cover',
                                                            material_type='Concrete02',
                                                            material_args={
                                                                'fpc': -24820,     
                                                                'epsc0': -0.002,
                                                                'fpcu': -4960,     
                                                                'epsU': -0.0035, 
                                                                'lambda': 0.1,
                                                                'ft': 500,         
                                                                'Ets': 250000      
                                                            })

column_core_mat = model.properties.create_uniaxial_material(tag=5, name='column_core',
                                                            material_type='Concrete02',
                                                            material_args={
                                                                'fpc': -25820,     
                                                                'epsc0': -0.002,
                                                                'fpcu': -4960,     
                                                                'epsU': -0.004, 
                                                                'lambda': 0.1,
                                                                'ft': 590,         
                                                                'Ets': 290000      
                                                            })

# Slab
slab_cover_mat = model.properties.create_uniaxial_material(tag=6, name='slab_cover',
                                                            material_type='Concrete02',
                                                            material_args={
                                                                'fpc': -31630,     
                                                                'epsc0': -0.002,
                                                                'fpcu': -6330,     
                                                                'epsU': -0.0035, 
                                                                'lambda': 0.1,
                                                                'ft': 560,         
                                                                'Ets': 280000      
                                                            })

slab_core_mat = model.properties.create_uniaxial_material(tag=7, name='slab_core',
                                                            material_type='Concrete02',
                                                            material_args={
                                                                'fpc': -32630,     
                                                                'epsc0': -0.002,
                                                                'fpcu': -6330,     
                                                                'epsU': -0.004, 
                                                                'lambda': 0.1,
                                                                'ft': 590,         
                                                                'Ets': 290000      
                                                            })


# infill
infill_mat = model.properties.create_uniaxial_material(tag=8, name='infill',
                                                            material_type='Concrete02',
                                                            material_args={
                                                                'fpc': -1150,      
                                                                'epsc0': -0.0219,
                                                                'fpcu': -690,      
                                                                'epsU': -0.0689, 
                                                                'lambda': 0.1, 
                                                                'ft': 1.0,
                                                                'Ets': 100.0
                                                            })


# Create fiber sections
# Column section
width = 0.13
height = 0.13
cover_depth = 0.032
lrebar_diameter = 8/1000
top_rebar_line = [
    (cover_depth + lrebar_diameter/2, height - cover_depth - lrebar_diameter/2),
    (width - cover_depth - lrebar_diameter/2, height - cover_depth - lrebar_diameter/2)
]
bottom_rebar_line = [
    (cover_depth + lrebar_diameter/2, cover_depth + lrebar_diameter/2),
    (width - cover_depth - lrebar_diameter/2, cover_depth + lrebar_diameter/2)
]

fs_column_section = model.properties.create_fiber_section(tag=1, name='fs_column_section', structural_element_type='column',
                                                            section_shape='rectangle',
                                                            shape_params={'width': width, 'height': height},
                                                            section_cover=cover_depth,
                                                            core_mat_tag=column_core_mat.tag,
                                                            cover_mat_tag=column_cover_mat.tag,
                                                            rebar_lines = {
                                                                f"top_rebars #{lrebar_diameter*1000}": {
                                                                    "points": top_rebar_line,
                                                                    "dia": lrebar_diameter,
                                                                    "n": 2,
                                                                    "mat_tag": steel_s500_mat.tag,
                                                                    "color": '#000000'
                                                                },
                                                                f"bottom_rebars #{lrebar_diameter*1000}": {
                                                                    "points": bottom_rebar_line,
                                                                    "dia": lrebar_diameter,
                                                                    "n": 2,
                                                                    "mat_tag": steel_s500_mat.tag,
                                                                    "color": '#f00000'
                                                                },
                                                            },
                                                            GJ=1e10
                                                        )
# fig = fs_column_section.visualize()
# plt.show()

# Beam section
width_e = 0.343
width = 0.2
height = 0.2
cover_depth = 0.02
lrebar_diameter = 10/1000

# Calculate the offset to center rebars in the wider section
offset = (width_e - width)/2

# Adjusted rebar positions with offset
top_rebar_line = [
    (offset + cover_depth + lrebar_diameter/2, height - cover_depth - lrebar_diameter/2),
    (offset + width - cover_depth - lrebar_diameter/2, height - cover_depth - lrebar_diameter/2)
]
bottom_rebar_line = [
    (offset + cover_depth + lrebar_diameter/2, cover_depth + lrebar_diameter/2),
    (offset + width - cover_depth - lrebar_diameter/2, cover_depth + lrebar_diameter/2)
]
mid_rebars_line = [
    (offset + cover_depth + lrebar_diameter/2, ((height - cover_depth - lrebar_diameter/2)+(cover_depth + lrebar_diameter/2))/2),
    (offset + width - cover_depth - lrebar_diameter/2, ((height - cover_depth - lrebar_diameter/2)+(cover_depth + lrebar_diameter/2))/2)
]

slab_rebars_top_line = [
    (cover_depth + lrebar_diameter/2, height - cover_depth - lrebar_diameter/2),
    (width_e - cover_depth - lrebar_diameter/2, height - cover_depth - lrebar_diameter/2)
]

slab_rebars_bottom_line = [
    (cover_depth + lrebar_diameter/2, cover_depth + lrebar_diameter/2),
    (width_e - cover_depth - lrebar_diameter/2, cover_depth + lrebar_diameter/2)
]

fs_beam_section = model.properties.create_fiber_section(tag=2, name='fs_beam_section', structural_element_type='beam',
                                                            section_shape='rectangle',
                                                            shape_params={'width': width_e, 'height': height},
                                                            section_cover=cover_depth,
                                                            core_mat_tag=slab_core_mat.tag,
                                                            cover_mat_tag=slab_cover_mat.tag,
                                                            rebar_lines = {
                                                                f"top_rebars #{lrebar_diameter*1000}": {
                                                                    "points": top_rebar_line,
                                                                    "dia": lrebar_diameter,
                                                                    "n": 3,
                                                                    "mat_tag": steel_s500_mat.tag,
                                                                    "color": '#000000'
                                                                },
                                                                f"bottom_rebars #{lrebar_diameter*1000}": {
                                                                    "points": bottom_rebar_line,
                                                                    "dia": lrebar_diameter,
                                                                    "n": 3,
                                                                    "mat_tag": steel_s500_mat.tag,
                                                                    "color": '#f00000'
                                                                },
                                                                f"mid_rebars #{lrebar_diameter*1000}": {
                                                                    "points": mid_rebars_line,
                                                                    "dia": lrebar_diameter,
                                                                    "n": 2,
                                                                    "mat_tag": steel_s500_mat.tag,
                                                                    "color": '#0014f0'
                                                                },
                                                                f"top_rebars_slab #{lrebar_diameter*1000}": {
                                                                    "points": slab_rebars_top_line,
                                                                    "dia": lrebar_diameter,
                                                                    "n": 2,
                                                                    "mat_tag": steel_s500_mat.tag,
                                                                    "color": '#00d4f0'
                                                                },
                                                                f"bottom_rebars_slab #{lrebar_diameter*1000}": {
                                                                    "points": slab_rebars_bottom_line,
                                                                    "dia": lrebar_diameter,
                                                                    "n": 2,
                                                                    "mat_tag": steel_s500_mat.tag,
                                                                    "color": '#b400f0'
                                                                },
                                                            },
                                                            GJ=1e10
                                                        )
# fig = fs_beam_section.visualize()
# plt.show()

# Base beam section
width = 0.2
height = 0.25
cover_depth = 0.02
lrebar_diameter = 14/1000
top_rebar_line = [
    (cover_depth + lrebar_diameter/2, height - cover_depth - lrebar_diameter/2),
    (width - cover_depth - lrebar_diameter/2, height - cover_depth - lrebar_diameter/2)
]
bottom_rebar_line = [
    (cover_depth + lrebar_diameter/2, cover_depth + lrebar_diameter/2),
    (width - cover_depth - lrebar_diameter/2, cover_depth + lrebar_diameter/2)
]

mid_rebars_line = [
    (cover_depth + lrebar_diameter/2, ((height - cover_depth - lrebar_diameter/2)+(cover_depth + lrebar_diameter/2))/2),
    (width - cover_depth - lrebar_diameter/2, ((height - cover_depth - lrebar_diameter/2)+(cover_depth + lrebar_diameter/2))/2)
]

fs_base_beam_section = model.properties.create_fiber_section(tag=3, name='fs_base_beam_section', structural_element_type='beam',
                                                                section_shape='rectangle',
                                                                shape_params={'width': width, 'height': height},
                                                                section_cover=cover_depth,
                                                                core_mat_tag=base_beam_core_mat.tag,
                                                                cover_mat_tag=base_beam_cover_mat.tag,
                                                                rebar_lines = {
                                                                    f"top_rebars #{lrebar_diameter*1000}": {
                                                                        "points": top_rebar_line,
                                                                        "dia": lrebar_diameter,
                                                                        "n": 3,
                                                                        "mat_tag": steel_s500_mat.tag,
                                                                        "color": '#000000'
                                                                    },
                                                                    f"bottom_rebars #{lrebar_diameter*1000}": {
                                                                        "points": bottom_rebar_line,
                                                                        "dia": lrebar_diameter,
                                                                        "n": 3,
                                                                        "mat_tag": steel_s500_mat.tag,
                                                                        "color": '#f00000'
                                                                    },
                                                                    f"mid_rebars #{lrebar_diameter*1000}": {
                                                                        "points": mid_rebars_line,
                                                                        "dia": lrebar_diameter,
                                                                        "n": 2,
                                                                        "mat_tag": steel_s500_mat.tag,
                                                                        "color": '#0014f0'
                                                                    },
                                                                },
                                                                GJ=1e10
                                                                )
# fig = fs_base_beam_section.visualize()
# plt.show()

# slab small section
width = 0.2
height = 0.2
cover_depth = 0.02
lrebar_diameter = 10/1000
top_rebar_line = [
    (cover_depth + lrebar_diameter/2, height - cover_depth - lrebar_diameter/2),
    (width - cover_depth - lrebar_diameter/2, height - cover_depth - lrebar_diameter/2)
]
bottom_rebar_line = [
    (cover_depth + lrebar_diameter/2, cover_depth + lrebar_diameter/2),
    (width - cover_depth - lrebar_diameter/2, cover_depth + lrebar_diameter/2)
]

fs_slab_small_section = model.properties.create_fiber_section(tag=4, name='fs_slab_small_section', structural_element_type='beam',
                                                            section_shape='rectangle',
                                                            shape_params={'width': width, 'height': height},
                                                            section_cover=cover_depth,
                                                            core_mat_tag=slab_core_mat.tag,
                                                            cover_mat_tag=slab_cover_mat.tag,
                                                            rebar_lines = {
                                                                f"top_rebars #{lrebar_diameter*1000}": {
                                                                    "points": top_rebar_line,
                                                                    "dia": lrebar_diameter,
                                                                    "n": 3,
                                                                    "mat_tag": steel_s500_mat.tag,
                                                                    "color": '#000000'
                                                                },
                                                                f"bottom_rebars #{lrebar_diameter*1000}": {
                                                                    "points": bottom_rebar_line,
                                                                    "dia": lrebar_diameter,
                                                                    "n": 3,
                                                                    "mat_tag": steel_s500_mat.tag,
                                                                    "color": '#f00000'
                                                                },
                                                            },
                                                            GJ=1e10
                                                        )
# fig = fs_slab_small_section.visualize()
# plt.show()

# beam solo section
width = 0.2
height = 0.2
cover_depth = 0.02
lrebar_diameter = 10/1000
top_rebar_line = [
    (cover_depth + lrebar_diameter/2, height - cover_depth - lrebar_diameter/2),
    (width - cover_depth - lrebar_diameter/2, height - cover_depth - lrebar_diameter/2)
]
bottom_rebar_line = [
    (cover_depth + lrebar_diameter/2, cover_depth + lrebar_diameter/2),
    (width - cover_depth - lrebar_diameter/2, cover_depth + lrebar_diameter/2)
]
mid_rebars_line = [
    (cover_depth + lrebar_diameter/2, ((height - cover_depth - lrebar_diameter/2)+(cover_depth + lrebar_diameter/2))/2),
    (width - cover_depth - lrebar_diameter/2, ((height - cover_depth - lrebar_diameter/2)+(cover_depth + lrebar_diameter/2))/2)
]

fs_beam_solo_section = model.properties.create_fiber_section(tag=5, name='fs_beam_solo_section', structural_element_type='beam',
                                                            section_shape='rectangle',
                                                            shape_params={'width': width, 'height': height},
                                                            section_cover=cover_depth,
                                                            core_mat_tag=slab_core_mat.tag,
                                                            cover_mat_tag=slab_cover_mat.tag,
                                                            rebar_lines = {
                                                                f"top_rebars #{lrebar_diameter*1000}": {
                                                                    "points": top_rebar_line,
                                                                    "dia": lrebar_diameter,
                                                                    "n": 3,
                                                                    "mat_tag": steel_s500_mat.tag,
                                                                    "color": '#000000'
                                                                },
                                                                f"bottom_rebars #{lrebar_diameter*1000}": {
                                                                    "points": bottom_rebar_line,
                                                                    "dia": lrebar_diameter,
                                                                    "n": 3,
                                                                    "mat_tag": steel_s500_mat.tag,
                                                                    "color": '#f00000'
                                                                },
                                                                f"mid_rebars #{lrebar_diameter*1000}": {
                                                                    "points": mid_rebars_line,
                                                                    "dia": lrebar_diameter,
                                                                    "n": 2,
                                                                    "mat_tag": steel_s500_mat.tag,
                                                                    "color": '#0014f0'
                                                                },
                                                            },
                                                            GJ=1e10
                                                        )
# fig = fs_beam_solo_section.visualize()
# plt.show()

# infill diagonal section
width = 0.263
height = 0.139
cover_depth = 0.00
lrebar_diameter = 2/1000
top_rebar_line = [
    (cover_depth + lrebar_diameter/2, height - cover_depth - lrebar_diameter/2),
    (width - cover_depth - lrebar_diameter/2, height - cover_depth - lrebar_diameter/2)
]
bottom_rebar_line = [
    (cover_depth + lrebar_diameter/2, cover_depth + lrebar_diameter/2),
    (width - cover_depth - lrebar_diameter/2, cover_depth + lrebar_diameter/2)
]
fs_infill_diagonal_section = model.properties.create_fiber_section(tag=6, name='fs_infill_diagonal_section', structural_element_type='beam',
                                                            section_shape='rectangle',
                                                            shape_params={'width': width, 'height': height},
                                                            section_cover=cover_depth,
                                                            core_mat_tag=infill_mat.tag,
                                                            cover_mat_tag=infill_mat.tag,
                                                            rebar_lines = {
                                                                f"top_rebars #{lrebar_diameter*1000}": {
                                                                    "points": top_rebar_line,
                                                                    "dia": lrebar_diameter,
                                                                    "n": 2,
                                                                    "mat_tag": steel_s500_mat.tag,
                                                                    "color": '#000000'
                                                                },
                                                                f"bottom_rebars #{lrebar_diameter*1000}": {
                                                                    "points": bottom_rebar_line,
                                                                    "dia": lrebar_diameter,
                                                                    "n": 2,
                                                                    "mat_tag": steel_s500_mat.tag,
                                                                    "color": '#f00000'
                                                                },
                                                            },
                                                            GJ=1e10
                                                        )
# fig = fs_infill_diagonal_section.visualize()
# plt.show()

# infill vertical section
width = 0.113
height = 0.139
cover_depth = 0.00
lrebar_diameter = 2/1000
top_rebar_line = [
    (cover_depth + lrebar_diameter/2, height - cover_depth - lrebar_diameter/2),
    (width - cover_depth - lrebar_diameter/2, height - cover_depth - lrebar_diameter/2)
]
bottom_rebar_line = [
    (cover_depth + lrebar_diameter/2, cover_depth + lrebar_diameter/2),
    (width - cover_depth - lrebar_diameter/2, cover_depth + lrebar_diameter/2)
]
fs_infill_vertical_section = model.properties.create_fiber_section(tag=7, name='fs_infill_vertical_section', structural_element_type='beam',
                                                            section_shape='rectangle',
                                                            shape_params={'width': width, 'height': height},
                                                            section_cover=cover_depth,
                                                            core_mat_tag=infill_mat.tag,
                                                            cover_mat_tag=infill_mat.tag,
                                                            rebar_lines = {
                                                                f"top_rebars #{lrebar_diameter*1000}": {
                                                                    "points": top_rebar_line,
                                                                    "dia": lrebar_diameter,
                                                                    "n": 2,
                                                                    "mat_tag": steel_s500_mat.tag,
                                                                    "color": '#000000'
                                                                },
                                                                f"bottom_rebars #{lrebar_diameter*1000}": {
                                                                    "points": bottom_rebar_line,
                                                                    "dia": lrebar_diameter,
                                                                    "n": 2,
                                                                    "mat_tag": steel_s500_mat.tag,
                                                                    "color": '#f00000'
                                                                },
                                                            },
                                                            GJ=1e10
                                                        )
# fig = fs_infill_vertical_section.visualize()
# plt.show()

# infill horizintal section
width = 0.091
height = 0.139
cover_depth = 0.00
lrebar_diameter = 0.5/1000
top_rebar_line = [
    (cover_depth + lrebar_diameter/2, height - cover_depth - lrebar_diameter/2),
    (width - cover_depth - lrebar_diameter/2, height - cover_depth - lrebar_diameter/2)
]
bottom_rebar_line = [
    (cover_depth + lrebar_diameter/2, cover_depth + lrebar_diameter/2),
    (width - cover_depth - lrebar_diameter/2, cover_depth + lrebar_diameter/2)
]
fs_infill_horizintal_section = model.properties.create_fiber_section(tag=8, name='fs_infill_horizontal_section', structural_element_type='beam',
                                                            section_shape='rectangle',
                                                            shape_params={'width': width, 'height': height},
                                                            section_cover=cover_depth,
                                                            core_mat_tag=infill_mat.tag,
                                                            cover_mat_tag=infill_mat.tag,
                                                            rebar_lines = {
                                                                f"top_rebars #{lrebar_diameter*1000}": {
                                                                    "points": top_rebar_line,
                                                                    "dia": lrebar_diameter,
                                                                    "n": 2,
                                                                    "mat_tag": steel_s500_mat.tag,
                                                                    "color": '#000000'
                                                                },
                                                                f"bottom_rebars #{lrebar_diameter*1000}": {
                                                                    "points": bottom_rebar_line,
                                                                    "dia": lrebar_diameter,
                                                                    "n": 2,
                                                                    "mat_tag": steel_s500_mat.tag,
                                                                    "color": '#f00000'
                                                                },
                                                            },
                                                            GJ=1e10
                                                        )
# fig = fs_infill_horizintal_section.visualize()
# plt.show()

# infill diagonal small section
width = 0.182
height = 0.139
cover_depth = 0.00
cover_depth = 0.00
lrebar_diameter = 2/1000
top_rebar_line = [
    (cover_depth + lrebar_diameter/2, height - cover_depth - lrebar_diameter/2),
    (width - cover_depth - lrebar_diameter/2, height - cover_depth - lrebar_diameter/2)
]
bottom_rebar_line = [
    (cover_depth + lrebar_diameter/2, cover_depth + lrebar_diameter/2),
    (width - cover_depth - lrebar_diameter/2, cover_depth + lrebar_diameter/2)
]
fs_infill_small_diagonal_section = model.properties.create_fiber_section(tag=9, name='fs_infill_small_diagonal_section', structural_element_type='beam',
                                                            section_shape='rectangle',
                                                            shape_params={'width': width, 'height': height},
                                                            section_cover=cover_depth,
                                                            core_mat_tag=infill_mat.tag,
                                                            cover_mat_tag=infill_mat.tag,
                                                            rebar_lines = {
                                                                f"top_rebars #{lrebar_diameter*1000}": {
                                                                    "points": top_rebar_line,
                                                                    "dia": lrebar_diameter,
                                                                    "n": 2,
                                                                    "mat_tag": steel_s500_mat.tag,
                                                                    "color": '#000000'
                                                                },
                                                                f"bottom_rebars #{lrebar_diameter*1000}": {
                                                                    "points": bottom_rebar_line,
                                                                    "dia": lrebar_diameter,
                                                                    "n": 2,
                                                                    "mat_tag": steel_s500_mat.tag,
                                                                    "color": '#f00000'
                                                                },
                                                            },
                                                            GJ=1e10
                                                        )
# fig = fs_infill_small_diagonal_section.visualize()
# plt.show()

# #-----------------------------------------

# Define the main structural nodes
main_nodes = {
    1: (-0.685,  0.685,  1.825), 
    2: (0.685,  0.685,  1.825),
    3: (0.685,  -0.685,  1.825),
    4: (-0.685,  -0.685,  1.825),
    
    5: (-0.685,  0.685,  1.225),
    6: (0.685,  0.685,  1.225),
    7: (0.685,  -0.685,  1.225),
    8: (-0.685,  -0.685,  1.225),
    
    9: (-0.685,  1.35,  1.225),
    10: (0.685,  1.35,  1.225),
    11: (1.35,  0.685,  1.225),
    12: (1.35,  -0.685,  1.225),
    13: (0.685,  -1.35,  1.225),
    14: (-0.685,  -1.35,  1.225),
    15: (-1.35,  -0.685,  1.225),
    16: (-1.35,  0.685,  1.225),
    
    17: (-0.685,  0.685,  0),
    18: (0.685,  0.685,  0),
    19: (0.685,  -0.685,  0),
    20: (-0.685,  -0.685,  0),
    
    21: (-0.685,  1.2,  0),
    22: (0.685,  1.2,  0),
    23: (1.2,  0.685,  0),
    24: (1.2,  -0.685,  0),
    25: (0.685,  -1.2,  0),
    26: (-0.685,  -1.2,  0),
    27: (-1.2,  -0.685,  0),
    28: (-1.2,  0.685,  0),

    29: (-0.342, 0.685, 1.225),      
    30: (0.685, 0, 1.225),
    31: (-0.342, -0.685, 1.225),  
    32: (-0.685, 0, 1.225),
    
    33: (-0.342, 0.685, 0),
    34: (0.685, 0, 0),         
    35: (-0.342, -0.685, 0),
    36: (-0.685, 0, 0),

    37: (-0.685,  0.685,  0.6125),
    38: (0.685,  0.685,  0.6125),
    39: (0.685,  -0.685,  0.6125),
    40: (-0.685,  -0.685,  0.6125),

    41: (-0.685,  0,  0.6125), 
    42: (-0.685,  0,  0.6125),
    43: (-0.685,  0,  0.6125),
    44: (-0.685,  0,  0.6125),

    45: (0.685,  0,  0.6125),
    46: (0.685,  0,  0.6125),
    47: (0.685,  0,  0.6125),
    48: (0.685,  0,  0.6125),

    49: (-0.5135,  -0.685,  0.6125),
    50: (-0.5135,  -0.685,  0.6125),

    53: (-0.5135,  0.685,  0.6125), 
    54: (-0.5135,  0.685,  0.6125),
}

# Add the nodes
for node_id, coords in main_nodes.items():
    model.geometry.create_node(node_id, *coords)

# Create elements - only the main structural elements
main_elements = {
    # Columns connecting floor to top (5-1, 6-2, 8-4, 7-3)
    1: (5, 1, 'column', 'column', 'fs_column_section'),
    2: (6, 2, 'column', 'column', 'fs_column_section'),
    3: (8, 4, 'column', 'column', 'fs_column_section'),
    4: (7, 3, 'column', 'column', 'fs_column_section'),

    # Columns from base to floor
    5: (17, 37, 'column', 'column', 'fs_column_section'),
    6: (37, 5, 'column', 'column', 'fs_column_section'),
    7: (18, 38, 'column', 'column', 'fs_column_section'),
    8: (38, 6, 'column', 'column', 'fs_column_section'),
    9: (19, 39, 'column', 'column', 'fs_column_section'),
    10: (39, 7, 'column', 'column', 'fs_column_section'),
    11: (20, 40, 'column', 'column', 'fs_column_section'),
    12: (40, 8, 'column', 'column', 'fs_column_section'),
    
    # Main beams at floor level
    13: (5, 29, 'beam', 'beam_x', 'fs_beam_section'),
    14: (29, 6, 'beam', 'beam_x', 'fs_beam_section'),
    15: (7, 30, 'beam', 'beam_y', 'fs_beam_section'),
    16: (30, 6, 'beam', 'beam_y', 'fs_beam_section'),
    17: (8, 31, 'beam', 'beam_x', 'fs_beam_section'),
    18: (31, 7, 'beam', 'beam_x', 'fs_beam_section'),
    19: (8, 32, 'beam', 'beam_y', 'fs_beam_section'),
    20: (32, 5, 'beam', 'beam_y', 'fs_beam_section'),
    
    # # Floor to outer edge connections
    21: (5, 9, 'beam', 'beam_balcony_y', 'fs_slab_small_section'),
    22: (9, 10, 'beam', 'beam_balcony_y', 'fs_slab_small_section'),
    23: (6, 10, 'beam', 'beam_balcony_x', 'fs_beam_solo_section'),
    24: (6, 11, 'beam', 'beam_balcony_x', 'fs_beam_solo_section'),
    25: (12, 11, 'beam', 'beam_balcony_y', 'fs_slab_small_section'),
    26: (7, 12, 'beam', 'beam_balcony_y', 'fs_beam_solo_section'),
    27: (13, 7, 'beam', 'beam_balcony_x', 'fs_beam_solo_section'),
    28: (14, 13, 'beam', 'beam_balcony_x', 'fs_slab_small_section'),
    29: (14, 8, 'beam', 'beam_balcony_x', 'fs_slab_small_section'),
    30: (15, 8, 'beam', 'beam_balcony_x', 'fs_beam_solo_section'),
    31: (15, 16, 'beam', 'beam_balcony_x', 'fs_slab_small_section'),
    32: (16, 5, 'beam', 'beam_balcony_x', 'fs_beam_solo_section'),

    # Base beams
    33: (17, 33, 'beam', 'beam_base_x', 'fs_base_beam_section'),
    34: (33, 18, 'beam', 'beam_base_x', 'fs_base_beam_section'),
    35: (19, 34, 'beam', 'beam_base_y', 'fs_base_beam_section'),
    36: (34, 18, 'beam', 'beam_base_y', 'fs_base_beam_section'),
    37: (20, 35, 'beam', 'beam_base_x', 'fs_base_beam_section'),
    38: (35, 19, 'beam', 'beam_base_x', 'fs_base_beam_section'),
    39: (20, 36, 'beam', 'beam_base_y', 'fs_base_beam_section'),
    40: (36, 17, 'beam', 'beam_base_y', 'fs_base_beam_section'),
    
    # Base to outer edge connections
    41: (28, 17, 'beam', 'beam_base_x', 'fs_base_beam_section'),
    42: (17, 21, 'beam', 'beam_base_y', 'fs_base_beam_section'),
    43: (18, 23, 'beam', 'beam_base_x', 'fs_base_beam_section'),
    44: (18, 22, 'beam', 'beam_base_y', 'fs_base_beam_section'),
    45: (19, 24, 'beam', 'beam_base_x', 'fs_base_beam_section'),
    46: (25, 19, 'beam', 'beam_base_y', 'fs_base_beam_section'),
    47: (27, 20, 'beam', 'beam_base_x', 'fs_base_beam_section'),
    48: (26, 20, 'beam', 'beam_base_y', 'fs_base_beam_section'),

    # INFILLS
    49: (17, 41, 'infill', 'infill', 'fs_infill_diagonal_section'), 
    50: (41, 8, 'infill', 'infill', 'fs_infill_diagonal_section'),
    51: (20, 42, 'infill', 'infill', 'fs_infill_diagonal_section'), 
    52: (42, 5, 'infill', 'infill', 'fs_infill_diagonal_section'),
    53: (36, 43, 'infill', 'infill', 'fs_infill_vertical_section'), 
    54: (43, 32, 'infill', 'infill', 'fs_infill_vertical_section'),
    55: (40, 44, 'infill', 'infill', 'fs_infill_horizontal_section'),
    56: (44, 37, 'infill', 'infill', 'fs_infill_horizontal_section'),

    57: (18, 45, 'infill', 'infill', 'fs_infill_diagonal_section'),
    58: (45, 7, 'infill', 'infill', 'fs_infill_diagonal_section'),
    59: (19, 46, 'infill', 'infill', 'fs_infill_diagonal_section'), 
    60: (46, 6, 'infill', 'infill', 'fs_infill_diagonal_section'),
    61: (34, 47, 'infill', 'infill', 'fs_infill_vertical_section'),
    62: (47, 30, 'infill', 'infill', 'fs_infill_vertical_section'),
    63: (39, 48, 'infill', 'infill', 'fs_infill_horizontal_section'),  
    64: (48, 38, 'infill', 'infill', 'fs_infill_horizontal_section'),

    65: (35, 49, 'infill', 'infill', 'fs_infill_small_diagonal_section'), 
    66: (49, 8, 'infill', 'infill', 'fs_infill_small_diagonal_section'),
    67: (20, 50, 'infill', 'infill', 'fs_infill_small_diagonal_section'),  
    68: (50, 31, 'infill', 'infill', 'fs_infill_small_diagonal_section'),

    69: (33, 53, 'infill', 'infill', 'fs_infill_small_diagonal_section'), 
    70: (53, 5, 'infill', 'infill', 'fs_infill_small_diagonal_section'),
    71: (17, 54, 'infill', 'infill', 'fs_infill_small_diagonal_section'),  
    72: (54, 29, 'infill', 'infill', 'fs_infill_small_diagonal_section'),



}

# Create beam integrations for each section
for i in range(1, 10):
    model.properties.create_beam_integration(
        tag=i,
        integration_type='Lobatto',
        structural_element_use='common',
        section_tag=i,
        num_points=5
    )

section_to_integration = {
    'fs_column_section': 1,
    'fs_beam_section': 2,
    'fs_base_beam_section': 3,
    'fs_slab_small_section': 4,
    'fs_beam_solo_section': 5,
    'fs_infill_diagonal_section': 6,
    'fs_infill_vertical_section': 7,
    'fs_infill_horizontal_section': 8,
    'fs_infill_small_diagonal_section': 9
}

# Then use it when creating elements:
for elem_id, elem_data in main_elements.items():
    start_node, end_node, struct_type, elem_group, section_name = elem_data
    
    # Raise error if section name not found in mapping
    if section_name not in section_to_integration:
        raise ValueError(f"Error at element {elem_id}: Section name '{section_name}' not found in integration mapping")
    
    model.geometry.create_element(
        tag=elem_id,
        start_node=start_node,
        end_node=end_node,
        element_type=struct_type,
        section_name=section_name,
        element_class='forceBeamColumn',
        integration_tag=section_to_integration[section_name]
    )
    model.geometry.add_to_element_group(element_id=elem_id, group_name=elem_group)

# Add fixed constraints to base nodes
fix_nodes = {
    17: (1, 1, 1, 0, 0, 0),
    18: (1, 1, 1, 0, 0, 0),
    19: (1, 1, 1, 0, 0, 0),
    20: (1, 1, 1, 0, 0, 0),
}

for node_id, constraints in fix_nodes.items():
    model.constraints.create_constraint(node_id, *constraints)

#Out of plane reponse should be the same for all different infills
model.constraints.create_equal_dof(41, 42, [1])
model.constraints.create_equal_dof(41, 43, [1])
model.constraints.create_equal_dof(41, 44, [1])

model.constraints.create_equal_dof(45, 46, [1])
model.constraints.create_equal_dof(45, 47, [1])
model.constraints.create_equal_dof(45, 48, [1])

model.constraints.create_equal_dof(49, 50, [2])

model.constraints.create_equal_dof(53, 54, [2])

model.constraints.create_rigid_diaphragm(3, 5, [6,7,8,
                                                 9,10,11,12,13,14,15,16,
                                                 29,30,31,32])


# Add nodal masses
node_masses = [

    # Top corners
    (1, 0.0105225, 0.0105225, 0.0105225, 0.0105225*0.01, 0.0105225*0.01, 0.0105225*0.01),
    (2, 0.0105225, 0.0105225, 0.0105225, 0.0105225*0.01, 0.0105225*0.01, 0.0105225*0.01),
    (3, 0.0105225, 0.0105225, 0.0105225, 0.0105225*0.01, 0.0105225*0.01, 0.0105225*0.01),
    (4, 0.0105225, 0.0105225, 0.0105225, 0.0105225*0.01, 0.0105225*0.01, 0.0105225*0.01),


    # Floor corners
    (5, 0.52891, 0.52891, 0.52891, 0.52891*0.01, 0.52891*0.01, 0.52891*0.01),
    (6, 0.52891, 0.52891, 0.52891, 0.52891*0.01, 0.52891*0.01, 0.52891*0.01),
    (7, 0.52891, 0.52891, 0.52891, 0.52891*0.01, 0.52891*0.01, 0.52891*0.01),
    (8, 0.52891, 0.52891, 0.52891, 0.52891*0.01, 0.52891*0.01, 0.52891*0.01),
    
    # Floor edges
    (9, 0.0971225, 0.0971225, 0.0971225, 0.0971225*0.01, 0.0971225*0.01, 0.0971225*0.01),
    (10,0.0971225, 0.0971225, 0.0971225, 0.0971225*0.01, 0.0971225*0.01, 0.0971225*0.01),
    (11, 0.10634, 0.10634, 0.10634, 0.10634*0.01, 0.10634*0.01, 0.10634*0.01),
    (12, 0.10634, 0.10634, 0.10634, 0.10634*0.01, 0.10634*0.01, 0.10634*0.01),
    (13, 0.0971225, 0.0971225, 0.0971225, 0.0971225*0.01, 0.0971225*0.01, 0.0971225*0.01),
    (14, 0.0971225, 0.0971225, 0.0971225, 0.0971225*0.01, 0.0971225*0.01, 0.0971225*0.01),
    (15, 0.10634, 0.10634, 0.10634, 0.10634*0.01, 0.10634*0.01, 0.10634*0.01),
    (16, 0.10634, 0.10634, 0.10634, 0.10634*0.01, 0.10634*0.01, 0.10634*0.01),
    
    # Base corners
    (17, 0.249491, 0.249491, 0.249491, 0.249491*0.01, 0.249491*0.01, 0.249491*0.01),
    (18, 0.249491, 0.249491, 0.249491, 0.249491*0.01, 0.249491*0.01, 0.249491*0.01),
    (19, 0.249491, 0.249491, 0.249491, 0.249491*0.01, 0.249491*0.01, 0.249491*0.01),
    (20, 0.249491, 0.249491, 0.249491, 0.249491*0.01, 0.249491*0.01, 0.249491*0.01),
    
    # Base edge
    (21, 0.0284895, 0.0284895, 0.0284895, 0.0284895*0.01, 0.0284895*0.01, 0.0284895*0.01),
    (22, 0.0284895, 0.0284895, 0.0284895, 0.0284895*0.01, 0.0284895*0.01, 0.0284895*0.01),
    (23, 0.0284895, 0.0284895, 0.0284895, 0.0284895*0.01, 0.0284895*0.01, 0.0284895*0.01),
    (24, 0.0284895, 0.0284895, 0.0284895, 0.0284895*0.01, 0.0284895*0.01, 0.0284895*0.01),
    (25, 0.0284895, 0.0284895, 0.0284895, 0.0284895*0.01, 0.0284895*0.01, 0.0284895*0.01),
    (26, 0.0284895, 0.0284895, 0.0284895, 0.0284895*0.01, 0.0284895*0.01, 0.0284895*0.01),
    (27, 0.0284895, 0.0284895, 0.0284895, 0.0284895*0.01, 0.0284895*0.01, 0.0284895*0.01),
    (28, 0.0284895, 0.0284895, 0.0284895, 0.0284895*0.01, 0.0284895*0.01, 0.0284895*0.01),

    # Infill
    (41, 0.02013, 0.02013, 0.02013, 0.02013*0.01, 0.02013*0.01, 0.02013*0.01),
    (42, 0.02013, 0.02013, 0.02013, 0.02013*0.01, 0.02013*0.01, 0.02013*0.01),
    (43, 0.02013, 0.02013, 0.02013, 0.02013*0.01, 0.02013*0.01, 0.02013*0.01),
    (44, 0.02013, 0.02013, 0.02013, 0.02013*0.01, 0.02013*0.01, 0.02013*0.01),
    (45, 0.02013, 0.02013, 0.02013, 0.02013*0.01, 0.02013*0.01, 0.02013*0.01),
    (46, 0.02013, 0.02013, 0.02013, 0.02013*0.01, 0.02013*0.01, 0.02013*0.01),
    (47, 0.02013, 0.02013, 0.02013, 0.02013*0.01, 0.02013*0.01, 0.02013*0.01),
    (48, 0.02013, 0.02013, 0.02013, 0.02013*0.01, 0.02013*0.01, 0.02013*0.01),

    (49, 0.00974, 0.00974, 0.00974, 0.00974*0.01, 0.00974*0.01, 0.00974*0.01),
    (50, 0.00974, 0.00974, 0.00974, 0.00974*0.01, 0.00974*0.01, 0.00974*0.01),
    (53, 0.00974, 0.00974, 0.00974, 0.00974*0.01, 0.00974*0.01, 0.00974*0.01),
    (54, 0.00974, 0.00974, 0.00974, 0.00974*0.01, 0.00974*0.01, 0.00974*0.01)
]

for node_id, mx, my, mz, rx, ry, rz in node_masses:
    if node_id in model.geometry.nodes:
        model.geometry.nodes[node_id].add_mass(mx, my, mz, rx, ry, rz)


# Build the model
model.build_model()

# Visualize the model
fig0 = model.visualization.visualize_model(show_elements=True)
fig0.show()


model.loading.create_linear_time_series(tag=1, factor=1)
glp = model.loading.create_load_pattern(tag=1, time_series=1)
# Define gravitational acceleration (m/s²)
g = 9.81
# Create dictionary of loads
# Format: node_id: [Fx, Fy, Fz, Mx, My, Mz]
# Mass in tons, force in kN (mass * g), moments are zero
gravity_loads = {
    # Top corners
    1: [0.0, 0.0, -0.0105225*g, 0.0, 0.0, 0.0],
    2: [0.0, 0.0, -0.0105225*g, 0.0, 0.0, 0.0],
    3: [0.0, 0.0, -0.0105225*g, 0.0, 0.0, 0.0],
    4: [0.0, 0.0, -0.0105225*g, 0.0, 0.0, 0.0],

    # Floor corners
    5: [0.0, 0.0, -0.52891*g, 0.0, 0.0, 0.0],
    6: [0.0, 0.0, -0.52891*g, 0.0, 0.0, 0.0],
    7: [0.0, 0.0, -0.52891*g, 0.0, 0.0, 0.0],
    8: [0.0, 0.0, -0.52891*g, 0.0, 0.0, 0.0],
    
    # Floor edges
    9: [0.0, 0.0, -0.0971225*g, 0.0, 0.0, 0.0],
    10: [0.0, 0.0, -0.0971225*g, 0.0, 0.0, 0.0],
    11: [0.0, 0.0, -0.10634*g, 0.0, 0.0, 0.0],
    12: [0.0, 0.0, -0.10634*g, 0.0, 0.0, 0.0],
    13: [0.0, 0.0, -0.0971225*g, 0.0, 0.0, 0.0],
    14: [0.0, 0.0, -0.0971225*g, 0.0, 0.0, 0.0],
    15: [0.0, 0.0, -0.10634*g, 0.0, 0.0, 0.0],
    16: [0.0, 0.0, -0.10634*g, 0.0, 0.0, 0.0],
    
    # # Base corners
    17: [0.0, 0.0, -0.249491*g, 0.0, 0.0, 0.0],
    18: [0.0, 0.0, -0.249491*g, 0.0, 0.0, 0.0],
    19: [0.0, 0.0, -0.249491*g, 0.0, 0.0, 0.0],
    20: [0.0, 0.0, -0.249491*g, 0.0, 0.0, 0.0],
    
    # Base edge
    21: [0.0, 0.0, -0.0284895*g, 0.0, 0.0, 0.0],
    22: [0.0, 0.0, -0.0284895*g, 0.0, 0.0, 0.0],
    23: [0.0, 0.0, -0.0284895*g, 0.0, 0.0, 0.0],
    24: [0.0, 0.0, -0.0284895*g, 0.0, 0.0, 0.0],
    25: [0.0, 0.0, -0.0284895*g, 0.0, 0.0, 0.0],
    26: [0.0, 0.0, -0.0284895*g, 0.0, 0.0, 0.0],
    27: [0.0, 0.0, -0.0284895*g, 0.0, 0.0, 0.0],
    28: [0.0, 0.0, -0.0284895*g, 0.0, 0.0, 0.0],

    # Full Infills
    41: [0.0, 0.0, -0.02013*g, 0.0, 0.0, 0.0],
    42: [0.0, 0.0, -0.02013*g, 0.0, 0.0, 0.0],
    43: [0.0, 0.0, -0.02013*g, 0.0, 0.0, 0.0],
    44: [0.0, 0.0, -0.02013*g, 0.0, 0.0, 0.0],
    45: [0.0, 0.0, -0.02013*g, 0.0, 0.0, 0.0],
    46: [0.0, 0.0, -0.02013*g, 0.0, 0.0, 0.0],
    47: [0.0, 0.0, -0.02013*g, 0.0, 0.0, 0.0],
    48: [0.0, 0.0, -0.02013*g, 0.0, 0.0, 0.0],

    # Small infills
    49: [0.0, 0.0, -0.00974*g, 0.0, 0.0, 0.0],
    50: [0.0, 0.0, -0.00974*g, 0.0, 0.0, 0.0],
    53: [0.0, 0.0, -0.00974*g, 0.0, 0.0, 0.0],
    54: [0.0, 0.0, -0.00974*g, 0.0, 0.0, 0.0],
}
for ndi, val in gravity_loads.items(): 
    fx, fy, fz, mx, my, mz = val
    glp.add_node_load(node_tag=ndi, fx=fx, fy=fy, fz=fz, mx=mx, my=my, mz=mz)


gravity_results = model.analysis.run_gravity_analysis(output_odb_tag='gravity', load_pattern_tag=1, n_steps=100)

fig0 = model.visualization.visualize_model(show_loads=True, show_elements=False, show_local_axes=False)
fig0.show()

##----------------------------------------------------------------------------------------
# Verify Gravity
node_react = opst.post.get_nodal_responses(odb_tag="gravity", resp_type="reaction")
import numpy as np
timei = 1.0
time_values = node_react.time.values
time_index = np.abs(time_values - timei).argmin() 
time_value = time_values[time_index]

uz_reactions_at_time = node_react.isel(time=time_index).sel(nodeTags=[17, 18, 19, 20], DOFs='UZ')
print(f"\nUZ reactions at time closest to {timei}:")
print(uz_reactions_at_time.sum(dim='nodeTags').values)
