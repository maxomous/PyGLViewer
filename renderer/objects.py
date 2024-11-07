from typing import Dict, Any, List
import ctypes
import numpy as np
from OpenGL.GL import *
from utils.transform import Transform



class BufferType:
    """Enumeration of OpenGL buffer types."""
    Static = GL_STATIC_DRAW
    Dynamic = GL_DYNAMIC_DRAW
    Stream = GL_STREAM_DRAW

class Buffer:
    """Base class for OpenGL buffer objects. Set size when using a dynamic / stream buffer."""
    def __init__(self, data, buffer_type, target, size):
        self.id = glGenBuffers(1)
        self.target = target
        self.buffer_type = buffer_type
        self.size = size
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
        if self.buffer_type == BufferType.Static:
            raise RuntimeError("Cannot update data in a static buffer, use dynamic or stream instead.")
        self.bind()
        glBufferSubData(self.target, offset, data.nbytes, data)

    def __del__(self):
        """Clean up buffer when object is destroyed."""
        glDeleteBuffers(1, [self.id])

class VertexBuffer(Buffer):
    """Vertex buffer object for storing vertex data."""
    def __init__(self, data, buffer_type, size):
        super().__init__(data, buffer_type, GL_ARRAY_BUFFER, size)

class IndexBuffer(Buffer):
    """Index buffer object for storing index data."""
    def __init__(self, data, buffer_type, size):
        super().__init__(data, buffer_type, GL_ELEMENT_ARRAY_BUFFER, size)
        self.count = len(data) if data is not None else 0

    def update_data(self, data, offset=0):
        """Update the buffer's data."""
        self.count = len(data) if data is not None else 0
        super().update_data(data, offset)

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
    def __init__(self, vertex_data, index_data, draw_type, line_width=1.0, point_size=1.0):
        self.vertex_data = vertex_data
        self.index_data = index_data
        self.draw_type = draw_type
        self.line_width = line_width
        self.point_size = point_size
        self.model_matrix = np.identity(4, dtype=np.float32)

    # TODO: Do we need offset??
    
    def set_vertex_data(self, data, offset=0):
        """Update the vertex data of this render object."""
        self.vertex_data = data

    def set_index_data(self, data, offset=0):
        """Update the index data of this render object."""
        self.index_data = data

    def set_transform(self, translate=(0, 0, 0), rotate=(0, 0, 0), scale=(1, 1, 1)):
        """Set the transform matrix - Will scale, rotate and translate the object, in that order."""
        self.model_matrix = Transform(translate, rotate, scale).transform_matrix().T # Transpose to convert row-major to column-major


# class RenderObject:
#     """Represents a renderable object with vertex, index buffers, and shader."""
#     def __init__(self, vb, ib, va, draw_type, shader, line_width=1.0, point_size=1.0):
#         self.vb = vb
#         self.ib = ib
#         self.va = va
#         self.shader = shader
#         self.draw_type = draw_type
#         self.line_width = line_width
#         self.point_size = point_size
#         self.model_matrix = np.identity(4, dtype=np.float32)

#     def set_vertex_data(self, data, offset=0):
#         """Update the vertex data of this render object."""
#         self.vb.update_data(data, offset)

#     def set_index_data(self, data, offset=0):
#         """Update the index data of this render object."""
#         self.ib.update_data(data, offset)

#     def set_transform(self, translate=(0, 0, 0), rotate=(0, 0, 0), scale=(1, 1, 1)):
#         """Set the transform matrix - Will scale, rotate and translate the object, in that order."""
#         self.model_matrix = Transform(translate, rotate, scale).transform_matrix().T # Transpose to convert row-major to column-major
