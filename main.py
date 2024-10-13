# https://visualstudio.microsoft.com/visual-cpp-build-tools/ -> Desktop development with C++
# pip install PyOpenGL
# pip install PyOpenGL_accelerate (optional)
# pip install glfw
# pip install imgui[glfw]

# To install docking branch
#   git clone https://github.com/pyimgui/pyimgui.git
#   cd pyimgui
#   git checkout docking
#   pip install .[glfw]
#   set ENABLE_DOCKING = True

import glfw
from OpenGL.GL import *
import numpy as np
from renderer import Renderer, Shader, BufferType, basic_vertex_shader, basic_fragment_shader
from geometry import Geometry
from color import Color
from camera import ThirdPersonCamera
import math
import imgui
from imgui.integrations.glfw import GlfwRenderer

ENABLE_DOCKING = True  # Set this to False to disable docking

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
        self.pan_sensitivity = 0.001
        self.scroll_sensitivity = 0.4
        self.invert_pan = [-1, 1]
        self.invert_yaw_pitch = [-1, 1]

        glfw.set_mouse_button_callback(window, self.mouse_button_callback)
        glfw.set_cursor_pos_callback(window, self.mouse_callback)
        glfw.set_scroll_callback(window, self.scroll_callback)

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
        yoffset = self.last_y - ypos  # Reversed since y-coordinates go from bottom to top
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
        print(yoffset)
        if imgui.get_io().want_capture_mouse:
            return
        print(yoffset)
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

class Application:
    def __init__(self, width, height, title):
        self.width = width
        self.height = height
        self.title = title
        self.window = None
        self.camera = None
        self.renderer = None
        self.shader = None
        self.projection = None
        self.mouse = None
        self.keyboard = None
        self.imgui_renderer = None
        self.dock_space_id = None

    def init(self):
        if not glfw.init():
            return False

        self.window = glfw.create_window(self.width, self.height, self.title, None, None)
        if not self.window:
            glfw.terminate()    
            return False
        
        glfw.make_context_current(self.window)
        glEnable(GL_DEPTH_TEST) # dont draw triangles facing the wrong way 
        glEnable(GL_CULL_FACE)  # dont draw vertices outside of our visible depth
        
        self.camera = ThirdPersonCamera(position=(5, 0, 2), target=(0, 0, -0), up=(0, 0, 1), distance=9)

        self.mouse = Mouse(self.window, self.camera)
        self.keyboard = Keyboard(self.window, self.camera)

        self.shader = Shader(basic_vertex_shader, basic_fragment_shader)
        self.init_renderer()
        self.projection = self.camera.get_perspective_projection(45.0, self.width / self.height, 0.1, 100.0)

        # Initialize ImGui
        print(imgui.get_version())
        imgui.create_context()
        io = imgui.get_io()
        if ENABLE_DOCKING:
            io.config_flags |= imgui.CONFIG_DOCKING_ENABLE
        self.imgui_renderer = GlfwRenderer(self.window, attach_callbacks=False)

        # Set ImGui style (optional)
        style = imgui.get_style()
        style.colors[imgui.COLOR_TEXT] = (1.0, 1.0, 1.0, 1.0)
        style.colors[imgui.COLOR_WINDOW_BACKGROUND] = (0.1, 0.1, 0.1, 0.7)

        # Set up the framebuffer size callback
        glfw.set_framebuffer_size_callback(self.window, self.framebuffer_size_callback_impl)

        return True

    def framebuffer_size_callback_impl(self, window, width, height):
        glViewport(0, 0, width, height)
        self.width = width
        self.height = height
        self.projection = self.camera.get_perspective_projection(45.0, self.width / self.height, 0.1, 100.0)

    def init_renderer(self):
        self.renderer = Renderer()
        self.renderer.add_cube((-1, 0, 0), 0.5, Color.RED, self.shader, buffer_type=BufferType.Static, show_wireframe=True)
        self.renderer.add_cube((0, 0, 0), 0.5, Color.GREEN, self.shader, buffer_type=BufferType.Static, show_wireframe=True)
        self.renderer.add_cube((1, 0, 0), 0.5, Color.BLUE, self.shader, buffer_type=BufferType.Static, show_wireframe=True)
        self.renderer.add_cube((0, 1, 0), 0.5, Color.rgb(128, 64, 32), self.shader, buffer_type=BufferType.Static, show_wireframe=True)

        self.renderer.add_axis(10.0, self.shader)
        grid_color = Color.rgb(100, 100, 100)  # Light gray color
        self.renderer.add_grid((0, 0, 0), 20.0, 1.0, grid_color, self.shader)

    def run(self):
        while not glfw.window_should_close(self.window):
            self.renderer.clear()
            self.keyboard.process_input()
            self.imgui_renderer.process_inputs()
            # Start new ImGui frame
            imgui.new_frame()

            if ENABLE_DOCKING:
                # Create dockspace
                flags = imgui.WINDOW_MENU_BAR | imgui.WINDOW_NO_DOCKING
                imgui.begin("DockSpace Demo", True, flags)

                # Get the current window size and create a dockspace that fills it
                width, height = glfw.get_window_size(self.window)
                imgui.set_next_window_size(width, height)
                imgui.set_next_window_position(0, 0)

                dockspace_flags = 0  # imgui.DOCKNODE_PASSTHRU_CENTRAL_NODE
                self.dock_space_id = imgui.get_id("MyDockSpace")
                imgui.dockspace(self.dock_space_id, (0, 0), dockspace_flags)

            # Create your ImGui windows and widgets here
            imgui.begin("Debug Window")
            imgui.text(f"Camera Position: {self.camera.position}")
            imgui.text(f"Camera Target: {self.camera.target}")
            imgui.text(f"FPS: {1.0 / glfw.get_time():.1f}")
            glfw.set_time(0)  # Reset the timer
            imgui.end()

            # Show the demo window (optional, for testing)
            imgui.show_demo_window()

            if ENABLE_DOCKING:
                imgui.end()  # End dockspace

            view_matrix = self.camera.get_view_matrix()

            self.shader.use()
            self.shader.set_uniform("view", view_matrix)
            self.shader.set_uniform("projection", self.projection)

            self.renderer.draw()

            # Render ImGui
            imgui.render()
            self.imgui_renderer.render(imgui.get_draw_data())
            
            glfw.swap_buffers(self.window)
            glfw.poll_events()

        # Cleanup
        self.imgui_renderer.shutdown()
        glfw.terminate()


if __name__ == "__main__":
    app = Application(800, 600, "Third Person Camera")
    if app.init():
        app.run()
