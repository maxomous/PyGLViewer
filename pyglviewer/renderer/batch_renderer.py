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
        
        
        self.objects = {}
        
        # Batch storage - simple list of objects per batch key
        # self.batches: Dict[str, List[Object]] = {}
        
        # Create initial buffers
        self.vertex_buffer, self.index_buffer, self.vao = self._create_buffers()
        
        # Statistics
        self.draw_calls = 0
        
        
        self.current_vertex = 0
        self.current_index = 0
        self.dangling = {'vertices': [], 'indices': []}
        
        # # Flag to track if buffer needs updating
        # self.needs_update = True  # TODO: Add this
        
        
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
            if self.vertex_count > 0: # TODO vertex_count NO LONGER EXISTS
                old_vertex_buffer.bind()
                glCopyBufferSubData(
                    GL_ARRAY_BUFFER, GL_ARRAY_BUFFER,
                    0, 0,
                    self.vertex_count * Vertex.vertex_size()# TODO vertex_count NO LONGER EXISTS
                )
                
            if self.index_count > 0: # TODO index_count NO LONGER EXISTS
                old_index_buffer.bind()
                glCopyBufferSubData(
                    GL_ELEMENT_ARRAY_BUFFER, GL_ELEMENT_ARRAY_BUFFER,
                    0, 0,
                    self.index_count * np.dtype(np.uint32).itemsize # TODO index_count NO LONGER EXISTS
                )
                
        finally:
            # Clean up old buffers
            old_vertex_buffer.shutdown()
            old_index_buffer.shutdown()
            old_vao.shutdown()
    
    # def clear(self):
    #     """Clear the buffer data."""
    #     # print(f"Clearing buffer: {self.buffer_type}")
    #     # if not self.needs_update:
    #     #     return
    #     self.batches.clear()
    #     self.draw_calls = 0
    #     self.vertex_count = 0 # TODO vertex_count NO LONGER EXISTS
    #     self.index_count = 0 # TODO index_count NO LONGER EXISTS
    
    #     # self.current_vertex = 0
    #     # self.current_index = 0
    #     # self.dangling = {'vertices': [], 'indices': []}
    


# class RenderBuffer:
#     objects = []
#     def add_object(object):
#         self.objects.append(object)

#     def set_shape(object, shape):
#         glBufferSubData

        
    # *** NEW ONE *** 
    def add_object(self, name, object: Object):
        if name in self.objects:
            raise ValueError(f"Object '{name}' already exists")
        self.objects[name] = object
    
    def remove_object(self, name):
        object = self.objects[name]
        self._clear_object_shapes(object)
        # TOOD: is there anything else to clear before the deleting an object?
        del self.objects[name]
    
    
    def _free_shape_data(self, object):
        '''Make list of redundant vertices and indices we can later reuse'''
        for shape_data in object.shape_data:
            shape = shape_data['shape']
            if shape.vertex_data is None or shape.indices is None:
                continue
            self.dangling['vertices'].append({'offset': shape_data['vertex_offset'], 'size': shape.vertex_count})
            self.dangling['indices'].append({'offset': shape_data['index_offset'], 'size': shape.index_count})
            
        # Clear the old shape data
        object.set_shape_data([])
        
    def _resize_shape_data(self, object: Object, shapes: list[Shape]):
        """
        Resize the object's shape list to match the provided shapes.
        Initializes vertex and index offsets for each shape in the batch buffer.
        """
        # Clear the old shape data
        self._free_shape_data(object)
        shape_data = []
        # Add shapes to object
        for shape in shapes:
            if shape.vertex_data is None or shape.indices is None:
                continue
            
            # Resize buffer if needed
            if self.current_vertex + shape.vertex_count > self.max_vertices or self.current_index + shape.index_count > self.max_indices:
                raise ValueError(f'Buffer is too small')
            # TODO: RESIZE BUFFER
            #     # Calculate new sizes with growth factor
            #     new_vertex_count = max(self.max_vertices, int(vertex_count * self.growth_factor))
            #     new_index_count = max(self.max_indices, int(index_count * self.growth_factor))
            #     self._resize_buffers(new_vertex_count, new_index_count)
            
            
            shape_data.append({
                'shape': shape, 
                'vertex_offset': self.current_vertex,   # TODO: Reuse self.dangling if possible
                'index_offset': self.current_index
            })

            # Resize the offsets
            self.current_vertex += shape.vertex_count
            self.current_index += shape.index_count

        object.set_shape_data(shape_data)



    def set_object_shapes(self, name, shapes: Shape | list[Shape]):
        """Add shape to the object, and update the gpu data"""
        
        if name not in self.objects:
            raise ValueError('Object does not exist in buffer')
        object = self.objects[name]
        # Make sure we have a list of Shapes
        if not isinstance(shapes, list):
            shapes = [shapes]
        
        # Calculate number of vertices / indices in the current and new shapes
        current_vertex_count = sum(shape_data['shape'].vertex_count for shape_data in object.shape_data)
        current_index_count = sum(shape_data['shape'].index_count for shape_data in object.shape_data)
        new_vertex_count = sum(shape.vertex_count for shape in shapes)
        new_index_count = sum(shape.index_count for shape in shapes)
        
        # print(f'current_vertex_count: {current_vertex_count}')
        # print(f'current_index_count: {current_index_count}')
        # print(f'new_vertex_count: {new_vertex_count}')
        # print(f'new_index_count: {new_index_count}')
        
        if new_vertex_count == 0 or new_index_count == 0:
            return
        
        # Compare number of vertices / indices and resize if needed
        if (new_vertex_count > current_vertex_count) or (new_index_count > current_index_count): 
            print(f'Resizing object shape data')
            # Set vertices & indices offsets to back of buffer
            self._resize_shape_data(object, shapes)

        # print(f'len(shapes): {len(shapes)}')
        # print(f'len(shape_data): {len(object.shape_data)}')
        
        if len(shapes) != len(object.shape_data):
            raise ValueError(f'Length of shapes {len(shapes)} does not match length of shape_data {len(object.shape_data)}')
        
        # Set vertex & index data
        for i, shape in enumerate(shapes):
            vertex_offset = object.shape_data[i]['vertex_offset']
            index_offset = object.shape_data[i]['index_offset']
            
            if shape.vertex_data is None or shape.indices is None:
                continue
            vertex_data = shape.vertex_data.reshape(-1, 9).astype(np.float32)
            index_data = (shape.indices + vertex_offset).astype(np.uint32)
            # Update buffers with new data (using glBufferSubData)
            self.vertex_buffer.update_data(vertex_data, offset=vertex_offset * Vertex.vertex_size())
            self.index_buffer.update_data(index_data, offset=index_offset * Vertex.index_size())
                    
        
        
    # def add_object_to_buffer(self, object: Object):
    #     """Add object to appropriate batch."""
        
    #     # Create batch key based on draw type
    #     batch_key = f"draw_type_{object.draw_type}"
    #     # Add shader id to key
    #     batch_key += f"_shader_{object.shader.program}"
    #     # Add line width to key if it's a line type
    #     if object.draw_type in (GL_LINES, GL_LINE_STRIP, GL_LINE_LOOP):
    #         batch_key += f"_line_width_{object._line_width}"
    #     # Add point size to key if it's a point type
    #     elif object.draw_type == GL_POINTS:
    #         batch_key += f"_point_size_{object._point_size}"
    #         batch_key += f"_point_shape_{object._point_shape}"
    #     # Add new batch if it doesn't exist
    #     if batch_key not in self.batches:
    #         self.batches[batch_key] = []
    #     # print(f'Batch key: {batch_key}')
    #     # Add object to batch
    #     self.batches[batch_key].append(object)
    #     # self.needs_update = True
    
    
    
    #             draw_type
    #             shader
    #             _vertex_data
    #             _index_data
                
    #             _line_width
    #             _point_size
    #             _point_shape
    #             model_matrix
    #             _alpha
    
    
    # def update_buffers(self):
    #     """Update buffer data."""
    #     # if not self.needs_update:
    #     #     return
    #     combined_vertices = []
    #     combined_indices = []
    #     vertex_offset = 0
        
    #     # First pass: collect all vertex and index data
    #     for batch_data in self.batches.values():
    #         # print(f'n objects: {len(batch_data)}')
    #         for obj in batch_data:
    #             if obj._vertex_data is None or obj._index_data is None:
    #                 continue
                    
    #             vertex_data = obj._vertex_data.reshape(-1, 9)
    #             num_vertices = len(vertex_data)
                
    #             combined_vertices.append(vertex_data)
    #             combined_indices.append(obj._index_data + vertex_offset)
    #             vertex_offset += num_vertices
        
    #     if not combined_vertices or not combined_indices:
    #         return
            
    #     # Combine all data
    #     vertex_data = np.concatenate(combined_vertices)
    #     index_data = np.concatenate(combined_indices)
        
    #     # Check if we need to resize buffers
    #     vertex_count = len(vertex_data)
    #     index_count = len(index_data)
        
    #     # print(f"Vertex count: {vertex_count}, Index count: {index_count}")
    #     if vertex_count > self.max_vertices or index_count > self.max_indices:
    #         # Calculate new sizes with growth factor
    #         new_vertex_count = max(self.max_vertices, int(vertex_count * self.growth_factor))
    #         new_index_count = max(self.max_indices, int(index_count * self.growth_factor))
    #         self._resize_buffers(new_vertex_count, new_index_count)
        
    #     # Update buffers with new data
    #     self.vertex_buffer.update_data(vertex_data.astype(np.float32))
    #     self.index_buffer.update_data(index_data.astype(np.uint32))
        
    #     # Update statistics
    #     self.vertex_count = vertex_count # TODO vertex_count NO LONGER EXISTS
    #     self.index_count = index_count # TODO index_count NO LONGER EXISTS
    #     # self.needs_update = False
    
    
    def render_buffer(self, view_matrix: np.ndarray, projection_matrix: np.ndarray, camera_pos: np.ndarray, lights: Optional[List] = None):
        """Render objects from specified buffer."""
        # Skip if no objects to render
        if not self.objects:
            return
        
        # Group shapes by (shader, draw_type)
        batches = defaultdict(list)
        for obj in self.objects.values():
            for shape_data in obj.shape_data:
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
                    vertex_offset = shape_data["vertex_offset"]
                    index_offset = shape_data["index_offset"]
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
        
    
    # def render_buffer(self, view_matrix: np.ndarray, projection_matrix: np.ndarray, camera_pos: np.ndarray, lights: Optional[List] = None):
    #     """Render objects from specified buffer."""
    #     # Skip if no objects to render
    #     if not self.objects:
    #         return
        
    #     # Bind VAO and shader
    #     self.vao.bind()
    #     self.vertex_buffer.bind()
    #     self.index_buffer.bind()
        
    #     # Draw each batch separately
    #     index_offset = 0        
    #     self.draw_calls = 0

    #     current_shader = None
        
    #     try:
    #         for batch_key, objects in self.batches.items():
    #             if not objects or len(objects) == 0:
    #                 continue
                
    #             # Get properties from first object in batch
    #             first_obj = objects[0]
    #             draw_type = first_obj.draw_type # TODO: Rename primitive
    #             shader = first_obj.shader
                
    #             # Only set up shader if it's different from the current one
    #             if shader != current_shader:
    #                 shader.use()
    #                 shader.set_view_matrix(view_matrix)
    #                 shader.set_projection_matrix(projection_matrix)
    #                 shader.set_view_position(camera_pos)
    #                 if lights:
    #                     shader.set_light_uniforms(lights)
    #                 current_shader = shader
                           
    #             # Set line width or point properties if needed
    #             if draw_type in (GL_LINES, GL_LINE_STRIP, GL_LINE_LOOP):
    #                 glLineWidth(first_obj._line_width)
    #             elif draw_type == GL_POINTS:
    #                 glPointSize(first_obj._point_size)
    #                 current_shader.set_point_shape(first_obj._point_shape)
                    
    #             # Draw each object in the batch
    #             for obj in objects:
    #                 if obj._vertex_data is None or obj._index_data is None:
    #                     continue
    #                 # Set model matrix for this object
    #                 current_shader.set_model_matrix(obj.model_matrix)
    #                 # Set alpha for transparency
    #                 current_shader.set_alpha(obj._alpha)
    #                 # Calculate number of indices for this object
    #                 num_indices = len(obj._index_data)
    #                 # Draw the object
    #                 glDrawElements(
    #                     draw_type,
    #                     num_indices,
    #                     GL_UNSIGNED_INT,
    #                     ctypes.c_void_p(index_offset * Vertex.index_size())  # 4 bytes per uint32
    #                 )
                    
    #                 index_offset += num_indices
    #                 self.draw_calls += 1
                    
    #     finally:
    #         # Cleanup state
    #         self.vao.unbind()
    #         self.vertex_buffer.unbind()
    #         self.index_buffer.unbind()
    #         glUseProgram(0)
        
    
    def get_stats(self):
        """Get key rendering statistics."""
        # Calculate batch stats - batches contains lists directly, not dictionaries
        total_objects = len(self.objects)
        total_shapes = sum(len(object.shape_data) for object in self.objects.values())
        
        # # Calculate buffer usage percentages
        # vertex_buffer_usage = (self.vertex_count / self.max_vertices * 100) if self.max_vertices > 0 else 0 # TODO vertex_count NO LONGER EXISTS
        # index_buffer_usage = (self.index_count / self.max_indices * 100) if self.max_indices > 0 else 0 # TODO index_count NO LONGER EXISTS
        
        return {
            'buffer_type': str(self.buffer_type),
            'draw_calls': self.draw_calls,
            'total_objects': total_objects,
            'total_shapes': total_shapes,
            # 'batch_count': len(self.batches),
            # 'buffer_usage': {
            #     'vertices': f"{self.vertex_count}/{self.max_vertices} ({vertex_buffer_usage:.1f}%)",
            #     'indices': f"{self.index_count}/{self.max_indices} ({index_buffer_usage:.1f}%)"
            # }
        }
