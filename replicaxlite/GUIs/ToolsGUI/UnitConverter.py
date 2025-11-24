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


from PySide6.QtWidgets import (QDoubleSpinBox, QWidget, QVBoxLayout, QHBoxLayout, 
                            QLabel, QComboBox, QPushButton, QLineEdit, QGridLayout, 
                            QDialog, QSizePolicy)
from PySide6 import QtCore
from PySide6.QtGui import QValidator

from ...UtilityAPI.UnitsAPI import ReplicaXUnits


class CustomSpinBox(QDoubleSpinBox):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setDecimals(16)
        self.setRange(-9999999999999999.0, 9999999999999999.0)

    def textFromValue(self, value):
        return f"{value:.16g}"

    def valueFromText(self, text):
        try:
            return float(text.replace(',', '.').strip())
        except ValueError:
            return 0.0

    def validate(self, text, pos):
        try:
            float(text.replace(',', '.').strip())
            return QValidator.Acceptable, text, pos
        except ValueError:
            if text.strip() in ['-', '+', '.', '']:
                return QValidator.Intermediate, text, pos
            return QValidator.Invalid, text, pos

    def fixup(self, text):
        return text.replace(',', '.').strip()


class ReplicaXUnitConverterManager(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.converter = ReplicaXUnits()
        self.create_ui()
        self.bindings()

    def create_ui(self):
        # Create main layout
        main_layout = QGridLayout(self)
        
        # Create and add labels
        main_layout.addWidget(QLabel("Quantity"), 0, 0)
        main_layout.addWidget(QLabel("Value"), 0, 1)
        main_layout.addWidget(QLabel("Unit from"), 0, 2)
        main_layout.addWidget(QLabel("Unit to"), 0, 4)
        main_layout.addWidget(QLabel("Converted Value"), 0, 5)
        
        # Create and add widgets
        self.comboBox_quantity = QComboBox()
        main_layout.addWidget(self.comboBox_quantity, 1, 0)
        
        # Value SpinBox
        self.doubleSpinBox_value_unit_from = CustomSpinBox()
        self.doubleSpinBox_value_unit_from.setMinimumWidth(150)
        main_layout.addWidget(self.doubleSpinBox_value_unit_from, 1, 1)
        
        # From Unit ComboBox
        self.comboBox_unit_from = QComboBox()
        self.comboBox_unit_from.setMinimumWidth(120)
        main_layout.addWidget(self.comboBox_unit_from, 1, 2)
        
        # Flip Units Button
        self.pushButton_flip_units = QPushButton("<->")
        self.pushButton_flip_units.setFocusPolicy(QtCore.Qt.NoFocus)
        main_layout.addWidget(self.pushButton_flip_units, 1, 3)
        
        # To Unit ComboBox
        self.comboBox_unit_to = QComboBox()
        self.comboBox_unit_to.setMinimumWidth(120)
        main_layout.addWidget(self.comboBox_unit_to, 1, 4)
        
        # Converted Value LineEdit
        self.lineEdit_unit_to = QLineEdit()
        self.lineEdit_unit_to.setReadOnly(True)
        self.lineEdit_unit_to.setMinimumWidth(200) 
        main_layout.addWidget(self.lineEdit_unit_to, 1, 5)
        
        # Fill the quantity combo box
        for unit_type in self.converter.units:
            self.comboBox_quantity.addItem(unit_type)
        
        # Set initial units
        self.fill_unit_comboboxes(self.comboBox_quantity.currentText())

    def fill_unit_comboboxes(self, unit_type):
        self.comboBox_unit_from.clear()
        self.comboBox_unit_to.clear()
        if unit_type:
            for unit in self.converter.units[unit_type]:
                self.comboBox_unit_from.addItem(unit)
                self.comboBox_unit_to.addItem(unit)
    
    def unit_converter_gui(self):
        unit_type = self.comboBox_quantity.currentText()
        from_unit = self.comboBox_unit_from.currentText()
        to_unit = self.comboBox_unit_to.currentText()
        from_value = self.doubleSpinBox_value_unit_from.value()

        if unit_type and from_unit and to_unit:
            to_value = self.converter.convert(from_value, unit_type, from_unit, to_unit)
            self.lineEdit_unit_to.setText(str(to_value))
        else:
            self.lineEdit_unit_to.clear()

    def flip_units(self):
        from_index = self.comboBox_unit_from.currentIndex()
        to_index = self.comboBox_unit_to.currentIndex()
        self.comboBox_unit_from.setCurrentIndex(to_index)
        self.comboBox_unit_to.setCurrentIndex(from_index)

    def bindings(self):
        self.comboBox_quantity.currentTextChanged.connect(self.fill_unit_comboboxes)
        self.comboBox_quantity.currentTextChanged.connect(self.unit_converter_gui)
        self.comboBox_unit_from.currentTextChanged.connect(self.unit_converter_gui)
        self.comboBox_unit_to.currentTextChanged.connect(self.unit_converter_gui)
        self.doubleSpinBox_value_unit_from.valueChanged.connect(self.unit_converter_gui)
        self.pushButton_flip_units.clicked.connect(self.flip_units)


class ReplicaXUnitConverterPopup(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Set window properties
        self.setWindowTitle("Unit Converter")
        self.setWindowFlags(self.windowFlags() | QtCore.Qt.WindowStaysOnTopHint)
        self.resize(800, 100)
        
        # Create layout
        layout = QVBoxLayout(self)
        
        # Create and add the UnitConverterWidget to the layout
        self.converter_widget = ReplicaXUnitConverterManager(self)
        layout.addWidget(self.converter_widget)
        
        # Set the window modality to non-modal so user can interact with other windows
        self.setModal(False)
        
        # Set window flags to make it a separate window
        self.setWindowFlags(QtCore.Qt.Window | 
                           QtCore.Qt.WindowMaximizeButtonHint | 
                           QtCore.Qt.WindowCloseButtonHint | 
                           QtCore.Qt.WindowStaysOnTopHint)

