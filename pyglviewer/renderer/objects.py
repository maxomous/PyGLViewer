from typing import Dict, Any, List
import ctypes
import numpy as np
from OpenGL.GL import *
from pyglviewer.utils.transform import Transform
from pyglviewer.renderer.shader import Shader, PointShape
from pyglviewer.renderer.shapes import Shape
from dataclasses import dataclass

# Used to give each object a unique ID
_global_object_counter = 0

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

class RenderObject:
    """Represents a renderable object with vertex, index buffers, and shader."""
    def __init__(self, point_size=1.0, line_width=1.0, point_shape=PointShape.CIRCLE, alpha=1.0, static=False, selectable=True):
        """Initialize object with given data and parameters.

        Parameters
        ----------
        is_static : bool
            Static or Dynamic buffer type
        point_size : float
            Size for point primitives
        line_width : float
            Width for line primitives
        point_shape : PointShape
            Shape for point primitives
        alpha : float
            Alpha value for transparency
        selectable : bool
            Allow object to be selected
        """
        
        # These should be controlled by the Object class
        self._point_size = point_size
        self._line_width = line_width
        self._point_shape = point_shape
        self._alpha = alpha  # Add alpha value (1.0 = fully opaque, 0.0 = fully transparent)
        self._static = static
        # Add selection-related properties
        self._selectable = selectable  # Flag to control if object can be selected
        self.selected = False
        # Set with set_transform_matrix
        self.model_matrix = np.identity(4, dtype=np.float32)
        # These are set with set_shapes
        self.draw_type = None
        self.shader = None
        self._vertex_data = None
        self._index_data = None
        # Cached boundary region
        self._world_bounds = None
        self._bounds_needs_update = True

    def set_shape(self, shape: Shape):
        """Update the vertex and index data from a Shape object.
        Returns self to allow chaining.
        Parameters
        ----------
        shape : Shape
            Shape object containing vertex and index data
        """
        self.draw_type = shape.draw_type
        self.shader = shape.shader
        self._vertex_data = np.array(shape.get_vertices(), dtype=np.float32)
        self._index_data = np.array(shape.get_indices(), dtype=np.uint32)
        self._bounds_needs_update = True  # Mark bounds for recalculation
        return self
    
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
        if self._vertex_data is None or len(self._vertex_data) == 0:
            return None
        # Return cached bounds if available and doesnt need update
        if not self._bounds_needs_update:
            return self._world_bounds
        
        # Get local bounds from actual vertex data
        vertices = self._vertex_data.reshape(-1, 3, 3)[:,0,:]  # Reshape to Nx3 array of positions and remove colours / normals
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

    def set_transform_matrix(self, transform: Transform):
        """Set the transform matrix.
        Returns self to allow chaining.
        
        Parameters
        ----------
        transform : Transform
            Transform object
        """
        self.model_matrix = transform.transform_matrix().T
        self._bounds_needs_update = True  # Mark bounds for recalculation
        return self
    
    def get_translate(self):
        """Get the translation of the object.
        
        Returns
        -------
        np.ndarray
            Translation vector (x,y,z)
        """
        return self.model_matrix[3, :3]
    
    def set_translate(self, translate=(0, 0, 0)):
        """Set the translation component of the object's model matrix.
        Returns self to allow chaining.
        
        Parameters
        ----------
        translate : tuple, optional
            Translation vector (x,y,z) (default: (0,0,0))
        """
        self.model_matrix[3, :3] = translate
        self._bounds_needs_update = True  # Mark bounds for recalculation
        return self
    
    def select(self):
        """Mark this object as selected.
        
        Only selects if object's selectable flag is True.
        """
        if self._selectable:
            self.selected = True

    def deselect(self):
        """Mark this object as not selected."""
        self.selected = False

    def toggle_selection(self):
        """Toggle the selection state of this object.
        
        Only toggles if object's selectable flag is True.
        """
        if self._selectable:
            self.selected = not self.selected


class Object:
    """An object is a container for multiple similar render objects (for example a body and its wireframe)."""
    def __init__(self, point_size=1.0, line_width=1.0, point_shape=PointShape.CIRCLE, alpha=1.0, static=False, selectable=True, metadata=None):
        # Give each object a unique ID and increment the counter
        global _global_object_counter
        self.id = _global_object_counter
        _global_object_counter += 1
        # Set properties
        self._point_size = point_size
        self._line_width = line_width
        self._point_shape = point_shape
        self._alpha = alpha
        self._static = static
        self._selectable = selectable
        self.metadata = metadata
        self._render_objects = []

    @staticmethod
    def reset_global_id_counter():
        """Reset the global object counter. Warning: only call this if all objects have been deleted from renderer."""
        global _global_object_counter
        _global_object_counter = 0
        
    # These functions are used to set the properties of each of the render objects inside the object
    def set_point_size(self, point_size):
        for obj in [self] + self._render_objects: obj._point_size = point_size
    def set_line_width(self, line_width):
        for obj in [self] + self._render_objects: obj._line_width = line_width
    def set_point_shape(self, point_shape):
        for obj in [self] + self._render_objects: obj._point_shape = point_shape
    def set_alpha(self, alpha):
        for obj in [self] + self._render_objects: obj._alpha = alpha
    def set_static(self, static):
        for obj in [self] + self._render_objects: obj._static = static
    def set_selectable(self, selectable):
        for obj in [self] + self._render_objects: obj._selectable = selectable
        
    def set_shapes(self, shapes):
        # Convert single shape to list if needed
        if not isinstance(shapes, list):
            shapes = [shapes]

        # Initialise objects if they don't exist
        if len(self._render_objects) == 0:
            # Create objects
            for shape in shapes:   
                # Create object for each shape
                self._render_objects.append(RenderObject(
                    point_size=self._point_size,
                    line_width=self._line_width,
                    point_shape=self._point_shape,
                    alpha=self._alpha,
                    static=self._static,
                    selectable=self._selectable,
                ))
                
        if len(shapes) != len(self._render_objects):
            raise ValueError("Number of shapes does not match number of objects")
        
        for i, shape in enumerate(shapes):
            self._render_objects[i].set_shape(shape)
        
        return self
    
    
    def get_mid_point(self):
        bounds = self.get_bounds()
        return (bounds['min'] + bounds['max']) / 2

    def get_bounds(self):
        bounds = []
        for obj in self._render_objects:
            bounds.append(obj.get_bounds())
        min = [b['min'] for b in bounds]
        max = [b['max'] for b in bounds]
        # get min and max bounds
        min_bounds = np.min(min, axis=0)
        max_bounds = np.max(max, axis=0)
        return {'min': min_bounds, 'max': max_bounds}

    def set_transform_matrix(self, transform):
        for obj in self._render_objects:
            obj.set_transform_matrix(transform)
        return self
    
    def get_translate(self):
        if len(self._render_objects) == 0:
            return None
        return self._render_objects[0].get_translate()
    
    def set_translate(self, translate):
        for obj in self._render_objects:
            obj.set_translate(translate)
        return self
    
    def select(self):
        for obj in self._render_objects:
            obj.select()
        return self
    
    def deselect(self):
        for obj in self._render_objects:
            obj.deselect()
        return self
    
    def toggle_selection(self):
        for obj in self._render_objects:
            obj.toggle_selection()
        return self
    