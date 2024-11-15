import imgui
import glfw
import numpy as np
from core.application import Application
from core.object_selection import SelectionSettings
from renderer.light import default_lighting
from renderer.objects import ObjectCollection
from utils.color import Color
from utils.config import Config
from utils.timer import Timer

class Example2DApplication(Application):
    
    def init(self):
        """ Initialise the application. Create the UI, variables, lighting and geometry. """
        GRID_SIZE = 20
        GRID_TRANSLATE = (0, 0, -0.002) # Move grid slightly below z=0 to avoid z-fighting
        # Grid and axis
        self.renderer.add_axis_ticks(size=GRID_SIZE, translate=GRID_TRANSLATE, scale=(1, 1, 1))
        self.renderer.add_grid(GRID_SIZE*2, translate=GRID_TRANSLATE)     
        angle = self.timer.oscillate_angle(1)
        # Example sine wave scatter plot
        x1 = np.linspace(0, 10, 200)
        y1 = np.sin(x1)
        x2 = np.linspace(0, 10, 50)
        y2 = np.sin(x2)
        self.plots = ObjectCollection({
            'plot_1': self.renderer.plot(x1, 1.5*y1, color=Color.CYAN, line_width=3.0),
            'plot_2': self.renderer.plot(x1, -0.75*y1, color=Color.RED, line_width=3.0),
            'scatter_1': self.renderer.scatter(x2, 0.5*y2, color=Color.GREEN, point_size=10.0)
        })

        self.camera.set_2d_mode(True)
        self.camera.set_projection(orthographic=True)
        
    def update_scene(self):
        """ update the scene """
        pass
        
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
