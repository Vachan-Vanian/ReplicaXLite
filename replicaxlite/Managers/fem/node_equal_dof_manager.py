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


class ReplicaXFemNodeEqualDOFManager:
    """
    Manager for the EqualDOF constraints table in ReplicaXLite.
    
    Creates and manages a ReplicaXTable with columns:
    - Retained Node Tag (dropdown from available nodes)
    - Constrained Node Tag (dropdown from available nodes)  
    - DOFs (multi-select dropdown of degrees of freedom)
    - Comment (str)
    """
    
    def __init__(self, equal_dofs_tab_widget, settings, nodes_table):
        """
        Initialize the EqualDOF constraint manager.
        
        Args:
            equal_dofs_tab_widget: The QWidget container for the EqualDOF tab
        """
        self.equal_dofs_tab_widget = equal_dofs_tab_widget
        self.settings = settings
        self.nodes_table = nodes_table

        layout = QVBoxLayout(self.equal_dofs_tab_widget)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)
        
        # Create the EqualDOF table with initial rows
        self.table = self.equal_dofs_table = ReplicaXTable(rows=0, columns=4, settings=self.settings)
        
        # Set headers
        self.equal_dofs_table.set_column_types(['int', 'int', 'list(int)', 'str'])
        self.equal_dofs_table.set_dropdown(0, [])  # Retained node dropdown (will be populated from nodes)
        self.equal_dofs_table.set_dropdown(1, [])  # Constrained node dropdown (will be populated from nodes)
        self.equal_dofs_table.set_dropdown(2, [1, 2, 3, 4, 5, 6], multi=True)  # DOFs multi-select
        self.equal_dofs_table.set_headers(['Retained Node', 'Constrained Node', 'DOFs', 'Comment'])

        # Link retained node dropdown to available node tags
        self.equal_dofs_table.link_dropdown_to_column(
            dropdown_col=0,   # Retained node dropdown
            source_table=self.nodes_table,
            source_col=0,    # Node Tag column
            include_empty=True
        )

        # Link constrained node dropdown to available node tags  
        self.equal_dofs_table.link_dropdown_to_column(
            dropdown_col=1,   # Constrained node dropdown
            source_table=self.nodes_table,
            source_col=0,    # Node Tag column
            include_empty=True

        )

        # Initialize table cells (this will sync dropdowns)
        self.equal_dofs_table.init_table_cells()

        layout.addWidget(self.equal_dofs_table)







    def create_fem_table_code(self, model):
        """
        Create all EqualDOF constraints from the GUI table.
        
        Args:
            model: StructuralModel instance
        Returns:
            None
        """
        rows = self.equal_dofs_table.rowCount()
        
        for i in range(rows):
            try:
                self.create_fem_table_row_code(model, i)
            except Exception as e:
                print(f"EqualDOF FEM Table: Error processing row {i}: {e}")
                continue

    def create_fem_table_row_code(self, model, row_index):
        """
        Build a single EqualDOF constraint from GUI data at specified row index.
        
        Args:
            model: StructuralModel instance
            row_index: Index of the row to process
        Returns:
            True else False
        """
        # Get basic info
        retained_node = self.equal_dofs_table.get_cell_value(row_index, 0)   # Retained Node column
        constrained_node = self.equal_dofs_table.get_cell_value(row_index, 1)  # Constrained Node column
        dofs = self.equal_dofs_table.get_cell_value(row_index, 2)  # DOFs column

        if not retained_node:
            return False
            
        if not constrained_node:
            return False
            
        if not dofs:
            print(f"Warning: No DOFs specified for EqualDOF constraint in row {row_index}")
            # Continue with empty list of DOFs, or skip
            dofs = []
            
        # Check that retained and constrained nodes are different
        if retained_node == constrained_node:
            print(f"Warning: Retained node {retained_node} cannot be the same as constrained node in row {row_index}")
            return False

        try:
            # Create the actual EqualDOF constraint object in model
            model.constraints.create_equal_dof(
                retained_node=retained_node,
                constrained_node=constrained_node,
                dofs=dofs
            )
            return True
            
        except Exception as e:
            print(f"Error building EqualDOF constraint from row {row_index}: {e}")
            return False
