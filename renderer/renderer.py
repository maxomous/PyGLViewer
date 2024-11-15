from OpenGL.GL import *
import numpy as np
from renderer.geometry import Geometry, Vertex
from utils.color import Color
from renderer.objects import BufferType, VertexBuffer, IndexBuffer, VertexArray, Object, ObjectCollection
from renderer.batch_renderer import BatchRenderer
from renderer.light import Light, default_lighting
from typing import Dict, List
from utils.config import Config
from renderer.shader import Shader, PointShape
from renderer.shader import vertex_shader_lighting, fragment_shader_lighting, vertex_shader_points, fragment_shader_points
# TODO: buffer_type is not really implemented for static buffer
# TODO: Remove the 1.01 scaling and replace with a input for every function


class Renderer:
    """OpenGL renderer for managing 3D objects, lights, and scene rendering.
    
    Handles creation and rendering of geometric objects,
    lighting setup, and camera transformations.
    Static objects are updated only once (or very rarely), dynamic objects update often/every frame
    """
    def __init__(self, config, static_max_vertices=10000, static_max_indices=30000, dynamic_max_vertices=10000, dynamic_max_indices=30000):
        """Initialize renderer with default settings and OpenGL state."""
        self.lights = []
        self.objects = []
        # Config file 
        config.add("background_colour", [0.21987, 0.34362, 0.40084], "Background colour")
        self.config = config

        # Default shaders
        self.default_shader = Shader(vertex_shader_lighting, fragment_shader_lighting)
        self.point_shader = Shader(vertex_shader_points, fragment_shader_points)
        
        # Set default values or pass arguments to add_x() functions individually
        self.default_point_size = 1.0
        self.default_line_width = 1.0
        self.default_segments = 16
        self.default_subdivisions = 4
        self.default_face_color = Color.WHITE
        self.default_wireframe_color = Color.BLACK
        self.default_arrow_dimensions = Renderer.ArrowDimensions(shaft_radius=0.03, head_radius=0.06, head_length=0.1)
        self.default_axis_ticks = [
            { 'increment': 1,    'tick_size': 0.08,   'line_width': 3, 'tick_color': Color.rgb(200, 200, 200) }, 
            { 'increment': 0.5,  'tick_size': 0.04,  'line_width': 3, 'tick_color': Color.rgb(200, 200, 200) }, 
            { 'increment': 0.1,  'tick_size': 0.02,  'line_width': 3, 'tick_color': Color.rgb(200, 200, 200) }
        ]
        self.default_grid_params = [ 
            {'increment': 0, 'color': Color.rgb(200, 200, 200), 'line_width': 3.0},
            {'increment': 1, 'color': Color.rgb(200, 200, 200), 'line_width': 1.0},
            {'increment': 0.1, 'color': Color.rgb(150, 150, 150), 'line_width': 1.0}
        ]

        # Initialize OpenGL state
        glEnable(GL_DEPTH_TEST)     # Enable depth testing
        glEnable(GL_CULL_FACE)      # Enable back-face culling
        glCullFace(GL_BACK)         # Cull back faces
        glEnable(GL_BLEND)            # Enable blending for transparent effects
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)   # Define how colours of transparent objects blend when overlapping 
                        
        self.view_matrix = None
        self.projection_matrix = None
        self.camera_position = None
        # Add static and dynamic batch renderers
        self.static_batch_renderer = BatchRenderer(max_vertices=static_max_vertices, max_indices=static_max_indices, buffer_type=BufferType.Static)
        self.dynamic_batch_renderer = BatchRenderer(max_vertices=dynamic_max_vertices, max_indices=dynamic_max_indices, buffer_type=BufferType.Dynamic)
        # Static objects should be updated only once (or very rarely), dynamic objects update every frame
        self.static_needs_update = True
        
    def get_selected_objects(self):
        """Get all selected objects."""
        return [obj for obj in self.objects if getattr(obj, 'selected', False)]
    
    def add_lights(self, lights):
        """Add multiple light sources to the scene.
        
        Parameters
        ----------
        lights : dict
            Dictionary of light data
        """
        for light_data in lights.values():
            self.lights.append(Light(**light_data))

    def get_lights(self):
        """Get all lights."""
        if not self.lights:
            self.add_lights(default_lighting)
        return self.lights

    def draw(self, view_matrix, projection_matrix, camera_position, lights):
        """Render all objects in the scene, using batching"""
        # Clear static batch renderer if needed
        if self.static_needs_update:
            self.static_batch_renderer.clear()
        # Clear dynamic batch renderer every frame
        self.dynamic_batch_renderer.clear()
        
        # Submit all objects to the batch renderer
        for obj in self.objects:
            # Add static objects only once
            if self.static_needs_update and obj.buffer_type == BufferType.Static:
                self.static_batch_renderer.add_object(obj)
            # Add dynamic objects every frame
            elif obj.buffer_type == BufferType.Dynamic:
                self.dynamic_batch_renderer.add_object(obj)

        # Render all static batched objects
        self.static_batch_renderer.render(view_matrix, projection_matrix, camera_position, lights)
        # Render all dynamic batched objects
        self.dynamic_batch_renderer.render(view_matrix, projection_matrix, camera_position, lights)
    
        # Reset to default state
        glEnable(GL_DEPTH_TEST)
        glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
        glLineWidth(1.0)
        glPointSize(1.0)
        self.static_needs_update = False

    def clear(self):
        """Clear the framebuffer with a dark teal background."""
        r, g, b = self.config["background_colour"]
        glClearColor(r, g, b, 1.0)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    def add_point(self, position, color, point_size=None, shape=PointShape.CIRCLE, buffer_type=BufferType.Static, selectable=True, shader=None):
        """Add a point primitive to the scene.
        
        Parameters
        ----------
        position : tuple
            3D position of point
        color : Color
            Point color
        point_size : float, optional
            Size in pixels (default is self.default_point_size)
        buffer_type : BufferType, optional
            Static or Dynamic buffer

        Returns
        -------
        RenderObject
            Point render object
        """
        geometry = Geometry.create_point(position, color)
        point = self.add_object(geometry, buffer_type, GL_POINTS, point_size=point_size, selectable=selectable, shader=shader)
        # Set point shape
        if shader is None:
            shader = self.point_shader
            shader.set_point_shape(shape) THIS IS NOT GOING TO WORK AS IT IS NOT IN THE LOOP
        return point

    def add_points(self, points, color=Color.WHITE, point_size=3.0, shape=PointShape.CIRCLE, buffer_type=BufferType.Static, 
                   translate=(0,0,0), rotate=(0,0,0), scale=(1,1,1), selectable=False, shader=None):
        """Add a series of points.
        
        Parameters
        ----------
        points : array-like
            Array of points (x,y,z)
        color : Color, optional
            Point color (default: white)
        point_size : float, optional
            Size of points (default: 3.0)
        buffer_type : BufferType, optional
            Static or Dynamic buffer
        translate : tuple, optional
            Translation vector (x,y,z)
        rotate : tuple, optional
            Rotation angles (x,y,z)
        scale : tuple, optional
            Scale factors (x,y,z)

        Returns
        -------
        RenderObject
            Points render object
        """
        geometry = Geometry.create_blank()
        for point in points:
            geometry = geometry + Geometry.create_point(point, color).transform(translate, rotate, scale)
        points = self.add_object(geometry, buffer_type, GL_POINTS, point_size=point_size, selectable=selectable, shader=shader)
        # Set point shape
        if shader is None:
            shader = self.point_shader
            shader.set_point_shape(shape)
        
        return points

    def add_line(self, p0, p1, color, line_width=None, buffer_type=BufferType.Static, 
                translate=(0,0,0), rotate=(0,0,0), scale=(1,1,1), selectable=True):
        """Add a line segment between two points.
        
        Parameters
        ----------
        p0 : tuple
            Start point
        p1 : tuple
            End point
        color : Color
            Line color
        line_width : float, optional
            Width in pixels (default is self.default_line_width)
        buffer_type : BufferType, optional
            Static or Dynamic buffer
        translate : tuple, optional
            Translation vector (x,y,z)
        rotate : tuple, optional
            Rotation angles (x,y,z)
        scale : tuple, optional
            Scale factors (x,y,z)

        Returns
        -------
        RenderObject
            Line render object
        """
        geometry = Geometry.create_line(p0, p1, color).transform(translate, rotate, scale)
        line = self.add_object(geometry, buffer_type, GL_LINES, line_width=line_width, selectable=selectable)
        return line

    def add_linestring(self, points, color=Color.WHITE, line_width=None, buffer_type=BufferType.Static, 
            translate=(0,0,0), rotate=(0,0,0), scale=(1,1,1), selectable=False):
        """Add a line through a series of points.
        
        Parameters
        ----------
        points : array-like
            Array of points (x,y,z)
        color : Color, optional
            Line color (default: white)
        line_width : float, optional
            Width of the line (default: 1.0)
        translate : tuple, optional
            Translation vector (x,y,z)
        rotate : tuple, optional
            Rotation angles (x,y,z)
        scale : tuple, optional
            Scale factors (x,y,z)

        Returns
        -------
        RenderObject
            Line render object
        """
        points = np.atleast_2d(points)
        
        if points.shape[1] != 3:
            raise ValueError("Points must have 3 values (x,y,z) per point")
            
        geometry = Geometry.create_linestring(points, color).transform(translate, rotate, scale)
        linestring = self.add_object(geometry, buffer_type, GL_LINES, line_width=line_width, selectable=selectable)
        return linestring

    def add_triangle(self, p1, p2, p3, color=None, wireframe_color=None, line_width=None,
                    buffer_type=BufferType.Static, show_body=True, show_wireframe=True, 
                    translate=(0,0,0), rotate=(0,0,0), scale=(1,1,1), selectable=True):
        """Add a triangle defined by three points.
        
        Parameters
        ----------
        p1, p2, p3 : tuple
            Triangle vertices
        color : Color, optional
            Fill color
        wireframe_color : Color, optional
            Outline color
        line_width : float, optional
            Outline width (default is self.default_line_width)
        buffer_type : BufferType, optional
            Static or Dynamic buffer
        show_body : bool, optional
            Show filled triangle
        show_wireframe : bool, optional
            Show outline
        translate : tuple, optional
            Translation vector (x,y,z)
        rotate : tuple, optional
            Rotation angles (x,y,z)
        scale : tuple, optional
            Scale factors (x,y,z)

        Returns
        -------
        ObjectCollection
            Collection containing 'body' and 'wireframe' objects
        """
        objects = {}
        if show_body:
            geometry = Geometry.create_triangle(p1, p2, p3, color or self.default_face_color).transform(translate, rotate, scale)
            objects['body'] = self.add_object(geometry, buffer_type, GL_TRIANGLES, selectable=selectable)
        if show_wireframe:
            geometry = Geometry.create_triangle_wireframe(p1, p2, p3, wireframe_color or self.default_wireframe_color).transform(translate, rotate, scale)
            objects['wireframe'] = self.add_object(geometry, buffer_type, GL_LINES, line_width=line_width, selectable=selectable)
        return ObjectCollection(objects)

    def add_rectangle(self, position, width, height, color=None, wireframe_color=None, line_width=None, 
                     buffer_type=BufferType.Static, show_body=True, show_wireframe=True, 
                     translate=(0,0,0), rotate=(0,0,0), scale=(1,1,1), selectable=True):
        """Add a rectangle in the XY plane.
        
        Parameters
        ----------
        position : tuple
            Bottom-left corner position (x,y)
        width : float
            Rectangle width
        height : float
            Rectangle height
        color : Color, optional
            Fill color
        wireframe_color : Color, optional
            Outline color
        line_width : float, optional
            Outline width (default is self.default_line_width)
        buffer_type : BufferType, optional
            Static or Dynamic buffer
        show_body : bool, optional
            Show filled rectangle
        show_wireframe : bool, optional
            Show outline
        translate : tuple, optional
            Translation vector (x,y,z)
        rotate : tuple, optional
            Rotation angles (x,y,z)
        scale : tuple, optional
            Scale factors (x,y,z)

        Returns
        -------
        ObjectCollection
            Collection containing 'body' and 'wireframe' objects
        """
        objects = {}
        if show_body:
            geometry = Geometry.create_rectangle(position[0], position[1], width, height, 
                                              color or self.default_face_color).transform(translate, rotate, scale)
            objects['body'] = self.add_object(geometry, buffer_type, GL_TRIANGLES, selectable=selectable)
        if show_wireframe:
            geometry = Geometry.create_rectangle_wireframe(position[0], position[1], width * 1.01, height * 1.01, 
                                                            wireframe_color or self.default_wireframe_color).transform(translate, rotate, scale)
            objects['wireframe'] = self.add_object(geometry, buffer_type, GL_LINES, line_width=line_width, selectable=selectable)
        return ObjectCollection(objects)

    def add_circle(self, position, radius, segments=None, color=None, wireframe_color=None, line_width=None, 
                  buffer_type=BufferType.Static, show_body=True, show_wireframe=True, 
                  translate=(0,0,0), rotate=(0,0,0), scale=(1,1,1), selectable=True ):
        """Add a circle in the XY plane.
        
        Parameters
        ----------
        position : tuple
            Center position
        radius : float
            Circle radius
        segments : int
            Number of segments in circle
        color : Color, optional
            Fill color
        wireframe_color : Color, optional
            Outline color
        line_width : float, optional
            Outline width (default is self.default_line_width)
        buffer_type : BufferType, optional
            Static or Dynamic buffer
        show_body : bool, optional
            Show filled circle
        show_wireframe : bool, optional
            Show outline
        translate : tuple, optional
            Translation vector (x,y,z)
        rotate : tuple, optional
            Rotation angles (x,y,z)
        scale : tuple, optional
            Scale factors (x,y,z)

        Returns
        -------
        ObjectCollection
            Collection containing 'body' and 'wireframe' objects
        """
        segments = segments or self.default_segments
        color = color or self.default_face_color
        wireframe_color = wireframe_color or self.default_wireframe_color
        
        objects = {}
        if show_body:
            geometry = Geometry.create_circle(position, radius, segments, color).transform(translate, rotate, scale)
            objects['body'] = self.add_object(geometry, buffer_type, GL_TRIANGLE_FAN, selectable=selectable)
        if show_wireframe:
            geometry = Geometry.create_circle_wireframe(position, radius * 1.01, segments, wireframe_color).transform(translate, rotate, scale)
            objects['wireframe'] = self.add_object(geometry, buffer_type, GL_LINE_LOOP, line_width=line_width, selectable=selectable)
        return ObjectCollection(objects)

    def add_cube(self, color=None, wireframe_color=None, line_width=None,
                buffer_type=BufferType.Static, show_body=True, show_wireframe=True, 
                translate=(0,0,0), rotate=(0,0,0), scale=(1,1,1), selectable=True):
        """Add a unit cube centered at origin.
        
        Parameters
        ----------
        color : Color, optional
            Fill color
        wireframe_color : Color, optional
            Outline color
        line_width : float, optional
            Outline width (default is self.default_line_width)
        buffer_type : BufferType, optional
            Static or Dynamic buffer
        show_body : bool, optional
            Show filled cube
        show_wireframe : bool, optional
            Show outline
        translate : tuple, optional
            Translation vector (x,y,z)
        rotate : tuple, optional
            Rotation angles (x,y,z)
        scale : tuple, optional
            Scale factors (x,y,z)

        Returns
        -------
        ObjectCollection
            Collection containing 'body' and 'wireframe' objects
        """
        color = color or self.default_face_color
        wireframe_color = wireframe_color or self.default_wireframe_color
        
        objects = {}
        if show_body:
            geometry = Geometry.create_cube(size=1.0, color=color).transform(translate, rotate, scale)
            objects['body'] = self.add_object(geometry, buffer_type, GL_TRIANGLES, selectable=selectable)
        if show_wireframe:
            geometry = Geometry.create_cube_wireframe(size=1.0, color=wireframe_color).transform(translate, rotate, scale)
            objects['wireframe'] = self.add_object(geometry, buffer_type, GL_LINES, line_width=line_width, selectable=selectable)
        return ObjectCollection(objects)

    def add_cylinder(self, color=None, wireframe_color=None, segments=None, line_width=None, 
                    buffer_type=BufferType.Static, show_body=True, show_wireframe=True, 
                    translate=(0,0,0), rotate=(0,0,0), scale=(1,1,1), selectable=True):
        """Add a unit cylinder centered at origin.
        
        Parameters
        ----------
        color : Color, optional
            Fill color
        wireframe_color : Color, optional
            Outline color
        segments : int, optional
            Number of segments around circumference
        line_width : float, optional
            Outline width (default is self.default_line_width)
        buffer_type : BufferType, optional
            Static or Dynamic buffer
        show_body : bool, optional
            Show filled cylinder
        show_wireframe : bool, optional
            Show outline
        translate : tuple, optional
            Translation vector (x,y,z)
        rotate : tuple, optional
            Rotation angles (x,y,z)
        scale : tuple, optional
            Scale factors (x,y,z)

        Returns
        -------
        ObjectCollection
            Collection containing 'body' and 'wireframe' objects
        """
        segments = segments or self.default_segments
        color = color or self.default_face_color
        wireframe_color = wireframe_color or self.default_wireframe_color
        
        objects = {}
        if show_body:
            geometry = Geometry.create_cylinder(segments, color).transform(translate, rotate, scale)
            objects['body'] = self.add_object(geometry, buffer_type, GL_TRIANGLES, selectable=selectable)
        if show_wireframe:
            geometry = Geometry.create_cylinder_wireframe(segments, wireframe_color).transform(translate, rotate, scale)
            objects['wireframe'] = self.add_object(geometry, buffer_type, GL_LINES, line_width=line_width, selectable=selectable)
        return ObjectCollection(objects)

    def add_cone(self, color=None, wireframe_color=None, segments=16, line_width=None,
                buffer_type=BufferType.Static, show_body=True, show_wireframe=True, 
                translate=(0,0,0), rotate=(0,0,0), scale=(1,1,1), selectable=True):
        """Add a unit cone centered at origin.
        
        Parameters
        ----------
        color : Color, optional
            Fill color
        wireframe_color : Color, optional
            Outline color
        segments : int, optional
            Number of segments around circumference
        line_width : float, optional
            Outline width (default is self.default_line_width)
        buffer_type : BufferType, optional
            Static or Dynamic buffer
        show_body : bool, optional
            Show filled cone
        show_wireframe : bool, optional
            Show outline
        translate : tuple, optional
            Translation vector (x,y,z)
        rotate : tuple, optional
            Rotation angles (x,y,z)
        scale : tuple, optional
            Scale factors (x,y,z)

        Returns
        -------
        ObjectCollection
            Collection containing 'body' and 'wireframe' objects
        """
        segments = segments or self.default_segments
        color = color or self.default_face_color
        wireframe_color = wireframe_color or self.default_wireframe_color
        
        objects = {}
        if show_body:
            geometry = Geometry.create_cone(segments, color).transform(translate, rotate, scale)
            objects['body'] = self.add_object(geometry, buffer_type, GL_TRIANGLES, selectable=selectable)
        if show_wireframe:
            geometry = Geometry.create_cone_wireframe(segments, wireframe_color).transform(translate, rotate, scale)
            objects['wireframe'] = self.add_object(geometry, buffer_type, GL_LINES, line_width=line_width, selectable=selectable)
        return ObjectCollection(objects)

    def add_sphere(self, radius, subdivisions=4, color=None, buffer_type=BufferType.Static, 
                  translate=(0,0,0), rotate=(0,0,0), scale=(1,1,1), selectable=True):
        """Add a sphere centered at origin.
        
        Parameters
        ----------
        radius : float
            Sphere radius
        subdivisions : int
            Number of recursive subdivisions (detail level)
        color : Color, optional
            Surface color
        buffer_type : BufferType, optional
            Static or Dynamic buffer
        translate : tuple, optional
            Translation vector (x,y,z)
        rotate : tuple, optional
            Rotation angles (x,y,z)
        scale : tuple, optional
            Scale factors (x,y,z)
        selectable : bool, optional
            Allow object to be selected

        Returns
        -------
        RenderObject
            Sphere render object
        """
        subdivisions = subdivisions or self.default_subdivisions
        color = color or self.default_face_color
        geometry = Geometry.create_sphere(radius, subdivisions, color).transform(translate, rotate, scale)
        sphere_body = self.add_object(geometry, buffer_type, GL_TRIANGLES, selectable=selectable)
        return sphere_body

    class ArrowDimensions:
        """Stores dimensions for arrow geometry.
        
        Parameters
        ----------
        shaft_radius : float, optional
            Radius of arrow shaft
        head_radius : float, optional
            Radius of arrow head base
        head_length : float, optional
            Length of arrow head
        """
        def __init__(self, shaft_radius=0.1, head_radius=0.2, head_length=0.4):
            self.shaft_radius = shaft_radius
            self.head_radius = head_radius
            self.head_length = head_length

    def add_arrow(self, p0, p1, arrow_dimensions=None, color=None, wireframe_color=None, segments=None,
                 buffer_type=BufferType.Static, show_body=True, show_wireframe=True, 
                 line_width=None, selectable=True):
        """Add an arrow from p0 to p1 with cylindrical shaft and conical head.
        
        Parameters
        ----------
        p0 : tuple
            Start point
        p1 : tuple
            End point
        shaft_radius : float, optional
            Shaft radius
        head_radius : float, optional
            Head radius
        head_length : float, optional
            Head length
        color : Color, optional
            Fill color
        wireframe_color : Color, optional
            Outline color
        segments : int, optional
            Number of segments in circular cross-sections
        buffer_type : BufferType, optional
            Static or Dynamic buffer
        show_body : bool, optional
            Show filled arrow
        show_wireframe : bool, optional
            Show outline
        line_width : float, optional
            Outline width (default is self.default_line_width)
        selectable : bool, optional
            Allow object to be selected

        Returns
        -------
        ObjectCollection
            Collection containing 'body' and 'wireframe' objects
        """
        segments = segments or self.default_segments
        arrow_dimensions = arrow_dimensions or self.default_arrow_dimensions
        color = color or self.default_face_color
        wireframe_color = wireframe_color or self.default_wireframe_color
        
        body, wireframe = Geometry.create_arrow(p0, p1, color, wireframe_color, arrow_dimensions.shaft_radius, 
                                                arrow_dimensions.head_radius, arrow_dimensions.head_length, segments)
        arrow_body = self.add_object(body, buffer_type, GL_TRIANGLES, selectable=selectable) if show_body else None
        arrow_wireframe = self.add_object(wireframe, buffer_type, GL_LINES, line_width=line_width, selectable=selectable) if show_wireframe else None
        return ObjectCollection({'body': arrow_body, 'wireframe': arrow_wireframe})

    def add_axis(self, size=1.0, arrow_dimensions=None, segments=None, 
                origin_radius=0.035, origin_subdivisions=None, 
                origin_color=Color.BLACK, wireframe_color=None, buffer_type=BufferType.Static, 
                show_body=True, show_wireframe=True, line_width=None, translate=(0,0,0), rotate=(0,0,0), 
                scale=(1,1,1), selectable=False):
        """Add coordinate axis arrows with sphere at origin.

        Creates RGB arrows along X, Y, Z axes with black sphere at origin.

        Parameters
        ----------
        size : float, optional
            Length of axis arrows
        arrow_dimensions : ArrowDimensions, optional
            Dimensions for axis arrows
        origin_radius : float, optional
            Radius of origin sphere
        origin_subdivisions : int, optional
            Subdivision level of origin sphere
        origin_color : Color, optional
            Color of origin sphere
        wireframe_color : Color, optional
            Outline color
        buffer_type : BufferType, optional
            Static or Dynamic buffer
        show_body : bool, optional
            Show filled geometry
        show_wireframe : bool, optional
            Show outlines
        line_width : float, optional
            Outline width (default is self.default_line_width)
        translate : tuple, optional
            Translation vector (x,y,z)
        rotate : tuple, optional
            Rotation angles (x,y,z)
        scale : tuple, optional
            Scale factors (x,y,z)
        selectable : bool, optional
            Allow object to be selected

        Returns
        -------
        ObjectCollection
            Collection containing 'body' and 'wireframe' objects
        """
        segments = segments or self.default_segments
        origin_subdivisions = origin_subdivisions or self.default_subdivisions
        arrow_dimensions = arrow_dimensions or self.default_arrow_dimensions
        wireframe_color = wireframe_color or self.default_wireframe_color
        
        x_geometry, x_wireframe = Geometry.create_arrow((0,0,0), (size,0,0), (1,0,0), wireframe_color, arrow_dimensions.shaft_radius, 
                                                      arrow_dimensions.head_radius, arrow_dimensions.head_length, segments)
        y_geometry, y_wireframe = Geometry.create_arrow((0,0,0), (0,size,0), (0,1,0), wireframe_color, arrow_dimensions.shaft_radius, 
                                                      arrow_dimensions.head_radius, arrow_dimensions.head_length, segments)
        z_geometry, z_wireframe = Geometry.create_arrow((0,0,0), (0,0,size), (0,0,1), wireframe_color, arrow_dimensions.shaft_radius, 
                                                      arrow_dimensions.head_radius, arrow_dimensions.head_length, segments)
        
        origin_geometry = Geometry.create_sphere(origin_radius, origin_subdivisions, origin_color)
        
        geometry = (x_geometry + y_geometry + z_geometry + origin_geometry).transform(translate, rotate, scale)
        wireframe = (x_wireframe + y_wireframe + z_wireframe).transform(translate, rotate, scale)

        axis_body = self.add_object(geometry, buffer_type, GL_TRIANGLES, selectable=selectable) if show_body else None
        axis_wireframe = self.add_object(wireframe, buffer_type, GL_LINES, line_width=line_width, selectable=selectable) if show_wireframe else None
        return ObjectCollection({'body': axis_body, 'wireframe': axis_wireframe})

    def add_axis_ticks(self, size=5.0, axis_tick_params=None, buffer_type=BufferType.Static,
                     translate=(0,0,0), rotate=(0,0,0), scale=(1,1,1), selectable=False):
        """Add ticks to the axis with multiple increment sizes.
        
        Parameters
        ----------
        size : float, optional
            Length of axis arrows
        axis_tick_params : list of dict, optional
            List of tick specifications, each containing:
            - 'increment': spacing between ticks
            - 'tick_size': size of ticks
            - 'tick_color': color of ticks
            - 'line_width': width of lines
            If None, uses self.default_axis_ticks
        buffer_type : BufferType, optional
            Static or Dynamic buffer
        translate : tuple, optional
            Translation vector (x,y,z)
        rotate : tuple, optional
            Rotation angles (x,y,z)
        scale : tuple, optional
            Scale factors (x,y,z)
        selectable : bool, optional
            Allow object to be selected

        Returns
        -------
        RenderObject
            Tick render object
        """
        tick_geometry = None
        
        # Use default ticks if none provided
        tick_params = axis_tick_params or self.default_axis_ticks
        
        # Sort by increment size (largest first) to ensure proper rendering order
        tick_params = sorted(tick_params, key=lambda x: x['increment'], reverse=True)
        
        # Create geometry for each increment level
        for params in tick_params:
            increment = params['increment']
            tick_size = params['tick_size']
            tick_color = params['tick_color']
            line_width = params.get('line_width', self.default_line_width)
            
            for i in np.arange(-size + increment, size + increment/2, increment):  # Added increment/2 to ensure last tick is included
                if abs(i) < 1e-10:  # Skip origin
                    continue
                    
                x_tick = Geometry.create_line((i, -tick_size, 0), (i, tick_size, 0), tick_color)
                y_tick = Geometry.create_line((-tick_size, i, 0), (tick_size, i, 0), tick_color)
                
                if tick_geometry is None:
                    tick_geometry = x_tick + y_tick
                else:
                    tick_geometry = tick_geometry + x_tick + y_tick

        if tick_geometry is None:
            return None
        
        tick_geometry = tick_geometry.transform(translate, rotate, scale)
        return self.add_object(tick_geometry, buffer_type, GL_LINES, line_width=line_width, selectable=selectable)

    def add_grid(self, size, grid_params=None, buffer_type=BufferType.Static,
                translate=(0,0,0), rotate=(0,0,0), scale=(1,1,1), selectable=False):
        """Add a grid with multiple increment sizes.
        
        Parameters
        ----------
        size : float
            Size of the grid
        grid_params : list of dict, optional
            List of grid specifications, each containing:
            - 'increment': spacing between grid lines (0 for main axes)
            - 'color': color of grid lines
            - 'line_width': width of lines
            If None, uses self.default_grid_params
        buffer_type : BufferType, optional
            Static or Dynamic buffer
        translate : tuple, optional
            Translation vector (x,y,z)
        rotate : tuple, optional
            Rotation angles (x,y,z)
        scale : tuple, optional
            Scale factors (x,y,z)
        selectable : bool, optional
            Allow object to be selected

        Returns
        -------
        RenderObject
            Grid render object
        """
        grid_params = grid_params or self.default_grid_params
        grid_params = sorted(grid_params, key=lambda x: (x['increment'] == 0, -x['increment']))
        
        objects = []  # Store separate objects for each line width
        
        # Create geometry for each increment level
        for params in grid_params:
            increment = params['increment']
            color = params['color']
            line_width = params.get('line_width', self.default_line_width)
            
            grid_geometry = None
            
            if increment == 0:
                # Draw main axes
                x_axis = Geometry.create_line((-size, 0, 0), (size, 0, 0), color)
                y_axis = Geometry.create_line((0, -size, 0), (0, size, 0), color)
                grid_geometry = x_axis + y_axis
            else:
                # Draw regular grid lines
                for i in np.arange(-size + increment, size + increment/2, increment):
                    if abs(i) < 1e-10:  # Skip center lines
                        continue
                        
                    vertical_line = Geometry.create_line((i, -size, 0), (i, size, 0), color)
                    horizontal_line = Geometry.create_line((-size, i, 0), (size, i, 0), color)
                    
                    if grid_geometry is None:
                        grid_geometry = vertical_line + horizontal_line
                    else:
                        grid_geometry = grid_geometry + vertical_line + horizontal_line

            if grid_geometry is not None:
                grid_geometry = grid_geometry.transform(translate, rotate, scale)
                grid_object = self.add_object(grid_geometry, buffer_type, GL_LINES, 
                                            line_width=line_width, selectable=selectable)
                
                # Enable polygon offset to prevent z-fighting
                grid_object.polygon_offset = True
                grid_object.polygon_offset_factor = -1.0
                grid_object.polygon_offset_units = -1.0
                
                objects.append(grid_object)
        
        # Return an ObjectCollection if multiple objects, otherwise return the single object
        return ObjectCollection({'grid': objects}) if len(objects) > 1 else objects[0]

    def plot(self, x, y, color=Color.WHITE, line_width=None, buffer_type=BufferType.Static, 
            translate=(0,0,0), rotate=(0,0,0), scale=(1,1,1), selectable=False):
        """Plot a line through a series of x,y points.
        
        Parameters
        ----------
        x : float or array-like
            X coordinates
        y : float or array-like
            Y coordinates
        color : Color, optional
            Line color (default: white)
        line_width : float, optional
            Width of the line (default: 1.0)
        transform : dict, optional
            Transform to apply to the points (translate, rotate, scale)

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
        
        return self.add_linestring(points, color, line_width, buffer_type, translate, rotate, scale, selectable)

    def scatter(self, x, y, color=None, point_size=3.0, shape=PointShape.CIRCLE, buffer_type=BufferType.Static, 
               translate=(0,0,0), rotate=(0,0,0), scale=(1,1,1), selectable=False):
        """Create a scatter plot of x,y points.
        
        Parameters
        ----------
        x : float or array-like
            X coordinates
        y : float or array-like
            Y coordinates
        color : Color, optional
            Point color (default: white)
        point_size : float, optional
            Size of points (default: 3.0)
        shape : PointShape, optional
            Shape of points (default: CIRCLE)
        translate : tuple, optional
            Translation vector (x,y,z)
        rotate : tuple, optional
            Rotation angles (x,y,z)
        scale : tuple, optional
            Scale factors (x,y,z)

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
        return self.add_points(points, color, point_size, shape, buffer_type, translate, rotate, scale, selectable)

    def add_blank_object(self, buffer_type=BufferType.Stream, draw_type=GL_TRIANGLES, 
                        line_width=None, point_size=None, selectable=True):
        """Add a blank object for a dynamic / stream buffer.
        
        Parameters
        ----------
        vertices_size : int
            Size of vertex data
        indices_size : int
            Size of index data
        buffer_type : BufferType, optional
            Static or Dynamic buffer
        draw_type : GL_enum, optional
            OpenGL primitive type (TRIANGLES, LINES, etc)
        line_width : float, optional
            Line width (default is self.default_line_width)
        point_size : float, optional
            Point size (default is self.default_point_size)

        Returns
        -------
        RenderObject
            Blank render object
        """        
        blank = self.add_object_base(None, None, buffer_type, draw_type, line_width, point_size, selectable)
        return blank

    def add_blank_objects(self, draw_types, buffer_type=BufferType.Dynamic):
        """Add a collection of blank objects for a dynamic / stream buffer.
        
        Parameters
        ----------
        draw_types : dict
            Dictionary of draw types for each object
        buffer_type : BufferType, optional
            Static or Dynamic buffer

        Returns
        -------
        ObjectCollection
            Collection of blank objects
        """
        return ObjectCollection({name: self.add_blank_object(buffer_type, draw_type) for name, draw_type in draw_types.items()})

    def add_object(self, geometry_data, buffer_type, draw_type=GL_TRIANGLES, line_width=None, point_size=None, selectable=True, shader=None):
        """Create and add a new render object to the scene.

        Parameters
        ----------
        geometry_data : GeometryData
            Vertex and index data for the object
            Set to None for dynamic / stream buffer
        buffer_type : BufferType
            Static or Dynamic buffer
        draw_type : GL_enum, optional
            OpenGL primitive type (TRIANGLES, LINES, etc)
        line_width : float, optional
            Width for line primitives (default is self.default_line_width)
        point_size : float, optional
            Size for point primitives
        shader : Shader, optional
            Shader for the object (default is self.default_shader)

        Returns
        -------
        RenderObject
            Created render object
        """
        # Interleave position, color, and normal data
        vertices = geometry_data.get_vertices()
        indices = geometry_data.get_indices()
        
        return self.add_object_base(vertices, indices, buffer_type, draw_type, line_width, point_size, selectable, shader)

    def add_object_base(self, vertices, indices, buffer_type, draw_type=GL_TRIANGLES, line_width=None, point_size=None, selectable=True, shader=None):
        """Create and add a new render object to the scene.

        Parameters
        ----------
        vertices : np.array
            Vertex data for the object
        indices : np.array
            Index data for the object
        vertices_size : int
            Size of vertex data
        indices_size : int
            Size of index data
        buffer_type : BufferType
            Static or Dynamic buffer
        draw_type : GL_enum, optional
            OpenGL primitive type (TRIANGLES, LINES, etc)
        line_width : float, optional
            Width for line primitives (default is self.default_line_width)
        point_size : float, optional
            Size for point primitives (default is self.default_point_size)
        shader : Shader, optional
            Shader for the object (default is self.default_shader)  

        Returns
        -------
        RenderObject
            Created render object
        """
        
        line_width = line_width or self.default_line_width
        point_size = point_size or self.default_point_size
        
        # Use point shader for point primitives if no shader specified
        if shader is None:
            shader = self.point_shader if (draw_type == GL_POINTS) else self.default_shader
        
        obj = Object(vertices, indices, draw_type, line_width, point_size, 
                    buffer_type, selectable, shader)
         
        self.objects.append(obj)
        return obj
