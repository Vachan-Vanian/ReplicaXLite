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


from abc import ABC, abstractmethod
from .p000_utility import dict_cmd_to_openseespy_list_cmd
import openseespy.opensees as ops


### REMEMBER an abstract class can NOT be instantiated directly
class Material(ABC):
    """Abstract base class for materials"""
    
    def __init__(self, tag: int, name: str):
        self.tag = tag
        self.name = name
        self._is_created_in_opensees = False
    
    @abstractmethod
    def create_in_opensees(self):
        """Create the material in OpenSees"""
        pass

### can create ANY uniaxial material
class UniaxialMaterial(Material):
    """Class for uniaxial materials"""
    
    def __init__(self, tag: int, name: str, material_type: str, material_args: dict):
        super().__init__(tag, name)
        self.material_type = material_type
        self.material_args = material_args
    
    def create_in_opensees(self):
        """Create the uniaxial material in OpenSees"""
        if not self._is_created_in_opensees:
            args = dict_cmd_to_openseespy_list_cmd(self.material_args)
            ops.uniaxialMaterial(self.material_type, self.tag, *args)
            self._is_created_in_opensees = True

