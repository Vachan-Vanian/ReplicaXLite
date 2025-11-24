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


class ReplicaXFemNodeRigidLinkManager:
    """
    Manager for the Rigid Link constraints table in ReplicaXLite.
    
    Creates and manages a ReplicaXTable with columns:
    - Link Type (dropdown: 'bar' or 'beam')
    - Master Node Tag (dropdown from available nodes)
    - Slave Node Tag (dropdown from available nodes)
    - Comment (str)
    """
    
    def __init__(self, rigid_links_tab_widget, settings, nodes_table):
        """
        Initialize the rigid link constraint manager.
        
        Args:
            rigid_links_tab_widget: The QWidget container for the rigid link tab
        """
        self.rigid_links_tab_widget = rigid_links_tab_widget
        self.settings = settings
        self.nodes_table = nodes_table

        layout = QVBoxLayout(self.rigid_links_tab_widget)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)
        
        # Create the rigid link table with initial rows
        self.table = self.rigid_links_table = ReplicaXTable(rows=0, columns=4, settings=self.settings)
        
        # Set headers
        self.rigid_links_table.set_column_types(['str', 'int', 'int', 'str'])
        self.rigid_links_table.set_dropdown(0, ['bar', 'beam'])  # Link type options
        self.rigid_links_table.set_dropdown(1, [])  # Master node dropdown (will be populated from nodes)
        self.rigid_links_table.set_dropdown(2, [])  # Slave node dropdown (will be populated from nodes)
        self.rigid_links_table.set_headers(['Link Type', 'Master Node', 'Slave Node', 'Comment'])

        # Link master node dropdown to available node tags
        self.rigid_links_table.link_dropdown_to_column(
            dropdown_col=1, # Master node dropdown
            source_table=self.nodes_table,
            source_col=0,  # Node Tag column
            include_empty=True
        )

        # Link slave node dropdown to available node tags  
        self.rigid_links_table.link_dropdown_to_column(
            dropdown_col=2, # Slave node dropdown
            source_table=self.nodes_table,
            source_col=0,  # Node Tag column
            include_empty=True
        )

        # Initialize table cells (this will sync dropdowns)
        self.rigid_links_table.init_table_cells()

        layout.addWidget(self.rigid_links_table)






    def create_fem_table_code(self, model):
        """
        Create all rigid link constraints from the GUI table.
        
        Args:
            model: StructuralModel instance
        Returns:
            None
        """
        rows = self.rigid_links_table.rowCount()
        
        for i in range(rows):
            try:
                self.create_fem_table_row_code(model, i)
            except Exception as e:
                print(f"Rigid Link FEM Table: Error processing row {i}: {e}")
                continue

    def create_fem_table_row_code(self, model, row_index):
        """
        Build a single rigid link constraint from GUI data at specified row index.
        
        Args:
            model: StructuralModel instance
            row_index: Index of the row to process
        Returns:
            True else False
        """
        # Get basic info
        link_type = self.rigid_links_table.get_cell_value(row_index, 0)   # Link Type column
        master_node = self.rigid_links_table.get_cell_value(row_index, 1)  # Master Node column
        slave_node = self.rigid_links_table.get_cell_value(row_index, 2)  # Slave Node column

        if not link_type:
            return False
            
        if not master_node:
            return False
            
        if not slave_node:
            return False
            
        # Check that master and slave nodes are different
        if master_node == slave_node:
            print(f"Warning: Master node {master_node} cannot be the same as slave node in row {row_index}")
            return False

        try:
            # Create the actual rigid link constraint object in model
            model.constraints.create_rigid_link(
                link_type=link_type,
                master_node=master_node,
                slave_node=slave_node
            )
            return True
            
        except Exception as e:
            print(f"Error building rigid link from row {row_index}: {e}")
            return False






