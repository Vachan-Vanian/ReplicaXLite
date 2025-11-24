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


class ReplicaXFemBeamElementManager:
    """
    Manager for the Beam Elements table in ReplicaXLite.
    
    Creates and manages a ReplicaXTable with columns:
    - Tag (int)
    - Start Node (int) 
    - End Node (int)
    - Element Type (str)
    - Section Name (str)
    - Element Class (str)
    - Integration Tag (int)
    - Comment (str)
    """
    
    def __init__(self, beam_elements_tab_widget, settings, nodes_table, 
                 elastic_sections_table, fiber_sections_table, beam_integrations_table):
        """
        Initialize the element manager.
        
        Args:
            elements_tab_widget: The QWidget container for the elements tab
            nodes_table: Reference to the node table for dropdown linking
        """
        self.beam_elements_tab_widget = beam_elements_tab_widget
        self.settings = settings
        self.nodes_table = nodes_table
        self.elastic_sections_table = elastic_sections_table
        self.fiber_sections_table = fiber_sections_table
        self.beam_integrations_table = beam_integrations_table

        layout = QVBoxLayout(self.beam_elements_tab_widget)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)
        
        # Create an update section tags button
        self.btn_update_section_tags = QPushButton("Update Section Tags")
        self.btn_update_section_tags.clicked.connect(lambda: self.update_update_section_tags())
        
        # Create the elements table with initial rows
        self.table = self.beam_elements_table = ReplicaXTable(rows=0, columns=8, settings=self.settings)
        
        # Set headers and data types
        self.beam_elements_table.set_column_types(['int', 'int', 'int', 'str',
                                              'str', 'str', 'int', 'str'])
        self.beam_elements_table.set_headers(['Tag', 'Start\nNode', 'End\nNode', 'Element\nType', 
                                        'Section\nName', 'Element\nClass', 'Integration\nTag', 'Comment'])

        # Configure dropdowns for element type and class
        # self.beam_elements_table.set_dropdown(3, [])
        self.beam_elements_table.set_dropdown(1, [])
        self.beam_elements_table.set_dropdown(2, [])
        self.beam_elements_table.set_dropdown(4, [])
        self.beam_elements_table.set_dropdown(5, ['elasticBeamColumn', 'forceBeamColumn', 'dispBeamColumn'])
        self.beam_elements_table.set_dropdown(6, [])

        # Link node tag dropdowns to available nodes
        self.beam_elements_table.link_dropdown_to_column(
            dropdown_col=1,  # Start Node column
            source_table=self.nodes_table,
            source_col=0,   # Node Tag column
            include_empty=True
        )
        
        self.beam_elements_table.link_dropdown_to_column(
            dropdown_col=2,  # End Node column
            source_table=self.nodes_table,
            source_col=0,   # Node Tag column
            include_empty=True
        )

        self.beam_elements_table.link_dropdown_to_column(
            dropdown_col=6,
            source_table=self.beam_integrations_table,
            source_col=0,
            include_empty=True
        )

        # Initialize table cells (this will sync dropdowns)
        self.beam_elements_table.init_table_cells()
        
        layout.addWidget(self.btn_update_section_tags)
        layout.addWidget(self.beam_elements_table)

    def update_update_section_tags(self):
        # Extract values from TableA column 0
        values_a = []
        for row in range(self.elastic_sections_table.rowCount()):
            value = self.elastic_sections_table.get_cell_value(row, 1)
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
            value = self.fiber_sections_table.get_cell_value(row, 1)
            if value is not None:
                try:
                    str_val = self.fiber_sections_table.data_manager.save_data_type_as_string(value, 'str')
                    if str_val.strip():
                        values_b.append(str_val)
                except:
                    values_b.append(str(value))
        
        # Combine and deduplicate
        combined_values = sorted(list(set([''] + values_a + values_b)))
        self.beam_elements_table.set_dropdown(4, combined_values, update_existing=True, multi=False)





    def create_fem_table_code(self, model):
        """
        Create all beam elements from the GUI table.
        
        Args:
            model: StructuralModel instance
        Returns:
            None
        """
        rows = self.beam_elements_table.rowCount()
        
        for i in range(rows):
            try:
                self.create_fem_table_row_code(model, i)
            except Exception as e:
                print(f"Beam Elements FEM Table: Error processing row {i}: {e}")
                continue

    def create_fem_table_row_code(self, model, row_index):
        """
        Build a single beam element from GUI data at specified row index.
        
        Args:
            model: StructuralModel instance
            row_index: Index of the row to process
        Returns:
            True else False
        """
        # Get basic info
        tag = self.beam_elements_table.get_cell_value(row_index, 0)   # Tag column
        start_node = self.beam_elements_table.get_cell_value(row_index, 1)  # Start Node column
        end_node = self.beam_elements_table.get_cell_value(row_index, 2)  # End Node column
        element_type = self.beam_elements_table.get_cell_value(row_index, 3)  # Element Type column
        section_name = self.beam_elements_table.get_cell_value(row_index, 4)  # Section Name column
        element_class = self.beam_elements_table.get_cell_value(row_index, 5)  # Element Class column
        integration_tag = self.beam_elements_table.get_cell_value(row_index, 6)  # Integration Tag column

        if not tag:
            return False
            
        if not start_node:
            return False
            
        if not end_node:
            return False
            
        if not section_name:
            return False

        # Handle case where integration_tag might be None or empty
        integration_tag = integration_tag if integration_tag is not None else 0  # Default to 0

        try:
            # Create the actual beam element object in model
            model.geometry.create_element(
                tag=tag,
                start_node=start_node,
                end_node=end_node,
                element_type=element_type,
                section_name=section_name,
                element_class=element_class,
                integration_tag=integration_tag
            )
            return True
            
        except Exception as e:
            print(f"Error building beam element from row {row_index}: {e}")
            return False

