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


import sys
import json
import zipfile
import os
import tempfile
import numpy as np
from PySide6 import QtWidgets, QtGui, QtCore
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
from ...UtilityAPI.UnitsAPI import ReplicaXUnits
from ...UtilityAPI.DataValidationAPI import ReplicaXDataTypesManager
import math

class ReplicaXLegacyTable(QtWidgets.QTableWidget):
    def __init__(self, rows, columns, parent=None):
        super().__init__(rows, columns, parent)

        self.setColumnCount(columns)
        self.setRowCount(rows)

        self.setAlternatingRowColors(True)
        self.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectItems)
        self.setSelectionMode(QtWidgets.QAbstractItemView.ContiguousSelection)

        self.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)

        self.cellClicked.connect(self.select_cell)
        self.horizontalHeader().sectionClicked.connect(self.select_multiple_columns)
        self.verticalHeader().sectionClicked.connect(self.select_multiple_rows)

        # Add shortcuts
        self.add_row_shortcut = QtGui.QShortcut(QtGui.QKeySequence("Ctrl++"), self)
        self.add_row_shortcut.activated.connect(self.add_row)
        
        self.import_rows_shortcut = QtGui.QShortcut(QtGui.QKeySequence("Ctrl+Shift++"), self)
        self.import_rows_shortcut.activated.connect(self.import_rows) 
        
        self.remove_row_shortcut = QtGui.QShortcut(QtGui.QKeySequence("Ctrl+-"), self)
        self.remove_row_shortcut.activated.connect(self.remove_row)

        self.remove_selected_rows_shortcut = QtGui.QShortcut(QtGui.QKeySequence("Ctrl+Shift+-"), self)
        self.remove_selected_rows_shortcut.activated.connect(self.remove_selected_rows)

        self.copy_shortcut = QtGui.QShortcut(QtGui.QKeySequence("Ctrl+C"), self)
        self.copy_shortcut.activated.connect(self.copy_selection_to_clipboard)

        self.paste_shortcut = QtGui.QShortcut(QtGui.QKeySequence("Ctrl+V"), self)
        self.paste_shortcut.activated.connect(self.paste_from_clipboard)

        self.delete_shortcut = QtGui.QShortcut(QtGui.QKeySequence("Delete"), self)
        self.delete_shortcut.activated.connect(self.clear_selection)

        self.data_manager = ReplicaXDataTypesManager()

    def _get_types(self):
        # Print the content and type of the table
        for row in range(self.rowCount()):
            for col in range(self.columnCount()):
                item = self.item(row, col)
                if item:
                    print(f"Row {row}, Column {col}: {item.text()} ({type(item.text())})")
                else:
                    print(f"Row {row}, Column {col}: None")

    def add_headers(self, column_name_list: list[str]):
        index = -1
        for column_name in column_name_list:
            index += 1
            self.setHorizontalHeaderItem(index, QtWidgets.QTableWidgetItem(column_name))

    def select_cell(self, row, column):
        self.clearSelection()
        self.setRangeSelected(QtWidgets.QTableWidgetSelectionRange(row, column, row, column), True)

    def select_multiple_rows(self, row):
        modifiers = QtWidgets.QApplication.keyboardModifiers()
        if modifiers == QtCore.Qt.ShiftModifier and self.selectedRanges():
            current_range = self.selectedRanges()[0]
            self.clearSelection()
            top_row = min(current_range.topRow(), row)
            bottom_row = max(current_range.bottomRow(), row)
            self.setRangeSelected(QtWidgets.QTableWidgetSelectionRange(top_row, 0, bottom_row, self.columnCount() - 1),
                                  True)
        else:
            self.clearSelection()
            self.setRangeSelected(QtWidgets.QTableWidgetSelectionRange(row, 0, row, self.columnCount() - 1), True)

    def select_multiple_columns(self, column):
        modifiers = QtWidgets.QApplication.keyboardModifiers()
        if modifiers == QtCore.Qt.ShiftModifier and self.selectedRanges():
            current_range = self.selectedRanges()[0]
            self.clearSelection()
            left_column = min(current_range.leftColumn(), column)
            right_column = max(current_range.rightColumn(), column)
            self.setRangeSelected(QtWidgets.QTableWidgetSelectionRange(0, left_column, self.rowCount() - 1, right_column),
                                  True)
        else:
            self.clearSelection()
            self.setRangeSelected(QtWidgets.QTableWidgetSelectionRange(0, column, self.rowCount() - 1, column), True)

    def add_row(self):
        current_row = self.currentRow()
        if current_row == -1:
            current_row = self.rowCount()  # Add at the end if no row is selected
        else:
            current_row += 1  # Add directly after the current row
        
        self.insertRow(current_row)
    
    def import_rows(self):
        # Prompt the user for the number of rows to import
        num_rows, ok = QtWidgets.QInputDialog.getInt(self, "Import Rows", "Number of rows to import:", 1, 1)
        if not ok or num_rows <= 0:
            return

        # Determine the starting point for importing
        current_row = self.currentRow()
        if current_row == -1:
            current_row = self.rowCount()  # Add at the end if no row is selected
        else:
            current_row += 1  # Add directly after the current row

        # Insert the specified number of rows starting from the current position
        for _ in range(num_rows):
            self.insertRow(current_row)

    def remove_row(self):
        current_row = self.currentRow()
        if current_row != -1:  # Only remove if a valid row is selected
            self.removeRow(current_row)

    def remove_selected_rows(self):
        selected_ranges = self.selectedRanges()
        if not selected_ranges:
            return

        rows_to_remove = set()
        for selection_range in selected_ranges:
            rows_to_remove.update(range(selection_range.topRow(), selection_range.bottomRow() + 1))

        for row in sorted(rows_to_remove, reverse=True):
            self.removeRow(row)

    def copy_selection_to_clipboard(self):
        selected_ranges = self.selectedRanges()
        if not selected_ranges:
            return

        data = []
        for selection_range in selected_ranges:
            for row in range(selection_range.topRow(), selection_range.bottomRow() + 1):
                row_data = []
                for col in range(selection_range.leftColumn(), selection_range.rightColumn() + 1):
                    item = self.item(row, col)
                    row_data.append(item.text() if item else "")
                data.append("\t".join(row_data))
        clipboard_data = "\n".join(data)

        # Set the clipboard data
        clipboard = QtWidgets.QApplication.clipboard()
        clipboard.setText(clipboard_data)

    def paste_from_clipboard(self):
        clipboard = QtWidgets.QApplication.clipboard()
        clipboard_data = clipboard.text()

        if not clipboard_data:
            return

        rows = clipboard_data.splitlines()
        start_row = self.currentRow()
        start_column = self.currentColumn()

        for i, row in enumerate(rows):
            columns = row.split('\t')
            for j, text in enumerate(columns):
                item = self.item(start_row + i, start_column + j)
                if not item:
                    item = QtWidgets.QTableWidgetItem()
                    self.setItem(start_row + i, start_column + j, item)
                item.setText(text)

    def clear_selection(self):
        selected_ranges = self.selectedRanges()
        for selection_range in selected_ranges:
            for row in range(selection_range.topRow(), selection_range.bottomRow() + 1):
                for col in range(selection_range.leftColumn(), selection_range.rightColumn() + 1):
                    item = self.item(row, col)
                    if item:
                        item.setText("")


class UnitManagementTable(QtWidgets.QTableWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setColumnCount(4)
        self.setHorizontalHeaderLabels(["Column", "Unit Type", "Default Units", "Plot Units"])
        self.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)


class PlotDataTable(QtWidgets.QTableWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setColumnCount(14)  # Increased from 13 to 14
        self.setHorizontalHeaderLabels([
            "X Data", "Y Data", "Start Row", "End Row", "X Label", "Y Label", "Title",
            "Zero Threshold", "Threshold Value", "X Scale", "Y Scale", "X Add", "Y Add",
            "Transformations"
        ])
        self.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)

class ReplicaXRecorderReader(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Recorder Reader")
        self.resize(1200, 800)
        self.current_file_path = None
        # Create a permanent label in the status bar
        self.status_label = QtWidgets.QLabel("No file opened")
        self.statusBar().addWidget(self.status_label)  # Changed from addPermanentWidget to addWidget

        self.unit_manager = ReplicaXUnits()
        self.tab_widget = QtWidgets.QTabWidget()
        self.setCentralWidget(self.tab_widget)

        # Tab: Data Table (with default units)
        self.data_table = ReplicaXLegacyTable(10, 5)
        self.tab_widget.addTab(self.data_table, "Table Data")

        # Tab: Plot Data (with converted units)
        self.plot_data_table = ReplicaXLegacyTable(10, 5)
        self.tab_widget.addTab(self.plot_data_table, "Plot Data")

        # Tab: Unit Management
        self.unit_management_tab = QtWidgets.QWidget()
        self.unit_management_layout = QtWidgets.QVBoxLayout()
        self.unit_management_table = UnitManagementTable()
        self.unit_management_layout.addWidget(self.unit_management_table)
        self.unit_management_tab.setLayout(self.unit_management_layout)
        self.tab_widget.addTab(self.unit_management_tab, "Unit Management")

        # Tab: Set Plots
        self.set_plots_tab = QtWidgets.QWidget()
        self.set_plots_layout = QtWidgets.QVBoxLayout()
        self.set_plots_table = PlotDataTable()
        self.set_plots_layout.addWidget(self.set_plots_table)
        self.set_plots_tab.setLayout(self.set_plots_layout)
        self.tab_widget.addTab(self.set_plots_tab, "Set Plots")

        # Tab: Plots
        self.plots_tab = QtWidgets.QWidget()
        self.plots_layout = QtWidgets.QVBoxLayout()
        self.plots_scroll_area = QtWidgets.QScrollArea()
        self.plots_scroll_area.setWidgetResizable(True)
        self.plots_scroll_content = QtWidgets.QWidget()
        self.plots_scroll_layout = QtWidgets.QVBoxLayout(self.plots_scroll_content)
        self.plots_scroll_area.setWidget(self.plots_scroll_content)
        self.plots_layout.addWidget(self.plots_scroll_area)
        self.plots_tab.setLayout(self.plots_layout)
        self.tab_widget.addTab(self.plots_tab, "Plots")

        self._create_menu()
        self._create_buttons()

        # Disable tabs and save button initially
        self.set_ui_state(False)

    def _create_menu(self):
        menu_bar = self.menuBar()
        file_menu = menu_bar.addMenu("File")

        open_file_action = QtGui.QAction("Open File", self)
        open_file_action.triggered.connect(self.open_file)
        file_menu.addAction(open_file_action)

        self.save_with_metadata_action = QtGui.QAction("Save with Metadata", self)
        self.save_with_metadata_action.triggered.connect(self.save_with_metadata)
        file_menu.addAction(self.save_with_metadata_action)

        load_with_metadata_action = QtGui.QAction("Load with Metadata", self)
        load_with_metadata_action.triggered.connect(self.load_with_metadata)
        file_menu.addAction(load_with_metadata_action)

        # Add new action for combining files
        merge_files_with_sum_values_action = QtGui.QAction("Merge Files (Sum Values)", self)
        merge_files_with_sum_values_action.triggered.connect(self.combine_files)
        file_menu.addAction(merge_files_with_sum_values_action)

        # Add action for copying metadata
        copy_metadata_to_files_action = QtGui.QAction("Copy Metadata to Files", self)
        copy_metadata_to_files_action.triggered.connect(self.copy_metadata_to_files)
        file_menu.addAction(copy_metadata_to_files_action)

        # Add new action for extending files
        combine_selected_columns_from_files_action = QtGui.QAction("Combine Selected Columns from Files", self)
        combine_selected_columns_from_files_action.triggered.connect(self.combine_selected_columns_from_files)
        file_menu.addAction(combine_selected_columns_from_files_action)

        exit_action = QtGui.QAction("Exit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

    def _create_buttons(self):
        button_layout = QtWidgets.QHBoxLayout()

        add_row_button = QtWidgets.QPushButton("Add Plot")
        add_row_button.clicked.connect(self.add_plot_data_row)
        button_layout.addWidget(add_row_button)

        remove_row_button = QtWidgets.QPushButton("Remove Last Plot")
        remove_row_button.clicked.connect(self.remove_last_plot_data_row)
        button_layout.addWidget(remove_row_button)

        plot_button = QtWidgets.QPushButton("Generate Plots")
        plot_button.clicked.connect(self.generate_plots)
        button_layout.addWidget(plot_button)

        self.set_plots_layout.addLayout(button_layout)

    def set_ui_state(self, enabled):
        # Enable/disable tabs
        for i in range(self.tab_widget.count()):
            self.tab_widget.setTabEnabled(i, enabled)
        # Enable/disable save button and menu action
        self.save_with_metadata_action.setEnabled(enabled)

    def update_status_bar(self, file_path):
        self.status_label.setText(f"Current file: {file_path}")

    ### -------------------------- START ACTION open_file
    
    def open_file(self):
        file_path, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Open Recorder File", "", "Out Files (*.out);;Dat Files (*.dat);;All Files (*)")
        if file_path:
            self.reset_plots()  # Always reset plots when opening a new file
            self.load_file(file_path)
            self.current_file_path = file_path
            self.set_ui_state(True)  # Enable UI elements after file is loaded
            self.update_status_bar(file_path)

    def load_file(self, file_path):
        with open(file_path, 'r') as file:
            data = [line.split() for line in file.readlines()]

        data = np.array(data, dtype=float)
        num_rows, num_cols = data.shape

        self.data_table.setRowCount(num_rows)
        self.data_table.setColumnCount(num_cols)
        self.plot_data_table.setRowCount(num_rows)
        self.plot_data_table.setColumnCount(num_cols)

        self.fill_default_headers(num_cols)
        self.update_status_bar(file_path)

        for row_idx in range(num_rows):
            for col_idx in range(num_cols):
                value = str(data[row_idx, col_idx])
                self.data_table.setItem(row_idx, col_idx, QtWidgets.QTableWidgetItem(value))
                self.plot_data_table.setItem(row_idx, col_idx, QtWidgets.QTableWidgetItem(value))

        self.fill_unit_management_table()
        self.fill_set_plots_table()

    def fill_default_headers(self, num_cols):
        headers = [f"Column {col + 1} [Unitless]" for col in range(num_cols)]
        self.data_table.setHorizontalHeaderLabels(headers)
        self.plot_data_table.setHorizontalHeaderLabels(headers)

    def fill_unit_management_table(self):
        headers = [self.data_table.horizontalHeaderItem(col).text() for col in range(self.data_table.columnCount())]
        self.unit_management_table.setRowCount(len(headers))

        for col, header in enumerate(headers):
            column_name_item = QtWidgets.QTableWidgetItem(header.split('[')[0].strip())
            self.unit_management_table.setItem(col, 0, column_name_item)
            column_name_item.setFlags(column_name_item.flags() | QtCore.Qt.ItemIsEditable)

            unit_type_combo = QtWidgets.QComboBox()
            unit_type_combo.addItems(["Unitless"] + self.unit_manager.unit_names)
            self.unit_management_table.setCellWidget(col, 1, unit_type_combo)

            default_units_combo = QtWidgets.QComboBox()
            self.unit_management_table.setCellWidget(col, 2, default_units_combo)

            plot_units_combo = QtWidgets.QComboBox()
            self.unit_management_table.setCellWidget(col, 3, plot_units_combo)

            unit_type_combo.currentTextChanged.connect(lambda unit_type, d_combo=default_units_combo, p_combo=plot_units_combo, col=col: self.update_units_combos(d_combo, p_combo, unit_type, col))
            self.update_units_combos(default_units_combo, plot_units_combo, "Unitless", col)  # Initialize with Unitless

        self.unit_management_table.itemChanged.connect(self.update_column_name)
    
    def fill_set_plots_table(self):
        headers = [self.plot_data_table.horizontalHeaderItem(col).text() for col in range(self.plot_data_table.columnCount())]
        self.set_plots_table.setRowCount(1)

        for col in range(2):
            combo = QtWidgets.QComboBox()
            combo.addItems(headers)
            self.set_plots_table.setCellWidget(0, col, combo)

        # Add Start Row and End Row
        start_row = QtWidgets.QSpinBox()
        start_row.setMinimum(0)
        start_row.setMaximum(self.plot_data_table.rowCount() - 1)
        self.set_plots_table.setCellWidget(0, 2, start_row)

        end_row = QtWidgets.QSpinBox()
        end_row.setMinimum(0)
        end_row.setMaximum(self.plot_data_table.rowCount() - 1)
        end_row.setValue(self.plot_data_table.rowCount() - 1)
        self.set_plots_table.setCellWidget(0, 3, end_row)

        # Add X Label, Y Label, and Title
        x_label = QtWidgets.QLineEdit()
        y_label = QtWidgets.QLineEdit()
        title = QtWidgets.QLineEdit()
        self.set_plots_table.setCellWidget(0, 4, x_label)
        self.set_plots_table.setCellWidget(0, 5, y_label)
        self.set_plots_table.setCellWidget(0, 6, title)

        # Add Zero Threshold checkbox and value
        zero_threshold = QtWidgets.QCheckBox("Apply")
        self.set_plots_table.setCellWidget(0, 7, zero_threshold)

        threshold_value = QtWidgets.QDoubleSpinBox()
        threshold_value.setRange(0, 1)
        threshold_value.setDecimals(15)
        threshold_value.setValue(0.00000000001)
        threshold_value.setSingleStep(0.00000000001)
        self.set_plots_table.setCellWidget(0, 8, threshold_value)

        # Add X and Y Scale factors
        x_scale = QtWidgets.QDoubleSpinBox()
        x_scale.setRange(-1e9, 1e9)
        x_scale.setValue(1.0)
        x_scale.setDecimals(6)
        self.set_plots_table.setCellWidget(0, 9, x_scale)

        y_scale = QtWidgets.QDoubleSpinBox()
        y_scale.setRange(-1e9, 1e9)
        y_scale.setValue(1.0)
        y_scale.setDecimals(6)
        self.set_plots_table.setCellWidget(0, 10, y_scale)

        # Add X and Y constant additions
        x_add = QtWidgets.QDoubleSpinBox()
        x_add.setRange(-1e9, 1e9)
        x_add.setValue(0.0)
        x_add.setDecimals(6)
        self.set_plots_table.setCellWidget(0, 11, x_add)

        y_add = QtWidgets.QDoubleSpinBox()
        y_add.setRange(-1e9, 1e9)
        y_add.setValue(0.0)
        y_add.setDecimals(6)
        self.set_plots_table.setCellWidget(0, 12, y_add)

        # Add checkbox for showing transformations in labels
        show_transformations = QtWidgets.QCheckBox("Show")
        show_transformations.setChecked(True)  # Default to showing transformations
        self.set_plots_table.setCellWidget(0, 13, show_transformations)

    ### -------------------------- END ACTION open_file


    ### -------------------------- START ACTION save_with_metadata
    
    def save_with_metadata(self):
        if not self.current_file_path:
            QtWidgets.QMessageBox.warning(self, "Error", "No file is currently open. Please open a file first.")
            return

        json_path = os.path.splitext(self.current_file_path)[0] + '.json'
        
        data = {
            "data_file_name": os.path.basename(self.current_file_path),  # Save the data file name
            "unit_management": self.serialize_unit_management(),
            "set_plots": self.serialize_set_plots()
        }
        
        try:
            with open(json_path, 'w') as json_file:
                json.dump(data, json_file, indent=2)
            QtWidgets.QMessageBox.information(self, "Success", f"Data saved successfully to {json_path}!")
        except Exception as e:
            QtWidgets.QMessageBox.warning(self, "Error", f"Failed to save data: {str(e)}")

    def serialize_unit_management(self):
        data = []
        for row in range(self.unit_management_table.rowCount()):
            row_data = {
                "column": self.unit_management_table.item(row, 0).text(),
                "unit_type": self.unit_management_table.cellWidget(row, 1).currentText(),
                "default_units": self.unit_management_table.cellWidget(row, 2).currentText(),
                "plot_units": self.unit_management_table.cellWidget(row, 3).currentText()
            }
            data.append(row_data)
        return data

    def serialize_set_plots(self):
        data = []
        for row in range(self.set_plots_table.rowCount()):
            row_data = {
                "x_column": self.set_plots_table.cellWidget(row, 0).currentText(),
                "y_column": self.set_plots_table.cellWidget(row, 1).currentText(),
                "start_row": self.set_plots_table.cellWidget(row, 2).value(),
                "end_row": self.set_plots_table.cellWidget(row, 3).value(),
                "x_label": self.set_plots_table.cellWidget(row, 4).text(),
                "y_label": self.set_plots_table.cellWidget(row, 5).text(),
                "title": self.set_plots_table.cellWidget(row, 6).text()
            }
            data.append(row_data)
        return data
    
    ### -------------------------- END ACTION save_with_metadata
    
    
    ### -------------------------- START ACTION load_with_metadata    
    
    def load_with_metadata(self):
        file_path, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Load All Information", "", "JSON Files (*.json)")
        if file_path:
            try:
                with open(file_path, 'r') as json_file:
                    data = json.load(json_file)
                
                # Load the corresponding data file
                data_file_name = data.get("data_file_name")
                if not data_file_name:
                    QtWidgets.QMessageBox.warning(self, "Error", "JSON file does not contain data file information.")
                    return

                data_file_path = os.path.join(os.path.dirname(file_path), data_file_name)
                if os.path.exists(data_file_path):
                    self.reset_plots()  # Always reset plots when loading new metadata
                    self.load_file(data_file_path)
                    self.current_file_path = data_file_path
                    self.update_status_bar(data_file_path)
                else:
                    QtWidgets.QMessageBox.warning(self, "Warning", f"Corresponding data file not found: {data_file_path}")
                    return
                
                # Update unit management and set plots
                self.update_unit_management(data.get('unit_management', []))
                self.update_set_plots(data.get('set_plots', []))
                
                self.set_ui_state(True)  # Enable UI elements after data is loaded
                QtWidgets.QMessageBox.information(self, "Success", "Data loaded successfully!")
            except Exception as e:
                QtWidgets.QMessageBox.warning(self, "Error", f"An error occurred while loading the file: {str(e)}")

    def update_unit_management(self, data):
        for row, row_data in enumerate(data):
            self.unit_management_table.setItem(row, 0, QtWidgets.QTableWidgetItem(row_data["column"]))
            self.unit_management_table.cellWidget(row, 1).setCurrentText(row_data["unit_type"])
            self.unit_management_table.cellWidget(row, 2).setCurrentText(row_data["default_units"])
            self.unit_management_table.cellWidget(row, 3).setCurrentText(row_data["plot_units"])
        self.update_plot_data_table()

    def update_set_plots(self, data):
        # Remove existing rows except the first one
        while self.set_plots_table.rowCount() > 1:
            self.set_plots_table.removeRow(1)
        
        # Add new rows and update data
        for i, row_data in enumerate(data):
            if i > 0:  # Skip the first row as it already exists
                self.add_plot_data_row()
            row = i
            self.set_plots_table.cellWidget(row, 0).setCurrentText(row_data["x_column"])
            self.set_plots_table.cellWidget(row, 1).setCurrentText(row_data["y_column"])
            self.set_plots_table.cellWidget(row, 2).setValue(row_data["start_row"])
            self.set_plots_table.cellWidget(row, 3).setValue(row_data["end_row"])
            self.set_plots_table.cellWidget(row, 4).setText(row_data["x_label"])
            self.set_plots_table.cellWidget(row, 5).setText(row_data["y_label"])
            self.set_plots_table.cellWidget(row, 6).setText(row_data["title"])

    ### -------------------------- END ACTION load_with_metadata    


    ### -------------------------- START ACTION combine_files   

    def combine_files(self):
        file_paths, _ = QtWidgets.QFileDialog.getOpenFileNames(self, "Select Files to Combine", "", "Out Files (*.out);;Dat Files (*.dat);;All Files (*)")
        if not file_paths:
            return

        # Ask user if the first column is time
        is_time_column = QtWidgets.QMessageBox.question(self, "Time Column", "Is the first column a time column?",
                                                        QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
        is_time_column = is_time_column == QtWidgets.QMessageBox.Yes

        combined_data = None
        first_column = None
        combined_units = None

        for file_path in file_paths:
            data, units = self.load_file_for_combining(file_path)
            if data is None:
                continue

            if combined_data is None:
                combined_data = data
                first_column = data[:, 0]
                combined_units = units
            else:
                # Check if first columns match if it's a time column
                if is_time_column and not np.array_equal(data[:, 0], first_column):
                    QtWidgets.QMessageBox.warning(self, "Error", f"Time values in {file_path} do not match the first file. Files cannot be combined.")
                    return

                # Check if units are consistent
                if not self.check_units_consistency(combined_units, units):
                    QtWidgets.QMessageBox.warning(self, "Error", f"Unit information in {file_path} does not match other files. Files cannot be combined.")
                    return

                # Add data (excluding first column if it's time)
                if is_time_column:
                    combined_data[:, 1:] += data[:, 1:]
                else:
                    combined_data += data

        if combined_data is None:
            QtWidgets.QMessageBox.warning(self, "Error", "No valid data files were selected.")
            return

        self.save_combined_data(combined_data, combined_units, file_paths)

    def load_file_for_combining(self, file_path):
        try:
            with open(file_path, 'r') as file:
                data = [line.split() for line in file.readlines()]
            data_array = np.array(data, dtype=float)

            # Check for corresponding JSON file
            json_path = os.path.splitext(file_path)[0] + '.json'
            units = None
            if os.path.exists(json_path):
                with open(json_path, 'r') as json_file:
                    json_data = json.load(json_file)
                    units = json_data.get('unit_management')

            return data_array, units
        except Exception as e:
            QtWidgets.QMessageBox.warning(self, "Error", f"Failed to load file {file_path}: {str(e)}")
            return None, None

    def check_units_consistency(self, units1, units2):
        if units1 is None or units2 is None:
            return True  # If either file doesn't have units, we consider it consistent
        if len(units1) != len(units2):
            return False
        for u1, u2 in zip(units1, units2):
            if u1['default_units'] != u2['default_units']:
                return False
        return True

    def save_combined_data(self, combined_array, units, original_file_paths):
        save_path, _ = QtWidgets.QFileDialog.getSaveFileName(self, "Save Combined File", "", "Out Files (*.out);;Dat Files (*.dat);;All Files (*)")
        if not save_path:
            return

        try:
            # Save the combined data
            np.savetxt(save_path, combined_array, fmt='%.15e', delimiter=' ')

            # Prepare JSON data
            json_data = {
                "data_file_name": os.path.basename(save_path),
                "original_files": [os.path.basename(path) for path in original_file_paths],
                "unit_management": units if units else []
            }

            # Save the JSON file
            json_path = os.path.splitext(save_path)[0] + '.json'
            with open(json_path, 'w') as json_file:
                json.dump(json_data, json_file, indent=2)

            QtWidgets.QMessageBox.information(self, "Success", f"Combined data saved successfully to {save_path} with associated JSON file!")
        except Exception as e:
            QtWidgets.QMessageBox.warning(self, "Error", f"Failed to save combined data: {str(e)}")

    ### -------------------------- END ACTION combine_files   


    ### -------------------------- START ACTION copy_metadata_to_files  
    
    def copy_metadata_to_files(self):
        # Select the source file (with existing metadata)
        source_file, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Select Source File with Metadata", "", "JSON Files (*.json)")
        if not source_file:
            return

        # Load the source metadata
        try:
            with open(source_file, 'r') as json_file:
                source_metadata = json.load(json_file)
        except Exception as e:
            QtWidgets.QMessageBox.warning(self, "Error", f"Failed to load source metadata: {str(e)}")
            return

        # Select the target files
        target_files, _ = QtWidgets.QFileDialog.getOpenFileNames(self, "Select Target Files", "", "Out Files (*.out);;Dat Files (*.dat);;All Files (*)")
        if not target_files:
            return

        # Copy metadata to each target file
        for target_file in target_files:
            target_json = os.path.splitext(target_file)[0] + '.json'
            
            # Check if the target JSON file already exists
            if os.path.exists(target_json):
                try:
                    with open(target_json, 'r') as json_file:
                        existing_metadata = json.load(json_file)
                except Exception as e:
                    QtWidgets.QMessageBox.warning(self, "Error", f"Failed to load existing metadata for {target_file}: {str(e)}")
                    continue
            else:
                existing_metadata = {}

            # Update the existing metadata with the source metadata
            existing_metadata.update(source_metadata)
            
            # Ensure the data_file_name is correct for this file
            existing_metadata['data_file_name'] = os.path.basename(target_file)
            
            # Save the updated metadata
            try:
                with open(target_json, 'w') as json_file:
                    json.dump(existing_metadata, json_file, indent=2)
            except Exception as e:
                QtWidgets.QMessageBox.warning(self, "Error", f"Failed to save metadata for {target_file}: {str(e)}")
                continue

        QtWidgets.QMessageBox.information(self, "Success", "Metadata updated for selected files successfully!")

    ### -------------------------- END ACTION copy_metadata_to_files  


    ### -------------------------- START ACTION combine_selected_columns_from_files  
    
    def combine_selected_columns_from_files(self):
        file_paths, _ = QtWidgets.QFileDialog.getOpenFileNames(self, "Select Files to Extend Horizontally", "", "Out Files (*.out);;Dat Files (*.dat);;All Files (*)")
        if not file_paths:
            return

        all_data = []
        all_units = []
        all_metadata = []

        for file_path in file_paths:
            data, units, metadata = self.load_file_with_metadata(file_path)
            if data is None:
                continue
            
            all_data.append(data)
            all_units.append(units if units else [])
            all_metadata.append(metadata)

        if not all_data:
            QtWidgets.QMessageBox.warning(self, "Error", "No valid data files were selected.")
            return

        selected_columns = self.get_column_selection(all_metadata)
        if not selected_columns:
            return  # User cancelled the selection

        extended_array, extended_units, extended_headers = self.process_selected_columns(all_data, all_units, all_metadata, selected_columns)

        self.save_combined_selected_columns_from_files(extended_array, extended_units, extended_headers, file_paths)

        ###3
    
    def load_file_with_metadata(self, file_path):
        data, units = self.load_file_for_combining(file_path)
        if data is None:
            return None, None, None

        json_path = os.path.splitext(file_path)[0] + '.json'
        file_name = os.path.basename(file_path)
        column_names = None

        if os.path.exists(json_path):
            try:
                with open(json_path, 'r') as json_file:
                    metadata = json.load(json_file)
                    column_names = metadata.get('column_names')
                    if not column_names:
                        column_names = [unit.get('column') for unit in metadata.get('unit_management', [])]
            except Exception as e:
                print(f"Error loading metadata for {file_path}: {str(e)}")

        if not column_names:
            column_names = [f"Column{i+1}" for i in range(data.shape[1])]

        return data, units, {'file_name': file_name, 'column_names': column_names}
    
    def get_column_selection(self, all_metadata):
        dialog = QtWidgets.QDialog(self)
        dialog.setWindowTitle("Select Columns to Include")
        dialog.resize(600, 400)  # Set a reasonable default size
        main_layout = QtWidgets.QVBoxLayout(dialog)

        scroll_area = QtWidgets.QScrollArea()
        scroll_area.setWidgetResizable(True)
        main_layout.addWidget(scroll_area)

        scroll_content = QtWidgets.QWidget()
        scroll_layout = QtWidgets.QVBoxLayout(scroll_content)

        checkboxes = []
        for file_idx, metadata in enumerate(all_metadata):
            file_name = metadata['file_name']
            group_box = QtWidgets.QGroupBox(f"File: {file_name}")
            group_layout = QtWidgets.QVBoxLayout(group_box)
            file_checkboxes = []

            for column_name in metadata['column_names']:
                checkbox = QtWidgets.QCheckBox(column_name)
                group_layout.addWidget(checkbox)
                file_checkboxes.append(checkbox)

            checkboxes.append(file_checkboxes)
            scroll_layout.addWidget(group_box)

        scroll_area.setWidget(scroll_content)

        button_box = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel)
        button_box.accepted.connect(dialog.accept)
        button_box.rejected.connect(dialog.reject)
        main_layout.addWidget(button_box)

        result = dialog.exec_()
        if result == QtWidgets.QDialog.Accepted:
            return [[checkbox.isChecked() for checkbox in file_checkboxes] for file_checkboxes in checkboxes]
        else:
            return None

    def process_selected_columns(self, all_data, all_units, all_metadata, selected_columns):
        extended_data = []
        extended_units = []
        extended_headers = []

        for data, units, metadata, selected in zip(all_data, all_units, all_metadata, selected_columns):
            selected_data = data[:, selected]
            extended_data.append(selected_data)
            
            if units:
                extended_units.extend([unit for unit, select in zip(units, selected) if select])
            
            file_name = metadata['file_name']
            column_names = metadata['column_names']
            extended_headers.extend([f"{file_name}_{column_name}" for column_name, select in zip(column_names, selected) if select])

        extended_array = np.hstack(extended_data)

        return extended_array, extended_units, extended_headers

    def save_combined_selected_columns_from_files(self, extended_array, units, column_names, original_file_paths):
        save_path, _ = QtWidgets.QFileDialog.getSaveFileName(self, "Save Horizontally Extended File", "", "Out Files (*.out);;Dat Files (*.dat);;All Files (*)")
        if not save_path:
            return

        try:
            np.savetxt(save_path, extended_array, fmt='%.6e', delimiter=' ')

            json_data = {
                "data_file_name": os.path.basename(save_path),
                "original_files": [os.path.basename(path) for path in original_file_paths],
                "unit_management": units if units else [],
                "column_names": column_names
            }

            json_path = os.path.splitext(save_path)[0] + '.json'
            with open(json_path, 'w') as json_file:
                json.dump(json_data, json_file, indent=2)

            QtWidgets.QMessageBox.information(self, "Success", f"Horizontally extended data saved successfully to {save_path} with associated JSON file!")
        except Exception as e:
            QtWidgets.QMessageBox.warning(self, "Error", f"Failed to save horizontally extended data: {str(e)}")

    ### -------------------------- END ACTION combine_selected_columns_from_files  


    ### --------------------------START  GENERAL FUNCTIONS FOR TABLE DATA INTERACTIONS
    
    def get_column_data(self, column_name, table):
        column_name_base = column_name.split('[')[0].strip()
        column_index = next(i for i in range(table.columnCount()) if table.horizontalHeaderItem(i).text().startswith(column_name_base))
        return [float(table.item(row, column_index).text()) for row in range(table.rowCount())]
    
    def get_column_units(self, col):
        unit_type_widget = self.unit_management_table.cellWidget(col, 1)
        default_unit_widget = self.unit_management_table.cellWidget(col, 2)
        plot_unit_widget = self.unit_management_table.cellWidget(col, 3)
        
        if unit_type_widget and default_unit_widget and plot_unit_widget:
            unit_type = unit_type_widget.currentText()
            default_unit = default_unit_widget.currentText()
            plot_unit = plot_unit_widget.currentText()
            return unit_type, default_unit, plot_unit
        else:
            return None, None, None

    def convert_data(self, data, unit_type, from_unit, to_unit):
        if unit_type == "Unitless" or from_unit == to_unit or not from_unit or not to_unit:
            return data
        try:
            return [self.unit_manager.convert(value, unit_type.replace(' ', '_'), from_unit, to_unit) for value in data]
        except KeyError:
            print(f"Conversion error: {unit_type}, {from_unit} to {to_unit}")
            return data
   
    ### --------------------------END  GENERAL FUNCTIONS FOR TABLE DATA INTERACTIONS
    

    ### --------------------------START  # Tab: Unit Management
    
    def update_units_combos(self, default_combo, plot_combo, unit_type, col):
        default_combo.clear()
        plot_combo.clear()
        if unit_type == "Unitless":
            default_combo.addItem("Unitless")
            plot_combo.addItem("Unitless")
        else:
            units = list(self.unit_manager.units[unit_type.replace(' ', '_')].keys())
            default_combo.addItems(units)
            plot_combo.addItems(units)
            default_combo.setCurrentIndex(0)  # Set first unit as default
            # Don't change plot units automatically
        
        column_name = self.unit_management_table.item(col, 0).text()
        new_header = f"{column_name} [{default_combo.currentText()}]"
        self.data_table.setHorizontalHeaderItem(col, QtWidgets.QTableWidgetItem(new_header))
        
        # Only update plot data table header if plot units have changed
        plot_header = f"{column_name} [{plot_combo.currentText()}]"
        self.plot_data_table.setHorizontalHeaderItem(col, QtWidgets.QTableWidgetItem(plot_header))

        default_combo.currentTextChanged.connect(lambda: self.update_data_table_header(col))
        plot_combo.currentTextChanged.connect(lambda: self.update_plot_data_table_header(col))
        self.update_set_plots_table()
        self.update_plot_data_table()

    def update_column_name(self, item):
        if item.column() == 0:  # Only update if the change is in the first column (Column Name)
            col = item.row()
            new_name = item.text()
            current_header = self.data_table.horizontalHeaderItem(col).text()
            current_units = current_header.split('[')[-1].strip(']') if '[' in current_header else "Unitless"
            new_header = f"{new_name} [{current_units}]"
            
            self.data_table.setHorizontalHeaderItem(col, QtWidgets.QTableWidgetItem(new_header))
            self.plot_data_table.setHorizontalHeaderItem(col, QtWidgets.QTableWidgetItem(new_header))
            self.update_set_plots_table()
    
    def update_set_plots_table(self):
        headers = [self.plot_data_table.horizontalHeaderItem(col).text() for col in range(self.plot_data_table.columnCount())]
        for row in range(self.set_plots_table.rowCount()):
            for col in range(2):  # Update only X and Y data columns
                combo = self.set_plots_table.cellWidget(row, col)
                current_selection = combo.currentText()
                combo.clear()
                combo.addItems(headers)
                if current_selection in headers:
                    combo.setCurrentText(current_selection)

    def update_plot_data_table(self):
        for col in range(self.data_table.columnCount()):
            data = self.get_column_data(self.data_table.horizontalHeaderItem(col).text(), self.data_table)
            unit_type, default_unit, plot_unit = self.get_column_units(col)
            if unit_type is not None and default_unit and plot_unit:
                converted_data = self.convert_data(data, unit_type, default_unit, plot_unit)
                for row, value in enumerate(converted_data):
                    self.plot_data_table.setItem(row, col, QtWidgets.QTableWidgetItem(str(value)))

    def update_data_table_header(self, col):
        column_name = self.unit_management_table.item(col, 0).text()
        plot_units = self.unit_management_table.cellWidget(col, 3).currentText()
        new_header = f"{column_name} [{plot_units}]"
        self.plot_data_table.setHorizontalHeaderItem(col, QtWidgets.QTableWidgetItem(new_header))
        self.update_set_plots_table()
        self.update_plot_data_table()

    def update_data_table_header(self, col):
        column_name = self.unit_management_table.item(col, 0).text()
        default_units = self.unit_management_table.cellWidget(col, 2).currentText()
        new_header = f"{column_name} [{default_units}]"
        self.data_table.setHorizontalHeaderItem(col, QtWidgets.QTableWidgetItem(new_header))
        self.update_set_plots_table()
        self.update_plot_data_table()

    def update_plot_data_table_header(self, col):
        column_name = self.unit_management_table.item(col, 0).text()
        plot_units = self.unit_management_table.cellWidget(col, 3).currentText()
        new_header = f"{column_name} [{plot_units}]"
        self.plot_data_table.setHorizontalHeaderItem(col, QtWidgets.QTableWidgetItem(new_header))
        self.update_set_plots_table()
        self.update_plot_data_table()
    
    ### --------------------------END  # Tab: Unit Management


    ### --------------------------START  # Tab: Set Plots
    
    def add_plot_data_row(self):
        row = self.set_plots_table.rowCount()
        self.set_plots_table.insertRow(row)
        headers = [self.plot_data_table.horizontalHeaderItem(col).text() for col in range(self.plot_data_table.columnCount())]
        
        for col in range(2):
            combo = QtWidgets.QComboBox()
            combo.addItems(headers)
            self.set_plots_table.setCellWidget(row, col, combo)

        # Add Start Row and End Row
        start_row = QtWidgets.QSpinBox()
        start_row.setMinimum(0)
        start_row.setMaximum(self.plot_data_table.rowCount() - 1)
        self.set_plots_table.setCellWidget(row, 2, start_row)

        end_row = QtWidgets.QSpinBox()
        end_row.setMinimum(0)
        end_row.setMaximum(self.plot_data_table.rowCount() - 1)
        end_row.setValue(self.plot_data_table.rowCount() - 1)
        self.set_plots_table.setCellWidget(row, 3, end_row)

        # Add X Label, Y Label, and Title
        x_label = QtWidgets.QLineEdit()
        y_label = QtWidgets.QLineEdit()
        title = QtWidgets.QLineEdit()
        self.set_plots_table.setCellWidget(row, 4, x_label)
        self.set_plots_table.setCellWidget(row, 5, y_label)
        self.set_plots_table.setCellWidget(row, 6, title)

        # Add Zero Threshold checkbox and value
        zero_threshold = QtWidgets.QCheckBox("Apply")
        self.set_plots_table.setCellWidget(row, 7, zero_threshold)

        threshold_value = QtWidgets.QDoubleSpinBox()
        threshold_value.setRange(0, 1)
        threshold_value.setDecimals(15)
        threshold_value.setValue(0.00000000001)
        threshold_value.setSingleStep(0.00000000001)
        self.set_plots_table.setCellWidget(row, 8, threshold_value)

        # Add X and Y Scale factors
        x_scale = QtWidgets.QDoubleSpinBox()
        x_scale.setRange(-1e9, 1e9)
        x_scale.setValue(1.0)
        x_scale.setDecimals(6)
        self.set_plots_table.setCellWidget(row, 9, x_scale)

        y_scale = QtWidgets.QDoubleSpinBox()
        y_scale.setRange(-1e9, 1e9)
        y_scale.setValue(1.0)
        y_scale.setDecimals(6)
        self.set_plots_table.setCellWidget(row, 10, y_scale)

        # Add X and Y constant additions
        x_add = QtWidgets.QDoubleSpinBox()
        x_add.setRange(-1e9, 1e9)
        x_add.setValue(0.0)
        x_add.setDecimals(6)
        self.set_plots_table.setCellWidget(row, 11, x_add)

        y_add = QtWidgets.QDoubleSpinBox()
        y_add.setRange(-1e9, 1e9)
        y_add.setValue(0.0)
        y_add.setDecimals(6)
        self.set_plots_table.setCellWidget(row, 12, y_add)

        # Add checkbox for showing transformations in labels
        show_transformations = QtWidgets.QCheckBox("Show")
        show_transformations.setChecked(True)  # Default to showing transformations
        self.set_plots_table.setCellWidget(row, 13, show_transformations)



    def remove_last_plot_data_row(self):
        row_count = self.set_plots_table.rowCount()
        if row_count > 1:
            self.set_plots_table.removeRow(row_count - 1)

    def generate_plots(self):
        for i in reversed(range(self.plots_scroll_layout.count())): 
            self.plots_scroll_layout.itemAt(i).widget().setParent(None)

        plot_data = []
        for row in range(self.set_plots_table.rowCount()):
            x_column = self.set_plots_table.cellWidget(row, 0).currentText()
            y_column = self.set_plots_table.cellWidget(row, 1).currentText()
            start_row = self.set_plots_table.cellWidget(row, 2).value()
            end_row = self.set_plots_table.cellWidget(row, 3).value()
            x_label = self.set_plots_table.cellWidget(row, 4).text() or x_column
            y_label = self.set_plots_table.cellWidget(row, 5).text() or y_column
            title = self.set_plots_table.cellWidget(row, 6).text() or f"{y_label} vs {x_label}"
            apply_zero_threshold = self.set_plots_table.cellWidget(row, 7).isChecked()
            threshold_value = self.set_plots_table.cellWidget(row, 8).value()
            x_scale = self.set_plots_table.cellWidget(row, 9).value()
            y_scale = self.set_plots_table.cellWidget(row, 10).value()
            x_add = self.set_plots_table.cellWidget(row, 11).value()
            y_add = self.set_plots_table.cellWidget(row, 12).value()
            show_transformations = self.set_plots_table.cellWidget(row, 13).isChecked()

            x_data = self.get_column_data(x_column, self.plot_data_table)[start_row:end_row+1]
            y_data = self.get_column_data(y_column, self.plot_data_table)[start_row:end_row+1]

            # Apply scaling and addition
            x_data = [(x * x_scale) + x_add for x in x_data]
            y_data = [(y * y_scale) + y_add for y in y_data]

            if apply_zero_threshold:
                y_data = [0 if abs(y) < threshold_value else y for y in y_data]

            # Update labels to reflect transformations if the option is checked
            if show_transformations:
                x_transform = []
                y_transform = []
                
                if x_scale != 1.0:
                    x_transform.append(f"x{x_scale}")
                if x_add != 0.0:
                    x_transform.append(f"{'+' if x_add > 0 else '-'}{abs(x_add)}")
                if x_transform:
                    x_label += f" ({' '.join(x_transform)})"
                
                if y_scale != 1.0:
                    y_transform.append(f"x{y_scale}")
                if y_add != 0.0:
                    y_transform.append(f"{'+' if y_add > 0 else '-'}{abs(y_add)}")
                if y_transform:
                    y_label += f" ({' '.join(y_transform)})"
                
                if apply_zero_threshold:
                    y_label += f" (Zero < {threshold_value})"

            plot_data.append((x_data, y_data, x_label, y_label, title))

        num_plots = len(plot_data)
        rows, cols = self.calculate_grid_layout(num_plots)

        figure = Figure(figsize=(5*cols, 4*rows), dpi=100)
        canvas = FigureCanvas(figure)

        for i, (x_data, y_data, x_label, y_label, title) in enumerate(plot_data):
            # Calculate subplot position with vertical-first, then horizontal priority
            row = i % rows
            col = i // rows
            ax = figure.add_subplot(rows, cols, row * cols + col + 1)
            
            ax.plot(x_data, y_data)
            ax.set_xlabel(x_label)
            ax.set_ylabel(y_label)
            ax.set_title(title)
            ax.grid(True, which='major', linestyle='-', linewidth=0.5)
            ax.grid(True, which='minor', linestyle=':', linewidth=0.5)
            ax.minorticks_on()

        figure.tight_layout()
        toolbar = NavigationToolbar(canvas, self)
        
        plot_widget = QtWidgets.QWidget()
        plot_layout = QtWidgets.QVBoxLayout(plot_widget)
        plot_layout.addWidget(toolbar)
        plot_layout.addWidget(canvas)
        
        self.plots_scroll_layout.addWidget(plot_widget)

    def calculate_grid_layout(self, num_plots):
        if num_plots <= 3:
            return num_plots, 1
        elif num_plots <= 3*6:
            return 3, math.ceil(num_plots / 3)
        else:
            base_rows = int(num_plots / 18)
            base_rows = 3+3*base_rows
            return base_rows, math.ceil(num_plots /base_rows)

    def reset_plots(self):
        # Check if the plots scroll area exists and has any widgets
        if hasattr(self, 'plots_scroll_layout') and self.plots_scroll_layout.count() > 0:
            # Clear only the matplotlib figures
            for i in reversed(range(self.plots_scroll_layout.count())): 
                widget = self.plots_scroll_layout.itemAt(i).widget()
                if isinstance(widget, QtWidgets.QWidget):
                    # Check if this widget contains a FigureCanvas
                    for child in widget.children():
                        if isinstance(child, FigureCanvas):
                            # Clear the figure
                            child.figure.clear()
                            # Update the canvas
                            child.draw()
                    # Remove the widget from the layout
                    widget.setParent(None)
    
    ### --------------------------END  # Tab: Set Plots



# def main():
#     app = QtWidgets.QApplication(sys.argv)
#     window = ReplicaXRecorderReader()
#     window.show()
#     sys.exit(app.exec())

# if __name__ == "__main__":
#     main()

