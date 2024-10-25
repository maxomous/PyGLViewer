from OpenGL.GL import *
import ctypes
import numpy as np

class BufferType:
    """Enumeration of OpenGL buffer types."""
    Static = GL_STATIC_DRAW
    Dynamic = GL_DYNAMIC_DRAW
    Stream = GL_STREAM_DRAW

class Buffer:
    """Base class for OpenGL buffer objects."""
    def __init__(self, data, buffer_type, target):
        self.id = glGenBuffers(1)
        self.target = target
        self.buffer_type = buffer_type
        self.size = data.nbytes
        self.bind()
        glBufferData(self.target, self.size, data, buffer_type)

    def bind(self):
        """Bind this buffer to its target."""
        glBindBuffer(self.target, self.id)

    def unbind(self):
        """Unbind this buffer from its target."""
        glBindBuffer(self.target, 0)

    def update_data(self, data, offset=0):
        """Update the buffer's data."""
        self.bind()
        glBufferSubData(self.target, offset, data.nbytes, data)

class VertexBuffer(Buffer):
    """Vertex buffer object for storing vertex data."""
    def __init__(self, data, buffer_type):
        super().__init__(data, buffer_type, GL_ARRAY_BUFFER)

class IndexBuffer(Buffer):
    """Index buffer object for storing index data."""
    def __init__(self, data, buffer_type):
        super().__init__(data, buffer_type, GL_ELEMENT_ARRAY_BUFFER)
        self.count = len(data)

class VertexArray:
    """Vertex array object for managing vertex attribute configurations."""
    def __init__(self):
        self.vao = glGenVertexArrays(1)

    def bind(self):
        """Bind this vertex array object."""
        glBindVertexArray(self.vao)

    def unbind(self):
        """Unbind this vertex array object."""
        glBindVertexArray(0)

    def add_buffer(self, vb, layout):
        """Add a vertex buffer with specified attribute layout to this VAO."""
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
    """Represents a renderable object with vertex, index buffers, and shader."""
    def __init__(self, vb, ib, va, draw_type, shader, line_width=1.0, point_size=1.0):
        self.vb = vb
        self.ib = ib
        self.va = va
        self.draw_type = draw_type
        self.shader = shader
        self.line_width = line_width
        self.point_size = point_size
        self.model_matrix = np.identity(4, dtype=np.float32)

    def update_vertex_data(self, data, offset=0):
        """Update the vertex data of this render object."""
        self.vb.update_data(data, offset)

    def update_index_data(self, data, offset=0):
        """Update the index data of this render object."""
        self.ib.update_data(data, offset)

    def set_model_matrix(self, model_matrix):
        self.model_matrix = model_matrix