# https://visualstudio.microsoft.com/visual-cpp-build-tools/ -> Desktop development with C++
# pip install PyOpenGL
# pip install PyOpenGL_accelerate (optional)
# pip install glfw
# pip install imgui[glfw]
''' OR Imgui docking branch 
  git clone --recurse-submodules https://github.com/pyimgui/pyimgui.git
  cd pyimgui
  git checkout docking
  pip install .[glfw] 
''' # set ENABLE_DOCKING = True
# Imgui intellisense 
#   https://github.com/masc-it/pyimgui-interface-generator/blob/master/imgui.pyi
#   Save to: AppData\Roaming\Python\Python311\site-packages\imgui\__init__.pyi


import os
import glfw
import imgui
import numpy as np
from OpenGL.GL import *
from imgui_manager import ImGuiManager

from camera import ThirdPersonCamera
from color import Color
from input_handlers import Mouse, Keyboard
from light import Light, LightType
from renderer import Renderer, BufferType
from geometry import Geometry

ENABLE_DOCKING = False  # Set this to False to disable docking

class Application:
    def __init__(self, width, height, title):
        self.width = width
        self.height = height
        self.title = title
        self.window = None
        self.camera = None
        self.renderer = None
        self.projection = None
        self.mouse = None
        self.keyboard = None
        self.imgui_manager = None

    def init(self):
        if not glfw.init():
            return False

        self.window = glfw.create_window(self.width, self.height, self.title, None, None)
        if not self.window:
            glfw.terminate()    
            return False
        
        glfw.make_context_current(self.window)
        print(f"OpenGL Version: {glGetString(GL_VERSION).decode()}")
        print(f"GLSL Version: {glGetString(GL_SHADING_LANGUAGE_VERSION).decode()}")
        print(f"ImGui Version: {imgui.get_version()}")
        
        self.camera = ThirdPersonCamera(position=(5, 0, 2), target=(0, 0, 0), up=(0, 0, 1), distance=9)
        self.mouse = Mouse(self.camera)
        self.keyboard = Keyboard(self.camera)
        self.init_renderer()
        self.set_frame_size(self.window, self.width, self.height)

        self.imgui_manager = ImGuiManager(self.window, enable_docking=ENABLE_DOCKING)
        
        font_path = './Fonts/Inter-Light.ttf'
        if not os.path.exists(font_path):
            print(f"Font file not found: {font_path}")
            font_path = 'C:/Windows/Fonts/arial.ttf'
        
        self.imgui_manager.load_font('large', font_path, 24)
        self.imgui_manager.load_font('medium', font_path, 18)
        self.imgui_manager.load_font('small', font_path, 12)

        glfw.set_framebuffer_size_callback(self.window, self.set_frame_size)

        return True

    def set_frame_size(self, window, width, height):
        glViewport(0, 0, width, height)
        self.width = width
        self.height = height
        aspect_ratio = self.width / self.height if self.height > 0 else 1.0
        self.projection = self.camera.get_perspective_projection(45.0, aspect_ratio, 0.1, 100.0)
    
    def init_renderer(self):
        self.renderer = Renderer()
        

        self.renderer.add_point((1,1,1), Color.RED, point_size=5.0)
        self.renderer.add_line((2,1,1), (2,2,2), Color.RED, line_width=5.0)
        
        self.renderer.add_grid(10, 1, Color.GRAY)#, translate=(1, 1, 0), rotate=(0, 0, np.pi/4), scale=(2, 2, 1))

        # self.renderer.add_grid(grid_data['vertices'], grid_data['indices'], Color.WHITE)
        self.renderer.add_axis(scale=(3.0, 3.0, 3.0), line_width=3.0)
        
        segments = 32
        self.renderer.add_circle(position=(1, 2, 0), radius=1.0, segments=segments, color=Color.GREEN, show_body=False, show_wireframe=True, line_width=3.0)
        self.renderer.add_circle(position=(3, 2, 0), radius=0.5, segments=segments, color=Color.GREEN, show_body=False, show_wireframe=True)
        self.renderer.add_cube(Color.RED, translate=(-1, 0, 0), scale=(0.5, 0.5, 0.5), buffer_type=BufferType.Dynamic, show_wireframe=True)
        self.renderer.add_cube(Color.GREEN, translate=(0, 0, 0), scale=(0.5, 0.5, 0.5), buffer_type=BufferType.Dynamic, show_wireframe=True)
        self.renderer.add_cube(Color.BLUE, translate=(1, 0, 0), scale=(0.5, 0.5, 0.5), buffer_type=BufferType.Dynamic, show_wireframe=True)
        self.renderer.add_cube(Color.rgb(255, 165, 0), translate=(0, 1, 0), scale=(0.5, 0.5, 0.5), buffer_type=BufferType.Dynamic, show_wireframe=True)
        self.renderer.add_cube(Color.YELLOW, translate=(0, 0, 1), scale=(0.5, 0.5, 0.5), buffer_type=BufferType.Dynamic, show_wireframe=True)
        self.renderer.add_cone(Color.rgb(255, 165, 0), segments=segments, translate=(5, 0, 0), scale=(0.5, 0.5, 0.5), show_wireframe=True)
        self.renderer.add_cylinder(Color.WHITE, segments=segments, translate=(2, 0, 0), scale=(0.5, 0.5, 0.5), show_wireframe=True)
        self.renderer.add_sphere(translate=(3,0,0), radius=0.5, stacks=16, sectors=16, color=Color.WHITE)
        self.init_lights()

    def init_lights(self):
        lights = {  
            # Slightly warm color
            "main": { "type": LightType.DIRECTIONAL, "position": (10, 10, 10), "target": (0, 0, 0), "color": (1.0, 0.95, 0.8),"intensity": 0.5},
            "main2": { "type": LightType.DIRECTIONAL, "position": (-10, -10, 10), "target": (0, 0, 0), "color": (1.0, 0.95, 0.8),"intensity": 0.5},
            "ambient": { "type": LightType.DIRECTIONAL, "direction": (0, 0, -1),  "color": (0.2, 0.2, 0.3), "intensity": 0.6 },
            "front":  {"type": LightType.DIRECTIONAL, "position": (0, 10, 0), "target": (0, 0, 0), "color": (0.9, 0.9, 1.0), "intensity": 0.3},
            "back":   {"type": LightType.DIRECTIONAL, "position": (0, -10, 0), "target": (0, 0, 0), "color": (1.0, 0.9, 0.8), "intensity": 0.3},
            "left":   {"type": LightType.DIRECTIONAL, "position": (-10, 0, 0), "target": (0, 0, 0), "color": (0.8, 1.0, 0.8), "intensity": 0.3},
            "right":  {"type": LightType.DIRECTIONAL, "position": (10, 0, 0), "target": (0, 0, 0), "color": (1.0, 0.8, 0.8), "intensity": 0.3},
            # "top":    {"type": LightType.DIRECTIONAL, "position": (0, 0, 10), "target": (0, 0, 0), "color": (0.9, 0.9, 1.0), "intensity": 0.3},
            "bottom": {"type": LightType.DIRECTIONAL, "position": (0, 0, -10), "target": (0, 0, 0), "color": (1.0, 0.9, 0.8), "intensity": 0.3},
        }
        # Create and add lights to the renderer
        for fill_light_data in lights.values():
            self.renderer.add_light(Light(**fill_light_data))

        # # Draw arrows for all lights
        # for light in self.renderer.lights:
        #     if light.position is not None:
        #         self.renderer.add_arrow(light.position, light.direction, color=Color.RED)
            
    def run(self):
        while not glfw.window_should_close(self.window):
            self.process_frame()
        self.cleanup()

    def process_frame(self):
        self.handle_events()
        self.update()
        self.render()

    def handle_events(self):
        glfw.poll_events()
        self.imgui_manager.process_inputs()

    def update(self):
        self.mouse.process_input()
        self.keyboard.process_input()

    def render(self):
        self.imgui_manager.new_frame()
        self.renderer.clear()

        self.imgui_manager.push_font('medium')
        self.imgui_manager.render_dockspace()
    
        self.render_debug_window()
        self.render_demo_window()
        
        self.render_3d_scene()
        self.imgui_manager.end_dockspace()
        self.imgui_manager.pop_font()
        self.imgui_manager.render()

        glfw.swap_buffers(self.window)

    def render_debug_window(self):
        imgui.begin("Debug Window")
        imgui.text(f"Camera Position: {self.camera.position}")
        imgui.text(f"Camera Target: {self.camera.target}")
        imgui.text(f"FPS: {1.0 / glfw.get_time():.1f}")
        glfw.set_time(0)  # Reset the timer
        imgui.text(f"Pan Sensitivity: {self.mouse.pan_sensitivity:.4f}")
        imgui.text(f"Scroll Sensitivity: {self.mouse.scroll_sensitivity:.4f}")
        imgui.text(f"Camera Distance: {self.camera.distance:.2f}")
        imgui.end()


    def render_demo_window(self):
        imgui.show_demo_window()

    def render_3d_scene(self):
        view_matrix = self.camera.get_view_matrix()
        camera_position = self.camera.position

        # Update renderer with new matrices and camera position
        self.renderer.set_view_matrix(view_matrix)
        self.renderer.set_projection_matrix(self.projection)
        self.renderer.set_camera_position(camera_position)

        # Draw the scene
        self.renderer.draw()

    def cleanup(self):
        self.imgui_manager.shutdown()
        glfw.terminate()


if __name__ == "__main__":
    app = Application(800, 600, "Third Person Camera")
    if app.init():
        app.run()

