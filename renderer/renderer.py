from OpenGL.GL import *
import numpy as np
from renderer.geometry import Geometry, Vertex
from utils.color import Color
from renderer.objects import BufferType, VertexBuffer, IndexBuffer, VertexArray, RenderObject
from renderer.batch_renderer import BatchRenderer
from typing import Dict, List
from utils.config import Config

# TODO: buffer_type is not really implemented for static buffer
# TODO: Remove the 1.01 scaling and replace with a input for every function
# 1 1 1
# 0 1 1
# 0 0 1
# 1 0 1
# 1 0 0
# 1 1 0

class Renderer:
    """OpenGL renderer for managing 3D objects, lights, and scene rendering.
    
    Handles creation and rendering of geometric objects,
    lighting setup, and camera transformations.
    """
    def __init__(self, config, static_max_vertices=10000, static_max_indices=30000, dynamic_max_vertices=10000, dynamic_max_indices=30000):
        """Initialize renderer with default settings and OpenGL state."""
        self.lights = []
        self.objects = []
        # Config file 
        config.add("background_colour", [0.21987, 0.34362, 0.40084], "Background colour")
        self.config = config
        # Set default values or pass arguments to add_x() functions individually
        self.default_point_size = 1.0
        self.default_line_width = 1.0
        self.default_segments = 16
        self.default_subdivisions = 4
        self.default_face_color = Color.WHITE
        self.default_wireframe_color = Color.BLACK
        self.default_arrow_dimensions = Renderer.ArrowDimensions(shaft_radius=0.03, head_radius=0.06, head_length=0.1)
        
        # Initialize OpenGL state
        glEnable(GL_DEPTH_TEST)      # Enable depth testing
        glEnable(GL_CULL_FACE)       # Enable back-face culling
        glCullFace(GL_BACK)          # Cull back faces
        
        # Enable blending for transparent effects
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
                
        self.view_matrix = None
        self.projection_matrix = None
        self.camera_position = None
        # Add batch renderer
        self.static_batch_renderer = BatchRenderer(max_vertices=static_max_vertices, max_indices=static_max_indices, buffer_type=BufferType.Static)
        self.dynamic_batch_renderer = BatchRenderer(max_vertices=dynamic_max_vertices, max_indices=dynamic_max_indices, buffer_type=BufferType.Dynamic)
        # Static objects should be updated only once (or very rarely), dynamic objects update every frame
        self.static_needs_update = True
        
    def get_selected_objects(self):
        """Get all selected objects."""
        return [obj for obj in self.objects if getattr(obj, 'selected', False)]
    
    def add_light(self, light):
        """Add a light source to the scene.
        
        Parameters
        ----------
        light : Light
            Light object to add
        """
        self.lights.append(light)

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

    def add_point(self, position, color, point_size=None, buffer_type=BufferType.Static, selectable=True):
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
        dict
            Dictionary containing "point" render object
        """
        geometry = Geometry.create_point(position, color)
        point = self.add_object(geometry, buffer_type, GL_POINTS, point_size=point_size, selectable=selectable)
        return {"point": point}

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
        dict
            Dictionary containing "line" render object
        """
        geometry = Geometry.create_line(p0, p1, color).transform(translate, rotate, scale)
        line = self.add_object(geometry, buffer_type, GL_LINES, line_width=line_width, selectable=selectable)
        return {"line": line}

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
        dict
            Dictionary containing "body" and "wireframe" render objects
        """
        triangle_body = triangle_wireframe = None
        if show_body:
            geometry = Geometry.create_triangle(p1, p2, p3, color or self.default_face_color).transform(translate, rotate, scale)
            triangle_body = self.add_object(geometry, buffer_type, GL_TRIANGLES, selectable=selectable)
        if show_wireframe:
            geometry = Geometry.create_triangle_wireframe(p1, p2, p3, wireframe_color or self.default_wireframe_color).transform(translate, rotate, scale)
            triangle_wireframe = self.add_object(geometry, buffer_type, GL_LINES, line_width=line_width, selectable=selectable)
        return {
            "body": triangle_body,
            "wireframe": triangle_wireframe
        }

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
        dict
            Dictionary containing "body" and "wireframe" render objects
        """
        rectangle_body = rectangle_wireframe = None
        if show_body:
            geometry = Geometry.create_rectangle(position[0], position[1], width, height, 
                                              color or self.default_face_color).transform(translate, rotate, scale)
            rectangle_body = self.add_object(geometry, buffer_type, GL_TRIANGLES, selectable=selectable)
        if show_wireframe:
            # Slightly larger wireframe to prevent z-fighting
            geometry = Geometry.create_rectangle_wireframe(position[0], position[1], width * 1.01, height * 1.01, 
                                                            wireframe_color or self.default_wireframe_color).transform(translate, rotate, scale)
            rectangle_wireframe = self.add_object(geometry, buffer_type, GL_LINES, line_width=line_width, selectable=selectable )
        return {
            "body": rectangle_body,
            "wireframe": rectangle_wireframe
        }

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
        dict
            Dictionary containing "body" and "wireframe" render objects
        """
        segments = segments or self.default_segments
        color = color or self.default_face_color
        wireframe_color = wireframe_color or self.default_wireframe_color
        
        circle_body = circle_wireframe = None
        if show_body:
            geometry = Geometry.create_circle(position, radius, segments, color).transform(translate, rotate, scale)
            circle_body = self.add_object(geometry, buffer_type, GL_TRIANGLE_FAN, selectable=selectable )
        if show_wireframe:
            # Slightly larger wireframe to prevent z-fighting
            geometry = Geometry.create_circle_wireframe(position, radius * 1.01, segments, wireframe_color).transform(translate, rotate, scale)
            circle_wireframe = self.add_object(geometry, buffer_type, GL_LINE_LOOP, line_width=line_width, selectable=selectable    )
        return {
            "body": circle_body,
            "wireframe": circle_wireframe
        }

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
        dict
            Dictionary containing "body" and "wireframe" render objects
        """
        color = color or self.default_face_color
        wireframe_color = wireframe_color or self.default_wireframe_color
        
        cube_body = cube_wireframe = None
        if show_body:
            geometry = Geometry.create_cube(size=1.0, color=color).transform(translate, rotate, scale)
            cube_body = self.add_object(geometry, buffer_type, GL_TRIANGLES, selectable=selectable  )
        if show_wireframe:
            geometry = Geometry.create_cube_wireframe(size=1.0, color=wireframe_color).transform(translate, rotate, scale)
            cube_wireframe = self.add_object(geometry, buffer_type, GL_LINES, line_width=line_width, selectable=selectable)
        return {
            "body": cube_body,
            "wireframe": cube_wireframe
        }

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
        dict
            Dictionary containing "body" and "wireframe" render objects
        """
        segments = segments or self.default_segments
        color = color or self.default_face_color
        wireframe_color = wireframe_color or self.default_wireframe_color
        
        cylinder_body = cylinder_wireframe = None
        if show_body:
            geometry = Geometry.create_cylinder(segments, color).transform(translate, rotate, scale)
            cylinder_body = self.add_object(geometry, buffer_type, GL_TRIANGLES, selectable=selectable)
        if show_wireframe:
            geometry = Geometry.create_cylinder_wireframe(segments, wireframe_color).transform(translate, rotate, scale)
            cylinder_wireframe = self.add_object(geometry, buffer_type, GL_LINES, line_width=line_width, selectable=selectable)
        return {
            "body": cylinder_body,
            "wireframe": cylinder_wireframe
        }

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
        dict
            Dictionary containing "body" and "wireframe" render objects
        """
        segments = segments or self.default_segments
        color = color or self.default_face_color
        wireframe_color = wireframe_color or self.default_wireframe_color
        
        cone_body = cone_wireframe = None
        if show_body:
            geometry = Geometry.create_cone(segments, color).transform(translate, rotate, scale)
            cone_body = self.add_object(geometry, buffer_type, GL_TRIANGLES, selectable=selectable)
        if show_wireframe:
            geometry = Geometry.create_cone_wireframe(segments, wireframe_color).transform(translate, rotate, scale)
            cone_wireframe = self.add_object(geometry, buffer_type, GL_LINES, line_width=line_width, selectable=selectable)
        return {
            "body": cone_body,
            "wireframe": cone_wireframe
        }

    def add_sphere(self, radius, subdivisions=4, color=None,buffer_type=BufferType.Static, 
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
        list
            [sphere_body] object (no wireframe support)
        """
        subdivisions = subdivisions or self.default_subdivisions
        color = color or self.default_face_color
        geometry = Geometry.create_sphere(radius, subdivisions, color).transform(translate, rotate, scale)
        sphere_body = self.add_object(geometry, buffer_type, GL_TRIANGLES, selectable=selectable)
        return {"body": sphere_body}

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
        dict
            Dictionary containing "body" and "wireframe" render objects
        """

        segments = segments or self.default_segments
        arrow_dimensions = arrow_dimensions or self.default_arrow_dimensions
        color = color or self.default_face_color
        wireframe_color = wireframe_color or self.default_wireframe_color
        
        body, wireframe = Geometry.create_arrow(p0, p1, color, wireframe_color, arrow_dimensions.shaft_radius, 
                                                arrow_dimensions.head_radius, arrow_dimensions.head_length, segments)
        arrow_body = self.add_object(body, buffer_type, GL_TRIANGLES, selectable=selectable) if show_body else None
        arrow_wireframe = self.add_object(wireframe, buffer_type, GL_LINES, line_width=line_width, selectable=selectable) if show_wireframe else None
        return {
            "body": arrow_body,
            "wireframe": arrow_wireframe
        }

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
        list
            [axis_body, axis_wireframe] objects
        """
        segments = segments or self.default_segments
        origin_subdivisions = origin_subdivisions or self.default_subdivisions
        arrow_dimensions = arrow_dimensions or self.default_arrow_dimensions
        wireframe_color = wireframe_color or self.default_wireframe_color
        # Create geometry for RGB arrows
        x_geometry, x_wireframe = Geometry.create_arrow((0,0,0), (size,0,0), (1,0,0), wireframe_color, arrow_dimensions.shaft_radius, 
                                                        arrow_dimensions.head_radius, arrow_dimensions.head_length, segments)
        y_geometry, y_wireframe = Geometry.create_arrow((0,0,0), (0,size,0), (0,1,0), wireframe_color, arrow_dimensions.shaft_radius, 
                                                        arrow_dimensions.head_radius, arrow_dimensions.head_length, segments)
        z_geometry, z_wireframe = Geometry.create_arrow((0,0,0), (0,0,size), (0,0,1), wireframe_color, arrow_dimensions.shaft_radius, 
                                                        arrow_dimensions.head_radius, arrow_dimensions.head_length, segments)
        
        # Add origin sphere
        origin_geometry = Geometry.create_sphere(origin_radius, origin_subdivisions, origin_color)
        
        # Combine and transform geometries
        geometry = (x_geometry + y_geometry + z_geometry + origin_geometry).transform(translate, rotate, scale)
        wireframe = (x_wireframe + y_wireframe + z_wireframe).transform(translate, rotate, scale)

        # Create render objects
        axis_body = self.add_object(geometry, buffer_type, GL_TRIANGLES, selectable=selectable) if show_body else None
        axis_wireframe = self.add_object(wireframe, buffer_type, GL_LINES, line_width=line_width, selectable=selectable) if show_wireframe else None
        return {
            "body": axis_body,
            "wireframe": axis_wireframe
        }

    def add_numbered_axis(self, size=5.0, increment=1.0, arrow_dimensions=None, segments=None,
                     origin_radius=0.035, origin_subdivisions=None, 
                     origin_color=Color.BLACK, axis_color=Color.WHITE, tick_color=Color.WHITE,
                     buffer_type=BufferType.Static, line_width=None, tick_size=0.1,
                     translate=(0,0,0), rotate=(0,0,0), scale=(1,1,1), selectable=False):
        """Add coordinate axes with number ticks."""
        # Create main axes
        x_axis = Geometry.create_line((-size, 0, 0), (size, 0, 0), axis_color)
        y_axis = Geometry.create_line((0, -size, 0), (0, size, 0), axis_color)
        
        # Create tick marks
        tick_geometry = None
        
        # Generate ticks from -size to +size at increment intervals
        for i in np.arange(-size + increment, size, increment):
            if abs(i) < 1e-10:  # Skip origin
                continue
                
            # X-axis tick - slightly offset in z to prevent z-fighting
            x_tick = Geometry.create_line((i, -tick_size, 0.01), (i, tick_size, 0.01), tick_color)
            # Y-axis tick - slightly offset in z to prevent z-fighting
            y_tick = Geometry.create_line((-tick_size, i, 0.01), (tick_size, i, 0.01), tick_color)
            
            # Combine with existing geometry
            if tick_geometry is None:
                tick_geometry = x_tick + y_tick
            else:
                tick_geometry = tick_geometry + x_tick + y_tick
        
        # Add origin sphere
        origin_geometry = Geometry.create_sphere(origin_radius, origin_subdivisions or self.default_subdivisions, origin_color)
        
        # Combine geometries
        axis_geometry = (x_axis + y_axis).transform(translate, rotate, scale)
        tick_geometry = tick_geometry.transform(translate, rotate, scale) if tick_geometry else None
        origin_geometry = origin_geometry.transform(translate, rotate, scale)
        
        # Create render objects
        axis_obj = self.add_object(axis_geometry, buffer_type, GL_LINES, line_width=line_width, selectable=selectable)
        tick_obj = self.add_object(tick_geometry, buffer_type, GL_LINES, line_width=line_width, selectable=selectable) if tick_geometry else None
        origin_obj = self.add_object(origin_geometry, buffer_type, GL_TRIANGLES, selectable=selectable)
        
        return {
            "axis": axis_obj,
            "ticks": tick_obj,
            "origin": origin_obj
        }
   

    def add_grid(self, size, increment, color, line_width=None, buffer_type=BufferType.Static, translate=(0,0,0), rotate=(0,0,0), scale=(1,1,1), selectable=False):
        """Add a grid of lines in the XY plane.

        Parameters
        ----------
        size : float
            Grid size (extends from -size to +size)
        increment : float
            Spacing between grid lines
        color : Color
            Grid line color
        line_width : float, optional
            Grid line width (default is self.default_line_width)
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
        dict
            Dictionary containing "line" render object
        """
        geometry = Geometry.create_grid(size, increment, color).transform(translate, rotate, scale)
        grid = self.add_object(geometry, buffer_type, GL_LINES, line_width=line_width, selectable=selectable)
        return {"line": grid}

    def plot(self, x, y, color=Color.WHITE, line_width=1.0, buffer_type=BufferType.Static, translate=(0,0,0), rotate=(0,0,0), scale=(1,1,1), selectable=False):
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
        """
        # Convert single points to arrays
        x = np.atleast_1d(x)
        y = np.atleast_1d(y)
        
        if len(x) != len(y):
            raise ValueError("x and y must have same length")
            
        # Add z=0 coordinate to make points 3D
        points = np.column_stack((x, y, np.zeros_like(x)))
        geometry = Geometry.create_linestring(points, color).transform(translate, rotate, scale)
        linestring = self.add_object(geometry, buffer_type, GL_LINES, line_width=line_width, selectable=selectable)
        return {"line": linestring}


    def scatter(self, x, y, color=None, point_size=3.0, buffer_type=BufferType.Static, translate=(0,0,0), rotate=(0,0,0), scale=(1,1,1), selectable=False):
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
        transform : dict, optional
            Transform to apply to the points (translate, rotate, scale)
        """
        # Convert single points to arrays
        x = np.atleast_1d(x)
        y = np.atleast_1d(y)
        
        if len(x) != len(y):
            raise ValueError("x and y must have same length")
        
        geometry = None
        for i in range(len(x)):
            # Create 3D point with z=0
            point = Geometry.create_point(np.array([x[i], y[i], 0]), color)
            geometry = point if geometry is None else geometry + point
            
        return self.add_object(geometry, buffer_type, GL_POINTS, point_size=point_size, selectable=selectable)
           
           
    def add_blank_object(self, buffer_type=BufferType.Stream, draw_type=GL_TRIANGLES, line_width=None, point_size=None, selectable=True):
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
        dict
            Dictionary containing either "body" (for GL_TRIANGLES) or "line" render object
        """        
        blank = self.add_object_base(None, None, buffer_type, draw_type, line_width, point_size, selectable)
        return {"body": blank} if draw_type == GL_TRIANGLES else {"line": blank} # TODO: This is garbage what about points?


    def add_object(self, geometry_data, buffer_type, draw_type=GL_TRIANGLES, line_width=None, point_size=None, selectable=True):
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

        Returns
        -------
        RenderObject
            Created render object
        """
        # Interleave position, color, and normal data
        vertices = geometry_data.get_vertices()
        indices = geometry_data.get_indices()
        
        return self.add_object_base(vertices, indices, buffer_type, draw_type, line_width, point_size, selectable)


    def add_object_base(self, vertices, indices, buffer_type, draw_type=GL_TRIANGLES, line_width=None, point_size=None, selectable=True):
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

        Returns
        -------
        RenderObject
            Created render object
        """
        
        line_width = line_width or self.default_line_width
        point_size = point_size or self.default_point_size
        
        
        # TODO: handle buffer_type for static and stream
        
        obj = RenderObject(vertices, indices, draw_type, line_width, point_size, buffer_type, selectable)
         
        self.objects.append(obj)
        return obj
