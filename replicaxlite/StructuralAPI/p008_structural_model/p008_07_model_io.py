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


import ezdxf


class ModelIO:
    """Handles import/export functions for the structural model"""
    
    def __init__(self, parent_model):
        self.parent = parent_model
    
    def export_to_dxf(self, filename: str):
        """
        Export the model to a DXF file.
        
        Parameters:
        -----------
        filename : str
            Path to output DXF file
        """
        # Create new DXF document
        doc = ezdxf.new('R2010')
        msp = doc.modelspace()
        
        # Create layer for each element type
        for element_type in self.parent.geometry.element_groups.keys():
            doc.layers.add(name=element_type.upper())
        
        # Add elements as lines
        for element in self.parent.geometry.elements.values():
            start_node = element.get_start_node()
            end_node = element.get_end_node()
            
            # Map element type to layer name
            layer_name = element.structural_type.upper()
            
            # Create line
            msp.add_line(
                (start_node.x, start_node.y, start_node.z),
                (end_node.x, end_node.y, end_node.z),
                dxfattribs={'layer': layer_name}
            )
        
        # Save DXF file
        doc.saveas(filename)
        self.parent._log(f"Model exported to DXF file: {filename}")
    
    def import_from_dxf(self, filename: str, layer_mapping: dict = None, 
                      priorities: list[str] = None, start_id_nodes: int = None, 
                      start_id_elements: int = None, merge_nodes: bool = True,
                      remove_duplicates: bool = True, remove_free_nodes: bool = True):
        """
        Import a model from a DXF file.
        
        Parameters:
        -----------
        filename : str
            Path to DXF file
        layer_mapping : dict
            Mapping from DXF layer names to element types
        priorities : list[str]
            Priority strings for coordinate sorting ('X+', 'Y-', 'Z+', etc.)
            If None, points will be processed in their original order
        start_id_nodes, start_id_elements : int
            Starting IDs for nodes and elements. If None, will use the next available IDs.
        merge_nodes : bool
            Whether to merge nodes that are very close to each other
        remove_duplicates : bool
            Whether to remove duplicate elements connecting the same nodes
        remove_free_nodes : bool
            Whether to remove nodes not connected to any elements
            
        Returns:
        --------
        dict
            Dictionary with counts of imported nodes and elements
        """
        # Check if model is already built
        if self.parent._model_built:
            raise RuntimeError("Cannot import model after OpenSees model has been built")
            
        # Default layer mapping
        if layer_mapping is None:
            layer_mapping = {
                "COLUMN": "column",
                "BEAM": "beam",
                "WALL": "wall",
                "SLAB": "slab",
                "TRUSS": "truss",
                "TREE": "tree",
                "INFILL": "infill",
                "GENERAL": "general",
                
                "BEAM_X": "beam_x",
                "BEAM_Y": "beam_y",
                "BEAM_XY": "beam_xy",
                "BEAM_BALCONY": "beam_balcony",
                "BEAM_BALCONY_X": "beam_balcony_x",
                "BEAM_BALCONY_Y": "beam_balcony_y",
                "BEAM_BALCONY_XY": "beam_balcony_xy",
                "BEAM_BASE": "beam_base",
                "BEAM_BASE_X": "beam_base_x",
                "BEAM_BASE_Y": "beam_base_y",
                "BEAM_BASE_XY": "beam_base_xy",
                "INFILL_X": "infill_x",
                "INFILL_BACKSLASH": "infill_backslash",
                "INFILL_FORWARD": "infill_forward",
                "INFILL_X_AND_CROSS": "infill_x_and_cross"  
            }
        
        # Set default starting IDs if not provided
        if start_id_nodes is None:
            start_id_nodes = self.parent.geometry.next_node_id
        
        if start_id_elements is None:
            start_id_elements = self.parent.geometry.next_element_id
        
        # Parse priorities if provided
        parsed_priorities = []
        if priorities is not None:
            for priority in priorities:
                if len(priority) != 2:
                    raise ValueError(f"Invalid priority format: {priority}")
                    
                axis = priority[0].upper()
                direction = priority[1]
                
                if axis not in ['X', 'Y', 'Z']:
                    raise ValueError(f"Invalid axis: {axis}")
                if direction not in ['+', '-']:
                    raise ValueError(f"Invalid direction: {direction}")
                    
                is_positive = (direction == '+')
                parsed_priorities.append((axis, is_positive))
        
        # Load DXF file
        try:
            doc = ezdxf.readfile(filename)
        except IOError:
            raise IOError(f"Cannot open DXF file: {filename}")
        except ezdxf.DXFStructureError:
            raise ValueError(f"Invalid or corrupted DXF file: {filename}")
        
        # Extract all lines from the DXF file
        msp = doc.modelspace()
        lines = []
        
        for entity in msp.query('LINE'):
            layer_name = entity.dxf.layer
            element_type = layer_mapping.get(layer_name, "unknown")
            
            # Skip unknown layers
            if element_type == "unknown":
                self.parent._log(f"Skipping entity on unknown layer: {layer_name}", level="warning")
                continue
            
            # Get start and end points
            start_point = entity.dxf.start
            end_point = entity.dxf.end
            
            # Store line data
            lines.append({
                'start': (start_point.x, start_point.y, start_point.z),
                'end': (end_point.x, end_point.y, end_point.z),
                'element_type': element_type
            })
        
        # Collect all unique points
        unique_points = set()
        for line in lines:
            unique_points.add(tuple(round(c, 6) for c in line['start']))
            unique_points.add(tuple(round(c, 6) for c in line['end']))
        
        # Convert to list and sort if priorities are provided
        if priorities is not None:
            # Sort points by coordinate priority
            def point_sort_key(point):
                key = []
                for axis, is_positive in parsed_priorities:
                    idx = ord(axis) - ord('X')  # Convert X,Y,Z to 0,1,2
                    value = point[idx]
                        
                    if not is_positive:
                        value = -value
                        
                    key.append(value)
                return tuple(key)
            
            sorted_points = sorted(unique_points, key=point_sort_key)
        else:
            # Use original order if no priorities provided
            sorted_points = list(unique_points)
        
        # Map coordinates to node IDs
        point_to_node_id = {}
        nodes = {}
        
        # Create nodes with sequential IDs starting from start_id_nodes
        node_id = start_id_nodes
        for point in sorted_points:
            point_to_node_id[point] = node_id
            nodes[node_id] = self.parent.geometry.create_node(node_id, *point)
            node_id += 1
        
        # Process lines to create elements
        elements = []
        for line in lines:
            start_key = tuple(round(c, 6) for c in line['start'])
            end_key = tuple(round(c, 6) for c in line['end'])
            
            # Get node IDs
            start_node_id = point_to_node_id[start_key]
            end_node_id = point_to_node_id[end_key]
            
            # Only add element if it has non-zero length
            if start_node_id != end_node_id:
                elements.append({
                    'start_node': nodes[start_node_id],
                    'end_node': nodes[end_node_id],
                    'element_type': line['element_type']
                })
        
        # Sort elements if priorities are provided
        if priorities is not None:
            def element_sort_key(elem):
                start_node = elem['start_node']
                end_node = elem['end_node']
                
                # Calculate midpoint
                mid_x = (start_node.x + end_node.x) / 2
                mid_y = (start_node.y + end_node.y) / 2
                mid_z = (start_node.z + end_node.z) / 2
                
                key = []
                for axis, is_positive in parsed_priorities:
                    if axis == 'X':
                        value = mid_x
                    elif axis == 'Y':
                        value = mid_y
                    else:  # axis == 'Z'
                        value = mid_z
                        
                    if not is_positive:
                        value = -value
                        
                    key.append(value)
                return tuple(key)
            
            elements.sort(key=element_sort_key)
        
        # Add elements to model with sequential IDs
        element_id = start_id_elements
        for elem in elements:
            new_element = self.parent.geometry.create_line_element(
                element_id, 
                elem['start_node'], 
                elem['end_node'], 
                elem['element_type']
            )
            element_id += 1
        
        # ---- INTEGRATED CLEANUP FUNCTIONALITY ----
        merged_nodes = 0
        removed_elements = 0
        removed_free_nodes = 0
        
        # 1. Merge duplicate nodes
        if merge_nodes:
            duplicate_pairs = self.parent.geometry.check_duplicate_nodes()
            
            if duplicate_pairs:
                # Create a mapping from old node IDs to new node IDs
                node_map = {}
                
                # Union-find algorithm to group duplicate nodes
                for node1_tag, node2_tag in duplicate_pairs:
                    # Find root representatives
                    while node1_tag in node_map:
                        node1_tag = node_map[node1_tag]
                    while node2_tag in node_map:
                        node2_tag = node_map[node2_tag]
                        
                    # Merge into the node with the lower ID
                    if node1_tag != node2_tag:
                        if node1_tag < node2_tag:
                            node_map[node2_tag] = node1_tag
                        else:
                            node_map[node1_tag] = node2_tag
                
                # Update all paths to point directly to the root
                for node_tag in list(node_map.keys()):
                    root_tag = node_tag
                    while root_tag in node_map:
                        root_tag = node_map[root_tag]
                    node_map[node_tag] = root_tag
                
                # Update elements to use the merged nodes
                for element in self.parent.geometry.elements.values():
                    if hasattr(element.start_node, 'tag') and element.start_node.tag in node_map:
                        element.start_node = self.parent.geometry.nodes[node_map[element.start_node.tag]]
                        
                    if hasattr(element.end_node, 'tag') and element.end_node.tag in node_map:
                        element.end_node = self.parent.geometry.nodes[node_map[element.end_node.tag]]
                
                # Update constraints if any
                for node_tag in list(self.parent.constraints.constraints.keys()):
                    if node_tag in node_map:
                        constraint = self.parent.constraints.constraints.pop(node_tag)
                        merged_tag = node_map[node_tag]
                        if merged_tag not in self.parent.constraints.constraints:
                            constraint.node_tag = merged_tag
                            self.parent.constraints.constraints[merged_tag] = constraint
                
                # Remove the duplicate nodes
                for node_tag in list(node_map.keys()):
                    if node_tag != node_map[node_tag]:  # Skip root nodes
                        if node_tag in self.parent.geometry.nodes:
                            del self.parent.geometry.nodes[node_tag]
                            merged_nodes += 1
        
        # 2. Remove duplicate elements
        if remove_duplicates:
            duplicate_element_pairs = self.parent.geometry.check_duplicate_elements()
            
            # Create a set of element IDs to remove
            elements_to_remove = set()
            
            for elem1_id, elem2_id in duplicate_element_pairs:
                # Keep the element with the lower ID
                if elem1_id < elem2_id:
                    elements_to_remove.add(elem2_id)
                else:
                    elements_to_remove.add(elem1_id)
            
            # Remove the duplicate elements
            for element_id in elements_to_remove:
                self.parent.geometry.remove_element(element_id)
                removed_elements += 1
        
        # 3. Remove free nodes
        if remove_free_nodes:
            removed_free_nodes = self.parent.geometry.remove_free_nodes()
        
        # ---- END OF INTEGRATED CLEANUP ----
        
        # Log results
        imported_count = {
            'nodes': len(self.parent.geometry.nodes),
            'elements': len(self.parent.geometry.elements),
            'merged_nodes': merged_nodes,
            'removed_elements': removed_elements,
            'removed_free_nodes': removed_free_nodes
        }
        
        self.parent._log(f"Model imported from DXF file: {filename}")
        self.parent._log(f"Imported {imported_count['nodes']} nodes and {imported_count['elements']} elements")
        
        cleanup_msg = []
        if merge_nodes and merged_nodes > 0:
            cleanup_msg.append(f"merged {merged_nodes} nodes")
        if remove_duplicates and removed_elements > 0:
            cleanup_msg.append(f"removed {removed_elements} duplicate elements")
        if remove_free_nodes and removed_free_nodes > 0:
            cleanup_msg.append(f"removed {removed_free_nodes} free nodes")
        
        if cleanup_msg:
            self.parent._log(f"Cleanup: {', '.join(cleanup_msg)}")
        
        return imported_count

