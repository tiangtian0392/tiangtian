import xlwings as xw
import tkinter as tk
from tkinter import filedialog


class ExcelHandler:
    def __init__(self, file_path=None):
        self.workbook = self.get_or_open_workbook(file_path)

    def get_or_open_workbook(self, file_path):
        # 尝试获取已打开的工作簿
        for app in xw.apps:
            for book in app.books:
                if book.fullname == file_path:
                    return book

        # 如果未打开，使用文件选择对话框打开工作簿
        root = tk.Tk()
        root.withdraw()  # 隐藏主窗口
        if file_path:
            try:
                workbook = xw.Book(file_path)
                return workbook
            except:
                print(f"无法打开工作簿: {file_path}")
                return None
        else:
            file_path = filedialog.askopenfilename(title="选择工作簿", filetypes=[("Excel 文件", "*.xlsx;*.xls")])
            try:
                workbook = xw.Book(file_path)
                return workbook
            except:
                print("无法打开工作簿")
                return None

    def select_sheet(self, sheet_name):
        # 选择工作表
        try:
            sheet = self.workbook.sheets[sheet_name]
            return sheet
        except:
            print(f"工作表 {sheet_name} 不存在")
            return None

    def get_table(self, sheet_name, header=True):
        # 获取整个表格
        sheet = self.select_sheet(sheet_name)
        if sheet:
            return sheet.range('A1').expand().value
        return None

    def get_row(self, sheet_name, row_number):
        # 获取指定行
        sheet = self.select_sheet(sheet_name)
        if sheet:
            return sheet.range(f"A{row_number}").expand('right').value
        return None

    def get_column(self, sheet_name, column_letter):
        # 获取指定列
        sheet = self.select_sheet(sheet_name)
        if sheet:
            return sheet.range(f"{column_letter}1").expand('down').value
        return None

    def get_cell(self, sheet_name, cell_address):
        # 获取指定单元格
        sheet = self.select_sheet(sheet_name)
        if sheet:
            return sheet.range(cell_address).value
        return None

    def get_range(self, sheet_name, start_address, end_address):
        # 获取指定区域
        sheet = self.select_sheet(sheet_name)
        if sheet:
            return sheet.range(f"{start_address}:{end_address}").value
        return None

    def close_workbook(self):
        # 关闭工作簿
        if self.workbook:
            self.workbook.close()

    def __del__(self):
        # 对象销毁时关闭工作簿
        self.close_workbook()


# 示例用法
if __name__ == "__main__":
    excel_handler = ExcelHandler()

    # # 示例：获取整个表格
    # table_data = excel_handler.get_table("Sheet1")
    # print("整个表格:")
    # print(table_data)
    #
    # # 示例：获取第2行数据
    # row_data = excel_handler.get_row("Sheet1", 2)
    # print("第2行数据:")
    # print(row_data)
    #
    # # 示例：获取第B列数据
    # column_data = excel_handler.get_column("Sheet1", 'B')
    # print("第B列数据:")
    # print(column_data)
    #
    # # 示例：获取单元格A1的数据
    # cell_data = excel_handler.get_cell("Sheet1", "A1")
    # print("单元格A1的数据:")
    # print(cell_data)
    #
    # # 示例：获取A1到B2的区域数据
    # range_data = excel_handler.get_range("Sheet1", "A1", "B2")
    # print("A1到B2的区域数据:")
    # print(range_data)
    #
    # # 关闭工作簿
    # excel_handler.close_workbook()
