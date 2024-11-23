"""
Core Shapes module providing classes for creating and manipulating 3D primitives.
Includes vertex data structures, shape containers, and shape factory methods.
"""

import numpy as np
from dataclasses import dataclass
from OpenGL.GL import *
from pyglviewer.utils.colour import Colour
from pyglviewer.utils.transform import Transform


@dataclass
class ArrowDimensions:
    """Dimensions for arrow objects."""
    shaft_radius: float
    head_radius: float
    head_length: float


class Vertex:
    """
    Represents a vertex in 3D space with position, colour, and normal attributes.
    Provides memory layout information for OpenGL vertex buffer organization.
    Each vertex contains position (xyz), colour (rgb), and normal (xyz) data.
    
    Attributes:
        position (np.array): 3D position vector (x, y, z)
        colour (np.array): RGB colour values (r, g, b)
        normal (np.array): Normal vector (nx, ny, nz)
    """

    def __init__(self, position, colour, normal):
        self.position = np.array(position, dtype=np.float32)
        self.colour = np.array(colour, dtype=np.float32)
        self.normal = np.array(normal, dtype=np.float32)

    def to_array(self):
        return np.concatenate([self.position, self.colour, self.normal])

    @staticmethod
    def from_array(data, offset=0):
        """Create vertex from flat array data."""
        return Vertex(
            position=data[offset:offset+3],
            colour=data[offset+3:offset+6],
            normal=data[offset+6:offset+9]
        )

class Shape:
    """
    Container for 3D shape data including vertices and indices.
    Provides methods for combining and transforming shapes.
    Vertices are stored in their transformed state.

    Attributes:
        vertices (list[Vertex]): List of vertices defining the shape
        indices (np.array): Indices of the vertices to render
    """
    def __init__(self, vertices=None, indices=None):
        """
        Args:
            vertices (list[Vertex]): List of vertices
            indices (list[int]): List of indices
        """
        self.vertices = np.array(vertices, dtype=Vertex) if vertices is not None else []
        self.indices = np.array(indices, dtype=np.uint32) if indices is not None else []
        self.vertex_count = len(vertices) if vertices is not None else 0
        self.index_count = len(indices) if indices is not None else 0
        
    def __add__(self, other):
        """Combine two shapes into a single shape.
        
        Args:
            other (Shape): Shape to combine with this one
        
        Returns:
            Shape: Combined shape with adjusted indices
            
        Raises:
            TypeError: If other is not a Shape instance
        """
        if not isinstance(other, Shape):
            raise TypeError("Can only add Shape to Shape")

        # Combine vertices
        combined_vertices = np.concatenate((self.vertices, other.vertices))

        # Adjust indices for the second object
        max_index = len(self.vertices)
        adjusted_other_indices = [index + max_index for index in other.indices]

        # Combine indices
        combined_indices = np.concatenate((self.indices, adjusted_other_indices))

        result = Shape(combined_vertices, combined_indices)
        return result

    def get_vertices(self):
        """Return interleaved vertex data as a flattened numpy array.
        
        Returns:
            np.ndarray: Flattened array of vertex data [x,y,z, r,g,b, nx,ny,nz, x,y,z...]
        """
        return np.array([vertex.to_array() for vertex in self.vertices], dtype=np.float32).flatten()

    def get_indices(self):
        """Get index data for batch rendering.
        
        Returns:
            np.ndarray: Array of vertex indices for rendering
        """
        return self.indices

    def update_vertices(self, data):
        """Update vertex data.
        
        Args:
            data (np.ndarray or list): New vertex data
        
        Returns:
            None
        """
        if isinstance(data, np.ndarray):
            vertex_count = len(data) // Vertex.SIZE
            vertices = []
            for i in range(vertex_count):
                idx = i * Vertex.SIZE
                vertices.append(Vertex(
                    position=data[idx:idx+3],
                    colour=data[idx+3:idx+6],
                    normal=data[idx+6:idx+9]
                ))
            self.vertices = np.array(vertices, dtype=Vertex)
        else:
            self.vertices = np.array(data, dtype=Vertex)
        self.vertex_count = len(self.vertices)

    def update_indices(self, data):
        """Update index data.
        
        Args:
            data (np.ndarray or list): New index data
        
        Returns:
            None
        """
        self.indices = np.array(data, dtype=np.uint32)
        self.index_count = len(self.indices)

    def transform(self, translate=(0, 0, 0), rotate=(0, 0, 0), scale=(1, 1, 1)):
        """Apply transformation to the vertices in this order: scale, rotate, translate.
        
        Args:
            translate (tuple): XYZ translation values. Defaults to (0, 0, 0)
            rotate (tuple): XYZ rotation angles in radians. Defaults to (0, 0, 0)
            scale (tuple): XYZ scale factors. Defaults to (1, 1, 1)
        
        Returns:
            Shape: Self reference for method chaining
        """
        if all(v == 0 for v in translate) and all(v == 0 for v in rotate) and all(v == 1 for v in scale):
            return self

        transform = Transform(translate, rotate, scale)
        normal_matrix = np.linalg.inv(transform.transform_matrix()[:3, :3]).T

        for vertex in self.vertices:
            # Transform position
            vertex.position = transform.transform_position(vertex.position)
            # Transform normal
            vertex.normal = normal_matrix @ vertex.normal
            vertex.normal = vertex.normal / np.linalg.norm(vertex.normal)

        return self
    
    def clone(self):
        """Create a deep copy of this shape.
        
        Returns:
            Shape: New shape with copied vertex and index data
        """
        return Shape(
            [Vertex(v.position.copy(), v.colour.copy(), v.normal.copy()) 
             for v in self.vertices],
            self.indices.copy()
        )
    
    
class Shapes:
    """
    Factory class providing static methods to create various 3D shapes.
    All shapes are centreed at origin unless specified otherwise.
    Includes both solid and wireframe generation methods.
    """
    @staticmethod
    def create_blank():
        """Create a blank shape.
        
        Returns:
            Shape: Empty shape with no vertices or indices
        """
        return Shape()
    
    @staticmethod
    def create_grid(size, increment, colour):
        """Create a grid in the XY plane centreed at origin.
        
        Args:
            size (float): Total size of the grid
            increment (float): Space between grid lines
            colour (tuple): RGB colour for the grid lines
        
        Returns:
            Shape: Grid shape with line segments
        """
        vertices = []
        indices = []
        num_lines = int(size / increment) + 1
        
        for i in range(num_lines):
            x = i * increment - size/2
            vertices.append(Vertex([x, -size/2, 0], colour, [0, 0, 1]))
            vertices.append(Vertex([x, size/2, 0], colour, [0, 0, 1]))
            
            y = i * increment - size/2
            vertices.append(Vertex([-size/2, y, 0], colour, [0, 0, 1]))
            vertices.append(Vertex([size/2, y, 0], colour, [0, 0, 1]))
            
            index = i * 4
            indices.extend([index, index + 1, index + 2, index + 3])

        return Shape(vertices, indices)

    @staticmethod
    def create_point(position, colour):
        """Create a single point in 3D space.
        
        Args:
            position (tuple): XYZ coordinates of the point
            colour (tuple): RGB colour values
        
        Returns:
            Shape: Point shape with single vertex
        """
        vertices = [Vertex(position, colour, [0, 0, 1])]
        indices = [0]
        return Shape(vertices, indices)
    
    @staticmethod
    def create_points(positions, colour):
        """Create a series of points in 3D space.
        
        Args:
            positions (list[tuple]): List of XYZ coordinates for each point
            colour (tuple): RGB colour values
        
        Returns:
            Shape: Point shape with multiple vertices
        """
        vertices = [Vertex(position, colour, [0, 0, 1]) for position in positions]
        indices = list(range(len(vertices)))
        return Shape(vertices, indices)
    
    @staticmethod
    def create_line(p0, p1, colour):
        """Create a line segment between two points.
        
        Args:
            p0 (tuple): Start point XYZ coordinates
            p1 (tuple): End point XYZ coordinates
            colour (tuple): RGB colour values
        
        Returns:
            Shape: Line shape with two vertices
        """
        direction = np.array(p1) - np.array(p0)
        normal = np.cross(direction, [0, 0, 1])
        norm = np.linalg.norm(normal)
            
        if norm > 1e-6:  # If the normal not (close to) zero
            normal = normal / norm
        else:  # The line is parallel to z-axis, so we can use any perpendicular vector
            normal = np.cross(direction, [1, 0, 0])
            norm = np.linalg.norm(normal)
        
        vertices = [
            Vertex(p0, colour, normal),
            Vertex(p1, colour, normal)
        ]
        indices = [0, 1]
        return Shape(vertices, indices)

    @staticmethod
    def create_linestring(points, colour):
        """Create a connected series of line segments through points.
        
        Args:
            points (list): List of XYZ coordinates for each point
            colour (tuple): RGB colour values
        
        Returns:
            Shape: Combined line segments with shared vertices
            
        Raises:
            ValueError: If fewer than 2 points provided
        """
        if len(points) < 2:
            raise ValueError("Line string requires at least 2 points")
            
        vertices = []
        indices = []
        
        # Create vertices for each point
        for i, point in enumerate(points):
            # Skip first point as we'll handle it with pairs
            if i == 0:
                continue
                
            p0 = points[i-1]
            p1 = point
            
            # Calculate normal for this segment (same as create_line)
            direction = np.array(p1) - np.array(p0)
            normal = np.cross(direction, [0, 0, 1])
            norm = np.linalg.norm(normal)
                
            if norm > 1e-6:  # If the normal not (close to) zero
                normal = normal / norm
            else:  # The line is parallel to z-axis, so we can use any perpendicular vector
                normal = np.cross(direction, [1, 0, 0])
                normal = normal / np.linalg.norm(normal)
            
            # Add vertices for this segment
            if i == 1:  # First segment needs both vertices
                vertices.append(Vertex(p0, colour, normal))
            vertices.append(Vertex(p1, colour, normal))
            
            # Add indices to connect this segment
            base_idx = i - 1
            indices.extend([base_idx, base_idx + 1])
        
        return Shape(vertices, indices)

    @staticmethod
    def create_triangle(p1, p2, p3, colour):
        """Create a filled triangle from three points.
        
        Args:
            p1 (tuple): First vertex XYZ coordinates
            p2 (tuple): Second vertex XYZ coordinates
            p3 (tuple): Third vertex XYZ coordinates
            colour (tuple): RGB colour values
        
        Returns:
            Shape: Triangle shape with computed normal
        """
        v1, v2 = np.array(p2) - np.array(p1), np.array(p3) - np.array(p1)
        normal = np.cross(v1, v2)
        normal = normal / np.linalg.norm(normal)
        vertices = [
            Vertex(p1, colour, normal),
            Vertex(p2, colour, normal),
            Vertex(p3, colour, normal)
        ]
        indices = [0, 1, 2]
        return Shape(vertices, indices)

    @staticmethod
    def create_triangle_wireframe(p1, p2, p3, colour):
        """Create a triangle wireframe from three points.
        
        Args:
            p1 (tuple): First vertex XYZ coordinates
            p2 (tuple): Second vertex XYZ coordinates
            p3 (tuple): Third vertex XYZ coordinates
            colour (tuple): RGB colour values
        
        Returns:
            Shape: Combined line segments forming triangle outline
        """
        return Shapes.create_line(p1, p2, colour) + Shapes.create_line(p2, p3, colour) + Shapes.create_line(p3, p1, colour)

    @staticmethod
    def create_rectangle(position, width, height, colour):
        """Create a 2D rectangle in the XY plane.
        
        Args:
            position (tuple): XYZ coordinates of rectangle centre
            width (float): Total width of rectangle
            height (float): Total height of rectangle
            colour (tuple): RGB colour values
        
        Returns:
            Shape: Rectangle shape in XY plane
        """
        x, y, z = position[0], position[1], position[2]
        half_w, half_h = width / 2, height / 2
        normal = [0, 0, 1]
        vertices = [
            Vertex([x - half_w, y - half_h, z], colour, normal),
            Vertex([x + half_w, y - half_h, z], colour, normal),
            Vertex([x + half_w, y + half_h, z], colour, normal),
            Vertex([x - half_w, y + half_h, z], colour, normal)
        ]
        indices = [0, 1, 2, 2, 3, 0]
        return Shape(vertices, indices)

    @staticmethod
    def create_rectangle_target(position, width, height, edge_length, colour):
        """Create a target rectangle with corner edges in the XY plane.
        
        Args:
            position (tuple): XYZ coordinates of rectangle centre
            width (float): Total width of rectangle
            height (float): Total height of rectangle
            edge_length (float): Length of corner edges
            colour (tuple): RGB colour values
        
        Returns:
            Shape: Rectangle shape with corner edges
        """
        x, y, z = position[0], position[1], position[2]
        half_w, half_h = width / 2, height / 2
        normal = [0, 0, 1]  # Normal pointing outwards
        
        # Calculate edge ratios to avoid edges longer than the rectangle sides
        edge_ratio_w = min(edge_length / width, 0.5)        # TODO: This is unused
        edge_ratio_h = min(edge_length / height, 0.5)       # TODO: This is unused
        
        # Corner vertices
        corners = [
            [x - half_w, y - half_h, z],  # Bottom left
            [x + half_w, y - half_h, z],  # Bottom right
            [x + half_w, y + half_h, z],  # Top right
            [x - half_w, y + half_h, z]   # Top left
        ]
        
        vertices = []
        indices = []
        
        # Create two edges for each corner
        for i, corner in enumerate(corners):
            corner = np.array(corner)
            vertices.append(Vertex(corner.tolist(), colour, normal))  # Corner vertex
            
            # For horizontal edges: left for right corners, right for left corners
            h_direction = np.array([-1 if i in [1, 2] else 1, 0, 0])  # Left for corners 1,2, Right for corners 0,3
            h_point = corner + h_direction * edge_length
            vertices.append(Vertex(h_point.tolist(), colour, normal))
            
            # For vertical edges: down for top corners, up for bottom corners
            v_direction = np.array([0, -1 if i in [2, 3] else 1, 0])  # Down for corners 2,3, Up for corners 0,1
            v_point = corner + v_direction * edge_length
            vertices.append(Vertex(v_point.tolist(), colour, normal))
            
            # Add indices for the two edges from this corner
            base_idx = i * 3
            indices.extend([base_idx, base_idx + 1])  # Horizontal edge
            indices.extend([base_idx, base_idx + 2])  # Vertical edge
        
        return Shape(vertices, indices)

    @staticmethod
    def create_rectangle_wireframe(position, width, height, colour):
        """Create a 2D rectangle wireframe in the XY plane.
        
        Args:
            position (tuple): XYZ coordinates of rectangle centre
            width (float): Total width of rectangle
            height (float): Total height of rectangle
            colour (tuple): RGB colour values
        
        Returns:
            Shape: Rectangle wireframe shape
        """
        x, y, z = position[0], position[1], position[2]
        half_w, half_h = width / 2, height / 2
        normal = [0, 0, 1]  # Normal pointing outwards
        vertices = [
            Vertex([x - half_w, y - half_h, z], colour, normal),
            Vertex([x + half_w, y - half_h, z], colour, normal),
            Vertex([x + half_w, y + half_h, z], colour, normal),
            Vertex([x - half_w, y + half_h, z], colour, normal)
        ]
        indices = [0, 1, 1, 2, 2, 3, 3, 0]
        return Shape(vertices, indices)

    @staticmethod
    def create_circle(position, radius, segments, colour):
        """Create a filled circle in the XY plane.
        
        Args:
            position (tuple): XYZ coordinates of circle centre
            radius (float): Circle radius
            segments (int): Number of segments around circumference
            colour (tuple): RGB colour values
        
        Returns:
            Shape: Circle shape made of triangular segments
        """
        normal = [0, 0, 1]  # Normal pointing outwards
        vertices = [Vertex(position, colour, normal)]
        indices = []
        for i in range(segments):
            angle = 2 * np.pi * i / segments
            x = position[0] + radius * np.cos(angle)
            y = position[1] + radius * np.sin(angle)
            vertices.append(Vertex([x, y, position[2]], colour, normal))
            if i > 0:
                indices.extend([0, i, i + 1])
        indices.extend([0, segments, 1])
        return Shape(vertices, indices)
        
    @staticmethod
    def create_circle_wireframe(position, radius, segments, colour):
        """Create a circle wireframe in the XY plane.
        
        Args:
            position (tuple): XYZ coordinates of circle centre
            radius (float): Circle radius
            segments (int): Number of segments around circumference
            colour (tuple): RGB colour values
        
        Returns:
            Shape: Circle wireframe shape
        """
        normal = [0, 0, 1]  # Normal pointing outwards
        vertices = []
        indices = []
        for i in range(segments):
            angle = 2 * np.pi * i / segments
            x = position[0] + radius * np.cos(angle)
            y = position[1] + radius * np.sin(angle)
            vertices.append(Vertex([x, y, position[2]], colour, normal))
            indices.extend([i, (i + 1) % segments])
        return Shape(vertices, indices)

    @staticmethod
    def create_cube(position=(0,0,0), size=1.0, colour=(1,1,1)):
        """Create a cube.
        
        Args:
            position (tuple): XYZ coordinates of cube centre. Defaults to origin
            size (float): Length of cube sides. Defaults to 1.0
            colour (tuple): RGB colour values. Defaults to white
        
        Returns:
            Shape: Cube shape
        """
        s = size / 2
        x, y, z = position
        vertices = [
            # Front face
            Vertex([x-s, y-s, z+s], colour, [0, 0, 1]),
            Vertex([x+s, y-s, z+s], colour, [0, 0, 1]),
            Vertex([x+s, y+s, z+s], colour, [0, 0, 1]),
            Vertex([x-s, y+s, z+s], colour, [0, 0, 1]),
            # Back face
            Vertex([x-s, y-s, z-s], colour, [0, 0, -1]),
            Vertex([x+s, y-s, z-s], colour, [0, 0, -1]),
            Vertex([x+s, y+s, z-s], colour, [0, 0, -1]),
            Vertex([x-s, y+s, z-s], colour, [0, 0, -1]),
            # Left face
            Vertex([x-s, y-s, z-s], colour, [-1, 0, 0]),
            Vertex([x-s, y-s, z+s], colour, [-1, 0, 0]),
            Vertex([x-s, y+s, z+s], colour, [-1, 0, 0]),
            Vertex([x-s, y+s, z-s], colour, [-1, 0, 0]),
            # Right face
            Vertex([x+s, y-s, z+s], colour, [1, 0, 0]),
            Vertex([x+s, y-s, z-s], colour, [1, 0, 0]),
            Vertex([x+s, y+s, z-s], colour, [1, 0, 0]),
            Vertex([x+s, y+s, z+s], colour, [1, 0, 0]),
            # Top face
            Vertex([x-s, y+s, z+s], colour, [0, 1, 0]),
            Vertex([x+s, y+s, z+s], colour, [0, 1, 0]),
            Vertex([x+s, y+s, z-s], colour, [0, 1, 0]),
            Vertex([x-s, y+s, z-s], colour, [0, 1, 0]),
            # Bottom face
            Vertex([x-s, y-s, z-s], colour, [0, -1, 0]),
            Vertex([x+s, y-s, z-s], colour, [0, -1, 0]),
            Vertex([x+s, y-s, z+s], colour, [0, -1, 0]),
            Vertex([x-s, y-s, z+s], colour, [0, -1, 0])
        ]

        indices = [
            0, 1, 2, 2, 3, 0,    # Front face
            4, 7, 6, 6, 5, 4,    # Back face
            8, 9, 10, 10, 11, 8, # Left face
            12, 13, 14, 14, 15, 12, # Right face 
            16, 17, 18, 18, 19, 16, # Top face
            20, 21, 22, 22, 23, 20  # Bottom face
        ]

        return Shape(vertices, indices)

    @staticmethod
    def create_cube_wireframe(position=(0,0,0), size=1.0, colour=(1,1,1)):
        """Create a cube wireframe.
        
        Args:
            position (tuple): XYZ coordinates of cube centre. Defaults to origin
            size (float): Length of cube edges. Defaults to 1.0
            colour (tuple): RGB colour values. Defaults to white
        
        Returns:
            Shape: Cube wireframe shape with eight vertices and twelve edges
        """
        s = size / 2
        x, y, z = position
        normal = [0, 0, 1]  # Normal pointing outwards
        vertices = [
            Vertex([x-s, y-s, z-s], colour, normal),
            Vertex([x+s, y-s, z-s], colour, normal),
            Vertex([x+s, y+s, z-s], colour, normal),
            Vertex([x-s, y+s, z-s], colour, normal),
            Vertex([x-s, y-s, z+s], colour, normal),
            Vertex([x+s, y-s, z+s], colour, normal),
            Vertex([x+s, y+s, z+s], colour, normal),
            Vertex([x-s, y+s, z+s], colour, normal)
        ]

        indices = [
            0, 1, 1, 2, 2, 3, 3, 0,  # Back face
            4, 5, 5, 6, 6, 7, 7, 4,  # Front face
            0, 4, 1, 5, 2, 6, 3, 7   # Connecting edges
        ]

        return Shape(vertices, indices)


    @staticmethod
    def create_cylinder(position=(0,0,0), radius=0.5, height=1.0, segments=32, colour=(1,1,1)):
        """Create a cylinder.
        
        Args:
            position (tuple): XYZ coordinates of base centre. Defaults to origin
            radius (float): Radius of cylinder. Defaults to 0.5
            height (float): Height of cylinder. Defaults to 1.0
            segments (int): Number of segments around circumference. Defaults to 32
            colour (tuple): RGB colour values. Defaults to white
        
        Returns:
            Shape: Cylinder shape
        """
        vertices = []
        indices = []

        # Create vertices for the cylinder body
        for i in range(segments + 1):  # +1 to close the cylinder
            angle = 2 * np.pi * i / segments
            x = radius * np.cos(angle)
            y = radius * np.sin(angle)
            normal = np.array([x, y, 0])
            normal = normal / np.linalg.norm(normal)  # Normalize the normal
            
            # Bottom vertex
            vertices.append(Vertex([x, y, 0], colour, normal))
            # Top vertex
            vertices.append(Vertex([x, y, height], colour, normal))

        # Indices for the side faces
        for i in range(segments):
            i1 = i * 2
            i2 = (i * 2 + 2) % (segments * 2 + 2)
            i3 = i * 2 + 1
            i4 = (i * 2 + 3) % (segments * 2 + 2)
            indices.extend([i1, i2, i3, i2, i4, i3])

        cylinder = Shape(vertices, indices)
        bottom = Shapes.create_circle(position=(0,0,0), radius=radius, segments=segments, colour=colour).transform(rotate=(np.pi,0,0))
        top = Shapes.create_circle(position=(0,0,1), radius=radius, segments=segments, colour=colour)
        # Transform to position
        if position != (0,0,0):
            cylinder.transform(translate=position)
            bottom.transform(translate=position)
            top.transform(translate=position)
        return cylinder + bottom + top
    

    @staticmethod
    def create_cylinder_wireframe(position=(0,0,0), radius=0.5, height=1.0, segments=32, colour=(1,1,1)):
        """Create a cylinder wireframe.
        
        Args:
            position (tuple): XYZ coordinates of cylinder centre. Defaults to origin
            radius (float): Radius of cylinder. Defaults to 0.5
            segments (int): Number of segments around circumference. Defaults to 32
            colour (tuple): RGB colour values. Defaults to white
        
        Returns:
            Shape: Combined wireframe for cylinder outline
        """
        bottom = Shapes.create_circle_wireframe(position=position, radius=radius, segments=segments, colour=colour)
        top_position = np.array(position) + np.array([0,0,height])
        top = Shapes.create_circle_wireframe(position=top_position, radius=radius, segments=segments, colour=colour)
        return bottom + top
    
    @staticmethod
    def create_cone(position=(0,0,0), radius=0.5, height=1.0, segments=32, colour=(1,1,1)):
        """Create a cone.
        
        Args:
            position (tuple): XYZ coordinates of base centre. Defaults to origin
            radius (float): Radius of cone base. Defaults to 0.5
            height (float): Height of cone. Defaults to 1.0
            segments (int): Number of segments around base circumference. Defaults to 32
            colour (tuple): RGB colour values. Defaults to white
        
        Returns:
            Shape: Cone shape
        """
        assert isinstance(segments, int) and segments > 2, "segments must be an integer greater than 2"
        assert len(colour) == 3, "colour must be a tuple of 3 values"
        
        vertices = []
        indices = []
        normal_apex = [0, 0, 1]  # Normal pointing outwards
        # Apex
        vertices.append(Vertex([0, 0, height], colour, normal_apex))
        # Side vertices
        for i in range(segments):
            angle = 2 * np.pi * i / segments
            x = radius * np.cos(angle)
            y = radius * np.sin(angle)
            normal = [x, y, 0.5]  # Adjusted normal for smooth shading
            normal = normal / np.linalg.norm(normal)
            vertices.append(Vertex([x, y, 0], colour, normal))

        # Base centre vertex
        vertices.append(Vertex([0, 0, 0], colour, [0, 0, -1]))  # Base centre with normal pointing down

        # Indices for the sides
        for i in range(segments):
            i1 = i + 1
            i2 = (i + 1) % segments + 1
            indices.extend([0, i1, i2])

        cone = Shape(vertices, indices)
        # Create bottom circle
        bottom = Shapes.create_circle(position=(0,0,0), radius=0.5, segments=segments, colour=colour).transform(rotate=(np.pi,0,0))
        # Transform to position
        if position != (0,0,0):
            cone.transform(translate=position)
            bottom.transform(translate=position)
        return cone + bottom

    @staticmethod
    def create_cone_wireframe(position=(0,0,0), radius=0.5, segments=32, colour=(1,1,1)):
        """Create a cone wireframe.
        
        Args:
            position (tuple): XYZ coordinates of cone base centre. Defaults to origin
            radius (float): Radius of cone base. Defaults to 0.5
            segments (int): Number of segments around base circumference. Defaults to 32
            colour (tuple): RGB colour values. Defaults to white
        
        Returns:
            Shape: Cone wireframe shape
        """
        return Shapes.create_circle_wireframe(position=position, radius=radius, segments=segments, colour=colour)

    @staticmethod
    def create_sphere(radius, subdivisions, colour, position=(0,0,0)):
        """Create a sphere.
        
        Args:
            radius (float): Sphere radius
            subdivisions (int): Number of subdivision iterations
            colour (tuple): RGB colour values
            position (tuple): XYZ coordinates of sphere centre. Defaults to origin
        
        Returns:
            Shape: Sphere shape with normalized vertices
        """
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
                
                v12 = Shapes.normalize([(v1[0] + v2[0])/2, (v1[1] + v2[1])/2, (v1[2] + v2[2])/2])
                v23 = Shapes.normalize([(v2[0] + v3[0])/2, (v2[1] + v3[1])/2, (v2[2] + v3[2])/2])
                v31 = Shapes.normalize([(v3[0] + v1[0])/2, (v3[1] + v1[1])/2, (v3[2] + v1[2])/2])
                
                vertices.extend([v12, v23, v31])
                
                i1, i2, i3 = indices[i], indices[i+1], indices[i+2]
                i12, i23, i31 = len(vertices) - 3, len(vertices) - 2, len(vertices) - 1
                
                new_indices.extend([i1, i12, i31, i2, i23, i12, i3, i31, i23, i12, i23, i31])
            
            indices = new_indices

        # Normalize all vertices to the sphere surface and create Vertex objects
        vertex_objects = []
        for v in vertices:
            normalized = Shapes.normalize(v)
            position = [x * radius for x in normalized]
            vertex_objects.append(Vertex(position, colour, normalized))

        sphere = Shape(vertex_objects, indices)
        if position != (0,0,0):
            sphere.transform(translate=position)
        return sphere
    
    ###########################################################################
    ###########  MULTIPLE GEOMETRIES  ##########################################
    ###########################################################################
    
    @staticmethod
    def create_beam(p0, p1, width, height, colour, wireframe_colour=(1,1,1)):
        """Create a rectangular beam between two points.
        
        Args:
            p0 (tuple): Start point XYZ coordinates
            p1 (tuple): End point XYZ coordinates
            width (float): Width of beam cross-section
            height (float): Height of beam cross-section
            colour (tuple): RGB colour values for filled shape
            wireframe_colour (tuple): RGB colour values for wireframe. Defaults to white
        
        Returns:
            list[Shape]: [Filled beam shape, Wireframe shape]
        """
        p0, p1 = np.array(p0), np.array(p1)
        direction = p1 - p0
        length = np.linalg.norm(direction)
        
        if length == 0:
            return [Shape(), Shape()]  # Return empty shape if p0 and p1 are the same
            
        # Calculate transforms - note we use midpoint since cube is centreed at origin
        dimensions = (width, height) if direction[0] == 0 and direction[1] == 0 else (height, width) # width & height get swapped if beam is vertical
        translation, rotation, scale = Shapes.calculate_transform(p0, p1, dimensions)
        # Create body and wireframe using cube, offset by 0.5 in z-direction, and transform to between p0 and p1
        body = Shapes.create_cube(colour=colour) \
            .transform(translate=(0, 0, 0.5)) \
            .transform(translation, rotation, scale)
        wireframe = Shapes.create_cube_wireframe(colour=wireframe_colour) \
            .transform(translate=(0, 0, 0.5)) \
            .transform(translation, rotation, scale)
        
        return [body, wireframe]
            
    @staticmethod
    def create_arrow(p0, p1, dimensions: ArrowDimensions, colour, wireframe_colour=(1,1,1), segments=16):
        """Create a 3D arrow from p0 to p1.
        
        Args:
            p0 (tuple): Start point XYZ coordinates
            p1 (tuple): End point XYZ coordinates
            dimensions (ArrowDimensions): Arrow dimensions (shaft_radius, head_radius, head_length)
            colour (tuple): RGB colour values for filled shape
            wireframe_colour (tuple): RGB colour values for wireframe. Defaults to white
            segments (int): Number of segments for circular parts. Defaults to 16
        
        Returns:
            list[Shape]: [Filled arrow shape, Wireframe shape]
        """
        p0, p1 = np.array(p0), np.array(p1)
        direction = p1 - p0
        length = np.linalg.norm(direction)
        
        if length == 0:
            return [Shape(), Shape()]  # Return empty shape if p0 and p1 are the same
    
        unit_direction = direction / length
        pHead = p1 - unit_direction * dimensions.head_length

        # Calculate transforms
        translation_shaft, rotation_shaft, scale_shaft = Shapes.calculate_transform(
            p0, pHead, (dimensions.shaft_radius, dimensions.shaft_radius))
        translation_head, rotation_head, scale_head = Shapes.calculate_transform(
            pHead, p1, (dimensions.head_radius, dimensions.head_radius))

        # Create shaft (cylinder)
        shaft = Shapes.create_cylinder(segments=segments, colour=colour) \
            .transform(translation_shaft, rotation_shaft, scale_shaft)
        # Create arrowhead (cone)
        head = Shapes.create_cone(segments=segments, colour=colour) \
            .transform(translation_head, rotation_head, scale_head)
        body = shaft + head
        # Create shaft (cylinder)
        shaft_wireframe = Shapes.create_cylinder_wireframe(segments=segments, colour=wireframe_colour) \
            .transform(translation_shaft, rotation_shaft, scale_shaft)
        # Create arrowhead (cone)
        head_wireframe = Shapes.create_cone_wireframe(segments=segments, colour=wireframe_colour) \
            .transform(translation_head, rotation_head, scale_head)
        wireframe = shaft_wireframe + head_wireframe
        return [body, wireframe]
    
    @staticmethod
    def calculate_transform(p0, p1, cross_section=(1, 1)):
        """Calculate transformation between (0, 1) and (p0, p1).
        
        Args:
            p0 (tuple): Start point XYZ coordinates
            p1 (tuple): End point XYZ coordinates
            cross_section (tuple): XY scale factors. Defaults to (1, 1)
        
        Returns:
            tuple: (translation, rotation, scale) transformation parameters
        """
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
        """Normalize a vector to unit length.
        
        Args:
            v (list/tuple): Vector to normalize
        
        Returns:
            list: Normalized vector, or original if zero length
        """
        length = np.linalg.norm(v)
        return [x / length for x in v] if length != 0 else v


