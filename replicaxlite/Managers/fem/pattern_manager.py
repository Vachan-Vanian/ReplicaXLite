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


class ReplicaXFemPatternManager:
    """
    Manager for all Pattern tables in ReplicaXLite.
    
    Creates a single table with type selection and nested property tables.
    Users select pattern type from dropdown, then properties are stored in nested tables.
    """
    
    def __init__(self, pattern_tab_widget, settings, time_series_table):
        """
        Initialize the pattern manager.
        
        Args:
            pattern_tab_widget: The QWidget container for the pattern tab
        """
        self.pattern_tab_widget = pattern_tab_widget
        self.settings = settings
        self.time_series_table = time_series_table

        layout = QVBoxLayout(self.pattern_tab_widget)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)
        
        # Create the main pattern table (with one less column now: removed 'Name')
        self.table = self.patterns_table = ReplicaXTable(rows=0, columns=5, settings=self.settings)
        
        # Set headers (removed 'Name' from list)
        self.patterns_table.set_column_types(['int', 'str', 'table', 'str', 'str'])
        self.patterns_table.set_headers(['Tag', 'Type', 'Properties', 'Group', 'Comment'])
        
        # Configure dropdown for Type column with valid pattern types
        pattern_types = ['', 'Simple', 'UniformExcitation']
        self.patterns_table.set_dropdown(1, pattern_types)  # Updated index to reflect new structure
        
        self._setup_nested_tables()
        # Initialize the table cells to set up widgets properly
        self.patterns_table.init_table_cells()
        
        layout.addWidget(self.patterns_table)
    
    def _setup_nested_tables(self):
        """Create and setup nested tables for different pattern types."""
        # Create empty table placeholder (for when no type is selected)
        empty_table = ReplicaXTable(rows=0, columns=0)
        
        #----------------------------------------------------------------------------------------------------

        # Create Simple Pattern properties table
        simple_props = ReplicaXTable(rows=1, columns=5, settings=self.settings)
        simple_props.set_column_types(['str', 'int', 'str', 'str', 'str'])
        simple_props.set_headers(['Property', 'Value', 'Optional', 'Group', 'Comment'])
                
        simple_props.set_cell_dropdown(0,1,[])
        simple_props.set_cell_value(0, 0, 'time_series')
        simple_props.set_cell_value(0, 2, 'No')  # Not optional

        # Link dropdown to time series table for the time_series cell
        simple_props.link_dropdown_to_cell(
            row=0,
            col=1,
            source_table=self.time_series_table,
            source_col=0,
            include_empty=True
        )

        # Initialize table cells (this will sync dropdowns)
        simple_props.init_table_cells()

        #----------------------------------------------------------------------------------------------------

        # Create Uniform Excitation Pattern properties table with all relevant parameters
        uniform_excitation_props = ReplicaXTable(rows=7, columns=5, settings=self.settings)
        uniform_excitation_props.set_column_types(['str', 'str', 'str', 'str', 'str'])  # Default to str type for flexibility
        uniform_excitation_props.set_headers(['Property', 'Value', 'Optional', 'Group', 'Comment'])

        uniform_excitation_props.set_cell_dropdown(0,1, [1,2,3,4,5,6])
        uniform_excitation_props.set_cell_dropdown(1,1, [])
        uniform_excitation_props.set_cell_dropdown(2,1, [])
        uniform_excitation_props.set_cell_dropdown(3,1, [])
        uniform_excitation_props.set_cell_dropdown(4,1, [])

        uniform_excitation_props.set_cell_unit(5,1, 'Velocity')

     
        uniform_excitation_props.set_row_types(0, ['str', 'int', 'str', 'str', 'str']) # direction
        uniform_excitation_props.set_row_types(1, ['str', 'int', 'str', 'str', 'str']) # time_series
        uniform_excitation_props.set_row_types(2, ['str', 'int', 'str', 'str', 'str']) # accel_series_tag
        uniform_excitation_props.set_row_types(3, ['str', 'int', 'str', 'str', 'str']) # disp_series_tag
        uniform_excitation_props.set_row_types(4, ['str', 'int', 'str', 'str', 'str']) # vel_series_tag
        uniform_excitation_props.set_row_types(5, ['str', 'float', 'str', 'str', 'str']) # vel0
        uniform_excitation_props.set_row_types(6, ['str', 'float', 'str', 'str', 'str']) # fact

        uniform_excitation_props.set_cell_value(0, 0, 'direction')
        uniform_excitation_props.set_cell_value(0, 2, 'No')
        uniform_excitation_props.set_cell_value(1, 0, 'time_series')
        uniform_excitation_props.set_cell_value(1, 2, 'Yes')
        uniform_excitation_props.set_cell_value(1, 3, 'g1')
        uniform_excitation_props.set_cell_value(2, 0, 'accel_series_tag')
        uniform_excitation_props.set_cell_value(2, 2, 'Yes')
        uniform_excitation_props.set_cell_value(2, 3, 'g2')
        uniform_excitation_props.set_cell_value(3, 0, 'disp_series_tag')
        uniform_excitation_props.set_cell_value(3, 2, 'Yes')
        uniform_excitation_props.set_cell_value(3, 3, 'g2')
        uniform_excitation_props.set_cell_value(4, 0, 'vel_series_tag')
        uniform_excitation_props.set_cell_value(4, 2, 'Yes')
        uniform_excitation_props.set_cell_value(4, 3, 'g2')
        uniform_excitation_props.set_cell_value(5, 0, 'vel0')
        uniform_excitation_props.set_cell_value(5, 2, 'Yes')
        uniform_excitation_props.set_cell_value(6, 0, 'fact')
        uniform_excitation_props.set_cell_value(6, 2, 'Yes')
        
        
        uniform_excitation_props.link_dropdown_to_cell(
            row=1,
            col=1,
            source_table=self.time_series_table,
            source_col=0,
            include_empty=True
        )

        uniform_excitation_props.link_dropdown_to_cell(
            row=2,
            col=1,
            source_table=self.time_series_table,
            source_col=0,
            include_empty=True
        )

        uniform_excitation_props.link_dropdown_to_cell(
            row=3,
            col=1,
            source_table=self.time_series_table,
            source_col=0,
            include_empty=True
        )

        uniform_excitation_props.link_dropdown_to_cell(
            row=4,
            col=1,
            source_table=self.time_series_table,
            source_col=0,
            include_empty=True
        )

        uniform_excitation_props.init_table_cells()

        #----------------------------------------------------------------------------------------------------      
        
        # Link dropdown to nested tables - this connects the type selection to property tables
        self.patterns_table.link_dropdown_to_table(
            dropdown_col=1,      # Type column (now index 1 due to removed Name)
            table_col=2,        # Properties column (adjusted accordingly)
            templates={
                '': empty_table,
                'Simple': simple_props,
                'UniformExcitation': uniform_excitation_props,
            }
        )

    def refresh_dropdown_nested_table_links_after_load(self):
        """Re-establish dropdown links after table load."""
        # Iterate through all rows in pattern table
        for row in range(self.patterns_table.rowCount()):
            # Get the pattern type from column 1 (Type column)
            pattern_type = self.patterns_table.get_cell_value(row, 1)

            # Get nested table reference
            nested_table = self.patterns_table.get_cell_value(row, 2)  # Properties column

            if not isinstance(nested_table, ReplicaXTable):
                continue

            if pattern_type == 'Simple':
                # Simple property table - link time_series dropdown to first cell (row 0)
                nested_table.link_dropdown_to_cell(
                    row=0,
                    col=1,
                    source_table=self.time_series_table,
                    source_col=0,
                    include_empty=True
                )
            elif pattern_type == 'UniformExcitation':
                # Uniform Excitation table - re-establish existing dropdowns
                nested_table.link_dropdown_to_cell(
                    row=1,
                    col=1,
                    source_table=self.time_series_table,
                    source_col=0,
                    include_empty=True
                )
                nested_table.link_dropdown_to_cell(
                    row=2,
                    col=1,
                    source_table=self.time_series_table,
                    source_col=0,
                    include_empty=True
                )
                nested_table.link_dropdown_to_cell(
                    row=3,
                    col=1,
                    source_table=self.time_series_table,
                    source_col=0,
                    include_empty=True
                )
                nested_table.link_dropdown_to_cell(
                    row=4,
                    col=1,
                    source_table=self.time_series_table,
                    source_col=0,
                    include_empty=True
                )





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


class ReplicaXFemPatternManager:
    """
    Manager for all Pattern tables in ReplicaXLite.
    
    Creates a single table with type selection and nested property tables.
    Users select pattern type from dropdown, then properties are stored in nested tables.
    """
    
    def __init__(self, pattern_tab_widget, settings, time_series_table):
        """
        Initialize the pattern manager.
        
        Args:
            pattern_tab_widget: The QWidget container for the pattern tab
        """
        self.pattern_tab_widget = pattern_tab_widget
        self.settings = settings
        self.time_series_table = time_series_table

        layout = QVBoxLayout(self.pattern_tab_widget)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)
        
        # Create the main pattern table (with one less column now: removed 'Name')
        self.table = self.patterns_table = ReplicaXTable(rows=0, columns=5, settings=self.settings)
        
        # Set headers (removed 'Name' from list)
        self.patterns_table.set_column_types(['int', 'str', 'table', 'str', 'str'])
        self.patterns_table.set_headers(['Tag', 'Type', 'Properties', 'Group', 'Comment'])
        
        # Configure dropdown for Type column with valid pattern types
        pattern_types = ['', 'Simple', 'UniformExcitation']
        self.patterns_table.set_dropdown(1, pattern_types)  # Updated index to reflect new structure
        
        self._setup_nested_tables()
        # Initialize the table cells to set up widgets properly
        self.patterns_table.init_table_cells()
        
        layout.addWidget(self.patterns_table)
    
    def _setup_nested_tables(self):
        """Create and setup nested tables for different pattern types."""
        # Create empty table placeholder (for when no type is selected)
        empty_table = ReplicaXTable(rows=0, columns=0)
        
        #----------------------------------------------------------------------------------------------------

        # Create Simple Pattern properties table
        simple_props = ReplicaXTable(rows=1, columns=5, settings=self.settings)
        simple_props.set_column_types(['str', 'int', 'str', 'str', 'str'])
        simple_props.set_headers(['Property', 'Value', 'Optional', 'Group', 'Comment'])
                
        simple_props.set_cell_dropdown(0,1,[])
        simple_props.set_cell_value(0, 0, 'time_series')
        simple_props.set_cell_value(0, 2, 'No')  # Not optional

        # Link dropdown to time series table for the time_series cell
        simple_props.link_dropdown_to_cell(
            row=0,
            col=1,
            source_table=self.time_series_table,
            source_col=0,
            include_empty=True
        )

        # Initialize table cells (this will sync dropdowns)
        simple_props.init_table_cells()

        #----------------------------------------------------------------------------------------------------

        # Create Uniform Excitation Pattern properties table with all relevant parameters
        uniform_excitation_props = ReplicaXTable(rows=7, columns=5, settings=self.settings)
        uniform_excitation_props.set_column_types(['str', 'str', 'str', 'str', 'str'])  # Default to str type for flexibility
        uniform_excitation_props.set_headers(['Property', 'Value', 'Optional', 'Group', 'Comment'])

        uniform_excitation_props.set_cell_dropdown(0,1, [1,2,3,4,5,6])
        uniform_excitation_props.set_cell_dropdown(1,1, [])
        uniform_excitation_props.set_cell_dropdown(2,1, [])
        uniform_excitation_props.set_cell_dropdown(3,1, [])
        uniform_excitation_props.set_cell_dropdown(4,1, [])

        uniform_excitation_props.set_cell_unit(5,1, 'Velocity')

     
        uniform_excitation_props.set_row_types(0, ['str', 'int', 'str', 'str', 'str']) # direction
        uniform_excitation_props.set_row_types(1, ['str', 'int', 'str', 'str', 'str']) # time_series
        uniform_excitation_props.set_row_types(2, ['str', 'int', 'str', 'str', 'str']) # accel_series_tag
        uniform_excitation_props.set_row_types(3, ['str', 'int', 'str', 'str', 'str']) # disp_series_tag
        uniform_excitation_props.set_row_types(4, ['str', 'int', 'str', 'str', 'str']) # vel_series_tag
        uniform_excitation_props.set_row_types(5, ['str', 'float', 'str', 'str', 'str']) # vel0
        uniform_excitation_props.set_row_types(6, ['str', 'float', 'str', 'str', 'str']) # fact

        uniform_excitation_props.set_cell_value(0, 0, 'direction')
        uniform_excitation_props.set_cell_value(0, 2, 'No')
        uniform_excitation_props.set_cell_value(1, 0, 'time_series')
        uniform_excitation_props.set_cell_value(1, 2, 'Yes')
        uniform_excitation_props.set_cell_value(1, 3, 'g1')
        uniform_excitation_props.set_cell_value(2, 0, 'accel_series_tag')
        uniform_excitation_props.set_cell_value(2, 2, 'Yes')
        uniform_excitation_props.set_cell_value(2, 3, 'g2')
        uniform_excitation_props.set_cell_value(3, 0, 'disp_series_tag')
        uniform_excitation_props.set_cell_value(3, 2, 'Yes')
        uniform_excitation_props.set_cell_value(3, 3, 'g2')
        uniform_excitation_props.set_cell_value(4, 0, 'vel_series_tag')
        uniform_excitation_props.set_cell_value(4, 2, 'Yes')
        uniform_excitation_props.set_cell_value(4, 3, 'g2')
        uniform_excitation_props.set_cell_value(5, 0, 'vel0')
        uniform_excitation_props.set_cell_value(5, 2, 'Yes')
        uniform_excitation_props.set_cell_value(6, 0, 'fact')
        uniform_excitation_props.set_cell_value(6, 2, 'Yes')
        
        
        uniform_excitation_props.link_dropdown_to_cell(
            row=1,
            col=1,
            source_table=self.time_series_table,
            source_col=0,
            include_empty=True
        )

        uniform_excitation_props.link_dropdown_to_cell(
            row=2,
            col=1,
            source_table=self.time_series_table,
            source_col=0,
            include_empty=True
        )

        uniform_excitation_props.link_dropdown_to_cell(
            row=3,
            col=1,
            source_table=self.time_series_table,
            source_col=0,
            include_empty=True
        )

        uniform_excitation_props.link_dropdown_to_cell(
            row=4,
            col=1,
            source_table=self.time_series_table,
            source_col=0,
            include_empty=True
        )

        uniform_excitation_props.init_table_cells()

        #----------------------------------------------------------------------------------------------------      
        
        # Link dropdown to nested tables - this connects the type selection to property tables
        self.patterns_table.link_dropdown_to_table(
            dropdown_col=1,      # Type column (now index 1 due to removed Name)
            table_col=2,        # Properties column (adjusted accordingly)
            templates={
                '': empty_table,
                'Simple': simple_props,
                'UniformExcitation': uniform_excitation_props,
            }
        )

    def refresh_dropdown_nested_table_links_after_load(self):
        """Re-establish dropdown links after table load."""
        # Iterate through all rows in pattern table
        for row in range(self.patterns_table.rowCount()):
            # Get the pattern type from column 1 (Type column)
            pattern_type = self.patterns_table.get_cell_value(row, 1)

            # Get nested table reference
            nested_table = self.patterns_table.get_cell_value(row, 2)  # Properties column

            if not isinstance(nested_table, ReplicaXTable):
                continue

            if pattern_type == 'Simple':
                # Simple property table - link time_series dropdown to first cell (row 0)
                nested_table.link_dropdown_to_cell(
                    row=0,
                    col=1,
                    source_table=self.time_series_table,
                    source_col=0,
                    include_empty=True
                )
            elif pattern_type == 'UniformExcitation':
                # Uniform Excitation table - re-establish existing dropdowns
                nested_table.link_dropdown_to_cell(
                    row=1,
                    col=1,
                    source_table=self.time_series_table,
                    source_col=0,
                    include_empty=True
                )
                nested_table.link_dropdown_to_cell(
                    row=2,
                    col=1,
                    source_table=self.time_series_table,
                    source_col=0,
                    include_empty=True
                )
                nested_table.link_dropdown_to_cell(
                    row=3,
                    col=1,
                    source_table=self.time_series_table,
                    source_col=0,
                    include_empty=True
                )
                nested_table.link_dropdown_to_cell(
                    row=4,
                    col=1,
                    source_table=self.time_series_table,
                    source_col=0,
                    include_empty=True
                )

    def create_fem_table_code(self, model):
        """
        Create all patterns from the GUI table.
        
        Args:
            model: StructuralModel instance
        Returns:
            None
        """
        rows = self.patterns_table.rowCount()
        
        for i in range(rows):
            try:
                self.create_fem_table_row_code(model, i)
            except Exception as e:
                print(f"Pattern FEM Table: Error processing row {i}: {e}")
                continue

    def create_fem_table_row_code(self, model, row_index):
        """
        Build a single pattern object from GUI data at specified row index.
        
        Args:
            model: StructuralModel instance
            row_index: Index of the row to process
        Returns:
            True else False
        """
        # Get basic info
        tag = self.patterns_table.get_cell_value(row_index, 0)   # Tag column
        pattern_type = self.patterns_table.get_cell_value(row_index, 1)  # Type column
        properties_table = self.patterns_table.get_cell_value(row_index, 2)  # Properties column
        group = self.patterns_table.get_cell_value(row_index, 3)  # Group column

        if not tag:
            return False
            
        if not pattern_type:
            print(f"Warning: No pattern type specified for row {row_index}")
            return False

        try:
            # Extract parameters based on pattern type
            params = self._extract_parameters(pattern_type, properties_table)
            
            # Create the actual pattern object in model
            if pattern_type == 'Simple':
                time_series_tag = params.get('time_series')
                if time_series_tag is not None:
                    model.loading.create_load_pattern(tag=tag, time_series=time_series_tag)
                else:
                    print(f"Warning: Missing time series for Simple pattern in row {row_index}")
                    return False
                    
            elif pattern_type == 'UniformExcitation':
                # Extract all Uniform Excitation parameters
                direction = params.get('direction')
                time_series_tag = params.get('time_series') 
                accel_series_tag = params.get('accel_series_tag')
                disp_series_tag = params.get('disp_series_tag')
                vel_series_tag = params.get('vel_series_tag')
                vel0 = params.get('vel0', 0.0)
                fact = params.get('fact', 1.0)
                
                if direction is not None:
                    model.loading.create_uniform_excitation_pattern(
                        tag=tag,
                        direction=direction,
                        time_series_tag=time_series_tag,
                        accel_series_tag=accel_series_tag,
                        disp_series_tag=disp_series_tag,
                        vel_series_tag=vel_series_tag,
                        vel0=vel0,
                        fact=fact,
                        group=group
                    )
                else:
                    print(f"Warning: Missing direction for UniformExcitation pattern in row {row_index}")
                    return False
                    
            else:
                # Handle empty or unknown types
                print(f"Warning: Unknown pattern type '{pattern_type}' for row {row_index}")
                return False
                
            return True
            
        except Exception as e:
            print(f"Error building pattern from row {row_index}: {e}")
            return False

    def _extract_parameters(self, pattern_type, nested_table):
        """
        Extract parameters from nested table based on pattern type.
        
        Args:
            pattern_type: The selected pattern type
            nested_table: The properties table for this pattern
            
        Returns:
            dict of parameters
        """
        params = {}
        
        # Handle different pattern types by extracting their specific parameters
        if pattern_type == 'Simple':
            # Extract time_series value (row 0, column 1)
            time_series_value = nested_table.get_cell_value(0, 1)
            if time_series_value is not None:
                params['time_series'] = time_series_value
                
        elif pattern_type == 'UniformExcitation':
            # Extract all Uniform Excitation parameters from the properties table
            try:
                # direction (row 0)
                direction_value = nested_table.get_cell_value(0, 1)
                if direction_value is not None:
                    params['direction'] = direction_value
                    
                # time_series (row 1) 
                time_series_value = nested_table.get_cell_value(1, 1)
                if time_series_value is not None:
                    params['time_series'] = time_series_value
                    
                # accel_series_tag (row 2)
                accel_series_value = nested_table.get_cell_value(2, 1)
                if accel_series_value is not None:
                    params['accel_series_tag'] = accel_series_value
                    
                # disp_series_tag (row 3)
                disp_series_value = nested_table.get_cell_value(3, 1)
                if disp_series_value is not None:
                    params['disp_series_tag'] = disp_series_value
                    
                # vel_series_tag (row 4)
                vel_series_value = nested_table.get_cell_value(4, 1)
                if vel_series_value is not None:
                    params['vel_series_tag'] = vel_series_value
                    
                # vel0 (row 5) - default to 0.0
                vel0_value = nested_table.get_cell_value(5, 1)
                if vel0_value is not None:
                    params['vel0'] = vel0_value
                    
                # fact (row 6) - default to 1.0  
                fact_value = nested_table.get_cell_value(6, 1)
                if fact_value is not None:
                    params['fact'] = fact_value
                    
            except Exception as e:
                print(f"Error extracting Uniform Excitation parameters: {e}")
                
        return params
