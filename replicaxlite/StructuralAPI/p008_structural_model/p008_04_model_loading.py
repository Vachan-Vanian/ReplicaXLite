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


from ..p006_time_series import ConstantTimeSeries, LinearTimeSeries, PathTimeSeries
from ..p007_load import LoadPattern, NodeLoad, ElementLoad, SPConstraint


class ModelLoading:
    """Handles loading and time series for the structural model"""
    
    def __init__(self, parent_model):
        self.parent = parent_model
        self.time_series = {}
        self.load_patterns = {}
    

    def add_time_series(self, time_series):
        """
        Add a time series to the model.
        
        Parameters:
        -----------
        time_series : TimeSeries
            Time series to add
            
        Returns:
        --------
        TimeSeries
            The added time series
        """
        self.time_series[time_series.tag] = time_series
        self.parent._log(f"Added time series with tag {time_series.tag}")
        return time_series

    def create_constant_time_series(self, tag: int, factor: float = 1.0):
        """
        USER FUNCTION
        Create a constant time series.
        
        Parameters:
        -----------
        tag : int
            Time series tag
        factor : float, optional
            Load factor
            
        Returns:
        --------
        ConstantTimeSeries
            The created time series
        """
        ts = ConstantTimeSeries(tag, factor)
        return self.add_time_series(ts)

    def create_linear_time_series(self, tag: int, factor: float = 1.0):
        """
        USER FUNCTION
        Create a linear time series.
        
        Parameters:
        -----------
        tag : int
            Time series tag
        factor : float, optional
            Load factor
            
        Returns:
        --------
        LinearTimeSeries
            The created time series
        """
        ts = LinearTimeSeries(tag, factor)
        return self.add_time_series(ts)

    def create_path_time_series(self, tag: int, dt: float = 0.0, values: list = None, 
                             time: list = None, file_path: str = "", file_time: str = "", 
                             factor: float = 1.0, start_time: float = 0.0, 
                             use_last: bool = False, prepend_zero: bool = False):
        """
        USER FUNCTION
        Create a path time series.
        
        Parameters:
        -----------
        tag : int
            Time series tag
        dt : float, optional
            Time interval
        values : list, optional
            Load factor values
        time : list, optional
            Time values
        file_path : str, optional
            Path to file with load factors
        file_time : str, optional
            Path to file with time values
        factor : float, optional
            Load factor
        start_time : float, optional
            Start time
        use_last : bool, optional
            Whether to use last value after end of series
        prepend_zero : bool, optional
            Whether to prepend a zero value
            
        Returns:
        --------
        PathTimeSeries
            The created time series
        """
        ts = PathTimeSeries(tag, dt, values, time, file_path, file_time, 
                        factor, start_time, use_last, prepend_zero)
        return self.add_time_series(ts)

    def create_load_pattern(self, tag: int, time_series=None) -> LoadPattern:
        """
        USER FUNCTION
        Create a new load pattern and add it to the model.
        
        Parameters:
        -----------
        tag : int
            Load pattern tag
        time_series : TimeSeries or int
            Time series object or tag to use
            
        Returns:
        --------
        LoadPattern
            The created load pattern
        """
        load_pattern = LoadPattern(tag, time_series)
        return self.add_load_pattern(load_pattern)

    def add_load_pattern(self, load_pattern: LoadPattern):
        """
        Add a load pattern to the model without creating it in OpenSees yet.
        
        Parameters:
        -----------
        load_pattern : LoadPattern
            Load pattern to add
            
        Returns:
        --------
        LoadPattern
            The added load pattern
        """
        self.load_patterns[load_pattern.tag] = load_pattern
        self.parent._log(f"Added load pattern with tag {load_pattern.tag}")
        return load_pattern

    def create_uniform_excitation_pattern(self, tag: int, direction: int, time_series=None,
                                        accel_series_tag: int = None, disp_series_tag: int = None, 
                                        vel_series_tag: int = None, vel0: float = None, 
                                        fact: float = None) -> LoadPattern:
        """
        USER FUNCTION
        Create a uniform excitation load pattern.
        
        Parameters:
        -----------
        tag : int
            Load pattern tag
        direction : int
            Direction of excitation (1=X, 2=Y, 3=Z, 4=RX, 5=RY, 6=RZ)
        time_series : TimeSeries or int, optional
            Time series object or tag for acceleration
        accel_series_tag : int, optional
            Tag of acceleration time series (alternative to time_series)
        disp_series_tag : int, optional
            Tag of displacement time series
        vel_series_tag : int, optional
            Tag of velocity time series
        vel0 : float, optional
            Initial velocity
        fact : float, optional
            Scale factor
            
        Returns:
        --------
        LoadPattern
            The created load pattern
        """
        # Create the load pattern
        load_pattern = LoadPattern(tag, time_series, pattern_type="UniformExcitation")
        
        # Determine acceleration series tag
        if accel_series_tag is None and hasattr(time_series, 'tag'):
            accel_series_tag = time_series.tag
        elif accel_series_tag is None and isinstance(time_series, int):
            accel_series_tag = time_series
        
        # Configure uniform excitation
        load_pattern.set_uniform_excitation(
            direction=direction,
            accel_series_tag=accel_series_tag,
            disp_series_tag=disp_series_tag,
            vel_series_tag=vel_series_tag,
            vel0=vel0,
            fact=fact
        )
        
        # Add to model
        return self.add_load_pattern(load_pattern)

    def create_multiple_support_pattern(self, tag: int) -> LoadPattern:
        """
        USER FUNCTION
        Create a multiple support load pattern.
        
        Parameters:
        -----------
        tag : int
            Load pattern tag
            
        Returns:
        --------
        LoadPattern
            The created load pattern
        """
        # Create the load pattern
        load_pattern = LoadPattern(tag, pattern_type="MultipleSupport")
        
        # Add to model
        return self.add_load_pattern(load_pattern)

    def add_plain_ground_motion(self, pattern: LoadPattern, gm_tag: int, 
                             disp_series_tag: int = None, vel_series_tag: int = None, 
                             accel_series_tag: int = None, integration_method: str = 'Trapezoidal', 
                             factor: float = 1.0) -> LoadPattern:
        """
        USER FUNCTION
        Add a plain ground motion to a multiple support pattern.
        
        Parameters:
        -----------
        pattern : LoadPattern
            The multiple support pattern
        gm_tag : int
            Tag for the ground motion
        disp_series_tag : int, optional
            Tag of displacement time series
        vel_series_tag : int, optional
            Tag of velocity time series
        accel_series_tag : int, optional
            Tag of acceleration time series
        integration_method : str, optional
            Integration method ('Trapezoidal', 'Simpson', etc.)
        factor : float, optional
            Scale factor
            
        Returns:
        --------
        LoadPattern
            The updated load pattern
        """
        if pattern.pattern_type != "MultipleSupport":
            self.parent._log("Warning: Adding ground motion to non-MultipleSupport pattern", level="warning")
        
        pattern.add_plain_ground_motion(
            gm_tag=gm_tag,
            disp_series_tag=disp_series_tag,
            vel_series_tag=vel_series_tag,
            accel_series_tag=accel_series_tag,
            integration_method=integration_method,
            factor=factor
        )
        
        return pattern

    def add_interpolated_ground_motion(self, pattern: LoadPattern, gm_tag: int, 
                                    gm_tags: list, factors: list = None) -> LoadPattern:
        """
        USER FUNCTION
        Add an interpolated ground motion to a multiple support pattern.
        
        Parameters:
        -----------
        pattern : LoadPattern
            The multiple support pattern
        gm_tag : int
            Tag for the ground motion
        gm_tags : list
            List of tags for ground motions to interpolate
        factors : list, optional
            List of scale factors for each ground motion
            
        Returns:
        --------
        LoadPattern
            The updated load pattern
        """
        if pattern.pattern_type != "MultipleSupport":
            self.parent._log("Warning: Adding ground motion to non-MultipleSupport pattern", level="warning")
        
        pattern.add_interpolated_ground_motion(
            gm_tag=gm_tag,
            gm_tags=gm_tags,
            factors=factors
        )
        
        return pattern

    def add_imposed_motion(self, pattern: LoadPattern, node_tag: int, 
                        dof: int, gm_tag: int) -> LoadPattern:
        """
        USER FUNCTION
        Add an imposed motion to a multiple support pattern.
        
        Parameters:
        -----------
        pattern : LoadPattern
            The multiple support pattern
        node_tag : int
            Tag of node for constraint placement
        dof : int
            Degree of freedom (1-6)
        gm_tag : int
            Tag of ground motion
            
        Returns:
        --------
        LoadPattern
            The updated load pattern
        """
        if pattern.pattern_type != "MultipleSupport":
            self.parent._log("Warning: Adding imposed motion to non-MultipleSupport pattern", level="warning")
        
        pattern.add_imposed_motion(
            node_tag=node_tag,
            dof=dof,
            gm_tag=gm_tag
        )
        
        return pattern

    def create_element_load(self, pattern_tag: int, element_tags: list, 
                        load_type: str, load_values: list):
        """
        USER FUNCTION
        Create an elemental load.
        
        Parameters:
        -----------
        pattern_tag : int
            Load pattern tag
        element_tags : list
            List of element tags
        load_type : str
            Type of load ('beamUniform', 'beamPoint', 'beamThermal')
        load_values : list
            Load values specific to the load type
            
        Returns:
        --------
        ElementLoad
            The created element load
        """
        if pattern_tag not in self.load_patterns:
            self.create_load_pattern(pattern_tag)
            
        load_pattern = self.load_patterns[pattern_tag]
        return load_pattern._add_element_load(element_tags, load_type, load_values)

    def create_beam_uniform_load(self, pattern_tag: int, element_tags: list,
                                Wz: float, Wy: float = None, Wx: float = 0.0):
        """
        USER FUNCTION
        Create a uniform load on beam elements.
        
        Parameters:
        -----------
        pattern_tag : int
            Load pattern tag
        element_tags : list
            List of element tags
        Wz : float
            Uniform load in vertical direction (local z)
        Wy : float, optional
            Uniform load in horizontal direction (local y)
        Wx : float, optional
            Uniform load in axial direction (local x)
            
        Returns:
        --------
        ElementLoad
            The created element load
        """
        if pattern_tag not in self.load_patterns:
            self.create_load_pattern(pattern_tag)
            
        load_pattern = self.load_patterns[pattern_tag]
        return load_pattern.add_beam_uniform_load(element_tags, Wz, Wy, Wx)

    def create_sp_constraint(self, pattern_tag: int, node_tag: int, dof: int, dof_value: float):
        """
        USER FUNCTION
        Create a single-point constraint (prescribed displacement).
        
        Parameters:
        -----------
        pattern_tag : int
            Load pattern tag
        node_tag : int
            Tag of node to constrain
        dof : int
            Degree of freedom (1=X, 2=Y, 3=Z, 4=RX, 5=RY, 6=RZ)
        dof_value : float
            Prescribed displacement value
            
        Returns:
        --------
        SPConstraint
            The created single-point constraint
        """
        if pattern_tag not in self.load_patterns:
            self.create_load_pattern(pattern_tag)
            
        load_pattern = self.load_patterns[pattern_tag]
        return load_pattern.add_sp_constraint(node_tag, dof, dof_value)

    def create_node_load(self, pattern_tag: int, node_tag: int, 
                      fx: float = 0, fy: float = 0, fz: float = 0, 
                      mx: float = 0, my: float = 0, mz: float = 0):
        
        if pattern_tag not in self.load_patterns:
            self.create_load_pattern(pattern_tag)

        load_pattern = self.load_patterns[pattern_tag]
        return load_pattern.add_node_load(node_tag, fx, fy, fz, mx, my, mz)
