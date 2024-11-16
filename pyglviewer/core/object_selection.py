import numpy as np
import imgui
from OpenGL.GL import GL_POINTS, GL_LINES
from pyglviewer.renderer.renderer import Renderer
from pyglviewer.renderer.geometry import Geometry
from pyglviewer.renderer.objects import BufferType
from pyglviewer.utils.colour import Colour

class SelectionSettings:
    def __init__(self, show_cursor_point=True, select_objects=True, drag_objects=False):
        self.show_cursor_point = show_cursor_point
        self.select_objects = select_objects
        self.drag_objects = drag_objects

class ObjectSelection:
    """Handles object selection based on mouse input."""
    def __init__(self, camera, renderer: Renderer, mouse, settings: SelectionSettings):
        self.camera = camera
        self.renderer = renderer
        self.mouse = mouse
        self.settings = settings
        self.target_edge_length = 0.02
        self.cursor_point = self.renderer.add_blank_object(draw_type=GL_POINTS, buffer_type=BufferType.Dynamic, selectable=False)
        self.selected_object = self.renderer.add_blank_object(draw_type=GL_LINES, buffer_type=BufferType.Dynamic, selectable=False)
        
    def process_input(self):
        if imgui.get_io().want_capture_mouse:
            return

        self.process_select()
        self.process_drag()
        self.process_cursor_point()
        self.process_selection_targets()
    
    def process_select(self):
        if not self.settings.select_objects or not self.camera.is_2d_mode:
            return
        
        io = imgui.get_io()
        # Handle object selection on left click
        if io.mouse_down[imgui.MOUSE_BUTTON_LEFT]:  # Left mouse button
            picked_object = self.get_object_under_cursor(io.mouse_pos[0], io.mouse_pos[1])
            
            # Clear previous selection if not holding shift
            if not io.key_shift:
                for obj in self.renderer.objects:
                    if hasattr(obj, 'selected'):
                        obj.selected = False
            
            # Select the picked object
            if picked_object:
                picked_object.toggle_selection()
            
    def process_drag(self):
        '''Drag selected objects with left mouse button pressed.'''
        if not self.settings.drag_objects:
            return
        
        # Drag selected objects
        if imgui.is_mouse_dragging(imgui.MOUSE_BUTTON_LEFT):
            selected_objects = self.renderer.get_selected_objects() 
            # Set initial object positions
            if not hasattr(self, 'object_start_pos') or self.object_start_pos is None:
                self.object_start_pos = [obj.get_translate().copy() for i, obj in enumerate(selected_objects)] if len(selected_objects) > 0 else None

            # Get mouse delta & convert to world space
            mouse_delta = imgui.get_mouse_drag_delta()
            print(f'mouse_delta: {mouse_delta}   ')
            x, y, _ = self.mouse.screen_to_world_delta(mouse_delta.x, mouse_delta.y)
            
            for i, obj in enumerate(selected_objects):
                # Set new object transform
                translate = self.object_start_pos[i] + np.array([x, y, 0.0])
                obj.set_translate(translate)
                
        if imgui.is_mouse_released(imgui.MOUSE_BUTTON_LEFT):
            self.object_start_pos = None
            
    def process_cursor_point(self):
        # Draw cursor point
        if hasattr(self.renderer, 'cursor_pos'):
            self.cursor_point.set_geometry_data(Geometry.create_point(self.renderer.cursor_pos, color=Colour.WHITE))
        
    def process_selection_targets(self):
        # Draw target on selected objects
        selected_geometry = Geometry.create_blank()
        # Get object under cursor
        if selected_objects := self.renderer.get_selected_objects():
            # Create a single geometry with multiple rectangles to indicate each selected object
            for i, obj in enumerate(selected_objects):
                if bounds := obj.get_bounds():
                    offset = self.camera.distance * 0.01
                    width, height, _ = (bounds['max'] - bounds['min']) + np.array([offset, offset, 0])
                    mid_x, mid_y, _ = obj.get_mid_point()
                    edge_length = self.camera.distance * self.target_edge_length
                    selected_geometry += Geometry.create_rectangle_target(mid_x, mid_y, width, height, edge_length, Colour.WHITE) 

        self.selected_object.set_geometry_data(selected_geometry)
        
    def get_object_under_cursor(self, cursor_x, cursor_y):
        """Determine which object is under the cursor"""
        world_pos = self.mouse.screen_to_world(cursor_x, cursor_y)
        self.renderer.cursor_pos = world_pos
        
        # Test intersection with objects
        valid_hits = []
        for obj in self.renderer.objects:
            hit, distance = obj.intersect_cursor(world_pos, self.camera.distance)
            if hit and distance > 0 and distance < float('inf'):
                valid_hits.append((distance, obj))
        
        if not valid_hits:
            return None
            
        # Sort by distance and get closest
        valid_hits.sort(key=lambda x: x[0])
        return valid_hits[0][1]
