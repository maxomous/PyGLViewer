import imgui
import numpy as np
from pyglviewer.core.application import Application
from pyglviewer.core.application_ui import render_core_ui
from pyglviewer.core.object_selection import SelectionSettings
from pyglviewer.gui.imgui_render_buffer import Texts, Images  # TODO: Should this be part of pyglviewer.renderer
from pyglviewer.renderer.objects import Object
from pyglviewer.renderer.shader import PointShape
from pyglviewer.renderer.shapes import Shapes
from pyglviewer.utils.colour import Colour
from pyglviewer.utils.config import Config
from pyglviewer.utils.timer import Timer
from pyglviewer.utils.transform import Transform

class Example2DApplication(Application):
    
    GRID_SIZE = 25 # units
    GRID_TRANSLATE = (0, 0, -0.002)  # Move grid slightly below z=0 to avoid z-fighting
    AXIS_SIZE = 100 # px
    
    def init(self):
        """ Initialise the application. Create the UI, variables, lighting and geometry. 
        All objects should have a unique name, use update_object() to modify the object from other parts of the program"""
        
        # Set 2D mode and orthographic projection
        # self.camera.set_2d_mode(True)
        self.camera.set_projection(orthographic=True)
        
        # Axis label
        self.renderer.update_text('axis_labels', 
            texts=Texts.axis(limits=[-self.GRID_SIZE, self.GRID_SIZE], increment=1),
            colour=Colour.WHITE,
            selectable=False
        )
        # Axis label
        self.renderer.update_text('some_text', 
            texts=Texts.text('hello', (4, 3, 0)),
            colour=Colour.WHITE,
            font='arial_rounded_mt_bold-medium'
        )
        # Image
        self.renderer.update_image('some_image', 
            images=Images.image(name='image_node', size=(32, 32), world_pos=(2,3,1))
        )
        # Grid
        self.renderer.update_object('grid', static=True, selectable=False,
            shape=Shapes.grid(size=self.GRID_SIZE*2, increment=1, colour=Colour.WHITE),
            transform=Transform(translate=self.GRID_TRANSLATE)
        )
        # Axis ticks
        self.renderer.update_object('axis_ticks', static=True, selectable=False,
            shape=Shapes.axis_ticks(size=self.GRID_SIZE),
            transform=Transform(translate=self.GRID_TRANSLATE)
        )
        # Axis
        self.renderer.update_object('axis', static=True, selectable=False,
            shape=Shapes.axis(size=1),
            transform=Transform(translate=self.GRID_TRANSLATE)
        )

        # Transparent circle
        self.renderer.update_object('circle', static=True, alpha=0.2,
            shape=Shapes.circle(position=(3, 1, 0), radius=0.1, colour=Colour.YELLOW)
        )
        # Rectangle
        self.renderer.update_object('rectangle', static=True, alpha=0.5,
            shape=Shapes.rectangle(position=(4, 1, 0), width=0.1, height=0.1, colour=Colour.RED)
        )
        # Triangle
        self.renderer.update_object('triangle', static=True, alpha=0.8,
            shape=Shapes.triangle(p1=(5, 1.1, 0), p2=(4.9, 0.9, 0), p3=(5.1, 0.9, 0), colour=Colour.GREEN)
        )
        
        # Example sine wave scatter plot
        x1 = np.linspace(-self.GRID_SIZE, self.GRID_SIZE, 500)
        y1 = np.sin(x1)
        x2 = np.linspace(-self.GRID_SIZE, self.GRID_SIZE, 200)
        y2 = np.sin(x2)

        # Plot lines with custom widths
        self.renderer.update_object('plot_cyan_line', static=True, selectable=False, line_width=1.0,
            shape=Shapes.plot(x=x1, y=2*y1, colour=Colour.CYAN)
        )
        self.renderer.update_object('plot_red_line', static=True, selectable=False, line_width=3.0,
            shape=Shapes.plot(x=x1, y=-0.5*y1, colour=Colour.RED)
        )

        # Scatter plots with custom point sizes and shapes
        self.renderer.update_object('scatter_green_circle', static=True, selectable=False, point_size=12.0, point_shape=PointShape.CIRCLE,
            shape=Shapes.scatter(x=x2, y=-1.5*y2, colour=Colour.GREEN)
        )
        self.renderer.update_object('scatter_orange_triangle', static=True, selectable=False, point_size=12.0, point_shape=PointShape.TRIANGLE,
            shape=Shapes.scatter(x=x2, y=1*y2, colour=Colour.ORANGE)
        )

        # Dynamic objects: By creating a shape first and then updating the transform is more efficient than creating a new shape each frame
        self.renderer.update_object('circle_green', static=False, selectable=False,
            shape=Shapes.circle(position=(0, 0, 0), radius=0.2, colour=Colour.GREEN)
        )
        
    def update_scene(self):
        """ update the scene """
        # Update axis size with zoom
        self.renderer.update_object('axis', transform=Transform(scale=self.mouse.screen_to_world(self.AXIS_SIZE, dimension=3)))

        size = self.timer.oscillate_translation(limits=[0.5, 1.5], speed=0.5)
        # Dynamic objects: When possible, update just the transform. This is more efficient than changing the shape
        self.renderer.update_object('circle_green', transform=Transform(translate=(size,0,0)))
        self.renderer.update_object('circle_blue', shape=Shapes.circle(position=(5, 2+size, 0), radius=0.2, colour=Colour.BLUE), static=False, selectable=False)
  
    def events(self):
        """ Process custom events, such as the keyboard & mouse. """
        pass
      
    def render_ui(self):
        """ render the UI """
        
        imgui.begin('Core', flags=imgui.WINDOW_HORIZONTAL_SCROLLING_BAR)
        render_core_ui(self.camera, self.renderer, self.config, self.timer, self.imgui_manager)
        
        # Display bounds info
        if imgui.tree_node("Dangling Buffer Data"):
            if imgui.tree_node("Vertices"):
                for buffer in [self.renderer.static_buffer, self.renderer.dynamic_buffer]:
                    for vertices in buffer.dangling['vertices']:
                        imgui.text(f"Offset: {vertices['offset']}\tSize: {vertices['size']}")
                imgui.tree_pop()
            if imgui.tree_node("Indices"):
                for buffer in [self.renderer.static_buffer, self.renderer.dynamic_buffer]:
                    for indices in buffer.dangling['indices']:
                        imgui.text(f"Offset: {indices['offset']}\tSize: {indices['size']}")
                imgui.tree_pop()
            imgui.tree_pop()
        
        if imgui.button('delete plot_red_line'):
            self.renderer.delete_object('plot_red_line')
        imgui.end()
    
if __name__ == '__main__':
    """  Setup your application. """
    app = Example2DApplication(
        width=1280,
        height=720,
        title='Example 2D PyGLViewer Window',
        camera_settings={ '2d_mode': True, 'target': (4, 0, 0), 'distance': 5 },
        fonts={
            'arial-medium': { 'path': 'C:/Windows/Fonts/arial.ttf', 'size': 16 }, # defaults to first font in list
            'arial_rounded_mt_bold-medium': { 'path': 'C:/Windows/Fonts/ARLRDBD.TTF', 'size': 15 },
        },
        images={
            'image_node': { 'path': './img/image.png' }
        },
        config=Config('example_2d_config.json'),
        enable_docking=True,
        selection_settings=SelectionSettings()
    )
    
    """ Initialise application & start the render loop. """
    if app.init_core():
        app.init()
        app.main_loop()
