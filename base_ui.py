import imgui
from imgui_widgets import ImGuiWidgets

def render_camera_section(camera):
    if imgui.collapsing_header('Camera', flags=imgui.TREE_NODE_DEFAULT_OPEN)[0]:
        imgui.indent()

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

        imgui.unindent()

def render_mouse_section(p):
    if imgui.collapsing_header('Mouse', flags=imgui.TREE_NODE_DEFAULT_OPEN)[0]:
        imgui.indent()
            
        if imgui.tree_node('Sensitivity'):
            text_width = 120
            slider_width = imgui.get_content_region_available()[0] - text_width
            
            imgui.push_item_width(slider_width)
            _, p["base_pan_sensitivity"] = imgui.slider_float('Pan Sensitivity', p["base_pan_sensitivity"], 0.001, 0.1, '%.4f')
            _, p["base_scroll_sensitivity"] = imgui.slider_float('Scroll Sensitivity', p["base_scroll_sensitivity"], 0.1, 2.0, '%.2f')
            _, p["rotate_sensitivity"] = imgui.slider_float('Rotate Sensitivity', p["rotate_sensitivity"], 0.01, 0.5, '%.2f')
            imgui.pop_item_width()
            imgui.tree_pop()
        
        if imgui.tree_node('Invert'):
            invert_yaw_pitch = p["invert_yaw_pitch"]
            _, yaw = imgui.checkbox('Invert Rotate X', invert_yaw_pitch[0] > 0)
            _, pitch = imgui.checkbox('Invert Rotate Y', invert_yaw_pitch[1] > 0)
            p["invert_yaw_pitch"] = [1 if x else -1 for x in (yaw, pitch)]
            
            invert_pan = p["invert_pan"]
            _, pan_x = imgui.checkbox('Invert Pan X', invert_pan[0] > 0)
            _, pan_y = imgui.checkbox('Invert Pan Y', invert_pan[1] > 0)
            p["invert_pan"] = [1 if x else -1 for x in (pan_x, pan_y)]
            
            _, scroll = imgui.checkbox('Invert Scroll', p["invert_scroll"] > 0)
            p["invert_scroll"] = 1 if scroll else -1
            imgui.tree_pop()
        
        imgui.unindent()

def render_performance_section(dt):
    if imgui.collapsing_header('Performance', flags=imgui.TREE_NODE_DEFAULT_OPEN)[0]:
        imgui.indent()
        fps = 1.0 / dt if dt > 0 else 0.0
        imgui.text(f'FPS: {fps:.1f}')
        imgui.unindent()

def render_parameters_section(p):
    if imgui.collapsing_header('Parameters', flags=imgui.TREE_NODE_DEFAULT_OPEN)[0]:
        imgui.indent()
        
        imgui.push_style_var(imgui.STYLE_FRAME_PADDING, (6, 6))
        
        if imgui.button("Reset to Defaults"):
            p.reset_to_defaults()
        
        imgui.same_line()
        if imgui.button("Save"):
            p.save()
        
        imgui.same_line()
        if imgui.button("Load"):
            p.load()
        
        imgui.pop_style_var()
        
        imgui.unindent()
