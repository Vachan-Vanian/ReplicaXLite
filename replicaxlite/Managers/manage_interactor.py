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


import pyvista as pv
import numpy as np
import os
from pathlib import Path

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from pyvistaqt import QtInteractor

class ReplicaXinteractorManager:
    def __init__(self, parent: 'QtInteractor', settings, model):
        self.interactor: 'QtInteractor' = parent
        self.settings = settings
        self.model = model
        self.display_model_actors = []
    
    def toggle_perspective_orthogonal_view(self):
        if self.interactor.camera.parallel_projection:
            self.interactor.camera.parallel_projection = False
        else:
            self.interactor.camera.parallel_projection = True

    def mesh_view_mode(self, mode, actor=None):
        """
        Set the view mode for mesh actors.
        
        Parameters:
        -----------
        mode : str
            One of "Surface with Edges", "Surface without Edges", or "Wireframe"
        actor : optional
            Specific actor to modify. If None, applies to all actors in the scene.
        """
        # Get list of actors to modify
        if actor is None:
            # Apply to all actors
            actors = self.interactor.renderer.actors.values()
        else:
            # Apply to specific actor only
            actors = [actor]
        
        # Apply the mode to each actor
        for act in actors:
            if mode == "Surface with Edges":
                act.GetProperty().SetRepresentationToSurface()
                act.GetProperty().EdgeVisibilityOn()
            elif mode == "Surface without Edges":
                act.GetProperty().SetRepresentationToSurface()
                act.GetProperty().EdgeVisibilityOff()
            elif mode == "Wireframe":
                act.GetProperty().SetRepresentationToWireframe()
            else:
                print(f"Invalid mode: {mode}")
                return
        
        # Refresh the render window
        self.interactor.render()

    def add_sphere(self):
        self.interactor.clear()
        mesh = pv.Sphere()
        actor = self.interactor.add_mesh(mesh)
        return actor
    
    def rotate_view_global(self, axis, angle):
        """
        Rotate the camera view around a global world axis.
        
        Parameters:
        -----------
        axis : str
            Global axis to rotate around: 'x', 'y', or 'z'
        angle : float
            Rotation angle in degrees
        """
        camera = self.interactor.camera
        import numpy as np
        
        # Get current camera parameters
        position = np.array(camera.GetPosition())
        focal_point = np.array(camera.GetFocalPoint())
        view_up = np.array(camera.GetViewUp())
        
        # Calculate vector from focal point to camera
        vector = position - focal_point
        
        # Convert angle to radians
        angle_rad = np.radians(angle)
        cos_a = np.cos(angle_rad)
        sin_a = np.sin(angle_rad)
        
        # Create rotation matrix based on axis
        if axis.lower() == 'x':
            # Rotation around X axis
            rotation_matrix = np.array([
                [1, 0, 0],
                [0, cos_a, -sin_a],
                [0, sin_a, cos_a]
            ])
        elif axis.lower() == 'y':
            # Rotation around Y axis
            rotation_matrix = np.array([
                [cos_a, 0, sin_a],
                [0, 1, 0],
                [-sin_a, 0, cos_a]
            ])
        elif axis.lower() == 'z':
            # Rotation around Z axis
            rotation_matrix = np.array([
                [cos_a, -sin_a, 0],
                [sin_a, cos_a, 0],
                [0, 0, 1]
            ])
        else:
            print(f"Invalid axis: {axis}. Use 'x', 'y', or 'z'")
            return
        
        # Rotate the camera position vector and view up vector
        rotated_vector = rotation_matrix @ vector
        rotated_view_up = rotation_matrix @ view_up
        
        # Set new camera position and view up
        new_position = focal_point + rotated_vector
        camera.SetPosition(new_position)
        camera.SetViewUp(rotated_view_up)
        
        # Reset the camera clipping range
        self.interactor.renderer.ResetCameraClippingRange()
        self.interactor.render()

    def move_camera_global(self, axis, distance_step):
        """
        Move camera along a global world axis.
        
        Parameters:
        -----------
        axis : str
            Global axis to move along: 'x', 'y', or 'z'
        distance : float
            Distance to move (positive or negative)
        """
        camera = self.interactor.camera
        
        # Get current camera parameters
        position = np.array(camera.GetPosition())
        focal_point = np.array(camera.GetFocalPoint())
        
        # Create movement vector based on axis
        if axis.lower() == 'x':
            movement = np.array([distance_step, 0, 0])
        elif axis.lower() == 'y':
            movement = np.array([0, distance_step, 0])
        elif axis.lower() == 'z':
            movement = np.array([0, 0, distance_step])
        else:
            print(f"Invalid axis: {axis}. Use 'x', 'y', or 'z'")
            return
        
        # Move both camera position and focal point
        camera.SetPosition(position + movement)
        camera.SetFocalPoint(focal_point + movement)
        
        # Reset the camera clipping range
        self.interactor.renderer.ResetCameraClippingRange()
        self.interactor.render()

    def take_screenshot(self, filename=None, transparent_background=False, scale=1):
        """
        Take a screenshot of the current view.
        
        Parameters:
        -----------
        filename : str, optional
            Output filename. If None, generates a timestamp-based name.
            Supported formats: .png, .jpg, .jpeg, .bmp, .tif, .tiff
        transparent_background : bool, optional
            If True, save with transparent background (PNG only). Default is False.
        scale : int, optional
            Resolution scale factor. Default is 1. Use 2 or higher for higher resolution.
        
        Returns:
        --------
        str : The path where the screenshot was saved
        """
        from datetime import datetime
        import tempfile
        
        # Generate filename if not provided
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"screenshot_{timestamp}.png"
        
        # Ensure file has an extension
        if not any(filename.endswith(ext) for ext in ['.png', '.jpg', '.jpeg', '.bmp', '.tif', '.tiff']):
            filename += '.png'
        
        # Determine save directory based on project folder setting
        project_folder = self.settings.get("project", {}).get("project_folder", "")
        
        if not project_folder or project_folder == "":
            # Use temporary directory if project folder is empty
            save_dir = tempfile.gettempdir()
        else:
            # Use project folder + UserData/screenshots
            save_dir = (Path(project_folder) / "UserData" / "screenshots").as_posix()
            # Create directory if it doesn't exist
            os.makedirs(save_dir, exist_ok=True)
        
        # Create full path
        abs_path = (Path(save_dir) / filename).as_posix()
        
        try:
            # Take the screenshot
            self.interactor.screenshot(
                filename=abs_path,
                transparent_background=transparent_background,
                scale=scale
            )
            print(f"Screenshot saved: {abs_path}")
            return abs_path
        except Exception as e:
            print(f"Error saving screenshot: {e}")
            return None


    #------------------------------------------------------------------------------

    def copy_to_interactor(self, original_plotter, actors_storage=[]):
        for name, actor in original_plotter.renderer.actors.items():
            self.interactor.renderer.add_actor(actor, name=name)
            actors_storage.append(actor)
        return actors_storage

    def clear_display_model(self):
        """Remove all actors added by display_model and clear the storage list."""
        for actor in self.display_model_actors:
            self.interactor.renderer.remove_actor(actor)
        self.display_model_actors.clear()
        self.interactor.render()

    def display_model(self, key=None):
        # Clear previous actors first
        self.clear_display_model()

        # Determine which key to use
        if key is None:
            key = self.settings.get("fem_model", {}).get("display_model")
        
        if key is None:
            self.interactor.render()
            return
        
        try:
            self.model[key].visualization.opsvis.set_plot_props(**self.settings["plot_props"])
            self.model[key].visualization.opsvis.set_plot_colors(**self.settings["plot_colors"])
            # Make sure model is built first
            if not self.model[key]._model_built:
                self.model[key].build_model()
            original_plotter = self.model[key].visualization.opsvis.plot_model(**self.settings["fem_model"]["group_plot_model"])
            self.copy_to_interactor(original_plotter, self.display_model_actors)
        except Exception as e:
            print(f"Error displaying model: {e}")
        
        self.interactor.render()
            
