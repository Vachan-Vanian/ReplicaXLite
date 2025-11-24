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


class Load:
    """Base class for loads"""
    
    def __init__(self, pattern_tag: int = None):
        self.pattern_tag = pattern_tag
        self._is_created_in_opensees = False


class NodeLoad(Load):
    """Class for nodal loads"""
    
    def __init__(self, node_tag: int, fx: float = 0, fy: float = 0, fz: float = 0, 
                mx: float = 0, my: float = 0, mz: float = 0, pattern_tag: int = None):
        super().__init__(pattern_tag)
        self.node_tag = node_tag
        self.load_values = (fx, fy, fz, mx, my, mz)
    
    def create_in_opensees(self):
        """Apply load to node"""
        if not self._is_created_in_opensees:
            ops.load(self.node_tag, *self.load_values)
            self._is_created_in_opensees = True


class ElementLoad(Load):
    """Class for elemental loads"""
    
    def __init__(self, element_tags: list, load_type: str, load_values: list, 
                pattern_tag: int = None):
        super().__init__(pattern_tag)
        self.element_tags = element_tags if isinstance(element_tags, list) else [element_tags]
        if load_type not in ['beamUniform', 'beamPoint']:
            raise ValueError("load_type must be either 'beamUniform' or 'beamPoint'")
        self.load_type = load_type
        self.load_values = load_values
    
    def create_in_opensees(self):
        """Apply load to elements"""
        if not self._is_created_in_opensees:            
            # Build the command string based on the load type
            cmd = ['-ele', *self.element_tags, '-type', f'-{self.load_type}', *self.load_values]
            ops.eleLoad(*cmd)
            self._is_created_in_opensees = True


class SPConstraint(Load):
    """Class for single-point constraints (prescribed displacements for fix nodes)"""
    
    def __init__(self, node_tag: int, dof: int, dof_value: float, pattern_tag: int = None):
        super().__init__(pattern_tag)
        self.node_tag = node_tag
        self.dof = dof
        self.dof_value = dof_value
    
    def create_in_opensees(self):
        """Apply single-point constraint"""
        if not self._is_created_in_opensees:
            ops.sp(self.node_tag, self.dof, self.dof_value)
            self._is_created_in_opensees = True


class LoadPattern:
    """Class for load patterns"""
    
    def __init__(self, tag: int, time_series=None, pattern_type: str = "Plain"):
        self.tag = tag
        self.time_series = time_series  # Can be a TimeSeries object or a tag
        self.pattern_type = pattern_type
        self.loads = []
        self.excitation_params = {}
        self.ground_motions = {}  # For MultipleSupport patterns
        self.imposed_motions = []  # For MultipleSupport patterns
        self._is_created_in_opensees = False
    
    def add_node_load(self, node_tag: int, 
                      fx: float = 0, fy: float = 0, fz: float = 0, 
                      mx: float = 0, my: float = 0, mz: float = 0):
        """Add nodal load to pattern"""
        load = NodeLoad(node_tag, fx, fy, fz, mx, my, mz, self.tag)
        self.loads.append(load)
        return load
    
    def add_beam_uniform_load(self, element_tags: list, Wz: float, Wy: float = None, Wx: float = 0.0):
        """
        Add uniform load to beam elements.
        
        Parameters:
        -----------
        element_tags : list
            List of element tags
        Wz : float
            Uniform load in local z direction (VERTICAL)
        Wy : float, optional
            Uniform load in local y direction (HORIZONTAL)
        Wx : float, optional
            Uniform load in axial direction
        """
        # Prepare OpenSees values in the order it expects (Wy, Wz, Wx)
        opensees_values = []
        
        # First parameter in OpenSees is Wy (horizontal)
        if Wy is not None:
            opensees_values.append(Wy)
        else:
            opensees_values.append(0.0)  # Default to zero if not provided
        
        # Second parameter in OpenSees is Wz (vertical)
        opensees_values.append(Wz)  # Always add Wz
        
        # Last parameter is Wx (axial)
        if Wx != 0.0:
            opensees_values.append(Wx)
        
        return self._add_element_load(element_tags, "beamUniform", opensees_values)
    
    def add_beam_point_load(self, element_tags: list, Pz: float, Py: float = None, xL: float = 0.5, Px: float = 0.0):
        """
        Add point load to beam elements.
        
        Parameters:
        -----------
        element_tags : list
            List of element tags
        Pz : float
            Point load in local z direction (VERTICAL)
        Py : float, optional
            Point load in local y direction (HORIZONTAL)
        xL : float
            Location of point load as a fraction of element length (0.0 to 1.0)
        Px : float, optional
            Point load in axial direction
        """
        # Prepare OpenSees values in the order it expects (Py, Pz, xL, Px)
        opensees_values = []
        
        # First parameter in OpenSees is Py (horizontal)
        if Py is not None:
            opensees_values.append(Py)
        else:
            opensees_values.append(0.0)  # Default to zero if not provided
        
        # Second parameter in OpenSees is Pz (vertical)
        opensees_values.append(Pz)  # Always add Pz
        
        # Location parameter
        opensees_values.append(xL)
        
        # Last parameter is Px (axial)
        if Px != 0.0:
            opensees_values.append(Px)
        
        return self._add_element_load(element_tags, "beamPoint", opensees_values)
      
    def add_sp_constraint(self, node_tag: int, dof: int, dof_value: float):
        """Add single-point constraint to pattern"""
        constraint = SPConstraint(node_tag, dof, dof_value, self.tag)
        self.loads.append(constraint)
        return constraint
    
    def _add_element_load(self, element_tags: list, load_type: str, load_values: list):
        """Internal method to add elemental loads"""
        load = ElementLoad(element_tags, load_type, load_values, self.tag)
        self.loads.append(load)
        return load
    
    def set_uniform_excitation(self, direction: int, 
                               accel_series_tag: int = None, 
                               disp_series_tag: int = None, 
                               vel_series_tag: int = None,
                               vel0: float = None, 
                               fact: float = None):
        """
        Configure the load pattern as a uniform excitation.
        
        Parameters:
        -----------
        direction : int
            Direction of excitation (1=X, 2=Y, 3=Z, 4=RX, 5=RY, 6=RZ)
        accel_series_tag : int, optional
            Tag of acceleration time series
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
        self
            For method chaining
        """
        self.pattern_type = "UniformExcitation"
        self.excitation_params = {
            'direction': direction
        }
        
        # Add optional parameters if provided
        if accel_series_tag is not None:
            self.excitation_params['accel'] = accel_series_tag
        if disp_series_tag is not None:
            self.excitation_params['disp'] = disp_series_tag
        if vel_series_tag is not None:
            self.excitation_params['vel'] = vel_series_tag
        if vel0 is not None:
            self.excitation_params['vel0'] = vel0
        if fact is not None:
            self.excitation_params['fact'] = fact
            
        # If time_series is an object rather than a tag, get its tag
        if hasattr(self.time_series, 'tag'):
            if 'accel' not in self.excitation_params:
                self.excitation_params['accel'] = self.time_series.tag
        
        return self
    
    def add_plain_ground_motion(self, gm_tag: int, disp_series_tag: int = None, 
                             vel_series_tag: int = None, accel_series_tag: int = None,
                             integration_method: str = 'Trapezoidal', factor: float = 1.0):
        """
        Add a plain ground motion to a MultipleSupport pattern.
        
        Parameters:
        -----------
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
        self
            For method chaining
        """
        if self.pattern_type != "MultipleSupport":
            self.pattern_type = "MultipleSupport"
        
        gm_params = {
            'type': 'Plain',
            'int': integration_method,
            'fact': factor
        }
        
        # Add optional parameters if provided
        if disp_series_tag is not None:
            gm_params['disp'] = disp_series_tag
        if vel_series_tag is not None:
            gm_params['vel'] = vel_series_tag
        if accel_series_tag is not None:
            gm_params['accel'] = accel_series_tag
            
        # Store ground motion parameters
        self.ground_motions[gm_tag] = gm_params
        
        return self
    
    def add_interpolated_ground_motion(self, gm_tag: int, gm_tags: list, factors: list = None):
        """
        Add an interpolated ground motion to a MultipleSupport pattern.
        
        Parameters:
        -----------
        gm_tag : int
            Tag for the ground motion
        gm_tags : list
            List of tags for ground motions to interpolate
        factors : list, optional
            List of scale factors for each ground motion
            
        Returns:
        --------
        self
            For method chaining
        """
        if self.pattern_type != "MultipleSupport":
            self.pattern_type = "MultipleSupport"
        
        gm_params = {
            'type': 'Interpolated',
            'gm_tags': gm_tags
        }
        
        if factors is not None:
            gm_params['facts'] = factors
            
        # Store ground motion parameters
        self.ground_motions[gm_tag] = gm_params
        
        return self
    
    def add_imposed_motion(self, node_tag: int, dof: int, gm_tag: int):
        """
        Add an imposed motion to a MultipleSupport pattern.
        
        Parameters:
        -----------
        node_tag : int
            Tag of node for constraint placement
        dof : int
            Degree of freedom (1-6)
        gm_tag : int
            Tag of ground motion
            
        Returns:
        --------
        self
            For method chaining
        """
        if self.pattern_type != "MultipleSupport":
            self.pattern_type = "MultipleSupport"
        
        # Store imposed motion parameters
        self.imposed_motions.append({
            'node_tag': node_tag,
            'dof': dof,
            'gm_tag': gm_tag
        })
        
        return self
    
    def create_in_opensees(self):
        """Create load pattern in OpenSees"""
        if not self._is_created_in_opensees:            
            # Handle different pattern types
            if self.pattern_type == "UniformExcitation":
                # Extract parameters for UniformExcitation
                direction = self.excitation_params['direction']
                
                # Build command arguments
                cmd_args = [self.tag, direction]
                
                # Add optional parameters in the correct format
                if 'accel' in self.excitation_params:
                    cmd_args.extend(['-accel', self.excitation_params['accel']])
                if 'vel' in self.excitation_params:
                    cmd_args.extend(['-vel', self.excitation_params['vel']])
                if 'disp' in self.excitation_params:
                    cmd_args.extend(['-disp', self.excitation_params['disp']])
                if 'vel0' in self.excitation_params:
                    cmd_args.extend(['-vel0', self.excitation_params['vel0']])
                if 'fact' in self.excitation_params:
                    cmd_args.extend(['-fact', self.excitation_params['fact']])
                
                # Create pattern
                ops.pattern('UniformExcitation', *cmd_args)
                
            elif self.pattern_type == "MultipleSupport":
                # Create the MultipleSupport pattern
                ops.pattern('MultipleSupport', self.tag)
                
                # Create ground motions
                for gm_tag, gm_params in self.ground_motions.items():
                    if gm_params['type'] == 'Plain':
                        # Build command arguments for Plain ground motion
                        gm_args = [gm_tag, 'Plain']
                        
                        # Add optional parameters in the correct format
                        if 'disp' in gm_params:
                            gm_args.extend(['-disp', gm_params['disp']])
                        if 'vel' in gm_params:
                            gm_args.extend(['-vel', gm_params['vel']])
                        if 'accel' in gm_params:
                            gm_args.extend(['-accel', gm_params['accel']])
                        if 'int' in gm_params:
                            gm_args.extend(['-int', gm_params['int']])
                        if 'fact' in gm_params:
                            gm_args.extend(['-fact', gm_params['fact']])
                        
                        # Create ground motion
                        ops.groundMotion(*gm_args)
                        
                    elif gm_params['type'] == 'Interpolated':
                        # Build command arguments for Interpolated ground motion
                        gm_args = [gm_tag, 'Interpolated', *gm_params['gm_tags']]
                        
                        # Add facts if provided
                        if 'facts' in gm_params:
                            gm_args.extend(['-fact', *gm_params['facts']])
                        
                        # Create ground motion
                        ops.groundMotion(*gm_args)
                
                # Create imposed motions
                for im in self.imposed_motions:
                    ops.imposedMotion(im['node_tag'], im['dof'], im['gm_tag'])
                    
            else:  # Default to "Plain" pattern
                # Determine time series tag
                # MODIFIED THIS SECTION TO RAISE ERROR INSTEAD OF CREATING DEFAULT
                if hasattr(self.time_series, 'tag') and hasattr(self.time_series, 'create_in_opensees'):
                    self.time_series.create_in_opensees()
                    time_series_tag = self.time_series.tag
                elif isinstance(self.time_series, int):
                    time_series_tag = self.time_series
                else:
                    # Instead of creating a default time series, raise an error
                    raise ValueError(f"No time series defined for load pattern {self.tag}. Please define a time series before creating the load pattern.")
                
                # Create pattern
                ops.pattern('Plain', self.tag, time_series_tag)
                
                # Apply loads
                for load in self.loads:
                    load.create_in_opensees()
                    
            self._is_created_in_opensees = True

