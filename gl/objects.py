from typing import Dict, Any, List
import ctypes
import numpy as np
from OpenGL.GL import *
from utils.transform import Transform
from core.geometry import GeometryData, Vertex

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

    def __del__(self):
        """Clean up VAO when object is destroyed."""
        glDeleteVertexArrays(1, [self.vao])

class BatchEntry:
    """Represents a single entry in a batch."""
    def __init__(self, geometry: GeometryData, model_matrix: np.ndarray, 
                 draw_type: int, line_width: float = 1.0, point_size: float = 1.0):
        self.geometry = geometry
        self.model_matrix = model_matrix
        self.draw_type = draw_type
        self.line_width = line_width
        self.point_size = point_size

class RenderBatch:
    """Manages a batch of similar geometry for rendering."""
    def __init__(self, shader, draw_type: int):
        self.shader = shader
        self.draw_type = draw_type
        self.entries: List[BatchEntry] = []
        self.vertex_count = 0
        self.index_count = 0

    def can_add(self, entry: BatchEntry) -> bool:
        """Check if an entry can be added to this batch."""
        return (self.shader == entry.geometry.shader and 
                self.draw_type == entry.draw_type)

class RenderObject:
    """Represents a renderable object with geometry and rendering properties."""
    def __init__(self, geometry: GeometryData, shader, draw_type: int, 
                 line_width: float = 1.0, point_size: float = 1.0):
        self.geometry = geometry
        self.shader = shader
        self.draw_type = draw_type
        self.line_width = line_width
        self.point_size = point_size
        self.model_matrix = np.identity(4, dtype=np.float32)
        
        # For dynamic/stream buffers
        self.buffer_type = BufferType.Static
        self.vertex_buffer_size = 0
        self.index_buffer_size = 0

    def set_vertex_data(self, data: np.ndarray, offset: int = 0):
        """Update the vertex data of this render object."""
        if hasattr(self.geometry, 'buffer_size'):
            # For dynamic/stream buffers
            vertex_count = len(data) // Vertex.SIZE  # Divide by 9 (3 pos + 3 color + 3 normal)
            vertices = []
            for i in range(vertex_count):
                idx = i * Vertex.SIZE
                vertices.append(Vertex(
                    position=data[idx:idx+3],
                    color=data[idx+3:idx+6],
                    normal=data[idx+6:idx+9]
                ))
            self.geometry.vertices = np.array(vertices, dtype=Vertex)
        else:
            self.geometry.update_vertices(data)

    def set_index_data(self, data: np.ndarray, offset: int = 0):
        """Update the index data of this render object."""
        if hasattr(self.geometry, 'buffer_size'):
            self.geometry.indices = np.array(data, dtype=np.uint32)
        else:
            self.geometry.update_indices(data)

    def set_transform(self, translate=(0, 0, 0), rotate=(0, 0, 0), scale=(1, 1, 1)):
        """Set the transform matrix - Will scale, rotate and translate the object, in that order."""
        self.model_matrix = Transform(translate, rotate, scale).transform_matrix().T # Transpose to convert row-major to column-major

