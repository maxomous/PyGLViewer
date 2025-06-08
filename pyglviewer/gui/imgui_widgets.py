import imgui

    
# Additional functions using the imgui module as the namespace
# e.g. imgui.some_function()

def imgui_method(func):
    """Decorator to automatically add a function to the imgui module"""
    original_func = getattr(imgui, func.__name__, None)  # Store the original function
    setattr(imgui, f"_{func.__name__}_original", original_func)  # Save it with a new name
    setattr(imgui, func.__name__, func)  # Set our new function
    return func

@imgui_method
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
    if imgui.begin_table(table_id, len(headers), flags):
        for header in headers:
            imgui.table_setup_column(header, imgui.TABLE_COLUMN_WIDTH_STRETCH)
        
        if flags & imgui.TABLE_ROW_HEADERS:
            imgui.table_headers_row()
        
        for row in rows:
            imgui.table_next_row()
            for cell in row:
                imgui.table_next_column()
                imgui.text(str(cell))
        
        imgui.end_table()
        return True
    return False 

@imgui_method
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
        is_active (bool): Whether the button is in active state (set with imgui.COLOR_BUTTON_ACTIVE)
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
    imgui.begin_group()
    
    # Get initial cursor position
    p0 = imgui.get_cursor_pos()
        
    # Set active color if needed
    if is_active:
        r, g, b, a = imgui.get_style().colors[imgui.COLOR_BUTTON_ACTIVE]
        imgui.push_style_color(imgui.COLOR_BUTTON, r, g, b)
        
    # Set text alignment and draw button
    imgui.push_style_var(imgui.STYLE_BUTTON_TEXT_ALIGN, text_offset)
    is_clicked = imgui.button(text, button_size[0], button_size[1])
    imgui.pop_style_var()
    
    # Clean up styles
    if is_active:
        imgui.pop_style_color()
        
    # Get cursor end position
    p1 = imgui.get_cursor_pos()
    
    # Calculate image position
    offset_to_centre = ((button_size[0] - image_size[0]) / 2, (button_size[1] - image_size[1]) / 2)
    
    # Set image position
    imgui.set_cursor_pos((p0[0] + offset_to_centre[0] + image_offset[0], p0[1] + offset_to_centre[1] + image_offset[1]))
    
    # Draw image (use hovered image if provided and button is hovered)
    if image_when_hovered and imgui.is_item_hovered():
        imgui.image(image_when_hovered, image_size[0], image_size[1])
    else:
        imgui.image(image, image_size[0], image_size[1])
        
    # Reset cursor position
    imgui.set_cursor_pos(p1)
    
    imgui.end_group()
    
    return is_clicked



# imgui.slider_float2() with list input
@imgui_method
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
    changed, new_values = imgui._slider_float2_original(label, values[0], values[1], min_val, max_val, format, flags)
    return changed, list(new_values)

# imgui.slider_float3() with list input
@imgui_method
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
    changed, new_values = imgui._slider_float3_original(label, values[0], values[1], values[2], min_val, max_val, format, flags)
    return changed, list(new_values)

# imgui.slider_float4() with list input
@imgui_method
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
    changed, new_values = imgui._slider_float4_original(label, values[0], values[1], values[2], values[3], min_val, max_val, format, flags)
    return changed, list(new_values)