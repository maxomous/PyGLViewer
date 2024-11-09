from typing import Dict, List, Optional
import numpy as np
from OpenGL.GL import *
from renderer.objects import BufferType, VertexBuffer, IndexBuffer, VertexArray, RenderObject
from renderer.shaders import Shader, basic_vertex_shader, basic_fragment_shader  

    

    #     # TODO: handle buffer_type for static and stream
    # def add_object_base(self, vertices, indices, buffer_type, draw_type=GL_TRIANGLES, line_width=None, point_size=None):
    
    # TODO: ADD STREAM BUFFER
    
    
class BatchRenderer:
    """Efficient batch renderer for OpenGL objects."""
    
    def __init__(self, max_vertices: int = 10000, max_indices: int = 30000, shader=None):
        """Initialize the batch renderer.
        
        Parameters
        ----------
        max_vertices : int
            Maximum number of vertices in a single batch
        max_indices : int
            Maximum number of indices in a single batch
        """
        self.max_vertices = max_vertices
        self.max_indices = max_indices
        self.shader = shader or Shader(basic_vertex_shader, basic_fragment_shader) # Default shader if None
        
        # Single batch storage with buffer type in the key
        self.batches: Dict[str, List[RenderObject]] = {}
        
        # Calculate vertex size: 3 (pos) + 3 (color) + 3 (normal) = 9 floats
        self.vertex_size = 9 * np.dtype(np.float32).itemsize  # Size in bytes
        
        # Create static buffers
        self.static_vertex_buffer = VertexBuffer(
            None,
            BufferType.Static,
            max_vertices * self.vertex_size
        )
        self.static_index_buffer = IndexBuffer(
            None,
            BufferType.Static,
            max_indices * np.dtype(np.uint32).itemsize
        )

        # Create dynamic buffers
        self.dynamic_vertex_buffer = VertexBuffer(
            None,
            BufferType.Dynamic,
            max_vertices * self.vertex_size
        )
        self.dynamic_index_buffer = IndexBuffer(
            None,
            BufferType.Dynamic,
            max_indices * np.dtype(np.uint32).itemsize
        )

        # Create VAO with both buffer sets
        self.vao = VertexArray()
        
        # Add dynamic buffers
        self.vao.add_buffer(self.dynamic_vertex_buffer, [
            { # Position attribute (location=0)
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

        # Add static buffers
        self.vao.add_buffer(self.static_vertex_buffer, [
            {
                'index': 3,
                'size': 3,
                'type': GL_FLOAT,
                'normalized': False,
                'stride': self.vertex_size,
                'offset': 0
            },
            {
                'index': 4,
                'size': 3,
                'type': GL_FLOAT,
                'normalized': False,
                'stride': self.vertex_size,
                'offset': 3 * np.dtype(np.float32).itemsize
            },
            {
                'index': 5,
                'size': 3,
                'type': GL_FLOAT,
                'normalized': False,
                'stride': self.vertex_size,
                'offset': 6 * np.dtype(np.float32).itemsize
            }
        ])
        
        # Statistics
        self.draw_calls = 0
        self.vertex_count = 0
        self.index_count = 0
        
        self.debug = False
    
    def clear(self):
        """Begin a new batch."""
        self.batches.clear()
        self.draw_calls = 0
        self.vertex_count = 0
        self.index_count = 0
    
    
    def _generate_batch_key(self, render_object: RenderObject):
        """Generate a batch key for a render object."""
        # Start with buffer type
        batch_key = f'{render_object.buffer_type}'
        # Add draw type
        batch_key += f'_{render_object.draw_type}'
        # Add line width to key if it's a line type
        if render_object.draw_type in (GL_LINES, GL_LINE_STRIP, GL_LINE_LOOP):
            batch_key += f'_lw{render_object.line_width}'
        # Add point size to key if it's a point type
        elif render_object.draw_type == GL_POINTS:
            batch_key += f'_ps{render_object.point_size}'
        return batch_key
    
    def add_object(self, render_object: RenderObject):
        """Submit a render object to the appropriate batch.
        
        Parameters
        ----------
        render_object : RenderObject
            The render object to batch
        """
        # Generate the key that determines which buffer the object goes in
        batch_key = self._generate_batch_key(render_object)
        # Create batch if it doesn't exist
        if batch_key not in self.batches:
            self.batches[batch_key] = []
        # Add object to batch
        self.batches[batch_key].append(render_object)
        # Mark static data as dirty if this was a static object
        if render_object.buffer_type == BufferType.Static:
            self.static_dirty = True
    
    def update_buffers(self):
        
        

        go throguh each of the batches
        if static:
            ...
        if dynamic:
        
        """Update buffers with batch data."""
        combined_vertices = []
        combined_indices = []
        vertex_offset = 0
        
        if self.debug:
            print("\nUpdating buffers:")
            print(f"Total batches: {len(self.batches)}")
            for key, objects in self.batches.items():
                print(f"Batch {key}: {len(objects)} objects")
        
        static_batch
        # Process static objects first, then dynamic
        for buffer_type in [BufferType.Static, BufferType.Dynamic]:
            # Skip static updates if not dirty
            if buffer_type == BufferType.Static and not self.static_dirty:
                print('Skipping static update for buffer')
                continue
                
            # Process objects of current buffer type
            for batch_key, objects in self.batches.items():
                if not batch_key.startswith(str(buffer_type)):
                    continue
                    
                for obj in objects:
                    if obj.vertex_data is None or obj.index_data is None:
                        continue
                    
                    # Get number of vertices (vertex_data shape should be (N, 9) where N is number of vertices)
                    vertex_data = obj.vertex_data.reshape(-1, 9)  # Reshape to ensure correct format
                    num_vertices = len(vertex_data)
                    
                    # Add vertices
                    combined_vertices.append(vertex_data)
                    
                    # Offset indices and add them
                    indices = obj.index_data + vertex_offset
                    combined_indices.append(indices)
                    
                    # Update offset for next object
                    vertex_offset += num_vertices
                    
                    if self.debug:
                        print(f"  Added object: vertices={num_vertices}, indices={len(indices)}")
        
        if not combined_vertices or not combined_indices:
            if self.debug:
                print("No data to update")
            return
        
        # Combine and update data
        vertex_data = np.concatenate(combined_vertices)
        index_data = np.concatenate(combined_indices)
        
        # Update statistics
        self.vertex_count = len(vertex_data)
        self.index_count = len(index_data)
        
        if self.debug:
            print(f"Final counts: vertices={self.vertex_count}, indices={self.index_count}")
        
        # Check buffer limits
        if self.vertex_count > self.max_vertices:
            raise RuntimeError(f"Vertex buffer overflow: {self.vertex_count} > {self.max_vertices}")
        if self.index_count > self.max_indices:
            raise RuntimeError(f"Index buffer overflow: {self.index_count} > {self.max_indices}")
        
        # Update static buffers
        self.static_vertex_buffer.update_data(vertex_data.astype(np.float32))
        self.static_index_buffer.update_data(index_data.astype(np.uint32))
        self.static_index_buffer.count = len(index_data)
        
        # Update dynamic buffers
        self.dynamic_vertex_buffer.update_data(vertex_data.astype(np.float32))
        self.dynamic_index_buffer.update_data(index_data.astype(np.uint32))
        self.dynamic_index_buffer.count = len(index_data)
        
        # Clear static dirty flag
        self.static_dirty = False
    
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
            print("\n=== Starting Render ===")
            print(f"Total batches: {len(self.batches)}")
        
        # Update buffers once for all batches
        self.update_buffers()
        if self.debug:
            print(f"After update_buffers: vertices={self.vertex_count}, indices={self.index_count}")
        
        # Bind VAO and shader
        self.vao.bind()
        self.shader.use()
        
        # Set shared uniforms
        self.shader.set_view_matrix(view_matrix)
        self.shader.set_projection_matrix(projection_matrix)
        self.shader.set_view_position(camera_pos)
        if lights:
            self.shader.set_light_uniforms(lights)
        
        # Reset draw calls counter
        self.draw_calls = 0
        index_offset = 0
        
        # Render static objects first, then dynamic
        for buffer_type in [BufferType.Static, BufferType.Dynamic]:
            for batch_key, objects in self.batches.items():
                if self.debug:
                    print(f"\nBatch: {batch_key} with {len(objects)} objects")
                if not batch_key.startswith(str(buffer_type)):
                    continue
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
                
        if self.debug:
            print(f"\nRender complete: {self.draw_calls} draw calls")
        self.vao.unbind()
    

    def get_stats(self):
        """Get comprehensive rendering statistics.
        
        Returns
        -------
        dict
            Dictionary containing various rendering statistics including:
            - Basic render stats (draw calls, vertex/index counts)
            - Buffer sizes and usage
            - Batch information
            - Memory usage
        """
        # Calculate batch stats
        batch_stats = {}
        total_objects = 0
        for batch_key, objects in self.batches.items():
            batch_objects = len(objects)
            total_objects += batch_objects
            
            # Parse batch key for type info
            if '_lw' in batch_key:
                draw_type, line_width = batch_key.split('_lw')
                batch_stats[batch_key] = {
                    'draw_type': draw_type,
                    'line_width': float(line_width),
                    'object_count': batch_objects
                }
            elif '_ps' in batch_key:
                draw_type, point_size = batch_key.split('_ps')
                batch_stats[batch_key] = {
                    'draw_type': draw_type,
                    'point_size': float(point_size),
                    'object_count': batch_objects
                }
            else:
                batch_stats[batch_key] = {
                    'draw_type': batch_key,
                    'object_count': batch_objects
                }

        # Calculate buffer usage
        vertex_buffer_size = self.max_vertices * self.vertex_size
        vertex_buffer_used = self.vertex_count * self.vertex_size
        vertex_buffer_usage = (vertex_buffer_used / vertex_buffer_size) * 100 if vertex_buffer_size > 0 else 0

        index_buffer_size = self.max_indices * np.dtype(np.uint32).itemsize
        index_buffer_used = self.index_count * np.dtype(np.uint32).itemsize
        index_buffer_usage = (index_buffer_used / index_buffer_size) * 100 if index_buffer_size > 0 else 0

        return {
            # Render statistics
            'draw_calls': self.draw_calls,
            'vertex_count': self.vertex_count,
            'index_count': self.index_count,
            'total_objects': total_objects,
            
            # Buffer information
            'vertex_buffer': {
                'size_bytes': vertex_buffer_size,
                'used_bytes': vertex_buffer_used,
                'usage_percent': vertex_buffer_usage,
                'max_vertices': self.max_vertices,
                'current_vertices': self.vertex_count
            },
            'index_buffer': {
                'size_bytes': index_buffer_size,
                'used_bytes': index_buffer_used,
                'usage_percent': index_buffer_usage,
                'max_indices': self.max_indices,
                'current_indices': self.index_count
            },
            
            # Memory usage
            'total_buffer_size_mb': (vertex_buffer_size + index_buffer_size) / (1024 * 1024),
            'total_buffer_used_mb': (vertex_buffer_used + index_buffer_used) / (1024 * 1024),
            
            # Batch information
            'batch_count': len(self.batches),
            'batches': batch_stats,
            
            # Vertex format
            'vertex_size_bytes': self.vertex_size,
            'vertex_attributes': {
                'position': {'size': 3, 'type': 'float', 'offset': 0},
                'color': {'size': 3, 'type': 'float', 'offset': 3 * 4},  # 4 bytes per float
                'normal': {'size': 3, 'type': 'float', 'offset': 6 * 4}
            }
        }

