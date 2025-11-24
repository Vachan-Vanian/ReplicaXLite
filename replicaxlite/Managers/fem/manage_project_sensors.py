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


import pyvista as pv
from pathlib import Path
from ...UtilityCode.TableGUI import ReplicaXTable
from pyvistaqt import QtInteractor
from ...GUIs.ToolsGUI.SensorReader import ReplicaXSensorDataReaderGUI
from PySide6.QtWidgets import QVBoxLayout, QPushButton, QHBoxLayout, QTableWidgetItem


class ReplicaXProjectSensors:
    """
    Manages sensor groups with nested tables for individual sensors.
    
    Main Table: Group | Type | Sensors | Display | Open | Delete | Path | Status
    Nested Table (Sensors): Sensor Name | X | Y | Z
    """
    
    # Main table columns
    COL_GROUP = 0
    COL_TYPE = 1
    COL_SENSORS = 2
    COL_DISPLAY = 3
    COL_OPEN = 4
    COL_DELETE = 5
    COL_PATH = 6
    COL_STATUS = 7

    def __init__(self, sensors_tab_widget, settings, interactor: 'QtInteractor'):
        self.sensors_tab_widget = sensors_tab_widget
        self.settings = settings
        self.interactor: 'QtInteractor' = interactor
        
        # {group_name: {'actors': {}, 'labels': {}, 'gui': ReplicaXSensorDataReaderGUI}}
        self.sensor_groups = {}
        
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self.sensors_tab_widget)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)

        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(5)
        
        self.btn_add = QPushButton("Add")
        self.btn_update = QPushButton("Update")
        self.btn_toggle = QPushButton("Toggle")
        self.btn_delete = QPushButton("Delete")
        self.btn_reset = QPushButton("Reset")
        
        self.btn_add.clicked.connect(self.add_content)
        self.btn_update.clicked.connect(self.update_content)
        self.btn_toggle.clicked.connect(self.toggle_content)
        self.btn_delete.clicked.connect(self.delete_content)
        self.btn_reset.clicked.connect(self.reset_content)
        
        for btn in [self.btn_add, self.btn_update, self.btn_toggle, self.btn_delete, self.btn_reset]:
            btn_layout.addWidget(btn)

        # Main table - 8 columns
        self.table = ReplicaXTable(rows=0, columns=8, parent=None, settings=self.settings)
        self.table.set_column_types(['str', 'str', 'table', 'bool', 'bool', 'bool', 'str', 'str'])
        self.table.set_headers(['Group', 'Type', 'Sensors', 'Display', 'Open', 'Delete', 'Path', 'Status'])
        
        # Setup dropdowns
        self.table.set_dropdown(self.COL_TYPE, ["", "Acceleration", "Displacement", "Strain", "Frequency"])
        self.table.set_dropdown(self.COL_DISPLAY, [True, False])
        self.table.set_dropdown(self.COL_OPEN, [False, True])
        self.table.set_dropdown(self.COL_DELETE, [False, True])
        
        # Setup nested table templates
        self._setup_nested_tables()
        
        self.table.init_table_cells()

        layout.addLayout(btn_layout)
        layout.addWidget(self.table)

    def _setup_nested_tables(self):
        """Create nested table templates for sensor types."""
        def create_sensors_template():
            t = ReplicaXTable(rows=1, columns=4, settings=self.settings)
            t.set_column_types(['str', 'float', 'float', 'float'])
            t.set_column_unit(1, unit_type="Length")
            t.set_column_unit(2, unit_type="Length")
            t.set_column_unit(3, unit_type="Length")
            t.set_headers(['Sensor Name', 'X', 'Y', 'Z'])
            t.init_table_cells()
            return t
        
        # Link Type dropdown to Sensors nested table
        self.table.link_dropdown_to_table(
            dropdown_col=self.COL_TYPE,
            table_col=self.COL_SENSORS,
            templates={
                "Acceleration": create_sensors_template(),
                "Displacement": create_sensors_template(),
                "Strain": create_sensors_template(),
                "Frequency": create_sensors_template(),
            }
        )

    def _get_sensor_color(self, sensor_type: str) -> str:
        """Get sensor color from settings."""
        try:
            return self.settings["sensors"]["group_sensor_colors"].get(sensor_type, "gray")
        except (KeyError, TypeError):
            return "gray"

    def _get_point_size(self) -> int:
        """Get sensor point size from settings."""
        try:
            return self.settings["sensors"]["group_display"].get("sensor_point_size", 12)
        except (KeyError, TypeError):
            return 15

    def _get_label_font_size(self) -> int:
        """Get label font size from settings."""
        try:
            return self.settings["sensors"]["group_display"].get("label_font_size", 15)
        except (KeyError, TypeError):
            return 12

    def _find_config(self, group_name: str, custom_path: str = None) -> Path | None:
        """Find sensor config JSON."""
        try:
            config_dir = self.settings["_project"]["project_folder"]
            default_path = Path(config_dir) / "UserData" / "Sensors" / f"{group_name}.json"
            if default_path.exists():
                return default_path
        except (KeyError, TypeError):
            pass
        
        if custom_path and custom_path.strip():
            p = Path(custom_path.strip())
            if p.exists():
                return p
        return None

    def _get_row_data(self, row: int) -> dict:
        """Extract main table row data."""
        return {
            'group': self.table.get_cell_value(row, self.COL_GROUP) or "",
            'type': self.table.get_cell_value(row, self.COL_TYPE) or "Acceleration",
            'display': self.table.get_cell_value(row, self.COL_DISPLAY),
            'open': self.table.get_cell_value(row, self.COL_OPEN),
            'delete': self.table.get_cell_value(row, self.COL_DELETE),
            'path': self.table.get_cell_value(row, self.COL_PATH) or "",
        }

    def _set_status(self, row: int, status: str):
        """Set status cell."""
        item = QTableWidgetItem(status)
        self.table.setItem(row, self.COL_STATUS, item)

    def _create_sensor_actor(self, name: str, x: float, y: float, z: float, sensor_type: str):
        """Create point and label actors for a sensor using current settings."""
        color = self._get_sensor_color(sensor_type)
        point_size = self._get_point_size()
        font_size = self._get_label_font_size()

        point = pv.PolyData([[x, y, z]])
        
        actor = self.interactor.add_mesh(
            point, name=f"sensor_{name}", color=color,
            point_size=point_size, render_points_as_spheres=True, render=False
        )
        label_actor = self.interactor.add_point_labels(
            point, [name], name=f"sensor_label_{name}",
            font_size=font_size, text_color=color, shape_color='white', render=False
        )
        return actor, label_actor

    def _remove_group_actors(self, group_name: str):
        """Remove actors/labels for a group by name (keeps GUI)."""
        if group_name not in self.sensor_groups:
            return
        
        group = self.sensor_groups[group_name]
        
        # Remove actors by name instead of object reference
        for sensor_name in group.get('actors', {}).keys():
            full_name = f"{group_name}_{sensor_name}"
            self.interactor.remove_actor(f"sensor_{full_name}")
        
        for sensor_name in group.get('labels', {}).keys():
            full_name = f"{group_name}_{sensor_name}"
            self.interactor.remove_actor(f"sensor_label_{full_name}")
        
        group['actors'] = {}
        group['labels'] = {}

    def _remove_group(self, group_name: str):
        """Remove all actors for a group by name and close GUI."""
        if group_name not in self.sensor_groups:
            return
        
        group = self.sensor_groups[group_name]
        
        # Remove actors by name instead of object reference
        for sensor_name in group.get('actors', {}).keys():
            full_name = f"{group_name}_{sensor_name}"
            self.interactor.remove_actor(f"sensor_{full_name}")
        
        for sensor_name in group.get('labels', {}).keys():
            full_name = f"{group_name}_{sensor_name}"
            self.interactor.remove_actor(f"sensor_label_{full_name}")
        
        if group.get('gui'):
            group['gui'].close()
        del self.sensor_groups[group_name]

    def _get_sensors_from_nested(self, nested_table: ReplicaXTable) -> list:
        """Extract sensor data from nested table."""
        sensors = []
        for row in range(nested_table.rowCount()):
            name = nested_table.get_cell_value(row, 0)
            x = nested_table.get_cell_value(row, 1)
            y = nested_table.get_cell_value(row, 2)
            z = nested_table.get_cell_value(row, 3)
            
            if name and x is not None and y is not None and z is not None:
                try:
                    sensors.append({
                        'name': str(name).strip(),
                        'x': float(x),
                        'y': float(y),
                        'z': float(z)
                    })
                except (ValueError, TypeError):
                    continue
        return sensors

    def _recreate_group_actors(self, group_name: str, row: int, data: dict):
        """Recreate all actors for a group with current settings."""
        nested = self.table.get_cell_value(row, self.COL_SENSORS)
        if not isinstance(nested, ReplicaXTable):
            return False
        
        sensors = self._get_sensors_from_nested(nested)
        if not sensors:
            return False
        
        # Remove old actors by name
        self._remove_group_actors(group_name)
        
        group = self.sensor_groups[group_name]
        visible = bool(data['display'])
        sensor_type = data['type']
        
        # Create new actors with current settings
        actors = {}
        labels = {}
        for sensor in sensors:
            full_name = f"{group_name}_{sensor['name']}"
            actor, label = self._create_sensor_actor(
                full_name, sensor['x'], sensor['y'], sensor['z'], sensor_type
            )
            actor.SetVisibility(visible)
            label.SetVisibility(visible)
            actors[sensor['name']] = actor
            labels[sensor['name']] = label
        
        group['actors'] = actors
        group['labels'] = labels
        group['type'] = sensor_type
        return True

    def add_content(self):
        """Add all sensor groups from table that aren't already added."""
        for row in range(self.table.rowCount()):
            data = self._get_row_data(row)
            group_name = data['group'].strip()
            
            if not group_name or group_name in self.sensor_groups:
                continue
            
            # Find config
            config_path = self._find_config(group_name, data['path'])
            if not config_path:
                self._set_status(row, "Config not found")
                continue
            
            # Create GUI
            gui = ReplicaXSensorDataReaderGUI()
            gui.load_config_from_file(str(config_path))
            
            # Get nested table with sensors
            nested = self.table.get_cell_value(row, self.COL_SENSORS)
            if not isinstance(nested, ReplicaXTable):
                self._set_status(row, "No sensors table")
                continue
            
            sensors = self._get_sensors_from_nested(nested)
            if not sensors:
                self._set_status(row, "No valid sensors")
                continue
            
            # Create actors
            actors = {}
            labels = {}
            sensor_type = data['type']
            visible = bool(data['display'])
            
            for sensor in sensors:
                full_name = f"{group_name}_{sensor['name']}"
                actor, label = self._create_sensor_actor(
                    full_name, sensor['x'], sensor['y'], sensor['z'], sensor_type
                )
                actor.SetVisibility(visible)
                label.SetVisibility(visible)
                actors[sensor['name']] = actor
                labels[sensor['name']] = label
            
            self.sensor_groups[group_name] = {
                'actors': actors,
                'labels': labels,
                'gui': gui,
                'type': sensor_type,
                'row': row
            }
            
            self._set_status(row, "OK")
        
        self.interactor.render()

    def update_content(self):
        """Update all existing groups: refresh from settings, handle Open requests."""
        for row in range(self.table.rowCount()):
            data = self._get_row_data(row)
            group_name = data['group'].strip()
            
            if not group_name or group_name not in self.sensor_groups:
                continue
            
            group = self.sensor_groups[group_name]
            
            # Handle Open request
            if data['open']:
                group['gui'].show()
            
            # Recreate all actors with current settings (handles color, size, type changes)
            if self._recreate_group_actors(group_name, row, data):
                self._set_status(row, "Updated")
            
            # Update row reference
            group['row'] = row
        
        self.interactor.render()

    def toggle_content(self):
        """Toggle visibility based on Display column."""
        for row in range(self.table.rowCount()):
            data = self._get_row_data(row)
            group_name = data['group'].strip()
            
            if not group_name or group_name not in self.sensor_groups:
                continue
            
            group = self.sensor_groups[group_name]
            visible = bool(data['display'])
            
            for actor in group['actors'].values():
                actor.SetVisibility(visible)
            for label in group['labels'].values():
                label.SetVisibility(visible)
        
        self.interactor.render()

    def delete_content(self):
        """Delete groups where Delete=True."""
        rows_to_remove = []
        
        for row in range(self.table.rowCount()):
            data = self._get_row_data(row)
            
            if data['delete']:
                group_name = data['group'].strip()
                if group_name:
                    self._remove_group(group_name)
                rows_to_remove.append(row)
        
        for row in reversed(rows_to_remove):
            self.table.setCurrentCell(row, 0)
            self.table.remove_row()
        
        # Update row indices
        for name, group in self.sensor_groups.items():
            for r in rows_to_remove:
                if group['row'] > r:
                    group['row'] -= 1
        
        self.interactor.render()

    def reset_content(self):
        """Reset all sensor groups and associated data."""
        # Step 1: Remove actors and labels from the interactor by name
        for group_name, group in self.sensor_groups.items():
            for sensor_name in group.get('actors', {}).keys():
                full_name = f"{group_name}_{sensor_name}"
                self.interactor.remove_actor(f"sensor_{full_name}")
            
            for sensor_name in group.get('labels', {}).keys():
                full_name = f"{group_name}_{sensor_name}"
                self.interactor.remove_actor(f"sensor_label_{full_name}")

        # Step 2: Close GUI windows
        for group in self.sensor_groups.values():
            if group.get('gui'):
                group['gui'].close()

        # Step 3: Clear internal data structures
        self.sensor_groups.clear()

        # Step 4: Call native API reset function
        self.table.reset_data() 

        # Final render update
        self.interactor.render()
