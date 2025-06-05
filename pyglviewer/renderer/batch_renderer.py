from typing import Dict, List, Optional
import numpy as np
from OpenGL.GL import *
from pyglviewer.renderer.objects import VertexBuffer, IndexBuffer, VertexArray, RenderObject
from pyglviewer.renderer.shapes import Vertex

class BatchBuffer:
    """Batch renderer buffer for OpenGL objects."""
    
    def __init__(self, max_vertices, max_indices, buffer_type):
        self.max_vertices = max_vertices
        self.max_indices = max_indices
        self.buffer_type = buffer_type
        self.growth_factor = 1.5  # Increase buffer by 50% when needed
        
        # Batch storage - simple list of objects per batch key
        self.batches: Dict[str, List[RenderObject]] = {}
        
        # Create initial buffers
        self.vertex_buffer, self.index_buffer, self.vao = self._create_buffers()
        
        # Statistics
        self.vertex_count = 0
        self.index_count = 0
        self.draw_calls = 0
        
        # # Flag to track if buffer needs updating
        # self.needs_update = True  # TODO: Add this
        
    def _create_buffers(self):
        """Create or recreate buffers with current max sizes."""
        vertex_size = Vertex.vertex_size()
        vertex_buffer = VertexBuffer(
            None,
            self.buffer_type,
            self.max_vertices * vertex_size
        )
        
        index_buffer = IndexBuffer(
            None,
            self.buffer_type,
            self.max_indices * np.dtype(np.uint32).itemsize
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
        
        print(f"Resizing buffers: vertices {self.max_vertices}->{new_vertex_count}, indices {self.max_indices}->{new_index_count}")
        
        # Store old buffers
        old_vertex_buffer = self.vertex_buffer
        old_index_buffer = self.index_buffer
        old_vao = self.vao
        
        # Update sizes
        self.max_vertices = new_vertex_count
        self.max_indices = new_index_count
        
        try:
            # Create new buffers
            self.vertex_buffer, self.index_buffer, self.vao = self._create_buffers()
            
            # Check buffer bindings
            current_array_buffer = glGetIntegerv(GL_ARRAY_BUFFER_BINDING)
            print(f"Current GL_ARRAY_BUFFER binding: {current_array_buffer}")

            # # Check buffer sizes (assuming you have a way to track them)
            # print(f"Source buffer size: {source_buffer_size}")
            # print(f"Destination buffer size: {destination_buffer_size}")

            # # Check offsets and size
            # print(f"Read offset: {readOffset}, Write offset: {writeOffset}, Size: {size}")

            # Check for OpenGL errors
            error = glGetError()
            if error != GL_NO_ERROR:
                print(f"OpenGL Error: {error}")
                
            # Copy existing data if any
            if self.vertex_count > 0:
                old_vertex_buffer.bind()
                glCopyBufferSubData(
                    GL_ARRAY_BUFFER, GL_ARRAY_BUFFER,
                    0, 0,
                    self.vertex_count * Vertex.vertex_size()
                )
                
            if self.index_count > 0:
                old_index_buffer.bind()
                glCopyBufferSubData(
                    GL_ELEMENT_ARRAY_BUFFER, GL_ELEMENT_ARRAY_BUFFER,
                    0, 0,
                    self.index_count * np.dtype(np.uint32).itemsize
                )
                
        finally:
            # Clean up old buffers
            old_vertex_buffer.shutdown()
            old_index_buffer.shutdown()
            old_vao.shutdown()
    
    def clear(self):
        """Clear the buffer data."""
        # print(f"Clearing buffer: {self.buffer_type}")
        # if not self.needs_update:
        #     return
        self.batches.clear()
        self.draw_calls = 0
        self.vertex_count = 0
        self.index_count = 0
    
    def add_object_to_buffer(self, render_object: RenderObject):
        """Add object to appropriate batch."""
        
        # Create batch key based on draw type
        batch_key = f"draw_type_{render_object.draw_type}"
        # Add shader id to key
        batch_key += f"_shader_{render_object.shader.program}"
        # Add line width to key if it's a line type
        if render_object.draw_type in (GL_LINES, GL_LINE_STRIP, GL_LINE_LOOP):
            batch_key += f"_line_width_{render_object._line_width}"
        # Add point size to key if it's a point type
        elif render_object.draw_type == GL_POINTS:
            batch_key += f"_point_size_{render_object._point_size}"
            batch_key += f"_point_shape_{render_object._point_shape}"
        # Add new batch if it doesn't exist
        if batch_key not in self.batches:
            self.batches[batch_key] = []
        # print(f'Batch key: {batch_key}')
        # Add object to batch
        self.batches[batch_key].append(render_object)
        # self.needs_update = True
    
    def update_buffers(self):
        """Update buffer data."""
        # if not self.needs_update:
        #     return
        combined_vertices = []
        combined_indices = []
        vertex_offset = 0
        
        # First pass: collect all vertex and index data
        for batch_data in self.batches.values():
            # print(f'n objects: {len(batch_data)}')
            for obj in batch_data:
                if obj._vertex_data is None or obj._index_data is None:
                    continue
                    
                vertex_data = obj._vertex_data.reshape(-1, 9)
                num_vertices = len(vertex_data)
                
                combined_vertices.append(vertex_data)
                combined_indices.append(obj._index_data + vertex_offset)
                vertex_offset += num_vertices
        
        if not combined_vertices or not combined_indices:
            return
            
        # Combine all data
        vertex_data = np.concatenate(combined_vertices)
        index_data = np.concatenate(combined_indices)
        
        # Check if we need to resize buffers
        vertex_count = len(vertex_data)
        index_count = len(index_data)
        
        # print(f"Vertex count: {vertex_count}, Index count: {index_count}")
        if vertex_count > self.max_vertices or index_count > self.max_indices:
            # Calculate new sizes with growth factor
            new_vertex_count = max(self.max_vertices, int(vertex_count * self.growth_factor))
            new_index_count = max(self.max_indices, int(index_count * self.growth_factor))
            self._resize_buffers(new_vertex_count, new_index_count)
        
        # Update buffers with new data
        self.vertex_buffer.update_data(vertex_data.astype(np.float32))
        self.index_buffer.update_data(index_data.astype(np.uint32))
        
        # Update statistics
        self.vertex_count = vertex_count
        self.index_count = index_count
        # self.needs_update = False
    
    def get_stats(self):
        """Get key rendering statistics."""
        # Calculate batch stats - batches contains lists directly, not dictionaries
        total_objects = sum(len(batch_objects) for batch_objects in self.batches.values())
        
        # Calculate buffer usage percentages
        vertex_buffer_usage = (self.vertex_count / self.max_vertices * 100) if self.max_vertices > 0 else 0
        index_buffer_usage = (self.index_count / self.max_indices * 100) if self.max_indices > 0 else 0
        
        return {
            'buffer_type': str(self.buffer_type),
            'draw_calls': self.draw_calls,
            'total_objects': total_objects,
            'batch_count': len(self.batches),
            'buffer_usage': {
                'vertices': f"{self.vertex_count}/{self.max_vertices} ({vertex_buffer_usage:.1f}%)",
                'indices': f"{self.index_count}/{self.max_indices} ({index_buffer_usage:.1f}%)"
            }
        }

class BatchRenderer:
    """Batch renderer for OpenGL objects."""
    
    def __init__(self, max_static_vertices=10000, max_static_indices=30000,
                 max_dynamic_vertices=10000, max_dynamic_indices=30000):
        """Initialize the batch renderer with static and dynamic buffers."""
        # Create static and dynamic buffers
        self.static_buffer = BatchBuffer(max_static_vertices, max_static_indices, GL_STATIC_DRAW)
        self.dynamic_buffer = BatchBuffer(max_dynamic_vertices, max_dynamic_indices, GL_DYNAMIC_DRAW)
    
    def add_object_to_batch(self, render_object: RenderObject):
        """Add object to appropriate buffer based on type."""
        buffer = self.static_buffer if render_object._static else self.dynamic_buffer
        buffer.add_object_to_buffer(render_object)
        
    def clear(self):
        """Clear both static and dynamic buffers."""
        self.static_buffer.clear()
        self.dynamic_buffer.clear()
    
    def update_buffers(self):
        """Update static buffer if needed."""
        self.static_buffer.update_buffers()
        self.dynamic_buffer.update_buffers()
    
    def render(self, view_matrix: np.ndarray, projection_matrix: np.ndarray,
               camera_pos: np.ndarray, lights: Optional[List] = None):
        """Render both static and dynamic buffers."""
        # Update buffers if required
        self.update_buffers()
        # Render static objects first
        self._render_buffer(self.static_buffer, view_matrix, projection_matrix, camera_pos, lights)
        # Then render dynamic objects
        self._render_buffer(self.dynamic_buffer, view_matrix, projection_matrix, camera_pos, lights)
    
    def _render_buffer(self, buffer: BatchBuffer, view_matrix: np.ndarray,
                      projection_matrix: np.ndarray, camera_pos: np.ndarray,
                      lights: Optional[List] = None):
        """Render objects from specified buffer."""
        # Skip if no objects to render
        if not buffer.batches:
            return
        
        # Bind VAO and shader
        buffer.vao.bind()
        buffer.vertex_buffer.bind()
        buffer.index_buffer.bind()
        
        # Draw each batch separately
        index_offset = 0        
        self.draw_calls = 0

        current_shader = None
        
        try:
            for batch_key, objects in buffer.batches.items():
                if not objects or len(objects) == 0:
                    continue
                
                # Get properties from first object in batch
                first_obj = objects[0]
                draw_type = first_obj.draw_type
                shader = first_obj.shader
                
                # Only set up shader if it's different from the current one
                if shader != current_shader:
                    shader.use()
                    shader.set_view_matrix(view_matrix)
                    shader.set_projection_matrix(projection_matrix)
                    shader.set_view_position(camera_pos)
                    if lights:
                        shader.set_light_uniforms(lights)
                    current_shader = shader
                
                # Set line width or point properties if needed
                if draw_type in (GL_LINES, GL_LINE_STRIP, GL_LINE_LOOP):
                    glLineWidth(first_obj._line_width)
                elif draw_type == GL_POINTS:
                    glPointSize(first_obj._point_size)
                    current_shader.set_point_shape(first_obj._point_shape)
                    
                # Draw each object in the batch
                for obj in objects:
                    if obj._vertex_data is None or obj._index_data is None:
                        continue
                    # Set model matrix for this object
                    current_shader.set_model_matrix(obj.model_matrix)
                    # Set alpha for transparency
                    current_shader.set_alpha(obj._alpha)
                    # Calculate number of indices for this object
                    num_indices = len(obj._index_data)
                    # Draw the object
                    glDrawElements(
                        draw_type,
                        num_indices,
                        GL_UNSIGNED_INT,
                        ctypes.c_void_p(index_offset * 4)  # 4 bytes per uint32
                    )
                    
                    index_offset += num_indices
                    self.draw_calls += 1
                    
        finally:
            # Cleanup state
            buffer.vao.unbind()
            buffer.vertex_buffer.unbind()
            buffer.index_buffer.unbind()
            glUseProgram(0)
        
    
    def get_stats(self):
        """Get combined rendering statistics."""
        return {
            'static': self.static_buffer.get_stats(),
            'dynamic': self.dynamic_buffer.get_stats()
        }
