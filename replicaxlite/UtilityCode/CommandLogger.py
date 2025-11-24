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


from ..config import INFO
import inspect
from functools import wraps


class CommandLogger:
    def __init__(self, log_file: str, prefix_obj: str="obj", commands_to_include: list[str]=None, header_to_include: str=None, commands_with_return: list[str]=None):
        """
        Initialize the command logger
        
        Args:
            log_file: Path to the log file
            prefix_obj: Prefix for the main object (default: "obj")
            commands_to_include: List of method names to log (if None, logs all)
            header_to_include: Header text to include at the start of the log file
            commands_with_return: List of method names that return data
        """
        self.log_file = log_file
        self.commands_to_include = commands_to_include or []
        self.header_to_include = header_to_include or ""
        self.commands_with_return = commands_with_return or []
        self.prefix_obj = prefix_obj
        self.visited_objects = set()
        self._initialize_log_file()
    
    def _initialize_log_file(self):
        """Create and initialize the log file with header"""
        with open(self.log_file, 'w') as f:
            f.write("### ------------------------------------------------------------------------------------- ###\n")
            f.write(f"# This code was automatically generated with ReplicaXLite version {INFO['version']}         #\n")
            f.write("### ------------------------------------------------------------------------------------- ###\n\n")
            f.write(self.header_to_include)
    
    def user_line_code_insert(self, code):
        with open(self.log_file, 'a') as f:
            f.write(code+"\n")

    def _log_command(self, func, prefix_obj):
        """Decorator to log function calls"""
        @wraps(func)
        def wrapper(*args, **kwargs):
            func_name = func.__name__
            
            # Only log if in include list (or if include list is empty)
            if not self.commands_to_include or func_name in self.commands_to_include:
                args_str = ', '.join(repr(arg) for arg in args)
                kwargs_str = ', '.join(f"{k}={repr(v)}" for k, v in kwargs.items())
                all_args = args_str
                if kwargs_str:
                    if args_str:
                        all_args += ', ' + kwargs_str
                    else:
                        all_args = kwargs_str
                
                command = f"{prefix_obj}.{func_name}({all_args})"

                # Check for return value prefix
                command_with_return = self.commands_with_return.get(func_name)
                if command_with_return:
                    command = f"{command_with_return} = {command}"
                
                with open(self.log_file, 'a') as f:
                    f.write(f"{command}\n")
            
            return func(*args, **kwargs)
        
        return wrapper
    
    def _wrap_object(self, obj, prefix_obj):
        """Recursively wrap methods on an object and its attributes"""
        # Check if we've already visited this object
        obj_id = id(obj)
        if obj_id in self.visited_objects:
            return
        
        # Mark this object as visited
        self.visited_objects.add(obj_id)
        
        # Skip modules entirely
        if inspect.ismodule(obj):
            return
        
        # Optional: Only wrap objects from replicaxlite package
        obj_module = getattr(obj.__class__, '__module__', '')
        if not obj_module.startswith('replicaxlite'):
            return
        
        try:
            members = inspect.getmembers(obj)
        except Exception:
            # If getmembers fails, skip this object
            return
        
        for name, attr in members:
            if name.startswith('_'):  # Skip private/magic methods
                continue
            
            # Skip modules
            if inspect.ismodule(attr):
                continue
                
            if inspect.ismethod(attr):
                try:
                    setattr(obj, name, self._log_command(attr, prefix_obj))
                except (AttributeError, TypeError):
                    pass  # Can't set attribute, skip it
            elif isinstance(attr, dict):
                # Wrap dictionary values
                for key, value in attr.items():
                    if hasattr(value, '__dict__') and not inspect.isclass(value) and not inspect.ismodule(value):
                        self._wrap_object(value, f"{prefix_obj}.{name}[{repr(key)}]")
            elif hasattr(attr, '__dict__') and not inspect.isclass(attr) and not inspect.ismodule(attr):
                # Recursively wrap nested objects
                self._wrap_object(attr, f"{prefix_obj}.{name}")
    
    def wrap_dict_item(self, obj, key, dict_name, parent_prefix):
        """
        Wrap a single item that was added to a dictionary after initial wrapping
        
        Args:
            obj: The object to wrap (e.g., a node)
            key: The dictionary key (e.g., node_tag)
            dict_name: Name of the dictionary (e.g., "nodes")
            parent_prefix: Prefix of the parent object (e.g., "model.geometry")
        """
        prefix = f"{parent_prefix}.{dict_name}[{repr(key)}]"
        self._wrap_object(obj, prefix)
    
    class LoggedDict(dict):
        """Dictionary that automatically wraps items when they are added"""
        def __init__(self, logger, parent_prefix, dict_name, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.logger = logger
            self.parent_prefix = parent_prefix
            self.dict_name = dict_name
        
        def __setitem__(self, key, value):
            """Override to wrap items when they're added to the dictionary"""
            # First add to dict using parent class method
            super().__setitem__(key, value)
            
            # Then wrap it if it's an object with methods
            if hasattr(value, '__dict__') and not inspect.isclass(value):
                prefix = f"{self.parent_prefix}.{self.dict_name}[{repr(key)}]"
                self.logger._wrap_object(value, prefix)
    
    def wrap_dict(self, parent_obj, dict_attr_name, parent_prefix):
        """
        Replace a dictionary attribute with an auto-wrapping LoggedDict
        
        Args:
            parent_obj: The parent object containing the dictionary
            dict_attr_name: Name of the dictionary attribute (e.g., "nodes")
            parent_prefix: Prefix for the parent object (e.g., "model.geometry")
        
        Example:
            logger.wrap_dict(model.geometry, "nodes", "model.geometry")
        """
        # Get the original dictionary
        original_dict = getattr(parent_obj, dict_attr_name)
        
        # Create LoggedDict with all existing items copied
        logged_dict = self.LoggedDict(
            self, 
            parent_prefix, 
            dict_attr_name, 
            original_dict  # This copies all existing key-value pairs
        )
        
        # Replace the attribute with our LoggedDict
        setattr(parent_obj, dict_attr_name, logged_dict)
        
        # Wrap all existing items that were in the original dict
        for key, value in logged_dict.items():
            if hasattr(value, '__dict__') and not inspect.isclass(value):
                prefix = f"{parent_prefix}.{dict_attr_name}[{repr(key)}]"
                self._wrap_object(value, prefix)
    
    def wrap(self, obj):
        """
        Wrap an object to log its method calls
        
        Args:
            obj: The object to wrap
        
        Returns:
            The wrapped object (same object, with methods wrapped)
        """
        self._wrap_object(obj, self.prefix_obj)
        return obj
