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


from PySide6 import QtWidgets, QtCore, QtGui
import json
import os
from ..UtilityAPI.DataValidationAPI import ReplicaXDataTypesManager
from ..UtilityAPI.UnitsAPI import ReplicaXUnits
from ..config import INFO

# ============================================================================
# Large cell data manage
# ============================================================================

class LargeTextEditorDialog(QtWidgets.QDialog):
    """
    Full-screen editor dialog for large text data.
    Handles millions of characters without truncation.
    """
    
    def __init__(self, initial_text, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Edit Large Data")
        self.resize(1000, 700)
        
        layout = QtWidgets.QVBoxLayout(self)
        
        # Info bar
        self.info_label = QtWidgets.QLabel()
        self.update_info(len(initial_text))
        layout.addWidget(self.info_label)
        
        # Text editor
        self.editor = QtWidgets.QPlainTextEdit()
        self.editor.setPlainText(initial_text)
        self.editor.setFont(QtGui.QFont("Courier", 10))
        self.editor.textChanged.connect(self.on_text_changed)
        layout.addWidget(self.editor)
        
        # Buttons
        btn_layout = QtWidgets.QHBoxLayout()
        btn_layout.addStretch()
        
        self.btn_save = QtWidgets.QPushButton("💾 Save")
        self.btn_save.clicked.connect(self.accept)
        self.btn_save.setDefault(True)
        btn_layout.addWidget(self.btn_save)
        
        btn_cancel = QtWidgets.QPushButton("Cancel")
        btn_cancel.clicked.connect(self.reject)
        btn_layout.addWidget(btn_cancel)
        
        layout.addLayout(btn_layout)
    
    def update_info(self, char_count):
        """Update character count display."""
        self.info_label.setText(
            f"📝 <b>Character Count:</b> {char_count:,} | "
            f"Lines: {self.editor.document().lineCount():,}" if hasattr(self, 'editor') else ""
        )
    
    def on_text_changed(self):
        """Update info when text changes."""
        text = self.editor.toPlainText()
        self.update_info(len(text))
    
    def get_text(self):
        """Get edited text."""
        return self.editor.toPlainText()


class LargeDataDelegate(QtWidgets.QStyledItemDelegate):
    """
    Custom delegate that detects large data and opens a proper editor.
    
    - Small data (< 1000 chars): Use default inline QLineEdit
    - Large data (>= 1000 chars): Open full dialog editor
    """
    
    def __init__(self, parent=None, size_threshold=1000):
        super().__init__(parent)
        self.size_threshold = size_threshold
    
    def createEditor(self, parent, option, index):
        """
        Create appropriate editor based on data size.
        Opens dialog for large data to avoid QLineEdit display limits.
        """
        # Get data from model
        data = index.model().data(index, QtCore.Qt.EditRole)
        
        if data and isinstance(data, str) and len(data) >= self.size_threshold:
            # Large data - open dialog editor
            dialog = LargeTextEditorDialog(data, parent.window())
            
            if dialog.exec() == QtWidgets.QDialog.Accepted:
                # Save immediately
                new_text = dialog.get_text()
                index.model().setData(index, new_text, QtCore.Qt.EditRole)
            
            # Return None to prevent default editor
            return None
        
        else:
            # Small data - use default inline editor
            return super().createEditor(parent, option, index)
    
    def setEditorData(self, editor, index):
        """Load data into inline editor (only for small data)."""
        if editor:
            super().setEditorData(editor, index)
    
    def setModelData(self, editor, model, index):
        """Save data from inline editor (only for small data)."""
        if editor:
            super().setModelData(editor, model, index)

# ============================================================================
# Multi-Select Dropdown Widget
# ============================================================================

class _MultiSelectDropdown(QtWidgets.QPushButton):
    """
    Custom widget for multi-select dropdown.
    Displays as button showing selected count, opens dialog with checkboxes.
    """
    
    selectionChanged = QtCore.Signal()
    
    def __init__(self, options, parent=None):
        super().__init__(parent)
        self.options = options
        self.selected = []
        self.setFocusPolicy(QtCore.Qt.StrongFocus)
        self._update_display()
        self.clicked.connect(self._show_selection_dialog)
    
    def set_options(self, options):
        """Update available options."""
        self.options = options
        # Remove selected items that are no longer in options
        self.selected = [s for s in self.selected if s in options]
        self._update_display()
    
    def get_selected(self):
        """Get list of selected items."""
        return self.selected.copy()
    
    def set_selected(self, selected):
        """Set selected items."""
        if selected is None:
            self.selected = []
        elif isinstance(selected, (list, tuple)):
            self.selected = [str(s) for s in selected if str(s) in self.options]
        else:
            # Single value - convert to list
            if str(selected) in self.options:
                self.selected = [str(selected)]
            else:
                self.selected = []
        self._update_display()
    
    def _update_display(self):
        """Update button text to show selection count."""
        count = len(self.selected)
        if count == 0:
            self.setText("Select...")
        elif count == 1:
            self.setText(f"✓ {self.selected[0]}")
        else:
            self.setText(f"✓ {count} selected")
    
    def _show_selection_dialog(self):
        """Show dialog with checkboxes for selection."""
        dialog = QtWidgets.QDialog(self)
        dialog.setWindowTitle("Select Items")
        dialog.resize(300, 400)
        
        layout = QtWidgets.QVBoxLayout(dialog)
        
        # Search box
        search_box = QtWidgets.QLineEdit()
        search_box.setPlaceholderText("Search...")
        layout.addWidget(search_box)
        
        # List widget with checkboxes
        list_widget = QtWidgets.QListWidget()
        list_widget.setSelectionMode(QtWidgets.QAbstractItemView.NoSelection)
        layout.addWidget(list_widget)
        
        # Populate list
        checkboxes = {}
        for option in self.options:
            option_str = str(option)
            if not option_str.strip():
                continue
            item = QtWidgets.QListWidgetItem(list_widget)
            checkbox = QtWidgets.QCheckBox(str(option))
            checkbox.setChecked(str(option) in self.selected)
            checkboxes[str(option)] = checkbox
            list_widget.setItemWidget(item, checkbox)
        
        # Search functionality
        def filter_items():
            search_text = search_box.text().lower()
            for i in range(list_widget.count()):
                item = list_widget.item(i)
                widget = list_widget.itemWidget(item)
                if widget:
                    visible = search_text in widget.text().lower()
                    item.setHidden(not visible)
        
        search_box.textChanged.connect(filter_items)
        
        # Buttons
        button_layout = QtWidgets.QHBoxLayout()
        
        btn_select_all = QtWidgets.QPushButton("Select All")
        btn_clear = QtWidgets.QPushButton("Clear All")
        btn_ok = QtWidgets.QPushButton("OK")
        btn_cancel = QtWidgets.QPushButton("Cancel")
        
        button_layout.addWidget(btn_select_all)
        button_layout.addWidget(btn_clear)
        button_layout.addStretch()
        button_layout.addWidget(btn_ok)
        button_layout.addWidget(btn_cancel)
        
        layout.addLayout(button_layout)
        
        # Button actions
        def select_all():
            for checkbox in checkboxes.values():
                if not list_widget.itemWidget(list_widget.item(list(checkboxes.values()).index(checkbox))).isHidden():
                    checkbox.setChecked(True)
        
        def clear_all():
            for checkbox in checkboxes.values():
                checkbox.setChecked(False)
        
        btn_select_all.clicked.connect(select_all)
        btn_clear.clicked.connect(clear_all)
        btn_ok.clicked.connect(dialog.accept)
        btn_cancel.clicked.connect(dialog.reject)
        
        # Execute dialog
        if dialog.exec() == QtWidgets.QDialog.Accepted:
            # Update selection
            old_selection = self.selected.copy()
            self.selected = [opt for opt, cb in checkboxes.items() if cb.isChecked()]
            self._update_display()
            
            # Emit signal if selection changed
            if self.selected != old_selection:
                self.selectionChanged.emit()


class ReplicaXTable(QtWidgets.QTableWidget):
    """
    ReplicaXTable 1.0.0 - Advanced table with unit conversion support.
    """
    
    def __init__(self, rows=5, columns=3, parent=None, settings=None):
        super().__init__(rows, columns, parent)
        
        # Core managers
        self.data_manager = ReplicaXDataTypesManager()
        self.units_converter = ReplicaXUnits()
        
        # Settings integration
        self.settings = settings
        
        # Existing attributes
        self.column_types = ['str'] * columns
        self.row_types = {}
        self.nested_tables = {}
        self.nested_table_dialogs = {}
        self.dropdown_options = {}
        self._copied_data = None
        self._validating = False
        
        # Multi-select dropdown tracking
        self.dropdown_multi_columns = set()  # Columns that are multi-select
        
        # Cell-level dropdown overrides
        self.cell_dropdowns = {}  # {(row, col): {'options': [...], 'multi': False}}
        
        # Dropdown linking features
        self._dropdown_table_links = {}
        self._dropdown_column_links = {}
        self._dropdown_cell_links = {}
        self._dropdown_dependent_tables = []
        
        # Unit conversion attributes
        self.column_units = {}  # {col: {'unit_type': 'Length', 'display_unit': 'mm', 'base_unit': 'm'}}
        self.row_units = {}     # {row: {col: {...}}} - row-level unit overrides
        self.cell_units = {}    # {(row, col): {...}} - cell-level unit overrides
        self._unit_display_mode = 'suffix'  # 'suffix', 'header', or 'none'
        
        # UI setup
        self.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)

        # Install custom delegate for large data
        self.setItemDelegate(LargeDataDelegate(size_threshold=32767))
        
        # Shortcuts
        shortcuts = [
            ("Ctrl++", self.add_row),
            ("Ctrl+Shift++", self.import_rows),
            ("Ctrl+-", self.remove_row),
            ("Ctrl+Shift+-", self.remove_selected_rows),
            ("Ctrl+C", self.copy_selection),
            ("Ctrl+V", self.paste_selection),
            ("Delete", self.clear_selection)
        ]
        for key, func in shortcuts:
            QtGui.QShortcut(QtGui.QKeySequence(key), self, func, context=QtCore.Qt.WidgetShortcut)
        
        # Signals
        self.cellDoubleClicked.connect(self._handle_double_click)
        self.cellChanged.connect(self._handle_cell_edit)
        
        # Track if we're internally updating to prevent recursion
        self._internal_update = False
    
    # ============================================================================
    # UNIT CONVERSION SYSTEM
    # ============================================================================
    
    def set_column_unit(self, col, unit_type, display_unit=None):
        """Configure automatic unit conversion for a column."""
        if col < 0 or col >= self.columnCount():
            raise ValueError(f"Column {col} out of range")
        
        if unit_type not in self.units_converter.units:
            raise ValueError(f"Unknown unit type: {unit_type}")
        
        # Get display unit from settings if not provided
        if display_unit is None and self.settings:
            unit_system = self.settings.get('unit_system', {}).get('new_unit_system', 'SI_m_kg_s')
            unit_systems = self.settings.get('unit_system', {}).get('_unit_systems', {})
            if unit_system in unit_systems:
                display_unit = unit_systems[unit_system].get(unit_type)
        
        # Fallback to first available unit
        if display_unit is None:
            display_unit = list(self.units_converter.units[unit_type].keys())[0]
        
        if display_unit not in self.units_converter.units[unit_type]:
            raise ValueError(f"Unknown unit: {display_unit} for type {unit_type}")
        
        # Determine base unit
        base_unit = self._get_base_unit(unit_type)
        
        self.column_units[col] = {
            'unit_type': unit_type,
            'display_unit': display_unit,
            'base_unit': base_unit
        }
        
        # Update header to show unit if in header mode
        if self._unit_display_mode == 'header':
            header_item = self.horizontalHeaderItem(col)
            if header_item:
                text = header_item.text()
                if '(' in text and ')' in text:
                    text = text[:text.index('(')].strip()
                header_item.setText(f"{text} ({display_unit})")
        
        return self
    
    def set_row_units(self, row, units_dict):
        """Override unit configuration for specific columns in a row."""
        if row < 0 or row >= self.rowCount():
            raise ValueError(f"Row {row} out of range [0, {self.rowCount()-1}]")
        
        if row not in self.row_units:
            self.row_units[row] = {}
        
        for col, unit_spec in units_dict.items():
            if col < 0 or col >= self.columnCount():
                raise ValueError(f"Column {col} out of range")
            
            # Parse unit specification
            if isinstance(unit_spec, tuple):
                unit_type = unit_spec[0]
                display_unit = unit_spec[1] if len(unit_spec) > 1 else None
            else:
                raise ValueError("Unit spec must be tuple: (unit_type,) or (unit_type, display_unit)")
            
            if unit_type not in self.units_converter.units:
                raise ValueError(f"Unknown unit type: {unit_type}")
            
            # Get display unit from settings if not provided
            if display_unit is None and self.settings:
                unit_system = self.settings.get('unit_system', {}).get('new_unit_system', 'SI_m_kg_s')
                unit_systems = self.settings.get('unit_system', {}).get('_unit_systems', {})
                if unit_system in unit_systems:
                    display_unit = unit_systems[unit_system].get(unit_type)
            
            # Fallback to first available unit
            if display_unit is None:
                display_unit = list(self.units_converter.units[unit_type].keys())[0]
            
            if display_unit not in self.units_converter.units[unit_type]:
                raise ValueError(f"Unknown unit: {display_unit} for type {unit_type}")
            
            base_unit = self._get_base_unit(unit_type)
            
            self.row_units[row][col] = {
                'unit_type': unit_type,
                'display_unit': display_unit,
                'base_unit': base_unit
            }
        
        return self
    
    def set_cell_unit(self, row, col, unit_type, display_unit=None):
        """Override unit configuration for a specific cell."""
        if row < 0 or row >= self.rowCount():
            raise ValueError(f"Row {row} out of range [0, {self.rowCount()-1}]")
        if col < 0 or col >= self.columnCount():
            raise ValueError(f"Column {col} out of range")
        
        if unit_type not in self.units_converter.units:
            raise ValueError(f"Unknown unit type: {unit_type}")
        
        # Get display unit from settings if not provided
        if display_unit is None and self.settings:
            unit_system = self.settings.get('unit_system', {}).get('new_unit_system', 'SI_m_kg_s')
            unit_systems = self.settings.get('unit_system', {}).get('_unit_systems', {})
            if unit_system in unit_systems:
                display_unit = unit_systems[unit_system].get(unit_type)
        
        # Fallback to first available unit
        if display_unit is None:
            display_unit = list(self.units_converter.units[unit_type].keys())[0]
        
        if display_unit not in self.units_converter.units[unit_type]:
            raise ValueError(f"Unknown unit: {display_unit} for type {unit_type}")
        
        base_unit = self._get_base_unit(unit_type)
        
        self.cell_units[(row, col)] = {
            'unit_type': unit_type,
            'display_unit': display_unit,
            'base_unit': base_unit
        }
        
        return self
    
    def clear_row_units(self, row=None):
        """Clear row unit overrides."""
        if row is None:
            self.row_units.clear()
        elif row in self.row_units:
            del self.row_units[row]
        return self
    
    def clear_cell_unit(self, row=None, col=None):
        """Clear cell unit overrides."""
        if row is None and col is None:
            self.cell_units.clear()
        elif row is not None and col is not None:
            key = (row, col)
            if key in self.cell_units:
                del self.cell_units[key]
        return self
    
    def _get_cell_unit_config(self, row, col):
        """Get effective unit config with priority: cell → row → column → None."""
        # Priority 1: Cell-level override
        if (row, col) in self.cell_units:
            return self.cell_units[(row, col)]
        
        # Priority 2: Row-level override
        if row in self.row_units and col in self.row_units[row]:
            return self.row_units[row][col]
        
        # Priority 3: Column-level default
        if col in self.column_units:
            return self.column_units[col]
        
        return None
    
    def _get_base_unit(self, unit_type):
        """Get the base unit for a unit type (conversion factor = 1)."""
        units_dict = self.units_converter.units[unit_type]
        for unit, factor in units_dict.items():
            if factor == 1:
                return unit
        return list(units_dict.keys())[0]
    
    def set_unit_display_mode(self, mode):
        """Set how units are displayed: 'suffix' (default), 'header', or 'none'."""
        if mode not in ['suffix', 'header', 'none']:
            raise ValueError("Mode must be 'suffix', 'header', or 'none'")
        self._unit_display_mode = mode
        return self
    
    def change_column_display_unit(self, col, new_display_unit, recursive=True):
        """
        Change the display unit for a column (updates all visible values).
        
        Args:
            col: Column index
            new_display_unit: New unit to display
            recursive: If True (default), also update nested tables
        """
        if col not in self.column_units:
            raise ValueError(f"Column {col} does not have units configured")
        
        unit_config = self.column_units[col]
        unit_type = unit_config['unit_type']
        
        if new_display_unit not in self.units_converter.units[unit_type]:
            raise ValueError(f"Unknown unit: {new_display_unit} for type {unit_type}")
        
        self.column_units[col]['display_unit'] = new_display_unit
        
        self.blockSignals(True)
        for row in range(self.rowCount()):
            if (row, col) in self.cell_units or (row in self.row_units and col in self.row_units[row]):
                continue
            
            value = self._get_cell_value_internal_use(row, col)
            self._update_cell_display(row, col, value)
        self.blockSignals(False)
        
        # Recursively update nested tables
        if recursive:
            for (row, col_nested), nested_table in self.nested_tables.items():
                if isinstance(nested_table, ReplicaXTable):
                    # Check if nested table has the same column and unit type
                    if col < nested_table.columnCount() and col in nested_table.column_units:
                        if nested_table.column_units[col]['unit_type'] == unit_type:
                            nested_table.change_column_display_unit(col, new_display_unit, recursive=True)
        
        return self
    
    def sync_units_from_settings(self, update_overrides=True, recursive=True):
        """
        Update all display units from current settings.
        
        Args:
            update_overrides: If True, also update row/cell unit overrides
            recursive: If True (default), also sync all nested tables
        """
        if not self.settings:
            return self
        
        unit_system = self.settings.get('unit_system', {}).get('new_unit_system', 'SI_m_kg_s')
        unit_systems = self.settings.get('unit_system', {}).get('_unit_systems', {})
        
        if unit_system not in unit_systems:
            return self
        
        system_units = unit_systems[unit_system]
        
        # Update column units
        for col, config in self.column_units.items():
            unit_type = config['unit_type']
            if unit_type in system_units:
                new_display_unit = system_units[unit_type]
                if new_display_unit in self.units_converter.units[unit_type]:
                    config['display_unit'] = new_display_unit
        
        # Optionally update row overrides
        if update_overrides:
            for row, units_dict in self.row_units.items():
                for col, config in units_dict.items():
                    unit_type = config['unit_type']
                    if unit_type in system_units:
                        new_display_unit = system_units[unit_type]
                        if new_display_unit in self.units_converter.units[unit_type]:
                            config['display_unit'] = new_display_unit
            
            for (row, col), config in self.cell_units.items():
                unit_type = config['unit_type']
                if unit_type in system_units:
                    new_display_unit = system_units[unit_type]
                    if new_display_unit in self.units_converter.units[unit_type]:
                        config['display_unit'] = new_display_unit
        
        # Refresh displays
        self.refresh_all_displays(recursive=recursive)
        
        # Recursively sync nested tables
        if recursive:
            for (row, col), nested_table in self.nested_tables.items():
                if isinstance(nested_table, ReplicaXTable):
                    nested_table.sync_units_from_settings(update_overrides=update_overrides, recursive=True)
        
        return self
    
    def refresh_all_displays(self, recursive=True):
        """
        Refresh all cell displays with current unit configuration.
        
        Args:
            recursive: If True (default), also refresh all nested tables
        """
        self.blockSignals(True)
        for row in range(self.rowCount()):
            for col in range(self.columnCount()):
                if col in self.dropdown_options or self._get_cell_type(row, col) == 'table':
                    continue
                
                unit_config = self._get_cell_unit_config(row, col)
                if unit_config is not None:
                    value = self._get_cell_value_internal_use(row, col, in_display_units=False)
                    if value is not None:
                        self._update_cell_display(row, col, value)
        self.blockSignals(False)
        
        # Recursively refresh nested tables
        if recursive:
            for (row, col), nested_table in self.nested_tables.items():
                if isinstance(nested_table, ReplicaXTable):
                    nested_table.refresh_all_displays(recursive=True)
        
        return self
    
    def _is_numeric_type(self, cell_type):
        """Check if cell type is numeric and can have unit conversion."""
        numeric_types = ['int', 'float', 'list(int)', 'list(float)']
        return cell_type in numeric_types
    
    def _convert_to_base_unit(self, value, row, col):
        """
        Convert value(s) from display unit to base unit.
        ALL conversions use data_manager for type preservation.
        Only applies to numeric types: int, float, list(int), list(float)
        """
        unit_config = self._get_cell_unit_config(row, col)
        if unit_config is None:
            return value
        
        if value is None:
            return None
        
        # Only apply unit conversion to numeric types
        cell_type = self._get_cell_type(row, col)
        if not self._is_numeric_type(cell_type):
            return value
        
        return self._recursive_convert(value, row, col, to_base=True)
    
    def _convert_from_base_unit(self, value, row, col):
        """
        Convert value(s) from base unit to display unit.
        ALL conversions use data_manager for type preservation.
        Only applies to numeric types: int, float, list(int), list(float)
        """
        unit_config = self._get_cell_unit_config(row, col)
        if unit_config is None:
            return value
        
        if value is None:
            return None
        
        # Only apply unit conversion to numeric types
        cell_type = self._get_cell_type(row, col)
        if not self._is_numeric_type(cell_type):
            return value
        
        return self._recursive_convert(value, row, col, to_base=False)
    
    def _recursive_convert(self, value, row, col, to_base=True):
        """
        Recursively convert numeric values using data_manager for type safety.
        Handles lists and preserves int vs float distinction.
        """
        unit_config = self._get_cell_unit_config(row, col)
        cell_type = self._get_cell_type(row, col)
        
        if isinstance(value, (list, tuple)):
            converted = []
            for element in value:
                if isinstance(element, (int, float)):
                    # Perform unit conversion
                    from_unit = unit_config['display_unit'] if to_base else unit_config['base_unit']
                    to_unit = unit_config['base_unit'] if to_base else unit_config['display_unit']
                    
                    converted_value = self.units_converter.convert(
                        float(element),
                        unit_config['unit_type'],
                        from_unit,
                        to_unit
                    )
                    
                    # Use data_manager to ensure proper type
                    if 'int' in cell_type:
                        try:
                            converted.append(self.data_manager.load_data_type(str(int(round(converted_value))), 'int'))
                        except:
                            converted.append(int(round(converted_value)))
                    else:
                        try:
                            converted.append(self.data_manager.load_data_type(str(converted_value), 'float'))
                        except:
                            converted.append(converted_value)
                else:
                    converted.append(element)
            
            return type(value)(converted)
        elif isinstance(value, (int, float)):
            # Perform unit conversion
            from_unit = unit_config['display_unit'] if to_base else unit_config['base_unit']
            to_unit = unit_config['base_unit'] if to_base else unit_config['display_unit']
            
            converted_value = self.units_converter.convert(
                float(value),
                unit_config['unit_type'],
                from_unit,
                to_unit
            )
            
            # Use data_manager to ensure proper type
            if 'int' in cell_type:
                try:
                    return self.data_manager.load_data_type(str(int(round(converted_value))), 'int')
                except:
                    return int(round(converted_value))
            else:
                try:
                    return self.data_manager.load_data_type(str(converted_value), 'float')
                except:
                    return converted_value
        else:
            return value
    
    def _parse_value_with_unit(self, text, row, col):
        """
        Parse user input using data_manager exclusively.
        Handles "100 mm", "100mm", or "100" formats.
        Also handles lists: "[1500, 2000, 500] mm"
        Only applies to numeric types: int, float, list(int), list(float)
        """
        unit_config = self._get_cell_unit_config(row, col)
        if unit_config is None:
            return text
        
        cell_type = self._get_cell_type(row, col)
        
        # Only apply unit parsing to numeric types
        if not self._is_numeric_type(cell_type):
            return text
        
        text_str = self.data_manager.load_data_type(str(text).strip(), 'str')
        if not text_str:
            return None
        
        unit_type = unit_config['unit_type']
        available_units = self.units_converter.units[unit_type]
        
        # Check if this is a list type
        is_list = cell_type.startswith('list(')
        
        # Try to extract unit from text
        value_without_unit = None
        found_unit = None
        
        for unit_str in sorted(available_units.keys(), key=len, reverse=True):
            for pattern in [f" {unit_str}", unit_str]:
                if text_str.endswith(pattern):
                    value_without_unit = text_str[:-len(pattern)].strip()
                    found_unit = unit_str
                    break
            if found_unit is not None:
                break
        
        # No unit found, assume display unit
        if found_unit is None:
            value_without_unit = text_str
            found_unit = unit_config['display_unit']
        
        # Parse the value using data_manager
        try:
            parsed_value = self.data_manager.load_data_type(value_without_unit, cell_type)
        except:
            return text_str
        
        # Convert to base unit using units_converter
        if is_list:
            # Handle list conversion recursively
            converted_list = []
            for element in parsed_value:
                if isinstance(element, (int, float)):
                    converted_element = self.units_converter.convert(
                        float(element),
                        unit_type,
                        found_unit,
                        unit_config['base_unit']
                    )
                    # Preserve type using data_manager
                    if 'int' in cell_type:
                        try:
                            converted_list.append(self.data_manager.load_data_type(str(int(round(converted_element))), 'int'))
                        except:
                            converted_list.append(int(round(converted_element)))
                    else:
                        try:
                            converted_list.append(self.data_manager.load_data_type(str(converted_element), 'float'))
                        except:
                            converted_list.append(converted_element)
                else:
                    converted_list.append(element)
            
            return converted_list
        else:
            # Handle scalar conversion
            if isinstance(parsed_value, (int, float)):
                converted = self.units_converter.convert(
                    float(parsed_value),
                    unit_type,
                    found_unit,
                    unit_config['base_unit']
                )
                
                # Return in proper type using data_manager
                if 'int' in cell_type:
                    try:
                        return self.data_manager.load_data_type(str(int(round(converted))), 'int')
                    except:
                        return int(round(converted))
                else:
                    try:
                        return self.data_manager.load_data_type(str(converted), 'float')
                    except:
                        return converted
            else:
                return parsed_value
    
    def _format_display_value(self, value, row, col):
        """
        Format value for display using data_manager.
        Only adds units to numeric types: int, float, list(int), list(float)
        """
        unit_config = self._get_cell_unit_config(row, col)
        cell_type = self._get_cell_type(row, col)
        
        # Only add unit display for numeric types
        if not self._is_numeric_type(cell_type):
            unit_config = None
        
        if unit_config is None or self._unit_display_mode == 'none':
            if value is None:
                return ""
            try:
                return self.data_manager.save_data_type_as_string(value, cell_type)
            except:
                return str(value)
        
        display_unit = unit_config['display_unit']
        
        if isinstance(value, (list, tuple)):
            # Format list elements WITHOUT individual units
            formatted = []
            for v in value:
                if isinstance(v, (int, float)):
                    try:
                        if isinstance(v, int):
                            v_str = self.data_manager.save_data_type_as_string(v, 'int')
                        else:
                            v_str = self.data_manager.save_data_type_as_string(v, 'float')
                    except:
                        v_str = str(v)
                else:
                    v_str = str(v)
                formatted.append(v_str)
            
            # Add unit to the whole list, not individual elements
            if self._unit_display_mode == 'suffix':
                return f"[{', '.join(formatted)}] {display_unit}"
            else:
                return f"[{', '.join(formatted)}]"
        elif isinstance(value, (int, float)):
            try:
                if isinstance(value, int):
                    v_str = self.data_manager.save_data_type_as_string(value, 'int')
                else:
                    v_str = self.data_manager.save_data_type_as_string(value, 'float')
            except:
                v_str = str(value)
            
            if self._unit_display_mode == 'suffix':
                return f"{v_str} {display_unit}"
            else:
                return v_str
        else:
            if value is None:
                return ""
            try:
                return self.data_manager.save_data_type_as_string(value, cell_type)
            except:
                return str(value)
    
    def _update_cell_display(self, row, col, base_value):
        """Update cell display with converted value using data_manager."""
        if col in self.dropdown_options or self._get_cell_type(row, col) == 'table':
            return
        
        # Convert to display unit
        display_value = self._convert_from_base_unit(base_value, row, col)
        
        # Format with unit
        display_text = self._format_display_value(display_value, row, col)
        
        # Update cell
        item = self.item(row, col)
        if not item:
            item = QtWidgets.QTableWidgetItem()
            self.setItem(row, col, item)
        item.setText(display_text)
    
    # ============================================================================
    # TYPE SYSTEM
    # ============================================================================
    
    def set_column_types(self, types):
        """Set default types for all columns."""
        if len(types) != self.columnCount():
            raise ValueError(f"Expected {self.columnCount()} types, got {len(types)}")
        self.column_types = types
        return self
    
    def set_row_types(self, row, types):
        """Override types for a specific row."""
        if row < 0 or row >= self.rowCount():
            raise ValueError(f"Row {row} out of range [0, {self.rowCount()-1}]")
        if len(types) != self.columnCount():
            raise ValueError(f"Expected {self.columnCount()} types, got {len(types)}")
        self.row_types[row] = types
        return self
    
    def clear_row_types(self, row=None):
        """Clear row type overrides."""
        if row is None:
            self.row_types.clear()
        elif row in self.row_types:
            del self.row_types[row]
        return self
    
    def _is_multi_select_dropdown(self, row, col):
        """
        Check if a cell is a multi-select dropdown.
        Checks both column-level and cell-level configuration.
        
        Returns:
            bool: True if multi-select, False otherwise
        """
        # Check cell-level override first
        if (row, col) in self.cell_dropdowns:
            return self.cell_dropdowns[(row, col)]['multi']
        
        # Check column-level
        if col in self.dropdown_options:
            return col in self.dropdown_multi_columns
        
        return False

    def _get_cell_type(self, row, col, dropdown_true_type=False):
        """
        Get effective type with dropdown awareness.
        
        Args:
            dropdown_true_type: If True, return the column/row type even for dropdowns
                        (useful for converting dropdown strings to other types)
        
        Priority (when dropdown_true_type=False):
        1. Multi-select dropdown → 'list(str)'
        2. Single-select dropdown → 'str'
        3. Row type override
        4. Column default type
        
        Priority (when dropdown_true_type=True):
        1. Row type override
        2. Column default type
        (ignores dropdown awareness - returns the true underlying type)
        """
        if not dropdown_true_type:
            # Check if it's a dropdown first
            dropdown_config = self._get_cell_dropdown_config(row, col)
            if dropdown_config is not None:
                # It's a dropdown - type depends on multi-select
                if dropdown_config['multi']:
                    return 'list(str)'
                else:
                    return 'str'
        
        # Not a dropdown OR dropdown_true_type=True - use original logic
        if row in self.row_types:
            return self.row_types[row][col]
        return self.column_types[col]
    
    # ============================================================================
    # CONFIGURATION
    # ============================================================================
    
    def set_headers(self, headers):
        """Set column headers."""
        if len(headers) != self.columnCount():
            raise ValueError(f"Expected {self.columnCount()} headers, got {len(headers)}")
        for i, h in enumerate(headers):
            self.setHorizontalHeaderItem(i, QtWidgets.QTableWidgetItem(h))
        return self
    
    def set_dropdown(self, col, options, update_existing=True, multi=False):
        """
        Configure a column as dropdown with given options.
        
        Args:
            col: Column index
            options: List of options
            update_existing: Update existing cells
            multi: If True, allows multiple selection (dropdown_multi type)
        
        Example:
            # Single-select dropdown
            table.set_dropdown(1, ['Option A', 'Option B', 'Option C'])
            
            # Multi-select dropdown
            table.set_dropdown(2, ['Tag1', 'Tag2', 'Tag3'], multi=True)
        """
        if col < 0 or col >= self.columnCount():
            raise ValueError(f"Column {col} out of range")
        
        self.dropdown_options[col] = options
        
        # Track multi-select columns
        if multi:
            self.dropdown_multi_columns.add(col)
        else:
            self.dropdown_multi_columns.discard(col)
        
        if update_existing:
            for row in range(self.rowCount()):
                # Skip cells with cell-level dropdown override
                if (row, col) in self.cell_dropdowns:
                    continue
                
                widget = self.cellWidget(row, col)
                
                if multi:
                    # Update multi-select widget
                    if isinstance(widget, _MultiSelectDropdown):
                        current = widget.get_selected()
                        widget.set_options([str(opt) for opt in options])
                        widget.set_selected(current)
                else:
                    # Update single-select widget
                    if isinstance(widget, QtWidgets.QComboBox):
                        current = widget.currentText()
                        widget.blockSignals(True)
                        widget.clear()
                        widget.addItems([str(opt) for opt in options])
                        idx = widget.findText(current)
                        widget.setCurrentIndex(max(0, idx))
                        widget.blockSignals(False)
        
        return self
    

    def set_cell_dropdown(self, row, col, options, multi=False, update_existing=True):
        """
        Configure a specific cell as dropdown (overrides column dropdown).
        
        Args:
            row: Row index
            col: Column index
            options: List of options for this specific cell
            multi: If True, allows multiple selection
            update_existing: If True, update existing widget; if False, recreate
        """
        if row < 0 or row >= self.rowCount():
            raise ValueError(f"Row {row} out of range")
        if col < 0 or col >= self.columnCount():
            raise ValueError(f"Column {col} out of range")
        
        # Store cell-level config
        self.cell_dropdowns[(row, col)] = {
            'options': options,
            'multi': multi
        }
        
        # Get existing widget
        widget = self.cellWidget(row, col)
        
        # update logic (matching set_dropdown)
        if update_existing and widget is not None:
            # Check if widget type matches
            widget_is_multi = isinstance(widget, _MultiSelectDropdown)
            widget_is_single = isinstance(widget, QtWidgets.QComboBox)
            
            if multi and widget_is_multi:
                # Update multi-select widget (preserve selection)
                current = widget.get_selected()
                widget.set_options([str(opt) for opt in options])
                widget.set_selected(current)
            
            elif not multi and widget_is_single:
                # Update single-select widget (preserve selection)
                current = widget.currentText()
                widget.blockSignals(True)
                widget.clear()
                widget.addItems([str(opt) for opt in options])
                idx = widget.findText(current)
                widget.setCurrentIndex(max(0, idx))
                widget.blockSignals(False)
            
            else:
                # Widget type changed (single ↔ multi) - must recreate
                self.removeCellWidget(row, col)
                self._add_widget(row, col, 'dropdown')
        
        else:
            # No existing widget OR update_existing=False - recreate
            if widget:
                self.removeCellWidget(row, col)
            self._add_widget(row, col, 'dropdown')
        
        return self
    
    def clear_cell_dropdown(self, row=None, col=None):
        """
        Clear cell-level dropdown override (reverts to column dropdown).
        
        Args:
            row, col: Specific cell to clear, or None for both to clear all
        """
        if row is None and col is None:
            self.cell_dropdowns.clear()
        elif row is not None and col is not None:
            key = (row, col)
            if key in self.cell_dropdowns:
                del self.cell_dropdowns[key]
                # Recreate widget with column config
                self._add_widget(row, col, 'dropdown')
        return self
    
    def _get_cell_dropdown_config(self, row, col):
        """
        Get effective dropdown config with priority: cell → column.
        
        Returns:
            Dict with 'options' and 'multi', or None if not a dropdown
        """
        # Priority 1: Cell-level override
        if (row, col) in self.cell_dropdowns:
            return self.cell_dropdowns[(row, col)]
        
        # Priority 2: Column-level default
        if col in self.dropdown_options:
            return {
                'options': self.dropdown_options[col],
                'multi': col in self.dropdown_multi_columns
            }
        
        return None
    
    def init_table_cells(self):
        """Initialize all special cell types and sync linked dropdowns.
        NEVER CALL THIS AFTER LOAD FROM FILE
        """
        for row in range(self.rowCount()):
            self._init_row(row)
        
        for dropdown_col in self._dropdown_column_links.keys():
            self._sync_dropdown_from_column(dropdown_col)
        
        for (row, col) in self._dropdown_cell_links.keys():
            self._sync_dropdown_from_cell(row, col)
        
        return self
    
    # ============================================================================
    # DROPDOWN LINKING
    # ============================================================================
    
    def link_dropdown_to_table(self, dropdown_col, table_col, templates):
        """
        Link dropdown selections to nested table templates.
        
        Args:
            dropdown_col: Dropdown column index
            table_col: Table column index
            templates: Dict mapping dropdown values to templates
                       Template can be:
                       - String path: 'path/to/template.json'
                       - JSON dict: {'rows': 5, 'columns': 3, ...}
                       - ReplicaXTable instance: existing_table
        
        Examples:
            # File paths
            table.link_dropdown_to_table(0, 1, {
                'TypeA': 'templates/typeA.json'
            })
            
            # JSON dicts
            table.link_dropdown_to_table(0, 1, {
                'TypeB': {'rows': 3, 'columns': 2, 'cells': [...]}
            })
            
            # ReplicaXTable instances
            template_table = ReplicaXTable(...)
            table.link_dropdown_to_table(0, 1, {
                'TypeC': template_table
            })
            
            # Mix all three!
            table.link_dropdown_to_table(0, 1, {
                'TypeA': 'path/to/typeA.json',
                'TypeB': {'rows': 3, ...},
                'TypeC': existing_table_instance
            })
        """
        if dropdown_col not in self.dropdown_options:
            raise ValueError(f"Column {dropdown_col} is not a dropdown column")
        
        if self.column_types[table_col] != 'table':
            raise ValueError(f"Column {table_col} must be type 'table'")
        
        # Validate templates
        for value, template in templates.items():
            if isinstance(template, str):
                # String path - validate file exists
                if not os.path.exists(template):
                    raise FileNotFoundError(f"Template file not found: {template}")
            elif isinstance(template, dict):
                # JSON dict - should have required keys
                if 'rows' not in template or 'columns' not in template:
                    raise ValueError(f"JSON template for '{value}' missing 'rows' or 'columns'")
            elif isinstance(template, ReplicaXTable):
                # ReplicaXTable instance - valid
                pass
            else:
                raise ValueError(
                    f"Template for '{value}' must be string path, JSON dict, or ReplicaXTable instance, "
                    f"got {type(template).__name__}"
                )
        
        self._dropdown_table_links[(dropdown_col, table_col)] = templates
        return self
    

    def _on_dropdown_template_changed(self, row, dropdown_col):
        """
        Internal: Handle dropdown change for template linking.
        Supports three template types: file path, JSON dict, ReplicaXTable instance.
        """
        dropdown_value = self._get_cell_value_internal_use(row, dropdown_col)
        
        # Handle both single and multi-select dropdowns
        # For multi-select, use first selected value for template
        if isinstance(dropdown_value, list):
            if len(dropdown_value) > 0:
                template_key = dropdown_value[0]
            else:
                return  # No selection, do nothing
        else:
            template_key = dropdown_value
        
        for (d_col, t_col), templates in self._dropdown_table_links.items():
            if d_col == dropdown_col and template_key in templates:
                template = templates[template_key]
                
                try:
                    new_table = ReplicaXTable(parent=None, settings=self.settings)
                    new_table.hide()
                    
                    # Handle three template types
                    if isinstance(template, str):
                        # Type 1: File path (existing behavior)
                        new_table.load_from_file(template)
                    
                    elif isinstance(template, dict):
                        # Type 2: JSON dict (new!)
                        new_table.from_json(json.dumps(template))
                    
                    elif isinstance(template, ReplicaXTable):
                        # Type 3: ReplicaXTable instance (new!)
                        # Clone the table by serializing and deserializing
                        json_str = template.to_json()
                        new_table.from_json(json_str)
                    
                    else:
                        raise ValueError(f"Unknown template type: {type(template).__name__}")
                    
                    # Re-establish dropdown links if original template had them
                    if isinstance(template, ReplicaXTable):
                        # Re-establish column-level dropdown links
                        if template._dropdown_column_links:
                            for col, link_info in template._dropdown_column_links.items():
                                if col < new_table.columnCount():
                                    new_table.link_dropdown_to_column(
                                        dropdown_col=col,
                                        source_table=link_info['source_table'],
                                        source_col=link_info['source_col'],
                                        auto_update=link_info['auto_update'],
                                        unique_only=link_info['unique_only'],
                                        skip_empty=link_info['skip_empty'],
                                        include_empty=link_info['include_empty']
                                    )
                        
                        # Re-establish cell-level dropdown links
                        if template._dropdown_cell_links:
                            for (tpl_row, tpl_col), link_info in template._dropdown_cell_links.items():
                                if tpl_row < new_table.rowCount() and tpl_col < new_table.columnCount():
                                    new_table.link_dropdown_to_cell(
                                        row=tpl_row,
                                        col=tpl_col,
                                        source_table=link_info['source_table'],
                                        source_col=link_info['source_col'],
                                        auto_update=link_info['auto_update'],
                                        unique_only=link_info['unique_only'],
                                        skip_empty=link_info['skip_empty'],
                                        include_empty=link_info['include_empty']
                                    )
                    
                    self.set_cell_value(row, t_col, new_table)
                    
                except Exception as e:
                    QtWidgets.QMessageBox.warning(
                        self, 
                        "Template Load Error",
                        f"Failed to load template for '{template_key}':\n{str(e)}"
                    )


    def link_dropdown_to_column(self, dropdown_col, source_table, source_col, 
                                 auto_update=True, unique_only=True, skip_empty=True, include_empty=False):
        """
        Link dropdown options to values from another table's column.
        
        Args:
            dropdown_col: Dropdown column index in this table
            source_table: Source ReplicaXTable instance
            source_col: Column index in source table
            auto_update: If True, sync when source changes
            unique_only: If True, only include unique values
            skip_empty: If True, skip empty values from source
            include_empty: If True, prepend '' option to synced values
        """
        if dropdown_col not in self.dropdown_options:
            raise ValueError(f"Column {dropdown_col} is not a dropdown column")
        
        if not isinstance(source_table, ReplicaXTable):
            raise ValueError("source_table must be a ReplicaXTable instance")
        
        if source_col < 0 or source_col >= source_table.columnCount():
            raise ValueError(f"source_col {source_col} out of range in source table")
        
        self._dropdown_column_links[dropdown_col] = {
            'source_table': source_table,
            'source_col': source_col,
            'auto_update': auto_update,
            'unique_only': unique_only,
            'skip_empty': skip_empty,
            'include_empty': include_empty
        }
        
        if auto_update:
            source_table.cellChanged.connect(
                lambda row, col: self._on_source_table_changed(dropdown_col, col)
            )
            source_table._dropdown_dependent_tables.append((self, dropdown_col))
      
        self._sync_dropdown_from_column(dropdown_col)
        return self
    
    def link_dropdown_to_cell(self, row, col, source_table, source_col,
                               auto_update=True, unique_only=True, skip_empty=True, include_empty=False):
        """
        Link a specific cell's dropdown options to values from another table's column.
        
        Args:
            row: Row index of the cell
            col: Column index of the cell
            source_table: Source ReplicaXTable instance
            source_col: Column index in source table
            auto_update: If True, sync when source changes
            unique_only: If True, only include unique values
            skip_empty: If True, skip empty values from source
            include_empty: If True, prepend '' option to synced values
        
        Example:
            # Cell [2, 1] dropdown syncs from nodes_table with empty option
            table.link_dropdown_to_cell(
                row=2,
                col=1,
                source_table=nodes_table,
                source_col=0,
                auto_update=True,
                include_empty=True  # Adds '' option at start
            )
        """
        if row < 0 or row >= self.rowCount():
            raise ValueError(f"Row {row} out of range")
        if col < 0 or col >= self.columnCount():
            raise ValueError(f"Column {col} out of range")
        
        # Cell must be a dropdown (either via column or cell-specific)
        dropdown_config = self._get_cell_dropdown_config(row, col)
        if dropdown_config is None:
            raise ValueError(f"Cell [{row}, {col}] is not a dropdown. Use set_dropdown() or set_cell_dropdown() first.")
        
        if not isinstance(source_table, ReplicaXTable):
            raise ValueError("source_table must be a ReplicaXTable instance")
        
        if source_col < 0 or source_col >= source_table.columnCount():
            raise ValueError(f"source_col {source_col} out of range in source table")
        
        self._dropdown_cell_links[(row, col)] = {
            'source_table': source_table,
            'source_col': source_col,
            'auto_update': auto_update,
            'unique_only': unique_only,
            'skip_empty': skip_empty,
            'include_empty': include_empty
        }
        
        if auto_update:
            # Connect to source table changes
            source_table.cellChanged.connect(
                lambda src_row, src_col: self._on_source_table_changed_cell((row, col), src_col)
            )
            source_table._dropdown_dependent_tables.append((self, (row, col)))
        
        self._sync_dropdown_from_cell(row, col)
        return self
    
    def sync_dropdown_from_source(self, dropdown_col):
        """Manually sync dropdown options from linked source table."""
        if dropdown_col not in self._dropdown_column_links:
            raise ValueError(f"Column {dropdown_col} is not linked to a source table")
        
        self._sync_dropdown_from_column(dropdown_col)
    
    def sync_cell_dropdown_from_source(self, row, col):
        """Manually sync cell dropdown options from linked source table."""
        if (row, col) not in self._dropdown_cell_links:
            raise ValueError(f"Cell [{row}, {col}] is not linked to a source table")
        
        self._sync_dropdown_from_cell(row, col)
    
    def _on_source_table_changed(self, dropdown_col, changed_col):
        """Internal: Handle source table changes for column-level auto-update."""
        if dropdown_col not in self._dropdown_column_links:
            return
        
        link_info = self._dropdown_column_links[dropdown_col]
        
        if changed_col == link_info['source_col']:
            self._sync_dropdown_from_column(dropdown_col)
    
    def _on_source_table_changed_cell(self, cell_key, changed_col):
        """Internal: Handle source table changes for cell-level auto-update."""
        if cell_key not in self._dropdown_cell_links:
            return
        
        link_info = self._dropdown_cell_links[cell_key]
        
        if changed_col == link_info['source_col']:
            row, col = cell_key
            self._sync_dropdown_from_cell(row, col)
    
    def _sync_dropdown_from_column(self, dropdown_col):
        """Internal: Sync dropdown options from source table column."""
        if dropdown_col not in self._dropdown_column_links:
            return
        
        link_info = self._dropdown_column_links[dropdown_col]
        source_table = link_info['source_table']
        source_col = link_info['source_col']
        
        values = self._extract_column_values(
            source_table, 
            source_col,
            unique=link_info['unique_only'],
            skip_empty=link_info['skip_empty']
        )
        
        # Add empty option if requested
        if link_info.get('include_empty', False):
            if '' not in values:
                values = [''] + values
        
        if not values:
            values = ['']
        
        # Save current selections
        current_selections = {}
        for row in range(self.rowCount()):
            widget = self.cellWidget(row, dropdown_col)
            if isinstance(widget, _MultiSelectDropdown):
                current_selections[row] = widget.get_selected()
            elif isinstance(widget, QtWidgets.QComboBox):
                current_selections[row] = widget.currentText()
        
        # Preserve multi-select flag when updating options
        is_multi = dropdown_col in self.dropdown_multi_columns
        self.set_dropdown(dropdown_col, values, update_existing=True, multi=is_multi)
        
        # Restore selections
        for row, selected_value in current_selections.items():
            widget = self.cellWidget(row, dropdown_col)
            if isinstance(widget, _MultiSelectDropdown):
                # For multi-select, filter out values no longer in options
                if isinstance(selected_value, list):
                    valid_selections = [v for v in selected_value if v in values]
                    widget.set_selected(valid_selections)
                else:
                    widget.set_selected([])
            elif isinstance(widget, QtWidgets.QComboBox):
                if selected_value not in values:
                    widget.setCurrentIndex(0)
                else:
                    idx = widget.findText(selected_value)
                    widget.setCurrentIndex(idx)
    
    def _sync_dropdown_from_cell(self, row, col):
        """Internal: Sync cell dropdown options from source table column."""
        if (row, col) not in self._dropdown_cell_links:
            return
        
        link_info = self._dropdown_cell_links[(row, col)]
        source_table = link_info['source_table']
        source_col = link_info['source_col']
        
        values = self._extract_column_values(
            source_table, 
            source_col,
            unique=link_info['unique_only'],
            skip_empty=link_info['skip_empty']
        )
        
        # Add empty option if requested
        if link_info.get('include_empty', False):
            if '' not in values:
                values = [''] + values
        
        if not values:
            values = ['']
        
        # Save current selection
        current_selection = None
        widget = self.cellWidget(row, col)
        if isinstance(widget, _MultiSelectDropdown):
            current_selection = widget.get_selected()
        elif isinstance(widget, QtWidgets.QComboBox):
            current_selection = widget.currentText()
        
        # Get current multi-select setting for this cell
        cell_config = self._get_cell_dropdown_config(row, col)
        is_multi = cell_config['multi'] if cell_config else False
        
        # Update cell dropdown options
        self.set_cell_dropdown(row, col, values, multi=is_multi)
        
        # Restore selection
        widget = self.cellWidget(row, col)
        if isinstance(widget, _MultiSelectDropdown):
            if isinstance(current_selection, list):
                valid_selections = [v for v in current_selection if v in values]
                widget.set_selected(valid_selections)
            else:
                widget.set_selected([])
        elif isinstance(widget, QtWidgets.QComboBox):
            if current_selection and current_selection in values:
                idx = widget.findText(current_selection)
                widget.setCurrentIndex(idx)
            else:
                widget.setCurrentIndex(0)
    
    def _extract_column_values(self, table, col, unique=True, skip_empty=True):
        """Extract values from a table column using data_manager."""
        values = []
        
        for row in range(table.rowCount()):
            value = table._get_cell_value_internal_use(row, col)
            
            if isinstance(value, ReplicaXTable):
                continue
            
            # Use data_manager to convert to string
            try:
                value_str = self.data_manager.save_data_type_as_string(value, 'str') if value is not None else ""
            except:
                value_str = str(value) if value is not None else ""
            
            if skip_empty and not value_str.strip():
                continue
            
            values.append(value_str)
        
        if unique:
            seen = set()
            unique_values = []
            for v in values:
                if v not in seen:
                    seen.add(v)
                    unique_values.append(v)
            return unique_values
        
        return values
        
    # Add this method to properly clean up dependent tables when they're deleted:
    def _cleanup_dependent_tables(self):
        """Clean up references to dependent tables that may have been destroyed."""
        valid_dependents = []
        for target_table, identifier in self._dropdown_dependent_tables:
            try:
                # Test if the table still exists by actually calling a method
                # This will raise RuntimeError if C++ object was deleted
                _ = target_table.rowCount()
                valid_dependents.append((target_table, identifier))
            except (RuntimeError, AttributeError):
                # Table was destroyed or is None, skip it
                continue
        self._dropdown_dependent_tables = valid_dependents

    def _notify_dependent_dropdowns(self):
        """Notify tables with linked dropdowns that data changed."""
        for target_table, identifier in self._dropdown_dependent_tables:
            try:
                # Safety check: ensure table still exists
                _ = target_table.rowCount()
                
                if isinstance(identifier, tuple):
                    # Cell-level link: identifier is (row, col)
                    row, col = identifier
                    target_table._sync_dropdown_from_cell(row, col)
                else:
                    # Column-level link: identifier is just col
                    target_table._sync_dropdown_from_column(identifier)
            except (RuntimeError, AttributeError):
                # Table was deleted between cleanup and notify, skip it
                continue

    # ============================================================================
    # DATA ACCESS - ALL via data_manager
    # ============================================================================
    
    def _get_cell_value_internal_use(self, row, col, in_display_units=False, dropdown_true_type=False):
        """
        Get cell value using data_manager exclusively.
        
        Args:
            row: Row index
            col: Column index
            in_display_units: If True, return value in display units
            dropdown_true_type: If True, convert dropdown values to column type
                        (e.g., convert ['1','2'] to [1,2] if column type is list(int))
        
        Returns:
            Value in base units (default) or display units, properly typed via data_manager.
            - For dropdowns with dropdown_true_type=False: returns str or list(str)
            - For dropdowns with dropdown_true_type=True: converts to column type (e.g., int, list(int))
        
        Examples:
            # Column type is 'list(int)', dropdown has ['1', '2', '3']
            table._get_cell_value_internal_use(0, 1)  # Returns ['1', '2', '3'] (list of strings)
            table._get_cell_value_internal_use(0, 1, dropdown_true_type=True)  # Returns [1, 2, 3] (list of ints)
        """
        if (row, col) in self.nested_tables:
            return self.nested_tables[(row, col)]
        
        cell_type = self._get_cell_type(row, col, dropdown_true_type=dropdown_true_type)
        
        # Check for dropdown (cell-level or column-level)
        dropdown_config = self._get_cell_dropdown_config(row, col)
        if dropdown_config is not None:
            widget = self.cellWidget(row, col)
            
            # Multi-select dropdown
            if isinstance(widget, _MultiSelectDropdown):
                selected = widget.get_selected()  # Returns list of strings
                # Use 'selected' instead of undefined 'value'
                try:
                    # If dropdown_true_type=True and column is list(int), this converts to integers
                    return self.data_manager.load_data_type(selected, cell_type)
                except:
                    return selected
            
            # Single-select dropdown
            if isinstance(widget, QtWidgets.QComboBox):
                value = widget.currentText()  # Returns string
                try:
                    # If dropdown_true_type=True and column is int, this converts to integer
                    return self.data_manager.load_data_type(value, cell_type)
                except:
                    return value
        
        item = self.item(row, col)
        if not item or not item.text():
            return None
        
        text = item.text()
        
        # Check if column has units and is numeric type
        unit_config = self._get_cell_unit_config(row, col)
        
        # Only apply unit conversion to numeric types
        if unit_config is not None and self._is_numeric_type(cell_type):
            base_value = self._parse_value_with_unit(text, row, col)
            if in_display_units:
                return self._convert_from_base_unit(base_value, row, col)
            return base_value
        
        # Regular cell - use data_manager
        try:
            return self.data_manager.load_data_type(text, cell_type)
        except:
            return text
    
    def set_cell_value(self, row, col, value, value_is_in_base_units=True):
        """
        Set cell value using data_manager exclusively.
        
        Args:
            row: Row index
            col: Column index
            value: Value to set
            value_is_in_base_units: If True (default), value is in base units
        """
        self.blockSignals(True)
        
        try:
            if isinstance(value, ReplicaXTable):
                if (row, col) in self.nested_table_dialogs:
                    self.nested_table_dialogs[(row, col)].deleteLater()
                    del self.nested_table_dialogs[(row, col)]
                value.setParent(None)
                value.hide()
                self.nested_tables[(row, col)] = value
                self._add_widget(row, col, 'table')
                return
            
            if self._get_cell_type(row, col) == 'table':
                return
            
            # Check for dropdown
            dropdown_config = self._get_cell_dropdown_config(row, col)
            if dropdown_config is not None:
                widget = self.cellWidget(row, col)
                is_multi = dropdown_config['multi']
                
                if widget is not None:
                    # Widget exists - update it
                    if isinstance(widget, _MultiSelectDropdown):
                        if isinstance(value, list):
                            widget.set_selected(value)
                        elif value is not None:
                            widget.set_selected([str(value)])
                        else:
                            widget.set_selected([])
                    
                    elif isinstance(widget, QtWidgets.QComboBox):
                        try:
                            value_str = self.data_manager.save_data_type_as_string(value, 'str')
                        except:
                            value_str = str(value) if value is not None else ""
                        idx = widget.findText(value_str)
                        widget.setCurrentIndex(max(0, idx))
                
                else:
                    # Widget doesn't exist - create it with value
                    if is_multi:
                        # Multi-select: pass list
                        if isinstance(value, list):
                            default_selection = value
                        elif value is not None:
                            default_selection = [str(value)]
                        else:
                            default_selection = []
                        self._add_widget(row, col, 'dropdown', default_selection)
                    else:
                        # Single-select: pass string
                        try:
                            value_str = self.data_manager.save_data_type_as_string(value, 'str')
                        except:
                            value_str = str(value) if value is not None else ""
                        self._add_widget(row, col, 'dropdown', value_str)
                
                return
            
            # Convert to base units if needed
            unit_config = self._get_cell_unit_config(row, col)
            if unit_config is not None and not value_is_in_base_units:
                value = self._convert_to_base_unit(value, row, col)
            
            # Store in base units, display with unit
            if unit_config is not None and value is not None:
                self._update_cell_display(row, col, value)
            else:
                # Regular cell - use data_manager
                item = self.item(row, col)
                if not item:
                    item = QtWidgets.QTableWidgetItem()
                    self.setItem(row, col, item)
                
                if value is not None:
                    try:
                        text = self.data_manager.save_data_type_as_string(value, self._get_cell_type(row, col))
                        item.setText(text)
                    except:
                        item.setText(str(value))
                else:
                    item.setText("")
        
        finally:
            self.blockSignals(False)
    
    def get_cell_value(self, row, col, in_display_units=True):
        """
        Convenience method to get cell value converted to its true column type.
        
        This is equivalent to calling _get_cell_value_internal_use() with dropdown_true_type=True.
        Useful for extracting typed data from dropdowns for calculations.
        
        Args:
            row: Row index
            col: Column index
            in_display_units: If True, return value in display units (for numeric types)
        
        Returns:
            Value converted to the column's defined type:
            - Dropdown with column type 'int': returns int
            - Dropdown with column type 'list(int)': returns list of ints
            - Dropdown with column type 'bool': returns bool
            - Regular cells: returns value in column type
        
        Examples:
            # Column type is 'list(int)', dropdown shows ['1', '2', '3']
            table.get_cell_true_value(0, 1)  # Returns [1, 2, 3] (list of ints)
            
            # Column type is 'bool', dropdown shows ['true', 'false']
            table.get_cell_true_value(0, 2)  # Returns True or False (bool)
            
            # Column type is 'int', dropdown shows ['10', '20', '30']
            table.get_cell_true_value(0, 3)  # Returns 10, 20, or 30 (int)
        """
        return self._get_cell_value_internal_use(row, col, in_display_units=in_display_units, dropdown_true_type=True)
    
    # ============================================================================
    # NESTED TABLES
    # ============================================================================
    
    def create_nested_table(self, row, col, rows=0, cols=0):
        """Create nested table at specified cell."""
        if self._get_cell_type(row, col) != 'table':
            raise ValueError(f"Cell [{row},{col}] is not type 'table'")
                
        # Clean up old dialog if replacing existing table
        if (row, col) in self.nested_table_dialogs:
            self.nested_table_dialogs[(row, col)].deleteLater()
            del self.nested_table_dialogs[(row, col)]

        nested = ReplicaXTable(rows, cols, parent=None, settings=self.settings)
        nested.hide()
        
        self.nested_tables[(row, col)] = nested
        self._add_widget(row, col, 'table')
        return nested
    
    # Replace _open_nested_table completely:
    def _open_nested_table(self, row, col):
        """Open nested table in dialog (creates dialog once, reuses it)."""
        if (row, col) not in self.nested_tables:
            self.create_nested_table(row, col)
        
        # Check if dialog already exists for this cell
        if (row, col) not in self.nested_table_dialogs:
            # Create dialog ONCE
            nested = self.nested_tables[(row, col)]
            
            dialog = QtWidgets.QDialog(self)
            dialog.setWindowTitle(f"Nested Table [Row {row+1}, Col {col+1}]")
            dialog.resize(700, 500)
            
            layout = QtWidgets.QVBoxLayout(dialog)
            
            # Set parent ONCE (never changes after this)
            nested.setParent(dialog)
            nested.show()
            layout.addWidget(nested)
            
            btn_close = QtWidgets.QPushButton("Close")
            btn_close.clicked.connect(dialog.accept)
            layout.addWidget(btn_close)
            
            # Cache the dialog
            self.nested_table_dialogs[(row, col)] = dialog
        
        # Reuse existing dialog
        dialog = self.nested_table_dialogs[(row, col)]
        dialog.exec()
    
    def _handle_double_click(self, row, col):
        """Handle double-click on table cells."""
        if self._get_cell_type(row, col) == 'table':
            self._open_nested_table(row, col)
    
    # ============================================================================
    # WIDGETS
    # ============================================================================
    
    def _add_widget(self, row, col, widget_type, default_value=None):
        """Create and set cell widget."""
        if widget_type == 'dropdown':
            dropdown_config = self._get_cell_dropdown_config(row, col)
            
            if dropdown_config is None:
                return
            
            options = dropdown_config['options']
            is_multi = dropdown_config['multi']
            
            if is_multi:
                # Multi-select dropdown
                multi_widget = _MultiSelectDropdown([str(opt) for opt in options])
                
                # Handle list default values
                if default_value is not None:
                    if isinstance(default_value, list):
                        multi_widget.set_selected(default_value)
                    else:
                        multi_widget.set_selected([str(default_value)])
                
                multi_widget.selectionChanged.connect(
                    lambda: self._on_dropdown_template_changed(row, col)
                )
                
                self.setCellWidget(row, col, multi_widget)
            else:
                # Single-select dropdown
                combo = QtWidgets.QComboBox()
                combo.setFocusPolicy(QtCore.Qt.StrongFocus)
                combo.addItems([str(opt) for opt in options])
                
                if default_value is not None:
                    try:
                        default_str = self.data_manager.save_data_type_as_string(default_value, 'str')
                    except:
                        default_str = str(default_value)
                    idx = combo.findText(default_str)
                    combo.setCurrentIndex(max(0, idx))
                
                combo.currentTextChanged.connect(
                    lambda: self._on_dropdown_template_changed(row, col)
                )
                
                self.setCellWidget(row, col, combo)
        
        elif widget_type == 'table':
            btn = QtWidgets.QPushButton("📊 Table")
            btn.setFocusPolicy(QtCore.Qt.NoFocus)
            btn.clicked.connect(lambda: self._open_nested_table(row, col))
            self.setCellWidget(row, col, btn)
    
    # ============================================================================
    # ROW MANAGEMENT
    # ============================================================================
    
    def add_row(self):
        """Add empty row (Ctrl++)."""
        row = self.currentRow() + 1 if self.currentRow() >= 0 else self.rowCount()
        self.insertRow(row)
        self._shift_indices_on_insert(row)
        self._init_row(row)
        self.setCurrentCell(row, 0)
        self._recreate_all_table_buttons()
    
    def import_rows(self):
        """Add multiple empty rows (Ctrl+Shift++)."""
        n, ok = QtWidgets.QInputDialog.getInt(self, "Import Rows", "Number of rows:", 1, 1, 1000)
        if ok:
            insert_at = self.currentRow() + 1 if self.currentRow() >= 0 else self.rowCount()
            for i in range(n):
                row = insert_at + i
                self.insertRow(row)
                self._shift_indices_on_insert(row)
                self._init_row(row)
            self._recreate_all_table_buttons()
    
    def remove_row(self):
        """Remove current row (Ctrl+-)."""
        row = self.currentRow()
        if row >= 0:
            self._cleanup_row(row)
            self.removeRow(row)
            self._cleanup_dependent_tables()
            self._notify_dependent_dropdowns()
            self._recreate_all_table_buttons()
    
    def remove_selected_rows(self):
        """Remove all selected rows (Ctrl+Shift+-)."""
        rows = set()
        for r in self.selectedRanges():
            rows.update(range(r.topRow(), r.bottomRow() + 1))
        
        for row in sorted(rows, reverse=True):
            self._cleanup_row(row)
            self.removeRow(row)
        
        self._cleanup_dependent_tables()
        self._notify_dependent_dropdowns()
        self._recreate_all_table_buttons()
    
    def _init_row(self, row):
        """Initialize widgets for a new row."""
        for col in range(self.columnCount()):
            cell_type = self._get_cell_type(row, col)
            if cell_type == 'table':
                self._add_widget(row, col, 'table')
            elif (row, col) in self.cell_dropdowns or col in self.dropdown_options:
                self._add_widget(row, col, 'dropdown')


    def _cleanup_row(self, row):
        """Clean up row data and shift ALL indices."""
        # Delete nested tables AND their dialogs
        cols_to_delete = [col for (r, col) in self.nested_tables.keys() if r == row]
        for col in cols_to_delete:
            del self.nested_tables[(row, col)]
            # Delete cached dialog too
            if (row, col) in self.nested_table_dialogs:
                self.nested_table_dialogs[(row, col)].deleteLater()
                del self.nested_table_dialogs[(row, col)]
        
        # ===============================XXX==========================
        cell_keys_to_delete = [(r, c) for (r, c) in self.cell_units.keys() if r == row]
        for key in cell_keys_to_delete:
            del self.cell_units[key]
        
        cell_dropdown_keys_to_delete = [(r, c) for (r, c) in self.cell_dropdowns.keys() if r == row]
        for key in cell_dropdown_keys_to_delete:
            del self.cell_dropdowns[key]
        
        cell_link_keys_to_delete = [(r, c) for (r, c) in self._dropdown_cell_links.keys() if r == row]
        for key in cell_link_keys_to_delete:
            del self._dropdown_cell_links[key]
        
        # Delete row-specific configs
        if row in self.row_types:
            del self.row_types[row]
        
        if row in self.row_units:
            del self.row_units[row]
        # ===============================XXX==========================

        # Shift nested tables
        new_nested = {}
        new_dialogs = {}  # Also shift dialogs
        for (r, c), table in self.nested_tables.items():
            if r > row:
                new_nested[(r - 1, c)] = table
                if (r, c) in self.nested_table_dialogs:
                    new_dialogs[(r - 1, c)] = self.nested_table_dialogs[(r, c)]
            elif r < row:
                new_nested[(r, c)] = table
                if (r, c) in self.nested_table_dialogs:
                    new_dialogs[(r, c)] = self.nested_table_dialogs[(r, c)]
        
        self.nested_tables = new_nested
        self.nested_table_dialogs = new_dialogs
        
        # ===============================XXX==========================
        # Shift row types
        new_row_types = {}
        for r, types in self.row_types.items():
            if r > row:
                new_row_types[r - 1] = types
            elif r < row:
                new_row_types[r] = types
        self.row_types = new_row_types
        
        # Shift row units
        new_row_units = {}
        for r, units in self.row_units.items():
            if r > row:
                new_row_units[r - 1] = units
            elif r < row:
                new_row_units[r] = units
        self.row_units = new_row_units
        
        # Shift cell units
        new_cell_units = {}
        for (r, c), config in self.cell_units.items():
            if r > row:
                new_cell_units[(r - 1, c)] = config
            elif r < row:
                new_cell_units[(r, c)] = config
        self.cell_units = new_cell_units
        
        # Shift cell dropdowns
        new_cell_dropdowns = {}
        for (r, c), config in self.cell_dropdowns.items():
            if r > row:
                new_cell_dropdowns[(r - 1, c)] = config
            elif r < row:
                new_cell_dropdowns[(r, c)] = config
        self.cell_dropdowns = new_cell_dropdowns
        
        # Shift cell dropdown links
        new_cell_links = {}
        for (r, c), link_info in self._dropdown_cell_links.items():
            if r > row:
                new_cell_links[(r - 1, c)] = link_info
            elif r < row:
                new_cell_links[(r, c)] = link_info
        self._dropdown_cell_links = new_cell_links
        # ===============================XXX==========================

     # ===============================XXX==========================
    def reset_data(self):
        """
        Reset all table data while preserving column configurations.
        Uses existing row cleanup logic for consistency.
        """
        self.blockSignals(True)
        try:
            # Remove all rows using existing cleanup logic
            for row in range(self.rowCount() - 1, -1, -1):
                self._cleanup_row(row)
                self.removeRow(row)
            
            # Clear clipboard
            self._copied_data = None
            
            # Reset internal flags
            self._validating = False
            self._internal_update = False
            
            # Notify dependent tables
            self._cleanup_dependent_tables()
            self._notify_dependent_dropdowns()
            
        finally:
            self.blockSignals(False)
        
        return self
     # ===============================XXX==========================
    
    def _shift_indices_on_insert(self, inserted_row):
        """Shift indices UP when row inserted."""
        new_nested = {}
        for (r, c), table in self.nested_tables.items():
            if r >= inserted_row:
                new_nested[(r + 1, c)] = table
            else:
                new_nested[(r, c)] = table
        self.nested_tables = new_nested
        
        # Shift nested table dialogs too
        new_dialogs = {}
        for (r, c), dialog in self.nested_table_dialogs.items():
            if r >= inserted_row:
                new_dialogs[(r + 1, c)] = dialog
                # Update dialog title to reflect new position
                dialog.setWindowTitle(f"Nested Table [Row {r+2}, Col {c+1}]")
            else:
                new_dialogs[(r, c)] = dialog
        self.nested_table_dialogs = new_dialogs
        
        # Shift row types
        new_row_types = {}
        for r, types in self.row_types.items():
            if r >= inserted_row:
                new_row_types[r + 1] = types
            else:
                new_row_types[r] = types
        self.row_types = new_row_types
    
    def _recreate_all_table_buttons(self):
        """Recreate all table buttons to fix lambda closure row indices."""
        for row in range(self.rowCount()):
            for col in range(self.columnCount()):
                if self._get_cell_type(row, col) == 'table':
                    # Only recreate if there's actually a nested table
                    if (row, col) in self.nested_tables:
                        # Remove old button
                        old_widget = self.cellWidget(row, col)
                        if old_widget:
                            self.removeCellWidget(row, col)
                        # Create new button with correct row/col
                        self._add_widget(row, col, 'table')
    
    # ============================================================================
    # CLIPBOARD - ALL via data_manager
    # ============================================================================
    
    def copy_selection(self):
        """Copy selection to clipboard (Ctrl+C)."""
        ranges = self.selectedRanges()
        if not ranges:
            return
        
        self._copied_data = {
            'text_data': [], 
            'nested_tables': {},
            'start_row': ranges[0].topRow(), 
            'start_col': ranges[0].leftColumn()
        }
        
        for r in ranges:
            for row in range(r.topRow(), r.bottomRow() + 1):
                cols = []
                for col in range(r.leftColumn(), r.rightColumn() + 1):
                    value = self._get_cell_value_internal_use(row, col, in_display_units=True)
                    if isinstance(value, ReplicaXTable):
                        rel_row = row - self._copied_data['start_row']
                        rel_col = col - self._copied_data['start_col']
                        self._copied_data['nested_tables'][(rel_row, rel_col)] = value.to_json()
                        cols.append("[Table]")
                    else:
                        try:
                            val_str = self.data_manager.save_data_type_as_string(value, 'str') if value is not None else ""
                        except:
                            val_str = str(value) if value is not None else ""
                        cols.append(val_str)
                self._copied_data['text_data'].append("\t".join(cols))
        
        QtWidgets.QApplication.clipboard().setText("\n".join(self._copied_data['text_data']))
    
    def paste_selection(self):
        """Paste from clipboard (Ctrl+V)."""
        text = QtWidgets.QApplication.clipboard().text()
        if not text:
            return
        
        row, col = self.currentRow(), self.currentColumn()
        if row < 0 or col < 0:
            return
        
        for i, line in enumerate(text.split('\n')):
            if not line:
                continue
            for j, val in enumerate(line.split('\t')):
                target_row, target_col = row + i, col + j
                if target_row >= self.rowCount() or target_col >= self.columnCount():
                    continue
                
                if val == "[Table]" and self._copied_data and (i, j) in self._copied_data['nested_tables']:
                    if self._get_cell_type(target_row, target_col) == 'table':
                        # Clean up old dialog if replacing
                        if (target_row, target_col) in self.nested_table_dialogs:
                            self.nested_table_dialogs[(target_row, target_col)].deleteLater()
                            del self.nested_table_dialogs[(target_row, target_col)]
                        nested = ReplicaXTable(parent=None, settings=self.settings)
                        nested.hide()
                        nested.from_json(self._copied_data['nested_tables'][(i, j)])
                        self.nested_tables[(target_row, target_col)] = nested
                        self._add_widget(target_row, target_col, 'table')
                    continue
                
                if self._get_cell_type(target_row, target_col) != 'table' and val != "[Table]":
                    # Parse unit-aware values before setting
                    unit_config = self._get_cell_unit_config(target_row, target_col)
                    cell_type = self._get_cell_type(target_row, target_col)
                    
                    if unit_config is not None and self._is_numeric_type(cell_type):
                        # Parse string with unit (e.g., "100 mm" → 0.1 in base units)
                        parsed_value = self._parse_value_with_unit(val, target_row, target_col)
                        self.set_cell_value(target_row, target_col, parsed_value, value_is_in_base_units=True)
                    else:
                        # Regular cell without units
                        self.set_cell_value(target_row, target_col, val)

    def clear_selection(self):
        """Clear selected cells (Delete)."""
        for r in self.selectedRanges():
            for row in range(r.topRow(), r.bottomRow() + 1):
                for col in range(r.leftColumn(), r.rightColumn() + 1):
                    if (row, col) in self.nested_tables:
                        del self.nested_tables[(row, col)]
                        # Also delete cached dialog
                        if (row, col) in self.nested_table_dialogs:
                            self.nested_table_dialogs[(row, col)].deleteLater()
                            del self.nested_table_dialogs[(row, col)]
                        self._add_widget(row, col, 'table')
                    elif (row, col) in self.cell_dropdowns or col in self.dropdown_options:
                        widget = self.cellWidget(row, col)
                        if isinstance(widget, _MultiSelectDropdown):
                            widget.set_selected([])
                        elif isinstance(widget, QtWidgets.QComboBox):
                            widget.setCurrentIndex(0)
                    else:
                        item = self.item(row, col)
                        if item:
                            item.setText("")
    
    # ============================================================================
    # VALIDATION & CELL EDITING - ALL via data_manager
    # ============================================================================
    
    def _handle_cell_edit(self, row, col):
        """
        Handle user editing cells using data_manager exclusively.
        Converts units and validates types.
        """
        if self._internal_update or self._validating:
            return
        
        cell_type = self._get_cell_type(row, col)
        if cell_type == 'table' or col in self.dropdown_options:
            return
        
        item = self.item(row, col)
        if not item or not item.text().strip():
            if item:
                item.setBackground(self.palette().base())
            return
        
        user_input = item.text().strip()
        
        self._validating = True
        try:
            unit_config = self._get_cell_unit_config(row, col)
            
            if unit_config is not None:
                # Parse with unit using data_manager
                base_value = self._parse_value_with_unit(user_input, row, col)
                
                # Validate via data_manager
                validated_value = self.data_manager.load_data_type(
                    self.data_manager.save_data_type_as_string(base_value, cell_type),
                    cell_type
                )
                
                # Update display
                self._internal_update = True
                self._update_cell_display(row, col, validated_value)
                self._internal_update = False
                
                item.setBackground(self.palette().base())
            else:
                # Regular cell - validate via data_manager
                validated_value = self.data_manager.load_data_type(user_input, cell_type)
                item.setBackground(self.palette().base())
                
        except Exception:
            # Validation failed - highlight error
            base = self.palette().base().color()
            error_color = QtGui.QColor(255, 200, 200) if base.lightness() > 128 else QtGui.QColor(100, 30, 30)
            item.setBackground(error_color)
        finally:
            self._validating = False
    
    # ============================================================================
    # JSON SERIALIZATION - ALL via data_manager
    # ============================================================================
    def to_json(self, filepath=None):
        """Serialize table to JSON using data_manager exclusively."""
        data = {
            'version': f'{INFO["version"]}',
            'rows': self.rowCount(),
            'columns': self.columnCount(),
            'column_types': self.column_types,
            'row_types': {str(k): v for k, v in self.row_types.items()},
            'headers': [
                self.horizontalHeaderItem(i).text() if self.horizontalHeaderItem(i) else f"Col{i}"
                for i in range(self.columnCount())
            ],
            'dropdown_options': {str(k): v for k, v in self.dropdown_options.items()},
            'dropdown_multi_columns': list(self.dropdown_multi_columns),
            'cell_dropdowns': {
                f"{r},{c}": {'options': config['options'], 'multi': config['multi']}
                for (r, c), config in self.cell_dropdowns.items()
            },
            'column_units': {
                str(col): {
                    'unit_type': config['unit_type'],
                    'display_unit': config['display_unit'],
                    'base_unit': config['base_unit']
                }
                for col, config in self.column_units.items()
            },
            'row_units': {
                str(row): {
                    str(col): {
                        'unit_type': config['unit_type'],
                        'display_unit': config['display_unit'],
                        'base_unit': config['base_unit']
                    }
                    for col, config in units.items()
                }
                for row, units in self.row_units.items()
            },
            'cell_units': {
                f"{r},{c}": {
                    'unit_type': config['unit_type'],
                    'display_unit': config['display_unit'],
                    'base_unit': config['base_unit']
                }
                for (r, c), config in self.cell_units.items()
            },
            'unit_display_mode': self._unit_display_mode,
            'cells': []
        }
        
        # Serialize cells using CORRECT type (dropdown-aware)
        for row in range(self.rowCount()):
            row_data = []
            for col in range(self.columnCount()):
                if (row, col) in self.nested_tables:
                    row_data.append(None)
                else:
                    value = self._get_cell_value_internal_use(row, col, in_display_units=False)
                    if value is not None:
                        # Use dropdown-aware cell type
                        cell_type = self._get_cell_type(row, col)
                        try:
                            # For multi-select (list(str)), this will save as JSON array
                            # For single-select (str), this will save as JSON string
                            validated = self.data_manager.save_data_type(value, cell_type)
                            row_data.append(validated)
                        except Exception as e:
                            # Fallback: save raw value
                            row_data.append(value)
                    else:
                        row_data.append(None)
            data['cells'].append(row_data)
        
        data['nested_tables'] = {
            f"{r},{c}": json.loads(t.to_json())
            for (r, c), t in self.nested_tables.items()
        }
        
        json_str = json.dumps(data, indent=2)
        
        if filepath:
            try:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(json_str)
            except IOError as e:
                raise IOError(f"Failed to save table to {filepath}: {e}")
        else:
            return json_str

    def from_json(self, source):
        """Load table from JSON using data_manager exclusively."""
        try:
            if isinstance(source, str):
                if source.strip().startswith('{'):
                    data = json.loads(source)
                else:
                    with open(source, 'r', encoding='utf-8') as f:
                        data = json.load(f)
            else:
                raise ValueError("Source must be a JSON string or filepath")
        
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON format: {e}")
        except FileNotFoundError:
            raise ValueError(f"File not found: {source}")
        except Exception as e:
            raise ValueError(f"Failed to load JSON: {e}")
        
        self.blockSignals(True)
        try:
            self.clear()
            self.nested_tables.clear()
            for dialog in self.nested_table_dialogs.values():
                dialog.deleteLater()
            self.nested_table_dialogs.clear()
            self.dropdown_options.clear()
            self.dropdown_multi_columns.clear()
            self.cell_dropdowns.clear()
            self.row_types.clear()
            self.column_units.clear()
            self.row_units.clear()
            self.cell_units.clear()
            
            self.setRowCount(data.get('rows', 0))
            self.setColumnCount(data.get('columns', 3))
            
            self.column_types = data.get('column_types', ['str'] * self.columnCount())
            
            if 'row_types' in data:
                for row_str, types in data['row_types'].items():
                    self.row_types[int(row_str)] = types
            
            # Load dropdown configs BEFORE init_table_cells
            if 'dropdown_options' in data:
                for col_str, options in data['dropdown_options'].items():
                    self.dropdown_options[int(col_str)] = options
            
            if 'dropdown_multi_columns' in data:
                self.dropdown_multi_columns = set(data['dropdown_multi_columns'])
            
            if 'cell_dropdowns' in data:
                for key, config in data['cell_dropdowns'].items():
                    row, col = map(int, key.split(','))
                    self.cell_dropdowns[(row, col)] = config
            
            if 'column_units' in data:
                for col_str, config in data['column_units'].items():
                    self.column_units[int(col_str)] = config
            
            if 'row_units' in data:
                for row_str, units_dict in data['row_units'].items():
                    self.row_units[int(row_str)] = {
                        int(col_str): config
                        for col_str, config in units_dict.items()
                    }
            
            if 'cell_units' in data:
                for key, config in data['cell_units'].items():
                    row, col = map(int, key.split(','))
                    self.cell_units[(row, col)] = config
            
            if 'unit_display_mode' in data:
                self._unit_display_mode = data['unit_display_mode']
            
            if 'headers' in data:
                self.set_headers(data['headers'])
            
            # Create widgets first
            self.init_table_cells()
            
            # THEN load values using dropdown-aware types
            for row, row_data in enumerate(data.get('cells', [])):
                if row >= self.rowCount():
                    break
                for col, val in enumerate(row_data):
                    if col >= self.columnCount():
                        break
                    if val is not None:
                        # Use dropdown-aware cell type
                        cell_type = self._get_cell_type(row, col)
                        try:
                            # For multi-select, val will be a JSON array (Python list)
                            # data_manager.load_data_type will handle it correctly
                            typed_value = self.data_manager.load_data_type(val, cell_type)
                            self.set_cell_value(row, col, typed_value, value_is_in_base_units=True)
                        except Exception as e:
                            # Fallback: try setting raw value
                            self.set_cell_value(row, col, val, value_is_in_base_units=True)
            
            if 'nested_tables' in data:
                for key, nested_data in data['nested_tables'].items():
                    row, col = map(int, key.split(','))
                    if row < self.rowCount() and col < self.columnCount():
                        nested = ReplicaXTable(parent=None, settings=self.settings)
                        nested.hide()
                        nested.from_json(json.dumps(nested_data))
                        self.nested_tables[(row, col)] = nested
                        self._add_widget(row, col, 'table')
        
        finally:
            self.blockSignals(False)
        
        return self

    def save_to_file(self, filepath):
        """Save table to JSON file."""
        self.to_json(filepath)
    
    def load_from_file(self, filepath):
        """Load table from JSON file."""
        self.from_json(filepath)
