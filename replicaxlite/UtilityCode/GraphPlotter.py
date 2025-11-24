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


import matplotlib.pyplot as plt
import numpy as np
from matplotlib.ticker import FuncFormatter

def create_enhanced_tick_formatter(
    max_decimals=13,
    scientific_threshold=1e6,
    small_threshold=1e-3,
    force_scientific=False,
    integer_threshold=1e-10
):
    """
    Creates a configurable tick formatter function.
    
    Parameters:
        max_decimals: Maximum decimal places to show (default: 3)
        scientific_threshold: Use scientific notation for abs(values) >= this (default: 1e6)
        small_threshold: Use scientific notation for abs(values) < this (default: 1e-3)
        force_scientific: If True, always use scientific notation (default: False)
        integer_threshold: Values closer than this to integers are shown as integers (default: 1e-10)
    
    Returns:
        Formatter function to use with matplotlib
    """
    def enhanced_tick_formatter(value, pos):
        # Handle zero
        if abs(value) < 1e-15:
            return "0"
        
        # Force scientific notation if requested
        if force_scientific:
            return f"{value:.{max_decimals-1}e}"
        
        # Use scientific notation for very large or very small numbers
        if abs(value) >= scientific_threshold or (abs(value) < small_threshold and value != 0):
            return f"{value:.{max_decimals-1}e}"
        
        # Check if it's very close to an integer
        if abs(value - round(value)) < integer_threshold:
            return f"{int(round(value))}"
        
        # For regular decimals, use smart decimal places
        # Start with max_decimals and reduce trailing zeros
        formatted = f"{value:.{max_decimals}f}"
        
        # Remove trailing zeros and unnecessary decimal point
        if '.' in formatted:
            formatted = formatted.rstrip('0').rstrip('.')
        
        return formatted
    
    return enhanced_tick_formatter

def create_replicax_report_plots(
    datasets,
    x_label="X label",
    y_label="Y label",
    x_limits=None,
    y_limits=None,
    x_step=None,
    y_step=None,
    x_label_pos=None,
    figsize=(10, 4),
    save_path='',
    file_name='Plot',
    major_grid=True,
    minor_grid=True,
    show_plot=False,
    tick_precision_config={
        'max_decimals': 3,
        'scientific_threshold': 1e6,
        'small_threshold': 1e-3,
        'force_scientific': False,
        'integer_threshold': 1e-10
    },
    separate_xy_precision=False,  # If True, allows different formatting for x and y axes
    x_tick_precision_config=None,  # Separate config for x-axis
    y_tick_precision_config=None,  # Separate config for y-axis
    fontcfg={
        'font.family': 'Times New Roman',
        'font.size': 10,
        'axes.titlesize': 10,
        'axes.labelsize': 10,
        'xtick.labelsize': 10,
        'ytick.labelsize': 10,
        'legend.fontsize': 10
    }
):
    """
    Enhanced version with configurable tick precision.
    
    New Parameters:
        tick_precision_config: Dictionary with precision settings for both axes
        separate_xy_precision: Boolean, if True allows different formatting for x and y axes
        x_tick_precision_config: Dictionary with precision settings for x-axis only
        y_tick_precision_config: Dictionary with precision settings for y-axis only
    
    Example usage:
        # High precision for scientific data:
        tick_precision_config={'max_decimals': 5, 'scientific_threshold': 1e3}
        
        # Force scientific notation:
        tick_precision_config={'force_scientific': True, 'max_decimals': 2}
        
        # Different precision for x and y axes:
        separate_xy_precision=True,
        x_tick_precision_config={'max_decimals': 1},
        y_tick_precision_config={'max_decimals': 4, 'scientific_threshold': 1e4}
    """
    
    # Apply font settings
    for key, value in fontcfg.items():
        plt.rcParams[key] = value
    
    # Create default fontsize dictionary if minimal settings provided
    default_fontsize = {
        'font.family': 'Times New Roman',
        'font.size': 10,
        'axes.titlesize': 10,
        'axes.labelsize': 10,
        'xtick.labelsize': 10,
        'ytick.labelsize': 10,
        'legend.fontsize': 10
    }
    
    # Apply any missing font settings from default
    for key, value in default_fontsize.items():
        if key not in fontcfg:
            plt.rcParams[key] = value

    # Calculate x_limits and y_limits if not provided
    if x_limits is None or y_limits is None:
        all_x_values = []
        all_y_values = []
        
        for data in datasets:
            all_x_values.extend(data['x_values'])
            all_y_values.extend(data['y_values'])
        
        if x_limits is None:
            x_min = min(all_x_values)
            x_max = max(all_x_values)
            x_range = x_max - x_min
            x_padding = 0.05 * x_range
            x_limits = (x_min - x_padding, x_max + x_padding)
        
        if y_limits is None:
            y_min = min(all_y_values)
            y_max = max(all_y_values)
            y_range = y_max - y_min
            y_padding = 0.1 * y_range
            y_limits = (y_min - y_padding, y_max + y_padding)
    
    # Calculate appropriate step sizes if not provided
    if x_step is None:
        x_range = x_limits[1] - x_limits[0]
        target_ticks = 8
        x_step = x_range / target_ticks
        magnitude = 10 ** np.floor(np.log10(x_step))
        scaled_step = x_step / magnitude
        if scaled_step < 1.5:
            x_step = magnitude
        elif scaled_step < 3:
            x_step = 2 * magnitude
        elif scaled_step < 7.5:
            x_step = 5 * magnitude
        else:
            x_step = 10 * magnitude
            
        x_min_nice = np.floor(x_limits[0] / x_step) * x_step
        x_max_nice = np.ceil(x_limits[1] / x_step) * x_step
        x_limits = (x_min_nice, x_max_nice)
    
    if y_step is None:
        y_range = y_limits[1] - y_limits[0]
        target_ticks = 6
        y_step = y_range / target_ticks
        magnitude = 10 ** np.floor(np.log10(y_step))
        scaled_step = y_step / magnitude
        if scaled_step < 1.5:
            y_step = magnitude
        elif scaled_step < 3:
            y_step = 2 * magnitude
        elif scaled_step < 7.5:
            y_step = 5 * magnitude
        else:
            y_step = 10 * magnitude
            
        y_min_nice = np.floor(y_limits[0] / y_step) * y_step
        y_max_nice = np.ceil(y_limits[1] / y_step) * y_step
        y_limits = (y_min_nice, y_max_nice)

    fig, ax = plt.subplots(figsize=figsize)

    # Define lists of default styles to cycle through
    default_colors = ['blue', 'red', 'green', 'purple', 'orange', 'brown', 'teal', 'magenta', 'black', 'cyan']
    default_line_styles = ['-']
    default_line_widths = [0.5, 0.75, 1.0, 1.25]

    for i, data in enumerate(datasets):
        default_label = f"Dataset {i+1}"
        
        color_index = i % len(default_colors)
        line_style_index = (i // len(default_colors)) % len(default_line_styles)
        line_width_index = i % len(default_line_widths)
        
        default_color = default_colors[color_index]
        default_line_style = default_line_styles[line_style_index]
        default_line_width = default_line_widths[line_width_index]
        
        ax.plot(
            data['x_values'],
            data['y_values'],
            label=data.get('label', default_label),
            color=data.get('color', default_color),
            linestyle=data.get('line_style', default_line_style),
            linewidth=data.get('line_width', default_line_width)
        )

    # Set axis limits
    ax.set_xlim(x_limits)
    ax.set_ylim(y_limits)

    # Create ticks
    x_ticks = np.arange(x_limits[0], x_limits[1] + x_step/2, x_step)
    y_ticks = np.arange(y_limits[0], y_limits[1] + y_step/2, y_step)
    
    ax.set_xticks(x_ticks)
    ax.set_yticks(y_ticks)
    
    # Apply enhanced tick formatting
    if separate_xy_precision and (x_tick_precision_config or y_tick_precision_config):
        # Use separate configurations for x and y axes
        x_config = x_tick_precision_config if x_tick_precision_config else tick_precision_config
        y_config = y_tick_precision_config if y_tick_precision_config else tick_precision_config
        
        x_formatter = create_enhanced_tick_formatter(**x_config)
        y_formatter = create_enhanced_tick_formatter(**y_config)
        
        ax.xaxis.set_major_formatter(FuncFormatter(x_formatter))
        ax.yaxis.set_major_formatter(FuncFormatter(y_formatter))
    else:
        # Use same configuration for both axes
        formatter = create_enhanced_tick_formatter(**tick_precision_config)
        ax.xaxis.set_major_formatter(FuncFormatter(formatter))
        ax.yaxis.set_major_formatter(FuncFormatter(formatter))

    # Customizing spines for aesthetics
    for spine in ['top', 'right', 'left', 'bottom']:
        ax.spines[spine].set_color('black')
        ax.spines[spine].set_linewidth(1.2)

    # Set axis labels
    ax.set_ylabel(y_label, color='black', labelpad=0, fontweight='bold')
    ax.set_xlabel(x_label, color='black', fontweight='bold')
    if x_label_pos:
        ax.xaxis.set_label_coords(*x_label_pos)

    # Tick marks
    ax.tick_params(axis='both', which='major', length=8, width=1.2, direction='inout', color='black', labelcolor='black')
    ax.tick_params(axis='both', which='minor', length=4, width=1, direction='in', color='black')

    # Minor ticks
    ax.minorticks_on()

    # Grid lines
    if major_grid:
        ax.grid(visible=True, which='major', color='gray', linestyle='--', linewidth=0.8, alpha=0.2)
    if minor_grid:
        ax.grid(visible=True, which='minor', color='gray', linestyle='-.', linewidth=0.1, alpha=0.5)

    # Legend
    legend = ax.legend(loc='upper right')
    frame = legend.get_frame()
    frame.set_facecolor('white')
    frame.set_alpha(1.0)

    # Save the figure
    if save_path:
        fig.savefig(f"{save_path}/{file_name}.jpeg", format="jpeg", dpi=300, bbox_inches='tight')

    if show_plot:
        plt.show()

    return fig, ax
