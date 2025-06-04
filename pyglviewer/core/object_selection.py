import numpy as np
import imgui
from typing import Callable
from OpenGL.GL import GL_POINTS, GL_LINES
from pyglviewer.renderer.renderer import Renderer
from pyglviewer.renderer.shapes import Shapes
from pyglviewer.utils.colour import Colour


class SelectionSettings:
    def __init__(self, show_cursor_point=True, select_objects=True, drag_objects=True, select_callback: Callable = None, drag_callback: Callable = None):
        self.show_cursor_point = show_cursor_point
        self.select_objects = select_objects
        self.drag_objects = drag_objects
        # Callbacks
        self.select_callback = select_callback
        self.drag_callback = drag_callback

class ObjectSelection:
    """Handles object selection based on mouse input."""
    def __init__(self, camera, renderer: Renderer, mouse, settings: SelectionSettings):
        self.camera = camera
        self.renderer = renderer
        self.mouse = mouse
        self.settings = settings
        self.target_edge_length = 0.02 
        self.min_selection_distance = 2.0
        
        self.cursor_point = self.renderer.add_object(selectable=False)
        self.selection_target = self.renderer.add_object(selectable=False)
        self.selected_objects_containers = []
        
    def process_input(self):
        # Always update selection targets
        self.process_selection_targets()
        
        if imgui.get_io().want_capture_mouse:
            return

        self.process_select()
        self.process_drag()
        self.process_release()
        self.process_cursor_point()
    
    def process_select(self):
        if not self.settings.select_objects or not self.camera.is_2d_mode:
            return
        
        # Handle object selection on left click
        if self.mouse.left_click:  # Left mouse click
            picked_object_container = self.get_object_container_under_cursor(self.mouse.position)
            
            # Clear previous selection if not holding shift
            if not self.mouse.shift_down:
                for container in self.renderer.object_containers:
                    for obj in container._objects:
                        obj.selected = False
            
            # Select the picked object
            if picked_object_container:
                for obj in picked_object_container._objects:
                    obj.toggle_selection()
                    # Call callback with object
                    if self.settings.select_callback:
                        self.settings.select_callback(obj)
        
            # Get selected objects to set the start positions
            self.selected_objects_containers = self.renderer.get_selected_object_containers() 
            # Set initial object positions
            if not hasattr(self, 'object_start_pos') or self.object_start_pos is None:
                self.object_start_pos = []
                for container in self.selected_objects_containers:
                    self.object_start_pos.append([obj.get_translate().copy() for obj in container._objects])
                    
    def process_drag(self):
        '''Drag selected objects with left mouse button pressed.'''
        if not self.settings.drag_objects:
            return
        if self.mouse.is_panning or self.mouse.is_rotating:
            return
        
        # Drag selected objects
        if self.mouse.left_down:
            # Get mouse delta & convert to world space
            mouse_delta_x = self.mouse.screen_to_world(self.mouse.click_position_delta[0])
            mouse_delta_y = self.mouse.screen_to_world(-self.mouse.click_position_delta[1])
            mouse_delta = np.array([mouse_delta_x, mouse_delta_y, 0.0])
            
            if not hasattr(self, 'object_start_pos') or self.object_start_pos is None or self.object_start_pos == []:
                return
            
            for i, container in enumerate(self.selected_objects_containers):
                for j, obj in enumerate(container._objects):
                    # Set new object transform
                    translate = self.object_start_pos[i][j] + mouse_delta
                    obj.set_translate(translate)
                    # Call callback with object
                    if self.settings.drag_callback:
                        self.settings.drag_callback(obj)
                
    def process_release(self):
        '''Release left mouse button.'''
        if imgui.is_mouse_released(imgui.MOUSE_BUTTON_LEFT):
            self.object_start_pos = None
            
    def process_cursor_point(self):
        # Draw cursor point
        if hasattr(self.renderer, 'cursor_pos'):
            self.cursor_point.set_shapes(Shapes.point(self.renderer.cursor_pos, colour=Colour.WHITE))
        
    def process_selection_targets(self):
        # Draw target on selected objects
        selected_geometry = Shapes.blank(GL_LINES)
        # Get object under cursor
        for container in self.renderer.get_selected_object_containers():
            bounds = container.get_bounds()
            mid_point = container.get_mid_point()
            size = (bounds['max'] - bounds['min'])

            # Get offset for target size
            offset = self.mouse.screen_to_world(10)
            if container._objects[0].draw_type == GL_POINTS:
                offset += self.mouse.screen_to_world(container._objects[0]._point_size)
                
            edge_length = self.camera.distance * self.target_edge_length
            selected_geometry += Shapes.target(mid_point, size + np.array([offset, offset, offset]), edge_length, Colour.WHITE) 

        self.selection_target.set_shapes(selected_geometry)
        
    def get_object_container_under_cursor(self, cursor_pos):
        """Determine which object is under the cursor"""
        cursor_world_pos = self.mouse.project_screen_to_world(cursor_pos)
        self.renderer.cursor_pos = cursor_world_pos
        
        scale_factor = self.mouse.screen_to_world(1)
        
        # Test intersection with objects
        valid_hits = []
        for container in self.renderer.object_containers:
            for obj in container._objects:
                hit, distance = self.intersect_cursor(obj, cursor_world_pos, scale_factor, min_distance=self.min_selection_distance)
                if hit and distance > 0 and distance < float('inf'):
                    valid_hits.append((distance, container))
        
        if not valid_hits:
            return None
            
        # Sort by distance and get closest
        valid_hits.sort(key=lambda x: x[0])
        return valid_hits[0][1]

    @staticmethod
    def intersect_cursor(obj, cursor_pos, scale_factor, min_distance):
        """Intersect ray with object bounds.
        
        Parameters
        ----------
        obj : Object
            Object to test intersection with
        cursor_pos : np.ndarray
            Cursor position in world space
        scale_factor : float
            Scale factor for point size (default: 1.0)
        min_distance : float
            Minimum distance to intersection in px
        
        Returns
        -------
        tuple
            (bool, float) - (intersection found, distance to intersection)
        """
        if not obj._selectable:
            return False, float('inf')
        bounds = obj.get_bounds()
        if bounds is None:
            return False, float('inf')
        
        # Expand bounds by offset
        scale = scale_factor * min_distance
        # Expand bounds by point_size if this is a point object
        if obj.draw_type == GL_POINTS:
            scale += scale_factor * obj._point_size / 2
        
        bounds['min'] = bounds['min'] - np.array([scale, scale, scale])
        bounds['max'] = bounds['max'] + np.array([scale, scale, scale])
            
        cursor_pos = np.round(cursor_pos, 3)
        if cursor_pos[0] >= bounds['min'][0] and cursor_pos[0] <= bounds['max'][0] and \
           cursor_pos[1] >= bounds['min'][1] and cursor_pos[1] <= bounds['max'][1]:
            midpoint = (bounds['min'] + bounds['max']) / 2
            distance = np.linalg.norm(cursor_pos - midpoint)
            return True, distance
        else:
            return False, float('inf')
        