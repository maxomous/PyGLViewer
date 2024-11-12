from typing import Dict, List, Optional
import numpy as np
from OpenGL.GL import *
from renderer.objects import BufferType, VertexBuffer, IndexBuffer, VertexArray, Object
from renderer.shaders import Shader, vertex_shader_lighting, fragment_shader_lighting  

    

    #     # TODO: handle buffer_type for static and stream
    # def add_object_base(self, vertices, indices, buffer_type, draw_type=GL_TRIANGLES, line_width=None, point_size=None):
    
class BatchRenderer:
    """Efficient batch renderer for OpenGL objects."""
    
    def __init__(self, max_vertices=10000, max_indices=30000, buffer_type=BufferType.Dynamic, shader=None, shader_point=None):
        """Initialize the batch renderer.
        
        Parameters
        ----------
        max_vertices : int
            Maximum number of vertices in a single batch
        max_indices : int
            Maximum number of indices in a single batch
        """
        self.initial_max_vertices = max_vertices
        self.initial_max_indices = max_indices
        self.max_vertices = max_vertices
        self.max_indices = max_indices
        self.growth_factor = 1.5  # Increase buffer by 50% when needed
        
        # Buffer overflow tracking
        self.overflow_count = 0
        self.max_overflow_warnings = 3
        
        self.buffer_type = buffer_type
        self.shader = shader or Shader(vertex_shader_lighting, fragment_shader_lighting) # Default shader if None
        
        # Batch storage
        self.batches: Dict[str, List[Object]] = {}
        
        # Calculate vertex size: 3 (pos) + 3 (color) + 3 (normal) = 9 floats
        self.vertex_size = 9 * np.dtype(np.float32).itemsize  # Size in bytes
        
        # Create initial buffers
        self._create_buffers()
        
        # Batch statistics
        self.draw_calls = 0
        self.vertex_count = 0
        self.index_count = 0
        
        self.debug = False
    
    def _create_buffers(self):
        """Create or recreate buffers with current max sizes."""
        self.vertex_buffer = VertexBuffer(
            None,
            self.buffer_type,
            self.max_vertices * self.vertex_size
        )
        
        self.index_buffer = IndexBuffer(
            None,
            self.buffer_type,
            self.max_indices * np.dtype(np.uint32).itemsize
        )
        
        # Create VAO with standard layout
        self.vao = VertexArray()
        self.vao.add_buffer(self.vertex_buffer, [
            # Position attribute (location=0)
            {
                'index': 0,
                'size': 3,
                'type': GL_FLOAT,
                'normalized': False,
                'stride': self.vertex_size,
                'offset': 0
            },
            # Color attribute (location=1)
            {
                'index': 1,
                'size': 3,
                'type': GL_FLOAT,
                'normalized': False,
                'stride': self.vertex_size,
                'offset': 3 * np.dtype(np.float32).itemsize
            },
            # Normal attribute (location=2)
            {
                'index': 2,
                'size': 3,
                'type': GL_FLOAT,
                'normalized': False,
                'stride': self.vertex_size,
                'offset': 6 * np.dtype(np.float32).itemsize
            }
        ])
    
    def _resize_buffers(self, new_vertex_count, new_index_count):
        """Resize buffers to accommodate more data."""
        if self.debug:
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
            self._create_buffers()
            
            # Copy existing data if any
            if self.vertex_count > 0:
                old_vertex_buffer.bind()
                glCopyBufferSubData(
                    GL_ARRAY_BUFFER, GL_ARRAY_BUFFER,
                    0, 0,
                    self.vertex_count * self.vertex_size
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
        """Begin a new batch."""
        self.batches.clear()
        self.draw_calls = 0
        self.vertex_count = 0
        self.index_count = 0
    
    def add_object(self, render_object: Object):
        """Submit a render object to the appropriate batch.
        
        Parameters
        ----------
        render_object : RenderObject
            The render object to batch
        """
        # Create batch key based on draw type and line/point size
        batch_key = f"{render_object.draw_type}"
        
        # Add line width to key if it's a line type
        if render_object.draw_type in (GL_LINES, GL_LINE_STRIP, GL_LINE_LOOP):
            batch_key += f"_lw{render_object.line_width}"
        # Add point size to key if it's a point type
        elif render_object.draw_type == GL_POINTS:
            batch_key += f"_ps{render_object.point_size}"
        
        if batch_key not in self.batches:
            self.batches[batch_key] = []
            
        self.batches[batch_key].append(render_object)
    
    def update_buffers(self):
        """Update buffers with combined vertex and index data."""
        combined_vertices = []
        combined_indices = []
        vertex_offset = 0
        
        # First pass: collect all vertex and index data
        for objects in self.batches.values():
            for obj in objects:
                if obj.vertex_data is None or obj.index_data is None:
                    continue
                    
                vertex_data = obj.vertex_data.reshape(-1, 9)
                num_vertices = len(vertex_data)
                
                combined_vertices.append(vertex_data)
                combined_indices.append(obj.index_data + vertex_offset)
                vertex_offset += num_vertices
        
        if not combined_vertices or not combined_indices:
            return
            
        # Combine all data
        vertex_data = np.concatenate(combined_vertices)
        index_data = np.concatenate(combined_indices)
        
        # Check if we need to resize buffers
        vertex_count = len(vertex_data)
        index_count = len(index_data)
        
        if vertex_count > self.max_vertices or index_count > self.max_indices:
            # Calculate new sizes with growth factor
            new_vertex_count = max(self.max_vertices, int(vertex_count * self.growth_factor))
            new_index_count = max(self.max_indices, int(index_count * self.growth_factor))
            
            self._resize_buffers(new_vertex_count, new_index_count)
            
            if self.debug:
                print(f"Buffer overflow {self.overflow_count + 1}: Resized to {new_vertex_count} vertices, {new_index_count} indices")
            
            self.overflow_count += 1
            if self.overflow_count <= self.max_overflow_warnings:
                print(f"Warning: Buffer overflow occurred ({self.overflow_count}/{self.max_overflow_warnings}) - Resizing buffers")
                print(f"Consider initializing with larger buffers: vertices={new_vertex_count}, indices={new_index_count}")
        
        # Update buffers with new data
        self.vertex_buffer.update_data(vertex_data.astype(np.float32))
        self.index_buffer.update_data(index_data.astype(np.uint32))
        
        # Update statistics
        self.vertex_count = vertex_count
        self.index_count = index_count
    
    def render(self, view_matrix: np.ndarray, projection_matrix: np.ndarray, 
             camera_pos: np.ndarray, lights: Optional[List] = None):
        """Render all batched objects.
        
        Parameters
        ----------
        view_matrix : np.ndarray
            The camera view matrix
        projection_matrix : np.ndarray
            The projection matrix
        camera_pos : np.ndarray
            The camera position for lighting calculations
        lights : Optional[List]
            List of lights in the scene
        """
        # Skip if no objects to render
        if not self.batches:
            return
        
        if self.debug:
            print(f"\n=== Starting {self.buffer_type} Render ===")
            print(f"Total batches: {len(self.batches)}")
        
        # Update buffers once for all batches
        self.update_buffers()
        if self.debug:
            print(f"After update_buffers: vertices={self.vertex_count}, indices={self.index_count}")
        
        # Bind VAO and shader
        self.vao.bind()
        self.vertex_buffer.bind()
        self.index_buffer.bind()
        
        # Set up shader
        self.shader.use()
        
        # Set shared uniforms
        self.shader.set_view_matrix(view_matrix)
        self.shader.set_projection_matrix(projection_matrix)
        self.shader.set_view_position(camera_pos)
        if lights:
            self.shader.set_light_uniforms(lights)
            
        # Draw each batch separately
        index_offset = 0
        self.draw_calls = 0
        
        try:
            for batch_key, objects in self.batches.items():
                if self.debug:
                    print(f"\nBatch: {batch_key} with {len(objects)} objects")
                if not objects:
                    continue
                    
                # Get draw type from first object
                draw_type = objects[0].draw_type
                
                # Set line width or point size if needed
                if draw_type in (GL_LINES, GL_LINE_STRIP, GL_LINE_LOOP):
                    glLineWidth(objects[0].line_width)
                elif draw_type == GL_POINTS:
                    glPointSize(objects[0].point_size)
                    
                # Draw each object in the batch
                for i, obj in enumerate(objects):
                    if obj.vertex_data is None or obj.index_data is None:
                        continue
                    # Set model matrix for this object
                    self.shader.set_model_matrix(obj.model_matrix)
                    
                    # Calculate number of indices for this object
                    num_indices = len(obj.index_data)
                    
                    if self.debug:
                        print(f"  Object {i}: indices={num_indices}, offset={index_offset}")
                    
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
            self.vao.unbind()
            self.vertex_buffer.unbind()
            self.index_buffer.unbind()
            glUseProgram(0)
        
        if self.debug:
            print(f"\nRender complete: {self.draw_calls} draw calls")
    

    def get_stats(self):
        """Get key rendering statistics."""
        # Calculate batch stats
        total_objects = sum(len(objects) for objects in self.batches.values())
        
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
