import glfw
from OpenGL.GL import *
from core.camera import ThirdPersonCamera
from core.keyboard import Keyboard
from core.mouse import Mouse
from renderer.renderer import Renderer
from utils.timer import Timer
from utils.config import Config
from gui.imgui_manager import ImGuiManager
import time

class Application:
    """Base class for OpenGL applications with ImGui integration.
    
    Handles window creation, rendering loop, and core components like camera,
    input handling, and scene rendering.
    
    To use this class:
    1. Inherit from BaseApplication
    2. Override render_ui() to add custom UI elements
    3. Override init_scene() to setup geometry and lights
    
    Example:
        class MyApp(BaseApplication):
            def init_scene(self):
                self.init_geometry()
                self.init_lights()
                
            def render_ui(self):
                # Add custom UI elements here
                pass
    
    Args:
        width (int): Initial window width
        height (int): Initial window height
        title (str): Window title
        camera_settings (dict): Camera configuration parameters
        fonts (dict): Font configurations for ImGui
        default_font (str): Name of default font to use
        config (Config): Configuration container with custom variables which are saved to a JSON file
        enable_docking (bool): Enable ImGui docking functionality
    """

    def __init__(self, width, height, title, camera_settings, fonts, default_font, config, enable_docking=True):
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
        self.config = config
        self.camera_settings = camera_settings
        self.fonts = fonts
        self.default_font = default_font
        self.enable_docking = enable_docking
        
    def init_core(self):
        """Initialize GLFW, OpenGL context, and application components.
        
        Returns:
            bool: True if initialization successful, False otherwise
        """
        if not self._init_glfw():
            return False
        self._init_components()
        self._init_imgui()
        return True

    def _init_glfw(self):
        """Initialize GLFW window and context.
        
        Returns:
            bool: True if initialization successful, False otherwise
        """
        if not glfw.init():
            return False

        # Request OpenGL 3.3 core profile
        glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
        glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
        glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
        
        # Enable vsync
        glfw.window_hint(glfw.DOUBLEBUFFER, True)

        self.window = glfw.create_window(self.width, self.height, self.title, None, None)
        if not self.window:
            glfw.terminate()    
            return False
        
        glfw.make_context_current(self.window)
        
        # Enable vsync (1 = enable, 0 = disable)
        glfw.swap_interval(1)
        # Set frame size callback
        glfw.set_framebuffer_size_callback(self.window, self.set_frame_size)
        return True

    def _init_components(self):
        self.camera = ThirdPersonCamera(
            target=self.camera_settings['target'],
            up=(0, 0, 1),  # Constant up vector
            distance=self.camera_settings['distance']
        )
        self.mouse = Mouse(self.camera, self.config)  # Pass parameters instance
        self.keyboard = Keyboard(self.camera)
        self.renderer = Renderer()
        self.set_frame_size(self.window, self.width, self.height)

    def _init_imgui(self):
        self.imgui_manager = ImGuiManager(self.window, enable_docking=self.enable_docking)
        self._load_fonts()

    def _load_fonts(self):
        for name, font in self.fonts.items():
            self.imgui_manager.load_font(name, font['path'], font['size'])

    def set_frame_size(self, window, width, height):
        """Handle window resize events.
        
        Args:
            window: GLFW window handle
            width (int): New window width
            height (int): New window height
        """
        glViewport(0, 0, width, height)
        self.width = width
        self.height = height
        self.camera.set_aspect_ratio(width, height)
        self.camera.update_projection()

    def main_loop(self):
        """Main application loop.
        
        Runs the application until window is closed.
        """
        while not glfw.window_should_close(self.window):
            self.process_frame()
        self.cleanup()

    def process_frame(self):
        """Process a single frame.
        
        Updates timer, handles events, updates state, and renders frame.
        """
        # Update
        self.timer.update()  # Update the timer to calculate delta time
        self.process_inputs()
        self.update_scene()
        # Render
        self.render_core()
        

    def process_inputs(self):
        """Process input events from GLFW and ImGui."""
        glfw.poll_events()
        self.imgui_manager.process_inputs()
        self.mouse.process_input()
        self.keyboard.process_input()
        self.events()
        
    def events(self):
        """Process custom input events specific to your application."""
        raise NotImplementedError("events() must be implemented in derived class")

    def update_scene(self):
        """Update scene state called every frame."""
        raise NotImplementedError("update_scene() must be implemented in derived class")

    def render_core(self):
        """Render frame with UI and 3D scene.
        
        Handles ImGui frame setup, font management, and buffer swapping.
        """
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
        """Render 3D scene with current camera settings.
        
        Updates view/projection matrices and camera position before rendering.
        """
        view_matrix = self.camera.get_view_matrix()
        projection = self.camera.get_projection_matrix()
        camera_position = self.camera.position
        
        self.renderer.draw(view_matrix, projection, camera_position, self.renderer.lights)

    def cleanup(self):
        """Clean up resources before application exit.
        
        Saves configuration, shuts down ImGui and terminates GLFW.
        """
        # Clean up renderer resources first
        if self.renderer:
            self.renderer.shutdown()
            
        # Save config
        if self.config:
            self.config.save()
        
        # Clean up ImGui
        if self.imgui_manager:
            self.imgui_manager.shutdown()
            
        # Clean up GLFW
        if glfw.get_current_context():
            glfw.destroy_window(self.window)
            glfw.terminate()

    def cleanup(self):
        """Clean up resources before application exit."""
        try:
            # Save config
            if self.config:
                self.config.save()
                
            # Clean up ImGui
            if self.imgui_manager:
                self.imgui_manager.shutdown()
                
            # Clean up GLFW
            if glfw.get_current_context():
                glfw.destroy_window(self.window)
                glfw.terminate()
                
        except Exception as e:
            print(f"Error during cleanup: {e}") 