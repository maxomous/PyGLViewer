# https://visualstudio.microsoft.com/visual-cpp-build-tools/ -> Desktop development with C++
# pip install PyOpenGL
# pip install PyOpenGL_accelerate (optional)
# pip install glfw
# pip install imgui[glfw]

# To install docking branch
#   git clone https://github.com/pyimgui/pyimgui.git
#   cd pyimgui
#   git checkout docking
#   pip install .[glfw] (this takes a while)
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
from light import Light, LightType

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
        self.invert_yaw_pitch = [-1, -1]

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

class ImGuiManager:
    def __init__(self, window, enable_docking=True):
        self.window = window
        self.enable_docking = enable_docking
        self.imgui_renderer = None
        self.init_imgui()

    def init_imgui(self):
        imgui.create_context()
        io = imgui.get_io()
        if self.enable_docking:
            io.config_flags |= imgui.CONFIG_DOCKING_ENABLE
        self.imgui_renderer = GlfwRenderer(self.window, attach_callbacks=False)

        # Set ImGui style (optional)
        style = imgui.get_style()
        style.colors[imgui.COLOR_TEXT] = (1.0, 1.0, 1.0, 1.0)
        style.colors[imgui.COLOR_WINDOW_BACKGROUND] = (0.1, 0.1, 0.1, 0.7)

    def new_frame(self):
        imgui.new_frame()

    def render(self):
        imgui.render()
        self.imgui_renderer.render(imgui.get_draw_data())

    def process_inputs(self):
        self.imgui_renderer.process_inputs()

    def shutdown(self):
        self.imgui_renderer.shutdown()

    def render_dockspace(self):
        if not self.enable_docking:
            return

        viewport = imgui.get_main_viewport()
        padding = 10.0
        toolbar_height = 0  # Set to 0 if no toolbar

        pos_x = viewport.work_pos[0] + padding
        pos_y = viewport.work_pos[1] + padding + (toolbar_height if toolbar_height else 0)
        size_x = viewport.work_size[0] - 2 * padding
        size_y = viewport.work_size[1] - 2 * padding - (toolbar_height if toolbar_height else 0)

        imgui.set_next_window_position(pos_x, pos_y)
        imgui.set_next_window_size(size_x, size_y)
        imgui.set_next_window_viewport(viewport.id)

        window_flags = (
            imgui.WINDOW_NO_BACKGROUND | 
            imgui.WINDOW_NO_DOCKING | 
            imgui.WINDOW_NO_TITLE_BAR | 
            imgui.WINDOW_NO_COLLAPSE | 
            imgui.WINDOW_NO_RESIZE | 
            imgui.WINDOW_NO_MOVE | 
            imgui.WINDOW_NO_BRING_TO_FRONT_ON_FOCUS | 
            imgui.WINDOW_NO_NAV_FOCUS
        )

        imgui.push_style_var(imgui.STYLE_WINDOW_PADDING, (0.0, 0.0))
        imgui.begin("DockSpace", None, window_flags)
        imgui.pop_style_var()

        dockspace_flags = (
            imgui.DOCKNODE_PASSTHRU_CENTRAL_NODE |
            imgui.DOCKNODE_NO_DOCKING_IN_CENTRAL_NODE
        )
        imgui.dockspace(imgui.get_id("DockSpace"), (0.0, 0.0), dockspace_flags)

    def end_dockspace(self):
        if self.enable_docking:
            imgui.end()

class Application:
    def __init__(self, width, height, title):
        self.width = width
        self.height = height
        self.title = title
        self.window = None
        self.camera = None
        self.renderer = None
        self.projection = None
        self.mouse = None
        self.keyboard = None
        self.imgui_manager = None

    def init(self):
        if not glfw.init():
            return False

        self.window = glfw.create_window(self.width, self.height, self.title, None, None)
        if not self.window:
            glfw.terminate()    
            return False
        
        glfw.make_context_current(self.window)
        print(f"OpenGL Version: {glGetString(GL_VERSION).decode()}")
        print(f"GLSL Version: {glGetString(GL_SHADING_LANGUAGE_VERSION).decode()}")
        print(f"ImGui Version: {imgui.get_version()}")
        self.init_opengl()
        
        self.camera = ThirdPersonCamera(position=(5, 0, 2), target=(0, 0, 0), up=(0, 0, 1), distance=9)
        self.mouse = Mouse(self.window, self.camera)
        self.keyboard = Keyboard(self.window, self.camera)
        self.init_renderer()
        self.set_frame_size(self.window, self.width, self.height)

        self.imgui_manager = ImGuiManager(self.window, enable_docking=True)

        glfw.set_framebuffer_size_callback(self.window, self.set_frame_size)

        return True

    def set_frame_size(self, window, width, height):
        glViewport(0, 0, width, height)
        self.width = width
        self.height = height
        aspect_ratio = self.width / self.height
        self.projection = self.camera.get_perspective_projection(45.0, aspect_ratio, 0.1, 100.0)
    
    def init_opengl(self):
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_CULL_FACE)
        glCullFace(GL_BACK)
        
    def init_renderer(self):
        self.renderer = Renderer()
        
        self.renderer.add_grid((0, 0, 0), 20.0, 1.0, Color.rgb(100, 100, 100))
        self.renderer.add_axis(10.0)
        
        self.renderer.add_cube((-1, 0, 0), 0.5, Color.RED, buffer_type=BufferType.Dynamic, show_wireframe=True)
        self.renderer.add_cube((0, 0, 0), 0.5, Color.GREEN, buffer_type=BufferType.Dynamic, show_wireframe=True)
        self.renderer.add_cube((1, 0, 0), 0.5, Color.BLUE, buffer_type=BufferType.Dynamic, show_wireframe=True)
        self.renderer.add_cube((0, 1, 0), 0.5, Color.rgb(128, 64, 32), buffer_type=BufferType.Dynamic, show_wireframe=True)
        
        self.init_lights()

    def init_lights(self):
        i = 0.3 # intensity
        c = (1.0, 0.9, 0.9) # color
        x = 10.0 # position
        # 1 light in each upper corner, 1 from below
        light_1 = Light(LightType.DIRECTIONAL, position=np.array((-1, -1, 1)) * x, direction=(1, 1, -1), color=c, intensity=i)
        light_2 = Light(LightType.DIRECTIONAL, position=np.array((1, 1, 1)) * x, direction=(-1, -1, -1), color=c, intensity=i)
        light_3 = Light(LightType.DIRECTIONAL, position=np.array((1, -1, 1)) * x, direction=(-1, 1, -1), color=c, intensity=i)
        light_4 = Light(LightType.DIRECTIONAL, position=np.array((-1, 1, 1)) * x, direction=(1, -1, -1), color=c, intensity=i)
        light_5 = Light(LightType.DIRECTIONAL, position=np.array((-1, -1, -1)) * x, direction=(1, 1, -1), color=c, intensity=i)
        light_6 = Light(LightType.DIRECTIONAL, position=np.array((1, 1, -1)) * x, direction=(-1, -1, -1), color=c, intensity=i)
        light_7 = Light(LightType.DIRECTIONAL, position=np.array((1, -1, -1)) * x, direction=(-1, 1, -1), color=c, intensity=i)
        light_8 = Light(LightType.DIRECTIONAL, position=np.array((-1, 1, -1)) * x, direction=(1, -1, -1), color=c, intensity=i)
        self.renderer.add_light(light_1)
        self.renderer.add_light(light_2)
        self.renderer.add_light(light_3)
        self.renderer.add_light(light_4)
        self.renderer.add_light(light_5)
        self.renderer.add_light(light_6)
        self.renderer.add_light(light_7)
        self.renderer.add_light(light_8)


    def run(self):
        while not glfw.window_should_close(self.window):
            self.process_frame()
        self.cleanup()

    def process_frame(self):
        self.handle_events()
        self.update()
        self.render()

    def handle_events(self):
        glfw.poll_events()
        self.imgui_manager.process_inputs()

    def update(self):
        self.keyboard.process_input()

    def render(self):
        self.imgui_manager.new_frame()
        self.renderer.clear()

        self.imgui_manager.render_dockspace()
        self.render_debug_window()
        self.render_demo_window()

        self.render_3d_scene()
        self.imgui_manager.end_dockspace()
        self.imgui_manager.render()

        glfw.swap_buffers(self.window)

    def render_debug_window(self):
        imgui.begin("Debug Window")
        imgui.text(f"Camera Position: {self.camera.position}")
        imgui.text(f"Camera Target: {self.camera.target}")
        imgui.text(f"FPS: {1.0 / glfw.get_time():.1f}")
        glfw.set_time(0)  # Reset the timer
        imgui.end()

    def render_demo_window(self):
        imgui.show_demo_window()

    def render_3d_scene(self):
        view_matrix = self.camera.get_view_matrix()
        camera_position = self.camera.position

        self.renderer.default_shader.use()
        self.renderer.default_shader.set_view_matrix(view_matrix)
        self.renderer.default_shader.set_projection_matrix(self.projection)
        self.renderer.default_shader.set_view_position(camera_position)
        self.renderer.default_shader.set_light_uniforms(self.renderer.lights)

        # Add a model matrix
        model_matrix = np.identity(4, dtype=np.float32)
        self.renderer.default_shader.set_uniform("model", model_matrix)
        
        self.render_debug_triangle()
        self.renderer.draw()

    def cleanup(self):
        self.imgui_manager.shutdown()
        glfw.terminate()

    def render_debug_triangle(self):
        vertices = np.array([
            -0.5, -0.5, 0.0, 1.0, 0.0, 0.0,
             0.5, -0.5, 0.0, 0.0, 1.0, 0.0,
             0.0,  0.5, 0.0, 0.0, 0.0, 1.0
        ], dtype=np.float32)

        vao = glGenVertexArrays(1)
        glBindVertexArray(vao)

        vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, vbo)
        glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)

        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 24, ctypes.c_void_p(0))
        glEnableVertexAttribArray(0)
        glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 24, ctypes.c_void_p(12))
        glEnableVertexAttribArray(1)

        self.renderer.default_shader.use()
        glDrawArrays(GL_TRIANGLES, 0, 3)

        glDeleteVertexArrays(1, [vao])
        glDeleteBuffers(1, [vbo])


if __name__ == "__main__":
    app = Application(800, 600, "Third Person Camera")
    if app.init():
        app.run()
