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
from abc import ABC, abstractmethod


class TimeSeries(ABC):
    """
    Abstract base class for OpenSees time series.
    
    All time series objects must implement the create_in_opensees method
    to define how they are created in the OpenSees domain.
    """
    
    def __init__(self, tag: int):
        """
        Initialize time series with a unique tag.
        
        Args:
            tag: Unique integer identifier for this time series
        """
        if not isinstance(tag, int) or tag <= 0:
            raise ValueError("Tag must be a positive integer")
        
        self.tag = tag
        self._is_created_in_opensees = False
    
    @abstractmethod
    def create_in_opensees(self) -> None:
        """
        Create the time series in OpenSees domain.
        
        This method must be implemented by all subclasses.
        """
        pass
    
    def is_created(self) -> bool:
        """Check if this time series has been created in OpenSees."""
        return self._is_created_in_opensees


class ConstantTimeSeries(TimeSeries):
    """Time series with constant load factor throughout the analysis."""
    
    def __init__(self, tag: int, factor: float = 1.0):
        """
        Initialize constant time series.
        
        Args:
            tag: Unique integer identifier
            factor: Constant load factor (default: 1.0)
        """
        super().__init__(tag)
        self.factor = float(factor)
    
    def create_in_opensees(self) -> None:
        """Create constant time series in OpenSees."""
        if not self._is_created_in_opensees:
            ops.timeSeries('Constant', self.tag, '-factor', self.factor)
            self._is_created_in_opensees = True


class LinearTimeSeries(TimeSeries):
    """Time series with linearly varying load factor from 0 to factor."""
    
    def __init__(self, tag: int, factor: float = 1.0):
        """
        Initialize linear time series.
        
        Args:
            tag: Unique integer identifier  
            factor: Maximum load factor reached at end of analysis (default: 1.0)
        """
        super().__init__(tag)
        self.factor = float(factor)
    
    def create_in_opensees(self) -> None:
        """Create linear time series in OpenSees."""
        if not self._is_created_in_opensees:
            ops.timeSeries('Linear', self.tag, '-factor', self.factor)
            self._is_created_in_opensees = True


class PathTimeSeries(TimeSeries):
    """Time series with load factor defined by a user-specified path."""
    
    def __init__(self, 
                 tag: int, 
                 dt: float = 0.0, 
                 values: list[float] | None = None, 
                 time: list[float] | None = None,
                 file_path: str = "", 
                 file_time: str = "", 
                 factor: float = 1.0,
                 start_time: float = 0.0, 
                 use_last: bool = False, 
                 prepend_zero: bool = False):
        """
        Initialize path time series.
        
        Args:
            tag: Unique integer identifier
            dt: Time interval for equally spaced values (default: 0.0)
            values: List of load factor values
            time: List of time points corresponding to values
            file_path: Path to file containing load factor values
            file_time: Path to file containing time points
            factor: Scale factor applied to all values (default: 1.0)
            start_time: Time to start applying load (default: 0.0)
            use_last: Use last value for times beyond specified range
            prepend_zero: Add zero value at start time
        """
        super().__init__(tag)
        
        # Validate inputs
        if values and time and len(values) != len(time):
            raise ValueError("Values and time lists must have the same length")
        
        self.dt = float(dt)
        self.time = list(time) if time else []
        self.values = list(values) if values else []
        self.file_time = file_time
        self.file_path = file_path
        self.factor = float(factor)
        self.start_time = float(start_time)
        self.use_last = use_last
        self.prepend_zero = prepend_zero
    
    def create_in_opensees(self) -> None:
        """Create path time series in OpenSees."""
        if not self._is_created_in_opensees:
            # Build command with required parameters
            cmd = ['Path', self.tag]
            
            # Add optional parameters in correct order
            if self.dt != 0.0:
                cmd.extend(['-dt', self.dt])
            
            if self.time:
                cmd.extend(['-time', *self.time])
            
            if self.values:
                cmd.extend(['-values', *self.values])
            
            if self.file_time:
                cmd.extend(['-fileTime', self.file_time])
            
            if self.file_path:
                cmd.extend(['-filePath', self.file_path])
            
            if self.factor != 1.0:
                cmd.extend(['-factor', self.factor])
            
            if self.start_time != 0.0:
                cmd.extend(['-startTime', self.start_time])
            
            if self.use_last:
                cmd.append('-useLast')
            
            if self.prepend_zero:
                cmd.append('-prependZero')
            
            ops.timeSeries(*cmd)
            self._is_created_in_opensees = True

