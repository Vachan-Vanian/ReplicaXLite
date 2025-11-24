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


from PySide6.QtWidgets import QVBoxLayout, QPushButton
from ...UtilityCode.TableGUI import ReplicaXTable


class ReplicaXFemBeamIntegrationManager:
    """
    Manager for the Beam Integrations table in ReplicaXLite.
    
    Creates and manages a ReplicaXTable with columns:
    - Tag (int)
    - Type (dropdown: 'Lobatto', 'Legendre', etc.)
    - Structural Element Use (str)
    - Section Tag (dropdown from available sections)
    - Number of Points (int)
    - Comment (str)
    """
    
    def __init__(self, beam_integrations_tab_widget, settings, elastic_sections_table, fiber_sections_table):
        """
        Initialize the beam integration manager.
        
        Args:
            beam_integrations_tab_widget: The QWidget container for the beam integrations tab
        """
        self.beam_integrations_tab_widget = beam_integrations_tab_widget
        self.settings = settings
        self.elastic_sections_table = elastic_sections_table
        self.fiber_sections_table = fiber_sections_table

        layout = QVBoxLayout(self.beam_integrations_tab_widget)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)

        # Create an update section tags button
        self.btn_update_section_tags = QPushButton("Update Section Tags")
        self.btn_update_section_tags.clicked.connect(lambda: self.update_update_section_tags())
        
        # Create the beam integrations table with initial rows
        self.table = self.beam_integrations_table = ReplicaXTable(rows=0, columns=6, settings=self.settings)
        
        # Set headers
        self.beam_integrations_table.set_column_types(['int', 'str', 'str', 'int', 'int', 'str'])
        self.beam_integrations_table.set_dropdown(1, ['Lobatto', 'Legendre', 'NewtonCotes', 'Radau', 
                                                     'Trapezoidal', 'CompositeSimpson'])  # Integration type options
        self.beam_integrations_table.set_dropdown(3,[])
        self.beam_integrations_table.set_headers(['Tag', 'Type', 'Structural Use', 'Section Tag', 'Num Points', 'Comment'])
        

        # Initialize table cells (this will sync dropdowns)
        self.beam_integrations_table.init_table_cells()
        
        layout.addWidget(self.btn_update_section_tags)
        layout.addWidget(self.beam_integrations_table)

    def update_update_section_tags(self):
        # Extract values from TableA column 0
        values_a = []
        for row in range(self.elastic_sections_table.rowCount()):
            value = self.elastic_sections_table.get_cell_value(row, 0)
            if value is not None:
                try:
                    str_val = self.elastic_sections_table.data_manager.save_data_type_as_string(value, 'str')
                    if str_val.strip():
                        values_a.append(str_val)
                except:
                    values_a.append(str(value))
        
        # Extract values from TableB column 0
        values_b = []
        for row in range(self.fiber_sections_table.rowCount()):
            value = self.fiber_sections_table.get_cell_value(row, 0)
            if value is not None:
                try:
                    str_val = self.fiber_sections_table.data_manager.save_data_type_as_string(value, 'str')
                    if str_val.strip():
                        values_b.append(str_val)
                except:
                    values_b.append(str(value))
        
        # Combine and deduplicate
        combined_values = sorted(list(set([''] + values_a + values_b)))
        self.beam_integrations_table.set_dropdown(3, combined_values, update_existing=True, multi=False)






    def create_fem_table_code(self, model):
        """
        Create all beam integrations from the GUI table.
        
        Args:
            model: StructuralModel instance
        Returns:
            None
        """
        rows = self.beam_integrations_table.rowCount()
        
        for i in range(rows):
            try:
                self.create_fem_table_row_code(model, i)
            except Exception as e:
                print(f"Beam Integration FEM Table: Error processing row {i}: {e}")
                continue

    def create_fem_table_row_code(self, model, row_index):
        """
        Build a single beam integration from GUI data at specified row index.
        
        Args:
            model: StructuralModel instance
            row_index: Index of the row to process
        Returns:
            True else False
        """
        # Get basic info
        tag = self.beam_integrations_table.get_cell_value(row_index, 0)   # Tag column
        integration_type = self.beam_integrations_table.get_cell_value(row_index, 1)  # Type column
        structural_element_use = self.beam_integrations_table.get_cell_value(row_index, 2)  # Structural Use column
        section_tag = self.beam_integrations_table.get_cell_value(row_index, 3)  # Section Tag column
        num_points = self.beam_integrations_table.get_cell_value(row_index, 4)  # Num Points column

        if not tag:
            return False
            
        if not integration_type:
            return False
            
        if not section_tag:
            return False

        # Handle case where number of points might be None or empty
        num_points = num_points if num_points is not None else 5  # Default to 10 points

        try:
            # Create the actual beam integration object in model
            model.properties.create_beam_integration(
                tag=tag,
                integration_type=integration_type,
                structural_element_use=structural_element_use,
                section_tag=section_tag,
                num_points=num_points
            )
            return True
            
        except Exception as e:
            print(f"Error building beam integration from row {row_index}: {e}")
            return False

