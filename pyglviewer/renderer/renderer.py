from dataclasses import dataclass, replace
from typing import Dict, List, Tuple, Optional
from OpenGL.GL import *
import numpy as np
from pyglviewer.utils.colour import Colour
from pyglviewer.utils.config import Config
from pyglviewer.utils.transform import Transform
from pyglviewer.renderer.shapes import Shapes, Shape, ArrowDimensions
from pyglviewer.renderer.objects import VertexBuffer, IndexBuffer, VertexArray, RenderObject, Object
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
        
    def clear(self):
        """Clear the renderer."""   
        self.objects = []
        RenderObject.reset_global_object_counter()
        
    def get_selected_object(self):
        """Get all selected objects."""
        selected_objects = []
        for obj in self.objects:
            for render_obj in obj._render_objects:
                if getattr(render_obj, 'selected', False):
                    selected_objects.append(obj)
        # Remove duplicates
        return list(set(selected_objects))
    
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
            for render_obj in obj._render_objects:
                # Add objects to appropriate buffer based on their type (if update is required)
                self.batch_renderer.add_object_to_batch(render_obj)
        
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

    def add_object(self, object):
        self.objects.append(object)
        return self.objects[-1]
            
    def remove_object(self, object):
        self.objects.remove(object)
        