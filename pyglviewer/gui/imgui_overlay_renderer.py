import imgui
import numpy as np
from dataclasses import dataclass
from typing import Tuple, Optional
from pyglviewer.utils.colour import Colour
# TODO: Using ImGui for text rendering means text appears on top of objects, ideally
#       we should implement our own text rendering so as to account for depth. It 
#       may also be faster.

@dataclass
class TextInfo:
    """Store information about text to be rendered."""
    text: str
    world_pos: Tuple[float, float, float]
    align_text: Tuple[float, float]
    colour: int  # ImGui packed colour
    font: str = None
    static: bool = False

@dataclass
class ImageInfo:
    """Store information about an image to be rendered."""
    texture_id: int  # OpenGL texture ID
    world_pos: Tuple[float, float, float]
    size: Tuple[float, float]  # Width, height
    align_image: Tuple[float, float] = (0, 0)
    static: bool = False

class ImguiOverlayRenderer:
    """Batch renderer for drawing text and images at 3D world positions using ImGui."""
    
    def __init__(self, mouse, imgui_manager):
        self.window_pos = (0, 0)
        self.mouse = mouse
        self.imgui_manager = imgui_manager
        self.text_batches = []  # Store text information for batch rendering
        self.image_batches = []  # Store image information for batch rendering
    
    def add_text(self, text, world_pos, colour, align_text=(0, 0), font=None, static=False):
        """Add text to be rendered at a 3D world position. 
        Stores text data to later (in that frame) be rendered in imgui window.
        Can be called any time in frame,
        
        Args:
            text (str): Text to display
            world_pos (tuple): 3D world position (x,y,z)
            colour (tuple): RGBA colour values (0-1)
            align_text (tuple): Text alignment (x,y)
            font (imgui.Font, optional): ImGui font to use. Uses default if None.
            static (bool): If True, text will not be removed when clearing text batches
        """
        # Convert colour to ImGui format (packed 32-bit RGBA)
        if len(colour) == 3:
            colour = (*colour, 1.0)
        imgui_colour = imgui.get_color_u32_rgba(*colour)
              
        # Store text information instead of rendering immediately
        self.text_batches.append(TextInfo(text=text, world_pos=world_pos, align_text=align_text, colour=imgui_colour, font=font, static=static))
    
    
    def add_axis_labels(self, xlim=[-10, 10], ylim=[-10, 10], increment=1, colour=Colour.WHITE, font=None, static=False):
        """Add axis labels to the viewport."""
        # Text in 3d space
        for i in range(xlim[0], xlim[1]+1, increment):
            if i != 0:
                self.add_text(f"{i}", (i, 0, 0), colour, (-5, 12), font, static)

        for i in range(ylim[0], ylim[1]+1, increment):
            if i != 0:
                self.add_text(f"{i}", (0, i, 0), colour, (-20, -8), font, static)

        # Draw 0 label
        self.add_text(f"{0}", (0, 0, 0), colour, (-20, 12), font, static)
            
    def add_image(self, texture_id, world_pos, size, align_image=(0, 0), static=False):
        """Add an image to be rendered at a 3D world position.
        
        Args:
            texture_id (int): OpenGL texture ID
            world_pos (tuple): 3D world position (x,y,z)
            size (tuple): Image size (width, height)
            align_image (tuple): Image alignment offset (x,y)
            static (bool): If True, image will not be removed when clearing batches
        """
        self.image_batches.append(ImageInfo(
            texture_id=texture_id,
            world_pos=world_pos,
            size=size,
            align_image=align_image,
            static=static
        ))
    
    def clear(self, clear_static=False):
        """Clear all non-static text and images."""
        # Keep only static items
        self.text_batches = [] if clear_static else [batch for batch in self.text_batches if batch.static]
        self.image_batches = [] if clear_static else [batch for batch in self.image_batches if batch.static]
        
    def render(self):
        """
        Render the text batches using ImGui.
        Because ImGui is a window system, we need to create an invisible window
        that covers the entire viewport to render the text. Text is then 
        rendered to the window in a position relative to the 3D coordinate. 
        Must be called whilst imgui is rendering.
        """
        # Create invisible window that covers the entire viewport
        viewport = imgui.get_main_viewport()
        self.window_pos = viewport.pos
        
        imgui.set_next_window_position(self.window_pos.x, self.window_pos.y)
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
        
        # Get draw list for direct rendering
        draw_list = imgui.get_window_draw_list()
            
        # Render text batches
        for batch in self.text_batches:
            
            if batch.font:
                self.imgui_manager.push_font(batch.font)
                
            # Project 3D position to screen space
            screen_pos = self.mouse.project_world_to_screen(batch.world_pos)
            if screen_pos != (None, None):
                # Adjust window position
                screen_pos = np.array(screen_pos) - np.array(self.window_pos) + np.array(batch.align_text)
                draw_list.add_text(screen_pos[0], screen_pos[1], batch.colour, batch.text)
                
            if batch.font:
                self.imgui_manager.pop_font()
                
        # Render image batches
        for batch in self.image_batches:
            # Project 3D position to screen space
            screen_pos = self.mouse.project_world_to_screen(batch.world_pos)
            if screen_pos != (None, None):
                # Adjust window position
                screen_pos = np.array(screen_pos) - np.array(self.window_pos) + np.array(batch.align_image)
                # Draw image
                draw_list.add_image(
                    batch.texture_id,
                    (screen_pos[0], screen_pos[1]),
                    (screen_pos[0] + batch.size[0], screen_pos[1] + batch.size[1])
                )
        
        # End text rendering batch
        imgui.end()

    def get_stats(self):
        """Get statistics about the renderer."""
        return {
            "total_text_batches": len(self.text_batches),
            "total_image_batches": len(self.image_batches),
            "static_text_items": sum(1 for batch in self.text_batches if batch.static),
            "static_image_items": sum(1 for batch in self.image_batches if batch.static),
            "dynamic_text_items": sum(1 for batch in self.text_batches if not batch.static),
            "dynamic_image_items": sum(1 for batch in self.image_batches if not batch.static)
        }
