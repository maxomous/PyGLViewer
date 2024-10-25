from OpenGL.GL import *
import numpy as np
from geometry import Geometry
from color import Color
from shaders import Shader, basic_vertex_shader, basic_fragment_shader
from gl_objects import BufferType, VertexBuffer, IndexBuffer, VertexArray, RenderObject
from geometry import GeometryData





class Renderer:
    def __init__(self):
        self.lights = []
        self.objects = []
        self.wireframe_color = Color.WHITE
        self.default_shader = Shader(basic_vertex_shader, basic_fragment_shader)
        # Initialize OpenGL
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_CULL_FACE)
        glCullFace(GL_BACK)
        self.view_matrix = None
        self.projection_matrix = None
        self.camera_position = None
        self.lights_need_update = True
    
    def set_view_matrix(self, view_matrix):
        if not np.array_equal(self.view_matrix, view_matrix):
            self.view_matrix = view_matrix
            self.default_shader.use()
            self.default_shader.set_view_matrix(view_matrix)

    def set_projection_matrix(self, projection_matrix):
        if not np.array_equal(self.projection_matrix, projection_matrix):
            self.projection_matrix = projection_matrix
            self.default_shader.use()
            self.default_shader.set_projection_matrix(projection_matrix)

    def set_camera_position(self, camera_position):
        if not np.array_equal(self.camera_position, camera_position):
            self.camera_position = camera_position
            self.default_shader.use()
            self.default_shader.set_view_position(camera_position)

    def update_lights(self):
        if self.lights_need_update:
            self.default_shader.use()
            self.default_shader.set_light_uniforms(self.lights)
            self.lights_need_update = False

    def add_light(self, light):
        self.lights.append(light)
        self.lights_need_update = True

    def draw(self):
        self.update_lights()
        for obj in self.objects:
            obj.shader.use()
            obj.va.bind()
            obj.ib.bind()
            
            # Set object-specific uniforms
            obj.shader.set_uniform("model", obj.model_matrix)
            
            # Set point size / line width
            if obj.draw_type == GL_POINTS:
                glPointSize(obj.point_size)
            elif obj.draw_type in (GL_LINES, GL_LINE_LOOP, GL_LINE_STRIP):
                glLineWidth(obj.line_width)
            
            glDrawElements(obj.draw_type, obj.ib.count, GL_UNSIGNED_INT, None)
            
            obj.va.unbind()
            obj.ib.unbind()

        # Reset to default state
        glEnable(GL_DEPTH_TEST)
        glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
        glLineWidth(1.0)
        glPointSize(1.0)
        
    def clear(self):
        glClearColor(0.2, 0.3, 0.3, 1.0)  # Set a dark teal background color
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)


    def add_point(self, position, color, point_size=1.0, shader=None, buffer_type=BufferType.Static, translate=(0,0,0), rotate=(0,0,0), scale=(1,1,1)):
        geometry = Geometry.create_point(position, color).transform(translate, rotate, scale)
        return self.add_object(geometry, buffer_type, shader, GL_POINTS, point_size=point_size)

    def add_line(self, start, end, color, line_width=1.0, shader=None, buffer_type=BufferType.Static, translate=(0,0,0), rotate=(0,0,0), scale=(1,1,1)):
        geometry = Geometry.create_line(start, end, color).transform(translate, rotate, scale)
        return self.add_object(geometry, buffer_type, shader, GL_LINES, line_width=line_width)

    def add_triangle(self, p1, p2, p3, color, line_width=1.0, shader=None, buffer_type=BufferType.Static, show_body=True, show_wireframe=False, translate=(0,0,0), rotate=(0,0,0), scale=(1,1,1)):
        objects = []
        if show_body:
            geometry = Geometry.create_triangle(p1, p2, p3, color).transform(translate, rotate, scale)
            objects += self.add_object(geometry, buffer_type, shader, GL_TRIANGLES)
        if show_wireframe:
            geometry = Geometry.create_triangle(p1, p2, p3, self.wireframe_color).transform(translate, rotate, scale)
            objects += self.add_object(geometry, buffer_type, shader, GL_LINES, line_width=line_width)
        return objects

    def add_rectangle(self, position, width, height, color, line_width=1.0, shader=None, buffer_type=BufferType.Static, show_body=True, show_wireframe=False, translate=(0,0,0), rotate=(0,0,0), scale=(1,1,1)):
        objects = []
        if show_body:
            geometry = Geometry.create_rectangle(position[0], position[1], width, height, color).transform(translate, rotate, scale)
            objects += self.add_object(geometry, buffer_type, shader, GL_TRIANGLES)
        if show_wireframe:
            geometry = Geometry.create_rectangle_wireframe(position[0], position[1], width * 1.01, height * 1.01, self.wireframe_color).transform(translate, rotate, scale)
            objects += self.add_object(geometry, buffer_type, shader, GL_LINES, line_width=line_width)
        return objects
        

    def add_circle(self, centre, radius, segments, color, line_width=1.0, shader=None, buffer_type=BufferType.Static, show_body=True, show_wireframe=False, translate=(0,0,0), rotate=(0,0,0), scale=(1,1,1)):
        objects = []
        if show_body:
            geometry = Geometry.create_circle(centre, radius, segments, color).transform(translate, rotate, scale)
            objects += self.add_object(geometry, buffer_type, shader, GL_TRIANGLE_FAN)
        if show_wireframe:
            geometry = Geometry.create_circle_wireframe(centre, radius * 1.01, segments, self.wireframe_color).transform(translate, rotate, scale)
            objects += self.add_object(geometry, buffer_type, shader, GL_LINE_LOOP, line_width=line_width)
        return objects

    def add_cube(self, position, size, color, line_width=1.0, shader=None, buffer_type=BufferType.Static, show_body=True, show_wireframe=False, translate=(0,0,0), rotate=(0,0,0), scale=(1,1,1)):
        objects = []
        if show_body:
            geometry = Geometry.create_cube(position, size, color).transform(translate, rotate, scale)
            objects += self.add_object(geometry, buffer_type, shader, GL_TRIANGLES)
        if show_wireframe:
            geometry = Geometry.create_cube_wireframe(position, size * 1.01, self.wireframe_color).transform(translate, rotate, scale)
            objects += self.add_object(geometry, buffer_type, shader, GL_LINES, line_width=line_width)
        return objects

    def add_cylinder(self, start, direction, length, radius, segments, color, line_width=1.0, shader=None, buffer_type=BufferType.Static, show_body=True, show_wireframe=False, translate=(0,0,0), rotate=(0,0,0), scale=(1,1,1)):
        objects = []
        if show_body:
            geometry = Geometry.create_cylinder(start, direction, length, radius, segments, color).transform(translate, rotate, scale)
            objects += self.add_object(geometry, buffer_type, shader, GL_TRIANGLES)
        if show_wireframe:
            geometry = Geometry.create_cylinder_wireframe(start, direction, length, radius * 1.01, segments, self.wireframe_color).transform(translate, rotate, scale)
            objects += self.add_object(geometry, buffer_type, shader, GL_LINES, line_width=line_width)
        return objects

    def add_cone(self, start, direction, length, radius, segments, color, line_width=1.0, shader=None, buffer_type=BufferType.Static, show_body=True, show_wireframe=False, translate=(0,0,0), rotate=(0,0,0), scale=(1,1,1)):
        objects = []
        if show_body:
            geometry = Geometry.create_cone(start, direction, length, radius, segments, color).transform(translate, rotate, scale)
            objects += self.add_object(geometry, buffer_type, shader, GL_TRIANGLES)
        if show_wireframe:
            geometry = Geometry.create_cone_wireframe(start, direction, length, radius * 1.01, segments, self.wireframe_color).transform(translate, rotate, scale)
            objects += self.add_object(geometry, buffer_type, shader, GL_LINES, line_width=line_width)
        return objects

    def add_arrow(self, start, end, shaft_radius=0.05, head_radius=0.1, head_length=0.3, color=Color.WHITE, wireframe_color=Color.BLACK, segments=16, shader=None, buffer_type=BufferType.Static, show_wireframe=True, line_width=1.0, translate=(0,0,0), rotate=(0,0,0), scale=(1,1,1)):
        direction = np.array(end) - np.array(start)
        length = np.linalg.norm(direction)
        shaft_length = length - head_length
        objects = []
        # Create shaft (cylinder)
        objects += self.add_cylinder(start, direction, shaft_length, shaft_radius, segments, color, line_width, shader, buffer_type, show_body=True, show_wireframe=show_wireframe).transform(translate, rotate, scale)
        # Create arrowhead (cone)
        head_start = start + direction * (shaft_length / length)
        objects += self.add_cone(head_start, direction, head_length, head_radius, segments, color, line_width, shader, buffer_type, show_wireframe).transform(translate, rotate, scale)
        return objects

    def add_axis(self, translate=(0,0,0), rotate=(0,0,0), scale=(1,1,1), line_width=1.0, shader=None, buffer_type=BufferType.Static):
        x_axis = self.add_line((0,0,0), (1,0,0), Color.RED, line_width, shader, buffer_type).transform(translate, rotate, scale)
        y_axis = self.add_line((0,0,0), (0,1,0), Color.GREEN, line_width, shader, buffer_type).transform(translate, rotate, scale)
        z_axis = self.add_line((0,0,0), (0,0,1), Color.BLUE, line_width, shader, buffer_type).transform(translate, rotate, scale)
        return [x_axis, y_axis, z_axis]

    def add_grid(self, size, increment, color, line_width=1.0, shader=None, buffer_type=BufferType.Static, translate=(0,0,0), rotate=(0,0,0), scale=(1,1,1)):
        geometry = Geometry.create_grid(position, size, increment, color).transform(translate, rotate, scale)
        return self.add_object(geometry, buffer_type, shader, GL_LINES, line_width=line_width)

    def add_object(self, geometry_data, buffer_type, shader=None, draw_type=GL_TRIANGLES, line_width=1.0, point_size=1.0):
        """
        Add a new object to the scene.

        This method creates a new renderable object from the provided GeometryData and adds it to the scene.

        Parameters:
        -----------
        geometry_data : GeometryData
            An instance of GeometryData containing vertices and indices for the object.
        buffer_type : int
            The OpenGL buffer type (e.g., GL_STATIC_DRAW, GL_DYNAMIC_DRAW).
        shader : Shader, optional
            The shader program to use for this object. If None, the default shader will be used.
        draw_type : int, optional
            The OpenGL draw type (e.g., GL_TRIANGLES, GL_LINES). Defaults to GL_TRIANGLES.
        line_width : float, optional
            The width of lines when drawing line-based objects. Defaults to 1.0.
        point_size : float, optional
            The size of points when drawing point-based objects. Defaults to 1.0.

        Returns:
        --------
        List of RenderObject
            A list containing the created render object, which has been added to the scene.
        """
        
        shader = shader or self.default_shader
        vb = VertexBuffer(geometry_data.vertices, buffer_type)
        ib = IndexBuffer(geometry_data.indices, buffer_type)
        va = VertexArray()
        
        layout = [
            {'index': 0, 'size': 3, 'type': GL_FLOAT, 'normalized': GL_FALSE, 'stride': 36, 'offset': 0},
            {'index': 1, 'size': 3, 'type': GL_FLOAT, 'normalized': GL_FALSE, 'stride': 36, 'offset': 12},
            {'index': 2, 'size': 3, 'type': GL_FLOAT, 'normalized': GL_FALSE, 'stride': 36, 'offset': 24}
        ]
        
        va.add_buffer(vb, layout)
        obj = RenderObject(vb, ib, va, draw_type, shader, line_width, point_size)
        self.objects.append(obj)
        return [obj]

