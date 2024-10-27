import numpy as np
from OpenGL.GL import *
from color import Color

class Vertex:
    SIZE = 9  # Total number of floats per vertex (3 for position, 3 for color, 3 for normal)
    STRIDE = SIZE * 4  # Stride in bytes (4 bytes per float)

    POSITION_OFFSET = 0
    COLOR_OFFSET = 3 * 4  # 3 floats * 4 bytes per float
    NORMAL_OFFSET = 6 * 4  # 6 floats * 4 bytes per float

    LAYOUT = [
        {'index': 0, 'size': 3, 'type': GL_FLOAT, 'normalized': GL_FALSE, 'stride': STRIDE, 'offset': POSITION_OFFSET},
        {'index': 1, 'size': 3, 'type': GL_FLOAT, 'normalized': GL_FALSE, 'stride': STRIDE, 'offset': COLOR_OFFSET},
        {'index': 2, 'size': 3, 'type': GL_FLOAT, 'normalized': GL_FALSE, 'stride': STRIDE, 'offset': NORMAL_OFFSET}
    ]

    def __init__(self, position, color, normal):
        self.position = np.array(position, dtype=np.float32)
        self.color = np.array(color, dtype=np.float32)
        self.normal = np.array(normal, dtype=np.float32)

    def to_array(self):
        return np.concatenate([self.position, self.color, self.normal])

class GeometryData:
    
    def __init__(self, vertices, indices):
        self.vertices = vertices
        self.indices = np.array(indices, dtype=np.uint32)

    def __add__(self, other):
        if not isinstance(other, GeometryData):
            raise TypeError("Can only add GeometryData to GeometryData")

        # Combine vertices
        combined_vertices = np.concatenate((self.vertices, other.vertices))

        # Adjust indices for the second object
        max_index = len(self.vertices)
        adjusted_other_indices = [index + max_index for index in other.indices]

        # Combine indices
        combined_indices = np.concatenate((self.indices, adjusted_other_indices))

        return GeometryData(combined_vertices, combined_indices)

    def transform(self, translate=(0, 0, 0), rotate=(0, 0, 0), scale=(1, 1, 1)):
        transform_matrix = GeometryData.transform_matrix(translate, rotate, scale)
        normal_matrix = np.linalg.inv(transform_matrix[:3, :3]).T  # For transforming normals

        for vertex in self.vertices:
            # Transform position
            position_homogeneous = np.append(vertex.position, 1)
            transformed_position = np.dot(transform_matrix, position_homogeneous)[:3]
            vertex.position = transformed_position

            # Transform normal
            transformed_normal = np.dot(normal_matrix, vertex.normal)
            vertex.normal = transformed_normal / np.linalg.norm(transformed_normal)

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
        vertices = []
        indices = []
        num_lines = int(size / increment) + 1
        
        for i in range(num_lines):
            x = i * increment - size/2
            vertices.append(Vertex([x, -size/2, 0], color, [0, 0, 1]))
            vertices.append(Vertex([x, size/2, 0], color, [0, 0, 1]))
            
            y = i * increment - size/2
            vertices.append(Vertex([-size/2, y, 0], color, [0, 0, 1]))
            vertices.append(Vertex([size/2, y, 0], color, [0, 0, 1]))
            
            index = i * 4
            indices.extend([index, index + 1, index + 2, index + 3])

        return GeometryData(vertices, indices)

    @staticmethod
    def create_point(position, color):
        vertices = [Vertex(position, color, [0, 0, 1])]
        indices = [0]
        return GeometryData(vertices, indices)
    
    @staticmethod
    def create_line(p0, p1, color):
        direction = np.array(p1) - np.array(p0)
        normal = np.cross(direction, [0, 0, 1])
        norm = np.linalg.norm(normal)
            
        if norm > 1e-6:  # If the normal not (close to) zero
            normal = normal / norm
        else:  # The line is parallel to z-axis, so we can use any perpendicular vector
            normal = np.cross(direction, [1, 0, 0])
            norm = np.linalg.norm(normal)
        
        vertices = [
            Vertex(p0, color, normal),
            Vertex(p1, color, normal)
        ]
        indices = [0, 1]
        return GeometryData(vertices, indices)

    @staticmethod
    def create_triangle(p1, p2, p3, color):
        ''' Returns GeometryData for a 3D triangle '''
        v1, v2 = np.array(p2) - np.array(p1), np.array(p3) - np.array(p1)
        normal = np.cross(v1, v2)
        normal = normal / np.linalg.norm(normal)
        vertices = [
            Vertex(p1, color, normal),
            Vertex(p2, color, normal),
            Vertex(p3, color, normal)
        ]
        indices = [0, 1, 2]
        return GeometryData(vertices, indices)

    @staticmethod
    def create_triangle_wireframe(p1, p2, p3, color):
        ''' Returns GeometryData for a 3D triangle wireframe '''
        return Geometry.create_line(p1, p2, color) + Geometry.create_line(p2, p3, color) + Geometry.create_line(p3, p1, color)

    @staticmethod
    def create_rectangle(x, y, width, height, color):
        ''' Returns GeometryData for a 2D rectangle '''
        half_w, half_h = width / 2, height / 2
        normal = [0, 0, 1]  # Normal pointing outwards
        vertices = [
            Vertex([x - half_w, y - half_h, 0], color, normal),
            Vertex([x + half_w, y - half_h, 0], color, normal),
            Vertex([x + half_w, y + half_h, 0], color, normal),
            Vertex([x - half_w, y + half_h, 0], color, normal)
        ]
        indices = [0, 1, 2, 2, 3, 0]
        return GeometryData(vertices, indices)

    @staticmethod
    def create_rectangle_wireframe(x, y, width, height, color):
        ''' Returns GeometryData for a 2D rectangle wireframe '''
        half_w, half_h = width / 2, height / 2
        normal = [0, 0, 1]  # Normal pointing outwards
        vertices = [
            Vertex([x - half_w, y - half_h, 0], color, normal),
            Vertex([x + half_w, y - half_h, 0], color, normal),
            Vertex([x + half_w, y + half_h, 0], color, normal),
            Vertex([x - half_w, y + half_h, 0], color, normal)
        ]
        indices = [0, 1, 1, 2, 2, 3, 3, 0]
        return GeometryData(vertices, indices)

    @staticmethod
    def create_circle(centre, radius, segments, color):
        ''' Returns GeometryData for a 2D circle '''
        normal = [0, 0, 1]  # Normal pointing outwards
        vertices = [Vertex(centre, color, normal)]
        indices = []
        for i in range(segments):
            angle = 2 * np.pi * i / segments
            x = centre[0] + radius * np.cos(angle)
            y = centre[1] + radius * np.sin(angle)
            vertices.append(Vertex([x, y, centre[2]], color, normal))
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
            x = centre[0] + radius * np.cos(angle)
            y = centre[1] + radius * np.sin(angle)
            vertices.append(Vertex([x, y, centre[2]], color, normal))
            indices.extend([i, (i + 1) % segments])
        return GeometryData(vertices, indices)

    @staticmethod
    def create_cube(size, color):
        ''' Returns GeometryData for a 3D cube '''
        s = size / 2
        vertices = [
            # Front face
            Vertex([-s, -s, s], color, [0, 0, 1]),
            Vertex([s, -s, s], color, [0, 0, 1]),
            Vertex([s, s, s], color, [0, 0, 1]),
            Vertex([-s, s, s], color, [0, 0, 1]),
            # Back face
            Vertex([-s, -s, -s], color, [0, 0, -1]),
            Vertex([s, -s, -s], color, [0, 0, -1]),
            Vertex([s, s, -s], color, [0, 0, -1]),
            Vertex([-s, s, -s], color, [0, 0, -1]),
            # Left face
            Vertex([-s, -s, -s], color, [-1, 0, 0]),
            Vertex([-s, -s, s], color, [-1, 0, 0]),
            Vertex([-s, s, s], color, [-1, 0, 0]),
            Vertex([-s, s, -s], color, [-1, 0, 0]),
            # Right face
            Vertex([s, -s, s], color, [1, 0, 0]),
            Vertex([s, -s, -s], color, [1, 0, 0]),
            Vertex([s, s, -s], color, [1, 0, 0]),
            Vertex([s, s, s], color, [1, 0, 0]),
            # Top face
            Vertex([-s, s, s], color, [0, 1, 0]),
            Vertex([s, s, s], color, [0, 1, 0]),
            Vertex([s, s, -s], color, [0, 1, 0]),
            Vertex([-s, s, -s], color, [0, 1, 0]),
            # Bottom face
            Vertex([-s, -s, -s], color, [0, -1, 0]),
            Vertex([s, -s, -s], color, [0, -1, 0]),
            Vertex([s, -s, s], color, [0, -1, 0]),
            Vertex([-s, -s, s], color, [0, -1, 0])
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
            Vertex([x-s, y-s, z-s], color, normal),
            Vertex([x+s, y-s, z-s], color, normal),
            Vertex([x+s, y+s, z-s], color, normal),
            Vertex([x-s, y+s, z-s], color, normal),
            Vertex([x-s, y-s, z+s], color, normal),
            Vertex([x+s, y-s, z+s], color, normal),
            Vertex([x+s, y+s, z+s], color, normal),
            Vertex([x-s, y+s, z+s], color, normal)
        ]

        indices = [
            0, 1, 1, 2, 2, 3, 3, 0,  # Back face
            4, 5, 5, 6, 6, 7, 7, 4,  # Front face
            0, 4, 1, 5, 2, 6, 3, 7   # Connecting edges
        ]

        return GeometryData(vertices, indices)

    @staticmethod
    def create_cylinder(segments, color):
        ''' Returns GeometryData for a 3D cylinder along Z-axis '''
        vertices = []
        indices = []

        radius = 0.5
        height = 1.0

        # Create vertices for the cylinder body
        for i in range(segments + 1):  # +1 to close the cylinder
            angle = 2 * np.pi * i / segments
            x = radius * np.cos(angle)
            y = radius * np.sin(angle)
            normal = np.array([x, y, 0])
            normal = normal / np.linalg.norm(normal)  # Normalize the normal
            
            # Bottom vertex
            vertices.append(Vertex([x, y, 0], color, normal))
            # Top vertex
            vertices.append(Vertex([x, y, height], color, normal))

        # Indices for the side faces
        for i in range(segments):
            i1 = i * 2
            i2 = (i * 2 + 2) % (segments * 2 + 2)
            i3 = i * 2 + 1
            i4 = (i * 2 + 3) % (segments * 2 + 2)
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
        vertices.append(Vertex([0, 0, 1], color, normal_apex))
        radius = 0.5
        # Side vertices
        for i in range(segments):
            angle = 2 * np.pi * i / segments
            x = radius * np.cos(angle)
            y = radius * np.sin(angle)
            normal = [x, y, 0.5]  # Adjusted normal for smooth shading
            normal = normal / np.linalg.norm(normal)
            vertices.append(Vertex([x, y, 0], color, normal))

        # Base center vertex
        vertices.append(Vertex([0, 0, 0], color, [0, 0, -1]))  # Base center with normal pointing down

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
    def create_sphere(radius, subdivisions, color):
        ''' Returns GeometryData for a 3D sphere using icosahedron subdivision '''
        vertices = []
        indices = []

        # Create initial icosahedron
        t = (1.0 + np.sqrt(5.0)) / 2.0
        vertices = [
            [-1, t, 0], [1, t, 0], [-1, -t, 0], [1, -t, 0],
            [0, -1, t], [0, 1, t], [0, -1, -t], [0, 1, -t],
            [t, 0, -1], [t, 0, 1], [-t, 0, -1], [-t, 0, 1]
        ]
        indices = [
            0, 11, 5, 0, 5, 1, 0, 1, 7, 0, 7, 10, 0, 10, 11,
            1, 5, 9, 5, 11, 4, 11, 10, 2, 10, 7, 6, 7, 1, 8,
            3, 9, 4, 3, 4, 2, 3, 2, 6, 3, 6, 8, 3, 8, 9,
            4, 9, 5, 2, 4, 11, 6, 2, 10, 8, 6, 7, 9, 8, 1
        ]

        # Subdivide
        for _ in range(subdivisions):
            new_indices = []
            for i in range(0, len(indices), 3):
                v1 = vertices[indices[i]]
                v2 = vertices[indices[i+1]]
                v3 = vertices[indices[i+2]]
                
                v12 = Geometry.normalize([(v1[0] + v2[0])/2, (v1[1] + v2[1])/2, (v1[2] + v2[2])/2])
                v23 = Geometry.normalize([(v2[0] + v3[0])/2, (v2[1] + v3[1])/2, (v2[2] + v3[2])/2])
                v31 = Geometry.normalize([(v3[0] + v1[0])/2, (v3[1] + v1[1])/2, (v3[2] + v1[2])/2])
                
                vertices.extend([v12, v23, v31])
                
                i1, i2, i3 = indices[i], indices[i+1], indices[i+2]
                i12, i23, i31 = len(vertices) - 3, len(vertices) - 2, len(vertices) - 1
                
                new_indices.extend([i1, i12, i31, i2, i23, i12, i3, i31, i23, i12, i23, i31])
            
            indices = new_indices

        # Normalize all vertices to the sphere surface and create Vertex objects
        vertex_objects = []
        for v in vertices:
            normalized = Geometry.normalize(v)
            position = [x * radius for x in normalized]
            vertex_objects.append(Vertex(position, color, normalized))

        return GeometryData(vertex_objects, indices)

    @staticmethod
    def create_arrow(p0, p1, color, wireframe_color=(1,1,1), shaft_radius=0.1, head_radius=0.2, head_length=0.4, segments=16):
        ''' Returns GeometryData for a 3D arrow from p0 to p1 '''
        p0, p1 = np.array(p0), np.array(p1)
        direction = p1 - p0
        length = np.linalg.norm(direction)
        
        if length == 0:
            return GeometryData([], [])  # Return empty geometry if p0 and p1 are the same

        unit_direction = direction / length
        pHead = p1 - unit_direction * head_length

        # Calculate transforms
        translation_shaft, rotation_shaft, scale_shaft = Geometry.calculate_transform(p0, pHead, (shaft_radius, shaft_radius, 1))
        translation_head, rotation_head, scale_head = Geometry.calculate_transform(pHead, p1, (head_radius, head_radius, 1))

        # Create shaft (cylinder)
        shaft = Geometry.create_cylinder(segments, color).transform(translation_shaft, rotation_shaft, scale_shaft)
        # Create arrowhead (cone)
        head = Geometry.create_cone(segments, color).transform(translation_head, rotation_head, scale_head)
        body = shaft + head
        # Create shaft (cylinder)
        shaft_wireframe = Geometry.create_cylinder_wireframe(segments, wireframe_color).transform(translation_shaft, rotation_shaft, scale_shaft)
        # Create arrowhead (cone)
        head_wireframe = Geometry.create_cone_wireframe(segments, wireframe_color).transform(translation_head, rotation_head, scale_head)
        wireframe = shaft_wireframe + head_wireframe
        return [body, wireframe]
    
    @staticmethod
    def calculate_transform(p0, p1, cross_section=(1, 1)):
        # Convert inputs to numpy arrays
        p0, p1 = np.array(p0), np.array(p1)

        # Calculate direction vector
        direction = p1 - p0
        length = np.linalg.norm(direction)

        # Calculate rotation angles
        if length > 0:
            # Normalize the direction vector
            unit_direction = direction / length

            # Calculate rotation angles
            rz = np.arctan2(unit_direction[1], unit_direction[0])
            ry = np.arctan2(unit_direction[0] * np.cos(rz) + unit_direction[1] * np.sin(rz), unit_direction[2])
            rx = 0  # We don't need to rotate around x-axis for this alignment

            rotation = (rx, ry, rz)
        else:
            # If p0 and p1 are the same point, no rotation is needed
            rotation = (0, 0, 0)

        # Calculate translation and scale
        translation = p0
        scale = np.array([cross_section[0], cross_section[1], length])

        return translation, rotation, scale
    
    @staticmethod
    def normalize(v):
        norm = np.linalg.norm(v)
        return [x / norm for x in v] if norm != 0 else v



