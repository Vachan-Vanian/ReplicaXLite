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


import json
import ast

class ReplicaXDataTypesManager:
    """
    A class for validating and converting data between different types.
    
    *Note*: This class performs strict type checking using isinstance().
    For numeric types, it strictly distinguishes between integers and floats.
    A list of integers will not validate as a list of floats, and vice versa
    """
    def __init__(self):
        self.type_checkers = {
            'str': self.is_str,
            'int': self.is_int,
            'float': self.is_float,
            'bool': self.is_bool,
            'list': self.is_list,
            'list(int)': self.is_list_int,
            'list(float)': self.is_list_float,
            'list(bool)': self.is_list_bool,
            'list(str)': self.is_list_str,
            'dict': self.is_dict
        }

### THIS PART IS FOR FURTHER DEVELOPMENET NEED WHEN AND IF NEEDED
        # Add support for structured type definitions
        # self.register_structured_types()
    
    # def register_structured_types(self):
    #     """Register validators for structured types."""
    #     # You can add more pre-defined structures here
    #     self.type_checkers['list(bool,float,dict)'] = lambda x: self.is_structured_list(x, ['bool', 'float', 'dict'])
    #     self.type_checkers['list(str,int,list)'] = lambda x: self.is_structured_list(x, ['str', 'int', 'list'])
        
    #     # Dictionary structures with specific key types
    #     self.type_checkers['dict(name:str,age:int,scores:list(float))'] = lambda x: self.is_structured_dict(
    #         x, {'name': 'str', 'age': 'int', 'scores': 'list(float)'}
    #     )
    
    ### THIS IS FOR ON THE FLY ADDITION OF NEEDED DATA TYPES
    # BUT prefer to have fixed costum types that will initialy populated 
    # by activating the 'register_structured_types' function
    def register_custom_structure(self, type_name, structure_def):
        """
        Register a custom structured type validator.
        
        Args:
            type_name (str): A unique name for this structured type
            structure_def (list or dict): Definition of the structure
                - If list: List of type names in order
                - If dict: Dict mapping keys to their expected types
        """
        if isinstance(structure_def, list):
            self.type_checkers[type_name] = lambda x: self.is_structured_list(x, structure_def)
        elif isinstance(structure_def, dict):
            self.type_checkers[type_name] = lambda x: self.is_structured_dict(x, structure_def)
        else:
            raise ValueError(f"Invalid structure definition. Must be list or dict, got {type(structure_def)}")
        
        return type_name  # Return the registered type name for convenience
    
    def save_data_type_as_string(self, ditem, dtype):
        """
        Validate data against a specified type and return it as a string representation.
        
        This method ensures the data conforms to the specified type, and then converts
        it to an appropriate string representation:
        - Strings remain as strings
        - Numbers and booleans are converted with str()
        - Lists and dictionaries are converted to JSON strings
        
        Args:
            ditem: The data item to validate and convert to string
            dtype (str): The target data type name (e.g., 'int', 'list(float)', 'dict')
        
        Returns:
            str: The string representation of the validated data
        
        Raises:
            ValueError: If the data cannot be validated/converted to the specified type,
                        or if the specified type is not supported
        
        Examples:
            >>> manager = ReplicaXDataTypesManager()
            >>> manager.save_data_type_as_string(123, "int")
            '123'
            >>> manager.save_data_type_as_string([1, 2, 3], "list")
            '[1, 2, 3]'
            >>> manager.save_data_type_as_string({"name": "John"}, "dict")
            '{"name": "John"}'
            
            # For structured data:
            >>> manager.register_custom_structure("user", {"id": "int", "active": "bool"})
            >>> manager.save_data_type_as_string({"id": 100, "active": True}, "user")
            '{"id": 100, "active": true}'
        """
        data = self.load_data_type(ditem, dtype, load_only=False)
        if data[0]:
            if data[2] == "str":
                return data[1]
            elif data[2] in ["int", "float", "bool"]:
                return str(data[1])
            elif data[2] == "dict" or data[2].startswith("list"):
                return json.dumps(data[1])
            else:
                raise ValueError(f"Unsupported data type: {data[2]}")
        else:
            raise ValueError(f"Failed to save data as string:\ndatatype= {dtype}\ndata= {ditem}")

    def save_data_type(self, ditem, dtype):
        """
        Validate data against a specified type and return the validated Python objects.
        
        This method ensures the data conforms to the specified type, converting it if necessary.
        Unlike `load_data_type`, this method always raises an error if validation fails.
        
        Args:
            ditem: The data item to validate and potentially convert
            dtype (str): The target data type name (e.g., 'int', 'list(float)', 'dict')
        
        Returns:
            The validated and potentially converted data in its native Python form
        
        Raises:
            ValueError: If the data cannot be validated/converted to the specified type,
                        or if the specified type is not supported
        
        Examples:
            >>> manager = ReplicaXDataTypesManager()
            >>> manager.save_data_type(123, "int")
            123
            >>> manager.save_data_type("123", "int")  # String converted to int
            123
            >>> manager.save_data_type({"id": "100", "active": "true"}, "dict")
            {'id': '100', 'active': 'true'}  # Simple dict validation without conversion
            
            # For structured dictionaries with specific key types:
            >>> manager.register_custom_structure("user", {"id": "int", "active": "bool"})
            >>> manager.save_data_type({"id": "100", "active": "true"}, "user")
            {'id': 100, 'active': True}  # Note the type conversions
        """
        data = self.load_data_type(ditem, dtype, load_only=False)
        if data[0]:
            return data[1]
        else:
            raise ValueError(f"Failed to save data:\ndatatype= {dtype}\ndata= {ditem}")

    def load_data_type(self, ditem, dtype, load_only=True):
        """
        Validate and convert data to the specified type.
        
        This is the core method used by both `save_data_type` and `save_data_type_as_string`.
        It attempts to validate and convert the provided data to the specified type.
        
        Args:
            ditem: The data item to validate and convert
            dtype (str): The target data type name (e.g., 'int', 'list(float)', 'dict')
            load_only (bool): Controls the return value:
                - If True (default): Returns only the converted value
                - If False: Returns a tuple of (success_bool, converted_value, type_name)
        
        Returns:
            If load_only=True: The converted value
            If load_only=False: Tuple of (success_bool, converted_value, type_name)
        
        Raises:
            ValueError: If the data cannot be validated/converted to the specified type,
                        or if the specified type is not supported
        
        Examples:
            >>> manager = ReplicaXDataTypesManager()
            >>> manager.load_data_type("123", "int")
            123
            >>> manager.load_data_type("not a number", "int")
            ValueError: Failed to load data: datatype= int, data= not a number
            
            # With load_only=False (used internally)
            >>> manager.load_data_type("123", "int", load_only=False)
            (True, 123, 'int')
        """
        checker = self.type_checkers.get(dtype)
        if not checker:
            raise ValueError(f"Unsupported data type: {dtype}")
        
        result = checker(ditem)
        if result[0]:
            if load_only:
                return result[1]
            else:
                return result
        else:
            raise ValueError(f"Failed to load data:\ndatatype= {dtype}\ndata= {ditem}")

    def is_str(self, ditem):
        try:
            return isinstance(ditem, str), ditem, 'str'
        except:
            return False, None, None

    def is_int(self, ditem):
        """
        Check if the data item is an integer or can be converted to an integer.
        
        Note: This method intentionally distinguishes between integers and floats.
        Float values (e.g., 123.0) will return False, while integer values (e.g., 123)
        will return True. This is to maintain strict type differentiation when needed.
        
        Args:
            ditem: Data item to check
            
        Returns:
            Tuple of (bool success, converted value if successful, type name)
        """
        try:
            if isinstance(ditem, float):
                return False, None, None
            return True, int(ditem), 'int'
        except ValueError:
            return False, None, None
    
    def is_float(self, ditem):
        """
        Check if the data item is a float or can be converted to a float.
        
        Note: This method intentionally distinguishes between integers and floats.
        Integer values (e.g., 123) will return False, while float values (e.g., 123.0)
        will return True. This is to maintain strict type differentiation when needed.
        
        Args:
            ditem: Data item to check
            
        Returns:
            Tuple of (bool success, converted value if successful, type name)
        """
        try:
            if isinstance(ditem, int):
                return False, None, None
            return True, float(ditem), 'float'
        except ValueError:
            return False, None, None
    
    def is_bool(self, ditem):
        if isinstance(ditem, bool):
            return True, ditem, 'bool'
        if isinstance(ditem, str) and ditem.lower() in ('true', 'false'):
            return True, ditem.lower() == 'true', 'bool'
        return False, None, None
          
    def is_list(self, ditem):
        if isinstance(ditem, list):
            return True, ditem, 'list'
        try:
            list_data = None
            try:
                list_data = json.loads(ditem)
            except:
                pass
            try:
                if list_data is None:
                    list_data = ast.literal_eval(ditem)
            except:
                pass
            if isinstance(list_data, list):
                return True, list_data, 'list'
        except:
            pass
        return False, None, None
    
    def _check_list_type(self, ditem, type_checker):
        """
        Check if all items in the list are of a specific type or can be converted to it.
        
        This method now attempts to convert items to the target type using the
        appropriate type checker method, maintaining consistency with single-value
        type checking behavior.
        
        Args:
            ditem: List to check or string representation of a list
            type_checker: Type to check against (e.g., int, float, bool, str)
            
        Returns:
            Tuple of (bool success, converted list if successful, type name)
        """
        try:
            jlist = None
            if isinstance(ditem, list):
                jlist = ditem
            else:
                try:
                    jlist = json.loads(ditem)
                except:
                    pass
                try:
                    if jlist is None:
                        jlist = ast.literal_eval(ditem)
                except:
                    pass
            
            if jlist is not None:
                type_name = type_checker.__name__  # 'int', 'float', 'bool', 'str'
                
                # Get the appropriate type checker method
                type_checker_method = self.type_checkers.get(type_name)
                if not type_checker_method:
                    return False, None, None
                
                # Convert each item using the type checker
                converted_list = []
                for item in jlist:
                    result = type_checker_method(item)
                    if not result[0]:  # Conversion failed
                        return False, None, None
                    converted_list.append(result[1])
                
                return True, converted_list, f'list({type_name})'
            
            return False, None, None
        except:
            return False, None, None    


    def is_list_int(self, ditem):
        return self._check_list_type(ditem, int)
        
    def is_list_float(self, ditem):
        return self._check_list_type(ditem, float)
    
    def is_list_bool(self, ditem):
        return self._check_list_type(ditem, bool)

    def is_list_str(self, ditem):
        return self._check_list_type(ditem, str)
    
    def is_dict(self, ditem):
        if isinstance(ditem, dict):
            return True, ditem, 'dict'
        try:
            dict_data = None
            try:
                dict_data = json.loads(ditem)
            except:
                pass
            try:
                if dict_data is None:
                    dict_data = ast.literal_eval(ditem)
            except:
                pass
            if isinstance(dict_data, dict):
                return True, dict_data, 'dict'
        except:
            pass
        return False, None, None
    
    # Validate complex data structures:
    # Validate: list(int,bool,str) or dict(name:str,age:int) etc.
    def is_structured_list(self, ditem, expected_types):
        """
        Validate that a list contains specific types in a specific order.
        
        Note: This method performs strict type checking for all values.
        For numeric types, it strictly distinguishes between integers and floats.
        A list of integers will not validate as a list of floats, and vice versa.
        
        Args:
            ditem: The data item to validate
            expected_types: List of type names in expected order
            
        Returns:
            Tuple of (bool success, data if successful, type name)
        """
        # First ensure it's a list
        list_result = self.is_list(ditem)
        if not list_result[0]:
            return False, None, None
            
        data_list = list_result[1]
        
        # Check length
        if len(data_list) != len(expected_types):
            return False, None, None
            
        # Check each item matches the expected type
        for i, (item, expected_type) in enumerate(zip(data_list, expected_types)):
            checker = self.type_checkers.get(expected_type)
            if not checker:
                # Unknown type in the expected_types list
                return False, None, None
                
            item_check = checker(item)
            if not item_check[0]:
                # This item doesn't match the expected type
                return False, None, None
                
            # Replace the item with the processed value
            data_list[i] = item_check[1]
            
        # All checks passed
        type_name = f"list({','.join(expected_types)})"
        return True, data_list, type_name
    
    def is_structured_dict(self, ditem, expected_keys_types):
        """
        Validate that a dict contains specific keys with specific types.
        
        Note: This method performs strict type checking for all values.
        For numeric types, it strictly distinguishes between integers and floats.
        A list of integers will not validate as a list of floats, and vice versa.
        
        Args:
            ditem: The data item to validate
            expected_keys_types: Dict mapping keys to their expected types
            
        Returns:
            Tuple of (bool success, data if successful, type name)
        """
        # First ensure it's a dict
        dict_result = self.is_dict(ditem)
        if not dict_result[0]:
            return False, None, None
            
        data_dict = dict_result[1]
        
        # Check all required keys exist
        for key in expected_keys_types:
            if key not in data_dict:
                return False, None, None
                
        # Check each value matches the expected type
        for key, expected_type in expected_keys_types.items():
            checker = self.type_checkers.get(expected_type)
            if not checker:
                # Unknown type in the expected_types dict
                return False, None, None
                
            value_check = checker(data_dict[key])
            if not value_check[0]:
                # This value doesn't match the expected type
                return False, None, None
                
            # Replace the value with the processed value
            data_dict[key] = value_check[1]
            
        # All checks passed
        # Create a type name like "dict(name:str,age:int)"
        type_parts = [f"{k}:{v}" for k, v in expected_keys_types.items()]
        type_name = f"dict({','.join(type_parts)})"
        return True, data_dict, type_name

    