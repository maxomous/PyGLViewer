from dataclasses import dataclass, replace
from typing import Dict, List, Tuple, Optional
from OpenGL.GL import *
import numpy as np
from pyglviewer.utils.colour import Colour
from pyglviewer.utils.config import Config
from pyglviewer.utils.transform import Transform
from pyglviewer.renderer.shapes import Shapes, Shape, ArrowDimensions
from pyglviewer.renderer.objects import VertexBuffer, IndexBuffer, VertexArray, Object
from pyglviewer.renderer.render_buffer import RenderBuffer
from pyglviewer.renderer.light import Light, default_lighting
from pyglviewer.renderer.shader import Shader, DefaultShaders, PointShape
from pyglviewer.gui.imgui_render_buffer import ImguiRenderBuffer, Image, Text


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
        self.imgui_render_buffer = ImguiRenderBuffer()

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
        """
        Update the rendering parameters of an object.

        Parameters
        ----------
        name : str
            Unique identifier for this object.
        shape : Optional[Shape | list[Shape]], default=None
            Geometry to associate with the object (single or multiple shapes).
            Default is an empty list of shape dictionaries at initialization.
        transform : Optional[Transform], default=None
            Transformation to apply (translation, rotation, scale).
            Defaults to an identity `Transform`.
        point_size : Optional[float], default=None
            Size of point primitives. Defaults to 1.0.
        line_width : Optional[float], default=None
            Width of line primitives. Defaults to 1.0.
        point_shape : Optional[PointShape], default=None
            Shape used when rendering point primitives.
            Defaults to `PointShape.CIRCLE`.
        alpha : Optional[float], default=None
            Transparency value (0.0 = fully transparent, 1.0 = fully opaque).
            Defaults to 1.0 (fully opaque).
        selectable : Optional[bool], default=None
            Whether the object can be selected. Defaults to True.
        metadata : Optional[dict], default=None
            Arbitrary metadata associated with the object. Defaults to {}.
        static : Optional[bool], default=None
            Whether the object is static (non-dynamic) for buffer optimization.
        """

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
    
    def _delete_object(self, name: str):
        # Check object exists  
        if name not in self.object_map:
            return
        buffer = self.static_buffer if self.object_map[name]['buffer'] == 'static' else self.dynamic_buffer
        object = buffer.objects[name]
        # Free vertices / indices from the buffer
        for shape_data in object._shape_data:
            buffer._free_segment(shape_data)
        # Remove from object list
        del buffer.objects[name]
        del self.object_map[name]
        
    def delete_objects(self, names: str | list[str]):
        # Support both single name and list of names
        if isinstance(names, str):
            names = [names]
        for name in names:
            self._delete_object(name)



    def get_objects_by_metadata(self, metadata_key, metadata_value):
        objects = []
        for buffer_type in ['static', 'dynamic', 'text', 'image']:
            if buffer_type == 'static':
                objects = self.static_buffer.objects
            elif buffer_type == 'dynamic':
                objects = self.dynamic_buffer.objects
            elif buffer_type == 'text':
                objects = self.imgui_render_buffer.text_objects
            elif buffer_type == 'image':
                objects = self.imgui_render_buffer.image_objects
            else:
                raise ValueError('Unknown buffer type')
            for obj in objects.values():
                if obj.get_metadata()[metadata_key] == metadata_value:
                    objects.append(obj)
        return objects

        
        
        
    def get_selected_objects(self): 
        """Get all selected objects."""
        selected_objects = []
        for buffer_type in ['static', 'dynamic', 'text', 'image']:
            
            if buffer_type == 'static':
                objects = self.static_buffer.objects
            elif buffer_type == 'dynamic':
                objects = self.dynamic_buffer.objects
            elif buffer_type == 'text':
                objects = self.imgui_render_buffer.text_objects
            elif buffer_type == 'image':
                objects = self.imgui_render_buffer.image_objects
            else:
                raise ValueError('Unknown buffer type')
            for name, obj in objects.items():
                if obj.get_selected():
                    if not any(d["object"] == obj for d in selected_objects):
                        selected_objects.append({"object": obj, "name": name, "buffer_type": buffer_type})
        # Remove duplicates
        return selected_objects
    
    
    def update_text(
        self, 
        name:       str,
        texts:      Optional[list[Text]] = None,
        align:      Optional[tuple[float, float]] = None, 
        font:       Optional[str] = None,
        colour:     Optional[tuple[float, float, float]] = None,        
        alpha:      Optional[float] = None,
        selectable: Optional[bool] = None,
        metadata:   Optional[dict] = None
    ):
        """
        Either create a new text or modify an existing text.

        Parameters
        ----------
        name : str
            Unique identifier for this text object.
        texts : Optional[list[Text]]
            List of text elements to render.
        align : Optional[tuple[float, float]]
            Alignment offset (x, y) relative to the anchor point.
        font : Optional[str]
            Font name or family used for rendering the text.
        colour : Optional[tuple[float, float, float]]
            RGB colour of the text (values in range 0.0–1.0).
        alpha : Optional[float]
            Opacity of the text (0.0 = fully transparent, 1.0 = fully opaque).
        selectable : Optional[bool]
            Whether the text can be selected.
        metadata : Optional[dict]
            Arbitrary metadata associated with the text object.
        """
        self.imgui_render_buffer.update_text(
            name=name,
            texts=texts,
            align=align, 
            font=font,
            colour=colour,        
            alpha=alpha,
            selectable=selectable,
            metadata=metadata
        )


    def update_image(
        self, 
        name:       str,
        images:     Optional[list[Image]] = None,
        align:      Optional[tuple[float, float]] = None, 
        selectable: Optional[bool] = None,
        metadata:   Optional[dict] = None,
    ):
        """
        Either create a new image or modify an existing image.

        Parameters
        ----------
        name : str
            Unique identifier for this image object.
        images : Optional[list[Image]]
            List of images to render.
        align : Optional[tuple[float, float]]
            Alignment offset (x, y) relative to the anchor point.
        selectable : Optional[bool]
            Whether the image can be selected.
        metadata : Optional[dict]
            Arbitrary metadata associated with the image object.
        """
        self.imgui_render_buffer.update_image(
            name=name,
            images=images,
            align=align, 
            selectable=selectable,
            metadata=metadata
        )

    def remove_texts(self, names: str | list[str]):
        """Remove text(s) using either a name id or a list of names"""
        self.imgui_render_buffer.remove_texts(names)
        
    def remove_images(self, names: str | list[str]):
        """Remove image(s) using either a name id or a list of names"""
        self.imgui_render_buffer.remove_images(names)
     
    
    def clear(self):
        """Clear both static and dynamic buffers, text and images."""
        self.static_buffer.clear()
        self.dynamic_buffer.clear()
        self.imgui_render_buffer.clear()
        self.object_map = {}
    
    def get_stats(self):
        """Get combined rendering statistics."""
        return {
            'static': self.static_buffer.get_stats(),
            'dynamic': self.dynamic_buffer.get_stats(),
        } |  self.imgui_render_buffer.get_stats()
