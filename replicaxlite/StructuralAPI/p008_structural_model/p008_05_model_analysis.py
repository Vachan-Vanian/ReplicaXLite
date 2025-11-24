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
import opstool as opst
import numpy as np
from tqdm import tqdm


class ModelAnalysis:
    """Handles analysis functions for the structural model"""
    
    def __init__(self, parent_model):
        self.parent = parent_model
        self._next_pattern_id = 1000  # Starting ID for dynamic patterns
        self._current_time = 0.0     # Track analysis time
        self._gravity_applied = False  # Track if gravity has been applied
    
    def _prepare_model(self):
        """Ensure model is built before analysis"""
        if not self.parent._model_built:
            self.parent._log("Building model before analysis...")
            self.parent.build_model()

    def _check_mass_defined(self):
        """
        Check if mass is properly defined in the model.
        
        Returns:
        --------
        bool
            True if mass is defined in the model, False otherwise
        """
        try:
            # Configure system for matrix extraction
            ops.wipeAnalysis()
            ops.system('FullGeneral')
            ops.numberer('Plain')
            ops.constraints('Transformation')
            ops.algorithm('Linear')
            ops.integrator('GimmeMCK', 1.0, 0.0, 0.0)  # Request only mass matrix
            ops.analysis('Transient')
            
            # Perform dummy analysis to generate matrices
            ops.analyze(1, 0.0)
            
            # Get mass matrix
            mass_matrix = ops.printA('-ret')
            
            if not mass_matrix or len(mass_matrix) == 0:
                self.parent._log("WARNING: No mass matrix could be extracted!", level="warning")
                return False
            
            # Check if there's any non-zero mass
            has_mass = any(abs(val) > 1e-10 for val in mass_matrix)
            
            if not has_mass:
                self.parent._log("WARNING: No mass detected in model!", level="warning")
                return False
                
            return True
            
        except Exception as e:
            self.parent._log(f"Error checking mass matrix: {str(e)}", level="warning")
            return False
        finally:
            # Restore analysis configuration
            ops.wipeAnalysis()

    def _create_smart_analyzer(self, analysis_type, smart_analyze_params=None):
        """
        Create a SmartAnalyze instance with the specified parameters.
        
        Parameters:
        -----------
        analysis_type : str
            "Transient" or "Static"
        smart_analyze_params : dict, optional
            Custom parameters for SmartAnalyze configuration
            
        Returns:
        --------
        SmartAnalyze
            Configured SmartAnalyze instance
        """
        # Default SmartAnalyze parameters based on analysis type
        if analysis_type == "Static":
            default_params = {
                "testType": "EnergyIncr",
                "testTol": 1.0e-8,
                "testIterTimes": 25,
                "tryAddTestTimes": True,
                "testIterTimesMore": [50, 100],
                "tryAlterAlgoTypes": True,
                "algoTypes": [40, 10, 20, 30, 50, 60],  # KrylovNewton, Newton, etc.
                "relaxation": 0.5,
                "minStep": 1.0e-6,
                "debugMode": False
            }
        elif analysis_type == "Transient":
            default_params = {
                "testType": "EnergyIncr",
                "testTol": 1.0e-8,
                "testIterTimes": 20,
                "tryAddTestTimes": True,
                "testIterTimesMore": [50],
                "tryAlterAlgoTypes": True,
                "algoTypes": [40, 10, 20, 30],  # KrylovNewton, Newton, etc.
                "relaxation": 0.5,
                "minStep": 1.0e-6,
                "debugMode": False
            }
        else:
            raise AttributeError("Smart_Analysis accept only `Static` or `Transient`.")
        
        # Update with user-provided parameters
        if smart_analyze_params:
            default_params.update(smart_analyze_params)
        
        # Create and return SmartAnalyze instance
        return opst.anlys.SmartAnalyze(analysis_type=analysis_type, **default_params)

    def prepare_next_analysis_stage(self, set_time_0=True, keep_loads=False, remove_recorders=True, 
                                    remove_time_series=None, remove_pattern=None,
                                    clear_damping=False):
        if set_time_0:
            ops.setTime(0.0)
        if keep_loads:
            ops.loadConst()
        if remove_recorders:
            ops.remove('recorders')
        if remove_pattern:
            for p_tag in remove_pattern:
                ops.remove('loadPattern', p_tag)
        if remove_time_series:
            for ts_tag in remove_time_series:
                ops.remove('timeSeries', ts_tag)
        if clear_damping:
            ops.rayleigh(0.0, 0.0, 0.0, 0.0)
            
        ops.wipeAnalysis()    
    
    def run_modal_analysis(self, num_modes=3, odb_tag="modal", solver="-genBandArpack"):
        """
        Run a modal (eigenvalue) analysis.
        
        Parameters:
        -----------
        num_modes : int
            Number of modes to calculate
        odb_tag : str
            Tag for output database
        solver : str
            Eigenvalue solver to use ("-genBandArpack", "-fullGenLapack", etc.)
            
        Returns:
        --------
        dict
            Dictionary with eigenvalues, periods, etc.
        """
        self._prepare_model()
        
        # Check if mass is defined
        self._check_mass_defined()
        
        # Configure eigenvalue analysis
        ops.wipeAnalysis()
        ops.system("BandGeneral")
        ops.numberer("RCM")
        ops.constraints("Transformation")
        
        # Compute eigenvalues
        self.parent._log(f"Computing {num_modes} eigenvalues using {solver}...")
        try:
            opst.post.save_eigen_data(odb_tag=odb_tag, mode_tag=num_modes, solver=solver)
        except Exception as e:
            self.parent._log(f"Modal analysis failed: {str(e)}", level="error")
            return None
        
        model_props, eigen_vectors = opst.post.get_eigen_data(odb_tag=odb_tag)
        model_props_df = model_props.to_pandas()
        eigen_values = model_props_df["eigenLambda"].to_list()
        omega =model_props_df["eigenOmega"].to_list()
        period = model_props_df["eigenPeriod"].to_list()
        frequency = model_props_df["eigenFrequency"].to_list()
        
        
        self.parent._log(f"Modal analysis completed with {num_modes} modes")
        self.parent._log(f"Periods: {period}")
        
        return {
            "eigen_values": eigen_values,
            "omega": omega,
            "period": period,
            "frequency": frequency,
            "odb_tag": odb_tag
        }
    
    def run_gravity_analysis(self, load_pattern_tag, n_steps=10, tol=1.0e-5, max_iter=25, 
                           output_odb_tag="gravity", show_progress=True, 
                           analysis_params=None):
        """
        Run gravity analysis on the model.
        
        Parameters:
        -----------
        load_pattern_tag : int
            Tag for the gravity load pattern
        n_steps : int
            Number of analysis steps
        tol : float
            Convergence tolerance
        max_iter : int
            Maximum iterations per step
        output_odb_tag : str
            Tag for output database
        show_progress : bool
            Whether to show progress bar
        analysis_params : dict, optional
            Custom analysis parameters dictionary
            
        Returns:
        --------
        object
            Analysis output database object
        """
        self._prepare_model()
        #Clean previous analysis
        ops.wipeAnalysis()

        # Verify gravity loads exist in the specified pattern
        if load_pattern_tag not in self.parent.loading.load_patterns:
            self.parent._log(f"Error: Load pattern {load_pattern_tag} not found for gravity analysis", 
                           level="error")
            return None
        
        self.parent.user_update_load_pattern(pattern_tag=load_pattern_tag)

        # Default analysis parameters
        default_params = {
            "system": "BandGeneral",
            "constraints": "Transformation",
            "numberer": "RCM",
            "test_type": "NormDispIncr",
            "test_tolerance": tol,
            "test_iterations": max_iter,
            "test_flag": 0,
            "algorithm": "Newton",
            "integrator": "LoadControl",
            "integrator_arg": 1.0/n_steps,
            "analysis": "Static"
        }
        
        # Use provided parameters or defaults
        params = analysis_params or default_params
        
        # Configure analysis
        ops.system(params.get("system", default_params["system"]))
        ops.constraints(params.get("constraints", default_params["constraints"]))
        ops.numberer(params.get("numberer", default_params["numberer"]))
        ops.test(
            params.get("test_type", default_params["test_type"]),
            params.get("test_tolerance", default_params["test_tolerance"]),
            params.get("test_iterations", default_params["test_iterations"]),
            params.get("test_flag", default_params["test_flag"])
        )
        ops.algorithm(params.get("algorithm", default_params["algorithm"]))
        ops.integrator(
            params.get("integrator", default_params["integrator"]), 
            params.get("integrator_arg", default_params["integrator_arg"])
        )
        ops.analysis(params.get("analysis", default_params["analysis"]))
        
        # Create output database
        odb = opst.post.CreateODB(odb_tag=output_odb_tag)
        
        # Run analysis
        if show_progress:
            step_iter = tqdm(range(n_steps), desc="Running Gravity Analysis", unit="step")
        else:
            step_iter = range(n_steps)
                
        for _ in step_iter:
            result = ops.analyze(1)
            if result < 0:
                self.parent._log("Gravity analysis failed", level="warning")
                break
            odb.fetch_response_step()
        odb.save_response()
        
        self._gravity_applied = True
        
        self.prepare_next_analysis_stage(
            set_time_0=True,
            keep_loads=True,
            remove_recorders=True
        )
        
        self.parent._log(f"Gravity analysis completed with {n_steps} steps")
        return odb

    def run_static_analysis(self, load_pattern_tag,  n_steps=10, output_odb_tag="static", 
                         show_progress=True, analysis_params=None):
        """
        Run a static analysis, building the model first if needed.
        
        Parameters:
        -----------
        load_pattern_tag : int
            Tag for the static load pattern
        n_steps : int
            Number of analysis steps
        output_odb_tag : str
            Tag for output database
        show_progress : bool
            Whether to show progress bar
        analysis_params : dict, optional
            Dictionary of analysis parameters
        Returns:
        --------
        object
            Analysis output database object
        """
        self._prepare_model()
        # Clean previous analysis
        ops.wipeAnalysis()
        # Verify loads exist in the specified pattern
        if load_pattern_tag not in self.parent.loading.load_patterns:
            self.parent._log(f"Error: Load pattern {load_pattern_tag} not found for static analysis", 
                           level="error")
            return None
        self.parent.user_update_load_pattern(pattern_tag=load_pattern_tag)

        # Default analysis parameters
        default_params = {
            "system": "BandGeneral",
            "constraints": "Transformation",
            "numberer": "RCM",
            "test_type": "NormDispIncr",
            "test_tolerance": 1.0e-5,
            "test_iterations": 300,
            "test_flag": 0,
            "algorithm": "Newton",
            "integrator": "LoadControl",
            "integrator_arg": 1.0/n_steps,
            "analysis": "Static"
        }
        
        # Use provided parameters or defaults
        params = analysis_params or default_params
        
        # Configure analysis
        ops.system(params.get("system", default_params["system"]))
        ops.constraints(params.get("constraints", default_params["constraints"]))
        ops.numberer(params.get("numberer", default_params["numberer"]))
        ops.test(
            params.get("test_type", default_params["test_type"]),
            params.get("test_tolerance", default_params["test_tolerance"]),
            params.get("test_iterations", default_params["test_iterations"]),
            params.get("test_flag", default_params["test_flag"])
        )
        ops.algorithm(params.get("algorithm", default_params["algorithm"]))
        ops.integrator(
            params.get("integrator", default_params["integrator"]), 
            params.get("integrator_arg", default_params["integrator_arg"])
        )
        ops.analysis(params.get("analysis", default_params["analysis"]))
        
        # Create output database
        odb = opst.post.CreateODB(odb_tag=output_odb_tag)
        
        # Run analysis
        if show_progress:
            step_iter = tqdm(range(n_steps), desc="Running Static Analysis", unit="step")
        else:
            step_iter = range(n_steps)
                
        for _ in step_iter:
            result = ops.analyze(1)  # one step of analysis
            if result < 0:
                self.parent._log("Static analysis failed", level="warning")
                break
            odb.fetch_response_step()  # fetch the response on the current step
        odb.save_response()

        self.prepare_next_analysis_stage(
            set_time_0=True,
            keep_loads=False,
            remove_recorders=True
        )
        
        self.parent._log(f"Static analysis completed with {n_steps} steps")
        return odb
    
    def run_pushover_analysis(self, load_pattern_tag, control_node, control_dof, 
                        target_protocol, max_step,
                        output_odb_tag="pushover",
                        analysis_params=None,
                        smart_analyze_params=None):
        """
        Run a displacement-controlled pushover analysis using SmartAnalyze.
        
        Parameters:
        -----------
        load_pattern_tag : int
            Tag of lateral load pattern to use
        control_node : int
            Node ID for displacement control
        control_dof : int
            Degree of freedom for control (1=X, 2=Y, 3=Z)
        target_protocol : list
            Target displacement history to reach
        output_odb_tag : str
            Tag for output database
        max_step : float
            Maximum step size for displacement history split
        analysis_params : dict, optional
            System-level analysis parameters
        smart_analyze_params : dict, optional
            Custom parameters for SmartAnalyze configuration
            
        Returns:
        --------
        object
            Analysis output database object
        """
        self._prepare_model()
        
        # Verify load pattern exists
        if load_pattern_tag not in self.parent.loading.load_patterns:
            self.parent._log(f"Error: Load pattern {load_pattern_tag} not found for pushover analysis", 
                        level="error")
            return None
        self.parent.user_update_load_pattern(pattern_tag=load_pattern_tag)
                
        # Default analysis parameters
        default_params = {
            "system": "UmfPack",  # More robust sparse solver
            "constraints": "Transformation",
            "numberer": "RCM"
        }
        
        # Use provided parameters or defaults
        params = default_params.copy()
        if analysis_params:
            params.update(analysis_params)
        
        # Configure system components
        ops.wipeAnalysis()
        ops.system(params.get("system", default_params["system"]))
        ops.constraints(params.get("constraints", default_params["constraints"]))
        ops.numberer(params.get("numberer", default_params["numberer"]))
        
        # Create output database
        odb = opst.post.CreateODB(odb_tag=output_odb_tag)
        
        # Create SmartAnalyze for Static analysis
        smart_analyze = self._create_smart_analyzer("Static", smart_analyze_params)

        segments = smart_analyze.static_split(target_protocol, maxStep=max_step)      
        
        # Run the analysis using SmartAnalyze
        step_count = 0
        
        for i, seg in enumerate(segments):
            # Run static analysis step with SmartAnalyze
            result = smart_analyze.StaticAnalyze(control_node, control_dof, seg)
            
            if result < 0:
                self.parent._log(f"Pushover analysis failed at step {i+1}", level="warning")
                break
                
            step_count += 1
            odb.fetch_response_step()
        
                
        # Save response data
        odb.save_response()
    
        # Clean up
        smart_analyze.close()

        self.prepare_next_analysis_stage(
            set_time_0=True,
            keep_loads=False,
            remove_recorders=True
        )

        # Log analysis completion
        self.parent._log(f"Pushover analysis completed with {step_count} steps")
        
        return odb

    def run_time_history_analysis(self, time_history, dt, n_steps, 
                                eigenvalues=None, damping_ratio=0.05, 
                                odb_tag="timehistory", direction=1, 
                                scale_factor=1.0, analysis_params=None,
                                pattern_type="UniformExcitation",
                                smart_analyze_params=None,
                                support_nodes=None):
        """
        Run a time history analysis with support for acceleration, velocity, and displacement inputs.
        
        Parameters:
        -----------
        time_history : dict
            Dictionary with 'time' and at least one of 'accel', 'vel', or 'disp' arrays
        dt : float
            Time step
        n_steps : int
            Number of analysis steps
        eigenvalues : list, optional
            Pre-computed eigenvalues for damping calculation from modal analysis
        damping_ratio : float
            Rayleigh damping ratio
        odb_tag : str
            Tag for output database
        direction : int
            Direction of excitation (1=X, 2=Y, 3=Z) - used for both UniformExcitation and MultipleSupport
        scale_factor : float
            Scale factor for time series values
        analysis_params : dict, optional
            Dictionary of analysis parameters
        pattern_type : str
            Type of pattern to use ("UniformExcitation" or "MultipleSupport")
            For MultipleSupport, also specify support_nodes parameter
        smart_analyze_params:  dict, optional
            Dictionary of Smart Analysis parameters
        support_nodes : list, optional
            List of node tags for MultipleSupport patterns where imposed motion will be applied.
            The motion is applied in the direction specified by the 'direction' parameter.
            
            Example:
            support_nodes = [1, 2, 5, 10]  # Motion applied to nodes 1, 2, 5, 10 in specified direction
            
        Returns:
        --------
        object
            Analysis output database object
        """
        # Prepare model
        self._prepare_model()

        # Clean and remove previous analysis
        ops.wipeAnalysis()
        
        # Generate tags
        pattern_tag = self._next_pattern_id
        self._next_pattern_id += 1
        
        # Record all time series and patterns to clean up later
        created_time_series = []
        created_patterns = [pattern_tag]
        
        # Check if time array exists
        if "time" not in time_history:
            raise ValueError("Time history must contain 'time' array")
        time_array = time_history["time"]
        
        # Initialize time series tags
        accel_series_tag = None
        vel_series_tag = None
        disp_series_tag = None
        
        # Create time series for acceleration if provided
        if "accel" in time_history:
            accel_array = time_history["accel"]
            accel_series_tag = self._next_pattern_id
            self._next_pattern_id += 1
            
            accel_ts = self.parent.loading.create_path_time_series(
                tag=accel_series_tag,
                time=list(time_array),
                values=list(accel_array),
                factor=scale_factor
            )
            accel_ts.create_in_opensees()
            created_time_series.append(accel_series_tag)
        
        # Create time series for velocity if provided
        if "vel" in time_history:
            vel_array = time_history["vel"]
            vel_series_tag = self._next_pattern_id
            self._next_pattern_id += 1
            
            vel_ts = self.parent.loading.create_path_time_series(
                tag=vel_series_tag,
                time=list(time_array),
                values=list(vel_array),
                factor=scale_factor
            )
            vel_ts.create_in_opensees()
            created_time_series.append(vel_series_tag)
        
        # Create time series for displacement if provided
        if "disp" in time_history:
            disp_array = time_history["disp"]
            disp_series_tag = self._next_pattern_id
            self._next_pattern_id += 1
            
            disp_ts = self.parent.loading.create_path_time_series(
                tag=disp_series_tag,
                time=list(time_array),
                values=list(disp_array),
                factor=scale_factor
            )
            disp_ts.create_in_opensees()
            created_time_series.append(disp_series_tag)
        
        # Verify that at least one time series was created
        if not any([accel_series_tag, vel_series_tag, disp_series_tag]):
            raise ValueError("Time history must contain at least one of 'accel', 'vel', or 'disp' arrays")
        
        # Create pattern based on pattern_type
        if pattern_type == "UniformExcitation":
            # Create uniform excitation pattern
            excitation_pattern = self.parent.loading.create_uniform_excitation_pattern(
                tag=pattern_tag,
                direction=direction,
                accel_series_tag=accel_series_tag,
                vel_series_tag=vel_series_tag,
                disp_series_tag=disp_series_tag
            )
            excitation_pattern.create_in_opensees()
            
            # Warn if support_nodes is provided for UniformExcitation
            if support_nodes:
                self.parent._log(
                    "Warning: support_nodes parameter is ignored for UniformExcitation patterns", 
                    level="warning"
                )
        
        elif pattern_type == "MultipleSupport":
            # Create multiple support pattern
            multi_pattern = self.parent.loading.create_multiple_support_pattern(tag=pattern_tag)
            
            # Add default ground motion
            default_gm_tag = pattern_tag + 1000  # Unique ground motion tag
            
            # Add all provided time series to the default ground motion
            self.parent.loading.add_plain_ground_motion(
                pattern=multi_pattern,
                gm_tag=default_gm_tag,
                accel_series_tag=accel_series_tag,
                vel_series_tag=vel_series_tag,
                disp_series_tag=disp_series_tag,
                factor=1.0
            )
            
            # Handle imposed supports automatically
            if support_nodes:
                # Validate support_nodes format
                if not isinstance(support_nodes, list):
                    raise ValueError("support_nodes must be a list of node tags")
                
                for node_tag in support_nodes:
                    # Validate node tag is integer
                    if not isinstance(node_tag, int):
                        raise ValueError(f"Node tag must be an integer, got: {node_tag}")
                    
                    # Validate node exists
                    if node_tag not in self.parent.geometry.nodes:
                        raise ValueError(f"Node {node_tag} not found in model")
                    
                    # Add imposed motion using the direction parameter (same as UniformExcitation)
                    self.parent.loading.add_imposed_motion(
                        pattern=multi_pattern,
                        node_tag=node_tag,
                        dof=direction,
                        gm_tag=default_gm_tag
                    )
                
                self.parent._log(f"Added imposed motions to {len(support_nodes)} nodes in direction {direction}")
            else:
                self.parent._log(
                    "Note: MultipleSupport pattern created but no support_nodes specified. "
                    "The pattern will not apply any ground motion to the structure.", 
                    level="warning"
                )
            
            # Create the pattern in OpenSees
            multi_pattern.create_in_opensees()
            
        else:
            raise ValueError(f"Unsupported pattern type: {pattern_type}")
        
        # Set up Rayleigh damping if eigenvalues provided
        if eigenvalues is not None:
            if len(eigenvalues) < 2:
                raise ValueError("At least two eigenvalues must be provided for Rayleigh damping calculation")
                
            omega1 = np.sqrt(eigenvalues[0])
            omega2 = np.sqrt(eigenvalues[1])
            
            alpha_m = damping_ratio * 2 * omega1 * omega2 / (omega1 + omega2)
            beta_k = damping_ratio * 2 / (omega1 + omega2)
            
            self.parent._log(f"Rayleigh damping: alpha_m={alpha_m}, beta_k={beta_k}")
            ops.rayleigh(alpha_m, 0.0, 0.0, beta_k)
        
        # Default analysis parameters
        # Better defaults for MultipleSupport
        if pattern_type == "MultipleSupport":
            default_params = {
                "system": "UmfPack",
                "constraints": "Transformation", 
                "numberer": "RCM",
                "integrator": "Newmark",
                "integrator_args": [0.5, 0.25]
            }
        else:  # UniformExcitation
            default_params = {
                "system": "BandGeneral",  # Fine for uniform excitation
                "constraints": "Transformation",
                "numberer": "RCM", 
                "integrator": "Newmark",
                "integrator_args": [0.5, 0.25]
            }
        
        # Use provided parameters or defaults
        params = analysis_params or default_params
        
        # Setup dynamic analysis
        ops.system(params.get("system", default_params["system"]))
        ops.constraints(params.get("constraints", default_params["constraints"]))
        ops.numberer(params.get("numberer", default_params["numberer"]))
        
        # Handle different integrators
        integrator = params.get("integrator", default_params["integrator"])
        if integrator == "Newmark":
            # Default Newmark parameters
            gamma, beta = 0.5, 0.25
            if "integrator_args" in params:
                if len(params["integrator_args"]) >= 2:
                    gamma, beta = params["integrator_args"][0], params["integrator_args"][1]
            ops.integrator(integrator, gamma, beta)
        elif "integrator_args" in params:
            ops.integrator(integrator, *params["integrator_args"])
        else:
            ops.integrator(integrator)
        
        # Create output database
        odb = opst.post.CreateODB(odb_tag=odb_tag)
        
        # Initialize SmartAnalyze for transient analysis
        smart_analyze = self._create_smart_analyzer("Transient", smart_analyze_params)
        
        # Prepare transient steps
        segs = smart_analyze.transient_split(n_steps) 

        # Run analysis
        self.parent._log(f"Running time history analysis with SmartAnalyze ({n_steps} steps)")
        success_steps = 0
        
        for i in range(n_steps):
            # Run single step with SmartAnalyze
            result = smart_analyze.TransientAnalyze(dt)
            
            if result < 0:
                self.parent._log(f"Time history analysis failed at step {i+1}", level="warning")
                break
            
            success_steps += 1
            odb.fetch_response_step()
                
        # Save response data with compression
        odb.save_response(zlib=True)
        
        # Clean up
        smart_analyze.close()
        
        # Prepare for next analysis stage with targeted cleanup
        self.prepare_next_analysis_stage(
            set_time_0=True,
            keep_loads=False,
            remove_recorders=True,
            remove_time_series=created_time_series,
            remove_pattern=created_patterns,
            clear_damping=True
        )
        
        self.parent._log(f"Time history analysis completed with {success_steps} successful steps")
        self.parent._log(f"Current analysis time: {self._current_time}")
        
        return odb
