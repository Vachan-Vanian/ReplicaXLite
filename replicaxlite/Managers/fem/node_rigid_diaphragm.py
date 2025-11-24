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


class ReplicaXFemNodeRigidDiaphragmManager:
    """
    Manager for the Rigid Diaphragm constraints table in ReplicaXLite.
    """
    
    def __init__(self, rigid_diaphragms_tab_widget, settings, nodes_table):
        self.rigid_diaphragms_tab_widget = rigid_diaphragms_tab_widget
        self.settings = settings
        self.nodes_table = nodes_table

        layout = QVBoxLayout(self.rigid_diaphragms_tab_widget)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)
        
        # Create table
        self.table = self.rigid_diaphragms_table = ReplicaXTable(rows=0, columns=4, settings=self.settings)
        
        # Set column types (DATA types, not widget types!)
        self.rigid_diaphragms_table.set_column_types(['int', 'int', 'list(int)', 'str'])
        
        # Set headers
        self.rigid_diaphragms_table.set_headers(['Direction', 'Master Node', 'Slave Nodes', 'Comment'])
        
        # Configure dropdowns BEFORE linking
        self.rigid_diaphragms_table.set_dropdown(0, [1, 2, 3])
        self.rigid_diaphragms_table.set_dropdown(1, [])
        self.rigid_diaphragms_table.set_dropdown(2, [], multi=True)  # ← Multi-select!
        
        # Link dropdowns to nodes table
        self.rigid_diaphragms_table.link_dropdown_to_column(
            dropdown_col=1,
            source_table=self.nodes_table,
            source_col=0,
            include_empty=True
        )
        
        self.rigid_diaphragms_table.link_dropdown_to_column(
            dropdown_col=2,
            source_table=self.nodes_table,
            source_col=0,
            include_empty=True
        )
        
        # Initialize table cells (this will sync dropdowns)
        self.rigid_diaphragms_table.init_table_cells()
        
        layout.addWidget(self.rigid_diaphragms_table)




    def create_fem_table_code(self, model):
        """
        Create all rigid diaphragm constraints from the GUI table.
        
        Args:
            model: StructuralModel instance
        Returns:
            None
        """
        rows = self.rigid_diaphragms_table.rowCount()
        
        for i in range(rows):
            try:
                self.create_fem_table_row_code(model, i)
            except Exception as e:
                print(f"Rigid Diaphragm FEM Table: Error processing row {i}: {e}")
                continue

    def create_fem_table_row_code(self, model, row_index):
        """
        Build a single rigid diaphragm constraint from GUI data at specified row index.
        
        Args:
            model: StructuralModel instance
            row_index: Index of the row to process
        Returns:
            True else False
        """
        # Get basic info
        direction = self.rigid_diaphragms_table.get_cell_value(row_index, 0)   # Direction column
        master_node = self.rigid_diaphragms_table.get_cell_value(row_index, 1)  # Master Node column
        slave_nodes = self.rigid_diaphragms_table.get_cell_value(row_index, 2)  # Slave Nodes column

        if not direction:
            return False
            
        if not master_node:
            return False
            
        # Handle case where slave_nodes might be None or empty list
        if slave_nodes is None or (isinstance(slave_nodes, list) and len(slave_nodes) == 0):
            print(f"Warning: No slave nodes specified for rigid diaphragm row {row_index}")
            # Continue with just master node if needed, or skip
            slave_nodes = []
        
        try:
            # Create the actual rigid diaphragm constraint object in model
            model.constraints.create_rigid_diaphragm(
                direction=direction,
                master_node=master_node,
                slave_nodes=slave_nodes
            )
            return True
            
        except Exception as e:
            print(f"Error building rigid diaphragm from row {row_index}: {e}")
            return False
