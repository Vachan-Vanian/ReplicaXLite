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


from ..UtilityCode.CommandLogger import CommandLogger
from ..StructuralAPI import StructuralModel
from pathlib import Path

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..Managers.manage_fem_table import ReplicaXFemTableManager
    from ..UtilityCode.TableGUI import ReplicaXTable


class ReplicaXFemTableModelBuilder:
    def __init__(self, parent: 'ReplicaXFemTableManager', console):
        self.parent = parent
        self.console = console
  
    def create_model(self, progress="run"):
        logger = CommandLogger(
            log_file=(Path(self.parent.settings['_project']['project_folder'])/"fem_table_model.py").as_posix(),
            prefix_obj = "model",
            commands_to_include=[
                'create_uniaxial_material',
                'create_elastic_section',
                'create_fiber_section',
                'create_node',
                'create_constraint',
                'create_rigid_diaphragm',
                'create_rigid_link',
                'create_equal_dof',
                'create_beam_integration',
                'create_element',
                
                'create_constant_time_series',
                'create_linear_time_series',
                'create_path_time_series',
                'create_load_pattern',
                'create_uniform_excitation_pattern',
                'create_beam_uniform_load',

                'add_mass',
                'add_node_load',

                'run_modal_analysis',
                'run_gravity_analysis',
                'run_static_analysis',
                'run_pushover_analysis',
                'run_time_history_analysis'



                ### add as needed
            ],
            commands_with_return= {
                'run_modal_analysis': 'modal_results'
            },

            header_to_include="""from replicaxlite.StructuralAPI import StructuralModel

# Create the model instance
model = StructuralModel("FEM_TABLE_MODEL")
    
"""
        )
        
        # Create and wrap your model
        model = StructuralModel("FEM_TABLE_MODEL")
        model = logger.wrap(model)

        # Make nodes dictionary auto-wrapping (RECOMMENDED)
        logger.wrap_dict(model.geometry, "nodes", "model.geometry")
        logger.wrap_dict(model.loading, "load_patterns", "model.loading")

        self.parent.materials.create_fem_table_code(model)

        self.parent.elastic_sections.create_fem_table_code(model)

        self.parent.fiber_sections.create_fem_table_code(model)

        self.parent.nodes.create_fem_table_code(model)

        self.parent.constraints.create_fem_table_code(model)

        self.parent.equal_dofs.create_fem_table_code(model)

        self.parent.rigid_links.create_fem_table_code(model)

        self.parent.rigid_diaphragms.create_fem_table_code(model)
         
        self.parent.masses.create_fem_table_code(model)

        self.parent.beam_integrations.create_fem_table_code(model)

        self.parent.beam_elements.create_fem_table_code(model)

        logger.user_line_code_insert("# WARNING: Comment out (app.) code sections when not actively using the module inside ReplicaxLite")
        logger.user_line_code_insert("app.model['0']=model")

        if progress=="run":
            # Now process analyses with proper dependency management TimeSeries → Pattern → NodeLoads/ElementLoads → Analysis
            self._process_analyses_with_dependencies2(model)
        
        return model

    def _process_analyses_with_dependencies2(self, model):
        """
        Process each analysis in dependency order to ensure:
        TimeSeries → Pattern → NodeLoads/ElementLoads → Analysis
        """
        rows = self.parent.analyses.analysis_table.rowCount()
        
        for i in range(rows):               
            try:
                # Get the analysis tag (ID) from the table directly since we're processing it as a row
                analysis_tag = self.parent.analyses.analysis_table.get_cell_value(i, 0)
                analysis_type = self.parent.analyses.analysis_table.get_cell_value(i, 1)
                analysis_param_table = self.parent.analyses.analysis_table.get_cell_value(i, 2)
                
                if not analysis_tag or str(analysis_tag).strip() == '':
                    print(f"WARNING: Skipping invalid/empty analysis ID at row {i}")
                    continue
                    
                print(f"Processing Analysis ID: {analysis_tag}")
                if analysis_type.lower()=='modal':
                    self.parent.analyses.create_fem_table_row_code(model, i)
                else:
                    if analysis_type.lower() in ['gravity', 'static', 'pushover']:
                        pattern_tag = analysis_param_table.get_cell_value(0, 1)
                        prows = self.parent.patterns.patterns_table.rowCount()
                        for pattern_row in range(prows):
                            if pattern_tag == self.parent.patterns.patterns_table.get_cell_value(pattern_row,0):
                                pattern_prop_table = self.parent.patterns.patterns_table.get_cell_value(pattern_row, 2)
                                break
                                
                        timeseries_tag = pattern_prop_table.get_cell_value(0,1)
                        tsrows = self.parent.patterns.patterns_table.rowCount()
                        for timeseries_row in range(tsrows):
                            if timeseries_tag == self.parent.time_series.time_series_table.get_cell_value(timeseries_row,0):
                                timeseries_prop_table = self.parent.time_series.time_series_table.get_cell_value(timeseries_row, 2)
                                break
                        
                        node_rows = []
                        element_rows = []

                        nrows = self.parent.node_loads.loads_table.rowCount()
                        erows = self.parent.beam_elements_uniform_loads.beam_elements_loads_table.rowCount()
                        for j in range(nrows):
                            if pattern_tag == self.parent.node_loads.loads_table.get_cell_value(j, 1):
                                node_rows.append(j)

                        for j in range(erows):
                            if pattern_tag == self.parent.beam_elements_uniform_loads.beam_elements_loads_table.get_cell_value(j, 1):
                                element_rows.append(j)

                        self.parent.time_series.create_fem_table_row_code(model, timeseries_row)
                        self.parent.patterns.create_fem_table_row_code(model, pattern_row)

                        for j in node_rows:
                            self.parent.node_loads.create_fem_table_row_code(model, j)
                        for j in element_rows:
                            self.parent.beam_elements_uniform_loads.create_fem_table_row_code(model, j)
                        
                        self.parent.analyses.create_fem_table_row_code(model, i)

                    else: # time history
                        self.parent.analyses.create_fem_table_row_code(model, i)
                    
            except Exception as e:
                print(f"ERROR: Stopping analysis processing due to exception at row {i}: {e}")
                break








