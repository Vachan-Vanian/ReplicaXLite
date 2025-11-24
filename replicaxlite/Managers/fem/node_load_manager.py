from PySide6.QtWidgets import QVBoxLayout
from ...UtilityCode.TableGUI import ReplicaXTable


class ReplicaXFemNodeLoadManager:
    """
    Manager for the Node Force table in ReplicaXLite.
    
    Creates and manages a ReplicaXTable with columns:
    - Tag (int)
    - Pattern (int) 
    - FX (float) 
    - FY (float)
    - FZ (float)
    - MX (float)
    - MY (float)
    - MZ (float)
    - Comment (str)
    """
    
    def __init__(self, loads_tab_widget, settings, nodes_table, patterns_table):
        """
        Initialize the force manager.
        
        Args:
            force_tab_widget: The QWidget container for the force tab
        """
        self.loads_tab_widget = loads_tab_widget
        self.settings = settings
        self.nodes_table = nodes_table
        self.patterns_table = patterns_table

        layout = QVBoxLayout(self.loads_tab_widget)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)
        
        # Create the force table with initial rows (keeping same structure)
        self.table = self.loads_table = ReplicaXTable(rows=0, columns=9, settings=self.settings)
        
        # Set headers - adding Pattern column after Tag
        self.loads_table.set_column_types(['int', 'int', 'float', 'float', 'float', 'float', 'float', 'float', 'str'])
        self.loads_table.set_column_unit(2, 'Concentrated_Force')  # FX column
        self.loads_table.set_column_unit(3, 'Concentrated_Force')  # FY column  
        self.loads_table.set_column_unit(4, 'Concentrated_Force')  # FZ column
        self.loads_table.set_column_unit(5, 'Moment')  # MX column
        self.loads_table.set_column_unit(6, 'Moment')  # MY column
        self.loads_table.set_column_unit(7, 'Moment')  # MZ column
        
        # Set dropdown 
        self.loads_table.set_dropdown(0, [])  # Tag column
        self.loads_table.set_dropdown(1, [])  # Pattern column
        
        self.loads_table.set_headers(['Tag', 'Pattern', 'FX', 'FY', 'FZ', 'MX', 'MY', 'MZ', 'Comment'])

        # Link node tag dropdown to available nodes
        self.loads_table.link_dropdown_to_column(
            dropdown_col=0,
            source_table=self.nodes_table,
            source_col=0,
            include_empty=True
        )

        self.loads_table.link_dropdown_to_column(
            dropdown_col=1,
            source_table=self.patterns_table, 
            source_col=0,
            include_empty=True
        )

        # Initialize table cells (this will sync dropdowns)
        self.loads_table.init_table_cells()

        layout.addWidget(self.loads_table)

    def create_fem_table_code(self, model):
        """
        Create all node loads from the GUI table.
        
        Args:
            model: StructuralModel instance
        Returns:
            None
        """
        rows = self.loads_table.rowCount()
        
        for i in range(rows):
            try:
                self.create_fem_table_row_code(model, i)
            except Exception as e:
                print(f"Node Load FEM Table: Error processing row {i}: {e}")
                continue

    def create_fem_table_row_code(self, model, row_index):
        """
        Build a single node load from GUI data at specified row index.
        
        Args:
            model: StructuralModel instance
            row_index: Index of the row to process
        Returns:
            True else False
        """
        # Get basic info - note that we don't extract node_tag because it's handled by dropdown in column 0
        tag = self.loads_table.get_cell_value(row_index, 0)       # Tag column 
        pattern_tag = self.loads_table.get_cell_value(row_index, 1)   # pattern_tag column  
        fx = self.loads_table.get_cell_value(row_index, 2)      # FX column
        fy = self.loads_table.get_cell_value(row_index, 3)      # FY column
        fz = self.loads_table.get_cell_value(row_index, 4)      # FZ column
        mx = self.loads_table.get_cell_value(row_index, 5)      # MX column
        my = self.loads_table.get_cell_value(row_index, 6)      # MY column
        mz = self.loads_table.get_cell_value(row_index, 7)      # MZ column

        if not tag:
            return False
            
        if not pattern_tag:
            return False

        # Handle case where some load values might be None or empty
        # Default to 0.0 for missing values (as per typical structural modeling)
        fx = fx if fx is not None else 0.0
        fy = fy if fy is not None else 0.0
        fz = fz if fz is not None else 0.0
        mx = mx if mx is not None else 0.0
        my = my if my is not None else 0.0
        mz = mz if mz is not None else 0.0

        try:
            # Access existing node and add load directly to it 
            # (node tag will be obtained from the dropdown in column 0)
            node_tag = self.loads_table.get_cell_value(row_index, 0)  # This was originally the Node Tag
            model.loading.load_patterns[pattern_tag].add_node_load(node_tag, fx, fy, fz, mx, my, mz)
            # model.loading.
            return True
            
        except Exception as e:
            print(f"Error building load for node {node_tag} from row {row_index}: {e}")
            return False

