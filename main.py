from core.application import Application
from core.application_ui import render_ui_camera, render_ui_mouse, render_ui_performance, render_ui_config
import imgui
import glfw
import numpy as np
from core.light import Light, LightType
from gl.objects import BufferType
from utils.color import Color
from utils.config import Config

class ExampleApplication(Application):
    def init_variables(self):
        """Variables added to config are saved in a JSON file and can be loaded/saved at runtime"""
        # Register variable - value will be read from config file if it exists else default value will be used
        self.config.add("variable 1", 0.001, "Description of variable 1")
        # Set variable
        self.config["variable 1"] = 0.002 
        
    def init_scene(self):
        """Initialize the 3D scene with geometry and lights"""
        self.init_geometry()
        self.init_lights()

    def init_geometry(self):
        """Create the geometric objects in the scene."""
        # Settings
        segments = 32 # n segments for circular shapes
        point_size = 7.0
        line_thickness = 3.0
        
        # Grid and axis
        self.renderer.add_grid(10, 1, Color.GRAY, translate=(0, 0, -0.01)) # Move grid slightly below z=0 to avoid z-fighting
        self.renderer.add_axis(size=1)
        
        # Row 1 - Wireframe Shapes
        self.renderer.add_point((-4, 4, 0), Color.RED, point_size=point_size)
        self.renderer.add_line((-2.5, 3.5, 0), (-1.5, 4.5, 0), Color.ORANGE, line_width=line_thickness)
        self.renderer.add_triangle((0, 4.433, 0), (-0.5, 3.567, 0), (0.5, 3.567, 0), wireframe_color=Color.YELLOW, show_wireframe=True, show_body=False, line_width=line_thickness)
        self.renderer.add_rectangle((2, 4), 1, 1, wireframe_color=Color.GREEN, show_wireframe=True, show_body=False, line_width=line_thickness)
        self.renderer.add_circle(position=(4, 4, 0), radius=0.5, segments=segments, wireframe_color=Color.BLUE, show_body=False, line_width=line_thickness)

        # Row 2 - Filled Shapes
        self.renderer.add_circle(position=(-4, 2, 0), radius=0.5, segments=segments, color=Color.GREEN, show_body=True)
        self.renderer.add_cube(Color.RED, translate=(-2, 2, 0.5), scale=(0.5, 0.5, 0.5), rotate=(np.pi/4, np.pi/4, 0), buffer_type=BufferType.Dynamic, show_body=True)
        self.renderer.add_cone(Color.rgb(255, 165, 0), segments=segments, translate=(0, 2, 0.5), scale=(0.5, 0.5, 0.5), show_body=True)
        self.renderer.add_cylinder(Color.WHITE, segments=segments, translate=(2, 2, 0.5), scale=(0.5, 0.5, 0.5), show_body=True)
        self.renderer.add_sphere(translate=(4, 2, 0.5), radius=0.25, subdivisions=4, color=Color.WHITE)

        # Row 3 - Filled Shapes
        self.renderer.add_cube(Color.YELLOW, translate=(-4, 0, 0.5), scale=(0.5, 0.5, 0.5), buffer_type=BufferType.Dynamic, show_body=True)
        self.renderer.add_arrow((-2.4, -0.4, 0.25), (-1.6, 0.4, 0.75), shaft_radius=0.2, head_radius=0.4, head_length=0.3, color=Color.RED, show_body=True)

    def init_lights(self):
        """Initialize lighting setup for the scene.
        Creates and adds three lights:
        - Main directional light from top-right
        - Ambient light for base illumination
        - Fill directional light from opposite side
        """
        lights = {  
            'main': {
                'type': LightType.DIRECTIONAL, 
                'position': (10, 10, 10), 
                'target': (0, 0, 0), 
                'color': (1.0, 0.95, 0.8),
                'intensity': 0.4
            },
            'ambient': {
                'type': LightType.AMBIENT, 
                'color': (1, 1, 1), 
                'intensity': 0.7
            },
            'fill': {
                'type': LightType.DIRECTIONAL, 
                'position': (-5, 5, -5), 
                'target': (0, 0, 0), 
                'color': (0.8, 0.9, 1.0), 
                'intensity': 0.3
            }
        }
        for light_data in lights.values():
            self.renderer.add_light(Light(**light_data))

    def custom_events(self):
        """Process custom input events specific to your application."""
        io = imgui.get_io()
        # If ImGui is capturing input, do not process further
        if io.want_capture_keyboard:
            return
        # Example: Check for specific key presses
        if io.keys_down[glfw.KEY_SPACE]:
            print("Space pressed!")
        
        # Example: Check mouse button states
        if io.mouse_down[glfw.MOUSE_BUTTON_LEFT]:
            print("Left mouse button pressed!")
        
        # Example: Get cursor position
        print(io.mouse_pos)

    def render_debug_window(self):
        """Render the debug UI window.
        Displays various debug information including:
        - Camera settings
        - Mouse state
        - Performance metrics
        - Adjustable parameters
        """
        imgui.begin('Debug Window', flags=imgui.WINDOW_ALWAYS_AUTO_RESIZE)
        
        render_ui_camera(self.camera)
        render_ui_mouse(self.config)
        render_ui_performance(self.timer.dt) # TODO replace with imgui
        render_ui_config(self.config)

        imgui.end()

    def render_ui(self):
        """Render UI elements."""
        imgui.show_demo_window()
        self.render_debug_window()

if __name__ == '__main__':
    """
    Application entry point. Sets up window, camera, and fonts 
    before starting the render loop.
    """
        
    # Font configuration
    fonts = {
        'arial-large': { 'path': 'C:/Windows/Fonts/arial.ttf', 'size': 24 },
        'arial-medium': { 'path': 'C:/Windows/Fonts/arial.ttf', 'size': 17 },
        'arial-small': { 'path': 'C:/Windows/Fonts/arial.ttf', 'size': 12 }
    }
    
    # Create application with settings
    app = ExampleApplication(
        width=1280,
        height=720,
        title='Example PyGLViewer Window',
        camera_settings={
            'target': (0, 0, 0),
            'distance': 10
        },
        fonts=fonts,
        default_font='arial-medium',
        config=Config('config.json'),
        enable_docking=True
    )
    
    if app.init():
        app.init_variables()
        app.init_scene()
        app.main_loop()
