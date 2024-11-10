from OpenGL.GL import *
import imgui
import glfw
import numpy as np
from core.application import Application
from core.application_ui import render_core_ui
from core.light import Light, LightType
from core.object_selection import ObjectSelection
from renderer.renderer import Renderer
from renderer.geometry import Geometry
from renderer.objects import BufferType
from utils.color import Color
from utils.config import Config   

class ExampleApplication(Application):
    
    def init(self):
        self.init_ui()
        self.init_variables()
        self.init_lights()
        self.init_geometry()
    
    def init_ui(self):
        """Initialize UI elements."""
        imgui.get_style().colors[imgui.COLOR_HEADER] = (0, 0, 0, 0)
        # imgui.get_style().colors[imgui.COLOR_HEADER_HOVERED] = (0, 0, 0, 0)
        # imgui.get_style().colors[imgui.COLOR_HEADER_ACTIVE] = (0, 0, 0, 0)

    def init_variables(self):
        """Variables added to config are saved in a JSON file and can be loaded/saved at runtime"""
        # Register variable - value will be read from config file if it exists else default value will be used
        self.config.add("variable 1", 0.001, "Description of variable 1")
        # Variables can be set like this
        self.config["variable 1"] = 0.002 
        
        self.object_start_pos = None
        
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

    def init_geometry(self):
        """Create the geometric objects in the scene."""
        # Settings
        self.renderer.default_point_size = 3.0
        self.renderer.default_line_width = 1.0 # lines & wireframes
        self.renderer.default_segments = 32 # n segments in circle
    
        RENDER_AREA = 50
        # Cursor 3D point
        self.cursor_3d = self.renderer.add_blank_object(draw_type=GL_POINTS, buffer_type=BufferType.Dynamic, selectable=False)
        self.selected_object = self.renderer.add_blank_object(draw_type=GL_LINES, buffer_type=BufferType.Dynamic, selectable=False)
        
        # Grid and axis
        self.renderer.add_grid(RENDER_AREA*2, 1, Color.GRAY, translate=(0, 0, -0.011), selectable=False) # Move grid slightly below z=0 to avoid z-fighting
        self.renderer.add_grid(RENDER_AREA*2, 10, Color.WHITE, translate=(0, 0, -0.01), selectable=False) # Move grid slightly below z=0 to avoid z-fighting
        # self.renderer.add_axis(size=1, selectable=False)
        
        # Add numbered axes
        self.renderer.add_numbered_axis(size=RENDER_AREA, increment=0.5, axis_color=Color.WHITE, tick_color=Color.rgb(200, 200, 200), line_width=1.0, tick_size=0.05)
        
        # Row 1 - Wireframe Shapes
        self.renderer.add_point((-4, 4, 0), Color.RED, point_size=10)
        self.renderer.add_line((-2.5, 3.5, 0), (-1.5, 4.5, 0), Color.ORANGE, line_width=5)
        self.renderer.add_triangle((0, 4.433, 0), (-0.5, 3.567, 0), (0.5, 3.567, 0), wireframe_color=Color.YELLOW, show_body=False)
        self.renderer.add_rectangle((2, 4), 1, 1, wireframe_color=Color.GREEN, show_body=False)
        self.renderer.add_circle(position=(4, 4, 0), radius=0.5, wireframe_color=Color.BLUE, show_body=False)


        # Row 2 - Filled Shapes
        self.renderer.add_circle(position=(-4, 2, 0), radius=0.5, color=Color.GREEN)
        # self.renderer.add_cube(Color.RED, translate=(-2, 2, 0.5), scale=(0.5, 0.5, 0.5), rotate=(np.pi/4, np.pi/4, 0), buffer_type=BufferType.Dynamic)
        self.renderer.add_cone(Color.rgb(255, 165, 0), segments=16, translate=(0, 2, 0.25), scale=(0.5, 0.5, 0.5))
        self.renderer.add_cylinder(Color.MAGENTA, translate=(2, 2, 0.25), scale=(0.5, 0.5, 0.5))
        self.renderer.add_sphere(translate=(4, 2, 0.5), radius=0.25, subdivisions=4, color=Color.RED)
        # Row 3 - Filled Shapes
        arrow_size = self.renderer.ArrowDimensions(shaft_radius=0.2, head_radius=0.4, head_length=0.3)
        self.renderer.add_arrow((-2.4, 1.6, 0.25), (-1.6, 2.4, 0.75), arrow_size, color=Color.PURPLE)
        
        # Dynamic objects (Rotating cubes - body & wireframe)
        self.rotating_cube = {
            **self.renderer.add_blank_object(draw_type=GL_TRIANGLES, buffer_type=BufferType.Dynamic), # body
            **self.renderer.add_blank_object(draw_type=GL_LINES, buffer_type=BufferType.Dynamic) # wireframe
        }

        # Example plots
        # Create a sine wave
        x = np.linspace(-3, 3, 25)
        y = np.sin(x)
        self.renderer.scatter(x, y, 
                              color=Color.CYAN, 
                              point_size=5.0,
                              translate=(-3, 0, 0))  # Move to left side

        # Create a parabola (y = x²)
        x = np.linspace(-1.5, 1.5, 100)  # x values from -1 to 1
        y = x**2                     # parabola equation: y = x²
        self.renderer.plot(x, y,
                          color=Color.GREEN,
                          line_width=2.0,
                          translate=(3, -1, 0))  # Move to right side


    def update_scene(self):
        """Update scene state called every frame."""
        # Draw cursor point
        if hasattr(self.renderer, 'cursor_pos'):
            point_geometry = Geometry.create_point(self.renderer.cursor_pos, Color.YELLOW)
            self.cursor_3d['line'].set_vertex_data(point_geometry.get_vertices())
            self.cursor_3d['line'].set_index_data(point_geometry.get_indices())
        
        # Get object under cursor
        if selected_objects := self.renderer.get_selected_objects():
            # Create a single geometry with multiple rectangles to indicate each selected object
            selected_geometry = []
            for i, obj in enumerate(selected_objects):
                if bounds := obj.get_bounds():
                    offset = self.camera.distance * 0.01
                    width, height, _ = (bounds['max'] - bounds['min']) + np.array([offset, offset, 0])
                    selected_geometry.append(Geometry.create_rectangle_target(*obj.get_mid_point()[:2], width, height, edge_length=self.camera.distance/50, color=Color.WHITE)) 
            selected_geometry = sum(selected_geometry, Geometry.create_blank())
        else:
            selected_geometry = Geometry.create_blank()
            
        self.selected_object['line'].set_vertex_data(selected_geometry.get_vertices())
        self.selected_object['line'].set_index_data(selected_geometry.get_indices())


        # Rotating cube
        rotate_geometry = (0, 0, self.timer.oscillate_angle(speed=0.6))
        rotate_object = (0, 0, self.timer.oscillate_angle(speed=0.5))

        # TODO: Update geometry only when required, set the model matrix instead of transforming the geometry
        rotating_cube_geometry = \
            Geometry.create_cube(size=0.5, color=Color.YELLOW) \
                .transform(translate=(-1, 0, 0.5), rotate=rotate_geometry) + \
            Geometry.create_cube(size=0.5, color=Color.GREEN) \
                .transform(translate=(1, 0, 0.5), rotate=rotate_geometry)

        
        # TODO: Sort objects make one combined class
        # Update vertex data
        self.rotating_cube['body'].set_vertex_data(rotating_cube_geometry.get_vertices())
        self.rotating_cube['body'].set_index_data(rotating_cube_geometry.get_indices()) # TODO: only needed first frame
        self.rotating_cube['body'].set_transform(translate=(self.timer.oscillate_translation(amplitude=2, speed=0.25), 0, 0), rotate=rotate_object)
        

        rotating_cube_wireframe = \
            Geometry.create_cube_wireframe(size=0.5, color=Color.BLACK) \
                .transform(translate=(-1, 0, 0.5), rotate=rotate_geometry, scale=(1.0001, 1.0001, 1.0001)) + \
            Geometry.create_cube_wireframe(size=0.5, color=Color.BLACK) \
                .transform(translate=(1, 0, 0.5), rotate=rotate_geometry, scale=(1.0001, 1.0001, 1.0001))
        
        # Update vertex data
        self.rotating_cube['line'].set_vertex_data(rotating_cube_wireframe.get_vertices())
        self.rotating_cube['line'].set_index_data(rotating_cube_wireframe.get_indices()) # TODO: only needed first frame
        self.rotating_cube['line'].set_transform(translate=(self.timer.oscillate_translation(amplitude=2, speed=0.25), 0, 0), rotate=rotate_object)
        
        
    def events(self):
        """Process custom input events specific to your application."""
        io = imgui.get_io()
        # If ImGui is capturing input, do not process further
        if io.want_capture_keyboard:
            return

        # Example: Check for specific key presses
        if imgui.is_key_pressed(glfw.KEY_SPACE):
            print("Space pressed!")
        
            
    def render_ui_window(self):
        """Render the example UI window."""
        imgui.begin('Example Window', flags=imgui.WINDOW_HORIZONTAL_SCROLLING_BAR)
        render_core_ui(self.camera, self.renderer, self.config, self.timer, self.imgui_manager)
        
        imgui.end()

    def render_ui(self):
        """Render UI elements."""
        imgui.show_demo_window()
        self.render_ui_window()

if __name__ == '__main__':
    """
    Application entry point. Sets up window, camera, and fonts 
    before starting the render loop.
    """
    # Create application with settings
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
        enable_drag_objects=False
    )
    
    if app.init_core():
        app.init()
        app.main_loop()
