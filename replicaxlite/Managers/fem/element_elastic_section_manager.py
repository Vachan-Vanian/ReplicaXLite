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

from PySide6.QtWidgets import QVBoxLayout
from ...UtilityCode.TableGUI import ReplicaXTable


class ReplicaXFemElementElasticSectionManager:
    """
    Manager for the Elastic Sections table in ReplicaXLite.
    
    Creates and manages a ReplicaXTable with columns:
    - Tag (int)
    - Name (str)
    - Structural Element Type (str)
    - Section Shape (str)
    - E Modulus (float)
    - G Modulus (float)
    - Rotation Angle (float)
    - Shear (bool)
    - Color (str)
    - Comment (str)
    """
    
    def __init__(self, elastic_sections_tab_widget, settings):
        """
        Initialize the elastic section manager.
        
        Args:
            elastic_sections_tab_widget: The QWidget container for the elastic sections tab
        """
        self.elastic_sections_tab_widget = elastic_sections_tab_widget
        self.settings = settings

        layout = QVBoxLayout(self.elastic_sections_tab_widget)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)
        
        # Create the elastic sections table with initial rows
        self.table = self.elastic_sections_table = ReplicaXTable(rows=0, columns=11, settings=self.settings)
        
        # Set headers
        self.elastic_sections_table.set_column_types(['int', 'str', 'str', 'str', 'table',
                                                      'float', 'float', 'float', 'bool', 
                                                      'str', 'str'])
        self.elastic_sections_table.set_headers([
            'Tag', 'Name', 'Struct. Elem.\nType', 'Section\nShape', 'Properties',
            'E\nModulus', 'G\nModulus', 'Rotation\nAngle', 'Shear',
            'Color', 'Comment'
        ])
        
        # Set units
        self.elastic_sections_table.set_column_unit(5, 'Stress')  # E Modulus column
        self.elastic_sections_table.set_column_unit(6, 'Stress')  # G Modulus column
        self.elastic_sections_table.set_column_unit(7, 'Angle')   # Rotation Angle column
        
        # Configure dropdowns for structural element types
        structural_element_types = ['beam', 'column', 'wall', 'infill', 'general']
        self.elastic_sections_table.set_dropdown(2, structural_element_types)
        
        # Configure dropdowns for section shapes
        section_shapes = ['', 'rectangle', 't_section', 'l_section', 'i_section', 'circular', 'user_section']
        self.elastic_sections_table.set_dropdown(3, section_shapes)

        # Shear deformation Options
        self.elastic_sections_table.set_dropdown(8, [False, True])
        
        # Link dropdown to nested tables 
        self.elastic_sections_table.link_dropdown_to_table(
            dropdown_col=3,
            table_col=4,
            templates={
                'rectangle': self.rectangle(),
                't_section': self.t_section(),
                'l_section': self.l_section(),
                'i_section': self.i_section(),
                'circular': self.circular(),
                'user_section': self.user_section(),

            }
        )
      
        # Initialize table cells (this will sync dropdowns and other widgets)
        self.elastic_sections_table.init_table_cells()

        layout.addWidget(self.elastic_sections_table)

    def rectangle(self):
        table = ReplicaXTable(rows=2, columns=5, settings=self.settings)
        table.set_column_types(['str', 'float', 'str', 'str', 'str'])
        table.set_headers(['Property', 'Value', 'Optional', 'Group', 'Comment'])

        # Set units
        table.set_cell_unit(0, 1, 'Length')
        table.set_cell_unit(1, 1, 'Length')
        
        # Populate with default values (same as before)
        table.set_cell_value(0, 0, 'width')
        table.set_cell_value(0, 2, 'No')
        table.set_cell_value(1, 0, 'height')
        table.set_cell_value(1, 2, 'No')

        return table

    def t_section(self):
        table = ReplicaXTable(rows=4, columns=5, settings=self.settings)
        table.set_column_types(['str', 'float', 'str', 'str', 'str'])
        table.set_headers(['Property', 'Value', 'Optional', 'Group', 'Comment'])

        # Set units
        table.set_cell_unit(0, 1, 'Length')
        table.set_cell_unit(1, 1, 'Length')
        table.set_cell_unit(2, 1, 'Length')
        table.set_cell_unit(3, 1, 'Length')
        
        # Populate with default values
        table.set_cell_value(0, 0, 'flange_width')
        table.set_cell_value(0, 2, 'No')
        table.set_cell_value(1, 0, 'height')
        table.set_cell_value(1, 2, 'No')
        table.set_cell_value(2, 0, 'flange_thickness')
        table.set_cell_value(2, 2, 'No')
        table.set_cell_value(3, 0, 'web_thickness')
        table.set_cell_value(3, 2, 'No')

        return table

    def l_section(self):
        table = ReplicaXTable(rows=4, columns=5, settings=self.settings)
        table.set_column_types(['str', 'float', 'str', 'str', 'str'])
        table.set_headers(['Property', 'Value', 'Optional', 'Group', 'Comment'])

        # Set units
        table.set_cell_unit(0, 1, 'Length')
        table.set_cell_unit(1, 1, 'Length')
        table.set_cell_unit(2, 1, 'Length')
        table.set_cell_unit(3, 1, 'Length')
        
        # Populate with default values
        table.set_cell_value(0, 0, 'flange_width')
        table.set_cell_value(0, 2, 'No')
        table.set_cell_value(1, 0, 'height')
        table.set_cell_value(1, 2, 'No')
        table.set_cell_value(2, 0, 'flange_thickness')
        table.set_cell_value(2, 2, 'No')
        table.set_cell_value(3, 0, 'web_thickness')
        table.set_cell_value(3, 2, 'No')

        return table

    def i_section(self):
        table = ReplicaXTable(rows=4, columns=5, settings=self.settings)
        table.set_column_types(['str', 'float', 'str', 'str', 'str'])
        table.set_headers(['Property', 'Value', 'Optional', 'Group', 'Comment'])

        # Set units
        table.set_cell_unit(0, 1, 'Length')
        table.set_cell_unit(1, 1, 'Length')
        table.set_cell_unit(2, 1, 'Length')
        table.set_cell_unit(3, 1, 'Length')
        
        # Populate with default values
        table.set_cell_value(0, 0, 'width')
        table.set_cell_value(0, 2, 'No')
        table.set_cell_value(1, 0, 'height')
        table.set_cell_value(1, 2, 'No')
        table.set_cell_value(2, 0, 'flange_thickness')
        table.set_cell_value(2, 2, 'No')
        table.set_cell_value(3, 0, 'web_thickness')
        table.set_cell_value(3, 2, 'No')

        return table

    def circular(self):
        table = ReplicaXTable(rows=1, columns=5, settings=self.settings)
        table.set_column_types(['str', 'float', 'str', 'str', 'str'])
        table.set_headers(['Property', 'Value', 'Optional', 'Group', 'Comment'])

        # Set units
        table.set_cell_unit(0, 1, 'Length')
        
        # Populate with default values
        table.set_cell_value(0, 0, 'radius')
        table.set_cell_value(0, 2, 'No')

        return table

    def user_section(self):
        table = ReplicaXTable(rows=4, columns=5, settings=self.settings)
        table.set_column_types(['str', 'list(float)', 'str', 'str', 'str'])
        table.set_headers(['Property', 'Value', 'Optional', 'Group', 'Comment'])

        # Populate with default values
        table.set_column_unit(1, 'Length')
        table.set_cell_value(0, 0, 'x_outline_points')
        table.set_cell_value(0, 2, 'No')
        table.set_cell_value(1, 0, 'y_outline_points')
        table.set_cell_value(1, 2, 'No')
        table.set_cell_value(2, 0, 'x_hole_points')
        table.set_cell_value(2, 2, 'No')
        table.set_cell_value(3, 0, 'y_hole_points')
        table.set_cell_value(3, 2, 'No')

        return table


    def create_fem_table_code(self, model):
        """
        Create all elastic sections from the GUI table.
        
        Args:
            model: StructuralModel instance
        Returns:
            None
        """
        rows = self.elastic_sections_table.rowCount()
        
        for i in range(rows):
            try:
                self.create_fem_table_row_code(model, i)
            except Exception as e:
                print(f"Elastic Sections FEM Table: Error processing row {i}: {e}")
                continue

    def create_fem_table_row_code(self, model, row_index):
        """
        Build a single elastic section object from GUI data at specified row index.
        
        Args:
            model: StructuralModel instance
            row_index: Index of the row to process
        Returns:
            True else False
        """
        # Get basic info
        tag = self.elastic_sections_table.get_cell_value(row_index, 0)  # Tag column
        name = self.elastic_sections_table.get_cell_value(row_index, 1)  # Name column
        element_type = self.elastic_sections_table.get_cell_value(row_index, 2)  # Structural Element Type column
        section_shape = self.elastic_sections_table.get_cell_value(row_index, 3)  # Section Shape column
        
        if not tag:
            return False

        if not element_type:
            return False
            
        if not section_shape:
            return False
        
        if not name:
            name = f"Section_{tag}"
        
        # Get the E modulus
        e_modulus = self.elastic_sections_table.get_cell_value(row_index, 5)
        
        # Get the G modulus  
        g_modulus = self.elastic_sections_table.get_cell_value(row_index, 6)
        
        # Get rotation angle (default to 0 if not specified)
        rotation_angle = self.elastic_sections_table.get_cell_value(row_index, 7) or 0
        
        # Get shear deformation option
        shear_deformation = self.elastic_sections_table.get_cell_value(row_index, 8)
        print(shear_deformation, type(shear_deformation))
        
        # Get color (default to green if not specified)
        section_color = self.elastic_sections_table.get_cell_value(row_index, 9) or "#88b378"
        
        # Get nested properties table for this row
        nested_table = self.elastic_sections_table.get_cell_value(row_index, 4)  # Properties column

        # Build parameters based on section shape
        try:
            params = self._extract_parameters(section_shape, nested_table)
            
            # Create the actual elastic section object
            model.properties.create_elastic_section(
                tag=tag,
                name=name,
                structural_element_type=element_type,
                section_shape=section_shape,
                shape_params=params,
                E_mod=e_modulus,
                G_mod=g_modulus,
                rotate_angle=rotation_angle,
                section_shear=shear_deformation,
                section_color=section_color
            )
            return True
            
        except Exception as e:
            print(f"Error building elastic section from row {row_index}: {e}")
            return False
    
    def _extract_parameters(self, section_shape, nested_table):
        """
        Extract parameters from nested table based on section shape.
        
        Args:
            section_shape: The selected section shape
            nested_table: The properties table for this section
            
        Returns:
            dict of parameters
        """
        params = {}
        
        # Handle different section shapes by extracting their specific parameters
        if section_shape == 'rectangle':
            # Extract width and height values (index 0, row 0; index 1, row 1)
            width_value = nested_table.get_cell_value(0, 1) 
            if width_value is not None:
                params['width'] = width_value
            
            height_value = nested_table.get_cell_value(1, 1)
            if height_value is not None:
                params['height'] = height_value
        
        elif section_shape == 't_section':
            # Extract flange_width, height, flange_thickness, web_thickness
            flange_width = nested_table.get_cell_value(0, 1)
            if flange_width is not None:
                params['flange_width'] = flange_width
                
            height = nested_table.get_cell_value(1, 1)
            if height is not None:
                params['height'] = height
                
            flange_thickness = nested_table.get_cell_value(2, 1)
            if flange_thickness is not None:
                params['flange_thickness'] = flange_thickness
                
            web_thickness = nested_table.get_cell_value(3, 1)
            if web_thickness is not None:
                params['web_thickness'] = web_thickness
        
        elif section_shape == 'l_section':
            # Extract flange_width, height, flange_thickness, web_thickness
            flange_width = nested_table.get_cell_value(0, 1)
            if flange_width is not None:
                params['flange_width'] = flange_width
                
            height = nested_table.get_cell_value(1, 1)
            if height is not None:
                params['height'] = height
                
            flange_thickness = nested_table.get_cell_value(2, 1)
            if flange_thickness is not None:
                params['flange_thickness'] = flange_thickness
                
            web_thickness = nested_table.get_cell_value(3, 1)
            if web_thickness is not None:
                params['web_thickness'] = web_thickness
        
        elif section_shape == 'i_section':
            # Extract width, height, flange_thickness, web_thickness
            width = nested_table.get_cell_value(0, 1)
            if width is not None:
                params['width'] = width
                
            height = nested_table.get_cell_value(1, 1)
            if height is not None:
                params['height'] = height
                
            flange_thickness = nested_table.get_cell_value(2, 1)
            if flange_thickness is not None:
                params['flange_thickness'] = flange_thickness
                
            web_thickness = nested_table.get_cell_value(3, 1)
            if web_thickness is not None:
                params['web_thickness'] = web_thickness
        
        elif section_shape == 'circular':
            # Extract radius value
            radius_value = nested_table.get_cell_value(0, 1) 
            if radius_value is not None:
                params['radius'] = radius_value
                
        elif section_shape == 'user_section':
            # Extract outline and hole points for user-defined sections
            
            # Get x_outline_points and y_outline_points
            x_outline_points = nested_table.get_cell_value(0, 1)
            y_outline_points = nested_table.get_cell_value(1, 1) 
            
            # Create combined outline points list
            outline_points = [[x, y] for x, y in zip(x_outline_points, y_outline_points)]
            
            # Handle holes (if any exist)
            hole_points = None
            try:
                # Get hole data - assuming it's structured as a nested list of holes
                x_hole_points = nested_table.get_cell_value(2, 1) 
                y_hole_points = nested_table.get_cell_value(3, 1)
                
                if x_hole_points and y_hole_points:
                    hole_points = [[x, y] for x, y in zip(x_hole_points, y_hole_points)]
                    # Ensure the hole is closed (first point equals last point)
                    if hole_points and hole_points[0] != hole_points[-1]:
                        hole_points.append(hole_points[0])
            except:
                pass  # No holes
            
            params['outline_points'] = outline_points
            if hole_points:
                params['hole_points'] = [hole_points]

        return params
