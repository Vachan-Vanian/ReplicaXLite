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


import openseespy.opensees as ops


class Constraint:
    """Class for node constraints"""
    
    def __init__(self, node_tag: int, dx: int = 0, dy: int = 0, dz: int = 0, 
                rx: int = 0, ry: int = 0, rz: int = 0):
        self.node_tag = node_tag
        self.constraints = (dx, dy, dz, rx, ry, rz)
        self._is_created_in_opensees = False
    
    def create_in_opensees(self):
        """Create constraint in OpenSees"""
        if not self._is_created_in_opensees:
            ops.fix(self.node_tag, *self.constraints)
            self._is_created_in_opensees = True

    def remove_constraint(self, node_tag: int) -> bool:
        """
        Remove a constraint from the model configuration.
        
        Parameters:
        -----------
        node_tag : int
            Node ID of the constraint to remove
            
        Returns:
        --------
        bool
            True if constraint was found and removed, False otherwise
            
        Raises:
        -------
        RuntimeError
            If attempting to remove a constraint after the model has been built
        """
        # Check if model is already built
        if self.parent._model_built:
            raise RuntimeError("Cannot remove constraints after OpenSees model has been built")
        
        if node_tag in self.constraints:
            del self.constraints[node_tag]
            self.parent._log(f"Removed constraint at node {node_tag}")
            return True
        else:
            self.parent._log(f"No constraint found at node {node_tag} to remove", level="warning")
            return False
        
    def update_constraint(self, node_tag: int, dx: int = None, dy: int = None, dz: int = None, 
                     rx: int = None, ry: int = None, rz: int = None) -> bool:
        """
        Update an existing constraint or create a new one.
        
        Parameters:
        -----------
        node_tag : int
            Node ID to constrain
        dx, dy, dz, rx, ry, rz : int, optional
            Constraint flags (1=fixed, 0=free)
            If None, existing values are kept (for existing constraints)
            
        Returns:
        --------
        bool
            True if constraint was updated or created, False otherwise
            
        Raises:
        -------
        RuntimeError
            If attempting to modify constraints after the model has been built
        """
        # Check if model is already built
        if self.parent._model_built:
            raise RuntimeError("Cannot modify constraints after OpenSees model has been built")
        
        # If constraint exists, update with non-None values
        if node_tag in self.constraints:
            constraint = self.constraints[node_tag]
            current = constraint.constraints
            
            # Create new constraints tuple using existing values where new ones aren't provided
            new_dx = dx if dx is not None else current[0]
            new_dy = dy if dy is not None else current[1]
            new_dz = dz if dz is not None else current[2]
            new_rx = rx if rx is not None else current[3]
            new_ry = ry if ry is not None else current[4]
            new_rz = rz if rz is not None else current[5]
            
            # Create a new constraint object (since constraint tuples are immutable)
            new_constraint = self.create_constraint(node_tag, new_dx, new_dy, new_dz, new_rx, new_ry, new_rz)
            self.parent._log(f"Updated constraint at node {node_tag}: {new_constraint.constraints}")
            return True
        else:
            # If no constraint exists and no values provided, return False
            if all(v is None for v in [dx, dy, dz, rx, ry, rz]):
                self.parent._log(f"No constraint found at node {node_tag} and no new values provided", level="warning")
                return False
            
            # Set default values of 0 (free) for any None values
            dx = 0 if dx is None else dx
            dy = 0 if dy is None else dy
            dz = 0 if dz is None else dz
            rx = 0 if rx is None else rx
            ry = 0 if ry is None else ry
            rz = 0 if rz is None else rz
            
            # Create new constraint
            self.create_constraint(node_tag, dx, dy, dz, rx, ry, rz)
            self.parent._log(f"Created new constraint at node {node_tag}")
            return True



# Define a class for multi-point constraints
class MPConstraint:
    """Base class for multi-point constraints"""
    
    def __init__(self, constraint_type: str):
        self.constraint_type = constraint_type
        self._is_created_in_opensees = False
    
    def create_in_opensees(self):
        """Create constraint in OpenSees"""
        pass


class EqualDOFConstraint(MPConstraint):
    """Class for EqualDOF constraints"""
    
    def __init__(self, retained_node: int, constrained_node: int, dofs: list[int]):
        super().__init__("equalDOF")
        self.retained_node = retained_node
        self.constrained_node = constrained_node
        self.dofs = dofs
    
    def create_in_opensees(self):
        """Create equalDOF constraint in OpenSees"""
        if not self._is_created_in_opensees:
            ops.equalDOF(self.retained_node, self.constrained_node, *self.dofs)
            self._is_created_in_opensees = True


class RigidDiaphragmConstraint(MPConstraint):
    """Class for rigidDiaphragm constraints"""
    
    def __init__(self, direction: int, master_node: int, slave_nodes: list[int]):
        super().__init__("rigidDiaphragm")
        self.direction = direction
        self.master_node = master_node
        self.slave_nodes = slave_nodes if isinstance(slave_nodes, list) else [slave_nodes]
    
    def create_in_opensees(self):
        """Create rigidDiaphragm constraint in OpenSees"""
        if not self._is_created_in_opensees:
            ops.rigidDiaphragm(self.direction, self.master_node, *self.slave_nodes)
            self._is_created_in_opensees = True


class RigidLinkConstraint(MPConstraint):
    """Class for rigidLink constraints"""
    
    def __init__(self, link_type: str, master_node: int, slave_node: int):
        super().__init__("rigidLink")
        if link_type not in ['bar', 'beam']:
            raise ValueError("link_type must be either 'bar' or 'beam'")
        self.link_type = link_type
        self.master_node = master_node
        self.slave_node = slave_node
    
    def create_in_opensees(self):
        """Create rigidLink constraint in OpenSees"""
        if not self._is_created_in_opensees:
            ops.rigidLink(self.link_type, self.master_node, self.slave_node)
            self._is_created_in_opensees = True

