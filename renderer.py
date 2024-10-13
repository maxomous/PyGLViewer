from OpenGL.GL import *
from OpenGL.GL import shaders
import numpy as np
import ctypes
from geometry import Geometry
from color import Color

basic_vertex_shader = """
#version 330 core
layout (location = 0) in vec3 aPos;
layout (location = 1) in vec3 aColor;
out vec3 ourColor;
uniform mat4 view;
uniform mat4 projection;
void main() {
    gl_Position = projection * view * vec4(aPos, 1.0);
    ourColor = aColor;
}
"""
basic_fragment_shader = """
#version 330 core
in vec3 ourColor;
out vec4 FragColor;
void main() {
    FragColor = vec4(ourColor, 1.0);
}
"""
class Shader:
        

    def __init__(self, vertex_source, fragment_source):
        self.program = self.create_shader_program(vertex_source, fragment_source)

    def create_shader_program(self, vertex_source, fragment_source):
        vertex_shader = shaders.compileShader(vertex_source, GL_VERTEX_SHADER)
        fragment_shader = shaders.compileShader(fragment_source, GL_FRAGMENT_SHADER)
        program = shaders.compileProgram(vertex_shader, fragment_shader)
        return program

    def use(self):
        glUseProgram(self.program)

    def set_uniform(self, name, value):
        location = glGetUniformLocation(self.program, name)
        if location == -1:
            print(f"Warning: Uniform '{name}' not found in shader program.")
            return

        if isinstance(value, int):
            glUniform1i(location, value)
        elif isinstance(value, float):
            glUniform1f(location, value)
        elif isinstance(value, (list, tuple, np.ndarray)):
            if isinstance(value, np.ndarray):
                value = value.flatten()  # Flatten the array
            if len(value) == 2:
                glUniform2f(location, *value)
            elif len(value) == 3:
                glUniform3f(location, *value)
            elif len(value) == 4:
                glUniform4f(location, *value)
            elif len(value) == 9:  # 3x3 matrix
                glUniformMatrix3fv(location, 1, GL_FALSE, (GLfloat * 9)(*value))
            elif len(value) == 16:  # 4x4 matrix
                glUniformMatrix4fv(location, 1, GL_FALSE, (GLfloat * 16)(*value))
            else:
                raise ValueError(f"Unsupported uniform vector size: {len(value)}")
        else:
            raise ValueError(f"Unsupported uniform type: {type(value)}")

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
        offset = 0
        stride = sum(attr['size'] * 4 for attr in layout)  # Assuming float (4 bytes) for all attributes
        for attribute in layout:
            glEnableVertexAttribArray(attribute['index'])
            glVertexAttribPointer(attribute['index'], attribute['size'], 
                                  GL_FLOAT, GL_FALSE, 
                                  stride, ctypes.c_void_p(offset))
            offset += attribute['size'] * 4

class RenderObject:
    def __init__(self, vb, ib, va, draw_type, shader, wireframe):
        self.vb = vb
        self.ib = ib
        self.va = va
        self.draw_type = draw_type
        self.shader = shader
        self.wireframe = wireframe

    def update_vertex_data(self, data, offset=0):
        self.vb.update_data(data, offset)

    def update_index_data(self, data, offset=0):
        self.ib.update_data(data, offset)
        
class Renderer:
    def __init__(self):
        self.objects = []
        self.wireframe_color = Color.WHITE

    def add_object(self, vertex_data, index_data, buffer_type, layout, draw_type, shader, wireframe=False):
        vb = VertexBuffer(vertex_data, buffer_type)
        ib = IndexBuffer(index_data, buffer_type)
        va = VertexArray()
        va.add_buffer(vb, layout)
        obj = RenderObject(vb, ib, va, draw_type, shader, wireframe)
        self.objects.append(obj)
        return obj

    def add_point(self, x, y, z, color, shader, buffer_type=BufferType.Static):
        vertices, indices = Geometry.create_point(x, y, z, color)
        return self.add_object(vertices, indices, buffer_type, [{'index': 0, 'size': 3}, {'index': 1, 'size': 3}], GL_POINTS, shader)

    def add_line(self, start, end, color, shader, buffer_type=BufferType.Static):
        vertices, indices = Geometry.create_line(start, end, color)
        return self.add_object(vertices, indices, buffer_type, [{'index': 0, 'size': 3}, {'index': 1, 'size': 3}], GL_LINES, shader)

    def add_triangle(self, p1, p2, p3, color, shader, buffer_type=BufferType.Static, show_wireframe=False):
        vertices, indices = Geometry.create_triangle(p1, p2, p3, color)
        solid_obj = self.add_object(vertices, indices, buffer_type, [{'index': 0, 'size': 3}, {'index': 1, 'size': 3}], GL_TRIANGLES, shader)
        
        if show_wireframe:
            vertices, indices = Geometry.create_triangle(p1, p2, p3, self.wireframe_color)
            wireframe_obj = self.add_object(vertices, indices, buffer_type, [{'index': 0, 'size': 3}, {'index': 1, 'size': 3}], GL_LINE_LOOP, shader, True)
            return [solid_obj, wireframe_obj]
        
        return solid_obj

    def add_rectangle(self, x, y, width, height, color, shader, buffer_type=BufferType.Static, show_wireframe=False):
        vertices, indices = Geometry.create_rectangle(x, y, width, height, color)
        solid_obj = self.add_object(vertices, indices, buffer_type, [{'index': 0, 'size': 3}, {'index': 1, 'size': 3}], GL_TRIANGLES, shader)
        
        if show_wireframe:
            wireframe_vertices, wireframe_indices = Geometry.create_rectangle(x, y, width * 1.01, height * 1.01, self.wireframe_color)
            wireframe_obj = self.add_object(wireframe_vertices, wireframe_indices, buffer_type, [{'index': 0, 'size': 3}, {'index': 1, 'size': 3}], GL_LINE_LOOP, shader, True)
            return [solid_obj, wireframe_obj]
        
        return solid_obj

    def add_circle(self, x, y, radius, segments, color, shader, buffer_type=BufferType.Static, show_wireframe=False):
        vertices, indices = Geometry.create_circle(x, y, radius, segments, color)
        solid_obj = self.add_object(vertices, indices, buffer_type, [{'index': 0, 'size': 3}, {'index': 1, 'size': 3}], GL_TRIANGLES, shader)
        
        if show_wireframe:
            wireframe_vertices, wireframe_indices = Geometry.create_circle(x, y, radius * 1.01, segments, self.wireframe_color)
            wireframe_obj = self.add_object(wireframe_vertices, wireframe_indices, buffer_type, [{'index': 0, 'size': 3}, {'index': 1, 'size': 3}], GL_LINE_LOOP, shader, True)
            return [solid_obj, wireframe_obj]
        
        return solid_obj

    def add_cube(self, position, size, color, shader, buffer_type=BufferType.Static, show_wireframe=False):
        vertices, indices = Geometry.create_cube(position, size, color)
        solid_obj = self.add_object(vertices, indices, buffer_type, [{'index': 0, 'size': 3}, {'index': 1, 'size': 3}], GL_TRIANGLES, shader)
        
        if show_wireframe:
            wireframe_vertices, wireframe_indices = Geometry.create_cube(position, size * 1.01, self.wireframe_color, wireframe=True)
            wireframe_obj = self.add_object(wireframe_vertices, wireframe_indices, buffer_type, [{'index': 0, 'size': 3}, {'index': 1, 'size': 3}], GL_LINES, shader, True)
            return [solid_obj, wireframe_obj]
        
        return solid_obj

    def add_axis(self, length, shader, buffer_type=BufferType.Static):
        # X-axis (red)
        self.add_line((0, 0, 0), (length, 0, 0), Color.RED, shader, buffer_type)
        # Y-axis (green)
        self.add_line((0, 0, 0), (0, length, 0), Color.GREEN, shader, buffer_type)
        # Z-axis (blue)
        self.add_line((0, 0, 0), (0, 0, length), Color.BLUE, shader, buffer_type)

    def add_grid(self, position, size, increment, color, shader, buffer_type=BufferType.Static):
        vertices = []
        indices = []
        index = 0
        
        # Calculate the number of lines based on size and increment
        num_lines = int(size / increment) + 1
        
        # Create vertices and indices for the grid lines
        for i in range(num_lines):
            # X-axis lines
            x = i * increment - size/2 + position[0]
            vertices.extend([x, position[1] - size/2, position[2], *color])
            vertices.extend([x, position[1] + size/2, position[2], *color])
            
            # Y-axis lines
            y = i * increment - size/2 + position[1]
            vertices.extend([position[0] - size/2, y, position[2], *color])
            vertices.extend([position[0] + size/2, y, position[2], *color])
            
            # Indices for X-axis lines
            indices.extend([index, index + 1])
            # Indices for Y-axis lines
            indices.extend([index + 2, index + 3])
            index += 4

        vertices = np.array(vertices, dtype=np.float32)
        indices = np.array(indices, dtype=np.uint32)

        return self.add_object(vertices, indices, buffer_type, 
                               [{'index': 0, 'size': 3}, {'index': 1, 'size': 3}], 
                               GL_LINES, shader)

    def draw(self):
        for obj in self.objects:
            obj.shader.use()
            obj.va.bind()
            obj.ib.bind()
            
            # if obj.wireframe:
            #     glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
            #     glDisable(GL_DEPTH_TEST)  # Disable depth testing for wireframes
            # else:
            #     glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
            
            glDrawElements(obj.draw_type, obj.ib.count, GL_UNSIGNED_INT, None)
            
            # if obj.wireframe:
            #     glEnable(GL_DEPTH_TEST)  # Re-enable depth testing
            
            obj.va.unbind()
            obj.ib.unbind()

    def clear(self):
        glClearColor(0.2, 0.3, 0.3, 1.0)  # Set a dark teal background color
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
