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


class ReplicaXFemBeamElementUniformLoadManager:
    """
    Manager for the Beam Uniform Load table in ReplicaXLite.
    
    Creates and manages a ReplicaXTable with columns:
    - Tag (int)
    - Pattern (int)
    - Elements (list[int])
    - Wz (float)
    - Wy (float)
    - Wx (float)
    - Comment (str)
    """
    
    def __init__(self, beam_elemenets_loads_tab_widget, settings, load_patterns_table, beam_elements_table):
        """
        Initialize the beam uniform load manager.
        
        Args:
            beam_elemenets_loads_tab_widget: The QWidget container for the beam loads tab
            load_pattern_table: Reference to the load pattern table for dropdown links
        """
        self.beam_elemenets_loads_tab_widget = beam_elemenets_loads_tab_widget
        self.settings = settings
        self.load_patterns_table = load_patterns_table
        self.beam_elements_table = beam_elements_table

        layout = QVBoxLayout(self.beam_elemenets_loads_tab_widget)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)
        
        # Create the beam loads table with initial rows
        self.table = self.beam_elements_loads_table = ReplicaXTable(rows=0, columns=7, settings=self.settings)
        
        # Set headers
        self.beam_elements_loads_table.set_column_types(['int', 'int', 'list(int)', 'float', 'float', 'float', 'str'])
        self.beam_elements_loads_table.set_headers(['Tag', 'Pattern', 'Elements', 'Wz', 'Wy', 'Wx', 'Comment'])

        # Set units
        self.beam_elements_loads_table.set_column_unit(3, 'Distributed_Force')  # Wz column
        self.beam_elements_loads_table.set_column_unit(4, 'Distributed_Force')  # Wy column
        self.beam_elements_loads_table.set_column_unit(5, 'Distributed_Force')  # Wx column

        self.beam_elements_loads_table.set_dropdown(1, [])
        self.beam_elements_loads_table.set_dropdown(2, [], multi=True)

        self.beam_elements_loads_table.link_dropdown_to_column(
            dropdown_col=1,  # Start Node column
            source_table=self.load_patterns_table,
            source_col=0,   # Node Tag column
            include_empty=True
        )

        self.beam_elements_loads_table.link_dropdown_to_column(
            dropdown_col=2,  # Start Node column
            source_table=self.beam_elements_table,
            source_col=0,   # Node Tag column
            include_empty=True
        )


        # Initialize table cells
        self.beam_elements_loads_table.init_table_cells()

        layout.addWidget(self.beam_elements_loads_table)





    def create_fem_table_code(self, model):
        """
        Create all beam uniform loads from the GUI table.
        
        Args:
            model: StructuralModel instance
        Returns:
            None
        """
        rows = self.beam_elements_loads_table.rowCount()
        
        for i in range(rows):
            try:
                self.create_fem_table_row_code(model, i)
            except Exception as e:
                print(f"Beam Uniform Load FEM Table: Error processing row {i}: {e}")
                continue

    def create_fem_table_row_code(self, model, row_index):
        """
        Build a single beam uniform load from GUI data at specified row index.
        
        Args:
            model: StructuralModel instance
            row_index: Index of the row to process
        Returns:
            True else False
        """
        # Get basic info
        tag = self.beam_elements_loads_table.get_cell_value(row_index, 0)   # Tag column
        pattern_tag = self.beam_elements_loads_table.get_cell_value(row_index, 1)  # Pattern column
        element_tags = self.beam_elements_loads_table.get_cell_value(row_index, 2)  # Elements column
        wz = self.beam_elements_loads_table.get_cell_value(row_index, 3)  # Wz column
        wy = self.beam_elements_loads_table.get_cell_value(row_index, 4)  # Wy column
        wx = self.beam_elements_loads_table.get_cell_value(row_index, 5)  # Wx column

        if not tag:
            return False
            
        if not pattern_tag:
            return False
            
        if not element_tags:
            print(f"Warning: No elements specified for beam load {tag} in row {row_index}")
            return False

        # Handle case where force values might be None or empty
        wz = wz if wz is not None else 0.0
        wy = wy if wy is not None else 0.0
        wx = wx if wx is not None else 0.0

        try:
            # Create the actual beam uniform load object in model
            model.loading.create_beam_uniform_load(
                pattern_tag=pattern_tag,
                element_tags=element_tags,
                Wz=wz,
                Wy=wy,
                Wx=wx
            )
            return True
            
        except Exception as e:
            print(f"Error building beam uniform load from row {row_index}: {e}")
            return False
