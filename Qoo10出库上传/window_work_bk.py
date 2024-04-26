import csv
import datetime
import json
import os
import sys
import threading
# from pywinauto.application import Application
# import pywinauto
import time
import tkinter as tk
from tkinter import Tk, filedialog, messagebox

import keyboard
import pandas as pd
import psutil
import pygetwindow
import win32api
import win32con
import win32gui
from PyQt5.QtCore import pyqtSignal, QThread
from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtWidgets import QFileDialog

from window_Qoo10 import Ui_Form


class MyWindow(QWidget, Ui_Form):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.fromtitle = 'Qoo10_work'
        self.setWindowTitle(self.fromtitle)
        # 检查配置文件完整性并读入

        with open("config.json", "r") as f:
            config = json.load(f)
        self.config = config
        # 根据配置文件中的路径初始化变量
        self.zaiku_file_path = config["zaiku_file_path"]
        self.output_folder = config["output_folder"]
        self.StockC_exe_path = config["StockC_exe_path"]
        print(self.config)

        # 各按键设置
        self.checkBox_select_all.stateChanged.connect(self.selectAllCheckBoxes)
        self.pushButton_start.clicked.connect(self.startProcess)
        self.pushButton_stop.clicked.connect(self.stopProcess)
        self.pushButton_set_config.clicked.connect(self.set_config)

        # 全局快捷键
        keyboard.add_hotkey('ctrl+f11', self.startProcess)
        keyboard.add_hotkey('ctrl+f12', self.stopProcess)

    # 调用配置文件
    def set_config(self):
        print('点击配置文件')
        config_window = ConfigWindow()
        config_window.run()

    def selectAllCheckBoxes(self):
        # 实现全选或反选逻辑
        print('点击全选')
        if self.checkBox_select_all.isChecked():
            # 全选
            self.checkBox_zaiku_down.setChecked(True)
            self.checkBox_dingdan_down.setChecked(True)
            self.checkBox_dingdan_work.setChecked(True)
            self.checkBox_dingdan_up.setChecked(True)
            self.checkBox_youji_up.setChecked(True)
            self.checkBox_zaiku_up.setChecked(True)
        else:
            # 反选
            self.checkBox_zaiku_down.setChecked(False)
            self.checkBox_dingdan_down.setChecked(False)
            self.checkBox_dingdan_work.setChecked(False)
            self.checkBox_dingdan_up.setChecked(False)
            self.checkBox_youji_up.setChecked(False)
            self.checkBox_zaiku_up.setChecked(False)

    # 程序运行完成
    def run_over(self, text):
        print(f'{self.fromtitle}_{text}')
        self.setWindowTitle(f'{self.fromtitle}_{text}')

    def startProcess(self):
        # 开始处理函数
        try:
            # 获取勾选状态
            placeholder_text = self.lineEdit_zaiku_up_num.placeholderText()
            checkbox_dict = {
                "在库下载": self.checkBox_zaiku_down.isChecked(),
                "定单下载": self.checkBox_dingdan_down.isChecked(),
                "定单处理": self.checkBox_dingdan_work.isChecked(),
                "定单上传": self.checkBox_dingdan_up.isChecked(),
                "クリックポスト上传": self.checkBox_youji_up.isChecked(),
                "出库": self.checkBox_zaiku_up.isChecked(),
                "出库上传": self.checkBox_zaiku_file_up.isChecked(),
                "出库行号": placeholder_text
            }

            print('点击开始')
            self.ff = StockManager(checkbox_dict, self.config)
            self.ff.run_over.connect(self.run_over)
            self.ff.start()

        except Exception as e:
            print(f'程序意外出错，报错内容：{e}')

    def stopProcess(self):
        # 结束处理函数
        print('点击结束')
        try:
            self.ff.stop()

        except Exception as e:
            print(f'停止程序，{e}')

    def process_finished(self):
        print("处理完成")


class StockManager(QThread):
    run_over = pyqtSignal(str)

    def __init__(self, checkbox_dict, log_config, no_list=None, path=None):

        super().__init__()
        self.config = log_config
        self.no_list = no_list
        self.path = path
        self.checkbox_dict = checkbox_dict
        print(self.checkbox_dict)

        self.running = True
        self.thread = None
        self.window_num = 0  # 设置获取窗口的数量，对比判断试用窗口是否出现
        self.time_sleep = 1  # 设置监视试用窗口时间

    def open_Stockc(self):
        from pywinauto.application import Application
        self.stop_flag = True
        if self.is_process_running('StockC.exe'):
            # result = 1/0
            # app = Application(backend="uia").connect(title_re=".*在庫番頭 Professional Edition.*",
            #                                          class_name="TMainForm", timeout=1)
            # app_dialog = app.window(title_re=".*在庫番頭 Professional Edition.*", class_name="TMainForm")
            # app_dialog.set_focus()
            # self.time_sleep = 1
            print('在库程序以打开')
        else:
            print(f"程序没有启动")
            try:

                try:
                    StockC_exe_path = self.config["StockC_exe_path"].replace('StockC.exe', '')
                    # cmd = f'start /d "{StockC_exe_path}" StockC.exe'
                    print(StockC_exe_path)
                    cmd = r'start /d "C:\Program Files (x86)\zbpro\" StockC.exe'
                    os.system(cmd)
                    # os.popen(r'"D:\stockc.bat"')
                except Exception as e:
                    print(f'打开文件错误，{e}')
                print('start 运行完成')
                # 判断app窗体出现后，激活窗体，并按键回车
                for i in range(50):
                    print(i, self.is_window_open('在庫番頭 Professional Edition'))
                    if self.is_window_open('在庫番頭 Professional Edition') > 0:
                        self.monitor_trial_window()
                        print('打开页面的试用窗口关闭完成')
                        break
                    time.sleep(1)
            except Exception as e:
                print(f"启动在库番頭应用程序失败: {e}")
            time.sleep(1)
            try:
                # from pywinauto.application import Application
                app = Application(backend="win32").connect(title_re=".*在庫番頭 Professional Edition.*",
                                                           class_name="TMainForm", timeout=3)
                app_window = app.window(title_re=".*在庫番頭 Professional Edition.*", class_name="TManageForm")
                app_window.set_focus()
                print('准备点击在库开始')
                # time.sleep(0.5)
                self.press_and_release(13)
                app_window.child_window(title="在庫管理実行", class_name="TBitBtn").click_input()
                for i in range(50):
                    print(i, self.is_window_open("(試用中)在庫番頭 Professional Edition"))
                    if self.is_window_open("(試用中)在庫番頭 Professional Edition") > 0:
                        self.window_num = self.is_window_open("(試用中)在庫番頭 Professional Edition")
                        print(f'现发现在库窗口{self.window_num}个')
                        break
                    time.sleep(1)
                # self.time_sleep = 100
            except Exception as e:
                print(f"点击在库番頭窗口失败: {e}")
        self.run_over.emit('窗体打开完成')
        # 启动监视试用窗口线程并守护本线程
        self.thread = threading.Thread(target=self.monitor_trial_window)
        self.thread.daemon = True
        self.thread.start()

    def run(self):
        # 选执行上传出库

        if self.running == False:
            return
        if self.checkbox_dict["在库下载"]:
            pass
        if self.checkbox_dict["定单下载"]:
            pass
        if self.checkbox_dict["定单处理"]:
            set_Qoo10 = OrderDataProcessor(self.config)
            self.path = set_Qoo10.generate_output_files()
        if self.checkbox_dict["定单上传"]:
            pass
        if self.checkbox_dict["クリックポスト上传"]:
            pass
        if self.checkbox_dict["出库上传"]:
            # 打开文件对话框选择 CSV 文件
            self.open_Stockc()
            if self.path is not None:
                try:
                    self.path, _ = QFileDialog.getOpenFileName(None, "选择CSV文件", "", "CSV Files (*.csv)")
                    print(f'出库上传文件路径={self.path}')
                    self.path = self.path.replace('/', '\\')
                    print(f'出库上传文件路径={self.path}')
                    if self.path:
                        with open(self.path, 'r', newline='', encoding='ANSI') as csvfile:
                            reader = csv.reader(csvfile)
                            next(reader)  # 跳过标题行
                            self.no_list = [row[0] for row in reader]  # 从 CSV 文件中读取数据并填充 self.no_list
                    else:
                        return
                except Exception as e:
                    print(f'打开文件出错，{e}')
                    return
            self.write_path(self.path)
        if self.checkbox_dict["出库"]:
            self.open_Stockc()
            if not self.no_list:  # 如果 self.no_list 为空
                # 打开文件对话框选择 CSV 文件
                try:
                    filename, _ = QFileDialog.getOpenFileName(None, "选择CSV文件", "", "CSV Files (*.csv)")
                    if filename:
                        with open(filename, 'r', newline='', encoding='ANSI') as csvfile:
                            reader = csv.reader(csvfile)
                            next(reader)  # 跳过标题行
                            self.no_list = [row[0] for row in reader]  # 从 CSV 文件中读取数据并填充 self.no_list
                    else:
                        return
                except Exception as e:
                    print(f'打开文件出错，{e}')
                    return

            print(self.no_list)
            for item in self.no_list:
                try:
                    self._run(item)
                except Exception as e:
                    print(f'_run运行出错：{e}')

        self.stop()

    def stop(self):
        self.running = False
        self.run_over.emit(f'程序停止')
        # raise MyException('点击菜单失败，超过重试次数，结束打开工作')

    # 用程序名判断进程是否启动 如：StockC.exe  是在库的启动文件
    def is_process_running(self, process_name):
        for p in psutil.process_iter():
            # print(p.name())
            if p.name() == process_name:
                print(f'找到运行中程序，{p.name()}')
                return True
        return False

    # 用标题查看窗体是否存在 如试用窗口：在庫番頭 Professional Edition，没有试用窗口时，标题有2个，加个试用窗口共计3个，所以默认值=2
    def is_window_open(self, window_title):
        windows = pygetwindow.getWindowsWithTitle(window_title)
        # print(len(windows))
        return len(windows)

    def _run(self, set_str_text):
        self.run_over.emit(f'出库变更：{set_str_text}')
        if self.running == False:
            return
        try:
            search_text_ID = self.set_window_get_ID("(試用中)在庫番頭 Professional Edition", class_name1="TGroupBox",
                                                    index1=1, class_name2="TEdit", index2=2)
            self.set_edit_control_text(search_text_ID, set_str_text)
            time.sleep(1)

            btn_click_ID = self.set_window_get_ID("(試用中)在庫番頭 Professional Edition", class_name1="TGroupBox",
                                                  index1=1, class_name2="TBitBtn", index2=1)
            win32gui.SendMessage(btn_click_ID, win32con.BM_CLICK, None, None)  # 点击按键

            # 点击出库参照
            self.Btn_click_Cuku("(試用中)在庫番頭 Professional Edition")
        except Exception as e:
            print(f'输入出库品番出错。{e}')
        self.run_over.emit(f'出库变更：{set_str_text},变量完成')
        # 根据title 确定位置

    def set_window_get_ID(self, window_title, class_name1, index1, class_name2=None, index2=None):
        hwnd = win32gui.FindWindow(None, window_title)
        if hwnd:
            hwnd_quick_search = self.find_control(hwnd, class_name1, None, index1)  # 获取第一个 "クイック検索" 控件
            if hwnd_quick_search:
                hwnd_edit = self.find_control(hwnd_quick_search, class_name2, None, index2)  # 获取第二个 TEdit 控件
                if hwnd_edit:
                    return hwnd_edit
                else:
                    print("在指定的控件下找不到编辑框")
            else:
                print("找不到指定的窗口")
        else:
            print("找不到指定的窗口")

    # 查找返回ID值
    def find_control(self, hwnd_parent, class_name, text, index):
        # 遍历指定父窗口的子控件
        child = None
        count = 0  # 控件计数器
        while True:
            child = win32gui.FindWindowEx(hwnd_parent, child, None, None)
            if child == 0:
                break
            # 检查控件的类名和文本
            class_name_buffer = win32gui.GetClassName(child)
            control_text = win32gui.GetWindowText(child)
            if class_name_buffer == class_name:
                count += 1
                if count == index:
                    return child
            # 如果子控件有子控件，则递归遍历子控件
            sub_child = self.find_control(child, class_name, text, index)
            if sub_child:
                return sub_child
        return None

    def set_edit_control_text(self, hwnd_edit, text):
        win32gui.SendMessage(hwnd_edit, win32con.WM_SETTEXT, None, text)

    # 出库变更
    def Btn_click_Cuku(self, window_title):
        # 你的按钮点击函数的代码，可以直接复制过来

        from pywinauto.application import Application
        hwnd = win32gui.FindWindow(None, window_title)
        if hwnd:
            rect = win32gui.GetWindowRect(hwnd)
            window_width = rect[2] - rect[0]  # 窗口宽度
            window_height = rect[3] - rect[1]  # 窗口高度
            if window_width < 480 or window_height < 70:
                win32gui.MoveWindow(hwnd, rect[0], rect[1], 1024, 800, True)
                rect = win32gui.GetWindowRect(hwnd)
            x = rect[0] + 480
            y = rect[1] + 70
            win32api.SetCursorPos((x, y))
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, x, y, 0, 0)
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, x, y, 0, 0)
            time.sleep(0.5)  # 等待0.5秒以确保点击生效
            # 检查"出庫処理"窗口是否存在
            hwnd_chuku = win32gui.FindWindow(None, "出庫処理")
            if not hwnd_chuku:
                time.sleep(1)  # 如果不存在则等待1秒
                win32api.SetCursorPos((x, y))  # 再次移动鼠标到指定位置
                win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, x, y, 0, 0)  # 再次模拟鼠标左键按下
                win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, x, y, 0, 0)  # 再次模拟鼠标左键释放
        else:
            print("找不到指定的窗口")

        # 启动应用程序或连接到已经运行的应用程序
        app = Application(backend="win32").connect(title="出庫参照", class_name="TDeliveryForm")

        chuku_biangeng_button = app.window(title="出庫参照", class_name="TDeliveryForm").child_window(title="出庫変更",
                                                                                                      class_name="TBitBtn")
        if not chuku_biangeng_button.is_enabled():
            xns_grid = app.window(title="出庫参照", class_name="TDeliveryForm").child_window(class_name="XnsGrid")
            xns_grid.set_focus()
            for _ in range(2):  # 尝试两次，如果第一次不成功
                win32api.keybd_event(win32con.VK_UP, 0, 0, 0)  # 模拟按键向上
                win32api.keybd_event(win32con.VK_UP, 0, win32con.KEYEVENTF_KEYUP, 0)  # 模拟释放按键
                time.sleep(0.5)  # 等待0.5秒以确保操作生效
                if chuku_biangeng_button.is_enabled():
                    break  # 如果按钮可用，则跳出循环
                win32api.keybd_event(win32con.VK_DOWN, 0, 0, 0)  # 模拟按键向下
                win32api.keybd_event(win32con.VK_DOWN, 0, win32con.KEYEVENTF_KEYUP, 0)  # 模拟释放按键
                time.sleep(0.5)  # 等待0.5秒以确保操作生效
                if chuku_biangeng_button.is_enabled():
                    break  # 如果按钮可用，则跳出循环
        app.window(title="出庫参照", class_name="TDeliveryForm").child_window(title="出庫変更",
                                                                              class_name="TBitBtn").click_input()
        app.window(title="出庫参照", class_name="TDeliveryForm").child_window(class_name="TMemo",
                                                                              found_index=4).click_input()

        app.window(title="出庫参照", class_name="TDeliveryForm").child_window(title="出庫変更",
                                                                              class_name="TBitBtn").click_input()

        time.sleep(0.5)
        # 点击试用
        app_1 = Application(backend="win32").connect(title="在庫番頭 Professional Edition", class_name="#32770")
        app_1.window(title="在庫番頭 Professional Edition", class_name="#32770").child_window(title="はい(&Y)",
                                                                                              class_name="Button").click_input()

        app.window(title="出庫参照", class_name="TDeliveryForm").child_window(title="閉じる",
                                                                              class_name="TBitBtn").click_input()

    # 超线程监控试用弹窗
    def monitor_trial_window(self):
        print('监视线程开始工作中......')
        from pywinauto.application import Application
        # def is_window_open(window_title):
        #     windows = pygetwindow.getWindowsWithTitle(window_title)
        #     # print(len(windows))
        #     return len(windows)

        while self.stop_flag:
            print('监视线程开始工作中......')
            if self.is_window_open('在庫番頭 Professional Edition') > self.window_num:
                app = Application(backend="win32").connect(title="在庫番頭 Professional Edition",
                                                           class_name="TLicenseForm")
                app.window(title="在庫番頭 Professional Edition", class_name="TLicenseForm").child_window(
                    class_name="TButton").click()
            time.sleep(1)
        print('监视线程结束')

    # 模拟按键
    def press_and_release(self, key):
        win32api.keybd_event(key, 0, 0, 0)
        time.sleep(0.1)
        win32api.keybd_event(key, 0, win32con.KEYEVENTF_KEYUP, 0)

    # 上传出库文件
    def write_path(self, path):
        self.run_over.emit('开始上传出库文件')
        from pywinauto.application import Application
        app = Application(backend="win32").connect(title="(試用中)在庫番頭 Professional Edition",
                                                   class_name="TMainForm")
        # 获取应用程序的顶层窗口
        top_window = app.top_window()
        # 激活顶层窗口
        top_window.set_focus()

        # 模拟按下 ALT + F
        def open_win():
            self.press_and_release(win32con.VK_MENU)
            self.press_and_release(0x46)  # F 键的 ASCII 码

            # 模拟按下 A 键
            self.press_and_release(0x41)  # A 键的 ASCII 码

        open_win()
        # 检查“ファイルを開く”窗口是否存在
        file_open_dialog = win32gui.FindWindow("#32770", "ファイルを開く")
        print("ファイルを開く", file_open_dialog)
        for i in range(5):
            if not file_open_dialog:
                # 如果不存在，则重复之前的动作打开窗口
                open_win()
                time.sleep(1)  # 等待窗口打开
            if i == 5:
                print('点击菜单失败，程序退出！')
                raise MyException('点击菜单失败，超过重试次数，结束打开工作')
        file_open_dialog = win32gui.FindWindow("#32770", "ファイルを開く")
        # 连接到应用程序
        # from pywinauto.application import Application
        app = Application(backend="win32").connect(title="ファイルを開く", class_name="#32770")

        # 获取主窗口
        main_window = app.window(title="ファイルを開く", class_name="#32770").child_window(
            class_name="ComboBoxEx32").child_window(class_name="ComboBox")

        main_window.child_window(class_name="Edit").set_edit_text(path)
        time.sleep(0.5)
        self.press_and_release(0x0D)
        time.sleep(1)

        app = Application(backend="win32").connect(title="出庫データ取り込み", class_name="TDelivImportForm")
        win = app.window(title="出庫データ取り込み", class_name="TDelivImportForm")
        panel = win.child_window(class_name="TPanel", found_index=1)
        button = panel.child_window(title='取り込み', class_name="TBitBtn")
        button.click_input()
        win.set_focus()
        time.sleep(2)
        self.press_and_release(0x0D)
        self.run_over.emit('出库文件上传完成')
    # 超线程监控试用弹窗


def monitor_trial_window(window_num, stop_flag):
    print('监视线程开始工作中......')
    from pywinauto.application import Application
    def is_window_open(window_title):
        windows = pygetwindow.getWindowsWithTitle(window_title)
        # print(len(windows))
        return len(windows)

    while not stop_flag:
        if is_window_open('在庫番頭 Professional Edition') > window_num:
            app = Application(backend="win32").connect(title="在庫番頭 Professional Edition",
                                                       class_name="TLicenseForm")
            app.window(title="在庫番頭 Professional Edition", class_name="TLicenseForm").child_window(
                class_name="TButton").click()
        time.sleep(1)
    print('监视线程结束')


# 处理定单类
class OrderDataProcessor:
    def __init__(self, config, Qoo10data_file=None):
        self.Qoo10data_file = Qoo10data_file
        self.zaiku_file_path = config["zaiku_file_path"]
        self.output_folder = config["output_folder"]

    def select_file_dialog(self):
        """弹出文件选择框选择文件"""
        root = Tk()
        root.withdraw()  # 隐藏Tk窗口
        self.Qoo10data_file = filedialog.askopenfilename()  # 获取文件路径

        if not self.Qoo10data_file:
            messagebox.showerror('错误', '没有选择文件，程序退出！')
            return
        if not self.Qoo10data_file.endswith('.csv'):
            messagebox.showerror('错误', '不是csv文件，程序退出！')
            return
        if 'detail' not in self.Qoo10data_file:
            messagebox.showerror('错误', '文件不是详情模式，程序退出！')
            return

        print(self.Qoo10data_file)
        return self.Qoo10data_file

    def generate_output_files(self):
        # 读取第一个表和在库表的数据
        if self.zaiku_file_path is None:
            self.zaiku_file_path = r"\\LS410D8E6\tool\bazhuayu\在庫.csv"
        if self.output_folder is None:
            self.output_folder = r"D:"
        if self.Qoo10data_file is None:
            self.select_file_dialog()
            if not self.Qoo10data_file:
                print(f'Qoo10data没有文件，退出')
                return
            # Qdata = pd.read_csv(self.Qoo10data_file, encoding='shift-jis')
        print(f'在定单处理函数中 Qoo10path = {self.Qoo10data_file}')
        Qdata = pd.read_csv(self.Qoo10data_file, encoding='shift-jis')
        zaiku_data = pd.read_csv(self.zaiku_file_path, encoding='shift-jis')

        Qdata['JANコード'] = Qdata['JANコード'].astype(str)
        zaiku_data['商品ID'] = zaiku_data['商品ID'].astype(str).str.strip()

        # 将日期数据转换为 datetime 格式
        Qdata['入金日'] = pd.to_datetime(Qdata['入金日'])
        # 根据入金日期升序对Qoo10data表进行排序
        Qdata.sort_values(by='入金日', ascending=True, inplace=True)

        # 初始化可出库表和出库UP表
        available_for_shipping = pd.DataFrame(columns=Qdata.columns)
        in_stock_UP = pd.DataFrame(
            columns=['品番', '注文番号', '発送予定日', '商品名', '数量', '決済サイト', '購入者決済金額', '供給原価の合計',
                     '販売者商品コード', 'JANコード'])

        # 获取今日日期
        now = datetime.datetime.now()
        # 将当前日期时间格式化为指定的格式（年月日时分）
        now_date = now.strftime('%Y%m%d%H%M')

        # 初始化字典
        dizhi_dict = {}
        zhuwenbanhao_dict = {}

        # 对于第一个表中的每个订单
        for index, row in Qdata.iterrows():
            # 在在库表中查找匹配的商品
            matching_items = zaiku_data[(zaiku_data['商品ID'] == row['JANコード']) & (zaiku_data['在庫数'] > 0)]

            # 获取地址和注文番号
            address = row['住所']
            order_number = row['注文番号']

            # 更新dizhi_dict和zhuwenbanhao_dict,无论是否有数据都向地址添加注文番号
            if address not in dizhi_dict:
                dizhi_dict[address] = [order_number]
            else:
                dizhi_dict[address].append(order_number)

            # 如果有库存，处理该订单
            if not matching_items.empty:

                if order_number not in zhuwenbanhao_dict:
                    # 创建出库UP表的条目
                    in_stock_up_item = {
                        '品番': zaiku_data.loc[matching_items.index[0], '品番'],
                        '注文番号': row['注文番号'],
                        '発送予定日': now_date,
                        '商品名': row['商品名'],
                        '数量': row['数量'],
                        '決済サイト': row['決済サイト'],
                        '購入者決済金額': row['購入者決済金額'],
                        '供給原価の合計': row['供給原価の合計'],
                        '販売者商品コード': row['販売者商品コード'],
                        'JANコード': row['JANコード']
                    }
                    zhuwenbanhao_dict[order_number] = [[row], [in_stock_up_item]]

                # 减少库存数量
                zaiku_data.loc[matching_items.index[0], '在庫数'] -= 1

        # 遍历dizhi_dict
        for address, order_numbers in dizhi_dict.items():
            # 检查对应地址的订单是否都有对应的在库商品
            all_orders_have_stock = True
            for order_number in order_numbers:
                if order_number not in zhuwenbanhao_dict:
                    all_orders_have_stock = False
                    break

            # 如果都有对应的在库商品，则将内容写入可出货表和出库UP表中
            if all_orders_have_stock:
                for order_number in order_numbers:
                    # 写入可出货表
                    available_for_shipping = available_for_shipping.append(zhuwenbanhao_dict[order_number][0],
                                                                           ignore_index=True)

                    # 写入出库UP表
                    for item in zhuwenbanhao_dict[order_number][1]:
                        in_stock_UP = in_stock_UP.append(item, ignore_index=True)
        # 保存可出库表和在库UP表
        available_for_shipping.to_csv(f"{self.output_folder}\\可出库{now_date}.csv", index=False, encoding='shift-jis')
        in_stock_UP.to_csv(f"{self.output_folder}\\出庫UP{now_date}.csv", index=False, encoding='ANSI')

        # 生成邮局上传文件
        # 过滤出配送会社为"ゆうパケット"的行
        yuupacket_data = available_for_shipping[available_for_shipping["配送会社"] == "ゆうパケット"]

        # 定义新表的标题行
        new_columns = ["お届け先郵便番号", "お届け先氏名", "お届け先敬称", "お届け先住所1行目", "お届け先住所2行目",
                       "お届け先住所3行目",
                       "お届け先住所4行目", "内容品"]
        new_data = pd.DataFrame(columns=new_columns)

        # 商品名关键字映射字典
        keyword_mapping = {
            "Switch": "ゲームソフト",
            "PS4": "ゲームソフト",
            "任天堂": "ゲームソフト",
            "ゲーム": "ゲームソフト",
            "Office": "PCソフト",
            "SSD": "PCパーツ(バッテリーなし)",
            "HHD": "PCパーツ(バッテリーなし)",
            "NVMe": "PCパーツ(バッテリーなし)",
            "SATA": "PCパーツ(バッテリーなし)",
            "M.2": "PCパーツ(バッテリーなし)",
            "メモリ": "PCパーツ(バッテリーなし)",
            "Keyboard": "キーボード",
            "Trackpad": "マウス"
        }

        # 遍历原始数据逐行生成新表
        for index, row in yuupacket_data.iterrows():
            # 在这里根据表1的标题行逐行处理原始数据，并生成新表的一行数据
            new_row = [
                row["郵便番号"][1:],  # お届け先郵便番号，去掉最前面的'
                row["受取人名"],  # お届け先氏名
                "様",  # お届け先敬称
                row["住所"][:20],  # お届け先住所1行目，最多20个字符
                row["住所"][20:40],  # お届け先住所2行目，最多20个字符
                row["住所"][40:60],  # お届け先住所3行目，最多20个字符
                row["受取人携帯電話番号"] if pd.notnull(row["受取人携帯電話番号"]) else row["受取人電話番号"],
                # お届け先住所4行目，如果受取人携帯電話番号为空则添入受取人電話番号
                row["商品名"]  # 数量
            ]
            # 根据关键字映射字典查找内容品
            for keyword, content in keyword_mapping.items():
                if keyword in row["商品名"]:
                    new_row[-1] = content
                    break
            new_data = new_data.append(pd.Series(new_row, index=new_data.columns), ignore_index=True)
        # 保存新表
        new_data.to_csv(f"{self.output_folder}\\ゆうパケット{now_date}.csv", index=False, encoding='ANSI')
        return f"{self.output_folder}\\出庫UP{now_date}.csv"


# 配置文件弹窗
class ConfigWindow:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("配置")

        try:
            # 尝试加载配置文件
            with open("config.json", "r") as f:
                self.config = json.load(f)
        except Exception as e:
            # 加载配置文件失败，重新创建配置文件
            messagebox.showerror("配置文件错误", f"加载配置文件出错: {str(e)}，将重新创建配置文件")
            self.config = {
                "zaiku_file_path": "",
                "output_folder": "",
                "StockC_exe_path": ""
            }
            with open("config.json", "w") as f:
                json.dump(self.config, f)

        # 添加输入框和按钮
        tk.Label(self.root, text="在库文件路径:").grid(row=0, column=0, sticky="w")
        self.zaiku_entry = tk.Entry(self.root, width=50)
        self.zaiku_entry.insert(0, self.config.get("zaiku_file_path", ""))  # 使用字典的 get 方法获取键值，如果键不存在则返回默认值
        self.zaiku_entry.grid(row=0, column=1, padx=5, pady=5)
        tk.Button(self.root, text="选择文件", command=self.choose_zaiku_file).grid(row=0, column=2)

        tk.Label(self.root, text="输出文件夹路径:").grid(row=1, column=0, sticky="w")
        self.output_entry = tk.Entry(self.root, width=50)
        self.output_entry.insert(0, self.config.get("output_folder", ""))  # 使用字典的 get 方法获取键值，如果键不存在则返回默认值
        self.output_entry.grid(row=1, column=1, padx=5, pady=5)
        tk.Button(self.root, text="选择文件夹", command=self.choose_output_folder).grid(row=1, column=2)

        tk.Label(self.root, text="StockC.exe路径:").grid(row=2, column=0, sticky="w")
        self.stockc_entry = tk.Entry(self.root, width=50)
        self.stockc_entry.insert(0, self.config.get("StockC_exe_path", ""))  # 使用字典的 get 方法获取键值，如果键不存在则返回默认值
        self.stockc_entry.grid(row=2, column=1, padx=5, pady=5)
        tk.Button(self.root, text="选择文件", command=self.choose_stockc_file).grid(row=2, column=2)

        tk.Button(self.root, text="保存配置", command=self.save_config).grid(row=3, column=1, pady=10)

    def choose_zaiku_file(self):
        filename = filedialog.askopenfilename()
        if filename:
            self.zaiku_entry.delete(0, tk.END)
            self.zaiku_entry.insert(0, filename)

    def choose_output_folder(self):
        foldername = filedialog.askdirectory()
        if foldername:
            self.output_entry.delete(0, tk.END)
            self.output_entry.insert(0, foldername)

    def choose_stockc_file(self):
        filename = filedialog.askopenfilename()
        if filename:
            self.stockc_entry.delete(0, tk.END)
            self.stockc_entry.insert(0, filename)

    def save_config(self):
        zaiku_path = self.zaiku_entry.get()
        output_folder = self.output_entry.get()
        stockc_path = self.stockc_entry.get()

        # 如果信息不完整，弹窗提示
        if not zaiku_path or not output_folder or not stockc_path:
            messagebox.showerror("保存失败", "请填写完整的配置信息")
            return

        # 保存配置到文件
        self.config["zaiku_file_path"] = zaiku_path
        self.config["output_folder"] = output_folder
        self.config["StockC_exe_path"] = stockc_path
        with open("config.json", "w") as f:
            json.dump(self.config, f)

        messagebox.showinfo("保存成功", "配置已保存")
        self.root.destroy()  # 关闭配置窗口

        # 创建并显示主窗口
        my_window = MyWindow()
        my_window.show()

        # 确保程序继续运行
        app.exec_()

    def run(self):
        self.root.mainloop()


# 抛出异常类，用来结束类的执行
class MyException(Exception):
    pass


# 检查配置文件完整性
def check_config():
    try:
        # 检查配置文件是否存在且非空
        if os.path.exists("config.json") and os.path.getsize("config.json") > 0:
            with open("config.json", "r") as f:
                config = json.load(f)
        else:
            raise FileNotFoundError("Config file not found or empty")

        # 检查配置是否完整
        zaiku_file_path = config.get("zaiku_file_path")
        output_folder = config.get("output_folder")
        StockC_exe_path = config.get("StockC_exe_path")
        if not zaiku_file_path or not output_folder or not StockC_exe_path:
            raise ValueError("Incomplete config")

        # 配置文件正常，返回配置
        return config

    except (FileNotFoundError, ValueError, json.JSONDecodeError) as e:
        # 配置文件有误，需要重新配置
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror("配置文件错误", f"加载配置文件出错: {str(e)}，将重新创建配置文件")
        config_window = ConfigWindow()
        config_window.run()
        root.destroy()  # 关闭配置窗口

        # 等待用户修正配置文件
        messagebox.showinfo("配置已更新", "已更新配置，请继续执行程序")
        # 重新检查配置文件并返回配置
        return


if __name__ == "__main__":
    app = QApplication(sys.argv)
    # try:
    #     config = check_config()
    # except Exception as e:
    #     messagebox.showerror("配置文件错误", f"加载配置文件出错: {str(e)}，将退出程序")
    print('开始检查配置文件')
    config = check_config()
    print('配置文件检查完成')

    my_window = MyWindow()
    my_window.show()
    sys.exit(app.exec_())
