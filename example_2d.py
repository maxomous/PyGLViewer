import imgui
import numpy as np
from pyglviewer.core.application import Application
from pyglviewer.core.object_selection import SelectionSettings
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
        """ Initialise the application. Create the UI, variables, lighting and geometry. """
        # Set 2D mode and orthographic projection
        # self.camera.set_2d_mode(True)
        self.camera.set_projection(orthographic=True)
        
        # Store the static texts in case we want to remove them later (same process for images)
        self.static_text = {}
        # Grid and axis
        self.static_text['axis_labels'] = self.imgui_overlay_renderer.add_axis_labels(
            xlim=[-self.GRID_SIZE, self.GRID_SIZE], 
            ylim=[-self.GRID_SIZE, self.GRID_SIZE], 
            increment=1, 
            colour=Colour.WHITE, 
            static=True
        )
        # Remove static text
        # self.imgui_overlay_renderer.remove_text(self.static_text['axis_labels'])
        
        # Create grid params with translation
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
            shape=Shapes.circle(position=(3, 1, 0), radius=0.1, colour=Colour.YELLOW),
            transform=Transform(translate=self.GRID_TRANSLATE)
        )
        # Rectangle
        self.renderer.update_object( 'rectangle', static=True, alpha=0.5,
            shape=Shapes.rectangle(position=(4, 1, 0), width=0.1, height=0.1, colour=Colour.RED),
            transform=Transform(translate=self.GRID_TRANSLATE)
        )
        # Triangle
        self.renderer.update_object('triangle', static=True, alpha=0.8,
            shape=Shapes.triangle(p1=(5, 1.1, 0), p2=(4.9, 0.9, 0), p3=(5.1, 0.9, 0), colour=Colour.GREEN),
            transform=Transform(translate=self.GRID_TRANSLATE)
        )
        
        # Example sine wave scatter plot
        x1 = np.linspace(-self.GRID_SIZE, self.GRID_SIZE, 500)
        y1 = np.sin(x1)
        x2 = np.linspace(-self.GRID_SIZE, self.GRID_SIZE, 200)
        y2 = np.sin(x2)

        # Plot lines with custom widths
        self.renderer.update_object('plot_cyan_line', static=True, selectable=False, line_width=1.0,
            shape=Shapes.plot(x=x1, y=2*y1, colour=Colour.CYAN),
            transform=Transform(translate=self.GRID_TRANSLATE)
        )
        self.renderer.update_object('plot_red_line', static=True, selectable=False, line_width=3.0,
            shape=Shapes.plot(x=x1, y=-0.5*y1, colour=Colour.RED),
            transform=Transform(translate=self.GRID_TRANSLATE)
        )

        # Scatter plots with custom point sizes and shapes
        self.renderer.update_object('scatter_green_circle', static=True, selectable=False, point_size=12.0, point_shape=PointShape.CIRCLE,
            shape=Shapes.scatter(x=x2, y=-1.5*y2, colour=Colour.GREEN),
            transform=Transform(translate=self.GRID_TRANSLATE)
        )
        self.renderer.update_object('scatter_orange_triangle', static=True, selectable=False, point_size=12.0, point_shape=PointShape.TRIANGLE,
            shape=Shapes.scatter(x=x2, y=1*y2, colour=Colour.ORANGE),
            transform=Transform(translate=self.GRID_TRANSLATE)
        )

        # Add circles with custom rendering parameters
        self.renderer.update_object('circle_red', static=True, selectable=False,
            shape=Shapes.circle(position=(3, 2, 0), radius=0.2, colour=Colour.RED),
            transform=Transform(translate=self.GRID_TRANSLATE)
        )
        self.renderer.update_object('circle_green', static=False, selectable=False,
            shape=Shapes.circle(position=(4, 2, 0), radius=0.2, colour=Colour.GREEN),
            transform=Transform(translate=self.GRID_TRANSLATE)
        )
        self.renderer.update_object('circle_blue', static=False, selectable=False,
            shape=Shapes.circle(position=(5, 2, 0), radius=0.2, colour=Colour.BLUE),
            transform=Transform(translate=self.GRID_TRANSLATE)
        )

    def update_scene(self):
        """ update the scene """
        # Update axis size with zoom
        self.renderer.update_object('axis', transform=Transform(scale=self.mouse.screen_to_world(self.AXIS_SIZE, dimension=3)))

        size = self.timer.oscillate_translation(limits=[0.5, 1.5], speed=0.5)
        # Dynamic objects
        self.renderer.update_object('circle_green', transform=Transform(translate=(size,0,0)))
        self.renderer.update_object('circle_blue', shape=Shapes.circle(position=(5, 2+size, 0), radius=0.2, colour=Colour.BLUE))
  
    def events(self):
        """ Process custom events, such as the keyboard & mouse. """
        pass
      
    def render_ui(self):
        """ render the UI """
        pass
    
if __name__ == '__main__':
    """  Setup your application. """
    app = Example2DApplication(
        width=1280,
        height=720,
        title='Example 2D PyGLViewer Window',
        camera_settings={ '2d_mode': True, 'target': (4, 0, 0), 'distance': 5 },
        fonts={
            'arial-medium': { 'path': 'C:/Windows/Fonts/arial.ttf', 'size': 16 },
            'arial_rounded_mt_bold-medium': { 'path': 'C:/Windows/Fonts/ARLRDBD.TTF', 'size': 15 },
        },
        default_font='arial-medium',
        images={},
        config=Config('example_2d_config.json'),
        enable_docking=True,
        selection_settings=SelectionSettings()
    )
    
    """ Initialise application & start the render loop. """
    if app.init_core():
        app.init()
        app.main_loop()
