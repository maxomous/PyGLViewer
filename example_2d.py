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
        self.camera.set_2d_mode(True)
        self.camera.set_projection(orthographic=True)
        
        # Grid and axis
        self.text_renderer.add_axis_labels(
            xlim=[-self.GRID_SIZE, self.GRID_SIZE], 
            ylim=[-self.GRID_SIZE, self.GRID_SIZE], 
            increment=1, 
            colour=Colour.WHITE, 
            static=True
        )
        # Create grid params with translation
        self.grid = self.renderer.add_object(Object(static=True, selectable=False)\
            .set_shapes(Shapes.grid(size=self.GRID_SIZE*2, increment=1, colour=Colour.WHITE))\
            .set_transform_matrix(Transform(translate=self.GRID_TRANSLATE)))
        self.axis_ticks = self.renderer.add_object(Object(static=True, selectable=False)\
            .set_shapes(Shapes.axis_ticks(size=self.GRID_SIZE))\
            .set_transform_matrix(Transform(translate=self.GRID_TRANSLATE)))
        self.axis = self.renderer.add_object(Object(static=True, selectable=False)\
            .set_shapes(Shapes.axis(size=1))\
            .set_transform_matrix(Transform(translate=self.GRID_TRANSLATE)))
        
        # Transparent circle
        self.renderer.add_object(Object(static=True, alpha=0.2)\
            .set_shapes(Shapes.circle(position=(3, 1, 0), radius=0.1, colour=Colour.YELLOW))\
            .set_transform_matrix(Transform(translate=self.GRID_TRANSLATE)))
        # Rectangle
        self.renderer.add_object(Object(static=True, alpha=0.5)\
            .set_shapes(Shapes.rectangle(position=(4, 1, 0), width=0.1, height=0.1, colour=Colour.RED))\
            .set_transform_matrix(Transform(translate=self.GRID_TRANSLATE)))
        # Triangle
        self.renderer.add_object(Object(static=True, alpha=0.8)\
            .set_shapes(Shapes.triangle(p1=(5, 1.1, 0), p2=(4.9, 0.9, 0), p3=(5.1, 0.9, 0), colour=Colour.GREEN))\
            .set_transform_matrix(Transform(translate=self.GRID_TRANSLATE)))
        
        # Example sine wave scatter plot
        x1 = np.linspace(-self.GRID_SIZE, self.GRID_SIZE, 500)
        y1 = np.sin(x1)
        x2 = np.linspace(-self.GRID_SIZE, self.GRID_SIZE, 200)
        y2 = np.sin(x2)
        
        # Plot lines with custom widths
        self.renderer.add_object(Object(static=True, selectable=False, line_width=1.0)\
            .set_shapes(Shapes.plot(x=x1, y=2*y1, colour=Colour.CYAN))\
            .set_transform_matrix(Transform(translate=self.GRID_TRANSLATE)))
        self.renderer.add_object(Object(static=True, selectable=False, line_width=3.0)\
            .set_shapes(Shapes.plot(x=x1, y=-0.5*y1, colour=Colour.RED))\
            .set_transform_matrix(Transform(translate=self.GRID_TRANSLATE)))
        
        # Scatter plots with custom point sizes and shapes
        self.renderer.add_object(Object(static=True, selectable=False, point_size=12.0, point_shape=PointShape.CIRCLE)\
            .set_shapes(Shapes.scatter(x=x2, y=-1.5*y2, colour=Colour.GREEN))\
            .set_transform_matrix(Transform(translate=self.GRID_TRANSLATE)))
        self.renderer.add_object(Object(static=True, selectable=False, point_size=12.0, point_shape=PointShape.TRIANGLE)\
            .set_shapes(Shapes.scatter(x=x2, y=1*y2, colour=Colour.ORANGE))\
            .set_transform_matrix(Transform(translate=self.GRID_TRANSLATE)))
        
        # Add circles with custom rendering parameters
        self.renderer.add_object(Object(static=True, selectable=False)\
            .set_shapes(Shapes.circle(position=(3, 2, 0), radius=0.2, colour=Colour.RED))\
            .set_transform_matrix(Transform(translate=self.GRID_TRANSLATE)))
        self.renderer.add_object(Object(static=True, selectable=False)\
            .set_shapes(Shapes.circle(position=(4, 2, 0), radius=0.2, colour=Colour.GREEN))\
            .set_transform_matrix(Transform(translate=self.GRID_TRANSLATE)))
        self.renderer.add_object(Object(static=True, selectable=False)\
            .set_shapes(Shapes.circle(position=(5, 2, 0), radius=0.2, colour=Colour.BLUE))\
            .set_transform_matrix(Transform(translate=self.GRID_TRANSLATE)))
        
    def update_scene(self):
        """ update the scene """
        # Update axis size
        self.axis.set_transform_matrix(Transform(scale=self.mouse.screen_to_world(self.AXIS_SIZE, dimension=3)))

        # Update axis size
        if self.camera.distance > 2.5:
            self.grid.set_transform_matrix(Transform(scale=(10, 10, 1))) # TODO: Only update on change
        else:
            self.grid.set_transform_matrix(Transform(scale=(1, 1, 1)))
  
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
        camera_settings={ 'target': (4, 0, 0), 'distance': 5 },
        fonts={
            'arial-medium': { 'path': 'C:/Windows/Fonts/arial.ttf', 'size': 16 },
            'arial_rounded_mt_bold-medium': { 'path': 'C:/Windows/Fonts/ARLRDBD.TTF', 'size': 15 },
        },
        default_font='arial-medium',
        config=Config('example_2d_config.json'),
        enable_docking=True,
        selection_settings=SelectionSettings()
    )
    
    """ Initialise application & start the render loop. """
    if app.init_core():
        app.init()
        app.main_loop()
