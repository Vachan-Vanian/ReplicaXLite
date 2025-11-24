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


class ReplicaXFemNodeManager:
    """
    Manager for the Nodes table in ReplicaXLite.
    
    Creates and manages a ReplicaXTable with columns:
    - Tag (int)
    - X (float)
    - Y (float)
    - Z (float)
    - Comment (str)
    """
    
    def __init__(self, nodes_tab_widget, settings):
        """
        Initialize the node manager.
        
        Args:
            nodes_tab_widget: The QWidget container for the nodes tab
        """
        self.nodes_tab_widget = nodes_tab_widget
        self.settings = settings

        layout = QVBoxLayout(self.nodes_tab_widget)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)
        
        # Create the nodes table with initial rows
        self.table = self.nodes_table = ReplicaXTable(rows=0, columns=5, settings=self.settings)
        
        # Set headers
        self.nodes_table.set_column_types(['int', 'float', 'float', 'float', 'str'])
        self.nodes_table.set_column_unit(1, 'Length')  # X column
        self.nodes_table.set_column_unit(2, 'Length')  # Y column  
        self.nodes_table.set_column_unit(3, 'Length')  # Z column
        self.nodes_table.set_headers(['Tag', 'X', 'Y', 'Z', 'Comment'])

        # Initialize table cells (this will sync dropdowns)
        self.nodes_table.init_table_cells()

        layout.addWidget(self.nodes_table)




    def create_fem_table_code(self, model):
        """
        Create all nodes from the GUI table.
        
        Args:
            model: StructuralModel instance
        Returns:
            None
        """
        rows = self.nodes_table.rowCount()
        for i in range(rows):
            try:
                self.create_fem_table_row_code(model, i)
            except Exception as e:
                print(f"Nodes FEM Table: Error processing row {i}: {e}")
                continue

    def create_fem_table_row_code(self, model, row_index):
        """
        Build a single node object from GUI data at specified row index.
        
        Args:
            model: StructuralModel instance
            row_index: Index of the row to process
        Returns:
            True else False
        """
        # Get basic info
        tag = self.nodes_table.get_cell_value(row_index, 0)   # Tag column
        x = self.nodes_table.get_cell_value(row_index, 1)     # X column
        y = self.nodes_table.get_cell_value(row_index, 2)     # Y column
        z = self.nodes_table.get_cell_value(row_index, 3)     # Z column

        if not tag:
            return False

        try:
            model.geometry.create_node(tag=tag, x=x, y=y, z=z)
            return True
        except Exception as e:
            print(f"Error building node from row {row_index}: {e}")
            return False

