from collections import namedtuple
import numpy as np
import imgui
from typing import Callable
from OpenGL.GL import GL_POINTS, GL_LINES
from pyglviewer.renderer.renderer import Renderer
from pyglviewer.renderer.objects import Object
from pyglviewer.renderer.shapes import Shapes
from pyglviewer.utils.colour import Colour

# TODO: Objects 


class SelectionSettings:
    def __init__(self, show_cursor_point=True, select_objects=True, drag_objects=True, select_callback: Callable = None, drag_callback: Callable = None):
        self.show_cursor_point = show_cursor_point
        self.select_objects = select_objects
        self.drag_objects = drag_objects
        # Callbacks
        self.select_callback = select_callback
        self.drag_callback = drag_callback

class ObjectSelection:
    """Handles object selection based on mouse input."""
    def __init__(self, camera, renderer: Renderer, mouse, settings: SelectionSettings):
        self.camera = camera
        self.renderer = renderer
        self.mouse = mouse
        self.settings = settings
        self.target_edge_length = 0.02 
        self.min_selection_distance = 2.0        
        self.selected_objects = []
        
    def process_input(self):
        # Always update selection targets
        self.process_selection_targets()
        
        if imgui.get_io().want_capture_mouse:
            return
        # Update cursor world position
        self.renderer.cursor_pos = self.mouse.project_screen_to_world(self.mouse.position)
        
        self.process_select()
        self.process_drag()
        self.process_release()
        self.process_cursor_point()
    
    def process_select(self):
        if not self.settings.select_objects or not self.camera.is_2d_mode:
            return
        
        # Handle object selection on left click
        if self.mouse.left_click:  # Left mouse click
            # Clear previous selection if not holding shift
            if not self.mouse.shift_down:
                for buffer in [self.renderer.static_buffer, self.renderer.dynamic_buffer]:
                    for obj in buffer.objects.values():
                        obj.deselect()
                for obj in self.renderer.imgui_render_buffer.text_objects.values():
                    obj.deselect()
                for obj in self.renderer.imgui_render_buffer.image_objects.values():
                    obj.deselect()
                    
            # Get Object under cursor
            closest_obj, name, buffer_type = self.get_object_under_cursor()       
            # Select the picked object
            if closest_obj:
                closest_obj.toggle_select()
                # Call callback with object
                if self.settings.select_callback:
                    self.settings.select_callback(closest_obj)
        
            # Get selected objects to set the start positions
            self.selected_objects = self.renderer.get_selected_objects() 
            # Set initial object positions
            if not hasattr(self, 'object_start_pos') or self.object_start_pos is None:
                self.object_start_pos = []
                for obj, name, buffer_type in self.selected_objects:
                    has_no_shapes = ((buffer_type == 'static') or (buffer_type == 'dynamic')) and (len(obj._shape_data) == 0)
                    if has_no_shapes or (buffer_type == 'image') or (buffer_type == 'text'):
                        continue
                    self.object_start_pos.append(obj.get_translate().copy())
                    
    def process_drag(self):
        '''Drag selected objects with left mouse button pressed.'''
        if not self.settings.drag_objects:
            return
        if self.mouse.is_panning or self.mouse.is_rotating:
            return
        
        # Drag selected objects
        if self.mouse.left_down:
            # Get mouse delta & convert to world space
            mouse_delta_x = self.mouse.screen_to_world(self.mouse.click_position_delta[0])
            mouse_delta_y = self.mouse.screen_to_world(-self.mouse.click_position_delta[1])
            mouse_delta = np.array([mouse_delta_x, mouse_delta_y, 0.0])
            
            if not hasattr(self, 'object_start_pos') or self.object_start_pos is None or self.object_start_pos == []:
                return
            
            for i, (obj, name, buffer) in enumerate(self.selected_objects):
                if (len(obj._shape_data) == 0) or (buffer == 'text') or (buffer == 'image'):
                    continue
                # Set new object transform
                translate = self.object_start_pos[i] + mouse_delta
                obj.set_translate(translate)
                # Call callback with object
                if self.settings.drag_callback:
                    self.settings.drag_callback(obj)
                
    def process_release(self):
        '''Release left mouse button.'''
        if imgui.is_mouse_released(imgui.MOUSE_BUTTON_LEFT):
            self.object_start_pos = None
            
    def process_cursor_point(self):
        # Draw cursor point
        if hasattr(self.renderer, 'cursor_pos'):
            self.renderer.update_object('cursor_point', static=False, selectable=False, point_size=5,
                shape=Shapes.point((self.renderer.cursor_pos[0], self.renderer.cursor_pos[1], 0), colour=Colour.WHITE)
            )
        
    def process_selection_targets(self):
        # Draw target on selected objects
        targets = Shapes.blank(GL_LINES)
        # Get object under cursor
        for obj, name, buffer in self.renderer.get_selected_objects():
            has_no_shapes = ((buffer == 'static') or (buffer == 'dynamic')) and (len(obj._shape_data) == 0)
            if has_no_shapes:
                continue
            
            # Midpoint
            midpoint = np.array(obj.get_midpoint())
            # convert to 3d (world) if 2d (screen)
            if midpoint.shape[0] == 2:
                midpoint = self.mouse.project_screen_to_world(midpoint)
                midpoint[2] = 0

            # Size
            size = np.array(obj.get_bounds()['max']) - np.array(obj.get_bounds()['min'])
            # add z=0 if only x,y
            if size.shape[0] == 2:
                size = np.append(size, 0.0)
                size = self.mouse.screen_to_world(size)
            # Get offset for target size
            offset = self.mouse.screen_to_world(10)
            
            if obj.is_point():
                point_size = obj._point_size
                offset += self.mouse.screen_to_world(point_size)
            
            edge_length = self.camera.distance * self.target_edge_length
            # print(f'Midpoint: {midpoint}    size: {size + np.array([offset, offset, offset])}')
            targets += Shapes.target(midpoint, size + np.array([offset, offset, offset]), edge_length, Colour.WHITE) 

        self.renderer.update_object('selection_targets', static=False, selectable=False, shape=targets)
        
    # TODO: Bounds and midpoints etc for Texts and Images are stored in screen space, whereas shape objects are stored as world, this is messy 
    # TODO: Create a second variable for _world & _screen 
        
    def get_object_under_cursor(self):
        """Determine which object is under the cursor"""
        scale_factor = self.mouse.screen_to_world(1)
        
        # Test intersection with objects
        valid_hits = []
        cursor_world = self.renderer.cursor_pos
        cursor_screen = self.mouse.position
        # Intersect cursor with static, dynamic, text & image objects
        valid_hits = self.intersect_objects(valid_hits, 'static', self.renderer.static_buffer.objects, cursor_world, scale_factor)
        valid_hits = self.intersect_objects(valid_hits, 'dynamic', self.renderer.dynamic_buffer.objects, cursor_world, scale_factor)
        
        valid_hits = self.intersect_objects(valid_hits, 'text', self.renderer.imgui_render_buffer.text_objects, cursor_screen, scale_factor)
        valid_hits = self.intersect_objects(valid_hits, 'image', self.renderer.imgui_render_buffer.image_objects, cursor_screen, scale_factor)

        # TODO: I THINK DISTANCE IS GOING TO BE WRONG AS ONE IS WORLD AND ONE IS SCREEN

        if not valid_hits:
            return (None, None, None)
            
        # Sort by distance and get closest
        valid_hits.sort(key=lambda x: x[0])
        distance, name, buffer_type = valid_hits[0]
        
        if buffer_type == 'static':
            buffer = self.renderer.static_buffer.objects
        elif buffer_type == 'dynamic':
            buffer = self.renderer.dynamic_buffer.objects
        elif buffer_type == 'text':
            buffer = self.renderer.imgui_render_buffer.text_objects
        elif buffer_type == 'image':
            buffer = self.renderer.imgui_render_buffer.image_objects
            
        return (buffer[name], name, buffer_type)
        
    def intersect_objects(self, valid_hits, buffer_type, objects, cursor, scale_factor):
        # Determine the 
        min_distance = scale_factor * self.min_selection_distance        
        for name, obj in objects.items():
            # If object is a point, add the size of the point to selection distance
            selection_distance = min_distance if not obj.is_point() else min_distance + scale_factor * obj._point_size / 2
            hit, distance = self.intersect_cursor(obj, cursor, selection_distance=selection_distance)
            if hit and distance > 0 and distance < float('inf'):
                valid_hits.append((distance, name, buffer_type))
                
        return valid_hits
    
    @staticmethod
    def intersect_cursor(obj, cursor_pos, selection_distance):
        """Intersect ray with object bounds.
        
        Parameters
        ----------
        obj : Object or TextObject or ImageObject
            Object to test intersection with
        cursor_pos : np.ndarray
            Cursor position in world space
        min_distance : float
            Minimum distance to intersection in px
        
        Returns
        -------
        tuple
            (bool, float) - (intersection found, distance to intersection)
        """
        if not obj._selectable:
            return False, float('inf')

        bounds = obj.get_bounds()
        if bounds is None:
            return False, float('inf')

        dim = len(bounds['min'])  # 2 or 3
        offset = np.full(dim, selection_distance)

        # Expand bounds by offset
        bounds['min'] = bounds['min'] - offset
        bounds['max'] = bounds['max'] + offset

        cursor_pos = np.round(cursor_pos, 3)

        if cursor_pos[0] >= bounds['min'][0] and cursor_pos[0] <= bounds['max'][0] and \
           cursor_pos[1] >= bounds['min'][1] and cursor_pos[1] <= bounds['max'][1]:
            midpoint = obj.get_midpoint()
            distance = np.linalg.norm(cursor_pos[:2] - midpoint[:2])
            return True, distance
        else:
            return False, float('inf')
        