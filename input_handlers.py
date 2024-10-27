import imgui
import glfw
import numpy as np
from parameters import parameters as p

# NOTE: Use ImGui instead of glfw to get inputs.

class Mouse:
    def __init__(self, camera):
        self.camera = camera
        self.last_x = 0
        self.last_y = 0
        self.uninitialised = True
        
        # Initialize parameters with defaults
        p.register("rotate_sensitivity", 0.1, "Sensitivity for rotation controls")
        p.register("base_pan_sensitivity", 0.0135, "Base sensitivity for panning")
        p.register("base_scroll_sensitivity", 0.6, "Base sensitivity for scrolling")
        p.register("invert_pan", [-1, -1], "Invert pan controls for X and Y axes")
        p.register("invert_yaw_pitch", [-1, -1], "Invert yaw and pitch controls")
        p.register("invert_scroll", -1, "Invert scroll direction")
        
    # Only keep the computed properties that actually do something
    @property
    def pan_sensitivity(self):
        return p["base_pan_sensitivity"] * (self.camera.distance / 10)

    @property
    def scroll_sensitivity(self):
        return p["base_scroll_sensitivity"] * (self.camera.distance / 10)

    def process_input(self):
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
            self.camera.pan(xoffset, yoffset, p["invert_pan"])
        elif left_pressed or middle_pressed:
            xoffset *= p["rotate_sensitivity"]
            yoffset *= p["rotate_sensitivity"]
            self.camera.rotate(xoffset, yoffset, p["invert_yaw_pitch"])

        # Handle scrolling
        wheel = io.mouse_wheel
        if wheel != 0:
            self.camera.zoom(-wheel * self.scroll_sensitivity * p["invert_scroll"])

        self.last_x, self.last_y = mouse_pos.x, mouse_pos.y

class Keyboard:
    def __init__(self, camera):
        self.camera = camera

    def process_input(self):
        io = imgui.get_io()

        if io.want_capture_keyboard:
            return

        speed = 0.5
        if io.keys_down[glfw.KEY_W]:
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

        if io.keys_down[glfw.KEY_Y]:
            self.camera.toggle_invert_yaw()
        if io.keys_down[glfw.KEY_P]:
            self.camera.toggle_invert_pitch()
