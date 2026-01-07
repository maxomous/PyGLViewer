from typing import Dict, Any, List, Optional
import ctypes
import numpy as np
from OpenGL.GL import *
from pyglviewer.utils.transform import Transform
from pyglviewer.renderer.shader import Shader, PointShape
from pyglviewer.renderer.shapes import Shape
from dataclasses import dataclass

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
        if data_size + offset > self.size:
            raise MemoryError(f'Buffer is not large enough (current: {self.size}, required: {data_size + offset})')
            # self.bind()
            # # Allocate new buffer with new size (maybe add some extra space for future growth)
            # new_size = (data_size + offset) * 2  # Double the size for future growth
            # glBufferData(self.target, new_size, None, self.buffer_type)  # Allocate new size
            # self.size = new_size
        
            # TODO: Replace with:
            # # if self.index_count > 0:
            # #     old_index_buffer.bind()
            # #     glCopyBufferSubData(
            # #         GL_ELEMENT_ARRAY_BUFFER, GL_ELEMENT_ARRAY_BUFFER,
            # #         0, 0,
            # #         self.index_count * np.dtype(np.uint32).itemsize
            # #     )
                
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
    """An object is a container for multiple similar render objects (for example a body and its wireframe)."""
    
    def __init__(self):
        # List of Shapes (usually body and wireframe)
        self._shape_data: List[dict]         = []        # list of dictionarys: [{'shape': shape, 'segment': buffer_segment}] where segment = {'vertex_offset': 0, 'index_offset': 0, 'vertex_size': 0, 'index_size': 0}
        # Set properties
        self._transform: Transform           = Transform()
        self._model_matrix                   = np.identity(4, dtype=np.float32)
        self._point_size: float              = 1.0
        self._line_width: float              = 1.0
        self._point_shape: PointShape        = PointShape.CIRCLE
        self._alpha: float                   = 1.0
        self._selectable: bool               = True
        self._selected: bool                 = False
        self._metadata: dict                 = {}
        # Cached boundary region
        self._world_bounds: Optional[dict]   = None
        self._bounds_needs_update: bool      = True
    
    # Setters
    
    # handled in render_buffer.py
    # def set_shape_data(self, shape_data):
    #     '''
    #     Update the shape data (vertex buffer, index buffer, draw type, and shader) 
    #     from one or more Shape objects
        
    #     Parameters
    #     ----------
    #     shape_data : list[dict]
    #         A list of dictionaries, each describing a shape entry. Each dictionary 
    #         should contain:
            
    #         - 'shape' : Shape
    #             The Shape object providing vertex and index data.
    #         - 'vertex_offset' : int
    #             Offset into the vertex buffer where this shape’s vertices begin.
    #         - 'index_offset' : int
    #             Offset into the index buffer where this shape’s indices begin.
    #     '''
    #     # Set shapes
    #     self._shape_data = shape_data
    #     # Mark bounds for recalculation
    #     self._bounds_needs_update = True
    
    def set_transform(self, transform: Transform):
        """Set the 4x4 transformation matrix.
        point_size=1.0, line_width=1.0, point_shape=PointShape.CIRCLE, alpha=1.0, static=False, selectable=True, metadata=None
        Parameters
        ----------
        transform : Transform
            Transform object
        """
        self._transform = Transform() if transform is None else transform
        self._model_matrix = np.identity(4, dtype=np.float32) if transform is None else transform.transform_matrix().T 
        self._bounds_needs_update = True  # Mark bounds for recalculation
    def set_translate(self, translate=(0, 0, 0)):
        """Set the translation component of the object's model matrix.
        
        Parameters
        ----------
        translate : tuple, optional
            Translation vector (x,y,z) (default: (0,0,0))
        """
        self._transform.set_translate(translate[0], translate[1], translate[2])
        self._model_matrix[3, :3] = translate
        self._bounds_needs_update = True  # Mark bounds for recalculation
    def set_point_size(self, point_size):
        self._point_size = point_size
    def set_line_width(self, line_width):
        self._line_width = line_width
    def set_point_shape(self, point_shape):
        self._point_shape = point_shape
    def set_alpha(self, alpha):
        self._alpha = alpha
    def set_metadata(self, metadata):
        self._metadata = metadata
    def set_selectable(self, selectable):
        self._selectable = selectable
    def select(self):        
        """Mark this object as selected. Only selects if object's selectable flag is True."""
        if self._selectable:
            self._selected = True
    def deselect(self):
        """Mark this object as not selected."""
        self._selected = False
    def toggle_select(self):
        """Toggle the selection state of this object. Only toggles if object's selectable flag is True."""
        if self._selectable:
            self._selected = not self._selected
    
    # Getters
    def get_point_size(self):
        return self._point_size
    def get_line_width(self):
        return self._line_width
    def get_point_shape(self):
        return self._point_shape
    def get_alpha(self):    
        return self._alpha
    def get_metadata(self):    
        return self._metadata
    def get_selectable(self):
        return self._selectable
    def get_selected(self):
        return self._selected
    def get_midpoint(self):
        '''Returns midpoint of bounding box of object'''
        bounds = self.get_bounds()
        if bounds is None:
            return None
        return (bounds['min'] + bounds['max']) / 2
    def get_bounds(self):
        """Calculate accurate bounds in world space.
        
        Returns
        -------
        dict or None
            Dictionary containing 'min' and 'max' bounds as np.ndarray, or None if no vertex data
        """
        if self._shape_data is None or len(self._shape_data) == 0:
            return None
        # Return cached bounds if available and doesnt need update
        if not self._bounds_needs_update:
            return self._world_bounds
        
        # Combine all shape vertices and reshape to Nx3 array of positions and remove colours / normals
        vertices = np.concatenate([shape_data['shape'].vertex_data for shape_data in self._shape_data]).reshape(-1, 3, 3)[:,0,:]
        # Get local bounds from actual vertex data
        local_min = np.min(vertices, axis=0)
        local_max = np.max(vertices, axis=0)
        
        # Apply transform to bounds
        world_min = (self._model_matrix.T @ np.append(local_min, 1))[:3]
        world_max = (self._model_matrix.T @ np.append(local_max, 1))[:3]
                
        # Ensure min is actually min and max is actually max after transform
        bounds_min = np.minimum(world_min, world_max)
        bounds_max = np.maximum(world_min, world_max)
        
        self._world_bounds = {
            'min': bounds_min,
            'max': bounds_max
        }
        self._bounds_needs_update = False
        return self._world_bounds
    def get_transform(self):
        """Get the transform of the object.
        
        Returns
        -------
        Transform
            The Transform of the object
        """
        return self._transform
    def get_translate(self):
        """Get the translation of the object.
        
        Returns
        -------
        np.ndarray
            Translation vector (x, y, z)
        """
        return self._transform.translate   # return self._model_matrix[3, :3]
    def get_scale(self):
        """Get the translation of the object.
        
        Returns
        -------
        np.ndarray
            Scale vector (sx, sy, sz)
        """
        return self._transform.scale
    def get_rotate(self):
        """Get the rotation of the object.
        
        Returns
        -------
        np.ndarray
            Rotation vector (rx, ry, rz) in radians
        """
        return self._transform.rotate

    def is_point(self):
        '''Returns true if any shape is a point'''
        return any([shape_data['shape'].draw_type == GL_POINTS for shape_data in self._shape_data])
