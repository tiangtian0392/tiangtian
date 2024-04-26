from pywinauto import Desktop


def But_all_goods():
    app = Desktop(backend="uia").window(title_re="配送管理 - Google Chrome*")
    edit_control = app.child_window(title="", control_type="Edit", auto_id="txt_shipping_type_registered")
    edit_control.click_input()

from pywinauto import Desktop
from pywinauto import Application
import re

# 初始化 Desktop 对象
desktop = Desktop(backend="uia")

# 查找匹配标题的 Chrome 窗口
chrome_windows = desktop.windows()
# print(chrome_windows)
# 如果有多个 Chrome 窗口，循环处理每个窗口
for chrome_window in chrome_windows:
    # 获取 Chrome 窗口内的所有标签页标题
    window_title = chrome_window.window_text()
    print(window_title)
    if 'chrome' in window_title:
        print('ok')
        chrome_w = Application(backend='uia').connect(title_re = window_title)
        dlg = chrome_w.window(title_re=window_title)
        dlg.print_control_identifiers()
        break
