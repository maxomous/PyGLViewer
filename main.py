from core.application import Application
from core.renderer import Renderer
from core.application_ui import render_ui
from OpenGL.GL import *
import imgui
import glfw
import numpy as np
from core.geometry import Geometry
from core.light import Light, LightType
from gl.objects import BufferType
from utils.color import Color
from utils.config import Config   

class ExampleApplication(Application):
    
    def init(self):
        self.init_ui()
        self.init_variables()
        self.init_scene()
    
    def init_ui(self):
        """Initialize UI elements."""
        imgui.get_style().colors[imgui.COLOR_HEADER] = (0, 0, 0, 0)
        # imgui.get_style().colors[imgui.COLOR_HEADER_HOVERED] = (0, 0, 0, 0)
        # imgui.get_style().colors[imgui.COLOR_HEADER_ACTIVE] = (0, 0, 0, 0)

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
        self.renderer.default_point_size = 5.0
        self.renderer.default_line_thickness = 3.0
        self.renderer.default_segments = 32
        
        # Grid and axis
        self.renderer.add_grid(10, 1, Color.GRAY, translate=(0, 0, -0.01)) # Move grid slightly below z=0 to avoid z-fighting
        self.renderer.add_axis(size=1)
        
        # Row 1 - Wireframe Shapes
        self.renderer.add_point((-4, 4, 0), Color.RED, point_size=10)
        self.renderer.add_line((-2.5, 3.5, 0), (-1.5, 4.5, 0), Color.ORANGE)
        self.renderer.add_triangle((0, 4.433, 0), (-0.5, 3.567, 0), (0.5, 3.567, 0), wireframe_color=Color.YELLOW, show_body=False, line_width=10)

        self.renderer.add_rectangle((0, 0), 1, 1, wireframe_color=Color.GREEN, show_body=False)
        
        self.renderer.add_circle(position=(4, 4, 0), radius=0.5, wireframe_color=Color.BLUE, show_body=False)


        # Row 2 - Filled Shapes
        self.renderer.add_circle(position=(-4, 2, 0), radius=0.5, color=Color.GREEN)
        # self.renderer.add_cube(Color.RED, translate=(-2, 2, 0.5), scale=(0.5, 0.5, 0.5), rotate=(np.pi/4, np.pi/4, 0), buffer_type=BufferType.Dynamic)
        self.renderer.add_cone(Color.rgb(255, 165, 0), segments=5, translate=(0, 2, 0.5), scale=(0.5, 0.5, 0.5))
        self.renderer.add_cylinder(Color.WHITE, translate=(2, 2, 0.5), scale=(0.5, 0.5, 0.5))
        self.renderer.add_sphere(translate=(4, 2, 0.5), radius=0.25, subdivisions=1, color=Color.WHITE)
        self.renderer.add_sphere(translate=(4, 0, 0.5), radius=0.25, subdivisions=4, color=Color.WHITE)
        # Row 3 - Filled Shapes
        arrow_size = self.renderer.ArrowDimensions(shaft_radius=0.2, head_radius=0.4, head_length=0.3)
        self.renderer.add_arrow((2, -1, 0.25), (1, 4, 0.75), arrow_size, color=Color.RED)

        # TODO: Dynamically allocate buffer size
        self.rotating_cube = {   
            'body': self.renderer.add_blank_object(vertices_size=10000, indices_size=10000, draw_type=GL_TRIANGLES, buffer_type=BufferType.Stream),
            'wireframe': self.renderer.add_blank_object(vertices_size=10000, indices_size=10000, draw_type=GL_LINES, buffer_type=BufferType.Stream)
        }

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

    def update_scene(self):
        # TODO: Make ObjectCollection to store multiple objects OR multiple geometries???
        """Update scene state called every frame."""

        # TODO: Update geometry only when required, set the model matrix instead of transforming the geometry
        cube_geometry = \
            Geometry.create_cube(size=0.5, color=Color.YELLOW) \
                .transform(translate=(-1, 0, 0.5), rotate=(0, 0, self.timer.oscillate_angle(speed=0.25))) + \
            Geometry.create_cube(size=0.5, color=Color.GREEN) \
                .transform(translate=(1, 0, 0.5), rotate=(0, 0, self.timer.oscillate_angle(speed=0.25)))
        
        # TODO: Sort objects make one combined class
        # Update vertex data
        self.rotating_cube['body'][0].set_vertex_data(cube_geometry.interleave_vertices())
        self.rotating_cube['body'][0].set_index_data(cube_geometry.indices) # TODO: maybe just first frame
        self.rotating_cube['body'][0].set_transform(translate=(self.timer.oscillate_translation(amplitude=2, speed=0.25), 0, 0), rotate=(0, 0, self.timer.oscillate_angle(0.5)))
        
        # rotating_cube_wireframe = \
        #     Geometry.create_cube_wireframe(size=1.0, color=Color.BLACK) \
        #         .transform(translate=(0, 0, 0.5), rotate=(0, 0, self.timer.oscillate_angle(speed=0.25)), scale=(0.501, 0.501, 0.501)) + \
        #     Geometry.create_cube_wireframe(size=1.0, color=Color.BLACK) \
        #         .transform(translate=(0, 0, self.timer.oscillate_translation(amplitude=2, speed=0.25)))
        
        # # Update vertex data
        # self.rotating_cube_wireframe[0].update_vertex_data(rotating_cube_wireframe.interleave_vertices())
        # self.rotating_cube_wireframe[0].update_index_data(rotating_cube_wireframe.indices) # TODO: maybe just first frame
        
        
    def events(self):
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
            print(f"Left mouse button clicked: {io.mouse_pos}")

    def render_debug_window(self):
        """Render the debug UI window.
        Displays various debug information including:
        - Camera settings
        - Mouse state
        - Performance metrics
        - Adjustable parameters
        """
        imgui.begin('Debug Window', flags=imgui.WINDOW_ALWAYS_AUTO_RESIZE)
        render_ui(self.camera, self.config, self.timer, self.imgui_manager)
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
        'arial-medium': { 'path': 'C:/Windows/Fonts/arial.ttf', 'size': 16 },
        'arial-small': { 'path': 'C:/Windows/Fonts/arial.ttf', 'size': 12 },
        'arial_rounded_mt_bold-medium': { 'path': 'C:/Windows/Fonts/ARLRDBD.TTF', 'size': 15 },
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
    
    if app.init_core():
        app.init()
        app.main_loop()
