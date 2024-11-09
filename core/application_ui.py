import imgui
from gui.imgui_widgets import ImGuiWidgets


def render_core_ui(camera, renderer, config, timer, imgui_manager):
    """Render UI panels."""
    imgui_manager.push_font('arial_rounded_mt_bold-medium')
    
    sections = [
        ('CAMERA', render_ui_camera, [camera], imgui.TREE_NODE_DEFAULT_OPEN),
        ('MOUSE', render_ui_mouse, [config], imgui.TREE_NODE_DEFAULT_OPEN),
        ('PERFORMANCE', render_ui_performance, [timer.dt], imgui.TREE_NODE_DEFAULT_OPEN),
        ('RENDERER', render_ui_renderer, [renderer, config], imgui.TREE_NODE_DEFAULT_OPEN),
        ('CONFIGURATION', render_ui_config, [config], imgui.TREE_NODE_DEFAULT_OPEN),
    ]
    
    for title, func, args, flags in sections:
        if imgui.collapsing_header(title, flags=flags)[0]:
            imgui_manager.push_font('arial-medium')
            imgui.indent()
            func(*args)
            imgui.unindent()
            imgui_manager.pop_font()
    
    imgui_manager.pop_font()
    

def render_ui_camera(camera):
    """Render camera control panel.
    
    Includes:
    - 2D/3D mode toggle buttons
    - Orthographic/Perspective projection toggle buttons
    - Detailed camera information table
    """
        
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
    
    imgui.same_line(spacing=20)
    
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
    
    if imgui.tree_node('Information'):
        ImGuiWidgets.create_table(
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

def render_ui_renderer(renderer, config):
    """Render renderer settings panel."""
    # Changed to use a single array of RGB values (each from 0-1)
    _, config["background_colour"] = imgui.color_edit3("Background Colour", *config["background_colour"])
    
    # Add ImGui stats window
    if imgui.tree_node('Stats'):
        stats = renderer.batch_renderer.get_stats()
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
