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


class ReplicaXFemTimeSeriesManager:
    """
    Manager for all Time Series tables in ReplicaXLite.

    Creates a single table with type selection and nested property tables.
    Users select time series type from dropdown, then properties are stored in nested tables.
    """

    def __init__(self, time_series_tab_widget, settings):
        """
        Initialize the time series manager.

        Args:
            time_series_tab_widget: The QWidget container for the time series tab
        """
        self.time_series_tab_widget = time_series_tab_widget
        self.settings = settings

        layout = QVBoxLayout(self.time_series_tab_widget)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)

        # Create the main time series table with 4 columns 
        self.table = self.time_series_table = ReplicaXTable(rows=0, columns=4, settings=self.settings)

        # Set headers - removed 'Name' and added 'Comment'
        self.time_series_table.set_column_types(['int', 'str', 'table', 'str'])
        self.time_series_table.set_headers(['Tag', 'Type', 'Properties', 'Comment'])

        # Configure dropdown for Type column with valid time series types
        time_series_types = ['', 'Constant', 'Linear', 'Path']
        self.time_series_table.set_dropdown(1, time_series_types)  # Column index for Type is now 1

        self._setup_nested_tables()
        # Initialize the table cells to set up widgets properly
        self.time_series_table.init_table_cells()

        layout.addWidget(self.time_series_table)

    def _setup_nested_tables(self):
        """Create and setup nested tables for different time series types."""
        # Create empty table placeholder (for when no type is selected)
        empty_table = ReplicaXTable(rows=0, columns=0)

        # Create Constant Time Series properties table
        constant_props = ReplicaXTable(rows=1, columns=5, settings=self.settings)
        constant_props.set_column_types(['str', 'float', 'str', 'str', 'str'])
        constant_props.set_headers(['Property', 'Value', 'Optional', 'Group', 'Comment'])
        constant_props.init_table_cells()
        constant_props.set_cell_value(0, 0, 'factor')
        constant_props.set_cell_value(0, 1, 1.0)  # Default factor

        # Create Linear Time Series properties table
        linear_props = ReplicaXTable(rows=1, columns=5, settings=self.settings)
        linear_props.set_column_types(['str', 'float', 'str', 'str', 'str'])
        linear_props.set_headers(['Property', 'Value', 'Optional', 'Group', 'Comment'])
        linear_props.init_table_cells()
        linear_props.set_cell_value(0, 0, 'factor')
        linear_props.set_cell_value(0, 1, 1.0)  # Default factor

        # Create Path Time Series properties table with all relevant parameters
        path_props = ReplicaXTable(rows=9, columns=5, settings=self.settings)
        path_props.set_column_types(['str', 'float', 'str', 'str', 'str'])
        path_props.set_headers(['Property', 'Value', 'Optional', 'Group', 'Comment'])

        # Override column types for specific rows (same as before)
        path_props.set_row_types(1, ['str', 'list(float)', 'str', 'str', 'str'])
        path_props.set_row_types(2, ['str', 'list(float)', 'str', 'str', 'str'])
        path_props.set_row_types(3, ['str', 'str', 'str', 'str', 'str'])
        path_props.set_row_types(4, ['str', 'str', 'str', 'str', 'str'])
        path_props.set_row_types(7, ['str', 'bool', 'str', 'str', 'str'])
        path_props.set_row_types(8, ['str', 'bool', 'str', 'str', 'str'])

        # Set units
        path_props.set_cell_unit(0, 1, 'Time')
        path_props.set_cell_unit(2, 1, 'Time')
        path_props.set_cell_unit(6, 1, 'Time')

        path_props.set_cell_dropdown(7,1,[False, True])
        path_props.set_cell_dropdown(8,1,[False, True])

        # Populate with default values (same as before)
        path_props.set_cell_value(0, 0, 'dt')
        path_props.set_cell_value(0, 1, 0.0)
        path_props.set_cell_value(0, 2, 'No')
        path_props.set_cell_value(0, 3, '')
        path_props.set_cell_value(1, 0, 'values')
        path_props.set_cell_value(1, 1, None)
        path_props.set_cell_value(1, 2, 'No')
        path_props.set_cell_value(1, 3, 'g1')
        path_props.set_cell_value(2, 0, 'time')
        path_props.set_cell_value(2, 1, None)
        path_props.set_cell_value(2, 2, 'No')
        path_props.set_cell_value(2, 3, 'g1')
        path_props.set_cell_value(3, 0, 'file_path')
        path_props.set_cell_value(3, 1, "")
        path_props.set_cell_value(3, 2, 'No')
        path_props.set_cell_value(3, 3, 'g1')
        path_props.set_cell_value(4, 0, 'file_time')
        path_props.set_cell_value(4, 1, "")
        path_props.set_cell_value(4, 2, 'No')
        path_props.set_cell_value(4, 3, 'g1')
        path_props.set_cell_value(5, 0, 'factor')
        path_props.set_cell_value(5, 1, 1.0)
        path_props.set_cell_value(5, 2, 'Yes')
        path_props.set_cell_value(6, 0, 'start_time')
        path_props.set_cell_value(6, 1, 0.0)
        path_props.set_cell_value(6, 2, 'Yes')
        path_props.set_cell_value(7, 0, 'use_last')
        path_props.set_cell_value(7, 2, 'Yes')
        path_props.set_cell_value(8, 0, 'prepend_zero')
        path_props.set_cell_value(8, 2, 'Yes')

        # Link dropdown to nested tables - adjust column indices accordingly
        self.time_series_table.link_dropdown_to_table(
            dropdown_col=1,      # Updated index for Type column (was 2)
            table_col=2,         # Properties column (was 3)
            templates={
                '': empty_table,
                'Constant': constant_props,
                'Linear': linear_props,
                'Path': path_props
            }
        )




    def create_fem_table_code(self, model):
        """
        Create all time series from the GUI table.
        
        Args:
            model: StructuralModel instance
        Returns:
            None
        """
        rows = self.time_series_table.rowCount()
        
        for i in range(rows):
            try:
                self.create_fem_table_row_code(model, i)
            except Exception as e:
                print(f"Time Series FEM Table: Error processing row {i}: {e}")
                continue

    def create_fem_table_row_code(self, model, row_index):
        """
        Build a single time series object from GUI data at specified row index.
        
        Args:
            model: StructuralModel instance
            row_index: Index of the row to process
        Returns:
            True else False
        """
        # Get basic info
        tag = self.time_series_table.get_cell_value(row_index, 0)   # Tag column
        time_series_type = self.time_series_table.get_cell_value(row_index, 1)  # Type column
        properties_table = self.time_series_table.get_cell_value(row_index, 2)  # Properties column

        if not tag:
            return False
            
        if not time_series_type:
            print(f"Warning: No time series type specified for row {row_index}")
            return False

        try:
            # Extract parameters based on time series type
            params = self._extract_parameters(time_series_type, properties_table)
            
            # Create the actual time series object in model
            # Assuming model has a method like create_time_series or similar
            if time_series_type == 'Constant':
                model.loading.create_constant_time_series(tag=tag, factor=params.get('factor', 1.0))
            elif time_series_type == 'Linear':
                model.loading.create_linear_time_series(tag=tag, factor=params.get('factor', 1.0))
            elif time_series_type == 'Path':
                # Extract all Path-specific parameters
                params_dict = {
                    'dt': params.get('dt'),
                    'values': params.get('values'),
                    'time': params.get('time'),
                    'file_path': params.get('file_path'),
                    'file_time': params.get('file_time'),
                    'factor': params.get('factor', 1.0),
                    'start_time': params.get('start_time', 0.0),
                    'use_last': params.get('use_last', False),
                    'prepend_zero': params.get('prepend_zero', False)
                }
                model.loading.create_path_time_series(tag=tag, **params_dict)
            else:
                # Handle empty or unknown types
                print(f"Warning: Unknown time series type '{time_series_type}' for row {row_index}")
                return False
                
            return True
            
        except Exception as e:
            print(f"Error building time series from row {row_index}: {e}")
            return False

    def _extract_parameters(self, time_series_type, nested_table):
        """
        Extract parameters from nested table based on time series type.
        
        Args:
            time_series_type: The selected time series type
            nested_table: The properties table for this time series
            
        Returns:
            dict of parameters
        """
        params = {}
        
        # Handle different time series types by extracting their specific parameters
        if time_series_type == 'Constant' or time_series_type == 'Linear':
            # Both have factor parameter
            factor_value = nested_table.get_cell_value(0, 1) 
            if factor_value is not None:
                params['factor'] = factor_value
                
        elif time_series_type == 'Path':
            # Extract all Path parameters from the properties table
            try:
                # dt (row 0)
                dt_value = nested_table.get_cell_value(0, 1)
                if dt_value is not None:
                    params['dt'] = dt_value
                    
                # values (row 1) - this might be a list
                values_value = nested_table.get_cell_value(1, 1)
                if values_value is not None:
                    params['values'] = values_value
                    
                # time (row 2) - this might be a list  
                time_value = nested_table.get_cell_value(2, 1)
                if time_value is not None:
                    params['time'] = time_value
                    
                # file_path (row 3)
                file_path_value = nested_table.get_cell_value(3, 1)
                if file_path_value is not None:
                    params['file_path'] = file_path_value
                    
                # file_time (row 4)
                file_time_value = nested_table.get_cell_value(4, 1)
                if file_time_value is not None:
                    params['file_time'] = file_time_value
                    
                # factor (row 5) 
                factor_value = nested_table.get_cell_value(5, 1)
                if factor_value is not None:
                    params['factor'] = factor_value
                    
                # start_time (row 6)
                start_time_value = nested_table.get_cell_value(6, 1)
                if start_time_value is not None:
                    params['start_time'] = start_time_value
                    
                # use_last (row 7)
                use_last_value = nested_table.get_cell_value(7, 1)
                if use_last_value is not None:
                    params['use_last'] = use_last_value
                    
                # prepend_zero (row 8)
                prepend_zero_value = nested_table.get_cell_value(8, 1)
                if prepend_zero_value is not None:
                    params['prepend_zero'] = prepend_zero_value
                    
            except Exception as e:
                print(f"Error extracting Path parameters: {e}")
                
        return params