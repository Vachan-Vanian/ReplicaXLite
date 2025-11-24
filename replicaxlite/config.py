######################################################################################################
# ReplicaXLite - A finite element toolkit for creating, analyzing and monitoring 3D structural models
# Copyright (C) 2024-2025 Vachan Vanian
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.
#
# Contact: vachanvanian@outlook.com
######################################################################################################


INFO = {
    "version": "1.0.0"
}

SETTINGS = {
    "_version": INFO["version"],
    "interactor": {
        # Use "group_" prefix - part after prefix becomes the group display name
        "group_camera_rotation": {
            "rotation_angle_deg_x": 5,
            "rotation_angle_deg_y": 5,
            "rotation_angle_deg_z": 5,
        },
        
        "group_camera_movement": {
            "distance_step_x": 0.1,
            "distance_step_y": 0.1,
            "distance_step_z": 0.1,
        },

        "group_screenshot": {
            "transparent_background": False,
            "scale": 1
        }
    },

    "_project": {
        "project_folder": "" # should be the folder inside with the project files are
    },

    "unit_system": {
        "_unit_systems": {
            'SI_m_kg_s': {
                'Length': 'm',
                'Mass': 'kg',
                'Time': 's',
                'Temperature': 'K',
                'Angle': 'rad',
                'Area': 'm^2',
                'Volume': 'm^3',
                'Concentrated_Force': 'N',
                'Distributed_Force': 'N/m',
                'Moment': 'N*m',
                'Pressure': 'Pa',
                'Stress': 'Pa',
                'E_G_K_Modulus': 'Pa',
                'Area_Force': 'N/m^2',
                'Volume_Force': 'N/m^3',
                'Specific_Weight': 'N/m^3',
                'Mass_per_Unit_Length': 'kg/m',
                'Displacement': 'm',
                'Velocity': 'm/s',
                'Acceleration': 'm/s^2',
                'Standard_Gravity': 'm/s^2',
                'Angular_Velocity': 'rad/s',
                'Angular_Acceleration': 'rad/s^2',
                'Rotation': 'rad',
                'First_Moment_of_Area': 'm^3',
                'Second_Moment_of_Area': 'm^4',
                'Flexural_Rigidity': 'N*m^2',
                'Axial_Rigidity': 'N',
                'Torsional_Rigidity': 'N*m^2',
                'Mass_Moments_of_Inertia': 'kg*m^2',
                'Coefficient_of_Thermal_Expansion': '1/K',
                'Thermal_Conductivity': 'W/mK',
                'Frequency': 'Hz',
                'Strain': 'strain'
            },
            
            'SI_mm_tonne_s': {
                'Length': 'mm',
                'Mass': 'tonne',
                'Time': 's',
                'Temperature': 'K',
                'Angle': 'rad',
                'Area': 'mm^2',
                'Volume': 'mm^3',
                'Concentrated_Force': 'N',
                'Distributed_Force': 'N/mm',
                'Moment': 'N*mm',
                'Pressure': 'MPa',
                'Stress': 'MPa',
                'E_G_K_Modulus': 'MPa',
                'Area_Force': 'N/mm^2',
                'Volume_Force': 'N/mm^3',
                'Specific_Weight': 'N/mm^3',
                'Mass_per_Unit_Length': 'tonne/mm',
                'Displacement': 'mm',
                'Velocity': 'mm/s',
                'Acceleration': 'mm/s^2',
                'Standard_Gravity': 'mm/s^2',
                'Angular_Velocity': 'rad/s',
                'Angular_Acceleration': 'rad/s^2',
                'Rotation': 'rad',
                'First_Moment_of_Area': 'mm^3',
                'Second_Moment_of_Area': 'mm^4',
                'Flexural_Rigidity': 'N*mm^2',
                'Axial_Rigidity': 'N',
                'Torsional_Rigidity': 'N*mm^2',
                'Mass_Moments_of_Inertia': 'tonne*mm^2',
                'Coefficient_of_Thermal_Expansion': '1/K',
                'Thermal_Conductivity': 'W/mK',
                'Frequency': 'Hz',
                'Strain': 'strain'
            },
            
            'SI_cm_g_s': {
                'Length': 'cm',
                'Mass': 'g',
                'Time': 's',
                'Temperature': 'K',
                'Angle': 'rad',
                'Area': 'cm^2',
                'Volume': 'cm^3',
                'Concentrated_Force': 'N',
                'Distributed_Force': 'N/cm',
                'Moment': 'N*cm',
                'Pressure': 'kPa',
                'Stress': 'kPa',
                'E_G_K_Modulus': 'kPa',
                'Area_Force': 'N/cm^2',
                'Volume_Force': 'N/cm^3',
                'Specific_Weight': 'N/cm^3',
                'Mass_per_Unit_Length': 'g/cm',
                'Displacement': 'cm',
                'Velocity': 'cm/s',
                'Acceleration': 'cm/s^2',
                'Standard_Gravity': 'cm/s^2',
                'Angular_Velocity': 'rad/s',
                'Angular_Acceleration': 'rad/s^2',
                'Rotation': 'rad',
                'First_Moment_of_Area': 'cm^3',
                'Second_Moment_of_Area': 'cm^4',
                'Flexural_Rigidity': 'N*cm^2',
                'Axial_Rigidity': 'N',
                'Torsional_Rigidity': 'N*cm^2',
                'Mass_Moments_of_Inertia': 'g*cm^2',
                'Coefficient_of_Thermal_Expansion': '1/K',
                'Thermal_Conductivity': 'W/mK',
                'Frequency': 'Hz',
                'Strain': 'strain'
            },
            
            'US_in_lbf_s': {
                'Length': 'in',
                'Mass': 'lbf*s^2/in',
                'Time': 's',
                'Temperature': 'F',
                'Angle': 'rad',
                'Area': 'in^2',
                'Volume': 'in^3',
                'Concentrated_Force': 'lbf',
                'Distributed_Force': 'lbf/in',
                'Moment': 'lbf*in',
                'Pressure': 'psi',
                'Stress': 'psi',
                'E_G_K_Modulus': 'psi',
                'Area_Force': 'lbf/in^2',
                'Volume_Force': 'lbf/in^3',
                'Specific_Weight': 'lbf/in^3',
                'Mass_per_Unit_Length': '(lbf*s^2/in)/in',
                'Displacement': 'in',
                'Velocity': 'in/s',
                'Acceleration': 'in/s^2',
                'Standard_Gravity': 'in/s^2',
                'Angular_Velocity': 'rad/s',
                'Angular_Acceleration': 'rad/s^2',
                'Rotation': 'rad',
                'First_Moment_of_Area': 'in^3',
                'Second_Moment_of_Area': 'in^4',
                'Flexural_Rigidity': 'lbf*in^2',
                'Axial_Rigidity': 'lbf',
                'Torsional_Rigidity': 'lbf*in^2',
                'Mass_Moments_of_Inertia': '(lbf*s^2/in)*in^2',
                'Coefficient_of_Thermal_Expansion': '1/F',
                'Thermal_Conductivity': 'BTU/(hr*ft*F)',
                'Frequency': 'Hz',
                'Strain': 'strain'
            },
            
            'US_ft_lbf_s': {
                'Length': 'ft',
                'Mass': 'lbf*s^2/ft',
                'Time': 's',
                'Temperature': 'F',
                'Angle': 'rad',
                'Area': 'ft^2',
                'Volume': 'ft^3',
                'Concentrated_Force': 'lbf',
                'Distributed_Force': 'lbf/ft',
                'Moment': 'lbf*ft',
                'Pressure': 'lbf/ft^2',
                'Stress': 'lbf/ft^2',
                'E_G_K_Modulus': 'lbf/ft^2',
                'Area_Force': 'lbf/ft^2',
                'Volume_Force': 'lbf/ft^3',
                'Specific_Weight': 'lbf/ft^3',
                'Mass_per_Unit_Length': '(lbf*s^2/ft)/ft',
                'Displacement': 'ft',
                'Velocity': 'ft/s',
                'Acceleration': 'ft/s^2',
                'Standard_Gravity': 'ft/s^2',
                'Angular_Velocity': 'rad/s',
                'Angular_Acceleration': 'rad/s^2',
                'Rotation': 'rad',
                'First_Moment_of_Area': 'ft^3',
                'Second_Moment_of_Area': 'ft^4',
                'Flexural_Rigidity': 'lbf*ft^2',
                'Axial_Rigidity': 'lbf',
                'Torsional_Rigidity': 'lbf*ft^2',
                'Mass_Moments_of_Inertia': '(lbf*s^2/ft)*ft^2',
                'Coefficient_of_Thermal_Expansion': '1/F',
                'Thermal_Conductivity': 'BTU/(hr*ft*F)',
                'Frequency': 'Hz',
                'Strain': 'strain'
            },
            
            'US_in_kip_s': {
                'Length': 'in',
                'Mass': 'kip*s^2/in',
                'Time': 's',
                'Temperature': 'F',
                'Angle': 'rad',
                'Area': 'in^2',
                'Volume': 'in^3',
                'Concentrated_Force': 'kip',
                'Distributed_Force': 'kip/in',
                'Moment': 'kip*in',
                'Pressure': 'ksi',
                'Stress': 'ksi',
                'E_G_K_Modulus': 'ksi',
                'Area_Force': 'kip/in^2',
                'Volume_Force': 'kip/in^3',
                'Specific_Weight': 'kip/in^3',
                'Mass_per_Unit_Length': '(kip*s^2/in)/in',
                'Displacement': 'in',
                'Velocity': 'in/s',
                'Acceleration': 'in/s^2',
                'Standard_Gravity': 'in/s^2',
                'Angular_Velocity': 'rad/s',
                'Angular_Acceleration': 'rad/s^2',
                'Rotation': 'rad',
                'First_Moment_of_Area': 'in^3',
                'Second_Moment_of_Area': 'in^4',
                'Flexural_Rigidity': 'kip*in^2',
                'Axial_Rigidity': 'kip',
                'Torsional_Rigidity': 'kip*in^2',
                'Mass_Moments_of_Inertia': '(kip*s^2/in)*in^2',
                'Coefficient_of_Thermal_Expansion': '1/F',
                'Thermal_Conductivity': 'BTU/(hr*ft*F)',
                'Frequency': 'Hz',
                'Strain': 'strain'
            },
            
            'US_ft_kip_s': {
                    'Length': 'ft',
                    'Mass': 'kip*s^2/ft',
                    'Time': 's',
                    'Temperature': 'F',
                    'Angle': 'rad',
                    'Area': 'ft^2',
                    'Volume': 'ft^3',
                    'Concentrated_Force': 'kip',
                    'Distributed_Force': 'kip/ft',
                    'Moment': 'kip*ft',
                    'Pressure': 'kip/ft^2',
                    'Stress': 'kip/ft^2',
                    'E_G_K_Modulus': 'kip/ft^2',
                    'Area_Force': 'kip/ft^2',
                    'Volume_Force': 'kip/ft^3',
                    'Specific_Weight': 'kip/ft^3',
                    'Mass_per_Unit_Length': '(kip*s^2/ft)/ft',
                    'Displacement': 'ft',
                    'Velocity': 'ft/s',
                    'Acceleration': 'ft/s^2',
                    'Standard_Gravity': 'ft/s^2',
                    'Angular_Velocity': 'rad/s',
                    'Angular_Acceleration': 'rad/s^2',
                    'Rotation': 'rad',
                    'First_Moment_of_Area': 'ft^3',
                    'Second_Moment_of_Area': 'ft^4',
                    'Flexural_Rigidity': 'kip*ft^2',
                    'Axial_Rigidity': 'kip',
                    'Torsional_Rigidity': 'kip*ft^2',
                    'Mass_Moments_of_Inertia': '(kip*s^2/ft)*ft^2',
                    'Coefficient_of_Thermal_Expansion': '1/F',
                    'Thermal_Conductivity': 'BTU/(hr*ft*F)',
                    'Frequency': 'Hz',
                    'Strain': 'strain'
                },
        
            'SI_m_tonne_s': {
                'Length': 'm',
                'Mass': 'tonne',
                'Time': 's',
                'Temperature': 'K',
                'Angle': 'rad',
                'Area': 'm^2',
                'Volume': 'm^3',
                'Concentrated_Force': 'kN',
                'Distributed_Force': 'kN/m',
                'Moment': 'kN*m',
                'Pressure': 'kPa',
                'Stress': 'kPa',
                'E_G_K_Modulus': 'kPa',
                'Area_Force': 'kN/m^2',
                'Volume_Force': 'kN/m^3',
                'Specific_Weight': 'kN/m^3',
                'Mass_per_Unit_Length': 'tonne/m',
                'Displacement': 'm',
                'Velocity': 'm/s',
                'Acceleration': 'm/s^2',
                'Standard_Gravity': 'm/s^2',
                'Angular_Velocity': 'rad/s',
                'Angular_Acceleration': 'rad/s^2',
                'Rotation': 'rad',
                'First_Moment_of_Area': 'm^3',
                'Second_Moment_of_Area': 'm^4',
                'Flexural_Rigidity': 'kN*m^2',
                'Axial_Rigidity': 'kN',
                'Torsional_Rigidity': 'kN*m^2',
                'Mass_Moments_of_Inertia': 'tonne*m^2',
                'Coefficient_of_Thermal_Expansion': '1/K',
                'Thermal_Conductivity': 'W/mK',
                'Frequency': 'Hz',
                'Strain': 'strain'
            }
        },
        "_old_unit_system": "SI_m_tonne_s",
        "new_unit_system": "SI_m_tonne_s"
    },

    "sensors": {
        "group_display": {
            "sensor_point_size": 10,
            "label_font_size": 15,
        },
        "group_sensor_colors": {
            "Acceleration": "red",
            "Displacement": "blue",
            "Strain": "green",
            "Frequency": "orange"
        }
    },

    "fem_model" :{
        "display_model": "0",
        # plot_model settings
        "group_plot_model": {
            "odb_tag": None,
            "show_node_numbering": True,
            "show_ele_numbering": False,
            "style": "surface",  # 'surface', 'wireframe', 'points', 'points_gaussian'
            "color": None,
            "show_bc": True,
            "bc_scale": 1.0,
            "show_link": True,
            "show_mp_constraint": True,
            "show_constraint_dofs": False,
            "show_nodal_loads": True,
            "show_ele_loads": True,
            "load_scale": 1.0,
            "show_local_axes": True,
            "local_axes_scale": 1.0,
            "show_outline": False,
            "show_legend": False,
            "cpos": "iso"  # 'iso', 'xy', 'yx', 'xz', 'zx', 'yz', 'zy'
        }

    },

    "plot_props": {
        # Rendering settings
        "point_size": 1.0,
        "line_width": 2.0,
        "theme": "default",  # 'default', 'document', 'dark', or 'paraview'
        "render_points_as_spheres": True,
        "render_lines_as_tubes": True,
        
        # Anti-aliasing settings
        "anti_aliasing": "msaa",  # 'ssaa', 'msaa', or 'fxaa'
        "msaa_multi_samples": 16,
        
        # Shading and smoothing
        "smooth_shading": None,
        "lighting": None,
        "line_smoothing": True,
        "polygon_smoothing": True,
        
        # Font settings
        "font_family": None,  # 'courier', 'times', or 'arial'
        "font_size": 12,
        "title_font_size": 18,
        
        # Scale and mesh settings
        "scale_factor": 0.0667,  # 1/15
        "show_mesh_edges": True,
        "mesh_edge_color": "black",
        "mesh_edge_width": 1.0,
        "mesh_opacity": 1.0,
        
        # Rendering mode
        "off_screen": False,
        
        # Scalar bar configuration
        "scalar_bar_kargs": {
            "fmt": "%10.3e",
            "n_labels": 10,
            "bold": False,
            "width": 0.1,
            "height": 0.5,
            "vertical": True,
            "font_family": "courier",
            "label_font_size": None,
            "title_font_size": None,
            "position_x": 0.825,
            "position_y": 0.05,
            "outline": False
        }
    },

    "plot_colors": {
        # Element type colors
        "point": "#FF0055",
        "frame": "#0652ff",
        "beam": "#0652ff",
        "truss": "#FF8C00",
        "link": "#39FF14",
        "shell": "#769958",
        "plane": "#00FFFF",
        "brick": "#FF4500",
        "tet": "#FFFF33",
        "joint": "#7FFF00",
        "contact": "#ff9408",
        "pfem": "#8080FF",
        "constraint": "#FF1493",
        "bc": "#15b01a",
        
        # Label colors
        "nodal_label": "#048243",
        "ele_label": "#650021",
        
        # Colormap settings
        "cmap": "jet",
        "cmap_model": None,
        "n_colors": 256,
        "color_map": "jet"
    },

}