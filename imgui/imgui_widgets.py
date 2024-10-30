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