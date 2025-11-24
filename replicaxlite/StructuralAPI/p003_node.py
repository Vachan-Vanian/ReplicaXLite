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


import math
from typing import Tuple
import openseespy.opensees as ops


class Node:
    """Class for structural nodes with delayed OpenSeesPy execution"""
    
    def __init__(self, tag: int, x: float, y: float, z: float):
        """
        Initialize a node.
        
        Parameters:
        -----------
        tag : int
            Unique identifier for the node
        x, y, z : float
            Coordinates in 3D space
        """
        self.tag = tag
        self.coords = (x, y, z)
        self.x = x
        self.y = y
        self.z = z
        self.mass = None
        self._is_created_in_opensees = False
    
    def translate(self, dx: float = 0, dy: float = 0, dz: float = 0):
        """
        Translate the node by the given amounts.
        
        Parameters:
        -----------
        dx, dy, dz : float
            Translation distances in X, Y, Z directions
        """
        if self._is_created_in_opensees:
            raise RuntimeError("Cannot modify node geometry after it has been created in OpenSeesPy")
        self.x += dx
        self.y += dy
        self.z += dz
        self.coords = (self.x, self.y, self.z)
        return self
    
    def rotate_about_z(self, angle_degrees: float, center_x: float = 0, center_y: float = 0):
        """
        Rotate the node around the Z axis.
        
        Parameters:
        -----------
        angle_degrees : float
            Rotation angle in degrees
        center_x, center_y : float
            Coordinates of the center of rotation in the XY plane
        """
        if self._is_created_in_opensees:
            raise RuntimeError("Cannot modify node geometry after it has been created in OpenSeesPy")
        
        angle_rad = math.radians(angle_degrees)
        cos_angle = math.cos(angle_rad)
        sin_angle = math.sin(angle_rad)
        
        # Translate to origin
        x = self.x - center_x
        y = self.y - center_y
        
        # Rotate
        new_x = x * cos_angle - y * sin_angle
        new_y = x * sin_angle + y * cos_angle
        
        # Translate back
        self.x = new_x + center_x
        self.y = new_y + center_y
        self.coords = (self.x, self.y, self.z)
        return self
    
    def distance_to(self, other: 'Node') -> float:
        """
        Calculate the Euclidean distance between this node and another.
        
        Parameters:
        -----------
        other : Node
            The other node
            
        Returns:
        --------
        float
            Distance between the nodes
        """
        return math.sqrt((self.x - other.x)**2 + (self.y - other.y)**2 + (self.z - other.z)**2)
    
    def is_close_to(self, other: 'Node', tolerance: float = 1e-6) -> bool:
        """
        Check if this node is close to another node within a tolerance.
        
        Parameters:
        -----------
        other : Node
            The other node
        tolerance : float
            Maximum distance to consider nodes as coincident
            
        Returns:
        --------
        bool
            True if nodes are within tolerance distance
        """
        return self.distance_to(other) < tolerance
    
    def get_coordinates(self) -> Tuple[float, float, float]:
        """
        Get the coordinates of the node.
        
        Returns:
        --------
        Tuple[float, float, float]
            (x, y, z) coordinates
        """
        return self.coords
    
    def set_coordinates(self, x: float, y: float, z: float):
        """
        Re-Set the coordinates of the node.
        
        Parameters:
        -----------
        x, y, z : float
            New coordinates
        """
        if self._is_created_in_opensees:
            raise RuntimeError("Cannot modify node geometry after it has been created in OpenSeesPy")
        self.x = x
        self.y = y
        self.z = z
        self.coords = (x, y, z)
        return self

    def add_mass(self, mass_x: float, mass_y: float, mass_z: float, mass_rx: float = 0, mass_ry: float = 0, mass_rz: float = 0):
        """
        Add mass to the node.
        
        Parameters:
        -----------
        mass_x, mass_y, mass_z : float
            Translational mass in each direction
        mass_rx, mass_ry, mass_rz : float
            Rotational mass around each axis
        """
        self.mass = (mass_x, mass_y, mass_z, mass_rx, mass_ry, mass_rz)
        return self
    
    def create_in_opensees(self):
        """Create the node in OpenSees"""
        if not self._is_created_in_opensees:
            ops.node(self.tag, *self.coords)
            if self.mass is not None:
                ops.mass(self.tag, *self.mass)
            self._is_created_in_opensees = True
    
    def __repr__(self) -> str:
        """String representation of the node"""
        return f"Node({self.tag}, {self.x:.3f}, {self.y:.3f}, {self.z:.3f})"

