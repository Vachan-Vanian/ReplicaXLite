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


class ReplicaXFemElementFiberSectionManager:
    """
    Manager for the Fiber Sections table in ReplicaXLite.
    
    Creates and manages a ReplicaXTable with columns:
    - Tag (int)
    - Name (str)
    - Structural Element Type (str)
    - Section Shape (str)
    - Properties (table)
    - Cover Thickness (float)
    - Cover Material Tag (int)
    - Core Material Tag (int)
    - Rebar Points (int)
    - Rebar Lines (int)
    - Rebar Circles (int)
    - Section Rotate (float)
    - G Modulus (float)
    - GJ Value (float)
    - Cover Color (str)
    - Core Color (str)
    - Comment (str)
    """
    
    def __init__(self, fiber_sections_tab_widget, settings, materials_table, rebar_points_table, rebar_lines_table, rebar_circles_table):
        """
        Initialize the fiber section manager.
        
        Args:
            fiber_sections_tab_widget: The QWidget container for the fiber sections tab
        """
        self.fiber_sections_tab_widget = fiber_sections_tab_widget
        self.settings = settings
        self.materials_table = materials_table
        self.rebar_points_table = rebar_points_table 
        self.rebar_lines_table = rebar_lines_table
        self.rebar_circles_table = rebar_circles_table

        layout = QVBoxLayout(self.fiber_sections_tab_widget)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)
        
        # Create the fiber sections table with initial rows
        self.table = self.fiber_sections_table = ReplicaXTable(rows=0, columns=17, settings=self.settings)
        
        # Set headers
        self.fiber_sections_table.set_column_types(['int', 'str', 'str', 'str', 'table',
                                                    'float', 'int', 'int',
                                                    'list(str)', 'list(str)', 'list(str)',
                                                    'float', 'float', 'float', 
                                                    'str', 'str', 'str'])
        self.fiber_sections_table.set_headers([
            'Tag', 'Name', 'Struct. Elem.\nType', 'Section\nShape', 'Properties',
            'Cover\nThickness', 'Cover \nMat. Tag', 'Core \nMat. Tag', 
            'Rebar\nPoints', 'Rebar\nLines', 'Rebar\nCircles', 
            'Section\nRotate','G', 'GJ',
            'Cover\nColor', 'Core\nColor', 'Comment'
        ])
        
        # Set units
        self.fiber_sections_table.set_column_unit(5, 'Length') # Cover Thickness
        self.fiber_sections_table.set_column_unit(11, 'Angle')  # Section Rotate
        self.fiber_sections_table.set_column_unit(12, 'E_G_K_Modulus')  # G
        self.fiber_sections_table.set_column_unit(13, 'Torsional_Rigidity')  # GJ
        
        # Configure dropdowns for structural element types
        structural_element_types = ['beam', 'column', 'wall', 'infill', 'general']
        self.fiber_sections_table.set_dropdown(2, structural_element_types)
        
        # Configure dropdowns for section shapes
        section_shapes = ['', 'rectangle', 't_section', 'l_section', 'i_section', 'circular', 'user_section']
        self.fiber_sections_table.set_dropdown(3, section_shapes)

        self.fiber_sections_table.set_dropdown(6, [])
        self.fiber_sections_table.set_dropdown(7, [])
        self.fiber_sections_table.set_dropdown(8, [], multi=True)
        self.fiber_sections_table.set_dropdown(9, [], multi=True)
        self.fiber_sections_table.set_dropdown(10, [], multi=True)
        
        # Link dropdown to nested tables - this connects the type selection to property tables
        self.fiber_sections_table.link_dropdown_to_table(
            dropdown_col=3,      # Section Shape column (index 3)
            table_col=4,        # Properties column (index 4)
            templates={
                'rectangle': self.rectangle(),
                't_section': self.t_section(),
                'l_section': self.l_section(),
                'i_section': self.i_section(),
                'circular': self.circular(),
                'user_section': self.user_section(),

            }
        )

        self.fiber_sections_table.link_dropdown_to_column(
            dropdown_col=6,
            source_table=self.materials_table,
            source_col=0,
            include_empty=True
        )

        self.fiber_sections_table.link_dropdown_to_column(
            dropdown_col=7,
            source_table=self.materials_table,
            source_col=0,
            include_empty=True
        )

        self.fiber_sections_table.link_dropdown_to_column(
            dropdown_col=8,
            source_table=self.rebar_points_table,
            source_col=0,
            include_empty=True
        )

        self.fiber_sections_table.link_dropdown_to_column(
            dropdown_col=9,
            source_table=self.rebar_lines_table,
            source_col=0,
            include_empty=True
        )

        self.fiber_sections_table.link_dropdown_to_column(
            dropdown_col=10,
            source_table=self.rebar_circles_table,
            source_col=0,
            include_empty=True
        )
        
        # Initialize table cells (this will sync dropdowns and other widgets)
        self.fiber_sections_table.init_table_cells()

        layout.addWidget(self.fiber_sections_table)

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

    def create_fem_table_code(self, model):
        """
        Create all fiber sections from the GUI table.
        
        Args:
            model: StructuralModel instance
        Returns:
            None
        """
        print("=== Starting create_fem_table_code ===")
        rows = self.fiber_sections_table.rowCount()
        print(f"Processing {rows} rows")
        
        for i in range(rows):
            try:
                print(f"Processing row {i}")
                result = self.create_fem_table_row_code(model, i)
                print(f"Row {i} processing result: {result}")
            except Exception as e:
                print(f"Fiber Sections FEM Table: Error processing row {i}: {e}")
                import traceback
                traceback.print_exc()
                continue

    def create_fem_table_row_code(self, model, row_index):
        """
        Build a single fiber section object from GUI data at specified row index.
        
        Args:
            model: StructuralModel instance
            row_index: Index of the row to process
        Returns:
            True else False
        """
        print(f"\n=== Processing Fiber Section Row {row_index} ===")
        
        # Get basic info - same as elastic version but with more fields
        tag = self.fiber_sections_table.get_cell_value(row_index, 0)  # Tag column
        name = self.fiber_sections_table.get_cell_value(row_index, 1)  # Name column
        element_type = self.fiber_sections_table.get_cell_value(row_index, 2)  # Structural Element Type column
        section_shape = self.fiber_sections_table.get_cell_value(row_index, 3)  # Section Shape column
        
        print(f"Tag: {tag}, Name: {name}, Element type: {element_type}, Section shape: {section_shape}")
        
        if not tag:
            print("ERROR: No tag found")
            return False

        if not element_type:
            print("ERROR: No element type found")
            return False
            
        if not section_shape:
            print("ERROR: No section shape found")  
            return False
        
        if not name:
            name = f"Section_{tag}"
            print(f"Set default name to: {name}")
        
        # Get additional fiber-specific properties
        cover_thickness = self.fiber_sections_table.get_cell_value(row_index, 5)
        cover_mat_tag = self.fiber_sections_table.get_cell_value(row_index, 6) 
        core_mat_tag = self.fiber_sections_table.get_cell_value(row_index, 7)
        
        # Get rebar references (these are group names or None)
        rebar_points_ref = self.fiber_sections_table.get_cell_value(row_index, 8)  # Points group name
        rebar_lines_ref = self.fiber_sections_table.get_cell_value(row_index, 9)   # Lines group name  
        rebar_circles_ref = self.fiber_sections_table.get_cell_value(row_index, 10) # Circles group name
        
        print(f"Rebar references - Points: {rebar_points_ref}, Lines: {rebar_lines_ref}, Circles: {rebar_circles_ref}")
        
        # Get rotation angle (default to 0 if not specified)
        section_rotate = self.fiber_sections_table.get_cell_value(row_index, 11) or 0
        
        # Get G modulus and GJ values
        g_modulus = self.fiber_sections_table.get_cell_value(row_index, 12)
        gj_value = self.fiber_sections_table.get_cell_value(row_index, 13)
        
        # Get colors (default to green if not specified)
        cover_color = self.fiber_sections_table.get_cell_value(row_index, 14) or "#dbb40c" 
        core_color = self.fiber_sections_table.get_cell_value(row_index, 15) or "#88b378"
        
        # Get comment
        comment = self.fiber_sections_table.get_cell_value(row_index, 16)
        
        print(f"Other properties - Cover thickness: {cover_thickness}, G modulus: {g_modulus}")
        
        # Get nested properties table for this row
        nested_table = self.fiber_sections_table.get_cell_value(row_index, 4)  # Properties column

        # Build parameters based on section shape
        try:
            print("Extracting parameters...")
            params = self._extract_parameters(section_shape, nested_table)
            print(f"Params extracted: {params}")
            
            # Construct rebar dictionaries from the reference groups
            rebar_points = None
            rebar_lines = None
            rebar_circles = None
            
            # Process rebar points - create dictionary with group data (if referenced)
            if rebar_points_ref:
                try:
                    print(f"Building rebar point dict for: {rebar_points_ref}")
                    rebar_points = self._build_rebar_point_dict(rebar_points_ref)
                    print(f"Rebar points built successfully: {rebar_points}")
                except Exception as e:
                    print(f"ERROR processing rebar points for section {tag}: {e}")
                    import traceback
                    traceback.print_exc()
            
            # Process rebar lines - create dictionary with group data (if referenced)  
            if rebar_lines_ref and isinstance(rebar_lines_ref, list):
                try:
                    print(f"Building rebar line dicts for: {rebar_lines_ref}")
                    rebar_lines = self._build_rebar_line_dict_multi(rebar_lines_ref)
                    print(f"Rebar lines built successfully: {rebar_lines}")
                except Exception as e:
                    print(f"ERROR processing rebar lines for section {tag}: {e}")
                    import traceback
                    traceback.print_exc()
            elif rebar_lines_ref and isinstance(rebar_lines_ref, str):
                try:
                    print(f"Building single rebar line dict for: {rebar_lines_ref}")
                    rebar_lines = self._build_rebar_line_dict_single(rebar_lines_ref)
                    print(f"Rebar lines built successfully: {rebar_lines}")
                except Exception as e:
                    print(f"ERROR processing rebar lines for section {tag}: {e}")
                    import traceback
                    traceback.print_exc()
                    
            # Process rebar circles - create dictionary with group data (if referenced)
            if rebar_circles_ref and isinstance(rebar_circles_ref, list):
                try:
                    print(f"Building rebar circle dicts for: {rebar_circles_ref}")
                    rebar_circles = self._build_rebar_circle_dict_multi(rebar_circles_ref)
                    print(f"Rebar circles built successfully: {rebar_circles}")
                except Exception as e:
                    print(f"ERROR processing rebar circles for section {tag}: {e}")
                    import traceback
                    traceback.print_exc()
            elif rebar_circles_ref and isinstance(rebar_circles_ref, str):
                try:
                    print(f"Building single rebar circle dict for: {rebar_circles_ref}")
                    rebar_circles = self._build_rebar_circle_dict_single(rebar_circles_ref)
                    print(f"Rebar circles built successfully: {rebar_circles}")
                except Exception as e:
                    print(f"ERROR processing rebar circles for section {tag}: {e}")
                    import traceback
                    traceback.print_exc()
            
            # Create the actual fiber section object
            print("Creating fiber section...")
            model.properties.create_fiber_section(
                tag=tag,
                name=name,
                structural_element_type=element_type,
                section_shape=section_shape,
                shape_params=params,
                section_cover=cover_thickness,
                cover_mat_tag=cover_mat_tag,
                core_mat_tag=core_mat_tag,
                rebar_points=rebar_points,  # Dictionary of rebar groups
                rebar_lines=rebar_lines,    # Dictionary of rebar groups  
                rebar_circles=rebar_circles, # Dictionary of rebar groups
                section_rotate=section_rotate,
                G=g_modulus,
                GJ=gj_value,
                cover_color=cover_color,
                core_color=core_color
                # comment=comment
            )
            print(f"Successfully created fiber section {tag}")
            return True
            
        except Exception as e:
            print(f"Error building fiber section from row {row_index}: {e}")
            import traceback
            traceback.print_exc()
            return False

    def _build_rebar_point_dict_multi(self, group_names):
        """Build multiple rebar point dictionaries from a list of group names."""
        result = {}
        for group_name in group_names:
            try:
                dict_result = self._build_rebar_point_dict_single(group_name)
                if dict_result:
                    result.update(dict_result)
            except Exception as e:
                print(f"Error building point dict for group {group_name}: {e}")
        return result

    def _build_rebar_point_dict_single(self, group_name):
        """Build single rebar point dictionary from the reference group name."""
        print(f"Building rebar point dict for group: '{group_name}'")
        
        # This would access data from self.rebar_points_table
        # Find matching row and extract data structure
        
        if not group_name:
            return {}
            
        rows = self.rebar_points_table.rowCount()
        print(f"Checking {rows} rows in rebar points table for group '{group_name}'")
        
        for i in range(rows):
            existing_group_name = self.rebar_points_table.get_cell_value(i, 0)  # group_name column
            print(f"Comparing with row {i}, group name: '{existing_group_name}'")
            
            if existing_group_name == group_name:
                points_data = self.rebar_points_table.get_cell_value(i, 2)  # points table
                
                print(f"Found matching group. Points data type: {type(points_data)}")
                
                # Extract point data from the nested table (X,Y coordinates)
                if points_data and isinstance(points_data, ReplicaXTable):
                    # Build list of [x,y] tuples
                    point_list = []
                    for j in range(points_data.rowCount()):
                        x_val = points_data.get_cell_value(j, 0)
                        y_val = points_data.get_cell_value(j, 1) 
                        if x_val is not None and y_val is not None:
                            point_list.append([x_val, y_val])
                    
                    print(f"Point list: {point_list}")
                    
                    # Get other properties for this group
                    dia = self.rebar_points_table.get_cell_value(i, 3)
                    mat_tag = self.rebar_points_table.get_cell_value(i, 4) 
                    color = self.rebar_points_table.get_cell_value(i, 5)
                    
                    print(f"Other props - Dia: {dia}, Mat tag: {mat_tag}, Color: {color}")
                    
                    return {
                        group_name: {
                            "points": point_list,
                            "dia": dia,
                            "mat_tag": mat_tag,
                            "color": color
                        }
                    }
        
        # If no matching group found - this could also be an issue, but just return empty dict for now
        print(f"No matching group found for '{group_name}'")
        return {group_name: {}}

    def _build_rebar_line_dict_multi(self, group_names):
        """Build multiple rebar line dictionaries from a list of group names."""
        result = {}
        for group_name in group_names:
            try:
                dict_result = self._build_rebar_line_dict_single(group_name)
                if dict_result:
                    result.update(dict_result)
            except Exception as e:
                print(f"Error building line dict for group {group_name}: {e}")
        return result

    def _build_rebar_line_dict_single(self, group_name):
        """Build single rebar line dictionary from the reference group name."""
        print(f"Building rebar line dict for group: '{group_name}'")
        
        # Find matching row and extract data structure
        if not group_name:
            return {}
            
        rows = self.rebar_lines_table.rowCount()
        print(f"Checking {rows} rows in rebar lines table for group '{group_name}'")
        
        for i in range(rows):
            existing_group_name = self.rebar_lines_table.get_cell_value(i, 0)  # group_name column
            print(f"Comparing with row {i}, group name: '{existing_group_name}'")
            
            if existing_group_name == group_name:
                # Extract line parameters directly from table cells (no nested tables needed)
                x_start = self.rebar_lines_table.get_cell_value(i, 1)
                y_start = self.rebar_lines_table.get_cell_value(i, 2) 
                x_end = self.rebar_lines_table.get_cell_value(i, 3)
                y_end = self.rebar_lines_table.get_cell_value(i, 4)
                
                dia = self.rebar_lines_table.get_cell_value(i, 5)
                n_rebars = self.rebar_lines_table.get_cell_value(i, 6)
                mat_tag = self.rebar_lines_table.get_cell_value(i, 7) 
                color = self.rebar_lines_table.get_cell_value(i, 8)
                
                print(f"Line data: X_start={x_start}, Y_start={y_start}, X_end={x_end}, Y_end={y_end}")
                print(f"Other props - Dia: {dia}, N_rebars: {n_rebars}, Mat tag: {mat_tag}, Color: {color}")
                
                return {
                    group_name: {
                        "points": [[x_start, y_start], [x_end, y_end]],
                        "dia": dia,
                        "n": n_rebars,
                        "mat_tag": mat_tag,
                        "color": color
                    }
                }
        
        # If no matching group found 
        print(f"No matching group found for '{group_name}'")
        return {group_name: {}}

    def _build_rebar_circle_dict_multi(self, group_names):
        """Build multiple rebar circle dictionaries from a list of group names."""
        result = {}
        for group_name in group_names:
            try:
                dict_result = self._build_rebar_circle_dict_single(group_name)
                if dict_result:
                    result.update(dict_result)
            except Exception as e:
                print(f"Error building circle dict for group {group_name}: {e}")
        return result

    def _build_rebar_circle_dict_single(self, group_name):
        """Build single rebar circle dictionary from the reference group name."""
        print(f"Building rebar circle dict for group: '{group_name}'")
        
        # Find matching row and extract data structure
        if not group_name:
            return {}
            
        rows = self.rebar_circles_table.rowCount()
        print(f"Checking {rows} rows in rebar circles table for group '{group_name}'")
        
        for i in range(rows):
            existing_group_name = self.rebar_circles_table.get_cell_value(i, 0)  # group_name column
            print(f"Comparing with row {i}, group name: '{existing_group_name}'")
            
            if existing_group_name == group_name:
                # Extract circle parameters directly from table cells (no nested tables needed)
                center_x = self.rebar_circles_table.get_cell_value(i, 1)
                center_y = self.rebar_circles_table.get_cell_value(i, 2) 
                radius = self.rebar_circles_table.get_cell_value(i, 3)
                
                dia = self.rebar_circles_table.get_cell_value(i, 4)
                angles = self.rebar_circles_table.get_cell_value(i, 5)
                mat_tag = self.rebar_circles_table.get_cell_value(i, 6) 
                color = self.rebar_circles_table.get_cell_value(i, 7)
                
                print(f"Circle data: Center=({center_x}, {center_y}), Radius={radius}")
                print(f"Other props - Dia: {dia}, Angles: {angles}, Mat tag: {mat_tag}, Color: {color}")
                
                return {
                    group_name: {
                        "xo": [center_x, center_y],
                        "radius": radius,
                        "dia": dia,
                        "angles": angles or [],
                        "mat_tag": mat_tag,
                        "color": color
                    }
                }
        
        # If no matching group found 
        print(f"No matching group found for '{group_name}'")
        return {group_name: {}}
