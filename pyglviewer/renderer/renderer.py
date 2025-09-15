from dataclasses import dataclass, replace
from typing import Dict, List, Tuple, Optional
from OpenGL.GL import *
import numpy as np
from pyglviewer.utils.colour import Colour
from pyglviewer.utils.config import Config
from pyglviewer.utils.transform import Transform
from pyglviewer.renderer.shapes import Shapes, Shape, ArrowDimensions
from pyglviewer.renderer.objects import VertexBuffer, IndexBuffer, VertexArray, Object
from pyglviewer.renderer.batch_renderer import RenderBuffer
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
        # Create static and dynamic buffers
        self.static_buffer = RenderBuffer(max_static_vertices, max_static_indices, GL_STATIC_DRAW)
        self.dynamic_buffer = RenderBuffer(max_dynamic_vertices, max_dynamic_indices, GL_DYNAMIC_DRAW)
        # Stores the buffer locations of the objects (i.e. object_map['my object'] = { 'buffer': 'static'})
        self.object_map = {}
                
        self.lights = []
               
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

    # def batch_renderer_update(self):
    #     """Update buffers if required."""
    #     # Clear batch renderer buffers (if update is required)
    #     self.batch_renderer.clear()
    #     # Submit all objects to the batch renderer 
    #     for obj in self.objects:
    #         # Add objects to appropriate buffer based on their type (if update is required)
    #         self.batch_renderer.add_object_to_batch(obj)
        
    def draw(self, view_matrix: np.ndarray, projection_matrix: np.ndarray, 
             camera_pos: np.ndarray, lights: Optional[List] = None):
        """Render all objects in the scene, using batching"""
        # Render static objects first
        self.static_buffer.render_buffer(view_matrix, projection_matrix, camera_pos, lights)
        # Then render dynamic objects
        self.dynamic_buffer.render_buffer(view_matrix, projection_matrix, camera_pos, lights)
        
        # Reset to default state
        glEnable(GL_DEPTH_TEST)
        glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
        glLineWidth(1.0)
        glPointSize(1.0)
 
    def clear_framebuffer(self):
        """Clear the framebuffer with a dark teal background."""
        r, g, b = self.config["background_colour"]
        glClearColor(r, g, b, 1.0)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)



    def update_object(
        self, 
        name:        str,
        shape:       Optional[Shape | list[Shape]] = None,
        transform:   Optional[Transform]  = None,
        point_size:  Optional[float]      = None,
        line_width:  Optional[float]      = None,
        point_shape: Optional[PointShape] = None,
        alpha:       Optional[float]      = None,
        selectable:  Optional[bool]       = None,
        metadata:    Optional[dict]       = None,
        static:      Optional[bool]       = None,
    ):
        # Create and add object to map if it doesn't already exist
        if name not in self.object_map:
            buffer = self.static_buffer if static else self.dynamic_buffer
            buffer.add_object(name, Object())
            self.object_map[name] = {'buffer': 'static' if static else 'dynamic'} # will default to dynamic if None
        
        # Buffer type (static / dynamic) cannot be changed after first call to this function TODO: It wouldn't be hard to add in this feature, make sure to set object_map['my_object']['buffer']

        buffer_type = self.object_map[name]['buffer']
        if ((static == True) and (buffer_type != 'static')) or ((static == False) and (buffer_type != 'dynamic')):
            raise ValueError('Buffer type cannot be changed after the first call to update_object() with that name')
        # Get the correct buffer & object
        buffer = self.static_buffer if buffer_type == 'static' else self.dynamic_buffer
        object = buffer.objects[name]
        # Add shape data to objects and upload data to opengl buffer 
        if shape is not None:
            buffer.set_object_shapes(name, shape)
        # Setters
        if transform is not None:
            object.set_transform(transform)
        if point_size is not None:
            object.set_point_size(point_size)
        if line_width is not None:
            object.set_line_width(line_width)
        if point_shape is not None:
            object.set_point_shape(point_shape)
        if alpha is not None:
            object.set_alpha(alpha)
        if selectable is not None:
            object.set_selectable(selectable)
        if metadata is not None:
            object.set_metadata(metadata)
    
        # select()
        # deselect()
        # toggle_select()
            
    

        


    # def add_object_to_batch(self, name, object: Object):
    #     """Add object to appropriate buffer based on type."""
    #     buffer = self.static_buffer if object._static else self.dynamic_buffer
    #     buffer.add_object(object)


    #     self.batch_renderer.add_object

    # def add_object(self, object):
    #     '''Add new object to batch, returns that object'''
    #     self.objects.append(object)
    #     return self.objects[-1]
            
    # def remove_object(self, object):
    #     '''Remove object(s) from the batch. object can be an Object or a list of Objects'''
    #     if isinstance(object, list):
    #         for obj in object:
    #             if obj in self.objects:
    #                 self.objects.remove(obj)
    #     else:
    #         if object in self.objects:
    #             self.objects.remove(object)
        
    # def clear(self):
    #     """Clear the renderer. Used to clear all (including static) objects"""   
    #     self.objects = []
        
    def get_selected_objects(self): 
        """Get all selected objects."""
        selected_objects = []
        for buffer_type in ['static', 'dynamic']:
            buffer = self.static_buffer if buffer_type == 'static' else self.dynamic_buffer
            for name, obj in buffer.objects.items():
                if obj.get_selected():
                    selected_objects.append((obj, name, buffer_type))
        # Remove duplicates
        return list(set(selected_objects))

    
    
    
    # def add_object_to_batch(self, object: Object):
    #     """Add object to appropriate buffer based on type."""
    #     buffer = self.static_buffer if object._static else self.dynamic_buffer
    #     buffer.add_object_to_buffer(object)
        
    def clear(self):
        """Clear both static and dynamic buffers."""
        self.static_buffer.clear()
        self.dynamic_buffer.clear()
    
    # def update_buffers(self):
    #     """Update static buffer if needed."""
    #     self.static_buffer.update_buffers()
    #     self.dynamic_buffer.update_buffers()
    
    
    def get_stats(self):
        """Get combined rendering statistics."""
        return {
            'static': self.static_buffer.get_stats(),
            'dynamic': self.dynamic_buffer.get_stats()
        }
