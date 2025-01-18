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
from pyglviewer.renderer.objects import ObjectContainer
from pyglviewer.renderer.shader import PointShape
from pyglviewer.utils.colour import Colour
from pyglviewer.utils.config import Config   
from pyglviewer.utils.timer import Timer
from pyglviewer.utils.transform import Transform

# TODO: UPDATE __init__.py


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
        
        Create Text using text_renderer.add_text(), text_renderer.add_axis_labels() etc. 
        To ensure text persists between frames, set static=True.
        Dynamic text can be updated in update_scene() & set to static=False.
        """
        # Set default shape settings
        Shapes.DEFAULT_SEGMENTS = 32     # n segments in circle
        Shapes.DEFAULT_SUBDIVISIONS = 4  # n subdivisions in sphere
    
        GRID_SIZE = 50
        GRID_TRANSLATE = (0, 0, -0.005) # Move grid slightly below z=0 to avoid z-fighting
        # Text Rendering
        self.text_renderer.add_axis_labels(xlim=[-10, 10], ylim=[-10, 10], increment=2, colour=Colour.WHITE, static=True)
        
        
        
        
        
        
        # object starts with no size
        # when set_shape is called, number of objects is set
        
        
        # Static object
        static_object = self.renderer.add_object(static=True).set_shape(Shapes.grid(size=GRID_SIZE, increment=1, colour=Colour.WHITE))
        # Dynamic object
        self.dynamic_object = self.renderer.add_object()
         
    
         
        # Grid and axis
        self.grid = self.renderer.add_object(static=True, selectable=False).set_shape(Shapes.grid(size=GRID_SIZE*2, increment=1, colour=Colour.WHITE)).set_transform_matrix(Transform(translate=GRID_TRANSLATE))
        self.renderer.add_object(static=True, selectable=False).set_shape(Shapes.axis_ticks(size=GRID_SIZE)).set_transform_matrix(Transform(translate=GRID_TRANSLATE))
        self.axis = self.renderer.add_object(static=True, selectable=False).set_shape(Shapes.axis(size=10))
        
        # Points with different shapes
        self.renderer.add_object(point_size=15, point_shape=PointShape.CIRCLE, static=True).set_shape(Shapes.point(position=(-4, 4, 0), colour=Colour.RED))
        self.renderer.add_object(point_size=15, point_shape=PointShape.TRIANGLE, static=True).set_shape(Shapes.point(position=(-4, 2.5, 0), colour=Colour.GREEN))
        self.renderer.add_object(point_size=15, point_shape=PointShape.SQUARE, static=True).set_shape(Shapes.point(position=(-4, 1, 0), colour=Colour.BLUE))
        
        # Lines and beams
        self.renderer.add_object(line_width=5, static=True).set_shape(Shapes.line(p0=(-2.5, 3.5, 0), p1=(-1.5, 4.5, 0), colour=Colour.ORANGE))
        self.renderer.add_object(static=True).set_shape(Shapes.beam(p0=(-2.5, 2.0, 0.25), p1=(-1.5, 3.0, 0.75), width=0.2, height=0.2, colour=Colour.YELLOW))
        
        # Arrow with dimensions
        arrow_dims = ArrowDimensions(
            shaft_radius=0.2,
            head_radius=0.35,
            head_length=0.3
        )
        self.renderer.add_object(static=True).set_shape(Shapes.arrow(p0=(-2.4, 0.6, 0.25), p1=(-1.6, 1.4, 0.75), dimensions=arrow_dims, colour=Colour.PURPLE))
        
        # Basic shapes - wireframe only
        self.renderer.add_object(static=True).set_shape(Shapes.triangle(p1=(0, 4.433, 0), p2=(-0.5, 3.567, 0), p3=(0.5, 3.567, 0), wireframe_colour=Colour.YELLOW, show_body=False))
        self.renderer.add_object(static=True).set_shape(Shapes.rectangle(position=(2, 4, 0), width=1, height=1, wireframe_colour=Colour.GREEN, show_body=False))
        self.renderer.add_object(static=True).set_shape(Shapes.circle(position=(4, 4, 0), radius=0.5, wireframe_colour=Colour.BLUE, show_body=False))
        
        # # Basic shapes - filled
        # self.renderer.add_triangle(p1=(0, 2.933, 0), p2=(-0.5, 2.067, 0), p3=(0.5, 2.067, 0), 
        #                          colour=Colour.YELLOW)
        # self.renderer.add_rectangle(position=(2, 2.5, 0), width=1, height=1, colour=Colour.GREEN)
        # self.renderer.add_circle(position=(4, 2.5, 0), radius=0.5, colour=Colour.BLUE)

        # # 3D shapes with transforms
        # self.renderer.add_cone(colour=Colour.rgb(255, 165, 0), 
        #                      params=RenderParams(translate=(0, 0.75, 0.5), 
        #                                        scale=(0.5, 0.5, 0.5), 
        #                                        rotate=(-np.pi/2, 0, 0)))
        # self.renderer.add_cylinder(colour=Colour.MAGENTA, 
        #                          params=RenderParams(translate=(2, 1, 0.25), 
        #                                            scale=(0.5, 0.5, 0.5)))
        # self.renderer.add_sphere(position=(4, 1, 0.5), radius=0.25, colour=Colour.RED, 
        #                        params=RenderParams())
                
        # # Dynamic objects
        # self.rotating_cubes = self.renderer.add_blank_objects({
        #     'body': GL_TRIANGLES, 
        #     'wireframe': GL_LINES
        # })

        # # Plots
        # x = np.linspace(-1.5, 1.5, 100)
        # y = x**2
        # self.renderer.plot(x, y, colour=Colour.GREEN, 
        #                  params=RenderParams(line_width=2.0, translate=(-3, -2, 0)))

        # x = np.linspace(0, 3, 50)
        # y = np.sin(x * np.pi / 1.5)
        # self.renderer.scatter(x, y, colour=Colour.CYAN, 
        #                     params=RenderParams(point_size=5.0, translate=(1, -1, 0)))

    def update_scene(self):
        """
        Update dynamic objects each frame:
        - Set the geometry of the object using object.set_geometry_data(). 
            - Multiple geometries can be summed ('+') together.
            - Geometries can be transformed individually and/or together 
                using the 'transform()' method as many times as required.
        - Transform an object with object.set_transform_matrix() once per frame.

        Note: Only update geometry if it actually changes, 
            update the Object transform if only translating, rotating or scaling.
            
        Dynamic Text can be rendered here every frame (make sure to set static=False).
        """
        self.dynamic_object.set_shape(Shapes.cube(size=0.5, colour=Colour.WHITE))

        return
        # Update axis size
        if self.camera.distance > 5:
            self.grid.set_transform_matrix(Transform(scale=(10, 10, 1)))
        else:
            self.grid.set_transform_matrix(Transform(scale=(1, 1, 1)))
            
        scale_axis = self.mouse.screen_to_world(100, dimension=3)
        self.axis.set_transform_matrix(Transform(scale=scale_axis))
        
        # Rotating cube
        rotate_geometry = (0, 0, self.timer.oscillate_angle(speed=0.6))
        rotate_object = (0, 0, self.timer.oscillate_angle(speed=0.5))
        # Rotating cubes
        self.rotating_cubes['body'].set_geometry_data(
            Shapes.cube(size=0.5, colour=Colour.YELLOW)
                .transform(translate=(-1, 0, 0.5), rotate=rotate_geometry) +
            Shapes.cube(size=0.5, colour=Colour.GREEN)
                .transform(translate=(1, 0, 0.5), rotate=rotate_geometry)
        )
        self.rotating_cubes['wireframe'].set_geometry_data(
            Shapes.cube_wireframe(size=0.5, colour=Colour.BLACK)
                .transform(translate=(-1, 0, 0.5), rotate=rotate_geometry, scale=(1.0001, 1.0001, 1.0001)) +
            Shapes.cube_wireframe(size=0.5, colour=Colour.BLACK)
                .transform(translate=(1, 0, 0.5), rotate=rotate_geometry, scale=(1.0001, 1.0001, 1.0001))
        )
        # Translate & rotate cube objects
        self.rotating_cubes.set_transform_matrix(Transform(translate=(self.timer.oscillate_translation(limits=[-2, 2], speed=0.25), -3, 0), rotate=rotate_object))

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
            drag_objects=True
        )
    )
    
    """ Initialise application & start the render loop. """
    if app.init_core():
        app.init()
        app.main_loop()
