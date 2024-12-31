from dataclasses import dataclass, replace
from typing import Dict, List, Tuple, Optional
from OpenGL.GL import *
import numpy as np
from pyglviewer.utils.colour import Colour
from pyglviewer.utils.config import Config
from pyglviewer.utils.transform import Transform
from pyglviewer.renderer.shapes import Shapes, Shape, ArrowDimensions
from pyglviewer.renderer.objects import VertexBuffer, IndexBuffer, VertexArray, Object, ObjectContainer
from pyglviewer.renderer.batch_renderer import BatchRenderer
from pyglviewer.renderer.light import Light, default_lighting
from pyglviewer.renderer.shader import Shader, DefaultShaders, PointShape

# TODO: buffer_type is not really implemented for static buffer
# TODO: Remove the 1.01 scaling and replace with a input for every function
# TODO: transform is not the same for everything, cube vs cylinder for example

# @dataclass
# class RenderParams:
#     """Common parameters for rendering objects.
    

#     Parameters
#     ----------
#     ### Object Parameters
#     line_width : float
#         Width for line primitives
#     point_size : float
#         Size for point primitives
#     point_shape : PointShape
#         Shape for point primitives
#     buffer_type : BufferType
#         Static or Dynamic buffer type
#     selectable : bool
#         Allow object to be selected
#     shader : Optional[Shader]
#         Custom shader for rendering
#     alpha : float
#         Alpha value for transparency
    
#     ### Transform Parameters
#     translate : Tuple[float, float, float]
#         Translation vector (x,y,z)
#     rotate : Tuple[float, float, float]
#         Rotation angles (x,y,z)
#     scale : Tuple[float, float, float]
#         Scale factors (x,y,z)
    
#     ### Display Parameters
#     show_body : bool
#         Show filled shape
#     show_wireframe : bool
#         Show wireframe
#     wireframe_colour : Optional[Colour]
#         Colour for wireframe
#     """
   

class Renderer:
    """OpenGL renderer for managing 3D objects, lights, and scene rendering.
    
    Handles creation and rendering of geometric objects,
    lighting setup, and camera transformations.
    Static objects are updated only once (or very rarely), dynamic objects update often/every frame
    """
    def __init__(self, config, max_static_vertices, max_static_indices, max_dynamic_vertices, max_dynamic_indices):
        """Initialize renderer with default settings and OpenGL state."""
        self.lights = []
        self.objects = []
        # Config file
        config.add("background_colour", [0.21987, 0.34362, 0.40084], "Background colour")
        self.config = config

        # Initialize OpenGL state
        glEnable(GL_DEPTH_TEST)     # Enable depth testing
        glEnable(GL_CULL_FACE)      # Enable back-face culling
        glCullFace(GL_BACK)         # Cull back faces
        glEnable(GL_BLEND)            # Enable blending for transparent effects
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)   # Define how colours of transparent objects blend when overlapping 
                        
        self.view_matrix = None
        self.projection_matrix = None
        self.camera_position = None
        
        # Initialise default shaders
        DefaultShaders.initialise()

        # Add batch renderer (now handles both static and dynamic internally)
        self.batch_renderer = BatchRenderer(max_static_vertices, max_static_indices,
                                            max_dynamic_vertices, max_dynamic_indices)
        
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

    def batch_renderer_update(self):
        """Update buffers if required."""
        # Clear batch renderer buffers (if update is required)
        self.batch_renderer.clear()
        # Submit all objects to the batch renderer 
        for obj in self.objects:
            # Add objects to appropriate buffer based on their type (if update is required)
            self.batch_renderer.add_object_to_batch(obj)
        
    def draw(self, view_matrix, projection_matrix, camera_position, lights):
        """Render all objects in the scene, using batching"""
        # Update buffers (if required)
        self.batch_renderer_update()
        # Render all objects (handles both static and dynamic internally)
        self.batch_renderer.render(view_matrix, projection_matrix, camera_position, lights)
    
        # Reset to default state
        glEnable(GL_DEPTH_TEST)
        glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
        glLineWidth(1.0)
        glPointSize(1.0)

    def clear(self):
        """Clear the framebuffer with a dark teal background."""
        r, g, b = self.config["background_colour"]
        glClearColor(r, g, b, 1.0)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)




    # def add_point(self, position, colour, params = RenderParams()):
    #     """Add a point primitive to the scene.
        
    #     Parameters
    #     ----------
    #     position : tuple
    #         3D position of point
    #     colour : Colour
    #         Point colour
    #     params : RenderParams, optional
    #         Rendering parameters

    #     Returns
    #     -------
    #     RenderObject
    #         Point render object
    #     """
    #     # Use point shader if not specified
    #     params.shader = params.shader or self.point_shader
    #     # Create point shape
    #     shape = Shapes.point(position, colour)
    #     # Add object to batch renderer
    #     return self.add_object(shape, params)

    # def add_points(self, points, colour=Colour.WHITE, params = RenderParams()):
    #     """Add a series of points.
        
    #     Parameters
    #     ----------
    #     points : array-like
    #         Array of points (x,y,z)
    #     colour : Colour, optional
    #         Point colour (default: white)
    #     params : RenderParams, optional
    #         Rendering parameters
        
    #     Returns
    #     -------
    #     RenderObject
    #         Points render object
    #     """
    #     shape = Shapes.points(points, colour).transform(params.translate, params.rotate, params.scale)
    #     return self.add_object(shape, params)


    # def add_line(self, p0, p1, colour=Colour.WHITE, params = RenderParams()):
    #     """Add a line from p0 to p1.
        
    #     Parameters
    #     ----------
    #     p0 : tuple
    #         Start point
    #     p1 : tuple
    #         End point
    #     colour : Colour, optional
    #         Line colour
    #     params : RenderParams, optional
    #         Rendering parameters

    #     Returns
    #     -------
    #     RenderObject
    #         Line render object
    #     """
    #     shape = Shapes.line(p0, p1, colour).transform(
    #         params.translate, params.rotate, params.scale)
    #     return self.add_object(shape, params)

    # def add_linestring(self, points, colour=Colour.WHITE, params = RenderParams()):
    #     """Add a line through a series of points.
        
    #     Parameters
    #     ----------
    #     points : array-like
    #         Array of points (x,y,z)
    #     colour : Colour, optional
    #         Line colour (default: white)
    #     params : RenderParams, optional
    #         Rendering parameters

    #     Returns
    #     -------
    #     RenderObject
    #         Line render object
    #     """
    #     points = np.atleast_2d(points)
    #     if points.shape[1] != 3:
    #         raise ValueError("Points must have 3 values (x,y,z) per point")
        
    #     shape = Shapes.linestring(points, colour).transform(
    #         params.translate, params.rotate, params.scale)
    #     return self.add_object(shape, params)

    # def add_triangle(self, p1, p2, p3, colour=None, params = RenderParams()):
    #     """Add a triangle defined by three points.
        
    #     Parameters
    #     ----------
    #     p1, p2, p3 : tuple
    #         Triangle vertices
    #     colour : Colour, optional
    #         Fill colour
    #     params : RenderParams, optional
    #         Rendering parameters

    #     Returns
    #     -------
    #     ObjectContainer
    #         Collection containing 'body' and 'wireframe' objects
    #     """
    #     colour = colour or self.default_face_colour
    #     objects = {}
        
    #     if params.show_body:
    #         shape = Shapes.triangle(p1, p2, p3, colour).transform(
    #             params.translate, params.rotate, params.scale)
    #         objects['body'] = self.add_object(shape, params)
        
    #     if params.show_wireframe:
    #         shape = Shapes.triangle_wireframe(
    #             p1, p2, p3, params.wireframe_colour or self.default_wireframe_colour
    #         ).transform(params.translate, params.rotate, params.scale)
    #         objects['wireframe'] = self.add_object(shape, params)
        
    #     return ObjectContainer(objects)

    # def add_rectangle(self, position, width, height, colour=None, params = RenderParams()):
    #     """Add a rectangle.
        
    #     Parameters
    #     ----------
    #     position : tuple
    #         Position (x,y)
    #     width : float
    #         Rectangle width
    #     height : float
    #         Rectangle height
    #     colour : Colour, optional
    #         Fill colour
    #     params : RenderParams, optional
    #         Rendering parameters

    #     Returns
    #     -------
    #     ObjectContainer
    #         Collection containing 'body' and 'wireframe' objects
    #     """
    #     colour = colour or self.default_face_colour
    #     objects = {}
        
    #     if params.show_body:
    #         shape = Shapes.rectangle(position, width, height, colour).transform(
    #             params.translate, params.rotate, params.scale)
    #         objects['body'] = self.add_object(shape, params)
        
    #     if params.show_wireframe:
    #         shape = Shapes.rectangle_wireframe(
    #             position, width * 1.01, height * 1.01, 
    #             params.wireframe_colour or self.default_wireframe_colour
    #         ).transform(params.translate, params.rotate, params.scale)
    #         objects['wireframe'] = self.add_object(shape, params)
        
    #     return ObjectContainer(objects)

    # def add_circle(self, position, radius, colour=None, params = RenderParams()):
    #     """Add a circle in the XY plane.
        
    #     Parameters
    #     ----------
    #     position : tuple
    #         Centre position
    #     radius : float
    #         Circle radius
    #     colour : Colour, optional
    #         Fill colour
    #     params : RenderParams, optional
    #         Rendering parameters

    #     Returns
    #     -------
    #     ObjectContainer
    #         Collection containing 'body' and 'wireframe' objects
    #     """
    #     colour = colour or self.default_face_colour
    #     segments = self.default_segments
        
    #     objects = {}
    #     if params.show_body:
    #         shape = Shapes.circle(position, radius, segments, colour).transform(
    #             params.translate, params.rotate, params.scale)
    #         objects['body'] = self.add_object(shape, params)
        
    #     if params.show_wireframe:
    #         shape = Shapes.circle_wireframe(
    #             position, radius * 1.01, segments, 
    #             params.wireframe_colour or self.default_wireframe_colour
    #         ).transform(params.translate, params.rotate, params.scale)
    #         objects['wireframe'] = self.add_object(shape, params)
        
    #     return ObjectContainer(objects)

    # def add_cube(self, position=(0,0,0), colour=None, params=RenderParams()):
    #     """Add a cube at specified position.
        
    #     Parameters
    #     ----------
    #     position : tuple
    #         XYZ coordinates of cube centre
    #     colour : Colour, optional
    #         Fill colour
    #     params : RenderParams, optional
    #         Rendering parameters
        
    #     Returns
    #     -------
    #     ObjectContainer
    #         Collection containing 'body' and 'wireframe' objects
    #     """
    #     colour = colour or self.default_face_colour
    #     objects = {}
        
    #     if params.show_body:
    #         shape = Shapes.cube(position=position, colour=colour).transform(
    #             params.translate, params.rotate, params.scale)
    #         objects['body'] = self.add_object(shape, params)
        
    #     if params.show_wireframe:
    #         shape = Shapes.cube_wireframe(
    #             position=position,
    #             colour=params.wireframe_colour or self.default_wireframe_colour
    #         ).transform(params.translate, params.rotate, params.scale)
    #         objects['wireframe'] = self.add_object(shape, params)
        
    #     return ObjectContainer(objects)

    # def add_beam(self, p0, p1, width, height, colour=None, params = RenderParams()):
    #     """Add a beam from p0 to p1.
        
    #     Parameters
    #     ----------
    #     p0 : tuple
    #         Start point
    #     p1 : tuple
    #         End point
    #     width : float
    #         Width of beam cross-section
    #     height : float
    #         Height of beam cross-section
    #     colour : Colour, optional
    #         Fill colour
    #     params : RenderParams, optional
    #         Rendering parameters

    #     Returns
    #     -------
    #     ObjectContainer
    #         Collection containing 'body' and 'wireframe' objects
    #     """
    #     colour = colour or self.default_face_colour
        
    #     body, wireframe = Shapes.beam(
    #         p0, p1, width, height, colour, 
    #         params.wireframe_colour or self.default_wireframe_colour
    #     )
        
    #     objects = {}
    #     if params.show_body:
    #         body = body.transform(params.translate, params.rotate, params.scale)
    #         objects['body'] = self.add_object(body, params)
        
    #     if params.show_wireframe:
    #         wireframe = wireframe.transform(params.translate, params.rotate, params.scale)
    #         objects['wireframe'] = self.add_object(wireframe, params)
        
    #     return ObjectContainer(objects)

    # def add_cylinder(self, position=(0,0,0), colour=None, params=RenderParams()):
    #     """Add a cylinder at specified position.
        
    #     Parameters
    #     ----------
    #     position : tuple
    #         XYZ coordinates of cylinder centre
    #     colour : Colour, optional
    #         Fill colour
    #     params : RenderParams, optional
    #         Rendering parameters

    #     Returns
    #     -------
    #     ObjectContainer
    #         Collection containing 'body' and 'wireframe' objects
    #     """
    #     colour = colour or self.default_face_colour
    #     segments = self.default_segments
        
    #     objects = {}
    #     if params.show_body:
    #         shape = Shapes.cylinder(
    #             position=position, segments=segments, colour=colour
    #         ).transform(params.translate, params.rotate, params.scale)
    #         objects['body'] = self.add_object(shape, params)
        
    #     if params.show_wireframe:
    #         shape = Shapes.cylinder_wireframe(
    #             position=position, segments=segments,
    #             colour=params.wireframe_colour or self.default_wireframe_colour
    #         ).transform(params.translate, params.rotate, params.scale)
    #         objects['wireframe'] = self.add_object(shape, params)
        
    #     return ObjectContainer(objects)

    # def add_cone(self, position=(0,0,0), colour=None, params=RenderParams()):
    #     """Add a cone at specified position.
        
    #     Parameters
    #     ----------
    #     position : tuple
    #         XYZ coordinates of cone centre
    #     colour : Colour, optional
    #         Fill colour
    #     params : RenderParams, optional
    #         Rendering parameters

    #     Returns
    #     -------
    #     ObjectContainer
    #         Collection containing 'body' and 'wireframe' objects
    #     """
    #     colour = colour or self.default_face_colour
    #     segments = self.default_segments
        
    #     objects = {}
    #     if params.show_body:
    #         shape = Shapes.cone(
    #             position=position, segments=segments, colour=colour
    #         ).transform(params.translate, params.rotate, params.scale)
    #         objects['body'] = self.add_object(shape, params)
        
    #     if params.show_wireframe:
    #         shape = Shapes.cone_wireframe(
    #             position=position, segments=segments,
    #             colour=params.wireframe_colour or self.default_wireframe_colour
    #         ).transform(params.translate, params.rotate, params.scale)
    #         objects['wireframe'] = self.add_object(shape, params)
        
    #     return ObjectContainer(objects)

    # def add_sphere(self, position=(0,0,0), radius=0.5, colour=None, params=RenderParams()):
    #     """Add a sphere at specified position.
        
    #     Parameters
    #     ----------
    #     position : tuple
    #         XYZ coordinates of sphere centre
    #     radius : float
    #         Sphere radius
    #     colour : Colour, optional
    #         Surface colour
    #     params : RenderParams, optional
    #         Rendering parameters

    #     Returns
    #     -------
    #     RenderObject
    #         Sphere render object
    #     """
    #     colour = colour or self.default_face_colour
    #     subdivisions = self.default_subdivisions
        
    #     shape = Shapes.sphere(
    #         position=position, radius=radius, 
    #         subdivisions=subdivisions, colour=colour
    #     ).transform(params.translate, params.rotate, params.scale)
    #     return self.add_object(shape, params)



    # def add_arrow(self, p0, p1, dimensions=None, colour=None, params = RenderParams()):
    #     """Add an arrow from p0 to p1.
        
    #     Parameters
    #     ----------
    #     p0 : tuple
    #         Start point (x,y,z)
    #     p1 : tuple
    #         End point (x,y,z)
    #     dimensions : ArrowDimensions, optional
    #         Arrow dimensions
    #     colour : Colour, optional
    #         Arrow colour
    #     params : RenderParams, optional
    #         Rendering parameters
        
    #     Returns
    #     -------
    #     ObjectContainer
    #         Collection containing 'body' and 'wireframe' objects
    #     """
    #     dimensions = dimensions or self.default_arrow_dimensions
    #     colour = colour or self.default_face_colour
    #     segments = self.default_segments
        
    #     body, wireframe = Shapes.arrow(p0, p1, dimensions, colour, 
    #                                               params.wireframe_colour, segments)
        
    #     objects = {}
    #     if params.show_body:
    #         body = body.transform(params.translate, params.rotate, params.scale)
    #         objects['body'] = self.add_object(body, params)
        
    #     if params.show_wireframe:
    #         wireframe = wireframe.transform(params.translate, params.rotate, params.scale)
    #         objects['wireframe'] = self.add_object(wireframe, params)
        
    #     return ObjectContainer(objects)


    # def add_axis(self, size=1.0, arrow_dimensions=None, origin_radius=0.035, 
    #             origin_colour=Colour.BLACK, params = RenderParams()):
    #     """Add coordinate axis arrows.
        
    #     Parameters
    #     ----------
    #     size : float, optional
    #         Length of axis arrows (default: 1.0)
    #     arrow_dimensions : ArrowDimensions, optional
    #         Arrow dimensions
    #     origin_radius : float, optional
    #         Radius of origin sphere (default: 0.035)
    #     origin_colour : Colour, optional
    #         Colour of origin sphere (default: BLACK)
    #     params : RenderParams, optional
    #         Rendering parameters
        
    #     Returns
    #     -------
    #     ObjectContainer
    #         Collection containing 'body' and 'wireframe' objects
    #     """
    #     arrow_dimensions = arrow_dimensions or self.default_arrow_dimensions
    #     segments = self.default_segments
    #     origin_subdivisions = self.default_subdivisions
        
    #     x_body, x_wireframe = Shapes.arrow(
    #         (0,0,0), (size,0,0), arrow_dimensions, 
    #         (1,0,0), params.wireframe_colour, segments)
    #     y_body, y_wireframe = Shapes.arrow(
    #         (0,0,0), (0,size,0), arrow_dimensions, 
    #         (0,1,0), params.wireframe_colour, segments)
    #     z_body, z_wireframe = Shapes.arrow(
    #         (0,0,0), (0,0,size), arrow_dimensions, 
    #         (0,0,1), params.wireframe_colour, segments)
        
    #     origin_shape = Shapes.sphere(position=(0,0,0), radius=origin_radius, subdivisions=origin_subdivisions, colour=origin_colour)
        
    #     objects = {}
    #     if params.show_body:
    #         shape = (x_body + y_body + z_body + origin_shape).transform(
    #             params.translate, params.rotate, params.scale)
    #         objects['body'] = self.add_object(shape, params)
        
    #     if params.show_wireframe:
    #         wireframe = (x_wireframe + y_wireframe + z_wireframe).transform(
    #             params.translate, params.rotate, params.scale)
    #         objects['wireframe'] = self.add_object(wireframe, params)
        
    #     return ObjectContainer(objects)

    # def add_axis_ticks(self, size=5.0, tick_params=DEFAULT_AXIS_TICKS, transform=None):
    #     """Add axis ticks in the XY plane.
         
    #     Parameters
    #     ----------
    #     size : float, optional
    #         Axis size (default: 5.0)
    #     tick_params : list, optional
    #         List of tick parameters for different detail levels
    #         Each dict contains: increment, tick_size, line_width (overrides RenderParams.line_width), tick_colour

    #     Returns
    #     -------
    #     ObjectContainer
    #         Collection containing tick objects at different detail levels
    #     """
    #     objects = {}
        
    #     for n, tick_level in enumerate(tick_params):
    #         increment = tick_level['increment']
    #         tick_size = tick_level['tick_size']
    #         line_width = tick_level['line_width']
    #         tick_colour = tick_level['tick_colour']
    #         tick_shape = None
            
    #         for i in np.arange(-size + increment, size + increment/2, increment):
    #             if abs(i) < 1e-10:  # Skip centre
    #                 continue
                    
    #             x_tick = Shapes.line((i, 0, 0), (i, tick_size, 0), tick_colour)
    #             y_tick = Shapes.line((0, i, 0), (tick_size, i, 0), tick_colour)
                
    #             if tick_shape is None:
    #                 tick_shape = x_tick + y_tick
    #             else:
    #                 tick_shape = tick_shape + x_tick + y_tick

    #         if tick_shape is not None:
    #             tick_shape = tick_shape.transform(params.translate, params.rotate, params.scale)
    #             tick_object = self.add_object(tick_shape, level_params)
                
    #             objects[f'ticks-{n}'] = tick_object
        
    #     return ObjectContainer(objects)

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

    # def scatter(self, x, y, colour=None, params = RenderParams()):
    #     """Create a scatter plot of x,y points.
        
    #     Parameters
    #     ----------
    #     x : float or array-like
    #         X coordinates
    #     y : float or array-like
    #         Y coordinates
    #     colour : Colour, optional
    #         Point colour
    #     params : RenderParams, optional
    #         Rendering parameters

    #     Returns
    #     -------
    #     RenderObject
    #         Points render object
    #     """
    #     x = np.atleast_1d(x)
    #     y = np.atleast_1d(y)
        
    #     if len(x) != len(y):
    #         raise ValueError("x and y must have same length")
    #     points = np.column_stack((x, y, np.zeros_like(x)))
        
    #     # Use point shader if not specified
    #     params.shader = params.shader or self.point_shader
    #     shape = Shapes.create_points(points, colour or self.default_face_colour)
    #     return self.add_object(shape, params)

    # def plot(self, x, y, colour=Colour.WHITE, params = RenderParams()):
    #     """Plot a line through a series of x,y points.
        
    #     Parameters
    #     ----------
    #     x : float or array-like
    #         X coordinates
    #     y : float or array-like
    #         Y coordinates
    #     colour : Colour, optional
    #         Line colour (default: white)
    #     params : RenderParams, optional
    #         Rendering parameters

    #     Returns
    #     -------
    #     RenderObject
    #         Line render object
    #     """
    #     x = np.atleast_1d(x)
    #     y = np.atleast_1d(y)
        
    #     if len(x) != len(y):
    #         raise ValueError("x and y must have same length")
        
    #     points = np.column_stack((x, y, np.zeros_like(x)))
    #     shape = Shapes.create_linestring(points, colour)
        
    #     return self.add_object(shape, params)

    # def add_blank_objects(self, draw_types: Dict[str, int], params = RenderParams()):
    #     """Add multiple blank objects.
        
    #     Parameters
    #     ----------
    #     draw_types : dict
    #         Dictionary of draw types for each object
    #     params : RenderParams, optional
    #         Rendering parameters

    #     Returns
    #     -------
    #     ObjectContainer
    #         Collection of blank objects
    #     """
    #     return ObjectContainer({
    #         name: self.add_blank_object(draw_type, params) for name, draw_type in draw_types.items()
    #     })

    # def add_blank_object(self, draw_type=GL_TRIANGLES, params = RenderParams()):
    #     """Add a blank object for a dynamic / stream buffer.
        
    #     Parameters
    #     ----------
    #     draw_type : GL_enum, optional
    #         OpenGL primitive type (TRIANGLES, LINES, etc)
    #     params : RenderParams, optional
    #         Rendering parameters

    #     Returns
    #     -------
    #     RenderObject
    #         Blank render object
    #     """        
    #     return self._add_object_base(None, None, draw_type, params)

    # def add_object(self, shape_data, params = RenderParams()):
    #     """Create and add a new render object to the scene.

    #     Parameters
    #     ----------
    #     shape_data : shapeData
    #         Vertex and index data for the object
    #         Set to None for dynamic / stream buffer
    #     params : RenderParams, optional
    #         Rendering parameters
                     
    #     Returns
    #     -------
    #     RenderObject
    #         Created render object
    #     """
    #     vertices = shape_data.get_vertices()
    #     indices = shape_data.get_indices()
    #     draw_type = shape_data.draw_type
        
    #     return self._add_object_base(vertices, indices, draw_type, params)





    # def _add_object_base(self, vertices, indices, draw_type, params = RenderParams()):
    #     """Create and add a new render object to the scene.

    #     Parameters
    #     ----------
    #     vertices : np.array or None
    #         Vertex data for the object
    #     indices : np.array or None
    #         Index data for the object
    #     draw_type : GL_enum, optional
    #         OpenGL primitive type (TRIANGLES, LINES, etc)
    #     params : RenderParams, optional
    #         Rendering parameters

    #     Returns
    #     -------
    #     RenderObject
    #         Created render object
    #     """
    #     params.shader = params.shader or self.default_shader
    #     obj = Object(vertices, indices, draw_type, params.line_width, 
    #                 params.point_size, params.point_shape, params.buffer_type, 
    #                 params.selectable, params.shader, params.alpha)
    #     self.objects.append(obj)
    #     return obj

    # def add_object(self,
    #                shape: Optional[Shape] = None,
    #                transform: Optional[Transform] = None,
    #                point_size: float = 1.0,
    #                line_width: float = 1.0,
    #                point_shape: PointShape = PointShape.CIRCLE,
    #                alpha: float = 1.0,
    #                static: bool = False, 
    #                selectable: bool = True
    # ):
    #     """Adds a new render object to the scene.
        
    #     Parameters
    #     ----------
    #     shape : Shape, optional
    #         Shape data containing vertices and indices, the draw type and the shader
    #     transform : Transform, optional
    #         Transform matrix to apply to the object
    #     point_size : float, optional
    #         Size of points when rendering point primitives (default: 1.0)
    #     line_width : float, optional
    #         Width of lines when rendering line primitives (default: 1.0)
    #     point_shape : PointShape, optional
    #         Shape to use when rendering points (default: CIRCLE)
    #     alpha : float, optional
    #         Transparency value between 0 and 1 (default: 1.0)
    #     static : bool, optional
    #         Whether the object's geometry is static (default: False)
    #     selectable : bool, optional
    #         Whether the object can be selected (default: True)
            
    #     Returns
    #     -------
    #     Object
    #         The created render object
    #     """
        
    #     objs = ObjectContainer()
        
    #     # Create object
    #     obj = Object(
    #         point_size=point_size,
    #         line_width=line_width,
    #         point_shape=point_shape,
    #         alpha=alpha,
    #         static=static,
    #         selectable=selectable,
    #     )
        
    #     # Set shape
    #     if shape is not None:
    #         obj.set_shape(shape)
        
    #     # Set transform matrix
    #     if transform is not None:
    #         obj.set_transform_matrix(transform)
            
    #     # Add to scene
    #     self.objects.append(obj)
    #     return obj

    def add_object(self,
                   shapes: Optional[List[Shape]] = None,
                   transform: Optional[Transform] = None,
                   point_size: float = 1.0,
                   line_width: float = 1.0,
                   point_shape: PointShape = PointShape.CIRCLE,
                   alpha: float = 1.0,
                   static: bool = False, 
                   selectable: bool = True,
    ):
        """Adds a new render object to the scene.
        
        Parameters
        ----------
        shapes : List[Shape] or Shape, optional
            Shape data containing vertices and indices, the draw type and the shader
        transform : Transform, optional
            Transform matrix to apply to the object
        point_size : float, optional
            Size of points when rendering point primitives (default: 1.0)
        line_width : float, optional
            Width of lines when rendering line primitives (default: 1.0)
        point_shape : PointShape, optional
            Shape to use when rendering points (default: CIRCLE)
        alpha : float, optional
            Transparency value between 0 and 1 (default: 1.0)
        static : bool, optional
            Whether the object's geometry is static (default: False)
        selectable : bool, optional
            Whether the object can be selected (default: True)
            
        Returns
        -------
        Object
            The created render object
        """
        
        objects = ObjectContainer(self, point_size, line_width, point_shape, alpha, static, selectable)
        
        # Set shape
        if shapes is not None:
            objects.set_shape(shapes)
        
        # Set transform matrix
        if transform is not None:
            objects.set_transform_matrix(transform)
            
        return objects
