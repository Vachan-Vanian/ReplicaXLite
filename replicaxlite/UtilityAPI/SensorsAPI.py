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


import os
import csv
import datetime
import json
import numpy as np
from scipy import signal
import matplotlib.pyplot as plt
from scipy.integrate import cumulative_trapezoid
from .UnitsAPI import ReplicaXUnits


# Stand‑alone utility function
def calculate_integrals(x, y, n=1, initial=0.0):
    """
    Return the first … n‑th cumulative integrals of y w.r.t. x (using the
    trapezoidal rule).

    Parameters
    ----------
    x : 1-D array-like
        Monotonically increasing time vector.
    y : 1-D array-like
        Samples of the signal to integrate.
    n : int, default 1
        Order of the last integral to return (n ≥ 1).
    initial : float, default 0.0
        Initial value for each cumulative integration.

    Returns
    -------
    list[np.ndarray]
        A list of length 'n'; element 'k' is the (k+1)-th integral.
        For example, n=2 → [ first_integral, second_integral ].
    """
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)

    if x.ndim != 1 or y.ndim != 1:
        raise ValueError("x and y must be 1-D")
    if x.size != y.size:
        raise ValueError("x and y must have the same length")
    if np.any(np.diff(x) < 0):
        raise ValueError("x must be sorted in ascending order")
    if n < 1:
        raise ValueError("n must be ≥ 1")

    integrals = []
    current = y
    for _ in range(n):
        current = cumulative_trapezoid(current, x, initial=initial)
        integrals.append(current)

    return integrals


def excel_to_zero_based_row(excel_row):
    """Convert from Excel's 1-based row index to 0-based index"""
    return excel_row - 1

def zero_based_to_excel_row(zero_row):
    """Convert from 0-based row index to Excel's 1-based index"""
    return zero_row + 1

def excel_column_to_index(column_letter):
    """Convert Excel column letter (A, B, C...) to 0-based index"""
    return ord(column_letter.upper()) - ord('A')

def index_to_excel_column(column_index):
    """Convert 0-based column index to Excel column letter (A, B, C...)"""
    return chr(column_index + ord('A'))

def get_cell_reference(excel_row, excel_column):
    """Get Excel cell reference (e.g., 'A1') from Excel row and column"""
    return f"{excel_column}{excel_row}"


class ReplicaXSensorDataReader:
    def __init__(self, config=None):
        """Initialize with an optional configuration dictionary"""
        # Initialize empty configuration
        self.config = config or {}
        self.processed_data = {}
        self.time_array = None
        
        # Simple string for logging
        self.log = "Log started\n"
        
        # Initialize unit converter
        self.converter = ReplicaXUnits()
        self.log_info("Unit converter initialized")
        
        # If configuration is provided, process the data
        if self.config and self._validate_config():
            self.process_data()
    
    def load_config_from_json(self, json_file_path):
        """Load configuration from a JSON file"""
        try:
            with open(json_file_path, 'r') as json_file:
                self.config = json.load(json_file)
            self.log_info(f"Configuration loaded from {json_file_path}")
            
            if self._validate_config():
                self.process_data()
                return True
            return False
        except Exception as e:
            self.log_error(f"Error loading configuration from JSON: {e}")
            return False
    
    def load_config_from_dict(self, config_dict):
        """Load configuration from a dictionary"""
        try:
            self.config = config_dict.copy()
            self.log_info("Configuration loaded from dictionary")
            
            if self._validate_config():
                self.process_data()
                return True
            return False
        except Exception as e:
            self.log_error(f"Error loading configuration from dictionary: {e}")
            return False
    
    def export_config_to_json(self, json_file_path):
        """Export current configuration to a JSON file"""
        try:
            with open(json_file_path, 'w') as json_file:
                json.dump(self.config, json_file, indent=4)
            self.log_info(f"Configuration exported to {json_file_path}")
            return True
        except Exception as e:
            self.log_error(f"Error exporting configuration to JSON: {e}")
            return False
    
    def export_config_to_dict(self):
        """Export current configuration as a dictionary"""
        return self.config.copy()
    
    def update_config(self, new_config):
        """Update the configuration with new values"""
        self.config.update(new_config)
        self.log_info("Configuration updated")
        
        # Clear processed data
        self.processed_data = {}
        self.time_array = None
        
        # Re-process data if configuration is valid
        if self._validate_config():
            self.process_data()
            return True
        return False
    
    def _validate_config(self):
        """Validate the configuration parameters"""
        required_params = [
            "file_path", "seperator", "decimal", "start_row", "end_row", 
            "dt", "time_column", 
            "data_type", "input_units", "output_units", 
            "data", "data_name", "data_correction"
        ]
        
        for param in required_params:
            if param not in self.config:
                self.log_error(f"Required configuration parameter '{param}' is missing")
                return False
        
        return True
    
    def log_info(self, message):
        """Add an info message to the log"""
        self.log += f"INFO: {message}\n"
    
    def log_warning(self, message):
        """Add a warning message to the log"""
        self.log += f"WARNING: {message}\n"
    
    def log_error(self, message):
        """Add an error message to the log"""
        self.log += f"ERROR: {message}\n"
    
    def print_log(self):
        """Print the log to the console"""
        print(self.log)
    
    def _apply_resample_correction(self, time_array, data_arrays, target_fs, method='linear'):
        """
        Resample time and data arrays to a uniform sampling rate
        
        Args:
            time_array: Original time array
            data_arrays: Dictionary mapping sensor names to data arrays
            target_fs: Target sampling frequency in Hz
            method: Interpolation method ('linear', 'cubic', 'nearest', etc.)
            
        Returns:
            Tuple containing new time array and dictionary of resampled data arrays
        """
        try:
            # Import scipy for advanced interpolation methods
            if method != 'linear':
                try:
                    from scipy import interpolate
                except ImportError:
                    self.log_error("SciPy required for advanced interpolation methods")
                    method = 'linear'  # Fallback to linear
            
            target_dt = 1.0 / target_fs
            
            # Create new uniform time array
            start_time = time_array[0]
            end_time = time_array[-1]
            new_time_array = np.arange(start_time, end_time + target_dt, target_dt)
            
            # Store original length for logging
            original_length = len(time_array)
            resampled_length = len(new_time_array)
            
            # Resample each data array
            resampled_data = {}
            for sensor_name, data_array in data_arrays.items():
                # Choose interpolation method
                if method == 'linear':
                    # Use numpy's interp for linear interpolation (faster)
                    new_values = np.interp(new_time_array, time_array, data_array)
                else:
                    # Use scipy's interp1d for other methods
                    f = interpolate.interp1d(
                        time_array, data_array, 
                        kind=method, 
                        bounds_error=False, 
                        fill_value=(data_array[0], data_array[-1])
                    )
                    new_values = f(new_time_array)
                
                resampled_data[sensor_name] = new_values
            
            self.log_info(f"Applied resample correction: {original_length} to {resampled_length} points")
            self.log_info(f"Target sampling rate: {target_fs} Hz (dt = {target_dt}s)")
            
            return new_time_array, resampled_data
        
        except Exception as e:
            self.log_error(f"Error in resampling: {e}")
            return time_array, data_arrays  # Return original arrays on error

    def _apply_zero_start_y_correction(self, data_array, n_values=None):
        """Shift the y values to start at 0 by examining the first n values"""
        if n_values is None or n_values <= 0:
            self.log_warning(f"zero_start_y_correction: n_values ({n_values}) <=0. Using only first value.")
            n_values = 1
            
        if n_values > len(data_array):
            self.log_warning(f"zero_start_y_correction: n_values ({n_values}) exceeds data array length ({len(data_array)}). Using all values.")
            n_values = len(data_array)  # Use the full array
            
        # Calculate average of first n values
        avg_start = np.mean(data_array[:n_values])
        self.log_info(f"Applied zero_start_y correction: shifted by {avg_start}")
        
        # Subtract this average from all values
        return data_array - avg_start
    
    def _apply_reverse_y_correction(self, data_array):
        """Reverse the y values (multiply by -1)"""
        self.log_info("Applied reverse_y correction")
        return data_array * -1
    
    def _apply_stretch_y_correction(self, data_array, stretch_factor):
        """
        Stretch y values by adding stretch_factor to multiply data
        """
        self.log_info(f"Applied stretch_y correction: factor = {stretch_factor}")
        
        # Create a copy of the array to avoid modifying the original
        result = np.copy(data_array)

        result *= stretch_factor

        return result
    
    def _apply_shift_time_correction(self, time_array, shift_value):
        """Add or subtract time values"""
        self.log_info(f"Applied shift_time correction: shifted by {shift_value}")
        return time_array + shift_value
    
    def _apply_normalize_correction(self, data_array):
        """Normalize values by dividing by the maximum absolute value"""
        max_abs_value = max(abs(np.min(data_array)), abs(np.max(data_array)))
        
        if max_abs_value > 0:
            self.log_info(f"Applied normalize correction: divided by {max_abs_value}")
            return data_array / max_abs_value
        else:
            self.log_warning("Cannot normalize: maximum absolute value is 0")
            return data_array

    def _apply_detrend_correction(self, data_array, detrend_type='linear', detrend_degree=2):
        """
        Remove trend from data using either linear or polynomial detrending
        
        Args:
            data_array: Input array to detrend
            detrend_type: Type of detrending ('linear' or 'poly')
            detrend_degree: Degree of polynomial for 'poly' detrending
                
        Returns:
            Detrended data array
        """
        try:
            if detrend_type == 'linear':
                # Use scipy's built-in linear detrend
                detrended_array = signal.detrend(data_array)
                self.log_info("Applied linear detrend correction (removed linear trend)")
                return detrended_array
            
            elif detrend_type == 'poly':
                # Apply polynomial detrending using numpy's polyfit
                x = np.arange(len(data_array))
                coeffs = np.polyfit(x, data_array, detrend_degree)
                trend = np.polyval(coeffs, x)
                detrended_array = data_array - trend
                
                self.log_info(f"Applied polynomial detrend correction (degree={detrend_degree})")
                return detrended_array
            
            else:
                self.log_warning(f"Unknown detrend type '{detrend_type}', using 'linear'")
                return signal.detrend(data_array)
                
        except Exception as e:
            self.log_error(f"Error applying detrend correction: {e}")
            return data_array  # Return original data on error

    def _apply_derivative_correction(self, data_array, dt=None):
        """
        Calculate the numerical derivative of a data array using np.gradient
        
        Args:
            data_array: Input array
            dt: Time step for differentiation (if None, use from config)
            
        Returns:
            Derivative of data array
        """
        if dt is None:
            # Calculate actual sampling frequency from time array
            if len(self.time_array) > 1:
                dt = float(np.mean(np.diff(self.time_array)))
            else:
                dt = self.config["dt"]
                self.log_warning("Single data point, using config dt for filter")
        
        # Calculate derivative using np.gradient
        derivative = np.gradient(data_array, dt)
        
        self.log_info(f"Applied derivative correction using np.gradient (dt={dt})")
        return derivative
    
    def _apply_trim_time_correction(self, time_array, data_arrays, start_time=None, end_time=None):
        """
        Trim time and data arrays to a specified time range while preserving dt
        
        Args:
            time_array: Time array
            data_arrays: Dictionary mapping sensor names to data arrays
            start_time: Start time for trimming (if None, use first time)
            end_time: End time for trimming (if None, use last time)
            
        Returns:
            Tuple containing trimmed time array and dictionary of trimmed data arrays
        """
        if start_time is None:
            start_time = time_array[0]
        
        if end_time is None:
            end_time = time_array[-1]
        
        # Ensure start_time <= end_time
        if start_time > end_time:
            start_time, end_time = end_time, start_time
            self.log_warning("Trim start_time > end_time; values were swapped")
        
        # Calculate dt from config
        # dt = self.config.get("dt", 0.001)
        if len(time_array) > 1:
            dt = np.mean(np.diff(time_array))
        else:
            dt = self.config["dt"]
            self.log_warning("Single data point, using config dt")
        
        # Find nearest indices that maintain dt spacing
        start_idx = int(round((start_time - time_array[0]) / dt))
        end_idx = int(round((end_time - time_array[0]) / dt))
        
        # Bound indices to valid range
        start_idx = max(0, start_idx)
        end_idx = min(len(time_array) - 1, end_idx)
        
        # Check if any points were found
        if start_idx > end_idx:
            self.log_error(f"No data points found between {start_time} and {end_time} at dt={dt}")
            return time_array, data_arrays
        
        # Extract time and data using indices
        new_time_array = time_array[start_idx:end_idx+1]
        
        # Get new data arrays
        new_data_arrays = {}
        for sensor_name, data_array in data_arrays.items():
            new_data_arrays[sensor_name] = data_array[start_idx:end_idx+1]
        
        # Log actual trim boundaries
        actual_start = new_time_array[0]
        actual_end = new_time_array[-1]
        
        self.log_info(f"Applied trim correction: {len(time_array)} to {len(new_time_array)} points")
        self.log_info(f"Requested time range: {start_time} to {end_time}")
        self.log_info(f"Actual time range: {actual_start} to {actual_end} (preserving dt={dt})")
        
        return new_time_array, new_data_arrays

    def _apply_zero_start_time_correction(self, time_array):
        """Shift time values to start at exactly 0"""
        time_offset = time_array[0]
        
        self.log_info(f"Applied zero_start_time correction: shifted by {time_offset}")
        return time_array - time_offset

    def _apply_detrend_correction(self, data_array, detrend_type='linear', detrend_degree=2):
        """
        Remove trend from data using either linear or polynomial detrending
        
        Args:
            data_array: Input array to detrend
            detrend_type: Type of detrending ('linear' or 'poly')
            detrend_degree: Degree of polynomial for 'poly' detrending
                
        Returns:
            Detrended data array
        """
        try:
            if detrend_type == 'linear':
                # Use scipy's built-in linear detrend
                detrended_array = signal.detrend(data_array)
                self.log_info("Applied linear detrend correction (removed linear trend)")
                return detrended_array
            
            elif detrend_type == 'poly':
                # Apply polynomial detrending using numpy's polyfit
                x = np.arange(len(data_array))
                coeffs = np.polyfit(x, data_array, detrend_degree)
                trend = np.polyval(coeffs, x)
                detrended_array = data_array - trend
                
                self.log_info(f"Applied polynomial detrend correction (degree={detrend_degree})")
                return detrended_array
            
            else:
                self.log_error(f"Unknown detrend type '{detrend_type}', NO detrend correction applied. Returning original data.")
                return data_array  # Return original data on error
                
        except Exception as e:
            self.log_error(f"Error applying detrend correction: {e}")
            return data_array  # Return original data on error

    def _apply_filter_correction(self, data_array, filter_config):
        """
        Apply different types of filters to the data array
        
        Args:
            data_array: Input signal to filter
            filter_config: Dictionary with filter configuration
                
        Returns:
            Filtered data array
        """
        filter_type = filter_config.get("type", "none")
        params = filter_config.get("params", {})
        
        if filter_type == 'none':
            self.log_info("No filter applied (filter type is 'none')")
            return data_array
        
        # Get sampling parameters once for all filter types
        if len(self.time_array) > 1:
            dt = float(np.mean(np.diff(self.time_array)))
        else:
            dt = self.config["dt"]
            self.log_warning("Single data point, using config dt")
        fs = 1/dt
        nyquist = 0.5 * fs
            
        # ======== CLASSICAL IIR FILTERS ========
        if filter_type in ['butterworth', 'chebyshev1', 'chebyshev2', 'elliptic', 'bessel']:
            try:
                # Common parameters for all IIR filters
                order = params.get('order', 4)
                btype = params.get('btype', 'low')  # Filter type: 'low', 'high', 'band', 'bandstop'
                zero_phase = params.get('zero_phase', True)  # Use filtfilt for zero-phase filtering?
                
                # Parameters for specific filter types
                rp = params.get('rp', 1.0)  # Passband ripple in dB (Chebyshev I, Elliptic)
                rs = params.get('rs', 40.0)  # Stopband ripple in dB (Chebyshev II, Elliptic)
                
                # Initialize filter design variables
                b, a = None, None
                
                # Handle different filter types
                if btype in ['low', 'high']:
                    # Single cutoff filters (low-pass or high-pass)
                    cutoff = params.get('cutoff', 0.1)  # Single cutoff frequency
                    normal_cutoff = cutoff / nyquist
                    
                    # Log filter parameters
                    filter_log = f"Applied {filter_type.capitalize()} filter: order={order}, type={btype}, "
                    filter_log += f"cutoff={cutoff}Hz (normalized={normal_cutoff:.4f})"
                    
                    # Design filter based on type
                    if filter_type == 'butterworth':
                        b, a = signal.butter(order, normal_cutoff, btype=btype)
                    elif filter_type == 'chebyshev1':
                        b, a = signal.cheby1(order, rp, normal_cutoff, btype=btype)
                    elif filter_type == 'chebyshev2':
                        b, a = signal.cheby2(order, rs, normal_cutoff, btype=btype)
                    elif filter_type == 'elliptic':
                        b, a = signal.ellip(order, rp, rs, normal_cutoff, btype=btype)
                    elif filter_type == 'bessel':
                        b, a = signal.bessel(order, normal_cutoff, btype=btype, norm='phase')
                
                elif btype in ['band', 'bandstop']:
                    # Dual cutoff filters (band-pass or band-stop)
                    cutoff_low = params.get('cutoff_low', 0.1)  # Lower cutoff
                    cutoff_high = params.get('cutoff_high', 0.2)  # Upper cutoff
                    
                    normal_cutoff_low = cutoff_low / nyquist
                    normal_cutoff_high = cutoff_high / nyquist
                    
                    # Ensure cutoffs are in the correct order
                    if normal_cutoff_low > normal_cutoff_high:
                        normal_cutoff_low, normal_cutoff_high = normal_cutoff_high, normal_cutoff_low
                        
                    # Log filter parameters
                    filter_log = f"Applied {filter_type.capitalize()} filter: order={order}, type={btype}, "
                    filter_log += f"cutoff_low={cutoff_low}Hz (normalized={normal_cutoff_low:.4f}), "
                    filter_log += f"cutoff_high={cutoff_high}Hz (normalized={normal_cutoff_high:.4f})"
                    
                    # Design filter based on type
                    if filter_type == 'butterworth':
                        b, a = signal.butter(order, [normal_cutoff_low, normal_cutoff_high], btype=btype)
                    elif filter_type == 'chebyshev1':
                        b, a = signal.cheby1(order, rp, [normal_cutoff_low, normal_cutoff_high], btype=btype)
                    elif filter_type == 'chebyshev2':
                        b, a = signal.cheby2(order, rs, [normal_cutoff_low, normal_cutoff_high], btype=btype)
                    elif filter_type == 'elliptic':
                        b, a = signal.ellip(order, rp, rs, [normal_cutoff_low, normal_cutoff_high], btype=btype)
                    elif filter_type == 'bessel':
                        b, a = signal.bessel(order, [normal_cutoff_low, normal_cutoff_high], btype=btype, norm='phase')
                
                else:
                    self.log_warning(f"Unknown filter btype: {btype}. Using 'low' instead.")
                    normal_cutoff = params.get('cutoff', 0.1) / nyquist
                    
                    # Design a default low-pass filter
                    if filter_type == 'butterworth':
                        b, a = signal.butter(order, normal_cutoff, btype='low')
                    elif filter_type == 'chebyshev1':
                        b, a = signal.cheby1(order, rp, normal_cutoff, btype='low')
                    elif filter_type == 'chebyshev2':
                        b, a = signal.cheby2(order, rs, normal_cutoff, btype='low')
                    elif filter_type == 'elliptic':
                        b, a = signal.ellip(order, rp, rs, normal_cutoff, btype='low')
                    elif filter_type == 'bessel':
                        b, a = signal.bessel(order, normal_cutoff, btype='low', norm='phase')
                
                # Apply filter
                if b is not None and a is not None:
                    self.log_info(filter_log)
                    if zero_phase:
                        # Zero-phase forward-backward filtering (no phase distortion)
                        return signal.filtfilt(b, a, data_array)
                    else:
                        # Standard causal filtering
                        return signal.lfilter(b, a, data_array)
                else:
                    self.log_error(f"Filter design failed for {filter_type}")
                    return data_array
                    
            except Exception as e:
                self.log_error(f"Error applying {filter_type} filter: {e}")
                return data_array  # Return original data on error
        
        # ======== FIR FILTER (Finite Impulse Response) ========
        elif filter_type == 'fir':
            try:
                # Get FIR filter parameters
                numtaps = params.get('numtaps', 101)  # Number of filter taps (should be odd)
                btype = params.get('btype', 'low')  # Filter type
                window = params.get('window', 'hamming')  # Window function
                
                # Make sure numtaps is odd
                if numtaps % 2 == 0:
                    numtaps += 1
                    self.log_warning(f"Adjusted numtaps to odd value: {numtaps}")
                
                b = None  # FIR filter coefficients
                
                # Design FIR filter based on type
                if btype in ['low', 'high']:
                    cutoff = params.get('cutoff', 0.1)
                    normal_cutoff = cutoff / nyquist
                    
                    filter_log = f"Applied FIR filter: numtaps={numtaps}, type={btype}, "
                    filter_log += f"cutoff={cutoff}Hz (normalized={normal_cutoff:.4f}), window={window}"
                    
                    if btype == 'low':
                        b = signal.firwin(numtaps, normal_cutoff, window=window)
                    elif btype == 'high':
                        b = signal.firwin(numtaps, normal_cutoff, window=window, pass_zero=False)
                
                elif btype in ['band', 'bandstop']:
                    cutoff_low = params.get('cutoff_low', 0.1)
                    cutoff_high = params.get('cutoff_high', 0.2)
                    
                    normal_cutoff_low = cutoff_low / nyquist
                    normal_cutoff_high = cutoff_high / nyquist
                    
                    # Ensure cutoffs are in the correct order
                    if normal_cutoff_low > normal_cutoff_high:
                        normal_cutoff_low, normal_cutoff_high = normal_cutoff_high, normal_cutoff_low
                    
                    filter_log = f"Applied FIR filter: numtaps={numtaps}, type={btype}, "
                    filter_log += f"cutoff_low={cutoff_low}Hz (normalized={normal_cutoff_low:.4f}), "
                    filter_log += f"cutoff_high={cutoff_high}Hz (normalized={normal_cutoff_high:.4f}), window={window}"
                    
                    if btype == 'band':
                        b = signal.firwin(numtaps, [normal_cutoff_low, normal_cutoff_high], window=window, pass_zero=False)
                    elif btype == 'bandstop':
                        b = signal.firwin(numtaps, [normal_cutoff_low, normal_cutoff_high], window=window)
                
                else:
                    self.log_warning(f"Unknown FIR filter type: {btype}. Using 'low' instead.")
                    normal_cutoff = params.get('cutoff', 0.1) / nyquist
                    b = signal.firwin(numtaps, normal_cutoff, window=window)
                    
                    filter_log = f"Applied FIR low-pass filter: numtaps={numtaps}, "
                    filter_log += f"cutoff={cutoff}Hz (normalized={normal_cutoff:.4f}), window={window}"
                
                # Apply FIR filter
                if b is not None:
                    self.log_info(filter_log)
                    
                    # Check if zero-phase filtering is requested
                    zero_phase = params.get('zero_phase', True)
                    if zero_phase:
                        # Use filtfilt for zero-phase filtering
                        return signal.filtfilt(b, [1.0], data_array)
                    else:
                        # Standard causal filtering
                        return signal.lfilter(b, [1.0], data_array)
                else:
                    self.log_error("FIR filter design failed")
                    return data_array
                    
            except Exception as e:
                self.log_error(f"Error applying FIR filter: {e}")
                return data_array
            
        # ======== SAVITZKY-GOLAY FILTER ========
        elif filter_type == 'savgol':
            # Savitzky-Golay filter
            window_length = params.get('window_length', 11)
            polyorder = params.get('polyorder', 3)
            self.log_info(f"Applied Savitzky-Golay filter: window_length={window_length}, polyorder={polyorder}")
            return signal.savgol_filter(data_array, window_length=window_length, polyorder=polyorder)
        
        # ======== MOVING AVERAGE FILTER ========
        elif filter_type == 'moving_avg':
            # Moving average filter
            window_size = params.get('window_size', 11)
            self.log_info(f"Applied moving average filter: window_size={window_size}")
            return np.convolve(data_array, np.ones(window_size)/window_size, mode='same')

        # ======== UNKNOWN FILTER TYPE ========
        else:
            self.log_warning(f"Unknown filter type: {filter_type}. No filter applied.")
            return data_array


    def process_data(self):
        """Process data from CSV and prepare for x,y pair examination"""
        if not self._validate_config():
            self.log_error("Invalid configuration. Cannot process data.")
            return False
                
        try:
            self.log_info(f"Processing data from {self.config['file_path']}")
            
            # Read the CSV file using csv reader
            with open(self.config["file_path"], 'r') as csvfile:
                reader = csv.reader(csvfile, delimiter=self.config["seperator"])
                
                # Calculate Python (0-based) indices from Excel (1-based) indices
                start_row_py = excel_to_zero_based_row(self.config["start_row"])
                end_row_py = excel_to_zero_based_row(self.config["end_row"])
                
                # Skip rows until we reach the start row
                for i in range(start_row_py):
                    next(reader, None)
                
                # Read all data rows
                data_rows = []
                current_py_row = start_row_py
                
                for row in reader:
                    if current_py_row > end_row_py:
                        break
                    
                    # Convert the current Python row index to Excel row for error reporting
                    current_excel_row = zero_based_to_excel_row(current_py_row)
                    
                    # Check for sensors added via add_sensor()
                    has_added_sensors = hasattr(self, 'added_raw_sensors') and self.added_raw_sensors
                    
                    # Only check CSV column count for original sensors (not added ones)
                    if not has_added_sensors:
                        # Standard column validation logic
                        max_col_letter = max([col for col in self.config["data"].values()])
                        max_col_idx = excel_column_to_index(max_col_letter)
                        
                        if len(row) <= max_col_idx:
                            raise ValueError(
                                f"Missing data in row {current_excel_row}. Expected columns up to "
                                f"'{max_col_letter}' but only found {len(row)} columns."
                            )
                    
                    # Convert all values to float with precise error reporting
                    float_row = []
                    for col_idx, val in enumerate(row):
                        if val.strip() == '':
                            col_letter = index_to_excel_column(col_idx)
                            cell_ref = get_cell_reference(current_excel_row, col_letter)
                            raise ValueError(f"Empty cell found at {cell_ref}")
                        
                        try:
                            float_row.append(float(val))
                        except ValueError:
                            col_letter = index_to_excel_column(col_idx)
                            cell_ref = get_cell_reference(current_excel_row, col_letter)
                            raise ValueError(f"Non-numeric data found at {cell_ref}: '{val}'")
                    
                    data_rows.append(float_row)
                    current_py_row += 1
            
            # Check if we have data rows
            if not data_rows:
                raise ValueError(
                    f"No valid data rows found in the CSV file between rows "
                    f"{self.config['start_row']} and {self.config['end_row']}"
                )
            
            # Extract time column
            time_col_idx = excel_column_to_index(self.config["time_column"])
            self.time_array = np.array([row[time_col_idx] for row in data_rows], dtype=float)
            
            # Apply unit conversion for time if needed
            time_from_unit = self.config['input_units']['time']
            time_to_unit = self.config['output_units']['time']
            
            if time_from_unit != time_to_unit:
                self.log_info(f"Converting time from {time_from_unit} to {time_to_unit}")
                conversion_factor = self.converter.convert(1.0, 'Time', time_from_unit, time_to_unit)
                self.time_array = self.time_array * conversion_factor
            
            # Collect all data arrays for potential time-based operations
            all_data_arrays = {}
            
            # Check if we have added sensors to include
            added_sensors = getattr(self, 'added_raw_sensors', {})
            
            for original_name, col_letter in self.config["data"].items():
                data_name = self.config["data_name"][original_name]
                
                # Check if this is an added sensor
                if original_name in added_sensors:
                    # Use the stored raw data instead of reading from CSV
                    data_array = added_sensors[original_name].copy()
                    self.log_info(f"Using stored raw data for added sensor '{original_name}'")
                else:
                    # Extract from CSV as usual
                    col_idx = excel_column_to_index(col_letter)
                    
                    # Make sure the index is valid
                    if col_idx >= len(data_rows[0]):
                        raise ValueError(
                            f"Invalid column index for '{original_name}': {col_letter} (index {col_idx}). "
                            f"CSV only has {len(data_rows[0])} columns."
                        )
                    
                    data_array = np.array([row[col_idx] for row in data_rows], dtype=float)
                
                # Apply unit conversion for data if needed
                data_from_unit = self.config['input_units']['data']
                data_to_unit = self.config['output_units']['data']
                data_type = self.config['data_type']
                
                if data_from_unit != data_to_unit:
                    self.log_info(f"Converting {data_name} from {data_from_unit} to {data_to_unit} ({data_type})")
                    conversion_factor = self.converter.convert(1.0, data_type, data_from_unit, data_to_unit)
                    data_array = data_array * conversion_factor
                
                all_data_arrays[data_name] = data_array
            
            # ===== APPLY CORRECTIONS IN THE AGREED ORDER =====
            
            # 1. TRIM_TIME - Select data range first
            if "data_correction" in self.config and "trim_time" in self.config["data_correction"]:
                trim_time_config = self.config["data_correction"]["trim_time"]
                if trim_time_config.get("process", False):
                    start_time = trim_time_config.get("start_time")
                    end_time = trim_time_config.get("end_time")
                    self.time_array, all_data_arrays = self._apply_trim_time_correction(
                        self.time_array, all_data_arrays, start_time, end_time
                    )

            # 2. RESAMPLE - Ensure uniform sampling (applied to all data at once)
            if "data_correction" in self.config and "resample" in self.config["data_correction"]:
                resample_config = self.config["data_correction"]["resample"]
                if resample_config.get("process", False) and resample_config.get("value") is not None:
                    target_fs = resample_config.get("value")
                    method = resample_config.get("method", "linear")
                    
                    # Apply resampling to time array and all data arrays at once
                    self.time_array, all_data_arrays = self._apply_resample_correction(
                        self.time_array, all_data_arrays, target_fs, method
                    )
                    
                    # Update dt in config to match resampling
                    self.config["dt"] = 1.0 / target_fs
            
            # 3. SHIFT_TIME - Apply time shift early
            if "data_correction" in self.config and "shift_time" in self.config["data_correction"]:
                shift_time_config = self.config["data_correction"]["shift_time"]
                if shift_time_config.get("process", False) and shift_time_config.get("value") is not None:
                    self.time_array = self._apply_shift_time_correction(
                        self.time_array, shift_time_config["value"]
                    )
            
            # Process each sensor's data with the agreed sequence of corrections
            for original_name, col_letter in self.config["data"].items():
                data_name = self.config["data_name"][original_name]
                
                # Use the potentially trimmed data
                data_array = all_data_arrays[data_name]
                
                # Apply data corrections if data_correction is in config
                if "data_correction" in self.config:
                    # 4. ZERO_START_Y - Baseline correction
                    zero_start_y_config = self.config["data_correction"].get("zero_start_y", {})
                    if zero_start_y_config.get("process", False):
                        n_values = zero_start_y_config.get("value")
                        data_array = self._apply_zero_start_y_correction(data_array, n_values)
                    
                    # 5. REVERSE_Y - Invert values
                    reverse_y_config = self.config["data_correction"].get("reverse_y", {})
                    if reverse_y_config.get("process", False):
                        data_array = self._apply_reverse_y_correction(data_array)
                    
                    # 6. DETREND - Remove linear or polynomial trend  
                    detrend_config = self.config["data_correction"].get("detrend", {})
                    if detrend_config.get("process", False):
                        detrend_type = detrend_config.get("type", "linear")
                        detrend_degree = detrend_config.get("degree", 2)
                        data_array = self._apply_detrend_correction(data_array, detrend_type, detrend_degree)

                    # 7. DERIVATIVE - Calculate on corrected data
                    derivative_config = self.config["data_correction"].get("derivative", {})
                    if derivative_config.get("process", False):
                        data_array = self._apply_derivative_correction(data_array)
                    
                    # 8. FILTER - Smooth data
                    filter_config = self.config["data_correction"].get("filter", {})
                    if filter_config.get("process", False):
                        data_array = self._apply_filter_correction(data_array, filter_config)
                    
                    # 9. STRETCH_Y - Scale values
                    stretch_y_config = self.config["data_correction"].get("stretch_y", {})
                    if stretch_y_config.get("process", False) and stretch_y_config.get("value") is not None:
                        data_array = self._apply_stretch_y_correction(data_array, stretch_y_config["value"])
                    
                    # 10. NORMALIZE - Normalize values
                    normalized_config = self.config["data_correction"].get("normilized", {})
                    if normalized_config.get("process", False):
                        data_array = self._apply_normalize_correction(data_array)
                
                # Store processed data back
                all_data_arrays[data_name] = data_array
            
            # 11. ZERO_START_TIME - Make time start at 0 (final step)
            if "data_correction" in self.config and "zero_start_time" in self.config["data_correction"]:
                zero_start_time_config = self.config["data_correction"]["zero_start_time"]
                if zero_start_time_config.get("process", False):
                    self.time_array = self._apply_zero_start_time_correction(self.time_array)
            
            # Store the final data in the processed_data dictionary
            for data_name, data_array in all_data_arrays.items():
                original_name = next((k for k, v in self.config["data_name"].items() if v == data_name), data_name)
                
                self.processed_data[data_name] = {
                    "y": data_array,
                    "original_name": original_name,
                    "first_value": data_array[0],  # Store first value AFTER all corrections
                    "last_value": data_array[-1]   # Store last value AFTER all corrections
                }
            
            # Log information about processed data
            self.log_info(f"Successfully processed {len(self.time_array)} data points for {len(self.processed_data)} sensors")
            self.log_info(f"Time range: {self.time_array[0]} to {self.time_array[-1]} seconds")
            
            return True
                
        except Exception as e:
            self.log_error(f"Error processing data: {e}")
            # Log debugging info
            self.log_error(f"File path: {self.config.get('file_path', 'Not set')}")
            self.log_error(f"Start row (Excel): {self.config.get('start_row', 'Not set')}")
            self.log_error(f"End row (Excel): {self.config.get('end_row', 'Not set')}")
            self.log_error(f"Time column: {self.config.get('time_column', 'Not set')}")
            self.log_error(f"dt: {self.config.get('dt', 'Not set')}")
            raise


    def get_xy(self, data_name):
        """Get x,y data for a given sensor name"""
        if data_name in self.processed_data:
            return self.time_array, self.processed_data[data_name]["y"]
        else:
            error_msg = f"Data name '{data_name}' not found in processed data. Available: {list(self.processed_data.keys())}"
            self.log_error(error_msg)
            raise ValueError(error_msg)
    
    def get_sensor_names(self):
        """Get list of available sensor names"""
        return list(self.processed_data.keys())
    
    def get_summary(self):
        """Get summary statistics for all sensors"""
        summary = {}
        for name, data in self.processed_data.items():
            summary[name] = {
                "original_name": data["original_name"],
                "first_value": data["first_value"],
                "last_value": data["last_value"],
                "min": float(min(data["y"])),
                "max": float(max(data["y"])),
            }
        return summary
    
    def export_to_csv(self, file_path, precision=14, export_config=True):
        """
        Export processed data to a new CSV file
        
        Args:
            file_path: Path to the output CSV file
            precision: Number of decimal places to use for numeric values
            export_config: Whether to export the configuration to a JSON file
        """
        if not self.processed_data or self.time_array is None:
            self.log_error("No processed data available to export")
            return False
        
        try:
            with open(file_path, 'w', newline='') as csvfile:
                writer = csv.writer(csvfile, delimiter=self.config["seperator"])
                
                # Write header row
                header = ["Time"]
                for sensor_name in self.processed_data.keys():
                    header.append(sensor_name)
                writer.writerow(header)
                
                # Write data rows
                format_str = f"{{:.{precision}f}}"
                for i in range(len(self.time_array)):
                    row = [format_str.format(self.time_array[i])]
                    for sensor_name in self.processed_data.keys():
                        row.append(format_str.format(self.processed_data[sensor_name]["y"][i]))
                    writer.writerow(row)
                    
            self.log_info(f"Exported processed data to {file_path}")
            
            # Export configuration if requested
            if export_config:
                config_file_path = os.path.splitext(file_path)[0] + '.json'
                
                # Create a copy of the current configuration
                updated_config = self.config.copy()
                
                # Update configuration for the exported file
                updated_config["file_path"] = file_path
                updated_config["start_row"] = 2
                updated_config["end_row"] = 1 + len(self.time_array)
                updated_config["time_column"] = "A"
                updated_config["input_units"] = updated_config["output_units"].copy()
                
                # Update dt if it changed due to resampling
                if len(self.time_array) > 1:
                    updated_config["dt"] = float(np.mean(np.diff(self.time_array)))
                
                # Update column references
                column_idx = 1  # Start from column B
                new_data = {}
                for orig_name in updated_config["data"].keys():
                    new_data[orig_name] = chr(ord('A') + column_idx)
                    column_idx += 1
                updated_config["data"] = new_data
                
                # Reset correction section
                updated_config["data_correction"] = {
                    "trim_time": {"process": False, "start_time": None, "end_time": None},
                    "resample": {"process": False, "value": None, "method": "linear"},
                    "shift_time": {"process": False, "value": None},
                    "zero_start_y": {"process": False, "value": None},
                    "reverse_y": {"process": False},
                    "detrend": {"process": False, "type": "linear", "degree": 2},
                    "derivative": {"process": False},
                    "filter": {"process": False, "type": "none", "params": {}},
                    "stretch_y": {"process": False, "value": None},
                    "normilized": {"process": False},
                    "zero_start_time": {"process": False}
                }
                
                # Export the updated config
                with open(config_file_path, 'w') as json_file:
                    json.dump(updated_config, json_file, indent=4)
                    
                self.log_info(f"Exported updated configuration to {config_file_path}")
                
            return True
        except Exception as e:
            self.log_error(f"Error exporting data to CSV: {e}")
            return False

    def export_selected_sensors_to_csv(self, file_path, sensor_names=None, precision=14, export_config=True):
        """
        Export selected sensors' processed data to a new CSV file
        
        Args:
            file_path: Path to the output CSV file
            sensor_names: List of sensor names to export, or None for all sensors
            precision: Number of decimal places to use for numeric values
            export_config: Whether to export the configuration to a JSON file
        """
        if not self.processed_data or self.time_array is None:
            self.log_error("No processed data available to export")
            return False
        
        # If no sensor names provided, use all available sensors
        if sensor_names is None:
            sensor_names = list(self.processed_data.keys())
        else:
            # Validate sensor names
            for name in sensor_names:
                if name not in self.processed_data:
                    self.log_error(f"Sensor name '{name}' not found in processed data")
                    return False
        
        try:
            with open(file_path, 'w', newline='') as csvfile:
                writer = csv.writer(csvfile, delimiter=self.config["seperator"])
                
                # Write header row
                header = ["Time"]
                for sensor_name in sensor_names:
                    header.append(sensor_name)
                writer.writerow(header)
                
                # Write data rows
                format_str = f"{{:.{precision}f}}"
                for i in range(len(self.time_array)):
                    row = [format_str.format(self.time_array[i])]
                    for sensor_name in sensor_names:
                        row.append(format_str.format(self.processed_data[sensor_name]["y"][i]))
                    writer.writerow(row)
                    
            self.log_info(f"Exported selected sensors' data to {file_path}")
            
            # Export configuration if requested
            if export_config:
                config_file_path = os.path.splitext(file_path)[0] + '.json'
                
                # Create a copy of the current configuration
                updated_config = self.config.copy()
                
                # Update configuration for the exported file
                updated_config["file_path"] = file_path
                updated_config["start_row"] = 2
                updated_config["end_row"] = 1 + len(self.time_array)
                updated_config["time_column"] = "A"
                updated_config["input_units"] = updated_config["output_units"].copy()
                
                # Update dt if it changed due to resampling
                if len(self.time_array) > 1:
                    updated_config["dt"] = float(np.mean(np.diff(self.time_array)))
                
                # Update data and data_name dictionaries for selected sensors
                new_data = {}
                new_data_name = {}
                column_idx = 1  # Start from column B
                
                # Find original names that map to selected sensor names
                for orig_name, mapped_name in self.config["data_name"].items():
                    if mapped_name in sensor_names:
                        new_data[orig_name] = chr(ord('A') + column_idx)
                        new_data_name[orig_name] = mapped_name
                        column_idx += 1
                        
                updated_config["data"] = new_data
                updated_config["data_name"] = new_data_name
                
                # Reset correction section
                updated_config["data_correction"] = {
                    "trim_time": {"process": False, "start_time": None, "end_time": None},
                    "resample": {"process": False, "value": None, "method": "linear"},
                    "shift_time": {"process": False, "value": None},
                    "zero_start_y": {"process": False, "value": None},
                    "reverse_y": {"process": False},
                    "detrend": {"process": False, "type": "linear", "degree": 2},
                    "derivative": {"process": False},
                    "filter": {"process": False, "type": "none", "params": {}},
                    "stretch_y": {"process": False, "value": None},
                    "normilized": {"process": False},
                    "zero_start_time": {"process": False}
                }
                
                # Export the updated config
                with open(config_file_path, 'w') as json_file:
                    json.dump(updated_config, json_file, indent=4)
                    
                self.log_info(f"Exported updated configuration to {config_file_path}")
                
            return True
        except Exception as e:
            self.log_error(f"Error exporting selected sensors' data to CSV: {e}")
            return False

    def export_processed_data_in_original_format(self, output_file_path=None, precision=14, export_config=True):
        """
        Export data in the original CSV file format with processed data and save to output_file_path.
        If output_file_path is None, creates a new file with '_updated' suffix.
        
        Args:
            output_file_path: Path to the output CSV file, or None to generate a path
            precision: Number of decimal places to use for numeric values
            export_config: Whether to export the configuration to a JSON file
        """
        if not self.processed_data or self.time_array is None:
            self.log_error("No processed data available to export")
            return False
        
        # If no output file specified, create one based on original file name
        if output_file_path is None:
            original_path = self.config["file_path"]
            file_name, file_ext = os.path.splitext(original_path)
            output_file_path = f"{file_name}_updated{file_ext}"
        
        try:
            # Read the entire original file
            with open(self.config["file_path"], 'r', newline='') as infile:
                reader = csv.reader(infile, delimiter=self.config["seperator"])
                all_rows = list(reader)
            
            # Calculate row indices
            start_row = self.config["start_row"] - 1  # Convert to 0-based
            end_row = min(self.config["end_row"] - 1, len(all_rows) - 1)  # Convert to 0-based
            
            # Get column indices
            time_col_idx = excel_column_to_index(self.config["time_column"])
            data_col_indices = {}
            for original_name, col_letter in self.config["data"].items():
                data_name = self.config["data_name"][original_name]
                data_col_indices[data_name] = excel_column_to_index(col_letter)
            
            # Format string for numeric values
            format_str = f"{{:.{precision}f}}"
            
            # Replace time values
            for i, time_val in enumerate(self.time_array):
                if start_row + i <= end_row and start_row + i < len(all_rows):
                    row_idx = start_row + i
                    # Ensure the row has enough columns
                    while len(all_rows[row_idx]) <= time_col_idx:
                        all_rows[row_idx].append("")
                    all_rows[row_idx][time_col_idx] = format_str.format(time_val)
            
            # Replace data values
            for sensor_name, data_info in self.processed_data.items():
                if sensor_name in data_col_indices:
                    col_idx = data_col_indices[sensor_name]
                    for i, data_val in enumerate(data_info["y"]):
                        if start_row + i <= end_row and start_row + i < len(all_rows):
                            row_idx = start_row + i
                            # Ensure the row has enough columns
                            while len(all_rows[row_idx]) <= col_idx:
                                all_rows[row_idx].append("")
                            all_rows[row_idx][col_idx] = format_str.format(data_val)
            
            # Truncate rows after the processed data
            last_data_row = start_row + len(self.time_array) - 1
            if last_data_row < len(all_rows) - 1:
                # Keep header rows and exactly enough data rows for our processed data
                all_rows = all_rows[:start_row + len(self.time_array)]
                self.log_info(f"Truncated rows beyond processed data (kept {len(all_rows)} rows)")

            # Write the updated data to the output file
            with open(output_file_path, 'w', newline='') as outfile:
                writer = csv.writer(outfile, delimiter=self.config["seperator"])
                writer.writerows(all_rows)
            
            self.log_info(f"Replaced data in original file and saved to {output_file_path}")
            
            # Export configuration if requested
            if export_config:
                config_file_path = os.path.splitext(output_file_path)[0] + '.json'
                
                # Create a copy of the current configuration
                updated_config = self.config.copy()
                
                # Update file path in the config
                updated_config["file_path"] = output_file_path
                
                # Update input units to match output units
                updated_config["input_units"] = updated_config["output_units"].copy()
                
                # Update dt if it changed due to resampling
                if len(self.time_array) > 1 and np.std(np.diff(self.time_array)) > 1e-10:
                    updated_config["dt"] = float(np.mean(np.diff(self.time_array)))
                
                # Reset correction section
                updated_config["data_correction"] = {
                    "trim_time": {"process": False, "start_time": None, "end_time": None},
                    "resample": {"process": False, "value": None, "method": "linear"},
                    "shift_time": {"process": False, "value": None},
                    "zero_start_y": {"process": False, "value": None},
                    "reverse_y": {"process": False},
                    "detrend": {"process": False, "type": "linear", "degree": 2},
                    "derivative": {"process": False},
                    "filter": {"process": False, "type": "none", "params": {}},
                    "stretch_y": {"process": False, "value": None},
                    "normilized": {"process": False},
                    "zero_start_time": {"process": False}
                }
                
                # Export the updated config
                with open(config_file_path, 'w') as json_file:
                    json.dump(updated_config, json_file, indent=4)
                    
                self.log_info(f"Exported updated configuration to {config_file_path}")
            
            return True
        except Exception as e:
            self.log_error(f"Error replacing data in original file: {e}")
            return False

    def add_sensor(self, name, data, column=None, no_override=True):
        """
        Add a new sensor to the processed data (ONLY when data_correction is empty)
        
        Args:
            name: Name for the new sensor
            data: NumPy array or list containing the raw sensor data
            column: Optional Excel column letter (for configuration tracking)
            no_override: If True, prevents overriding existing sensors with the same name
                
        Returns:
            True if successful, False otherwise
        """
        # Check if time data is available
        if self.time_array is None:
            self.log_error("Cannot add sensor: no time array available. Process data first.")
            return False
        
        # CRITICAL: Check that data_correction is empty - only allow adding when no corrections are active
        if "data_correction" in self.config and any(
            corr.get("process", False) for corr in self.config["data_correction"].values()
        ):
            self.log_error(
                "Cannot add sensor: data_correction is not empty. "
                "New sensors can ONLY be added when no data corrections are active."
            )
            return False
        
        # Check if sensor with this name already exists
        if name in self.processed_data and no_override:
            self.log_error(f"Cannot add sensor: '{name}' already exists and no_override=True")
            return False
        
        try:
            # Convert data to numpy array if it's not already
            data_array = np.array(data, dtype=float)
            
            # Verify data length matches time array
            if len(data_array) != len(self.time_array):
                self.log_error(f"Data length ({len(data_array)}) doesn't match time array length ({len(self.time_array)})")
                return False
            
            # Generate a column letter if not provided
            if column is None:
                used_columns = set(self.config["data"].values())
                column = 'A'
                while column in used_columns:
                    column = chr(ord(column) + 1)
                    if ord(column) > ord('Z'):
                        column = 'AA'
                        break
            
            # Create raw data storage if it doesn't exist
            if not hasattr(self, 'added_raw_sensors'):
                self.added_raw_sensors = {}
            
            # Store the raw data for future processing
            self.added_raw_sensors[name] = data_array.copy()
            
            # Add to processed data (use name as original_name too)
            self.processed_data[name] = {
                "y": data_array,
                "original_name": name,
                "first_value": float(data_array[0]),
                "last_value": float(data_array[-1])
            }
            
            # Update configuration
            self.config["data"][name] = column
            self.config["data_name"][name] = name
            
            self.log_info(f"Added new sensor '{name}' with {len(data_array)} data points")
            self.log_info("After adding sensors, use update_config() to apply corrections to all sensors uniformly")
            return True
                
        except Exception as e:
            self.log_error(f"Error adding sensor: {e}")
            return False


    def calculate_integrals(self, sensor_name, n=1, initial=0.0):
        """
        Calculate the 1st … n-th cumulative integrals of data_name.

        Parameters
        ----------
        data_name : str
            Name returned by get_sensor_names() / get_xy().
        n : int, default 1
            Highest integral order to compute.
        initial : float, default 0.0
            Initial value for every integration.

        Returns
        -------
        (time_array, data_array_for_integration, [int_1, int_2, …, int_n])
            time_array is the same length as the integrals.
        """
        # get x, y – will raise ValueError if sensor_name is missing
        x, y = self.get_xy(sensor_name)

        integrals = calculate_integrals(x, y, n=n, initial=initial)
        return x, y, integrals
    
    def visualize_integrals(self, sensor_name, n=1, initial=0.0):
        """
        Visualize the original sensor data and its cumulative integrals.
        
        Parameters
        ----------
        sensor_name : str
            Name of the sensor to visualize.
        n : int, default 1
            Highest integral order to compute.
        initial : float, default 0.0
            Initial value for every integration.
            
        Returns
        -------
        matplotlib.figure.Figure
            Figure object containing the plots. Use .show() to display.
        """
        
        # Get data
        x, y, integrals = self.calculate_integrals(sensor_name, n=n, initial=initial)
        
        # Create figure with n+1 subplots (original + n integrals)
        fig, axs = plt.subplots(n+1, 1, figsize=(12, 3*(n+1)), sharex=True)
        
        # Handle case where n=1 (axs is not an array)
        if n == 1:
            axs = [axs]
        
        # Plot original function
        axs[0].plot(x, y, label=f"{sensor_name}", linewidth=2, color='blue')
        axs[0].set_ylabel(sensor_name)
        axs[0].legend()
        axs[0].grid(True, alpha=0.3)
        
        # Plot integrals
        for i, integral in enumerate(integrals, 1):
            # Create label with proper integral notation
            if i == 1:
                label = f"∫ {sensor_name} dx"
            elif i == 2:
                label = f"∫∫ {sensor_name} dx²"
            elif i == 3:
                label = f"∫∫∫ {sensor_name} dx³"
            else:
                # Use superscript for the integral order
                label = f"∫⁽{i}⁾ {sensor_name}"
            
            # Create ylabel (simplified for display)
            if i == 1:
                ylabel = f"∫ {sensor_name} dx"
            elif i == 2:
                ylabel = f"∫∫ {sensor_name} dx²"
            elif i == 3:
                ylabel = f"∫∫∫ {sensor_name} dx³"
            else:
                ylabel = f"∫⁽{i}⁾ {sensor_name}"
            
            # Plot
            axs[i].plot(x, integral, label=label, linewidth=2, color=f'C{i}')
            axs[i].set_ylabel(ylabel)
            axs[i].legend()
            axs[i].grid(True, alpha=0.3)
        
        # Set x-label only on bottom plot
        axs[-1].set_xlabel("Time")
        
        # Set figure title
        fig.suptitle(f'{sensor_name} and Its Integrals', fontsize=16)
        fig.tight_layout()

        return fig

    def visualize_sensor(self, sensor_name,
                        labels=None,                  # Labels for legend
                        title=None,                   # Plot title
                        xlabel=None,                  # X-axis label
                        ylabel=None,                  # Y-axis label
                        figsize=(10, 6),              # Figure size (width, height) in inches
                        plot_type='line',             # 'line', 'scatter', 'bar', 'hist'
                        colors=None,                  # Colors for lines/markers
                        grid=True,                    # Show grid
                        legend=True,                  # Show legend
                        save_path=None,               # Path to save figure
                        style=None,                   # Matplotlib style to use
                        xlim=None,                    # X-axis limits [min, max]
                        ylim=None,                    # Y-axis limits [min, max]
                        **kwargs                      # Additional kwargs passed to plot function
        ):
        """
        Visualize a sensor's data using matplotlib.
        
        Parameters:
        -----------
        sensor_name : str
            Name of the sensor to visualize (must exist in processed_data).
        
        labels : str or list of str, optional
            Labels for legend.
        
        title : str, optional
            Plot title. If None, uses the sensor name.
        
        xlabel : str, optional
            X-axis label. Default is "Time".
        
        ylabel : str, optional
            Y-axis label. Default is sensor name.
        
        figsize : tuple, optional
            Figure size (width, height) in inches.
        
        plot_type : str, optional
            Type of plot: 'line', 'scatter', 'bar', 'hist'
        
        colors : str or list of str, optional
            Colors for each series.
        
        grid : bool, optional
            Whether to show grid.
        
        legend : bool, optional
            Whether to show legend.
        
        save_path : str, optional
            Path to save figure. If provided, saves the figure.
        
        style : str, optional
            Matplotlib style to use (e.g., 'ggplot', 'seaborn').
        
        xlim : tuple, optional
            X-axis limits [min, max].
        
        ylim : tuple, optional
            Y-axis limits [min, max].
        
        **kwargs : 
            Additional keyword arguments passed to the plotting function.
        
        Returns:
        --------
        fig : matplotlib.figure.Figure
            Figure object.
        """
        
        # Get data for the sensor
        try:
            x, y = self.get_xy(sensor_name)
        except ValueError as e:
            self.log_error(f"Error visualizing sensor '{sensor_name}': {e}")
            return None, None
        
        # Apply style if specified
        if style:
            plt.style.use(style)
        
        # Create figure and axes
        fig, ax = plt.subplots(figsize=figsize)
        
        # Handle labels
        if labels is None:
            label = sensor_name
        elif isinstance(labels, list):
            label = labels[0] if labels else sensor_name
        else:
            label = labels
        
        # Handle colors
        color = colors if colors else None
        
        plot_kwargs = kwargs.copy()
        if color:
            plot_kwargs['color'] = color
        
        # Create plot based on plot_type
        if plot_type == 'line':
            ax.plot(x, y, label=label, **plot_kwargs)
        
        elif plot_type == 'scatter':
            ax.scatter(x, y, label=label, **plot_kwargs)
        
        else:
            raise ValueError(f"Unknown plot_type: {plot_type}")
        
        # Set title and labels with defaults
        ax.set_title(title if title else f"{sensor_name} Data")
        ax.set_xlabel(xlabel if xlabel else "Time")
        ax.set_ylabel(ylabel if ylabel else sensor_name)
        
        # Set axis limits if provided
        if xlim:
            ax.set_xlim(xlim)
        if ylim:
            ax.set_ylim(ylim)
        
        # Add grid if requested
        if grid:
            ax.grid(True, linestyle='--', alpha=0.7)
        
        # Add legend if requested
        if legend:
            ax.legend()
        
        # Make layout tight
        fig.tight_layout()
        
        # Save figure if path provided
        if save_path:
            fig.savefig(save_path, bbox_inches='tight')

        # Return figure for further customization
        return fig

    def quick_visualize_sensor(self, sensor_name, **kwargs):
        """
        Ultra-simple plot function for sensor data. Returns fig, ax objects.
        
        Parameters:
        -----------
        sensor_name : str
            Name of the sensor to visualize.
        
        **kwargs : 
            Additional arguments passed to visualize_sensor.
        
        Returns:
        --------
        fig: matplotlib figure object
        """
        return self.visualize_sensor(sensor_name=sensor_name, **kwargs)

### FILTER COMPARISON METHODS

    # FILTER COMPARE PROCESS
    def compare_filters(self, sensor_name, filter_configs, reference_data=None, num_dominant_peaks=5):
        """
        Compare multiple filter configurations on a single sensor and return detailed metrics.
        
        Args:
            sensor_name: Name of the sensor to analyze
            filter_configs: List of dictionaries with filter configurations
            reference_data: Optional reference data to compare against (if None, uses unfiltered data)
            num_dominant_peaks: Number of dominant frequency peaks to identify
            
        Returns:
            Dictionary with comprehensive comparison metrics
        """
        # Get original/reference data
        time_array, orig_data = self.get_xy(sensor_name)
        reference_data = reference_data if reference_data is not None else orig_data
        
        # Calculate sampling frequency
        fs = 1.0 / (time_array[1] - time_array[0])
        
        # Compute FFT of reference data
        ref_freqs, ref_magnitudes = self._compute_fft(reference_data, fs)
        
        # Identify dominant frequencies in reference data
        ref_dominant_peaks = self._identify_dominant_frequencies(
            ref_freqs, ref_magnitudes, num_peaks=num_dominant_peaks
        )
        
        # Store original config to restore later
        original_config = self.export_config_to_dict()
        
        # Process each filter configuration
        results = {}
        results["__reference_fft"] = {
            "frequencies": ref_freqs,
            "magnitudes": ref_magnitudes,
            "dominant_peaks": ref_dominant_peaks
        }
        
        for filter_config in filter_configs:
            filter_name = filter_config.get("name", "Unknown Filter")
            
            # Process this filter
            filtered_data = self._apply_filter_config(original_config, filter_config, sensor_name)
            if filtered_data is None:
                self.log_error(f"Failed to process data for {filter_name}")
                continue
                
            # Calculate metrics
            results[filter_name] = self._calculate_filter_metrics(
                reference_data, filtered_data, fs, num_dominant_peaks, ref_dominant_peaks
            )
            
            # Store the filtered data
            results[filter_name]["filtered_data"] = filtered_data
            
        return results

    def _apply_filter_config(self, original_config, filter_config, sensor_name):
        """Apply a filter configuration and return the filtered data"""
        # Create a new filter configuration
        new_config = {
            "data_correction": {
                "filter": {
                    "process": True,
                    **filter_config["filter"]
                }
            }
        }
        
        # Apply this filter using a temporary SensorData instance
        temp_sensor = type(self)()
        temp_sensor.load_config_from_dict(original_config)
        temp_sensor.update_config(new_config)
        
        # Process with this filter
        if not temp_sensor.process_data():
            return None
        
        # Get filtered data
        _, filtered_data = temp_sensor.get_xy(sensor_name)
        return filtered_data

    def _calculate_filter_metrics(self, reference_data, filtered_data, fs, num_dominant_peaks, ref_dominant_peaks):
        """Calculate comprehensive metrics for a filtered dataset"""
        # Calculate time domain metrics
        time_metrics = {
            "mse": np.mean((reference_data - filtered_data)**2),
            "rmse": np.sqrt(np.mean((reference_data - filtered_data)**2)),
            "mae": np.mean(np.abs(reference_data - filtered_data)),
            "max_abs_error": np.max(np.abs(reference_data - filtered_data)),
            "correlation": np.corrcoef(reference_data, filtered_data)[0, 1],
            "energy_ratio": np.sum(filtered_data**2) / np.sum(reference_data**2),
            "snr_db": 10 * np.log10(np.sum(reference_data**2) / np.sum((reference_data - filtered_data)**2)) 
                    if np.sum((reference_data - filtered_data)**2) > 0 else float('inf')
        }
        
        # Calculate frequency domain metrics using Welch's method
        f_ref, psd_ref = signal.welch(reference_data, fs, nperseg=min(512, len(reference_data)//10))
        f_filt, psd_filt = signal.welch(filtered_data, fs, nperseg=min(512, len(filtered_data)//10))
        
        # Define frequency bands for analysis
        bands = {
            "low": (0, 20),
            "mid": (20, 100),
            "high": (100, fs/2)
        }
        
        # Calculate power ratios for each frequency band
        freq_metrics = {}
        for band_name, (flow, fhigh) in bands.items():
            ref_band_indices = (f_ref >= flow) & (f_ref <= fhigh)
            ref_band_power = np.sum(psd_ref[ref_band_indices])
            
            filt_band_indices = (f_filt >= flow) & (f_filt <= fhigh)
            filt_band_power = np.sum(psd_filt[filt_band_indices])
            
            freq_metrics[f"{band_name}_band_ratio"] = filt_band_power / ref_band_power if ref_band_power > 0 else float('inf')
        
        # Compute FFT of filtered data
        filt_freqs, filt_magnitudes = self._compute_fft(filtered_data, fs)
        
        # Identify dominant frequencies in filtered data
        filt_dominant_peaks = self._identify_dominant_frequencies(
            filt_freqs, filt_magnitudes, num_peaks=num_dominant_peaks
        )
        
        # Compute peak preservation metrics
        peak_metrics = self._compute_peak_preservation_metrics(
            ref_dominant_peaks, filt_dominant_peaks
        )
        
        # Return combined results
        return {
            "time_metrics": time_metrics,
            "frequency_metrics": freq_metrics,
            "fft": {
                "frequencies": filt_freqs,
                "magnitudes": filt_magnitudes,
                "dominant_peaks": filt_dominant_peaks
            },
            "peak_preservation": peak_metrics
        }

    def rank_filters(self, comparison_results, ranking_criteria=None):
        """
        Rank filters based on specified criteria.
        
        Args:
            comparison_results: Output from compare_filters method
            ranking_criteria: Dictionary mapping metric names to weight and goal ('min' or 'max')
                Example: {'rmse': {'weight': 2, 'goal': 'min'}, 'correlation': {'weight': 1, 'goal': 'max'}}
                
        Returns:
            Tuple of (ranked_filter_names, scores_dict)
        """
        # Default ranking criteria if none provided
        if ranking_criteria is None:
            ranking_criteria = {
                'rmse': {'weight': 1, 'goal': 'min'},
                'snr_db': {'weight': 1, 'goal': 'max'},
                'correlation': {'weight': 1, 'goal': 'max'}
            }
        
        # Only process actual filter results (skip reference data entries that start with __)
        filter_entries = {k: v for k, v in comparison_results.items() if not k.startswith('__')}
        
        # Gather all metric values for normalization
        metric_values = {metric: [] for metric in ranking_criteria}
        
        for _, results in filter_entries.items():
            for metric in ranking_criteria:
                value = None
                
                # Locate the metric in the appropriate results section
                if metric in results.get("time_metrics", {}):
                    value = results["time_metrics"][metric]
                elif metric in results.get("frequency_metrics", {}):
                    value = results["frequency_metrics"][metric]
                elif metric == 'preservation_score' and 'peak_preservation' in results:
                    value = results["peak_preservation"]["overall_preservation_score"]
                
                if value is not None:
                    metric_values[metric].append(value)
        
        # Calculate normalized scores for each filter
        scores = {}
        for filter_name, results in filter_entries.items():
            scores[filter_name] = 0
            
            for metric, criteria in ranking_criteria.items():
                weight = criteria['weight']
                goal = criteria['goal']
                
                # Get metric value from the appropriate section
                value = None
                if metric in results.get("time_metrics", {}):
                    value = results["time_metrics"][metric]
                elif metric in results.get("frequency_metrics", {}):
                    value = results["frequency_metrics"][metric]
                elif metric == 'preservation_score' and 'peak_preservation' in results:
                    value = results["peak_preservation"]["overall_preservation_score"]
                
                if value is None:
                    continue
                
                # Normalize based on min/max across all filters
                min_val = min(metric_values[metric])
                max_val = max(metric_values[metric])
                
                if max_val == min_val:
                    normalized_score = 1.0
                elif goal == 'min':
                    normalized_score = 1 - (value - min_val) / (max_val - min_val)
                else:  # goal == 'max'
                    normalized_score = (value - min_val) / (max_val - min_val)
                
                # Add weighted score
                scores[filter_name] += weight * normalized_score
        
        # Sort filters by score
        ranked_filters = sorted(scores.keys(), key=lambda x: scores[x], reverse=True)
        
        return ranked_filters, scores

    def _compute_fft(self, data_array, fs):
        """Compute FFT and return frequencies and magnitude spectrum"""
        n = len(data_array)
        
        # Apply Hanning window to reduce spectral leakage
        window = np.hanning(n)
        windowed_data = data_array * window
        
        # Compute FFT and magnitude spectrum
        fft_result = np.fft.rfft(windowed_data)
        magnitude = np.abs(fft_result) * 2.0 / np.sum(window)
        frequencies = np.fft.rfftfreq(n, 1/fs)
        
        return frequencies, magnitude

    def _identify_dominant_frequencies(self, frequencies, magnitude, num_peaks=5, height_threshold=0.1, distance=1):
        """Find the N most dominant frequency peaks"""
        # Set minimum height threshold and find peaks
        height = np.max(magnitude) * height_threshold
        
        peak_indices, _ = signal.find_peaks(
            magnitude, 
            height=height,
            distance=distance
        )
        
        # Sort peaks by magnitude and get top N
        sorted_indices = np.argsort(-magnitude[peak_indices])
        sorted_peak_indices = peak_indices[sorted_indices]
        top_peak_indices = sorted_peak_indices[:min(num_peaks, len(sorted_peak_indices))]
        
        # Return peak information sorted by frequency
        result = [(frequencies[i], magnitude[i], i) for i in top_peak_indices]
        result.sort(key=lambda x: x[0])
        
        return result

    def _compute_peak_preservation_metrics(self, original_peaks, filtered_peaks, freq_tolerance=0.5):
        """Compute metrics for how well filter preserves dominant peaks"""
        # Initialize metrics dictionary
        metrics = {
            "preserved_peak_count": 0,
            "peak_magnitude_ratios": [],
            "peak_frequency_shifts": [],
            "overall_preservation_score": 0.0,
            "matched_peaks": []
        }
        
        # Nothing to compare if either peak list is empty
        if not original_peaks or not filtered_peaks:
            return metrics
        
        # Match peaks between original and filtered signals
        matched_peaks = []
        
        for orig_freq, orig_mag, orig_idx in original_peaks:
            # Find closest peak in filtered signal within tolerance
            best_match = None
            min_freq_diff = float('inf')
            
            for filt_freq, filt_mag, filt_idx in filtered_peaks:
                freq_diff = abs(orig_freq - filt_freq)
                if freq_diff < min_freq_diff and freq_diff <= freq_tolerance:
                    min_freq_diff = freq_diff
                    best_match = (filt_freq, filt_mag, filt_idx)
            
            # If a match was found within tolerance
            if best_match is not None:
                filt_freq, filt_mag, filt_idx = best_match
                
                # Calculate metrics for this peak
                freq_shift = filt_freq - orig_freq
                mag_ratio = filt_mag / orig_mag if orig_mag > 0 else float('inf')
                
                matched_peaks.append((
                    (orig_freq, orig_mag, orig_idx),
                    (filt_freq, filt_mag, filt_idx),
                    freq_shift,
                    mag_ratio
                ))
        
        # Store metrics
        metrics["preserved_peak_count"] = len(matched_peaks)
        metrics["peak_magnitude_ratios"] = [match[3] for match in matched_peaks]
        metrics["peak_frequency_shifts"] = [match[2] for match in matched_peaks]
        metrics["matched_peaks"] = matched_peaks
        
        # Calculate overall preservation score (1.0 = perfect preservation)
        if original_peaks:
            # Ratio of matched peaks to original peaks
            peak_count_ratio = len(matched_peaks) / len(original_peaks)
            
            # Calculate average magnitude ratio and frequency shift metrics
            if matched_peaks:
                # Cap magnitude ratios between 0.5 and 2.0 for scoring
                mag_ratios = [min(max(ratio, 0.5), 2.0) for ratio in metrics["peak_magnitude_ratios"]]
                avg_mag_ratio = np.mean([2.0 - abs(1.0 - ratio) for ratio in mag_ratios])
                
                # Calculate frequency shift score if we have frequency values
                nyquist = original_peaks[-1][0] * 2 if original_peaks[0][0] > 0 else 1.0
                avg_freq_shift = 1.0 - np.mean([min(abs(shift) / nyquist, 1.0) for shift in metrics["peak_frequency_shifts"]])
            else:
                avg_mag_ratio = 0.0
                avg_freq_shift = 0.0
            
            # Combined score (peak count 40%, magnitude preservation 40%, frequency stability 20%)
            metrics["overall_preservation_score"] = 0.4 * peak_count_ratio + 0.4 * avg_mag_ratio + 0.2 * avg_freq_shift
        
        return metrics

    # FILTER COMPARE VISUALIZATION PART
    def visualize_filter_comparison(self, sensor_name, comparison_results, output_dir=None, plot_types=None):
        """
        Generate visual comparisons of multiple filters.
        
        Args:
            sensor_name: Name of the sensor being analyzed
            comparison_results: Output from compare_filters method
            output_dir: Directory to save plots (if None, only returns figure objects)
            plot_types: List of plot types to generate (options: 'time', 'frequency', 'fft', 'peaks', 'metrics')
                        If None, generates all plot types
                        
        Returns:
            Dictionary with generated figure objects
        """
        
        # Default to all plot types if none specified
        if plot_types is None:
            plot_types = ['time', 'frequency', 'fft', 'peaks', 'metrics']
        
        # Get original data and time array
        time_array, original_data = self.get_xy(sensor_name)
        fs = 1.0 / (time_array[1] - time_array[0])
        
        # Create output directory if needed
        if output_dir is not None and not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        # Get filter names and prepare color map
        filter_names = [name for name in comparison_results.keys() if not name.startswith('__')]
        colors = plt.cm.tab10(np.linspace(0, 1, len(filter_names)))
        
        # Get reference FFT data
        ref_fft = comparison_results.get('__reference_fft', None)
        
        # Dictionary to store generated figures
        figures = {}
        
        # Generate requested plot types
        for plot_type in plot_types:
            if plot_type == 'time':
                figures['time'] = self._create_time_domain_plot(
                    time_array, original_data, comparison_results, filter_names, colors, sensor_name
                )
            elif plot_type == 'frequency':
                figures['frequency'] = self._create_frequency_domain_plot(
                    original_data, comparison_results, filter_names, colors, fs, sensor_name
                )
            elif plot_type == 'fft':
                figures['fft'] = self._create_fft_plot(
                    comparison_results, filter_names, colors, fs, sensor_name
                )
            elif plot_type == 'peaks':
                figures['peaks'] = self._create_peak_preservation_plot(
                    comparison_results, filter_names, colors, sensor_name
                )
            elif plot_type == 'metrics':
                figures['metrics'] = self._create_metrics_plot(
                    comparison_results, filter_names, colors, sensor_name
                )
        
        # Save figures if output directory provided
        if output_dir:
            for plot_type, fig in figures.items():
                fig.savefig(os.path.join(output_dir, f"{sensor_name}_{plot_type}_comparison.png"), dpi=300)
                
                # Also generate detailed plots for each filter if doing comprehensive analysis
                if plot_type == 'time':
                    for i, filter_name in enumerate(filter_names):
                        detail_fig = self._create_filter_detail_plot(
                            time_array, original_data, comparison_results[filter_name], 
                            filter_name, colors[i], fs, sensor_name
                        )
                        safe_name = filter_name.replace(' ', '_').lower()
                        detail_fig.savefig(os.path.join(output_dir, f"{sensor_name}_{safe_name}_detail.png"), dpi=300)
                        plt.close(detail_fig)
        
        return figures

    def _create_time_domain_plot(self, time_array, original_data, comparison_results, filter_names, colors, sensor_name):
        """Create time domain comparison plot"""
        import matplotlib.pyplot as plt
        
        fig = plt.figure(figsize=(12, 8))
        plt.plot(time_array, original_data, 'k-', linewidth=2, label='Original')
        
        for i, filter_name in enumerate(filter_names):
            plt.plot(time_array, comparison_results[filter_name]['filtered_data'], 
                    color=colors[i], linewidth=1.5, alpha=0.8, label=filter_name)
        
        plt.title(f"{sensor_name} - Time Domain Comparison", fontsize=14)
        plt.xlabel("Time (s)", fontsize=12)
        plt.ylabel("Amplitude", fontsize=12)
        plt.grid(True, alpha=0.3)
        plt.legend(loc='best', fontsize=10)
        
        return fig

    def _create_frequency_domain_plot(self, original_data, comparison_results, filter_names, colors, fs, sensor_name):
        """Create frequency domain comparison plot using Welch PSD"""
        import matplotlib.pyplot as plt
        from scipy import signal
        
        fig = plt.figure(figsize=(12, 8))
        
        f_orig, psd_orig = signal.welch(original_data, fs, nperseg=min(512, len(original_data)//10))
        plt.semilogy(f_orig, psd_orig, 'k-', linewidth=2, label='Original')
        
        for i, filter_name in enumerate(filter_names):
            f, psd = signal.welch(
                comparison_results[filter_name]['filtered_data'], 
                fs, 
                nperseg=min(512, len(comparison_results[filter_name]['filtered_data'])//10)
            )
            plt.semilogy(f, psd, color=colors[i], linewidth=1.5, alpha=0.8, label=filter_name)
        
        plt.title(f"{sensor_name} - Frequency Domain Comparison (Welch PSD)", fontsize=14)
        plt.xlabel("Frequency (Hz)", fontsize=12)
        plt.ylabel("Power Spectral Density", fontsize=12)
        plt.grid(True, alpha=0.3)
        plt.xlim([0, min(fs/2, 200)])
        plt.legend(loc='best', fontsize=10)
        
        return fig

    def _create_fft_plot(self, comparison_results, filter_names, colors, fs, sensor_name):
        """Create FFT magnitude spectrum comparison plot"""
        import matplotlib.pyplot as plt
        import numpy as np
        
        fig = plt.figure(figsize=(14, 8))
        
        # Get maximum magnitude for scaling
        max_magnitude = 0
        ref_fft = comparison_results.get('__reference_fft', None)
        
        if ref_fft:
            max_magnitude = max(max_magnitude, np.max(ref_fft['magnitudes']))
            
            # Plot reference FFT
            plt.plot(ref_fft['frequencies'], ref_fft['magnitudes'], 
                    'k-', linewidth=2, alpha=0.7, label='Original')
            
            # Mark dominant peaks in reference data
            for freq, mag, _ in ref_fft['dominant_peaks']:
                plt.plot(freq, mag, 'ko', markersize=8)
                plt.annotate(f"{freq:.1f} Hz", 
                            xy=(freq, mag), 
                            xytext=(0, 10),
                            textcoords='offset points',
                            ha='center',
                            fontsize=8)
        
        # Plot filtered FFTs
        for i, filter_name in enumerate(filter_names):
            results = comparison_results[filter_name]
            if 'fft' not in results:
                continue
                
            plt.plot(results['fft']['frequencies'], results['fft']['magnitudes'], 
                    color=colors[i], linewidth=1.5, alpha=0.8, label=filter_name)
            
            max_magnitude = max(max_magnitude, np.max(results['fft']['magnitudes']))
            
            # Mark dominant peaks in filtered data
            for freq, mag, _ in results['fft']['dominant_peaks']:
                plt.plot(freq, mag, 'o', color=colors[i], markersize=6)
        
        plt.title(f"{sensor_name} - FFT Magnitude Spectrum Comparison", fontsize=14)
        plt.xlabel("Frequency (Hz)", fontsize=12)
        plt.ylabel("Magnitude", fontsize=12)
        plt.grid(True, alpha=0.3)
        plt.xlim([0, min(fs/2, 200)])
        plt.ylim([0, max_magnitude * 1.1])
        plt.legend(loc='best', fontsize=10)
        
        return fig

    def _create_peak_preservation_plot(self, comparison_results, filter_names, colors, sensor_name):
        """Create peak preservation comparison plot"""
        import matplotlib.pyplot as plt
        from matplotlib.gridspec import GridSpec
        import numpy as np
        
        fig = plt.figure(figsize=(14, 10))
        gs = GridSpec(2, 2, figure=fig)
        
        # Get reference peak count
        ref_peak_count = 0
        ref_fft = comparison_results.get('__reference_fft', None)
        if ref_fft:
            ref_peak_count = len(ref_fft['dominant_peaks'])
        
        # Collect data for plots
        peak_counts = []
        preservation_scores = []
        frequency_shifts = []
        magnitude_ratios = []
        
        for filter_name in filter_names:
            results = comparison_results[filter_name]
            if 'peak_preservation' not in results:
                continue
            
            pp = results['peak_preservation']
            peak_counts.append(pp['preserved_peak_count'])
            preservation_scores.append(pp['overall_preservation_score'])
            
            # Collect individual peak metrics for scatter plots
            if pp['peak_frequency_shifts']:
                frequency_shifts.append((filter_name, pp['peak_frequency_shifts']))
            if pp['peak_magnitude_ratios']:
                magnitude_ratios.append((filter_name, pp['peak_magnitude_ratios']))
        
        # Set x locations and create subplots
        x_locs = np.arange(len(filter_names))
        
        # 1. Peak count preservation
        ax1 = fig.add_subplot(gs[0, 0])
        bars = ax1.bar(x_locs, peak_counts, color=colors[:len(filter_names)])
        
        # Add peak count labels
        for bar, count in zip(bars, peak_counts):
            ax1.text(bar.get_x() + bar.get_width()/2., bar.get_height() + 0.1,
                    f'{count}/{ref_peak_count}', ha='center', va='bottom', fontsize=10)
        
        ax1.set_xticks(x_locs)
        ax1.set_xticklabels(filter_names, rotation=45, ha='right')
        ax1.set_title("Peak Preservation Count", fontsize=12)
        ax1.set_ylabel("Number of Preserved Peaks", fontsize=10)
        ax1.grid(True, alpha=0.3)
        
        # 2. Overall preservation score
        ax2 = fig.add_subplot(gs[0, 1])
        bars = ax2.bar(x_locs, preservation_scores, color=colors[:len(filter_names)])
        
        # Add score labels
        for bar, score in zip(bars, preservation_scores):
            ax2.text(bar.get_x() + bar.get_width()/2., bar.get_height() + 0.02,
                    f'{score:.2f}', ha='center', va='bottom', fontsize=10)
        
        ax2.set_xticks(x_locs)
        ax2.set_xticklabels(filter_names, rotation=45, ha='right')
        ax2.set_title("Overall Peak Preservation Score", fontsize=12)
        ax2.set_ylabel("Score", fontsize=10)
        # ax2.set_ylim([0, 1.1])
        ax2.grid(True, alpha=0.3)
        
        # 3. Frequency shift diagram
        ax3 = fig.add_subplot(gs[1, 0])
        
        for i, (filter_name, shifts) in enumerate(frequency_shifts):
            filter_idx = filter_names.index(filter_name)
            ax3.scatter([x_locs[filter_idx]] * len(shifts), shifts, 
                        color=colors[filter_idx], s=50, alpha=0.7, edgecolors='k')
        
        ax3.axhline(y=0, color='k', linestyle='--', alpha=0.3)
        ax3.set_xticks(x_locs)
        ax3.set_xticklabels(filter_names, rotation=45, ha='right')
        ax3.set_title("Frequency Shift of Peaks", fontsize=12)
        ax3.set_ylabel("Shift (Hz)", fontsize=10)
        ax3.grid(True, alpha=0.3)
        
        # 4. Magnitude ratio diagram
        ax4 = fig.add_subplot(gs[1, 1])
        
        for i, (filter_name, ratios) in enumerate(magnitude_ratios):
            filter_idx = filter_names.index(filter_name)
            ax4.scatter([x_locs[filter_idx]] * len(ratios), ratios, 
                        color=colors[filter_idx], s=50, alpha=0.7, edgecolors='k')
        
        ax4.axhline(y=1.0, color='k', linestyle='--', alpha=0.3)
        ax4.set_xticks(x_locs)
        ax4.set_xticklabels(filter_names, rotation=45, ha='right')
        ax4.set_title("Magnitude Ratio of Peaks", fontsize=12)
        ax4.set_ylabel("Ratio (filtered/original)", fontsize=10)
        ax4.set_ylim([0, 2])
        ax4.grid(True, alpha=0.3)
        
        plt.tight_layout()
        return fig

    def _create_metrics_plot(self, comparison_results, filter_names, colors, sensor_name):
        """Create metrics comparison plot"""
        import matplotlib.pyplot as plt
        from matplotlib.gridspec import GridSpec
        import numpy as np
        
        # Select metrics to visualize
        metrics = ['rmse', 'snr_db', 'correlation', 'energy_ratio']
        
        # Check if we have preservation scores
        if any('peak_preservation' in comparison_results[f] for f in filter_names):
            metrics.append('preservation_score')
        
        # Collect metric data
        metric_data = {metric: [] for metric in metrics}
        
        for filter_name in filter_names:
            results = comparison_results[filter_name]
            
            for metric in metrics:
                if metric == 'preservation_score' and 'peak_preservation' in results:
                    metric_data[metric].append(results['peak_preservation']['overall_preservation_score'])
                elif metric in results.get('time_metrics', {}):
                    metric_data[metric].append(results['time_metrics'][metric])
                else:
                    metric_data[metric].append(0.0)
        
        # Create figure with subplots for each metric
        fig = plt.figure(figsize=(14, 10))
        rows = (len(metrics) + 1) // 2  # Ceiling division
        gs = GridSpec(rows, 2, figure=fig)
        
        x_locs = np.arange(len(filter_names))
        
        for i, metric in enumerate(metrics):
            ax = fig.add_subplot(gs[i//2, i%2])
            
            # Normalize values for better visualization
            values = metric_data[metric]
            if len(values) > 0 and max(values) > min(values):
                if metric in ['rmse', 'mae']:
                    # Lower is better
                    normalized = [1 - (val - min(values)) / (max(values) - min(values)) for val in values]
                    goal = "Lower is better"
                else:
                    # Higher is better
                    normalized = [(val - min(values)) / (max(values) - min(values)) for val in values]
                    goal = "Higher is better"
            else:
                normalized = [0.5 for _ in values]
                goal = "No variation"
            
            # Create bar chart
            bars = ax.bar(x_locs, normalized, color=colors[:len(filter_names)])
            
            # Add value labels
            for j, bar in enumerate(bars):
                ax.text(bar.get_x() + bar.get_width()/2., bar.get_height() + 0.02,
                        f'{values[j]:.4f}', ha='center', va='bottom', fontsize=8)
            
            ax.set_xticks(x_locs)
            ax.set_xticklabels(filter_names, rotation=45, ha='right')
            ax.set_title(f"{metric.upper()} ({goal})")
            ax.set_ylim([0, 1.1])
            ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        return fig

    def _create_filter_detail_plot(self, time_array, original_data, filter_results, filter_name, color, fs, sensor_name):
        """Create detailed plot for a single filter"""
        import matplotlib.pyplot as plt
        from matplotlib.gridspec import GridSpec
        from scipy import signal
        
        fig = plt.figure(figsize=(14, 10))
        gs = GridSpec(2, 2, figure=fig)
        
        filtered_data = filter_results['filtered_data']
        
        # Time domain - full view
        ax_time_full = fig.add_subplot(gs[0, :])
        ax_time_full.plot(time_array, original_data, 'k-', alpha=0.7, label='Original')
        ax_time_full.plot(time_array, filtered_data, color=color, label=filter_name)
        ax_time_full.set_title(f"{filter_name} - Time Domain (Full)", fontsize=12)
        ax_time_full.set_xlabel("Time (s)")
        ax_time_full.set_ylabel("Amplitude")
        ax_time_full.grid(True, alpha=0.3)
        ax_time_full.legend()
        
        # Time domain - zoomed view (middle 10%)
        ax_time_zoom = fig.add_subplot(gs[1, 0])
        mid_point = len(time_array) // 2
        window = len(time_array) // 10
        start_idx = mid_point - window // 2
        end_idx = mid_point + window // 2
        
        ax_time_zoom.plot(time_array[start_idx:end_idx], original_data[start_idx:end_idx], 
                        'k-', alpha=0.7, label='Original')
        ax_time_zoom.plot(time_array[start_idx:end_idx], filtered_data[start_idx:end_idx], 
                        color=color, label=filter_name)
        ax_time_zoom.set_title(f"{filter_name} - Time Domain (Zoomed)", fontsize=12)
        ax_time_zoom.set_xlabel("Time (s)")
        ax_time_zoom.set_ylabel("Amplitude")
        ax_time_zoom.grid(True, alpha=0.3)
        ax_time_zoom.legend()
        
        # Frequency domain
        ax_freq = fig.add_subplot(gs[1, 1])
        f_orig, psd_orig = signal.welch(original_data, fs, nperseg=min(512, len(original_data)//10))
        f, psd = signal.welch(filtered_data, fs, nperseg=min(512, len(filtered_data)//10))
        
        ax_freq.semilogy(f_orig, psd_orig, 'k-', alpha=0.7, label='Original')
        ax_freq.semilogy(f, psd, color=color, label=filter_name)
        ax_freq.set_title(f"{filter_name} - Frequency Domain", fontsize=12)
        ax_freq.set_xlabel("Frequency (Hz)")
        ax_freq.set_ylabel("Power Spectral Density")
        ax_freq.grid(True, alpha=0.3)
        ax_freq.set_xlim([0, min(fs/2, 200)])
        ax_freq.legend()
        
        # Add metrics as text
        metrics_text = f"Metrics:\n"
        metrics_text += f"RMSE: {filter_results['time_metrics']['rmse']:.6f}\n"
        metrics_text += f"Correlation: {filter_results['time_metrics']['correlation']:.6f}\n"
        metrics_text += f"SNR (dB): {filter_results['time_metrics']['snr_db']:.2f}\n"
        metrics_text += f"Energy Ratio: {filter_results['time_metrics']['energy_ratio']:.6f}\n"
        
        # Add peak preservation metrics if available
        if 'peak_preservation' in filter_results:
            pp = filter_results['peak_preservation']
            metrics_text += f"\nPeak Preservation:\n"
            metrics_text += f"Preserved peaks: {pp['preserved_peak_count']}\n"
            metrics_text += f"Overall score: {pp['overall_preservation_score']:.4f}\n"
        
        fig.text(0.02, 0.02, metrics_text, fontsize=10, backgroundcolor='white', alpha=0.8)
        
        plt.tight_layout()
        return fig

    # FILTER COMPARE GENERATE REPORT PART
    def generate_filter_report(self, sensor_name, comparison_results, output_dir, ranking_criteria=None):
        """
        Generate a comprehensive HTML report of filter comparisons.
        
        Args:
            sensor_name: Name of the sensor being analyzed
            comparison_results: Output from compare_filters method
            output_dir: Directory to save the report
            ranking_criteria: Optional criteria for ranking filters
            
        Returns:
            Path to the generated HTML report
        """
        
        # Create output directory if needed
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        # Generate all plots
        self.visualize_filter_comparison(sensor_name, comparison_results, output_dir)
        
        # Rank filters
        ranked_filters, scores = self.rank_filters(comparison_results, ranking_criteria)
        
        # Generate HTML report
        report_path = os.path.join(output_dir, f"{sensor_name}_filter_report.html")
        
        with open(report_path, 'w') as f:
            # Write HTML header and CSS
            self._write_html_header(f, sensor_name)
            
            # Write filter rankings section
            self._write_filter_rankings(f, ranked_filters, scores)
            
            # Write metrics comparison section
            self._write_metrics_comparison(f, ranked_filters, comparison_results)
            
            # Write frequency band analysis section
            self._write_frequency_band_analysis(f, ranked_filters, comparison_results)
            
            # Write dominant frequency analysis section
            self._write_dominant_frequency_analysis(f, ranked_filters, comparison_results)
            
            # Write plots section
            self._write_plots_section(f, sensor_name, ranked_filters)
            
            # Write HTML footer
            f.write("</body>\n</html>")
            
        return report_path

    def _write_html_header(self, file, sensor_name):
        """Write HTML header with CSS styles"""
        file.write(f"""<!DOCTYPE html>
    <html>
    <head>
        <title>Filter Comparison Report - {sensor_name}</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; }}
            h1, h2, h3 {{ color: #2c3e50; }}
            table {{ border-collapse: collapse; width: 100%; margin-bottom: 20px; }}
            th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
            th {{ background-color: #f2f2f2; }}
            tr:nth-child(even) {{ background-color: #f9f9f9; }}
            .metric-good {{ color: green; }}
            .metric-bad {{ color: red; }}
            .container {{ display: flex; flex-wrap: wrap; justify-content: space-between; }}
            .image-container {{ width: 48%; margin-bottom: 20px; }}
            img {{ max-width: 100%; height: auto; border: 1px solid #ddd; }}
        </style>
    </head>
    <body>
        <h1>Filter Comparison Report</h1>
        <p><strong>Sensor:</strong> {sensor_name}</p>
        <p><strong>Date:</strong> {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    """)

    def _write_filter_rankings(self, file, ranked_filters, scores):
        """Write filter rankings section"""
        file.write("""
        <h2>Filter Rankings</h2>
        <table>
            <tr>
                <th>Rank</th>
                <th>Filter</th>
                <th>Score</th>
            </tr>
    """)
        
        for i, filter_name in enumerate(ranked_filters):
            file.write(f"""
            <tr>
                <td>{i+1}</td>
                <td>{filter_name}</td>
                <td>{scores[filter_name]:.4f}</td>
            </tr>""")
        
        file.write("</table>\n")

    def _write_metrics_comparison(self, file, ranked_filters, comparison_results):
        """Write metrics comparison section"""
        file.write("""
        <h2>Metrics Comparison</h2>
        <table>
            <tr>
                <th>Filter</th>
                <th>RMSE</th>
                <th>SNR (dB)</th>
                <th>Correlation</th>
                <th>Energy Ratio</th>
            </tr>
    """)
        
        for filter_name in ranked_filters:
            metrics = comparison_results[filter_name]['time_metrics']
            file.write(f"""
            <tr>
                <td>{filter_name}</td>
                <td class="metric-{"good" if metrics['rmse'] < 0.1 else "bad"}">{metrics['rmse']:.6f}</td>
                <td class="metric-{"good" if metrics['snr_db'] > 20 else "bad"}">{metrics['snr_db']:.2f}</td>
                <td class="metric-{"good" if metrics['correlation'] > 0.9 else "bad"}">{metrics['correlation']:.6f}</td>
                <td class="metric-{"good" if 0.9 < metrics['energy_ratio'] < 1.1 else "bad"}">{metrics['energy_ratio']:.6f}</td>
            </tr>""")
        
        file.write("</table>\n")

    def _write_frequency_band_analysis(self, file, ranked_filters, comparison_results):
        """Write frequency band analysis section"""
        file.write("""
        <h2>Frequency Band Analysis</h2>
        <table>
            <tr>
                <th>Filter</th>
                <th>Low Band Ratio</th>
                <th>Mid Band Ratio</th>
                <th>High Band Ratio</th>
            </tr>
    """)
        
        for filter_name in ranked_filters:
            freq_metrics = comparison_results[filter_name]['frequency_metrics']
            file.write(f"""
            <tr>
                <td>{filter_name}</td>
                <td class="metric-{"good" if 0.9 < freq_metrics['low_band_ratio'] < 1.1 else "bad"}">{freq_metrics['low_band_ratio']:.6f}</td>
                <td class="metric-{"good" if 0.9 < freq_metrics['mid_band_ratio'] < 1.1 else "bad"}">{freq_metrics['mid_band_ratio']:.6f}</td>
                <td class="metric-{"good" if 0.9 < freq_metrics['high_band_ratio'] < 1.1 else "bad"}">{freq_metrics['high_band_ratio']:.6f}</td>
            </tr>""")
        
        file.write("</table>\n")

    def _write_dominant_frequency_analysis(self, file, ranked_filters, comparison_results):
        """Write dominant frequency analysis section"""
        file.write("""
        <h2>Dominant Frequency Analysis</h2>
        <table>
            <tr>
                <th>Filter</th>
                <th>Preserved Peaks</th>
                <th>Preservation Score</th>
                <th>Dominant Frequencies</th>
            </tr>
    """)
        
        # Get reference peak count
        ref_peak_count = 0
        if '__reference_fft' in comparison_results:
            ref_peak_count = len(comparison_results['__reference_fft']['dominant_peaks'])
        
        for filter_name in ranked_filters:
            if 'peak_preservation' in comparison_results[filter_name]:
                peak_metrics = comparison_results[filter_name]['peak_preservation']
                preserved_count = peak_metrics['preserved_peak_count']
                preservation_score = peak_metrics['overall_preservation_score']
                
                # Get dominant peaks
                dominant_peaks = []
                if 'fft' in comparison_results[filter_name]:
                    dominant_peaks = comparison_results[filter_name]['fft']['dominant_peaks']
                
                # Format peak information
                peak_str = ", ".join([f"{freq:.1f} Hz (mag: {mag:.3f})" for freq, mag, _ in dominant_peaks])
                
                file.write(f"""
            <tr>
                <td>{filter_name}</td>
                <td class="metric-{"good" if preserved_count == ref_peak_count else "bad"}">{preserved_count}/{ref_peak_count}</td>
                <td class="metric-{"good" if preservation_score > 0.8 else "bad"}">{preservation_score:.4f}</td>
                <td>{peak_str}</td>
            </tr>""")
        
        file.write("</table>\n")

    def _write_plots_section(self, file, sensor_name, ranked_filters):
        """Write plots section with image references"""
        plot_sections = [
            ("Time Domain Comparison", f"{sensor_name}_time_comparison.png"),
            ("Frequency Domain Comparison", f"{sensor_name}_frequency_comparison.png"),
            ("FFT Comparison", f"{sensor_name}_fft_comparison.png"),
            ("Peak Preservation Analysis", f"{sensor_name}_peaks_comparison.png"),
            ("Metrics Comparison", f"{sensor_name}_metrics_comparison.png")
        ]
        
        for title, image_file in plot_sections:
            file.write(f"""
        <h2>{title}</h2>
        <div class="image-container">
            <img src="./{image_file}" alt="{title}">
        </div>
    """)
        
        # Individual filter details
        file.write("""
        <h2>Individual Filter Details</h2>
        <div class="container">
    """)
        
        for filter_name in ranked_filters:
            safe_name = filter_name.replace(' ', '_').lower()
            file.write(f"""
            <div class="image-container">
                <h3>{filter_name}</h3>
                <img src="./{sensor_name}_{safe_name}_detail.png" alt="{filter_name} Details">
            </div>""")
        
        file.write("\n    </div>\n")

