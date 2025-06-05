"""
Core Shapes module providing classes for creating and manipulating 3D primitives.
Includes vertex data structures, shapes, and shape factory methods.
"""

import numpy as np
from dataclasses import dataclass
from OpenGL.GL import *
from pyglviewer.utils.colour import Colour
from pyglviewer.utils.transform import Transform
from pyglviewer.renderer.shader import Shader, DefaultShaders

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

    @staticmethod
    def vertex_size():
        """Get the size of a vertex in bytes."""
        return 9 * np.dtype(np.float32).itemsize
    
class Shape:
    
    """
    Container for 3D shape data including vertices and indices.
    Use the Shapes factory class for helper functions to create shape objects.
    Provides methods for combining and transforming shapes.
    Vertices are stored in their transformed state.

    Attributes:
        draw_type (int): OpenGL draw type (GL_TRIANGLES, GL_LINES, etc.)
        vertices (list[Vertex]): List of vertices defining the shape
        indices (np.array): Indices of the vertices to render
    """
    def __init__(self, draw_type, vertices=None, indices=None, shader=None):
        """
        Args:
            vertices (list[Vertex]): List of vertices
            indices (list[int]): List of indices
        """
        self.draw_type = draw_type
        self.shader = shader or DefaultShaders.default_shader
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

        if self.draw_type != other.draw_type:
            raise ValueError("Cannot combine shapes with different draw types")

        if self.shader != other.shader:
            raise ValueError("Cannot combine shapes with different shaders")

        # Combine vertices
        combined_vertices = np.concatenate((self.vertices, other.vertices))

        # Adjust indices for the second object
        max_index = len(self.vertices)
        adjusted_other_indices = [index + max_index for index in other.indices]

        # Combine indices
        combined_indices = np.concatenate((self.indices, adjusted_other_indices))

        result = Shape(self.draw_type, combined_vertices, combined_indices, self.shader)
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
            self.draw_type,
            [Vertex(v.position.copy(), v.colour.copy(), v.normal.copy()) 
             for v in self.vertices],
            self.indices.copy(),
            self.shader
        )


class Shapes:
    
    """
    Factory class providing static methods to create various 3D shapes.
    All shapes are centreed at origin unless specified otherwise.
    """    
    
    # Default values moved from Renderer
    DEFAULT_SEGMENTS = 16
    DEFAULT_SUBDIVISIONS = 4
    DEFAULT_POINT_COLOUR = Colour.BLACK
    DEFAULT_LINE_COLOUR = Colour.BLACK
    DEFAULT_FACE_COLOUR = Colour.WHITE
    DEFAULT_WIREFRAME_COLOUR = Colour.BLACK
    DEFAULT_ARROW_DIMENSIONS = ArrowDimensions(shaft_radius=0.03, head_radius=0.06, head_length=0.1)
    DEFAULT_AXIS_TICKS = [
        { 'increment': 1,    'tick_size': 0.08,  'line_width': 3, 'tick_colour': Colour.rgb(200, 200, 200) }, 
        { 'increment': 0.5,  'tick_size': 0.04,  'line_width': 3, 'tick_colour': Colour.rgb(200, 200, 200) }, 
        { 'increment': 0.1,  'tick_size': 0.02,  'line_width': 3, 'tick_colour': Colour.rgb(200, 200, 200) }
    ]
    DEFAULT_GRID_PARAMS = [ 
        {'increment': 0,    'colour': Colour.rgb(200, 200, 200), 'line_width': 3.0},
        {'increment': 1,    'colour': Colour.rgb(200, 200, 200), 'line_width': 1.0},
        {'increment': 0.1,  'colour': Colour.rgb(150, 150, 150), 'line_width': 1.0}
    ]
    
    @staticmethod
    def combine(shapes: list[Shape | list[Shape]]) -> list[Shape]:
        """Combine a list of shapes into a single shape.
        
        Args:
            shapes (list): List of shapes to combine. Can be either:
                - List of Shape objects
                - List of lists of Shape objects
        
        Returns:
            list[Shape]: List of combined shapes grouped by draw_type
        """
        # Flatten the list if it contains nested lists
        flat_shapes = []
        for shape in shapes:
            if isinstance(shape, list):
                flat_shapes.extend(shape)
            else:
                flat_shapes.append(shape)
            
        # Group shapes by draw_type
        shape_list = {}
        for shape in flat_shapes:
            if shape.draw_type not in shape_list:
                shape_list[shape.draw_type] = Shapes.blank(shape.draw_type)
            shape_list[shape.draw_type] += shape
        return list(shape_list.values())    
    
    @staticmethod
    def blank(draw_type):
        """Create a blank shape with default shader."""
        return Shape(draw_type)
    
    @staticmethod
    def point(position, colour=DEFAULT_POINT_COLOUR):
        """Create a single point in 3D space.
        
        Args:
            position (tuple): XYZ coordinates of the point
            colour (tuple): RGB colour values
        
        Returns:
            Shape: Point shape with single vertex
        """
        vertices = [Vertex(position, colour, [0, 0, 1])]
        indices = [0]
        return Shape(GL_POINTS, vertices, indices, DefaultShaders.default_point_shader)
    
    @staticmethod
    def points(positions, colour=DEFAULT_POINT_COLOUR):
        """Create a series of points in 3D space.
        
        Args:
            positions (list[tuple]): List of XYZ coordinates for each point
            colour (tuple): RGB colour values
        
        Returns:
            Shape: Point shape with multiple vertices
        """
        vertices = [Vertex(position, colour, [0, 0, 1]) for position in positions]
        indices = list(range(len(vertices)))
        return Shape(GL_POINTS, vertices, indices, DefaultShaders.default_point_shader)
    
    @staticmethod
    def line(p0, p1, colour=DEFAULT_LINE_COLOUR):
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
        return Shape(GL_LINES, vertices, indices)

    @staticmethod
    def linestring(points, colour=DEFAULT_LINE_COLOUR):
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
        
        return Shape(GL_LINES, vertices, indices)

    @staticmethod
    def triangle(p1, p2, p3, colour=DEFAULT_FACE_COLOUR, wireframe_colour=DEFAULT_WIREFRAME_COLOUR, show_body=True, show_wireframe=True):
        """Create a filled triangle from three points.
        
        Args:
            p1 (tuple): First vertex XYZ coordinates
            p2 (tuple): Second vertex XYZ coordinates
            p3 (tuple): Third vertex XYZ coordinates
            colour (tuple): RGB colour values
        
        Returns:
            Shape: Triangle shape with computed normal
        """ 
        shapes = []
        if show_body:
            shapes.append(Shapes.triangle_body(p1, p2, p3, colour))
        if show_wireframe:
            shapes.append(Shapes.triangle_wireframe(p1, p2, p3, wireframe_colour))
        return shapes
    
    @staticmethod
    def triangle_body(p1, p2, p3, colour=DEFAULT_FACE_COLOUR):
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
        return Shape(GL_TRIANGLES, vertices, indices)

    @staticmethod
    def triangle_wireframe(p1, p2, p3, colour=DEFAULT_WIREFRAME_COLOUR):
        """Create a triangle wireframe from three points.
        
        Args:
            p1 (tuple): First vertex XYZ coordinates
            p2 (tuple): Second vertex XYZ coordinates
            p3 (tuple): Third vertex XYZ coordinates
            colour (tuple): RGB colour values
        
        Returns:
            Shape: Combined line segments forming triangle outline
        """
        return Shapes.line(p1, p2, colour) + Shapes.line(p2, p3, colour) + Shapes.line(p3, p1, colour)

    @staticmethod
    def quad(p1, p2, p3, p4, colour=DEFAULT_FACE_COLOUR, wireframe_colour=DEFAULT_WIREFRAME_COLOUR, show_body=True, show_wireframe=True):
        """Create a quadrilateral.
        
        Args:
            p1 (tuple): First vertex XYZ coordinates
            p2 (tuple): Second vertex XYZ coordinates
            p3 (tuple): Third vertex XYZ coordinates
            p4 (tuple): Fourth vertex XYZ coordinates
            colour (tuple): RGB colour values
            wireframe_colour (tuple): RGB colour values
            show_body (bool): Whether to show the body of the quadrilateral
            show_wireframe (bool): Whether to show the wireframe of the quadrilateral
            
        Returns:
            Shape: Quadrilateral shape
        """
        shapes = []
        if show_body:
            shapes.append(Shapes.quad_body(p1, p2, p3, p4, colour))
        if show_wireframe:
            shapes.append(Shapes.quad_wireframe(p1, p2, p3, p4, wireframe_colour))
        return shapes
    
    @staticmethod
    def quad_body(p1, p2, p3, p4, colour=DEFAULT_FACE_COLOUR):
        """Create a filled quadrilateral from four points.
        
        Args:
            p1 (tuple): First vertex XYZ coordinates
            p2 (tuple): Second vertex XYZ coordinates
            p3 (tuple): Third vertex XYZ coordinates
            p4 (tuple): Fourth vertex XYZ coordinates
            colour (tuple): RGB colour values
        
        Returns:
            Shape: Quadrilateral shape
        """
        return Shapes.triangle_body(p1, p2, p3, colour) + Shapes.triangle_body(p1, p3, p4, colour)
    
    @staticmethod
    def quad_wireframe(p1, p2, p3, p4, colour=DEFAULT_WIREFRAME_COLOUR):
        """Create a quadrilateral wireframe from four points.
        
        Args:
            p1 (tuple): First vertex XYZ coordinates
            p2 (tuple): Second vertex XYZ coordinates
            p3 (tuple): Third vertex XYZ coordinates
            p4 (tuple): Fourth vertex XYZ coordinates
            colour (tuple): RGB colour values
        
        Returns:
            Shape: Quadrilateral wireframe shape
        """
        return Shapes.line(p1, p2, colour) + Shapes.line(p2, p3, colour) + Shapes.line(p3, p4, colour) + Shapes.line(p4, p1, colour)

    @staticmethod
    def rectangle(position, width, height, colour=DEFAULT_FACE_COLOUR, wireframe_colour=DEFAULT_WIREFRAME_COLOUR, show_body=True, show_wireframe=True):
        """Create a 2D rectangle.
        
        Args:
            position (tuple): XYZ coordinates of rectangle centre
            width (float): Total width of rectangle
            height (float): Total height of rectangle
            colour (tuple): RGB colour values
            wireframe_colour (tuple): RGB colour values
            show_body (bool): Whether to show the body of the rectangle
            show_wireframe (bool): Whether to show the wireframe of the rectangle

        Returns:
            Shape: Rectangle shape
        """
        shapes = []
        if show_body:
            shapes.append(Shapes.rectangle_body(position, width, height, colour))   
        if show_wireframe:
            shapes.append(Shapes.rectangle_wireframe(position, width, height, wireframe_colour))
        return shapes

    @staticmethod
    def rectangle_body(position, width, height, colour=DEFAULT_FACE_COLOUR):
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
        return Shape(GL_TRIANGLES, vertices, indices)

    @staticmethod
    def rectangle_wireframe(position, width, height, colour=DEFAULT_WIREFRAME_COLOUR):
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
        return Shape(GL_LINES, vertices, indices)

    @staticmethod
    def circle(position, radius, segments=DEFAULT_SEGMENTS, colour=DEFAULT_FACE_COLOUR, wireframe_colour=DEFAULT_WIREFRAME_COLOUR, show_body=True, show_wireframe=True):
        """Create a circle.
        
        Args:
            position (tuple): XYZ coordinates of circle centre
            radius (float): Circle radius
            segments (int): Number of segments around circumference
            colour (tuple): RGB colour values
            wireframe_colour (tuple): RGB colour values
            show_body (bool): Whether to show the body of the circle
            show_wireframe (bool): Whether to show the wireframe of the circle

        Returns:
            Shape: Circle shape
        """
        shapes = []
        if show_body:
            shapes.append(Shapes.circle_body(position, radius, segments, colour))
        if show_wireframe:
            shapes.append(Shapes.circle_wireframe(position, radius, segments, wireframe_colour))
        return shapes

    @staticmethod
    def circle_body(position, radius, segments=DEFAULT_SEGMENTS, colour=DEFAULT_FACE_COLOUR):
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
        return Shape(GL_TRIANGLES, vertices, indices)
        
    @staticmethod
    def circle_wireframe(position, radius, segments=DEFAULT_SEGMENTS, colour=DEFAULT_WIREFRAME_COLOUR):
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
        return Shape(GL_LINES, vertices, indices)


    @staticmethod
    def cube(position=(0,0,0), size=1.0, colour=DEFAULT_FACE_COLOUR, wireframe_colour=DEFAULT_WIREFRAME_COLOUR, show_body=True, show_wireframe=True):
        """Create a cube.
        
        Args:
            position (tuple): XYZ coordinates of cube centre. Defaults to origin
            size (float): Length of cube sides. Defaults to 1.0 
            colour (tuple): RGB colour values. Defaults to white
            wireframe_colour (tuple): RGB colour values. Defaults to white
            show_body (bool): Whether to show the body of the cube
            show_wireframe (bool): Whether to show the wireframe of the cube
        
        Returns:
            Shape: Cube shape
        """
        shapes = []
        if show_body:
            shapes.append(Shapes.cube_body(position, size, colour))
        if show_wireframe:
            shapes.append(Shapes.cube_wireframe(position, size, wireframe_colour))
        return shapes
    
    @staticmethod
    def cube_body(position=(0,0,0), size=1.0, colour=DEFAULT_FACE_COLOUR):
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

        return Shape(GL_TRIANGLES, vertices, indices)

    @staticmethod
    def cube_wireframe(position=(0,0,0), size=1.0, colour=DEFAULT_WIREFRAME_COLOUR):
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

        return Shape(GL_LINES, vertices, indices)

    @staticmethod
    def cylinder(position=(0,0,0), radius=0.5, height=1.0, segments=DEFAULT_SEGMENTS, colour=DEFAULT_FACE_COLOUR, wireframe_colour=DEFAULT_WIREFRAME_COLOUR, show_body=True, show_wireframe=True):
        """Create a cylinder.
        
        Args:
            position (tuple): XYZ coordinates of base centre. Defaults to origin
            radius (float): Radius of cylinder. Defaults to 0.5
            height (float): Height of cylinder. Defaults to 1.0
            segments (int): Number of segments around circumference. Defaults to 32
            colour (tuple): RGB colour values. Defaults to white
            wireframe_colour (tuple): RGB colour values. Defaults to white
            show_body (bool): Whether to show the body of the cylinder
            show_wireframe (bool): Whether to show the wireframe of the cylinder
        """
        shapes = []
        if show_body:
            shapes.append(Shapes.cylinder_body(position, radius, height, segments, colour))
        if show_wireframe:
            shapes.append(Shapes.cylinder_wireframe(position, radius, height, segments, wireframe_colour))
        return shapes

    @staticmethod
    def cylinder_body(position=(0,0,0), radius=0.5, height=1.0, segments=DEFAULT_SEGMENTS, colour=DEFAULT_FACE_COLOUR):
        """Create a filled cylinder.
        
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

        # Cylinder body
        cylinder = Shape(GL_TRIANGLES, vertices, indices)
        # Bottom and top circle bodies + wireframes
        bottom = Shapes.circle_body(position=(0,0,0), radius=radius, segments=segments, colour=colour).transform(rotate=(np.pi,0,0))
        top = Shapes.circle_body(position=(0,0,height), radius=radius, segments=segments, colour=colour)
        body = cylinder + bottom + top
        # Transform to position
        if position != (0,0,0):
            body.transform(translate=position)
        return body
    
    @staticmethod
    def cylinder_wireframe(position=(0,0,0), radius=0.5, height=1.0, segments=DEFAULT_SEGMENTS, colour=DEFAULT_WIREFRAME_COLOUR):
        """Create a cylinder wireframe.
        
        Args:
            position (tuple): XYZ coordinates of cylinder centre. Defaults to origin
            radius (float): Radius of cylinder. Defaults to 0.5
            segments (int): Number of segments around circumference. Defaults to 32
            colour (tuple): RGB colour values. Defaults to white
        
        Returns:
            Shape: Combined wireframe for cylinder outline
        """
        bottom = Shapes.circle_wireframe(position=position, radius=radius, segments=segments, colour=colour)
        top_position = np.array(position) + np.array([0,0,height])
        top = Shapes.circle_wireframe(position=top_position, radius=radius, segments=segments, colour=colour)
        return bottom + top


    @staticmethod
    def prism(position=(0,0,0), radius=1, depth=1, colour=DEFAULT_FACE_COLOUR, wireframe_colour=DEFAULT_WIREFRAME_COLOUR, show_body=True, show_wireframe=True):
        """Create a prism.
        
        Args:
            position (tuple): XYZ coordinates of base centre. Defaults to origin
            height (float): Height of prism. Defaults to 1.0
            colour (tuple): RGB colour values. Defaults to white
            wireframe_colour (tuple): RGB colour values. Defaults to white
            show_body (bool): Whether to show the body of the prism
            show_wireframe (bool): Whether to show the wireframe of the prism

        Returns:
            Shape: Prism shape
        """
        shapes = []
        if show_body:
            shapes.append(Shapes.prism_body(position, radius, depth, colour))
        if show_wireframe:
            shapes.append(Shapes.prism_wireframe(position, radius, depth, wireframe_colour))
        return shapes
            
    @staticmethod
    def prism_body(position=(0,0,0), radius=1, depth=1, colour=DEFAULT_FACE_COLOUR):
        """Create a prism body.
        
        Args:
            position (tuple): XYZ coordinates of base centre. Defaults to origin
            height (float): Height of prism. Defaults to 1.0
            depth (float): Depth of prism. Defaults to 1.0
            colour (tuple): RGB colour values. Defaults to white
            
        Returns:
            Shape: Prism body shape
        """
        p1 = np.array([0, radius/2, 0])
        p2 = np.array([-0.866 * radius/2, -0.5 * radius/2, 0])
        p3 = np.array([0.866 * radius/2, -0.5 * radius/2, 0])
        z = np.array([0, 0, depth/2])
        # Top and bottom triangles
        top = Shapes.triangle_body(p1+z, p2+z, p3+z, colour)
        bottom = Shapes.triangle_body(p1-z, p3-z, p2-z, colour)
        # Side quads
        side_1 = Shapes.quad_body(p1+z, p1-z, p2-z, p2+z, colour)
        side_2 = Shapes.quad_body(p2+z, p2-z, p3-z, p3+z, colour)
        side_3 = Shapes.quad_body(p3+z, p3-z, p1-z, p1+z, colour)
        return (top + bottom + side_1 + side_2 + side_3).transform(translate=position)
    
    @staticmethod
    def prism_wireframe(position=(0,0,0), radius=1, depth=1, colour=DEFAULT_WIREFRAME_COLOUR):
        """Create a prism wireframe.
        
        Args:
            position (tuple): XYZ coordinates of base centre. Defaults to origin
            height (float): Height of prism. Defaults to 1.0
            colour (tuple): RGB colour values. Defaults to white
            
        Returns:
            Shape: Prism wireframe shape
        """
        p1 = np.array([0, radius/2, 0])
        p2 = np.array([-0.866 * radius/2, -0.5 * radius/2, 0])
        p3 = np.array([0.866 * radius/2, -0.5 * radius/2, 0])
        z = np.array([0, 0, depth/2])
        top = Shapes.triangle_wireframe(p1+z, p2+z, p3+z, colour)
        bottom = Shapes.triangle_wireframe(p1-z, p3-z, p2-z, colour)
        line_1 = Shapes.line(p1+z, p1-z, colour) 
        line_2 = Shapes.line(p2+z, p2-z, colour)
        line_3 = Shapes.line(p3+z, p3-z, colour)
        return (top + bottom + line_1 + line_2 + line_3).transform(translate=position)
    
    @staticmethod
    def cone(position=(0,0,0), radius=0.5, height=1.0, segments=DEFAULT_SEGMENTS, colour=DEFAULT_FACE_COLOUR, wireframe_colour=DEFAULT_WIREFRAME_COLOUR, show_body=True, show_wireframe=True):
        """Create a cone.
        
        Args:
            position (tuple): XYZ coordinates of base centre. Defaults to origin
            radius (float): Radius of cone base. Defaults to 0.5
            height (float): Height of cone. Defaults to 1.0
            segments (int): Number of segments around base circumference. Defaults to 32
            colour (tuple): RGB colour values. Defaults to white
            wireframe_colour (tuple): RGB colour values. Defaults to white
            show_body (bool): Whether to show the body of the cone
            show_wireframe (bool): Whether to show the wireframe of the cone

        Returns:
            Shape: Cone shape
        """
        shapes = []
        if show_body:
            shapes.append(Shapes.cone_body(position, radius, height, segments, colour))
        if show_wireframe:
            shapes.append(Shapes.cone_wireframe(position, radius, segments, wireframe_colour))
        return shapes
            
    @staticmethod
    def cone_body(position=(0,0,0), radius=0.5, height=1.0, segments=DEFAULT_SEGMENTS, colour=DEFAULT_FACE_COLOUR):
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

        cone = Shape(GL_TRIANGLES, vertices, indices)
        # Create bottom circle
        base_circle = Shapes.circle_body(position=(0,0,0), radius=0.5, segments=segments, colour=colour).transform(rotate=(np.pi,0,0))
        body = cone + base_circle
        # Transform to position
        if position != (0,0,0):
            body.transform(translate=position)
        return body

    @staticmethod
    def cone_wireframe(position=(0,0,0), radius=0.5, segments=DEFAULT_SEGMENTS, colour=DEFAULT_WIREFRAME_COLOUR):
        """Create a cone wireframe.
        
        Args:
            position (tuple): XYZ coordinates of cone base centre. Defaults to origin
            radius (float): Radius of cone base. Defaults to 0.5
            segments (int): Number of segments around base circumference. Defaults to 32
            colour (tuple): RGB colour values. Defaults to white
        
        Returns:
            Shape: Cone wireframe shape
        """
        return Shapes.circle_wireframe(position=position, radius=radius, segments=segments, colour=colour)

    @staticmethod
    def sphere(position=(0,0,0), radius=0.5, subdivisions=DEFAULT_SUBDIVISIONS, colour=DEFAULT_FACE_COLOUR):
        """Create a sphere.
        
        Args:
            radius (float): Sphere radius
            subdivisions (int): Number of subdivision iterations
            colour (tuple): RGB colour values
            position (tuple): XYZ coordinates of sphere centre. Defaults to origin
        
        Returns:
            Shape: Sphere shape with normalized vertices
        """
        
        def normalize(v):
            # Normalize a vector to unit length
            length = np.linalg.norm(v)
            return [x / length for x in v] if length != 0 else v

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
                
                v12 = normalize([(v1[0] + v2[0])/2, (v1[1] + v2[1])/2, (v1[2] + v2[2])/2])
                v23 = normalize([(v2[0] + v3[0])/2, (v2[1] + v3[1])/2, (v2[2] + v3[2])/2])
                v31 = normalize([(v3[0] + v1[0])/2, (v3[1] + v1[1])/2, (v3[2] + v1[2])/2])
                
                vertices.extend([v12, v23, v31])
                
                i1, i2, i3 = indices[i], indices[i+1], indices[i+2]
                i12, i23, i31 = len(vertices) - 3, len(vertices) - 2, len(vertices) - 1
                
                new_indices.extend([i1, i12, i31, i2, i23, i12, i3, i31, i23, i12, i23, i31])
            
            indices = new_indices

        # Normalize all vertices to the sphere surface and create Vertex objects
        vertex_objects = []
        for v in vertices:
            normalized = normalize(v)
            vertex_position = [x * radius for x in normalized]
            vertex_objects.append(Vertex(vertex_position, colour, normalized))

        sphere = Shape(GL_TRIANGLES, vertex_objects, indices)
        if position != (0,0,0):
            sphere.transform(translate=position)
        return sphere
    
    @staticmethod
    def grid(size, increment, colour):
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

        return Shape(GL_LINES, vertices, indices)

    # # TODO: Move to grid class
    # def add_grid(self, size=5.0, grid_params=None, params = RenderParams()):
    #     """Add a grid in the XY plane.
        
    #     Parameters
    #     ----------
    #     size : float, optional
    #         Grid size (default: 5.0)
    #     grid_params : list, optional
    #         List of grid parameters for different detail levels
    #         Each dict contains: increment, colour, line_width (overrides RenderParams.line_width)
    #     params : RenderParams, optional
    #         Rendering parameters

    #     Returns
    #     -------
    #     ObjectContainer
    #         Collection containing grid objects at different detail levels
    #     """
    #     grid_params = grid_params or self.default_grid_params
    #     objects = {}
        
    #     for n, grid_level in enumerate(grid_params):
    #         increment = grid_level['increment']
    #         colour = grid_level['colour']
    #         line_width = grid_level['line_width'] or params.line_width
            
            
    #         # Create new params with updated line width
    #         level_params = replace(params, line_width=line_width)
            
    #         grid_shape = Shapes.create_blank(GL_LINES)
            
    #         if increment == 0:
    #             # Draw main axes
    #             grid_shape += Shapes.create_line((-size, 0, 0), (size, 0, 0), colour)
    #             grid_shape += Shapes.create_line((0, -size, 0), (0, size, 0), colour)
    #         else:
    #             # Draw regular grid lines
    #             for i in np.arange(-size + increment, size + increment/2, increment):
    #                 if abs(i) < 1e-10:  # Skip centre lines
    #                     continue
                        
    #                 grid_shape += Shapes.create_line((i, -size, 0), (i, size, 0), colour)
    #                 grid_shape += Shapes.create_line((-size, i, 0), (size, i, 0), colour)

    #         if grid_shape is not None:
    #             grid_shape = grid_shape.transform(params.translate, params.rotate, params.scale)
    #             grid_object = self.add_object(grid_shape, level_params)
            
    #             objects[f'grid-{n}'] = grid_object
        
    #     return ObjectContainer(objects)














    @staticmethod
    def target(position, size, edge_length, colour):
        """Create a target around a 3D shape.
        
        Args:
            position (tuple): XYZ coordinates of shape centre
            size (tuple): XYZ size of shape (width, height, length)
            edge_length (float): Length of corner edges
            colour (tuple): RGB colour values
        
        Returns:
            Shape: 3D target shape with corner edges
        """
        x, y, z = position[0], position[1], position[2]
        width, height, length = size
        half_w, half_h, half_l = width / 2, height / 2, length / 2
        
        # Define all 8 corners of the box
        corners = [
            # Front face (z + half_l)
            [x - half_w, y - half_h, z + half_l],  # Front bottom left  (0)
            [x + half_w, y - half_h, z + half_l],  # Front bottom right (1)
            [x + half_w, y + half_h, z + half_l],  # Front top right    (2)
            [x - half_w, y + half_h, z + half_l],  # Front top left     (3)
            # Back face (z - half_l)
            [x - half_w, y - half_h, z - half_l],  # Back bottom left   (4)
            [x + half_w, y - half_h, z - half_l],  # Back bottom right  (5)
            [x + half_w, y + half_h, z - half_l],  # Back top right     (6)
            [x - half_w, y + half_h, z - half_l],  # Back top left      (7)
        ]
        
        vertices = []
        indices = []
        
        # Create three edges for each corner
        for i, corner in enumerate(corners):
            corner = np.array(corner)
            vertices.append(Vertex(corner.tolist(), colour, [0, 0, 1]))  # Corner vertex
            
            # For horizontal edges (along x): left for right corners, right for left corners
            h_direction = np.array([(-1 if i in [1, 2, 5, 6] else 1), 0, 0])
            h_point = corner + h_direction * min(edge_length, width / 2)
            vertices.append(Vertex(h_point.tolist(), colour, [0, 1, 0]))
            
            # For vertical edges (along y): down for top corners, up for bottom corners
            v_direction = np.array([0, (-1 if i in [2, 3, 6, 7] else 1), 0])
            v_point = corner + v_direction * min(edge_length, height / 2)
            vertices.append(Vertex(v_point.tolist(), colour, [1, 0, 0]))
            
            # For depth edges (along z): back for front corners, forward for back corners
            d_direction = np.array([0, 0, (-1 if i < 4 else 1)])
            d_point = corner + d_direction * min(edge_length, length / 2)
            vertices.append(Vertex(d_point.tolist(), colour, [1, 1, 0]))
            
            # Add indices for the three edges from this corner
            base_idx = i * 4  # Now 4 vertices per corner (corner + 3 edge endpoints)
            indices.extend([
                base_idx, base_idx + 1,  # Horizontal edge
                base_idx, base_idx + 2,  # Vertical edge
                base_idx, base_idx + 3   # Depth edge
            ])
        
        return Shape(GL_LINES, vertices, indices)

    
    @staticmethod
    def scatter(x, y, colour=DEFAULT_POINT_COLOUR):
        """Create a scatter plot of x,y points.
        
        Parameters
        ----------
        x : float or array-like
            X coordinates
        y : float or array-like
            Y coordinates
        colour : Colour, optional
            Point colour

        Returns
        -------
        RenderObject
            Points render object
        """
        x = np.atleast_1d(x)
        y = np.atleast_1d(y)
        
        if len(x) != len(y):
            raise ValueError("x and y must have same length")
        points = np.column_stack((x, y, np.zeros_like(x)))
        
        # Use point shader if not specified
        return Shapes.points(points, colour)

    @staticmethod
    def plot(x, y, colour=DEFAULT_LINE_COLOUR):
        """Plot a line through a series of x,y points.
        
        Parameters
        ----------
        x : float or array-like
            X coordinates
        y : float or array-like
            Y coordinates
        colour : Colour, optional
            Line colour (default: white)
        params : RenderParams, optional
            Rendering parameters

        Returns
        -------
        RenderObject
            Line render object
        """
        x = np.atleast_1d(x)
        y = np.atleast_1d(y)
        
        if len(x) != len(y):
            raise ValueError("x and y must have same length")
        
        points = np.column_stack((x, y, np.zeros_like(x)))
        return Shapes.linestring(points, colour)
    
    ###########################################################################
    ###########  MULTIPLE GEOMETRIES  #########################################
    
    @staticmethod
    def beam(p0, p1, width, height, colour=DEFAULT_FACE_COLOUR, wireframe_colour=DEFAULT_WIREFRAME_COLOUR, show_body=True, show_wireframe=True):
        """Create a rectangular beam between two points.
        
        Args:
            p0 (tuple): Start point XYZ coordinates
            p1 (tuple): End point XYZ coordinates
            width (float): Width of beam cross-section
            height (float): Height of beam cross-section
            colour (tuple): RGB colour values for filled shape
            wireframe_colour (tuple): RGB colour values for wireframe. Defaults to white
            show_body (bool): Whether to show the body of the beam
            show_wireframe (bool): Whether to show the wireframe of the beam

        Returns:
            list[Shape]: [Filled beam shape, Wireframe shape]
        """
        p0, p1 = np.array(p0), np.array(p1)
        direction = p1 - p0
        length = np.linalg.norm(direction)
        
        if length == 0:
            return [Shape(GL_TRIANGLES), Shape(GL_LINES)]  # Return empty shape if p0 and p1 are the same
            
        # Calculate transforms - note we use midpoint since cube is centreed at origin
        dimensions = (width, height) if direction[0] == 0 and direction[1] == 0 else (height, width) # width & height get swapped if beam is vertical
        translation, rotation, scale = Shapes._calculate_transform(p0, p1, dimensions)
        # Create body and wireframe using cube, offset by 0.5 in z-direction, and transform to between p0 and p1
        shapes = []
        if show_body:
            body = Shapes.cube_body(colour=colour) \
                .transform(translate=(0, 0, 0.5)) \
                .transform(translation, rotation, scale)
            shapes.append(body)
        if show_wireframe:
            wireframe = Shapes.cube_wireframe(colour=wireframe_colour) \
                .transform(translate=(0, 0, 0.5)) \
                .transform(translation, rotation, scale)
            shapes.append(wireframe)
        
        return shapes
            
    @staticmethod
    def arrow(p0, p1, dimensions=DEFAULT_ARROW_DIMENSIONS, colour=DEFAULT_FACE_COLOUR, wireframe_colour=DEFAULT_WIREFRAME_COLOUR, segments=DEFAULT_SEGMENTS, show_body=True, show_wireframe=True):
        """Create a 3D arrow from p0 to p1.
        
        Args:
            p0 (tuple): Start point XYZ coordinates
            p1 (tuple): End point XYZ coordinates
            dimensions (ArrowDimensions): Arrow dimensions (shaft_radius, head_radius, head_length)
            colour (tuple): RGB colour values for filled shape
            wireframe_colour (tuple): RGB colour values for wireframe. Defaults to white
            segments (int): Number of segments for circular parts. Defaults to 16
            show_body (bool): Whether to show the body of the arrow
            show_wireframe (bool): Whether to show the wireframe of the arrow

        Returns:
            list[Shape]: [Filled arrow shape, Wireframe shape]
        """
        p0, p1 = np.array(p0), np.array(p1)
        direction = p1 - p0
        length = np.linalg.norm(direction)
        
        if length == 0:
            return [Shape(GL_TRIANGLES), Shape(GL_LINES)]  # Return empty shape if p0 and p1 are the same
    
        unit_direction = direction / length
        pHead = p1 - unit_direction * dimensions.head_length

        # Calculate transforms
        translation_shaft, rotation_shaft, scale_shaft = Shapes._calculate_transform(
            p0, pHead, (dimensions.shaft_radius, dimensions.shaft_radius))
        translation_head, rotation_head, scale_head = Shapes._calculate_transform(
            pHead, p1, (dimensions.head_radius, dimensions.head_radius))

        shapes = []
        if show_body:
            # Create shaft (cylinder)
            shaft = Shapes.cylinder_body(segments=segments, colour=colour) \
                .transform(translation_shaft, rotation_shaft, scale_shaft)
            # Create arrowhead (cone)
            head = Shapes.cone_body(segments=segments, colour=colour) \
                .transform(translation_head, rotation_head, scale_head)
            body = shaft + head
            shapes.append(body)
        if show_wireframe:
            # Create shaft (cylinder)
            shaft_wireframe = Shapes.cylinder_wireframe(segments=segments, colour=wireframe_colour) \
                .transform(translation_shaft, rotation_shaft, scale_shaft)
            # Create arrowhead (cone)
            head_wireframe = Shapes.cone_wireframe(segments=segments, colour=wireframe_colour) \
                .transform(translation_head, rotation_head, scale_head)
            wireframe = shaft_wireframe + head_wireframe
            shapes.append(wireframe)
        return shapes
    
    @staticmethod
    def axis(size=1.0, origin_radius=0.035, arrow_dimensions=DEFAULT_ARROW_DIMENSIONS,
                 origin_colour=Colour.BLACK, wireframe_colour=DEFAULT_WIREFRAME_COLOUR,
                 segments=DEFAULT_SEGMENTS, subdivisions=DEFAULT_SUBDIVISIONS, show_body=True, show_wireframe=True):
        """Add coordinate axis arrows.
        
        Parameters
        ----------
        size : float, optional
            Length of axis arrows (default: 1.0)
        origin_radius : float, optional
            Radius of origin sphere (default: 0.035)
        arrow_dimensions : ArrowDimensions, optional
            Arrow dimensions
        origin_colour : Colour, optional
            Colour of origin sphere (default: BLACK)
        wireframe_colour : Colour, optional
            Colour of wireframe (default: BLACK)
        segments : int, optional
            Number of segments for circular parts. Defaults to 16
        subdivisions : int, optional
            Number of subdivisions for sphere. Defaults to 4
        show_body : bool, optional
            Whether to show body of axis arrows. Defaults to True
        show_wireframe : bool, optional
            Whether to show wireframe of axis arrows. Defaults to True
        

        Returns
        -------
        list[Shape]
            Collection containing 'body' and 'wireframe' shapes
        """
        return Shapes.combine([
            Shapes.arrow((0,0,0), (size,0,0), arrow_dimensions, (1,0,0), wireframe_colour, segments),
            Shapes.arrow((0,0,0), (0,size,0), arrow_dimensions, (0,1,0), wireframe_colour, segments),
            Shapes.arrow((0,0,0), (0,0,size), arrow_dimensions, (0,0,1), wireframe_colour, segments),
            Shapes.sphere(position=(0,0,0), radius=origin_radius, subdivisions=subdivisions, colour=origin_colour)
        ])

    @staticmethod
    def axis_ticks(size=5.0, tick_params=DEFAULT_AXIS_TICKS):
        """Add axis ticks in the XY plane.

        TODO: Update this function to use the new tick_params structure
        
        Parameters
        ----------
        size : float, optional
            Axis size (default: 5.0)
        tick_params : list, optional
            List of tick parameters for different detail levels
            Each dict contains: increment, tick_size, line_width (overrides RenderParams.line_width), tick_colour TODO: add line width

        Returns
        -------
        list[Shape]
            Collection containing tick shapes at different detail levels
        """
        shapes = []
        
        for n, tick_level in enumerate(tick_params):
            increment = tick_level['increment']
            tick_size = tick_level['tick_size']
            # line_width = tick_level['line_width'] # TODO: add line width
            tick_colour = tick_level['tick_colour']
            tick_shape = None
            
            for i in np.arange(-size + increment, size + increment/2, increment):
                if abs(i) < 1e-10:  # Skip centre
                    continue
                    
                x_tick = Shapes.line((i, 0, 0), (i, tick_size, 0), tick_colour)
                y_tick = Shapes.line((0, i, 0), (tick_size, i, 0), tick_colour)
                
                if tick_shape is None:
                    tick_shape = x_tick + y_tick
                else:
                    tick_shape = tick_shape + x_tick + y_tick

            if tick_shape is not None:
                shapes.append(tick_shape)
                
        return shapes
    
    @staticmethod
    def _calculate_transform(p0, p1, cross_section=(1, 1)):
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