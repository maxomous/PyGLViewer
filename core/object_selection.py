import numpy as np
import imgui
from renderer.renderer import Renderer

class ObjectSelection:
    """Handles object selection based on mouse input."""
    def __init__(self, camera, renderer: Renderer):
        self.camera = camera
        self.renderer = renderer
    
    def process_input(self, width, height):
        io = imgui.get_io()
        if io.want_capture_mouse:
            return
        
        # Handle object selection on left click
        if io.mouse_down[imgui.MOUSE_BUTTON_LEFT]:  # Left mouse button
            picked_object = self.get_object_under_cursor(io.mouse_pos[0], io.mouse_pos[1], width, height)
            
            # Clear previous selection if not holding shift
            if not io.key_shift:
                for obj in self.renderer.objects:
                    if hasattr(obj, 'selected'):
                        obj.selected = False
            
            # Select the picked object
            if picked_object:
                picked_object.toggle_selection()
            
    def get_object_under_cursor(self, cursor_x, cursor_y, width, height):
        """Determine which object is under the cursor using ray casting.
        
        Args:
            cursor_x (float): Cursor X position in screen coordinates
            cursor_y (float): Cursor Y position in screen coordinates
            
        Returns:
            object: The picked object or None if nothing was hit
        """
        # Convert screen coordinates to NDC
        ndc_x, ndc_y = self.screen_to_ndc(cursor_x, cursor_y, width, height)
        # Get matrices
        view = self.camera.get_view_matrix()
        projection = self.camera.get_projection_matrix()
        
        # Let the renderer handle the actual picking
        return self.pick_object(ndc_x, ndc_y, view, projection)


    def pick_object(self, ndc_x, ndc_y, view_matrix, projection_matrix):
        """Optimized object picking."""
       
        # Get camera position (ray origin) in world space
        inv_view = np.linalg.inv(view_matrix)
        camera_pos = inv_view[3, :3]
        
        # Convert NDC to view space
        inv_projection = np.linalg.inv(projection_matrix)
        
        # Point on near plane
        point_ndc = np.array([ndc_x, ndc_y, 0.0, 1.0])
        point_view = inv_projection @ point_ndc
        point_view = point_view / point_view[3]  # Perspective divide
        
        # Convert view space point to world space
        self.renderer.cursor_pos = (inv_view @ np.append(point_view[:3], 1.0))[:3]
        self.renderer.cursor_pos += (camera_pos[0], camera_pos[1], 0)        
        
        # Test intersection with objects
        valid_hits = []
        
        for i, obj in enumerate(self.renderer.objects):
            hit, distance = obj.intersect_cursor(self.renderer.cursor_pos, self.camera.distance)
            if hit and distance > 0 and distance < float('inf'):
                valid_hits.append((distance, obj))
        
        if not valid_hits:
            return None
            
        # Sort by distance and get closest
        valid_hits.sort(key=lambda x: x[0])
        closest_hit = valid_hits[0]
        
        return closest_hit[1]

    def screen_to_ndc(self, screen_x, screen_y, width, height):
        """Convert screen coordinates to normalized device coordinates (NDC).
        
        Args:
            screen_x (float): X coordinate in screen space
            screen_y (float): Y coordinate in screen space
            
        Returns:
            tuple: (x, y) in NDC space (-1 to 1)
        """
        # Convert to NDC
        ndc_x = (2.0 * screen_x) / width - 1.0
        ndc_y = 1.0 - (2.0 * screen_y) / height  # Flip Y coordinate
        return ndc_x, ndc_y

