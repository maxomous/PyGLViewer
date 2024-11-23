from dataclasses import dataclass, replace
from typing import Dict, List, Tuple, Optional
from OpenGL.GL import *
import numpy as np
from pyglviewer.renderer.shapes import Shapes, ArrowDimensions
from pyglviewer.utils.colour import Colour
from pyglviewer.renderer.objects import BufferType, VertexBuffer, IndexBuffer, VertexArray, Object, ObjectCollection
from pyglviewer.renderer.batch_renderer import BatchRenderer
from pyglviewer.renderer.light import Light, default_lighting
from pyglviewer.utils.config import Config
from pyglviewer.renderer.shader import Shader, PointShape
from pyglviewer.renderer.shader import vertex_shader_lighting, fragment_shader_lighting, vertex_shader_points, fragment_shader_points
# TODO: buffer_type is not really implemented for static buffer
# TODO: Remove the 1.01 scaling and replace with a input for every function
# TODO: transform is not the same for everything, cube vs cylinder for example

@dataclass
class RenderParams:
    """Common parameters for rendering objects.
    
    Parameters
    ----------
    ### Object Parameters
    line_width : float
        Width for line primitives
    point_size : float
        Size for point primitives
    point_shape : PointShape
        Shape for point primitives
    buffer_type : BufferType
        Static or Dynamic buffer type
    selectable : bool
        Allow object to be selected
    shader : Optional[Shader]
        Custom shader for rendering
    alpha : float
        Alpha value for transparency
    
    ### Transform Parameters
    translate : Tuple[float, float, float]
        Translation vector (x,y,z)
    rotate : Tuple[float, float, float]
        Rotation angles (x,y,z)
    scale : Tuple[float, float, float]
        Scale factors (x,y,z)
    
    ### Display Parameters
    show_body : bool
        Show filled geometry
    show_wireframe : bool
        Show wireframe
    wireframe_colour : Optional[Colour]
        Colour for wireframe
    """
    # Object Parameters
    line_width: float = 1.0
    point_size: float = 1.0
    point_shape: PointShape = PointShape.CIRCLE
    buffer_type: BufferType = BufferType.Static
    selectable: bool = True
    shader: Optional[Shader] = None
    alpha: float = 1.0
    
    # Transform Parameters
    translate: Tuple[float, float, float] = (0, 0, 0)
    rotate: Tuple[float, float, float] = (0, 0, 0)
    scale: Tuple[float, float, float] = (1, 1, 1)
    
    # Display Parameters
    show_body: bool = True
    show_wireframe: bool = True
    wireframe_colour: Optional[Colour] = Colour.BLACK


class Renderer:
    """OpenGL renderer for managing 3D objects, lights, and scene rendering.
    
    Handles creation and rendering of geometric objects,
    lighting setup, and camera transformations.
    Static objects are updated only once (or very rarely), dynamic objects update often/every frame
    """
    def __init__(self, config, static_max_vertices, static_max_indices, dynamic_max_vertices, dynamic_max_indices):
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
        self.default_segments = 16
        self.default_subdivisions = 4
        
        self.default_face_colour = Colour.WHITE
        self.default_wireframe_colour = Colour.BLACK
        self.default_arrow_dimensions = ArrowDimensions(shaft_radius=0.03, head_radius=0.06, head_length=0.1)
        self.default_axis_ticks = [
            { 'increment': 1,    'tick_size': 0.08,  'line_width': 3, 'tick_colour': Colour.rgb(200, 200, 200) }, 
            { 'increment': 0.5,  'tick_size': 0.04,  'line_width': 3, 'tick_colour': Colour.rgb(200, 200, 200) }, 
            { 'increment': 0.1,  'tick_size': 0.02,  'line_width': 3, 'tick_colour': Colour.rgb(200, 200, 200) }
        ]
        self.default_grid_params = [ 
            {'increment': 0,    'colour': Colour.rgb(200, 200, 200), 'line_width': 3.0},
            {'increment': 1,    'colour': Colour.rgb(200, 200, 200), 'line_width': 1.0},
            {'increment': 0.1,  'colour': Colour.rgb(150, 150, 150), 'line_width': 1.0}
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

    def add_point(self, position, colour, params = RenderParams()):
        """Add a point primitive to the scene.
        
        Parameters
        ----------
        position : tuple
            3D position of point
        colour : Colour
            Point colour
        params : RenderParams, optional
            Rendering parameters

        Returns
        -------
        RenderObject
            Point render object
        """
        # Use point shader if not specified
        params.shader = params.shader or self.point_shader
        # Create point geometry
        geometry = Shapes.create_point(position, colour)
        # Add object to batch renderer
        return self.add_object(geometry, GL_POINTS, params)

    def add_points(self, points, colour=Colour.WHITE, params = RenderParams()):
        """Add a series of points.
        
        Parameters
        ----------
        points : array-like
            Array of points (x,y,z)
        colour : Colour, optional
            Point colour (default: white)
        params : RenderParams, optional
            Rendering parameters
        
        Returns
        -------
        RenderObject
            Points render object
        """
        geometry = Shapes.create_blank()
        for point in points:
            geometry = geometry + Shapes.create_point(point, colour).transform(
                params.translate, params.rotate, params.scale)
        
        return self.add_object(geometry, GL_POINTS, params)

    def add_line(self, p0, p1, colour=Colour.WHITE, params = RenderParams()):
        """Add a line from p0 to p1.
        
        Parameters
        ----------
        p0 : tuple
            Start point
        p1 : tuple
            End point
        colour : Colour, optional
            Line colour
        params : RenderParams, optional
            Rendering parameters

        Returns
        -------
        RenderObject
            Line render object
        """
        geometry = Shapes.create_line(p0, p1, colour).transform(
            params.translate, params.rotate, params.scale)
        return self.add_object(geometry, GL_LINES, params)

    def add_linestring(self, points, colour=Colour.WHITE, params = RenderParams()):
        """Add a line through a series of points.
        
        Parameters
        ----------
        points : array-like
            Array of points (x,y,z)
        colour : Colour, optional
            Line colour (default: white)
        params : RenderParams, optional
            Rendering parameters

        Returns
        -------
        RenderObject
            Line render object
        """
        points = np.atleast_2d(points)
        if points.shape[1] != 3:
            raise ValueError("Points must have 3 values (x,y,z) per point")
        
        geometry = Shapes.create_linestring(points, colour).transform(
            params.translate, params.rotate, params.scale)
        return self.add_object(geometry, GL_LINES, params)

    def add_triangle(self, p1, p2, p3, colour=None, params = RenderParams()):
        """Add a triangle defined by three points.
        
        Parameters
        ----------
        p1, p2, p3 : tuple
            Triangle vertices
        colour : Colour, optional
            Fill colour
        params : RenderParams, optional
            Rendering parameters

        Returns
        -------
        ObjectCollection
            Collection containing 'body' and 'wireframe' objects
        """
        colour = colour or self.default_face_colour
        objects = {}
        
        if params.show_body:
            geometry = Shapes.create_triangle(p1, p2, p3, colour).transform(
                params.translate, params.rotate, params.scale)
            objects['body'] = self.add_object(geometry, GL_TRIANGLES, params)
        
        if params.show_wireframe:
            geometry = Shapes.create_triangle_wireframe(
                p1, p2, p3, params.wireframe_colour or self.default_wireframe_colour
            ).transform(params.translate, params.rotate, params.scale)
            objects['wireframe'] = self.add_object(geometry, GL_LINES, params)
        
        return ObjectCollection(objects)

    def add_rectangle(self, position, width, height, colour=None, params = RenderParams()):
        """Add a rectangle.
        
        Parameters
        ----------
        position : tuple
            Position (x,y)
        width : float
            Rectangle width
        height : float
            Rectangle height
        colour : Colour, optional
            Fill colour
        params : RenderParams, optional
            Rendering parameters

        Returns
        -------
        ObjectCollection
            Collection containing 'body' and 'wireframe' objects
        """
        colour = colour or self.default_face_colour
        objects = {}
        
        if params.show_body:
            geometry = Shapes.create_rectangle(position, width, height, colour).transform(
                params.translate, params.rotate, params.scale)
            objects['body'] = self.add_object(geometry, GL_TRIANGLES, params)
        
        if params.show_wireframe:
            geometry = Shapes.create_rectangle_wireframe(
                position, width * 1.01, height * 1.01, 
                params.wireframe_colour or self.default_wireframe_colour
            ).transform(params.translate, params.rotate, params.scale)
            objects['wireframe'] = self.add_object(geometry, GL_LINES, params)
        
        return ObjectCollection(objects)

    def add_circle(self, position, radius, colour=None, params = RenderParams()):
        """Add a circle in the XY plane.
        
        Parameters
        ----------
        position : tuple
            Centre position
        radius : float
            Circle radius
        colour : Colour, optional
            Fill colour
        params : RenderParams, optional
            Rendering parameters

        Returns
        -------
        ObjectCollection
            Collection containing 'body' and 'wireframe' objects
        """
        colour = colour or self.default_face_colour
        segments = self.default_segments
        
        objects = {}
        if params.show_body:
            geometry = Shapes.create_circle(position, radius, segments, colour).transform(
                params.translate, params.rotate, params.scale)
            objects['body'] = self.add_object(geometry, GL_TRIANGLE_FAN, params)
        
        if params.show_wireframe:
            geometry = Shapes.create_circle_wireframe(
                position, radius * 1.01, segments, 
                params.wireframe_colour or self.default_wireframe_colour
            ).transform(params.translate, params.rotate, params.scale)
            objects['wireframe'] = self.add_object(geometry, GL_LINE_LOOP, params)
        
        return ObjectCollection(objects)

    def add_cube(self, colour=None, params = RenderParams()):
        """Add a unit cube centreed at origin.
        
        Parameters
        ----------
        colour : Colour, optional
            Fill colour
        params : RenderParams, optional
            Rendering parameters
        
        Returns
        -------
        ObjectCollection
            Collection containing 'body' and 'wireframe' objects
        """
        colour = colour or self.default_face_colour
        objects = {}
        
        if params.show_body:
            geometry = Shapes.create_cube(colour=colour).transform(
                params.translate, params.rotate, params.scale)
            objects['body'] = self.add_object(geometry, GL_TRIANGLES, params)
        
        if params.show_wireframe:
            geometry = Shapes.create_cube_wireframe(
                colour=params.wireframe_colour or self.default_wireframe_colour
            ).transform(params.translate, params.rotate, params.scale)
            objects['wireframe'] = self.add_object(geometry, GL_LINES, params)
        
        return ObjectCollection(objects)

    def add_beam(self, p0, p1, width, height, colour=None, params = RenderParams()):
        """Add a beam from p0 to p1.
        
        Parameters
        ----------
        p0 : tuple
            Start point
        p1 : tuple
            End point
        width : float
            Width of beam cross-section
        height : float
            Height of beam cross-section
        colour : Colour, optional
            Fill colour
        params : RenderParams, optional
            Rendering parameters

        Returns
        -------
        ObjectCollection
            Collection containing 'body' and 'wireframe' objects
        """
        colour = colour or self.default_face_colour
        
        body, wireframe = Shapes.create_beam(
            p0, p1, width, height, colour, 
            params.wireframe_colour or self.default_wireframe_colour
        )
        
        objects = {}
        if params.show_body:
            body = body.transform(params.translate, params.rotate, params.scale)
            objects['body'] = self.add_object(body, GL_TRIANGLES, params)
        
        if params.show_wireframe:
            wireframe = wireframe.transform(params.translate, params.rotate, params.scale)
            objects['wireframe'] = self.add_object(wireframe, GL_LINES, params)
        
        return ObjectCollection(objects)

    def add_cylinder(self, colour=None, params = RenderParams()):
        """Add a unit cylinder centreed at origin.
        
        Parameters
        ----------
        colour : Colour, optional
            Fill colour
        params : RenderParams, optional
            Rendering parameters

        Returns
        -------
        ObjectCollection
            Collection containing 'body' and 'wireframe' objects
        """
        colour = colour or self.default_face_colour
        segments = self.default_segments
        
        objects = {}
        if params.show_body:
            geometry = Shapes.create_cylinder(segments=segments, colour=colour).transform(
                params.translate, params.rotate, params.scale)
            objects['body'] = self.add_object(geometry, GL_TRIANGLES, params)
        
        if params.show_wireframe:
            geometry = Shapes.create_cylinder_wireframe(
                segments=segments, colour=params.wireframe_colour or self.default_wireframe_colour
            ).transform(params.translate, params.rotate, params.scale)
            objects['wireframe'] = self.add_object(geometry, GL_LINES, params)
        
        return ObjectCollection(objects)

    def add_cone(self, colour=None, params = RenderParams()):
        """Add a unit cone centreed at origin.
        
        Parameters
        ----------
        colour : Colour, optional
            Fill colour
        params : RenderParams, optional
            Rendering parameters

        Returns
        -------
        ObjectCollection
            Collection containing 'body' and 'wireframe' objects
        """
        colour = colour or self.default_face_colour
        segments = self.default_segments
        
        objects = {}
        if params.show_body:
            geometry = Shapes.create_cone(segments=segments, colour=colour).transform(
                params.translate, params.rotate, params.scale)
            objects['body'] = self.add_object(geometry, GL_TRIANGLES, params)
        
        if params.show_wireframe:
            geometry = Shapes.create_cone_wireframe(
                segments=segments, colour=params.wireframe_colour or self.default_wireframe_colour
            ).transform(params.translate, params.rotate, params.scale)
            objects['wireframe'] = self.add_object(geometry, GL_LINES, params)
        
        return ObjectCollection(objects)

    def add_sphere(self, position=(0,0,0), radius=0.5, colour=None, params = RenderParams()):
        """Add a sphere centreed at origin.
        
        Parameters
        ----------
        radius : float
            Sphere radius
        colour : Colour, optional
            Surface colour
        params : RenderParams, optional
            Rendering parameters

        Returns
        -------
        RenderObject
            Sphere render object
        """
        colour = colour or self.default_face_colour
        subdivisions = self.default_subdivisions
        
        geometry = Shapes.create_sphere(position=position, radius=radius, subdivisions=subdivisions, colour=colour).transform(
            params.translate, params.rotate, params.scale)
        return self.add_object(geometry, GL_TRIANGLES, params)

    def add_arrow(self, p0, p1, dimensions=None, colour=None, params = RenderParams()):
        """Add an arrow from p0 to p1.
        
        Parameters
        ----------
        p0 : tuple
            Start point (x,y,z)
        p1 : tuple
            End point (x,y,z)
        dimensions : ArrowDimensions, optional
            Arrow dimensions
        colour : Colour, optional
            Arrow colour
        params : RenderParams, optional
            Rendering parameters
        
        Returns
        -------
        ObjectCollection
            Collection containing 'body' and 'wireframe' objects
        """
        dimensions = dimensions or self.default_arrow_dimensions
        colour = colour or self.default_face_colour
        segments = self.default_segments
        
        geometry, wireframe = Shapes.create_arrow(p0, p1, dimensions, colour, 
                                                  params.wireframe_colour, segments)
        
        objects = {}
        if params.show_body:
            geometry = geometry.transform(params.translate, params.rotate, params.scale)
            objects['body'] = self.add_object(geometry, GL_TRIANGLES, params)
        
        if params.show_wireframe:
            wireframe = wireframe.transform(params.translate, params.rotate, params.scale)
            objects['wireframe'] = self.add_object(wireframe, GL_LINES, params)
        
        return ObjectCollection(objects)

    def add_axis(self, size=1.0, arrow_dimensions=None, origin_radius=0.035, 
                origin_colour=Colour.BLACK, params = RenderParams()):
        """Add coordinate axis arrows.
        
        Parameters
        ----------
        size : float, optional
            Length of axis arrows (default: 1.0)
        arrow_dimensions : ArrowDimensions, optional
            Arrow dimensions
        origin_radius : float, optional
            Radius of origin sphere (default: 0.035)
        origin_colour : Colour, optional
            Colour of origin sphere (default: BLACK)
        params : RenderParams, optional
            Rendering parameters
        
        Returns
        -------
        ObjectCollection
            Collection containing 'body' and 'wireframe' objects
        """
        arrow_dimensions = arrow_dimensions or self.default_arrow_dimensions
        segments = self.default_segments
        origin_subdivisions = self.default_subdivisions
        
        x_geometry, x_wireframe = Shapes.create_arrow(
            (0,0,0), (size,0,0), arrow_dimensions, 
            (1,0,0), params.wireframe_colour, segments)
        y_geometry, y_wireframe = Shapes.create_arrow(
            (0,0,0), (0,size,0), arrow_dimensions, 
            (0,1,0), params.wireframe_colour, segments)
        z_geometry, z_wireframe = Shapes.create_arrow(
            (0,0,0), (0,0,size), arrow_dimensions, 
            (0,0,1), params.wireframe_colour, segments)
        
        origin_geometry = Shapes.create_sphere(position=(0,0,0), radius=origin_radius, subdivisions=origin_subdivisions, colour=origin_colour)
        
        objects = {}
        if params.show_body:
            geometry = (x_geometry + y_geometry + z_geometry + origin_geometry).transform(
                params.translate, params.rotate, params.scale)
            objects['body'] = self.add_object(geometry, GL_TRIANGLES, params)
        
        if params.show_wireframe:
            wireframe = (x_wireframe + y_wireframe + z_wireframe).transform(
                params.translate, params.rotate, params.scale)
            objects['wireframe'] = self.add_object(wireframe, GL_LINES, params)
        
        return ObjectCollection(objects)

    def add_axis_ticks(self, size=5.0, tick_params=None, params = RenderParams()):
        """Add axis ticks in the XY plane.
        
        Parameters
        ----------
        size : float, optional
            Axis size (default: 5.0)
        tick_params : list, optional
            List of tick parameters for different detail levels
            Each dict contains: increment, tick_size, line_width (overrides RenderParams.line_width), tick_colour
        params : RenderParams, optional
            Rendering parameters

        Returns
        -------
        ObjectCollection
            Collection containing tick objects at different detail levels
        """
        tick_params = tick_params or self.default_axis_ticks
        objects = {}
        
        for n, tick_level in enumerate(tick_params):
            increment = tick_level['increment']
            tick_size = tick_level['tick_size']
            line_width = tick_level['line_width'] or params.line_width
            tick_colour = tick_level['tick_colour']
            
            # Create new params with updated line width
            level_params = replace(params, line_width=line_width)
            
            tick_geometry = None
            
            for i in np.arange(-size + increment, size + increment/2, increment):
                if abs(i) < 1e-10:  # Skip centre
                    continue
                    
                x_tick = Shapes.create_line((i, 0, 0), (i, tick_size, 0), tick_colour)
                y_tick = Shapes.create_line((0, i, 0), (tick_size, i, 0), tick_colour)
                
                if tick_geometry is None:
                    tick_geometry = x_tick + y_tick
                else:
                    tick_geometry = tick_geometry + x_tick + y_tick

            if tick_geometry is not None:
                tick_geometry = tick_geometry.transform(params.translate, params.rotate, params.scale)
                tick_object = self.add_object(tick_geometry, GL_LINES, level_params)
                
                objects[f'ticks-{n}'] = tick_object
        
        return ObjectCollection(objects)

    def add_grid(self, size=5.0, grid_params=None, params = RenderParams()):
        """Add a grid in the XY plane.
        
        Parameters
        ----------
        size : float, optional
            Grid size (default: 5.0)
        grid_params : list, optional
            List of grid parameters for different detail levels
            Each dict contains: increment, colour, line_width (overrides RenderParams.line_width)
        params : RenderParams, optional
            Rendering parameters

        Returns
        -------
        ObjectCollection
            Collection containing grid objects at different detail levels
        """
        grid_params = grid_params or self.default_grid_params
        objects = {}
        
        for n, grid_level in enumerate(grid_params):
            increment = grid_level['increment']
            colour = grid_level['colour']
            line_width = grid_level['line_width'] or params.line_width
            
            # Create new params with updated line width
            level_params = replace(params, line_width=line_width)
            
            grid_geometry = Shapes.create_blank()
            
            if increment == 0:
                # Draw main axes
                grid_geometry += Shapes.create_line((-size, 0, 0), (size, 0, 0), colour)
                grid_geometry += Shapes.create_line((0, -size, 0), (0, size, 0), colour)
            else:
                # Draw regular grid lines
                for i in np.arange(-size + increment, size + increment/2, increment):
                    if abs(i) < 1e-10:  # Skip centre lines
                        continue
                        
                    grid_geometry += Shapes.create_line((i, -size, 0), (i, size, 0), colour)
                    grid_geometry += Shapes.create_line((-size, i, 0), (size, i, 0), colour)

            if grid_geometry is not None:
                grid_geometry = grid_geometry.transform(params.translate, params.rotate, params.scale)
                grid_object = self.add_object(grid_geometry, GL_LINES, level_params)
            
                objects[f'grid-{n}'] = grid_object
        
        return ObjectCollection(objects)

    def scatter(self, x, y, colour=None, params = RenderParams()):
        """Create a scatter plot of x,y points.
        
        Parameters
        ----------
        x : float or array-like
            X coordinates
        y : float or array-like
            Y coordinates
        colour : Colour, optional
            Point colour
        params : RenderParams, optional
            Rendering parameters

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
        params.shader = params.shader or self.point_shader
        geometry = Shapes.create_points(points, colour or self.default_face_colour)
        return self.add_object(geometry, GL_POINTS, params)

    def plot(self, x, y, colour=Colour.WHITE, params = RenderParams()):
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
        geometry = Shapes.create_linestring(points, colour).transform(
            params.translate, params.rotate, params.scale)
        
        return self.add_object(geometry, GL_LINES, params)

    def add_blank_objects(self, draw_types: Dict[str, int], params = RenderParams()):
        """Add multiple blank objects.
        
        Parameters
        ----------
        draw_types : dict
            Dictionary of draw types for each object
        params : RenderParams, optional
            Rendering parameters

        Returns
        -------
        ObjectCollection
            Collection of blank objects
        """
        return ObjectCollection({
            name: self.add_blank_object(draw_type, params)
            for name, draw_type in draw_types.items()
        })

    def add_blank_object(self, draw_type=GL_TRIANGLES, params = RenderParams()):
        """Add a blank object for a dynamic / stream buffer.
        
        Parameters
        ----------
        draw_type : GL_enum, optional
            OpenGL primitive type (TRIANGLES, LINES, etc)
        params : RenderParams, optional
            Rendering parameters

        Returns
        -------
        RenderObject
            Blank render object
        """        
        return self._add_object_base(None, None, draw_type, params)

    def add_object(self, geometry_data, draw_type=GL_TRIANGLES, params = RenderParams()):
        """Create and add a new render object to the scene.

        Parameters
        ----------
        geometry_data : GeometryData
            Vertex and index data for the object
            Set to None for dynamic / stream buffer
        draw_type : GL_enum, optional
            OpenGL primitive type (TRIANGLES, LINES, etc)
        params : RenderParams, optional
            Rendering parameters
                     
        Returns
        -------
        RenderObject
            Created render object
        """
        vertices = geometry_data.get_vertices()
        indices = geometry_data.get_indices()
        
        return self._add_object_base(vertices, indices, draw_type, params)

    def _add_object_base(self, vertices, indices, draw_type=GL_TRIANGLES, params = RenderParams()):
        """Create and add a new render object to the scene.

        Parameters
        ----------
        vertices : np.array or None
            Vertex data for the object
        indices : np.array or None
            Index data for the object
        draw_type : GL_enum, optional
            OpenGL primitive type (TRIANGLES, LINES, etc)
        params : RenderParams, optional
            Rendering parameters

        Returns
        -------
        RenderObject
            Created render object
        """
        params.shader = params.shader or self.default_shader
        obj = Object(vertices, indices, draw_type, params.line_width, 
                    params.point_size, params.point_shape, params.buffer_type, 
                    params.selectable, params.shader, params.alpha)
        self.objects.append(obj)
        return obj

