import numpy as np
from OpenGL.GL import *
from color import Color

class GeometryData:
    def __init__(self, vertices, indices):
        self.vertices = np.array(vertices, dtype=np.float32)
        self.indices = np.array(indices, dtype=np.uint32)

    def __add__(self, other):
        if not isinstance(other, GeometryData):
            raise TypeError("Can only add GeometryData to GeometryData")

        # Combine vertices
        combined_vertices = np.concatenate((self.vertices, other.vertices))

        # Adjust indices for the second object
        max_index = len(self.vertices) // 9  # Assuming 9 values per vertex (position, color, normal)
        adjusted_other_indices = other.indices + max_index

        # Combine indices
        combined_indices = np.concatenate((self.indices, adjusted_other_indices))

        return GeometryData(combined_vertices, combined_indices)

    def transform(self, translate=(0, 0, 0), rotate=(0, 0, 0), scale=(1, 1, 1)):
        # Reshape vertices to separate positions, colors, and normals
        vertices = self.vertices.reshape(-1, 9)
        positions = vertices[:, :3]
        colors = vertices[:, 3:6]
        normals = vertices[:, 6:]

        # Create transformation matrices
        transform_matrix = self.transform_matrix(translate, rotate, scale)
        normal_matrix = np.linalg.inv(transform_matrix[:3, :3]).T  # For transforming normals

        # Apply transformation to positions
        positions_homogeneous = np.column_stack((positions, np.ones(positions.shape[0])))
        transformed_positions = np.dot(positions_homogeneous, transform_matrix.T)[:, :3]

        # Apply transformation to normals
        transformed_normals = np.dot(normals, normal_matrix)
        # Normalize the transformed normals
        transformed_normals = transformed_normals / np.linalg.norm(transformed_normals, axis=1)[:, np.newaxis]

        # Combine transformed positions, original colors, and transformed normals
        transformed_vertices = np.column_stack((transformed_positions, colors, transformed_normals))
        self.vertices = transformed_vertices.flatten().astype(np.float32)
        return self

    @staticmethod
    def transform_matrix(translate=(0, 0, 0), rotate=(0, 0, 0), scale=(1, 1, 1)):
        """
        Create a 4x4 transformation matrix from the current transform parameters.
        
        :return: 4x4 numpy array representing the transformation matrix
        """
        tx, ty, tz = translate
        rx, ry, rz = rotate
        sx, sy, sz = scale

        # Create rotation matrices
        Rx = np.array([[1, 0, 0], [0, np.cos(rx), -np.sin(rx)], [0, np.sin(rx), np.cos(rx)]])
        Ry = np.array([[np.cos(ry), 0, np.sin(ry)], [0, 1, 0], [-np.sin(ry), 0, np.cos(ry)]])
        Rz = np.array([[np.cos(rz), -np.sin(rz), 0], [np.sin(rz), np.cos(rz), 0], [0, 0, 1]])

        # Combine rotations
        R = Rz @ Ry @ Rx

        # Create transformation matrix
        transform = np.array([
            [R[0, 0]*sx, R[0, 1]*sy, R[0, 2]*sz, tx],
            [R[1, 0]*sx, R[1, 1]*sy, R[1, 2]*sz, ty],
            [R[2, 0]*sx, R[2, 1]*sy, R[2, 2]*sz, tz],
            [0, 0, 0, 1]
        ])

        return transform


class Geometry:
    @staticmethod
    def create_grid(size, increment, color):
        ''' Returns GeometryData for a 3D grid centered at origin '''
        vertices, indices = [], []
        index = 0
        num_lines = int(size / increment) + 1
        
        for i in range(num_lines):
            x = i * increment - size/2
            vertices.extend([x, -size/2, 0, *color, 0, 0, 1])
            vertices.extend([x, size/2, 0, *color, 0, 0, 1])
            
            y = i * increment - size/2
            vertices.extend([-size/2, y, 0, *color, 0, 0, 1])
            vertices.extend([size/2, y, 0, *color, 0, 0, 1])
            
            indices.extend([index, index + 1, index + 2, index + 3])
            index += 4

        return GeometryData(vertices, indices)

    @staticmethod
    def create_point(position, color):
        ''' Returns GeometryData for a 3D point '''
        return GeometryData(
            [position[0], position[1], position[2], *color, 0, 0, 1],
            [0]
        )
    
    @staticmethod
    def create_line(start, end, color):
        ''' Returns GeometryData for a 3D line '''
        direction = np.array(end) - np.array(start)
        normal = np.cross(direction, [0, 0, 1])
        if np.allclose(normal, 0):
            normal = [1, 0, 0]
        normal = normal / np.linalg.norm(normal)
        return GeometryData(
            [*start, *color, *normal, *end, *color, *normal],
            [0, 1]
        )

    @staticmethod
    def create_triangle(p1, p2, p3, color):
        ''' Returns GeometryData for a 3D triangle '''
        v1, v2 = np.array(p2) - np.array(p1), np.array(p3) - np.array(p1)
        normal = np.cross(v1, v2)
        normal = normal / np.linalg.norm(normal)
        return GeometryData(
            [
                *p1, *color, *normal,
                *p2, *color, *normal,
                *p3, *color, *normal
            ],
            [0, 1, 2]
        )

    @staticmethod
    def create_rectangle(x, y, width, height, color):
        ''' Returns GeometryData for a 2D rectangle '''
        half_w, half_h = width / 2, height / 2
        normal = [0, 0, 1]  # Normal pointing outwards
        return GeometryData(
            [
                x - half_w, y - half_h, 0, *color, *normal,
                x + half_w, y - half_h, 0, *color, *normal,
                x + half_w, y + half_h, 0, *color, *normal,
                x - half_w, y + half_h, 0, *color, *normal
            ],
            [0, 1, 2, 2, 3, 0]
        )

    @staticmethod
    def create_rectangle_wireframe(x, y, width, height, color):
        ''' Returns GeometryData for a 2D rectangle wireframe '''
        half_w, half_h = width / 2, height / 2
        normal = [0, 0, 1]  # Normal pointing outwards
        return GeometryData(
            [
                x - half_w, y - half_h, 0, *color, *normal,
                x + half_w, y - half_h, 0, *color, *normal,
                x + half_w, y + half_h, 0, *color, *normal,
                x - half_w, y + half_h, 0, *color, *normal
            ],
            [0, 1, 1, 2, 2, 3, 3, 0]
        )

    @staticmethod
    def create_circle(centre, radius, segments, color):
        ''' Returns GeometryData for a 2D circle '''
        normal = [0, 0, 1]  # Normal pointing outwards
        vertices = [*centre, *color, *normal]
        indices = []
        for i in range(segments):
            angle = 2 * np.pi * i / segments
            vertices.extend([
                centre[0] + radius * np.cos(angle),
                centre[1] + radius * np.sin(angle),
                centre[2], *color, *normal
            ])
            if i > 0:
                indices.extend([0, i, i + 1])
        indices.extend([0, segments, 1])
        return GeometryData(vertices, indices)
        
    @staticmethod
    def create_circle_wireframe(centre, radius, segments, color):
        ''' Returns GeometryData for a 3D circle wireframe '''
        normal = [0, 0, 1]  # Normal pointing outwards
        vertices = []
        indices = []
        for i in range(segments):
            angle = 2 * np.pi * i / segments
            vertices.extend([
                centre[0] + radius * np.cos(angle),
                centre[1] + radius * np.sin(angle),
                centre[2], *color, *normal
            ])
            indices.extend([i, (i + 1) % segments])
        return GeometryData(vertices, indices)

    @staticmethod
    def create_cube(size, color):
        ''' Returns GeometryData for a 3D cube '''
        s = size / 2
        vertices = [
            # Front face
            -s, -s, s, *color, 0, 0, 1,
            s, -s, s, *color, 0, 0, 1,
            s, s, s, *color, 0, 0, 1,
            -s, s, s, *color, 0, 0, 1,
            # Back face
            -s, -s, -s, *color, 0, 0, -1,
            s, -s, -s, *color, 0, 0, -1,
            s, s, -s, *color, 0, 0, -1,
            -s, s, -s, *color, 0, 0, -1,
            # Left face
            -s, -s, -s, *color, -1, 0, 0,
            -s, -s, s, *color, -1, 0, 0,
            -s, s, s, *color, -1, 0, 0,
            -s, s, -s, *color, -1, 0, 0,
            # Right face
            s, -s, s, *color, 1, 0, 0,
            s, -s, -s, *color, 1, 0, 0,
            s, s, -s, *color, 1, 0, 0,
            s, s, s, *color, 1, 0, 0,
            # Top face
            -s, s, s, *color, 0, 1, 0,
            s, s, s, *color, 0, 1, 0,
            s, s, -s, *color, 0, 1, 0,
            -s, s, -s, *color, 0, 1, 0,
            # Bottom face
            -s, -s, -s, *color, 0, -1, 0,
            s, -s, -s, *color, 0, -1, 0,
            s, -s, s, *color, 0, -1, 0,
            -s, -s, s, *color, 0, -1, 0
        ]

        indices = [
            0, 1, 2, 2, 3, 0,    # Front face
            4, 7, 6, 6, 5, 4,    # Back face
            8, 9, 10, 10, 11, 8, # Left face
            12, 13, 14, 14, 15, 12, # Right face 
            16, 17, 18, 18, 19, 16, # Top face
            20, 21, 22, 22, 23, 20  # Bottom face
        ]

        return GeometryData(vertices, indices)

    @staticmethod
    def create_cube_wireframe(size, color):
        ''' Returns GeometryData for a 3D cube wireframe '''
        s = size / 2
        x, y, z = (0,0,0)
        normal = [0, 0, 1]  # Normal pointing outwards
        vertices = [
            x-s, y-s, z-s, *color, *normal,
            x+s, y-s, z-s, *color, *normal,
            x+s, y+s, z-s, *color, *normal,
            x-s, y+s, z-s, *color, *normal,
            x-s, y-s, z+s, *color, *normal,
            x+s, y-s, z+s, *color, *normal,
            x+s, y+s, z+s, *color, *normal,
            x-s, y+s, z+s, *color, *normal
        ]

        indices = [
            0, 1, 1, 2, 2, 3, 3, 0,  # Back face
            4, 5, 5, 6, 6, 7, 7, 4,  # Front face
            0, 4, 1, 5, 2, 6, 3, 7   # Connecting edges
        ]

        return GeometryData(vertices, indices)

    def create_cylinder(segments, color):
        ''' Returns GeometryData for a 3D cylinder along Z-axis '''
        vertices = []
        indices = []

        radius = 0.5
        for i in range(segments):
            angle = 2 * np.pi * i / segments
            x = radius * np.cos(angle)
            y = radius * np.sin(angle)
            normal = [x, y, 0]
            
            # Bottom circle
            vertices.extend([x, y, 0, *color, *normal])
            # Top circle
            vertices.extend([x, y, 1, *color, *normal])

        # Indices for the side faces
        for i in range(segments):
            i1 = i * 2
            i2 = (i * 2 + 2) % (segments * 2)
            i3 = i * 2 + 1
            i4 = (i * 2 + 3) % (segments * 2)
            indices.extend([i1, i2, i3, i2, i4, i3])
            
        cylinder = GeometryData(vertices, indices)
        bottom = Geometry.create_circle(centre=(0,0,0), radius=radius, segments=segments, color=color).transform(rotate=(np.pi,0,0))
        top = Geometry.create_circle(centre=(0,0,1), radius=radius, segments=segments, color=color)
        return cylinder + bottom + top

    @staticmethod
    def create_cylinder_wireframe(segments, color):
        ''' Returns GeometryData for a 3D cylinder wireframe along Z-axis '''
        
        bottom = Geometry.create_circle_wireframe(centre=(0,0,0), radius=0.5, segments=segments, color=color)
        top = Geometry.create_circle_wireframe(centre=(0,0,1), radius=0.5, segments=segments, color=color)
        return bottom + top
        
    @staticmethod
    def create_cone(segments, color):
        ''' Returns GeometryData for a 3D cone along Z-axis '''
        assert isinstance(segments, int) and segments > 2, "segments must be an integer greater than 2"
        assert len(color) == 3, "color must be a tuple of 3 values"
        
        vertices = []
        indices = []
        normal_apex = [0, 0, 1]  # Normal pointing outwards
        # Apex
        vertices.extend([0, 0, 1, *color, *normal_apex])
        radius = 0.5
        # Side vertices
        for i in range(segments):
            angle = 2 * np.pi * i / segments
            x = radius * np.cos(angle)
            y = radius * np.sin(angle)
            normal = [x, y, 0.5]  # Adjusted normal for smooth shading
            normal = normal / np.linalg.norm(normal)
            vertices.extend([x, y, 0, *color, *normal])

        # Base center vertex
        base_center_index = len(vertices) // 9
        vertices.extend([0, 0, 0, *color, 0, 0, -1])  # Base center with normal pointing down

        # Indices for the sides
        for i in range(segments):
            i1 = i + 1
            i2 = (i + 1) % segments + 1
            indices.extend([0, i1, i2])

        cone = GeometryData(vertices, indices)
        bottom = Geometry.create_circle(centre=(0,0,0), radius=0.5, segments=segments, color=color).transform(rotate=(np.pi,0,0))
        return cone + bottom

    @staticmethod
    def create_cone_wireframe(segments, color):
        ''' Returns GeometryData for a 3D cone wireframe along Z-axis '''
        return Geometry.create_circle_wireframe(centre=(0,0,0), radius=0.5, segments=segments, color=color)

    @staticmethod
    def create_sphere(radius, stacks, sectors, color):
        ''' Returns GeometryData for a 3D sphere '''
        vertices = []
        indices = []

        for i in range(stacks + 1):
            V = i / stacks
            phi = V * np.pi

            for j in range(sectors + 1):
                U = j / sectors
                theta = U * 2 * np.pi

                x = radius * np.cos(theta) * np.sin(phi)
                y = radius * np.sin(theta) * np.sin(phi)
                z = radius * np.cos(phi)

                normal = [x, y, z]
                normal = normal / np.linalg.norm(normal)

                vertices.extend([x, y, z, *color, *normal])

        for i in range(stacks):
            for j in range(sectors):
                first = i * (sectors + 1) + j
                second = first + sectors + 1

                indices.extend([first, second, first + 1])
                indices.extend([second, second + 1, first + 1])

        return GeometryData(vertices, indices)
