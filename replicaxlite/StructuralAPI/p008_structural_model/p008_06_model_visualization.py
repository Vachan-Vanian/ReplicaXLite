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


import opstool.vis.pyvista as opsvis
import pyvista as pv
import numpy as np


class ModelVisualization:
    """Handles visualization functions for the structural model"""
    
    def __init__(self, parent_model):
        self.parent = parent_model
        self.opsvis = opsvis
    
    def visualize_model(self, odb_tag=None, show_nodes=True, show_elements=True, 
                    show_local_axes=True, show_loads=True, style="surface",
                    color=None, show_bc=True, bc_scale=1.0, show_link=True,
                    show_mp_constraint=True, show_constraint_dofs=False,
                    show_ele_loads=False, load_scale=1.0, local_axes_scale=1.0,
                    show_outline=False, show_legend=False, cpos="iso"):
        """
        Visualize the structural model with comprehensive options.
        
        Parameters:
        -----------
        odb_tag : str or None
            Tag of the output database (None uses current model state)
        show_nodes : bool
            Whether to show node numbers
        show_elements : bool
            Whether to show element numbers
        show_local_axes : bool
            Whether to show local element axes
        show_loads : bool
            Whether to show nodal loads
        style : str
            Visualization style ('surface', 'wireframe', 'points', 'points_gaussian')
        color : str or None
            Model display color
        show_bc : bool
            Whether to display boundary supports
        bc_scale : float
            Scale the size of boundary support display
        show_link : bool
            Whether to show link elements
        show_mp_constraint : bool
            Whether to show multipoint constraints
        show_constraint_dofs : bool
            Whether to show DOFs of MP-constraints
        show_ele_loads : bool
            Whether to show element loads
        load_scale : float
            Scale the size of load arrow presentation
        local_axes_scale : float
            Scale the presentation size of local axes
        show_outline : bool
            Whether to display the outline of the model
        show_legend : bool
            Whether to show legend
        cpos : str
            Model display perspective ("iso", "xy", "yx", "xz", "zx", "yz", "zy")
            
        Returns:
        --------
        object
            Visualization figure object
        """
        
        # If model is not built yet, build it but don't run any analysis
        if not self.parent._model_built:
            self.parent._log("Building model for visualization...")
            self.parent.build_model()
              
        # Create visualization
        fig_model = self.opsvis.plot_model(
            odb_tag=odb_tag,
            show_node_numbering=show_nodes, 
            show_ele_numbering=show_elements, 
            style=style,
            color=color,
            show_bc=show_bc,
            bc_scale=bc_scale,
            show_link=show_link,
            show_mp_constraint=show_mp_constraint,
            show_constraint_dofs=show_constraint_dofs,
            show_nodal_loads=show_loads,
            show_ele_loads=show_ele_loads,
            load_scale=load_scale,
            show_local_axes=show_local_axes,
            local_axes_scale=local_axes_scale,
            show_outline=show_outline,
            show_legend=show_legend,
            cpos=cpos
        )
        
        self.parent._log("Model visualization created")
        return fig_model
    
    def visualize_section_forces(self, odb_tag: str = "static", section_forces: list = None):
        """
        Visualize section forces from analysis results.
        
        Parameters:
        -----------
        odb_tag : str
            Tag of the output database
        section_forces : list
            List of section forces to visualize
            
        Returns:
        --------
        dict
            Dict of visualization figures
        """
        
        if section_forces is None:
            section_forces = ["N", "MZ", "VY", "MY", "VZ", "T"]
        
        figures = {}
        self.parent._log(f"Creating visualization for section forces: {section_forces}")
        
        for section_force in section_forces:
            fig = opsvis.plot_frame_responses(
                odb_tag=odb_tag,
                resp_type="sectionForces",
                resp_dof=section_force,
                slides=True,
                scale=1.0,
                line_width=3,
                show_values=True
            )
            fig.show_axes()
            figures[section_force] = fig
        
        return figures
    
    def visualize_deformation(self, odb_tag: str = "static", scale_factor: float = 1.0,
                            show_undeformed: bool = False, resp_type: str = "disp",
                            resp_dof: str = "UX,UY,UZ", cpos: str = "iso",
                            show_bc: bool = True, slides: bool = True,
                            show_mp_constraint: bool = False, style: str = "surface"):
        """
        Visualize deformed shape from analysis results with enhanced options.
        
        Parameters:
        -----------
        odb_tag : str
            Tag of the output database
        scale_factor : float
            Magnification factor for deformations
        show_undeformed : bool
            Whether to show the undeformed shape
        resp_type : str
            Type of response ("disp", "vel", "accel", "reaction", etc.)
        resp_dof : str
            Components to visualize ("UX", "UY", "UZ", "RX", "RY", "RZ")
            Can be provided as comma-separated string or list
        cpos : str
            Visualization perspective ("iso", "xy", "yz", etc.)
        show_bc : bool
            Whether to display boundary supports
        slides : bool
            Whether to show step-by-step slideshow
        show_mp_constraint : bool
            Whether to show multi-point constraints
        style : str
            Visualization style ("surface", "wireframe", "points", "points_gaussian")
            
        Returns:
        --------
        object
            Visualization figure
        """
        # Process resp_dof if it's a comma-separated string
        if isinstance(resp_dof, str) and "," in resp_dof:
            resp_dof = resp_dof.split(",")
        
        self.parent._log(f"Creating deformation visualization with scale factor {scale_factor}")
        
        fig = opsvis.plot_nodal_responses(
            odb_tag=odb_tag,
            slides=slides,
            # scale=scale_factor,
            show_defo=True,
            resp_type=resp_type,
            resp_dof=resp_dof,
            cpos=cpos,
            show_bc=show_bc,
            show_mp_constraint=show_mp_constraint,
            show_undeformed=show_undeformed,
            style=style,
            show_outline=True
        )
        fig.show_axes()
        
        return fig


    ### UNDER REVIEW
    def visualize_geometry(self, 
                        show_nodes: bool = True, 
                        show_element_ids: bool = True, 
                        node_size: float = 5.0, 
                        line_width: float = 2.0):
        """
        Visualize the geometric model using PyVista without modifying OpenSees model.
        
        Parameters:
        -----------
        show_nodes : bool
            Whether to show node points
        show_element_ids : bool
            Whether to show element IDs
        node_size : float
            Size of node points in visualization
        line_width : float
            Width of element lines
        
        Returns:
        --------
        pyvista.Plotter
            Visualization plotter object
        """
        # Collect node coordinates
        nodes = self.parent.geometry.nodes
        node_coords = np.array([list(node.coords) for node in nodes.values()])
        
        # Collect element connections
        elements = self.parent.geometry.elements
        
        # Create PyVista plotter
        plotter = pv.Plotter()
        
        # Plot nodes
        if show_nodes:
            cloud = pv.PolyData(node_coords)
            plotter.add_mesh(cloud, 
                            color='red', 
                            point_size=node_size, 
                            render_points_as_spheres=True)
            
            # Add node labels if needed
            if show_nodes:
                for node in nodes.values():
                    plotter.add_point_labels(
                        [node.coords], 
                        [str(node.tag)], 
                        point_size=node_size, 
                        font_size=10
                    )
        
        # Plot elements as lines
        for element in elements.values():
            start_node = element.get_start_node()
            end_node = element.get_end_node()
            
            # Create line between nodes
            line = pv.Line(start_node.coords, end_node.coords)
            
            # Color based on element type
            color_map = {
                'column': 'red',
                'beam': 'green',
                'beam_x': 'green',
                'beam_y': 'green',
                'wall': 'orange',
                'default': 'blue'
            }
            color = color_map.get(element.structural_type, color_map['default'])
            
            plotter.add_mesh(line, 
                            color=color, 
                            line_width=line_width)
            
            # Add element ID if requested
            if show_element_ids:
                midpoint = [(start_node.coords[i] + end_node.coords[i])/2 for i in range(3)]
                plotter.add_point_labels(
                    [midpoint], 
                    [str(element.tag)], 
                    font_size=10
                )
        
        # Configure view
        plotter.show_axes()
        plotter.set_background('white')
        
        
        return plotter

