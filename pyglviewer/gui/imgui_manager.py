import imgui
from imgui.integrations.glfw import GlfwRenderer
import os
from PIL import Image
from OpenGL.GL import *

class ImGuiManager:
    """Manager class for ImGui integration with GLFW.
    
    Handles ImGui context creation, font loading, docking setup,
    and rendering integration with GLFW window.
    
    Args:
        window: GLFW window handle
        enable_docking (bool): Enable ImGui docking functionality
    """

    def __init__(self, window, enable_docking=True):
        self.window = window
        self.enable_docking = enable_docking
        self.imgui_renderer = None
        self.fonts = {}
        self.init_imgui()

    def init_imgui(self):
        """Initialize ImGui context and GLFW renderer.
        
        Sets up docking if enabled and configures default style.
        """
        imgui.create_context()
        io = imgui.get_io()
    
        # Check if docking is available
        if not hasattr(imgui, 'CONFIG_DOCKING_ENABLE'):
            print("Warning: Docking is not available in this version of imgui")
            self.enable_docking = False
        # Enable docking
        if self.enable_docking:
            io.config_flags |= imgui.CONFIG_DOCKING_ENABLE
        
        self.imgui_renderer = GlfwRenderer(self.window)
        # Set ImGui style
        style = imgui.get_style()
        style.colors[imgui.COLOR_WINDOW_BACKGROUND] = (0.1, 0.1, 0.1, 0.975)

    def load_font(self, name, path, size):
        """Load a font from file and add it to ImGui.
        
        Args:
            name (str): Identifier for the font
            path (str): Path to .ttf font file
            size (float): Font size in pixels
        """
        if not os.path.exists(path):
            print(f"Warning: Font file not found: {path}")
            return

        io = imgui.get_io()
        font = io.fonts.add_font_from_file_ttf(path, size)
        self.fonts[name] = font
        self.imgui_renderer.refresh_font_texture()

    def push_font(self, name):
        """Push named font onto ImGui font stack.
        
        Args:
            name (str): Font identifier previously loaded
        """
        if name in self.fonts:
            imgui.push_font(self.fonts[name])
        else:
            print(f"Warning: Font not found: {name}")

    def pop_font(self):
        """Pop current font from ImGui font stack."""
        imgui.pop_font()

    def load_image(self, path):
        """Load an image and convert it to an OpenGL texture.
        Returns a blank white texture if loading fails.
        """
        try:
            # Load image using PIL
            image = Image.open(path)
            # Convert to RGBA if not already
            if image.mode != 'RGBA':
                image = image.convert('RGBA')
            # Get image data
            image_data = image.tobytes()
            width, height = image.size
        except Exception as e:
            print(f"Error loading texture: {e}")
            # Create a 1x1 white pixel for the blank texture
            width, height = 1, 1
            image_data = bytes([255, 255, 255, 255])  # White RGBA pixel
        
        # Create OpenGL texture
        texture_id = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, texture_id)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, width, height, 0, GL_RGBA, GL_UNSIGNED_BYTE, image_data)
        
        return texture_id

    def new_frame(self):
        """Begin new ImGui frame."""
        imgui.new_frame()

    def render(self):
        """Render ImGui draw data."""
        imgui.render()
        self.imgui_renderer.render(imgui.get_draw_data())

    def process_inputs(self):
        """Process GLFW input events for ImGui."""
        self.imgui_renderer.process_inputs()

    def shutdown(self):
        """Clean up ImGui renderer resources."""
        self.imgui_renderer.shutdown()

    def render_dockspace(self):
        """Setup and render ImGui docking space.
        
        Creates a full viewport docking space with padding and optional toolbar space.
        Only active if docking is enabled.
        """
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
        """End the docking space if enabled."""
        if self.enable_docking:
            imgui.end()
