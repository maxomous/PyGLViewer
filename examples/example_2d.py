import imgui
import numpy as np
from pyglviewer.core.application import Application
from pyglviewer.core.object_selection import SelectionSettings
from pyglviewer.renderer.objects import ObjectCollection
from pyglviewer.renderer.shader import PointShape
from pyglviewer.utils.colour import Colour
from pyglviewer.utils.config import Config
from pyglviewer.utils.timer import Timer
from pyglviewer.renderer.renderer import RenderParams


class Example2DApplication(Application):
    
    GRID_SIZE = 25
    GRID_TRANSLATE = (0, 0, -0.002)  # Move grid slightly below z=0 to avoid z-fighting
    
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
        grid_params = RenderParams(
            translate=self.GRID_TRANSLATE,
            scale=(1, 1, 1)
        )
        
        self.renderer.add_axis_ticks(size=self.GRID_SIZE, params=grid_params)
        self.grid = self.renderer.add_grid(self.GRID_SIZE, params=grid_params)
                
        # Example sine wave scatter plot
        x1 = np.linspace(-self.GRID_SIZE, self.GRID_SIZE, 500)
        y1 = np.sin(x1)
        x2 = np.linspace(-self.GRID_SIZE, self.GRID_SIZE, 200)
        y2 = np.sin(x2)
        
        # Plot lines with custom widths
        self.renderer.plot(
            x=x1, y=2*y1, 
            colour=Colour.CYAN, 
            params=RenderParams(line_width=3.0)
        )
        self.renderer.plot(
            x=x1, y=-0.5*y1, 
            colour=Colour.RED, 
            params=RenderParams(line_width=3.0)
        )
        
        # Scatter plots with custom point sizes and shapes
        self.renderer.scatter(
            x=x2, y=-1.5*y2, 
            colour=Colour.GREEN, 
            params=RenderParams(point_size=12.0, point_shape=PointShape.CIRCLE)
        )
        self.renderer.scatter(
            x=x2, y=1*y2, 
            colour=Colour.ORANGE, 
            params=RenderParams(point_size=12.0, point_shape=PointShape.TRIANGLE)
        )
        
        # Add circles with custom rendering parameters
        circle_params = RenderParams(show_wireframe=False)
        self.renderer.add_circle(
            radius=0.2, 
            colour=Colour.RED, 
            position=(3, 2, 0),
            params=circle_params
        )
        self.renderer.add_circle(
            radius=0.2, 
            colour=Colour.GREEN, 
            position=(4, 2, 0),
            params=circle_params
        )
        self.renderer.add_circle(
            radius=0.2, 
            colour=Colour.BLUE, 
            position=(5, 2, 0),
            params=circle_params
        )
        
        # Transparent circle
        transparent_circle_params = RenderParams(show_wireframe=False, alpha=0.5)
        self.renderer.add_circle(
            radius=3, 
            colour=Colour.YELLOW, 
            position=(4, 1.5, 0),
            params=transparent_circle_params
        )
        
    def update_scene(self):
        """ update the scene """
        # Update axis size
        if self.camera.distance > 2.5:
            self.grid.set_transform_matrix(scale=(10, 10, 1)) # TODO: Only update on change
        else:
            self.grid.set_transform_matrix(scale=(1, 1, 1))
  
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
