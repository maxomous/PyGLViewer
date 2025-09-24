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
from pyglviewer.gui.imgui_render_buffer import Texts, Images  # TODO: Should this be part of pyglviewer.renderer
from pyglviewer.gui.imgui_widgets import imgui
from pyglviewer.utils.colour import Colour
from pyglviewer.utils.config import Config   
from pyglviewer.utils.timer import Timer
from pyglviewer.utils.transform import Transform

# TODO: UPDATE __init__.py


class ExampleApplication(Application):
    
    GRID_SIZE = 50
    GRID_TRANSLATE = (0, 0, -0.005) # Move grid slightly below z=0 to avoid z-fighting
    AXIS_SIZE = 100 # px
    
    def __init__(self):
        """
        Initialise the core application.
        """
        super().__init__(
            width=1280,
            height=720,
            title='Example 3D PyGLViewer Window',
            camera_settings={
                '2d_mode': False,
                'target': (0, 0, 0),
                'distance': 10
            },
            fonts={
                'arial-medium': { 'path': 'C:/Windows/Fonts/arial.ttf', 'size': 16 }, # defaults to first font in list
                'arial-large': { 'path': 'C:/Windows/Fonts/arial.ttf', 'size': 24 },
                'arial-small': { 'path': 'C:/Windows/Fonts/arial.ttf', 'size': 12 },
                'arial_rounded_mt_bold-medium': { 'path': 'C:/Windows/Fonts/ARLRDBD.TTF', 'size': 15 },
            },
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
        
    def init(self):
        """
        Initialise your application.
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
        """ Initialise the scene geometry, text, and images.

            Use `renderer.update_object()` to add static or dynamic geometry, and 
            `renderer.update_text()` / `renderer.update_image()` for text and images.

            - Use `static=True` for rarely changing geometry, and `static=False` for 
            frequently updated objects (updated later in `update_scene()`).
            - Transforms can be updated directly via the `transform` argument.
            - Text and images persist between frames if `static=True`. 
            For dynamic text/images, set `static=False` and update each frame.
        """

        # Axis labels
        self.renderer.update_text('axis_labels',
            texts=Texts.axis(limits=[-10, 10], increment=2),
            colour=Colour.WHITE,
            selectable=False
        )

        # Example image
        self.renderer.update_image('my_image',
            images=Images.image(name='image_node', size=(48, 48), world_pos=(0, -3, 0))
        )

        # Grid, axis, axis ticks
        self.renderer.update_object('grid', static=True, selectable=False,
            shape=Shapes.grid(size=self.GRID_SIZE*2, increment=1, colour=Colour.WHITE),
            transform=Transform(translate=self.GRID_TRANSLATE)
        )
        self.renderer.update_object('axis', static=True, selectable=False,
            shape=Shapes.axis(size=1)
        )
        self.renderer.update_object('axis_ticks', static=True, selectable=False,
            shape=Shapes.axis_ticks(size=self.GRID_SIZE),
            transform=Transform(translate=self.GRID_TRANSLATE)
        )

        # Points with different shapes
        self.renderer.update_object('point_red', static=True, point_size=15, point_shape=PointShape.CIRCLE,
            shape=Shapes.point(position=(-4, 4, 0), colour=Colour.RED)
        )
        self.renderer.update_object('point_green', static=True, point_size=15, point_shape=PointShape.TRIANGLE,
            shape=Shapes.point(position=(-4, 2.5, 0), colour=Colour.GREEN)
        )
        self.renderer.update_object('point_blue', static=True, point_size=15, point_shape=PointShape.SQUARE,
            shape=Shapes.point(position=(-4, 1, 0), colour=Colour.BLUE)
        )

        # Lines and beams
        self.renderer.update_object('line_orange', static=True, line_width=5,
            shape=Shapes.line(p0=(-2.5, 3.5, 0), p1=(-1.5, 4.5, 0), colour=Colour.ORANGE)
        )
        self.renderer.update_object('beam_yellow', static=True,
            shape=Shapes.beam(p0=(-2.5, 2.0, 0.25), p1=(-1.5, 3.0, 0.75),
                            width=0.2, height=0.2, colour=Colour.YELLOW)
        )

        # Arrow with dimensions
        arrow_dimensions = ArrowDimensions(shaft_radius=0.2, head_radius=0.35, head_length=0.3)
        self.renderer.update_object('arrow_purple', static=True,
            shape=Shapes.arrow(p0=(-2.4, 0.6, 0.25), p1=(-1.6, 1.4, 0.75),
                            dimensions=arrow_dimensions, colour=Colour.PURPLE)
        )

        # Basic shapes (wireframe)
        self.renderer.update_object('triangle_wire', static=True,
            shape=Shapes.triangle(p1=(0, 4.433, 0), p2=(-0.5, 3.567, 0), p3=(0.5, 3.567, 0),
                                wireframe_colour=Colour.YELLOW, show_body=False)
        )
        self.renderer.update_object('rectangle_wire', static=True,
            shape=Shapes.rectangle(position=(2, 4, 0), width=1, height=1,
                                wireframe_colour=Colour.GREEN, show_body=False)
        )
        self.renderer.update_object('circle_wire', static=True,
            shape=Shapes.circle(position=(4, 4, 0), radius=0.5,
                                wireframe_colour=Colour.BLUE, show_body=False)
        )

        # Basic shapes (filled)
        self.renderer.update_object('triangle_filled', static=True,
            shape=Shapes.triangle(p1=(0, 2.933, 0), p2=(-0.5, 2.067, 0), p3=(0.5, 2.067, 0),
                                colour=Colour.YELLOW)
        )
        self.renderer.update_object('quad_red', static=True,
            shape=Shapes.quad(p1=(1.5, 3, 0.5), p2=(1.5, 2, 0),
                            p3=(2.5, 2, 0.5), p4=(2.5, 3, 1), colour=Colour.RED)
        )
        self.renderer.update_object('rectangle_green', static=True,
            shape=Shapes.rectangle(position=(4, 2.5, 0), width=1, height=1, colour=Colour.GREEN)
        )
        self.renderer.update_object('circle_blue', static=True,
            shape=Shapes.circle(position=(6, 2.5, 0), radius=0.5, colour=Colour.BLUE)
        )

        # 3D shapes with transforms
        self.renderer.update_object('cone', static=True,
            shape=Shapes.cone(colour=Colour.rgb(255, 165, 0)),
            transform=Transform(translate=(0, 0.75, 0.5), scale=(0.5, 0.5, 0.5), rotate=(-np.pi/2, 0, 0))
        )
        self.renderer.update_object('cylinder', static=True,
            shape=Shapes.cylinder(colour=Colour.MAGENTA),
            transform=Transform(translate=(2, 1, 0.25), scale=(0.5, 0.5, 0.5))
        )
        self.renderer.update_object('prism', static=True,
            shape=Shapes.prism(position=(4, 1, 0), radius=1, depth=1, colour=Colour.ORANGE)
        )
        self.renderer.update_object('sphere_red', static=True,
            shape=Shapes.sphere(position=(6, 1, 0.5), radius=0.5, colour=Colour.RED)
        )

        # Dynamic object (updated in update_scene)
        self.renderer.update_object('dynamic_cube', static=False,
            shape=Shapes.cube(size=1, colour=Colour.WHITE)
        )

        # Plots
        x = np.linspace(-1.5, 1.5, 100)
        y = x**2
        self.renderer.update_object('plot_green', static=True, line_width=2.0,
            shape=Shapes.plot(x, y, colour=Colour.GREEN),
            transform=Transform(translate=(-3, -2, 0))
        )
        x = np.linspace(0, 3, 50)
        y = np.sin(x * np.pi / 1.5)
        self.renderer.update_object('scatter_cyan', static=True, point_size=5.0,
            shape=Shapes.scatter(x, y, colour=Colour.CYAN),
            transform=Transform(translate=(1, -1, 0))
        )


    def update_scene(self):
        """Update dynamic objects, transforms, and text each frame.

        - Use `renderer.update_object()` to update transforms or replace shapes.
        - Static objects can still have their transforms updated efficiently.
        - Dynamic objects (`static=False`) are intended for frequently changing geometry.
        - Dynamic text and images can be added each frame with `static=False`.
        """

        # Animate dynamic cube size
        size = self.timer.oscillate_translation(limits=[0.5, 1.5], speed=0.5)
        self.renderer.update_object('dynamic_cube',
            shape=Shapes.cube(size=size, colour=Colour.WHITE)
        )

        # Scale axis depending on camera distance
        if self.camera.distance > 5:
            self.renderer.update_object('grid',
                transform=Transform(scale=(10, 10, 1))
            )
        else:
            self.renderer.update_object('grid',
                transform=Transform(scale=(1, 1, 1))
            )

        # Update axis transform with zoom
        self.renderer.update_object('axis',
            transform=Transform(scale=self.mouse.screen_to_world(self.AXIS_SIZE, dimension=3))
        )

        # Dynamic text label
        self.renderer.update_text('label_3d',
            texts=Texts.text('3D LABEL', (self.timer.oscillate_translation(limits=[-1.5, 1.5], speed=0.25), -0.5, 1)),
            colour=Colour.ORANGE,
            font='arial_rounded_mt_bold-medium',
            selectable=False
        )



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
        render_core_ui(self.camera, self.renderer, self.config, self.timer, self.imgui_manager)
        imgui.end()

    def render_ui_window(self):
        """
        An example UI window demonstrating various ImGui widgets.
        """
        imgui.begin('Example Window', flags=imgui.WINDOW_HORIZONTAL_SCROLLING_BAR)
        # Text
        imgui.text("Basic widgets")
            
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
            print("Image button 1 clicked!")
        
        if imgui.image_button_with_text('Button', self.images['image_node'], (65, 80), (32, 32), text_offset=(0.5, 0.8), image_offset=(0, -15), is_active=True, image_when_hovered=self.images['image_node']):
            print("Image button 2 clicked!")
        
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
    app = ExampleApplication()
    
    """ Initialise application & start the render loop. """
    if app.init_core():
        app.init()
        app.main_loop()
