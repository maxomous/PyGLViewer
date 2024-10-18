import glfw
import imgui

class Mouse:
    def __init__(self, window, camera):
        self.window = window
        self.camera = camera
        self.last_x = 400
        self.last_y = 300
        self.first_mouse = True
        self.left_pressed = False
        self.middle_pressed = False
        self.rotate_sensitivity = 0.1
        self.base_pan_sensitivity = 0.0135
        self.base_scroll_sensitivity = 0.6
        self.invert_pan = [-1, -1]
        self.invert_yaw_pitch = [-1, -1]

        glfw.set_mouse_button_callback(window, self.mouse_button_callback)
        glfw.set_cursor_pos_callback(window, self.mouse_callback)
        glfw.set_scroll_callback(window, self.scroll_callback)

    @property
    def pan_sensitivity(self):
        # Adjust pan sensitivity based on camera distance
        return self.base_pan_sensitivity * (self.camera.distance / 10)  # Adjust this formula as needed

    @property
    def scroll_sensitivity(self):
        # Adjust scroll sensitivity based on camera distance
        return self.base_scroll_sensitivity * (self.camera.distance / 10)  # Adjust this formula as needed

    def mouse_button_callback(self, window, button, action, mods):       
        if imgui.get_io().want_capture_mouse:
            return
        if button == glfw.MOUSE_BUTTON_LEFT:
            self.left_pressed = action == glfw.PRESS
        elif button == glfw.MOUSE_BUTTON_MIDDLE:
            self.middle_pressed = action == glfw.PRESS

    def mouse_callback(self, window, xpos, ypos):
        if imgui.get_io().want_capture_mouse:
            return
        if self.first_mouse:
            self.last_x, self.last_y = xpos, ypos
            self.first_mouse = False
        
        xoffset = xpos - self.last_x
        yoffset = ypos - self.last_y
        self.last_x, self.last_y = xpos, ypos

        ctrl_pressed = glfw.get_key(self.window, glfw.KEY_LEFT_CONTROL) == glfw.PRESS
        if (self.left_pressed and ctrl_pressed) or (self.middle_pressed and ctrl_pressed):
            xoffset *= self.pan_sensitivity
            yoffset *= self.pan_sensitivity
            self.camera.pan(xoffset, yoffset, self.invert_pan)
        elif self.left_pressed or self.middle_pressed:
            xoffset *= self.rotate_sensitivity
            yoffset *= self.rotate_sensitivity
            self.camera.rotate(xoffset, yoffset, self.invert_yaw_pitch)

    def scroll_callback(self, window, xoffset, yoffset):
        if imgui.get_io().want_capture_mouse:
            return
        self.camera.zoom(-yoffset * self.scroll_sensitivity)

class Keyboard:
    def __init__(self, window, camera):
        self.window = window
        self.camera = camera

    def process_input(self):
        if imgui.get_io().want_capture_keyboard:
            return
        if glfw.get_key(self.window, glfw.KEY_ESCAPE) == glfw.PRESS:
            glfw.set_window_should_close(self.window, True)

        speed = 0.5
        if glfw.get_key(self.window, glfw.KEY_W) == glfw.PRESS:
            self.camera.move("FORWARD", speed)
        if glfw.get_key(self.window, glfw.KEY_S) == glfw.PRESS:
            self.camera.move("BACKWARD", speed)
        if glfw.get_key(self.window, glfw.KEY_A) == glfw.PRESS:
            self.camera.move("LEFT", speed)
        if glfw.get_key(self.window, glfw.KEY_D) == glfw.PRESS:
            self.camera.move("RIGHT", speed)

        if glfw.get_key(self.window, glfw.KEY_Q) == glfw.PRESS:
            self.camera.zoom(0.1)
        if glfw.get_key(self.window, glfw.KEY_E) == glfw.PRESS:
            self.camera.zoom(-0.1)

        if glfw.get_key(self.window, glfw.KEY_Y) == glfw.PRESS:
            self.camera.toggle_invert_yaw()
        if glfw.get_key(self.window, glfw.KEY_P) == glfw.PRESS:
            self.camera.toggle_invert_pitch()
