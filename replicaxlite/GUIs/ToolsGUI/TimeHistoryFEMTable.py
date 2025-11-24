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


from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton, 
                              QMessageBox, QApplication)
from PySide6.QtCore import Qt
from ...UtilityCode.TableGUI import ReplicaXTable

class TimeHistoryDataDialog(QDialog):
    """
    A dialog for inputting time history data with acceleration, velocity, and displacement.
    
    The dialog allows users to enter time steps and corresponding values for the three
    types of motion inputs, then copy them in dictionary format suitable for use 
    with the run_time_history_analysis function.
    """
    
    def __init__(self, parent=None, settings=None):
        super().__init__(parent)
        self.settings = settings
        self.setWindowTitle("Time History Data Input")
        self.setModal(True)
        self.resize(600, 500)
        
        # Initialize table with 10000 rows and settings
        self.table = ReplicaXTable(rows=10000, columns=4, settings=self.settings)
        self.table.set_column_types(['float', 'float', 'float', 'float'])
        self.table.set_headers(['Time', 'Acceleration', 'Velocity', 'Displacement'])
        
        # Set units for columns (similar to NodeTable implementation)
        self.table.set_column_unit(0, 'Time')  # Time column
        self.table.set_column_unit(1, 'Acceleration')  # Acceleration column  
        self.table.set_column_unit(2, 'Velocity')  # Velocity column
        self.table.set_column_unit(3, 'Displacement')  # Displacement column
        
        # Add copy button
        copy_btn = QPushButton("Copy to Dictionary Format")
        copy_btn.clicked.connect(self.copy_to_dict_format)
        
        # Layout
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.table)
        main_layout.addWidget(copy_btn)
        self.setLayout(main_layout)
        
    def copy_to_dict_format(self):
        """
        Convert table data to dictionary format and copy to clipboard.
        Strict validation: 
        - Must have time and acceleration data (minimum required)
        - All motion arrays must have same length  
        - All values must be numerical
        - Data must be continuous (no None values after filtering)
        """
        # First pass: detect ALL types of illogical data
        row_count = self.table.rowCount()
        rows_missing_time = []
        rows_missing_accel = []
        rows_incomplete = []
        
        for i in range(row_count):
            try:
                time_val = self.table.get_cell_value(i, 0)
                accel_val = self.table.get_cell_value(i, 1)
                vel_val = self.table.get_cell_value(i, 2)
                disp_val = self.table.get_cell_value(i, 3)
                
                has_time = time_val is not None
                has_accel = accel_val is not None
                has_vel = vel_val is not None
                has_disp = disp_val is not None
                has_any_motion = has_accel or has_vel or has_disp
                
                # Check for illogical patterns:
                # 1. Any motion data without time
                if has_any_motion and not has_time:
                    rows_missing_time.append(i + 1)
                
                # 2. Time exists but no acceleration (acceleration is REQUIRED with time)
                elif has_time and not has_accel:
                    rows_missing_accel.append(i + 1)
                
                # 3. Velocity or displacement without acceleration
                elif (has_vel or has_disp) and not has_accel:
                    rows_incomplete.append(i + 1)
                    
            except Exception:
                continue
        
        # BLOCK copying if there's ANY illogical data
        error_messages = []
        
        if rows_missing_time:
            row_list = ", ".join(str(r) for r in rows_missing_time[:10])
            if len(rows_missing_time) > 10:
                row_list += f" ... ({len(rows_missing_time)} total)"
            error_messages.append(f"• Rows with motion data but NO TIME:\n  {row_list}")
        
        if rows_missing_accel:
            row_list = ", ".join(str(r) for r in rows_missing_accel[:10])
            if len(rows_missing_accel) > 10:
                row_list += f" ... ({len(rows_missing_accel)} total)"
            error_messages.append(f"• Rows with time but NO ACCELERATION:\n  {row_list}")
        
        if rows_incomplete:
            row_list = ", ".join(str(r) for r in rows_incomplete[:10])
            if len(rows_incomplete) > 10:
                row_list += f" ... ({len(rows_incomplete)} total)"
            error_messages.append(f"• Rows with velocity/displacement but NO ACCELERATION:\n  {row_list}")
        
        if error_messages:
            QMessageBox.critical(self, "Invalid Data Structure", 
                            f"Cannot copy data with illogical structure!\n\n"
                            + "\n\n".join(error_messages) +
                            f"\n\nFIX REQUIRED:\n"
                            f"• Every row with data must have BOTH time AND acceleration\n"
                            f"• Velocity/displacement cannot exist without acceleration")
            return
        
        # Second pass: collect valid rows
        valid_rows = []
        
        for i in range(row_count):
            try:
                time_val = self.table.get_cell_value(i, 0)
                accel_val = self.table.get_cell_value(i, 1)
                vel_val = self.table.get_cell_value(i, 2)
                disp_val = self.table.get_cell_value(i, 3)
                
                # Only include rows with both time AND acceleration
                if time_val is not None and accel_val is not None:
                    # Validate numerical values
                    try:
                        float(time_val)
                        float(accel_val)
                        if vel_val is not None:
                            float(vel_val)
                        if disp_val is not None:
                            float(disp_val)
                    except (ValueError, TypeError):
                        QMessageBox.warning(self, "Invalid Data", 
                                        f"Row {i+1} contains non-numerical values.")
                        return
                    
                    valid_rows.append({
                        'time': float(time_val),
                        'accel': float(accel_val),
                        'vel': float(vel_val) if vel_val is not None else None,
                        'disp': float(disp_val) if disp_val is not None else None
                    })
                        
            except Exception:
                continue
        
        # Validate that we have data
        if not valid_rows:
            QMessageBox.warning(self, "No Valid Data", 
                            "No valid data to copy. Please enter time and acceleration values.")
            return
        
        # Extract data for each column from valid rows
        time_data = [row['time'] for row in valid_rows]
        accel_data = [row['accel'] for row in valid_rows]
        vel_data = [row['vel'] for row in valid_rows]
        disp_data = [row['disp'] for row in valid_rows]
        
        # Check if velocity or displacement have any non-None values
        has_velocity = any(x is not None for x in vel_data)
        has_displacement = any(x is not None for x in disp_data)
        
        # Validate consistency: if we have velocity or displacement data,
        # check that they don't have gaps (all should be present or all absent)
        if has_velocity:
            none_count = sum(1 for x in vel_data if x is None)
            if none_count > 0:
                QMessageBox.warning(self, "Incomplete Data", 
                                f"Velocity data has {none_count} missing values. "
                                "All rows with time/acceleration must have velocity data, or none should.")
                return
        
        if has_displacement:
            none_count = sum(1 for x in disp_data if x is None)
            if none_count > 0:
                QMessageBox.warning(self, "Incomplete Data", 
                                f"Displacement data has {none_count} missing values. "
                                "All rows with time/acceleration must have displacement data, or none should.")
                return
        
        # Validate time is monotonically increasing
        for i in range(1, len(time_data)):
            if time_data[i] <= time_data[i-1]:
                QMessageBox.warning(self, "Invalid Time Data", 
                                f"Time values must be monotonically increasing. "
                                f"Issue at row {i+1}: {time_data[i]} <= {time_data[i-1]}")
                return
        
        # Build dictionary with clean data (all arrays have same length)
        dict_str = "{\n"
        dict_str += "    'time': [" + ", ".join(str(x) for x in time_data) + "],\n"
        dict_str += "    'accel': [" + ", ".join(str(x) for x in accel_data) + "]"
        
        # Add velocity if present (all values must be non-None at this point)
        if has_velocity:
            dict_str += ",\n    'vel': [" + ", ".join(str(x) for x in vel_data) + "]"
        
        # Add displacement if present (all values must be non-None at this point)
        if has_displacement:
            dict_str += ",\n    'disp': [" + ", ".join(str(x) for x in disp_data) + "]"
        
        dict_str += "\n}\n"
        
        # Copy to clipboard
        clipboard = QApplication.clipboard()
        clipboard.setText(dict_str)
        
        # Show confirmation with data summary
        data_summary = f"Copied {len(time_data)} data points"
        if has_velocity:
            data_summary += " (with velocity)"
        if has_displacement:
            data_summary += " (with displacement)"
        
        QMessageBox.information(self, "Copied", 
                            f"{data_summary} to clipboard.")
        
        return dict_str
