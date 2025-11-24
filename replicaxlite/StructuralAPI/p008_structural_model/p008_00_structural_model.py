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


from datetime import datetime
import openseespy.opensees as ops

from .p008_01_model_geometry import ModelGeometry
from .p008_02_model_properties import ModelProperties
from .p008_03_model_constraints import ModelConstraints
from .p008_04_model_loading import ModelLoading
from .p008_05_model_analysis import ModelAnalysis
from .p008_06_model_visualization import ModelVisualization
from .p008_07_model_io import ModelIO

from ..p000_utility import dict_cmd_to_openseespy_list_cmd


class StructuralModel:
    """Main model class to manage the OpenSees model with delayed execution"""
    
    def __init__(self, model_name: str = "Structural3DModel"):
        """Initialize a structural model."""
        self.reset(model_name)
    
    def reset(self, model_name):
        self.model_name = model_name
        self.ndm = 3
        self.ndf = 6
        
        # Parameters and configuration
        self.params = {
            'node_merge_tolerance': 1e-6,  # meters
            'floor_height_tolerance': 0.1,  # meters
            'debug': False,
            'verbose': True
        }
        
        # Component managers
        self.geometry = ModelGeometry(self)
        self.properties = ModelProperties(self)
        self.constraints = ModelConstraints(self)
        self.loading = ModelLoading(self)
        self.analysis = ModelAnalysis(self)
        self.visualization = ModelVisualization(self)
        self.io = ModelIO(self)
        
        # Tracking variables
        self._opensees_initialized = False
        self._model_built = False
        self._is_forced_released = False

        # reset opensees model
        ops.wipe()
    
    def _log(self, message: str, level: str = 'info'):
        """Log a message based on verbosity settings."""
        if self.params['verbose'] or (level == 'debug' and self.params['debug']):
            print(f"ReplicaXLite::{datetime.now()} | {level.upper()}: {message}")

    def _initialize_opensees_model(self):
        """Initialize the OpenSees model only when needed"""
        if not self._opensees_initialized:
            ops.wipe()
            ops.model('basic', '-ndm', self.ndm, '-ndf', self.ndf)
            self._opensees_initialized = True
            self._log("OpenSees model initialized")
    
    def build_model(self):
        """Build the actual OpenSees model"""
        if self._model_built:
            self._log("Model has already been built", level='warning')
            return
        
        if self._is_forced_released:
            self._log("Model was FORCED relesed by user.\nUpdates of model MUST provided by user!", level='warning')
            return
            
        # Check for line elements
        if self.geometry.has_line_elements():
            self._log("Model contains unconverted line elements which cannot be created in OpenSees", 
                    level='error')
            raise RuntimeError(
                "Model contains unconverted line elements. "
                "Use convert_line_elements method to convert them before building the model."
            )        

        # Initialize OpenSees
        self._initialize_opensees_model()
        
        # Create materials
        for material in self.properties.materials.values():
            material.create_in_opensees()
        
        # Create sections
        for section in self.properties.sections.values():
            section.create_in_opensees()
        
        # Create beam integrations
        for beam_integration in self.properties.beam_integrations.values():
            beam_integration.create_in_opensees()
        
        # Create nodes
        for node in self.geometry.nodes.values():
            node.create_in_opensees()
        
        # Create constraints
        for constraint in self.constraints.constraints.values():
            constraint.create_in_opensees()

        # Create multi-point constraints
        for mp_constraint in self.constraints.mp_constraints:
            mp_constraint.create_in_opensees()
        
        # Create elements
        for element in self.geometry.elements.values():
            element.create_in_opensees(self)

        # Create time series before load patterns
        for time_series in self.loading.time_series.values():
            time_series.create_in_opensees()
        
        # Create load patterns
        for load_pattern in self.loading.load_patterns.values():
            load_pattern.create_in_opensees()
        
        self._model_built = True
        self._log(f"Successfully built OpenSees model with {len(self.geometry.nodes)} nodes and {len(self.geometry.elements)} elements")
    
    def execute_ops_command(self, func_name: str, *args, auto_initialize: bool = True, 
                       update_model_state: bool = False, **kwargs):
        """
        Execute OpenSeesPy commands while maintaining model state.
        
        This method allows direct execution of OpenSeesPy functions not exposed 
        through the API, with support for both positional and keyword arguments.
        
        Parameters:
        -----------
        func_name : str
            Name of the OpenSeesPy function to call
        *args : Any
            Positional arguments to pass to the OpenSeesPy function
        auto_initialize : bool
            Automatically initialize the OpenSeesPy model if not already done
        update_model_state : bool
            Update model's built state after command execution
        **kwargs : Any
            Keyword arguments to pass to the OpenSeesPy function,
            will be processed using dict_cmd_to_openseespy_list_cmd
            
        Returns:
        --------
        Any
            Result of the OpenSeesPy function call
            
        Examples:
        ---------
        >>> model.execute_ops_command("nodeCoord", 101)
        [10.0, 20.0, 0.0]
        
        >>> model.execute_ops_command("element", "zeroLengthSection", 1001, 10, 11, 
                                "-orient", [1, 0, 0, 0, 1, 0], 
                                update_model_state=True)
        
        >>> model.execute_ops_command("timeSeries", "Path", 1, 
                                dt=0.01, 
                                values=[0.1, 0.2, 0.3], 
                                **{"-factor": 1.5})
        """
        
        # Initialize OpenSeesPy model if needed and requested
        if auto_initialize and not self._opensees_initialized:
            self._initialize_opensees_model()
        
        # Prevent execution if not initialized
        if not self._opensees_initialized:
            raise RuntimeError("OpenSeesPy model is not initialized. Set auto_initialize=True or call build_model() first.")
        
        # Execute the command
        try:
            # Get the function from the ops module
            if not hasattr(ops, func_name):
                raise AttributeError(f"Function '{func_name}' not found in OpenSeesPy")
            
            func = getattr(ops, func_name)
            
            # Process kwargs using utility function if provided
            if kwargs:
                kwargs_args = dict_cmd_to_openseespy_list_cmd(kwargs)
                result = func(*args, *kwargs_args)
            else:
                result = func(*args)
            
            # Update model state if requested
            if update_model_state:
                self._model_built = True
                self._log(f"Model state updated after executing OpenSeesPy command: {func_name}")
            
            # MORED DETAILED LOG
            args_repr = [repr(arg) for arg in args]
            kwargs_repr = [f"{k}={repr(v)}" for k, v in kwargs.items()] if kwargs else []
            command_format = f"{func_name}({', '.join(args_repr + kwargs_repr)})"
            self._log(f"Executed OpenSeesPy command: {command_format}")
            return result
        
        except Exception as e:
            self._log(f"Error executing OpenSeesPy command: {str(e)}", level="error")
            raise


    ### for user update model

    def force_release_model(self):
        """
        Release control of the model to the user for advanced customization.
        
        WARNING: After calling this method, the user becomes responsible for
        model consistency. The built-in safety checks will be bypassed.
        """
        if not self._opensees_initialized:
            self._initialize_opensees_model()
            
        self._is_forced_released = True
        self._model_built = True
        self._log("Model control released to user. The user becomes responsible for model consistency. Use with caution!", level='warning')
        return self
    
    def user_update_materials(self):
        """
        Update material properties in the OpenSees model.
        
        For use after the model is built or force-released.
        """
        if not self._opensees_initialized:
            raise RuntimeError("OpenSees model not initialized. Call build_model() first.")
        
        for material in self.properties.materials.values():
            material.create_in_opensees()
            
        self._log("User-initiated material update completed")
        return self

    def user_update_sections(self):
        """
        Update section properties in the OpenSees model.
        
        For use after the model is built or force-released.
        """
        if not self._opensees_initialized:
            raise RuntimeError("OpenSees model not initialized. Call build_model() first.")
        
        for section in self.properties.sections.values():
            section.create_in_opensees()
            
        self._log("User-initiated section update completed")
        return self

    def user_update_beam_integrations(self):
        """
        Update beam integration definitions in the OpenSees model.
        
        For use after the model is built or force-released.
        """
        if not self._opensees_initialized:
            raise RuntimeError("OpenSees model not initialized. Call build_model() first.")
        
        for beam_integration in self.properties.beam_integrations.values():
            beam_integration.create_in_opensees()
            
        self._log("User-initiated beam integration update completed")
        return self

    def user_update_nodes(self):
        """
        Update node definitions in the OpenSees model.
        
        For use after the model is built or force-released.
        """
        if not self._opensees_initialized:
            raise RuntimeError("OpenSees model not initialized. Call build_model() first.")
        
        for node in self.geometry.nodes.values():
            node.create_in_opensees()
            
        self._log("User-initiated node update completed")
        return self

    def user_update_constraints(self):
        """
        Update constraints in the OpenSees model.
        
        For use after the model is built or force-released.
        """
        if not self._opensees_initialized:
            raise RuntimeError("OpenSees model not initialized. Call build_model() first.")
        
        for constraint in self.constraints.constraints.values():
            constraint.create_in_opensees()
            
        self._log("User-initiated constraint update completed")
        return self
    
    #UNDER REVIEW
    def user_update_mp_constraints(self):
        """
        Update multi-point constraints in the OpenSees model.
        
        For use after the model is built or force-released.
        """
        if not self._opensees_initialized:
            raise RuntimeError("OpenSees model not initialized. Call build_model() first.")
        
        # Update all multi-point constraints
        for mp_constraint in self.constraints.mp_constraints:
            mp_constraint.create_in_opensees()
            
        self._log("User-initiated multi-point constraint update completed")
        return self


    def user_update_elements(self):
        """
        Update elements in the OpenSees model.
        
        For use after the model is built or force-released.
        """
        if not self._opensees_initialized:
            raise RuntimeError("OpenSees model not initialized. Call build_model() first.")
        
        for element in self.geometry.elements.values():
            element.create_in_opensees(self)
            
        self._log("User-initiated element update completed")
        return self

    def _update_time_series(self, time_series_tag):
        """
        Update time series in the OpenSees model.
        
        For use after the model is built or force-released.
        """
        if not self._opensees_initialized:
            raise RuntimeError("OpenSees model not initialized. Call build_model() first.")
        
        time_series=self.loading.time_series[time_series_tag]
        time_series.create_in_opensees()
            
        self._log(f"Time Series tag={time_series_tag} update completed")
        return self

    def user_update_load_pattern(self, pattern_tag):
        """
        Update load patterns in the OpenSees model.
        
        For use after the model is built or force-released.
        """
        if not self._opensees_initialized:
            raise RuntimeError("OpenSees model not initialized. Call build_model() first.")
        load_pattern = self.loading.load_patterns[pattern_tag]
        if hasattr(load_pattern.time_series, 'tag'):
            time_series_tag = load_pattern.time_series.tag
        else:
            time_series_tag = load_pattern.time_series

        self._update_time_series(time_series_tag)
        load_pattern.create_in_opensees()
            
        self._log(f"User-initiated load pattern tag={pattern_tag} update completed")
        return self

    def user_update_all(self):
        """
        Update all components in the OpenSees model.
        
        This is equivalent to build_model() but can be used after the model
        has been force-released or when components have been modified.
        """
        if not self._opensees_initialized:
            self._initialize_opensees_model()
        
        self.user_update_materials()
        self.user_update_sections()
        self.user_update_beam_integrations()
        self.user_update_nodes()
        self.user_update_constraints()
        self.user_update_mp_constraints()
        self.user_update_elements()
        # this should be updated before each analysis for specific loadcase
        # or automatic if run with API analysis
        # self.user_update_time_series()
        # self.user_update_load_patterns()
        
        self._log("User-initiated complete model update completed")
        return self

