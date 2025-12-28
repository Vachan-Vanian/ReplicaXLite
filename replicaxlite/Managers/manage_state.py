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
import json
import copy
from pathlib import Path
from collections import OrderedDict
from PySide6.QtWidgets import QMessageBox
from ..config import INFO, SETTINGS
from ..StructuralAPI import StructuralModel



class ProjectStructure:
    """Defines and manages the project folder structure"""
    
    def __init__(self, manager):
        self.manager = manager
        self.structure = OrderedDict({
            ".opstool.output": {},
            "ModelData": {
                "fem_tables": {}
            },
            "ResultData": {},
            "UserData": {
                "Sensors": {}
            }
        })
    
    def create_structure(self, base_folder):
        """Create the project folder structure"""
        def create_recursive(folder, structure):
            os.makedirs(folder, exist_ok=True)
            for name, content in structure.items():
                path = (Path(folder) / name).as_posix()
                if callable(content):
                    # It's a file - call the export function
                    content(path)
                elif isinstance(content, dict):
                    # It's a folder - recurse
                    create_recursive(path, content)
        
        create_recursive(base_folder, self.structure)
    
    def validate_structure(self, base_folder):
        """Validate that the folder has correct project structure"""
        def validate_recursive(folder, structure):
            for name, content in structure.items():
                path = (Path(folder) / name).as_posix()
                if callable(content):
                    # Should be a file
                    if not os.path.isfile(path):
                        return False
                elif isinstance(content, dict):
                    # Should be a folder
                    if not os.path.isdir(path) or not validate_recursive(path, content):
                        return False
            return True
        
        return validate_recursive(base_folder, self.structure)


class ReplicaXProjectManager:
    """Manages project creation, opening, saving, and closing"""
    
    def __init__(self, parent):
        self.parent = parent
        self.settings = self.parent.settings
        self.dialog = self.parent.dialog_helper  # DialogHelper instance
        self.status_bar = self.parent.statusbar_helper
        self.manage_fem_table = self.parent.manage_fem_table

        self.project_structure = ProjectStructure(self)
        
        # State tracking
        self.current_project_folder_path = None
    
    # ==================== Core Project Operations ====================
    
    def create_project(self):
        """Create a new project"""
        try:
            # Get project name
            project_name, ok = self.dialog.get_text("Create New Project", "Enter project name:")
            
            if not ok or not project_name:
                return
            
            # Select parent folder
            parent_folder = self.dialog.get_directory("Select Parent Folder", str(Path.home()))
            
            if not parent_folder:
                return
            
            # Create project folder
            project_folder = (Path(parent_folder) / project_name).as_posix()
            
            if os.path.exists(project_folder):
                self.dialog.show_warning("Project Exists", f"A folder named '{project_name}' already exists in this location.")
                return
            
            # Create structure
            os.makedirs(project_folder, exist_ok=True)
            self.project_structure.create_structure(project_folder)
            
            # reset project if opened
            self._reset_project()

            # Initialize project
            self._initialize_project(project_folder)
            self._save_project_data()

            
            self.dialog.show_info("Project Created", f"Project '{project_name}' created successfully!")
            self.status_bar.update_message(f"Project '{project_name}' created successfully!", 5000)
            
        except Exception as e:
            self.dialog.show_error("Error Creating Project", f"Failed to create project:\n{str(e)}")
   
    def open_project(self):
        """Open an existing project"""
        try:
            # Select project folder
            project_folder = self.dialog.get_directory("Open Project", str(Path.home()))
            
            if not project_folder:
                return
            
            # Validate structure
            if not self.project_structure.validate_structure(project_folder):
                self.dialog.show_warning("Invalid Project", "The selected folder is not a valid ReplicaXLite project.")
                return
            
            # reset project if opened
            self._reset_project()

            # Load project
            self._initialize_project(project_folder)
            self._load_project_data()          
            
            self.dialog.show_info("Project Opened", "Project opened successfully!")
            self.status_bar.update_message("Project opened successfully!", 5000)
            
        except Exception as e:
            self.dialog.show_error("Error Opening Project", f"Failed to open project:\n{str(e)}")
    
    def save_project(self):
        """Save the current project"""
        try:
            if not self.current_project_folder_path:
                self.dialog.show_warning("No Project Open", "No project is currently open.")
                return
            
            self._save_project_data()
            
            self.dialog.show_info("Project Saved", "Project saved successfully!")
            self.status_bar.update_message("Project saved successfully!", 5000)
            
        except Exception as e:
            self.dialog.show_error("Error Saving Project", f"Failed to save project:\n{str(e)}")
    
    def close_project(self):
        """Close the current project"""
        try:

            if not self.current_project_folder_path:
                self.dialog.show_info("No Project Open", "No project is currently open.")
                return       
            # Reset state
            self.current_project_folder_path = None
            self.settings["_project"]["project_folder"] = ""
            
            # reset project if opened
            self._reset_project()
            
            self.dialog.show_info("Project Closed", "Project closed successfully!")
            self.status_bar.update_message("Project closed successfully!", 5000)
            
        except Exception as e:
            self.dialog.show_error("Error Closing Project", f"Failed to close project:\n{str(e)}")
    
    def _reset_project(self):
        # Set fresh copy of the settings
        # self.parent.settings.update(copy.deepcopy(SETTINGS))
        self.settings.update(copy.deepcopy(SETTINGS))
        
        # Set window title
        self.parent.setWindowTitle(f"ReplicaXLite {INFO['version']} - © 2024-2025 | Project: No project is opened.")

        # Clear interactor
        self.parent.interactor.clear()
        self.parent.interactor.show_axes()

        # Clear fem tables
        self.parent.manage_fem_table.reset_all_tables()

        # Reset FEM model
        self.parent.model.clear()


    # ==================== Helper Methods ====================
    def safe_chdir(target_folder):
        """Change working directory safely"""
        old_cwd = os.getcwd()  # Save current directory
        try:
            os.chdir(target_folder)
            print(f"Changed to: {os.getcwd()}")
            return True
        except Exception as e:
            print(f"Failed to change directory to {target_folder}: {e}")
            os.chdir(old_cwd)  # Revert back on failure
            return False

    def _initialize_project(self, project_folder):
        """Initialize project state after creation or opening"""
        self.current_project_folder_path = project_folder
        self.settings["_project"]["project_folder"] = project_folder
        
        # Update window title
        self._update_title()

        # Optionally set CWD to the project folder for this session:
        try:
            os.chdir(project_folder)
            print(f"Working directory changed to: {os.getcwd()}")
        except Exception as e:
            print(f"Warning: Could not change working directory - {e}")
    
    def _update_title(self):
        """Update window title via callback"""
        if self.current_project_folder_path:
            project_name = Path(self.current_project_folder_path).name
            title = f"ReplicaXLite {INFO['version']} - © 2024-2025 | Project: {project_name}"
        else:
            title = f"ReplicaXLite {INFO['version']} - © 2024-2025 | Project: No project is opened."
        
        self.parent.setWindowTitle(title)

    def _load_project_data(self):
        """Load project data from folder"""
        # Load settings
        settings_file_path = (Path(self.current_project_folder_path) / "ModelData" / "settings.json").as_posix()
        if os.path.exists(settings_file_path):
            with open(settings_file_path, 'r') as f:
                loaded_settings = json.load(f)
                # Merge loaded settings with current settings
                self.settings.update(loaded_settings)
                self.settings["_project"]["project_folder"] = self.current_project_folder_path  # UPDATE THE PROJECT FOLDER IF IT WAS MOVED
        
        fem_table_folder_path = Path(self.current_project_folder_path) / "ModelData" / "fem_tables"
        self.manage_fem_table.load_all_tables(fem_table_folder_path)

    def _save_project_data(self):
        # Save settings
        settings_file_path = (Path(self.current_project_folder_path) / "ModelData" / "settings.json").as_posix()
        with open(settings_file_path, 'w') as f:
            json.dump(self.settings, f, indent=2)
        fem_table_folder_path = Path(self.current_project_folder_path) / "ModelData" / "fem_tables"
        self.manage_fem_table.save_all_table(fem_table_folder_path)


        
    # ==================== Utility Methods ====================
    
    def get_project_path(self):
        """Get the current project path"""
        return self.current_project_folder_path
    
    def get_model_data_path(self):
        """Get the ModelData folder path"""
        if self.current_project_folder_path:
            return (Path(self.current_project_folder_path) / "ModelData").as_posix()
        return None
    
    def get_result_data_path(self):
        """Get the ResultData folder path"""
        if self.current_project_folder_path:
            return (Path(self.current_project_folder_path) / "ResultData").as_posix()
        return None
    
    def get_user_data_path(self):
        """Get the UserData folder path"""
        if self.current_project_folder_path:
            return (Path(self.current_project_folder_path) / "UserData").as_posix()
        return None
