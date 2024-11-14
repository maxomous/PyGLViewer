import imgui
import glfw
import numpy as np
from core.application import Application
from core.object_selection import SelectionSettings
from renderer.light import default_lighting
from utils.color import Color
from utils.config import Config   

class Example2DApplication(Application):
    
    def init(self):
        """ Initialise the application. Create the UI, variables, lighting and geometry. """
        # Add lighting to the scene
        # self.renderer.add_lights(default_lighting)
    
        GRID_SIZE = 20
        GRID_TRANSLATE = (0, 0, -0.002) # Move grid slightly below z=0 to avoid z-fighting
        # Grid and axis
        self.renderer.add_axis_ticks(size=GRID_SIZE, translate=GRID_TRANSLATE, scale=(1, 1, 1))
        self.renderer.add_grid(GRID_SIZE*2, translate=GRID_TRANSLATE)        
        
        # Example sine wave scatter plot
        x = np.linspace(0, 10, 200)
        y = 1.5 * np.sin(x)
        self.renderer.plot(x, y, color=Color.CYAN, line_width=3.0)

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
