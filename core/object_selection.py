import numpy as np
import imgui
from renderer.renderer import Renderer

class ObjectSelection:
    """Handles object selection based on mouse input."""
    def __init__(self, camera, renderer: Renderer, mouse, drag_objects=True):
        self.camera = camera
        self.renderer = renderer
        self.mouse = mouse
        self.drag_objects = drag_objects
    
    def process_input(self):
        if imgui.get_io().want_capture_mouse:
            return

        self.process_select()
        if self.drag_objects:
            self.process_drag()
    
    def process_select(self):
        if not self.camera.is_2d_mode:
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
    