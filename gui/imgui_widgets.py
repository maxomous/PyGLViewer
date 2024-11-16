import imgui

class ImGuiWidgets:
    """
    Collection of reusable ImGui widget patterns and layouts.
    Provides static methods for common UI components.
    """
    
    @staticmethod
    def create_table(table_id: str, headers: list, rows: list, flags: int = 0) -> bool:
        """
        Creates and renders an ImGui table with the specified headers and rows.
        
        Args:
            table_id (str): Unique identifier for the table
            headers (list): List of column headers
            rows (list): List of rows, where each row is a list of cells
            flags (int, optional): ImGui table flags. Defaults to 0
        
        Returns:
            bool: True if table was created and rendered successfully
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
    
# Additional functions using the imgui module as the namespace
# e.g. imgui.some_function()

def imgui_method(func):
    """Decorator to automatically add a function to the imgui module"""
    original_func = getattr(imgui, func.__name__, None)  # Store the original function
    setattr(imgui, f"_{func.__name__}_original", original_func)  # Save it with a new name
    setattr(imgui, func.__name__, func)  # Set our new function
    return func


# imgui.slider_float2() with list input
@imgui_method
def slider_float2(label: str, values: list, min_val: float = 0.0, max_val: float = 1.0, format: str = "%.3f", flags: int = 0) -> tuple[bool, list]:
    changed, new_values = imgui._slider_float2_original(label, values[0], values[1], min_val, max_val, format, flags)
    return changed, list(new_values)

# imgui.slider_float3() with list input
@imgui_method
def slider_float3(label: str, values: list, min_val: float = 0.0, max_val: float = 1.0, format: str = "%.3f", flags: int = 0) -> tuple[bool, list]:
    changed, new_values = imgui._slider_float3_original(label, values[0], values[1], values[2], min_val, max_val, format, flags)
    return changed, list(new_values)

# imgui.slider_float4() with list input
@imgui_method
def slider_float4(label: str, values: list, min_val: float = 0.0, max_val: float = 1.0, format: str = "%.3f", flags: int = 0) -> tuple[bool, list]:
    changed, new_values = imgui._slider_float4_original(label, values[0], values[1], values[2], values[3], min_val, max_val, format, flags)
    return changed, list(new_values)