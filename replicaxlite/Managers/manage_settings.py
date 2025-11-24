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


from PySide6.QtWidgets import (
    QDialog, QTabWidget, QWidget, QVBoxLayout, QHBoxLayout,
    QFormLayout, QLabel, QLineEdit, QComboBox, QCheckBox,
    QPushButton, QMessageBox, QGroupBox, QTextEdit, QSpinBox,
    QDoubleSpinBox, QColorDialog, QScrollArea
)
from PySide6.QtGui import QColor
from PySide6.QtCore import Qt
import re


class SettingsEditor(QDialog):
    """
    Self-aware settings editor that automatically generates UI from SETTINGS dict.
    
    Rules:
    - Keys starting with "_" are treated as metadata/private (not editable)
    - Keys starting with "group_" define explicit groups (e.g., "group_camera_rotation" -> "Camera Rotation")
    - Types are inferred from default values
    - Special key patterns trigger special widgets:
        - *_color, *_Color, *Color -> Color picker
        - Choices can be defined with "_<key>_choices" metadata
    - Nested dicts with "group_" prefix create groups, top-level keys create tabs
    - String value "None" is treated as Python None type
    """
    
    # Prefix for explicit group definitions
    GROUP_PREFIX = "group_"
    
    # Widget type inference rules
    TYPE_RULES = {
        'color': lambda k, v: isinstance(v, str) and ('color' in k.lower() or 
                              v.startswith('#') or v.lower() in 
                              ['red','green','blue','yellow','orange','purple','white','black','cyan','magenta']),
        'bool': lambda k, v: isinstance(v, bool),
        'int': lambda k, v: isinstance(v, int) and not isinstance(v, bool),
        'float': lambda k, v: isinstance(v, float),
        'str': lambda k, v: isinstance(v, str),
        'none': lambda k, v: v is None,
        'choice': lambda k, v, meta: f"_{k}_choices" in meta,  # For dropdown selections
    }
    
    def __init__(self, settings_dict, statusbar_helper=None, callbacks=None):
        """
        Args:
            settings_dict: Reference to the SETTINGS dictionary
            statusbar_helper: Optional helper for updating statusbar
            callbacks: Dict of {setting_path: callable} for special actions after save
        """
        super().__init__()
        self.settings = settings_dict
        self.statusbar_helper = statusbar_helper
        self.callbacks = callbacks or {}
        self.widgets = {}  # {path: widget} for all created widgets
        
        self.setModal(True)
        self.setWindowTitle("Settings Editor")
        self.resize(750, 650)
        
        self._build_ui()
    
    def _build_ui(self):
        """Auto-generate the entire UI from settings structure"""
        main_layout = QVBoxLayout()
        tabs = QTabWidget()
        
        for section_key, section_value in self.settings.items():
            # Skip private/metadata keys
            if section_key.startswith("_"):
                continue
            
            # Each top-level key becomes a tab
            if isinstance(section_value, dict):
                tab = self._create_tab_for_section(section_key, section_value)
                tab_name = self._format_label(section_key)
                tabs.addTab(tab, tab_name)
        
        main_layout.addWidget(tabs)
        
        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        
        save_btn = QPushButton("Save Settings")
        save_btn.clicked.connect(self._save_all_settings)
        
        btn_layout.addWidget(cancel_btn)
        btn_layout.addWidget(save_btn)
        main_layout.addLayout(btn_layout)
        
        self.setLayout(main_layout)
    
    def _create_tab_for_section(self, section_key, section_data):
        """Create a scrollable tab for a settings section"""
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        
        container = QWidget()
        layout = QVBoxLayout()
        
        # Detect groups using explicit "group_" prefix
        groups = self._detect_groups(section_data)
        
        for group_name, keys_data in groups.items():
            group_box = QGroupBox(self._format_label(group_name))
            form = QFormLayout()
            
            for key, value in keys_data.items():
                if key.startswith("_"):
                    continue
                
                path = f"{section_key}.{group_name}.{key}" if group_name != "general" else f"{section_key}.{key}"
                
                widget = self._create_widget_for_value(key, value, section_data)
                if widget:
                    self.widgets[path] = widget
                    # Use exact key name as-is from dictionary
                    form.addRow(key, widget)
            
            group_box.setLayout(form)
            layout.addWidget(group_box)
        
        # Handle special case: unit_system with selector + preview
        if section_key == "unit_system" and "_unit_systems" in section_data:
            self._add_unit_system_preview(layout, section_data)
        
        layout.addStretch()
        container.setLayout(layout)
        scroll.setWidget(container)
        return scroll
    
    def _detect_groups(self, section_data):
        """
        Detect groups using explicit "group_" prefix.
        
        Keys starting with "group_" are treated as group containers.
        The part after "group_" becomes the group display name.
        Keys not inside a group_ dict go into "general" group.
        
        Example:
            "group_camera_rotation": {
                "angle_x": 5,
                "angle_y": 5
            }
            -> Group name: "camera_rotation" (displayed as "Camera Rotation")
        """
        groups = {}
        ungrouped = {}
        
        for key, value in section_data.items():
            # Skip private/metadata keys
            if key.startswith("_"):
                continue
            
            # Check for explicit group prefix
            if key.startswith(self.GROUP_PREFIX) and isinstance(value, dict):
                # Extract group name (part after "group_")
                group_name = key[len(self.GROUP_PREFIX):]
                groups[group_name] = value
            else:
                # Non-group items go to "general"
                ungrouped[key] = value
        
        # Add ungrouped items under "general" if any exist
        if ungrouped:
            groups["general"] = ungrouped
        
        return groups
    
    def _create_widget_for_value(self, key, value, section_data=None):
        """Create appropriate widget based on value type and key name"""
        section_data = section_data or {}
        
        # Handle None type - create editable text field with "None" placeholder
        if self.TYPE_RULES['none'](key, value):
            widget = QLineEdit()
            widget.setText("None")
            widget.setPlaceholderText("None")
            widget._is_none_field = True  # Mark for special handling on save
            return widget
        
        # Check for explicit choices: _<key>_choices
        choices_key = f"_{key}_choices"
        if choices_key in section_data:
            widget = QComboBox()
            widget.addItems(section_data[choices_key])
            widget.setCurrentText(str(value))
            return widget
        
        # Auto-detect choices from related dict (e.g., new_unit_system -> _unit_systems)
        # Pattern: if key ends with common suffixes and a matching _*s dict exists
        for meta_key, meta_val in section_data.items():
            if meta_key.startswith("_") and meta_key.endswith("s") and isinstance(meta_val, dict):
                # e.g., _unit_systems -> unit_system pattern
                base_name = meta_key[1:-1]  # Remove _ prefix and s suffix: "unit_system"
                if base_name in key:  # "new_unit_system" contains "unit_system"
                    widget = QComboBox()
                    widget.addItems(list(meta_val.keys()))
                    widget.setCurrentText(str(value))
                    return widget
        
        # Color detection
        if self.TYPE_RULES['color'](key, value):
            widget = QPushButton()
            widget.setFixedSize(80, 25)
            widget._color_value = value
            self._update_color_button(widget, value)
            widget.clicked.connect(lambda checked, w=widget: self._pick_color(w))
            return widget
        
        # Bool
        if self.TYPE_RULES['bool'](key, value):
            widget = QCheckBox()
            widget.setChecked(value)
            return widget
        
        # Int
        if self.TYPE_RULES['int'](key, value):
            widget = QSpinBox()
            widget.setRange(-999999, 999999)
            widget.setValue(value)
            return widget
        
        # Float
        if self.TYPE_RULES['float'](key, value):
            widget = QDoubleSpinBox()
            widget.setRange(-999999.0, 999999.0)
            widget.setDecimals(4)
            widget.setValue(value)
            return widget
        
        # String (default)
        if self.TYPE_RULES['str'](key, value):
            widget = QLineEdit()
            widget.setText(str(value))
            return widget
        
        return None
    
    def _update_color_button(self, button, color_name):
        """Update button appearance to show color"""
        button._color_value = color_name
        button.setText(color_name)
        button.setStyleSheet(f"""
            QPushButton {{
                background-color: {color_name};
                color: {'white' if color_name.lower() in ['black','blue','green','red','purple'] else 'black'};
                border: 1px solid #666;
            }}
        """)
    
    def _pick_color(self, button):
        """Open color picker dialog"""
        current = QColor(button._color_value)
        color = QColorDialog.getColor(current, self, "Select Color")
        if color.isValid():
            # Use color name if it's a named color, otherwise hex
            color_name = color.name()
            self._update_color_button(button, color_name)
    
    def _add_unit_system_preview(self, layout, section_data):
        """Add special unit system preview widget"""
        preview_group = QGroupBox("Unit System Details")
        preview_layout = QVBoxLayout()
        
        self._unit_preview_text = QTextEdit()
        self._unit_preview_text.setReadOnly(True)
        self._unit_preview_text.setMaximumHeight(150)
        
        # Connect combo change to preview update
        combo_path = "unit_system.new_unit_system"
        if combo_path in self.widgets:
            combo = self.widgets[combo_path]
            combo.currentTextChanged.connect(
                lambda sys: self._update_unit_preview(sys, section_data)
            )
            # Initial update
            self._update_unit_preview(combo.currentText(), section_data)
        
        preview_layout.addWidget(self._unit_preview_text)
        preview_group.setLayout(preview_layout)
        layout.addWidget(preview_group)
    
    def _update_unit_preview(self, system_name, section_data):
        """Update unit system preview text"""
        systems = section_data.get("_unit_systems", {})
        if system_name in systems:
            details = systems[system_name]
            text = "\n".join(f"{k}: {v}" for k, v in details.items())
            self._unit_preview_text.setText(text)
    
    def _format_label(self, key):
        """Convert key_name to 'Key Name' display format"""
        # Remove leading underscores
        key = key.lstrip("_")
        # Split on underscores and capitalize
        words = key.split("_")
        return " ".join(word.capitalize() for word in words)
    
    def _get_widget_value(self, widget):
        """Extract value from any widget type, handling None conversion"""
        if isinstance(widget, QCheckBox):
            return widget.isChecked()
        elif isinstance(widget, QSpinBox):
            return widget.value()
        elif isinstance(widget, QDoubleSpinBox):
            return widget.value()
        elif isinstance(widget, QComboBox):
            return widget.currentText()
        elif isinstance(widget, QLineEdit):
            text = widget.text()
            # Convert "None" string to Python None type
            if text.strip().lower() == "none":
                return None
            return text
        elif isinstance(widget, QPushButton) and hasattr(widget, '_color_value'):
            return widget._color_value
        return None
    
    def _save_all_settings(self):
        """Save all widget values back to settings dict"""
        try:
            for path, widget in self.widgets.items():
                parts = path.split(".")
                value = self._get_widget_value(widget)
                
                # Navigate to correct location in settings
                # Handle both grouped (section.group.key) and ungrouped (section.key) paths
                target = self.settings
                for part in parts[:-1]:
                    # For grouped items, need to add "group_" prefix back
                    if part != "general" and f"{self.GROUP_PREFIX}{part}" in target:
                        target = target[f"{self.GROUP_PREFIX}{part}"]
                    elif part in target:
                        target = target[part]
                    else:
                        # Fallback: try with group_ prefix
                        target = target.get(f"{self.GROUP_PREFIX}{part}", target.get(part, {}))
                
                # Handle unit system special case
                if path == "unit_system.new_unit_system":
                    old_val = target.get("new_unit_system")
                    target["_old_unit_system"] = old_val
                
                target[parts[-1]] = value
            
            # Execute any registered callbacks
            for path, callback in self.callbacks.items():
                if callable(callback):
                    callback()
            
            self.accept()
            
            if self.statusbar_helper:
                self.statusbar_helper.update_message("Settings saved successfully!", 2000)
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save settings: {str(e)}")
    
    def showEvent(self, event):
        """Refresh all widgets when dialog is shown"""
        super().showEvent(event)
        self._sync_widgets_from_settings()
    
    def _sync_widgets_from_settings(self):
        """Sync all widgets with current settings values"""
        for path, widget in self.widgets.items():
            parts = path.split(".")
            
            # Navigate to value, handling group_ prefix
            value = self.settings
            for part in parts:
                if part != "general" and f"{self.GROUP_PREFIX}{part}" in value:
                    value = value[f"{self.GROUP_PREFIX}{part}"]
                elif part in value:
                    value = value[part]
            
            # Update widget (handle None values)
            if isinstance(widget, QCheckBox):
                widget.setChecked(value if value is not None else False)
            elif isinstance(widget, QSpinBox):
                widget.setValue(value if value is not None else 0)
            elif isinstance(widget, QDoubleSpinBox):
                widget.setValue(value if value is not None else 0.0)
            elif isinstance(widget, QComboBox):
                widget.setCurrentText(str(value) if value is not None else "")
            elif isinstance(widget, QLineEdit):
                # Display "None" for Python None values
                widget.setText("None" if value is None else str(value))
            elif isinstance(widget, QPushButton) and hasattr(widget, '_color_value'):
                self._update_color_button(widget, value if value else "#FFFFFF")
