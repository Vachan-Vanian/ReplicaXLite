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
from enum import Enum
from abc import ABC, abstractmethod
from typing import List, Tuple, Union
from .p003_node import Node
from .p000_utility import calculate_aligned_vecxz, dict_cmd_to_openseespy_list_cmd
import openseespy.opensees as ops


class StructuralElement(Enum):
    """Types of structural elements supported by the model"""
    COLUMN = "column"
    BEAM = "beam"
    WALL = "wall"
    INFILL = "infill"
    TREE = "tree"
    SLAB = "slab"
    TRUSS = "truss"
    GENERAL = "general"

    BEAM_X = "beam_x",
    BEAM_Y = "beam_y",
    BEAM_XY = "beam_xy",
    BEAM_BALCONY = "beam_balcony",
    BEAM_BALCONY_X = "beam_balcony_x",
    BEAM_BALCONY_Y = "beam_balcony_y",
    BEAM_BALCONY_XY = "beam_balcony_xy",
    BEAM_BASE = "beam_base",
    BEAM_BASE_X = "beam_base_x",
    BEAM_BASE_Y = "beam_base_y",
    BEAM_BASE_XY = "beam_base_xy",
    INFILL_X = "infill_x",
    INFILL_BACKSLASH = "infill_backslash",
    INFILL_FORWARD = "infill_forward",
    INFILL_X_AND_CROSS = "infill_x_and_cross"  


class BeamIntegration:
    """Class for beam integration methods for structural analysis"""
    
    def __init__(self, tag: int, integration_type: str, structural_element_use: str = None, 
                section_tag: int = None, num_points: int = 5):
        """
        Constructor for backward compatibility
        
        Parameters
        ----------
        tag : int
            Tag identifier for the beam integration
        integration_type : str
            Type of integration (e.g., 'Lobatto', 'Legendre', etc.)
        structural_element_use : str, optional
            Description of structural element use
        section_tag : int, optional
            Section tag for basic integration
        num_points : int, optional
            Number of integration points (default: 5)
        """
        self.tag = tag
        self.integration_type = integration_type
        self.structural_element_use = structural_element_use
        self.section_tag = section_tag
        self.num_points = num_points
        self._is_created_in_opensees = False
        
        # Parameters for various integration methods
        self.sec_tag = section_tag  # Alias for backward compatibility
        self.sec_tags = None
        self.locs = None
        self.wts = None
        self.sec_i = None
        self.lp_i = None
        self.sec_j = None
        self.lp_j = None
        self.sec_e = None
        self.nc = None  # For LowOrder integration
        
    def create_in_opensees(self):
        """Create beam integration in OpenSees based on the integration type"""
        if self._is_created_in_opensees:
            return
            
        # Handle different integration types
        if self.integration_type == 'Lobatto' or self.integration_type == 'Legendre' or \
           self.integration_type == 'NewtonCotes' or self.integration_type == 'Radau' or \
           self.integration_type == 'Trapezoidal' or self.integration_type == 'CompositeSimpson':
            ops.beamIntegration(self.integration_type, self.tag, self.sec_tag, self.num_points)
            
        elif self.integration_type == 'UserDefined':
            if self.locs is None or self.wts is None or self.sec_tags is None:
                raise ValueError("UserDefined integration requires locs, wts, and sec_tags")
            ops.beamIntegration(self.integration_type, self.tag, len(self.sec_tags), 
                              *self.sec_tags, *self.locs, *self.wts)
                              
        elif self.integration_type == 'FixedLocation':
            if self.locs is None or self.sec_tags is None:
                raise ValueError("FixedLocation integration requires locs and sec_tags")
            ops.beamIntegration(self.integration_type, self.tag, len(self.sec_tags), 
                              *self.sec_tags, *self.locs)
                              
        elif self.integration_type == 'LowOrder':
            if self.locs is None or self.wts is None or self.sec_tags is None:
                raise ValueError("LowOrder integration requires locs, wts, and sec_tags")
            ops.beamIntegration(self.integration_type, self.tag, len(self.sec_tags), 
                              *self.sec_tags, *self.locs, *self.wts)
                              
        elif self.integration_type == 'MidDistance':
            if self.locs is None or self.sec_tags is None:
                raise ValueError("MidDistance integration requires locs and sec_tags")
            ops.beamIntegration(self.integration_type, self.tag, len(self.sec_tags), 
                              *self.sec_tags, *self.locs)
                              
        elif self.integration_type == 'UserHinge':
            if (self.sec_e is None or self.sec_i is None or self.locs is None or 
                self.wts is None or self.sec_j is None):
                raise ValueError("UserHinge integration requires all hinge parameters")
            # Handle parameter structure for UserHinge
            ops.beamIntegration(self.integration_type, self.tag, self.sec_e, 
                              self.np_i, *self.secs_i, *self.locs_i, *self.wts_i,
                              self.np_j, *self.secs_j, *self.locs_j, *self.wts_j)
                              
        elif self.integration_type in ['HingeMidpoint', 'HingeRadau', 'HingeRadauTwo', 'HingeEndpoint']:
            if self.sec_i is None or self.lp_i is None or self.sec_j is None or self.lp_j is None or self.sec_e is None:
                raise ValueError(f"{self.integration_type} requires sec_i, lp_i, sec_j, lp_j, and sec_e")
            ops.beamIntegration(self.integration_type, self.tag, self.sec_i, self.lp_i, 
                              self.sec_j, self.lp_j, self.sec_e)
                              
        else:
            raise ValueError(f"Unknown integration type: {self.integration_type}")
            
        self._is_created_in_opensees = True

    # Factory methods for each integration type
    @classmethod
    def Lobatto(cls, tag: int, sec_tag: int, num_points: int):
        """
        Create a Gauss-Lobatto beamIntegration object.
        
        Gauss-Lobatto integration is the most common approach for evaluating 
        the response of forceBeamColumn because it places an integration point
        at each end of the element, where bending moments are largest in the 
        absence of interior element loads.
        
        Parameters
        ----------
        tag : int
            Tag of the beam integration
        sec_tag : int
            A previous-defined section object
        num_points : int
            Number of integration points along the element
            
        Returns
        -------
        BeamIntegration
            A beam integration object
        """
        obj = cls(tag, 'Lobatto', None, sec_tag, num_points)
        return obj
        
    @classmethod
    def Legendre(cls, tag: int, sec_tag: int, num_points: int):
        """
        Create a Gauss-Legendre beamIntegration object.
        
        Gauss-Legendre integration is more accurate than Gauss-Lobatto;
        however, it is not common in force-based elements because there
        are no integration points at the element ends.
        
        Parameters
        ----------
        tag : int
            Tag of the beam integration
        sec_tag : int
            A previous-defined section object
        num_points : int
            Number of integration points along the element
            
        Returns
        -------
        BeamIntegration
            A beam integration object
        """
        obj = cls(tag, 'Legendre', None, sec_tag, num_points)
        return obj
        
    @classmethod
    def NewtonCotes(cls, tag: int, sec_tag: int, num_points: int):
        """
        Create a Newton-Cotes beamIntegration object.
        
        Newton-Cotes places integration points uniformly along the element,
        including a point at each end of the element.
        
        Parameters
        ----------
        tag : int
            Tag of the beam integration
        sec_tag : int
            A previous-defined section object
        num_points : int
            Number of integration points along the element
            
        Returns
        -------
        BeamIntegration
            A beam integration object
        """
        obj = cls(tag, 'NewtonCotes', None, sec_tag, num_points)
        return obj
        
    @classmethod
    def Radau(cls, tag: int, sec_tag: int, num_points: int):
        """
        Create a Gauss-Radau beamIntegration object.
        
        Gauss-Radau integration is not common in force-based elements because
        it places an integration point at only one end of the element; however,
        it forms the basis for optimal plastic hinge integration methods.
        
        Parameters
        ----------
        tag : int
            Tag of the beam integration
        sec_tag : int
            A previous-defined section object
        num_points : int
            Number of integration points along the element
            
        Returns
        -------
        BeamIntegration
            A beam integration object
        """
        obj = cls(tag, 'Radau', None, sec_tag, num_points)
        return obj
        
    @classmethod
    def Trapezoidal(cls, tag: int, sec_tag: int, num_points: int):
        """
        Create a Trapezoidal beamIntegration object.
        
        Parameters
        ----------
        tag : int
            Tag of the beam integration
        sec_tag : int
            A previous-defined section object
        num_points : int
            Number of integration points along the element
            
        Returns
        -------
        BeamIntegration
            A beam integration object
        """
        obj = cls(tag, 'Trapezoidal', None, sec_tag, num_points)
        return obj
        
    @classmethod
    def CompositeSimpson(cls, tag: int, sec_tag: int, num_points: int):
        """
        Create a CompositeSimpson beamIntegration object.
        
        Parameters
        ----------
        tag : int
            Tag of the beam integration
        sec_tag : int
            A previous-defined section object
        num_points : int
            Number of integration points along the element
            
        Returns
        -------
        BeamIntegration
            A beam integration object
        """
        obj = cls(tag, 'CompositeSimpson', None, sec_tag, num_points)
        return obj
        
    @classmethod
    def UserDefined(cls, tag: int, num_points: int, sec_tags: List[int], 
                   locs: List[float], wts: List[float]):
        """
        Create a UserDefined beamIntegration object.
        
        This option allows user-specified locations and weights of the integration points.
        
        Parameters
        ----------
        tag : int
            Tag of the beam integration
        num_points : int
            Number of integration points along the element
        sec_tags : List[int]
            A list of previous-defined section objects
        locs : List[float]
            Locations of integration points along the element (0 to 1)
        wts : List[float]
            Weights of integration points (0 to 1)
            
        Returns
        -------
        BeamIntegration
            A beam integration object
        """
        if len(sec_tags) != num_points or len(locs) != num_points or len(wts) != num_points:
            raise ValueError("sec_tags, locs, and wts should be of length num_points")
            
        obj = cls(tag, 'UserDefined', None, None, num_points)
        obj.sec_tags = sec_tags
        obj.locs = locs
        obj.wts = wts
        return obj
        
    @classmethod
    def FixedLocation(cls, tag: int, num_points: int, sec_tags: List[int], locs: List[float]):
        """
        Create a FixedLocation beamIntegration object.
        
        This option allows user-specified locations of the integration points.
        The associated integration weights are computed by the method of 
        undetermined coefficients (Vandermonde system).
        
        Parameters
        ----------
        tag : int
            Tag of the beam integration
        num_points : int
            Number of integration points along the element
        sec_tags : List[int]
            A list of previous-defined section objects
        locs : List[float]
            Locations of integration points along the element (0 to 1)
            
        Returns
        -------
        BeamIntegration
            A beam integration object
        """
        if len(sec_tags) != num_points or len(locs) != num_points:
            raise ValueError("sec_tags and locs should be of length num_points")
            
        obj = cls(tag, 'FixedLocation', None, None, num_points)
        obj.sec_tags = sec_tags
        obj.locs = locs
        return obj
        
    @classmethod
    def LowOrder(cls, tag: int, num_points: int, sec_tags: List[int], 
                locs: List[float], wts: List[float]):
        """
        Create a LowOrder beamIntegration object.
        
        This option is a generalization of the FixedLocation and UserDefined
        integration approaches and is useful for moving load analysis.
        The locations of the integration points are user defined, while a 
        selected number of weights are specified and the remaining
        weights are computed by the method of undetermined coefficients.
        
        Parameters
        ----------
        tag : int
            Tag of the beam integration
        num_points : int
            Number of integration points along the element
        sec_tags : List[int]
            A list of previous-defined section objects
        locs : List[float]
            Locations of integration points along the element (0 to 1)
        wts : List[float]
            Weights of integration points, can be of length Nc (0 to num_points)
            
        Returns
        -------
        BeamIntegration
            A beam integration object
        """
        if len(sec_tags) != num_points or len(locs) != num_points or len(wts) > num_points:
            raise ValueError("sec_tags, locs should be of length num_points, wts up to num_points")
            
        obj = cls(tag, 'LowOrder', None, None, num_points)
        obj.sec_tags = sec_tags
        obj.locs = locs
        obj.wts = wts
        obj.nc = len(wts)  # Number of specified weights
        return obj
        
    @classmethod
    def MidDistance(cls, tag: int, num_points: int, sec_tags: List[int], locs: List[float]):
        """
        Create a MidDistance beamIntegration object.
        
        This option allows user-specified locations of the integration points.
        The associated integration weights are determined from the midpoints 
        between adjacent integration point locations.
        
        Parameters
        ----------
        tag : int
            Tag of the beam integration
        num_points : int
            Number of integration points along the element
        sec_tags : List[int]
            A list of previous-defined section objects
        locs : List[float]
            Locations of integration points along the element (0 to 1)
            
        Returns
        -------
        BeamIntegration
            A beam integration object
        """
        if len(sec_tags) != num_points or len(locs) != num_points:
            raise ValueError("sec_tags and locs should be of length num_points")
            
        obj = cls(tag, 'MidDistance', None, None, num_points)
        obj.sec_tags = sec_tags
        obj.locs = locs
        return obj
        
    @classmethod
    def UserHinge(cls, tag: int, sec_e: int, 
                 np_i: int, secs_i: List[int], locs_i: List[float], wts_i: List[float],
                 np_j: int, secs_j: List[int], locs_j: List[float], wts_j: List[float]):
        """
        Create a UserHinge beamIntegration object.
        
        Parameters
        ----------
        tag : int
            Tag of the beam integration
        sec_e : int
            A previous-defined section tag for element interior
        np_i : int
            Number of integration points along the hinge at end I
        secs_i : List[int]
            A list of previous-defined section tags for hinge at end I
        locs_i : List[float]
            A list of locations of integration points for hinge at end I
        wts_i : List[float]
            A list of weights of integration points for hinge at end I
        np_j : int
            Number of integration points along the hinge at end J
        secs_j : List[int]
            A list of previous-defined section tags for hinge at end J
        locs_j : List[float]
            A list of locations of integration points for hinge at end J
        wts_j : List[float]
            A list of weights of integration points for hinge at end J
            
        Returns
        -------
        BeamIntegration
            A beam integration object
        """
        if (len(secs_i) != np_i or len(locs_i) != np_i or len(wts_i) != np_i or
            len(secs_j) != np_j or len(locs_j) != np_j or len(wts_j) != np_j):
            raise ValueError("Lists must match their respective np_i or np_j length")
            
        obj = cls(tag, 'UserHinge', None, None)
        obj.sec_e = sec_e
        obj.np_i = np_i
        obj.secs_i = secs_i
        obj.locs_i = locs_i
        obj.wts_i = wts_i
        obj.np_j = np_j
        obj.secs_j = secs_j
        obj.locs_j = locs_j
        obj.wts_j = wts_j
        return obj
        
    @classmethod
    def HingeMidpoint(cls, tag: int, sec_i: int, lp_i: float, 
                     sec_j: int, lp_j: float, sec_e: int):
        """
        Create a HingeMidpoint beamIntegration object.
        
        Midpoint integration over each hinge region is the most accurate
        one-point integration rule; however, it does not place integration 
        points at the element ends and there is a small integration error 
        for linear curvature distributions along the element.
        
        Parameters
        ----------
        tag : int
            Tag of the beam integration
        sec_i : int
            A previous-defined section object for hinge at I
        lp_i : float
            The plastic hinge length at I
        sec_j : int
            A previous-defined section object for hinge at J
        lp_j : float
            The plastic hinge length at J
        sec_e : int
            A previous-defined section object for the element interior
            
        Returns
        -------
        BeamIntegration
            A beam integration object
        """
        obj = cls(tag, 'HingeMidpoint', None, None)
        obj.sec_i = sec_i
        obj.lp_i = lp_i
        obj.sec_j = sec_j
        obj.lp_j = lp_j
        obj.sec_e = sec_e
        return obj
        
    @classmethod
    def HingeRadau(cls, tag: int, sec_i: int, lp_i: float, 
                  sec_j: int, lp_j: float, sec_e: int):
        """
        Create a HingeRadau beamIntegration object.
        
        Modified two-point Gauss-Radau integration over each hinge region places
        an integration point at the element ends and at 8/3 the hinge length inside
        the element. This approach represents linear curvature distributions exactly
        and the characteristic length for softening plastic hinges is equal to the
        assumed plastic hinge length.
        
        Parameters
        ----------
        tag : int
            Tag of the beam integration
        sec_i : int
            A previous-defined section object for hinge at I
        lp_i : float
            The plastic hinge length at I
        sec_j : int
            A previous-defined section object for hinge at J
        lp_j : float
            The plastic hinge length at J
        sec_e : int
            A previous-defined section object for the element interior
            
        Returns
        -------
        BeamIntegration
            A beam integration object
        """
        obj = cls(tag, 'HingeRadau', None, None)
        obj.sec_i = sec_i
        obj.lp_i = lp_i
        obj.sec_j = sec_j
        obj.lp_j = lp_j
        obj.sec_e = sec_e
        return obj
        
    @classmethod
    def HingeRadauTwo(cls, tag: int, sec_i: int, lp_i: float, 
                     sec_j: int, lp_j: float, sec_e: int):
        """
        Create a HingeRadauTwo beamIntegration object.
        
        Two-point Gauss-Radau integration over each hinge region places an 
        integration point at the element ends and at 2/3 the hinge length inside
        the element. This approach represents linear curvature distributions exactly;
        however, the characteristic length for softening plastic hinges is not equal
        to the assumed plastic hinge length (equals 1/4 of the plastic hinge length).
        
        Parameters
        ----------
        tag : int
            Tag of the beam integration
        sec_i : int
            A previous-defined section object for hinge at I
        lp_i : float
            The plastic hinge length at I
        sec_j : int
            A previous-defined section object for hinge at J
        lp_j : float
            The plastic hinge length at J
        sec_e : int
            A previous-defined section object for the element interior
            
        Returns
        -------
        BeamIntegration
            A beam integration object
        """
        obj = cls(tag, 'HingeRadauTwo', None, None)
        obj.sec_i = sec_i
        obj.lp_i = lp_i
        obj.sec_j = sec_j
        obj.lp_j = lp_j
        obj.sec_e = sec_e
        return obj
        
    @classmethod
    def HingeEndpoint(cls, tag: int, sec_i: int, lp_i: float, 
                     sec_j: int, lp_j: float, sec_e: int):
        """
        Create a HingeEndpoint beamIntegration object.
        
        Endpoint integration over each hinge region moves the integration points to
        the element ends; however, there is a large integration error for linear
        curvature distributions along the element.
        
        Parameters
        ----------
        tag : int
            Tag of the beam integration
        sec_i : int
            A previous-defined section object for hinge at I
        lp_i : float
            The plastic hinge length at I
        sec_j : int
            A previous-defined section object for hinge at J
        lp_j : float
            The plastic hinge length at J
        sec_e : int
            A previous-defined section object for the element interior
            
        Returns
        -------
        BeamIntegration
            A beam integration object
        """
        obj = cls(tag, 'HingeEndpoint', None, None)
        obj.sec_i = sec_i
        obj.lp_i = lp_i
        obj.sec_j = sec_j
        obj.lp_j = lp_j
        obj.sec_e = sec_e
        return obj


class Element(ABC):
    """Abstract base class for elements with delayed OpenSeesPy execution"""
    
    def __init__(self, tag: int, start_node: Union[Node, int], end_node: Union[Node, int], 
                 structural_element_type: str):
        """
        Initialize an element.
        
        Parameters:
        -----------
        tag : int
            Unique identifier for the element
        start_node, end_node : Node or int
            Start and end nodes (or their IDs)
        structural_element_type : str
            Type of the element (MUST be one of the StructuralElement enum values)
        """
        # Validate structural_element_type is a valid enum value
        try:
            StructuralElement(structural_element_type)
        except ValueError:
            raise ValueError(f"Invalid structural_element_type: '{structural_element_type}'. "
                            f"Must be one of: {', '.join([e.value for e in StructuralElement])}")
                
        self.tag = tag
        self.start_node = start_node
        self.end_node = end_node
        self.structural_type = structural_element_type
        self._is_created_in_opensees = False
    
    def length(self) -> float:
        """
        Calculate the length of the element.
        
        Returns:
        --------
        float
            Length of the element
        """
        start_node = self.get_start_node()
        end_node = self.get_end_node()
        return start_node.distance_to(end_node)
    
    def is_zero_length(self, tolerance: float = 1e-6) -> bool:
        """
        Check if the element has zero (or near-zero) length.
        
        Parameters:
        -----------
        tolerance : float
            Maximum length considered to be "zero"
            
        Returns:
        --------
        bool
            True if element length is less than tolerance
        """
        return self.length() <= tolerance
    
    def get_start_node(self) -> Node:
        """
        Get the start node object.
        
        Returns:
        --------
        Node
            Start node of the element
        """
        if isinstance(self.start_node, Node):
            return self.start_node
        else:
            raise ValueError(f"Start node [{self.start_node}] is not a Node object. You need to resolve this reference.")
    
    def get_end_node(self) -> Node:
        """
        Get the end node object.
        
        Returns:
        --------
        Node
            End node of the element
        """
        if isinstance(self.end_node, Node):
            return self.end_node
        else:
            raise ValueError(f"End node [{self.end_node}] is not a Node object. You need to resolve this reference.")
    
    def direction_vector(self) -> Tuple[float, float, float]:
        """
        Calculate the normalized direction vector of the element.
        
        Returns:
        --------
        Tuple[float, float, float]
            (dx, dy, dz) unit vector in the direction from start to end node
        """
        start_node = self.get_start_node()
        end_node = self.get_end_node()
        
        dx = end_node.x - start_node.x
        dy = end_node.y - start_node.y
        dz = end_node.z - start_node.z
        length = math.sqrt(dx**2 + dy**2 + dz**2)
        
        if length > 0:
            return (dx/length, dy/length, dz/length)
        else:
            return (0, 0, 0)
    
    def is_vertical(self, tolerance: float = 1e-6) -> bool:
        """
        Check if the element is vertical (aligned with the Z axis).
        
        Parameters:
        -----------
        tolerance : float
            Maximum deviation from vertical
            
        Returns:
        --------
        bool
            True if element is vertical
        """
        if self.is_zero_length(tolerance):
            return False
            
        # Get direction vector components
        dx, dy, dz = self.direction_vector()
        
        # For a vertical element, dx and dy should be close to 0
        # and |dz| should be close to 1
        return abs(dx) <= tolerance and abs(dy) <= tolerance and abs(abs(dz) - 1.0) <= tolerance
    
    def is_horizontal(self, tolerance: float = 1e-6) -> bool:
        """
        Check if the element is horizontal (perpendicular to the Z axis).
        
        Parameters:
        -----------
        tolerance : float
            Maximum deviation from horizontal
            
        Returns:
        --------
        bool
            True if element is horizontal
        """
        if self.is_zero_length(tolerance):
            return False
            
        # Get direction vector components
        _, _, dz = self.direction_vector()
        
        # For a horizontal element, dz should be close to 0
        return abs(dz) <= tolerance
    
    def is_in_xy_plane(self, z: float = None, tolerance: float = 1e-6) -> bool:
        """
        Check if the element lies in a specific XY plane.
        
        Parameters:
        -----------
        z : float, optional
            Z coordinate of the plane to check against
        tolerance : float
            Maximum deviation allowed
            
        Returns:
        --------
        bool
            True if element is in the specified XY plane
        """
        if self.is_zero_length(tolerance):
            return False
        
        # First check if the element is parallel to the XY plane
        _, _, dz = self.direction_vector()
        parallel_to_xy = abs(dz) <= tolerance
        
        # If z is None, we only care if it's parallel to XY plane
        if z is None:
            return parallel_to_xy
        
        # If z is specified, check if both nodes lie in that plane
        start_node = self.get_start_node()
        end_node = self.get_end_node()
        return (parallel_to_xy and 
                abs(start_node.z - z) <= tolerance and 
                abs(end_node.z - z) <= tolerance)
    
    def is_in_xz_plane(self, y: float = None, tolerance: float = 1e-6) -> bool:
        """
        Check if the element lies in a specific XZ plane.
        
        Parameters:
        -----------
        y : float, optional
            Y coordinate of the plane to check against
        tolerance : float
            Maximum deviation allowed
            
        Returns:
        --------
        bool
            True if element is in the specified XZ plane
        """
        if self.is_zero_length(tolerance):
            return False
        
        # First check if the element is parallel to the XZ plane
        _, dy, _ = self.direction_vector()
        parallel_to_xz = abs(dy) <= tolerance
        
        # If y is None, we only care if it's parallel to XZ plane
        if y is None:
            return parallel_to_xz
        
        # If y is specified, check if both nodes lie in that plane
        start_node = self.get_start_node()
        end_node = self.get_end_node()
        return (parallel_to_xz and 
                abs(start_node.y - y) <= tolerance and 
                abs(end_node.y - y) <= tolerance)

    def is_in_yz_plane(self, x: float = None, tolerance: float = 1e-6) -> bool:
        """
        Check if the element lies in a specific YZ plane.
        
        Parameters:
        -----------
        x : float, optional
            X coordinate of the plane to check against
        tolerance : float
            Maximum deviation allowed
            
        Returns:
        --------
        bool
            True if element is in the specified YZ plane
        """
        if self.is_zero_length(tolerance):
            return False
        
        # First check if the element is parallel to the YZ plane
        dx, _, _ = self.direction_vector()
        parallel_to_yz = abs(dx) <= tolerance
        
        # If x is None, we only care if it's parallel to YZ plane
        if x is None:
            return parallel_to_yz
        
        # If x is specified, check if both nodes lie in that plane
        start_node = self.get_start_node()
        end_node = self.get_end_node()
        return (parallel_to_yz and 
                abs(start_node.x - x) <= tolerance and 
                abs(end_node.x - x) <= tolerance)
    
    def is_diagonal(self, tolerance: float = 1e-6) -> bool:
        """
        Check if the element is diagonal (not horizontal or vertical).
        
        Parameters:
        -----------
        tolerance : float
            Maximum deviation allowed
            
        Returns:
        --------
        bool
            True if element is diagonal
        """
        if self.is_zero_length(tolerance):
            return False
            
        return not(self.is_horizontal(tolerance) or self.is_vertical(tolerance))
    
    def is_backslash_diagonal(self, tolerance: float = 1e-6) -> bool:
        """
        Check if the element is a backslash diagonal (/).
        
        Parameters:
        -----------
        tolerance : float
            Maximum deviation allowed
            
        Returns:
        --------
        bool
            True if element is a backslash diagonal
        """
        if not self.is_diagonal(tolerance):
            return False
        
        # Get the z-component of the direction vector
        _, _, dz = self.direction_vector()
        
        # If z-component is negative, it's a backslash diagonal
        return dz < 0

    def is_forward_diagonal(self, tolerance: float = 1e-6) -> bool:
        """
        Check if the element is a forward diagonal (/).
        
        Parameters:
        -----------
        tolerance : float
            Maximum deviation allowed
            
        Returns:
        --------
        bool
            True if element is a forward diagonal
        """
        if not self.is_diagonal(tolerance):
            return False
        
        # Get the z-component of the direction vector
        _, _, dz = self.direction_vector()
        
        # If z-component is positive, it's a forward diagonal
        return dz > 0
    
    def floor_level(self) -> float:
        """
        Determine the floor level of the element (minimum Z-coordinate).
        
        Returns:
        --------
        float
            Floor level (minimum Z value of start and end nodes)
        """
        start_node = self.get_start_node()
        end_node = self.get_end_node()
        return min(start_node.z, end_node.z)
    
    def aligned_vecxz(self, tol: float = 1e-6) -> List[float]:
        """
        Calculate the vecxz vector for the element (for OpenSees transformation).
        
        Parameters:
        -----------
        tol : float
            Tolerance for geometric checks
            
        Returns:
        --------
        List[float]
            The vecxz vector for OpenSees transformation
        """
        start_node = self.get_start_node()
        end_node = self.get_end_node()
        
        # Get Element Nodes Coordinates
        start = start_node.coords
        end = end_node.coords

        zAxis = calculate_aligned_vecxz(start, end, tol)
        return zAxis
    
    @abstractmethod
    def create_in_opensees(self, model):
        """
        Create the element in OpenSees.
        
        Parameters:
        -----------
        model : StructuralModel
            The structural model containing this element
        """
        pass
    
    def __repr__(self) -> str:
        """String representation of the element"""
        if isinstance(self.start_node, Node) and isinstance(self.end_node, Node):
            return f"Element({self.tag}, {self.structural_type}, {self.start_node.tag}->{self.end_node.tag}, L={self.length():.3f})"
        else:
            return f"Element({self.tag}, {self.structural_type}, {self.start_node}->{self.end_node})"


class Line(Element):
    """Basic geometric line element with no structural properties."""
    
    def __init__(self, tag: int, start_node: Union[Node, int], end_node: Union[Node, int], 
                 element_type: str = None, metadata: dict = None):
        super().__init__(tag, start_node, end_node, element_type or "line")
        self.metadata = metadata or {}
    
    
    def create_in_opensees(self, model):
        """This element doesn't directly create anything in OpenSees."""
        raise NotImplementedError(
            "Line elements are geometric only and cannot be created in OpenSees. "
            "Convert to a structural element type first."
        )
        
    def convert_to_beam_column(self, section_name: str, element_class: str = "forceBeamColumn", 
                              integration_tag: int = None, element_args: dict = None) -> 'BeamColumn':
        """Convert this geometric element to a BeamColumn structural element."""
        return BeamColumn(
            self.tag, 
            self.start_node, 
            self.end_node, 
            self.structural_type, 
            section_name,
            element_class, 
            integration_tag, 
            element_args or {}
        )
    
    # Add additional conversion methods directly to this class as needed
    # def convert_to_truss(self, section_name: str, material_name: str) -> 'TrussElement':
    #     """Convert to truss element"""
    #     return TrussElement(...)
    
    def __repr__(self) -> str:
        """String representation of the element"""
        if isinstance(self.start_node, Node) and isinstance(self.end_node, Node):
            return f"Line({self.tag}, {self.structural_type}, {self.start_node.tag}->{self.end_node.tag}, L={self.length():.3f})"
        else:
            return f"Line({self.tag}, {self.structural_type}, {self.start_node}->{self.end_node})"


class BeamColumn(Element):
    """Class for beam-column elements"""
    
    def __init__(self, tag: int, start_node: Union[Node, int], end_node: Union[Node, int], 
                structural_element_type: str, section_name: str,
                element_class: str = "forceBeamColumn", integration_tag: int = None, 
                element_args: dict = None):
        super().__init__(tag, start_node, end_node, structural_element_type)
        self.section_name = section_name
        self.element_class = element_class
        self.integration_tag = integration_tag
        self.element_args = element_args or {}
        self.transform_tag = None
    
    def create_in_opensees(self, model):
        """Create beam-column element in OpenSees"""
        if not self._is_created_in_opensees:
            
            # Get nodes
            if isinstance(self.start_node, Node):
                start_node = self.start_node
                if not start_node._is_created_in_opensees:
                    start_node.create_in_opensees()
                start_node_tag = start_node.tag
            else:
                start_node_tag = self.start_node
                
            if isinstance(self.end_node, Node):
                end_node = self.end_node
                if not end_node._is_created_in_opensees:
                    end_node.create_in_opensees()
                end_node_tag = end_node.tag
            else:
                end_node_tag = self.end_node
            
            # Determine transform type based on element type
            if self.structural_type == 'column' or self.structural_type == 'wall':
                transform_type = 'PDelta'
            else:
                transform_type = 'Linear'
            
            # Get transformation ID
            self.transform_tag = model.properties.create_transformation(start_node_tag, end_node_tag, transform_type)
            
            # Convert element args to list
            args_list = dict_cmd_to_openseespy_list_cmd(self.element_args)
            
            # Create element
            if self.element_class == "elasticBeamColumn":
                section_tag = model.properties.sections[self.section_name].tag
                ops.element('elasticBeamColumn', self.tag, start_node_tag, end_node_tag, section_tag, self.transform_tag, *args_list)
            elif self.element_class == "forceBeamColumn":
                ops.element('forceBeamColumn', self.tag, start_node_tag, end_node_tag, self.transform_tag, self.integration_tag, *args_list)
            elif self.element_class == "dispBeamColumn":
                ops.element('dispBeamColumn', self.tag, start_node_tag, end_node_tag, self.transform_tag, self.integration_tag, *args_list)
            else:
                raise ValueError(f"Unsupported element class: {self.element_class}. Use 'GeneralElement' instead.")
                
            self._is_created_in_opensees = True

    def __repr__(self) -> str:
        """String representation of the element"""
        if isinstance(self.start_node, Node) and isinstance(self.end_node, Node):
            return f"BeamColumn({self.tag}, {self.structural_type}, {self.start_node.tag}->{self.end_node.tag}, L={self.length():.3f})"
        else:
            return f"BeamColumn({self.tag}, {self.structural_type}, {self.start_node}->{self.end_node})"


class GeneralElement(Element):
    """Class for general element types with flexible creation"""
    
    def __init__(self, tag: int, start_node: Union[Node, int], end_node: Union[Node, int], 
                 element_type: str, structural_element_type: str, 
                 element_args: dict = None, use_transformation: bool = False,
                 transform_type: str = None, transform_keyword: str = 'transfTag'):
        super().__init__(tag, start_node, end_node, structural_element_type)
        self.element_type = element_type  # OpenSees element type (truss, zeroLength, etc.)
        self.element_args = element_args or {}
        self.transform_tag = None
        self.use_transformation = use_transformation
        self.transform_type = transform_type  # If None, will be determined automatically
        self.transform_keyword = transform_keyword  # User-specified keyword for transformation
    
    def create_in_opensees(self, model):
        """Create general element in OpenSees"""
        if not self._is_created_in_opensees:
            # Get nodes
            if isinstance(self.start_node, Node):
                start_node = self.start_node
                if not start_node._is_created_in_opensees:
                    start_node.create_in_opensees()
                start_node_tag = start_node.tag
            else:
                start_node_tag = self.start_node
                
            if isinstance(self.end_node, Node):
                end_node = self.end_node
                if not end_node._is_created_in_opensees:
                    end_node.create_in_opensees()
                end_node_tag = end_node.tag
            else:
                end_node_tag = self.end_node
            
            # Create transformation if requested
            if self.use_transformation:
                transform_type = self.transform_type
                if not transform_type:
                    # Determine transform type based on element type if not specified
                    if self.structural_type == 'column' or self.structural_type == 'wall':
                        transform_type = 'PDelta'
                    else:
                        transform_type = 'Linear'
                
                self.transform_tag = model.properties.create_transformation(
                    start_node_tag, end_node_tag, transform_type
                )
                
                # Add transformation tag to arguments using user-specified keyword
                self.element_args[self.transform_keyword] = self.transform_tag
            
            # Convert element args to list
            args_list = dict_cmd_to_openseespy_list_cmd(self.element_args)
            
            # Create element with dynamic type
            ops.element(self.element_type, self.tag, start_node_tag, end_node_tag, *args_list)
            self._is_created_in_opensees = True

