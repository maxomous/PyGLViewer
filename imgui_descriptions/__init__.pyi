from typing import Any
from imgui.core import *  # noqa
from imgui import core
from imgui.extra import *  # noqa
from imgui import extra
from imgui import _compat
from imgui import internal

VERTEX_BUFFER_POS_OFFSET = extra.vertex_buffer_vertex_pos_offset()
VERTEX_BUFFER_UV_OFFSET = extra.vertex_buffer_vertex_uv_offset()
VERTEX_BUFFER_COL_OFFSET = extra.vertex_buffer_vertex_col_offset()

VERTEX_SIZE = extra.vertex_buffer_vertex_size()

INDEX_SIZE = extra.index_buffer_index_size()

# ==== Condition constants (redefines for autodoc)
#: No condition (always set the variable), same as _Always
NONE = core.NONE
#: No condition (always set the variable)
ALWAYS = core.ALWAYS
#: Set the variable once per runtime session (only the first call will succeed)
ONCE = core.ONCE
#: Set the variable if the object/window has no persistently saved data (no entry in .ini file)
FIRST_USE_EVER = core.FIRST_USE_EVER
#: Set the variable if the object/window is appearing after being hidden/inactive (or the first time)
APPEARING = core.APPEARING


# === Key map constants (redefines for autodoc)
#: for tabbing through fields
KEY_TAB = core.KEY_TAB
#: for text edit
KEY_LEFT_ARROW = core.KEY_LEFT_ARROW
#: for text edit
KEY_RIGHT_ARROW = core.KEY_RIGHT_ARROW
#: for text edit
KEY_UP_ARROW = core.KEY_UP_ARROW
#: for text edit
KEY_DOWN_ARROW = core.KEY_DOWN_ARROW
KEY_PAGE_UP = core.KEY_PAGE_UP
KEY_PAGE_DOWN = core.KEY_PAGE_DOWN
#: for text edit
KEY_HOME = core.KEY_HOME
#: for text edit
KEY_END = core.KEY_END
#: for text edit
KEY_INSERT = core.KEY_INSERT
#: for text edit
KEY_DELETE = core.KEY_DELETE
#: for text edit
KEY_BACKSPACE = core.KEY_BACKSPACE
#: for text edit
KEY_SPACE = core.KEY_SPACE
#: for text edit
KEY_ENTER = core.KEY_ENTER
#: for text edit
KEY_ESCAPE = core.KEY_ESCAPE
#: 
KEY_PAD_ENTER = core.KEY_PAD_ENTER
#: for text edit CTRL+A: select all
KEY_A = core.KEY_A
#: for text edit CTRL+C: copy
KEY_C = core.KEY_C
#: for text edit CTRL+V: paste
KEY_V = core.KEY_V
#: for text edit CTRL+X: cut
KEY_X = core.KEY_X
#: for text edit CTRL+Y: redo
KEY_Y = core.KEY_Y
#: for text edit CTRL+Z: undo
KEY_Z = core.KEY_Z

# === Nav Input (redefines for autodoc)
#: activate / open / toggle / tweak value        e.g. Cross  (PS4), A (Xbox), A (Switch), Space (Keyboard)
NAV_INPUT_ACTIVATE = core.NAV_INPUT_ACTIVATE
#: cancel / close / exit                         e.g. Circle (PS4), B (Xbox), B (Switch), Escape (Keyboard)
NAV_INPUT_CANCEL = core.NAV_INPUT_CANCEL
#: text input / on-screen keyboard               e.g. Triang.(PS4), Y (Xbox), X (Switch), Return (Keyboard)
NAV_INPUT_INPUT = core.NAV_INPUT_INPUT
#: tap: toggle menu / hold: focus, move, resize  e.g. Square (PS4), X (Xbox), Y (Switch), Alt (Keyboard)
NAV_INPUT_MENU = core.NAV_INPUT_MENU
#: move / tweak / resize window (w/ PadMenu)     e.g. D-pad Left/Right/Up/Down (Gamepads), Arrow keys (Keyboard)
NAV_INPUT_DPAD_LEFT = core.NAV_INPUT_DPAD_LEFT
#:
NAV_INPUT_DPAD_RIGHT = core.NAV_INPUT_DPAD_RIGHT
#:
NAV_INPUT_DPAD_UP = core.NAV_INPUT_DPAD_UP
#:
NAV_INPUT_DPAD_DOWN = core.NAV_INPUT_DPAD_DOWN
#: scroll / move window (w/ PadMenu)             e.g. Left Analog Stick Left/Right/Up/Down
NAV_INPUT_L_STICK_LEFT = core.NAV_INPUT_L_STICK_LEFT
#:
NAV_INPUT_L_STICK_RIGHT = core.NAV_INPUT_L_STICK_RIGHT 
#:
NAV_INPUT_L_STICK_UP = core.NAV_INPUT_L_STICK_UP
#:
NAV_INPUT_L_STICK_DOWN = core.NAV_INPUT_L_STICK_DOWN
#: next window (w/ PadMenu)                      e.g. L1 or L2 (PS4), LB or LT (Xbox), L or ZL (Switch)
NAV_INPUT_FOCUS_PREV = core.NAV_INPUT_FOCUS_PREV
#: prev window (w/ PadMenu)                      e.g. R1 or R2 (PS4), RB or RT (Xbox), R or ZL (Switch)
NAV_INPUT_FOCUS_NEXT = core.NAV_INPUT_FOCUS_NEXT
#: slower tweaks                                 e.g. L1 or L2 (PS4), LB or LT (Xbox), L or ZL (Switch)
NAV_INPUT_TWEAK_SLOW = core.NAV_INPUT_TWEAK_SLOW
#: faster tweaks                                 e.g. R1 or R2 (PS4), RB or RT (Xbox), R or ZL (Switch)
NAV_INPUT_TWEAK_FAST    = core.NAV_INPUT_TWEAK_FAST


# === Key Mode Flags (redefines for autodoc)
KEY_MOD_NONE = core.KEY_MOD_NONE
KEY_MOD_CTRL = core.KEY_MOD_CTRL
KEY_MOD_SHIFT = core.KEY_MOD_SHIFT
KEY_MOD_ALT = core.KEY_MOD_ALT
KEY_MOD_SUPER = core.KEY_MOD_SUPER

# === Style var constants (redefines for autodoc)
#: associated type: ``float``.
STYLE_ALPHA = core.STYLE_ALPHA
#: associated type: ``Vec2``.
STYLE_WINDOW_PADDING = core.STYLE_WINDOW_PADDING
#: associated type: ``float``.
STYLE_WINDOW_ROUNDING = core.STYLE_WINDOW_ROUNDING
#: associated type: ``float``.
STYLE_WINDOW_BORDERSIZE = core.STYLE_WINDOW_BORDERSIZE
#: associated type: ``Vec2``.
STYLE_WINDOW_MIN_SIZE = core.STYLE_WINDOW_MIN_SIZE
#: associated type: ``Vec2``.
STYLE_WINDOW_TITLE_ALIGN = core.STYLE_WINDOW_TITLE_ALIGN
#: associated type: ``float``.
STYLE_CHILD_ROUNDING = core.STYLE_CHILD_ROUNDING
#: associated type: ``float``.
STYLE_CHILD_BORDERSIZE = core.STYLE_CHILD_BORDERSIZE
#: associated type: ``float``.
STYLE_POPUP_ROUNDING = core.STYLE_POPUP_ROUNDING
#: associated type: ``float``.
STYLE_POPUP_BORDERSIZE = core.STYLE_POPUP_BORDERSIZE
#: associated type: ``Vec2``.
STYLE_FRAME_PADDING = core.STYLE_FRAME_PADDING
#: associated type: ``float``.
STYLE_FRAME_ROUNDING = core.STYLE_FRAME_ROUNDING
#: associated type: ``float``.
STYLE_FRAME_BORDERSIZE = core.STYLE_FRAME_BORDERSIZE
#: associated type: ``Vec2``.
STYLE_ITEM_SPACING = core.STYLE_ITEM_SPACING
#: associated type: ``Vec2``.
STYLE_ITEM_INNER_SPACING = core.STYLE_ITEM_INNER_SPACING
#: associated type: ``float``.
STYLE_INDENT_SPACING = core.STYLE_INDENT_SPACING
#: associated type: ``Vec2``.
STYLE_CELL_PADDING = core.STYLE_CELL_PADDING
#: associated type: ``float``.
STYLE_SCROLLBAR_SIZE = core.STYLE_SCROLLBAR_SIZE
#: associated type: ``float``.
STYLE_SCROLLBAR_ROUNDING = core.STYLE_SCROLLBAR_ROUNDING
#: associated type: ``float``.
STYLE_GRAB_MIN_SIZE = core.STYLE_GRAB_MIN_SIZE
#: associated type: ``float``.
STYLE_GRAB_ROUNDING = core.STYLE_GRAB_ROUNDING
#: associated type: ``float``
STYLE_TAB_ROUNDING = core.STYLE_TAB_ROUNDING
#: associated type: flags ImGuiAlign_*.
STYLE_BUTTON_TEXT_ALIGN = core.STYLE_BUTTON_TEXT_ALIGN
#: associated type: Vec2
STYLE_SELECTABLE_TEXT_ALIGN = core.STYLE_SELECTABLE_TEXT_ALIGN

# === Button Flags (redefines for autodoc)
BUTTON_NONE = core.BUTTON_NONE
#: React on left mouse button (default)
BUTTON_MOUSE_BUTTON_LEFT = core.BUTTON_MOUSE_BUTTON_LEFT
#: React on right mouse button
BUTTON_MOUSE_BUTTON_RIGHT = core.BUTTON_MOUSE_BUTTON_RIGHT
#: React on center mouse button
BUTTON_MOUSE_BUTTON_MIDDLE = core.BUTTON_MOUSE_BUTTON_MIDDLE

# === Window flag constants (redefines for autodoc)
#:
WINDOW_NONE = core.WINDOW_NONE
#: Disable title-bar.
WINDOW_NO_TITLE_BAR = core.WINDOW_NO_TITLE_BAR
#: Disable user resizing with the lower-right grip.
WINDOW_NO_RESIZE = core.WINDOW_NO_RESIZE
#: Disable user moving the window.
WINDOW_NO_MOVE = core.WINDOW_NO_MOVE
#: Disable scrollbars (window can still scroll with mouse or programmatically).
WINDOW_NO_SCROLLBAR = core.WINDOW_NO_SCROLLBAR
#: Disable user vertically scrolling with mouse wheel. On child window, mouse wheel will be forwarded to the parent unless NoScrollbar is also set.
WINDOW_NO_SCROLL_WITH_MOUSE = core.WINDOW_NO_SCROLL_WITH_MOUSE
#: Disable user collapsing window by double-clicking on it.
WINDOW_NO_COLLAPSE = core.WINDOW_NO_COLLAPSE
#: Resize every window to its content every frame.
WINDOW_ALWAYS_AUTO_RESIZE = core.WINDOW_ALWAYS_AUTO_RESIZE
#: Disable drawing background color (WindowBg, etc.) and outside border. Similar as using SetNextWindowBgAlpha(0.0f).
WINDOW_NO_BACKGROUND = core.WINDOW_NO_BACKGROUND
#: Never load/save settings in ``.ini`` file.
WINDOW_NO_SAVED_SETTINGS = core.WINDOW_NO_SAVED_SETTINGS
#: Disable catching mouse, hovering test with pass through.
WINDOW_NO_MOUSE_INPUTS = core.WINDOW_NO_MOUSE_INPUTS
#: Has a menu-bar.
WINDOW_MENU_BAR = core.WINDOW_MENU_BAR
#: Allow horizontal scrollbar to appear (off by default). You may use SetNextWindowContentSize(ImVec2(width,0.0f)); prior to calling Begin() to specify width. Read code in imgui_demo in the "Horizontal Scrolling" section.
WINDOW_HORIZONTAL_SCROLLING_BAR = core.WINDOW_HORIZONTAL_SCROLLING_BAR
#: Disable taking focus when transitioning from hidden to visible state.
WINDOW_NO_FOCUS_ON_APPEARING = core.WINDOW_NO_FOCUS_ON_APPEARING
#: Disable bringing window to front when taking focus (e.g. clicking on it or programmatically giving it focus).
WINDOW_NO_BRING_TO_FRONT_ON_FOCUS = core.WINDOW_NO_BRING_TO_FRONT_ON_FOCUS
#: Always show vertical scrollbar (even if ContentSize.y < Size.y).
WINDOW_ALWAYS_VERTICAL_SCROLLBAR = core.WINDOW_ALWAYS_VERTICAL_SCROLLBAR
#: Always show horizontal scrollbar (even if ContentSize.x < Size.x).
WINDOW_ALWAYS_HORIZONTAL_SCROLLBAR = core.WINDOW_ALWAYS_HORIZONTAL_SCROLLBAR
#: Ensure child windows without border uses style.WindowPadding (ignored by default for non-bordered child windows, because more convenient).
WINDOW_ALWAYS_USE_WINDOW_PADDING = core.WINDOW_ALWAYS_USE_WINDOW_PADDING
#: No gamepad/keyboard navigation within the window.
WINDOW_NO_NAV_INPUTS = core.WINDOW_NO_NAV_INPUTS
#: No focusing toward this window with gamepad/keyboard navigation (e.g. skipped by CTRL+TAB).
WINDOW_NO_NAV_FOCUS = core.WINDOW_NO_NAV_FOCUS
#: Append '*' to title without affecting the ID, as a convenience to avoid using the ### operator. When used in a tab/docking context, tab is selected on closure and closure is deferred by one frame to allow code to cancel the closure (with a confirmation popup, etc.) without flicker.
WINDOW_UNSAVED_DOCUMENT = core.WINDOW_UNSAVED_DOCUMENT
#: Disable docking of this window
WINDOW_NO_DOCKING = core.WINDOW_NO_DOCKING
#: Shortcut: ``imgui.WINDOW_NO_NAV_INPUTS | imgui.WINDOW_NO_NAV_FOCUS``.
WINDOW_NO_NAV = core.WINDOW_NO_NAV
#: Shortcut: ``imgui.WINDOW_NO_TITLE_BAR | imgui.WINDOW_NO_RESIZE | imgui.WINDOW_NO_SCROLLBAR | imgui.WINDOW_NO_COLLAPSE``.
WINDOW_NO_DECORATION = core.WINDOW_NO_DECORATION
#: Shortcut: ``imgui.WINDOW_NO_MOUSE_INPUTS | imgui.WINDOW_NO_NAV_INPUTS | imgui.WINDOW_NO_NAV_FOCUS``.
WINDOW_NO_INPUTS = core.WINDOW_NO_INPUTS

# === Color Edit Flags (redefines for autodoc)
#:
COLOR_EDIT_NONE = core.COLOR_EDIT_NONE
#: ColorEdit, ColorPicker, ColorButton: ignore Alpha component (will only read 3 components from the input pointer).
COLOR_EDIT_NO_ALPHA = core.COLOR_EDIT_NO_ALPHA
#: ColorEdit: disable picker when clicking on color square.
COLOR_EDIT_NO_PICKER = core.COLOR_EDIT_NO_PICKER
#: ColorEdit: disable toggling options menu when right-clicking on inputs/small preview.
COLOR_EDIT_NO_OPTIONS = core.COLOR_EDIT_NO_OPTIONS
#: ColorEdit, ColorPicker: disable color square preview next to the inputs. (e.g. to show only the inputs)
COLOR_EDIT_NO_SMALL_PREVIEW = core.COLOR_EDIT_NO_SMALL_PREVIEW
#: ColorEdit, ColorPicker: disable inputs sliders/text widgets (e.g. to show only the small preview color square).
COLOR_EDIT_NO_INPUTS = core.COLOR_EDIT_NO_INPUTS
#: ColorEdit, ColorPicker, ColorButton: disable tooltip when hovering the preview.
COLOR_EDIT_NO_TOOLTIP = core.COLOR_EDIT_NO_TOOLTIP
#: ColorEdit, ColorPicker: disable display of inline text label (the label is still forwarded to the tooltip and picker).
COLOR_EDIT_NO_LABEL = core.COLOR_EDIT_NO_LABEL
#: ColorPicker: disable bigger color preview on right side of the picker, use small color square preview instead.
COLOR_EDIT_NO_SIDE_PREVIEW = core.COLOR_EDIT_NO_SIDE_PREVIEW
#: ColorEdit: disable drag and drop target. ColorButton: disable drag and drop source.
COLOR_EDIT_NO_DRAG_DROP = core.COLOR_EDIT_NO_DRAG_DROP
#: ColorButton: disable border (which is enforced by default)
COLOR_EDIT_NO_BORDER = core.COLOR_EDIT_NO_BORDER

#: ColorEdit, ColorPicker: show vertical alpha bar/gradient in picker.
COLOR_EDIT_ALPHA_BAR = core.COLOR_EDIT_ALPHA_BAR
#: ColorEdit, ColorPicker, ColorButton: display preview as a transparent color over a checkerboard, instead of opaque.
COLOR_EDIT_ALPHA_PREVIEW = core.COLOR_EDIT_ALPHA_PREVIEW
#: ColorEdit, ColorPicker, ColorButton: display half opaque / half checkerboard, instead of opaque.
COLOR_EDIT_ALPHA_PREVIEW_HALF = core.COLOR_EDIT_ALPHA_PREVIEW_HALF
#: (WIP) ColorEdit: Currently only disable 0.0f..1.0f limits in RGBA edition (note: you probably want to use ImGuiColorEditFlags_Float flag as well).
COLOR_EDIT_HDR = core.COLOR_EDIT_HDR
#: ColorEdit: override _display_ type among RGB/HSV/Hex. ColorPicker: select any combination using one or more of RGB/HSV/Hex.
COLOR_EDIT_DISPLAY_RGB = core.COLOR_EDIT_DISPLAY_RGB
#: ColorEdit: override _display_ type among RGB/HSV/Hex. ColorPicker: select any combination using one or more of RGB/HSV/Hex.
COLOR_EDIT_DISPLAY_HSV = core.COLOR_EDIT_DISPLAY_HSV
#: ColorEdit: override _display_ type among RGB/HSV/Hex. ColorPicker: select any combination using one or more of RGB/HSV/Hex.
COLOR_EDIT_DISPLAY_HEX = core.COLOR_EDIT_DISPLAY_HEX
#: ColorEdit, ColorPicker, ColorButton: _display_ values formatted as 0..255.
COLOR_EDIT_UINT8 = core.COLOR_EDIT_UINT8
#: ColorEdit, ColorPicker, ColorButton: _display_ values formatted as 0.0f..1.0f floats instead of 0..255 integers. No round-trip of value via integers.
COLOR_EDIT_FLOAT = core.COLOR_EDIT_FLOAT
#: ColorPicker: bar for Hue, rectangle for Sat/Value.
COLOR_EDIT_PICKER_HUE_BAR = core.COLOR_EDIT_PICKER_HUE_BAR
#: ColorPicker: wheel for Hue, triangle for Sat/Value.
COLOR_EDIT_PICKER_HUE_WHEEL = core.COLOR_EDIT_PICKER_HUE_WHEEL
#: ColorEdit, ColorPicker: input and output data in RGB format.
COLOR_EDIT_INPUT_RGB = core.COLOR_EDIT_INPUT_RGB
#: ColorEdit, ColorPicker: input and output data in HSV format.
COLOR_EDIT_INPUT_HSV = core.COLOR_EDIT_INPUT_HSV

#: Shortcut: ``imgui.COLOR_EDIT_UINT8 | imgui.COLOR_EDIT_DISPLAY_RGB | imgui.COLOR_EDIT_INPUT_RGB | imgui.COLOR_EDIT_PICKER_HUE_BAR``.
COLOR_EDIT_DEFAULT_OPTIONS = core.COLOR_EDIT_DEFAULT_OPTIONS

# === Tree node flag constants (redefines for autodoc)
#:
TREE_NODE_NONE = core.TREE_NODE_NONE
#: Draw as selected
TREE_NODE_SELECTED = core.TREE_NODE_SELECTED
#: Draw frame with background (e.g. for :func:`imgui.core.collapsing_header`).
TREE_NODE_FRAMED = core.TREE_NODE_FRAMED
#: Hit testing to allow subsequent widgets to overlap this one
TREE_NODE_ALLOW_ITEM_OVERLAP = core.TREE_NODE_ALLOW_ITEM_OVERLAP
#: Don't do a ``TreePush()`` when open
#: (e.g. for :func:`imgui.core.collapsing_header`).
#: No extra indent nor pushing on ID stack.
TREE_NODE_NO_TREE_PUSH_ON_OPEN = core.TREE_NODE_NO_TREE_PUSH_ON_OPEN
#: Don't automatically and temporarily open node when Logging is active
#: (by default logging will automatically open tree nodes).
TREE_NODE_NO_AUTO_OPEN_ON_LOG = core.TREE_NODE_NO_AUTO_OPEN_ON_LOG
#: Default node to be open
TREE_NODE_DEFAULT_OPEN = core.TREE_NODE_DEFAULT_OPEN
#: Need double-click to open node.
TREE_NODE_OPEN_ON_DOUBLE_CLICK = core.TREE_NODE_OPEN_ON_DOUBLE_CLICK
#: Only open when clicking on the arrow part. If
#: :py:data:`TREE_NODE_OPEN_ON_DOUBLE_CLICK` is also set,
#: single-click arrow or double-click all box to open.
TREE_NODE_OPEN_ON_ARROW = core.TREE_NODE_OPEN_ON_ARROW
#: No collapsing, no arrow (use as a convenience for leaf nodes).
TREE_NODE_LEAF = core.TREE_NODE_LEAF
#: Display a bullet instead of arrow.
TREE_NODE_BULLET = core.TREE_NODE_BULLET
#: Use FramePadding (even for an unframed text node) to vertically align
#: text baseline to regular widget height. Equivalent to calling
#: ``align_text_to_frame_padding()``
TREE_NODE_FRAME_PADDING = core.TREE_NODE_FRAME_PADDING
#: Extend hit box to the right-most edge, even if not framed. This is not the default in order to allow adding other items on the same line. In the future we may refactor the hit system to be front-to-back, allowing natural overlaps and then this can become the default.
TREE_NODE_SPAN_AVAILABLE_WIDTH = core.TREE_NODE_SPAN_AVAILABLE_WIDTH
#: Extend hit box to the left-most and right-most edges (bypass the indented area).
TREE_NODE_SPAN_FULL_WIDTH = core.TREE_NODE_SPAN_FULL_WIDTH
#: (WIP) Nav: left direction may move to this TreeNode() from any of its child (items submitted between TreeNode and TreePop)
TREE_NODE_NAV_LEFT_JUPS_BACK_HERE = core.TREE_NODE_NAV_LEFT_JUPS_BACK_HERE
#: Shortcut: ``imgui.TREE_NODE_FRAMED | imgui.TREE_NODE_NO_AUTO_OPEN_ON_LOG``.
TREE_NODE_COLLAPSING_HEADER = core.TREE_NODE_COLLAPSING_HEADER

# === Popup Flags (redefines for autodoc)
POPUP_NONE = core.POPUP_NONE
POPUP_MOUSE_BUTTON_LEFT = core.POPUP_MOUSE_BUTTON_LEFT
POPUP_MOUSE_BUTTON_RIGHT = core.POPUP_MOUSE_BUTTON_RIGHT
POPUP_MOUSE_BUTTON_MIDDLE = core.POPUP_MOUSE_BUTTON_MIDDLE
POPUP_MOUSE_BUTTON_MASK = core.POPUP_MOUSE_BUTTON_MASK
POPUP_MOUSE_BUTTON_DEFAULT = core.POPUP_MOUSE_BUTTON_DEFAULT
POPUP_NO_OPEN_OVER_EXISTING_POPUP = core.POPUP_NO_OPEN_OVER_EXISTING_POPUP
POPUP_NO_OPEN_OVER_ITEMS = core.POPUP_NO_OPEN_OVER_ITEMS
POPUP_ANY_POPUP_ID = core.POPUP_ANY_POPUP_ID
POPUP_ANY_POPUP_LEVEL = core.POPUP_ANY_POPUP_LEVEL
POPUP_ANY_POPUP = core.POPUP_ANY_POPUP

# === Color flag constants (redefines for autodoc)
COLOR_TEXT = core.COLOR_TEXT
COLOR_TEXT_DISABLED = core.COLOR_TEXT_DISABLED
COLOR_WINDOW_BACKGROUND = core.COLOR_WINDOW_BACKGROUND
COLOR_CHILD_BACKGROUND = core.COLOR_CHILD_BACKGROUND
COLOR_POPUP_BACKGROUND = core.COLOR_POPUP_BACKGROUND
COLOR_BORDER = core.COLOR_BORDER
COLOR_BORDER_SHADOW = core.COLOR_BORDER_SHADOW
COLOR_FRAME_BACKGROUND = core.COLOR_FRAME_BACKGROUND
COLOR_FRAME_BACKGROUND_HOVERED = core.COLOR_FRAME_BACKGROUND_HOVERED
COLOR_FRAME_BACKGROUND_ACTIVE = core.COLOR_FRAME_BACKGROUND_ACTIVE
COLOR_TITLE_BACKGROUND = core.COLOR_TITLE_BACKGROUND
COLOR_TITLE_BACKGROUND_ACTIVE = core.COLOR_TITLE_BACKGROUND_ACTIVE
COLOR_TITLE_BACKGROUND_COLLAPSED = core.COLOR_TITLE_BACKGROUND_COLLAPSED
COLOR_MENUBAR_BACKGROUND = core.COLOR_MENUBAR_BACKGROUND
COLOR_SCROLLBAR_BACKGROUND = core.COLOR_SCROLLBAR_BACKGROUND
COLOR_SCROLLBAR_GRAB = core.COLOR_SCROLLBAR_GRAB
COLOR_SCROLLBAR_GRAB_HOVERED = core.COLOR_SCROLLBAR_GRAB_HOVERED
COLOR_SCROLLBAR_GRAB_ACTIVE = core.COLOR_SCROLLBAR_GRAB_ACTIVE
COLOR_CHECK_MARK = core.COLOR_CHECK_MARK
COLOR_SLIDER_GRAB = core.COLOR_SLIDER_GRAB
COLOR_SLIDER_GRAB_ACTIVE = core.COLOR_SLIDER_GRAB_ACTIVE
COLOR_BUTTON = core.COLOR_BUTTON
COLOR_BUTTON_HOVERED = core.COLOR_BUTTON_HOVERED
COLOR_BUTTON_ACTIVE = core.COLOR_BUTTON_ACTIVE
COLOR_HEADER = core.COLOR_HEADER
COLOR_HEADER_HOVERED = core.COLOR_HEADER_HOVERED
COLOR_HEADER_ACTIVE = core.COLOR_HEADER_ACTIVE
COLOR_SEPARATOR = core.COLOR_SEPARATOR
COLOR_SEPARATOR_HOVERED = core.COLOR_SEPARATOR_HOVERED
COLOR_SEPARATOR_ACTIVE = core.COLOR_SEPARATOR_ACTIVE
COLOR_RESIZE_GRIP = core.COLOR_RESIZE_GRIP
COLOR_RESIZE_GRIP_HOVERED = core.COLOR_RESIZE_GRIP_HOVERED
COLOR_RESIZE_GRIP_ACTIVE = core.COLOR_RESIZE_GRIP_ACTIVE
COLOR_TAB = core.COLOR_TAB
COLOR_TAB_HOVERED = core.COLOR_TAB_HOVERED                           
COLOR_TAB_ACTIVE = core.COLOR_TAB_ACTIVE                            
COLOR_TAB_UNFOCUSED = core.COLOR_TAB_UNFOCUSED                         
COLOR_TAB_UNFOCUSED_ACTIVE = core.COLOR_TAB_UNFOCUSED_ACTIVE
#: Preview overlay color when about to docking something
COLOR_DOCKING_PREVIEW = core.COLOR_DOCKING_PREVIEW
#: Background color for empty node (e.g. CentralNode with no window docked into it)
COLOR_DOCKING_EMPTY_BACKGROUND = core.COLOR_DOCKING_EMPTY_BACKGROUND
COLOR_PLOT_LINES = core.COLOR_PLOT_LINES
COLOR_PLOT_LINES_HOVERED = core.COLOR_PLOT_LINES_HOVERED
COLOR_PLOT_HISTOGRAM = core.COLOR_PLOT_HISTOGRAM
COLOR_PLOT_HISTOGRAM_HOVERED = core.COLOR_PLOT_HISTOGRAM_HOVERED
COLOR_TABLE_HEADER_BACKGROUND = core.COLOR_TABLE_HEADER_BACKGROUND
COLOR_TABLE_BORDER_STRONG = core.COLOR_TABLE_BORDER_STRONG
COLOR_TABLE_BORDER_LIGHT = core.COLOR_TABLE_BORDER_LIGHT
COLOR_TABLE_ROW_BACKGROUND = core.COLOR_TABLE_ROW_BACKGROUND
COLOR_TABLE_ROW_BACKGROUND_ALT = core.COLOR_TABLE_ROW_BACKGROUND_ALT
COLOR_TEXT_SELECTED_BACKGROUND = core.COLOR_TEXT_SELECTED_BACKGROUND
COLOR_DRAG_DROP_TARGET = core.COLOR_DRAG_DROP_TARGET
COLOR_NAV_HIGHLIGHT = core.COLOR_NAV_HIGHLIGHT
COLOR_NAV_WINDOWING_HIGHLIGHT = core.COLOR_NAV_WINDOWING_HIGHLIGHT
COLOR_NAV_WINDOWING_DIM_BACKGROUND = core.COLOR_NAV_WINDOWING_DIM_BACKGROUND
COLOR_MODAL_WINDOW_DIM_BACKGROUND = core.COLOR_MODAL_WINDOW_DIM_BACKGROUND
COLOR_COUNT = core.COLOR_COUNT

# === Data Type (redefines for autodoc)
DATA_TYPE_S8     = core.DATA_TYPE_S8    
DATA_TYPE_U8     = core.DATA_TYPE_U8    
DATA_TYPE_S16    = core.DATA_TYPE_S16   
DATA_TYPE_U16    = core.DATA_TYPE_U16   
DATA_TYPE_S32    = core.DATA_TYPE_S32   
DATA_TYPE_U32    = core.DATA_TYPE_U32   
DATA_TYPE_S64    = core.DATA_TYPE_S64   
DATA_TYPE_U64    = core.DATA_TYPE_U64   
DATA_TYPE_FLOAT  = core.DATA_TYPE_FLOAT 
DATA_TYPE_DOUBLE = core.DATA_TYPE_DOUBLE


# === Selectable flag constants (redefines for autodoc)
SELECTABLE_NONE = core.SELECTABLE_NONE
#: Clicking this don't close parent popup window.
SELECTABLE_DONT_CLOSE_POPUPS = core.SELECTABLE_DONT_CLOSE_POPUPS
#: Selectable frame can span all columns
#: (text will still fit in current column).
SELECTABLE_SPAN_ALL_COLUMNS = core.SELECTABLE_SPAN_ALL_COLUMNS
#: Generate press events on double clicks too.
SELECTABLE_ALLOW_DOUBLE_CLICK = core.SELECTABLE_ALLOW_DOUBLE_CLICK
SELECTABLE_DISABLED = core.SELECTABLE_DISABLED
SELECTABLE_ALLOW_ITEM_OVERLAP = core.SELECTABLE_ALLOW_ITEM_OVERLAP

# === Combo flag constants (redefines for autodoc)
COMBO_NONE = core.COMBO_NONE
#: Align the popup toward the left by default
COMBO_POPUP_ALIGN_LEFT = core.COMBO_POPUP_ALIGN_LEFT
#: Max ~4 items visible. Tip: If you want your combo popup to be a
#: specific size you can use SetNextWindowSizeConstraints() prior
#: to calling BeginCombo()
COMBO_HEIGHT_SMALL = core.COMBO_HEIGHT_SMALL
#: Max ~8 items visible (default)
COMBO_HEIGHT_REGULAR = core.COMBO_HEIGHT_REGULAR
#: Max ~20 items visible
COMBO_HEIGHT_LARGE = core.COMBO_HEIGHT_LARGE
#: As many fitting items as possible
COMBO_HEIGHT_LARGEST = core.COMBO_HEIGHT_LARGEST
#: Display on the preview box without the square arrow button
COMBO_NO_ARROW_BUTTON = core.COMBO_NO_ARROW_BUTTON
#: Display only a square arrow button
COMBO_NO_PREVIEW = core.COMBO_NO_PREVIEW
#: Shortcut: ``imgui.COMBO_HEIGHT_SMALL | imgui.COMBO_HEIGHT_REGULAR | imgui.COMBO_HEIGHT_LARGE | imgui.COMBO_HEIGHT_LARGEST``.
COMBO_HEIGHT_MASK = COMBO_HEIGHT_SMALL | COMBO_HEIGHT_REGULAR | COMBO_HEIGHT_LARGE | COMBO_HEIGHT_LARGEST

# === Tab Bar Flags (redefines for autodoc)
TAB_BAR_NONE = core.TAB_BAR_NONE
#: Allow manually dragging tabs to re-order them + New tabs are appended at the end of list
TAB_BAR_REORDERABLE = core.TAB_BAR_REORDERABLE
#: Automatically select new tabs when they appear
TAB_BAR_AUTO_SELECT_NEW_TABS = core.TAB_BAR_AUTO_SELECT_NEW_TABS
#: Disable buttons to open the tab list popup
TAB_BAR_TAB_LIST_POPUP_BUTTON = core.TAB_BAR_TAB_LIST_POPUP_BUTTON
#: Disable behavior of closing tabs (that are submitted with p_open != NULL) with middle mouse button. You can still repro this behavior on user's side with if (IsItemHovered() && IsMouseClicked(2)) *p_open = false.
TAB_BAR_NO_CLOSE_WITH_MIDDLE_MOUSE_BUTTON = core.TAB_BAR_NO_CLOSE_WITH_MIDDLE_MOUSE_BUTTON
#: Disable scrolling buttons (apply when fitting policy is ImGuiTabBarFlags_FittingPolicyScroll)
TAB_BAR_NO_TAB_LIST_SCROLLING_BUTTONS = core.TAB_BAR_NO_TAB_LIST_SCROLLING_BUTTONS
#: Disable tooltips when hovering a tab
TAB_BAR_NO_TOOLTIP = core.TAB_BAR_NO_TOOLTIP
#: Resize tabs when they don't fit
TAB_BAR_FITTING_POLICY_RESIZE_DOWN = core.TAB_BAR_FITTING_POLICY_RESIZE_DOWN
#: Add scroll buttons when tabs don't fit
TAB_BAR_FITTING_POLICY_SCROLL = core.TAB_BAR_FITTING_POLICY_SCROLL
#: TAB_BAR_FITTING_POLICY_RESIZE_DOWN | TAB_BAR_FITTING_POLICY_SCROLL
TAB_BAR_FITTING_POLICY_MASK = core.TAB_BAR_FITTING_POLICY_MASK
#: TAB_BAR_FITTING_POLICY_RESIZE_DOWN
TAB_BAR_FITTING_POLICY_DEFAULT = core.TAB_BAR_FITTING_POLICY_DEFAULT

# === Tab Item Flags (redefines for autodoc)
TAB_ITEM_NONE = core.TAB_ITEM_NONE
#: Append '*' to title without affecting the ID, as a convenience to avoid using the ### operator. Also: tab is selected on closure and closure is deferred by one frame to allow code to undo it without flicker.
TAB_ITEM_UNSAVED_DOCUMENT = core.TAB_ITEM_UNSAVED_DOCUMENT
#: Trigger flag to programmatically make the tab selected when calling BeginTabItem()
TAB_ITEM_SET_SELECTED = core.TAB_ITEM_SET_SELECTED
#: Disable behavior of closing tabs (that are submitted with p_open != NULL) with middle mouse button. You can still repro this behavior on user's side with if (IsItemHovered() && IsMouseClicked(2)) *p_open = false.
TAB_ITEM_NO_CLOSE_WITH_MIDDLE_MOUSE_BUTTON = core.TAB_ITEM_NO_CLOSE_WITH_MIDDLE_MOUSE_BUTTON
#: Don't call PushID(tab->ID)/PopID() on BeginTabItem()/EndTabItem()
TAB_ITEM_NO_PUSH_ID = core.TAB_ITEM_NO_PUSH_ID
#: Disable tooltip for the given tab
TAB_ITEM_NO_TOOLTIP = core.TAB_ITEM_NO_TOOLTIP
#: Disable reordering this tab or having another tab cross over this tab
TAB_ITEM_NO_REORDER = core.TAB_ITEM_NO_REORDER
#: Enforce the tab position to the left of the tab bar (after the tab list popup button)
TAB_ITEM_LEADING = core.TAB_ITEM_LEADING
#: Enforce the tab position to the right of the tab bar (before the scrolling buttons)
TAB_ITEM_TRAILING = core.TAB_ITEM_TRAILING


# === Table Flags ===
#: # Features
#: None
TABLE_NONE                   = core.TABLE_NONE
#: Enable resizing columns.
TABLE_RESIZABLE              = core.TABLE_RESIZABLE
#: Enable reordering columns in header row (need calling TableSetupColumn() + TableHeadersRow() to display headers)
TABLE_REORDERABLE            = core.TABLE_REORDERABLE
#: Enable hiding/disabling columns in context menu.
TABLE_HIDEABLE               = core.TABLE_HIDEABLE
#: Enable sorting. Call TableGetSortSpecs() to obtain sort specs. Also see ImGuiTableFlags_SortMulti and ImGuiTableFlags_SortTristate.
TABLE_SORTABLE               = core.TABLE_SORTABLE
#: Disable persisting columns order, width and sort settings in the .ini file.
TABLE_NO_SAVED_SETTINGS      = core.TABLE_NO_SAVED_SETTINGS
#: Right-click on columns body/contents will display table context menu. By default it is available in TableHeadersRow().
TABLE_CONTEXT_MENU_IN_BODY   = core.TABLE_CONTEXT_MENU_IN_BODY
#: # Decorations
#: Set each RowBg color with ImGuiCol_TableRowBg or ImGuiCol_TableRowBgAlt (equivalent of calling TableSetBgColor with ImGuiTableBgFlags_RowBg0 on each row manually)
TABLE_ROW_BACKGROUND                    = core.TABLE_ROW_BACKGROUND
#: Draw horizontal borders between rows.
TABLE_BORDERS_INNER_HORIZONTAL          = core.TABLE_BORDERS_INNER_HORIZONTAL
#: Draw horizontal borders at the top and bottom.
TABLE_BORDERS_OUTER_HORIZONTAL          = core.TABLE_BORDERS_OUTER_HORIZONTAL
#: Draw vertical borders between columns.
TABLE_BORDERS_INNER_VERTICAL            = core.TABLE_BORDERS_INNER_VERTICAL
#: Draw vertical borders on the left and right sides.
TABLE_BORDERS_OUTER_VERTICAL            = core.TABLE_BORDERS_OUTER_VERTICAL
#: Draw horizontal borders.
TABLE_BORDERS_HORIZONTAL                = core.TABLE_BORDERS_HORIZONTAL
#: Draw vertical borders.
TABLE_BORDERS_VERTICAL                  = core.TABLE_BORDERS_VERTICAL
#: Draw inner borders.
TABLE_BORDERS_INNER                     = core.TABLE_BORDERS_INNER
#: Draw outer borders.
TABLE_BORDERS_OUTER                     = core.TABLE_BORDERS_OUTER
#: Draw all borders.
TABLE_BORDERS                           = core.TABLE_BORDERS
#: [ALPHA] Disable vertical borders in columns Body (borders will always appears in Headers). -> May move to style
TABLE_NO_BORDERS_IN_BODY                = core.TABLE_NO_BORDERS_IN_BODY
#: [ALPHA] Disable vertical borders in columns Body until hovered for resize (borders will always appears in Headers). -> May move to style
TABLE_NO_BORDERS_IN_BODY_UTIL_RESIZE    = core.TABLE_NO_BORDERS_IN_BODY_UTIL_RESIZE
#: # Sizing Policy (read above for defaults)
#: Columns default to _WidthFixed or _WidthAuto (if resizable or not resizable), matching contents width.
TABLE_SIZING_FIXED_FIT      = core.TABLE_SIZING_FIXED_FIT
#: Columns default to _WidthFixed or _WidthAuto (if resizable or not resizable), matching the maximum contents width of all columns. Implicitly enable ImGuiTableFlags_NoKeepColumnsVisible.
TABLE_SIZING_FIXED_SAME     = core.TABLE_SIZING_FIXED_SAME
#: Columns default to _WidthStretch with default weights proportional to each columns contents widths.
TABLE_SIZING_STRETCH_PROP   = core.TABLE_SIZING_STRETCH_PROP
#: Columns default to _WidthStretch with default weights all equal, unless overriden by TableSetupColumn().
TABLE_SIZING_STRETCH_SAME   = core.TABLE_SIZING_STRETCH_SAME
#: # Sizing Extra Options
#: Make outer width auto-fit to columns, overriding outer_size.x value. Only available when ScrollX/ScrollY are disabled and Stretch columns are not used.
TABLE_NO_HOST_EXTEND_X          = core.TABLE_NO_HOST_EXTEND_X
#: Make outer height stop exactly at outer_size.y (prevent auto-extending table past the limit). Only available when ScrollX/ScrollY are disabled. Data below the limit will be clipped and not visible.
TABLE_NO_HOST_EXTEND_Y          = core.TABLE_NO_HOST_EXTEND_Y
#: Disable keeping column always minimally visible when ScrollX is off and table gets too small. Not recommended if columns are resizable.
TABLE_NO_KEEP_COLUMNS_VISIBLE   = core.TABLE_NO_KEEP_COLUMNS_VISIBLE
#: Disable distributing remainder width to stretched columns (width allocation on a 100-wide table with 3 columns: Without this flag: 33,33,34. With this flag: 33,33,33). With larger number of columns, resizing will appear to be less smooth.
TABLE_PRECISE_WIDTHS            = core.TABLE_PRECISE_WIDTHS
#: # Clipping
#: Disable clipping rectangle for every individual columns (reduce draw command count, items will be able to overflow into other columns). Generally incompatible with TableSetupScrollFreeze().
TABLE_NO_CLIP = core.TABLE_NO_CLIP
#: # Padding
#: Default if BordersOuterV is on. Enable outer-most padding. Generally desirable if you have headers.
TABLE_PAD_OUTER_X       = core.TABLE_PAD_OUTER_X
#: Default if BordersOuterV is off. Disable outer-most padding.
TABLE_NO_PAD_OUTER_X    = core.TABLE_NO_PAD_OUTER_X
#: Disable inner padding between columns (double inner padding if BordersOuterV is on, single inner padding if BordersOuterV is off).
TABLE_NO_PAD_INNER_X    = core.TABLE_NO_PAD_INNER_X
#: # Scrolling
#: Enable horizontal scrolling. Require 'outer_size' parameter of BeginTable() to specify the container size. Changes default sizing policy. Because this create a child window, ScrollY is currently generally recommended when using ScrollX.
TABLE_SCROLL_X = core.TABLE_SCROLL_X 
#: Enable vertical scrolling. Require 'outer_size' parameter of BeginTable() to specify the container size.
TABLE_SCROLL_Y = core.TABLE_SCROLL_Y
#: # Sorting
#: Hold shift when clicking headers to sort on multiple column. TableGetSortSpecs() may return specs where (SpecsCount > 1).
TABLE_SORT_MULTI    = core.TABLE_SORT_MULTI
#: Allow no sorting, disable default sorting. TableGetSortSpecs() may return specs where (SpecsCount == 0).
TABLE_SORT_TRISTATE = core.TABLE_SORT_TRISTATE

# === Table Column Flags ===
#: # Input configuration flags
#: None
TABLE_COLUMN_NONE                   = core.TABLE_COLUMN_NONE
#: Default as a hidden/disabled column.
TABLE_COLUMN_DEFAULT_HIDE           = core.TABLE_COLUMN_DEFAULT_HIDE
#: Default as a sorting column.
TABLE_COLUMN_DEFAULT_SORT           = core.TABLE_COLUMN_DEFAULT_SORT
#: Column will stretch. Preferable with horizontal scrolling disabled (default if table sizing policy is _SizingStretchSame or _SizingStretchProp).
TABLE_COLUMN_WIDTH_STRETCH          = core.TABLE_COLUMN_WIDTH_STRETCH
#: Column will not stretch. Preferable with horizontal scrolling enabled (default if table sizing policy is _SizingFixedFit and table is resizable).
TABLE_COLUMN_WIDTH_FIXED            = core.TABLE_COLUMN_WIDTH_FIXED
#: Disable manual resizing.
TABLE_COLUMN_NO_RESIZE              = core.TABLE_COLUMN_NO_RESIZE
#: Disable manual reordering this column, this will also prevent other columns from crossing over this column.
TABLE_COLUMN_NO_REORDER             = core.TABLE_COLUMN_NO_REORDER
#: Disable ability to hide/disable this column.
TABLE_COLUMN_NO_HIDE                = core.TABLE_COLUMN_NO_HIDE
#: Disable clipping for this column (all NoClip columns will render in a same draw command).
TABLE_COLUMN_NO_CLIP                = core.TABLE_COLUMN_NO_CLIP
#: Disable ability to sort on this field (even if ImGuiTableFlags_Sortable is set on the table).
TABLE_COLUMN_NO_SORT                = core.TABLE_COLUMN_NO_SORT
#: Disable ability to sort in the ascending direction.
TABLE_COLUMN_NO_SORT_ASCENDING      = core.TABLE_COLUMN_NO_SORT_ASCENDING
#: Disable ability to sort in the descending direction.
TABLE_COLUMN_NO_SORT_DESCENDING     = core.TABLE_COLUMN_NO_SORT_DESCENDING
#: Disable header text width contribution to automatic column width.
TABLE_COLUMN_NO_HEADER_WIDTH        = core.TABLE_COLUMN_NO_HEADER_WIDTH
#: Make the initial sort direction Ascending when first sorting on this column (default).
TABLE_COLUMN_PREFER_SORT_ASCENDING  = core.TABLE_COLUMN_PREFER_SORT_ASCENDING
#: Make the initial sort direction Descending when first sorting on this column.
TABLE_COLUMN_PREFER_SORT_DESCENDING = core.TABLE_COLUMN_PREFER_SORT_DESCENDING
#: Use current Indent value when entering cell (default for column 0).
TABLE_COLUMN_INDENT_ENABLE          = core.TABLE_COLUMN_INDENT_ENABLE
#: Ignore current Indent value when entering cell (default for columns > 0). Indentation changes _within_ the cell will still be honored.
TABLE_COLUMN_INDENT_DISABLE         = core.TABLE_COLUMN_INDENT_DISABLE
#: # Output status flags, read-only via TableGetColumnFlags()
#: Status: is enabled == not hidden by user/api (referred to as "Hide" in _DefaultHide and _NoHide) flags.
TABLE_COLUMN_IS_ENABLED     = core.TABLE_COLUMN_IS_ENABLED
#: Status: is visible == is enabled AND not clipped by scrolling.
TABLE_COLUMN_IS_VISIBLE     = core.TABLE_COLUMN_IS_VISIBLE
#: Status: is currently part of the sort specs
TABLE_COLUMN_IS_SORTED      = core.TABLE_COLUMN_IS_SORTED
#: Status: is hovered by mouse
TABLE_COLUMN_IS_HOVERED     = core.TABLE_COLUMN_IS_HOVERED

# === Table Row Flags ===
#: None
TABLE_ROW_NONE      = core.TABLE_ROW_NONE
#: Identify header row (set default background color + width of its contents accounted different for auto column width)
TABLE_ROW_HEADERS   = core.TABLE_ROW_HEADERS

# === Table Background Target ===
#: None
TABLE_BACKGROUND_TARGET_NONE        = core.TABLE_BACKGROUND_TARGET_NONE
#: Set row background color 0 (generally used for background, automatically set when ImGuiTableFlags_RowBg is used)
TABLE_BACKGROUND_TARGET_ROW_BG0     = core.TABLE_BACKGROUND_TARGET_ROW_BG0
#: Set row background color 1 (generally used for selection marking)
TABLE_BACKGROUND_TARGET_ROW_BG1     = core.TABLE_BACKGROUND_TARGET_ROW_BG1
#: Set cell background color (top-most color)
TABLE_BACKGROUND_TARGET_CELL_BG     = core.TABLE_BACKGROUND_TARGET_CELL_BG

# === Focus flag constants (redefines for autodoc)
FOCUS_NONE = core.FOCUS_NONE
#: IsWindowFocused(): Return true if any children of the window is focused
FOCUS_CHILD_WINDOWS = core.FOCUS_CHILD_WINDOWS
#: IsWindowFocused(): Test from root window (top most parent of the current hierarchy)
FOCUS_ROOT_WINDOW = core.FOCUS_ROOT_WINDOW
#: IsWindowFocused(): Return true if any window is focused
FOCUS_ANY_WINDOW = core.FOCUS_ANY_WINDOW
#: Shortcut: ``imgui.FOCUS_CHILD_WINDOWS | imgui.FOCUS_ROOT_WINDOW``.
FOCUS_ROOT_AND_CHILD_WINDOWS = core.FOCUS_CHILD_WINDOWS | core.FOCUS_ROOT_WINDOW

# === Hovered flag constants (redefines for autodoc)
#: Return true if directly over the item/window, not obstructed by
#: another window, not obstructed by an active popup or modal
#: blocking inputs under them.
HOVERED_NONE = core.HOVERED_NONE
#: IsWindowHovered() only: Return true if any children of the window is hovered
HOVERED_CHILD_WINDOWS = core.HOVERED_CHILD_WINDOWS
#: IsWindowHovered() only: Test from root window (top most parent of the current hierarchy)
HOVERED_ROOT_WINDOW = core.HOVERED_ROOT_WINDOW
#: IsWindowHovered() only: Return true if any window is hovered
HOVERED_ANY_WINDOW = core.HOVERED_ANY_WINDOW
#: Return true even if a popup window is normally blocking access to this item/window
HOVERED_ALLOW_WHEN_BLOCKED_BY_POPUP = core.HOVERED_ALLOW_WHEN_BLOCKED_BY_POPUP
#: Return true even if an active item is blocking access to this item/window. Useful for Drag and Drop patterns.
HOVERED_ALLOW_WHEN_BLOCKED_BY_ACTIVE_ITEM = core.HOVERED_ALLOW_WHEN_BLOCKED_BY_ACTIVE_ITEM
#: Return true even if the position is overlapped by another window
HOVERED_ALLOW_WHEN_OVERLAPPED = core.HOVERED_ALLOW_WHEN_OVERLAPPED
HOVERED_ALLOW_WHEN_DISABLED = core.HOVERED_ALLOW_WHEN_DISABLED
#: Shortcut: ``imgui.HOVERED_ALLOW_WHEN_BLOCKED_BY_POPUP | imgui.HOVERED_ALLOW_WHEN_BLOCKED_BY_ACTIVE_ITEM | imgui.HOVERED_ALLOW_WHEN_OVERLAPPED``.
HOVERED_RECT_ONLY = core.HOVERED_ALLOW_WHEN_BLOCKED_BY_POPUP | core.HOVERED_ALLOW_WHEN_BLOCKED_BY_ACTIVE_ITEM | core.HOVERED_ALLOW_WHEN_OVERLAPPED
#: Shortcut: ``imgui.HOVERED_ROOT_WINDOW | imgui.HOVERED_CHILD_WINDOWS``.
HOVERED_ROOT_AND_CHILD_WINDOWS = core.HOVERED_ROOT_WINDOW | core.HOVERED_CHILD_WINDOWS

# === Flags for imgui.dockspace(), shared/inherited by child nodes. (redefines for autodoc)
#: (Some flags can be applied to individual nodes directly)
DOCKNODE_NONE = core.DOCKNODE_NONE
#: Shared       # Don't display the dockspace node but keep it alive. Windows docked into this dockspace node won't be undocked.
DOCKNODE_KEEPALIVE_ONLY = core.DOCKNODE_KEEPALIVE_ONLY
#: Shared       # Disable docking inside the Central Node, which will be always kept empty.
DOCKNODE_NO_DOCKING_IN_CENTRAL_NODE = core.DOCKNODE_NO_DOCKING_IN_CENTRAL_NODE
#: Shared       # Enable passthru dockspace: 1) dockspace() will render a COLOR_WINDOW_BACKGROUND background covering everything excepted the Central Node when empty. Meaning the host window should probably use set_next_window_bg_alpha(0.0f) prior to begin() when using this. 2) When Central Node is empty: let inputs pass-through + won't display a DockingEmptyBg background. See demo for details.
DOCKNODE_PASSTHRU_CENTRAL_NODE = core.DOCKNODE_PASSTHRU_CENTRAL_NODE
#: Shared/Local # Disable splitting the node into smaller nodes. Useful e.g. when embedding dockspaces into a main root one (the root one may have splitting disabled to reduce confusion). Note: when turned off, existing splits will be preserved.
DOCKNODE_NO_SPLIT = core.DOCKNODE_NO_SPLIT
#: Shared/Local # Disable resizing node using the splitter/separators. Useful with programmatically setup dockspaces.
DOCKNODE_NO_RESIZE = core.DOCKNODE_NO_RESIZE
#: Shared/Local # Tab bar will automatically hide when there is a single window in the dock node.
DOCKNODE_AUTO_HIDE_TABBAR = core.DOCKNODE_AUTO_HIDE_TABBAR

# === Drag Drop flag constants (redefines for autodoc)
DRAG_DROP_NONE = core.DRAG_DROP_NONE
#: By default, a successful call to BeginDragDropSource opens a tooltip
#: so you can display a preview or description of the source contents.
#: This flag disable this behavior.
DRAG_DROP_SOURCE_NO_PREVIEW_TOOLTIP = core.DRAG_DROP_SOURCE_NO_PREVIEW_TOOLTIP
#: By default, when dragging we clear data so that IsItemHovered() will
#: return true, to avoid subsequent user code submitting tooltips. This
#: flag disable this behavior so you can still call IsItemHovered() on
#: the source item.
DRAG_DROP_SOURCE_NO_DISABLE_HOVER = core.DRAG_DROP_SOURCE_NO_DISABLE_HOVER
#: Disable the behavior that allows to open tree nodes and collapsing
#: header by holding over them while dragging a source item.
DRAG_DROP_SOURCE_NO_HOLD_TO_OPEN_OTHERS = core.DRAG_DROP_SOURCE_NO_HOLD_TO_OPEN_OTHERS
#: Allow items such as Text(), Image() that have no unique identifier to
#: be used as drag source, by manufacturing a temporary identifier based
#: on their window-relative position. This is extremely unusual within the
#: dear imgui ecosystem and so we made it explicit.
DRAG_DROP_SOURCE_ALLOW_NULL_ID = core.DRAG_DROP_SOURCE_ALLOW_NULL_ID
#: External source (from outside of imgui), won't attempt to read current
#: item/window info. Will always return true. Only one Extern source can
#: be active simultaneously.
DRAG_DROP_SOURCE_EXTERN = core.DRAG_DROP_SOURCE_EXTERN
#: Automatically expire the payload if the source cease to be submitted
#: (otherwise payloads are persisting while being dragged)
DRAG_DROP_SOURCE_AUTO_EXPIRE_PAYLOAD = core.DRAG_DROP_SOURCE_AUTO_EXPIRE_PAYLOAD

# === Accept Drag Drop Payload flag constants (redefines for autodoc)
#: AcceptDragDropPayload() will returns true even before the mouse button
#: is released. You can then call IsDelivery() to test if the payload
#: needs to be delivered.
DRAG_DROP_ACCEPT_BEFORE_DELIVERY = core.DRAG_DROP_ACCEPT_BEFORE_DELIVERY
#: Do not draw the default highlight rectangle when hovering over target.
DRAG_DROP_ACCEPT_NO_DRAW_DEFAULT_RECT = core.DRAG_DROP_ACCEPT_NO_DRAW_DEFAULT_RECT
DRAG_DROP_ACCEPT_NO_PREVIEW_TOOLTIP = core.DRAG_DROP_ACCEPT_NO_PREVIEW_TOOLTIP
#: For peeking ahead and inspecting the payload before delivery.
DRAG_DROP_ACCEPT_PEEK_ONLY = core.DRAG_DROP_ACCEPT_PEEK_ONLY

# === Cardinal Direction
#: Direction None
DIRECTION_NONE = core.DIRECTION_NONE
#: Direction Left
DIRECTION_LEFT = core.DIRECTION_LEFT
#: Direction Right
DIRECTION_RIGHT = core.DIRECTION_RIGHT
#: Direction Up
DIRECTION_UP = core.DIRECTION_UP
#: Direction Down
DIRECTION_DOWN = core.DIRECTION_DOWN

# === Sorting direction
SORT_DIRECTION_NONE  = core.SORT_DIRECTION_NONE 
#: Ascending = 0->9, A->Z etc.
SORT_DIRECTION_ASCENDING = core.SORT_DIRECTION_ASCENDING
#: Descending = 9->0, Z->A etc.
SORT_DIRECTION_DESCENDING = core.SORT_DIRECTION_DESCENDING

# === Mouse cursor flag constants (redefines for autodoc)
MOUSE_CURSOR_NONE = core.MOUSE_CURSOR_NONE
MOUSE_CURSOR_ARROW = core.MOUSE_CURSOR_ARROW
#: When hovering over InputText, etc.
MOUSE_CURSOR_TEXT_INPUT = core.MOUSE_CURSOR_TEXT_INPUT
#: Unused
MOUSE_CURSOR_RESIZE_ALL = core.MOUSE_CURSOR_RESIZE_ALL
#: When hovering over an horizontal border
MOUSE_CURSOR_RESIZE_NS = core.MOUSE_CURSOR_RESIZE_NS
#: When hovering over a vertical border or a column
MOUSE_CURSOR_RESIZE_EW = core.MOUSE_CURSOR_RESIZE_EW
#: When hovering over the bottom-left corner of a window
MOUSE_CURSOR_RESIZE_NESW = core.MOUSE_CURSOR_RESIZE_NESW
#: When hovering over the bottom-right corner of a window
MOUSE_CURSOR_RESIZE_NWSE = core.MOUSE_CURSOR_RESIZE_NWSE
#: (Unused by imgui functions. Use for e.g. hyperlinks)
MOUSE_CURSOR_HAND = core.MOUSE_CURSOR_HAND
MOUSE_CURSOR_NOT_ALLOWED = core.MOUSE_CURSOR_NOT_ALLOWED

# === Text input flag constants (redefines for autodoc)
INPUT_TEXT_NONE = core.INPUT_TEXT_NONE
#: Allow ``0123456789.+-*/``
INPUT_TEXT_CHARS_DECIMAL = core.INPUT_TEXT_CHARS_DECIMAL
#: Allow ``0123456789ABCDEFabcdef``
INPUT_TEXT_CHARS_HEXADECIMAL = core.INPUT_TEXT_CHARS_HEXADECIMAL
#: Turn a..z into A..Z
INPUT_TEXT_CHARS_UPPERCASE = core.INPUT_TEXT_CHARS_UPPERCASE
#: Filter out spaces, tabs
INPUT_TEXT_CHARS_NO_BLANK = core.INPUT_TEXT_CHARS_NO_BLANK
#: Select entire text when first taking mouse focus
INPUT_TEXT_AUTO_SELECT_ALL = core.INPUT_TEXT_AUTO_SELECT_ALL
#: Return 'true' when Enter is pressed (as opposed to when the
#: value was modified)
INPUT_TEXT_ENTER_RETURNS_TRUE = core.INPUT_TEXT_ENTER_RETURNS_TRUE
#: Call user function on pressing TAB (for completion handling)
INPUT_TEXT_CALLBACK_COMPLETION = core.INPUT_TEXT_CALLBACK_COMPLETION
#: Call user function on pressing Up/Down arrows (for history handling)
INPUT_TEXT_CALLBACK_HISTORY = core.INPUT_TEXT_CALLBACK_HISTORY
#: Call user function every time. User code may query cursor position,
#: modify text buffer.
INPUT_TEXT_CALLBACK_ALWAYS = core.INPUT_TEXT_CALLBACK_ALWAYS
#: Call user function to filter character. Modify data->EventChar to
#: replace/filter input, or return 1 to discard character.
INPUT_TEXT_CALLBACK_CHAR_FILTER = core.INPUT_TEXT_CALLBACK_CHAR_FILTER
#: Pressing TAB input a '\t' character into the text field
INPUT_TEXT_ALLOW_TAB_INPUT = core.INPUT_TEXT_ALLOW_TAB_INPUT
#: In multi-line mode, allow exiting edition by pressing Enter.
#: Ctrl+Enter to add new line (by default adds new lines with Enter).
INPUT_TEXT_CTRL_ENTER_FOR_NEW_LINE = core.INPUT_TEXT_CTRL_ENTER_FOR_NEW_LINE
#: Disable following the cursor horizontally
INPUT_TEXT_NO_HORIZONTAL_SCROLL = core.INPUT_TEXT_NO_HORIZONTAL_SCROLL
#: Overwrite mode
INPUT_TEXT_ALWAYS_OVERWRITE = core.INPUT_TEXT_ALWAYS_OVERWRITE
#: OBSOLETED in 1.82 (from Mars 2021)
INPUT_TEXT_ALWAYS_INSERT_MODE = core.INPUT_TEXT_ALWAYS_INSERT_MODE
#: Read-only mode
INPUT_TEXT_READ_ONLY = core.INPUT_TEXT_READ_ONLY
#: Password mode, display all characters as '*'
INPUT_TEXT_PASSWORD = core.INPUT_TEXT_PASSWORD
#: Disable undo/redo. Note that input text owns the text data while
#: active, if you want to provide your own undo/redo stack you need
#: e.g. to call clear_active_id().
INPUT_TEXT_NO_UNDO_REDO = core.INPUT_TEXT_NO_UNDO_REDO
INPUT_TEXT_CHARS_SCIENTIFIC = core.INPUT_TEXT_CHARS_SCIENTIFIC
INPUT_TEXT_CALLBACK_RESIZE = core.INPUT_TEXT_CALLBACK_RESIZE
INPUT_TEXT_CALLBACK_EDIT = core.INPUT_TEXT_CALLBACK_EDIT

# === Draw Corner Flags (redefines for autodoc)
DRAW_CORNER_NONE = core.DRAW_CORNER_NONE
DRAW_CORNER_TOP_LEFT = core.DRAW_CORNER_TOP_LEFT
DRAW_CORNER_TOP_RIGHT = core.DRAW_CORNER_TOP_RIGHT
DRAW_CORNER_BOTTOM_LEFT = core.DRAW_CORNER_BOTTOM_LEFT
DRAW_CORNER_BOTTOM_RIGHT = core.DRAW_CORNER_BOTTOM_RIGHT
DRAW_CORNER_TOP = core.DRAW_CORNER_TOP
DRAW_CORNER_BOTTOM = core.DRAW_CORNER_BOTTOM
DRAW_CORNER_LEFT = core.DRAW_CORNER_LEFT
DRAW_CORNER_RIGHT = core.DRAW_CORNER_RIGHT
DRAW_CORNER_ALL = core.DRAW_CORNER_ALL

# === Draw Flags (redifines for autodoc)
#: None
DRAW_NONE                        = core.DRAW_NONE
#: path_stroke(), add_polyline(): specify that shape should be closed (Important: this is always == 1 for legacy reason)
DRAW_CLOSED                      = core.DRAW_CLOSED                     
#: add_rect(), add_rect_filled(), path_rect(): enable rounding top-left corner only (when rounding > 0.0f, we default to all corners). Was 0x01.
DRAW_ROUND_CORNERS_TOP_LEFT      = core.DRAW_ROUND_CORNERS_TOP_LEFT     
#: add_rect(), add_rect_filled(), path_rect(): enable rounding top-right corner only (when rounding > 0.0f, we default to all corners). Was 0x02.
DRAW_ROUND_CORNERS_TOP_RIGHT     = core.DRAW_ROUND_CORNERS_TOP_RIGHT    
#: add_rect(), add_rect_filled(), path_rect(): enable rounding bottom-left corner only (when rounding > 0.0f, we default to all corners). Was 0x04.
DRAW_ROUND_CORNERS_BOTTOM_LEFT   = core.DRAW_ROUND_CORNERS_BOTTOM_LEFT  
#: add_rect(), add_rect_filled(), path_rect(): enable rounding bottom-right corner only (when rounding > 0.0f, we default to all corners). Wax 0x08.
DRAW_ROUND_CORNERS_BOTTOM_RIGHT  = core.DRAW_ROUND_CORNERS_BOTTOM_RIGHT 
#: add_rect(), add_rect_filled(), path_rect(): disable rounding on all corners (when rounding > 0.0f). This is NOT zero, NOT an implicit flag!
DRAW_ROUND_CORNERS_NONE          = core.DRAW_ROUND_CORNERS_NONE         
#: DRAW_ROUND_CORNERS_TOP_LEFT | DRAW_ROUND_CORNERS_TOP_RIGHT
DRAW_ROUND_CORNERS_TOP           = core.DRAW_ROUND_CORNERS_TOP          
#: DRAW_ROUND_CORNERS_BOTTOM_LEFT | DRAW_ROUND_CORNERS_BOTTOM_RIGHT
DRAW_ROUND_CORNERS_BOTTOM        = core.DRAW_ROUND_CORNERS_BOTTOM       
#: DRAW_ROUND_CORNERS_BOTTOM_LEFT | DRAW_ROUND_CORNERS_TOP_LEFT
DRAW_ROUND_CORNERS_LEFT          = core.DRAW_ROUND_CORNERS_LEFT         
#: DRAW_ROUND_CORNERS_BOTTOM_RIGHT | DRAW_ROUND_CORNERS_TOP_RIGHT
DRAW_ROUND_CORNERS_RIGHT         = core.DRAW_ROUND_CORNERS_RIGHT        
#: DRAW_ROUND_CORNERS_TOP_LEFT | DRAW_ROUND_CORNERS_TOP_RIGHT | DRAW_ROUND_CORNERS_BOTTOM_LEFT | DRAW_ROUND_CORNERS_BOTTOM_RIGHT
DRAW_ROUND_CORNERS_ALL           = core.DRAW_ROUND_CORNERS_ALL          

# === Draw List Flags (redefines for autodoc)
DRAW_LIST_NONE = core.DRAW_LIST_NONE
DRAW_LIST_ANTI_ALIASED_LINES = core.DRAW_LIST_ANTI_ALIASED_LINES
DRAW_LIST_ANTI_ALIASED_LINES_USE_TEX = core.DRAW_LIST_ANTI_ALIASED_LINES_USE_TEX
DRAW_LIST_ANTI_ALIASED_FILL = core.DRAW_LIST_ANTI_ALIASED_FILL
DRAW_LIST_ALLOW_VTX_OFFSET = core.DRAW_LIST_ALLOW_VTX_OFFSET

# === Font Atlas Flags (redefines for autodoc)
FONT_ATLAS_NONE = core.FONT_ATLAS_NONE
FONT_ATLAS_NO_POWER_OF_TWO_HEIGHT = core.FONT_ATLAS_NO_POWER_OF_TWO_HEIGHT
FONT_ATLAS_NO_MOUSE_CURSOR = core.FONT_ATLAS_NO_MOUSE_CURSOR
FONT_ATLAS_NO_BAKED_LINES = core.FONT_ATLAS_NO_BAKED_LINES

# === Config Flags (redefines for autodoc)
CONFIG_NONE = core.CONFIG_NONE
CONFIG_NAV_ENABLE_KEYBOARD = core.CONFIG_NAV_ENABLE_KEYBOARD
CONFIG_NAV_ENABLE_GAMEPAD = core.CONFIG_NAV_ENABLE_GAMEPAD
CONFIG_NAV_ENABLE_SET_MOUSE_POS = core.CONFIG_NAV_ENABLE_SET_MOUSE_POS
CONFIG_NAV_NO_CAPTURE_KEYBOARD = core.CONFIG_NAV_NO_CAPTURE_KEYBOARD
CONFIG_NO_MOUSE = core.CONFIG_NO_MOUSE
CONFIG_NO_MOUSE_CURSOR_CHANGE = core.CONFIG_NO_MOUSE_CURSOR_CHANGE
#: Docking enable flags.
CONFIG_DOCKING_ENABLE = core.CONFIG_DOCKING_ENABLE
#: Viewport enable flags (require both ImGuiBackendFlags_PlatformHasViewports + ImGuiBackendFlags_RendererHasViewports set by the respective backends)
CONFIG_VIEWEPORTS_ENABLE = core.CONFIG_VIEWEPORTS_ENABLE
#: [BETA: Don't use] FIXME-DPI: Reposition and resize imgui windows when the DpiScale of a viewport changed (mostly useful for the main viewport hosting other window). Note that resizing the main window itself is up to your application.
CONFIG_DPI_ENABLE_SCALE_VIEWPORTS = core.CONFIG_DPI_ENABLE_SCALE_VIEWPORTS
#: [BETA: Don't use] FIXME-DPI: Request bitmap-scaled fonts to match DpiScale. This is a very low-quality workaround. The correct way to handle DPI is _currently_ to replace the atlas and/or fonts in the Platform_OnChangedViewport callback, but this is all early work in progress.
CONFIG_DPI_ENABLE_SCALE_FONTS = core.CONFIG_DPI_ENABLE_SCALE_FONTS
CONFIG_IS_RGB = core.CONFIG_IS_RGB
CONFIG_IS_TOUCH_SCREEN = core.CONFIG_IS_TOUCH_SCREEN

# === Backend Flags (redefines for autodoc)
BACKEND_NONE = core.BACKEND_NONE
BACKEND_HAS_GAMEPAD = core.BACKEND_HAS_GAMEPAD
BACKEND_HAS_MOUSE_CURSORS = core.BACKEND_HAS_MOUSE_CURSORS
BACKEND_HAS_SET_MOUSE_POS = core.BACKEND_HAS_SET_MOUSE_POS
BACKEND_RENDERER_HAS_VTX_OFFSET = core.BACKEND_RENDERER_HAS_VTX_OFFSET
#: Backend Platform supports multiple viewports.
BACKEND_PLATFORM_HAS_VIEWPORTS = core.BACKEND_PLATFORM_HAS_VIEWPORTS
#: Backend Platform supports setting io.MouseHoveredViewport to the viewport directly under the mouse _IGNORING_ viewports with the ImGuiViewportFlags_NoInputs flag and _REGARDLESS_ of whether another viewport is focused and may be capturing the mouse. This information is _NOT EASY_ to provide correctly with most high-level engines! Don't set this without studying _carefully_ how the backends handle ImGuiViewportFlags_NoInputs!
BACKEND_HAS_MOUSE_HOVERED_VIEWPORT = core.BACKEND_HAS_MOUSE_HOVERED_VIEWPORT
#: Backend Renderer supports multiple viewports.
BACKEND_RENDERER_HAS_VIEWPORTS = core.BACKEND_RENDERER_HAS_VIEWPORTS

# === Slider flag (redefines for autodoc)
SLIDER_FLAGS_NONE
#: Clamp value to min/max bounds when input manually with CTRL+Click. By default CTRL+Click allows going out of bounds.
SLIDER_FLAGS_ALWAYS_CLAMP 
#: Make the widget logarithmic (linear otherwise). Consider using ImGuiSliderFlags_NoRoundToFormat with this if using a format-string with small amount of digits.
SLIDER_FLAGS_LOGARITHMIC 
#: Disable rounding underlying value to match precision of the display format string (e.g. %.3f values are rounded to those 3 digits)
SLIDER_FLAGS_NO_ROUND_TO_FORMAT 
#: Disable CTRL+Click or Enter key allowing to input text directly into the widget
SLIDER_FLAGS_NO_INPUT 

# === Mouse Button (redefines for autodoc)
MOUSE_BUTTON_LEFT = core.MOUSE_BUTTON_LEFT
MOUSE_BUTTON_RIGHT = core.MOUSE_BUTTON_RIGHT
MOUSE_BUTTON_MIDDLE = core.MOUSE_BUTTON_MIDDLE 

# === Viewport Flags (redifines for autodoc)
#: None
VIEWPORT_FLAGS_NONE                = core.VIEWPORT_FLAGS_NONE
#: Represent a Platform Window
VIEWPORT_FLAGS_IS_PLATFORM_WINDOW  = core.VIEWPORT_FLAGS_IS_PLATFORM_WINDOW
#: Represent a Platform Monitor (unused yet)
VIEWPORT_FLAGS_IS_PLATFORM_MONITOR = core.VIEWPORT_FLAGS_IS_PLATFORM_MONITOR
#: Platform Window: is created/managed by the application (rather than a dear imgui backend)
VIEWPORT_FLAGS_OWNED_BY_APP        = core.VIEWPORT_FLAGS_OWNED_BY_APP
#: Platform Window: Disable platform decorations: title bar, borders, etc. (generally set all windows, but if ImGuiConfigFlags_ViewportsDecoration is set we only set this on popups/tooltips)
VIEWPORT_FLAGS_NO_DECORATION = core.VIEWPORT_FLAGS_NO_DECORATION
#: Platform Window: Disable platform task bar icon (generally set on popups/tooltips, or all windows if ImGuiConfigFlags_ViewportsNoTaskBarIcon is set)
VIEWPORT_FLAGS_NO_TASK_BAR_ICON = core.VIEWPORT_FLAGS_NO_TASK_BAR_ICON
#: Platform Window: Don't take focus when created.
VIEWPORT_FLAGS_NO_FOCUS_ON_APPEARING  = core.VIEWPORT_FLAGS_NO_FOCUS_ON_APPEARING 
#: Platform Window: Don't take focus when clicked on.
VIEWPORT_FLAGS_NO_FOCUS_ON_CLICK = core.VIEWPORT_FLAGS_NO_FOCUS_ON_CLICK
#: Platform Window: Make mouse pass through so we can drag this window while peaking behind it.
VIEWPORT_FLAGS_NO_INPUTS = core.VIEWPORT_FLAGS_NO_INPUTS
#: Platform Window: Renderer doesn't need to clear the framebuffer ahead (because we will fill it entirely).
VIEWPORT_FLAGS_NO_RENDERER_CLEAR = core.VIEWPORT_FLAGS_NO_RENDERER_CLEAR
#: Platform Window: Display on top (for tooltips only).
VIEWPORT_FLAGS_TOP_MOST = core.VIEWPORT_FLAGS_TOP_MOST
#: Platform Window: Window is minimized, can skip render. When minimized we tend to avoid using the viewport pos/size for clipping window or testing if they are contained in the viewport.
VIEWPORT_FLAGS_MINIMIZED = core.VIEWPORT_FLAGS_MINIMIZED
#: Platform Window: Avoid merging this window into another host window. This can only be set via ImGuiWindowClass viewport flags override (because we need to now ahead if we are going to create a viewport in the first place!).
VIEWPORT_FLAGS_NO_AUTO_MERGE = core.VIEWPORT_FLAGS_NO_AUTO_MERGE
#: Main viewport: can host multiple imgui windows (secondary viewports are associated to a single window).
VIEWPORT_FLAGS_CAN_HOST_OTHER_WINDOWS = core.VIEWPORT_FLAGS_CAN_HOST_OTHER_WINDOWS

def get_io() -> Any:
    """
    Get the current ImGui IO object.

    Example:     
        ```python
        io = imgui.get_io()
        print(io.framerate())
        ```
    """
    ...

def new_frame() -> Any:
    """
    Start a new ImGui frame. Call this at the beginning of your render loop.

    Example:     
        ```python
        imgui.new_frame()
        # ... your UI code ...
        imgui.render()
        ```
    """
    ...

def render() -> Any:
    """
    Ends the ImGui frame and renders the draw data.

    Example:     
        ```python
        imgui.new_frame()
        # ... your UI code ...
        imgui.render()
        ```
    """
    ...

def get_version() -> Any:
    """
    Returns the Dear ImGui version string.

    Example:     
        ```python
        print(imgui.get_version())
        ```
    """
    ...

def style_colors_classic(dst: Any = None) -> Any:
    """
    Set the ImGui style to the classic theme.

    Example:     
        ```python
        imgui.style_colors_classic()
        ```
    """
    ...

def show_style_editor(style: Any = None) -> Any:
    """
    Opens the ImGui style editor window.

    Example:     
        ```python
        imgui.show_style_editor()
        ```
    """
    ...

def show_font_selector(label: str) -> Any:
    """
    Show a font selector combo box.

    Example:     
        ```python
        imgui.show_font_selector("Choose Font")
        ```
    """
    ...

def get_draw_data() -> Any:
    """
    Get the current frame's draw data.

    Example:	     
        ```python
        draw_data = imgui.get_draw_data()
        ```
    """
    ...

def begin_child(label: Any, width: float = 0, height: float = 0, border: bool = False, flags: Any = 0) -> Any:
    """
    Begin a child window.

    Example:     
        ```python
        if imgui.begin_child("Child", 200, 100):
            imgui.text("Inside child")
        imgui.end_child()
        ```
    """
    ...

def end_child() -> Any:
    """
    End a child window started with begin_child.

    Example:     
        ```python
        imgui.begin_child("Child", 200, 100)
        imgui.text("Inside child")
        imgui.end_child()
        ```
    """
    ...

def get_content_region_available() -> Any:
    """
    Get the available space in the current content region.

    Example:     
        ```python
        avail = imgui.get_content_region_available()
        print(avail)
        ```
    """
    ...

def get_window_content_region_min() -> Any:
    """
    Get the minimum coordinates of the window content region.

    Example:     
        ```python
        min_pos = imgui.get_window_content_region_min()
        print(min_pos)
        ```
    """
    ...

def get_window_content_region_width() -> Any:
    """
    Get the width of the window content region.

    Example:     
        ```python
        width = imgui.get_window_content_region_width()
        print(width)
        ```
    """
    ...

def set_window_focus_labeled(label: str) -> Any:
    """
    Set keyboard focus to the specified window by label.

    Example:     
        ```python
        imgui.set_window_focus_labeled("MyWindow")
        ```
    """
    ...

def set_window_size_named(label: str, width: float, height: float, condition: int = ONCE) -> Any:
    """
    Set the size of a window by label.

    Example:     
        ```python
        imgui.set_window_size_named("MyWindow", 400, 300)
        ```
    """
    ...

def get_scroll_y() -> Any:
    """
    Get the current vertical scroll position.

    Example:     
        ```python
        scroll_y = imgui.get_scroll_y()
        print(scroll_y)
        ```
    """
    ...

def get_scroll_max_y() -> Any:
    """
    Get the maximum vertical scroll position.

    Example:     
        ```python
        max_scroll_y = imgui.get_scroll_max_y()
        print(max_scroll_y)
        ```
    """
    ...

def set_scroll_y(scroll_y: float) -> Any:
    """
    Set the vertical scroll position.

    Example:     
        ```python
        imgui.set_scroll_y(100.0)
        ```
    """
    ...

def set_next_window_collapsed(collapsed: bool, condition: int = ALWAYS) -> Any:
    """
    Set the next window's collapsed state.

    Example:     
        ```python
        imgui.set_next_window_collapsed(True)
        ```
    """
    ...

def set_next_window_focus() -> Any:
    """
    Set the next window to be focused.

    Example:     
        ```python
        imgui.set_next_window_focus()
        ```
    """
    ...

def get_window_draw_list() -> Any:
    """Get the draw list for the current window.
    
    Returns:
        ImDrawList: The draw list for the current window that can be used for custom drawing.
        
    Example:     
        ```python
        draw_list = imgui.get_window_draw_list()
        # Draw a line from (100,100) to (200,200) in red
        draw_list.add_line(100, 100, 200, 200, imgui.get_color_u32_rgba(1,0,0,1))
        ```
    """
    ...

def get_overlay_draw_list() -> Any:
    """Get the draw list for the overlay layer that renders on top of all windows.
    
    Returns:
        ImDrawList: The draw list for the overlay layer that can be used for custom drawing.
        
    Example:     
        ```python
        overlay = imgui.get_overlay_draw_list()
        # Draw a circle at (400,300) with radius 50 in blue
        overlay.add_circle(400, 300, 50, imgui.get_color_u32_rgba(0,0,1,1))
        ```
    """
    ...

def get_window_dpi_scale() -> Any:
    """Get the DPI scale factor for the current window.
    
    Returns:
        float: The DPI scale factor (1.0 = 100% scaling)
        
    Example:     
        ```python
        dpi_scale = imgui.get_window_dpi_scale()
        # Adjust sizes based on DPI
        button_width = 100 * dpi_scale
        imgui.button("DPI Scaled Button", width=button_width)
        ```
    """
    ...

def set_next_window_position(x: float, y: float, condition: int = ALWAYS, pivot_x: float = 0, pivot_y: float = 0) -> Any:
    """Set the position of the next window.
    
    Args:
        x (float): X position in screen coordinates
        y (float): Y position in screen coordinates
        condition (int): When to set the position (ALWAYS, ONCE, FIRST_USE_EVER, etc.)
        pivot_x (float): Pivot point X (0.0 = left, 0.5 = center, 1.0 = right)
        pivot_y (float): Pivot point Y (0.0 = top, 0.5 = center, 1.0 = bottom)
        
    Example:     
        ```python
        # Position window at center of screen
        imgui.set_next_window_position(400, 300, imgui.ALWAYS, 0.5, 0.5)
        imgui.begin("Centered Window")
        imgui.text("This window is centered")
        imgui.end()
        ```
    """
    ...

def set_next_window_size(width: float, height: float, condition: int = ALWAYS) -> Any:
    """Set the size of the next window.
    
    Args:
        width (float): Width in pixels
        height (float): Height in pixels
        condition (int): When to set the size (ALWAYS, ONCE, FIRST_USE_EVER, etc.)
        
    Example:     
        ```python
        # Create a 400x300 window
        imgui.set_next_window_size(400, 300)
        imgui.begin("Fixed Size Window")
        imgui.text("This window has a fixed size")
        imgui.end()
        ```
    """
    ...

def set_next_window_size_constraints(size_min: Any, size_max: Any, callback: Any = None, user_data: Any = None) -> Any:
    """Set minimum and maximum size constraints for the next window.
    
    Args:
        size_min (tuple): Minimum window size as (width, height) in pixels
        size_max (tuple): Maximum window size as (width, height) in pixels
        callback (callable): Optional callback function for dynamic constraints. Signature: callback(window, user_data) -> (min_size, max_size)
        user_data (Any): Optional user data passed to the callback function
        
    Example:     
        ```python
        # Static constraints
        imgui.set_next_window_size_constraints((200, 200), (400, 400))
        
        # Dynamic constraints using callback
        def size_callback(window, user_data):
            return ((200, 200), (400, 400))
            
        imgui.set_next_window_size_constraints((0, 0), (0, 0), size_callback)
        
        imgui.begin("Constrained Window")
        imgui.text("This window's size is constrained")
        imgui.end()
        ```
    """
    ...

def set_next_window_content_size(width: float, height: float) -> Any:
    """Set the content size for the next window, affecting its scrollable area.
    
    Args:
        width (float): Content width in pixels
        height (float): Content height in pixels
        
    Note:
        This sets the size of the scrollable content area, not the window itself.
        The window can still be resized, but the content area will maintain this size.
        
    Example:     
        ```python
        imgui.set_next_window_content_size(500, 1000)
        imgui.begin("Window with Large Content")
        for i in range(20):
            imgui.text(f"Line {i}")
        imgui.end()
        ```
    """
    ...

def set_window_position(x: float, y: float, condition: int = ALWAYS) -> Any:
    """Set the position of the current window in screen coordinates.
    
    Args:
        x (float): X position in screen coordinates
        y (float): Y position in screen coordinates
        condition (int): When to set the position:
            - ALWAYS: Set every frame
            - ONCE: Set only once
            - FIRST_USE_EVER: Set only on first use
            - APPEARING: Set when window appears
            
    Example:     
        ```python
        imgui.begin("Positioned Window")
        # Position window at screen center
        screen_width, screen_height = imgui.get_io().display_size
        imgui.set_window_position(screen_width/2, screen_height/2, imgui.ONCE)
        imgui.text("This window is positioned at screen center")
        imgui.end()
        ```
    """
    ...

def set_window_collapsed(collapsed: bool, condition: int = ALWAYS) -> Any:
    """Set the collapsed state of the current window.
    
    Args:
        collapsed (bool): True to collapse the window, False to expand it
        condition (int): When to set the state:
            - ALWAYS: Set every frame
            - ONCE: Set only once
            - FIRST_USE_EVER: Set only on first use
            - APPEARING: Set when window appears
            
    Example:     
        ```python
        imgui.begin("Collapsible Window")
        if imgui.button("Toggle"):
            # Toggle between collapsed and expanded states
            imgui.set_window_collapsed(not imgui.is_window_collapsed())
        imgui.text("Window content")
        imgui.end()
        ```
    """
    ...

def is_window_collapsed() -> Any:
    """Check if the current window is collapsed.
    
    Returns:
        bool: True if the window is collapsed, False if it's expanded
        
    Note:
        This function must be called between begin() and end() of a window.
        
    Example:     
        ```python
        imgui.begin("My Window")
        if imgui.is_window_collapsed():
            imgui.text("Window is collapsed")
        else:
            imgui.text("Window is expanded")
            imgui.text("More content...")
        imgui.end()
        ```
    """
    ...

def tree_node( text: str, flags: int = 0) -> Any:
    """Create a tree node that can be expanded/collapsed.
    
    Args:
        text (str): Label for the tree node
        flags (int): Additional flags for the tree node
        
    Returns:
        bool: True if the node is open/expanded
        
    Example:     
        ```python
        if imgui.tree_node("Settings"):
            imgui.text("Setting 1")
            imgui.text("Setting 2")
            imgui.tree_pop()
        ```
    """
    ...
def tree_pop() -> Any:
    """Close the current tree node.
    
    Example:     
        ```python
        if imgui.tree_node("Parent"):
            if imgui.tree_node("Child"):
                imgui.text("Child content")
                imgui.tree_pop()  # Close child
            imgui.tree_pop()  # Close parent
        ```
    """
    ...
def collapsing_header( text: str,visible: Any = None, flags: int = 0) -> Any:
    """Create a collapsible header section.
    
    Args:
        text (str): Label for the header
        visible (bool): Optional reference to store the open/closed state
        flags (int): Additional flags for the header
        
    Returns:
        bool: True if the header is open
        
    Example:     
        ```python
        if imgui.collapsing_header("Advanced Settings"):
            imgui.text("These are advanced settings")
            imgui.checkbox("Enable Feature", True)
        ```
    """
    ...
def set_next_item_open( is_open: bool, condition: int = 0) -> Any:
    """Set the open state of the next tree node or collapsing header.
    
    Args:
        is_open (bool): True to open the item, False to close it
        condition (int): When to set the state:
            - ALWAYS: Set every frame
            - ONCE: Set only once
            - FIRST_USE_EVER: Set only on first use
            - APPEARING: Set when item appears
            
    Note:
        This function must be called before the tree node or collapsing header
        that it affects. It works with tree_node() and collapsing_header().
        
    Example:     
        ```python
        # Force a tree node to be open
        imgui.set_next_item_open(True, imgui.ONCE)
        if imgui.tree_node("Always Open Node"):
            imgui.text("This node starts open")
            imgui.tree_pop()
            
        # Force a collapsing header to be closed
        imgui.set_next_item_open(False, imgui.ONCE)
        if imgui.collapsing_header("Always Closed Header"):
            imgui.text("This content is hidden")
        ```
    """
    ...
def selectable( label: str,selected: Any = False, flags: int = 0,width: int = 0,height: int = 0) -> Any:
    """Create a selectable item that can be clicked and highlighted.
    
    Args:
        label (str): Text label for the selectable item
        selected (bool): Whether the item is currently selected
        flags (int): Additional flags for the selectable:
            - SELECTABLE_NONE: Default behavior
            - SELECTABLE_DONT_CLOSE_POPUPS: Don't close parent popup when selected
            - SELECTABLE_SPAN_ALL_COLUMNS: Span all columns
            - SELECTABLE_ALLOW_DOUBLE_CLICK: Allow double-click selection
            - SELECTABLE_DISABLED: Disable the selectable
        width (int): Width of the selectable in pixels (0 = auto)
        height (int): Height of the selectable in pixels (0 = auto)
        
    Returns:
        bool: True if the item was clicked
        
    Note:
        The selectable can be used in various contexts:
        - As a list item
        - In a popup menu
        - As a button alternative
        - In a multi-select list
        
    Example:     
        ```python
        # Basic selectable
        selected = False
        if imgui.selectable("Click me!", selected):
            selected = not selected
            
        # Selectable with custom size
        if imgui.selectable("Large selectable", False, width=200, height=50):
            print("Large selectable clicked")
            
        # Selectable in a list
        items = ["Item 1", "Item 2", "Item 3"]
        selected_item = 0
        for i, item in enumerate(items):
            if imgui.selectable(item, selected_item == i):
                selected_item = i
                
        # Disabled selectable
        imgui.selectable("Disabled", False, flags=imgui.SELECTABLE_DISABLED)
        ```
    """
    ...
def listbox(label: str, current: int, items: Any, height_in_items: int = -1) -> Any:
    """Create a list box with selectable items.
    
    Args:
        label (str): Label for the list box
        current (int): Index of currently selected item
        items (list): List of item strings to display
        height_in_items (int): Height in number of items (-1 = fit to content)
        
    Returns:
        tuple: (bool, int) - (whether selection changed, new selection index)
        
    Example:     
        ```python
        items = ["Apple", "Banana", "Cherry", "Date"]
        changed, selected = imgui.listbox("Select Fruit", 0, items)
        if changed:
            print(f"Selected: {items[selected]}")
        ```
    """
    ...

def begin_list_box(label: str, width: int = 0, height: int = 0) -> Any:
    """Begin a list box with custom rendering.
    
    Args:
        label (str): Label for the list box
        width (int): Width in pixels (0 = auto)
        height (int): Height in pixels (0 = auto)
        
    Returns:
        bool: True if the list box is open
        
    Example:     
        ```python
        if imgui.begin_list_box("Custom List", 200, 100):
            for i in range(5):
                if imgui.selectable(f"Item {i}"):
                    print(f"Selected item {i}")
            imgui.end_list_box()
        ```
    """
    ...

def end_list_box() -> Any:
    """End a list box started with begin_list_box.
    
    Example:     
        ```python
        if imgui.begin_list_box("My List"):
            # Add items here
            imgui.end_list_box()
        ```
    """
    ...

def begin_tooltip() -> Any:
    """Begin a tooltip window.
    
    Returns:
        bool: True if the tooltip is open
        
    Example:     
        ```python
        imgui.text("Hover me")
        if imgui.is_item_hovered():
            imgui.begin_tooltip()
            imgui.text("This is a tooltip")
            imgui.text("It can have multiple lines")
            imgui.end_tooltip()
        ```
    """
    ...

def end_tooltip() -> Any:
    """End a tooltip window.
    
    Example:     
        ```python
        if imgui.is_item_hovered():
            imgui.begin_tooltip()
            imgui.text("Tooltip content")
            imgui.end_tooltip()
        ```
    """
    ...

def end_main_menu_bar() -> Any:
    """End the main menu bar.
    
    Example:     
        ```python
        if imgui.begin_main_menu_bar():
            if imgui.begin_menu("File"):
                if imgui.menu_item("Exit"):
                    print("Exit selected")
                imgui.end_menu()
            imgui.end_main_menu_bar()
        ```
    """
    ...

def end_menu_bar() -> Any:
    """End a window menu bar.
    
    Example:     
        ```python
        if imgui.begin_menu_bar():
            if imgui.begin_menu("Options"):
                imgui.menu_item("Settings")
                imgui.end_menu()
            imgui.end_menu_bar()
        ```
    """
    ...

def end_menu() -> Any:
    """End a menu.
    
    Example:     
        ```python
        if imgui.begin_menu("File"):
            imgui.menu_item("Open")
            imgui.menu_item("Save")
            imgui.end_menu()
        ```
    """
    ...

def open_popup(label: str, flags: Any = 0) -> Any:
    """Open a popup window.
    
    Args:
        label (str): Unique identifier for the popup
        flags (int): Additional flags for the popup
        
    Example:     
        ```python
        if imgui.button("Open Popup"):
            imgui.open_popup("MyPopup")
            
        if imgui.begin_popup("MyPopup"):
            imgui.text("Popup content")
            if imgui.button("Close"):
                imgui.close_current_popup()
            imgui.end_popup()
        ```
    """
    ...

def open_popup_on_item_click(label: str = None, popup_flags: Any = 1) -> Any:
    """Open a popup when the last item is clicked.
    
    Args:
        label (str): Unique identifier for the popup
        popup_flags (int): Additional flags for the popup
        
    Example:     
        ```python
        imgui.text("Right-click me")
        imgui.open_popup_on_item_click("ContextMenu")
        
        if imgui.begin_popup("ContextMenu"):
            if imgui.menu_item("Option 1"):
                print("Option 1 selected")
            if imgui.menu_item("Option 2"):
                print("Option 2 selected")
            imgui.end_popup()
        ```
    """
    ...

def begin_popup_modal(title: str, visible: Any = None, flags: Any = 0) -> Any:
    """Begin a modal popup window that blocks interaction with other windows.
    
    Args:
        title (str): Title of the popup window
        visible (bool): Optional reference to store the open/closed state
        flags (int): Additional flags for the popup window
        
    Returns:
        bool: True if the popup is open
        
    Example:     
        ```python
        if imgui.begin_popup_modal("Confirm Action"):
            imgui.text("Are you sure you want to proceed?")
            if imgui.button("Yes"):
                # Handle confirmation
                imgui.close_current_popup()
            imgui.same_line()
            if imgui.button("No"):
                imgui.close_current_popup()
            imgui.end_popup()
        ```
    """
    ...
def begin_popup_context_item(label: str = None, mouse_button: Any = 1) -> Any:
    """Begin a popup that appears when right-clicking on the last item.
    
    Args:
        label (str): Optional unique identifier for the popup
        mouse_button (int): Mouse button that triggers the popup (0=left, 1=right, 2=middle)
        
    Returns:
        bool: True if the popup is open
        
    Example:     
        ```python
        imgui.text("Right-click this text")
        if imgui.begin_popup_context_item("ItemContext"):
            if imgui.menu_item("Copy"):
                print("Copy selected")
            if imgui.menu_item("Paste"):
                print("Paste selected")
            imgui.end_popup()
        ```
    """
    ...

def begin_popup_context_window(label: str = None, popup_flags: Any = 1, also_over_items: bool = True) -> Any:
    """Begin a popup that appears when right-clicking anywhere in the current window.
    
    Args:
        label (str): Optional unique identifier for the popup
        popup_flags (int): Additional flags for the popup
        also_over_items (bool): Whether the popup should appear when clicking over items
        
    Returns:
        bool: True if the popup is open
        
    Example:     
        ```python
        if imgui.begin_popup_context_window("WindowContext"):
            if imgui.menu_item("Window Option 1"):
                print("Option 1 selected")
            if imgui.menu_item("Window Option 2"):
                print("Option 2 selected")
            imgui.end_popup()
        ```
    """
    ...

def begin_popup_context_void(label: str = None, popup_flags: Any = 1) -> Any:
    """Begin a popup that appears when right-clicking in empty space.
    
    Args:
        label (str): Optional unique identifier for the popup
        popup_flags (int): Additional flags for the popup
        
    Returns:
        bool: True if the popup is open
        
    Example:     
        ```python
        if imgui.begin_popup_context_void("VoidContext"):
            if imgui.menu_item("Create New"):
                print("Create new selected")
            if imgui.menu_item("Refresh"):
                print("Refresh selected")
            imgui.end_popup()
        ```
    """
    ...

def end_popup() -> Any:
    """End a popup window started with any of the popup begin functions.
    
    Example:     
        ```python
        if imgui.begin_popup_context_item("MyPopup"):
            imgui.text("Popup content")
            if imgui.button("Close"):
                imgui.close_current_popup()
            imgui.end_popup()
        ```
    """
    ...
def begin_table(label: str, column: int, flags: Any = 0, outer_size_width: float = 0.0, outer_size_height: float = 0.0, inner_width: float = 0.0) -> Any:
    """Begin a table with multiple columns.
    
    Args:
        label (str): Unique identifier for the table
        column (int): Number of columns
        flags (int): Additional flags for the table
        outer_size_width (float): Width of the outer container
        outer_size_height (float): Height of the outer container
        inner_width (float): Width of the inner content
        
    Returns:
        bool: True if the table is open
        
    Example:     
        ```python
        if imgui.begin_table("MyTable", 3):
            imgui.table_setup_column("Name")
            imgui.table_setup_column("Age")
            imgui.table_setup_column("Email")
            imgui.table_headers_row()
            
            # Add rows
            imgui.table_next_row()
            imgui.table_next_column()
            imgui.text("John")
            imgui.table_next_column()
            imgui.text("30")
            imgui.table_next_column()
            imgui.text("john@example.com")
            
            imgui.end_table()
        ```
    """
    ...
def end_table() -> Any:
    """End a table started with begin_table.
    
    Example:     
        ```python
        if imgui.begin_table("MyTable", 3):
            imgui.table_setup_column("Name")
            imgui.table_setup_column("Age")
            imgui.table_setup_column("Email")
            imgui.table_headers_row()
            
            # Add rows
            imgui.table_next_row()
            imgui.table_next_column()
            imgui.text("John")
            imgui.table_next_column()
            imgui.text("30")
            imgui.table_next_column()
            imgui.text("john@example.com")
            
            imgui.end_table()
        ```
    """
    ...

def table_next_column() -> Any:
    """Move to the next column in the current table row.
    
    Example:     
        ```python
        if imgui.begin_table("MyTable", 3):
            imgui.table_next_row()
            imgui.table_next_column()
            imgui.text("Column 1")
            imgui.table_next_column()
            imgui.text("Column 2")
            imgui.table_next_column()
            imgui.text("Column 3")
            imgui.end_table()
        ```
    """
    ...

def table_setup_column(label: str, flags: Any = 0, init_width_or_weight: float = 0.0, user_id: int = 0) -> Any:
    """Set up a column in the table.
    
    Args:
        label (str): Column header label
        flags (int): Column flags:
            - TABLE_COLUMN_NONE: Default
            - TABLE_COLUMN_DEFAULT_HIDE: Hide by default
            - TABLE_COLUMN_DEFAULT_SORT: Sort by default
            - TABLE_COLUMN_WIDTH_STRETCH: Stretch to fill available space
            - TABLE_COLUMN_WIDTH_FIXED: Fixed width
            - TABLE_COLUMN_NO_RESIZE: Cannot be resized
            - TABLE_COLUMN_NO_REORDER: Cannot be reordered
            - TABLE_COLUMN_NO_HIDE: Cannot be hidden
            - TABLE_COLUMN_NO_CLIP: Do not clip content
            - TABLE_COLUMN_NO_SORT: Cannot be sorted
            - TABLE_COLUMN_NO_HEADER: No header
        init_width_or_weight (float): Initial width or weight of the column
        user_id (int): Optional user ID for the column
        
    Example:     
        ```python
        if imgui.begin_table("MyTable", 3):
            # Fixed width column
            imgui.table_setup_column("Name", imgui.TABLE_COLUMN_WIDTH_FIXED, 100)
            # Stretch column
            imgui.table_setup_column("Description", imgui.TABLE_COLUMN_WIDTH_STRETCH)
            # Non-resizable column
            imgui.table_setup_column("ID", imgui.TABLE_COLUMN_NO_RESIZE, 50)
            imgui.end_table()
        ```
    """
    ...

def table_setup_scroll_freez(cols: int, rows: int) -> Any:
    """Set up frozen columns and rows in the table.
    
    Args:
        cols (int): Number of columns to freeze from the left
        rows (int): Number of rows to freeze from the top
        
    Example:     
        ```python
        if imgui.begin_table("MyTable", 5):
            # Freeze first column and first row
            imgui.table_setup_scroll_freez(1, 1)
            # Setup columns...
            imgui.end_table()
        ```
    """
    ...

def table_header(label: str) -> Any:
    """Set the header text for the current column.
    
    Args:
        label (str): Header text
        
    Example:     
        ```python
        if imgui.begin_table("MyTable", 3):
            imgui.table_setup_column("Name")
            imgui.table_header("Name")
            imgui.table_next_column()
            imgui.table_setup_column("Age")
            imgui.table_header("Age")
            imgui.end_table()
        ```
    """
    ...

def table_get_column_count() -> Any:
    """Get the number of columns in the current table.
    
    Returns:
        int: Number of columns
        
    Example:     
        ```python
        if imgui.begin_table("MyTable", 3):
            col_count = imgui.table_get_column_count()
            imgui.text(f"Table has {col_count} columns")
            imgui.end_table()
        ```
    """
    ...

def table_get_row_index() -> Any:
    """Get the index of the current row in the table.
    
    Returns:
        int: Current row index
        
    Example:     
        ```python
        if imgui.begin_table("MyTable", 3):
            for i in range(5):
                imgui.table_next_row()
                row_idx = imgui.table_get_row_index()
                imgui.text(f"Row {row_idx}")
            imgui.end_table()
        ```
    """
    ...

def table_get_column_flags(column_n: int = -1) -> Any:
    """Get the flags for a specific column in the table.
    
    Args:
        column_n (int): Column index (-1 for current column)
        
    Returns:
        int: Column flags
        
    Example:     
        ```python
        if imgui.begin_table("MyTable", 3):
            imgui.table_setup_column("Name", imgui.TABLE_COLUMN_WIDTH_FIXED)
            flags = imgui.table_get_column_flags(0)
            if flags & imgui.TABLE_COLUMN_WIDTH_FIXED:
                imgui.text("First column is fixed width")
            imgui.end_table()
        ```
    """
    ...
def text(text: str) -> Any:
    """Display a text label.
    
    Args:
        text (str): Text to display
        
    Example:     
        ```python
        imgui.text("Hello, World!")
        imgui.text(f"Current value: {some_value}")
        ```
    """
    ...
def text_disabled(text: str) -> Any:
    """Display text in a disabled (grayed out) style.
    
    Args:
        text (str): Text to display
        
    Example:     
        ```python
        imgui.text_disabled("This text appears grayed out")
        imgui.text("This text is normal")
        ```
    """
    ...

def label_text(label: str, text: str) -> Any:
    """Display a label followed by text on the same line.
    
    Args:
        label (str): Label text
        text (str): Value text
        
    Example:     
        ```python
        imgui.label_text("Name", "John Doe")
        imgui.label_text("Age", "30")
        imgui.label_text("Status", "Active")
        ```
    """
    ...

def bullet() -> Any:
    """Display a bullet point.
    
    Example:     
        ```python
        imgui.bullet()
        imgui.text("First item")
        imgui.bullet()
        imgui.text("Second item")
        ```
    """
    ...

def bullet_text(text: str) -> Any:
    """Display a bullet point with text in one call.
    
    Args:
        text (str): Text to display after the bullet
        
    Example:     
        ```python
        imgui.bullet_text("First item")
        imgui.bullet_text("Second item")
        imgui.bullet_text("Third item")
        ```
    """
    ...

def small_button(label: str) -> Any:
    """Create a small-sized button.
    
    Args:
        label (str): Button text
        
    Returns:
        bool: True if the button was clicked
        
    Example:     
        ```python
        if imgui.small_button("Click me"):
            print("Small button clicked")
        ```
    """
    ...

def invisible_button(identifier: str, width: float, height: float, flags: Any = 0) -> Any:
    """Create an invisible button that can be clicked.
    
    Args:
        identifier (str): Unique identifier for the button
        width (float): Width of the button
        height (float): Height of the button
        flags (int): Additional flags for the button
        
    Returns:
        bool: True if the button was clicked
        
    Example:     
        ```python
        if imgui.invisible_button("invisible_btn", 100, 50):
            print("Invisible area clicked")
        ```
    """
    ...

def image_button(texture_id, width: float, height: float, uv0: Any = (0,0), uv1: Any = (1,1), tint_color: Any = (1,1,1,1), border_color: Any = (0,0,0,0), frame_padding: int = -1) -> Any:
    """Create a button with an image.
    
    Args:
        texture_id: OpenGL texture ID
        width (float): Width of the button
        height (float): Height of the button
        uv0 (tuple): UV coordinates for top-left corner (0,0 to 1,1)
        uv1 (tuple): UV coordinates for bottom-right corner (0,0 to 1,1)
        tint_color (tuple): RGBA color to tint the image (1,1,1,1 = no tint)
        border_color (tuple): RGBA color for the border (0,0,0,0 = no border)
        frame_padding (int): Padding around the image (-1 = use default)
        
    Returns:
        bool: True if the button was clicked
        
    Example:     
        ```python
        if imgui.image_button(texture_id, 100, 100, 
                            uv0=(0,0), uv1=(1,1),
                            tint_color=(1,1,1,1),
                            border_color=(1,0,0,1)):
            print("Image button clicked")
        ```
    """
    ...

def image(texture_id, width: float, height: float, uv0: Any = (0,0), uv1: Any = (1,1), tint_color: Any = (1,1,1,1), border_color: Any = (0,0,0,0)) -> Any:
    """Display an image.
    
    Args:
        texture_id: OpenGL texture ID
        width (float): Width of the image
        height (float): Height of the image
        uv0 (tuple): UV coordinates for top-left corner (0,0 to 1,1)
        uv1 (tuple): UV coordinates for bottom-right corner (0,0 to 1,1)
        tint_color (tuple): RGBA color to tint the image (1,1,1,1 = no tint)
        border_color (tuple): RGBA color for the border (0,0,0,0 = no border)
        
    Example:     
        ```python
        imgui.image(texture_id, 200, 200,
                   uv0=(0,0), uv1=(1,1),
                   tint_color=(1,1,1,1),
                   border_color=(0,0,0,1))
        ```
    """
    ...
def checkbox( label: str, state: bool) -> Any:
    """Create a checkbox that can be toggled.
    
    Args:
        label (str): Text label for the checkbox
        state (bool): Current state of the checkbox
        
    Returns:
        tuple: (bool, bool) - (new state, whether state changed)
        
    Example:     
        ```python
        enabled = False
        changed, enabled = imgui.checkbox("Enable Feature", enabled)
        if changed:
            print(f"Checkbox state changed to: {enabled}")
        ```
    """
    ...
def radio_button(label: str, active: bool) -> Any:
    """Create a radio button that can be selected.
    
    Args:
        label (str): Label for the radio button
        active (bool): Whether this radio button is currently selected
        
    Returns:
        bool: True if the radio button was clicked
        
    Note:
        Radio buttons are typically used in groups where only one can be selected.
        To create a group of radio buttons, use a shared variable for the active state.
        
    Example:     
        ```python
        # Single radio button
        if imgui.radio_button("Option 1", selected_option == 0):
            selected_option = 0
            
        # Group of radio buttons
        if imgui.radio_button("Option 1", selected_option == 0):
            selected_option = 0
        if imgui.radio_button("Option 2", selected_option == 1):
            selected_option = 1
        if imgui.radio_button("Option 3", selected_option == 2):
            selected_option = 2
        ```
    """
    ...

def combo(label: str, current: int, items: Any, height_in_items: int = -1) -> Any:
    """Create a combo box (dropdown) with selectable items.
    
    Args:
        label (str): Label for the combo box
        current (int): Index of currently selected item
        items (list): List of item strings to display
        height_in_items (int): Height in number of items (-1 = fit to content)
        
    Returns:
        tuple: (bool, int) - (whether selection changed, new selection index)
        
    Note:
        The combo box displays the currently selected item and shows a dropdown
        list of all items when clicked.
        
    Example:     
        ```python
        items = ["Option 1", "Option 2", "Option 3", "Option 4"]
        changed, selected = imgui.combo("Select Option", 0, items)
        if changed:
            print(f"Selected: {items[selected]}")
            
        # With custom height
        changed, selected = imgui.combo("Select Option", 0, items, height_in_items=3)
        ```
    """
    ...
def color_edit4( label: str, r: float, g: float, b: float, a: float, flags: Any = 0) -> Any:
    """Create a color picker for RGBA values.
    
    Args:
        label (str): Label for the color picker
        r (float): Red component (0.0 to 1.0)
        g (float): Green component (0.0 to 1.0)
        b (float): Blue component (0.0 to 1.0)
        a (float): Alpha component (0.0 to 1.0)
        flags (int): Additional flags for the color picker
        
    Returns:
        tuple: (bool, float, float, float, float) - (whether changed, new r, new g, new b, new a)
        
    Example:     
        ```python
        color = [1.0, 0.0, 0.0, 1.0]  # Red
        changed, *color = imgui.color_edit4("Pick Color", *color)
        if changed:
            print(f"Color changed to: {color}")
        ```
    """
    ...
def drag_float2(label: str, value0: float, value1: float, change_speed: float = 1.0, min_value: float = 0.0, max_value: float = 0.0, format: str = "%.3f", flags: Any = 0) -> Any:
    """Create a drag control for a 2D float vector.
    
    Args:
        label (str): Label for the control
        value0 (float): First component (x)
        value1 (float): Second component (y)
        change_speed (float): Speed of value change when dragging
        min_value (float): Minimum allowed value (0.0 = no limit)
        max_value (float): Maximum allowed value (0.0 = no limit)
        format (str): Format string for display
        flags (int): Additional flags for the control
        
    Returns:
        tuple: (bool, float, float) - (whether changed, new x, new y)
        
    Example:     
        ```python
        position = [0.0, 0.0]
        changed, position[0], position[1] = imgui.drag_float2(
            "Position", position[0], position[1],
            change_speed=0.1,
            min_value=-10.0,
            max_value=10.0
        )
        ```
    """
    ...

def drag_float3(label: str, value0: float, value1: float, value2: float, change_speed: float = 1.0, min_value: float = 0.0, max_value: float = 0.0, format: str = "%.3f", flags: Any = 0) -> Any:
    """Create a drag control for a 3D float vector.
    
    Args:
        label (str): Label for the control
        value0 (float): First component (x)
        value1 (float): Second component (y)
        value2 (float): Third component (z)
        change_speed (float): Speed of value change when dragging
        min_value (float): Minimum allowed value (0.0 = no limit)
        max_value (float): Maximum allowed value (0.0 = no limit)
        format (str): Format string for display
        flags (int): Additional flags for the control
        
    Returns:
        tuple: (bool, float, float, float) - (whether changed, new x, new y, new z)
        
    Example:     
        ```python
        position = [0.0, 0.0, 0.0]
        changed, position[0], position[1], position[2] = imgui.drag_float3(
            "Position", position[0], position[1], position[2],
            change_speed=0.1,
            min_value=-10.0,
            max_value=10.0
        )
        ```
    """
    ...

def drag_float4(label: str, value0: float, value1: float, value2: float, value3: float, change_speed: float = 1.0, min_value: float = 0.0, max_value: float = 0.0, format: str = "%.3f", flags: Any = 0) -> Any:
    """Create a drag control for a 4D float vector.
    
    Args:
        label (str): Label for the control
        value0 (float): First component (x)
        value1 (float): Second component (y)
        value2 (float): Third component (z)
        value3 (float): Fourth component (w)
        change_speed (float): Speed of value change when dragging
        min_value (float): Minimum allowed value (0.0 = no limit)
        max_value (float): Maximum allowed value (0.0 = no limit)
        format (str): Format string for display
        flags (int): Additional flags for the control
        
    Returns:
        tuple: (bool, float, float, float, float) - (whether changed, new x, new y, new z, new w)
        
    Example:     
        ```python
        color = [1.0, 0.0, 0.0, 1.0]  # RGBA
        changed, *color = imgui.drag_float4(
            "Color", *color,
            change_speed=0.01,
            min_value=0.0,
            max_value=1.0
        )
        ```
    """
    ...

def drag_float_range2(label: str, current_min: float, current_max: float, speed: float = 1.0, min_value: float = 0.0, max_value: float = 0.0, format: str = "%.3f", format_max: str = None, flags: Any = 0) -> Any:
    """Create a drag control for a float range (min-max).
    
    Args:
        label (str): Label for the control
        current_min (float): Current minimum value
        current_max (float): Current maximum value
        speed (float): Speed of value change when dragging
        min_value (float): Minimum allowed value (0.0 = no limit)
        max_value (float): Maximum allowed value (0.0 = no limit)
        format (str): Format string for minimum value
        format_max (str): Format string for maximum value (None = use format)
        flags (int): Additional flags for the control
        
    Returns:
        tuple: (bool, float, float) - (whether changed, new min, new max)
        
    Example:     
        ```python
        range_min, range_max = 0.0, 1.0
        changed, range_min, range_max = imgui.drag_float_range2(
            "Range", range_min, range_max,
            speed=0.01,
            min_value=0.0,
            max_value=10.0
        )
        ```
    """
    ...

def drag_int(label: str, value: int, change_speed: float = 1.0, min_value: int = 0, max_value: int = 0, format: str = "%d", flags: Any = 0) -> Any:
    """Create a drag control for an integer value.
    
    Args:
        label (str): Label for the control
        value (int): Current value
        change_speed (float): Speed of value change when dragging
        min_value (int): Minimum allowed value (0 = no limit)
        max_value (int): Maximum allowed value (0 = no limit)
        format (str): Format string for display
        flags (int): Additional flags for the control
        
    Returns:
        tuple: (bool, int) - (whether changed, new value)
        
    Example:     
        ```python
        count = 0
        changed, count = imgui.drag_int(
            "Count", count,
            change_speed=1.0,
            min_value=0,
            max_value=100
        )
        ```
    """
    ...

def drag_int2(label: str, value0: int, value1: int, change_speed: float = 1.0, min_value: int = 0, max_value: int = 0, format: str = "%d", flags: Any = 0) -> Any:
    """Create a drag control for a 2D integer vector.
    
    Args:
        label (str): Label for the control
        value0 (int): First component (x)
        value1 (int): Second component (y)
        change_speed (float): Speed of value change when dragging
        min_value (int): Minimum allowed value (0 = no limit)
        max_value (int): Maximum allowed value (0 = no limit)
        format (str): Format string for display
        flags (int): Additional flags for the control
        
    Returns:
        tuple: (bool, int, int) - (whether changed, new x, new y)
        
    Example:     
        ```python
        position = [0, 0]
        changed, position[0], position[1] = imgui.drag_int2(
            "Position", position[0], position[1],
            change_speed=1.0,
            min_value=-100,
            max_value=100
        )
        ```
    """
    ...

def drag_int3(label: str, value0: int, value1: int, value2: int, change_speed: float = 1.0, min_value: int = 0, max_value: int = 0, format: str = "%d", flags: Any = 0) -> Any:
    """Create a drag control for a 3D integer vector.
    
    Args:
        label (str): Label for the control
        value0 (int): First component (x)
        value1 (int): Second component (y)
        value2 (int): Third component (z)
        change_speed (float): Speed of value change when dragging
        min_value (int): Minimum allowed value (0 = no limit)
        max_value (int): Maximum allowed value (0 = no limit)
        format (str): Format string for display
        flags (int): Additional flags for the control
        
    Returns:
        tuple: (bool, int, int, int) - (whether changed, new x, new y, new z)
        
    Example:     
        ```python
        position = [0, 0, 0]
        changed, position[0], position[1], position[2] = imgui.drag_int3(
            "Position", position[0], position[1], position[2],
            change_speed=1.0,
            min_value=-100,
            max_value=100
        )
        ```
    """
    ...

def drag_int4(label: str, value0: int, value1: int, value2: int, value3: int, change_speed: float = 1.0, min_value: int = 0, max_value: int = 0, format: str = "%d", flags: Any = 0) -> Any:
    """Create a drag control for a 4D integer vector.
    
    Args:
        label (str): Label for the control
        value0 (int): First component (x)
        value1 (int): Second component (y)
        value2 (int): Third component (z)
        value3 (int): Fourth component (w)
        change_speed (float): Speed of value change when dragging
        min_value (int): Minimum allowed value (0 = no limit)
        max_value (int): Maximum allowed value (0 = no limit)
        format (str): Format string for display
        flags (int): Additional flags for the control
        
    Returns:
        tuple: (bool, int, int, int, int) - (whether changed, new x, new y, new z, new w)
        
    Example:     
        ```python
        values = [0, 0, 0, 0]
        changed, *values = imgui.drag_int4(
            "Values", *values,
            change_speed=1.0,
            min_value=-100,
            max_value=100
        )
        ```
    """
    ...

def drag_int_range2(label: str, current_min: int, current_max: int, speed: float = 1.0, min_value: int = 0, max_value: int = 0, format: str = "%d", format_max: str = None, flags: Any = 0) -> Any:
    """Create a drag control for an integer range (min-max).
    
    Args:
        label (str): Label for the control
        current_min (int): Current minimum value
        current_max (int): Current maximum value
        speed (float): Speed of value change when dragging
        min_value (int): Minimum allowed value (0 = no limit)
        max_value (int): Maximum allowed value (0 = no limit)
        format (str): Format string for minimum value
        format_max (str): Format string for maximum value (None = use format)
        flags (int): Additional flags for the control
        
    Returns:
        tuple: (bool, int, int) - (whether changed, new min, new max)
        
    Example:     
        ```python
        range_min, range_max = 0, 100
        changed, range_min, range_max = imgui.drag_int_range2(
            "Range", range_min, range_max,
            speed=1.0,
            min_value=0,
            max_value=1000
        )
        ```
    """
    ...

def drag_scalar(label: str, data_type: Any, data: Any, change_speed: float, min_value: Any = None, max_value: Any = None, format: str = None, flags: Any = 0) -> Any:
    """Create a drag control for a scalar value of any type.
    
    Args:
        label (str): Label for the control
        data_type: Type of the data (e.g., FLOAT, INT)
        data: Current value
        change_speed (float): Speed of value change when dragging
        min_value: Minimum allowed value
        max_value: Maximum allowed value
        format (str): Format string for display
        flags (int): Additional flags for the control
        
    Returns:
        tuple: (bool, Any) - (whether changed, new value)
        
    Example:     
        ```python
        value = 0.0
        changed, value = imgui.drag_scalar(
            "Value", imgui.FLOAT, value,
            change_speed=0.1,
            min_value=0.0,
            max_value=1.0,
            format="%.3f"
        )
        ```
    """
    ...
def input_text( label: str, value: str, buffer_length: int, flags: Any = 0, callback: Any = None,user_data: Any = None) -> Any:
    """Create a text input field.
    
    Args:
        label (str): Label for the input field
        value (str): Current text value
        buffer_length (int): Maximum length of the text buffer
        flags (int): Additional flags for the input field
        callback (callable): Optional callback function
        user_data (Any): Optional user data passed to callback
        
    Returns:
        tuple: (bool, str) - (whether value changed, new value)
        
    Example:     
        ```python
        text = "Initial text"
        changed, text = imgui.input_text("Enter text", text, 256)
        if changed:
            print(f"Text changed to: {text}")
        ```
    """
    ...
def input_text_multiline( label: str, value: str, buffer_length: int, width: float = 0, height: float = 0, flags: Any = 0, callback: Any = None,user_data: Any = None) -> Any:
    """Creates a multi-line text input field.
    
    Args:
        label: Label displayed next to the input field
        value: Current text value
        buffer_length: Maximum length of the text buffer
        width: Width of the input field (0 = auto)
        height: Height of the input field (0 = auto)
        flags: Input flags (e.g. ImGuiInputTextFlags_EnterReturnsTrue)
        callback: Optional callback function for text changes
        user_data: Optional user data passed to callback
        
    Returns:
        Tuple of (bool, str) - (was_edited, new_value)
        
    Example:     
        ```python
        text = "Hello\nWorld"
        changed, text = imgui.input_text_multiline("Multi-line", text, 256, width=200, height=100)
        if changed:
            print(f"Text changed to: {text}")
        ```
    """
    ...
def input_text_with_hint( label: str, hint: str, value: str, buffer_length: int, flags: Any = 0, callback: Any = None,user_data: Any = None) -> Any:
    """Creates a text input field with a hint text shown when empty.
    
    Args:
        label: Label displayed next to the input field
        hint: Hint text shown when input is empty
        value: Current text value
        buffer_length: Maximum length of the text buffer
        flags: Input flags (e.g. ImGuiInputTextFlags_EnterReturnsTrue)
        callback: Optional callback function for text changes
        user_data: Optional user data passed to callback
        
    Returns:
        Tuple of (bool, str) - (was_edited, new_value)
        
    Example:     
        ```python
        text = ""
        changed, text = imgui.input_text_with_hint("Search", "Type to search...", text, 256)
        if changed:
            print(f"Search text: {text}")
        ```
    """
    ...
def input_float( label: str, value: float, step: float = 0.0, step_fast: float = 0.0, format: str = "%.3f", flags: Any = 0) -> Any:
    """Creates a single float input field with optional step controls.
    
    Args:
        label: Label displayed next to the input field
        value: Current float value
        step: Step increment for arrow buttons
        step_fast: Step increment when holding Ctrl
        format: Format string for display
        flags: Input flags
        
    Returns:
        Tuple of (bool, float) - (was_edited, new_value)
        
    Example:	     
        ```python
        value = 42.0
        changed, value = imgui.input_float("Float", value, step=0.1, step_fast=1.0)
        if changed:
            print(f"New value: {value}")
        ```
    """
    ...
def input_float2( label: str, value0: float, value1: float, format: str = "%.3f", flags: Any = 0) -> Any:
    """Creates a 2-component float input field.
    
    Args:
        label: Label displayed next to the input field
        value0: First float value
        value1: Second float value
        format: Format string for display
        flags: Input flags
        
    Returns:
        Tuple of (bool, float, float) - (was_edited, new_value0, new_value1)
        
    Example:     
        ```python
        x, y = 1.0, 2.0
        changed, x, y = imgui.input_float2("Position", x, y)
        if changed:
            print(f"New position: ({x}, {y})")
        ```
    """
    ...
def input_float3( label: str, value0: float, value1: float, value2: float, format: str = "%.3f", flags: Any = 0) -> Any:
    """Creates a 3-component float input field.
    
    Args:
        label: Label displayed next to the input field
        value0: First float value
        value1: Second float value
        value2: Third float value
        format: Format string for display
        flags: Input flags
        
    Returns:
        Tuple of (bool, float, float, float) - (was_edited, new_value0, new_value1, new_value2)
        
    Example:     
        ```python
        x, y, z = 1.0, 2.0, 3.0
        changed, x, y, z = imgui.input_float3("Position", x, y, z)
        if changed:
            print(f"New position: ({x}, {y}, {z})")
        ```
    """
    ...
def input_float4( label: str, value0: float, value1: float, value2: float, value3: float, format: str = "%.3f", flags: Any = 0) -> Any:
    """Creates a 4-component float input field.
    
    Args:
        label: Label displayed next to the input field
        value0: First float value
        value1: Second float value
        value2: Third float value
        value3: Fourth float value
        format: Format string for display
        flags: Input flags
        
    Returns:
        Tuple of (bool, float, float, float, float) - (was_edited, new_value0, new_value1, new_value2, new_value3)
        
    Example:     
        ```python
        r, g, b, a = 1.0, 0.5, 0.0, 1.0
        changed, r, g, b, a = imgui.input_float4("Color", r, g, b, a)
        if changed:
            print(f"New color: ({r}, {g}, {b}, {a})")
        ```
    """
    ...
def input_int( label: str, value: int, step: int = 1, step_fast: int = 100, flags: Any = 0) -> Any:
    """Creates a single integer input field with optional step controls.
    
    Args:
        label: Label displayed next to the input field
        value: Current integer value
        step: Step increment for arrow buttons
        step_fast: Step increment when holding Ctrl
        flags: Input flags
        
    Returns:
        Tuple of (bool, int) - (was_edited, new_value)
        
    Example:     
        ```python
        count = 42
        changed, count = imgui.input_int("Count", count, step=1, step_fast=10)
        if changed:
            print(f"New count: {count}")
        ```
    """
    ...
def input_int2( label: str, value0: int, value1: int, flags: Any = 0) -> Any:
    """Creates a 2-component integer input field.
    
    Args:
        label: Label displayed next to the input field
        value0: First integer value
        value1: Second integer value
        flags: Input flags
        
    Returns:
        Tuple of (bool, int, int) - (was_edited, new_value0, new_value1)
        
    Example:     
        ```python
        x, y = 100, 200
        changed, x, y = imgui.input_int2("Grid Position", x, y)
        if changed:
            print(f"New grid position: ({x}, {y})")
        ```
    """
    ...
def input_int3( label: str, value0: int, value1: int, value2: int, flags: Any = 0) -> Any:
    """Creates a 3-component integer input field.
    
    Args:
        label: Label displayed next to the input field
        value0: First integer value
        value1: Second integer value
        value2: Third integer value
        flags: Input flags
        
    Returns:
        Tuple of (bool, int, int, int) - (was_edited, new_value0, new_value1, new_value2)
        
    Example:     
        ```python
        x, y, z = 100, 200, 300
        changed, x, y, z = imgui.input_int3("Grid Position", x, y, z)
        if changed:
            print(f"New grid position: ({x}, {y}, {z})")
        ```
    """
    ...
def input_int4( label: str, value0: int, value1: int, value2: int, value3: int, flags: Any = 0) -> Any:
    """Creates a 4-component integer input field.
    
    Args:
        label: Label displayed next to the input field
        value0: First integer value
        value1: Second integer value
        value2: Third integer value
        value3: Fourth integer value
        flags: Input flags
        
    Returns:
        Tuple of (bool, int, int, int, int) - (was_edited, new_value0, new_value1, new_value2, new_value3)
        
    Example:     
        ```python
        r, g, b, a = 255, 128, 0, 255
        changed, r, g, b, a = imgui.input_int4("Color", r, g, b, a)
        if changed:
            print(f"New color: ({r}, {g}, {b}, {a})")
        ```
    """
    ...
def input_double( label: str, value: float, step: float = 0.0, step_fast: float = 0.0, format: str = "%.6f", flags: Any = 0) -> Any:
    """Creates a double-precision float input field with optional step controls.
    
    Args:
        label: Label displayed next to the input field
        value: Current double value
        step: Step increment for arrow buttons
        step_fast: Step increment when holding Ctrl
        format: Format string for display
        flags: Input flags
        
    Returns:
        Tuple of (bool, float) - (was_edited, new_value)
        
    Example:     
        ```python
        value = 3.14159265359
        changed, value = imgui.input_double("Pi", value, step=0.0001, step_fast=0.01)
        if changed:
            print(f"New value: {value}")
        ```
    """
    ...
def input_scalar( label: str, data_type: Any, data: Any, step: Any = None, step_fast: Any = None, format: str = None, flags: Any = 0) -> Any:
    """Creates a generic scalar input field based on the data type.
    
    Args:
        label: Label displayed next to the input field
        data_type: Type of the scalar (e.g. ImGuiDataType_Float, ImGuiDataType_Int)
        data: Current value
        step: Step increment for arrow buttons
        step_fast: Step increment when holding Ctrl
        format: Format string for display
        flags: Input flags
        
    Returns:
        Tuple of (bool, Any) - (was_edited, new_value)
        
    Example:     
        ```python
        value = 42.0
        changed, value = imgui.input_scalar("Value", imgui.ImGuiDataType_Float, value)
        if changed:
            print(f"New value: {value}")
        ```
    """
    ...
def slider_float( label: str, value: float, min_value: float, max_value: float, format: str = "%.3f", flags: Any = 0,) -> Any:
    """Create a slider for float values.
    
    Args:
        label (str): Label for the slider
        value (float): Current value
        min_value (float): Minimum value
        max_value (float): Maximum value
        format (str): Format string for the value display
        flags (int): Additional flags for the slider
        
    Returns:
        tuple: (bool, float) - (whether value changed, new value)
        
    Example:     
        ```python
        value = 0.5
        changed, value = imgui.slider_float("Scale", value, 0.0, 1.0)
        if changed:
            print(f"Scale changed to: {value}")
        ```
    """
    ...   
def slider_float2( label: str, value0: float, value1: float, min_value: float, max_value: float, format: str = "%.3f", flags: Any = 0,) -> Any:
    """Creates a 2-component float slider.
    
    Args:
        label: Label displayed next to the slider
        value0: First float value
        value1: Second float value
        min_value: Minimum value for both components
        max_value: Maximum value for both components
        format: Format string for display
        flags: Slider flags
        
    Returns:
        Tuple of (bool, float, float) - (was_edited, new_value0, new_value1)
        
    Example:          
        ```python
        x, y = 0.5, 0.7
        changed, x, y = imgui.slider_float2("Position", x, y, 0.0, 1.0)
        if changed:
            print(f"New position: ({x}, {y})")
        ```
    """
    ...
def slider_float3( label: str, value0: float, value1: float, value2: float, min_value: float, max_value: float, format: str = "%.3f", flags: Any = 0,) -> Any:
    """Creates a 3-component float slider.
    
    Args:
        label: Label displayed next to the slider
        value0: First float value
        value1: Second float value
        value2: Third float value
        min_value: Minimum value for all components
        max_value: Maximum value for all components
        format: Format string for display
        flags: Slider flags
        
    Returns:
        Tuple of (bool, float, float, float) - (was_edited, new_value0, new_value1, new_value2)
	
    Example:          
        ```python
        x, y, z = 0.5, 0.7, 0.3
        changed, x, y, z = imgui.slider_float3("Position", x, y, z, 0.0, 1.0)
        if changed:
            print(f"New position: ({x}, {y}, {z})")
        ```
    """
    ...
def slider_float4( label: str, value0: float, value1: float, value2: float, value3: float, min_value: float, max_value: float, format: str = "%.3f", flags: Any = 0,) -> Any:
    """Creates a 4-component float slider.
    
    Args:
        label: Label displayed next to the slider
        value0: First float value
        value1: Second float value
        value2: Third float value
        value3: Fourth float value
        min_value: Minimum value for all components
        max_value: Maximum value for all components
        format: Format string for display
        flags: Slider flags
        
    Returns:
        Tuple of (bool, float, float, float, float) - (was_edited, new_value0, new_value1, new_value2, new_value3)
        
    Example:     
        ```python
        r, g, b, a = 0.5, 0.7, 0.3, 1.0
        changed, r, g, b, a = imgui.slider_float4("Color", r, g, b, a, 0.0, 1.0)
        if changed:
            print(f"New color: ({r}, {g}, {b}, {a})")
        ```
    """
    ...
def slider_angle( label: str, rad_value: float, value_degrees_min: float = -360.0, value_degrees_max: float = 360, format= "%.0f deg", flags: Any = 0) -> Any:
    """Creates a slider for angle values in radians with degree display.
    
    Args:
        label: Label displayed next to the slider
        rad_value: Current angle value in radians
        value_degrees_min: Minimum angle in degrees
        value_degrees_max: Maximum angle in degrees
        format: Format string for display
        flags: Slider flags
        
    Returns:
        Tuple of (bool, float) - (was_edited, new_value_in_radians)
        
    Example:     
        ```python
        angle = 0.0  # 0 degrees
        changed, angle = imgui.slider_angle("Rotation", angle)
        if changed:
            print(f"New angle: {angle} radians ({angle * 180 / 3.14159} degrees)")
        ```
    """
    ...
def slider_int( label: str, value: int, min_value: int, max_value: int, format: str = "%.f", flags: Any = 0) -> Any:
    """Creates a slider for integer values.
    
    Args:
        label: Label displayed next to the slider
        value: Current integer value
        min_value: Minimum value
        max_value: Maximum value
        format: Format string for display
        flags: Slider flags
        
    Returns:
        Tuple of (bool, int) - (was_edited, new_value)
        
    Example:     
        ```python
        count = 50
        changed, count = imgui.slider_int("Count", count, 0, 100)
        if changed:
            print(f"New count: {count}")
        ```
    """
    ...
def slider_int2( label: str, value0: int, value1: int, min_value: int, max_value: int, format: str = "%.f", flags: Any = 0) -> Any:
    """Creates a 2-component integer slider.
    
    Args:
        label: Label displayed next to the slider
        value0: First integer value
        value1: Second integer value
        min_value: Minimum value for both components
        max_value: Maximum value for both components
        format: Format string for display
        flags: Slider flags
        
    Returns:
        Tuple of (bool, int, int) - (was_edited, new_value0, new_value1)
        
    Example:     
        ```python
        x, y = 50, 75
        changed, x, y = imgui.slider_int2("Grid Position", x, y, 0, 100)
        if changed:
            print(f"New grid position: ({x}, {y})")
        ```
    """
    ...
def slider_int3( label: str, value0: int, value1: int, value2: int, min_value: int, max_value: int, format: str = "%.f", flags: Any = 0) -> Any:
    """Creates a 3-component integer slider.
    
    Args:
        label: Label displayed next to the slider
        value0: First integer value
        value1: Second integer value
        value2: Third integer value
        min_value: Minimum value for all components
        max_value: Maximum value for all components
        format: Format string for display
        flags: Slider flags
        
    Returns:
        Tuple of (bool, int, int, int) - (was_edited, new_value0, new_value1, new_value2)
        
    Example:     
        ```python
        x, y, z = 50, 75, 25
        changed, x, y, z = imgui.slider_int3("Grid Position", x, y, z, 0, 100)
        if changed:
            print(f"New grid position: ({x}, {y}, {z})")
        ```
    """
    ...
def slider_int4( label: str, value0: int, value1: int, value2: int, value3: int, min_value: int, max_value: int, format: str = "%.f", flags: Any = 0) -> Any:
    """Creates a 4-component integer slider.
    
    Args:
        label: Label displayed next to the slider
        value0: First integer value
        value1: Second integer value
        value2: Third integer value
        value3: Fourth integer value
        min_value: Minimum value for all components
        max_value: Maximum value for all components
        format: Format string for display
        flags: Slider flags
        
    Returns:
        Tuple of (bool, int, int, int, int) - (was_edited, new_value0, new_value1, new_value2, new_value3)
        
    Example:     
        ```python
        r, g, b, a = 255, 128, 0, 255
        changed, r, g, b, a = imgui.slider_int4("Color", r, g, b, a, 0, 255)
        if changed:
            print(f"New color: ({r}, {g}, {b}, {a})")
        ```
    """
    ...
def slider_scalar( label: str, data_type: Any, data: Any, min_value: Any, max_value: Any, format: str = None, flags: Any = 0) -> Any:
    """Creates a generic scalar slider based on the data type.
    
    Args:
        label: Label displayed next to the slider
        data_type: Type of the scalar (e.g. ImGuiDataType_Float, ImGuiDataType_Int)
        data: Current value
        min_value: Minimum value
        max_value: Maximum value
        format: Format string for display
        flags: Slider flags
        
    Returns:
        Tuple of (bool, Any) - (was_edited, new_value)
        
    Example:     
        ```python
        value = 42.0
        changed, value = imgui.slider_scalar("Value", imgui.ImGuiDataType_Float, value, 0.0, 100.0)
        if changed:
            print(f"New value: {value}")
        ```
    """
    ...
def v_slider_float( label: str, width: float, height: float, value: float, min_value: float, max_value: float, format: str = "%.f", flags: Any = 0) -> Any:
    """Creates a vertical float slider.
    
    Args:
        label: Label displayed next to the slider
        width: Width of the slider
        height: Height of the slider
        value: Current float value
        min_value: Minimum value
        max_value: Maximum value
        format: Format string for display
        flags: Slider flags
        
    Returns:
        Tuple of (bool, float) - (was_edited, new_value)
        
    Example:     
        ```python
        value = 0.5
        changed, value = imgui.v_slider_float("Scale", 20, 100, value, 0.0, 1.0)
        if changed:
            print(f"New scale: {value}")
        ```
    """
    ...
def v_slider_int( label: str, width: float, height: float, value: int, min_value: int, max_value: int, format: str = "%d", flags: Any = 0) -> Any:
    """Creates a vertical integer slider.
    
    Args:
        label: Label displayed next to the slider
        width: Width of the slider
        height: Height of the slider
        value: Current integer value
        min_value: Minimum value
        max_value: Maximum value
        format: Format string for display
        flags: Slider flags
        
    Returns:
        Tuple of (bool, int) - (was_edited, new_value)
        
    Example:     
        ```python
        value = 50
        changed, value = imgui.v_slider_int("Count", 20, 100, value, 0, 100)
        if changed:
            print(f"New count: {value}")
        ```
    """
    ...
def v_slider_scalar( label: str, width: float, height: float, data_type: Any, data: Any, min_value: Any, max_value: Any, format: str = None, flags: Any = 0) -> Any:
    """Creates a vertical generic scalar slider based on the data type.
    
    Args:
        label: Label displayed next to the slider
        width: Width of the slider
        height: Height of the slider
        data_type: Type of the scalar (e.g. ImGuiDataType_Float, ImGuiDataType_Int)
        data: Current value
        min_value: Minimum value
        max_value: Maximum value
        format: Format string for display
        flags: Slider flags
        
    Returns:
        Tuple of (bool, Any) - (was_edited, new_value)
        
    Example:     
        ```python
        value = 42.0
        changed, value = imgui.v_slider_scalar("Value", 20, 100, imgui.ImGuiDataType_Float, value, 0.0, 100.0)
        if changed:
            print(f"New value: {value}")
        ```
    """
    ...
def progress_bar( fraction: float, size: Any = (-FLOAT_MIN,0), overlay: str = "") -> Any:
    """Creates a progress bar widget.
    
    Args:
        fraction: Progress value between 0.0 and 1.0
        size: Size of the progress bar (width, height)
        overlay: Optional text overlay to display on the progress bar
        
    Returns:
        None
        
    Example:     
        ```python
        imgui.progress_bar(0.75, (100, 20), "75%")
        ```
    """
    ...
def set_keyboard_focus_here( offset: int = 0) -> Any:
    """Sets keyboard focus to the next widget.
    
    Args:
        offset: Offset from the current position
        
    Returns:
        None
        
    Example:     
        ```python
        imgui.set_keyboard_focus_here()  # Focus next widget
        ```
    """
    ...
def is_item_focused() -> Any:
    """Checks if the last item is focused.
    
    Returns:
        bool: True if the last item is focused
        
    Example:     
        ```python
        if imgui.is_item_focused():
            print("Item is focused")
        ```
    """
    ...
def is_item_clicked( mouse_button: Any = 0) -> Any:
    """Checks if the last item was clicked.
    
    Args:
        mouse_button: Mouse button to check (0=left, 1=right, 2=middle)
        
    Returns:
        bool: True if the item was clicked
        
    Example:     
        ```python
        if imgui.is_item_clicked():
            print("Item was clicked")
        ```
    """
    ...
def is_item_edited() -> Any:
    """Checks if the last item was edited.
    
    Returns:
        bool: True if the item was edited
        
    Example:     
        ```python
        if imgui.is_item_edited():
            print("Item was edited")
        ```
    """
    ...
def is_item_deactivated() -> Any:
    """Checks if the last item was deactivated.
    
    Returns:
        bool: True if the item was deactivated
        
    Example:     
        ```python
        if imgui.is_item_deactivated():
            print("Item was deactivated")
        ```
    """
    ...
def is_item_toggled_open() -> Any:
    """Checks if the last item was toggled open.
    
    Returns:
        bool: True if the item was toggled open
        
    Example:     
        ```python
        if imgui.is_item_toggled_open():
            print("Item was toggled open")
        ```
    """
    ...
def is_any_item_active() -> Any:
    """Checks if any item is active.
    
    Returns:
        bool: True if any item is active
        
    Example:     
        ```python
        if imgui.is_any_item_active():
            print("An item is active")
        ```
    """
    ...
def get_item_rect_min() -> Any:
    """Gets the minimum point of the last item's rectangle.
    
    Returns:
        tuple: (x, y) coordinates of the minimum point
        
    Example:     
        ```python
        min_x, min_y = imgui.get_item_rect_min()
        print(f"Item min position: ({min_x}, {min_y})")
        ```
    """
    ...
def get_item_rect_size() -> Any:
    """Gets the size of the last item's rectangle.
    
    Returns:
        tuple: (width, height) of the item
        
    Example:     
        ```python
        width, height = imgui.get_item_rect_size()
        print(f"Item size: {width}x{height}")
        ```
    """
    ...
def get_main_viewport() -> Any:
    """Gets the main viewport.
    
    Returns:
        ImGuiViewport: The main viewport object
        
    Example:     
        ```python
        viewport = imgui.get_main_viewport()
        print(f"Viewport size: {viewport.size}")
        ```
    """
    ...
def is_window_hovered( flags: Any = 0) -> Any:
    """Checks if the current window is hovered.
    
    Args:
        flags: Additional flags for hover check
        
    Returns:
        bool: True if the window is hovered
        
    Example:     
        ```python
        if imgui.is_window_hovered():
            print("Window is hovered")
        ```
    """
    ...
def is_window_focused( flags: Any = 0) -> Any:
    """Checks if the current window is focused.
    
    Args:
        flags: Additional flags for focus check
        
    Returns:
        bool: True if the window is focused
        
    Example:     
        ```python
        if imgui.is_window_focused():
            print("Window is focused")
        ```
    """
    ...
def is_rect_visible( size_width: float, size_height: float) -> Any:
    """Checks if a rectangle would be visible.
    
    Args:
        size_width: Width of the rectangle
        size_height: Height of the rectangle
        
    Returns:
        bool: True if the rectangle would be visible
        
    Example:     
        ```python
        if imgui.is_rect_visible(100, 50):
            print("Rectangle would be visible")
        ```
    """
    ...
def get_time() -> Any:
    """Gets the current time in seconds.
    
    Returns:
        float: Current time in seconds
        
    Example:     
        ```python
        current_time = imgui.get_time()
        print(f"Current time: {current_time}")
        ```
    """
    ...
def get_foreground_draw_list() -> Any:
    """Gets the foreground draw list.
    
    Returns:
        ImDrawList: The foreground draw list
        
    Example:     
        ```python
        draw_list = imgui.get_foreground_draw_list()
        draw_list.add_line(0, 0, 100, 100, 0xFF0000FF)
        ```
    """
    ...
def is_key_pressed( key_index: int, repeat: bool = False) -> Any:
    """Checks if a key is pressed.
    
    Args:
        key_index: Index of the key to check
        repeat: Whether to check for key repeat
        
    Returns:
        bool: True if the key is pressed
        
    Example:     
        ```python
        if imgui.is_key_pressed(imgui.KEY_A):
            print("A key is pressed")
        ```
    """
    ...
def is_mouse_hovering_rect( r_min_x: float, r_min_y: float, r_max_x: float, r_max_y: float, clip: bool = True) -> Any:
    """Checks if the mouse is hovering over a rectangle.
    
    Args:
        r_min_x: Minimum x coordinate
        r_min_y: Minimum y coordinate
        r_max_x: Maximum x coordinate
        r_max_y: Maximum y coordinate
        clip: Whether to clip the check to the current window
        
    Returns:
        bool: True if the mouse is hovering over the rectangle
        
    Example:
        ```python	
        if imgui.is_mouse_hovering_rect(0, 0, 100, 100):
            print("Mouse is hovering over rectangle")
        ```
    """
    ...
def is_mouse_double_clicked( button: int = 0) -> Any:
    """Checks if a mouse button was double-clicked.
    
    Args:
        button: Mouse button to check (0=left, 1=right, 2=middle)
        
    Returns:
        bool: True if the button was double-clicked
        
    Example:     
        ```python
        if imgui.is_mouse_double_clicked():
            print("Left mouse button was double-clicked")
        ```
    """
    ...
def is_mouse_released( button: int = 0) -> Any:
    """Checks if a mouse button was released.
    
    Args:
        button: Mouse button to check (0=left, 1=right, 2=middle)
        
    Returns:
        bool: True if the button was released
        
    Example:     
        ```python
        if imgui.is_mouse_released():
            print("Left mouse button was released")
        ```
    """
    ...
def is_mouse_dragging( button: int, lock_threshold: float = -1.0) -> Any:
    """Checks if a mouse button is being dragged.
    
    Args:
        button: Mouse button to check (0=left, 1=right, 2=middle)
        lock_threshold: Threshold for drag lock
        
    Returns:
        bool: True if the button is being dragged
        
    Example:     
        ```python
        if imgui.is_mouse_dragging(0):
            print("Left mouse button is being dragged")
        ```
    """
    ...
def get_mouse_pos() -> Any:
    """Gets the current mouse position.
    
    Returns:
        tuple: (x, y) coordinates of the mouse position
        
    Example:     
        ```python
        x, y = imgui.get_mouse_pos()
        print(f"Mouse position: ({x}, {y})")
        ```
    """
    ...
def get_mouse_cursor() -> Any:
    """Gets the current mouse cursor type.
    
    Returns:
        int: Mouse cursor type
        
    Example:     
        ```python
        cursor = imgui.get_mouse_cursor()
        print(f"Current cursor type: {cursor}")
        ```
    """
    ...
def capture_mouse_from_app( want_capture_mouse_value: bool = True) -> Any:
    """Captures or releases mouse input from the application.
    
    Args:
        want_capture_mouse_value: Whether to capture mouse input
        
    Returns:
        None
        
    Example:     
        ```python
        imgui.capture_mouse_from_app(True)  # Capture mouse input
        ```
    """
    ...
def load_ini_settings_from_disk( ini_file_name: str) -> Any:
    """Loads ImGui settings from an INI file.
    
    Args:
        ini_file_name: Path to the INI file
        
    Returns:
        None
        
    Example:     
        ```python
        imgui.load_ini_settings_from_disk("imgui.ini")
        ```
    """
    ...
def save_ini_settings_to_disk( ini_file_name: str) -> Any:
    """Saves ImGui settings to an INI file.
    
    Args:
        ini_file_name: Path to the INI file
        
    Returns:
        None
        
    Example:     
        ```python
        imgui.save_ini_settings_to_disk("imgui.ini")
        ```
    """
    ...
def set_clipboard_text( text: str) -> Any:
    """Sets the clipboard text.
    
    Args:
        text: Text to set in the clipboard
        
    Returns:
        None
        
    Example:     
        ```python
        imgui.set_clipboard_text("Hello, World!")
        ```
    """
    ...
def set_scroll_here_x( center_x_ratio: float = 0.5) -> Any:
    """Sets the horizontal scroll position.
    
    Args:
        center_x_ratio: Ratio to center the scroll position
        
    Returns:
        None
        
    Example:     
        ```python
        imgui.set_scroll_here_x(0.5)  # Center horizontally
        ```
    """
    ...
def set_scroll_from_pos_x( local_x: float, center_x_ratio: float = 0.5) -> Any:
    """Sets the horizontal scroll position from a local x coordinate.
    
    Args:
        local_x: Local x coordinate
        center_x_ratio: Ratio to center the scroll position
        
    Returns:
        None
        
    Example:     
        ```python
        imgui.set_scroll_from_pos_x(100, 0.5)  # Scroll to x=100
        ```
    """
    ...
def push_font(font: Any) -> Any:
    """Pushes a font onto the font stack.
    
    Args:
        font: Font to push
        
    Returns:
        None
        
    Example:     
        ```python
        imgui.push_font(my_font)
        ```
    """
    ...
def color_convert_u32_to_float4( in_: int) -> Any:
    """Converts a 32-bit color to float4.
    
    Args:
        in_: 32-bit color value
        
    Returns:
        tuple: (r, g, b, a) color components as floats
        
    Example:     
        ```python
        r, g, b, a = imgui.color_convert_u32_to_float4(0xFF0000FF)
        print(f"Color: ({r}, {g}, {b}, {a})")
        ```
    """
    ...
def color_convert_rgb_to_hsv( r: float, g: float, b: float) -> Any:
    """Converts RGB color to HSV.
    
    Args:
        r: Red component (0-1)
        g: Green component (0-1)
        b: Blue component (0-1)
        
    Returns:
        tuple: (h, s, v) color components
        
    Example:     
        ```python
        h, s, v = imgui.color_convert_rgb_to_hsv(1.0, 0.0, 0.0)
        print(f"HSV: ({h}, {s}, {v})")
        ```
    """
    ...
def separator() -> Any:
    """Creates a horizontal separator line.
    
    Returns:
        None
        
    Example:     
        ```python
        imgui.separator()
        ```
    """
    ...
def new_line() -> Any:
    """Creates a new line.
    
    Returns:
        None
        
    Example:     
        ```python
        imgui.new_line()
        ```
    """
    ...
def dummy(width: float, height: float) -> Any:
    """Creates an invisible dummy widget.
    
    Args:
        width: Width of the dummy
        height: Height of the dummy
        
    Returns:
        None
        
    Example:     
        ```python
        imgui.dummy(100, 20)  # Create 100x20 invisible space
        ```
    """
    ...
def unindent( width: float = 0.0) -> Any:
    """Unindents the current layout.
    
    Args:
        width: Width to unindent
        
    Returns:
        None
        
    Example:     
        ```python
        imgui.unindent(20)  # Unindent by 20 pixels
        ```
    """
    ...
def next_column() -> Any:
    """Moves to the next column in a multi-column layout.
    
    Returns:
        None
        
    Example:     
        ```python
        imgui.next_column()
        ```
    """
    ...
def get_column_offset( column_index: int = -1) -> Any:
    """Gets the offset of a column.
    
    Args:
        column_index: Index of the column (-1 for current)
        
    Returns:
        float: Column offset
        
    Example:     
        ```python
        offset = imgui.get_column_offset()
        print(f"Current column offset: {offset}")
        ```
    """
    ...
def get_column_width( column_index: int = -1) -> Any:
    """Gets the width of a column.
    
    Args:
        column_index: Index of the column (-1 for current)
        
    Returns:
        float: Column width
        
    Example:     
        ```python
        width = imgui.get_column_width()
        print(f"Current column width: {width}")
        ```
    """
    ...
def get_columns_count() -> Any:
    """Gets the number of columns in the current layout.
    
    Returns:
        int: Number of columns
        
    Example:     
        ```python
        count = imgui.get_columns_count()
        print(f"Number of columns: {count}")
        ```
    """
    ...
def end_tab_bar() -> Any:
    """Ends a tab bar.
    
    Returns:
        None
        
    Example:     
        ```python
        imgui.end_tab_bar()
        ```
    """
    ...
def end_tab_item() -> Any:
    """Ends a tab item.
    
    Returns:
        None
        
    Example:     
        ```python
        imgui.end_tab_item()
        ```
    """
    ...
def set_tab_item_closed( tab_or_docked_window_label: str) -> Any:
    """Sets a tab or docked window as closed.
    
    Args:
        tab_or_docked_window_label: Label of the tab or window
        
    Returns:
        None
        
    Example:     
        ```python
        imgui.set_tab_item_closed("My Tab")
        ```
    """
    ...
def dockspace( id: Any, size: Any = (0,0), flags: Any = 0) -> Any:
    """Creates a dockspace.
    
    Args:
        id: Unique identifier for the dockspace
        size: Size of the dockspace
        flags: Dockspace flags
        
    Returns:
        int: Dockspace ID
        
    Example:     
        ```python
        dockspace_id = imgui.dockspace("MyDockspace", (800, 600))
        ```
    """
    ...
def is_window_docked() -> Any:
    """Checks if the current window is docked.
    
    Returns:
        bool: True if the window is docked
        
    Example:     
        ```python
        if imgui.is_window_docked():
            print("Window is docked")
        ```
    """
    ...
def set_drag_drop_payload( type: str, data: Any, condition: int = 0) -> Any:
    """Sets drag and drop payload data.
    
    Args:
        type: Type of the payload
        data: Payload data
        condition: Condition for setting the payload
        
    Returns:
        bool: True if the payload was set
        
    Example:     
        ```python
        if imgui.set_drag_drop_payload("MyType", my_data):
            print("Drag and drop payload set")
        ```
    """
    ...
def begin_drag_drop_target() -> Any:
    """Begins a drag and drop target.
    
    Returns:
        bool: True if the target is active
        
    Example:     
        ```python
        if imgui.begin_drag_drop_target():
            # Handle drag and drop
            imgui.end_drag_drop_target()
        ```
    """
    ...
def end_drag_drop_target() -> Any:
    """Ends a drag and drop target.
    
    Returns:
        None
        
    Example:     
        ```python
        imgui.end_drag_drop_target()
        ```
    """
    ...
def push_clip_rect( clip_rect_min_x: float, clip_rect_min_y: float, clip_rect_max_x: float, clip_rect_max_y: float, intersect_with_current_clip_rect: bool = False) -> Any:
    """Pushes a clip rectangle onto the clip stack.
    
    Args:
        clip_rect_min_x: Minimum x coordinate
        clip_rect_min_y: Minimum y coordinate
        clip_rect_max_x: Maximum x coordinate
        clip_rect_max_y: Maximum y coordinate
        intersect_with_current_clip_rect: Whether to intersect with current clip rect
        
    Returns:
        None
        
    Example:     
        ```python
        imgui.push_clip_rect(0, 0, 100, 100)
        ```
    """
    ...
def pop_clip_rect() -> Any:
    """Pops the last clip rectangle from the clip stack.
    
    Returns:
        None
        
    Example:     
        ```python
        imgui.pop_clip_rect()
        ```
    """
    ...
def end_group() -> Any:
    """Ends a group.
    
    Returns:
        None
        
    Example:     
        ```python
        imgui.end_group()
        ```
    """
    ...
def get_cursor_pos_x() -> Any:
    """Gets the current cursor x position.
    
    Returns:
        float: Cursor x position
        
    Example:     
        ```python
        x = imgui.get_cursor_pos_x()
        print(f"Cursor x position: {x}")
        ```
    """
    ...
def set_cursor_pos_y( y: float) -> Any:
    """Sets the cursor y position.
    
    Args:
        y: Y position to set
        
    Returns:
        None
        
    Example:     
        ```python
        imgui.set_cursor_pos_y(100)
        ```
    """
    ...
def get_cursor_screen_pos() -> Any:
    """Gets the cursor position in screen coordinates.
    
    Returns:
        tuple: (x, y) screen coordinates
        
    Example:     
        ```python
        x, y = imgui.get_cursor_screen_pos()
        print(f"Cursor screen position: ({x}, {y})")
        ```
    """
    ...
def align_text_to_frame_padding() -> Any:
    """Aligns text to frame padding.
    
    Returns:
        None
        
    Example:     
        ```python
        imgui.align_text_to_frame_padding()
        ```
    """
    ...
def get_text_line_height_with_spacing() -> Any:
    """Gets the height of a text line including spacing.
    
    Returns:
        float: Line height with spacing
        
    Example:     
        ```python
        height = imgui.get_text_line_height_with_spacing()
        print(f"Line height with spacing: {height}")
        ```
    """
    ...
def get_frame_height_with_spacing() -> Any:
    """Gets the height of a frame including spacing.
    
    Returns:
        float: Frame height with spacing
        
    Example:     
        ```python
        height = imgui.get_frame_height_with_spacing()
        print(f"Frame height with spacing: {height}")
        ```
    """
    ...
def destroy_context( ctx: Any = None) -> Any:
    """Destroys an ImGui context.
    
    Args:
        ctx: Context to destroy (None for current)
        
    Returns:
        None
        
    Example:     
        ```python
        imgui.destroy_context()
        ```
    """
    ...
def set_current_context( ctx: Any) -> Any:
    """Sets the current ImGui context.
    
    Args:
        ctx: Context to set as current
        
    Returns:
        None
        
    Example:     
        ```python
        imgui.set_current_context(my_context)
        ```
    """
    ...
def pop_id() -> Any:
    """Pops the last ID from the ID stack.
    
    Returns:
        None
        
    Example:     
        ```python
        imgui.pop_id()
        ```
    """
    ...
def _ansifeed_text_ansi( text: str) -> Any:
    """Internal function for ANSI text handling.
    
    Args:
        text: Text to process
        
    Returns:
        None
        
    Example:     
        ```python
        imgui._ansifeed_text_ansi("\033[31mRed text\033[0m")
        ```
    """
    ...
def _py_font( font: Any) -> Any:
    """Internal function for font handling.
    
    Args:
        font: Font to process
        
    Returns:
        None
        
    Example:     
        ```python
        imgui._py_font(my_font)
        ```
    """
    ...
def _py_styled( variable: Any, value: Any) -> Any:
    """Internal function for style handling.
    
    Args:
        variable: Style variable
        value: Style value
        
    Returns:
        None
        
    Example:     
        ```python
        imgui._py_styled(imgui.STYLE_ALPHA, 0.5)
        ```
    """
    ...
def _py_scoped( str_id: str) -> Any:
    """Internal function for scoped ID handling.
    
    Args:
        str_id: String ID
        
    Returns:
        None
        
    Example:     
        ```python
        imgui._py_scoped("my_id")
        ```
    """
    ...
def _py_vertex_buffer_vertex_uv_offset() -> Any:
    """Internal function to get vertex UV offset.
    
    Returns:
        int: UV offset
        
    Example:     
        ```python
        offset = imgui._py_vertex_buffer_vertex_uv_offset()
        ```
    """
    ...
def _py_vertex_buffer_vertex_size() -> Any:
    """Internal function to get vertex size.
    
    Returns:
        int: Vertex size
        
    Example:     
        ```python
        size = imgui._py_vertex_buffer_vertex_size()
        ```
    """
    ...
def update_platform_windows() -> Any:
    """Updates platform windows.
    
    Returns:
        None
        
    Example:     
        ```python
        imgui.update_platform_windows()
        ```
    """
    ...
def get_style() -> Any:
    """Gets the current ImGui style.
    
    Returns:
        ImGuiStyle: Current style object
        
    Example:     
        ```python
        style = imgui.get_style()
        print(f"Window padding: {style.window_padding}")
        ```
    """
    ...
def end_frame() -> Any:
    """Ends the current ImGui frame.
    
    Returns:
        None
        
    Example:     
        ```python
        imgui.end_frame()
        ```
    """
    ...
def show_user_guide() -> Any:
    """Shows the ImGui user guide window.
    
    Returns:
        None
        
    Example:     
        ```python
        imgui.show_user_guide()
        ```
    """
    ...
def style_colors_dark( dst: Any = None) -> Any:
    """Sets dark color theme.
    
    Args:
        dst: Optional style object to modify
        
    Returns:
        None
        
    Example:     
        ```python
        imgui.style_colors_dark()
        ```
    """
    ...
def style_colors_light( dst: Any = None) -> Any:
    """Sets light color theme.
    
    Args:
        dst: Optional style object to modify
        
    Returns:
        None
        
    Example:     
        ```python
        imgui.style_colors_light()
        ```
    """
    ...
def show_test_window() -> Any:
    """Shows the ImGui test window.
    
    Returns:
        None
        
    Example:     
        ```python
        imgui.show_test_window()
        ```
    """
    ...
def show_style_selector( label: str) -> Any:
    """Shows the style selector window.
    
    Args:
        label: Label for the window
        
    Returns:
        None
        
    Example:     
        ```python
        imgui.show_style_selector("Style Editor")
        ```
    """
    ...
def begin( label: str, closable: Any = False, flags: Any = 0) -> Any:
    """Begins a window.
    
    Args:
        label: Window label
        closable: Whether the window can be closed
        flags: Window flags
        
    Returns:
        bool: True if the window is open
        
    Example:     
        ```python
        if imgui.begin("My Window", True):
            imgui.text("Window content")
            imgui.end()
        ```
    """
    ...
def end() -> Any:
    """Ends a window.
    
    Returns:
        None
        
    Example:     
        ```python
        imgui.end()
        ```
    """
    ...
def get_content_region_max() -> Any:
    """Gets the maximum content region size.
    
    Returns:
        tuple: (x, y) maximum content region size
        
    Example:     
        ```python
        max_x, max_y = imgui.get_content_region_max()
        print(f"Max content region: ({max_x}, {max_y})")
        ```
    """
    ...
def get_content_region_available_width() -> Any:
    """Gets the available content region width.
    
    Returns:
        float: Available width
        
    Example:     
        ```python
        width = imgui.get_content_region_available_width()
        print(f"Available width: {width}")
        ```
    """
    ...
def get_window_content_region_max() -> Any:
    """Gets the maximum window content region size.
    
    Returns:
        tuple: (x, y) maximum window content region size
        
    Example:     
        ```python
        max_x, max_y = imgui.get_window_content_region_max()
        print(f"Max window content region: ({max_x}, {max_y})")
        ```
    """
    ...
def set_window_focus() -> Any:
    """Sets focus to the current window.
    
    Returns:
        None
        
    Example:     
        ```python
        imgui.set_window_focus()
        ```
    """
    ...
def get_scroll_x() -> Any:
    """Gets the horizontal scroll position.
    
    Returns:
        float: Scroll position
    
    Example:     
        ```python
        scroll_x = imgui.get_scroll_x()
        print(f"Horizontal scroll: {scroll_x}")
        ```
    """
    ...
def get_scroll_max_x() -> Any:
    """Gets the maximum horizontal scroll position.
    
    Returns:
        float: Maximum scroll position
        
    Example:     
        ```python
        max_scroll = imgui.get_scroll_max_x()
        print(f"Max horizontal scroll: {max_scroll}")
        ```
    """
    ...
def set_scroll_x( scroll_x: float) -> Any:
    """Sets the horizontal scroll position.
    
    Args:
        scroll_x: Scroll position to set
        
    Returns:
        None
        
    Example:     
        ```python
        imgui.set_scroll_x(100)
        ```
    """
    ...
def set_window_font_scale( scale: float) -> Any:
    """Sets the window font scale.
    
    Args:
        scale: Font scale factor
        
    Returns:
        None
        
    Example:     
        ```python
        imgui.set_window_font_scale(1.5)  # 50% larger text
        ```
    """
    ...
def set_next_window_bg_alpha( alpha: float) -> Any:
    """Sets the background alpha for the next window.
    
    Args:
        alpha: Alpha value (0-1)
        
    Returns:
        None
        
    Example:     
        ```python
        imgui.set_next_window_bg_alpha(0.5)  # 50% transparent
        ```
    """
    ...
def get_window_position() -> Any:
    """Gets the current window position.
    
    Returns:
        tuple: (x, y) window position
        
    Example:     
        ```python
        x, y = imgui.get_window_position()
        print(f"Window position: ({x}, {y})")
        ```
    """
    ...
def get_window_size() -> Any:
    """Gets the current window size.
    
    Returns:
        tuple: (width, height) window size
        
    Example:     
        ```python
        width, height = imgui.get_window_size()
        print(f"Window size: {width}x{height}")
        ```
    """
    ...
def get_window_height() -> Any:
    """Gets the current window height.
    
    Returns:
        float: Window height
        
    Example:     
        ```python
        height = imgui.get_window_height()
        print(f"Window height: {height}")
        ```
    """
    ...
def set_next_window_viewport( viewport_id: Any) -> Any:
    """Sets the viewport for the next window.
    
    Args:
        viewport_id: Viewport ID
        
    Returns:
        None
        
    Example:     
        ```python
        imgui.set_next_window_viewport(my_viewport_id)
        ```
    """
    ...
def set_window_position_labeled( label: str, x: float, y: float, condition: int = ALWAYS) -> Any:
    """Sets the position of a window by label.
    
    Args:
        label: Window label
        x: X position
        y: Y position
        condition: When to set the position
        
    Returns:
        None
        
    Example:     
        ```python
        imgui.set_window_position_labeled("My Window", 100, 100)
        ```
    """
    ...
def set_window_collapsed_labeled( label: str, collapsed: bool, condition: int = ALWAYS) -> Any:
    """Sets the collapsed state of a window by label.
    
    Args:
        label: Window label
        collapsed: Whether the window should be collapsed
        condition: When to set the collapsed state
        
    Returns:
        None
        
    Example:     
        ```python
        imgui.set_window_collapsed_labeled("My Window", True)
        ```
    """
    ...
def is_window_appearing() -> Any:
    """Checks if the current window is appearing.
    
    Returns:
        bool: True if the window is appearing
        
    Example:     
        ```python
        if imgui.is_window_appearing():
            print("Window is appearing")
        ```
    """
    ...
def get_tree_node_to_label_spacing() -> Any:
    """Gets the spacing between tree node and label.
    
    Returns:
        float: Spacing value
        
    Example:     
        ```python
        spacing = imgui.get_tree_node_to_label_spacing()
        print(f"TreeNode spacing: {spacing}")
        ```
    """
    ...
def listbox_footer() -> Any:
    """Ends a listbox.
    
    Returns:
        None
        
    Example:     
        ```python
        imgui.listbox_footer()
        ```
    """
    ...
def set_tooltip( text: str) -> Any:
    """Sets a tooltip for the last item.
    
    Args:
        text: Tooltip text
        
    Returns:
        None
        
    Example:     
        ```python
        imgui.set_tooltip("This is a tooltip")
        ```
    """

def begin_main_menu_bar() -> Any:
    """Begin a menu bar at the top of a window.
    
    Returns:
        bool: True if the menu bar is open
        
    Example:     
        ```python
        if imgui.begin_menu_bar():
            if imgui.begin_menu("File"):
                if imgui.menu_item("Open"):
                    print("Open selected")
                if imgui.menu_item("Save"):
                    print("Save selected")
                imgui.end_menu()
            if imgui.begin_menu("Edit"):
                if imgui.menu_item("Copy"):
                    print("Copy selected")
                imgui.end_menu()
            imgui.end_menu_bar()
        ```
    """
    ...
def begin_menu_bar() -> Any:
    """Begin a menu bar within the current window or menu.

    Returns:
        bool: True if the menu bar is open.

    Example:     
        ```python
        if imgui.begin_menu_bar():
            if imgui.begin_menu("File"):
                if imgui.menu_item("Open"):
                    print("Open selected")
                imgui.end_menu()
            imgui.end_menu_bar()
        ```
    """
    ...

def begin_menu(label: str, enabled: Any = True) -> Any:
    """Begin a new menu with a given label.

    Args:
        label (str): The label of the menu.
        enabled (bool): Whether the menu is enabled.

    Returns:
        bool: True if the menu is open and items can be added.

    Example:     
        ```python
        if imgui.begin_menu("Edit"):
            if imgui.menu_item("Undo"):
                print("Undo selected")
            imgui.end_menu()
        ```
    """
    ...

def begin_popup(label: str, flags: Any = 0) -> Any:
    """Begin a popup window with a specified label.

    Args:
        label (str): The identifier for the popup.
        flags (int): Optional flags controlling popup behavior.

    Returns:
        bool: True if the popup is open.

    Example:     
        ```python
        if imgui.begin_popup("confirm_delete"):
            imgui.text("Are you sure you want to delete this?")
            if imgui.button("Yes"):
                delete_item()
                imgui.close_current_popup()
            imgui.end_popup()
        ```
    """
    ...

def is_popup_open(label: str, flags: Any = 0) -> Any:
    """Check whether a popup with the specified label is open.

    Args:
        label (str): The identifier of the popup.
        flags (int): Optional flags.

    Returns:
        bool: True if the popup is currently open.

    Example:     
        ```python
        if imgui.is_popup_open("settings_popup"):
            print("Settings popup is open")
        ```
    """
    ...

def close_current_popup() -> Any:
    """Close the currently active popup.

    Example:     
        ```python
        if imgui.button("Cancel"):
            imgui.close_current_popup()
        ```
    """
    ...

def table_set_column_index(column_n: int) -> Any:
    """Manually set the current table column index.

    Args:
        column_n (int): The index of the column to set.

    Example:     
        ```python
        imgui.table_next_row()
        imgui.table_set_column_index(1)
        imgui.text("Column 1 content")
        ```
    """
    ...

def table_headers_row() -> Any:
    """Create a row in the table for headers.

    Example:     
        ```python
        imgui.begin_table("example_table", 3)
        imgui.table_headers_row()
        imgui.end_table()
        ```
    """
    ...

def table_get_sort_specs() -> Any:
    """Get the current sort specifications for the table.

    Returns:
        Any: A structure containing sort specifications.

    Example:     
        ```python
        sort_specs = imgui.table_get_sort_specs()
        if sort_specs and sort_specs.specs_dirty:
            sort_data(sort_specs)
        ```
    """
    ...

def table_get_column_index() -> Any:
    """Get the current column index.

    Returns:
        int: The index of the current column.

    Example:     
        ```python
        current_index = imgui.table_get_column_index()
        print(f"Currently in column {current_index}")
        ```
    """
    ...

def table_get_column_name(column_n: int = -1) -> Any:
    """Get the name of the specified column.

    Args:
        column_n (int): The index of the column. Defaults to -1 (current column).

    Returns:
        str: The name of the column.

    Example:     
        ```python
        name = imgui.table_get_column_name()
        print(f"Current column name: {name}")
        ```
    """
    ...

def text_colored( text: str, r: float, g: float, b: float, a: float = 1.) -> Any:
    """Display a text label with custom color.
    
    Args:
        text (str): Text to display
        r (float): Red component (0.0 to 1.0)
        g (float): Green component (0.0 to 1.0)
        b (float): Blue component (0.0 to 1.0)
        a (float): Alpha component (0.0 to 1.0)
        
    Example:     
        ```python
        imgui.text_colored("Error!", 1.0, 0.0, 0.0)  # Red text
        imgui.text_colored("Success", 0.0, 1.0, 0.0)  # Green text
        ```
    """
    ...
def text_wrapped(text: str) -> Any:
    """Display text with automatic word-wrapping.

    Args:
        text (str): The text to display.

    Example:     
        ```python
        imgui.text_wrapped("This is a long sentence that will wrap automatically "
                           "within the current window or column width.")
        ```
    """
    ...

def text_unformatted(text: str) -> Any:
    """Display text without any formatting or wrapping.

    Args:
        text (str): The text to display exactly as is.

    Example:     
        ```python
        raw_text = "Line 1\nLine 2\nLine 3"
        imgui.text_unformatted(raw_text)
        ```
    """
    ...

def button( label: str,width: int = 0,height: int = 0) -> Any:
    """Create a clickable button.
    
    Args:
        label (str): Text label for the button
        width (int): Width of the button (0 = auto)
        height (int): Height of the button (0 = auto)
        
    Returns:
        bool: True if the button was clicked
        
    Example:     
        ```python
        if imgui.button("Click Me"):
            print("Button clicked!")
            
        # Custom sized button
        if imgui.button("Large Button", width=200, height=50):
            print("Large button clicked!")
        ```
    """
    ...
def arrow_button(label: str, direction: Any = DIRECTION_NONE) -> Any:
    """Display a small arrow button.

    Args:
        label (str): Unique ID for the button.
        direction: Direction the arrow points (e.g., imgui.DIRECTION_RIGHT).

    Returns:
        bool: True if the button is clicked.

    Example:     
        ```python
        if imgui.arrow_button("##right", imgui.DIRECTION_RIGHT):
            print("Arrow clicked")
        ```
    """
    ...

def checkbox_flags(label: str, flags: int, flags_value: int) -> Any:
    """Display a checkbox that toggles bits in a flags integer.

    Args:
        label (str): Label displayed next to the checkbox.
        flags (int): Bitfield reference.
        flags_value (int): The flag bit to toggle.

    Returns:
        bool: True if the checkbox state changed.

    Example:     
        ```python
        flags = 0b0100
        if imgui.checkbox_flags("Enable feature", flags, 0b0100):
            print("Feature toggled")
        ```
    """
    ...

def color_edit3(label: str, r: float, g: float, b: float, flags: Any = 0) -> Any:
    """Display a color editor for 3 float RGB values.

    Args:
        label (str): Label for the color editor.
        r, g, b (float): RGB components.
        flags: Optional configuration flags.

    Returns:
        bool: True if the color was edited.

    Example:     
        ```python
        r, g, b = 1.0, 0.5, 0.0
        if imgui.color_edit3("Color", r, g, b):
            print(f"New color: {r}, {g}, {b}")
        ```
    """
    ...

def set_item_default_focus() -> Any:
    """Give keyboard/gamepad focus to the most recent item.

    Example:     
        ```python
        imgui.input_text("Name", buffer)
        imgui.set_item_default_focus()
        ```
    """
    ...

def is_item_active() -> Any:
    """Check if the last item is active (e.g., being edited or clicked).

    Returns:
        bool: True if the item is active.

    Example:     
        ```python
        imgui.input_text("Field", buffer)
        if imgui.is_item_active():
            print("Field is active")
        ```
    """
    ...

def is_item_visible() -> Any:
    """Check if the last item is visible (not clipped).

    Returns:
        bool: True if visible.

    Example:     
        ```python
        if imgui.is_item_visible():
            print("Item is visible")
        ```
    """
    ...

def is_item_activated() -> Any:
    """Check if the item was just activated (e.g., clicked or focused).

    Returns:
        bool: True if activated.

    Example:     
        ```python
        imgui.button("Click me")
        if imgui.is_item_activated():
            print("Button was activated")
        ```
    """
    ...

def is_item_deactivated_after_edit() -> Any:
    """Check if the item was edited and then deactivated.

    Returns:
        bool: True if edited and deactivated.

    Example:     
        ```python
        imgui.input_float("Value", value)
        if imgui.is_item_deactivated_after_edit():
            print("Value changed")
        ```
    """
    ...

def is_any_item_hovered() -> Any:
    """Check if any item is currently hovered.

    Returns:
        bool: True if any item is hovered.

    Example:     
        ```python
        if imgui.is_any_item_hovered():
            print("An item is hovered")
        ```
    """
    ...

def is_any_item_focused() -> Any:
    """Check if any item is focused.

    Returns:
        bool: True if any item is focused.

    Example:     
        ```python
        if imgui.is_any_item_focused():
            print("An item is focused")
        ```
    """
    ...

def get_item_rect_max() -> Any:
    """Get the bottom-right corner of the last item.

    Returns:
        Tuple[float, float]: (x, y) coordinates.

    Example:     
        ```python
        imgui.button("Check")
        max_x, max_y = imgui.get_item_rect_max()
        print(f"Bottom-right at: {max_x}, {max_y}")
        ```
    """
    ...

def set_item_allow_overlap() -> Any:
    """Allow the last item to be overlapped by other widgets.

    Example:     
        ```python
        imgui.set_item_allow_overlap()
        ```
    """
    ...

def get_window_viewport() -> Any:
    """Get the current window's viewport.

    Returns:
        Viewport: The window's viewport object.

    Example:     
        ```python
        viewport = imgui.get_window_viewport()
        print(viewport.size)
        ```
    """
    ...

def get_style_color_name(index: int) -> Any:
    """Get the name of a style color by index.

    Args:
        index (int): Style color index.

    Returns:
        str: Name of the style color.

    Example:     
        ```python
        print(imgui.get_style_color_name(imgui.COLOR_BUTTON))
        ```
    """
    ...

def get_background_draw_list() -> Any:
    """Get draw list for background layer.

    Returns:
        DrawList: The background draw list.

    Example:     
        ```python
        draw_list = imgui.get_background_draw_list()
        draw_list.add_text((10, 10), imgui.COLOR_WHITE, "Overlay Text")
        ```
    """
    ...

def get_key_index(key: int) -> Any:
    """Convert ImGui key enum to index.

    Args:
        key (int): ImGui key code.

    Returns:
        int: Internal index.

    Example:     
        ```python
        index = imgui.get_key_index(imgui.KEY_A)
        ```
    """
    ...

def is_key_down(key_index: int) -> Any:
    """Check if key is currently held down.

    Args:
        key_index (int): Key index.

    Returns:
        bool: True if the key is down.

    Example:     
        ```python
        if imgui.is_key_down(imgui.get_key_index(imgui.KEY_SPACE)):
            print("Space is down")
        ```
    """
    ...

def is_mouse_clicked(button: int = 0, repeat: bool = False) -> Any:
    """Check if a mouse button was clicked.

    Args:
        button (int): Mouse button index.
        repeat (bool): Whether to repeat.

    Returns:
        bool: True if clicked.

    Example:     
        ```python
        if imgui.is_mouse_clicked(0):
            print("Left mouse clicked")
        ```
    """
    ...

def is_mouse_down(button: int = 0) -> Any:
    """Check if a mouse button is held down.

    Args:
        button (int): Mouse button index.

    Returns:
        bool: True if the button is held.

    Example:     
        ```python
        if imgui.is_mouse_down(1):
            print("Right mouse down")
        ```
    """
    ...

def get_mouse_drag_delta(button: int = 0, lock_threshold: float = -1.0) -> Any:
    """Get the mouse drag delta from the time the button was pressed.

    Args:
        button (int): Mouse button index.
        lock_threshold (float): Movement threshold.

    Returns:
        Tuple[float, float]: Drag delta.

    Example:     
        ```python
        dx, dy = imgui.get_mouse_drag_delta()
        print(f"Dragged: dx={dx}, dy={dy}")
        ```
    """
    ...

def reset_mouse_drag_delta(button: int = 0) -> Any:
    """Reset the drag delta for the specified mouse button.

    Args:
        button (int): Mouse button index.

    Example:     
        ```python
        imgui.reset_mouse_drag_delta()
        ```
    """
    ...

def set_mouse_cursor(mouse_cursor_type: Any) -> Any:
    """Change the mouse cursor.

    Args:
        mouse_cursor_type: Cursor type, e.g., imgui.MOUSE_CURSOR_HAND.

    Example:     
        ```python
        imgui.set_mouse_cursor(imgui.MOUSE_CURSOR_TEXT_INPUT)
        ```
    """
    ...

def get_clipboard_text() -> Any:
    """Get text from the system clipboard.

    Returns:
        str: Clipboard text.

    Example:     
        ```python
        text = imgui.get_clipboard_text()
        print(text)
        ```
    """
    ...

def load_ini_settings_from_memory(ini_data: str) -> Any:
    """Load settings from memory (INI format).

    Args:
        ini_data (str): INI-formatted settings string.

    Example:     
        ```python
        imgui.load_ini_settings_from_memory("[Window][Example]\nPos=60,60\n")
        ```
    """
    ...

def save_ini_settings_to_memory() -> Any:
    """Save current settings to a memory string.

    Returns:
        str: INI-formatted settings string.

    Example:     
        ```python
        ini_data = imgui.save_ini_settings_to_memory()
        print(ini_data)
        ```
    """
    ...

def set_scroll_here_y(center_y_ratio: float = 0.5) -> Any:
    """Scroll to current item on the Y-axis.

    Args:
        center_y_ratio (float): Position of the item in the view.

    Example:     
        ```python
        imgui.set_scroll_here_y(0.0)
        ```
    """
    ...

def set_scroll_from_pos_y(local_y: float, center_y_ratio: float = 0.5) -> Any:
    """Scroll to a Y position from a local offset.

    Args:
        local_y (float): Local Y offset.
        center_y_ratio (float): Scroll target ratio.

    Example:     
        ```python
        imgui.set_scroll_from_pos_y(100.0)
        ```
    """
    ...

def pop_font() -> Any:
    """Pop the last pushed font from the stack.

    Example:     
        ```python
        imgui.pop_font()
        ```
    """
    ...

def calc_text_size(text: str, hide_text_after_double_hash: bool = False, wrap_width: float = -1.0) -> Any:
    """Calculate size of given text.

    Args:
        text (str): Text to measure.
        hide_text_after_double_hash (bool): Ignore text after '##'.
        wrap_width (float): Wrap width.

    Returns:
        Tuple[float, float]: (width, height)

    Example:     
        ```python
        w, h = imgui.calc_text_size("Example Text")
        print(w, h)
        ```
    """
    ...

def color_convert_float4_to_u32(r: float, g: float, b: float, a: float) -> Any:
    """Convert RGBA floats to packed 32-bit integer.

    Args:
        r, g, b, a (float): Color components.

    Returns:
        int: Packed color.

    Example:     
        ```python
        color = imgui.color_convert_float4_to_u32(1.0, 0.0, 0.0, 1.0)
        ```
    """
    ...

def color_convert_hsv_to_rgb(h: float, s: float, v: float) -> Any:
    """Convert HSV to RGB color.

    Args:
        h, s, v (float): HSV components.

    Returns:
        Tuple[float, float, float]: RGB values.

    Example:     
        ```python
        r, g, b = imgui.color_convert_hsv_to_rgb(0.5, 1.0, 1.0)
        ```
    """
    ...

def push_style_var(variable: Any, value) -> Any:
    """Push a style variable onto the stack.

    Args:
        variable: Style variable ID.
        value: New value.

    Example:     
        ```python
        imgui.push_style_var(imgui.STYLE_ALPHA, 0.5)
        ```
    """
    ...

def pop_style_var(count: int = 1) -> Any:
    """Pop style variable(s) from the stack.

    Args:
        count (int): Number of variables to pop.

    Example:     
        ```python
        imgui.pop_style_var()
        ```
    """
    ...

def get_font_size() -> Any:
    """Get the current font size.

    Returns:
        float: Font size.

    Example:     
        ```python
        size = imgui.get_font_size()
        print(size)
        ```
    """
    ...

def get_style_color_vec_4(idx: Any) -> Any:
    """Get style color as a float4 vector.

    Args:
        idx: Color index.

    Returns:
        Tuple[float, float, float, float]: RGBA

    Example:     
        ```python
        color = imgui.get_style_color_vec_4(imgui.COLOR_TEXT)
        ```
    """
    ...

def get_font_tex_uv_white_pixel() -> Any:
    """Get the UV of the white pixel in font texture.

    Returns:
        Tuple[float, float]: UV coordinates.

    Example:     
        ```python
        uv = imgui.get_font_tex_uv_white_pixel()
        ```
    """
    ...

def get_color_u32_idx(idx: Any, alpha_mul: float = 1.0) -> Any:
    """Get color as packed u32 from color index.

    Args:
        idx: Style color index.
        alpha_mul (float): Alpha multiplier.

    Returns:
        int: Packed color.

    Example:     
        ```python
        color = imgui.get_color_u32_idx(imgui.COLOR_TEXT)
        ```
    """
    ...

def get_color_u32_rgba(r: float, g: float, b: float, a: float) -> Any:
    """Get packed color u32 from RGBA floats.

    Args:
        r, g, b, a (float): Color values.

    Returns:
        int: Packed color.

    Example:     
        ```python
        color = imgui.get_color_u32_rgba(1.0, 0.5, 0.0, 1.0)
        ```
    """
    ...

def get_color_u32(col: int) -> Any:
    """Return color unchanged (for API consistency).

    Args:
        col (int): Color.

    Returns:
        int: Same value.

    Example:     
        ```python
        color = imgui.get_color_u32(0xff0000ff)
        ```
    """
    ...

def push_item_width(item_width: float) -> Any:
    """Set width of upcoming items.

    Args:
        item_width (float): Width to set.

    Example:     
        ```python
        imgui.push_item_width(200)
        ```
    """
    ...

def pop_item_width() -> Any:
    """Restore item width to previous value.

    Example:     
        ```python
        imgui.pop_item_width()
        ```
    """
    ...

def set_next_item_width(item_width: float) -> Any:
    """Set width for the next item only.

    Args:
        item_width (float): Width in pixels.

    Example:     
        ```python
        imgui.set_next_item_width(150)
        imgui.input_text("Field", buffer)
        ```
    """
    ...

def calculate_item_width() -> Any:
    """Calculate current item width.

    Returns:
        float: Width.

    Example:     
        ```python
        width = imgui.calculate_item_width()
        ```
    """
    ...

def push_text_wrap_pos(wrap_pos_x: float = 0.0) -> Any:
    """Push wrapping width for text.

    Args:
        wrap_pos_x (float): Wrap width.

    Example:     
        ```python
        imgui.push_text_wrap_pos(300)
        ```
    """
    ...

def pop_text_wrap_pos() -> Any:
    """Pop the last text wrap position.

    Example:     
        ```python
        imgui.pop_text_wrap_pos()
        ```
    """
    ...

def push_allow_keyboard_focus(allow_focus: bool) -> Any:
    """Set whether next item can be focused with keyboard.

    Args:
        allow_focus (bool): Allow or disallow.

    Example:     
        ```python
        imgui.push_allow_keyboard_focus(False)
        ```
    """
    ...

def pop_allow_keyboard_focus() -> Any:
    """Restore previous keyboard focus state.

    Example:     
        ```python
        imgui.pop_allow_keyboard_focus()
        ```
    """
    ...

def push_button_repeat(repeat: bool) -> Any:
    """Set button repeat behavior when held.

    Args:
        repeat (bool): Enable repeat.

    Example:     
        ```python
        imgui.push_button_repeat(True)
        ```
    """
    ...

def pop_button_repeat() -> Any:
    """Restore button repeat behavior.

    Example:     
        ```python
        imgui.pop_button_repeat()
        ```
    """
    ...

def pop_style_color(count: int = 1) -> Any:
    """Pop one or more color styles.

    Args:
        count (int): Number of colors to pop.

    Example:     
        ```python
        imgui.pop_style_color()
        ```
    """
    ...

def same_line(position: float = 0.0, spacing: float = -1.0) -> Any:
    """Keep next item on same horizontal line.

    Args:
        position (float): X position (optional).
        spacing (float): Spacing (optional).

    Example:     
        ```python
        imgui.text("Label:")
        imgui.same_line()
        imgui.input_text("##field", buffer)
        ```
    """
    ...

def spacing() -> Any:
    """Insert vertical spacing.

    Example:     
        ```python
        imgui.spacing()
        ```
    """
    ...

def indent(width: float = 0.0) -> Any:
    """Increase the horizontal indentation level.

    Args:
        width (float): Custom indentation width.

    Example:     
        ```python
        imgui.indent()
        imgui.text("Indented")
        ```
    """
    ...

def columns(count: int = 1, identifier: str = None, border: bool = True) -> Any:
    """Create horizontal columns.

    Args:
        count (int): Number of columns.
        identifier (str): Optional ID.
        border (bool): Show border.

    Example:     
        ```python
        imgui.columns(2)
        imgui.text("Column 1")
        imgui.next_column()
        imgui.text("Column 2")
        imgui.columns(1)
        ```
    """
    ...

def get_column_index() -> Any:
    """Get current column index.

    Returns:
        int: Column index.

    Example:     
        ```python
        col = imgui.get_column_index()
        ```
    """
    ...

def set_column_offset(column_index: int, offset_x: float) -> Any:
    """Set horizontal offset of a column.

    Args:
        column_index (int): Index.
        offset_x (float): Offset in pixels.

    Example:     
        ```python
        imgui.set_column_offset(1, 100.0)
        ```
    """
    ...

def set_column_width(column_index: int, width: float) -> Any:
    """Set width of a column.

    Args:
        column_index (int): Column index.
        width (float): Desired width.

    Example:     
        ```python
        imgui.set_column_width(0, 150.0)
        ```
    """
    ...

def begin_tab_bar( identifier: str, flags: Any = 0) -> Any:
    """Begin a tab bar container.
    
    Args:
        identifier (str): Unique identifier for the tab bar
        flags (int): Additional flags for the tab bar
        
    Returns:
        bool: True if the tab bar is open
        
    Example:     
        ```python
        if imgui.begin_tab_bar("MyTabBar"):
            if imgui.begin_tab_item("Tab 1"):
                imgui.text("Content of tab 1")
                imgui.end_tab_item()
            if imgui.begin_tab_item("Tab 2"):
                imgui.text("Content of tab 2")
                imgui.end_tab_item()
            imgui.end_tab_bar()
        ```
    """
    ...
def begin_tab_item( label: str,opened: Any = None, flags: Any = 0) -> Any:
    """Begin a tab item in the current tab bar.
    
    Args:
        label (str): Label for the tab
        opened (bool): Optional reference to store the open/closed state
        flags (int): Additional flags for the tab
        
    Returns:
        bool: True if the tab is selected
        
    Example:     
        ```python
        if imgui.begin_tab_bar("Tabs"):
            if imgui.begin_tab_item("Settings"):
                imgui.checkbox("Enable Feature", True)
                imgui.end_tab_item()
            if imgui.begin_tab_item("About"):
                imgui.text("Version 1.0")
                imgui.end_tab_item()
            imgui.end_tab_bar()
        ```
    """
    ...
def tab_item_button(label: str, flags: Any = 0) -> Any:
    """Create a tab-like button that behaves like a tab.

    This is useful for custom tab bars when not using `begin_tab_bar()`.

    Args:
        label (str): Label to display on the tab.
        flags: Optional flags, e.g., imgui.TAB_ITEM_ALWAYS_AUTO_RESIZE.

    Returns:
        bool: True if the button was clicked.

    Example:     
        ```python
        if imgui.tab_item_button("Settings"):
            print("Settings tab clicked")
        ```
    """
    ...


def get_window_dock_id() -> Any:
    """Retrieve the docking ID of the current window.

    Returns:
        int: Docking ID of the current window (0 if not docked).

    Example:     
        ```python
        dock_id = imgui.get_window_dock_id()
        print(f"Window dock ID: {dock_id}")
        ```
    """
    ...

def begin_drag_drop_source( flags: Any = 0) -> Any:
    """Begin a drag and drop source operation.
    
    Args:
        flags (int): Additional flags for the drag source
        
    Returns:
        bool: True if the drag source is active
        
    Example:     
        ```python
        if imgui.begin_drag_drop_source():
            imgui.set_drag_drop_payload("ITEM", "data", 0)
            imgui.text("Drag me!")
            imgui.end_drag_drop_source()
        ```
    """
    ...
def end_drag_drop_source() -> Any:
    """End a drag and drop source context.

    This should be called after `begin_drag_drop_source()` to finalize the drag source definition.

    Returns:
        None

    Example:     
        ```python
        if imgui.begin_drag_drop_source():
            imgui.text("Dragging item")
            imgui.set_drag_drop_payload("MY_PAYLOAD", b"123", 3)
            imgui.end_drag_drop_source()
        ```
    """
    ...

def accept_drag_drop_payload( type: str, flags: Any = 0) -> Any:
    """Accept a drag and drop payload of the specified type.
    
    Args:
        type (str): Type identifier to accept
        flags (int): Additional flags
        
    Returns:
        Any: The payload data if accepted, None otherwise
        
    Example:     
        ```python
        if imgui.begin_drag_drop_target():
            if payload := imgui.accept_drag_drop_payload("ITEM"):
                print(f"Received: {payload}")
            imgui.end_drag_drop_target()
        ```
    """
    ...
def get_drag_drop_payload() -> Any: ...
def begin_group() -> Any: ...
def get_cursor_pos() -> Any: ...
def get_cursor_pos_y() -> Any: ...
def set_cursor_pos_x( x: float) -> Any: ...
def get_cursor_start_pos() -> Any: ...
def get_text_line_height() -> Any: ...
def get_frame_height() -> Any: ...
def create_context( shared_font_atlas: Any = None) -> Any: ...
def get_current_context() -> Any: ...
def push_id( str_id: str) -> Any: ...
def get_id( str_id: str) -> Any: ...
def _ansifeed_text_ansi_colored( text: str, r: float, g: float, b: float, a: float = 1.) -> Any: ...
def _py_vertex_buffer_vertex_pos_offset() -> Any: ...
def _py_vertex_buffer_vertex_col_offset() -> Any: ...
def _py_index_buffer_index_size() -> Any: ...
def destroy_platform_windows() -> Any: ...
def find_viewport_by_platform_handle( platform_handle: Any) -> Any: ...
def find_viewport_by_id( id: Any) -> Any: ...


class GlyphRanges(object):
	pass

class GuiStyle(object):
	def alpha(self) -> Any: ...
	def window_padding(self) -> Any: ...
	def window_min_size(self) -> Any: ...
	def window_rounding(self) -> Any: ...
	def window_border_size(self) -> Any: ...
	def child_rounding(self) -> Any: ...
	def child_border_size(self) -> Any: ...
	def popup_rounding(self) -> Any: ...
	def popup_border_size(self) -> Any: ...
	def window_title_align(self) -> Any: ...
	def window_menu_button_position(self) -> Any: ...
	def frame_padding(self) -> Any: ...
	def frame_rounding(self) -> Any: ...
	def frame_border_size(self) -> Any: ...
	def item_spacing(self) -> Any: ...
	def item_inner_spacing(self) -> Any: ...
	def cell_padding(self) -> Any: ...
	def touch_extra_padding(self) -> Any: ...
	def indent_spacing(self) -> Any: ...
	def columns_min_spacing(self) -> Any: ...
	def scrollbar_size(self) -> Any: ...
	def scrollbar_rounding(self) -> Any: ...
	def grab_min_size(self) -> Any: ...
	def grab_rounding(self) -> Any: ...
	def log_slider_deadzone(self) -> Any: ...
	def tab_rounding(self) -> Any: ...
	def tab_border_size(self) -> Any: ...
	def tab_min_width_for_close_button(self) -> Any: ...
	def color_button_position(self) -> Any: ...
	def button_text_align(self) -> Any: ...
	def selectable_text_align(self) -> Any: ...
	def display_window_padding(self) -> Any: ...
	def display_safe_area_padding(self) -> Any: ...
	def mouse_cursor_scale(self) -> Any: ...
	def anti_aliased_lines(self) -> Any: ...
	def anti_aliased_line_use_tex(self) -> Any: ...
	def anti_aliased_fill(self) -> Any: ...
	def curve_tessellation_tolerance(self) -> Any: ...
	def circle_segment_max_error(self) -> Any: ...
	def circle_tessellation_max_error(self) -> Any: ...
	def color(self, variable: Any) -> Any: ...
	def colors(self) -> Any: ...
	def scale_all_sizes(self, scale_factor: float) -> Any: ...
	def create() -> Any: ...

class ImGuiWindowClass(object):
	def _require_pointer(self) -> Any: ...
	def class_id(self) -> Any: ...
	def viewport_flags_override_set(self) -> Any: ...
	def tab_item_flags_override_set(self) -> Any: ...
	def docking_always_tab_bar(self) -> Any: ...
	def imgui_window_class(self) -> Any: ...
	def from_ptr( ptr: Any) -> Any: ...
	def parent_viewport_id(self) -> Any: ...
	def viewport_flags_override_clear(self) -> Any: ...
	def docknode_flags_override_set(self) -> Any: ...
	def docking_allow_unclassed(self) -> Any: ...

class _Colors(object):
	pass

class _DrawCmd(object):
	def texture_id(self) -> Any: ...
	def elem_count(self) -> Any: ...
	def from_ptr( ptr: Any) -> Any: ...
	def clip_rect(self) -> Any: ...

class _DrawData(object):
	def _require_pointer(self) -> Any: ...
	def deindex_all_buffers(self) -> Any: ...
	def valid(self) -> Any: ...
	def total_vtx_count(self) -> Any: ...
	def display_size(self) -> Any: ...
	def total_idx_count(self) -> Any: ...
	def owner_viewport(self) -> Any: ...
	def from_ptr( ptr: Any) -> Any: ...
	def scale_clip_rects(self,width,height) -> Any: ...
	def cmd_count(self) -> Any: ...
	def display_pos(self) -> Any: ...
	def frame_buffer_scale(self) -> Any: ...
	def commands_lists(self) -> Any: ...

class _DrawList(object):
	def cmd_buffer_size(self) -> Any: ...
	def vtx_buffer_size(self) -> Any: ...
	def idx_buffer_size(self) -> Any: ...
	def flags(self) -> Any: ...
	def push_clip_rect(self, clip_rect_min_x: float, clip_rect_min_y: float, clip_rect_max_x: float, clip_rect_max_y: float, intersect_with_current_clip_rect: bool = False) -> Any: ...
	def push_clip_rect_full_screen(self) -> Any: ...
	def push_texture_id(self,texture_id) -> Any: ...
	def get_clip_rect_min(self) -> Any: ...
	def add_line(self, start_x: float, start_y: float, end_x: float, end_y: float, col: int, thickness: float = 1.0,) -> Any: ...
	def add_rect(self, upper_left_x: float, upper_left_y: float, lower_right_x: float, lower_right_y: float, col: int, rounding: float = 0.0, flags: Any = 0, thickness: float = 1.0,) -> Any: ...
	def add_rect_filled(self, upper_left_x: float, upper_left_y: float, lower_right_x: float, lower_right_y: float, col: int, rounding: float = 0.0, flags: Any = 0,) -> Any: ...
	def add_circle(self, centre_x: float, centre_y: float, radius: float, col: int, num_segments: int = 0, thickness: float = 1.0) -> Any: ...
	def add_circle_filled(self, centre_x: float, centre_y: float, radius: float, col: int, num_segments: int = 0) -> Any: ...
	def add_ngon(self, centre_x: float, centre_y: float, radius: float, col: int, num_segments: int, thickness: float = 1.0) -> Any: ...
	def add_ngon_filled(self, centre_x: float, centre_y: float, radius: float, col: int, num_segments: int) -> Any: ...
	def add_text(self, pos_x: float, pos_y: float, col: int, text: str) -> Any: ...
	def add_image(self,texture_id, a: Any, b: Any, uv_a: Any = (0,0), uv_b: Any = (1,1), col: int = 0xffffffff) -> Any: ...
	def add_polyline(self, points: Any, col: int, flags: Any = 0, thickness: float = 1.0) -> Any: ...
	def channels_split(self, channels_count: int) -> Any: ...
	def channels_merge(self) -> Any: ...
	def prim_unreserve(self, idx_count: int, vtx_count: int) -> Any: ...
	def prim_write_vtx(self, pos_x: float, pos_y: float, u: float, v: float, color: int = 0xFFFFFFFF) -> Any: ...
	def prim_vtx(self, pos_x: float, pos_y: float, u: float, v: float, color: int = 0xFFFFFFFF) -> Any: ...
	def from_ptr( ptr: Any) -> Any: ...
	def cmd_buffer_data(self) -> Any: ...
	def vtx_buffer_data(self) -> Any: ...
	def idx_buffer_data(self) -> Any: ...
	def pop_texture_id(self) -> Any: ...
	def get_clip_rect_max(self) -> Any: ...
	def channels_set_current(self, idx: int) -> Any: ...
	def prim_reserve(self, idx_count: int, vtx_count: int) -> Any: ...
	def prim_rect(self, a_x: float, a_y: float, b_x: float, b_y: float, color: int = 0xFFFFFFFF) -> Any: ...
	def prim_write_idx(self, idx: Any) -> Any: ...
	def commands(self) -> Any: ...

class _Font(object):
	def from_ptr( ptr: Any) -> Any: ...

class _FontAtlas(object):
	def _require_pointer(self) -> Any: ...
	def add_font_from_file_ttf(self, filename: str, size_pixels: float,font_config: Any = None,glyph_ranges: Any = None) -> Any: ...
	def clear_tex_data(self) -> Any: ...
	def clear_fonts(self) -> Any: ...
	def get_glyph_ranges_default(self) -> Any: ...
	def get_glyph_ranges_japanese(self) -> Any: ...
	def get_glyph_ranges_chinese(self) -> Any: ...
	def get_glyph_ranges_thai(self) -> Any: ...
	def get_glyph_ranges_latin(self) -> Any: ...
	def get_tex_data_as_rgba32(self) -> Any: ...
	def texture_width(self) -> Any: ...
	def texture_id(self,value) -> Any: ...
	def from_ptr( ptr: Any) -> Any: ...
	def add_font_default(self) -> Any: ...
	def clear_input_data(self) -> Any: ...
	def clear(self) -> Any: ...
	def get_glyph_ranges_korean(self) -> Any: ...
	def get_glyph_ranges_chinese_full(self) -> Any: ...
	def get_glyph_ranges_cyrillic(self) -> Any: ...
	def get_glyph_ranges_vietnamese(self) -> Any: ...
	def get_tex_data_as_alpha8(self) -> Any: ...
	def texture_height(self) -> Any: ...

class _IO(object):
	def config_flags(self) -> Any: ...
	def backend_flags(self) -> Any: ...
	def display_size(self) -> Any: ...
	def delta_time(self) -> Any: ...
	def ini_saving_rate(self) -> Any: ...
	def log_file_name(self) -> Any: ...
	def ini_file_name(self) -> Any: ...
	def mouse_double_click_time(self) -> Any: ...
	def mouse_double_click_max_distance(self) -> Any: ...
	def mouse_drag_threshold(self) -> Any: ...
	def key_map(self) -> Any: ...
	def key_repeat_delay(self, value: float) -> Any: ...
	def key_repeat_rate(self, value: float) -> Any: ...
	def font_global_scale(self) -> Any: ...
	def font_allow_user_scaling(self) -> Any: ...
	def display_fb_scale(self) -> Any: ...
	def config_mac_osx_behaviors(self) -> Any: ...
	def config_cursor_blink(self) -> Any: ...
	def config_drag_click_to_input_text(self) -> Any: ...
	def config_windows_resize_from_edges(self) -> Any: ...
	def config_windows_move_from_title_bar_only(self) -> Any: ...
	def config_memory_compact_timer(self) -> Any: ...
	def get_clipboard_text_fn(self) -> Any: ...
	def set_clipboard_text_fn(self) -> Any: ...
	def mouse_pos(self) -> Any: ...
	def mouse_down(self) -> Any: ...
	def mouse_wheel(self, value: float) -> Any: ...
	def mouse_wheel_horizontal(self, value: float) -> Any: ...
	def mouse_draw_cursor(self, value: bool) -> Any: ...
	def key_ctrl(self, value: bool) -> Any: ...
	def key_shift(self, value: bool) -> Any: ...
	def key_alt(self, value: bool) -> Any: ...
	def key_super(self, value: bool) -> Any: ...
	def nav_inputs(self) -> Any: ...
	def add_input_character_utf16(self, utf16_chars: str) -> Any: ...
	def clear_input_characters(self) -> Any: ...
	def want_capture_keyboard(self) -> Any: ...
	def want_set_mouse_pos(self) -> Any: ...
	def nav_active(self) -> Any: ...
	def framerate(self) -> Any: ...
	def metrics_render_indices(self) -> Any: ...
	def metrics_active_windows(self) -> Any: ...
	def mouse_delta(self) -> Any: ...
	def config_docking_with_shift(self) -> Any: ...
	def config_docking_transparent_payload(self) -> Any: ...
	def config_viewports_no_task_bar_icon(self) -> Any: ...
	def config_viewports_no_default_parent(self) -> Any: ...
	def fonts(self) -> Any: ...
	def keys_down(self) -> Any: ...
	def add_input_character(self, c: int) -> Any: ...
	def add_input_characters_utf8(self, utf8_chars: str) -> Any: ...
	def want_capture_mouse(self) -> Any: ...
	def want_text_input(self) -> Any: ...
	def want_save_ini_settings(self) -> Any: ...
	def nav_visible(self) -> Any: ...
	def metrics_render_vertices(self) -> Any: ...
	def metrics_render_windows(self) -> Any: ...
	def metrics_active_allocations(self) -> Any: ...
	def config_docking_no_split(self) -> Any: ...
	def config_docking_always_tab_bar(self) -> Any: ...
	def config_viewports_no_auto_merge(self) -> Any: ...
	def config_viewports_no_decoration(self) -> Any: ...
	def mouse_hovered_viewport(self) -> Any: ...
	def populate(self,callback_fn,user_data) -> Any: ...

class _ImGuiContext(object):
	def from_ptr( ptr: Any) -> Any: ...

class _ImGuiInputTextCallbackData(object):
	def _require_pointer(self) -> Any: ...
	def flags(self) -> Any: ...
	def event_char(self) -> Any: ...
	def event_key(self) -> Any: ...
	def buffer_text_length(self) -> Any: ...
	def buffer_dirty(self) -> Any: ...
	def cursor_pos(self) -> Any: ...
	def selection_start(self) -> Any: ...
	def selection_end(self) -> Any: ...
	def delete_chars(self, pos: int, bytes_count: int) -> Any: ...
	def select_all(self) -> Any: ...
	def has_selection(self) -> Any: ...
	def from_ptr( ptr: Any) -> Any: ...
	def event_flag(self) -> Any: ...
	def user_data(self) -> Any: ...
	def buffer(self) -> Any: ...
	def buffer_size(self) -> Any: ...
	def insert_chars(self, pos: int, text: str) -> Any: ...
	def clear_selection(self) -> Any: ...

class _ImGuiPayload(object):
	def _require_pointer(self) -> Any: ...
	def data(self) -> Any: ...
	def is_preview(self) -> Any: ...
	def is_data_type(self, type: str) -> Any: ...
	def from_ptr( ptr: Any) -> Any: ...
	def data_size(self) -> Any: ...
	def is_delivery(self) -> Any: ...

class _ImGuiSizeCallbackData(object):
	def _require_pointer(self) -> Any: ...
	def pos(self) -> Any: ...
	def desired_size(self) -> Any: ...
	def from_ptr( ptr: Any) -> Any: ...
	def user_data(self) -> Any: ...
	def current_size(self) -> Any: ...

class _ImGuiTableColumnSortSpecs(object):
	def _require_pointer(self) -> Any: ...
	def column_user_id(self) -> Any: ...
	def column_index(self) -> Any: ...
	def sort_order(self) -> Any: ...
	def sort_direction(self) -> Any: ...
	def from_ptr( ptr: Any) -> Any: ...
	def from_ptr( ptr: Any) -> Any: ...
	def _get_item(self, idx: Any) -> Any: ...

class _ImGuiTableColumnSortSpecs_array(object):
	pass

class _ImGuiTableSortSpecs(object):
	def specs(self) -> Any: ...
	def specs_dirty(self) -> Any: ...
	def from_ptr( ptr: Any) -> Any: ...
	def specs_count(self) -> Any: ...

class _ImGuiViewport(object):
	def id(self) -> Any: ...
	def dpi_scale(self) -> Any: ...
	def pos(self) -> Any: ...
	def work_pos(self) -> Any: ...
	def draw_data(self) -> Any: ...
	def platform_request_resize(self) -> Any: ...
	def platform_request_close(self) -> Any: ...
	def get_work_center(self) -> Any: ...
	def from_ptr( ptr: Any) -> Any: ...
	def parent_viewport_id(self) -> Any: ...
	def size(self) -> Any: ...
	def work_size(self) -> Any: ...
	def platform_request_move(self) -> Any: ...
	def get_center(self) -> Any: ...

class _StaticGlyphRanges(object):
	def from_ptr( ptr: Any) -> Any: ...

class _callback_user_info(object):
	pass

# Additional custom functions using the imgui module as the namespace
def get_color_rgb(col_imU32):
    """Extract RGBA components from an ImGui color value.
    
    Args:
        col_imU32 (int): ImGui color value in U32 format
        
    Returns:
        tuple: (r, g, b, a) values in range 0-255
        
    Example:
        ```python
        color = imgui.get_color_rgb(imgui.COLOR_BUTTON)
        r, g, b, a = color
        print(f"Color components: R={r}, G={g}, B={b}, A={a}")
        ```
    """
...
def create_table(table_id: str, headers: list, rows: list, flags: int = 0) -> bool:
    """Creates and renders an ImGui table with the specified headers and rows.
    
    Args:
        table_id (str): Unique identifier for the table
        headers (list): List of column headers
        rows (list): List of rows, where each row is a list of cells
        flags (int, optional): ImGui table flags. Defaults to 0
    
    Returns:
        bool: True if table was created and rendered successfully
        
    Example:
        ```python
        headers = ["Name", "Age", "City"]
        rows = [
            ["John", "25", "New York"],
            ["Alice", "30", "London"]
        ]
        imgui.create_table("my_table", headers, rows)
        ```
    """
...
def image_button_with_text(text, image, button_size, image_size, text_offset=(0, 0), image_offset=(0, 0), is_active=False, image_when_hovered=None):
    """Create a button with both text and an image.
    
    Args:
        text (str): Text to display on the button
        image (int): OpenGL texture ID for the main image
        button_size (tuple): Size of the button (width, height)
        image_size (tuple): Size of the image (width, height)
        text_offset (tuple): Offset for text position (x, y) where:
            x: 0 = left, 0.5 = center, 1 = right
            y: 0 = top, 0.5 = center, 1 = bottom
        image_offset (tuple): Offset for image position (x, y)
        is_active (bool): Whether the button is in active state
        image_when_hovered (int, optional): OpenGL texture ID for hover state
        
    Returns:
        bool: True if button was clicked
        
    Example:
        ```python
        # Assuming texture_id is a valid OpenGL texture ID
        clicked = imgui.image_button_with_text(
            "Click Me",
            texture_id,
            button_size=(100, 50),
            image_size=(32, 32),
            text_offset=(0.5, 0.5),  # Center text
            image_offset=(0, 0)
        )
        if clicked:
            print("Button was clicked!")
        ```
    """
...
def slider_float2(label: str, values: list, min_val: float = 0.0, max_val: float = 1.0, format: str = "%.3f", flags: int = 0) -> tuple[bool, list]:
    """Create a slider for 2 float values.
    
    Args:
        label (str): Label for the slider
        values (list): List of 2 float values [x, y]
        min_val (float): Minimum value
        max_val (float): Maximum value
        format (str): Format string for display
        flags (int): ImGui slider flags
        
    Returns:
        tuple: (changed, new_values) where changed is bool and new_values is list[float]
        
    Example:
        ```python
        values = [0.5, 0.7]
        changed, new_values = imgui.slider_float2(
            "Position",
            values,
            min_val=0.0,
            max_val=1.0
        )
        if changed:
            x, y = new_values
            print(f"New position: ({x}, {y})")
        ```
    """
...
def slider_float3(label: str, values: list, min_val: float = 0.0, max_val: float = 1.0, format: str = "%.3f", flags: int = 0) -> tuple[bool, list]:
    """Create a slider for 3 float values.
    
    Args:
        label (str): Label for the slider
        values (list): List of 3 float values [x, y, z]
        min_val (float): Minimum value
        max_val (float): Maximum value
        format (str): Format string for display
        flags (int): ImGui slider flags
        
    Returns:
        tuple: (changed, new_values) where changed is bool and new_values is list[float]
        
    Example:
        ```python
        values = [0.5, 0.7, 0.3]
        changed, new_values = imgui.slider_float3(
            "Color",
            values,
            min_val=0.0,
            max_val=1.0
        )
        if changed:
            r, g, b = new_values
            print(f"New color: RGB({r}, {g}, {b})")
        ```
    """
...
def slider_float4(label: str, values: list, min_val: float = 0.0, max_val: float = 1.0, format: str = "%.3f", flags: int = 0) -> tuple[bool, list]:
    """Create a slider for 4 float values.
    
    Args:
        label (str): Label for the slider
        values (list): List of 4 float values [x, y, z, w]
        min_val (float): Minimum value
        max_val (float): Maximum value
        format (str): Format string for display
        flags (int): ImGui slider flags
        
    Returns:
        tuple: (changed, new_values) where changed is bool and new_values is list[float]
        
    Example:
        ```python
        values = [0.5, 0.7, 0.3, 1.0]
        changed, new_values = imgui.slider_float4(
            "Transform",
            values,
            min_val=0.0,
            max_val=1.0
        )
        if changed:
            x, y, z, w = new_values
            print(f"New transform: ({x}, {y}, {z}, {w})")
        ```
    """
...