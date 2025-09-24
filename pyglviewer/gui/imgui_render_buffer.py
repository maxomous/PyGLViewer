import imgui
import numpy as np
from dataclasses import dataclass
from typing import Tuple, Optional
from pyglviewer.utils.colour import Colour

# TODO: Using ImGui for text rendering means text appears on top of objects, ideally
#       we should implement our own text rendering so as to account for depth. It 
#       may also be faster.


# TODO: Add selection functions
# TODO: Bounds functions?
    
################ TEXTS ################

class Text:
    def __init__(self, 
        text: str, 
        world_pos: Optional[Tuple[float, float, float]] = None, 
        screen_pos: Optional[Tuple[float, float]] = None
    ):
        '''
        Holds text and position data to render using imgui drawlist.
        If screen position is set to None, the world position is projected to 
        the screen position every frame (Note: This is much slower than 
        providing screen position directly but allows the position to 
        update when the camera moves) 
        '''
        self.text = text
        self.world_pos = world_pos
        self.screen_pos = screen_pos 
        self.size: Tuple[float, float] = (0, 0) # updated in render loop
        self.size_needs_update: bool = True
        self.bounds = { 'min': (0, 0), 'max': (0, 0) }
        
class Texts:
    """
    Factory class providing static methods to create various 2D Text.
    """  
    @staticmethod
    def text(text: str, world_pos: Tuple[float, float, float]):
        return [Text(text=text, world_pos=world_pos)]
    
    @staticmethod
    def text_2D(text, screen_pos: Tuple[float, float]):
        return [Text(text=text, screen_pos=screen_pos)]

    @staticmethod
    def axis(limits=[-10, 10], increment=1):
        """Add axis labels to the viewport."""
        # TODO: Handle offset from axis
        texts = []
        # Text in 3d space
        for i in range(limits[0], limits[1]+1, increment):
            if i != 0: # only draw 0 once
                texts = texts + Texts.text(f"{i}", (i, 0, 0))
            texts = texts + Texts.text(f"{i}", (0, i, 0))
        return texts
    
class TextObject:
    """
    TextObject hold a list of texts and their settings required for rendering 
    """  
    def __init__(self):
        self._texts: list[Text]              = []        # list of texts to render (equiv. to shapes)
        self._align: tuple[float, float]     = (0, 0)
        self._font: Optional[str]            = None      # will use current font if None
        self._colour: tuple[float, float, float] = (1.0, 1.0, 1.0)
        self._alpha: float                   = 1.0
        self._imgui_colour: int              = 0xFFFFFFFF
        self._colour_needs_update: bool      = True
        self._selectable: bool               = True
        self._selected: bool                 = False
        self._metadata: dict                 = {}
        # Cached boundary region
        self._world_bounds: Optional[dict]   = None
    
    def select(self):        
        """Mark this object as selected. Only selects if object's selectable flag is True."""
        if self._selectable:
            self._selected = True
    def deselect(self):
        """Mark this object as not selected."""
        self._selected = False
    def toggle_select(self):
        """Toggle the selection state of this object. Only toggles if object's selectable flag is True."""
        if self._selectable:
            self._selected = not self._selected
    def get_selected(self):
        return self._selected
    def get_midpoint(self):
        '''Returns midpoint of bounding box of object'''
        bounds = self.get_bounds()
        if bounds is None:
            return None
        return (np.array(bounds['min']) + np.array(bounds['max'])) / 2
    def get_bounds(self):
        """Calculate accurate bounds in world space.
        
        Returns
        -------
        dict or None
            Dictionary containing 'min' and 'max' bounds as np.ndarray, or None if no vertex data
        """
        if self._texts is None or len(self._texts) == 0:
            return None
        p_min = (min([text.bounds['min'][0] for text in self._texts]), min([text.bounds['min'][1] for text in self._texts]))
        p_max = (max([text.bounds['max'][0] for text in self._texts]), max([text.bounds['max'][1] for text in self._texts]))
        self._world_bounds = { 'min': p_min, 'max': p_max }
        # Set in render loop
        return self._world_bounds
    def is_point(self):
        return False

################ IMAGES ################

class Image:
    def __init__(self, 
        name_id: str, 
        size: Tuple[float, float], 
        world_pos: Optional[Tuple[float, float, float]] = None, 
        screen_pos: Optional[Tuple[float, float]] = None
    ):
        '''
        Holds image and position data to render using imgui drawlist.
        If screen position is set to None, the world position is projected to 
        the screen position every frame (Note: This is much slower than 
        providing screen position directly but allows the position to 
        update when the camera moves) 
        '''
        self.name_id = name_id
        self.size = size
        self.world_pos = world_pos
        self.screen_pos = screen_pos 
        self.bounds = { 'min': (0, 0), 'max': (0, 0) }

class Images:
    """
    Factory class providing static methods to create various 2D Image.
    """  
    @staticmethod
    def image(name: str, size: Tuple[float, float], world_pos: Tuple[float, float, float]):
        return [Image(name_id=name, size=size, world_pos=world_pos)]
    
    @staticmethod
    def image_2D(name: str, size: Tuple[float, float], screen_pos: Tuple[float, float]):
        return [Image(name_id=name, size=size, screen_pos=screen_pos)]

class ImageObject:
    """
    ImageObject hold a list of images and their settings required for rendering 
    """  
    def __init__(self):
        self._images: list[Image]            = []        # list of images to render (equiv. to shapes)
        self._align: tuple[float, float]     = (0, 0)
        self._selectable: bool               = True
        self._selected: bool                 = False
        self._metadata: dict                 = {}
        # # Cached boundary region
        self._world_bounds: Optional[dict]   = None
        # self._bounds_needs_update: bool      = True
    
    def select(self):        
        """Mark this object as selected. Only selects if object's selectable flag is True."""
        if self._selectable:
            self._selected = True
    def deselect(self):
        """Mark this object as not selected."""
        self._selected = False
    def toggle_select(self):
        """Toggle the selection state of this object. Only toggles if object's selectable flag is True."""
        if self._selectable:
            self._selected = not self._selected
    def get_selected(self):
        return self._selected
    
    def get_midpoint(self):
        '''Returns midpoint of bounding box of object'''
        bounds = self.get_bounds()
        if bounds is None:
            return None
        return (np.array(bounds['min']) + np.array(bounds['max'])) / 2
    def get_bounds(self):
        """Calculate accurate bounds in world space.
        
        Returns
        -------
        dict or None
            Dictionary containing 'min' and 'max' bounds as np.ndarray, or None if no vertex data
        """
        if self._images is None or len(self._images) == 0:
            return None
        p_min = (min([image.bounds['min'][0] for image in self._images]), min([image.bounds['min'][1] for image in self._images]))
        p_max = (max([image.bounds['max'][0] for image in self._images]), max([image.bounds['max'][1] for image in self._images]))
        self._world_bounds = { 'min': p_min, 'max': p_max }
        # Set in render loop
        return self._world_bounds
    def is_point(self):
        return False
################ RENDER BUFFER ################

class ImguiRenderBuffer:
    """Batch renderer for drawing text and images at 3D world positions using ImGui."""
    
    def __init__(self):
        self.text_objects = {}      # dicionary of TextObjects
        self.image_objects = {}     # dictionary of ImageObjects
    
    def update_text(
        self, 
        name:       str,
        texts:      Optional[list[Text]]        = None,
        align:      Optional[tuple[float, float]] = None,
        font:       Optional[str]               = None,
        colour:     Optional[tuple[float, float, float]] = None,        
        alpha:      Optional[float]             = None,   # opacity
        selectable: Optional[bool]              = None,
        metadata:   Optional[dict]              = None
        ):
        """Either create a new text or modify an existing text"""

        # Create and add text if it doesn't already exist
        if name not in self.text_objects:
            self.text_objects[name] = TextObject()
        obj = self.text_objects[name]
        # Setters
        if texts is not None:
            obj._texts = texts
        if align is not None:
            obj._align = align
        if font is not None:
            obj._font = font
            for text in obj._texts: 
                text.size_needs_update = True
        if colour is not None:    
            obj._colour = colour
            obj._colour_needs_update = True
        if alpha is not None:
            obj._alpha = alpha
            obj._colour_needs_update = True
        if selectable is not None:
            obj._selectable = selectable
        if metadata is not None:
            obj._metadata = metadata
            
        # Update imgui colour
        if obj._colour_needs_update:
            obj._imgui_colour = imgui.get_color_u32_rgba(obj._colour[0], obj._colour[1], obj._colour[2], obj._alpha)    # ImGui format (packed 32-bit RGBA)
            obj._colour_needs_update = False
    
    def update_image(
        self, 
        name:       str,
        images:     Optional[list[Image]]       = None,
        align:      Optional[tuple[float, float]] = None,
        selectable: Optional[bool]              = None,
        metadata:   Optional[dict]              = None,
        ):
        """Either create a new image or modify an existing image"""
        # Create and add image if it doesn't already exist
        if name not in self.image_objects:
            self.image_objects[name] = ImageObject()
        obj = self.image_objects[name]
        # Setters
        if images is not None:
            obj._images = images
        if align is not None:
            obj._align = align
        if selectable is not None:
            obj._selectable = selectable
        if metadata is not None:
            obj._metadata = metadata    
    
    def remove_texts(self, names: str | list[str]):
        """Remove text(s) using either a name id or a list of names"""
        # Support both single name and list of names
        if isinstance(names, str):
            names = [names]
        # Remove each of the texts
        for name in names:
            self.text_objects.pop(name, None)
            
    def remove_images(self, names: str | list[str]):
        """Remove image(s) using either a name id or a list of names"""
        # Support both single name and list of names
        if isinstance(names, str):
            names = [names]
        # Remove each of the images
        for name in names:
            self.image_objects.pop(name, None)
    
    def clear(self):
        """Clear all text and images."""
        self.text_objects =  {}
        self.image_objects = {}
        
    
    def draw(self, mouse, imgui_manager, images):
        """
        Render the text batches using ImGui.
        Because ImGui is a window system, we need to create an invisible window
        that covers the entire viewport to render the text. Text is then 
        rendered to the window in a position relative to the 3D coordinate. 
        Must be called whilst imgui is rendering.
        """
        # Create invisible window that covers the entire viewport
        viewport = imgui.get_main_viewport()
        window_pos = viewport.pos
                
        imgui.set_next_window_position(window_pos.x, window_pos.y)
        imgui.set_next_window_size(viewport.size.x, viewport.size.y)
        # Create transparent overlay window
        imgui.begin("##TextOverlay", 
                   flags=imgui.WINDOW_NO_DECORATION |
                         imgui.WINDOW_NO_MOVE |
                         imgui.WINDOW_NO_SCROLL_WITH_MOUSE |
                         imgui.WINDOW_NO_SAVED_SETTINGS |
                         imgui.WINDOW_NO_INPUTS |
                         imgui.WINDOW_NO_FOCUS_ON_APPEARING |
                         imgui.WINDOW_NO_BRING_TO_FRONT_ON_FOCUS |
                         imgui.WINDOW_NO_BACKGROUND)
        
        # Render text objects
        for obj in self.text_objects.values():
            # Set font
            if obj._font:
                imgui_manager.push_font(obj._font)
            # Add each text to imgui draw list
            for text in obj._texts:
                # Update text size
                if text.size_needs_update:
                    text.size = imgui.calc_text_size(text.text, True)
                    text.size_needs_update = False
                # Project 3D position to screen space
                if text.world_pos is not None:
                    text.screen_pos = mouse.project_world_to_screen(text.world_pos)
                # Adjust window position, align text and draw
                if (text.screen_pos is not None) and (text.screen_pos != (None, None)):
                    adjusted_pos = np.array(text.screen_pos) - np.array(window_pos) + np.array(obj._align) * np.array(text.size)
                    # update text bounds
                    text.bounds = {
                        'min': (adjusted_pos[0], adjusted_pos[1]),
                        'max': (adjusted_pos[0]+text.size[0], adjusted_pos[1]+text.size[1])
                    }
                    # Add to imgui draw list
                    imgui.get_window_draw_list().add_text(adjusted_pos[0], adjusted_pos[1], obj._imgui_colour, text.text)                    
            # Unset font
            if obj._font:
                imgui_manager.pop_font()
        
        # Render image objects
        for obj in self.image_objects.values():
            # Add each text to imgui draw list
            for img in obj._images:
                # Project 3D position to screen space
                if img.world_pos is not None:
                    img.screen_pos = mouse.project_world_to_screen(img.world_pos)
                # Adjust window position, align text and draw
                if (img.screen_pos is not None) and (img.screen_pos != (None, None)) and (img.name_id is not None):
                    # Adjust window position & align image
                    texture_id = images[img.name_id]
                    adjusted_pos = np.array(img.screen_pos) - np.array(window_pos) + np.array(obj._align) * np.array(img.size)
                    p0 = (adjusted_pos[0], adjusted_pos[1])
                    p1 = (adjusted_pos[0] + img.size[0], adjusted_pos[1] + img.size[1])
                    # update text bounds
                    img.bounds = {
                        'min': p0,
                        'max': p1
                    }
                    # Add to imgui draw list
                    imgui.get_window_draw_list().add_image(texture_id, p0, p1)
                    
        # End text rendering batch
        imgui.end()

    def get_stats(self):
        """Get statistics about the renderer."""
        return {
            "total_text_objects": len(self.text_objects),
            "total_image_objects": len(self.image_objects),
            "total_texts": sum([len(obj._texts) for obj in self.text_objects]),
            "total_images": sum([len(obj._images) for obj in self.image_objects])
        }






# class ImguiRenderBuffer:
#     """Batch renderer for drawing text and images at 3D world positions using ImGui."""
    
#     def __init__(self, mouse, imgui_manager):
#         self.window_pos = (0, 0)
#         self.mouse = mouse
#         self.imgui_manager = imgui_manager
#         self.text_batches = []  # Store text information for batch rendering
#         self.image_batches = []  # Store image information for batch rendering
#         self.global_text_counter = 0
#         self.global_image_counter = 0
    
#     def add_text(self, text='', world_pos=(0, 0, 0), colour=Colour.WHITE, align_text=(0, 0), font=None, static=False):
#         """Add text to be rendered at a 3D world position. 
#         Stores text data to later (in that frame) be rendered in imgui window.
#         Can be called any time in frame,
        
#         Args:
#             text (str): Text to display
#             world_pos (tuple): 3D world position (x,y,z)
#             colour (tuple): RGBA colour values (0-1)
#             align_text (tuple): Text alignment (x,y)
#             font (imgui.Font, optional): ImGui font to use. Uses default if None.
#             static (bool): If True, text will not be removed when clearing text batches
#         """
#         # Create new id
#         id = self.global_text_counter
#         self.global_text_counter += 1
        
#         # Convert colour to ImGui format (packed 32-bit RGBA)
#         if len(colour) == 3:
#             colour = (*colour, 1.0)
#         imgui_colour = imgui.get_color_u32_rgba(*colour)
              
#         # Project 3D position to screen space
#         screen_pos = self.mouse.project_world_to_screen(world_pos)
#         if screen_pos != (None, None):
#             # Adjust window position
#             screen_pos = np.array(screen_pos) - np.array(self.window_pos) + np.array(align_text)
            
#         # Store text information instead of rendering immediately
#         self.text_batches.append(TextInfo(
#             id=id,
#             text=text, 
#             world_pos=world_pos, 
#             screen_pos=screen_pos,
#             align_text=align_text, 
#             colour=imgui_colour, 
#             font=font, 
#             static=static
#         ))
        
#         return id 
    
#     def remove_texts(self, text_id):
#         # Support both single int and list of ints
#         if isinstance(text_id, int):
#             ids_to_remove = [text_id]
#         elif isinstance(text_id, (list, tuple, set)):
#             ids_to_remove = list(text_id)
#         else:
#             return  # Invalid type

#         # Get indexes of any text with matching ids and delete them
#         indexes = [i for i, text in enumerate(self.text_batches) if text.id in ids_to_remove]
#         for index in sorted(indexes, reverse=True):
#             del self.text_batches[index]
        
                
    
#     def add_axis_labels(self, xlim=[-10, 10], ylim=[-10, 10], increment=1, colour=Colour.WHITE, font=None, static=False):
#         """Add axis labels to the viewport."""
#         text_ids = []
#         # Text in 3d space
#         for i in range(xlim[0], xlim[1]+1, increment):
#             if i != 0:
#                 text_ids.append(self.add_text(f"{i}", (i, 0, 0), colour, (-5, 12), font, static))

#         for i in range(ylim[0], ylim[1]+1, increment):
#             if i != 0:
#                 text_ids.append(self.add_text(f"{i}", (0, i, 0), colour, (-20, -8), font, static))

#         # Draw 0 label
#         text_ids.append(self.add_text(f"{0}", (0, 0, 0), colour, (-20, 12), font, static))
#         return text_ids
            
#     def add_image(self, texture_id=None, world_pos=(0, 0, 0), size=(32, 32), align_image=(0, 0), static=False):
#         """Add an image to be rendered at a 3D world position.
        
#         Args:
#             texture_id (int): OpenGL texture ID
#             world_pos (tuple): 3D world position (x,y,z)
#             size (tuple): Image size (width, height)
#             align_image (tuple): Image alignment offset (x,y)
#             static (bool): If True, image will not be removed when clearing batches
#         """
#         id = self.global_image_counter
#         self.global_image_counter += 1
        
#         # Project 3D position to screen space
#         screen_pos = self.mouse.project_world_to_screen(world_pos)
#         if screen_pos != (None, None):
#             # Adjust window position
#             screen_pos = np.array(screen_pos) - np.array(self.window_pos) + np.array(align_image)
        
#         self.image_batches.append(ImageInfo(
#             id=id,
#             texture_id=texture_id,
#             world_pos=world_pos,
#             screen_pos=screen_pos,
#             size=size,
#             align_image=align_image,
#             static=static
#         ))
#         return id 
    
#     def remove_images(self, image_id):
#         # Support both single int and list of ints
#         if isinstance(image_id, int):
#             ids_to_remove = [image_id]
#         elif isinstance(image_id, (list, tuple, set)):
#             ids_to_remove = list(image_id)
#         else:
#             return  # Invalid type

#         # Get indexes of any images with matching ids and delete them
#         indexes = [i for i, img in enumerate(self.image_batches) if img.id in ids_to_remove]
#         for index in sorted(indexes, reverse=True):
#             del self.image_batches[index]
        
#     def clear(self, clear_static=False):
#         """Clear all non-static text and images."""
#         if clear_static:
#             self.text_batches = []
#             self.image_batches = []
#             self.global_text_counter = 0
#             self.global_image_counter = 0
#             return
#         # Keep static items
#         self.text_batches =  [batch for batch in self.text_batches if batch.static]
#         self.image_batches = [batch for batch in self.image_batches if batch.static]
        
#     def render(self):
#         """
#         Render the text batches using ImGui.
#         Because ImGui is a window system, we need to create an invisible window
#         that covers the entire viewport to render the text. Text is then 
#         rendered to the window in a position relative to the 3D coordinate. 
#         Must be called whilst imgui is rendering.
#         """
#         # Create invisible window that covers the entire viewport
#         viewport = imgui.get_main_viewport()
#         self.window_pos = viewport.pos
        
#         imgui.set_next_window_position(self.window_pos.x, self.window_pos.y)
#         imgui.set_next_window_size(viewport.size.x, viewport.size.y)
#         # Create transparent overlay window
#         imgui.begin("##TextOverlay", 
#                    flags=imgui.WINDOW_NO_DECORATION |
#                          imgui.WINDOW_NO_MOVE |
#                          imgui.WINDOW_NO_SCROLL_WITH_MOUSE |
#                          imgui.WINDOW_NO_SAVED_SETTINGS |
#                          imgui.WINDOW_NO_INPUTS |
#                          imgui.WINDOW_NO_FOCUS_ON_APPEARING |
#                          imgui.WINDOW_NO_BRING_TO_FRONT_ON_FOCUS |
#                          imgui.WINDOW_NO_BACKGROUND)
        
#         # Get draw list for direct rendering
#         draw_list = imgui.get_window_draw_list()
                                        
#         # Render text batches
#         for batch in self.text_batches:
            
#             if batch.font:
#                 self.imgui_manager.push_font(batch.font)
                
#             # Project 3D position to screen space
#             screen_pos = self.mouse.project_world_to_screen(batch.world_pos)
#             if screen_pos != (None, None):
#                 # Adjust window position
#                 screen_pos = np.array(screen_pos) - np.array(self.window_pos) + np.array(batch.align_text)
#                 draw_list.add_text(screen_pos[0], screen_pos[1], batch.colour, batch.text)
                
#             if batch.font:
#                 self.imgui_manager.pop_font()
            
#         # Render image batches
#         for batch in self.image_batches:
#             # Project 3D position to screen space
#             screen_pos = self.mouse.project_world_to_screen(batch.world_pos)
#             if screen_pos != (None, None) and batch.texture_id is not None:
#                 # Adjust window position
#                 screen_pos = np.array(screen_pos) - np.array(self.window_pos) + np.array(batch.align_image)
#                 # Draw image
#                 draw_list.add_image(
#                     batch.texture_id,
#                     (screen_pos[0], screen_pos[1]),
#                     (screen_pos[0] + batch.size[0], screen_pos[1] + batch.size[1])
#                 )
               
#         # End text rendering batch
#         imgui.end()

#     def get_stats(self):
#         """Get statistics about the renderer."""
#         return {
#             "total_text_batches": len(self.text_batches),
#             "total_image_batches": len(self.image_batches),
#             "static_text_items": sum(1 for batch in self.text_batches if batch.static),
#             "static_image_items": sum(1 for batch in self.image_batches if batch.static),
#             "dynamic_text_items": sum(1 for batch in self.text_batches if not batch.static),
#             "dynamic_image_items": sum(1 for batch in self.image_batches if not batch.static)
#         }

