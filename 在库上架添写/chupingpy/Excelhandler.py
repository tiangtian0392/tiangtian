import win32com.client
import datetime

class ExcelHandler:

    def __init__(self, filename_keyword=None):
        self.excel = win32com.client.Dispatch("Excel.Application")
        self.excel.Visible = True
        self.workbook = None
        self.connected = False
        if filename_keyword:
            self.workbook = self.bind_open_workbook(filename_keyword)
            if self.workbook is None:
                print(f"未找到包含关键词 '{filename_keyword}' 的工作簿")
            else:
                self.connected = True


    def bind_open_workbook(self, filename_keyword):
        """
        绑定以打开的工作簿，根据文件名关键词查找
        """
        for workbook in self.excel.Workbooks:
            if filename_keyword in workbook.Name:
                return workbook
        return None


    def activate_workbook(self):
        """
        激活当前工作簿
        """
        if self.workbook:
            self.workbook.Activate()

    def _convert_cell_name_to_indices(self, cell_name):
        """
        将单元格名称（如"A1"）转换为行列索引
        """
        import re
        match = re.match(r"([A-Z]+)(\d+)", cell_name)
        if match:
            col_letters, row = match.groups()
            col = sum((ord(letter) - ord('A') + 1) * (26 ** i) for i, letter in enumerate(reversed(col_letters)))
            return int(row), col
        else:
            raise ValueError("Invalid cell name")

    def _convert_to_str(self, value):
        """
        将 pywintypes.datetime 对象转换为字符串格式
        """
        if isinstance(value, datetime.datetime):
            return value.strftime('%Y-%m-%d %H:%M:%S')
        return value

    def read_cell(self, sheet_name, cell_name):
        """
        读取单元格的值
        """
        row, col = self._convert_cell_name_to_indices(cell_name)
        sheet = self.workbook.Sheets(sheet_name)
        value = sheet.Cells(row, col).Value
        return self._convert_to_str(value)

    def read_ranges(self, sheet_name, start_cell_name, end_cell_name=None):
        """
        读取指定范围的值。如果只提供起始单元格，则读取从起始单元格到所有有数据的单元格。
        返回一个嵌套数组，表示每个单元格的值。
        """
        start_row, start_col = self._convert_cell_name_to_indices(start_cell_name)
        sheet = self.workbook.Sheets(sheet_name)
        if end_cell_name:
            end_row, end_col = self._convert_cell_name_to_indices(end_cell_name)
        else:
            used_range = sheet.UsedRange
            end_row = used_range.Rows.Count
            end_col = used_range.Columns.Count

        values = sheet.Range(sheet.Cells(start_row, start_col), sheet.Cells(end_row, end_col)).Value
        if isinstance(values, tuple):
            return [[self._convert_to_str(cell) for cell in row] for row in values]
        else:
            return [[self._convert_to_str(values)]]

    def read_row(self, sheet_name, row):
        """
        读取整行的值，返回一个数组
        """
        sheet = self.workbook.Sheets(sheet_name)
        values = sheet.Rows(row).Value
        if isinstance(values, tuple):
            return [self._convert_to_str(cell) for cell in values[0]]
        else:
            return [self._convert_to_str(values)]

    def read_column(self, sheet_name, col):
        """
        读取整列的值，返回一个数组
        """
        sheet = self.workbook.Sheets(sheet_name)
        # 获取已使用范围的行数
        used_range = sheet.UsedRange
        last_row = used_range.Rows.Count
        # 获取列的值
        values = sheet.Range(f"{col}1:{col}{last_row}").Value
        if isinstance(values, tuple):
            return [self._convert_to_str(row[0]) for row in values]
        else:
            return [self._convert_to_str(values)]

    def get_row_count(self, sheet_name):
        """
        获取使用的行数
        """
        sheet = self.workbook.Sheets(sheet_name)
        return sheet.UsedRange.Rows.Count

    def get_column_count(self, sheet_name):
        """
        获取使用的列数
        """
        sheet = self.workbook.Sheets(sheet_name)
        return sheet.UsedRange.Columns.Count

    def write_cell(self, sheet_name, cell_name, value):
        """
        写入单元格的值
        """
        row, col = self._convert_cell_name_to_indices(cell_name)
        sheet = self.workbook.Sheets(sheet_name)
        sheet.Cells(row, col).Value = value

    def write_range(self, sheet_name, start_cell_name, end_cell_name, values):
        """
        写入指定范围的值，values 为嵌套数组
        """
        start_row, start_col = self._convert_cell_name_to_indices(start_cell_name)
        end_row, end_col = self._convert_cell_name_to_indices(end_cell_name)
        sheet = self.workbook.Sheets(sheet_name)
        sheet.Range(sheet.Cells(start_row, start_col), sheet.Cells(end_row, end_col)).Value = values

    def write_row(self, sheet_name, row, values):
        """
        写入整行的值，values 为数组
        """
        sheet = self.workbook.Sheets(sheet_name)
        # for col, value in enumerate(values, start=1):
        #     sheet.Cells(row, col).Value = value
        array = [values]
        sheet.Range(sheet.Cells(row, 1), sheet.Cells(row, len(values))).Value = array
    def write_column(self, sheet_name, col, values):
        """
        写入整列的值，values 为数组
        """
        sheet = self.workbook.Sheets(sheet_name)
        for row, value in enumerate(values, start=1):
            sheet.Cells(row, col).Value = value

    def write_last_row(self, sheet_name, values):
        """
        写入最后一行，values 为数组
        """
        sheet = self.workbook.Sheets(sheet_name)
        last_row = sheet.UsedRange.Rows.Count + 1
        self.write_row(sheet_name, last_row, values)

    def write_last_column(self, sheet_name, values):
        """
        写入最后一列，values 为数组
        """
        sheet = self.workbook.Sheets(sheet_name)
        last_col = sheet.UsedRange.Columns.Count + 1
        self.write_column(sheet_name, last_col, values)

    def delete_row(self, sheet_name, row):
        """
        删除整行
        """
        sheet = self.workbook.Sheets(sheet_name)
        sheet.Rows(row).Delete()

    def delete_column(self, sheet_name, col):
        """
        删除整列
        """
        sheet = self.workbook.Sheets(sheet_name)
        sheet.Columns(col).Delete()

    def delete_range(self, sheet_name, start_cell_name, end_cell_name):
        """
        删除指定范围
        """
        start_row, start_col = self._convert_cell_name_to_indices(start_cell_name)
        end_row, end_col = self._convert_cell_name_to_indices(end_cell_name)
        sheet = self.workbook.Sheets(sheet_name)
        sheet.Range(sheet.Cells(start_row, start_col), sheet.Cells(end_row, end_col)).Delete()

    def switch_sheet(self, sheet_name):
        """
        切换到指定工作表
        """
        sheet = self.workbook.Sheets(sheet_name)
        sheet.Activate()

    def run_macro(self, macro_name, workbook_name=None):
        """
        执行指定的宏。如果提供了工作簿名称，则运行该工作簿中的宏。
        """
        if workbook_name:
            full_macro_name = f"'{workbook_name}'!{macro_name}"
        else:
            full_macro_name = macro_name
        self.excel.Application.Run(full_macro_name)

    def save(self):
        """
        保存当前工作簿
        """
        if self.workbook:
            self.workbook.Save()

    def close(self):
        """
        关闭当前工作簿并退出 Excel
        """
        if self.workbook:
            self.workbook.Close(SaveChanges=1)
        self.excel.Quit()

# 示例使用
# if __name__ == "__main__":
#     excel_handler = ExcelHandler("paichu00")  # 文件名关键词，例如 'example'
#     print(excel_handler.workbook)
#     if excel_handler.workbook:
#         excel_handler.activate_workbook()
#         print(excel_handler.read_cell("Sheet1", "A1"))  # 读取 Sheet1 中 A1 单元格的值
#
#         print(excel_handler.read_ranges('Sheet1','A1','B4'))
#         # excel_handler.write_cell("Sheet1", "E3", "Hello")  # 写入 Hello 到 Sheet1 中 A1 单元格
#         # excel_handler.write_last_row('Sheet1',[1,2,3])
#         # print(excel_handler.read_range("Sheet1", "A1"))  # 从 A1 单元格开始读取所有有数据的单元格
#         # excel_handler.save()
#         # excel_handler.close()
#     else:
#         print('绑定文件不成功，程序退出！')