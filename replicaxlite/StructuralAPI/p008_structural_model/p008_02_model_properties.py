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


import openseespy.opensees as ops
from ..p001_material import UniaxialMaterial
from ..p002_section import Section, ElasticSection, FiberSection
from ..p004_element import BeamIntegration
from ..p000_utility import calculate_aligned_vecxz


class ModelProperties:
    """Handles materials, sections and transformations for the structural model"""
    
    def __init__(self, parent_model):
        self.parent = parent_model
        
        # Component collections
        self.materials = {}
        self.sections = {}
        self.beam_integrations = {}
        self.transformations = {}
        self.transformation_map = {}
        
    ### material
    def create_uniaxial_material(self, tag: int, name: str, material_type: str, material_args: dict):
        """
        USER FUNCTION
        Create a uniaxial material and add it to the model.
        
        Parameters:
        -----------
        tag : int
            Material tag
        name : str
            Material name
        material_type : str
            Type of material (e.g., 'Steel01', 'Concrete01')
        material_args : dict
            Material parameters
            
        Returns:
        --------
        UniaxialMaterial
            The created material
        """
        material = UniaxialMaterial(tag, name, material_type, material_args)
        return self.add_uniaxial_material(material)

    def add_uniaxial_material(self, material: UniaxialMaterial):
        """
        Add a uniaxial material to the model without creating it in OpenSees yet.
        
        Parameters:
        -----------
        material : UniaxialMaterial
            Material to add
            
        Returns:
        --------
        UniaxialMaterial
            The added material
        """
        self.materials[material.name] = material
        self.parent._log(f"Added uniaxial material {material.name} (tag={material.tag})")
        return material
    
    ### section
    def create_elastic_section(self, tag: int, name: str, structural_element_type: str,
                             section_shape: str, shape_params: dict,
                             E_mod: float, G_mod: float, rotate_angle: float = 0, 
                             section_shear: bool = False, section_color: str = "#88b378"):
        """
        USER FUNCTION
        Create an elastic section and add it to the model.
        
        Parameters:
        -----------
        tag : int
            Section tag
        name : str
            Section name
        structural_element_type : str
            Type of structural element this section is for
        section_shape : str
            Shape of the section (e.g., 'rectangle', 'i_section')
        shape_params : dict
            Shape parameters
        E_mod : float
            Elastic modulus
        G_mod : float
            Shear modulus
        rotate_angle : float
            Rotation angle
        section_shear : bool
            Whether to include shear deformation
        section_color : str
            Color for visualization
            
        Returns:
        --------
        Section
            The created section
        """
        section = ElasticSection(tag, name, structural_element_type, section_shape, 
                                shape_params, E_mod, G_mod, rotate_angle, section_shear, 
                                section_color)
        return self.add_section(section)

    def create_fiber_section(self, tag: int, name: str, structural_element_type: str,
                           section_shape: str, shape_params: dict,
                           section_cover: float = 0, cover_mat_tag: int = None, core_mat_tag: int = None,
                           rebar_points: dict = None, rebar_lines: dict = None, rebar_circles: dict = None,
                           section_rotate: float = 0, G: float = None, GJ: float = None,
                           cover_color: str = "#dbb40c", core_color: str = "#88b378"):
        """
        USER FUNCTION
        Create a fiber section and add it to the model.
        
        Parameters:
        -----------
        tag : int
            Section tag
        name : str
            Section name
        structural_element_type : str
            Type of structural element this section is for
        section_shape : str
            Shape of the section (e.g., 'rectangle', 'i_section')
        shape_params : dict
            Shape parameters
        section_cover : float
            Concrete cover thickness
        cover_mat_tag : int
            Material tag for cover
        core_mat_tag : int
            Material tag for core
        rebar_points : dict
            Dictionary defining point rebars
        rebar_lines : dict
            Dictionary defining line rebars
        rebar_circles : dict
            Dictionary defining circular rebars
        section_rotate : float
            Rotation angle
        G : float
            Shear modulus
        GJ : float
            Torsional rigidity
        cover_color : str
            Color for cover visualization
        core_color : str
            Color for core visualization
            
        Returns:
        --------
        Section
            The created section
        """
        section = FiberSection(tag, name, structural_element_type, section_shape,
                             shape_params, section_cover, cover_mat_tag, core_mat_tag,
                             rebar_points, rebar_lines, rebar_circles,
                             section_rotate, G, GJ, cover_color, core_color)
        return self.add_section(section)

    def add_section(self, section: Section):
        """
        Add a section to the model without creating it in OpenSees yet.
        
        Parameters:
        -----------
        section : Section
            Section to add
            
        Returns:
        --------
        Section
            The added section
        """
        self.sections[section.name] = section
        self.parent._log(f"Added section {section.name} (tag={section.tag})")
        return section
    
    ### beam integration
    def create_beam_integration(self, tag: int, integration_type: str, 
                             structural_element_use: str, section_tag: int, 
                             num_points: int = 5) -> BeamIntegration:
        """
        Create a new beam integration and add it to the model.
        
        Parameters:
        -----------
        tag : int
            Beam integration tag
        integration_type : str
            Type of integration (e.g., 'Lobatto')
        structural_element_use : str
            Structural element type this integration is used for
        section_tag : int
            Section tag to use
        num_points : int
            Number of integration points
            
        Returns:
        --------
        BeamIntegration
            The created beam integration
        """
        beam_integration = BeamIntegration(
            tag, integration_type, structural_element_use, section_tag, num_points
        )
        return self.add_beam_integration(beam_integration)

    def add_beam_integration(self, beam_integration: BeamIntegration):
        """
        Add a beam integration to the model without creating it in OpenSees yet.
        
        Parameters:
        -----------
        beam_integration : BeamIntegration
            Beam integration to add
            
        Returns:
        --------
        BeamIntegration
            The added beam integration
        """
        self.beam_integrations[beam_integration.tag] = beam_integration
        self.parent._log(f"Added beam integration with tag {beam_integration.tag}")
        return beam_integration
    
    ### transformation
    def create_transformation(self, start_node, end_node, transform_type='Linear', tol=1e-6):
        """
        Create or retrieve a geometric transformation.
        
        Parameters:
        -----------
        start_node, end_node : Node or int
            Start and end nodes (or their IDs)
        transform_type : str
            Type of transformation
            
        Returns:
        --------
        int
            Transformation ID
        """
        # Get node coordinates
        if hasattr(start_node, 'coords'):
            start_coords = start_node.coords
        else:
            start_coords = self.parent.geometry.nodes[start_node].coords
            
        if hasattr(end_node, 'coords'):
            end_coords = end_node.coords
        else:
            end_coords = self.parent.geometry.nodes[end_node].coords
        
        # Calculate the vecxz vector first
        vec_xz = calculate_aligned_vecxz(start_coords, end_coords, tol)
        
        # Round vector components to handle floating-point precision
        rounded_vec = tuple(round(v, 6) for v in vec_xz)
        
        # Create key based on type and the actual vector parameters
        key = (transform_type, rounded_vec)
        
        # Check if transformation with these parameters already exists
        if key in self.transformation_map:
            return self.transformation_map[key]
        
        # Create a new transformation
        new_id = max(self.transformations.keys(), default=0) + 1
        
        # Only create in OpenSees if model is initialized
        if self.parent._opensees_initialized:
            ops.geomTransf(transform_type, new_id, *vec_xz)
        
        # Store transformation data
        self.transformations[new_id] = {
            "type": transform_type,
            "vec_xz": vec_xz,
            "key": key
        }
        self.transformation_map[key] = new_id
        
        return new_id

