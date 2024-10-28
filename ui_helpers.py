import imgui

class UIHelpers:
    @staticmethod
    def create_table(table_id, headers, rows, flags=0):
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
