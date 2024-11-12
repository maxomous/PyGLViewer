from OpenGL.GL import *
import imgui
import glfw
import numpy as np
from core.application import Application
from core.application_ui import render_core_ui
from core.object_selection import ObjectSelection, SelectionSettings
from renderer.light import Light, LightType, default_lighting
from renderer.renderer import Renderer
from renderer.geometry import Geometry
from renderer.objects import BufferType, ObjectCollection
from utils.color import Color
from utils.config import Config   

class ExampleApplication(Application):
    
    def init(self):
        self.init_ui()
        self.init_variables()
        self.renderer.add_lights(default_lighting)
        self.init_geometry()
    
    def init_ui(self):
        """Initialize UI elements."""
        imgui.get_style().colors[imgui.COLOR_HEADER] = (0, 0, 0, 0) # COLOR_HEADER_HOVERED / COLOR_HEADER_ACTIVE
        
    def init_variables(self):
        """Variables added to config are saved in a JSON file and can be loaded/saved at runtime"""
        # Register variable to read/write from config file (if it doesn't exist, default value will be used)
        self.config.add("variable 1", 0.001, "Description of variable to be saved in config file")
        # Variables can be set like this
        self.config["variable 1"] = 0.002 
                
    def init_geometry(self):
        """Create the geometric objects in the scene."""
        # Settings
        self.renderer.default_point_size = 3.0
        self.renderer.default_line_width = 1.0  # lines & wireframes
        self.renderer.default_segments = 32     # n segments in circle
    
        GRID_SIZE = 50
        # Grid and axis
        translate_grid = (0, 0, -0.002) # Move grid slightly below z=0 to avoid z-fighting
        self.renderer.add_grid(GRID_SIZE*2, 10, Color.WHITE, translate=translate_grid)
        self.renderer.add_grid(GRID_SIZE*2, 1, Color.GRAY, translate=translate_grid)
        self.renderer.add_numbered_axis(size=GRID_SIZE, increment=0.5, axis_color=Color.WHITE, tick_color=Color.rgb(200, 200, 200), line_width=1.0, tick_size=0.05, draw_origin=False, translate=translate_grid)
        self.axis = self.renderer.add_axis()
        
        # Wireframe Shapes
        self.renderer.add_point((-4, 4, 0), Color.RED, point_size=10)
        self.renderer.add_line((-2.5, 3.5, 0), (-1.5, 4.5, 0), Color.ORANGE, line_width=5)
        self.renderer.add_triangle((0, 4.433, 0), (-0.5, 3.567, 0), (0.5, 3.567, 0), wireframe_color=Color.YELLOW, show_body=False)
        self.renderer.add_rectangle((2, 4), 1, 1, wireframe_color=Color.GREEN, show_body=False)
        self.renderer.add_circle(position=(4, 4, 0), radius=0.5, wireframe_color=Color.BLUE, show_body=False)

        # Filled Shapes
        self.renderer.add_circle(position=(-4, 2, 0), radius=0.5, color=Color.GREEN)
        self.renderer.add_cone(Color.rgb(255, 165, 0), segments=16, translate=(0, 2, 0.25), scale=(0.5, 0.5, 0.5))
        self.renderer.add_cylinder(Color.MAGENTA, translate=(2, 2, 0.25), scale=(0.5, 0.5, 0.5))
        self.renderer.add_sphere(translate=(4, 2, 0.5), radius=0.25, subdivisions=4, color=Color.RED)
        arrow_dimensions = self.renderer.ArrowDimensions(shaft_radius=0.2, head_radius=0.4, head_length=0.3)
        self.renderer.add_arrow((-2.4, 1.6, 0.25), (-1.6, 2.4, 0.75), arrow_dimensions, color=Color.PURPLE)

        # Dynamic objects (2 objects, body & wireframe)
        self.rotating_cubes = self.renderer.add_blank_objects({'body': GL_TRIANGLES, 'wireframe': GL_LINES})

        # Example plots
        # Create a sine wave
        x = np.linspace(-3, 3, 25)
        y = np.sin(x)
        self.renderer.scatter(x, y, color=Color.CYAN, point_size=5.0, translate=(-3, 0, 0))  # Move to left side

        # Create a parabola (y = x²)
        x = np.linspace(-1.5, 1.5, 100) # x values from -1 to 1
        y = x**2                        # parabola equation: y = x²
        self.renderer.plot(x, y, color=Color.GREEN, line_width=2.0, translate=(3, -1, 0))  # Move to right side


    def update_scene(self):
        """Update dynamic objects in the scene, called every frame."""
        # Update axis size
        self.axis.set_transform(scale=(self.camera.distance/10, self.camera.distance/10, self.camera.distance/10))
        
        # Rotating cube
        rotate_geometry = (0, 0, self.timer.oscillate_angle(speed=0.6))
        rotate_object = (0, 0, self.timer.oscillate_angle(speed=0.5))
        # Rotating cubes
        self.rotating_cubes['body'].set_geometry_data(
            Geometry.create_cube(size=0.5, color=Color.YELLOW).transform(translate=(-1, 0, 0.5), rotate=rotate_geometry) +
            Geometry.create_cube(size=0.5, color=Color.GREEN).transform(translate=(1, 0, 0.5), rotate=rotate_geometry)
        )
        self.rotating_cubes['wireframe'].set_geometry_data(
            Geometry.create_cube_wireframe(size=0.5, color=Color.BLACK).transform(translate=(-1, 0, 0.5), rotate=rotate_geometry, scale=(1.0001, 1.0001, 1.0001)) +
            Geometry.create_cube_wireframe(size=0.5, color=Color.BLACK).transform(translate=(1, 0, 0.5), rotate=rotate_geometry, scale=(1.0001, 1.0001, 1.0001))
        )
        # Translate & rotate cube objects
        self.rotating_cubes.set_transform(translate=(self.timer.oscillate_translation(amplitude=2, speed=0.25), 0, 0), rotate=rotate_object)
    
        
    def events(self):
        """Process custom input events specific to your application."""
        io = imgui.get_io()
        # If ImGui is capturing input, do not process further
        if io.want_capture_keyboard:
            return

        # Space pressed
        if imgui.is_key_pressed(glfw.KEY_SPACE):
            pass 
        # Left mouse button pressed
        if imgui.is_mouse_down(glfw.MOUSE_BUTTON_LEFT):
            pass 
            
    def render_ui_window(self):
        """Example UI window."""
        imgui.begin('Example Window', flags=imgui.WINDOW_HORIZONTAL_SCROLLING_BAR)
        # Render core UI elements (mouse, camera etc.)
        render_core_ui(self.camera, self.renderer, self.config, self.timer, self.imgui_manager)
        
        imgui.end()

    def render_ui(self):
        """Render your UI elements."""
        imgui.show_demo_window()
        self.render_ui_window()

if __name__ == '__main__':
    """ Setup your application"""
    app = ExampleApplication(
        width=1280,
        height=720,
        title='Example PyGLViewer Window',
        camera_settings={
            'target': (0, 0, 0),
            'distance': 10
        },
        fonts={
            'arial-large': { 'path': 'C:/Windows/Fonts/arial.ttf', 'size': 24 },
            'arial-medium': { 'path': 'C:/Windows/Fonts/arial.ttf', 'size': 16 },
            'arial-small': { 'path': 'C:/Windows/Fonts/arial.ttf', 'size': 12 },
            'arial_rounded_mt_bold-medium': { 'path': 'C:/Windows/Fonts/ARLRDBD.TTF', 'size': 15 },
        },
        default_font='arial-medium',
        config=Config('config.json'),
        enable_docking=True,
        selection_settings=SelectionSettings(
            show_cursor_point=True,
            select_objects=True,
            drag_objects=False
        )
    )
    
    """ Initialise application & start the render loop. """
    if app.init_core():
        app.init()
        app.main_loop()
