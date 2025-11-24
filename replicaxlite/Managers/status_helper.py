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

from PySide6.QtWidgets import QLabel


class StatusBarHelper:
    """Helper class for managing status bar messages"""
    
    def __init__(self, status_bar):
        self.status_bar = status_bar
        self.status_label = QLabel("")
        self.status_bar.addWidget(self.status_label, 1)  # Stretch factor
    
    def update_message(self, message, duration=0):
        """
        Show a message in the status bar
        
        Args:
            message: The message to display
            duration: Duration in milliseconds (0 = permanent)
        """
        if duration > 0:
            # Temporary message using Qt's built-in mechanism
            self.status_bar.showMessage(message, duration)
        else:
            # Permanent message using our label
            self.status_label.setText(message)
      
    def clear(self):
        """Clear the status bar message"""
        self.status_label.setText("")
        self.status_bar.clearMessage()
    
    def get_message(self):
        """Get the current status message"""
        return self.status_label.text()
