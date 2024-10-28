from base_application import BaseApplication
from base_ui import render_camera_section, render_mouse_section, render_performance_section, render_parameters_section
from parameters import parameters as p
import imgui
import glfw
import numpy as np
from color import Color
from light import Light, LightType
from renderer import BufferType

class Application(BaseApplication):
    def init_scene(self):
        """Initialize the 3D scene with geometry and lights"""
        self.init_geometry()
        self.init_lights()

    def init_geometry(self):
        segments = 32
        self.renderer.add_grid(10, 1, Color.GRAY)
        self.renderer.add_axis(size=1)

        # Row 1 (all wireframe with consistent thickness, different colors)
        point_size = 7.0
        line_thickness = 3.0

        self.renderer.add_point((-4, 4, 0), Color.RED, point_size=point_size)
        self.renderer.add_line((-2.5, 3.5, 0), (-1.5, 4.5, 0), Color.ORANGE, line_width=line_thickness)
        self.renderer.add_triangle((0, 4.433, 0), (-0.5, 3.567, 0), (0.5, 3.567, 0), wireframe_color=Color.YELLOW, show_wireframe=True, show_body=False, line_width=line_thickness)
        self.renderer.add_rectangle((2, 4), 1, 1, wireframe_color=Color.GREEN, show_wireframe=True, show_body=False, line_width=line_thickness)
        self.renderer.add_circle(position=(4, 4, 0), radius=0.5, segments=segments, wireframe_color=Color.BLUE, show_body=False, line_width=line_thickness)

        # Row 2 (filled shapes)
        self.renderer.add_circle(position=(-4, 2, 0), radius=0.5, segments=segments, color=Color.GREEN, show_body=True)
        self.renderer.add_cube(Color.RED, translate=(-2, 2, 0.5), scale=(0.5, 0.5, 0.5), rotate=(np.pi/4, np.pi/4, 0), buffer_type=BufferType.Dynamic, show_body=True)
        self.renderer.add_cone(Color.rgb(255, 165, 0), segments=segments, translate=(0, 2, 0.5), scale=(0.5, 0.5, 0.5), show_body=True)
        self.renderer.add_cylinder(Color.WHITE, segments=segments, translate=(2, 2, 0.5), scale=(0.5, 0.5, 0.5), show_body=True)
        self.renderer.add_sphere(translate=(4, 2, 0.5), radius=0.25, subdivisions=4, color=Color.WHITE)

        # Row 3 (filled shapes)
        self.renderer.add_cube(Color.YELLOW, translate=(-4, 0, 0.5), scale=(0.5, 0.5, 0.5), buffer_type=BufferType.Dynamic, show_body=True)
        self.renderer.add_arrow((-2.4, -0.4, 0.25), (-1.6, 0.4, 0.75), shaft_radius=0.2, head_radius=0.4, head_length=0.3, color=Color.RED, show_body=True)

    def init_lights(self):
        lights = {  
            'main': {
                'type': LightType.DIRECTIONAL, 
                'position': (10, 10, 10), 
                'target': (0, 0, 0), 
                'color': (1.0, 0.95, 0.8),
                'intensity': 0.4
            },
            'ambient': {
                'type': LightType.AMBIENT, 
                'color': (1, 1, 1), 
                'intensity': 0.7
            },
            'fill': {
                'type': LightType.DIRECTIONAL, 
                'position': (-5, 5, -5), 
                'target': (0, 0, 0), 
                'color': (0.8, 0.9, 1.0), 
                'intensity': 0.3
            }
        }
        for light_data in lights.values():
            self.renderer.add_light(Light(**light_data))

    def render_debug_window(self):
        imgui.begin('Debug Window', flags=imgui.WINDOW_ALWAYS_AUTO_RESIZE)
        
        render_camera_section(self.camera)
        render_mouse_section(p)
        render_performance_section(self.timer.get_delta_time()) 
        render_parameters_section(p)

        imgui.end()

    def render_ui(self):
        """Called by BaseApplication.render()"""
        self.render_debug_window()
        imgui.show_demo_window()

if __name__ == '__main__':
    
    # Font configuration
    fonts = {
        'arial-large': {
            'path': 'C:/Windows/Fonts/arial.ttf',
            'size': 24
        },
        'arial-medium': {
            'path': 'C:/Windows/Fonts/arial.ttf',
            'size': 17
        },
        'arial-small': {
            'path': 'C:/Windows/Fonts/arial.ttf',
            'size': 12
        }
    }
    
    # Create application with settings
    app = Application(
        width=1280,
        height=720,
        title='Example PyGLViewer Window',
        camera_settings={
            'target': (0, 0, 0),
            'distance': 10
        },
        fonts=fonts,
        default_font='arial-medium'
    )
    
    if app.init():
        app.init_scene()
        app.run()
