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


class ReplicaXFemNodeMassManager:
    """
    Manager for the Mass table in ReplicaXLite.
    
    Creates and manages a ReplicaXTable with columns:
    - Node Tag (int)
    - MX (float) 
    - MY (float)
    - MZ (float)
    - RX (float)
    - RY (float)
    - RZ (float)
    - Comment (str)
    """
    
    def __init__(self, masses_tab_widget, settings, nodes_table):
        """
        Initialize the mass manager.
        
        Args:
            masses_tab_widget: The QWidget container for the mass tab
        """
        self.masses_tab_widget = masses_tab_widget
        self.settings = settings
        self.nodes_table = nodes_table

        layout = QVBoxLayout(self.masses_tab_widget)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)
        
        # Create the mass table with initial rows
        self.table = self.masses_table = ReplicaXTable(rows=0, columns=8, settings=self.settings)
        
        # Set headers
        self.masses_table.set_column_types(['int', 'float', 'float', 'float', 'float', 'float', 'float', 'str'])
        self.masses_table.set_column_unit(1, 'Mass')  # MX column
        self.masses_table.set_column_unit(2, 'Mass')  # MY column  
        self.masses_table.set_column_unit(3, 'Mass')  # MZ column
        self.masses_table.set_column_unit(4, 'Mass_Moments_of_Inertia')  # RX column
        self.masses_table.set_column_unit(5, 'Mass_Moments_of_Inertia')  # RY column
        self.masses_table.set_column_unit(6, 'Mass_Moments_of_Inertia')  # RZ column
        self.masses_table.set_dropdown(0, [])  # Node Tag dropdown
        self.masses_table.set_headers(['Node Tag', 'MX', 'MY', 'MZ', 'RX', 'RY', 'RZ', 'Comment'])

        # Link node tag dropdown to available nodes
        self.masses_table.link_dropdown_to_column(
            dropdown_col=0,
            source_table=self.nodes_table,
            source_col=0,
            include_empty=True
        )

        # Initialize table cells (this will sync dropdowns)
        self.masses_table.init_table_cells()

        layout.addWidget(self.masses_table)





    def create_fem_table_code(self, model):
            """
            Create all mass constraints from the GUI table.
            
            Args:
                model: StructuralModel instance
            Returns:
                None
            """
            rows = self.masses_table.rowCount()
            
            for i in range(rows):
                try:
                    self.create_fem_table_row_code(model, i)
                except Exception as e:
                    print(f"Mass FEM Table: Error processing row {i}: {e}")
                    continue

    def create_fem_table_row_code(self, model, row_index):
        """
        Build a single mass constraint from GUI data at specified row index.
        
        Args:
            model: StructuralModel instance
            row_index: Index of the row to process
        Returns:
            True else False
        """
        # Get basic info
        node_tag = self.masses_table.get_cell_value(row_index, 0)   # Node Tag column
        mx = self.masses_table.get_cell_value(row_index, 1)      # MX column
        my = self.masses_table.get_cell_value(row_index, 2)      # MY column
        mz = self.masses_table.get_cell_value(row_index, 3)      # MZ column
        rx = self.masses_table.get_cell_value(row_index, 4)      # RX column
        ry = self.masses_table.get_cell_value(row_index, 5)      # RY column
        rz = self.masses_table.get_cell_value(row_index, 6)      # RZ column

        if not node_tag:
            return False
            
        # Handle case where some mass values might be None or empty
        # Default to 0.0 for missing values (as per typical structural modeling)
        mx = mx if mx is not None else 0.0
        my = my if my is not None else 0.0
        mz = mz if mz is not None else 0.0
        rx = rx if rx is not None else 0.0
        ry = ry if ry is not None else 0.0
        rz = rz if rz is not None else 0.0

        try:
            # Special case: access existing node and add mass directly to it
            # model.geometry.add_mass(node_tag, mx, my, mz, rx, ry, rz)
            model.geometry.nodes[node_tag].add_mass(mx, my, mz, rx, ry, rz)
            return True
            
        except Exception as e:
            print(f"Error building mass for node {node_tag} from row {row_index}: {e}")
            return False

