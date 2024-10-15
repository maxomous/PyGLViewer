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
    def __init__(self, vb, ib, va, draw_type, shader):
        self.vb = vb
        self.ib = ib
        self.va = va
        self.draw_type = draw_type
        self.shader = shader

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
        
    def add_object(self, vertices, indices, buffer_type, shader=None, draw_type=GL_TRIANGLES):
        shader = shader or self.default_shader
        vb = VertexBuffer(vertices, buffer_type)
        ib = IndexBuffer(indices, buffer_type)
        va = VertexArray()
        
        layout = [
            {'index': 0, 'size': 3, 'type': GL_FLOAT, 'normalized': GL_FALSE, 'stride': 36, 'offset': 0},
            {'index': 1, 'size': 3, 'type': GL_FLOAT, 'normalized': GL_FALSE, 'stride': 36, 'offset': 12},
            {'index': 2, 'size': 3, 'type': GL_FLOAT, 'normalized': GL_FALSE, 'stride': 36, 'offset': 24}
        ]
        
        va.add_buffer(vb, layout)
        obj = RenderObject(vb, ib, va, draw_type, shader)
        self.objects.append(obj)
        return obj

    def add_point(self, x, y, z, color, shader=None, buffer_type=BufferType.Static):
        vertices, indices = Geometry.create_point(x, y, z, color)
        return self.add_object(vertices, indices, buffer_type, shader, GL_POINTS)

    def add_line(self, start, end, color, shader=None, buffer_type=BufferType.Static):
        vertices, indices = Geometry.create_line(start, end, color)
        return self.add_object(vertices, indices, buffer_type, shader, GL_LINES)

    def add_triangle(self, p1, p2, p3, color, shader=None, buffer_type=BufferType.Static, show_wireframe=False):
        vertices, indices = Geometry.create_triangle(p1, p2, p3, color)
        solid_obj = self.add_object(vertices, indices, buffer_type, shader, GL_TRIANGLES)
        
        if show_wireframe:
            wireframe_vertices, wireframe_indices = Geometry.create_triangle_wireframe(p1, p2, p3, self.wireframe_color)
            wireframe_obj = self.add_object(wireframe_vertices, wireframe_indices, buffer_type, shader, GL_LINES)
            return [solid_obj, wireframe_obj]
        
        return solid_obj

    def add_rectangle(self, x, y, width, height, color, shader=None, buffer_type=BufferType.Static, show_wireframe=False):
        vertices, indices = Geometry.create_rectangle(x, y, width, height, color)
        solid_obj = self.add_object(vertices, indices, buffer_type, shader, GL_TRIANGLES)
        
        if show_wireframe:
            wireframe_vertices, wireframe_indices = Geometry.create_rectangle_wireframe(x, y, width * 1.01, height * 1.01, self.wireframe_color)
            wireframe_obj = self.add_object(wireframe_vertices, wireframe_indices, buffer_type, shader, GL_LINES)
            return [solid_obj, wireframe_obj]
        
        return solid_obj

    def add_circle(self, x, y, radius, segments, color, shader=None, buffer_type=BufferType.Static, show_wireframe=False):
        vertices, indices = Geometry.create_circle(x, y, radius, segments, color)
        solid_obj = self.add_object(vertices, indices, buffer_type, shader, GL_TRIANGLE_FAN)
        
        if show_wireframe:
            wireframe_vertices, wireframe_indices = Geometry.create_circle_wireframe(x, y, radius * 1.01, segments, self.wireframe_color)
            wireframe_obj = self.add_object(wireframe_vertices, wireframe_indices, buffer_type, shader, GL_LINE_LOOP)
            return [solid_obj, wireframe_obj]
        
        return solid_obj

    def add_cube(self, position, size, color, shader=None, buffer_type=BufferType.Static, show_wireframe=False):
        vertices, indices = Geometry.create_cube_solid(position, size, color)
        solid_obj = self.add_object(vertices, indices, buffer_type, shader, GL_TRIANGLES)
        
        if show_wireframe:
            wireframe_vertices, wireframe_indices = Geometry.create_cube_wireframe(position, size * 1.01, self.wireframe_color)
            wireframe_obj = self.add_object(wireframe_vertices, wireframe_indices, buffer_type, shader, GL_LINES)
            return [solid_obj, wireframe_obj]
        
        return solid_obj

    def add_axis(self, length, shader=None, buffer_type=BufferType.Static):
        # X-axis (red)
        self.add_line((0, 0, 0), (length, 0, 0), Color.RED, shader, buffer_type)
        # Y-axis (green)
        self.add_line((0, 0, 0), (0, length, 0), Color.GREEN, shader, buffer_type)
        # Z-axis (blue)
        self.add_line((0, 0, 0), (0, 0, length), Color.BLUE, shader, buffer_type)

    def add_grid(self, position, size, increment, color, shader=None, buffer_type=BufferType.Static):
        vertices, indices = Geometry.create_grid(position, size, increment, color)
        return self.add_object(vertices, indices, buffer_type, shader, GL_LINES)

    def add_light(self, light):
        self.lights.append(light)

    def draw(self):
        for obj in self.objects:
            obj.shader.use()
            obj.va.bind()
            obj.ib.bind()
            
            if (obj.draw_type == GL_LINES) or (obj.draw_type == GL_LINE_LOOP) or (obj.draw_type == GL_LINE_STRIP):
                glDisable(GL_DEPTH_TEST)
                glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
            else:
                glEnable(GL_DEPTH_TEST)
                glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
            
            glDrawElements(obj.draw_type, obj.ib.count, GL_UNSIGNED_INT, None)
            
            obj.va.unbind()
            obj.ib.unbind()
        
        # Reset to default state
        glEnable(GL_DEPTH_TEST)
        glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
            
    def clear(self):
        glClearColor(0.2, 0.3, 0.3, 1.0)  # Set a dark teal background color
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

class LightType:
    DIRECTIONAL = 0
    POINT = 1
    SPOT = 2

class Light:
    def __init__(self, light_type, position=None, direction=None, color=(1, 1, 1), intensity=1.0, 
                 attenuation=(1.0, 0.0, 0.0), cutoff=None):
        self.light_type = light_type
        self.position = np.array(position) if position else None
        self.direction = np.array(direction) if direction else None
        self.color = np.array(color)
        self.intensity = intensity
        self.attenuation = np.array(attenuation)  # (constant, linear, quadratic)
        self.cutoff = cutoff  # for spot light



