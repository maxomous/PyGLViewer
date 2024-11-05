from OpenGL.GL import *
import numpy as np
from typing import List, Dict, Any
from dataclasses import dataclass, field
from enum import Enum
from gl.objects import VertexBuffer, IndexBuffer, VertexArray, BufferType
from utils.transform import Transform
from core.geometry import GeometryData, Vertex
import ctypes

class BatchType(Enum):
    """Defines different types of batches for different primitive types"""
    TRIANGLES = GL_TRIANGLES
    LINES = GL_LINES
    POINTS = GL_POINTS
    LINE_STRIP = GL_LINE_STRIP
    LINE_LOOP = GL_LINE_LOOP
    TRIANGLE_FAN = GL_TRIANGLE_FAN
    TRIANGLE_STRIP = GL_TRIANGLE_STRIP

@dataclass
class Batch:
    """Represents a single batch of geometry"""
    draw_type: int
    shader: Any
    vertices: np.ndarray
    indices: np.ndarray
    line_width: float = 1.0
    point_size: float = 1.0
    transform: np.ndarray = None

class BatchStats:
    draw_calls: int = 0
    vertex_count: int = 0
    index_count: int = 0
    batches_merged: int = 0
    buffer_updates: int = 0
    shader_switches: int = 0
    state_changes: int = 0
    
    def reset(self):
        """Reset all stats to zero."""
        self.draw_calls = 0
        self.vertex_count = 0
        self.index_count = 0
        self.batches_merged = 0
        self.buffer_updates = 0
        self.shader_switches = 0
        self.state_changes = 0
    
    def get_detailed_stats(self):
        """Get detailed performance metrics."""
        return {
            "Draw Calls": self.draw_calls,
            "Vertices": self.vertex_count,
            "Indices": self.index_count,
            "Batches Merged": self.batches_merged,
            "Buffer Updates": self.buffer_updates,
            "Shader Switches": self.shader_switches,
            "State Changes": self.state_changes,
            "Vertices/Draw": f"{self.vertex_count / max(1, self.draw_calls):.1f}",
            "Indices/Draw": f"{self.index_count / max(1, self.draw_calls):.1f}",
            "Merge Ratio": f"{self.batches_merged / max(1, self.draw_calls):.2f}"
        }

class BufferPool:
    def __init__(self, max_buffers=4):
        self.max_buffers = max_buffers
        self.available_buffers = []
        self.in_use_buffers = []

    def get_buffer(self, size):
        """Get a buffer from the pool or create a new one."""
        if self.available_buffers:
            buffer = self.available_buffers.pop()
            if buffer.size >= size:
                self.in_use_buffers.append(buffer)
                return buffer

        # Create new buffer if none available or too small
        buffer = np.zeros(size, dtype=np.float32)
        self.in_use_buffers.append(buffer)
        return buffer

    def return_buffer(self, buffer):
        """Return a buffer to the pool."""
        if buffer in self.in_use_buffers:
            self.in_use_buffers.remove(buffer)
            if len(self.available_buffers) < self.max_buffers:
                self.available_buffers.append(buffer)

class BatchRenderer:
    """
    Batches multiple geometries into single draw calls based on their material and primitive type.
    """
    MAX_VERTICES = 100000
    MAX_INDICES = 100000
    VERTEX_SIZE = 9  # 3 pos + 3 color + 3 normal

    # Size constants
    FLOAT_SIZE = 4    # 4 bytes per float
    UINT32_SIZE = 4   # 4 bytes per unsigned int

    def __init__(self):
        self.stats = BatchStats()
        
        # Create buffers with correct sizes
        vertex_buffer_size = self.MAX_VERTICES * self.VERTEX_SIZE * 4  # 4 bytes per float
        index_buffer_size = self.MAX_INDICES * 4  # 4 bytes per uint32
        
        self.vertex_buffer = VertexBuffer(None, BufferType.Dynamic, vertex_buffer_size)
        self.index_buffer = IndexBuffer(None, BufferType.Dynamic, index_buffer_size)
        self.vertex_array = VertexArray()
        self.vertex_array.add_buffer(self.vertex_buffer, Vertex.LAYOUT)
        
        # Initialize batches dictionary
        self.batches = []
        
        # Matrices
        self.view_matrix = np.identity(4, dtype=np.float32)
        self.projection_matrix = np.identity(4, dtype=np.float32)
        self.camera_position = np.zeros(3, dtype=np.float32)

        # Add buffer pools
        self.vertex_pool = BufferPool()
        self.index_pool = BufferPool()

    def begin(self):
        """Begin a new frame."""
        self.batches.clear()
        self.stats = BatchStats()

    def submit(self, geometry_data, shader, draw_type, transform=None, line_width=1.0, point_size=1.0):
        """Submit geometry to batch."""
        if geometry_data is None or shader is None:
            return True

        vertices = geometry_data.get_vertex_data()
        indices = geometry_data.get_index_data()

        if len(vertices) == 0 or len(indices) == 0:
            return True

        # Get buffers from pool
        vertex_buffer = self.vertex_pool.get_buffer(len(vertices))
        index_buffer = self.index_pool.get_buffer(len(indices))
        
        # Copy data to pooled buffers
        vertex_buffer[:len(vertices)] = vertices
        index_buffer[:len(indices)] = indices

        # For line primitives, don't merge to avoid unwanted connections
        if draw_type in (GL_LINES, GL_LINE_STRIP, GL_LINE_LOOP):
            batch = Batch(
                draw_type=draw_type,
                shader=shader,
                vertices=vertex_buffer[:len(vertices)].astype(np.float32),
                indices=index_buffer[:len(indices)].astype(np.uint32),
                line_width=line_width,
                point_size=point_size,
                transform=transform
            )
            self.batches.append(batch)
            self.stats.vertex_count += len(vertices) // self.VERTEX_SIZE
            self.stats.index_count += len(indices)
            return True

        # Try to find compatible batch for non-line primitives
        for batch in self.batches:
            if (batch.shader == shader and 
                batch.draw_type == draw_type and 
                batch.draw_type not in (GL_LINES, GL_LINE_STRIP, GL_LINE_LOOP) and
                batch.line_width == line_width and 
                batch.point_size == point_size and 
                np.array_equal(batch.transform, transform)):
                
                # Check if we can merge (within buffer limits)
                if (len(batch.vertices) + len(vertices) <= self.MAX_VERTICES * self.VERTEX_SIZE and
                    len(batch.indices) + len(indices) <= self.MAX_INDICES):
                    
                    # Calculate vertex offset for indices
                    vertex_offset = len(batch.vertices) // self.VERTEX_SIZE
                    
                    # Get new buffers from pool for merged data
                    new_vertex_buffer = self.vertex_pool.get_buffer(len(batch.vertices) + len(vertices))
                    new_index_buffer = self.vertex_pool.get_buffer(len(batch.indices) + len(indices))
                    
                    # Merge vertices and indices
                    new_vertex_buffer[:len(batch.vertices)] = batch.vertices
                    new_vertex_buffer[len(batch.vertices):] = vertices
                    
                    new_index_buffer[:len(batch.indices)] = batch.indices
                    new_index_buffer[len(batch.indices):] = indices + vertex_offset
                    
                    # Return old buffers to pool
                    self.vertex_pool.return_buffer(batch.vertices)
                    self.index_pool.return_buffer(batch.indices)
                    
                    # Update batch with new buffers
                    batch.vertices = new_vertex_buffer
                    batch.indices = new_index_buffer
                    
                    # Update stats
                    self.stats.vertex_count += len(vertices) // self.VERTEX_SIZE
                    self.stats.index_count += len(indices)
                    self.stats.batches_merged += 1
                    
                    return True

    def flush(self):
        """Render all batches."""
        if not self.batches:
            return

        # Enable depth testing
        glEnable(GL_DEPTH_TEST)
        glDepthFunc(GL_LESS)
        
        # Sort batches by shader and draw type to minimize state changes
        self.batches.sort(key=lambda b: (id(b.shader), b.draw_type))
        
        current_shader = None
        current_draw_type = None
        current_line_width = 1.0
        current_point_size = 1.0

        self.vertex_array.bind()

        for batch in self.batches:
            try:
                # Track buffer updates
                self.stats.buffer_updates += 2
                self.vertex_buffer.update_data(batch.vertices)
                self.index_buffer.update_data(batch.indices)
                
                # Only change shader if different
                if batch.shader is not current_shader:
                    self.stats.shader_switches += 1
                    batch.shader.use()
                    # Set common uniforms that don't change per batch
                    batch.shader.set_view_matrix(self.view_matrix)
                    batch.shader.set_projection_matrix(self.projection_matrix)
                    batch.shader.set_view_position(self.camera_position)
                    current_shader = batch.shader
                
                # Only change draw type state if different
                if batch.draw_type != current_draw_type:
                    self.stats.state_changes += 1
                    current_draw_type = batch.draw_type
                    
                    # Update line width/point size only when draw type changes
                    if current_draw_type in (GL_LINES, GL_LINE_STRIP, GL_LINE_LOOP):
                        if batch.line_width != current_line_width:
                            glLineWidth(batch.line_width)
                            current_line_width = batch.line_width
                    elif current_draw_type == GL_POINTS:
                        if batch.point_size != current_point_size:
                            glPointSize(batch.point_size)
                            current_point_size = batch.point_size
                
                # Set transform
                if batch.transform is not None:
                    batch.shader.set_model_matrix(batch.transform)
                else:
                    batch.shader.set_model_matrix(np.identity(4, dtype=np.float32))
                
                # Draw
                glDrawElements(
                    batch.draw_type,
                    len(batch.indices),
                    GL_UNSIGNED_INT,
                    None
                )
                
                self.stats.draw_calls += 1

            except Exception as e:
                print(f"Error rendering batch: {str(e)}")
                continue

        # Reset state
        if current_line_width != 1.0:
            glLineWidth(1.0)
        if current_point_size != 1.0:
            glPointSize(1.0)
        glDisable(GL_DEPTH_TEST)
        
        # Clear batches
        self.batches.clear()

    def __del__(self):
        """Clean up GPU resources."""
        if hasattr(self, 'vertex_buffer'):
            del self.vertex_buffer
        if hasattr(self, 'index_buffer'):
            del self.index_buffer
        if hasattr(self, 'vertex_array'):
            del self.vertex_array
        if hasattr(self, 'vertex_pool'):
            for buffer in self.vertex_pool.available_buffers + self.vertex_pool.in_use_buffers:
                del buffer
        if hasattr(self, 'index_pool'):
            for buffer in self.index_pool.available_buffers + self.index_pool.in_use_buffers:
                del buffer

    def get_stats_string(self):
        """Get a formatted string of the current batch statistics."""
        stats = self.stats
        
        # Calculate derived metrics
        vertices_per_draw = stats.vertex_count / max(1, stats.draw_calls)
        indices_per_draw = stats.index_count / max(1, stats.draw_calls)
        merge_ratio = stats.batches_merged / max(1, stats.draw_calls + stats.batches_merged)
        
        return (
            f"Rendering Statistics:\n"
            f"-------------------\n"
            f"Draw Calls: {stats.draw_calls}\n"
            f"Vertices: {stats.vertex_count:,}\n"
            f"Indices: {stats.index_count:,}\n"
            f"Batches Merged: {stats.batches_merged}\n"
            f"Merge Ratio: {merge_ratio:.2%}\n"
            f"\nEfficiency Metrics:\n"
            f"-------------------\n"
            f"Vertices/Draw: {vertices_per_draw:.1f}\n"
            f"Indices/Draw: {indices_per_draw:.1f}\n"
            f"Memory Used: {(stats.vertex_count * self.VERTEX_SIZE * 4 + stats.index_count * 4) / 1024:.1f}KB\n"
            f"Buffer Capacity: {self.MAX_VERTICES:,} vertices, {self.MAX_INDICES:,} indices"
        )