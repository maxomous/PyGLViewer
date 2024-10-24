import numpy as np
from OpenGL.GL import *

class Geometry:
    
    @staticmethod
    def create_grid(position, size, increment, color):
        ''' Returns vertices and indices for a 3D grid '''
        vertices, indices = [], []
        index = 0
        num_lines = int(size / increment) + 1
        
        for i in range(num_lines):
            x = i * increment - size/2 + position[0]
            vertices.extend([x, position[1] - size/2, position[2], *color, 0, 0, 1])
            vertices.extend([x, position[1] + size/2, position[2], *color, 0, 0, 1])
            
            y = i * increment - size/2 + position[1]
            vertices.extend([position[0] - size/2, y, position[2], *color, 0, 0, 1])
            vertices.extend([position[0] + size/2, y, position[2], *color, 0, 0, 1])
            
            indices.extend([index, index + 1, index + 2, index + 3])
            index += 4

        return {
            'vertices': np.array(vertices, dtype=np.float32),
            'indices': np.array(indices, dtype=np.uint32)
        }

    @staticmethod
    def create_point(position, color):
        ''' Returns geometry data for a 3D point '''
        return {
            'vertices': np.array([position[0], position[1], position[2], *color, 0, 0, 1], dtype=np.float32),
            'indices': np.array([0], dtype=np.uint32)
        }
    
    @staticmethod
    def create_line(start, end, color):
        ''' Returns geometry data for a 3D line '''
        direction = np.array(end) - np.array(start)
        normal = np.cross(direction, [0, 0, 1])
        if np.allclose(normal, 0):
            normal = [1, 0, 0]
        normal = normal / np.linalg.norm(normal)
        return {
            'vertices': np.array([*start, *color, *normal, *end, *color, *normal], dtype=np.float32),
            'indices': np.array([0, 1], dtype=np.uint32)
        }

    @staticmethod
    def create_triangle(p1, p2, p3, color):
        ''' Returns geometry data for a 3D triangle '''
        v1, v2 = np.array(p2) - np.array(p1), np.array(p3) - np.array(p1)
        normal = np.cross(v1, v2)
        normal = normal / np.linalg.norm(normal)
        return {
            'vertices': np.array([
                *p1, *color, *normal,
                *p2, *color, *normal,
                *p3, *color, *normal
            ], dtype=np.float32),
            'indices': np.array([0, 1, 2], dtype=np.uint32)
        }

    @staticmethod
    def create_rectangle(x, y, width, height, color):
        ''' Returns vertices and indices for a 2D rectangle '''
        half_w, half_h = width / 2, height / 2
        normal = [0, 0, 1]  # Normal pointing outwards
        return {
            'vertices': np.array([
                x - half_w, y - half_h, 0, *color, *normal,
                x + half_w, y - half_h, 0, *color, *normal,
                x + half_w, y + half_h, 0, *color, *normal,
                x - half_w, y + half_h, 0, *color, *normal
            ], dtype=np.float32),
            'indices': np.array([0, 1, 2, 2, 3, 0], dtype=np.uint32)
        }

    @staticmethod
    def create_rectangle_wireframe(x, y, width, height, color):
        ''' Returns vertices and indices for a 2D rectangle wireframe '''
        half_w, half_h = width / 2, height / 2
        return {
            'vertices': np.array([
                x - half_w, y - half_h, 0, *color, 0, 0, 0,
                x + half_w, y - half_h, 0, *color, 0, 0, 0,
                x + half_w, y + half_h, 0, *color, 0, 0, 0,
                x - half_w, y + half_h, 0, *color, 0, 0, 0
            ], dtype=np.float32),
            'indices': np.array([0, 1, 1, 2, 2, 3, 3, 0], dtype=np.uint32)
        }

    @staticmethod
    def create_circle(centre, radius, segments, color):
        ''' Returns vertices and indices for a 2D circle '''
        normal = [0, 0, 1]  # Normal pointing outwards
        vertices = [centre[0], centre[1], 0, *color, *normal]
        indices = []
        for i in range(segments):
            angle = 2 * np.pi * i / segments
            vertices.extend([
                centre[0] + radius * np.cos(angle),
                centre[1] + radius * np.sin(angle),
                0, *color, *normal
            ])
            if i > 0:
                indices.extend([0, i, i + 1])
        indices.extend([0, segments, 1])
        return {
            'vertices': np.array(vertices, dtype=np.float32),
            'indices': np.array(indices, dtype=np.uint32)
        }
        
    @staticmethod
    def create_circle(centre, normal, radius, segments, color):
        ''' Returns vertices and indices for a 3D circle '''
        # Normalize the normal vector
        normal = normal / np.linalg.norm(normal)
        
        # Create an orthonormal basis using the normal
        if np.allclose(normal, [0, 0, 1]):
            right = np.array([1, 0, 0])
        else:
            right = np.cross([0, 0, 1], normal)
            right /= np.linalg.norm(right)
        up = np.cross(normal, right)

        vertices = []
        indices = []

        # Center vertex
        vertices.extend((*centre, *color, *normal))

        # Create vertices around the circle
        for i in range(segments):
            angle = 2 * np.pi * i / segments
            x = radius * np.cos(angle)
            y = radius * np.sin(angle)
            point = centre + right * x + up * y
            vertices.extend((*point, *color, *normal))
            if i > 0:
                indices.extend([0, i, i + 1])

        # Close the circle
        indices.extend([0, segments, 1])

        return {
            'vertices': np.array(vertices, dtype=np.float32),
            'indices': np.array(indices, dtype=np.uint32)
        }
    
    @staticmethod
    def create_circle_wireframe(centre, radius, segments, color):
        ''' Returns vertices and indices for a 3D circle wireframe '''
        vertices = []
        indices = []
        for i in range(segments):
            angle = 2 * np.pi * i / segments
            vertices.extend([
                centre[0] + radius * np.cos(angle),
                centre[1] + radius * np.sin(angle),
                0, *color, 0, 0, 0
            ])
            indices.extend([i, (i + 1) % segments])
        return {
            'vertices': np.array(vertices, dtype=np.float32),
            'indices': np.array(indices, dtype=np.uint32)
        }

    @staticmethod
    def create_cube(position, size, color):
        ''' Returns vertices and indices for a 3D cube '''
        s = size / 2
        x, y, z = position
        vertices = np.array([
            # Front face
            x-s, y-s, z+s, *color, 0, 0, 1,
            x+s, y-s, z+s, *color, 0, 0, 1,
            x+s, y+s, z+s, *color, 0, 0, 1,
            x-s, y+s, z+s, *color, 0, 0, 1,
            # Back face
            x-s, y-s, z-s, *color, 0, 0, -1,
            x+s, y-s, z-s, *color, 0, 0, -1,
            x+s, y+s, z-s, *color, 0, 0, -1,
            x-s, y+s, z-s, *color, 0, 0, -1,
            # Left face
            x-s, y-s, z-s, *color, -1, 0, 0,
            x-s, y-s, z+s, *color, -1, 0, 0,
            x-s, y+s, z+s, *color, -1, 0, 0,
            x-s, y+s, z-s, *color, -1, 0, 0,
            # Right face
            x+s, y-s, z+s, *color, 1, 0, 0,
            x+s, y-s, z-s, *color, 1, 0, 0,
            x+s, y+s, z-s, *color, 1, 0, 0,
            x+s, y+s, z+s, *color, 1, 0, 0,
            # Top face
            x-s, y+s, z+s, *color, 0, 1, 0,
            x+s, y+s, z+s, *color, 0, 1, 0,
            x+s, y+s, z-s, *color, 0, 1, 0,
            x-s, y+s, z-s, *color, 0, 1, 0,
            # Bottom face
            x-s, y-s, z-s, *color, 0, -1, 0,
            x+s, y-s, z-s, *color, 0, -1, 0,
            x+s, y-s, z+s, *color, 0, -1, 0,
            x-s, y-s, z+s, *color, 0, -1, 0
        ], dtype=np.float32)

        indices = np.array([
            0, 1, 2, 2, 3, 0,    # Front face (+Z)
            4, 7, 6, 6, 5, 4,    # Back face (-Z)
            8, 9, 10, 10, 11, 8, # Left face (-X)
            12, 13, 14, 14, 15, 12, # Right face (+X) 
            16, 17, 18, 18, 19, 16, # Top face (+Y)
            20, 21, 22, 22, 23, 20  # Bottom face (-Y)
        ], dtype=np.uint32)

        return {
            'vertices': vertices,
            'indices': indices
        }

    @staticmethod
    def create_cube_wireframe(position, size, color):
        ''' Returns vertices and indices for a 3D cube wireframe '''
        s = size / 2
        x, y, z = position
        vertices = np.array([
            x-s, y-s, z-s, *color, 0, 0, 0,
            x+s, y-s, z-s, *color, 0, 0, 0,
            x+s, y+s, z-s, *color, 0, 0, 0,
            x-s, y+s, z-s, *color, 0, 0, 0,
            x-s, y-s, z+s, *color, 0, 0, 0,
            x+s, y-s, z+s, *color, 0, 0, 0,
            x+s, y+s, z+s, *color, 0, 0, 0,
            x-s, y+s, z+s, *color, 0, 0, 0
        ], dtype=np.float32)

        indices = np.array([
            0, 1, 1, 2, 2, 3, 3, 0,  # Back face
            4, 5, 5, 6, 6, 7, 7, 4,  # Front face
            0, 4, 1, 5, 2, 6, 3, 7   # Connecting edges
        ], dtype=np.uint32)

        return {
            'vertices': vertices,
            'indices': indices
        }

    @staticmethod
    def create_cylinder(start, direction, length, radius, segments, color):
        ''' Returns vertices and indices for a 3D cylinder '''
        direction = direction / np.linalg.norm(direction)
        
        # Choose a vector that's not parallel to direction
        if np.abs(direction[0]) < 0.9:
            right = np.array([1, 0, 0])
        elif np.abs(direction[1]) < 0.9:
            right = np.array([0, 1, 0])
        else:
            right = np.array([0, 0, 1])
        
        # Create an orthonormal basis
        right = np.cross(direction, right)
        right /= np.linalg.norm(right)
        up = np.cross(direction, right)

        vertices = []
        indices = []

        for i in range(segments):
            angle = 2 * np.pi * i / segments
            x = radius * np.cos(angle)
            y = radius * np.sin(angle)
            
            for end in [0, 1]:
                point = start + direction * (length * end) + right * x + up * y
                normal = right * np.cos(angle) + up * np.sin(angle)
                vertices.extend((*point, *normal, *color))

        for i in range(segments):
            i0 = i * 2
            i1 = (i * 2 + 2) % (segments * 2)
            i2 = i * 2 + 1
            i3 = (i * 2 + 3) % (segments * 2)

            indices.extend([i0, i1, i2, i1, i3, i2])

        # vertices_1, indices_1 = Geometry.create_circle(start[0], start[1], radius, segments, color)
        # end = start + direction * length
        # vertices_2, indices_2 = Geometry.create_circle(end[0], end[1], radius, segments, color)
        # vertices.extend(vertices_1)
        # indices.extend(indices_1)
        # vertices.extend(vertices_2)
        # indices.extend(indices_2)

        return {
            'vertices': np.array(vertices, dtype=np.float32),
            'indices': np.array(indices, dtype=np.uint32)
        }

    @staticmethod
    def create_cylinder_wireframe(start, direction, length, radius, segments, color):
        ''' Returns vertices and indices for a 3D cylinder wireframe '''
        direction = direction / np.linalg.norm(direction)
        up = np.array([0, 0, 1])
        if np.allclose(direction, up):
            right = np.array([1, 0, 0])
        else:
            right = np.cross(up, direction)
            right /= np.linalg.norm(right)
        up = np.cross(direction, right)

        vertices = []
        indices = []

        for i in range(segments):
            angle = 2 * np.pi * i / segments
            x = radius * np.cos(angle)
            y = radius * np.sin(angle)
            
            for end in [0, 1]:
                point = start + direction * (length * end) + right * x + up * y
                vertices.extend((*point, *color))

        # Circular edges
        for i in range(segments):
            indices.extend([i, (i + 1) % segments])
            indices.extend([i + segments, (i + 1) % segments + segments])

        # Longitudinal edges
        for i in range(segments):
            indices.extend([i, i + segments])

        return {
            'vertices': np.array(vertices, dtype=np.float32),
            'indices': np.array(indices, dtype=np.uint32)
        }

    @staticmethod
    def create_cone(start, direction, length, radius, segments, color):
        
        direction = direction / np.linalg.norm(direction)
        up = np.array([0, 0, 1])
        if np.allclose(direction, up):
            right = np.array([1, 0, 0])
        else:
            right = np.cross(up, direction)
            right /= np.linalg.norm(right)
        up = np.cross(direction, right)

        vertices = []
        indices = []

        # Apex
        apex = start + direction * length
        vertices.extend((*apex, *direction, *color))

        # Base
        for i in range(segments):
            angle = 2 * np.pi * i / segments
            x = radius * np.cos(angle)
            y = radius * np.sin(angle)
            point = start + right * x + up * y
            normal = right * np.cos(angle) + up * np.sin(angle)
            vertices.extend((*point, *normal, *color))

        # Indices for the base
        for i in range(1, segments - 1):
            indices.extend([0, i, i + 1])

        # Indices for the sides
        for i in range(segments):
            i1 = i + 1
            i2 = (i + 1) % segments + 1
            indices.extend([0, i2, i1])

        return {
            'vertices': np.array(vertices, dtype=np.float32),
            'indices': np.array(indices, dtype=np.uint32)
        }

    @staticmethod
    def create_cone_wireframe(start, direction, length, radius, segments, color):
        direction = direction / np.linalg.norm(direction)
        up = np.array([0, 0, 1])
        if np.allclose(direction, up):
            right = np.array([1, 0, 0])
        else:
            right = np.cross(up, direction)
            right /= np.linalg.norm(right)
        up = np.cross(direction, right)

        vertices = []
        indices = []

        # Apex
        apex = start + direction * length
        vertices.extend((*apex, *color))

        # Base
        for i in range(segments):
            angle = 2 * np.pi * i / segments
            x = radius * np.cos(angle)
            y = radius * np.sin(angle)
            point = start + right * x + up * y
            vertices.extend((*point, *color))

        # Circular base
        for i in range(1, segments + 1):
            indices.extend([i, i % segments + 1])

        # Lines from base to apex
        for i in range(1, segments + 1):
            indices.extend([0, i])

        return {
            'vertices': np.array(vertices, dtype=np.float32),
            'indices': np.array(indices, dtype=np.uint32)
        }

