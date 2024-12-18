from typing import Dict, Any, List
import ctypes
import numpy as np
from OpenGL.GL import *
from pyglviewer.utils.transform import Transform
from pyglviewer.renderer.shader import Shader, PointShape
from dataclasses import dataclass
from typing import Optional

# At the top of the file, after imports
_global_object_counter = 0

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
        self.deleted = False  # Track if buffer has been deleted
        self.bind()
        glBufferData(self.target, self.size, data, buffer_type)

    def bind(self):
        """Bind this buffer to its target."""
        glBindBuffer(self.target, self.id)

    def unbind(self):
        """Unbind this buffer from its target."""
        glBindBuffer(self.target, 0)

    def update_data(self, data, offset=0):
        """Update the buffer's data. Reallocates if data is larger than current size."""
        data_size = data.nbytes
        
        # If new data is larger than current buffer, reallocate
        if data_size > self.size:
            self.bind()
            # Allocate new buffer with new size (maybe add some extra space for future growth)
            new_size = data_size * 2  # Double the size for future growth
            glBufferData(self.target, new_size, None, self.buffer_type)  # Allocate new size
            self.size = new_size
        
        self.bind()
        glBufferSubData(self.target, offset, data_size, data)

    def shutdown(self):
        """Clean up buffer."""
        if hasattr(self, 'id') and not self.deleted:
            try:
                glDeleteBuffers(1, [self.id])
                self.deleted = True
                self.id = None
            except Exception:
                # Context might be destroyed, ignore errors
                pass

    def __del__(self):
        """Ensure cleanup on deletion."""
        # Only attempt cleanup if not already deleted
        if hasattr(self, 'deleted') and not self.deleted:
            self.shutdown()

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
        self.deleted = False  # Track if VAO has been deleted

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

    def shutdown(self):
        """Clean up VAO."""
        if hasattr(self, 'vao') and not self.deleted:
            try:
                glDeleteVertexArrays(1, [self.vao])
                self.deleted = True
                self.vao = None
            except Exception:
                # Context might be destroyed, ignore errors
                pass

    def __del__(self):
        """Ensure cleanup on deletion."""
        # Only attempt cleanup if not already deleted
        if hasattr(self, 'deleted') and not self.deleted:
            self.shutdown()

class Object:
    """Represents a renderable object with vertex, index buffers, and shader."""
    def __init__(self, vertex_data, index_data, draw_type, line_width, point_size, 
                 point_shape, buffer_type, selectable, shader=None, alpha=1.0):
        """Initialize object with given data and parameters.
        
        Parameters
        ----------
        vertex_data : np.ndarray or None
            Vertex data for the object
        index_data : np.ndarray or None
            Index data for the object
        draw_type : GL_enum
            OpenGL primitive type (TRIANGLES, LINES, etc)
        line_width : float
            Width for line primitives
        point_size : float
            Size for point primitives
        point_shape : PointShape
            Shape for point primitives
        buffer_type : BufferType
            Static or Dynamic buffer type
        selectable : bool
            Allow object to be selected
        shader : Optional[Shader], optional
            Custom shader for rendering (default: None)
        alpha : float, optional
            Alpha value for transparency (default: 1.0)
        """
        global _global_object_counter
        self.id = _global_object_counter
        _global_object_counter += 1 
        # Ensure vertex_data is a numpy array with the correct shape
        self.vertex_data = vertex_data if vertex_data is None else np.array(vertex_data, dtype=np.float32)
        # Ensure index_data is a numpy array
        self.index_data = index_data if index_data is None else np.array(index_data, dtype=np.uint32)
        self.draw_type = draw_type
        self.line_width = line_width
        self.point_size = point_size
        self.point_shape = point_shape
        self.model_matrix = np.identity(4, dtype=np.float32)
        self.buffer_type = buffer_type
        self.shader = shader  # Store shader per object
        # Add selection-related properties
        self.selected = False
        self.selectable = selectable  # Flag to control if object can be selected
        self.alpha = alpha  # Add alpha value (1.0 = fully opaque, 0.0 = fully transparent)

        # Cache transformed bounds for faster picking
        self._world_bounds = None
        self._bounds_needs_update = True

    def get_mid_point(self):
        """Get the mid point of the object.
        
        Returns
        -------
        np.ndarray
            Mid point coordinates (x,y,z)
        """
        return (self.get_bounds()['min'] + self.get_bounds()['max']) / 2

    def get_bounds(self):
        """Calculate accurate bounds in world space.
        
        Returns
        -------
        dict or None
            Dictionary containing 'min' and 'max' bounds as np.ndarray, or None if no vertex data
        """
        if not hasattr(self, 'vertex_data') or self.vertex_data is None or len(self.vertex_data) == 0:
            return None
        # Return cached bounds if available and doesnt need update
        if not self._bounds_needs_update:
            return self._world_bounds
        
        # Get local bounds from actual vertex data
        vertices = self.vertex_data.reshape(-1, 3, 3)[:,0,:]  # Reshape to Nx3 array of positions and remove colours / normals
        local_min = np.min(vertices, axis=0)
        local_max = np.max(vertices, axis=0)
        
        # Apply transform to bounds
        world_min = (self.model_matrix.T @ np.append(local_min, 1))[:3]
        world_max = (self.model_matrix.T @ np.append(local_max, 1))[:3]
                
        # Ensure min is actually min and max is actually max after transform
        bounds_min = np.minimum(world_min, world_max)
        bounds_max = np.maximum(world_min, world_max)
        
        self._world_bounds = {
            'min': bounds_min,
            'max': bounds_max
        }
        self._bounds_needs_update = False
        return self._world_bounds

    def set_vertex_data(self, data):
        """Update the vertex data.
        
        Parameters
        ----------
        data : np.ndarray
            New vertex data
        """
        self.vertex_data = np.array(data, dtype=np.float32)
        self._bounds_needs_update = True  # Mark bounds for recalculation

    def set_index_data(self, data):
        """Update the index data of this render object.
        
        Parameters
        ----------
        data : np.ndarray
            New index data
        """
        self.index_data = np.array(data, dtype=np.uint32)

    def set_geometry_data(self, geometry):
        """Update the vertex and index data from a geometry object.
        
        Parameters
        ----------
        geometry : Geometry
            Geometry object containing vertex and index data
        """
        self.set_vertex_data(geometry.get_vertices())
        self.set_index_data(geometry.get_indices())
            
    def set_transform_matrix(self, translate=(0, 0, 0), rotate=(0, 0, 0), scale=(1, 1, 1)):
        """Set the transform matrix.
        
        Parameters
        ----------
        translate : tuple, optional
            Translation vector (x,y,z) (default: (0,0,0))
        rotate : tuple, optional
            Rotation angles (x,y,z) (default: (0,0,0))
        scale : tuple, optional
            Scale factors (x,y,z) (default: (1,1,1))
        """
        self.model_matrix = Transform(translate, rotate, scale).transform_matrix().T
        self._bounds_needs_update = True  # Mark bounds for recalculation

    def get_translate(self):
        """Get the translation of the object.
        
        Returns
        -------
        np.ndarray
            Translation vector (x,y,z)
        """
        return self.model_matrix[3, :3]
    
    def set_translate(self, translate=(0, 0, 0)):
        """Set the translation of the object.
        
        Parameters
        ----------
        translate : tuple, optional
            Translation vector (x,y,z) (default: (0,0,0))
        """
        self.model_matrix[3, :3] = translate
        self._bounds_needs_update = True  # Mark bounds for recalculation

    def select(self):
        """Mark this object as selected.
        
        Only selects if object's selectable flag is True.
        """
        if self.selectable:
            self.selected = True

    def deselect(self):
        """Mark this object as not selected."""
        self.selected = False

    def toggle_selection(self):
        """Toggle the selection state of this object.
        
        Only toggles if object's selectable flag is True.
        """
        if self.selectable:
            self.selected = not self.selected


class ObjectCollection:
    def __init__(self, objects: dict[str, Object]):
        self.objects = objects
        
    def __getitem__(self, key: str) -> Object:
        return self.objects[key]
        
    def __setitem__(self, key: str, value: Object):
        self.objects[key] = value
        
    def set_transform_matrix(self, translate=(0, 0, 0), rotate=(0, 0, 0), scale=(1, 1, 1)):
        for object in self.objects.values():
            object.set_transform_matrix(translate, rotate, scale)