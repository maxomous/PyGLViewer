import imgui
from core.camera import Camera
from utils.config import Config

# NOTE: You should ideally use ImGui instead of glfw to get inputs

class Mouse:
    """Mouse input handler for camera control.
    
    Handles mouse movement, scrolling and button presses for camera manipulation.
    Uses ImGui for input capture and configuration for sensitivity settings.
    """

    def __init__(self, camera, config):
        self.camera = camera
        self.config = config
        self.last_x = 0
        self.last_y = 0
        self.uninitialised = True
        
        # Initialize configuration with defaults
        self.config.add("mouse.rotate_sensitivity", 0.1, "Sensitivity for rotation controls")
        self.config.add("mouse.base_pan_sensitivity", 0.0135, "Base sensitivity for panning")
        self.config.add("mouse.base_scroll_sensitivity", 0.6, "Base sensitivity for scrolling")
        self.config.add("mouse.invert_pan", [-1, -1], "Invert pan controls for X and Y axes")
        self.config.add("mouse.invert_yaw_pitch", [-1, -1], "Invert yaw and pitch controls")
        self.config.add("mouse.invert_scroll", -1, "Invert scroll direction")

    @property
    def pan_sensitivity(self):
        """Calculate pan sensitivity based on camera distance."""
        return self.config["mouse.base_pan_sensitivity"] * (self.camera.distance / 10) 
    
    @property
    def scroll_sensitivity(self):
        """Calculate scroll sensitivity based on camera distance."""
        return self.config["mouse.base_scroll_sensitivity"] * (self.camera.distance / 10)

    def process_input(self):
        """Process mouse input for camera control.
        
        Handles:
        - Left/middle click + drag for rotation
        - Ctrl + left/middle click for panning
        - Scroll wheel for zoom
        """

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
            self.camera.pan(xoffset, yoffset, self.config["mouse.invert_pan"])
        elif left_pressed or middle_pressed:
            xoffset *= self.config["mouse.rotate_sensitivity"]
            yoffset *= self.config["mouse.rotate_sensitivity"]
            self.camera.rotate(xoffset, yoffset, self.config["mouse.invert_yaw_pitch"])

        # Handle scrolling
        wheel = io.mouse_wheel
        if wheel != 0:
            self.camera.zoom(-wheel * self.scroll_sensitivity * self.config["mouse.invert_scroll"])

        self.last_x, self.last_y = mouse_pos.x, mouse_pos.y