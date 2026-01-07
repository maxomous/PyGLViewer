from typing import Dict, List, Optional
from collections import defaultdict
import numpy as np
from OpenGL.GL import *
from pyglviewer.renderer.objects import VertexBuffer, IndexBuffer, VertexArray, Object
from pyglviewer.renderer.shapes import Shape, Vertex


class RenderBuffer:
    """ Buffer to store and renderer objects in OpenGL"""
    
    def __init__(self, max_vertices, max_indices, buffer_type):
        self.max_vertices = max_vertices
        self.max_indices = max_indices
        self.buffer_type = buffer_type
        self.growth_factor = 1.5  # Increase buffer by 50% when needed
        # Create initial buffers
        self.vertex_buffer, self.index_buffer, self.vao = self._create_buffers()
        self.objects = {}    
        self.current_vertex = 0
        self.current_index = 0
        self.dangling = {'vertices': [], 'indices': []}
        # Statistics
        self.draw_calls = 0
        
    def _create_buffers(self):
        """Create or recreate buffers with current max sizes."""
        vertex_size = Vertex.vertex_size()
        index_size = Vertex.index_size()
        
        vertex_buffer = VertexBuffer(
            None,
            self.buffer_type,
            self.max_vertices * vertex_size
        )
        
        index_buffer = IndexBuffer(
            None,
            self.buffer_type,
            self.max_indices * index_size
        )
        
        # Create VAO with standard layout
        vao = VertexArray()
        vao.add_buffer(vertex_buffer, [
            # Position attribute (location=0)
            {
                'index': 0,
                'size': 3,
                'type': GL_FLOAT,
                'normalized': False,
                'stride': vertex_size,
                'offset': 0
            },
            # Colour attribute (location=1)
            {
                'index': 1,
                'size': 3,
                'type': GL_FLOAT,
                'normalized': False,
                'stride': vertex_size,
                'offset': 3 * np.dtype(np.float32).itemsize
            },
            # Normal attribute (location=2)
            {
                'index': 2,
                'size': 3,
                'type': GL_FLOAT,
                'normalized': False,
                'stride': vertex_size,
                'offset': 6 * np.dtype(np.float32).itemsize
            }
        ])
        return vertex_buffer, index_buffer, vao
    
    def _resize_buffers(self, new_vertex_count, new_index_count):
        """Resize buffers to accommodate more data."""
        # Store old buffers
        old_vertex_buffer, old_index_buffer, old_vao = self.vertex_buffer, self.index_buffer, self.vao
        old_max_vertices, old_max_indices = self.max_vertices, self.max_indices
        
        # Update sizes
        self.max_vertices = new_vertex_count
        self.max_indices = new_index_count
        print(f"Resizing buffers: vertices {old_max_vertices}->{new_vertex_count}, indices {old_max_indices}->{new_index_count}")
        try:
            # Create new buffers
            self.vertex_buffer, self.index_buffer, self.vao = self._create_buffers()
            # Copy old contents into new buffer
            glBindBuffer(GL_COPY_READ_BUFFER, old_vertex_buffer.id)
            glBindBuffer(GL_COPY_WRITE_BUFFER, self.vertex_buffer.id)
            glCopyBufferSubData(GL_COPY_READ_BUFFER, GL_COPY_WRITE_BUFFER, 0, 0, min(old_max_vertices, self.max_vertices) * Vertex.vertex_size())
            # Copy old contents into new buffer
            glBindBuffer(GL_COPY_READ_BUFFER, old_index_buffer.id)
            glBindBuffer(GL_COPY_WRITE_BUFFER, self.index_buffer.id)
            glCopyBufferSubData(GL_COPY_READ_BUFFER, GL_COPY_WRITE_BUFFER, 0, 0, min(old_max_indices, self.max_indices) * Vertex.index_size())
            # Cleanup: unbind copy targets
            glBindBuffer(GL_COPY_READ_BUFFER, 0)
            glBindBuffer(GL_COPY_WRITE_BUFFER, 0)

        finally:
            # Clean up old buffers           
            old_vertex_buffer.shutdown()
            old_index_buffer.shutdown()
            old_vao.shutdown()
    
    def clear(self):
        """Clear the buffer data."""
        for name in list(self.objects.keys()):
            self.remove_object(name)
        self.draw_calls = 0
        self.current_vertex = 0
        self.current_index = 0
        self.dangling = {'vertices': [], 'indices': []}
    
        print(f'Clear() is not properly implemented')
    
    def add_object(self, name, object: Object):
        if name in self.objects:
            raise ValueError(f"Object '{name}' already exists")
        self.objects[name] = object
    
    def remove_object(self, name):
        object = self.objects[name]
        self._clear_object_shapes(object)
        # TOOD: is there anything else to clear before the deleting an object?
        del self.objects[name]
    
    def _free_segment(self, shape_data):
        '''Make list of redundant vertices and indices we can later reuse'''
        shape = shape_data['shape']
        segment = shape_data['segment']
        if (shape is None) or (segment is None) or (shape.vertex_data is None) or (shape.indices is None):
            return
        if segment['vertex_size'] > 0:
            self.dangling['vertices'].append({'offset': segment['vertex_offset'], 'size': segment['vertex_size']})
        if segment['index_size'] > 0:
            self.dangling['indices'].append({'offset': segment['index_offset'], 'size': segment['index_size']})
            
        
    def _allocate_segment(self, vertex_count, index_count):
        """
        Resize the object's shape list to match the provided shapes.
        """
        # Resize buffer if needed (see self.growth_factor)
        if self.current_vertex + vertex_count > self.max_vertices or self.current_index + index_count > self.max_indices:
            new_vertex_count = max(self.max_vertices, int(self.current_vertex + vertex_count * self.growth_factor))
            new_index_count = max(self.max_indices, int(self.current_index + index_count * self.growth_factor))
            self._resize_buffers(new_vertex_count, new_index_count)
        
        buffer_segment = {
            'vertex_offset': self.current_vertex,   # TODO: Reuse self.dangling if possible
            'index_offset': self.current_index,
            'vertex_size': vertex_count,
            'index_size': index_count
        }
        # Update global offsets
        self.current_vertex += vertex_count
        self.current_index += index_count
        print(f'Allocating segment (current_vertex: {self.current_vertex}, current_index: {self.current_index})')
        return buffer_segment
        
        
    def _allocate_space(self, name: str, shapes: list[Shape]):
        """
        Resize the object's shape list to match the provided shapes.
        """    
        object = self.objects[name]
        # make sure there is at least as many shape_datas as shapes
        while len(object._shape_data) < len(shapes):
            object._shape_data.append({'shape': None, 'segment': None})
        
        for i, shape, in enumerate(shapes):
            # If size of new shape is larger than the availble segement, mark the old for reuse and allocate a new space
            if (
                object._shape_data[i]['segment'] is None
                or shape.vertex_count > object._shape_data[i]['segment']['vertex_size']
                or shape.index_count > object._shape_data[i]['segment']['index_size']
            ):
                self._free_segment(object._shape_data[i])
                object._shape_data[i]['segment'] = self._allocate_segment(shape.vertex_count, shape.index_count)
                object._bounds_needs_update = True
       
    def _update_shapes(self, name: str, shapes: list[Shape]):
        object = self.objects[name]
        # Clear old shape data
        for shape_data in object._shape_data:
            shape_data['shape'] = None
        # Set shapes to shape_data
        for i, shape in enumerate(shapes):
            object._shape_data[i]['shape'] = shape
        # Since we are manually modifying the object's shape, we must also set a flag to update the bounds
        object._bounds_needs_update = True
            

    def set_object_shapes(self, name, shapes: Shape | list[Shape]):
        """Add shape to the object, and update the gpu data"""
        
        if name not in self.objects:
            raise ValueError('Object does not exist in buffer')
        object = self.objects[name]
        
        if not isinstance(shapes, list) and not isinstance(shapes, Shape):
            raise ValueError('Shapes must be a list of Shapes or a single Shape')
        # Make sure we have a list of Shapes
        if not isinstance(shapes, list):
            shapes = [shapes]
        
        
        # Allocate more space if required
        self._allocate_space(name, shapes)
         
        # Sanity check
        if len(shapes) > len(object._shape_data):
            raise ValueError(f'Thare more shapes {len(shapes)} than shape_data {len(object._shape_data)}')
        
        # Clear and set shapes to shape_data 
        self._update_shapes(name, shapes)
        
        # Set vertex & index data
        for i, shape in enumerate(shapes):
            if shape.vertex_data is None or shape.indices is None:
                continue
            vertex_offset, index_offset, vertex_size, index_size = object._shape_data[i]['segment'].values()
            vertex_data = shape.vertex_data.reshape(-1, 9).astype(np.float32)
            index_data = (shape.indices + vertex_offset).astype(np.uint32)
            # Update buffers with new data (using glBufferSubData)
            self.vertex_buffer.update_data(vertex_data, offset=vertex_offset * Vertex.vertex_size())
            self.index_buffer.update_data(index_data, offset=index_offset * Vertex.index_size())
                    
    
    def render_buffer(self, view_matrix: np.ndarray, projection_matrix: np.ndarray, camera_pos: np.ndarray, lights: Optional[List] = None):
        """Render objects from specified buffer."""
        # Skip if no objects to render
        if not self.objects:
            return
        
        # Group shapes by (shader, draw_type)
        batches = defaultdict(list)
        for name, obj in self.objects.items():
            for shape_data in obj._shape_data:
                batch_key = f"Shader:{shape_data['shape'].shader.program}_Primitive:{shape_data['shape'].draw_type}"
                batches[batch_key].append((obj, shape_data))
        
        # Bind VAO and shader
        self.vao.bind()
        self.vertex_buffer.bind()
        self.index_buffer.bind()
        
        self.draw_calls = 0
        current_shader = None
        
        # Draw each batch
        try:
            
            for batch_key, batch_data in batches.items():
                for (object, shape_data) in batch_data:
                    shape = shape_data["shape"]
                    vertex_offset, index_offset, vertex_size, index_size = shape_data['segment'].values()
                    # Handle blank shapes
                    if not shape:
                        continue
                    
                    # Get properties from first object in batch
                    primitive = shape.draw_type
                    shader = shape.shader
                    
                    # Set up shader if it's different from the current one
                    if shader != current_shader:
                        shader.use()
                        shader.set_view_matrix(view_matrix)
                        shader.set_projection_matrix(projection_matrix)
                        shader.set_view_position(camera_pos)
                        if lights:
                            shader.set_light_uniforms(lights)
                        current_shader = shader
                            
                    # Set line width or point properties if needed
                    if primitive in (GL_LINES, GL_LINE_STRIP, GL_LINE_LOOP):
                        glLineWidth(object._line_width)
                    elif primitive == GL_POINTS:
                        glPointSize(object._point_size)
                        current_shader.set_point_shape(object._point_shape)
                        
                    # Draw each object in the batch
                    if shape.vertex_data is None or shape.indices is None:
                        continue
                    # Set model matrix for this object
                    current_shader.set_model_matrix(object._model_matrix)
                    # Set alpha for transparency
                    current_shader.set_alpha(object._alpha)
                    # Draw the object
                    glDrawElements(
                        primitive,
                        shape.index_count,
                        GL_UNSIGNED_INT,
                        ctypes.c_void_p(index_offset * Vertex.index_size())  # 4 bytes per uint32
                    )
                    # Count the draw calls
                    self.draw_calls += 1
                    
        finally:
            # Cleanup state
            self.vao.unbind()
            self.vertex_buffer.unbind()
            self.index_buffer.unbind()
            glUseProgram(0)
        
    
    def get_stats(self):
        """Get key rendering statistics."""
        # Calculate batch stats - batches contains lists directly, not dictionaries
        total_objects = len(self.objects)
        total_shapes = sum(len(object._shape_data) for object in self.objects.values())
        
        # Calculate buffer usage percentages
        vertex_buffer_usage = (self.current_vertex / self.max_vertices * 100) if self.max_vertices > 0 else 0 # TODO vertex_count NO LONGER EXISTS
        index_buffer_usage = (self.current_index / self.max_indices * 100) if self.max_indices > 0 else 0 # TODO index_count NO LONGER EXISTS
        
        return {
            'buffer_type': str(self.buffer_type),
            'draw_calls': self.draw_calls,
            'total_objects': total_objects,
            'total_shapes': total_shapes,
            'buffer_usage': {
                'vertices': f"{self.current_vertex}/{self.max_vertices} ({vertex_buffer_usage:.1f}%)",
                'indices': f"{self.current_index}/{self.max_indices} ({index_buffer_usage:.1f}%)"
            }
        }
