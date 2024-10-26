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

    def add_triangle(self, p1, p2, p3, color, line_width=1.0, shader=None, buffer_type=BufferType.Static, show_body=True, show_wireframe=False, translate=(0,0,0), rotate=(0,0,0), scale=(1,1,1)):
        triangle_body = triangle_wireframe = None
        if show_body:
            geometry = Geometry.create_triangle(p1, p2, p3, color).transform(translate, rotate, scale)
            triangle_body = self.add_object(geometry, buffer_type, shader, GL_TRIANGLES)
        if show_wireframe:
            geometry = Geometry.create_triangle(p1, p2, p3, self.wireframe_color).transform(translate, rotate, scale)
            triangle_wireframe = self.add_object(geometry, buffer_type, shader, GL_LINES, line_width=line_width)
        return [triangle_body, triangle_wireframe]

    def add_rectangle(self, position, width, height, color, line_width=1.0, shader=None, buffer_type=BufferType.Static, show_body=True, show_wireframe=False, translate=(0,0,0), rotate=(0,0,0), scale=(1,1,1)):
        rectangle_body = rectangle_wireframe = None
        if show_body:
            geometry = Geometry.create_rectangle(position[0], position[1], width, height, color).transform(translate, rotate, scale)
            rectangle_body = self.add_object(geometry, buffer_type, shader, GL_TRIANGLES)
        if show_wireframe:
            geometry = Geometry.create_rectangle_wireframe(position[0], position[1], width * 1.01, height * 1.01, self.wireframe_color).transform(translate, rotate, scale)
            rectangle_wireframe = self.add_object(geometry, buffer_type, shader, GL_LINES, line_width=line_width)
        return [rectangle_body, rectangle_wireframe]
        

    def add_circle(self, position, radius, segments, color, line_width=1.0, shader=None, buffer_type=BufferType.Static, show_body=True, show_wireframe=False, translate=(0,0,0), rotate=(0,0,0), scale=(1,1,1)):
        circle_body = circle_wireframe = None
        if show_body:
            geometry = Geometry.create_circle(position, radius, segments, color).transform(translate, rotate, scale)
            circle_body = self.add_object(geometry, buffer_type, shader, GL_TRIANGLE_FAN)
        if show_wireframe:
            geometry = Geometry.create_circle_wireframe(position, radius * 1.01, segments, self.wireframe_color).transform(translate, rotate, scale)
            circle_wireframe = self.add_object(geometry, buffer_type, shader, GL_LINE_LOOP, line_width=line_width)
        return [circle_body, circle_wireframe]

    def add_cube(self, color, line_width=1.0, shader=None, buffer_type=BufferType.Static, show_body=True, show_wireframe=False, translate=(0,0,0), rotate=(0,0,0), scale=(1,1,1)):
        cube_body = cube_wireframe = None
        if show_body:
            geometry = Geometry.create_cube(size=1.0, color=color).transform(translate, rotate, scale)
            cube_body = self.add_object(geometry, buffer_type, shader, GL_TRIANGLES)
        if show_wireframe:
            geometry = Geometry.create_cube_wireframe(size=1.0, color=self.wireframe_color).transform(translate, rotate, scale)
            cube_wireframe = self.add_object(geometry, buffer_type, shader, GL_LINES, line_width=line_width)
        return [cube_body, cube_wireframe]

    def add_cylinder(self, color, segments, line_width=1.0, shader=None, buffer_type=BufferType.Static, show_body=True, show_wireframe=False, translate=(0,0,0), rotate=(0,0,0), scale=(1,1,1)):
        cylinder_body = cylinder_wireframe = None
        if show_body:
            geometry = Geometry.create_cylinder(segments, color).transform(translate, rotate, scale)
            cylinder_body = self.add_object(geometry, buffer_type, shader, GL_TRIANGLES)
        if show_wireframe:
            geometry = Geometry.create_cylinder_wireframe(segments, self.wireframe_color).transform(translate, rotate, scale)
            cylinder_wireframe = self.add_object(geometry, buffer_type, shader, GL_LINES, line_width=line_width)
        return [cylinder_body, cylinder_wireframe]

    def add_cone(self, color, segments, line_width=1.0, shader=None, buffer_type=BufferType.Static, show_body=True, show_wireframe=False, translate=(0,0,0), rotate=(0,0,0), scale=(1,1,1)):
        cone_body = cone_wireframe = None
        if show_body:
            geometry = Geometry.create_cone(segments, color).transform(translate, rotate, scale)
            cone_body = self.add_object(geometry, buffer_type, shader, GL_TRIANGLES)
        if show_wireframe:
            geometry = Geometry.create_cone_wireframe(segments, self.wireframe_color).transform(translate, rotate, scale)
            cone_wireframe = self.add_object(geometry, buffer_type, shader, GL_LINES, line_width=line_width)
        return [cone_body, cone_wireframe]

    def add_sphere(self, radius, stacks, sectors, color, shader=None, buffer_type=BufferType.Static, translate=(0,0,0), rotate=(0,0,0), scale=(1,1,1)):
        geometry = Geometry.create_sphere(radius, stacks, sectors, color).transform(translate, rotate, scale)
        sphere_body = self.add_object(geometry, buffer_type, shader, GL_TRIANGLES)
        return [sphere_body]


    def add_arrow(self, color=Color.WHITE, wireframe_color=Color.BLACK, segments=16, shader=None, buffer_type=BufferType.Static, show_wireframe=True, line_width=1.0, translate=(0,0,0), rotate=(0,0,0), scale=(1,1,1)):
        arrow_shaft = self.add_cylinder(color, segments, line_width, shader, buffer_type, show_body=True, show_wireframe=show_wireframe, translate=translate, rotate=rotate, scale=scale)
        
        # Adjust scale for the cone (arrowhead)
        cone_scale = list(scale)
        cone_scale[2] *= 0.2  # Adjust the length of the cone
        cone_translate = list(translate)
        cone_translate[2] += scale[2] * 0.9  # Move the cone to the end of the cylinder
        
        arrow_head = self.add_cone(color, segments, line_width, shader, buffer_type, show_body=True, show_wireframe=show_wireframe, translate=tuple(cone_translate), rotate=rotate, scale=tuple(cone_scale))
        
        return [arrow_shaft, arrow_head]

    def add_axis(self, translate=(0,0,0), rotate=(0,0,0), scale=(1,1,1), line_width=1.0, shader=None, buffer_type=BufferType.Static):
        geometry = Geometry.create_line((0,0,0), (1,0,0), Color.RED).transform(translate, rotate, scale)
        geometry += Geometry.create_line((0,0,0), (0,1,0), Color.GREEN).transform(translate, rotate, scale)
        geometry += Geometry.create_line((0,0,0), (0,0,1), Color.BLUE).transform(translate, rotate, scale)
        axes = self.add_object(geometry, buffer_type, shader, GL_LINES, line_width=line_width)
        return [axes]

    def add_grid(self, size, increment, color, line_width=1.0, shader=None, buffer_type=BufferType.Static, translate=(0,0,0), rotate=(0,0,0), scale=(1,1,1)):
        geometry = Geometry.create_grid(size, increment, color).transform(translate, rotate, scale)
        grid = self.add_object(geometry, buffer_type, shader, GL_LINES, line_width=line_width)
        return [grid]

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
        return obj



