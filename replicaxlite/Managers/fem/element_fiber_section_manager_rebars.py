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


class ReplicaXFemElementFiberSectionRebarPointManager:
    """
    Manager for the Rebar Lines table in Fiber Sections.
    
    Creates and manages a ReplicaXTable with columns:
    - group_name (str)
    - points (table)
    - dia (float)
    - mat_tag (int)
    - color (str)
    - Comment (str)
    """
    
    def __init__(self, rebar_points_tab_widget, settings, materials_table):
        self.rebar_points_tab_widget = rebar_points_tab_widget
        self.settings = settings
        self.materials_table = materials_table

        layout = QVBoxLayout(self.rebar_points_tab_widget)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)
        
        # Create the rebar lines table with initial rows
        self.table = self.rebar_points_table = ReplicaXTable(rows=0, columns=7, settings=self.settings)
        
        # Set headers
        self.rebar_points_table.set_column_types(['str', 'str', 'table', 'float', 'int', 'str', 'str'])
        self.rebar_points_table.set_headers(['group_name', 'type', 'points', 'dia', 'mat_tag', 'color', 'Comment'])
        
        # Set units
        self.rebar_points_table.set_column_unit(3, 'Length')
        self.rebar_points_table.set_dropdown(4,[])
        
        # Configure dropdown for Material Tag column
        self.rebar_points_table.link_dropdown_to_column(
            dropdown_col=4,
            source_table=self.materials_table,
            source_col=0,
            include_empty=True
        )

        point_table = ReplicaXTable(rows=0, columns=2, settings=self.settings)
        # Set headers
        point_table.set_column_types(['float', 'float'])
        point_table.set_headers(['X', 'Y'])
        # Set units
        point_table.set_column_unit(0, 'Length')
        point_table.set_column_unit(1, 'Length')

        self.rebar_points_table.set_dropdown(1,['', 'Point'])

        self.rebar_points_table.link_dropdown_to_table(
            dropdown_col=1,
            table_col=2,
            templates={
                '': ReplicaXTable(0,0),
                "Point": point_table,
            }
        )
        
        # Initialize table cells (this will sync dropdowns and other widgets)
        self.rebar_points_table.init_table_cells()

        layout.addWidget(self.rebar_points_table)

class ReplicaXFemElementFiberSectionRebarLineManager:
    """
    Manager for the Rebar Lines table in Fiber Sections.
    
    Creates and manages a ReplicaXTable with columns:
    - group_name (str)
    - X Start (float)
    - Y Start (float)
    - X End (float)
    - Y End (float)
    - dia (float)
    - number of rebars (int)
    - mat_tag (int)
    - color (str)
    - Comment (str)
    """
    
    def __init__(self, rebar_lines_tab_widget, settings, materials_table):
        self.rebar_lines_tab_widget = rebar_lines_tab_widget
        self.settings = settings
        self.materials_table = materials_table

        layout = QVBoxLayout(self.rebar_lines_tab_widget)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)
        
        # Create the rebar lines table with initial rows
        self.table = self.rebar_lines_table = ReplicaXTable(rows=0, columns=10, settings=self.settings)
        
        # Set headers
        self.rebar_lines_table.set_column_types(['str', 
                                                 'float', 'float', 'float', 'float',
                                                 'float', 'int', 'int', 'str', 'str'])
        self.rebar_lines_table.set_headers(['group_name', 
                                            'X Start', 'Y Start', 'X End', 'Y End', 
                                            'dia', 'number of rebars', 'mat_tag', 'color', 'Comment'])
        
        # Set units
        self.rebar_lines_table.set_column_unit(1, 'Length')
        self.rebar_lines_table.set_column_unit(2, 'Length')
        self.rebar_lines_table.set_column_unit(3, 'Length')
        self.rebar_lines_table.set_column_unit(4, 'Length')
        self.rebar_lines_table.set_column_unit(5, 'Length')
        self.rebar_lines_table.set_dropdown(7,[])
        
        # Configure dropdown for Material Tag column
        self.rebar_lines_table.link_dropdown_to_column(
            dropdown_col=7,
            source_table=self.materials_table,
            source_col=0,
            include_empty=True
        )
        
        # Initialize table cells (this will sync dropdowns and other widgets)
        self.rebar_lines_table.init_table_cells()

        layout.addWidget(self.rebar_lines_table)

class ReplicaXFemElementFiberSectionRebarCircleManager:
    """
    Manager for the Rebar Circles table in Fiber Sections.
    
    Creates and manages a ReplicaXTable with columns:
    - group_name (str)
    - Center X (float)
    - Center Y (float)
    - radius (float)
    - dia (float)
    - angles (list(float))
    - mat_tag (int)
    - color (str)
    - Comment (str)
    """
    
    def __init__(self, rebar_circles_tab_widget, settings, materials_table):
        self.rebar_circles_tab_widget = rebar_circles_tab_widget
        self.settings = settings
        self.materials_table = materials_table

        layout = QVBoxLayout(self.rebar_circles_tab_widget)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)
        
        # Create the rebar circles table with initial rows
        self.table = self.rebar_circles_table = ReplicaXTable(rows=0, columns=9, settings=self.settings)
        
        # Set headers
        self.rebar_circles_table.set_column_types(['str', 'float', 'float', 'float', 'float', 'list(float)', 'int', 'str', 'str'])
        self.rebar_circles_table.set_headers(['group_name', 'Center X', 'Center Y', 'radius', 'dia', 'angles', 'mat_tag', 'color','Comment'])
        
        # Set units
        self.rebar_circles_table.set_column_unit(1, 'Length')
        self.rebar_circles_table.set_column_unit(2, 'Length')
        self.rebar_circles_table.set_column_unit(3, 'Length')
        self.rebar_circles_table.set_column_unit(4, 'Length')
        self.rebar_circles_table.set_column_unit(5, 'Angle')
        
        self.rebar_circles_table.set_dropdown(6,[])

        # Configure dropdown for Material Tag column
        self.rebar_circles_table.link_dropdown_to_column(
            dropdown_col=6,
            source_table=self.materials_table,
            source_col=0,
            include_empty=True
        )

        # Initialize table cells (this will sync dropdowns and other widgets)
        self.rebar_circles_table.init_table_cells()

        layout.addWidget(self.rebar_circles_table)

