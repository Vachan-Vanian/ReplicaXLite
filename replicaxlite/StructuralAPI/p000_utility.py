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


def dict_cmd_to_openseespy_list_cmd(ops_dic_cmd: dict) -> list:
    """
    Process opensees arguments from a dictionary into a flat list suitable for 
    OpenSeesPy function. 
    
    For keys starting with '-', None or empty string values are skipped.
    For other keys, None or empty string values will raise a ValueError.
    
    Parameters:
    -----------
    ops_dic_cmd : dict
        Dictionary of command arguments
        
    Returns:
    --------
    list
        Flattened list of arguments
        
    Raises:
    -------
    ValueError
        If None or empty string values are found for keys not starting with '-'
    """
    # Initialize the list to collect processed arguments
    args = []
    
    # Process each key-value pair according to the rules
    for key, value in ops_dic_cmd.items():
        # Check if key starts with '-'
        if key.startswith('-'):
            args.append(key)
            # Skip None or empty string values
            if value is not None and value != '':
                if isinstance(value, list):
                    args.extend(value)
                else:
                    args.append(value)
        
        # For other keys (including those starting with '*')
        else:
            if isinstance(value, list):
                args.extend(value)
            elif value is None or value == '':
                raise ValueError(f"None or empty string value not allowed for key '{key}'. This may lead to incorrect argument count.")
            else:
                args.append(value)
    
    return args


def calculate_aligned_vecxz(start: tuple[float, float, float], end: tuple[float, float, float], tol: float = 1e-6) -> list[float]:
    """
    Calculate the vector defining the local z-axis for an element in OpenSees transformation.
    
    This function computes the appropriate local z-axis vector for an element defined by
    two points in 3D space. This is used in OpenSees to define the geometric transformation
    of frame elements.
    
    Parameters:
    -----------
    start : tuple[float, float, float]
        Coordinates of the start node as (x, y, z)
    end : tuple[float, float, float]
        Coordinates of the end node as (x, y, z)
    tol : float, optional
        Tolerance for geometric checks, defaults to 1e-6
        
    Returns:
    --------
    List[float]
        The vecxz vector (local z-axis direction) for OpenSees transformation
    
    Raises:
    -------
    ValueError
        If the element length is too small (less than tolerance)
    """
    
    xAxis = [end[0] - start[0], end[1] - start[1], end[2] - start[2]]
    length = math.sqrt(sum(x**2 for x in xAxis))
    
    if length < tol:
        raise ValueError("Element length is too small")
    
    xAxis = [x/length for x in xAxis]
    
    # Check if member is vertical
    is_vertical = abs(abs(xAxis[2]) - 1.0) < tol
    
    if is_vertical:
        # For vertical members, align y-axis with global Y
        yAxis = [0.0, 1.0, 0.0]
        
        # Ensure y-axis is perpendicular to x-axis
        dot_product = sum(y*x for y, x in zip(yAxis, xAxis))
        yAxis = [y - dot_product * x for y, x in zip(yAxis, xAxis)]
        
        y_norm = math.sqrt(sum(y**2 for y in yAxis))
        
        if y_norm > tol:
            yAxis = [y/y_norm for y in yAxis]
        else:
            # If y is parallel to x, use a different reference
            if abs(xAxis[0]) < tol and abs(xAxis[1]) < tol:
                yAxis = [1.0, 0.0, 0.0]
            else:
                yAxis = [0.0, 0.0, 1.0]
            
            dot_product = sum(y*x for y, x in zip(yAxis, xAxis))
            yAxis = [y - dot_product * x for y, x in zip(yAxis, xAxis)]
            y_norm = math.sqrt(sum(y**2 for y in yAxis))
            yAxis = [y/y_norm for y in yAxis]
        
        # Calculate z-axis using cross product
        zAxis = [
            xAxis[1] * yAxis[2] - xAxis[2] * yAxis[1],
            xAxis[2] * yAxis[0] - xAxis[0] * yAxis[2],
            xAxis[0] * yAxis[1] - xAxis[1] * yAxis[0]
        ]
    else:
        # For non-vertical members, z-axis has component pointing up
        globalZ = [0.0, 0.0, 1.0]
        
        # Project global Z onto plane perpendicular to x-axis
        dot_product = sum(z*x for z, x in zip(globalZ, xAxis))
        projZ = [z - dot_product * x for z, x in zip(globalZ, xAxis)]
        
        projZ_norm = math.sqrt(sum(z**2 for z in projZ))
        
        if projZ_norm < tol:
            # Handle case where member is almost vertical
            globalY = [0.0, 1.0, 0.0]
            dot_product = sum(y*x for y, x in zip(globalY, xAxis))
            projZ = [y - dot_product * x for y, x in zip(globalY, xAxis)]
            projZ_norm = math.sqrt(sum(z**2 for z in projZ))
            projZ = [z/projZ_norm for z in projZ]
        else:
            projZ = [z/projZ_norm for z in projZ]
        
        zAxis = projZ
    
    return zAxis


def calculate_zerolength_orientation(dummy_direction: tuple[float, float, float], tol: float = 1e-6) -> tuple[list[float], list[float]]:
    """
    Calculate orientation vectors for a zeroLength element in OpenSees.
    
    This function DIRECTLY uses the regular element's approach to maintain consistency.
    """
    # Treat dummy_direction as element direction vector (from start to end node)
    start = (0, 0, 0)  # Dummy start point
    end = dummy_direction  # Direction becomes the end point
    
    # Get the z-axis using the same function as for regular elements
    zAxis = calculate_aligned_vecxz(start, end)
    
    # Normalize direction to get x-axis
    xAxis = list(dummy_direction)
    length = math.sqrt(sum(x**2 for x in xAxis))
    
    if length < tol:
        raise ValueError("Direction vector length is too small")
    
    xAxis = [x/length for x in xAxis]
    
    # Calculate y-axis = z-axis × x-axis (cross product)
    yAxis = [
        zAxis[1] * xAxis[2] - zAxis[2] * xAxis[1],
        zAxis[2] * xAxis[0] - zAxis[0] * xAxis[2],
        zAxis[0] * xAxis[1] - zAxis[1] * xAxis[0]
    ]
    
    # Normalize y-axis
    y_norm = math.sqrt(sum(y**2 for y in yAxis))
    yAxis = [y/y_norm for y in yAxis]
    
    # Return vecx and vecyp for zeroLength element orientation
    # xAxis=vecx, vecyp=yAxis
    return xAxis, yAxis

