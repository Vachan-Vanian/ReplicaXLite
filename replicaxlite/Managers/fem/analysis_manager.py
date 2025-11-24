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

from PySide6.QtWidgets import QVBoxLayout, QPushButton, QHBoxLayout
from ...UtilityCode.TableGUI import ReplicaXTable


class ReplicaXFemAnalysisManager:
    """
    Manager for the Analysis table in ReplicaXLite.
    
    Creates and manages a ReplicaXTable with columns:
    - Tag (int)
    - Analysis Type (str)
    - Parameters (nested table)
    - Comment (str)
    """
    
    def __init__(self, analysis_tab_widget, settings, load_patterns_table, nodes_table):
        """
        Initialize the analysis manager.
        
        Args:
            analysis_tab_widget: The QWidget container for the analysis tab
        """
        self.analysis_tab_widget = analysis_tab_widget
        self.settings = settings
        self.load_patterns_table = load_patterns_table
        self.nodes_table = nodes_table
        self.store_modal_results = []  # SPECIAL CASE FOR RESET TABLE

        layout = QVBoxLayout(self.analysis_tab_widget)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)
        # Create an update section tags button

                # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(5)
        self.btn_build_model = QPushButton("Build Model")
        self.btn_build_and_run_model = QPushButton("Build and Run Model")
        for btn in [self.btn_build_model, self.btn_build_and_run_model]:
            btn_layout.addWidget(btn)
        
        # Create the analysis table with initial rows
        self.table = self.analysis_table = ReplicaXTable(rows=0, columns=4, settings=self.settings)
        
        # Set headers and data types
        self.analysis_table.set_column_types(['int', 'str', 'table', 'str'])
        self.analysis_table.set_headers(['ID', 'Analysis Type', 'Parameters', 'Comment'])

        # Configure dropdown for Analysis Type column with valid analysis types
        analysis_types = ['', 'Modal', 'Gravity', 'Static', 'Pushover', 'TimeHistory']
        self.analysis_table.set_dropdown(1, analysis_types)
        
        # Setup nested tables for different analysis parameters
        self._setup_nested_tables()
        
        # Initialize table cells (this will sync dropdowns)
        self.analysis_table.init_table_cells()
        
        layout.addLayout(btn_layout)
        layout.addWidget(self.analysis_table)
    
    def _setup_nested_tables(self):
        """Create and setup nested tables for different analysis parameter configurations."""
        # Create empty table placeholder (for when no type is selected)
        empty_table = ReplicaXTable(rows=0, columns=0)
        
        #----------------------------------------------------------------------------------------------------
        # Modal Analysis Parameters Table
        modal_params = ReplicaXTable(rows=3, columns=5, settings=self.settings)
        modal_params.set_column_types(['str', 'str', 'str', 'str', 'str'])
        modal_params.set_headers(['Property', 'Value', 'Optional', 'Group', 'Comment'])
        
        modal_params.set_cell_dropdown(1,1, ['-genBandArpack', '-fullGenLapack'])

        modal_params.set_row_types(0, ['str', 'int', 'str', 'str', 'str'])

        # Set default values for modal analysis parameters
        modal_params.set_cell_value(0, 0, 'Num Modes')
        modal_params.set_cell_value(0, 1, 3)
        modal_params.set_cell_value(0, 2, 'No')
        modal_params.set_cell_value(1, 0, 'Solver')
        # modal_params.set_cell_value(1, 1, '-genBandArpack')
        modal_params.set_cell_value(1, 2, 'Yes')
        modal_params.set_cell_value(2, 0, 'Output Tag') 
        modal_params.set_cell_value(2, 1, 'modal') 
        modal_params.set_cell_value(2, 2, 'No') 
        # Initialize table cells
        modal_params.init_table_cells()
        
        #----------------------------------------------------------------------------------------------------
        # Gravity Analysis Parameters Table
        gravity_params = ReplicaXTable(rows=7, columns=5, settings=self.settings)
        gravity_params.set_column_types(['str', 'int', 'str', 'str', 'str'])
        gravity_params.set_headers(['Property', 'Value', 'Optional', 'Group', 'Comment'])
        
        gravity_params.set_row_types(2, ['str', 'float', 'str', 'str', 'str'])
        gravity_params.set_row_types(4, ['str', 'str', 'str', 'str', 'str'])
        gravity_params.set_row_types(5, ['str', 'bool', 'str', 'str', 'str'])
        gravity_params.set_row_types(6, ['str', 'dict', 'str', 'str', 'str'])

        gravity_params.set_cell_dropdown(0,1, [])
        gravity_params.set_cell_dropdown(5,1, [True, False])

        # Set default values for gravity analysis parameters
        gravity_params.set_cell_value(0, 0, 'Load Pattern Tag')
        # gravity_params.set_cell_value(0, 1, 1)
        gravity_params.set_cell_value(0, 2, 'No')
        gravity_params.set_cell_value(1, 0, 'Steps')  
        gravity_params.set_cell_value(1, 1, 10)
        gravity_params.set_cell_value(1, 2, 'Yes')
        gravity_params.set_cell_value(2, 0, 'Tolerance')  
        gravity_params.set_cell_value(2, 1, 1e-5)
        gravity_params.set_cell_value(2, 2, 'Yes')
        gravity_params.set_cell_value(3, 0, 'Max Iterations')  
        gravity_params.set_cell_value(3, 1, 25)
        gravity_params.set_cell_value(3, 2, 'Yes')
        gravity_params.set_cell_value(4, 0, 'Output Tag')  
        gravity_params.set_cell_value(4, 1, 'gravity')
        gravity_params.set_cell_value(4, 2, 'No')
        gravity_params.set_cell_value(5, 0, 'Show Progress')  
        # gravity_params.set_cell_value(5, 1, 'True')
        gravity_params.set_cell_value(5, 2, 'Yes')
        gravity_params.set_cell_value(6, 0, 'Analysis Params')
        gravity_params.set_cell_value(6, 2, 'Yes')

        gravity_params.link_dropdown_to_cell(
            row=0,
            col=1,
            source_table=self.load_patterns_table,
            source_col=0,
            include_empty=True
        )
        
        # Initialize table cells
        gravity_params.init_table_cells()
        
        #----------------------------------------------------------------------------------------------------
        # Static Analysis Parameters Table
        static_params = ReplicaXTable(rows=5, columns=5, settings=self.settings)
        static_params.set_column_types(['str', 'int', 'str', 'str', 'str'])
        static_params.set_headers(['Property', 'Value', 'Optional', 'Group', 'Comment'])
        
        static_params.set_row_types(2, ['str', 'str', 'str', 'str', 'str'])
        static_params.set_row_types(3, ['str', 'bool', 'str', 'str', 'str'])
        static_params.set_row_types(4, ['str', 'dict', 'str', 'str', 'str'])

        static_params.set_cell_dropdown(0,1, [])
        static_params.set_cell_dropdown(3,1, [True, False])

        # Set default values for static analysis parameters
        static_params.set_cell_value(0, 0, 'Load Pattern Tag')
        # static_params.set_cell_value(0, 1, 2)
        static_params.set_cell_value(0, 2, 'No')
        static_params.set_cell_value(1, 0, 'Steps')  
        static_params.set_cell_value(1, 1, 10)
        static_params.set_cell_value(1, 2, 'Yes')
        static_params.set_cell_value(2, 0, 'Output Tag')  
        static_params.set_cell_value(2, 1, 'static')
        static_params.set_cell_value(2, 2, 'No')
        static_params.set_cell_value(3, 0, 'Show Progress')  
        # static_params.set_cell_value(3, 1, 'True')
        static_params.set_cell_value(3, 2, 'Yes')
        static_params.set_cell_value(4, 0, 'Analysis Params')
        static_params.set_cell_value(4, 2, 'Yes')
        
        static_params.link_dropdown_to_cell(
            row=0,
            col=1,
            source_table=self.load_patterns_table,
            source_col=0,
            include_empty=True
        )

        # Initialize table cells
        static_params.init_table_cells()
        
        #----------------------------------------------------------------------------------------------------
        # Pushover Analysis Parameters Table
        pushover_params = ReplicaXTable(rows=8, columns=5, settings=self.settings)
        pushover_params.set_column_types(['str', 'int', 'str', 'str', 'str'])
        pushover_params.set_headers(['Property', 'Value', 'Optional', 'Group', 'Comment'])
        
        pushover_params.set_row_types(3, ['str', 'list(float)', 'str', 'str', 'str'])
        pushover_params.set_row_types(4, ['str', 'float', 'str', 'str', 'str'])
        pushover_params.set_row_types(5, ['str', 'str', 'str', 'str', 'str'])
        pushover_params.set_row_types(6, ['str', 'dict', 'str', 'str', 'str'])
        pushover_params.set_row_types(7, ['str', 'dict', 'str', 'str', 'str'])

        pushover_params.set_cell_dropdown(0,1, [])
        pushover_params.set_cell_dropdown(1,1, [])
        pushover_params.set_cell_dropdown(2,1, [1,2,3])

        # Set default values for pushover analysis parameters
        pushover_params.set_cell_value(0, 0, 'Load Pattern Tag')
        # pushover_params.set_cell_value(0, 1, 3)
        pushover_params.set_cell_value(0, 2, 'No')
        pushover_params.set_cell_value(1, 0, 'Control Node')  
        # pushover_params.set_cell_value(1, 1, 1)
        pushover_params.set_cell_value(1, 2, 'No')
        pushover_params.set_cell_value(2, 0, 'Control DOF')  
        # pushover_params.set_cell_value(2, 1, 1)
        pushover_params.set_cell_value(2, 2, 'No')
        pushover_params.set_cell_value(3, 0, 'Target Protocol')  
        # pushover_params.set_cell_value(3, 1, [0.0, 0.5, 1.0])
        pushover_params.set_cell_value(3, 2, 'No')
        pushover_params.set_cell_value(4, 0, 'Max Step Size')  
        # pushover_params.set_cell_value(4, 1, 0.1)
        pushover_params.set_cell_value(4, 2, 'No')
        pushover_params.set_cell_value(5, 0, 'Output Tag')  
        pushover_params.set_cell_value(5, 1, 'pushover')
        pushover_params.set_cell_value(5, 2, 'No')
        pushover_params.set_cell_value(6, 0, 'Analysis Params')  
        pushover_params.set_cell_value(6, 2, 'Yes')
        pushover_params.set_cell_value(7, 0, 'Smart Analysis Params')  
        pushover_params.set_cell_value(7, 2, 'Yes')
        
        pushover_params.link_dropdown_to_cell(
            row=0,
            col=1,
            source_table=self.load_patterns_table,
            source_col=0,
            include_empty=True
        )

        pushover_params.link_dropdown_to_cell(
            row=1,
            col=1,
            source_table=self.nodes_table,
            source_col=0,
            include_empty=True
        )

        # Initialize table cells
        pushover_params.init_table_cells()
        
        #----------------------------------------------------------------------------------------------------
        # Time History Analysis Parameters Table
        timehistory_params = ReplicaXTable(rows=11, columns=5, settings=self.settings)
        timehistory_params.set_column_types(['str', 'int', 'str', 'str', 'str'])
        timehistory_params.set_headers(['Property', 'Value', 'Optional', 'Group', 'Comment'])

        timehistory_params.set_row_types(0, ['str', 'dict', 'str', 'str', 'str'])
        timehistory_params.set_row_types(1, ['str', 'float', 'str', 'str', 'str'])
        timehistory_params.set_row_types(2, ['str', 'int', 'str', 'str', 'str'])
        timehistory_params.set_row_types(3, ['str', 'list(float)', 'str', 'str', 'str'])
        timehistory_params.set_row_types(4, ['str', 'float', 'str', 'str', 'str'])
        timehistory_params.set_row_types(5, ['str', 'str', 'str', 'str', 'str'])
        timehistory_params.set_row_types(6, ['str', 'int', 'str', 'str', 'str'])
        timehistory_params.set_row_types(7, ['str', 'float', 'str', 'str', 'str'])
        timehistory_params.set_row_types(8, ['str', 'dict', 'str', 'str', 'str'])
        timehistory_params.set_row_types(9, ['str', 'str', 'str', 'str', 'str'])
        timehistory_params.set_row_types(10, ['str', 'dict', 'str', 'str', 'str'])
        # timehistory_params.set_row_types(11, ['str', 'list(int)', 'str', 'str', 'str'])

        timehistory_params.set_cell_dropdown(6,1, [1,2,3])

        # Set default values for time history analysis parameters
        timehistory_params.set_cell_value(0, 0, 'time_history')
        # timehistory_params.set_cell_value(0, 1, 'accel')  # Default to acceleration input
        timehistory_params.set_cell_value(0, 2, 'No')
        timehistory_params.set_cell_value(1, 0, 'dt')  
        # timehistory_params.set_cell_value(1, 1, 0.02)
        timehistory_params.set_cell_value(1, 2, 'No')
        timehistory_params.set_cell_value(2, 0, 'n_steps')  
        # timehistory_params.set_cell_value(2, 1, 100)
        timehistory_params.set_cell_value(2, 2, 'No')
        timehistory_params.set_cell_value(3, 0, 'eigenvalues')  
        # timehistory_params.set_cell_value(3, 1, [])
        timehistory_params.set_cell_value(3, 2, 'No')
        timehistory_params.set_cell_value(4, 0, 'damping_ratio')  
        timehistory_params.set_cell_value(4, 1, 0.05)
        timehistory_params.set_cell_value(4, 2, 'Yes')
        timehistory_params.set_cell_value(5, 0, 'odb_tag')  
        timehistory_params.set_cell_value(5, 1, 'timehistory')
        timehistory_params.set_cell_value(5, 2, 'No')
        timehistory_params.set_cell_value(6, 0, 'direction')  
        # timehistory_params.set_cell_value(6, 1, 1)
        timehistory_params.set_cell_value(6, 2, 'Yes')
        timehistory_params.set_cell_value(7, 0, 'scale_factor')  
        timehistory_params.set_cell_value(7, 1, '1.0')
        timehistory_params.set_cell_value(7, 2, 'Yes')
        timehistory_params.set_cell_value(8, 0, 'analysis_params')  
        # timehistory_params.set_cell_value(8, 1, '')
        timehistory_params.set_cell_value(8, 2, 'Yes')
        timehistory_params.set_cell_value(9, 0, 'pattern_type')  
        timehistory_params.set_cell_value(9, 1, 'UniformExcitation')
        timehistory_params.set_cell_value(9, 2, 'Yes')
        timehistory_params.set_cell_value(10, 0, 'smart_analyze_params')  
        # timehistory_params.set_cell_value(10, 1, '')
        timehistory_params.set_cell_value(10, 2, 'Yes')
        # timehistory_params.set_cell_value(11, 0, 'support_nodes')  
        # timehistory_params.set_cell_value(11, 1, '')
        # timehistory_params.set_cell_value(11, 2, 'Yes')

        # timehistory_dict = ReplicaXTable(rows=0, columns=4, settings=self.settings)
        # timehistory_dict.set_column_types(['float', 'float', 'float', 'float'])
        # timehistory_dict.set_headers(['time', 'accel', 'vel', 'disp'])

        # timehistory_dict.set_column_unit(0,'Time')
        # timehistory_dict.set_column_unit(0,'Acceleration')
        # timehistory_dict.set_column_unit(0,'Velocity')
        # timehistory_dict.set_column_unit(0,'Displacement')

        # Initialize table cells
        timehistory_params.init_table_cells()
        
        #----------------------------------------------------------------------------------------------------
        # Link dropdown to nested tables - this connects the type selection to parameter tables
        self.analysis_table.link_dropdown_to_table(
            dropdown_col=1,     
            table_col=2,        
            templates={
                '': empty_table,
                'Modal': modal_params,
                'Gravity': gravity_params,
                'Static': static_params,
                'Pushover': pushover_params,
                'TimeHistory': timehistory_params
            }
        )

    def refresh_dropdown_nested_table_links_after_load(self):
        """Re-establish dropdown links after table load."""
        # Iterate through all rows in analysis table to re-link dropdowns 
        for row in range(self.analysis_table.rowCount()):
            # Get the analysis type from column 1 (Analysis Type column)
            analysis_type = self.analysis_table.get_cell_value(row, 1)

            # Get nested table reference
            nested_table = self.analysis_table.get_cell_value(row, 2)  # Parameters column

            if not isinstance(nested_table, ReplicaXTable):
                continue

            # Re-establish dropdown links based on analysis type
            if analysis_type == 'Gravity':
                # Gravity analysis - link Load Pattern Tag dropdown to load patterns table
                nested_table.link_dropdown_to_cell(
                    row=0,
                    col=1,
                    source_table=self.load_patterns_table,
                    source_col=0,
                    include_empty=True
                )
                
            elif analysis_type == 'Static':
                # Static analysis - link Load Pattern Tag dropdown to load patterns table  
                nested_table.link_dropdown_to_cell(
                    row=0,
                    col=1,
                    source_table=self.load_patterns_table,
                    source_col=0,
                    include_empty=True
                )
                
            elif analysis_type == 'Pushover':
                # Pushover analysis - link Load Pattern Tag dropdown to load patterns table
                nested_table.link_dropdown_to_cell(
                    row=0,
                    col=1,
                    source_table=self.load_patterns_table,
                    source_col=0,
                    include_empty=True
                )
                
                # Pushover analysis - link Control Node dropdown to nodes table
                nested_table.link_dropdown_to_cell(
                    row=1,
                    col=1,
                    source_table=self.nodes_table,
                    source_col=0,
                    include_empty=True
                )




    def create_fem_table_code(self, model):
        """
        Create all analyses from the GUI table.
        
        Args:
            model: StructuralModel instance
        Returns:
            None
        """
        rows = self.analysis_table.rowCount()
        
        for i in range(rows):
            try:
                if self.create_fem_table_row_code(model, i):
                    pass  # Success case
            except Exception as e:
                print(f"Analysis FEM Table: Error processing row {i}: {e}")
                continue

    def create_fem_table_row_code(self, model, row_index):
        """
        Build a single analysis from GUI data at specified row index.
        
        Args:
            model: StructuralModel instance
            row_index: Index of the row to process
        Returns:
            True if successful else False
        """
        # Get basic info
        tag = self.analysis_table.get_cell_value(row_index, 0)   # ID column
        analysis_type = self.analysis_table.get_cell_value(row_index, 1)  # Analysis Type column
        
        if not tag or not str(tag).strip():
            return False
            
        if not analysis_type:
            return False

        # Get the nested parameters table for this row
        nested_table = self.analysis_table.get_cell_value(row_index, 2)  # Parameters column

        try:
            # Extract parameters based on analysis type
            params = self._extract_parameters_from_nested_table(analysis_type, nested_table)
            
            if not params:  # No valid parameters extracted
                return False
                
            # Run the actual analysis method in model.analysis
            if analysis_type == 'Modal':
                result = model.analysis.run_modal_analysis(
                    num_modes=params.get('num_modes', 3),
                    odb_tag=params.get('output_tag', 'modal'),
                    solver=params.get('solver', '-genBandArpack')
                )
                self.store_modal_results.append(result)
                
            elif analysis_type == 'Gravity':
                result = model.analysis.run_gravity_analysis(
                    load_pattern_tag=params['load_pattern_tag'],
                    n_steps=params.get('steps', 10),
                    tol=params.get('tolerance', 1e-5),
                    max_iter=params.get('max_iterations', 25),
                    output_odb_tag=params.get('output_tag', 'gravity'),
                    show_progress=params.get('show_progress', True)
                )
                
            elif analysis_type == 'Static':
                result = model.analysis.run_static_analysis(
                    load_pattern_tag=params['load_pattern_tag'],
                    n_steps=params.get('steps', 10),
                    output_odb_tag=params.get('output_tag', 'static'),
                    show_progress=params.get('show_progress', True)
                )
                
            elif analysis_type == 'Pushover':
                result = model.analysis.run_pushover_analysis(
                    load_pattern_tag=params['load_pattern_tag'],
                    control_node=params['control_node'],
                    control_dof=params['control_dof'],
                    target_protocol=params['target_protocol'],
                    max_step=params['max_step_size'],
                    output_odb_tag=params.get('output_tag', 'pushover')
                )
                
            elif analysis_type == 'TimeHistory':
                result = model.analysis.run_time_history_analysis(
                    time_history=params['time_history'],
                    dt=params['dt'],
                    n_steps=params['n_steps'],
                    eigenvalues=params.get('eigenvalues'),
                    damping_ratio=params.get('damping_ratio', 0.05),
                    odb_tag=params.get('odb_tag', 'timehistory'),
                    direction=params.get('direction', 1),
                    scale_factor=params.get('scale_factor', 1.0)
                )
            else:
                print(f"Warning: Unknown analysis type '{analysis_type}' for row {row_index}")
                return False
                
            return True
            
        except Exception as e:
            print(f"Error running analysis from row {row_index}: {e}")
            return False

    def _extract_parameters_from_nested_table(self, analysis_type, nested_table):
        """
        Extract parameters from nested table based on analysis type.
        
        Args:
            analysis_type: The selected analysis type
            nested_table: The parameters table for this analysis
            
        Returns:
            dict of parameters
        """
        params = {}
        
        # Handle different analysis types by extracting their specific parameters
        
        if not isinstance(nested_table, ReplicaXTable):
            return params

        try:
            if analysis_type == 'Modal':
                # Extract Modal Analysis Parameters
                num_modes = nested_table.get_cell_value(0, 1)
                if num_modes is not None and str(num_modes).strip():
                    params['num_modes'] = int(float(str(num_modes).strip()))
                    
                solver = nested_table.get_cell_value(1, 1)
                if solver is not None and str(solver).strip():
                    params['solver'] = str(solver).strip()
                    
                output_tag = nested_table.get_cell_value(2, 1)
                if output_tag is not None and str(output_tag).strip():
                    params['output_tag'] = str(output_tag).strip()

            elif analysis_type == 'Gravity':
                # Extract Gravity Analysis Parameters
                load_pattern_tag = nested_table.get_cell_value(0, 1)
                if load_pattern_tag is not None and str(load_pattern_tag).strip():
                    params['load_pattern_tag'] = int(float(str(load_pattern_tag).strip()))
                    
                steps = nested_table.get_cell_value(1, 1)
                if steps is not None and str(steps).strip():
                    params['steps'] = int(float(str(steps).strip()))
                    
                tolerance = nested_table.get_cell_value(2, 1)
                if tolerance is not None and str(tolerance).strip():
                    params['tolerance'] = float(str(tolerance).strip())
                    
                max_iterations = nested_table.get_cell_value(3, 1)
                if max_iterations is not None and str(max_iterations).strip():
                    params['max_iterations'] = int(float(str(max_iterations).strip()))
                    
                output_tag = nested_table.get_cell_value(4, 1)
                if output_tag is not None and str(output_tag).strip():
                    params['output_tag'] = str(output_tag).strip()
                    
                show_progress = nested_table.get_cell_value(5, 1)
                if show_progress is not None:
                    # Handle boolean conversion properly
                    if isinstance(show_progress, bool):
                        params['show_progress'] = show_progress
                    elif isinstance(show_progress, str):
                        params['show_progress'] = show_progress.lower() in ('true', '1', 'yes')
                    else:
                        params['show_progress'] = bool(show_progress)

            elif analysis_type == 'Static':
                # Extract Static Analysis Parameters
                load_pattern_tag = nested_table.get_cell_value(0, 1)
                if load_pattern_tag is not None and str(load_pattern_tag).strip():
                    params['load_pattern_tag'] = int(float(str(load_pattern_tag).strip()))
                    
                steps = nested_table.get_cell_value(1, 1)
                if steps is not None and str(steps).strip():
                    params['steps'] = int(float(str(steps).strip()))
                    
                output_tag = nested_table.get_cell_value(2, 1)
                if output_tag is not None and str(output_tag).strip():
                    params['output_tag'] = str(output_tag).strip()
                    
                show_progress = nested_table.get_cell_value(3, 1)
                if show_progress is not None:
                    # Handle boolean conversion properly
                    if isinstance(show_progress, bool):
                        params['show_progress'] = show_progress
                    elif isinstance(show_progress, str):
                        params['show_progress'] = show_progress.lower() in ('true', '1', 'yes')
                    else:
                        params['show_progress'] = bool(show_progress)

            elif analysis_type == 'Pushover':
                # Extract Pushover Analysis Parameters
                load_pattern_tag = nested_table.get_cell_value(0, 1)
                if load_pattern_tag is not None and str(load_pattern_tag).strip():
                    params['load_pattern_tag'] = int(float(str(load_pattern_tag).strip()))
                    
                control_node = nested_table.get_cell_value(1, 1)
                if control_node is not None and str(control_node).strip():
                    params['control_node'] = int(float(str(control_node).strip()))
                    
                control_dof = nested_table.get_cell_value(2, 1)
                if control_dof is not None and str(control_dof).strip():
                    params['control_dof'] = int(float(str(control_dof).strip()))
                    
                target_protocol = nested_table.get_cell_value(3, 1)
                if target_protocol is not None:
                    # Handle list conversion properly
                    try:
                        import ast
                        parsed_target = ast.literal_eval(str(target_protocol).strip())
                        params['target_protocol'] = parsed_target if isinstance(parsed_target, (list, tuple)) else [parsed_target]
                    except:
                        if isinstance(target_protocol, str) and len(str(target_protocol).strip()) > 0:
                            # Try splitting by comma
                            try:
                                params['target_protocol'] = [float(x.strip()) for x in str(target_protocol).split(',')]
                            except:
                                pass  # Keep original or handle appropriately
                        
                max_step_size = nested_table.get_cell_value(4, 1)
                if max_step_size is not None and str(max_step_size).strip():
                    params['max_step_size'] = float(str(max_step_size).strip())
                    
                output_tag = nested_table.get_cell_value(5, 1)
                if output_tag is not None and str(output_tag).strip():
                    params['output_tag'] = str(output_tag).strip()

            elif analysis_type == 'TimeHistory':
                # Extract Time History Analysis Parameters
                time_history_data = nested_table.get_cell_value(0, 1)
                if time_history_data is not None:
                    params['time_history'] = time_history_data
                    
                dt = nested_table.get_cell_value(1, 1)
                if dt is not None and str(dt).strip():
                    params['dt'] = float(str(dt).strip())
                    
                n_steps = nested_table.get_cell_value(2, 1)
                if n_steps is not None and str(n_steps).strip():
                    params['n_steps'] = int(float(str(n_steps).strip()))
                    
                eigenvalues = nested_table.get_cell_value(3, 1)
                if eigenvalues is not None:
                    # Handle list conversion for eigenvalues
                    try:
                        import ast
                        parsed_eigenvals = ast.literal_eval(str(eigenvalues).strip())
                        params['eigenvalues'] = list(parsed_eigenvals) if isinstance(parsed_eigenvals, (list, tuple)) else [parsed_eigenvals]
                    except:
                        # If that fails, keep as original or handle appropriately
                        pass
                else:# SPECIAL CASE FOR SEQUENTIAL ANALYSIS
                    if self.store_modal_results:
                        params['eigenvalues'] = self.store_modal_results[-1]['eigen_values']
                    else:
                        raise ValueError("Run Model analysis first OR provide eigan values manually!")
                        
                damping_ratio = nested_table.get_cell_value(4, 1)
                if damping_ratio is not None and str(damping_ratio).strip():
                    params['damping_ratio'] = float(str(damping_ratio).strip())
                    
                odb_tag = nested_table.get_cell_value(5, 1)
                if odb_tag is not None and str(odb_tag).strip():
                    params['odb_tag'] = str(odb_tag).strip()
                    
                direction = nested_table.get_cell_value(6, 1)
                if direction is not None and str(direction).strip():
                    params['direction'] = int(float(str(direction).strip()))
                    
                scale_factor = nested_table.get_cell_value(7, 1)
                if scale_factor is not None and str(scale_factor).strip():
                    # Handle float conversion for string representations
                    try:
                        params['scale_factor'] = float(str(scale_factor).strip())
                    except ValueError:
                        params['scale_factor'] = 1.0
                        
            return params
            
        except Exception as e:
            print(f"Error extracting parameters for {analysis_type}: {e}")
            return {}
