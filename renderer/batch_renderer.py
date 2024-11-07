from typing import Dict, List, Optional
import numpy as np
from OpenGL.GL import *
from renderer.objects import BufferType, VertexBuffer, IndexBuffer, VertexArray, RenderObject
from renderer.shaders import Shader, basic_vertex_shader, basic_fragment_shader  

    

    #     # TODO: handle buffer_type for static and stream
    # def add_object_base(self, vertices, indices, buffer_type, draw_type=GL_TRIANGLES, line_width=None, point_size=None):
    
    
    
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
        
        # Batch storage
        self.batches: Dict[str, List[RenderObject]] = {}
        
        # Calculate vertex size: 3 (pos) + 3 (color) + 3 (normal) = 9 floats
        self.vertex_size = 9 * np.dtype(np.float32).itemsize  # Size in bytes
        
        # Create buffers with initial size
        self.vertex_buffer = VertexBuffer(
            None,
            BufferType.Dynamic,
            max_vertices * self.vertex_size
        )
        
        self.index_buffer = IndexBuffer(
            None,
            BufferType.Dynamic,
            max_indices * np.dtype(np.uint32).itemsize
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
        
        # Batch statistics
        self.draw_calls = 0
        self.vertex_count = 0
        self.index_count = 0
    
    def clear(self):
        """Begin a new batch."""
        self.batches.clear()
        self.draw_calls = 0
        self.vertex_count = 0
        self.index_count = 0
    
    def add_object(self, render_object: RenderObject):
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
        """Update the batch buffers with the combined vertex and index data."""
        combined_vertices = []
        combined_indices = []
        vertex_offset = 0
        
        # First pass: collect all vertex and index data
        for objects in self.batches.values():
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
        
        if not combined_vertices or not combined_indices:
            return
            
        # Combine all data
        vertex_data = np.concatenate(combined_vertices)
        index_data = np.concatenate(combined_indices)
        
        # Update statistics
        self.vertex_count = len(vertex_data)
        self.index_count = len(index_data)
        
        # Update buffers
        self.vertex_buffer.update_data(vertex_data.astype(np.float32))
        self.index_buffer.update_data(index_data.astype(np.uint32))
        self.index_buffer.count = len(index_data)
        
        

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
            
        # Update buffers once for all batches
        self.update_buffers()
        
        # Bind VAO and shader
        self.vao.bind()
        self.shader.use()
        
        # Set shared uniforms
        self.shader.set_view_matrix(view_matrix)
        self.shader.set_projection_matrix(projection_matrix)
        self.shader.set_view_position(camera_pos)
        if lights:
            self.shader.set_light_uniforms(lights)
            
        # Draw each batch separately
        index_offset = 0
        for batch_key, objects in self.batches.items():
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
            for obj in objects:
                # Set model matrix for this object
                self.shader.set_model_matrix(obj.model_matrix)
                
                # Calculate number of indices for this object
                num_indices = len(obj.index_data)
                
                # Draw the object
                glDrawElements(
                    draw_type,
                    num_indices,
                    GL_UNSIGNED_INT,
                    ctypes.c_void_p(index_offset * 4)  # 4 bytes per uint32
                )
                
                index_offset += num_indices
                self.draw_calls += 1
                
        self.vao.unbind()
    

    def get_stats(self):
        """Get rendering statistics."""
        return {
            'draw_calls': self.draw_calls,
            'vertex_count': self.vertex_count,
            'index_count': self.index_count
        }

