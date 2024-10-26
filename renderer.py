from OpenGL.GL import *
import numpy as np
from geometry import Geometry, Vertex
from color import Color
from shaders import Shader, basic_vertex_shader, basic_fragment_shader
from gl_objects import BufferType, VertexBuffer, IndexBuffer, VertexArray, RenderObject
from geometry import GeometryData





class Renderer:
    def __init__(self):
        self.lights = []
        self.objects = []
        self.wireframe_color = Color.BLACK
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


    def add_point(self, position, color, point_size=1.0, shader=None, buffer_type=BufferType.Static):
        geometry = Geometry.create_point(position, color)
        point = self.add_object(geometry, buffer_type, shader, GL_POINTS, point_size=point_size)
        return [point]

    def add_line(self, p0, p1, color, line_width=1.0, shader=None, buffer_type=BufferType.Static, translate=(0,0,0), rotate=(0,0,0), scale=(1,1,1)):
        geometry = Geometry.create_line(p0, p1, color).transform(translate, rotate, scale)
        line = self.add_object(geometry, buffer_type, shader, GL_LINES, line_width=line_width)
        return [line]

    def add_triangle(self, p1, p2, p3, color, line_width=1.0, shader=None, buffer_type=BufferType.Static, show_body=True, show_wireframe=True, translate=(0,0,0), rotate=(0,0,0), scale=(1,1,1)):
        triangle_body = triangle_wireframe = None
        if show_body:
            geometry = Geometry.create_triangle(p1, p2, p3, color).transform(translate, rotate, scale)
            triangle_body = self.add_object(geometry, buffer_type, shader, GL_TRIANGLES)
        if show_wireframe:
            geometry = Geometry.create_triangle_wireframe(p1, p2, p3, self.wireframe_color).transform(translate, rotate, scale)
            triangle_wireframe = self.add_object(geometry, buffer_type, shader, GL_LINES, line_width=line_width)
        return [triangle_body, triangle_wireframe]

    def add_rectangle(self, position, width, height, color, line_width=1.0, shader=None, buffer_type=BufferType.Static, show_body=True, show_wireframe=True, translate=(0,0,0), rotate=(0,0,0), scale=(1,1,1)):
        rectangle_body = rectangle_wireframe = None
        if show_body:
            geometry = Geometry.create_rectangle(position[0], position[1], width, height, color).transform(translate, rotate, scale)
            rectangle_body = self.add_object(geometry, buffer_type, shader, GL_TRIANGLES)
        if show_wireframe:
            geometry = Geometry.create_rectangle_wireframe(position[0], position[1], width * 1.01, height * 1.01, self.wireframe_color).transform(translate, rotate, scale)
            rectangle_wireframe = self.add_object(geometry, buffer_type, shader, GL_LINES, line_width=line_width)
        return [rectangle_body, rectangle_wireframe]
        

    def add_circle(self, position, radius, segments, color, line_width=1.0, shader=None, buffer_type=BufferType.Static, show_body=True, show_wireframe=True, translate=(0,0,0), rotate=(0,0,0), scale=(1,1,1)):
        circle_body = circle_wireframe = None
        if show_body:
            geometry = Geometry.create_circle(position, radius, segments, color).transform(translate, rotate, scale)
            circle_body = self.add_object(geometry, buffer_type, shader, GL_TRIANGLE_FAN)
        if show_wireframe:
            geometry = Geometry.create_circle_wireframe(position, radius * 1.01, segments, self.wireframe_color).transform(translate, rotate, scale)
            circle_wireframe = self.add_object(geometry, buffer_type, shader, GL_LINE_LOOP, line_width=line_width)
        return [circle_body, circle_wireframe]

    def add_cube(self, color, line_width=1.0, shader=None, buffer_type=BufferType.Static, show_body=True, show_wireframe=True, translate=(0,0,0), rotate=(0,0,0), scale=(1,1,1)):
        cube_body = cube_wireframe = None
        if show_body:
            geometry = Geometry.create_cube(size=1.0, color=color).transform(translate, rotate, scale)
            cube_body = self.add_object(geometry, buffer_type, shader, GL_TRIANGLES)
        if show_wireframe:
            geometry = Geometry.create_cube_wireframe(size=1.0, color=self.wireframe_color).transform(translate, rotate, scale)
            cube_wireframe = self.add_object(geometry, buffer_type, shader, GL_LINES, line_width=line_width)
        return [cube_body, cube_wireframe]

    def add_cylinder(self, color, segments, line_width=1.0, shader=None, buffer_type=BufferType.Static, show_body=True, show_wireframe=True, translate=(0,0,0), rotate=(0,0,0), scale=(1,1,1)):
        cylinder_body = cylinder_wireframe = None
        if show_body:
            geometry = Geometry.create_cylinder(segments, color).transform(translate, rotate, scale)
            cylinder_body = self.add_object(geometry, buffer_type, shader, GL_TRIANGLES)
        if show_wireframe:
            geometry = Geometry.create_cylinder_wireframe(segments, self.wireframe_color).transform(translate, rotate, scale)
            cylinder_wireframe = self.add_object(geometry, buffer_type, shader, GL_LINES, line_width=line_width)
        return [cylinder_body, cylinder_wireframe]




    def add_cone(self, color, segments, line_width=1.0, shader=None, buffer_type=BufferType.Static, show_body=True, show_wireframe=True, translate=(0,0,0), rotate=(0,0,0), scale=(1,1,1)):
        cone_body = cone_wireframe = None
        if show_body:
            geometry = Geometry.create_cone(segments, color).transform(translate, rotate, scale)
            cone_body = self.add_object(geometry, buffer_type, shader, GL_TRIANGLES)
        if show_wireframe:
            geometry = Geometry.create_cone_wireframe(segments, self.wireframe_color).transform(translate, rotate, scale)
            cone_wireframe = self.add_object(geometry, buffer_type, shader, GL_LINES, line_width=line_width)
        return [cone_body, cone_wireframe]

    def add_sphere(self, radius, subdivisions, color, shader=None, buffer_type=BufferType.Static, translate=(0,0,0), rotate=(0,0,0), scale=(1,1,1)):
        geometry = Geometry.create_sphere(radius, subdivisions, color).transform(translate, rotate, scale)
        sphere_body = self.add_object(geometry, buffer_type, shader, GL_TRIANGLES)
        return [sphere_body]

    def add_arrow(self, p0, p1, shaft_radius=0.1, head_radius=0.2, head_length=0.4, color=Color.WHITE, segments=16, shader=None, buffer_type=BufferType.Static, show_body=True, show_wireframe=True, line_width=1.0):
        body, wireframe = Geometry.create_arrow(p0, p1, color, self.wireframe_color, shaft_radius, head_radius, head_length, segments)
        arrow_body = self.add_object(body, buffer_type, shader, GL_TRIANGLES) if show_body else None
        arrow_wireframe = self.add_object(wireframe, buffer_type, shader, GL_LINES, line_width=line_width) if show_wireframe else None
        return [arrow_body, arrow_wireframe]
    
    def add_axis(self, size=1.0, shaft_radius=0.1, head_radius=0.2, head_length=0.4, segments=16, shader=None, buffer_type=BufferType.Static, show_body=True, show_wireframe=True, line_width=1.0, translate=(0,0,0), rotate=(0,0,0), scale=(1,1,1)):      
        # Create geometry
        x_geometry, x_wireframe = Geometry.create_arrow((0,0,0), (size,0,0), (1,0,0), self.wireframe_color, shaft_radius, head_radius, head_length, segments)
        y_geometry, y_wireframe = Geometry.create_arrow((0,0,0), (0,size,0), (0,1,0), self.wireframe_color, shaft_radius, head_radius, head_length, segments)
        z_geometry, z_wireframe = Geometry.create_arrow((0,0,0), (0,0,size), (0,0,1), self.wireframe_color, shaft_radius, head_radius, head_length, segments)
        radius, subdivisions, color = 0.12, 4, Color.BLACK
        sphere_geometry = Geometry.create_sphere(radius, subdivisions, color)
        # Transform geometry
        geometry = (x_geometry + y_geometry + z_geometry + sphere_geometry).transform(translate, rotate, scale)
        wireframe = (x_wireframe + y_wireframe + z_wireframe).transform(translate, rotate, scale)
        # Add objects
        axis_body = self.add_object(geometry, buffer_type, shader, GL_TRIANGLES) if show_body else None
        axis_wireframe = self.add_object(wireframe, buffer_type, shader, GL_LINES, line_width=line_width) if show_wireframe else None
        # Return objects
        return [axis_body, axis_wireframe]


    def add_grid(self, size, increment, color, line_width=1.0, shader=None, buffer_type=BufferType.Static, translate=(0,0,0), rotate=(0,0,0), scale=(1,1,1)):
        geometry = Geometry.create_grid(size, increment, color).transform(translate, rotate, scale)
        grid = self.add_object(geometry, buffer_type, shader, GL_LINES, line_width=line_width)
        return [grid]

    def add_object(self, geometry_data, buffer_type, shader=None, draw_type=GL_TRIANGLES, line_width=1.0, point_size=1.0):
        shader = shader or self.default_shader

        # Interleave position, color, and normal data
        interleaved_data = np.array([vertex.to_array() for vertex in geometry_data.vertices], dtype=np.float32).flatten()
        
        vb = VertexBuffer(interleaved_data, buffer_type)
        ib = IndexBuffer(geometry_data.indices, buffer_type)
        va = VertexArray()
        
        va.add_buffer(vb, Vertex.LAYOUT)
        obj = RenderObject(vb, ib, va, draw_type, shader, line_width, point_size)
        self.objects.append(obj)
        return obj









