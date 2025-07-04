import imgui
from pyglviewer.gui.imgui_widgets import imgui

def render_core_ui(camera, renderer, text_renderer, config, timer, imgui_manager):
    """Render UI panels."""
    imgui_manager.push_font('arial_rounded_mt_bold-medium')
    
    sections = [
        ('SELECTION', render_ui_selection_widget, [renderer]),
        ('CAMERA', render_ui_camera, [camera]),
        ('MOUSE', render_ui_mouse, [config]),
        ('PERFORMANCE', render_ui_performance, [timer.dt]),
        ('RENDERER', render_ui_renderer, [config, renderer, text_renderer]),
        ('CONFIGURATION', render_ui_config, [config]),
    ]
    
    for title, func, args in sections:
        if imgui.collapsing_header(title, flags=imgui.TREE_NODE_DEFAULT_OPEN)[0]:
            imgui_manager.push_font('arial-medium')
            imgui.indent()
            func(*args)
            imgui.unindent()
            imgui_manager.pop_font()
    
    imgui_manager.pop_font()
    

def render_ui_selection_widget(renderer):
    """Render widget showing information about selected object."""
    selected_object = renderer.get_selected_object()

    if not selected_object:
        imgui.text("No object selected")
    else:
        for obj in selected_object:
            if imgui.tree_node(f"Object {obj.id}"):
                for i, render_obj in enumerate(obj._render_objects):
                    
                    if imgui.tree_node(f"Render Object {i}"):
                        # Display object properties
                        imgui.text(f"Draw Type: {render_obj.draw_type}")
                            
                        # Display transform info
                        if imgui.tree_node("Transform"):
                            # Extract position from model matrix (last column)
                            position = render_obj.model_matrix[3, :3]
                            # imgui.text(f"Position: {position[0]:.2f}, {position[1]:.2f}, {position[2]:.2f}")
                            
                            # Add transform controls
                            changed, new_pos = imgui.drag_float3("Position", *position, 0.1)
                            if changed:
                                # Update object position
                                render_obj.set_translate(translate=new_pos)
                                
                            # Display vertex count
                            if render_obj._vertex_data is not None:
                                vertex_count = len(render_obj._vertex_data) // 3  # Assuming 3 components per vertex
                                imgui.text(f"Vertex Count: {vertex_count}")
                            
                            
                            imgui.tree_pop()
                        
                        # Display bounds info
                        if imgui.tree_node("Bounds"):
                            bounds = render_obj.get_bounds()
                            if bounds:
                                imgui.text(f"Min: {bounds['min'][0]:.2f}, {bounds['min'][1]:.2f}, {bounds['min'][2]:.2f}")
                                imgui.text(f"Max: {bounds['max'][0]:.2f}, {bounds['max'][1]:.2f}, {bounds['max'][2]:.2f}")
                            imgui.tree_pop()
                    
                imgui.tree_pop()
        
def render_ui_camera_2d_3d_mode(camera):
    """Render camera 2D/3D mode settings panel."""
    # Dimension Mode buttons
    is_2d_mode = camera.is_2d_mode
        
    # 2D button
    if is_2d_mode:
        imgui.push_style_color(imgui.COLOR_BUTTON, 0.2, 0.6, 0.2, 1.0)  # Green when active
    else:
        imgui.push_style_color(imgui.COLOR_BUTTON, 0.4, 0.4, 0.4, 1.0)  # Gray when inactive
    if imgui.button("2D"):
        if not is_2d_mode:
            camera.toggle_2d_mode()
            camera.update_projection()
    imgui.pop_style_color()
    
    imgui.same_line()
    
    # 3D button
    if not is_2d_mode:
        imgui.push_style_color(imgui.COLOR_BUTTON, 0.2, 0.6, 0.2, 1.0)  # Green when active
    else:
        imgui.push_style_color(imgui.COLOR_BUTTON, 0.4, 0.4, 0.4, 1.0)  # Gray when inactive
    if imgui.button("3D"):
        if is_2d_mode:
            camera.toggle_2d_mode()
            camera.update_projection()
    imgui.pop_style_color()
        
def render_ui_camera_projection(camera):
    """Render camera Orthographic/Perspective projection settings panel."""
    # Projection Mode buttons
    is_orthographic = camera.is_orthographic
    
    # Orthographic button
    if is_orthographic:
        imgui.push_style_color(imgui.COLOR_BUTTON, 0.2, 0.6, 0.2, 1.0)  # Green when active
    else:
        imgui.push_style_color(imgui.COLOR_BUTTON, 0.4, 0.4, 0.4, 1.0)  # Gray when inactive
    if imgui.button("Orthographic"):
        if not is_orthographic:
            camera.toggle_projection()
            camera.update_projection()
    imgui.pop_style_color()
    
    imgui.same_line()
    
    # Perspective button
    if not is_orthographic:
        imgui.push_style_color(imgui.COLOR_BUTTON, 0.2, 0.6, 0.2, 1.0)  # Green when active
    else:
        imgui.push_style_color(imgui.COLOR_BUTTON, 0.4, 0.4, 0.4, 1.0)  # Gray when inactive
    if imgui.button("Perspective"):
        if is_orthographic: 
            camera.toggle_projection()
            camera.update_projection()
    imgui.pop_style_color()
        
def render_ui_camera(camera):
    """Render camera control panel.
    
    Includes:
    - 2D/3D mode toggle buttons
    - Orthographic/Perspective projection toggle buttons
    - Detailed camera information table
    """
    # 2D/3D mode toggle buttons
    render_ui_camera_2d_3d_mode(camera)
    
    imgui.same_line(spacing=20)
    
    # Orthographic/Perspective projection toggle buttons
    render_ui_camera_projection(camera)
    
    if imgui.tree_node('Information'):
        imgui.create_table(
            'camera_info',
            ['', ''],
            [
                ('Position',    camera.position.round(2)),
                ('Target',      camera.target.round(2)),
                ('Yaw',         f'{camera.yaw:.2f}°'),
                ('Pitch',       f'{camera.pitch:.2f}°'),
                ('Distance',    f'{camera.distance:.2f}'),
                ('Front',       camera.front.round(2)),
                ('Up',          camera.up.round(2)),
                ('Right',       camera.right.round(2)),
                ('World Up',    camera.world_up.round(2))
            ]
        )
        imgui.tree_pop()

def render_ui_mouse(config):
    """Render mouse settings panel."""
        
    if imgui.tree_node('Sensitivity'):
        text_width = 120
        slider_width = imgui.get_content_region_available()[0] - text_width
        
        imgui.push_item_width(slider_width)
        _, config["mouse.base_pan_sensitivity"] = imgui.slider_float('Pan Sensitivity', config["mouse.base_pan_sensitivity"], 0.001, 0.1, '%.4f')
        _, config["mouse.base_scroll_sensitivity"] = imgui.slider_float('Scroll Sensitivity', config["mouse.base_scroll_sensitivity"], 0.1, 2.0, '%.2f')
        _, config["mouse.rotate_sensitivity"] = imgui.slider_float('Rotate Sensitivity', config["mouse.rotate_sensitivity"], 0.01, 0.5, '%.2f')
        imgui.pop_item_width()
        imgui.tree_pop()
    
    if imgui.tree_node('Invert'):
        invert_yaw_pitch = config["mouse.invert_yaw_pitch"]
        _, yaw = imgui.checkbox('Invert Rotate X', invert_yaw_pitch[0] > 0)
        _, pitch = imgui.checkbox('Invert Rotate Y', invert_yaw_pitch[1] > 0)
        config["mouse.invert_yaw_pitch"] = [1 if x else -1 for x in (yaw, pitch)]
        
        invert_pan = config["mouse.invert_pan"]
        _, pan_x = imgui.checkbox('Invert Pan X', invert_pan[0] > 0)
        _, pan_y = imgui.checkbox('Invert Pan Y', invert_pan[1] > 0)
        config["mouse.invert_pan"] = [1 if x else -1 for x in (pan_x, pan_y)]
        
        _, scroll = imgui.checkbox('Invert Scroll', config["mouse.invert_scroll"] > 0)
        config["mouse.invert_scroll"] = 1 if scroll else -1
        imgui.tree_pop()
        
def render_ui_performance(dt):
    """Render performance metrics panel.
    
    Args:
        dt (float): Delta time between frames
    """
    fps = 1.0 / dt if dt > 0 else 0.0
    imgui.text(f'FPS: {fps:.1f}')

def render_ui_renderer(config, renderer, text_renderer):
    """Render renderer settings panel."""
    # Changed to use a single array of RGB values (each from 0-1)
    _, config["background_colour"] = imgui.color_edit3("Background Colour", *config["background_colour"])
   
    # Add ImGui stats window
    def render_batch_renderer_stats(renderer_name, renderer):
        if imgui.tree_node(renderer_name):
            stats = renderer.get_stats()
            for key, value in stats.items():
                if isinstance(value, dict):
                    for k, v in value.items():
                        if isinstance(v, dict):
                            for k2, v2 in v.items():
                                imgui.text(f"{key}.{k}.{k2}: {v2}")
                        else:
                            imgui.text(f"{key}.{k}: {v}")
                else:
                    imgui.text(f"{key}: {value}")
            imgui.tree_pop()
    
    def render_batch_renderer_stats(renderer_name, renderer):
        if imgui.tree_node(renderer_name):
            stats = renderer.get_stats()
            for key, value in stats.items():
                imgui.text(f"{key.replace('_', ' ').title()}: {value}")
            imgui.tree_pop()    
    
    render_batch_renderer_stats('Static Buffer Info', renderer.batch_renderer.static_buffer)
    render_batch_renderer_stats('Dynamic Buffer Info', renderer.batch_renderer.dynamic_buffer)
    render_batch_renderer_stats('Text Buffer Info', text_renderer)


def render_ui_config(config):
    """Render configuration panel to save/load configuration."""
    imgui.push_style_var(imgui.STYLE_FRAME_PADDING, (6, 6))
    
    if imgui.button("Reset to Defaults"):
        config.reset_to_defaults()
    
    imgui.same_line()
    if imgui.button("Save"):
        config.save()
    
    imgui.same_line()
    if imgui.button("Load"):
        config.load()
    
    imgui.pop_style_var()

