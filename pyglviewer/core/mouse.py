import glfw
import imgui
import numpy as np
from pyglviewer.core.camera import Camera
from pyglviewer.utils.config import Config

# NOTE: Ideally use ImGui instead of glfw to get inputs

class Mouse:
    """Mouse input handler for camera control.
    
    Handles mouse movement, scrolling and button presses for camera manipulation.
    Uses ImGui for input capture and configuration for sensitivity settings.
    """

    def __init__(self, application):
        self.app = application # Reference to parent application
        self.last_x = 0
        self.last_y = 0
        # Cursor state tracking
        self.last_cursor = None
        self.uninitialised = True
        
        # Initialize configuration with defaults
        self.app.config.add("mouse.rotate_sensitivity", 0.1, "Sensitivity for rotation controls")
        self.app.config.add("mouse.base_pan_sensitivity", 0.0135, "Base sensitivity for panning")
        self.app.config.add("mouse.base_scroll_sensitivity", 0.6, "Base sensitivity for scrolling")
        self.app.config.add("mouse.invert_pan", [-1, -1], "Invert pan controls for X and Y axes")
        self.app.config.add("mouse.invert_yaw_pitch", [-1, -1], "Invert yaw and pitch controls")
        self.app.config.add("mouse.invert_scroll", -1, "Invert scroll direction")

    @property
    def pan_sensitivity(self):
        """Calculate pan sensitivity based on camera distance."""
        return self.app.config["mouse.base_pan_sensitivity"] * (self.app.camera.distance / 10) 
    
    @property
    def scroll_sensitivity(self):
        """Calculate scroll sensitivity based on camera distance."""
        return self.app.config["mouse.base_scroll_sensitivity"] * (self.app.camera.distance / 10)

    def process_input(self):
        """Process mouse input for camera control.
        
        Handles:
        - Left/middle click + drag for rotation
        - Ctrl + left/middle click for panning
        - Scroll wheel for zoom
        """

        # Update cursor
        self.update_cursor()
        
        io = imgui.get_io()

        if io.want_capture_mouse:
            return

        mouse_pos = io.mouse_pos
        mouse_delta = io.mouse_delta
        left_pressed = io.mouse_down[0]
        middle_pressed = io.mouse_down[2]
        ctrl_pressed = io.key_ctrl

        if self.uninitialised:
            self.last_x, self.last_y = mouse_pos.x, mouse_pos.y
            self.uninitialised = False

        xoffset = mouse_delta.x
        yoffset = mouse_delta.y

        if (left_pressed and ctrl_pressed) or (middle_pressed and ctrl_pressed):
            xoffset *= self.pan_sensitivity
            yoffset *= self.pan_sensitivity
            self.app.camera.pan(xoffset, yoffset, self.app.config["mouse.invert_pan"])
        elif left_pressed or middle_pressed:
            xoffset *= self.app.config["mouse.rotate_sensitivity"]
            yoffset *= self.app.config["mouse.rotate_sensitivity"]
            self.app.camera.rotate(xoffset, yoffset, self.app.config["mouse.invert_yaw_pitch"])

        # Handle scrolling
        wheel = io.mouse_wheel
        if wheel != 0:
            self.app.camera.zoom(-wheel * self.scroll_sensitivity * self.app.config["mouse.invert_scroll"])

        self.last_x, self.last_y = mouse_pos.x, mouse_pos.y
        
        


    def update_cursor(self):
        """Update the cursor based on ImGui state.
        These aren't currently called when setting up glfw so we need to call them manually."""
        io = imgui.get_io()
        
        if io.want_capture_mouse:
            # Get ImGui's desired cursor
            cursor = imgui.get_mouse_cursor()
            
            # Only update if cursor changed
            if cursor != self.last_cursor:
                # print(f"Cursor: {cursor}")
                if cursor == imgui.MOUSE_CURSOR_ARROW:
                    glfw.set_cursor(self.app.window, glfw.create_standard_cursor(glfw.ARROW_CURSOR))
                elif cursor == imgui.MOUSE_CURSOR_RESIZE_NS:
                    glfw.set_cursor(self.app.window, glfw.create_standard_cursor(glfw.VRESIZE_CURSOR))
                elif cursor == imgui.MOUSE_CURSOR_RESIZE_EW:
                    glfw.set_cursor(self.app.window, glfw.create_standard_cursor(glfw.HRESIZE_CURSOR))
                elif cursor == imgui.MOUSE_CURSOR_RESIZE_NESW:
                    glfw.set_cursor(self.app.window, glfw.create_standard_cursor(glfw.HRESIZE_CURSOR))  # RESIZE_NESW_CURSOR doesn't work
                elif cursor == imgui.MOUSE_CURSOR_RESIZE_NWSE:
                    glfw.set_cursor(self.app.window, glfw.create_standard_cursor(glfw.HRESIZE_CURSOR))  # RESIZE_NWSE_CURSOR doesn't work
                elif cursor == imgui.MOUSE_CURSOR_TEXT_INPUT:
                    glfw.set_cursor(self.app.window, glfw.create_standard_cursor(glfw.IBEAM_CURSOR))
                elif cursor == imgui.MOUSE_CURSOR_HAND:
                    glfw.set_cursor(self.app.window, glfw.create_standard_cursor(glfw.HAND_CURSOR))
                else:
                    glfw.set_cursor(self.app.window, glfw.create_standard_cursor(glfw.ARROW_CURSOR))
                    
                self.last_cursor = cursor
        else:
            # Reset to default cursor when not over ImGui windows
            if self.last_cursor is not None:
                glfw.set_cursor(self.app.window, glfw.create_standard_cursor(glfw.ARROW_CURSOR))
                self.last_cursor = None
                import numpy as np

    def world_to_screen(self, position):
        """Convert world coordinates to screen space position.
        
        Args:
            world_pos (tuple or np.ndarray): Position in world space (x, y, z)
            view_matrix (np.ndarray): 4x4 view matrix
            projection_matrix (np.ndarray): 4x4 projection matrix
            window_size (tuple): Window dimensions (width, height)
                
        Returns:
            tuple or None: (x, y) position in screen space (pixels), or None if behind camera
        """
        view_matrix = self.app.camera.get_view_matrix().T
        projection_matrix = self.app.camera.get_projection_matrix().T
        # Convert world_pos to homogeneous coordinates
        position = np.append(position, 1.0)
        
        # Transform to view space
        view_pos = view_matrix @ position
        
        # Check if point is behind camera
        if view_pos[2] > 0:  # OpenGL uses negative z for "in front"
            return (None, None)
            
        # Transform to clip space
        clip_pos = projection_matrix @ view_pos
        
        # Perspective divide to get NDC
        ndc = clip_pos[:3] / clip_pos[3]
        
        # Get window size
        width, height = self.app.window_width, self.app.window_height
        
        # Convert NDC to screen coordinates
        screen_x = (ndc[0] + 1.0) * width * 0.5
        screen_y = (1.0 - ndc[1]) * height * 0.5  # Flip Y coordinate
        
        return (screen_x, screen_y)
                
    def screen_to_world(self, screen_x, screen_y):
        """Convert screen coordinates to world space position.
        
        Args:
            screen_x (float): X coordinate in screen space (px)
            screen_y (float): Y coordinate in screen space (px)
            
        Returns:
            np.ndarray: Position in world space (x, y, z)
        """
        # Get matrices
        view_matrix = self.app.camera.get_view_matrix()
        projection_matrix = self.app.camera.get_projection_matrix()
        width, height = self.app.window_width, self.app.window_height

        # Convert screen coordinates to NDC
        ndc_x = (2.0 * screen_x) / width - 1.0
        ndc_y = 1.0 - (2.0 * screen_y) / height  # Flip Y coordinate
        
        # Get camera position
        inv_view = np.linalg.inv(view_matrix)
        camera_pos = inv_view[3, :3]
        
        # Convert NDC to view space
        inv_projection = np.linalg.inv(projection_matrix)
        point_ndc = np.array([ndc_x, ndc_y, 0.0, 1.0])
        point_view = inv_projection @ point_ndc
        point_view = point_view / point_view[3]  # Perspective divide
        
        # Convert view space point to world space
        world_pos = (inv_view @ np.append(point_view[:3], 1.0))[:3]
        world_pos += camera_pos
        
        return world_pos
    
    def screen_to_world_delta(self, screen_delta_x, screen_delta_y):
        """Convert a screen space delta to world space delta.
        
        Args:
            screen_delta_x (float): Change in X position in screen space (px)
            screen_delta_y (float): Change in Y position in screen space (px)
            
        Returns:
            np.ndarray: Change in position in world space (x, y, z)
        """
        # Get current mouse position
        io = imgui.get_io()
        current_x, current_y = io.mouse_pos.x, io.mouse_pos.y
        
        # Convert current position to world space
        current_world = self.screen_to_world(current_x, current_y)
        
        # Convert position + delta to world space
        next_world = self.screen_to_world(current_x + screen_delta_x, current_y + screen_delta_y)
        
        # Calculate the difference in world space
        world_delta = next_world - current_world
        
        return world_delta
    