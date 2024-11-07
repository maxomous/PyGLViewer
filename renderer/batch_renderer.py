from typing import Dict, List, Optional
import numpy as np
from OpenGL.GL import *
from renderer.objects import BufferType, VertexBuffer, IndexBuffer, VertexArray, RenderObject
from renderer.shaders import Shader, basic_vertex_shader, basic_fragment_shader  
# TODO:
#     This should be from Vertex
#         # Create VAO with standard layout
#         self.vao = VertexArray()
#         self.vao.add_buffer(self.vertex_buffer, [
#             {'index': 0, 'size': 3, 'type': GL_FLOAT, 'normalized': False, 
#              'stride': vertex_size, 'offset': 0},  # position
#             {'index': 1, 'size': 3, 'type': GL_FLOAT, 'normalized': False,
#              'stride': vertex_size, 'offset': 12},  # color
#             {'index': 2, 'size': 3, 'type': GL_FLOAT, 'normalized': False,
#              'stride': vertex_size, 'offset': 24}   # normal
#         ])


# these shouold be inside batch renderer

#             # Get shader and draw type from first object
#             shader = objects[0].shader
#             draw_type = objects[0].draw_type


# replace 36
#                     glDrawArrays(draw_type, 0, obj.vb.size // 36)  # 36 = 9 floats * 4 bytes
#   
#   interleave_vertices() replace with vertices?
# any shutdown functions
    
    
    
#     More recent TODOS:


# find: VertexBuffer(


#         # self.vb.update_data(data, offset)
#         # self.ib.update_data(data, offset)


# update RenderObject( to remove shader param


#     # TODO: Do we need offset??    
#     def set_vertex_data(self, data, offset=0):



# was         now
# self.vb == batch_renderer.vertex_buffer  # Shared vertex buffer for batch
# self.ib == batch_renderer.index_buffer  # Shared index buffer for batch
# self.va == batch_renderer.vao  # Shared vertex array for attribute layout
      
            
# check all of these are being used:
# class RenderObject:
#         self.vertex_data = vertex_data
#         self.index_data = index_data
#         self.draw_type = draw_type
#         self.line_width = line_width
#         self.point_size = point_size
#         self.model_matrix = np.identity(4, dtype=np.float32)
    
    
    
    
    
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
        
        # Buffer for batched data
        vertex_size = (3 + 3 + 3) * 4  # pos(3) + color(3) + normal(3) in float32
        self.vertex_buffer = VertexBuffer(
            None,
            BufferType.Dynamic,
            max_vertices * vertex_size
        )
        
        self.index_buffer = IndexBuffer(
            None,
            BufferType.Dynamic,
            max_indices * 4  # uint32 indices
        )
        
        # Create VAO with standard layout
        self.vao = VertexArray()
        self.vao.add_buffer(self.vertex_buffer, [
            {'index': 0, 'size': 3, 'type': GL_FLOAT, 'normalized': False, 'stride': vertex_size, 'offset': 0},  # position
            {'index': 1, 'size': 3, 'type': GL_FLOAT, 'normalized': False, 'stride': vertex_size, 'offset': 12},  # color
            {'index': 2, 'size': 3, 'type': GL_FLOAT, 'normalized': False, 'stride': vertex_size, 'offset': 24}   # normal
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
        # Create batch key based on shader and draw type
        batch_key = f"{render_object.shader.program}_{render_object.draw_type}"
        
        if batch_key not in self.batches:
            self.batches[batch_key] = []
            
        self.batches[batch_key].append(render_object)
    
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
        for batch_key, objects in self.batches.items():
            if not objects:
                continue
            
            # Bind shader and set shared uniforms
            self.shader.use()
            self.shader.set_view_matrix(view_matrix)
            self.shader.set_projection_matrix(projection_matrix)
            self.shader.set_view_position(camera_pos)
            
            if lights:
                self.shader.set_light_uniforms(lights)
            
            # Bind VAO
            self.vao.bind()
            
            # Combine vertex and index data for this batch
            combined_vertices = []
            combined_indices = []
            base_vertex = 0
            
            for obj in objects:
                if obj.vertex_data is None:
                    continue
                    WE DONT WANT TO DO TRANFORM IN SHADER FOR BATCH RENDERING
                # Transform vertices by model matrix
                vertices = obj.vertex_data.reshape(-1, 9)  # Reshape to (N, 9) for pos,color,normal
                positions = np.column_stack([vertices[:, 0:3], np.ones(len(vertices))])
                transformed_positions = (positions @ obj.model_matrix)[:, 0:3]
                vertices[:, 0:3] = transformed_positions
                
                # Add vertices and indices to batch
                combined_vertices.append(vertices.flatten())
                combined_indices.extend((obj.index_data + base_vertex) if obj.index_data is not None else [])
                base_vertex += len(obj.vertex_data.reshape(-1, 9))
            
            if not combined_vertices or not combined_indices:
                continue
                
            # TODO: handle none on first go? 
                
            # Update batch buffers
            if combined_vertices:
                self.vertex_buffer.update_data(np.concatenate(combined_vertices))
            if combined_indices:
                self.index_buffer.update_data(np.concatenate(combined_indices))
        
            
            # Render each object in batch
            for obj in objects:
                self.shader.set_model_matrix(obj.model_matrix)
                
                # Set line width or point size if needed
                if obj.draw_type in (GL_LINES, GL_LINE_STRIP, GL_LINE_LOOP):
                    glLineWidth(obj.line_width)
                elif obj.draw_type == GL_POINTS:
                    glPointSize(obj.point_size)
                sd
                # Draw the object
                if obj.ib is not None:
                    glDrawElements(obj.draw_type, obj.ib.count, GL_UNSIGNED_INT, None)
                else:
                    # Assuming triangles if no index buffer
                    glDrawArrays(obj.draw_type, 0, obj.vb.size // 36)  # 36 = 9 floats * 4 bytes
                
                self.draw_calls += 1
            
            self.vao.unbind()
    