import glfw
from OpenGL.GL import *
from imgui_manager import ImGuiManager
from camera import ThirdPersonCamera
from input_handlers import Mouse, Keyboard
from renderer import Renderer
from timer import Timer  # Import the Timer class
import os

class BaseApplication:
    def __init__(self, width, height, title, camera_settings, fonts, default_font):
        self.width = width
        self.height = height
        self.title = title
        self.window = None
        self.camera = None
        self.renderer = None
        self.mouse = None
        self.keyboard = None
        self.imgui_manager = None
        self.timer = Timer()  # Initialize the Timer
        
        self.camera_settings = camera_settings
        self.fonts = fonts
        self.default_font = default_font

    def init(self):
        if not self._init_glfw():
            return False
        self._init_components()
        self._init_imgui()
        return True

    def _init_glfw(self):
        if not glfw.init():
            return False

        self.window = glfw.create_window(self.width, self.height, self.title, None, None)
        if not self.window:
            glfw.terminate()    
            return False
        
        glfw.make_context_current(self.window)
        glfw.set_framebuffer_size_callback(self.window, self.set_frame_size)
        return True

    def _init_components(self):
        self.camera = ThirdPersonCamera(
            target=self.camera_settings['target'],
            up=(0, 0, 1),  # Constant up vector
            distance=self.camera_settings['distance']
        )
        self.mouse = Mouse(self.camera)
        self.keyboard = Keyboard(self.camera)
        self.renderer = Renderer()
        self.set_frame_size(self.window, self.width, self.height)

    def _init_imgui(self):
        self.imgui_manager = ImGuiManager(self.window, enable_docking=True)
        self._load_fonts()

    def _load_fonts(self):
        for name, font in self.fonts.items():
            self.imgui_manager.load_font(name, font['path'], font['size'])

    def set_frame_size(self, window, width, height):
        glViewport(0, 0, width, height)
        self.width = width
        self.height = height
        self.camera.set_aspect_ratio(width, height)
        self.camera.update_projection()

    def run(self):
        while not glfw.window_should_close(self.window):
            self.process_frame()
        self.cleanup()

    def process_frame(self):
        self.timer.update()  # Update the timer to calculate delta time
        self.handle_events()
        self.update()
        self.render()

    def handle_events(self):
        glfw.poll_events()
        self.imgui_manager.process_inputs()

    def update(self):
        self.mouse.process_input()
        self.keyboard.process_input()

    def render(self):
        self.imgui_manager.new_frame()
        self.renderer.clear()

        self.imgui_manager.push_font(self.default_font)
        self.imgui_manager.render_dockspace()
    
        self.render_ui()
        self.render_scene()
        
        self.imgui_manager.end_dockspace()
        self.imgui_manager.pop_font()
        self.imgui_manager.render()

        glfw.swap_buffers(self.window)

    def render_ui(self):
        pass  # Override in derived class

    def render_scene(self):
        """Render the 3D scene"""
        view_matrix = self.camera.get_view_matrix()
        projection = self.camera.get_projection_matrix()
        camera_position = self.camera.position
        
        self.renderer.set_view_matrix(view_matrix)
        self.renderer.set_projection_matrix(projection)
        self.renderer.set_camera_position(camera_position)
        self.renderer.draw()

    def cleanup(self):
        self.imgui_manager.shutdown()
        glfw.terminate()
