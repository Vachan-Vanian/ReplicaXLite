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


import sys
import time
from pathlib import Path
from PySide6.QtWidgets import (QApplication, QMainWindow, QMenuBar, QStatusBar, 
                              QMenu, QToolBar, QDockWidget, QTextEdit, QMessageBox, 
                              QSplashScreen, QLabel, QPushButton)
from PySide6.QtWidgets import (QSplitter, QTabWidget, QWidget, QFrame, QVBoxLayout)
from PySide6.QtCore import Qt
from PySide6.QtGui import QAction, QKeySequence, QIcon, QPalette, QPixmap
from PySide6.QtCore import Qt, Slot
from PySide6.QtWidgets import QFileDialog, QInputDialog, QMessageBox
from pyvistaqt import QtInteractor
from .Managers.manage_tools import ReplicaXToolsManager
from .Managers.manage_info import ReplicaXInfoManger
from .Managers.manage_console import ConsoleManager
from .Managers.manage_interactor import ReplicaXinteractorManager
from .Managers.manage_state import ReplicaXProjectManager
from .Managers.dialog_helper import DialogHelper
from .Managers.status_helper import StatusBarHelper
from .Managers.manage_fem_table import ReplicaXFemTableManager
from .Managers.manage_settings import SettingsEditor
from .Managers.manage_project_files import ProjectFileViewer
from .StructuralAPI import StructuralModel
from typing import Dict

from .config import INFO, SETTINGS
import copy


class ReplicaXLite(QMainWindow):
    def __init__(self, package_root):
        super().__init__()
        self.package_root = package_root
        self.settings = copy.deepcopy(SETTINGS)
        self.model: Dict[str, StructuralModel] = {}
               
        # Set window title
        self.setWindowTitle(f"ReplicaXLite {INFO['version']} - © 2024-2025 | Project: No project is opened.")
      
        # Set window size
        self.setMinimumSize(1280, 720)
        self.resize(1536, 864)
        
        # Create helper classes
        self.setup_status_bar()
        self.dialog_helper = DialogHelper(self)

        ### ------------- MAIN MENU ------------- 
        self.setup_resources()
        self.create_menus()
        ### ------------- MAIN MENU ------------- 
        # Set central widget
        self.create_main_interface()
        
        self.setup_managers()
        self.create_connections()  # Connect after managers exist
        

    def __setattr__(self, name, value):
        """Track when settings gets reassigned"""
        if name == 'settings' and hasattr(self, 'settings'):
            # settings already exists and is being reassigned
            import traceback
            print(f"\n⚠️ WARNING: self.settings being reassigned!")
            print(f"  Old ID: {id(self.settings)}")
            print(f"  New ID: {id(value)}")
            print(f"  Call stack:")
            traceback.print_stack()
        super().__setattr__(name, value)
    
    ### ------------- STATUS BAR ------------
    def setup_status_bar(self):
        """Setup the status bar with helper"""
        # Create status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        # Create status bar helper
        self.statusbar_helper = StatusBarHelper(self.status_bar)
    
    ### ------------- STATUS BAR ------------
    
    ### ------------- MAIN MENU ------------- 
    def setup_resources(self):
        """Initialize resource paths for the application"""
        # Set the icons directory path
        self.icons_dir = self.package_root / "GUIs" / "icons"
        
        # Ensure the icons directory exists
        if not self.icons_dir.exists():
            print(f"Warning: Icons directory not found at {self.icons_dir}")
    
    def get_icon(self, icon_relative_path):
        """
        Get QIcon from the specified relative path
        
        Args:
            icon_path: Relative path to the icon file from the icons directory
                    (e.g., 'main_menu/new.png' or 'about/help.png')
                
        Returns:
            QIcon object
        """
        # Construct the full path to the icon
        full_path = self.icons_dir / icon_relative_path
        # Check if the file exists
        if not full_path.exists():
            print(f"Warning: Icon not found at {full_path}")
            # Return an empty icon
            return QIcon()
        
        # Return the icon
        return QIcon(str(full_path))

    def create_menus(self):
        """Create all menus, actions, icons, and shortcuts (NO connections)"""
        self.main_menu = {}
        self.menu_actions = {}
        menu_bar = self.menuBar()
        
        # ==================== PROJECT MENU ====================
        self.main_menu['project'] = menu_bar.addMenu("Project")
        
        self.menu_actions['new_project'] = QAction("New", self)
        self.menu_actions['new_project'].setIcon(self.get_icon("main_menu/new_project.png"))
        self.menu_actions['new_project'].setShortcut(QKeySequence("Ctrl+N"))
        self.main_menu['project'].addAction(self.menu_actions['new_project'])
        
        self.menu_actions['open_project'] = QAction("Open", self)
        self.menu_actions['open_project'].setIcon(self.get_icon("main_menu/open_project.png"))
        self.menu_actions['open_project'].setShortcut(QKeySequence("Ctrl+O"))
        self.main_menu['project'].addAction(self.menu_actions['open_project'])
        
        self.menu_actions['save_project'] = QAction("Save", self)
        self.menu_actions['save_project'].setIcon(self.get_icon("main_menu/save_project.png"))
        self.menu_actions['save_project'].setShortcut(QKeySequence("Ctrl+S"))
        self.main_menu['project'].addAction(self.menu_actions['save_project'])
        
        self.menu_actions['close_project'] = QAction("Close", self)
        self.menu_actions['close_project'].setIcon(self.get_icon("main_menu/close_project.png"))
        self.main_menu['project'].addAction(self.menu_actions['close_project'])
        
        self.main_menu['project'].addSeparator()
        
        self.menu_actions['settings'] = QAction("Settings", self)
        self.menu_actions['settings'].setIcon(self.get_icon("main_menu/settings.png"))
        self.main_menu['project'].addAction(self.menu_actions['settings'])
        
        self.main_menu['project'].addSeparator()
        
        self.menu_actions['exit'] = QAction("Exit", self)
        self.menu_actions['exit'].setIcon(self.get_icon("main_menu/exit.png"))
        self.main_menu['project'].addAction(self.menu_actions['exit'])
        
        # ==================== VIEW MENU ====================
        self.main_menu['view'] = menu_bar.addMenu("View")
        
        self.menu_actions['view_isometric'] = QAction("Isometric", self)
        self.menu_actions['view_isometric'].setIcon(self.get_icon("main_menu/isometric_view.png"))
        self.menu_actions['view_isometric'].setShortcut(QKeySequence("Ctrl+0"))
        self.main_menu['view'].addAction(self.menu_actions['view_isometric'])
        
        self.menu_actions['view_yz_plus'] = QAction("Plane YZ | +X", self)
        self.menu_actions['view_yz_plus'].setIcon(self.get_icon("main_menu/plane_yz_plus.png"))
        self.menu_actions['view_yz_plus'].setShortcut(QKeySequence("Ctrl+1"))
        self.main_menu['view'].addAction(self.menu_actions['view_yz_plus'])
        
        self.menu_actions['view_xz_plus'] = QAction("Plane XZ | +Y", self)
        self.menu_actions['view_xz_plus'].setIcon(self.get_icon("main_menu/plane_xz_plus.png"))
        self.menu_actions['view_xz_plus'].setShortcut(QKeySequence("Ctrl+2"))
        self.main_menu['view'].addAction(self.menu_actions['view_xz_plus'])
        
        self.menu_actions['view_xy_plus'] = QAction("Plane XY | +Z", self)
        self.menu_actions['view_xy_plus'].setIcon(self.get_icon("main_menu/plane_xy_plus.png"))
        self.menu_actions['view_xy_plus'].setShortcut(QKeySequence("Ctrl+3"))
        self.main_menu['view'].addAction(self.menu_actions['view_xy_plus'])
        
        self.menu_actions['view_yz_minus'] = QAction("Plane YZ | -X", self)
        self.menu_actions['view_yz_minus'].setIcon(self.get_icon("main_menu/plane_yz_minus.png"))
        self.menu_actions['view_yz_minus'].setShortcut(QKeySequence("Ctrl+Alt+1"))
        self.main_menu['view'].addAction(self.menu_actions['view_yz_minus'])
        
        self.menu_actions['view_xz_minus'] = QAction("Plane XZ | -Y", self)
        self.menu_actions['view_xz_minus'].setIcon(self.get_icon("main_menu/plane_xz_minus.png"))
        self.menu_actions['view_xz_minus'].setShortcut(QKeySequence("Ctrl+Alt+2"))
        self.main_menu['view'].addAction(self.menu_actions['view_xz_minus'])
        
        self.menu_actions['view_xy_minus'] = QAction("Plane XY | -Z", self)
        self.menu_actions['view_xy_minus'].setIcon(self.get_icon("main_menu/plane_xy_minus.png"))
        self.menu_actions['view_xy_minus'].setShortcut(QKeySequence("Ctrl+Alt+3"))
        self.main_menu['view'].addAction(self.menu_actions['view_xy_minus'])
        
        self.main_menu['view'].addSeparator()
        
        self.menu_actions['rotate_x_pos'] = QAction("Rotate X+", self)
        self.menu_actions['rotate_x_pos'].setIcon(self.get_icon("main_menu/plane_yz_plus.png"))
        self.menu_actions['rotate_x_pos'].setShortcut(QKeySequence("Alt+1"))
        self.main_menu['view'].addAction(self.menu_actions['rotate_x_pos'])
        
        self.menu_actions['rotate_x_neg'] = QAction("Rotate X-", self)
        self.menu_actions['rotate_x_neg'].setIcon(self.get_icon("main_menu/plane_yz_plus.png"))
        self.menu_actions['rotate_x_neg'].setShortcut(QKeySequence("Alt+4"))
        self.main_menu['view'].addAction(self.menu_actions['rotate_x_neg'])
        
        self.menu_actions['rotate_y_pos'] = QAction("Rotate Y+", self)
        self.menu_actions['rotate_y_pos'].setIcon(self.get_icon("main_menu/plane_xz_plus.png"))
        self.menu_actions['rotate_y_pos'].setShortcut(QKeySequence("Alt+2"))
        self.main_menu['view'].addAction(self.menu_actions['rotate_y_pos'])
        
        self.menu_actions['rotate_y_neg'] = QAction("Rotate Y-", self)
        self.menu_actions['rotate_y_neg'].setIcon(self.get_icon("main_menu/plane_xz_plus.png"))
        self.menu_actions['rotate_y_neg'].setShortcut(QKeySequence("Alt+5"))
        self.main_menu['view'].addAction(self.menu_actions['rotate_y_neg'])
        
        self.menu_actions['rotate_z_pos'] = QAction("Rotate Z+", self)
        self.menu_actions['rotate_z_pos'].setIcon(self.get_icon("main_menu/plane_xy_plus.png"))
        self.menu_actions['rotate_z_pos'].setShortcut(QKeySequence("Alt+3"))
        self.main_menu['view'].addAction(self.menu_actions['rotate_z_pos'])
        
        self.menu_actions['rotate_z_neg'] = QAction("Rotate Z-", self)
        self.menu_actions['rotate_z_neg'].setIcon(self.get_icon("main_menu/plane_xy_plus.png"))
        self.menu_actions['rotate_z_neg'].setShortcut(QKeySequence("Alt+6"))
        self.main_menu['view'].addAction(self.menu_actions['rotate_z_neg'])
        
        self.main_menu['view'].addSeparator()

        # Camera Movement Actions
        self.menu_actions['move_x_positive'] = QAction("Move X+", self)
        self.menu_actions['move_x_positive'].setIcon(self.get_icon("main_menu/move_x_plus.png"))
        self.menu_actions['move_x_positive'].setShortcut(QKeySequence("Ctrl+Up"))
        self.main_menu['view'].addAction(self.menu_actions['move_x_positive'])

        self.menu_actions['move_x_negative'] = QAction("Move X-", self)
        self.menu_actions['move_x_negative'].setIcon(self.get_icon("main_menu/move_x_minus.png"))
        self.menu_actions['move_x_negative'].setShortcut(QKeySequence("Ctrl+Down"))
        self.main_menu['view'].addAction(self.menu_actions['move_x_negative'])

        self.menu_actions['move_y_positive'] = QAction("Move Y+", self)
        self.menu_actions['move_y_positive'].setIcon(self.get_icon("main_menu/move_y_plus.png"))
        self.menu_actions['move_y_positive'].setShortcut(QKeySequence("Ctrl+Right"))
        self.main_menu['view'].addAction(self.menu_actions['move_y_positive'])

        self.menu_actions['move_y_negative'] = QAction("Move Y-", self)
        self.menu_actions['move_y_negative'].setIcon(self.get_icon("main_menu/move_y_minus.png"))
        self.menu_actions['move_y_negative'].setShortcut(QKeySequence("Ctrl+Left"))
        self.main_menu['view'].addAction(self.menu_actions['move_y_negative'])

        self.menu_actions['move_z_positive'] = QAction("Move Z+", self)
        self.menu_actions['move_z_positive'].setIcon(self.get_icon("main_menu/move_z_plus.png"))
        self.menu_actions['move_z_positive'].setShortcut(QKeySequence("Alt+Up"))
        self.main_menu['view'].addAction(self.menu_actions['move_z_positive'])

        self.menu_actions['move_z_negative'] = QAction("Move Z-", self)
        self.menu_actions['move_z_negative'].setIcon(self.get_icon("main_menu/move_z_minus.png"))
        self.menu_actions['move_z_negative'].setShortcut(QKeySequence("Alt+Down"))
        self.main_menu['view'].addAction(self.menu_actions['move_z_negative'])
        
        self.main_menu['view'].addSeparator()

        self.menu_actions['toggle_perspective'] = QAction("Toggle Perspective/Orthogonal", self)
        self.menu_actions['toggle_perspective'].setIcon(self.get_icon("main_menu/toggle_presp_ortho.png"))
        self.menu_actions['toggle_perspective'].setShortcut(QKeySequence("Ctrl+8"))
        self.main_menu['view'].addAction(self.menu_actions['toggle_perspective'])
        
        self.menu_actions['toggle_fullscreen'] = QAction("Toggle Full Screen Mode", self)
        self.menu_actions['toggle_fullscreen'].setIcon(self.get_icon("main_menu/full_screen.png"))
        self.menu_actions['toggle_fullscreen'].setShortcut(QKeySequence("Shift+F"))
        self.main_menu['view'].addAction(self.menu_actions['toggle_fullscreen'])
        
        self.main_menu['view'].addSeparator()
        
        self.menu_actions['surface_with_edges'] = QAction("Surface with Edges", self)
        self.menu_actions['surface_with_edges'].setIcon(self.get_icon("main_menu/solid_with_edges_view.png"))
        self.menu_actions['surface_with_edges'].setShortcut(QKeySequence("Ctrl+4"))
        self.main_menu['view'].addAction(self.menu_actions['surface_with_edges'])
        
        self.menu_actions['surface_without_edges'] = QAction("Surface without Edges", self)
        self.menu_actions['surface_without_edges'].setIcon(self.get_icon("main_menu/solid_view.png"))
        self.menu_actions['surface_without_edges'].setShortcut(QKeySequence("Ctrl+5"))
        self.main_menu['view'].addAction(self.menu_actions['surface_without_edges'])
        
        self.menu_actions['wireframe'] = QAction("Wireframe", self)
        self.menu_actions['wireframe'].setIcon(self.get_icon("main_menu/wireframe_view.png"))
        self.menu_actions['wireframe'].setShortcut(QKeySequence("Ctrl+6"))
        self.main_menu['view'].addAction(self.menu_actions['wireframe'])
        
        # ==================== INTERACTOR MENU ====================
        self.main_menu['interactor'] = menu_bar.addMenu("Interactor")
        
        self.menu_actions['display_model'] = QAction("Display/Update Model", self)
        self.menu_actions['display_model'].setIcon(self.get_icon("main_menu/interactor_display_model.png"))
        self.main_menu['interactor'].addAction(self.menu_actions['display_model'])
        
        self.menu_actions['clear_displayed_model'] = QAction("Clear Displayed Model", self)
        self.menu_actions['clear_displayed_model'].setIcon(self.get_icon("main_menu/interactor_clear_displayed_model.png"))
        self.main_menu['interactor'].addAction(self.menu_actions['clear_displayed_model'])

        self.menu_actions['clear_interactor'] = QAction("Clear ALL", self)
        self.menu_actions['clear_interactor'].setIcon(self.get_icon("main_menu/interactor_clear_all.png"))
        self.main_menu['interactor'].addAction(self.menu_actions['clear_interactor'])

        self.menu_actions['add_sphere'] = QAction("Add Sphere", self)
        self.menu_actions['add_sphere'].setIcon(self.get_icon("main_menu/interactor_add_sphere.png"))
        self.main_menu['interactor'].addAction(self.menu_actions['add_sphere'])
                
        self.menu_actions['screenshot'] = QAction("Screenshot", self)
        self.menu_actions['screenshot'].setIcon(self.get_icon("main_menu/screenshot.png"))
        self.menu_actions['screenshot'].setShortcut(QKeySequence("Ctrl+P"))
        self.main_menu['interactor'].addAction(self.menu_actions['screenshot'])

        # ==================== TOOLS MENU ====================
        self.main_menu['tools'] = menu_bar.addMenu("Tools")
        
        self.menu_actions['sensor_data_reader'] = QAction("Sensor Data Reader", self)
        self.menu_actions['sensor_data_reader'].setIcon(self.get_icon("main_menu/tools_sensor.png"))
        self.main_menu['tools'].addAction(self.menu_actions['sensor_data_reader'])
        
        self.menu_actions['unit_converter'] = QAction("Unit Converter", self)
        self.menu_actions['unit_converter'].setIcon(self.get_icon("main_menu/tools_converter.png"))
        self.main_menu['tools'].addAction(self.menu_actions['unit_converter'])
        
        self.menu_actions['opensees_recorder_reader'] = QAction("OpenSees Recorder Reader", self)
        self.menu_actions['opensees_recorder_reader'].setIcon(self.get_icon("main_menu/tools_recorder_reader.png"))
        self.main_menu['tools'].addAction(self.menu_actions['opensees_recorder_reader'])

        self.main_menu['tools'].addSeparator()

        self.menu_actions['color_picker'] = QAction("Color Picker", self)
        self.menu_actions['color_picker'].setIcon(self.get_icon("main_menu/tools_color_picker.png"))
        self.main_menu['tools'].addAction(self.menu_actions['color_picker'])

        self.menu_actions['time_history_data'] = QAction("Time History Data", self)
        self.menu_actions['time_history_data'].setIcon(self.get_icon("main_menu/tools_time_history.png"))
        self.main_menu['tools'].addAction(self.menu_actions['time_history_data'])
        
        # ==================== INFO MENU ====================
        self.main_menu['info'] = menu_bar.addMenu("Info")
        
        self.menu_actions['about'] = QAction("About", self)
        self.menu_actions['about'].setIcon(self.get_icon("main_menu/about.png"))
        self.main_menu['info'].addAction(self.menu_actions['about'])

    def create_connections(self):
        """Connect all menu actions to their functions"""
        
        # ==================== PROJECT CONNECTIONS ====================
        self.menu_actions['new_project'].triggered.connect(self.manage_project.create_project)
        self.menu_actions['open_project'].triggered.connect(self.manage_project.open_project)
        self.menu_actions['save_project'].triggered.connect(self.manage_project.save_project)
        self.menu_actions['close_project'].triggered.connect(self.manage_project.close_project)
        self.menu_actions['settings'].triggered.connect(lambda: self.manage_settings.show())
        self.menu_actions['exit'].triggered.connect(self.close)
        
        # ==================== VIEW CONNECTIONS ====================
        self.menu_actions['view_isometric'].triggered.connect(lambda: self.interactor.view_isometric())
        self.menu_actions['view_yz_plus'].triggered.connect(lambda: self.interactor.view_yz())
        self.menu_actions['view_xz_plus'].triggered.connect(lambda: self.interactor.view_xz(negative=True))
        self.menu_actions['view_xy_plus'].triggered.connect(lambda: self.interactor.view_xy())
        self.menu_actions['view_yz_minus'].triggered.connect(lambda: self.interactor.view_yz(negative=True))
        self.menu_actions['view_xz_minus'].triggered.connect(lambda: self.interactor.view_xz())
        self.menu_actions['view_xy_minus'].triggered.connect(lambda: self.interactor.view_xy(negative=True))
        
        self.menu_actions['rotate_x_pos'].triggered.connect(lambda: self.manage_interactor.rotate_view_global(axis='x', angle=self.settings['interactor']['group_camera_rotation']['rotation_angle_deg_x']))
        self.menu_actions['rotate_x_neg'].triggered.connect(lambda: self.manage_interactor.rotate_view_global(axis='x', angle=-self.settings['interactor']['group_camera_rotation']['rotation_angle_deg_x']))
        self.menu_actions['rotate_y_pos'].triggered.connect(lambda: self.manage_interactor.rotate_view_global(axis='y', angle=self.settings['interactor']['group_camera_rotation']['rotation_angle_deg_y']))
        self.menu_actions['rotate_y_neg'].triggered.connect(lambda: self.manage_interactor.rotate_view_global(axis='y', angle=-self.settings['interactor']['group_camera_rotation']['rotation_angle_deg_y']))
        self.menu_actions['rotate_z_pos'].triggered.connect(lambda: self.manage_interactor.rotate_view_global(axis='z', angle=self.settings['interactor']['group_camera_rotation']['rotation_angle_deg_z']))
        self.menu_actions['rotate_z_neg'].triggered.connect(lambda: self.manage_interactor.rotate_view_global(axis='z', angle=-self.settings['interactor']['group_camera_rotation']['rotation_angle_deg_z']))

        self.menu_actions['move_x_positive'].triggered.connect(lambda: self.manage_interactor.move_camera_global('x', -self.settings['interactor']['group_camera_movement']['distance_step_x']))
        self.menu_actions['move_x_negative'].triggered.connect(lambda: self.manage_interactor.move_camera_global('x', self.settings['interactor']['group_camera_movement']['distance_step_x']))
        self.menu_actions['move_y_positive'].triggered.connect(lambda: self.manage_interactor.move_camera_global('y', -self.settings['interactor']['group_camera_movement']['distance_step_y']))
        self.menu_actions['move_y_negative'].triggered.connect(lambda: self.manage_interactor.move_camera_global('y', self.settings['interactor']['group_camera_movement']['distance_step_y']))
        self.menu_actions['move_z_positive'].triggered.connect(lambda: self.manage_interactor.move_camera_global('z', -self.settings['interactor']['group_camera_movement']['distance_step_z']))
        self.menu_actions['move_z_negative'].triggered.connect(lambda: self.manage_interactor.move_camera_global('z', self.settings['interactor']['group_camera_movement']['distance_step_z']))
        
        self.menu_actions['toggle_perspective'].triggered.connect(lambda: self.manage_interactor.toggle_perspective_orthogonal_view())
        self.menu_actions['toggle_fullscreen'].triggered.connect(lambda: self.toggle_full_screen())
        
        self.menu_actions['surface_with_edges'].triggered.connect(lambda: self.manage_interactor.mesh_view_mode("Surface with Edges"))
        self.menu_actions['surface_without_edges'].triggered.connect(lambda: self.manage_interactor.mesh_view_mode("Surface without Edges"))
        self.menu_actions['wireframe'].triggered.connect(lambda: self.manage_interactor.mesh_view_mode("Wireframe"))
        
        # ==================== INTERACTOR CONNECTIONS ====================
        self.menu_actions['display_model'].triggered.connect(lambda: self.manage_interactor.display_model())
        self.menu_actions['clear_displayed_model'].triggered.connect(lambda: self.manage_interactor.clear_display_model())
        self.menu_actions['clear_interactor'].triggered.connect(lambda: self.manage_interactor.interactor.clear())
        self.menu_actions['add_sphere'].triggered.connect(lambda: self.manage_interactor.add_sphere())
        self.menu_actions['screenshot'].triggered.connect(lambda: self.manage_interactor.take_screenshot(None, self.settings['interactor']['group_screenshot']['transparent_background'], self.settings['interactor']['group_screenshot']['scale']))
              
        # ==================== TOOLS CONNECTIONS ====================
        self.menu_actions['sensor_data_reader'].triggered.connect(lambda: self.manage_tools.sensor_data_gui_popup.show())
        self.menu_actions['unit_converter'].triggered.connect(lambda: self.manage_tools.unit_converter_gui_popup.show())
        self.menu_actions['opensees_recorder_reader'].triggered.connect(lambda: self.manage_tools.opensees_recorder_reader_popop.show())
        self.menu_actions['color_picker'].triggered.connect(lambda: self.manage_tools.color_picker.show())
        self.menu_actions['time_history_data'].triggered.connect(lambda: self.manage_tools.time_history_data.show())
        
        # ==================== INFO CONNECTIONS ====================
        self.menu_actions['about'].triggered.connect(lambda: self.manage_info.about_popup.show())

    ### ------------- MAIN MENU ------------- 

    def create_main_interface(self):
        """
        Create the main window interface with a top-level notebook tab containing all widgets
        """
        # Create main notebook tab widget as the central widget
        self.main_notebook = QTabWidget()
        self.setCentralWidget(self.main_notebook)

        # Create dictionary to store references to widgets - only fem_table_tabs now
        self.process_nb_tabs = {}
        self.setup_nb = {}
        self.fem_table_tabs = {}
            
        # Create the main tabs
        self.process_nb_tabs['setup'] = QWidget()
            
        # Add the main tabs to the notebook
        self.main_notebook.addTab(self.process_nb_tabs['setup'], "Setup")
            
        # Main layout for the setup tab content
        main_layout = QVBoxLayout(self.process_nb_tabs['setup'])
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
            
        # Main horizontal splitter (divides window into three sections)
        self.main_splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(self.main_splitter)
            
        # 1. # Create the project file viewer directly
        self.project_file_viewer = ProjectFileViewer(self, self.settings)
            
        # 2. Center panel - Vertical splitter
        self.center_splitter = QSplitter(Qt.Vertical)
            
        # Frame for QtInteractor
        self.qt_interactor_frame = QFrame()
        qt_interactor_layout = QVBoxLayout(self.qt_interactor_frame)
        qt_interactor_layout.setContentsMargins(0, 0, 0, 0)
        qt_interactor_layout.setSpacing(0)
        self.interactor = QtInteractor(self.qt_interactor_frame)
        qt_interactor_layout.addWidget(self.interactor)
        self.interactor.show_axes()
            
        # Bottom tabbed widget
        self.setup_nb['fem_table'] = QTabWidget()
        
        # Define tab structure: {category: [subtabs]} or {category: {subtab: [sub-subtabs]}}
        tab_structure = {
            'materials': None,
            'sections': {
                'elastic': None, 
                'fiber': ['section', 'rebar_points', 'rebar_lines', 'rebar_circles']},
            'nodes': {
                'coordinates': None,
                'constraints': None,
                'restraints': ['rigid_diaphragms', 'rigid_links', 'equal_dofs'],
                'masses': None,
                'loads': None
            },
            'elements': ['beam_integrations', 'connections', 'loads'],
            'time_series': None,
            'patterns': None,
            'analyses': None,
            'sensors': None
        }
        
        # Create tabs based on structure with nested dictionaries
        for category, subtabs in tab_structure.items():
            display_name = ' '.join(word.capitalize() for word in category.split('_'))
            
            if subtabs is None:
                # Simple widget with no subtabs
                self.fem_table_tabs[category] = QWidget()
                self.setup_nb['fem_table'].addTab(self.fem_table_tabs[category], display_name)
            
            elif isinstance(subtabs, list):
                # Category with list of subtabs (e.g., sections, elements)
                # Create nested dictionary for this category
                self.fem_table_tabs[category] = {}
                tab_widget = QTabWidget()
                
                for subtab in subtabs:
                    widget = QWidget()
                    self.fem_table_tabs[category][subtab] = widget
                    tab_widget.addTab(widget, ' '.join(word.capitalize() for word in subtab.split('_')))
                
                self.setup_nb['fem_table'].addTab(tab_widget, display_name)
            
            elif isinstance(subtabs, dict):
                # Category with nested structure (e.g., nodes)
                # Create nested dictionary for this category
                self.fem_table_tabs[category] = {}
                tab_widget = QTabWidget()
                
                for subtab, sub_subtabs in subtabs.items():
                    if sub_subtabs is None:
                        # Simple subtab (e.g., coordinates, constraints)
                        widget = QWidget()
                        self.fem_table_tabs[category][subtab] = widget
                        tab_widget.addTab(widget, ' '.join(word.capitalize() for word in subtab.split('_')))
                    
                    else:
                        # Subtab with its own nested tabs (e.g., restraints)
                        # Create another nested dictionary
                        self.fem_table_tabs[category][subtab] = {}
                        sub_tab_widget = QTabWidget()
                        
                        for sub_subtab in sub_subtabs:
                            widget = QWidget()
                            self.fem_table_tabs[category][subtab][sub_subtab] = widget
                            sub_tab_widget.addTab(widget, ' '.join(word.capitalize() for word in sub_subtab.split('_')))
                        
                        tab_widget.addTab(sub_tab_widget, ' '.join(word.capitalize() for word in subtab.split('_')))
                
                self.setup_nb['fem_table'].addTab(tab_widget, display_name)
            
        # Add widgets to center splitter
        self.center_splitter.addWidget(self.qt_interactor_frame)
        self.center_splitter.addWidget(self.setup_nb['fem_table'])
        self.center_splitter.setSizes([600, 200])
            
        # 3. Right panel - Console notebook tab
        self.setup_nb['console'] = QTabWidget()
        self.setup_nb['console'].addTab(QWidget(), "Console")
            
        # Add all three panels to the main splitter
        self.main_splitter.addWidget(self.project_file_viewer)
        self.main_splitter.addWidget(self.center_splitter)
        self.main_splitter.addWidget(self.setup_nb['console'])
        self.main_splitter.setSizes([200, 800, 200])

        self.setup_console_interface()
            
    def setup_console_interface(self):
        """
        Set up the Jupyter console interface
        """
        # Get the console tab widget
        console_tab_widget = self.setup_nb['console'].widget(0)
        
        # Initialize the console manager - it handles everything!
        self.console_manager = ConsoleManager(self, console_tab_widget)

    def setup_managers(self):
        self.manage_tools = ReplicaXToolsManager(self.settings)
        self.manage_info = ReplicaXInfoManger(self.package_root)
        self.manage_interactor = ReplicaXinteractorManager(self.interactor, self.settings, self.model)
        self.manage_fem_table = ReplicaXFemTableManager(self.settings, self.fem_table_tabs, self.interactor, self.console_manager.console)

        self.manage_project = ReplicaXProjectManager(self)
        self.manage_settings = SettingsEditor(
            settings_dict=self.settings,
            statusbar_helper=self.statusbar_helper,
            callbacks={
                "unit_system.new_unit_system": self.manage_fem_table.sync_units_from_settings
            }
        )


### =======================================================================================================
    
    ### ------------- UTILITY FUNCTIONS ------------- 
   
    # Close Event Handlers
    def closeEvent(self, event):
        # Create message box
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle('Confirm Exit')
        msg_box.setText("Close the application? Unsaved changes will be lost!")
        msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg_box.setDefaultButton(QMessageBox.No)
        
        # Make it stay on top of all other windows
        msg_box.setWindowFlags(msg_box.windowFlags() | Qt.WindowStaysOnTopHint)
        
        reply = msg_box.exec() 

        if reply == QMessageBox.Yes:
            for window in QApplication.topLevelWidgets():
                window.close()
            event.accept()
        else:
            event.ignore()
    
    def toggle_full_screen(self):
        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()

    ### ------------- UTILITY FUNCTIONS ------------- 


def main():    
    # Create QApplication
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    # Get the path to the package root - this works when installed as a package
    package_root = Path(__file__).parent
    icons_dir = package_root / "GUIs" / "icons"
    splash_icon_path = icons_dir / "splashscreen" / "replicax_ss.png"
    
    # Check if splash screen exists, if not use a simple startup
    if splash_icon_path.exists():
        splash_pix = QPixmap(str(splash_icon_path))
        splashscreen = QSplashScreen(splash_pix)
        splashscreen.show()

        dots = 0
        for _ in range(5):
            dots = (dots + 1) % 4
            splashscreen.showMessage(f"Loading{'.' * dots}", Qt.AlignBottom | Qt.AlignCenter, Qt.yellow)
            time.sleep(0.25)
            app.processEvents()
    else:
        splashscreen = None
        print("ReplicaXLite: Starting application...")

    # Create and show main window
    window = ReplicaXLite(package_root)
    
    if splashscreen:
        splashscreen.finish(window)
    
    window.show()
    
    # Start the application event loop
    sys.exit(app.exec())

def ReplicaXLiteApp():
    main()

if __name__ == "__main__":
    main()
