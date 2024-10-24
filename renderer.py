from OpenGL.GL import *
import numpy as np
import ctypes
from geometry import Geometry
from color import Color
from shaders import Shader, basic_vertex_shader, basic_fragment_shader


class BufferType:
    Static = GL_STATIC_DRAW
    Dynamic = GL_DYNAMIC_DRAW
    Stream = GL_STREAM_DRAW

class Buffer:
    def __init__(self, data, buffer_type, target):
        self.id = glGenBuffers(1)
        self.target = target
        self.buffer_type = buffer_type
        self.size = data.nbytes
        self.bind()
        glBufferData(self.target, self.size, data, buffer_type)

    def bind(self):
        glBindBuffer(self.target, self.id)

    def unbind(self):
        glBindBuffer(self.target, 0)

    def update_data(self, data, offset=0):
        self.bind()
        glBufferSubData(self.target, offset, data.nbytes, data)

class VertexBuffer(Buffer):
    def __init__(self, data, buffer_type):
        super().__init__(data, buffer_type, GL_ARRAY_BUFFER)

class IndexBuffer(Buffer):
    def __init__(self, data, buffer_type):
        super().__init__(data, buffer_type, GL_ELEMENT_ARRAY_BUFFER)
        self.count = len(data)

class VertexArray:
    def __init__(self):
        self.vao = glGenVertexArrays(1)

    def bind(self):
        glBindVertexArray(self.vao)

    def unbind(self):
        glBindVertexArray(0)

    def add_buffer(self, vb, layout):
        self.bind()
        vb.bind()
        for attribute in layout:
            glEnableVertexAttribArray(attribute['index'])
            glVertexAttribPointer(
                attribute['index'], 
                attribute['size'], 
                attribute['type'], 
                attribute['normalized'], 
                attribute['stride'], 
                ctypes.c_void_p(attribute['offset'])
            )

class RenderObject:
    def __init__(self, vb, ib, va, draw_type, shader, line_width=1.0, point_size=1.0):
        self.vb = vb
        self.ib = ib
        self.va = va
        self.draw_type = draw_type
        self.shader = shader
        self.line_width = line_width
        self.point_size = point_size

    def update_vertex_data(self, data, offset=0):
        self.vb.update_data(data, offset)

    def update_index_data(self, data, offset=0):
        self.ib.update_data(data, offset)

    
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
    
    def draw(self):
        for obj in self.objects:
            obj.shader.use()
            obj.va.bind()
            obj.ib.bind()
            
            # Set point size / line width
            if obj.draw_type == GL_POINTS:
                glPointSize(obj.point_size)
            elif (obj.draw_type == GL_LINES) or (obj.draw_type == GL_LINE_LOOP) or (obj.draw_type == GL_LINE_STRIP):
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


    def add_light(self, light):
        self.lights.append(light)

    def add_object(self, geometry_data, buffer_type, shader=None, draw_type=GL_TRIANGLES, line_width=1.0, point_size=1.0):
        """
        Add a new object to the scene.

        This method creates a new renderable object from the provided geometry data and adds it to the scene.

        Parameters:
        -----------
        geometry_data : dict
            A dictionary containing 'vertices' and 'indices' for the object.
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
        RenderObject
            The created render object, which has been added to the scene.
        """
        shader = shader or self.default_shader
        vb = VertexBuffer(geometry_data['vertices'], buffer_type)
        ib = IndexBuffer(geometry_data['indices'], buffer_type)
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

    def add_point(self, position, color, point_size=1.0, shader=None, buffer_type=BufferType.Static):
        return self.add_object(Geometry.create_point(position, color), buffer_type, shader, GL_POINTS, point_size=point_size)

    def add_line(self, start, end, color, line_width=1.0, shader=None, buffer_type=BufferType.Static):
        return self.add_object(Geometry.create_line(start, end, color), buffer_type, shader, GL_LINES, line_width=line_width)

    def add_triangle(self, p1, p2, p3, color, line_width=1.0, shader=None, buffer_type=BufferType.Static, show_body=True, show_wireframe=False):
        objects = []
        if show_body:
            objects.append(self.add_object(Geometry.create_triangle(p1, p2, p3, color), buffer_type, shader, GL_TRIANGLES))
        if show_wireframe:
            objects.append(self.add_object(Geometry.create_triangle_wireframe(p1, p2, p3, self.wireframe_color), buffer_type, shader, GL_LINES, line_width=line_width))
        return objects

    def add_rectangle(self, position, width, height, color, line_width=1.0, shader=None, buffer_type=BufferType.Static, show_body=True, show_wireframe=False):
        objects = []
        if show_body:
            objects.append(self.add_object(Geometry.create_rectangle(position[0], position[1], width, height, color), buffer_type, shader, GL_TRIANGLES))
        if show_wireframe:
            objects.append(self.add_object(Geometry.create_rectangle_wireframe(position[0], position[1], width * 1.01, height * 1.01, self.wireframe_color), buffer_type, shader, GL_LINES, line_width=line_width))
        return objects
        

    def add_circle(self, centre, radius, segments, color, line_width=1.0, shader=None, buffer_type=BufferType.Static, show_body=True, show_wireframe=False):
        objects = []
        if show_body:
            objects.append(self.add_object(Geometry.create_circle(centre, radius, segments, color), buffer_type, shader, GL_TRIANGLE_FAN))
        if show_wireframe:
            objects.append(self.add_object(Geometry.create_circle_wireframe(centre, radius * 1.01, segments, self.wireframe_color), buffer_type, shader, GL_LINE_LOOP, line_width=line_width))
        return objects

    def add_cube(self, position, size, color, line_width=1.0, shader=None, buffer_type=BufferType.Static, show_body=True, show_wireframe=False):
        objects = []
        if show_body:
            objects.append(self.add_object(Geometry.create_cube(position, size, color), buffer_type, shader, GL_TRIANGLES))
        if show_wireframe:
            objects.append(self.add_object(Geometry.create_cube_wireframe(position, size * 1.01, self.wireframe_color), buffer_type, shader, GL_LINES, line_width=line_width))
        return objects

    def add_cylinder(self, start, direction, length, radius, segments, color, line_width=1.0, shader=None, buffer_type=BufferType.Static, show_body=True, show_wireframe=False):
        objects = []
        if show_body:
            objects.append(self.add_object(Geometry.create_cylinder(start, direction, length, radius, segments, color), buffer_type, shader, GL_TRIANGLES))
        if show_wireframe:
            objects.append(self.add_object(Geometry.create_cylinder_wireframe(start, direction, length, radius * 1.01, segments, self.wireframe_color), buffer_type, shader, GL_LINES, line_width=line_width))
        return objects

    def add_cone(self, start, direction, length, radius, segments, color, line_width=1.0, shader=None, buffer_type=BufferType.Static, show_body=True, show_wireframe=False):
        objects = []
        if show_body:
            objects.append(self.add_object(Geometry.create_cone(start, direction, length, radius, segments, color), buffer_type, shader, GL_TRIANGLES))
        if show_wireframe:
            objects.append(self.add_object(Geometry.create_cone_wireframe(start, direction, length, radius * 1.01, segments, self.wireframe_color), buffer_type, shader, GL_LINES, line_width=line_width))
        return objects

    def add_arrow(self, start, end, shaft_radius=0.05, head_radius=0.1, head_length=0.3, color=Color.WHITE, wireframe_color=Color.BLACK, segments=16, shader=None, buffer_type=BufferType.Static, show_wireframe=True, line_width=1.0):
        direction = np.array(end) - np.array(start)
        length = np.linalg.norm(direction)
        shaft_length = length - head_length
        objects = []
        # Create shaft (cylinder)
        objects += self.add_cylinder(start, direction, shaft_length, shaft_radius, segments, color, line_width, shader, buffer_type, show_body=True, show_wireframe=show_wireframe)
        # Create arrowhead (cone)
        head_start = start + direction * (shaft_length / length)
        objects += self.add_cone(head_start, direction, head_length, head_radius, segments, color, line_width, shader, buffer_type, show_wireframe)
        return objects

    def add_axis(self, length, position=(0, 0, 0), line_width=1.0, shader=None, buffer_type=BufferType.Static):
        p0 = np.array(position)
        x_axis = self.add_line(p0, p0 + np.array([length, 0, 0]), Color.RED, line_width, shader, buffer_type)
        y_axis = self.add_line(p0, p0 + np.array([0, length, 0]), Color.GREEN, line_width, shader, buffer_type)
        z_axis = self.add_line(p0, p0 + np.array([0, 0, length]), Color.BLUE, line_width, shader, buffer_type)
        return [x_axis, y_axis, z_axis]

    def add_grid(self, position, size, increment, color, line_width=1.0, shader=None, buffer_type=BufferType.Static):
        return self.add_object(Geometry.create_grid(position, size, increment, color), buffer_type, shader, GL_LINES, line_width=line_width)
