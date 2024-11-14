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
from utils.timer import Timer
from utils.transform import Transform

class ExampleApplication(Application):
    
    def init(self):
        """
        Initialise the application.
        Create the UI, variables, lightingand geometry.
        """
        self.init_ui()
        self.init_variables()
        # Add lighting to the scene (Custom lighting can be used instead)
        self.renderer.add_lights(default_lighting)
        self.init_geometry()
    
    def init_ui(self):
        """
        Initialise ImGui (UI) elements.
        """
        #
        imgui.get_style().colors[imgui.COLOR_HEADER] = (0, 0, 0, 0) # / COLOR_HEADER_HOVERED / COLOR_HEADER_ACTIVE
        
    def init_variables(self):
        """
        Variables can be added to a config file (JSON format) which can be loaded/saved at runtime
        """
        self.config.add("variable 1", 0.5, "Value of float slider")
        self.config.add("variable 2", (0.5, 0.5, 0.5), "Value of float slider 3D")
        self.config.add("variable 3", 2, "Value of dropdown")
        self.config.add("variable 4", True, "Value of checkbox")
    
    def init_geometry(self):
        """
        Create objects using either:
        1. Built-in shapes: renderer.add_cube(), renderer.add_sphere(), etc.
        2. Custom shapes: combine / transform Geometry classes and pass to renderer.add_object()

        Buffer Types:
        - Static: Fixed geometry (rarely changes)
        - Dynamic: Frequent updates (use add_blank_object() and update in update_scene())

        Both types support transform operations (translate, rotate, scale) in update_scene()
        """
        # Settings
        self.renderer.default_point_size = 3.0
        self.renderer.default_line_width = 1.0  # lines & wireframes
        self.renderer.default_segments = 32     # n segments in circle
    
        GRID_SIZE = 50
        GRID_TRANSLATE = (0, 0, -0.002) # Move grid slightly below z=0 to avoid z-fighting
        # Grid and axis
        self.renderer.add_grid(GRID_SIZE*2, translate=GRID_TRANSLATE)
        self.renderer.add_axis_ticks(size=GRID_SIZE, translate=GRID_TRANSLATE)
        self.axis = self.renderer.add_axis()
        
        # Wireframe Shapes (show_body=False)
        self.renderer.add_point((-4, 4, 0), Color.RED, point_size=10)
        self.renderer.add_line((-2.5, 3.5, 0), (-1.5, 4.5, 0), Color.ORANGE, line_width=5)
        self.renderer.add_triangle((0, 4.433, 0), (-0.5, 3.567, 0), (0.5, 3.567, 0), wireframe_color=Color.YELLOW, show_body=False)
        self.renderer.add_rectangle((2, 4), 1, 1, wireframe_color=Color.GREEN, show_body=False)
        self.renderer.add_circle(position=(4, 4, 0), radius=0.5, wireframe_color=Color.BLUE, show_body=False)

        # Filled Shapes with wireframe
        self.renderer.add_circle(position=(-4, 2, 0), radius=0.5, color=Color.GREEN)
        self.renderer.add_cone(Color.rgb(255, 165, 0), segments=16, translate=(0, 2, 0.25), scale=(0.5, 0.5, 0.5))
        self.renderer.add_cylinder(Color.MAGENTA, translate=(2, 2, 0.25), scale=(0.5, 0.5, 0.5))
        self.renderer.add_sphere(translate=(4, 2, 0.5), radius=0.25, subdivisions=4, color=Color.RED)
        arrow_dimensions = self.renderer.ArrowDimensions(shaft_radius=0.2, head_radius=0.4, head_length=0.3)
        self.renderer.add_arrow((-2.4, 1.6, 0.25), (-1.6, 2.4, 0.75), arrow_dimensions, color=Color.PURPLE)

        # Create two dynamic object placeholders (body + wireframe)
        self.rotating_cubes = self.renderer.add_blank_objects({'body': GL_TRIANGLES, 'wireframe': GL_LINES})

        # Example parabola (y = x²) plot
        x = np.linspace(-1.5, 1.5, 100) # x values from -1 to 1
        y = x**2                        # parabola equation: y = x²
        self.renderer.plot(x, y, color=Color.GREEN, line_width=2.0, translate=(-3, -1, 0))  # Move to right side

        # Example sine wave scatter plot
        x = np.linspace(-3, 3, 25)
        y = np.sin(x)
        self.renderer.scatter(x, y, color=Color.CYAN, point_size=5.0, translate=(3, 0, 0))  # Move to left side


    def update_scene(self):
        """
        Update dynamic objects each frame:
        - Set the geometry of the object using object.set_geometry_data(). 
            - Multiple geometries can be summed ('+') together.
            - Geometries can be transformed individually and/or together 
                using the 'transform()' method as many times as required.
        - Transform an object with object.set_transform() once per frame.

        Note: Only update geometry if it actually changes, 
            update the Object transform if only translating, rotating or scaling.
        """
        SCALE_WITH_ZOOM = np.repeat(self.camera.distance, 3)
        # Update axis size
        self.axis.set_transform(scale=SCALE_WITH_ZOOM/10)
        
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
        """
        Process custom events, such as the keyboard & mouse.
        """
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
            
    def render_core_ui_window(self):
        """
        Creates a UI window for core settings.
        """
        imgui.begin('Core', flags=imgui.WINDOW_HORIZONTAL_SCROLLING_BAR)
        render_core_ui(self.camera, self.renderer, self.config, self.timer, self.imgui_manager)
        imgui.end()

    def render_ui_window(self):
        """
        An example UI window demonstrating various ImGui widgets.
        """
        imgui.begin('Example Window', flags=imgui.WINDOW_HORIZONTAL_SCROLLING_BAR)
        # Text
        imgui.text("Basic widgets")
        # Buttons
        if imgui.button("Click Me!", width=100, height=30):
            print("Button clicked!")
        # Sliders - this variable is stored in the config file
        changed, self.config["variable 1"] = imgui.slider_float("Float Slider", self.config["variable 1"], 0.0, 1.0)
        # Sliders - this variable is stored in the config file
        changed, self.config["variable 2"] = imgui.slider_float3("Float Slider 3D", self.config["variable 2"], 0.0, 1.0)
        # Combo box (dropdown)
        items = ["Option 1", "Option 2", "Option 3"]
        changed, self.config["variable 3"] = imgui.combo("Dropdown", self.config["variable 3"], items)
        # Checkbox
        changed, self.config["variable 4"] = imgui.checkbox("Checkbox", self.config["variable 4"])
        # End UI window
        imgui.end()

    def render_ui(self):
        """
        Render all of the UI windows here.
        The imgui demo window shows all of the available ImGui functions.
        The code is here: https://github.com/ocornut/imgui/blob/master/imgui_demo.cpp 
        """
        imgui.show_demo_window()
        self.render_core_ui_window()
        self.render_ui_window()

if __name__ == '__main__':
    """ 
    Setup your application.
    """
    app = ExampleApplication(
        width=1280,
        height=720,
        title='Example 3D PyGLViewer Window',
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
        config=Config('example_3d_config.json'),
        enable_docking=True,
        selection_settings=SelectionSettings(
            show_cursor_point=True,
            select_objects=True,
            drag_objects=False
        )
    )
    
    """ 
    Initialise application & start the render loop. 
    """
    if app.init_core():
        app.init()
        app.main_loop()
