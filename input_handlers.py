import imgui
import glfw
import numpy as np

# NOTE: Use ImGui instead of glfw to get inputs.

class Mouse:
    def __init__(self, camera):
        self.camera = camera
        self.last_x = 400
        self.last_y = 300
        self.first_mouse = True
        self.rotate_sensitivity = 0.1
        self.base_pan_sensitivity = 0.0135
        self.base_scroll_sensitivity = 0.6
        self.invert_pan = [-1, -1]
        self.invert_yaw_pitch = [-1, -1]

    @property
    def pan_sensitivity(self):
        return self.base_pan_sensitivity * (self.camera.distance / 10)

    @property
    def scroll_sensitivity(self):
        return self.base_scroll_sensitivity * (self.camera.distance / 10)

    def process_input(self):
        io = imgui.get_io()

        if io.want_capture_mouse:
            return

        mouse_pos = io.mouse_pos
        mouse_delta = io.mouse_delta
        left_pressed = io.mouse_down[0]
        middle_pressed = io.mouse_down[2]
        ctrl_pressed = io.key_ctrl

        if self.first_mouse:
            self.last_x, self.last_y = mouse_pos.x, mouse_pos.y
            self.first_mouse = False

        xoffset = mouse_delta.x
        yoffset = mouse_delta.y

        if (left_pressed and ctrl_pressed) or (middle_pressed and ctrl_pressed):
            xoffset *= self.pan_sensitivity
            yoffset *= self.pan_sensitivity
            self.camera.pan(xoffset, yoffset, self.invert_pan)
        elif left_pressed or middle_pressed:
            xoffset *= self.rotate_sensitivity
            yoffset *= self.rotate_sensitivity
            self.camera.rotate(xoffset, yoffset, self.invert_yaw_pitch)

        # Handle scrolling
        wheel = io.mouse_wheel
        if wheel != 0:
            self.camera.zoom(-wheel * self.scroll_sensitivity)

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
