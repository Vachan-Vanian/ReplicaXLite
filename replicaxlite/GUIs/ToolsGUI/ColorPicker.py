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

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                              QPushButton, QColorDialog, QDialog, QApplication)
from PySide6.QtGui import QColor
from PySide6.QtCore import Qt


class ColorPickerDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_color = QColor(255, 255, 255)
        
        # Set dialog properties
        self.setWindowTitle("Color Picker")
        self.setModal(True)  # Make it modal
        
        # Create layout
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Color display area
        self.color_display = QLabel()
        self.color_display.setFixedSize(260, 100)
        self.color_display.setStyleSheet("QLabel { background-color: white; border: 2px solid black; }")
        
        # Hex label
        self.hex_label = QLabel("Hex: #FFFFFF")
        self.hex_label.setAlignment(Qt.AlignCenter)
        self.hex_label.setStyleSheet("QLabel { font-size: 14px; margin: 5px; }")
        
        # Buttons
        button_layout = QHBoxLayout()
        self.pick_button = QPushButton("Pick Color")
        self.copy_button = QPushButton("Copy Hex")
        self.copy_button.clicked.connect(self.copy_hex_to_clipboard)
        
        # Add a close button
        self.close_button = QPushButton("Close")
        self.close_button.clicked.connect(self.accept)
        
        button_layout.addWidget(self.pick_button)
        button_layout.addWidget(self.copy_button)
        button_layout.addWidget(self.close_button)
        
        layout.addWidget(self.color_display)
        layout.addWidget(self.hex_label)
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
        
        # Connect color picker
        self.pick_button.clicked.connect(self.open_color_dialog)
        
        # Initialize display
        self.update_display()
    
    def open_color_dialog(self):
        color = QColorDialog.getColor(self.current_color, self)
        if color.isValid():
            self.current_color = color
            self.update_display()
    
    def update_display(self):
        self.color_display.setStyleSheet(f"QLabel {{ background-color: {self.current_color.name()}; border: 2px solid black; }}")
        self.hex_label.setText(f"Hex: {self.current_color.name()}")
    
    def copy_hex_to_clipboard(self):
        QApplication.clipboard().setText(self.current_color.name())
    
    def get_hex_color(self):
        return self.current_color.name()
    