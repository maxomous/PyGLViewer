import imgui
import glfw
# NOTE: You should ideally use ImGui instead of glfw to get inputs

class Keyboard:
    """Keyboard input handler for camera control.
    
    Handles WASD movement, zoom keys, and camera inversion toggles.
    
    Args:
        camera: Camera instance to control
    """

    def __init__(self, camera):
        self.camera = camera

    def process_input(self):
        """Process keyboard input for camera control.
        
        Handles:
        - WASD keys for camera movement
        - Numpad +/- for zoom
        """

        io = imgui.get_io()

        if io.want_capture_keyboard:
            return

        speed = 0.5
        if io.keys_down[glfw.KEY_X]:
            self.camera.move("FORWARD", speed)
        if io.keys_down[glfw.KEY_S]:
            self.camera.move("BACKWARD", speed)
        if io.keys_down[glfw.KEY_A]:
            self.camera.move("LEFT", speed)
        if io.keys_down[glfw.KEY_D]:
            self.camera.move("RIGHT", speed)

        if io.keys_down[glfw.KEY_KP_ADD]:
            self.camera.zoom(0.1)
        if io.keys_down[glfw.KEY_KP_SUBTRACT]:
            self.camera.zoom(-0.1)

