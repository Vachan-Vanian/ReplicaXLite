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
import subprocess
import sys
from pathlib import Path
from datetime import datetime
from PySide6 import QtWidgets, QtCore, QtGui


class ProjectFileViewer(QtWidgets.QWidget):
    """
    Production-ready Project File Browser
    
    Features:
    - Tree view of project files and folders
    - Auto-refresh on file changes
    - Manual refresh button
    - File type icons
    - Context menu (right-click)
    - Double-click to open files
    - File info display
    - Search/filter functionality
    """
    
    # Signal emitted when a Python file is double-clicked
    file_opened = QtCore.Signal(str)
    
    def __init__(self, parent, settings):
        super().__init__(parent)
        
        self.parent = parent
        self.settings = settings
        self.project_folder = None
        self.file_watcher = None
        
        # Setup UI
        self.setup_ui()
        
        # Load project folder
        self.refresh_project()
    
    def setup_ui(self):
        """Setup the file viewer UI"""
        # Main layout
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)
        
        # Create tree view first (needed by toolbar)
        self.tree = QtWidgets.QTreeWidget()
        self.tree.setHeaderLabels(["Name", "Size", "Modified"])
        self.tree.setColumnWidth(0, 200)
        self.tree.setColumnWidth(1, 80)
        self.tree.setAlternatingRowColors(True)
        self.tree.setAnimated(True)
        
        # Enable drag and drop
        self.tree.setDragEnabled(True)
        self.tree.setAcceptDrops(False)
        
        # Connect signals
        self.tree.itemDoubleClicked.connect(self.on_item_double_clicked)
        self.tree.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.tree.customContextMenuRequested.connect(self.show_context_menu)
        
        # Now create toolbar (can reference self.tree)
        toolbar = self.create_toolbar()
        layout.addWidget(toolbar)
        
        # Search bar
        search_layout = QtWidgets.QHBoxLayout()
        self.search_input = QtWidgets.QLineEdit()
        self.search_input.setPlaceholderText("🔍 Search files...")
        self.search_input.textChanged.connect(self.filter_tree)
        search_layout.addWidget(self.search_input)
        
        btn_clear_search = QtWidgets.QPushButton("✕")
        btn_clear_search.setMaximumWidth(30)
        btn_clear_search.setToolTip("Clear search")
        btn_clear_search.clicked.connect(lambda: self.search_input.clear())
        search_layout.addWidget(btn_clear_search)
        
        layout.addLayout(search_layout)
        
        # Add tree to layout
        layout.addWidget(self.tree)
        
        # Status label
        self.status_label = QtWidgets.QLabel("No project loaded")
        self.status_label.setStyleSheet("color: gray; font-size: 9pt;")
        layout.addWidget(self.status_label)
    
    def create_toolbar(self):
        """Create toolbar with action buttons"""
        toolbar = QtWidgets.QWidget()
        toolbar_layout = QtWidgets.QHBoxLayout(toolbar)
        toolbar_layout.setContentsMargins(0, 0, 0, 0)
        toolbar_layout.setSpacing(5)
        
        # Refresh button
        btn_refresh = QtWidgets.QPushButton("🔄 Refresh")
        btn_refresh.setToolTip("Refresh file tree")
        btn_refresh.clicked.connect(self.refresh_project)
        toolbar_layout.addWidget(btn_refresh)
        
        # Open in Explorer/Finder
        btn_open_folder = QtWidgets.QPushButton("📁 Open Folder")
        btn_open_folder.setToolTip("Open project folder in file explorer")
        btn_open_folder.clicked.connect(self.open_in_explorer)
        toolbar_layout.addWidget(btn_open_folder)
        
        # # Auto-refresh toggle
        # self.auto_refresh_checkbox = QtWidgets.QCheckBox("Auto")
        # self.auto_refresh_checkbox.setToolTip("Automatically refresh when files change")
        # self.auto_refresh_checkbox.setChecked(False)
        # self.auto_refresh_checkbox.stateChanged.connect(self.toggle_auto_refresh)
        # toolbar_layout.addWidget(self.auto_refresh_checkbox)
        
        toolbar_layout.addStretch()
        
        # Collapse/Expand buttons
        btn_collapse = QtWidgets.QPushButton("▼")
        btn_collapse.setMaximumWidth(30)
        btn_collapse.setToolTip("Collapse all")
        btn_collapse.clicked.connect(self.tree.collapseAll)
        toolbar_layout.addWidget(btn_collapse)
        
        btn_expand = QtWidgets.QPushButton("▶")
        btn_expand.setMaximumWidth(30)
        btn_expand.setToolTip("Expand all")
        btn_expand.clicked.connect(self.tree.expandAll)
        toolbar_layout.addWidget(btn_expand)
        
        return toolbar
    
    def refresh_project(self):
        """Refresh the project file tree"""
        # Clear tree
        self.tree.clear()
        
        # Get project folder from settings
        project_folder = self.settings.get('_project', {}).get('project_folder')
        
        if not project_folder or not os.path.exists(project_folder):
            self.status_label.setText("⚠ No valid project folder")
            self.project_folder = None
            return
        
        self.project_folder = Path(project_folder)
        
        # # Setup file watcher for auto-refresh
        # if self.auto_refresh_checkbox.isChecked():
        #     self.setup_file_watcher()
        
        # Populate tree
        self.populate_tree(self.project_folder, self.tree.invisibleRootItem())
        
        # Update status
        file_count = self.count_files(self.project_folder)
        self.status_label.setText(f"📂 {self.project_folder.name} | {file_count} files")
        
        # print(f"✓ Project Refreshed: {self.project_folder}")
    
    def populate_tree(self, path, parent_item):
        """Recursively populate tree with files and folders"""
        try:
            # Get all items in directory
            items = sorted(path.iterdir(), key=lambda x: (not x.is_dir(), x.name.lower()))
            
            for item in items:
                # # Skip hidden files
                # if item.name.startswith('.'):
                #     continue
                
                # Create tree item
                tree_item = QtWidgets.QTreeWidgetItem(parent_item)
                tree_item.setText(0, item.name)
                tree_item.setData(0, QtCore.Qt.UserRole, str(item))
                
                if item.is_dir():
                    # Folder
                    tree_item.setIcon(0, self.get_icon("folder"))
                    tree_item.setText(1, "")
                    tree_item.setText(2, "")
                    
                    # Recursively add contents
                    self.populate_tree(item, tree_item)
                    
                else:
                    # File
                    tree_item.setIcon(0, self.get_icon_for_file(item))
                    
                    # File size
                    size = item.stat().st_size
                    tree_item.setText(1, self.format_size(size))
                    
                    # Modified date
                    modified = datetime.fromtimestamp(item.stat().st_mtime)
                    tree_item.setText(2, modified.strftime("%Y-%m-%d %H:%M"))
        
        except PermissionError:
            pass  # Skip folders we can't access
        except Exception as e:
            print(f"Error populating tree: {e}")
    
    def get_icon(self, icon_type):
        """Get icon for file type"""
        style = self.style()
        
        if icon_type == "folder":
            return style.standardIcon(QtWidgets.QStyle.SP_DirIcon)
        elif icon_type == "python":
            return style.standardIcon(QtWidgets.QStyle.SP_FileIcon)
        elif icon_type == "image":
            return style.standardIcon(QtWidgets.QStyle.SP_FileIcon)
        elif icon_type == "text":
            return style.standardIcon(QtWidgets.QStyle.SP_FileDialogDetailedView)
        else:
            return style.standardIcon(QtWidgets.QStyle.SP_FileIcon)
    
    def get_icon_for_file(self, file_path):
        """Get appropriate icon based on file extension"""
        suffix = file_path.suffix.lower()
        
        icon_map = {
            '.py': 'python',
            '.txt': 'text',
            '.md': 'text',
            '.json': 'text',
            '.xml': 'text',
            '.csv': 'text',
            '.png': 'image',
            '.jpg': 'image',
            '.jpeg': 'image',
            '.gif': 'image',
            '.bmp': 'image',
        }
        
        return self.get_icon(icon_map.get(suffix, 'file'))
    
    def format_size(self, size):
        """Format file size in human-readable format"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} TB"
    
    def count_files(self, path):
        """Count total number of files in directory"""
        count = 0
        try:
            for item in path.rglob('*'):
                if item.is_file() and not item.name.startswith('.'):
                    count += 1
        except:
            pass
        return count
    
    def filter_tree(self, search_text):
        """Filter tree items based on search text"""
        if not search_text:
            # Show all items
            self.show_all_items(self.tree.invisibleRootItem())
            return
        
        search_text = search_text.lower()
        
        # Hide items that don't match
        self.filter_items(self.tree.invisibleRootItem(), search_text)
    
    def show_all_items(self, parent_item):
        """Recursively show all items"""
        for i in range(parent_item.childCount()):
            child = parent_item.child(i)
            child.setHidden(False)
            self.show_all_items(child)
    
    def filter_items(self, parent_item, search_text):
        """Recursively filter items based on search text"""
        for i in range(parent_item.childCount()):
            child = parent_item.child(i)
            
            # Check if item matches
            item_text = child.text(0).lower()
            matches = search_text in item_text
            
            # Check children
            child_matches = self.filter_items(child, search_text)
            
            # Show if this item or any child matches
            child.setHidden(not (matches or child_matches))
            
            if matches or child_matches:
                # Expand parent to show matches
                parent_item.setExpanded(True)
        
        # Return True if any child matched
        has_visible_children = False
        for i in range(parent_item.childCount()):
            if not parent_item.child(i).isHidden():
                has_visible_children = True
                break
        
        return has_visible_children
    
    def on_item_double_clicked(self, item, column):
        """Handle double-click on item"""
        file_path = item.data(0, QtCore.Qt.UserRole)
        
        if not file_path:
            return
        
        path = Path(file_path)
        
        if path.is_file():
            # Handle file based on extension
            if path.suffix.lower() == '.py':
                # Open Python file in console
                self.open_python_file(path)
            else:
                # Open with default application
                self.open_file_external(path)
    
    def open_python_file(self, file_path):
        """Open Python file in Jupyter console"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                code = f.read()
            
            # Execute in console if available
            if hasattr(self.parent, 'console_manager'):
                self.parent.console_manager.execute_code(code)
                print(f"✓ Executed: {file_path.name}")
            else:
                print(f"✓ Loaded: {file_path.name}")
                print(code)
        
        except Exception as e:
            QtWidgets.QMessageBox.warning(
                self,
                "Error",
                f"Could not open file:\n{str(e)}"
            )
    
    def open_file_external(self, file_path):
        """Open file with system default application"""
        try:
            if sys.platform == 'win32':
                os.startfile(file_path)
            elif sys.platform == 'darwin':
                subprocess.call(['open', file_path])
            else:
                subprocess.call(['xdg-open', file_path])
        except Exception as e:
            print(f"Error opening file: {e}")
    
    def open_in_explorer(self):
        """Open project folder in file explorer"""
        if not self.project_folder or not self.project_folder.exists():
            QtWidgets.QMessageBox.warning(
                self,
                "No Project",
                "No valid project folder to open."
            )
            return
        
        try:
            if sys.platform == 'win32':
                os.startfile(self.project_folder)
            elif sys.platform == 'darwin':
                subprocess.call(['open', self.project_folder])
            else:
                subprocess.call(['xdg-open', self.project_folder])
        except Exception as e:
            QtWidgets.QMessageBox.warning(
                self,
                "Error",
                f"Could not open folder:\n{str(e)}"
            )
    
    def show_context_menu(self, position):
        """Show context menu on right-click"""
        item = self.tree.itemAt(position)
        
        if not item:
            return
        
        file_path = item.data(0, QtCore.Qt.UserRole)
        if not file_path:
            return
        
        path = Path(file_path)
        
        menu = QtWidgets.QMenu()
        
        if path.is_file():
            # File actions
            action_open = menu.addAction("📂 Open")
            action_open.triggered.connect(lambda: self.open_file_external(path))
            
            if path.suffix.lower() == '.py':
                action_run = menu.addAction("▶ Run in Console")
                action_run.triggered.connect(lambda: self.open_python_file(path))
            
            menu.addSeparator()
            
            action_copy_path = menu.addAction("📋 Copy Path")
            action_copy_path.triggered.connect(lambda: self.copy_path(path))
            
            action_copy_name = menu.addAction("📋 Copy Name")
            action_copy_name.triggered.connect(lambda: self.copy_name(path))
            
            menu.addSeparator()
            
            action_show = menu.addAction("📁 Show in Explorer")
            action_show.triggered.connect(lambda: self.show_in_explorer(path))
            
            menu.addSeparator()
            
            action_delete = menu.addAction("🗑️ Delete")
            action_delete.triggered.connect(lambda: self.delete_file(path))
        
        else:
            # Folder actions
            action_open = menu.addAction("📁 Open in Explorer")
            action_open.triggered.connect(lambda: self.open_file_external(path))
            
            menu.addSeparator()
            
            action_copy_path = menu.addAction("📋 Copy Path")
            action_copy_path.triggered.connect(lambda: self.copy_path(path))
            
            menu.addSeparator()
            
            action_new_file = menu.addAction("➕ New File")
            action_new_file.triggered.connect(lambda: self.create_new_file(path))
            
            action_new_folder = menu.addAction("➕ New Folder")
            action_new_folder.triggered.connect(lambda: self.create_new_folder(path))
        
        menu.exec_(self.tree.viewport().mapToGlobal(position))
    
    def copy_path(self, path):
        """Copy file path to clipboard"""
        clipboard = QtWidgets.QApplication.clipboard()
        clipboard.setText(str(path))
        print(f"✓ Copied path: {path}")
    
    def copy_name(self, path):
        """Copy file name to clipboard"""
        clipboard = QtWidgets.QApplication.clipboard()
        clipboard.setText(path.name)
        print(f"✓ Copied name: {path.name}")
    
    def show_in_explorer(self, path):
        """Show file in file explorer"""
        try:
            if sys.platform == 'win32':
                subprocess.run(['explorer', '/select,', str(path)])
            elif sys.platform == 'darwin':
                subprocess.run(['open', '-R', str(path)])
            else:
                # Open parent folder on Linux
                subprocess.run(['xdg-open', str(path.parent)])
        except Exception as e:
            print(f"Error showing in explorer: {e}")
    
    def delete_file(self, path):
        """Delete file with confirmation"""
        reply = QtWidgets.QMessageBox.question(
            self,
            "Delete File?",
            f"Are you sure you want to delete:\n{path.name}",
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
            QtWidgets.QMessageBox.No
        )
        
        if reply == QtWidgets.QMessageBox.Yes:
            try:
                path.unlink()
                self.refresh_project()
                print(f"✓ Deleted: {path.name}")
            except Exception as e:
                QtWidgets.QMessageBox.critical(
                    self,
                    "Error",
                    f"Could not delete file:\n{str(e)}"
                )
    
    def create_new_file(self, parent_folder):
        """Create new file in folder"""
        name, ok = QtWidgets.QInputDialog.getText(
            self,
            "New File",
            "Enter file name:",
            text="new_file.py"
        )
        
        if ok and name:
            try:
                new_file = parent_folder / name
                new_file.touch()
                self.refresh_project()
                print(f"✓ Created: {name}")
            except Exception as e:
                QtWidgets.QMessageBox.critical(
                    self,
                    "Error",
                    f"Could not create file:\n{str(e)}"
                )
    
    def create_new_folder(self, parent_folder):
        """Create new folder"""
        name, ok = QtWidgets.QInputDialog.getText(
            self,
            "New Folder",
            "Enter folder name:"
        )
        
        if ok and name:
            try:
                new_folder = parent_folder / name
                new_folder.mkdir(exist_ok=True)
                self.refresh_project()
                print(f"✓ Created folder: {name}")
            except Exception as e:
                QtWidgets.QMessageBox.critical(
                    self,
                    "Error",
                    f"Could not create folder:\n{str(e)}"
                )
    
    # def setup_file_watcher(self):
    #     """Setup file system watcher for auto-refresh"""
    #     if self.file_watcher:
    #         self.file_watcher.deleteLater()
        
    #     if not self.project_folder:
    #         return
        
    #     self.file_watcher = QtCore.QFileSystemWatcher()
    #     self.file_watcher.addPath(str(self.project_folder))
        
    #     # Watch subdirectories
    #     for subfolder in self.project_folder.rglob('*'):
    #         if subfolder.is_dir():
    #             self.file_watcher.addPath(str(subfolder))
        
    #     self.file_watcher.directoryChanged.connect(self.on_directory_changed)
    
    # def on_directory_changed(self, path):
    #     """Handle directory change event"""
    #     if self.auto_refresh_checkbox.isChecked():
    #         # Delay refresh slightly to avoid multiple rapid refreshes
    #         QtCore.QTimer.singleShot(500, self.refresh_project)
    
    # def toggle_auto_refresh(self, state):
    #     """Toggle auto-refresh on/off"""
    #     if state == QtCore.Qt.Checked:
    #         self.setup_file_watcher()
    #         print("✓ Auto-refresh enabled")
    #     else:
    #         if self.file_watcher:
    #             self.file_watcher.deleteLater()
    #             self.file_watcher = None
    #         print("✓ Auto-refresh disabled")

