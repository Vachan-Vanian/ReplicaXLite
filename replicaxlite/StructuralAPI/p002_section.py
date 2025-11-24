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


from abc import ABC, abstractmethod
import math
import opstool as opst
import numpy as np
import openseespy.opensees as ops


class SectionOutline:
    """Class to generate section outlines for different shapes"""
    
    @staticmethod
    def rectangle_section(width: float, height: float) -> list[list[float]]:
        """Generate a rectangular section outline"""
        return [
            [0, 0],
            [width, 0],
            [width, height],
            [0, height],
            [0, 0]
        ]
    
    @staticmethod
    def t_section(flange_width: float, height: float, flange_thickness: float, web_thickness: float) -> list[list[float]]:
        """Generate a T-section outline"""
        # Center the web with respect to the flange
        web_start_x = (flange_width - web_thickness) / 2
        
        return [
            [web_start_x, 0],                     # Bottom left of web
            [web_start_x + web_thickness, 0],     # Bottom right of web
            [web_start_x + web_thickness, height - flange_thickness],  # Upper right of web
            [flange_width, height - flange_thickness],  # Bottom right of flange
            [flange_width, height],               # Top right
            [0, height],                          # Top left
            [0, height - flange_thickness],       # Bottom left of flange
            [web_start_x, height - flange_thickness],  # Upper left of web
            [web_start_x, 0]                      # Back to start
        ]
    
    @staticmethod
    def l_section(flange_width: float, height: float, flange_thickness: float, web_thickness: float) -> list[list[float]]:
        """Generate an L-section outline"""
        return [
            [0, 0],                          # Bottom left
            [web_thickness, 0],              # Bottom right of web
            [web_thickness, height-flange_thickness], # Top right of web
            [flange_width, height-flange_thickness],  # Right bottom of flange
            [flange_width, height],           # Top right
            [0, height],                      # Top left
            [0, 0]                            # Back to start
        ]
    
    @staticmethod
    def i_section(width: float, height: float, flange_thickness: float, web_thickness: float) -> list[list[float]]:
        """Generate an I-section outline"""
        # Center the web with respect to the flange
        web_start_x = (width - web_thickness) / 2
        
        return [
            [0, 0],                           # Bottom left
            [width, 0],                       # Bottom right
            [width, flange_thickness],        # Top right of bottom flange
            [web_start_x + web_thickness, flange_thickness],  # Right bottom corner of web
            [web_start_x + web_thickness, height - flange_thickness],  # Right top corner of web
            [width, height - flange_thickness],  # Bottom right of top flange
            [width, height],                  # Top right
            [0, height],                      # Top left
            [0, height - flange_thickness],   # Bottom left of top flange
            [web_start_x, height - flange_thickness],  # Left top corner of web
            [web_start_x, flange_thickness],  # Left bottom corner of web
            [0, flange_thickness],            # Top left of bottom flange
            [0, 0]                            # Back to start
        ]
    
    @staticmethod
    def circular_section(radius: float, num_points: int = 16) -> list[list[float]]:
        """Generate a circular section outline"""
        outline = []
        for i in range(num_points + 1):
            theta = 2 * math.pi * i / num_points
            x = radius * math.cos(theta)
            y = radius * math.sin(theta)
            outline.append([x, y])
        return outline
    
    # NEW ADDITION: User-defined section support
    @staticmethod
    def user_section(outline_points: list[list[float]], hole_points: list[list[list[float]]] = None) -> dict:
        """
        Generate a user-defined section outline
        
        Parameters:
        -----------
        outline_points : list[list[float]]
            List of [x, y] coordinates defining the outer boundary
        hole_points : list[list[list[float]]], optional
            List of holes, where each hole is defined by a list of [x, y] coordinates
            
        Returns:
        --------
        dict
            Dictionary containing 'outline' and optionally 'holes'
        """
        # Ensure the outline is closed
        if outline_points[0] != outline_points[-1]:
            outline_points = outline_points + [outline_points[0]]
        
        result = {"outline": outline_points}
        
        # If holes are provided, ensure each hole is closed
        if hole_points:
            closed_holes = []
            for hole in hole_points:
                if hole[0] != hole[-1]:
                    hole = hole + [hole[0]]
                closed_holes.append(hole)
            result["holes"] = closed_holes
        
        return result


class Section(ABC):
    """Abstract base class for sections"""
    
    def __init__(self, tag: int, name: str, structural_element_type: str):
        self.tag = tag
        self.name = name
        self.structural_element_type = structural_element_type
        self.section_mesh = None
        self._is_created_in_opensees = False
    
    @abstractmethod
    def create_in_opensees(self):
        """Create the section in OpenSees"""
        pass
    
    def visualize(self, fill: bool = True, show_legend: bool = True, aspect_ratio: float = 1):
        """
        Visualize the section.
        
        Parameters:
        -----------
        fill : bool
            Whether to fill the section
        show_legend : bool
            Whether to show the legend
        aspect_ratio : float
            Aspect ratio for the plot
        """
        if self.section_mesh:
            fig = self.section_mesh.view(fill=fill, show_legend=show_legend, aspect_ratio=aspect_ratio)
            return fig
        return None


class ElasticSection(Section):
    """Class for elastic sections"""
    
    def __init__(self, tag: int, name: str, structural_element_type: str, 
                 section_shape: str, shape_params: dict, 
                 E_mod: float, G_mod: float, 
                 rotate_angle: float = 0, section_shear: bool = False, 
                 section_color: str = "#88b378"):
        super().__init__(tag, name, structural_element_type)
        self.section_shape = section_shape
        self.shape_params = shape_params
        self.E_mod = E_mod
        self.G_mod = G_mod
        self.section_shear = section_shear
        self.rotate_angle = rotate_angle
        self.section_color = section_color
        
        # Initialize properties
        self.outline = None
        self.holes = None  # NEW: Support for holes
        self.A = None
        self.Iz = None
        self.Iy = None
        self.Jxx = None
        self.alphaY = None
        self.alphaZ = None
        
        # Generate section properties
        self._generate_section()
    
    def _generate_section(self):
        """Generate section outline and compute properties"""
        
        # Generate outline based on shape
        if self.section_shape == 'rectangle':
            self.outline = SectionOutline.rectangle_section(**self.shape_params)
        elif self.section_shape == 't_section':
            self.outline = SectionOutline.t_section(**self.shape_params)
        elif self.section_shape == 'l_section':
            self.outline = SectionOutline.l_section(**self.shape_params)
        elif self.section_shape == 'i_section':
            self.outline = SectionOutline.i_section(**self.shape_params)
        elif self.section_shape == 'circular':
            self.outline = SectionOutline.circular_section(**self.shape_params)
        # NEW: User-defined section case
        elif self.section_shape == 'user_section':
            user_section_data = SectionOutline.user_section(**self.shape_params)
            self.outline = user_section_data["outline"]
            self.holes = user_section_data.get("holes", None)
        else:
            raise ValueError(f"Unsupported section shape {self.section_shape}")
        
        # Create geometry and compute properties
        # MODIFIED: Handle holes if present
        if self.holes:
            section_geo = opst.pre.section.create_polygon_patch(self.outline, holes=self.holes)
        else:
            section_geo = opst.pre.section.create_polygon_patch(self.outline)
            
        self.section_mesh = opst.pre.section.FiberSecMesh(sec_name=self.name)
        self.section_mesh.add_patch_group({"section": section_geo})
        self.section_mesh.set_mesh_color({"section": self.section_color})
        self.section_mesh.mesh()
        
        # Apply rotation if needed
        if self.rotate_angle != 0:
            self.section_mesh.rotate(self.rotate_angle, remesh=True)
        
        # Center the section
        self.section_mesh.centring()
        
        # Get section properties
        SP = self.section_mesh.get_sec_props()
        self.A = float(SP['A'])
        self.Iz = float(SP['Iz'])
        self.Iy = float(SP['Iy'])
        self.Jxx = float(SP['J'])
        
        if self.section_shear:
            self.alphaY = float(SP['Asy'])
            self.alphaZ = float(SP['Asz'])
    
    def create_in_opensees(self):
        """Create elastic section in OpenSees"""
        if not self._is_created_in_opensees:
            if self.section_shear:
                ops.section('Elastic', self.tag, self.E_mod, self.A, self.Iz, self.Iy, self.G_mod, self.Jxx, self.alphaY, self.alphaZ)
            else:
                ops.section('Elastic', self.tag, self.E_mod, self.A, self.Iz, self.Iy, self.G_mod, self.Jxx)
            self._is_created_in_opensees = True

    def get_section_properties(self) -> dict:
        """
        Return section properties.
        
        Returns:
        --------
        dict
            Section properties {A, Iz, Iy, Jxx, [alphaY, alphaZ]}
        """
        if self.section_shear:
            return {'A': self.A, 'Iz': self.Iz, 'Iy': self.Iy, 'Jxx': self.Jxx, 'alphaY': self.alphaY, 'alphaZ': self.alphaZ}
        else:
            return {'A': self.A, 'Iz': self.Iz, 'Iy': self.Iy, 'Jxx': self.Jxx}
    
    def get_material_properties(self) -> dict:
        """
        Return material properties.
        
        Returns:
        --------
        dict
            Material properties {E_mod, G_mod}
        """
        return {'E_mod':self.E_mod, 'G_mod': self.G_mod}

  
class FiberSection(Section):
    """Class for fiber sections

    -------------------------------------------------------
    Note: This implementation does not validate rebar placement. Users are responsible for
          ensuring rebars are correctly positioned within section boundaries. 
    
    ### rebar_points = {
    "group_name": {
        "points": [(x1, y1), (x2, y2), ...],  # List of (x,y) coordinates
        "dia": float,                         # Diameter of the rebar
        "mat_tag": int,                       # Material tag for the rebar
        "color": str                          # Color for visualization (e.g., "#ff0000")
    },
        # Additional groups as needed
    }

    ### rebar_lines = {
    "group_name": {
        "points": [(x1, y1), (x2, y2)],   # Start and end points of the line
        "dia": float,                     # Diameter of each rebar
        "n": int,                         # Number of rebars to place along the line
        "mat_tag": int,                   # Material tag for the rebars
        "color": str                      # Color for visualization (e.g., "#ff0000")
    },
        # Additional groups as needed
    }

    ### rebar_circles = {
    "group_name": {
        "xo": (x, y),                     # Center point of the circle
        "radius": float,                  # Radius of the circle
        "dia": float,                     # Diameter of each rebar
        "angles": [angle1, angle2, ...],  # Angles (in degrees) for each rebar
        "mat_tag": int,                   # Material tag for the rebars
        "color": str                      # Color for visualization (e.g., "#ff0000")
    },
        # Additional groups as needed
    }
    """
    def __init__(self, tag: int, name: str, structural_element_type: str, 
                 section_shape: str, shape_params: dict, 
                 section_cover: float = 0, cover_mat_tag: int = None, core_mat_tag: int = None, 
                 rebar_points: dict = None, rebar_lines: dict = None, rebar_circles: dict = None, 
                 section_rotate: float = 0, 
                 G: float = None, GJ: float = None,
                 cover_color:str = "#dbb40c", core_color:str = "#88b378"):
        super().__init__(tag, name, structural_element_type)
        self.section_shape = section_shape
        self.shape_params = shape_params
        self.section_cover = section_cover
        self.cover_mat_tag = cover_mat_tag
        self.core_mat_tag = core_mat_tag
        self.rebar_points = rebar_points or {}
        self.rebar_lines = rebar_lines or {}
        self.rebar_circles = rebar_circles or {}
        self.section_rotate = section_rotate
        self.G = G
        self.GJ = GJ
        self.outline = None
        self.holes = None  # NEW: Support for holes
        self.cover_color = cover_color
        self.core_color = core_color
        
        # Generate section
        self._generate_section()
    
    def _generate_section(self):
        """Generate section outline and create mesh"""
        
        # Generate outline based on shape
        if self.section_shape == 'rectangle':
            self.outline = SectionOutline.rectangle_section(**self.shape_params)
        elif self.section_shape == 't_section':
            self.outline = SectionOutline.t_section(**self.shape_params)
        elif self.section_shape == 'l_section':
            self.outline = SectionOutline.l_section(**self.shape_params)
        elif self.section_shape == 'i_section':
            self.outline = SectionOutline.i_section(**self.shape_params)
        elif self.section_shape == 'circular':
            self.outline = SectionOutline.circular_section(**self.shape_params)
        # NEW: User-defined section case
        elif self.section_shape == 'user_section':
            user_section_data = SectionOutline.user_section(**self.shape_params)
            self.outline = user_section_data["outline"]
            self.holes = user_section_data.get("holes", None)
        else:
            raise ValueError(f"Unsupported section shape {self.section_shape}")
        
        # Create fiber section mesh
        self.section_mesh = opst.pre.section.FiberSecMesh(sec_name=self.name)
        
        # Handle case where section_cover = 0
        if self.section_cover == 0:
            # If no cover, the entire section is treated as core
            # MODIFIED: Handle holes if present
            if self.holes:
                core_geo = opst.pre.section.create_polygon_patch(self.outline, holes=self.holes)
            else:
                core_geo = opst.pre.section.create_polygon_patch(self.outline)
            
            # Add only the core patch group
            self.section_mesh.add_patch_group({"core": core_geo})
            
            # Set material tag for core
            self.section_mesh.set_ops_mat_tag({"core": self.core_mat_tag})
            
            # Set color for visualization
            self.section_mesh.set_mesh_color({"core": self.core_color})
        else:
            # Normal case with non-zero cover
            # Create cover boundary by offsetting outline
            coverlines = opst.pre.section.offset(self.outline, d=self.section_cover)
            
            # Create cover and core geometries
            # CORRECTED: User holes only affect core, not cover
            cover_geo = opst.pre.section.create_polygon_patch(self.outline, holes=[coverlines])
            
            if self.holes:
                # Core: inside coverlines, with user holes
                core_geo = opst.pre.section.create_polygon_patch(coverlines, holes=self.holes)
            else:
                # Core: inside coverlines, no holes
                core_geo = opst.pre.section.create_polygon_patch(coverlines)

            # Add patch groups
            self.section_mesh.add_patch_group({"cover": cover_geo, "core": core_geo})

            # Set material tags
            self.section_mesh.set_ops_mat_tag({
                "cover": self.cover_mat_tag,
                "core": self.core_mat_tag
            })

            # Set colors for visualization
            self.section_mesh.set_mesh_color({"cover": self.cover_color, "core": self.core_color})
            # THIS NEED FURTHER VERIFICATION IF ACTIVATED
            # self.section_mesh.set_mesh_size({"cover": 0.02, "core": 0.02})

        # Add rebars
        self._add_rebars()
        
        # Generate mesh
        self.section_mesh.mesh()

        # Rotate if needed
        if self.section_rotate != 0:
            self.section_mesh.rotate(self.section_rotate, remesh=True)

        # Center the section
        self.section_mesh.centring()

    def _add_rebars(self):
        """Add rebars to the section"""
        # Add point rebars
        for key, prop_dict in self.rebar_points.items():
            self.section_mesh.add_rebar_points(
                points=prop_dict['points'],
                dia=prop_dict['dia'],
                ops_mat_tag=prop_dict['mat_tag'],
                color=prop_dict['color'],
                group_name=key
            )

        # Add line rebars
        for key, prop_dict in self.rebar_lines.items():
            self.section_mesh.add_rebar_line(
                points=prop_dict['points'],
                dia=prop_dict['dia'],
                n=prop_dict['n'],
                ops_mat_tag=prop_dict['mat_tag'],
                color=prop_dict['color'],
                group_name=key
            )

        # Add circular rebars
        for key, prop_dict in self.rebar_circles.items():
            self.section_mesh.add_rebar_circle(
                xo=prop_dict['xo'],
                radius=prop_dict['radius'],
                dia=prop_dict['dia'],
                angles=prop_dict['angles'],
                ops_mat_tag=prop_dict['mat_tag'],
                color=prop_dict['color'],
                group_name=key
            )
    
    def create_in_opensees(self):
        """Create fiber section in OpenSees"""
        if not self._is_created_in_opensees:
            
            # Check if either G or GJ is provided
            if self.GJ is None and self.G is None:
                raise ValueError("Either GJ or G must be provided for fiber section")
            
            # Calculate GJ if not provided
            if self.GJ is None:
                GJ = self.G * self.section_mesh.get_j()
            else:
                GJ = self.GJ
            
            # Create fiber section
            ops.section("Fiber", self.tag, "-GJ", GJ)
            
            # Add fibers from the mesh
            names = self.section_mesh.fiber_centers_map.keys()
            for name in names:
                centers = self.section_mesh.fiber_centers_map[name]
                areas = self.section_mesh.fiber_areas_map[name]
                matTag = self.section_mesh.mat_ops_map[name]
                for center, area in zip(centers, areas):
                    ops.fiber(float(center[0]), float(center[1]), float(area), matTag)
            
            # Add rebars
            for data in self.section_mesh.rebar_data:
                rebar_xy = data["rebar_xy"]
                dia = data["dia"]
                matTag = data["matTag"]
                for xy in rebar_xy:
                    area = np.pi / 4 * dia**2
                    ops.fiber(float(xy[0]), float(xy[1]), float(area), matTag)
            
            self._is_created_in_opensees = True

