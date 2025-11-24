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


class ReplicaXFemNodeConstraintManager:
    """
    Manager for the Constraints table in ReplicaXLite.
    
    Creates and manages a ReplicaXTable with columns:
    - Node Tag (int)
    - DX (bool) 
    - DY (bool)
    - DZ (bool)
    - RX (bool)
    - RY (bool)
    - RZ (bool)
    - Comment (str)
    """
    
    def __init__(self, constraints_tab_widget, settings, nodes_table):
        """
        Initialize the constraint manager.
        
        Args:
            constraints_tab_widget: The QWidget container for the constraints tab
        """
        self.constraints_tab_widget = constraints_tab_widget
        self.settings = settings
        self.nodes_table = nodes_table

        layout = QVBoxLayout(self.constraints_tab_widget)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)
        
        # Create the constraints table with initial rows
        self.table = self.constraints_table = ReplicaXTable(rows=0, columns=8, settings=self.settings)
        
        # Set headers
        self.constraints_table.set_column_types(['int', 'bool', 'bool', 'bool', 'bool', 'bool', 'bool', 'str'])
        self.constraints_table.set_dropdown(0, [])
        self.constraints_table.set_dropdown(1, [True, False])  # DX
        self.constraints_table.set_dropdown(2, [True, False])  # DY
        self.constraints_table.set_dropdown(3, [True, False])  # DZ
        self.constraints_table.set_dropdown(4, [True, False])  # RX
        self.constraints_table.set_dropdown(5, [True, False])  # RY
        self.constraints_table.set_dropdown(6, [True, False])  # RZ
        self.constraints_table.set_headers(['Node Tag', 'DX', 'DY', 'DZ', 'RX', 'RY', 'RZ', 'Comment'])

        # Link dropdown to library's Material column
        self.constraints_table.link_dropdown_to_column(
            dropdown_col=0,                     # Dropdown column of the the current table
            source_table=self.nodes_table,
            source_col=0,
            auto_update=True,
            unique_only=True,
            skip_empty=False
        )

        # Initialize table cells (this will sync dropdowns)
        self.constraints_table.init_table_cells()

        layout.addWidget(self.constraints_table)





    def create_fem_table_code(self, model):
        """
        Create all constraints from the GUI table.
        
        Args:
            model: StructuralModel instance
        Returns:
            None
        """
        rows = self.constraints_table.rowCount()
        
        for i in range(rows):
            try:
                self.create_fem_table_row_code(model, i)
            except Exception as e:
                print(f"Constraints FEM Table: Error processing row {i}: {e}")
                continue

    def create_fem_table_row_code(self, model, row_index):
        """
        Build a single constraint object from GUI data at specified row index.
        
        Args:
            model: StructuralModel instance
            row_index: Index of the row to process
        Returns:
            True else False
        """
        # Get basic info
        node_tag = self.constraints_table.get_cell_value(row_index, 0)   # Node Tag column
        dx = self.constraints_table.get_cell_value(row_index, 1)      # DX column
        dy = self.constraints_table.get_cell_value(row_index, 2)      # DY column
        dz = self.constraints_table.get_cell_value(row_index, 3)      # DZ column
        rx = self.constraints_table.get_cell_value(row_index, 4)      # RX column
        ry = self.constraints_table.get_cell_value(row_index, 5)      # RY column
        rz = self.constraints_table.get_cell_value(row_index, 6)      # RZ column

        if not node_tag:
            return False
            
        try:
            # Convert boolean values to integers (True -> 1, False -> 0)
            dx_int = int(dx) if isinstance(dx, bool) else dx
            dy_int = int(dy) if isinstance(dy, bool) else dy
            dz_int = int(dz) if isinstance(dz, bool) else dz
            rx_int = int(rx) if isinstance(rx, bool) else rx
            ry_int = int(ry) if isinstance(ry, bool) else ry
            rz_int = int(rz) if isinstance(rz, bool) else rz
            
            # Create the actual constraint object in model
            model.constraints.create_constraint(
                node_tag=node_tag,
                dx=dx_int,
                dy=dy_int,
                dz=dz_int,
                rx=rx_int,
                ry=ry_int,
                rz=rz_int
            )
            return True
            
        except Exception as e:
            print(f"Error building constraint from row {row_index}: {e}")
            return False
