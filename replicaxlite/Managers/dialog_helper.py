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

from PySide6.QtWidgets import QMessageBox, QInputDialog, QFileDialog


class DialogHelper:
    """Helper class for creating standard dialogs"""
    
    def __init__(self, parent=None):
        self.parent = parent
    
    def show_info(self, title, message):
        """Show information dialog"""
        QMessageBox.information(self.parent, title, message)
    
    def show_warning(self, title, message):
        """Show warning dialog"""
        QMessageBox.warning(self.parent, title, message)
    
    def show_error(self, title, message):
        """Show error dialog"""
        QMessageBox.critical(self.parent, title, message)
    
    def show_question(self, title, message, buttons=QMessageBox.Yes | QMessageBox.No):
        """Show question dialog and return the user's choice"""
        return QMessageBox.question(self.parent, title, message, buttons, QMessageBox.Yes)
    
    def get_text(self, title, label, default_text=""):
        """Get text input from user. Returns (text, ok)"""
        return QInputDialog.getText(self.parent, title, label, text=default_text)
    
    def get_directory(self, title, start_dir=""):
        """Get directory path from user. Returns path string or empty string if cancelled"""
        return QFileDialog.getExistingDirectory(self.parent, title, start_dir)
    
    def get_save_filename(self, title, start_dir="", filter_str="All Files (*)"):
        """Get save file path from user. Returns (filepath, selected_filter)"""
        return QFileDialog.getSaveFileName(self.parent, title, start_dir, filter_str)
    
    def get_open_filename(self, title, start_dir="", filter_str="All Files (*)"):
        """Get open file path from user. Returns (filepath, selected_filter)"""
        return QFileDialog.getOpenFileName(self.parent, title, start_dir, filter_str)
