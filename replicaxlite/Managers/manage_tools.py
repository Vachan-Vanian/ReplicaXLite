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


from ..GUIs.ToolsGUI.SensorReader import ReplicaXSensorDataReaderGUI
from ..GUIs.ToolsGUI.UnitConverter import ReplicaXUnitConverterPopup
from ..GUIs.ToolsGUI.OpenSeesRecorderReader import ReplicaXRecorderReader
from ..GUIs.ToolsGUI.ColorPicker import ColorPickerDialog
from ..GUIs.ToolsGUI.TimeHistoryFEMTable import TimeHistoryDataDialog


class ReplicaXToolsManager:
    def __init__(self, settings):
        self.settings = settings
        self.sensor_data_gui_popup = ReplicaXSensorDataReaderGUI()
        self.unit_converter_gui_popup = ReplicaXUnitConverterPopup()
        self.opensees_recorder_reader_popop = ReplicaXRecorderReader()
        self.color_picker = ColorPickerDialog()
        self.time_history_data = TimeHistoryDataDialog(settings=self.settings)
        