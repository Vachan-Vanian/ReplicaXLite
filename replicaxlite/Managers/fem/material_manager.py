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


class ReplicaXFemMaterialManager:
    """
    Manager for the Materials table in ReplicaXLite.
    
    Creates and manages a ReplicaXTable with columns:
    - Tag (int)
    - Name (str)
    - Type (str) 
    - Properties (nested table)
    - Comment (str)
    """
    
    def __init__(self, materials_tab_widget, settings):
        """
        Initialize the materials manager.
        
        Args:
            materials_tab_widget: The QWidget container for the materials tab
        """
        self.materials_tab_widget = materials_tab_widget
        self.settings = settings

        layout = QVBoxLayout(self.materials_tab_widget)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)
        
        # Create the materials table with initial rows
        self.table = self.materials_table = ReplicaXTable(rows=0, columns=5, settings=self.settings)
        
        # Set headers
        self.materials_table.set_column_types(['int', 'str', 'str', 'table', 'str'])
        self.materials_table.set_headers(['Tag', 'Name', 'Type', 'Properties', 'Comment'])
        self.materials_table.set_dropdown(2, ['', 'Elastic', 'ElasticPP', 'ElasticPPGap', 'ENT', 'Steel01', 'Steel02', 
                                            'Dodd_Restrepo', 'RambergOsgoodSteel', 'SteelMPF', 'Concrete01', 'Concrete02', 
                                            'Concrete04', 'Concrete06', 'Concrete07', 'Concrete01WithSITC', 'Masonry', 
                                            'Series', 'Parallel'])
        
        # Link dropdown to templates
        self.materials_table.link_dropdown_to_table(
            dropdown_col=2,      # Material dropdown
            table_col=3,         # Properties nested table
            templates={
                '': ReplicaXTable(0,0),
                'Elastic': self.Elastic(),
                'ElasticPP': self.ElasticPP(),
                'ElasticPPGap': self.ElasticPPGap(),
                'ENT': self.ENT(),
                'Steel01': self.Steel01(),
                'Steel02': self.Steel02(),
                'Dodd_Restrepo': self.Dodd_Restrepo(),
                'RambergOsgoodSteel': self.RambergOsgoodSteel(),
                'SteelMPF': self.SteelMPF(),
                'Concrete01': self.Concrete01(),
                'Concrete02': self.Concrete02(),
                'Concrete04': self.Concrete04(),
                'Concrete06': self.Concrete06(),
                'Concrete07': self.Concrete07(),
                'Concrete01WithSITC': self.Concrete01WithSITC(),
                'Masonry': self.Masonry(),
                'Series': self.Series(),
                'Parallel': self.Parallel()

            }
        )

        # Initialize table cells (this will sync dropdowns)
        self.materials_table.init_table_cells()

        layout.addWidget(self.materials_table)

    def fill_table(self, cell_data, table):
        for i, row_data in enumerate(cell_data):
            for j, value in enumerate(row_data):
                if value is not None:
                    table.set_cell_value(i, j, value)
        return table
    
    def Elastic(self):
        cell_data = [
            ["name", "Elastic", "No", None, None],
            ["E", "200 GPa", "No", None, None],
            ["eta", None, "Yes", None, None],
            ["Eneg", None, "Yes", None, None]
        ]
        if cell_data:
            rows = len(cell_data)
            columns = len(cell_data[0]) if cell_data[0] else 0
        else:
            rows, columns = 0, 0

        table= ReplicaXTable(rows=rows, columns=columns, settings=self.settings)
        # Set main column types
        table.set_column_types(['str', 'float', 'str', 'str', 'str'])
        # Set row-specific type overrides (row 0 and row 1)
        table.set_row_types(0, ['str', 'str', 'str', 'str', 'str'])
        table.set_row_types(1, ['str', 'int', 'str', 'str', 'str'])
        # Set headers
        table.set_headers(['Property', 'Value', 'Optional', 'Group', 'Comment'])
        # Set cell-specific units configurations instead of row_units
        table.set_cell_unit(1, 1, 'E_G_K_Modulus')  # Row 1, Col 1
        table.set_cell_unit(3, 1, 'E_G_K_Modulus')  # Row 3, Col 1

        return self.fill_table(cell_data, table)

    def ElasticPP(self):
        cell_data = [
            ["Name", "ElasticPP", "No", None, None],
            ["E", '200 GPa', "No", None, None],
            ["epsyP", 0.002, "No", None, None],
            ["epsyN", None, "Yes", None, None],
            ["eps0", None, "Yes", None, None]
        ]
        
        if cell_data:
            rows = len(cell_data)
            columns = len(cell_data[0]) if cell_data[0] else 0
        else:
            rows, columns = 0, 0

        table = ReplicaXTable(rows=rows, columns=columns, settings=self.settings)
        # Set main column types
        table.set_column_types(['str', 'float', 'str', 'str', 'str'])
         # Set row-specific type overrides (row 0 and row 1)
        table.set_row_types(0, ['str', 'str', 'str', 'str', 'str'])
        table.set_row_types(1, ['str', 'int', 'str', 'str', 'str'])
        # Set headers
        table.set_headers(['Property', 'Value', 'Optional', 'Group', 'Comment'])
        # Set cell-specific units configurations instead of row_units
        table.set_cell_unit(1, 1, 'E_G_K_Modulus')  # Row 1 , Col 1

        return self.fill_table(cell_data, table)
    
    def ElasticPPGap(self):
        cell_data = [
            ["Name", "ElasticPPGap", "No", None, None],
            ["E", '200 GPa', "No", None, None],
            ["Fy", '500 MPa', "No", None, None],
            ["gap", 0.0, "No", None, None],
            ["eta", None, "Yes", None, None],
            ["damage", None, "Yes", None, None]
        ]

        if cell_data:
            rows = len(cell_data)
            columns = len(cell_data[0]) if cell_data[0] else 0
        else:
            rows, columns = 0, 0

        table = ReplicaXTable(rows=rows, columns=columns, settings=self.settings)
        # Set main column types
        table.set_column_types(['str', 'float', 'str', 'str', 'str'])
         # Set row-specific type overrides (row 0 and row 1)
        table.set_row_types(0, ['str', 'str', 'str', 'str', 'str'])
        table.set_row_types(5, ['str', 'str', 'str', 'str', 'str'])

        # Set headers
        table.set_headers(['Property', 'Value', 'Optional', 'Group', 'Comment'])
        # Set cell-specific units configurations instead of row_units
        table.set_cell_unit(1, 1, 'E_G_K_Modulus')  # Row 1 , Col 1
        table.set_cell_unit(2, 1, 'Stress') # Row 2, Col 1

        table.set_cell_dropdown(5,1, ["", "noDamage", "damage"])
        table.init_table_cells()

        return self.fill_table(cell_data, table)

 
    def ENT(self):
        cell_data = [
            ["Name", "ENT", "No", None, None],
            ["E", '200 GPa', "No", None, None]
        ]

        if cell_data:
            rows = len(cell_data)
            columns = len(cell_data[0]) if cell_data[0] else 0
        else:
            rows, columns = 0, 0

        table = ReplicaXTable(rows=rows, columns=columns, settings=self.settings)
        # Set main column types
        table.set_column_types(['str', 'float', 'str', 'str', 'str'])
         # Set row-specific type overrides row 0
        table.set_row_types(0, ['str', 'str', 'str', 'str', 'str'])

        # Set headers
        table.set_headers(['Property', 'Value', 'Optional', 'Group', 'Comment'])
        # Set cell-specific units configurations instead of row_units
        table.set_cell_unit(1, 1, 'E_G_K_Modulus')  # Row 1 , Col 1

        return self.fill_table(cell_data, table)

    def Steel01(self):
        cell_data = [
            ["Name", "Steel01", "No", None, None],
            ["Fy", '550 MPa', "No", None, None],
            ["E0", '200 GPa', "No", None, None],
            ["b", 0.01, "No", None, None],
            ["a1", None, "Yes", "g1", None],
            ["a2", None, "Yes", "g1", None],
            ["a3", None, "Yes", "g1", None],
            ["a4", None, "Yes", "g1", None]
        ]

        if cell_data:
            rows = len(cell_data)
            columns = len(cell_data[0]) if cell_data[0] else 0
        else:
            rows, columns = 0, 0

        table = ReplicaXTable(rows=rows, columns=columns, settings=self.settings)
        # Set main column types
        table.set_column_types(['str', 'float', 'str', 'str', 'str'])
         # Set row-specific type overrides (row 0 and row 1)
        table.set_row_types(0, ['str', 'str', 'str', 'str', 'str'])

        # Set headers
        table.set_headers(['Property', 'Value', 'Optional', 'Group', 'Comment'])
        # Set cell-specific units configurations instead of row_units
        table.set_cell_unit(1, 1, 'Stress')  # Row 1 , Col 1
        table.set_cell_unit(2, 1, 'E_G_K_Modulus') #Row 2, Col 1

        return self.fill_table(cell_data, table)

    def Steel02(self):
        cell_data = [
            ["Name", "Steel02", "No", None, None],
            ["Fy", '550 MPa', "No", None, None],
            ["E0", '200 GPa', "No", None, None],
            ["b", 0.01, "No", None, None],
            ["*[R0,cR1,cR2]", [15.0, 0.925, 0.15], "No", None, None],
            ["a1", None, "Yes", "g1", None],
            ["a2", None, "Yes", "g1", None],
            ["a3", None, "Yes", "g1", None],
            ["a4", None, "Yes", "g1", None],
            ["sigInit", None, "Yes", None, None]
        ]

        if cell_data:
            rows = len(cell_data)
            columns = len(cell_data[0]) if cell_data[0] else 0
        else:
            rows, columns = 0, 0

        table = ReplicaXTable(rows=rows, columns=columns, settings=self.settings)
        # Set main column types
        table.set_column_types(['str', 'float', 'str', 'str', 'str'])
         # Set row-specific type overrides (row 0 and row 1)
        table.set_row_types(0, ['str', 'str', 'str', 'str', 'str'])
        table.set_row_types(4, ['str', 'list(float)', 'str', 'str', 'str'])

        # Set headers
        table.set_headers(['Property', 'Value', 'Optional', 'Group', 'Comment'])
        # Set cell-specific units configurations instead of row_units
        table.set_cell_unit(1, 1, 'Stress')  # Row 1 , Col 1
        table.set_cell_unit(2, 1, 'E_G_K_Modulus') #Row 2, Col 1

        return self.fill_table(cell_data, table)

    def SteelMPF(self):
        cell_data = [
            ["Name", "SteelMPF", "No", None, None],
            ["fyp", '500 MPa', "No", None, None],
            ["fyn", '-500 MPa', "No", None, None],
            ["E0", '200 GPa', "No", None, None],
            ["bp", 0.01, "No", None, None],
            ["bn", 0.01, "No", None, None],
            ["*params", [20.0, 0.925, 0.15], "No", None, None],
            ["a1", None, "Yes", None, None],
            ["a2", None, "Yes", None, None],
            ["a3", None, "Yes", None, None],
            ["a4", None, "Yes", None, None]
        ]

        if cell_data:
            rows = len(cell_data)
            columns = len(cell_data[0]) if cell_data[0] else 0
        else:
            rows, columns = 0, 0

        table = ReplicaXTable(rows=rows, columns=columns, settings=self.settings)
        # Set main column types
        table.set_column_types(['str', 'float', 'str', 'str', 'str'])
         # Set row-specific type overrides (row 0 and row 1)
        table.set_row_types(0, ['str', 'str', 'str', 'str', 'str'])
        table.set_row_types(7, ['str', 'list(float)', 'str', 'str', 'str'])

        # Set headers
        table.set_headers(['Property', 'Value', 'Optional', 'Group', 'Comment'])
        # Set cell-specific units configurations instead of row_units
        table.set_cell_unit(1, 1, 'Stress')  # Row 1 , Col 1
        table.set_cell_unit(2, 1, 'Stress') # Row 2, Col 1
        table.set_cell_unit(3, 1, 'E_G_K_Modulus')

        return self.fill_table(cell_data, table)

    def Dodd_Restrepo(self):
        cell_data = [
            ["Name", "Dodd_Restrepo", "No", None, None],
            ["Fy", '500 MPa', "No", None, None],
            ["Fsu", '600 MPa', "No", None, None],
            ["ESH", 0.02, "No", None, None],
            ["ESU", 0.12, "No", None, None],
            ["Youngs", '200 GPa', "No", None, None],
            ["ESHI", 0.06, "No", None, None],
            ["FSHI", '550 MPa', "No", None, None],
            ["OmegaFac", None, "Yes", None, None]
        ]

        if cell_data:
            rows = len(cell_data)
            columns = len(cell_data[0]) if cell_data[0] else 0
        else:
            rows, columns = 0, 0

        table = ReplicaXTable(rows=rows, columns=columns, settings=self.settings)
        # Set main column types
        table.set_column_types(['str', 'float', 'str', 'str', 'str'])
         # Set row-specific type overrides row 0
        table.set_row_types(0, ['str', 'str', 'str', 'str', 'str'])

        # Set headers
        table.set_headers(['Property', 'Value', 'Optional', 'Group', 'Comment'])
        # Set cell-specific units configurations instead of row_units
        table.set_cell_unit(1, 1, 'Stress')  # Row 1 , Col 1
        table.set_cell_unit(2, 1, 'Stress') # Row 2, Col 1
        table.set_cell_unit(5, 1, 'E_G_K_Modulus') # Row 5, Col 1
        table.set_cell_unit(7, 1, 'Stress')  # Row 7, Col 1

        return self.fill_table(cell_data, table)

    def RambergOsgoodSteel(self):
        cell_data = [
            ["Name", "RambergOsgoodSteel", "No", None, None],
            ["fy", '500 MPa', "No", None, None],
            ["E0", '200 GPa', "No", None, None],
            ["a", 0.002, "No", None, None],
            ["n", 10.0, "No", None, None]
        ]

        if cell_data:
            rows = len(cell_data)
            columns = len(cell_data[0]) if cell_data[0] else 0
        else:
            rows, columns = 0, 0

        table = ReplicaXTable(rows=rows, columns=columns, settings=self.settings)
        # Set main column types
        table.set_column_types(['str', 'float', 'str', 'str', 'str'])
         # Set row-specific type overrides (row 0 and row 1)
        table.set_row_types(0, ['str', 'str', 'str', 'str', 'str'])

        # Set headers
        table.set_headers(['Property', 'Value', 'Optional', 'Group', 'Comment'])
        # Set cell-specific units configurations instead of row_units
        table.set_cell_unit(1, 1, 'Stress')  # Row 1 , Col 1
        table.set_cell_unit(2, 1, 'E_G_K_Modulus') # Row 2, Col 1

        return self.fill_table(cell_data, table)

    def Concrete01(self):
        cell_data = [
            ["Name", "Concrete01", "No", None, None],
            ["fpc", '-30 MPa', "No", None, "Compressive concrete parameters should be input as negative values"],
            ["epsc0", '-0.002', "No", None, None],
            ["fpcu", '-25 MPa', "No", None, None],
            ["epsU", '-0.004', "No", None, None]
        ]

        if cell_data:
            rows = len(cell_data)
            columns = len(cell_data[0]) if cell_data[0] else 0
        else:
            rows, columns = 0, 0

        table = ReplicaXTable(rows=rows, columns=columns, settings=self.settings)
        # Set main column types
        table.set_column_types(['str', 'float', 'str', 'str', 'str'])
         # Set row-specific type overrides (row 0 and row 1)
        table.set_row_types(0, ['str', 'str', 'str', 'str', 'str'])

        # Set headers
        table.set_headers(['Property', 'Value', 'Optional', 'Group', 'Comment'])
        # Set cell-specific units configurations instead of row_units
        table.set_cell_unit(1, 1, 'Stress')  # Row 1 , Col 1
        table.set_cell_unit(3, 1, 'Stress') # Row 3, Col 1

        return self.fill_table(cell_data, table)
    
    def Concrete02(self):
        cell_data = [
            ["Name", "Concrete02", "No", None, None],
            ["fpc", '-30 MPa', "No", None, None],
            ["epsc0", '-0.002', "No", None, None],
            ["fpcu", '-10 MPa', "No", None, None],
            ["epsU", '-0.01', "No", None, None],
            ["lambda", 0.5, "No", None, None],
            ["ft", '2 MPa', "No", None, None],
            ["Ets", '1 GPa', "No", None, None]
        ]

        if cell_data:
            rows = len(cell_data)
            columns = len(cell_data[0]) if cell_data[0] else 0
        else:
            rows, columns = 0, 0

        table = ReplicaXTable(rows=rows, columns=columns, settings=self.settings)
        # Set main column types
        table.set_column_types(['str', 'float', 'str', 'str', 'str'])
         # Set row-specific type overrides (row 0 and row 1)
        table.set_row_types(0, ['str', 'str', 'str', 'str', 'str'])

        # Set headers
        table.set_headers(['Property', 'Value', 'Optional', 'Group', 'Comment'])
        # Set cell-specific units configurations instead of row_units
        table.set_cell_unit(1, 1, 'Stress')  # Row 1 , Col 1
        table.set_cell_unit(3, 1, 'Stress') # Row 3, Col 1
        table.set_cell_unit(6, 1, 'Stress') # Row 6, Col 1
        table.set_cell_unit(7, 1, 'E_G_K_Modulus')  # Row 7, Col 1

        return self.fill_table(cell_data, table)

    def Concrete04(self):
        cell_data = [
            ["Name", "Concrete04", "No", None, None],
            ["fc", '-30 MPa', "No", None, None],
            ["epsc", '-0.002', "No", None, None],
            ["epscu", '-0.01', "No", None, None],
            ["Ec", '30 GPa', "No", None, None],
            ["fct", None, "Yes", None, None],
            ["et", None, "Yes", None, None],
            ["beta", None, "Yes", None, None]
        ]

        if cell_data:
            rows = len(cell_data)
            columns = len(cell_data[0]) if cell_data[0] else 0
        else:
            rows, columns = 0, 0

        table = ReplicaXTable(rows=rows, columns=columns, settings=self.settings)
        # Set main column types
        table.set_column_types(['str', 'float', 'str', 'str', 'str'])
         # Set row-specific type overrides (row 0 and row 1)
        table.set_row_types(0, ['str', 'str', 'str', 'str', 'str'])

        # Set headers
        table.set_headers(['Property', 'Value', 'Optional', 'Group', 'Comment'])
        # Set cell-specific units configurations instead of row_units
        table.set_cell_unit(1, 1, 'Stress')  # Row 1 , Col 1
        table.set_cell_unit(4, 1, 'E_G_K_Modulus') # Row 4, Col 1
        table.set_cell_unit(5, 1, 'Stress') # Row 4, Col 1

        return self.fill_table(cell_data, table)

    def Concrete06(self):
        cell_data = [
            ["Name", "Concrete06", "No", None, None],
            ["fc", '-30 MPa', "No", None, None],
            ["e0", '-0.002', "No", None, None],
            ["n", 2.0, "No", None, None],
            ["k", 0.67, "No", None, None],
            ["alpha1", 0.5, "No", None, None],
            ["fcr", '3 MPa', "No", None, None],
            ["ecr", '0.0001', "No", None, None],
            ["b", 1.0, "No", None, None],
            ["alpha2", 0.5, "No", None, None]
        ]

        if cell_data:
            rows = len(cell_data)
            columns = len(cell_data[0]) if cell_data[0] else 0
        else:
            rows, columns = 0, 0

        table = ReplicaXTable(rows=rows, columns=columns, settings=self.settings)
        # Set main column types
        table.set_column_types(['str', 'float', 'str', 'str', 'str'])
         # Set row-specific type overrides (row 0 and row 1)
        table.set_row_types(0, ['str', 'str', 'str', 'str', 'str'])

        # Set headers
        table.set_headers(['Property', 'Value', 'Optional', 'Group', 'Comment'])
        # Set cell-specific units configurations instead of row_units
        table.set_cell_unit(1, 1, 'Stress')  # Row 1 , Col 1
        table.set_cell_unit(6, 1, 'Stress') # Row 6, Col 1

        return self.fill_table(cell_data, table)

    def Concrete07(self):
        cell_data = [
            ["Name", "Concrete07", "No", None, None],
            ["fc", '-30 MPa', "No", None, None],
            ["epsc", '-0.002', "No", None, None],
            ["Ec", '30 GPa', "No", None, None],
            ["ft", '3 MPa', "No", None, None],
            ["et", '0.0001', "No", None, None],
            ["xp", 2.0, "No", None, None],
            ["xn", 2.3, "No", None, None],
            ["r", 1.2, "No", None, None]
        ]

        if cell_data:
            rows = len(cell_data)
            columns = len(cell_data[0]) if cell_data[0] else 0
        else:
            rows, columns = 0, 0

        table = ReplicaXTable(rows=rows, columns=columns, settings=self.settings)
        # Set main column types
        table.set_column_types(['str', 'float', 'str', 'str', 'str'])
         # Set row-specific type overrides (row 0 and row 1)
        table.set_row_types(0, ['str', 'str', 'str', 'str', 'str'])

        # Set headers
        table.set_headers(['Property', 'Value', 'Optional', 'Group', 'Comment'])
        # Set cell-specific units configurations instead of row_units
        table.set_cell_unit(1, 1, 'Stress')  # Row 1 , Col 1
        table.set_cell_unit(3, 1, 'E_G_K_Modulus') # Row 3, Col 1
        table.set_cell_unit(4, 1, 'Stress') # Row 4, Col 1

        return self.fill_table(cell_data, table)

    def Concrete01WithSITC(self):
        cell_data = [
            ["Name", "Concrete01WithSITC", "No", None, None],
            ["fpc", '-30 MPa', "No", None, None],
            ["epsc0", '-0.002', "No", None, None],
            ["fpcu", '-25 MPa', "No", None, None],
            ["epsU", '-0.004', "No", None, None],
            ["endStrainSITC", 0.03, "Yes", None, None]
        ]

        if cell_data:
            rows = len(cell_data)
            columns = len(cell_data[0]) if cell_data[0] else 0
        else:
            rows, columns = 0, 0

        table = ReplicaXTable(rows=rows, columns=columns, settings=self.settings)
        # Set main column types
        table.set_column_types(['str', 'float', 'str', 'str', 'str'])
         # Set row-specific type overrides (row 0 and row 1)
        table.set_row_types(0, ['str', 'str', 'str', 'str', 'str'])

        # Set headers
        table.set_headers(['Property', 'Value', 'Optional', 'Group', 'Comment'])
        # Set cell-specific units configurations instead of row_units
        table.set_cell_unit(1, 1, 'Stress')  # Row 1 , Col 1
        table.set_cell_unit(3, 1, 'Stress') # Row 3, Col 1

        return self.fill_table(cell_data, table)

    def Masonry(self):
        cell_data = [
            ["Name", "Masonry", "No", None, None],
            ["Fm", '-10 MPa', "No", None, None],
            ["Ft", '1 MPa', "No", None, None],
            ["Um", '-0.002', "No", None, None],
            ["Uult", '-0.01', "No", None, None],
            ["Ucl", '0.001', "No", None, None],
            ["Emo", '5 GPa', "No", None, None],
            ["L", 1.0, "No", None, None],
            ["a1", 1.0, "No", None, None],
            ["a2", 0.5, "No", None, None],
            ["D1", '-0.005', "No", None, None],
            ["D2", '-0.015', "No", None, None],
            ["Ach", 0.4, "No", None, None],
            ["Are", 0.3, "No", None, None],
            ["Ba", 1.75, "No", None, None],
            ["Bch", 0.9, "No", None, None],
            ["Gun", 2.0, "No", None, None],
            ["Gplu", 0.6, "No", None, None],
            ["Gplr", 1.3, "No", None, None],
            ["Exp1", 1.75, "No", None, None],
            ["Exp2", 1.25, "No", None, None],
            ["IENV", 0, "No", None, None]
        ]

        if cell_data:
            rows = len(cell_data)
            columns = len(cell_data[0]) if cell_data[0] else 0
        else:
            rows, columns = 0, 0

        table = ReplicaXTable(rows=rows, columns=columns, settings=self.settings)
        # Set main column types
        table.set_column_types(['str', 'float', 'str', 'str', 'str'])
         # Set row-specific type overrides (row 0 and row 1)
        table.set_row_types(0, ['str', 'str', 'str', 'str', 'str'])
        table.set_row_types(21, ['str', 'int', 'str', 'str', 'str'])

        table.set_cell_dropdown(21,1, [0, 1])
        # Set headers
        table.set_headers(['Property', 'Value', 'Optional', 'Group', 'Comment'])
        # Set cell-specific units configurations instead of row_units
        table.set_cell_unit(1, 1, 'Stress')  # Row 1 , Col 1
        table.set_cell_unit(2, 1, 'Stress') # Row 2, Col 1
        table.set_cell_unit(6, 1, 'E_G_K_Modulus')
        table.set_cell_unit(7, 1, 'Length')

        table.init_table_cells()

        return self.fill_table(cell_data, table)
    
    def Series(self):
        cell_data = [
            ["Name", "Series", "No", None, None],
            ["matTags", [], "No", None, None]
        ]

        if cell_data:
            rows = len(cell_data)
            columns = len(cell_data[0]) if cell_data[0] else 0
        else:
            rows, columns = 0, 0

        table = ReplicaXTable(rows=rows, columns=columns, settings=self.settings)
        # Set main column types
        table.set_column_types(['str', 'float', 'str', 'str', 'str'])
         # Set row-specific type overrides (row 0 and row 1)
        table.set_row_types(0, ['str', 'str', 'str', 'str', 'str'])
        table.set_row_types(1, ['str', 'list(int)', 'str', 'str', 'str'])

        # Set headers
        table.set_headers(['Property', 'Value', 'Optional', 'Group', 'Comment'])

        table.set_cell_dropdown(1,1,[], multi=True)

        table.link_dropdown_to_cell(
            row=1,
            col=1,
            source_table=self.materials_table,
            source_col=0,
            include_empty=True
        )

        table.init_table_cells()

        return self.fill_table(cell_data, table)

    def Parallel(self):
        cell_data = [
            ["Name", "Parallel", "No", None, None],
            ["MatTags", [], "No", None, None],
            ["-factors", None, "Yes", None, None]
        ]

        if cell_data:
            rows = len(cell_data)
            columns = len(cell_data[0]) if cell_data[0] else 0
        else:
            rows, columns = 0, 0

        table = ReplicaXTable(rows=rows, columns=columns, settings=self.settings)
        # Set main column types
        table.set_column_types(['str', 'float', 'str', 'str', 'str'])
         # Set row-specific type overrides (row 0 and row 1)
        table.set_row_types(0, ['str', 'str', 'str', 'str', 'str'])
        table.set_row_types(1, ['str', 'list(int)', 'bool', 'str', 'str'])
        table.set_row_types(2, ['str', 'list(float)', 'bool', 'str', 'str'])

        # Set headers
        table.set_headers(['Property', 'Value', 'Optional', 'Group', 'Comment'])

        table.set_cell_dropdown(1,1,[], multi=True)

        table.link_dropdown_to_cell(
            row=1,
            col=1,
            source_table=self.materials_table,
            source_col=0,
            include_empty=True
        )

        table.init_table_cells()

        return self.fill_table(cell_data, table)


    def refresh_dropdown_nested_table_links_after_load(self):
        """Re-establish dropdown links after table load."""
        # Iterate through all rows in table
        for row in range(self.materials_table.rowCount()):
            # Get the pattern type from column 1 (Type column)
            pattern_type = self.materials_table.get_cell_value(row, 1)

            # Get nested table reference
            nested_table = self.materials_table.get_cell_value(row, 2)  # Properties column

            if not isinstance(nested_table, ReplicaXTable):
                continue

            if pattern_type == 'Series':
                nested_table.link_dropdown_to_cell(
                    row=1,
                    col=1,
                    source_table=self.materials_table,
                    source_col=0,
                    include_empty=True
                )
            elif pattern_type == 'Parallel':
                nested_table.link_dropdown_to_cell(
                    row=1,
                    col=1,
                    source_table=self.materials_table,
                    source_col=0,
                    include_empty=True
                )
    


    def create_fem_table_code(self, model):
        """
        Create all materials from the GUI table.
        
        Returns:
            
        """
        rows = self.materials_table.rowCount()
        
        for i in range(rows):
            try:
                self.create_fem_table_row_code(model, i)
            except Exception as e:
                print(f"Materials FEM Table: Error processing row {i}: {e}")
                continue



    def create_fem_table_row_code(self, model, row_index):
        """
        Build a single material object from GUI data at specified row index.
        
        Args:
            model: StructuralModel instance
            row_index: Index of the row to process
        Returns:
            True else False
        """
        # Get basic info
        tag = self.materials_table.get_cell_value(row_index, 0)  # Tag column
        name = self.materials_table.get_cell_value(row_index, 1)  # Name column
        material_type = self.materials_table.get_cell_value(row_index, 2)  # Type column
        
        if not tag:
            return False

        if not material_type:
            return False
        
        if not name:
            name = f"Material_{tag}"
        
        # Get the nested properties table for this row
        nested_table = self.materials_table.get_cell_value(row_index, 3)  # Properties column

        # Build parameters based on material type
        try:
            params = self._extract_parameters(material_type, nested_table)
            
            # Create the actual material object (this is what your user function does)
            model.properties.create_uniaxial_material(tag, name, material_type, params)
            return True
            
        except Exception as e:
            print(f"Error building material from row {row_index}: {e}")
            return False
    
    def _extract_parameters(self, material_type, nested_table):
        """
        Extract parameters from nested table based on material type.
        
        Args:
            material_type: The selected material type
            nested_table: The properties table for this material
            
        Returns:
            dict of parameters
        """
        params = {}
        
        # Handle different material types by extracting their specific parameters
        if material_type == 'Elastic':
            # Extract E and eta values (index 1, row 1)
            e_value = nested_table.get_cell_value(1, 1) 
            if e_value is not None:
                params['E'] = e_value
            
            # Handle optional parameters
            eta_value = nested_table.get_cell_value(2, 1)
            if eta_value is not None:
                params['eta'] = eta_value
                
            eneg_value = nested_table.get_cell_value(3, 1)
            if eneg_value is not None:
                params['Eneg'] = eneg_value
        
        elif material_type == 'ElasticPP':
            # Extract E and epsyP values
            e_value = nested_table.get_cell_value(1, 1) 
            if e_value is not None:
                params['E'] = e_value
                
            epsyp_value = nested_table.get_cell_value(2, 1)
            if epsyp_value is not None:
                params['epsyP'] = epsyp_value
            
            # Handle optional parameters                
            epsyn_value = nested_table.get_cell_value(3, 1)
            if epsyn_value is not None:
                params['epsyN'] = epsyn_value
                
            eps0_value = nested_table.get_cell_value(4, 1)
            if eps0_value is not None:
                params['eps0'] = eps0_value
        
        elif material_type == 'ElasticPPGap':
            # Extract E, Fy, gap values
            e_value = nested_table.get_cell_value(1, 1) 
            if e_value is not None:
                params['E'] = e_value
                
            fy_value = nested_table.get_cell_value(2, 1)
            if fy_value is not None:
                params['Fy'] = fy_value
                
            gap_value = nested_table.get_cell_value(3, 1)
            if gap_value is not None:
                params['gap'] = gap_value
            
            # Handle optional parameters 
            eta_value = nested_table.get_cell_value(4, 1)
            if eta_value is not None:
                params['eta'] = eta_value
                
            damage_value = nested_table.get_cell_value(5, 1)
            if damage_value is not None:
                params['damage'] = damage_value
        
        elif material_type == 'ENT':
            # Extract E value
            e_value = nested_table.get_cell_value(1, 1) 
            if e_value is not None:
                params['E'] = e_value
        
        elif material_type == 'Steel01':
            # Extract Fy, E0, b values
            fy_value = nested_table.get_cell_value(1, 1)
            if fy_value is not None:
                params['Fy'] = fy_value
                
            e0_value = nested_table.get_cell_value(2, 1)
            if e0_value is not None:
                params['E0'] = e0_value
                
            b_value = nested_table.get_cell_value(3, 1)
            if b_value is not None:
                params['b'] = b_value
                
            # Handle optional parameters (a1-a4)
            a1_value = nested_table.get_cell_value(4, 1)
            if a1_value is not None:
                params['a1'] = a1_value
            
            a2_value = nested_table.get_cell_value(5, 1)
            if a2_value is not None:
                params['a2'] = a2_value

            a3_value = nested_table.get_cell_value(6, 1)
            if a3_value is not None:
                params['a3'] = a3_value

            a4_value = nested_table.get_cell_value(7, 1)
            if a4_value is not None:
                params['a4'] = a4_value
        
        elif material_type == 'Steel02':
            # Extract Fy, E0, b values
            fy_value = nested_table.get_cell_value(1, 1)
            if fy_value is not None:
                params['Fy'] = fy_value
                
            e0_value = nested_table.get_cell_value(2, 1)
            if e0_value is not None:
                params['E0'] = e0_value
                
            b_value = nested_table.get_cell_value(3, 1)
            if b_value is not None:
                params['b'] = b_value
                
            # Handle the special case with [R0,cR1,cR2] list
            param_start_value = nested_table.get_cell_value(4, 1)
            if param_start_value:
                params['*params'] = param_start_value
            
            # Handle optional parameters (a1-a4)
            a1_value = nested_table.get_cell_value(5, 1)
            if a1_value is not None:
                params['a1'] = a1_value
            
            a2_value = nested_table.get_cell_value(6, 1)
            if a2_value is not None:
                params['a2'] = a2_value

            a3_value = nested_table.get_cell_value(7, 1)
            if a3_value is not None:
                params['a3'] = a3_value

            a4_value = nested_table.get_cell_value(8, 1)
            if a4_value is not None:
                params['a4'] = a4_value
                    
            # Handle optional sigInit parameter (row 9)
            siginit_value = nested_table.get_cell_value(9, 1)
            if siginit_value is not None:
                params['sigInit'] = siginit_value
        
        elif material_type == 'SteelMPF':
            # Extract fyp, fyn, E0, bp, bn values
            fyp_value = nested_table.get_cell_value(1, 1)
            if fyp_value is not None:
                params['fyp'] = fyp_value
                
            fyn_value = nested_table.get_cell_value(2, 1)
            if fyn_value is not None:
                params['fyn'] = fyn_value
                
            e0_value = nested_table.get_cell_value(3, 1)
            if e0_value is not None:
                params['E0'] = e0_value
                
            bp_value = nested_table.get_cell_value(4, 1)
            if bp_value is not None:
                params['bp'] = bp_value
                
            bn_value = nested_table.get_cell_value(5, 1)
            if bn_value is not None:
                params['bn'] = bn_value
                
            # Handle the special case with [params] list
            param_start_value = nested_table.get_cell_value(6, 1)  
            if param_start_value:
                params['*params'] = param_start_value
            
            # Handle optional parameters (a1-a4)
            a1_value = nested_table.get_cell_value(7, 1)
            if a1_value is not None:
                params['a1'] = a1_value
            
            a2_value = nested_table.get_cell_value(8, 1)
            if a2_value is not None:
                params['a2'] = a2_value

            a3_value = nested_table.get_cell_value(9, 1)
            if a3_value is not None:
                params['a3'] = a3_value

            a4_value = nested_table.get_cell_value(10, 1)
            if a4_value is not None:
                params['a4'] = a4_value
        
        elif material_type == 'Dodd_Restrepo':
            # Extract Fy, Fsu, ESH, ESU, Youngs, ESHI, FSHI values
            fy_value = nested_table.get_cell_value(1, 1)
            if fy_value is not None:
                params['Fy'] = fy_value
                
            fsu_value = nested_table.get_cell_value(2, 1)
            if fsu_value is not None:
                params['Fsu'] = fsu_value
                
            esh_value = nested_table.get_cell_value(3, 1)
            if esh_value is not None:
                params['ESH'] = esh_value
                
            esu_value = nested_table.get_cell_value(4, 1)
            if esu_value is not None:
                params['ESU'] = esu_value
                
            youngs_value = nested_table.get_cell_value(5, 1)
            if youngs_value is not None:
                params['Youngs'] = youngs_value
                
            eshi_value = nested_table.get_cell_value(6, 1)
            if eshi_value is not None:
                params['ESHI'] = eshi_value
                
            fshi_value = nested_table.get_cell_value(7, 1)
            if fshi_value is not None:
                params['FSHI'] = fshi_value
            
            # Handle optional parameters
            omega_value = nested_table.get_cell_value(8, 1)
            if omega_value is not None:
                params['OmegaFac'] = omega_value
        
        elif material_type == 'RambergOsgoodSteel':
            # Extract fy, E0, a, n values
            fy_value = nested_table.get_cell_value(1, 1)
            if fy_value is not None:
                params['fy'] = fy_value
                
            e0_value = nested_table.get_cell_value(2, 1)
            if e0_value is not None:
                params['E0'] = e0_value
                
            a_value = nested_table.get_cell_value(3, 1)
            if a_value is not None:
                params['a'] = a_value
                
            n_value = nested_table.get_cell_value(4, 1)
            if n_value is not None:
                params['n'] = n_value
        
        elif material_type == 'Concrete01':
            # Extract fpc, epsc0, fpcu, epsU values
            fpc_value = nested_table.get_cell_value(1, 1)
            if fpc_value is not None:
                params['fpc'] = fpc_value
                
            epsc0_value = nested_table.get_cell_value(2, 1)
            if epsc0_value is not None:
                params['epsc0'] = epsc0_value
                
            fpcu_value = nested_table.get_cell_value(3, 1)
            if fpcu_value is not None:
                params['fpcu'] = fpcu_value
                
            epsU_value = nested_table.get_cell_value(4, 1)
            if epsU_value is not None:
                params['epsU'] = epsU_value
        
        elif material_type == 'Concrete02':
            # Extract fpc, epsc0, fpcu, epsU values
            fpc_value = nested_table.get_cell_value(1, 1)
            if fpc_value is not None:
                params['fpc'] = fpc_value
                
            epsc0_value = nested_table.get_cell_value(2, 1)
            if epsc0_value is not None:
                params['epsc0'] = epsc0_value
                
            fpcu_value = nested_table.get_cell_value(3, 1)
            if fpcu_value is not None:
                params['fpcu'] = fpcu_value
                
            epsU_value = nested_table.get_cell_value(4, 1)
            if epsU_value is not None:
                params['epsU'] = epsU_value
                
            # Extract lambda, ft, Ets values
            lambda_value = nested_table.get_cell_value(5, 1)
            if lambda_value is not None:
                params['lambda'] = lambda_value
                
            ft_value = nested_table.get_cell_value(6, 1)
            if ft_value is not None:
                params['ft'] = ft_value
                
            e_ts_value = nested_table.get_cell_value(7, 1)
            if e_ts_value is not None:
                params['Ets'] = e_ts_value
        
        elif material_type == 'Concrete04':
            # Extract fc, epsc, epscu, Ec values
            fc_value = nested_table.get_cell_value(1, 1)
            if fc_value is not None:
                params['fc'] = fc_value
                
            epsc_value = nested_table.get_cell_value(2, 1)
            if epsc_value is not None:
                params['epsc'] = epsc_value
                
            epscu_value = nested_table.get_cell_value(3, 1)
            if epscu_value is not None:
                params['epscu'] = epscu_value
                
            ec_value = nested_table.get_cell_value(4, 1)
            if ec_value is not None:
                params['Ec'] = ec_value
                
            # Extract optional parameters
            fct_value = nested_table.get_cell_value(5, 1)
            if fct_value is not None:
                params['fct'] = fct_value
                
            et_value = nested_table.get_cell_value(6, 1)
            if et_value is not None:
                params['et'] = et_value
                
            beta_value = nested_table.get_cell_value(7, 1)
            if beta_value is not None:
                params['beta'] = beta_value
        
        elif material_type == 'Concrete06':
            # Extract fc, e0, n, k, alpha1 values
            fc_value = nested_table.get_cell_value(1, 1)
            if fc_value is not None:
                params['fc'] = fc_value
                
            e0_value = nested_table.get_cell_value(2, 1)
            if e0_value is not None:
                params['e0'] = e0_value
                
            n_value = nested_table.get_cell_value(3, 1)
            if n_value is not None:
                params['n'] = n_value
                
            k_value = nested_table.get_cell_value(4, 1)
            if k_value is not None:
                params['k'] = k_value
                
            alpha1_value = nested_table.get_cell_value(5, 1)
            if alpha1_value is not None:
                params['alpha1'] = alpha1_value
                
            # Extract fcr, ecr, b, alpha2 values
            fcr_value = nested_table.get_cell_value(6, 1)
            if fcr_value is not None:
                params['fcr'] = fcr_value
                
            ecr_value = nested_table.get_cell_value(7, 1)
            if ecr_value is not None:
                params['ecr'] = ecr_value
                
            b_value = nested_table.get_cell_value(8, 1)
            if b_value is not None:
                params['b'] = b_value
                
            alpha2_value = nested_table.get_cell_value(9, 1)
            if alpha2_value is not None:
                params['alpha2'] = alpha2_value
        
        elif material_type == 'Concrete07':
            # Extract fc, epsc, Ec values
            fc_value = nested_table.get_cell_value(1, 1)
            if fc_value is not None:
                params['fc'] = fc_value
                
            epsc_value = nested_table.get_cell_value(2, 1)
            if epsc_value is not None:
                params['epsc'] = epsc_value
                
            ec_value = nested_table.get_cell_value(3, 1)
            if ec_value is not None:
                params['Ec'] = ec_value
                
            # Extract ft, et, xp, xn, r values
            ft_value = nested_table.get_cell_value(4, 1)
            if ft_value is not None:
                params['ft'] = ft_value
                
            et_value = nested_table.get_cell_value(5, 1)
            if et_value is not None:
                params['et'] = et_value
                
            xp_value = nested_table.get_cell_value(6, 1)
            if xp_value is not None:
                params['xp'] = xp_value
                
            xn_value = nested_table.get_cell_value(7, 1)
            if xn_value is not None:
                params['xn'] = xn_value
                
            r_value = nested_table.get_cell_value(8, 1)
            if r_value is not None:
                params['r'] = r_value
        
        elif material_type == 'Concrete01WithSITC':
            # Extract fpc, epsc0, fpcu, epsU values
            fpc_value = nested_table.get_cell_value(1, 1)
            if fpc_value is not None:
                params['fpc'] = fpc_value
                
            epsc0_value = nested_table.get_cell_value(2, 1)
            if epsc0_value is not None:
                params['epsc0'] = epsc0_value
                
            fpcu_value = nested_table.get_cell_value(3, 1)
            if fpcu_value is not None:
                params['fpcu'] = fpcu_value
                
            epsU_value = nested_table.get_cell_value(4, 1)
            if epsU_value is not None:
                params['epsU'] = epsU_value
                
            # Extract optional endStrainSITC
            endstrain_value = nested_table.get_cell_value(5, 1)
            if endstrain_value is not None:
                params['endStrainSITC'] = endstrain_value
        
        elif material_type == 'Masonry':
            # Extract Fm, Ft, Um, Uult, Ucl values
            fm_value = nested_table.get_cell_value(1, 1)
            if fm_value is not None:
                params['Fm'] = fm_value
                
            ft_value = nested_table.get_cell_value(2, 1)
            if ft_value is not None:
                params['Ft'] = ft_value
                
            um_value = nested_table.get_cell_value(3, 1)
            if um_value is not None:
                params['Um'] = um_value
                
            uult_value = nested_table.get_cell_value(4, 1)
            if uult_value is not None:
                params['Uult'] = uult_value
                
            ucl_value = nested_table.get_cell_value(5, 1)
            if ucl_value is not None:
                params['Ucl'] = ucl_value
                
            # Extract Emo, L, a1, a2 values
            emoo_value = nested_table.get_cell_value(6, 1)
            if emoo_value is not None:
                params['Emo'] = emoo_value
                
            l_value = nested_table.get_cell_value(7, 1)
            if l_value is not None:
                params['L'] = l_value
                
            a1_value = nested_table.get_cell_value(8, 1)
            if a1_value is not None:
                params['a1'] = a1_value
                
            a2_value = nested_table.get_cell_value(9, 1)
            if a2_value is not None:
                params['a2'] = a2_value
                
            # Extract D1, D2, Ach, Are values
            d1_value = nested_table.get_cell_value(10, 1)
            if d1_value is not None:
                params['D1'] = d1_value
                
            d2_value = nested_table.get_cell_value(11, 1)
            if d2_value is not None:
                params['D2'] = d2_value
                
            ach_value = nested_table.get_cell_value(12, 1)
            if ach_value is not None:
                params['Ach'] = ach_value
                
            are_value = nested_table.get_cell_value(13, 1)
            if are_value is not None:
                params['Are'] = are_value
                
            # Extract Ba, Bch, Gun, Gplu, Gplr values
            ba_value = nested_table.get_cell_value(14, 1)
            if ba_value is not None:
                params['Ba'] = ba_value
                
            bch_value = nested_table.get_cell_value(15, 1)
            if bch_value is not None:
                params['Bch'] = bch_value
                
            gun_value = nested_table.get_cell_value(16, 1)
            if gun_value is not None:
                params['Gun'] = gun_value
                
            gplu_value = nested_table.get_cell_value(17, 1)
            if gplu_value is not None:
                params['Gplu'] = gplu_value
                
            gplr_value = nested_table.get_cell_value(18, 1)
            if gplr_value is not None:
                params['Gplr'] = gplr_value
                
            # Extract Exp1, Exp2 values
            exp1_value = nested_table.get_cell_value(19, 1)
            if exp1_value is not None:
                params['Exp1'] = exp1_value
                
            exp2_value = nested_table.get_cell_value(20, 1)
            if exp2_value is not None:
                params['Exp2'] = exp2_value
                
            # Extract IENV (integer value)
            ienv_value = nested_table.get_cell_value(21, 1)
            if ienv_value is not None:
                params['IENV'] = ienv_value
        
        elif material_type == 'Series':
            # Extract matTags list
            mat_tags_value = nested_table.get_cell_value(1, 1)
            if mat_tags_value is not None and isinstance(mat_tags_value, list):
                params['matTags'] = mat_tags_value
        
        elif material_type == 'Parallel':
            # Extract MatTags and -factors lists
            mat_tags_value = nested_table.get_cell_value(1, 1)
            if mat_tags_value is not None and isinstance(mat_tags_value, list):
                params['MatTags'] = mat_tags_value
                
            factors_value = nested_table.get_cell_value(2, 1)  
            if factors_value is not None and isinstance(factors_value, list):
                params['-factors'] = factors_value
        
        return params
