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


from typing import List, Union
from ..p005_constraint import Constraint, EqualDOFConstraint, RigidDiaphragmConstraint, RigidLinkConstraint, MPConstraint


class ModelConstraints:
    """Handles constraints for the structural model"""
    
    def __init__(self, parent_model):
        self.parent = parent_model
        self.constraints = {} # node_tag -> Constraint
        self.mp_constraints = []  # List of multi-point constraints
    
    def create_constraint(self, node_tag: int, dx: int = 0, dy: int = 0, dz: int = 0, 
                         rx: int = 0, ry: int = 0, rz: int = 0) -> Constraint:
        """
        Create a new constraint and add it to the model.
        
        Parameters:
        -----------
        node_tag : int
            Node ID to constrain
        dx, dy, dz, rx, ry, rz : int
            Constraint flags (1=fixed, 0=free)
            
        Returns:
        --------
        Constraint
            The created constraint
        """
        constraint = Constraint(node_tag, dx, dy, dz, rx, ry, rz)
        return self.add_constraint(constraint)

    def add_constraint(self, constraint: Constraint):
        """
        Add a constraint to the model without creating it in OpenSees yet.
        
        Parameters:
        -----------
        constraint : Constraint
            Constraint to add
            
        Returns:
        --------
        Constraint
            The added constraint
        """
        self.constraints[constraint.node_tag] = constraint
        self.parent._log(f"Added constraint at node {constraint.node_tag}: {constraint.constraints}")
        return constraint
    

    def create_equal_dof(self, retained_node: int, constrained_node: int, dofs: List[int]) -> EqualDOFConstraint:
        """
        USER FUNCTION
        Create an equalDOF constraint between two nodes.
        
        Parameters:
        -----------
        retained_node : int
            Tag of the retained (primary/master) node
        constrained_node : int
            Tag of the constrained (secondary/slave) node
        dofs : List[int]
            List of degrees of freedom to constrain (1-6)
            
        Returns:
        --------
        EqualDOFConstraint
            The created constraint
        """
        constraint = EqualDOFConstraint(retained_node, constrained_node, dofs)
        return self.add_mp_constraint(constraint)
    
    def create_rigid_diaphragm(self, direction: int, master_node: int, 
                            slave_nodes: Union[int, List[int]]) -> RigidDiaphragmConstraint:
        """
        USER FUNCTION
        Create a rigid diaphragm constraint.
        
        Parameters:
        -----------
        direction : int
            Direction perpendicular to the rigid plane (1=X|(YZ PLane), 2=Y|(XZ Plane), 3=Z|(XY Plane))
        master_node : int
            Tag of the master node
        slave_nodes : int or List[int]
            Tag(s) of the slave node(s)
            
        Returns:
        --------
        RigidDiaphragmConstraint
            The created constraint
        """
        constraint = RigidDiaphragmConstraint(direction, master_node, slave_nodes)
        return self.add_mp_constraint(constraint)
    
    def create_rigid_link(self, link_type: str, master_node: int, slave_node: int) -> RigidLinkConstraint:
        """
        USER FUNCTION
        Create a rigid link constraint between two nodes.
        
        Parameters:
        -----------
        link_type : str
            Type of rigid link ('bar' or 'beam')
            - 'bar': constrain only translational DOFs
            - 'beam': constrain both translational and rotational DOFs
        master_node : int
            Tag of the master node
        slave_node : int
            Tag of the slave node
            
        Returns:
        --------
        RigidLinkConstraint
            The created constraint
        """
        constraint = RigidLinkConstraint(link_type, master_node, slave_node)
        return self.add_mp_constraint(constraint)
    
    def add_mp_constraint(self, constraint: MPConstraint) -> MPConstraint:
        """
        Add a multi-point constraint to the model without creating it in OpenSees yet.
        
        Parameters:
        -----------
        constraint : MPConstraint
            Multi-point constraint to add
            
        Returns:
        --------
        MPConstraint
            The added constraint
        """
        self.mp_constraints.append(constraint)
        self.parent._log(f"Added {constraint.constraint_type} constraint")
        return constraint
