from OpenGL.GL import *
import imgui
import glfw
import numpy as np
from pyglviewer.core.application import Application
from pyglviewer.core.application_ui import render_core_ui
from pyglviewer.core.object_selection import ObjectSelection, SelectionSettings
from pyglviewer.renderer.light import Light, LightType, default_lighting
from pyglviewer.renderer.renderer import Renderer
from pyglviewer.renderer.shapes import Shapes, ArrowDimensions
from pyglviewer.renderer.objects import Object
from pyglviewer.renderer.shader import PointShape
from pyglviewer.utils.colour import Colour
from pyglviewer.utils.config import Config   
from pyglviewer.utils.timer import Timer
from pyglviewer.utils.transform import Transform

# TODO: UPDATE __init__.py


class ExampleApplication(Application):
    
    GRID_SIZE = 50
    GRID_TRANSLATE = (0, 0, -0.005) # Move grid slightly below z=0 to avoid z-fighting
    AXIS_SIZE = 100 # px
    
    def init(self):
        """
        Initialise the application.
        Create the UI, variables, lightingand geometry.
        """
        self.init_ui()
        self.init_variables()
        # Add lighting to the scene (Custom lighting can be used instead)
        self.renderer.add_lights(default_lighting)
        self.init_geometry(initialise=True)
    
    def init_ui(self):
        """ 
        Initialise ImGui (UI) elements.
        """
        imgui.get_style().colors[imgui.COLOR_HEADER] = (0, 0, 0, 0) # / COLOR_HEADER_HOVERED / COLOR_HEADER_ACTIVE
        
    def init_variables(self):
        """
        Variables can be added to a config file (JSON format) which can be loaded/saved at runtime
        """
        
        self.config.add("variable 1", 0.5, "Value of float slider")
        self.config.add("variable 2", (0.5, 0.5, 0.5), "Value of float slider 3D")
        self.config.add("variable 3", 2, "Value of dropdown")
        self.config.add("variable 4", True, "Value of checkbox")
    
    def init_geometry(self, initialise=False):
        """
        Create an object with obj = self.renderer.add_object()
        
        Add geometry to an object using either:
        1. Built-in shapes: obj.set_shape(Shapes.add_sphere()) etc.
        2. Or create custom shapes using the Shape class

        Buffer Types:
        - Static: Fixed geometry (rarely changes)
        - Dynamic: Frequent updates (use add_object() and update in update_scene())

        Buffers support transform operations using set_transform_matrix(translate, rotate, scale) in update_scene()
        
        Create Text using text_renderer.add_text(), text_renderer.add_axis_labels() etc. 
        To ensure text persists between frames, set static=True.
        Dynamic text can be updated in update_scene() & set to static=False.
        """
        
        # Set default shape settings
        Shapes.DEFAULT_SEGMENTS = 32     # n segments in circle
        Shapes.DEFAULT_SUBDIVISIONS = 4  # n subdivisions in sphere
    
        # Run this only once on initialisation (else we will add it each time init_geometry is called)
        if initialise:
            # Text Rendering
            self.text_renderer.add_axis_labels(xlim=[-10, 10], ylim=[-10, 10], increment=2, colour=Colour.WHITE, static=True)
        
               
        # Static objects
        
        # Grid and axis
        self.grid = self.renderer.add_object(Object(static=True, selectable=False)\
            .set_shapes(Shapes.grid(size=self.GRID_SIZE*2, increment=1, colour=Colour.WHITE))\
            .set_transform_matrix(Transform(translate=self.GRID_TRANSLATE)))
        self.axis = self.renderer.add_object(Object(static=True, selectable=False)\
            .set_shapes(Shapes.axis(size=1)))
        self.axis_ticks = self.renderer.add_object(Object(static=True, selectable=False)\
            .set_shapes(Shapes.axis_ticks(size=self.GRID_SIZE))\
            .set_transform_matrix(Transform(translate=self.GRID_TRANSLATE)))
        
        # Points with different shapes
        self.renderer.add_object(Object(point_size=15, point_shape=PointShape.CIRCLE, static=True)\
            .set_shapes(Shapes.point(position=(-4, 4, 0), colour=Colour.RED)))
        self.renderer.add_object(Object(point_size=15, point_shape=PointShape.TRIANGLE, static=True)\
            .set_shapes(Shapes.point(position=(-4, 2.5, 0), colour=Colour.GREEN)))
        self.renderer.add_object(Object(point_size=15, point_shape=PointShape.SQUARE, static=True)\
            .set_shapes(Shapes.point(position=(-4, 1, 0), colour=Colour.BLUE)))
        
        # Lines and beams
        self.renderer.add_object(Object(line_width=5, static=True)\
            .set_shapes(Shapes.line(p0=(-2.5, 3.5, 0), p1=(-1.5, 4.5, 0), colour=Colour.ORANGE)))
        self.renderer.add_object(Object(static=True)\
            .set_shapes(Shapes.beam(p0=(-2.5, 2.0, 0.25), p1=(-1.5, 3.0, 0.75), width=0.2, height=0.2, colour=Colour.YELLOW)))
        
        # Arrow with dimensions
        arrow_dimensions = ArrowDimensions(shaft_radius=0.2, head_radius=0.35, head_length=0.3)
        self.renderer.add_object(Object(static=True)\
            .set_shapes(Shapes.arrow(p0=(-2.4, 0.6, 0.25), p1=(-1.6, 1.4, 0.75), dimensions=arrow_dimensions, colour=Colour.PURPLE)))
        
        # Basic shapes - wireframe
        self.renderer.add_object(Object(static=True)\
            .set_shapes(Shapes.triangle(p1=(0, 4.433, 0), p2=(-0.5, 3.567, 0), p3=(0.5, 3.567, 0), wireframe_colour=Colour.YELLOW, show_body=False)))
        self.renderer.add_object(Object(static=True)\
            .set_shapes(Shapes.rectangle(position=(2, 4, 0), width=1, height=1, wireframe_colour=Colour.GREEN, show_body=False)))
        self.renderer.add_object(Object(static=True)\
            .set_shapes(Shapes.circle(position=(4, 4, 0), radius=0.5, wireframe_colour=Colour.BLUE, show_body=False)))
        
        # Basic shapes - filled
        self.renderer.add_object(Object(static=True)\
            .set_shapes(Shapes.triangle(p1=(0, 2.933, 0), p2=(-0.5, 2.067, 0), p3=(0.5, 2.067, 0), colour=Colour.YELLOW)))
        self.renderer.add_object(Object(static=True)\
            .set_shapes(Shapes.quad(p1=(1.5, 3, 0.5), p2=(1.5, 2, 0), p3=(2.5, 2, 0.5), p4=(2.5, 3, 1), colour=Colour.RED)))
        self.renderer.add_object(Object(static=True)\
            .set_shapes(Shapes.rectangle(position=(4, 2.5, 0), width=1, height=1, colour=Colour.GREEN)))
        self.renderer.add_object(Object(static=True)\
            .set_shapes(Shapes.circle(position=(6, 2.5, 0), radius=0.5, colour=Colour.BLUE)))

        # 3D shapes with transforms
        self.renderer.add_object(Object(static=True)\
            .set_shapes(Shapes.cone(colour=Colour.rgb(255, 165, 0)))\
            .set_transform_matrix(Transform(translate=(0, 0.75, 0.5), scale=(0.5, 0.5, 0.5), rotate=(-np.pi/2, 0, 0))))
            
        self.renderer.add_object(Object(static=True)\
            .set_shapes(Shapes.cylinder(colour=Colour.MAGENTA))\
            .set_transform_matrix(Transform(translate=(2, 1, 0.25), scale=(0.5, 0.5, 0.5))))
            
        self.renderer.add_object(Object(static=True)\
            .set_shapes(Shapes.prism(position=(4, 1, 0), radius=1, depth=1, colour=Colour.ORANGE)))

        self.sphere_object = self.renderer.add_object(Object(static=True)\
            .set_shapes(Shapes.sphere(position=(6, 1, 0.5), radius=0.5, colour=Colour.RED)))
        
        
        # Dynamic objects
        self.dynamic_object = self.renderer.add_object(Object())
         
        # Plots
        x = np.linspace(-1.5, 1.5, 100)
        y = x**2
        self.renderer.add_object(Object(static=True, line_width=2.0)\
            .set_shapes(Shapes.plot(x, y, colour=Colour.GREEN).transform(translate=(-3, -2, 0))))

        x = np.linspace(0, 3, 50)
        y = np.sin(x * np.pi / 1.5)
        self.renderer.add_object(Object(static=True, point_size=5.0)\
            .set_shapes(Shapes.scatter(x, y, colour=Colour.CYAN).transform(translate=(1, -1, 0))))

    def update_scene(self):
        """
        Update objects each frame:
        - Objects should be created first using self.renderer.add_object()
        - If an object only needs to move, scale or rotate, the transform matrix 
            can be set for both static or dynamic objects with obj.set_transform_matrix(). 
            Tranforming a static object is much quicker than transforming the geometry each frame.
        - Dynamic objects are used when geometry wants to change often, using .set_shape() 
            - Multiple geometries can be summed ('+') together.
            - Geometries can be transformed individually and/or together 
                using the 'transform()' method as many times as required.

        Dynamic Text can be rendered here every frame (make sure to set static=False).
        """
        # Rotating cube
        # rotate_geometry = (0, 0, self.timer.oscillate_angle(speed=0.6))
        # rotate_object = (0, 0, self.timer.oscillate_angle(speed=0.5))
        # self.rotating_cubes.set_shape(Shapes.cube(size=0.5, colour=Colour.YELLOW)
        #         .transform(translate=(-1, 0, 0.5), rotate=rotate_geometry) +
        #     Shapes.cube(size=0.5, colour=Colour.GREEN)
        #         .transform(translate=(1, 0, 0.5), rotate=rotate_geometry))
        
        
        size = self.timer.oscillate_translation(limits=[0.5, 1.5], speed=0.5)
        self.dynamic_object.set_shapes(Shapes.cube(size=size, colour=Colour.WHITE))

        # Update axis size
        if self.camera.distance > 5:
            self.grid.set_transform_matrix(Transform(scale=(10, 10, 1)))
        else:
            self.grid.set_transform_matrix(Transform(scale=(1, 1, 1)))
            
        self.axis.set_transform_matrix(Transform(scale=self.mouse.screen_to_world(self.AXIS_SIZE, dimension=3)))
        
        # Text Rendering
        self.text_renderer.add_text('3D LABEL', (self.timer.oscillate_translation(limits=[-1.5, 1.5], speed=0.25), -0.5, 1), Colour.ORANGE, font='arial_rounded_mt_bold-medium')

    def events(self):
        """
        Process custom events, such as the keyboard & mouse.
        """
        io = imgui.get_io()
        # If ImGui is capturing keyboard input, do not process further
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
        render_core_ui(self.camera, self.renderer, self.text_renderer, self.config, self.timer, self.imgui_manager)
        imgui.end()

    def render_ui_window(self):
        """
        An example UI window demonstrating various ImGui widgets.
        """
        imgui.begin('Example Window', flags=imgui.WINDOW_HORIZONTAL_SCROLLING_BAR)
        # Text
        imgui.text("Basic widgets")
        # Buttons
        if imgui.button("Clear Renderer!", width=100, height=30):
            print("Clearing renderer!")
            self.renderer.clear()
            self.init_geometry()
            
        # Sliders - this variable is stored in the config file
        changed, self.config["variable 1"] = imgui.slider_float("Float Slider", self.config["variable 1"], 0.0, 1.0)
        # Sliders - this variable is stored in the config file
        changed, self.config["variable 2"] = imgui.slider_float3("Float Slider 3D", self.config["variable 2"], 0.0, 1.0)
        # Combo box (dropdown)
        items = ["Option 1", "Option 2", "Option 3"]
        changed, self.config["variable 3"] = imgui.combo("Dropdown", self.config["variable 3"], items)
        # Checkbox
        changed, self.config["variable 4"] = imgui.checkbox("Checkbox", self.config["variable 4"])
        
        if imgui.image_button(self.images['image_node'], 32, 32):
            print("Image button clicked!")
        
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
        images={
            'image_node': { 'path': './img/image.png' },
        },
        config=Config('example_3d_config.json'),
        enable_docking=True,
        selection_settings=SelectionSettings(
            show_cursor_point=True,
            select_objects=True,
            drag_objects=True
            # select_callback=lambda obj: print(f"Selected object: {obj}"),
            # drag_callback=lambda obj: print(f"Dragged object: {obj}")
        )
    )
    
    """ Initialise application & start the render loop. """
    if app.init_core():
        app.init()
        app.main_loop()
