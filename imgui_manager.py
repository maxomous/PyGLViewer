import imgui
from imgui.integrations.glfw import GlfwRenderer
import os

class ImGuiManager:
    def __init__(self, window, enable_docking=True):
        self.window = window
        self.enable_docking = enable_docking
        self.imgui_renderer = None
        self.fonts = {}
        self.init_imgui()

    def init_imgui(self):
        imgui.create_context()
        io = imgui.get_io()
        if self.enable_docking:
            io.config_flags |= imgui.CONFIG_DOCKING_ENABLE
        self.imgui_renderer = GlfwRenderer(self.window, attach_callbacks=True)
        # # Manually attach callbacks to the renderer
        # r = self.imgui_renderer
        # glfw.set_key_callback(r.window, lambda *a: r.queue.put((r.keyboard_callback, a)))
        # # glfw.set_cursor_pos_callback(r.window, lambda *a: r.queue.put((r.mouse_callback, a)))
        # # glfw.set_window_size_callback(r.window, lambda *a: r.queue.put((r.resize_callback, a)))
        # glfw.set_char_callback(r.window, lambda *a: r.queue.put((r.char_callback, a)))
        # glfw.set_scroll_callback(r.window, lambda *a: r.queue.put((r.scroll_callback, a)))

        # Set ImGui style
        style = imgui.get_style()
        style.colors[imgui.COLOR_WINDOW_BACKGROUND] = (0.1, 0.1, 0.1, 0.975)

    def load_font(self, name, path, size):
        if not os.path.exists(path):
            print(f"Font file not found: {path}")
            return

        io = imgui.get_io()
        font = io.fonts.add_font_from_file_ttf(path, size)
        self.fonts[name] = font
        self.imgui_renderer.refresh_font_texture()

    def push_font(self, name):
        if name in self.fonts:
            imgui.push_font(self.fonts[name])
        else:
            print(f"Font not found: {name}")

    def pop_font(self):
        imgui.pop_font()

    def new_frame(self):
        imgui.new_frame()

    def render(self):
        imgui.render()
        self.imgui_renderer.render(imgui.get_draw_data())

    def process_inputs(self):
        self.imgui_renderer.process_inputs()

    def shutdown(self):
        self.imgui_renderer.shutdown()

    def render_dockspace(self):
        if not self.enable_docking:
            return

        viewport = imgui.get_main_viewport()
        padding = 10.0
        toolbar_height = 0  # Set to 0 if no toolbar

        pos_x = viewport.work_pos[0] + padding
        pos_y = viewport.work_pos[1] + padding + (toolbar_height if toolbar_height else 0)
        size_x = viewport.work_size[0] - 2 * padding
        size_y = viewport.work_size[1] - 2 * padding - (toolbar_height if toolbar_height else 0)

        imgui.set_next_window_position(pos_x, pos_y)
        imgui.set_next_window_size(size_x, size_y)
        imgui.set_next_window_viewport(viewport.id)

        window_flags = (
            imgui.WINDOW_NO_BACKGROUND | 
            imgui.WINDOW_NO_DOCKING | 
            imgui.WINDOW_NO_TITLE_BAR | 
            imgui.WINDOW_NO_COLLAPSE | 
            imgui.WINDOW_NO_RESIZE | 
            imgui.WINDOW_NO_MOVE | 
            imgui.WINDOW_NO_BRING_TO_FRONT_ON_FOCUS | 
            imgui.WINDOW_NO_NAV_FOCUS
        )

        imgui.push_style_var(imgui.STYLE_WINDOW_PADDING, (0.0, 0.0))
        imgui.begin("DockSpace", None, window_flags)
        imgui.pop_style_var()

        dockspace_flags = (
            imgui.DOCKNODE_PASSTHRU_CENTRAL_NODE |
            imgui.DOCKNODE_NO_DOCKING_IN_CENTRAL_NODE
        )
        imgui.dockspace(imgui.get_id("DockSpace"), (0.0, 0.0), dockspace_flags)

    def end_dockspace(self):
        if self.enable_docking:
            imgui.end()
