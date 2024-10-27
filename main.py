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
from parameters import parameters as p

ENABLE_DOCKING = True  # Set this to False to disable docking

class Application:
    def __init__(self, width, height, title):
        self.width = width
        self.height = height
        self.aspect_ratio = None
        self.title = title
        self.window = None
        self.camera = None
        self.renderer = None
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
                
        print(f'OpenGL Version: {glGetString(GL_VERSION).decode()}')
        print(f'GLSL Version: {glGetString(GL_SHADING_LANGUAGE_VERSION).decode()}')
        print(f'ImGui Version: {imgui.get_version()}')
        
        self.camera = ThirdPersonCamera(position=(5, 0, 2), target=(0, 0, 0), up=(0, 0, 1), distance=9)
        self.mouse = Mouse(self.camera)
        self.keyboard = Keyboard(self.camera)
        self.init_renderer()
        self.set_frame_size(self.window, self.width, self.height) # also initialises camera

        self.imgui_manager = ImGuiManager(self.window, enable_docking=ENABLE_DOCKING)
        
        font_path = './Fonts/Inter-Light.ttf'
        if not os.path.exists(font_path):
            print(f'Font file not found: {font_path}')
            font_path = 'C:/Windows/Fonts/arial.ttf'
        
        self.imgui_manager.load_font('large', font_path, 24)
        self.imgui_manager.load_font('medium', font_path, 17)
        self.imgui_manager.load_font('small', font_path, 12)

        glfw.set_framebuffer_size_callback(self.window, self.set_frame_size)

        return True

    def set_frame_size(self, window, width, height):
        glViewport(0, 0, width, height)
        self.width = width
        self.height = height
        self.camera.set_aspect_ratio(width, height)
        self.camera.update_projection()
    
    
    def init_renderer(self):
        self.renderer = Renderer()
        segments = 32  # Define segments here for consistent use

        # Add grid and axis
        self.renderer.add_grid(10, 1, Color.GRAY)
        self.renderer.add_axis(size=1)

        # Row 1 (all wireframe with consistent thickness, different colors)
        point_size = 7.0  # Consistent line thickness for all shapes
        line_thickness = 3.0  # Consistent line thickness for all shapes

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

        self.init_lights()

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

    def create_imgui_table(self, table_id, headers, rows, flags=0):
        ''' Add TABLE_ROW_HEADERS to flags to add headers '''
        if imgui.begin_table(table_id, len(headers), flags):
            # Setup columns
            for header in headers:
                imgui.table_setup_column(header, imgui.TABLE_COLUMN_WIDTH_STRETCH)
            
            # Optionally add headers
            if flags & imgui.TABLE_ROW_HEADERS:
                imgui.table_headers_row()
            
            # Add rows
            for row in rows:
                imgui.table_next_row()
                for cell in row:
                    imgui.table_next_column()
                    imgui.text(str(cell))
            
            imgui.end_table()
            return True
        return False

    def render_debug_window(self):
        imgui.begin('Debug Window', flags=imgui.WINDOW_ALWAYS_AUTO_RESIZE)

        if imgui.collapsing_header('Camera', flags=imgui.TREE_NODE_DEFAULT_OPEN)[0]:
            imgui.indent()

            # Camera Settings
            if imgui.tree_node('View Mode', flags=imgui.TREE_NODE_DEFAULT_OPEN):
                changed, _ = imgui.checkbox('2D Mode', self.camera.is_2d_mode)
                if changed:
                    self.camera.toggle_2d_mode()
                    self.camera.update_projection()
                
                changed, _ = imgui.checkbox('Orthographic Projection', self.camera.is_orthographic)
                if changed:
                    self.camera.toggle_projection()
                    self.camera.update_projection()
                imgui.tree_pop()
                
            # Camera Information
            if imgui.tree_node('Information'):
                
                self.create_imgui_table(
                    table_id='camera_info',
                    headers=['', ''],
                    rows=[
                        ('Position',    self.camera.position.round(2)),
                        ('Target',      self.camera.target.round(2)),
                        ('Yaw',         f'{self.camera.yaw:.2f}°'),
                        ('Pitch',       f'{self.camera.pitch:.2f}°'),
                        ('Distance',    f'{self.camera.distance:.2f}'),
                        ('Front',       self.camera.front.round(2)),
                        ('Up',          self.camera.up.round(2)),
                        ('Right',       self.camera.right.round(2)),
                        ('World Up',    self.camera.world_up.round(2))
                    ]
                )
                imgui.tree_pop()

            imgui.unindent()

        # Input Settings Section
        if imgui.collapsing_header('Mouse', flags=imgui.TREE_NODE_DEFAULT_OPEN)[0]:
            imgui.indent()
                
            # Sensitivity settings in a tree node
            if imgui.tree_node('Sensitivity'):
                # Calculate width to account for text label
                text_width = 120  # Adjust this value based on your longest label
                slider_width = imgui.get_content_region_available()[0] - text_width
                
                imgui.push_item_width(slider_width)
                _, p["base_pan_sensitivity"] = imgui.slider_float('Pan Sensitivity', p["base_pan_sensitivity"], 0.001, 0.1, '%.4f')
                _, p["base_scroll_sensitivity"] = imgui.slider_float('Scroll Sensitivity', p["base_scroll_sensitivity"], 0.1, 2.0, '%.2f')
                _, p["rotate_sensitivity"] = imgui.slider_float('Rotate Sensitivity', p["rotate_sensitivity"], 0.01, 0.5, '%.2f')
                imgui.pop_item_width()
                imgui.tree_pop()
            
            # Invert controls in a tree node
            if imgui.tree_node('Invert'):
                # Rotate invert
                invert_yaw_pitch = p["invert_yaw_pitch"]
                _, yaw = imgui.checkbox('Invert Rotate X', invert_yaw_pitch[0] > 0)
                _, pitch = imgui.checkbox('Invert Rotate Y', invert_yaw_pitch[1] > 0)
                p["invert_yaw_pitch"] = [1 if x else -1 for x in (yaw, pitch)]
                
                # Pan invert
                invert_pan = p["invert_pan"]
                _, pan_x = imgui.checkbox('Invert Pan X', invert_pan[0] > 0)
                _, pan_y = imgui.checkbox('Invert Pan Y', invert_pan[1] > 0)
                p["invert_pan"] = [1 if x else -1 for x in (pan_x, pan_y)]
                
                # Scroll invert
                _, scroll = imgui.checkbox('Invert Scroll', p["invert_scroll"] > 0)
                p["invert_scroll"] = 1 if scroll else -1
                imgui.tree_pop()
            
            imgui.unindent()

        # Performance Section
        if imgui.collapsing_header('Performance', flags=imgui.TREE_NODE_DEFAULT_OPEN)[0]:
            imgui.indent()
            imgui.text(f'FPS: {1.0 / glfw.get_time():.1f}')
            glfw.set_time(0)  # Reset the timer
            imgui.unindent()

        # Parameters Section
        if imgui.collapsing_header('Parameters', flags=imgui.TREE_NODE_DEFAULT_OPEN)[0]:
            imgui.indent()
            
            # Control buttons
            imgui.push_style_var(imgui.STYLE_FRAME_PADDING, (6, 6))  # Make the buttons larger by increasing padding around text
            
            if imgui.button("Reset to Defaults"):
                p.reset_to_defaults()
            
            imgui.same_line()
            if imgui.button("Save"):
                p.save()
            
            imgui.same_line()
            if imgui.button("Load"):
                p.load()
            
            imgui.pop_style_var()  # Restore original padding
            
            imgui.unindent()

        imgui.end()


    def render_demo_window(self):
        imgui.show_demo_window()

    def render_3d_scene(self):
        view_matrix = self.camera.get_view_matrix()
        projection = self.camera.get_projection_matrix()
        camera_position = self.camera.position
        
        # Update renderer with new matrices and camera position
        self.renderer.set_view_matrix(view_matrix)
        self.renderer.set_projection_matrix(projection)
        self.renderer.set_camera_position(camera_position)

        # Draw the scene
        self.renderer.draw()

    def cleanup(self):
        p.save() # save parameters to file
        self.imgui_manager.shutdown()
        glfw.terminate()


if __name__ == '__main__':
    app = Application(1280, 720, 'Third Person Camera')
    if app.init():
        app.run()

