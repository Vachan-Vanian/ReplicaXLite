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


from ..p003_node import Node
from ..p004_element import Element, BeamColumn, Line, GeneralElement


class ModelGeometry:
    """Handles node and element management for the structural model"""
    
    def __init__(self, parent_model):
        self.parent = parent_model
        
        # Component collections
        self.nodes = {}
        self.elements = {}
        
        # Element organization
        self.element_groups = {
            # Core element groups (these match StructuralElement enum values)
            'column': set(),
            'beam': set(),
            'wall': set(),
            'slab': set(),
            'truss': set(),
            'tree': set(),
            'infill': set(),
            'other': set(),

            # Predefined organizational groups
            'beam_x': set(),
            'beam_y': set(),
            'beam_xy': set(),
            'beam_balcony': set(),
            'beam_balcony_x': set(),
            'beam_balcony_y': set(),
            'beam_balcony_xy': set(),
            'beam_base': set(),
            'beam_base_x': set(),
            'beam_base_y': set(),
            'beam_base_xy': set(),
            'infill_backslash': set(),
            'infill_forward': set(),
            'infill_x': set(),
            'infill_x_and_cross': set()

        }

        self.floors = {}  # floor_level -> set of element IDs
        
        # Tracking variables
        self.next_node_id = 1
        self.next_element_id = 1
    
    ### geometry creation
    def create_node(self, tag: int, x: float, y: float, z: float) -> Node:
        """
        USER FUNCTION
        Create a new node and add it to the model.
        
        Parameters:
        -----------
        tag : int
            Node ID (if None, auto-assign)
        x, y, z : float
            Coordinates
            
        Returns:
        --------
        Node
            The created node
        """
        if tag is None:
            tag = self.next_node_id
            self.next_node_id += 1
        
        node = Node(tag, x, y, z)
        return self.add_node(node)
        
    def add_node(self, node: Node) -> Node:
        """
        Add a node to the model without creating it in OpenSees yet.
        
        Parameters:
        -----------
        node : Node
            Node to add to the model
            
        Returns:
        --------
        Node
            The added node
        """
        self.nodes[node.tag] = node
        # Update next node ID if needed
        if node.tag >= self.next_node_id:
            self.next_node_id = node.tag + 1
        self.parent._log(f"Added node {node}")
        return node

    def create_element(self, tag: int, start_node: Node | int, end_node: Node | int, 
                    element_type: str, section_name: str = None, 
                    element_class: str = "forceBeamColumn", integration_tag: int = None, 
                    element_args: dict = None) -> Element:
        """
        USER FUNCTION
        Create a new element and add it to the model.
        
        Parameters:
        -----------
        tag : int
            Element ID (if None, auto-assign)
        start_node, end_node : Node or int
            Start and end nodes (or their IDs)
        element_type : str
            Type of element (from StructuralElement enum)
        section_name : str
            Name of section to use
        element_class : str
            OpenSees element class (elasticBeamColumn, forceBeamColumn, dispBeamColumn)
        integration_tag : int
            Beam integration tag
        element_args : dict
            Additional element arguments
            
        Returns:
        --------
        Element
            The created element
        """
        if tag is None:
            tag = self.next_element_id
        
        # Resolve node references if needed
        if isinstance(start_node, int):
            if start_node in self.nodes:
                start_node = self.nodes[start_node]
            else:
                raise ValueError(f"Node with ID {start_node} not found")
                
        if isinstance(end_node, int):
            if end_node in self.nodes:
                end_node = self.nodes[end_node]
            else:
                raise ValueError(f"Node with ID {end_node} not found")
        
        # Create appropriate element type
        if section_name is not None:
            element = BeamColumn(
                tag, start_node, end_node, element_type, section_name,
                element_class, integration_tag, element_args
            )
        else:
            # For other element types that don't need a section
            element = BeamColumn(tag, start_node, end_node, element_type, None)
        
        return self.add_element(element)
    
    def create_general_element(self, tag: int, start_node: Node | int, end_node: Node | int,
                            element_type: str, structural_element_type: str = "general", 
                            element_args: dict = None, use_transformation: bool = False,
                            transform_type: str = None, transform_keyword: str = 'transfTag') -> GeneralElement:
        """
        USER FUNCTION
        Create a general element of any OpenSeesPy element type.
        
        Parameters:
        -----------
        tag : int
            Element ID (if None, auto-assign)
        start_node, end_node : Node or int
            Start and end nodes (or their IDs)
        element_type : str
            OpenSees element type command (e.g., 'truss', 'zeroLength')
        structural_element_type : str
            Type identifier for model organization (from StructuralElement enum)
        element_args : dict
            Additional element arguments as a dictionary
        use_transformation : bool
            Whether to use geometric transformation
        transform_type : str
            Type of transformation ('Linear', 'PDelta', or 'Corotational')
            If None, will be automatically determined based on element type
        transform_keyword : str
            Keyword to use for transformation in arguments (default: 'transfTag')
            
        Returns:
        --------
        GeneralElement
            The created element
        """
        if tag is None:
            tag = self.next_element_id
        
        # Resolve node references if needed
        if isinstance(start_node, int):
            if start_node in self.nodes:
                start_node = self.nodes[start_node]
            else:
                raise ValueError(f"Node with ID {start_node} not found")
                
        if isinstance(end_node, int):
            if end_node in self.nodes:
                end_node = self.nodes[end_node]
            else:
                raise ValueError(f"Node with ID {end_node} not found")
        
        # Create element
        element = GeneralElement(tag, start_node, end_node, element_type,
                            structural_element_type, element_args, 
                            use_transformation, transform_type, transform_keyword)
        
        return self.add_element(element)

    def add_element(self, element: Element) -> Element:
        """
        Add an element to the model without creating it in OpenSees yet.
        
        Parameters:
        -----------
        element : Element
            Element to add
            
        Returns:
        --------
        Element
            The added element
        """
        self.elements[element.tag] = element
        
        # Update next element ID if needed
        if element.tag >= self.next_element_id:
            self.next_element_id = element.tag + 1
            
        # Add to element group
        if element.structural_type in self.element_groups:
            self.element_groups[element.structural_type].add(element.tag)
        else:
            self.parent._log(f"Element type '{element.structural_type}' not in predefined groups", level='warning')
            
        # Add to floor
        floor_level = element.floor_level()
        rounded_floor = self._find_nearest_floor_level(floor_level)
        
        if rounded_floor not in self.floors:
            self.floors[rounded_floor] = set()
            
        self.floors[rounded_floor].add(element.tag)
        
        self.parent._log(f"Added element {element}")
        return element
    
    def create_line_element(self, tag: int, start_node: Node | int, end_node: Node | int, 
                        element_type: str = None) -> Line:
        """
        USER FUNCTION
        Create a geometric line element without structural properties.
        
        This function creates a Line element that represents a geometric connection between
        two nodes, but doesn't have any structural analysis properties. Useful for visualization,
        boundaries, or geometric references.
        
        Parameters:
        -----------
        tag : int or None
            Element ID. If None, an ID is automatically assigned.
        start_node : Node or int
            Starting node object or node ID.
        end_node : Node or int
            Ending node object or node ID.
        element_type : str, optional
            Type identifier for the line element (default=None).
            
        Returns:
        --------
        Line
            The created line element.
            
        Raises:
        -------
        ValueError
            If a node ID is provided but not found in the model.
        """
        if tag is None:
            tag = self.next_element_id
        
        # Resolve node references if needed
        if isinstance(start_node, int):
            if start_node in self.nodes:
                start_node = self.nodes[start_node]
            else:
                raise ValueError(f"Node with ID {start_node} not found")
                
        if isinstance(end_node, int):
            if end_node in self.nodes:
                end_node = self.nodes[end_node]
            else:
                raise ValueError(f"Node with ID {end_node} not found")
        
        # Create line element
        element = Line(tag, start_node, end_node, element_type)
        
        return self.add_element(element)
    
    def convert_line_elements(self, section_mapping: dict[str, str], 
                            default_section: str = None,
                            element_class: str = "forceBeamColumn",
                            integration_tag: int = None) -> int:
        """
        USER FUNCTION
        Convert all line elements to beam-column elements using the provided mapping.
        
        This function transforms geometric Line elements into structural BeamColumn elements
        by assigning sections based on the provided mapping. Useful when building a model
        geometrically first and then assigning structural properties.
        
        Parameters:
        -----------
        section_mapping : dict[str, str]
            Dictionary mapping line element types to section names.
            Format: {element_type: section_name}
        default_section : str, optional
            Default section name to use for element types not in the mapping.
            If None, all element types must be in the section_mapping.
        element_class : str, optional
            Type of beam-column element to create (default="forceBeamColumn").
        integration_tag : int, optional
            Beam integration tag to use for the new elements (default=None).
            
        Returns:
        --------
        int
            Number of line elements successfully converted.
            
        Raises:
        -------
        ValueError
            If not all line element types have a mapping and no default_section is provided.
        """
        if default_section is None and not all(et in section_mapping for et in set(
                e.structural_type for e in self.elements.values() if isinstance(e, Line))):
            raise ValueError("Not all line element types have a section mapping and no default_section provided")
        
        converted = 0
        
        for element_id, element in list(self.elements.items()):
            if isinstance(element, Line):
                # Determine section name
                element_type = element.structural_type
                section_name = section_mapping.get(element_type, default_section)
                
                if section_name is None:
                    self.parent._log(f"Skipping conversion of line element {element_id} with type {element_type}: no section mapping", 
                            level="warning")
                    continue
                    
                # Convert to beam-column
                beam_column = element.convert_to_beam_column(section_name, element_class, integration_tag)
                
                # Replace in model
                self.elements[element_id] = beam_column
                converted += 1
        
        self.parent._log(f"Converted {converted} line elements to beam-column elements")
        return converted

    def add_to_element_group(self, element_id: int, group_name: str) -> bool:
        """
        Add an element to a group.
        
        Parameters:
        -----------
        element_id : int
            Element ID
        group_name : str
            Group name
            
        Returns:
        --------
        bool
            True if added, False otherwise
        """
        if element_id not in self.elements:
            self.parent._log(f"Element {element_id} not found", level='warning')
            return False
            
        if group_name not in self.element_groups:
            self.element_groups[group_name] = set()
            
        self.element_groups[group_name].add(element_id)
        self.parent._log(f"Added element {element_id} to group {group_name}")
        return True
    
    ### information gathering
    def find_node(self, x: float, y: float, z: float, tolerance: float = None) -> Node | None:
        """
        USER FUNCTION
        Find a node at the given coordinates within tolerance.
        
        Parameters:
        -----------
        x, y, z : float
            Coordinates to search for
        tolerance : float, optional
            Maximum distance to consider a match
            
        Returns:
        --------
        Node or None
            The found node, or None if not found
        """
        if tolerance is None:
            tolerance = self.parent.params['node_merge_tolerance']
            
        test_node = Node(-1, x, y, z)
        for node in self.nodes.values():
            if node.is_close_to(test_node, tolerance):
                self.parent._log(f"Found node {node} at ({x:.6f}, {y:.6f}, {z:.6f})")
                return node
        
        return None
    
    def has_line_elements(self) -> bool:
        """
        Check if the model has any unconverted line elements.
        
        Returns:
        --------
        bool
            True if model contains at least one Line element, False otherwise.
            Line elements are geometric entities without structural properties.
        """
        return any(isinstance(element, Line) for element in self.elements.values())

    def get_elements_by_group(self, group_name: str) -> list[Element]:
        """
        Get all elements in a group.
        
        Parameters:
        -----------
        group_name : str
            Name of the group
            
        Returns:
        --------
        List[Element]
            List of elements in the group
        """
        if group_name not in self.element_groups:
            self.parent._log(f"Group '{group_name}' not found", level='warning')
            return []
            
        return [self.elements[element_id] for element_id in self.element_groups[group_name] 
                if element_id in self.elements]
    
    def get_elements_by_floor(self, floor_level: float) -> list[Element]:
        """
        Get all elements at a floor level.
        
        Parameters:
        -----------
        floor_level : float
            Floor level
            
        Returns:
        --------
        List[Element]
            List of elements at the floor
        """
        rounded_floor = self._find_nearest_floor_level(floor_level)
        
        if rounded_floor not in self.floors:
            self.parent._log(f"Floor level {floor_level} not found", level='warning')
            return []
            
        return [self.elements[element_id] for element_id in self.floors[rounded_floor] 
                if element_id in self.elements]

    def check_free_nodes(self) -> list[int]:
        """
        Find nodes that are not connected to any elements.
        
        Returns:
        --------
        List[int]
            List of node IDs not used by any element
        """
        connected_nodes = set()
        
        for element in self.elements.values():
            if isinstance(element.start_node, Node):
                connected_nodes.add(element.start_node.tag)
            else:
                connected_nodes.add(element.start_node)
                
            if isinstance(element.end_node, Node):
                connected_nodes.add(element.end_node.tag)
            else:
                connected_nodes.add(element.end_node)
            
        all_nodes = set(self.nodes.keys())
        free_nodes = all_nodes - connected_nodes
        
        return list(free_nodes)

    def check_duplicate_nodes(self, tolerance: float = None) -> list[tuple[int, int]]:
        """
        Find pairs of nodes that are very close to each other.
        
        Parameters:
        -----------
        tolerance : float, optional
            Maximum distance to consider nodes as duplicates
            
        Returns:
        --------
        List[Tuple[int, int]]
            List of pairs of node IDs that are duplicates
        """
        if tolerance is None:
            tolerance = self.parent.params['node_merge_tolerance']
            
        duplicate_pairs = []
        nodes_list = list(self.nodes.values())
        
        for i in range(len(nodes_list)):
            for j in range(i+1, len(nodes_list)):
                if nodes_list[i].is_close_to(nodes_list[j], tolerance):
                    duplicate_pairs.append((nodes_list[i].tag, nodes_list[j].tag))
                    
        return duplicate_pairs
    
    def check_duplicate_elements(self) -> list[tuple[int, int]]:
        """
        Find pairs of elements that connect the same nodes.
        
        Returns:
        --------
        List[Tuple[int, int]]
            List of pairs of element IDs that connect the same nodes
        """
        duplicate_pairs = []
        elements_list = list(self.elements.values())
        
        for i in range(len(elements_list)):
            for j in range(i+1, len(elements_list)):
                elem1 = elements_list[i]
                elem2 = elements_list[j]
                
                start1 = elem1.get_start_node().tag if isinstance(elem1.start_node, Node) else elem1.start_node
                end1 = elem1.get_end_node().tag if isinstance(elem1.end_node, Node) else elem1.end_node
                start2 = elem2.get_start_node().tag if isinstance(elem2.start_node, Node) else elem2.start_node
                end2 = elem2.get_end_node().tag if isinstance(elem2.end_node, Node) else elem2.end_node
                
                # Check if both elements connect the same nodes
                if ((start1 == start2 and end1 == end2) or
                    (start1 == end2 and end1 == start2)):
                    duplicate_pairs.append((elem1.tag, elem2.tag))
                    
        return duplicate_pairs

    def _find_nearest_floor_level(self, z: float) -> float:
        """
        Round a Z coordinate to the nearest floor level.
        
        Parameters:
        -----------
        z : float
            Z coordinate to round
            
        Returns:
        --------
        float
            Nearest floor level
        """
        if not self.floors:
            return z
            
        # Find the closest existing floor level
        closest_floor = None
        min_dist = float('inf')
        
        for floor_level in self.floors:
            dist = abs(z - floor_level)
            if dist < min_dist and dist < self.parent.params['floor_height_tolerance']:
                min_dist = dist
                closest_floor = floor_level
                
        if closest_floor is not None:
            return closest_floor
            
        return z

    ### manipulate geometry            
    def translate_structure(self, dx: float = 0, dy: float = 0, dz: float = 0):
        """
        Translate the entire structure.
        
        Parameters:
        -----------
        dx, dy, dz : float
            Translation distances
            
        Returns:
        --------
        StructuralModel
            The model (for chaining)
        """
        if self.parent._model_built:
            raise RuntimeError("Cannot modify structure after OpenSees model has been built")
            
        for node in self.nodes.values():
            node.translate(dx, dy, dz)
            
        self.parent._log(f"Translated structure by ({dx}, {dy}, {dz})")
        return self
    
    def rotate_structure_about_z(self, angle_degrees: float, center_x: float = 0, center_y: float = 0):
        """
        Rotate the entire structure around the Z axis.
        
        Parameters:
        -----------
        angle_degrees : float
            Rotation angle in degrees
        center_x, center_y : float
            Center of rotation
            
        Returns:
        --------
        StructuralModel
            The model (for chaining)
        """
        if self.parent._model_built:
            raise RuntimeError("Cannot modify structure after OpenSees model has been built")
            
        for node in self.nodes.values():
            node.rotate_about_z(angle_degrees, center_x, center_y)
            
        self.parent._log(f"Rotated structure by {angle_degrees} degrees around Z axis at ({center_x}, {center_y})")
        return self

    def subdivide_element(self, element_id: int, num_segments: int) -> list[int]:
        """
        Subdivide an element into multiple segments.
        
        Parameters:
        -----------
        element_id : int
            ID of the element to subdivide
        num_segments : int
            Number of segments to create
            
        Returns:
        --------
        List[int]
            IDs of the new elements
        """
        if self.parent._model_built:
            raise RuntimeError("Cannot subdivide elements after OpenSees model has been built")
            
        if element_id not in self.elements or num_segments < 2:
            self.parent._log(f"Element {element_id} not found or invalid number of segments", level='warning')
            return []
            
        element = self.elements[element_id]
        element_structural_type = element.structural_type
        
        # Get properties of the element
        start_node = element.get_start_node()
        end_node = element.get_end_node()
        
        # Create intermediate nodes
        new_nodes = []
        
        for i in range(1, num_segments):
            t = i / num_segments
            x = start_node.x + t * (end_node.x - start_node.x)
            y = start_node.y + t * (end_node.y - start_node.y)
            z = start_node.z + t * (end_node.z - start_node.z)
            
            new_node = self.create_node(None, x, y, z)
            new_nodes.append(new_node)
        
        # Create new elements
        new_element_ids = []
        prev_node = start_node
        
        # Handle different element types
        if isinstance(element, Line):
            # For Line elements, create new Line elements
            for node in new_nodes:
                new_element = self.create_line_element(
                    None, prev_node, node, element_structural_type
                )
                new_element_ids.append(new_element.tag)
                prev_node = node
            
            # Create last segment
            new_element = self.create_line_element(None, prev_node, end_node, element_structural_type)
            new_element_ids.append(new_element.tag)
            
        elif isinstance(element, BeamColumn):
            # For BeamColumn elements, preserve additional properties
            section_name = element.section_name
            element_class = element.element_class
            integration_tag = element.integration_tag
            element_args = element.element_args
            
            for node in new_nodes:
                new_element = self.create_element(
                    None, prev_node, node, element_structural_type, section_name,
                    element_class, integration_tag, element_args
                )
                new_element_ids.append(new_element.tag)
                prev_node = node
            
            # Create last segment
            new_element = self.create_element(
                None, prev_node, end_node, element_structural_type, section_name,
                element_class, integration_tag, element_args
            )
            new_element_ids.append(new_element.tag)
        
        elif isinstance(element, GeneralElement):
            # For GeneralElement, preserve all properties
            element_type = element.element_type
            element_args = element.element_args
            use_transformation = element.use_transformation
            transform_type = element.transform_type
            transform_keyword = element.transform_keyword
            
            for node in new_nodes:
                new_element = self.create_general_element(
                    None, prev_node, node, element_type, element_structural_type,
                    element_args, use_transformation, transform_type, transform_keyword
                )
                new_element_ids.append(new_element.tag)
                prev_node = node
            
            # Create last segment
            new_element = self.create_general_element(
                None, prev_node, end_node, element_type, element_structural_type,
                element_args, use_transformation, transform_type, transform_keyword
            )
            new_element_ids.append(new_element.tag)
        
        else:
            # Handle any other element types that might be added in the future
            raise TypeError(f"Subdivision not implemented for element type {type(element).__name__}")
        
        # Remove the original element
        self.remove_element(element_id)
        
        self.parent._log(f"Subdivided element {element_id} into {num_segments} segments")
        return new_element_ids

    def remove_node(self, node_id: int) -> bool:
        """
        Remove a node from the model.
        
        Parameters:
        -----------
        node_id : int
            ID of the node to remove
            
        Returns:
        --------
        bool
            True if successfully removed, False otherwise
        
        Raises:
        -------
        RuntimeError
            If attempting to remove a node after the model has been built
            or if the node is still used by elements
        """
        if self.parent._model_built and not self.parent._is_forced_released:
            raise RuntimeError("Cannot remove nodes after OpenSees model has been built")
            
        if node_id not in self.nodes:
            self.parent._log(f"Node {node_id} not found for removal", level='warning')
            return False
            
        # Check if node is used by any elements
        for element_id, element in self.elements.items():
            start_node_id = element.start_node.tag if isinstance(element.start_node, Node) else element.start_node
            end_node_id = element.end_node.tag if isinstance(element.end_node, Node) else element.end_node
            
            if node_id == start_node_id or node_id == end_node_id:
                raise RuntimeError(f"Cannot remove node {node_id} because it is used by element {element_id}")
        
        # Remove node from any constraints
        if node_id in self.parent.constraints.constraints:
            del self.parent.constraints.constraints[node_id]
            self.parent._log(f"Removed constraint at node {node_id}")
        
        # Remove node from the collection
        removed_node = self.nodes.pop(node_id)
        self.parent._log(f"Removed node {node_id}")
        
        return True

    def remove_element(self, element_id: int) -> bool:
        """Remove an element from the model."""
        if self.parent._model_built and not self.parent._is_forced_released:
            raise RuntimeError("Cannot remove elements after OpenSees model has been built")

        if element_id not in self.elements:
            self.parent._log(f"Element {element_id} not found for removal", level='warning')
            return False
            
        element = self.elements[element_id]
        
        # Remove from element groups
        for group in self.element_groups.values():
            group.discard(element_id)
            
        # Remove from floors
        floor_level = self._find_nearest_floor_level(element.floor_level())
        if floor_level in self.floors:
            self.floors[floor_level].discard(element_id)
            
        del self.elements[element_id]
        self.parent._log(f"Removed element {element_id}")
        return True
    
    def remove_free_nodes(self) -> int:
        """
        Remove nodes that are not connected to any elements.
        
        Returns:
        --------
        int
            Number of nodes removed
        """
        if self.parent._model_built and not self.parent._is_forced_released:
            raise RuntimeError("Cannot remove nodes after OpenSees model has been built")
            
        free_nodes = self.check_free_nodes()
        
        # Remove free nodes
        for node_id in free_nodes:
            del self.nodes[node_id]
            
            # Remove from constraints if present
            if node_id in self.parent.constraints.constraints:
                del self.parent.constraints.constraints[node_id]
                
        self.parent._log(f"Removed {len(free_nodes)} free nodes")
        return len(free_nodes)

    ### automatic structure (geometry) creation
    def create_grid(self, x_coords: list[float], y_coords: list[float], z_coords: list[float],
                create_columns: bool = True, create_beams: bool = True, 
                column_type: str = "column", beam_x_type: str = "beam_x", 
                beam_y_type: str = "beam_y") -> dict[str, int]:
        """
        Create a 3D grid of nodes and geometric line elements.
        
        Parameters:
        -----------
        x_coords, y_coords, z_coords : List[float]
            Coordinates defining the grid points
        create_columns, create_beams : bool
            Whether to create column and beam elements
        column_type, beam_x_type, beam_y_type : str
            Element type identifiers for columns and beams
            
        Returns:
        --------
        dict[str, int]
            Dictionary with counts of created nodes and elements
        """
        if self.parent._model_built:
            raise RuntimeError("Cannot create grid after OpenSees model has been built")
            
        # Grid node mapping (x,y,z) -> node_id
        grid_nodes = {}
        
        # Create nodes at grid intersections
        for z in z_coords:
            for y in y_coords:
                for x in x_coords:
                    # Check if node already exists
                    existing_node = self.find_node(x, y, z)
                    if existing_node:
                        grid_nodes[(x, y, z)] = existing_node.tag
                    else:
                        node = self.create_node(None, x, y, z)
                        grid_nodes[(x, y, z)] = node.tag
        
        elements_created = 0
        
        # Create column elements
        if create_columns:
            for x in x_coords:
                for y in y_coords:
                    for i in range(len(z_coords) - 1):
                        start_node_id = grid_nodes[(x, y, z_coords[i])]
                        end_node_id = grid_nodes[(x, y, z_coords[i+1])]
                        # Create geometric line element instead of structural element
                        self.create_line_element(None, start_node_id, end_node_id, column_type)
                        elements_created += 1
        
        # Create beam elements
        if create_beams:
            for z in z_coords:
                # X-direction beams
                for y in y_coords:
                    for i in range(len(x_coords) - 1):
                        start_node_id = grid_nodes[(x_coords[i], y, z)]
                        end_node_id = grid_nodes[(x_coords[i+1], y, z)]
                        # Create geometric line element
                        self.create_line_element(None, start_node_id, end_node_id, beam_x_type)
                        elements_created += 1
                
                # Y-direction beams
                for x in x_coords:
                    for i in range(len(y_coords) - 1):
                        start_node_id = grid_nodes[(x, y_coords[i], z)]
                        end_node_id = grid_nodes[(x, y_coords[i+1], z)]
                        # Create geometric line element
                        self.create_line_element(None, start_node_id, end_node_id, beam_y_type)
                        elements_created += 1
        
        self.parent._log(f"Created grid with {len(grid_nodes)} nodes and {elements_created} geometric line elements")
        return {
            'nodes_created': len(grid_nodes),
            'elements_created': elements_created
        }

