import sys
from PyQt5.QtWidgets import QApplication, QWidget, QShortcut, QMessageBox
from PyQt5.QtCore import QObject, pyqtSignal, QThread, QTimer
from PyQt5.QtGui import QKeySequence
from PyQt5.QtCore import Qt
import pyautogui
import keyboard
from window_Qoo10 import Ui_Form
import win32gui
import win32con
import win32api
# from pywinauto.application import Application
import time
import threading
import psutil
import pygetwindow
import os
import csv
from PyQt5.QtWidgets import QFileDialog
import pandas as pd
import datetime
from tkinter import Tk, filedialog, messagebox
import tkinter as tk
import json


class MyWindow(QWidget, Ui_Form):
    re_path = pyqtSignal(str, str)

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

    def get_Qoo10filepath(self, str_text):
        filenamepath, _ = QFileDialog.getOpenFileName(None, str_text, "", "CSV Files (*.csv)")
        print('addsf',filenamepath,_)
        self.re_path.emit(filenamepath, str_text)
        # return filenamepath,str_text

    # 调用配置文件
    def set_config(self):
        print('点击配置文件')
        config_window = ConfigWindow()
        config_window.run()

    def selectAllCheckBoxes(self, state):
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
            self.checkBox_zaiku_file_up.setChecked(True)
        else:
            # 反选
            self.checkBox_zaiku_down.setChecked(False)
            self.checkBox_dingdan_down.setChecked(False)
            self.checkBox_dingdan_work.setChecked(False)
            self.checkBox_dingdan_up.setChecked(False)
            self.checkBox_youji_up.setChecked(False)
            self.checkBox_zaiku_up.setChecked(False)
            self.checkBox_zaiku_file_up.setChecked(False)

    # 程序运行完成
    def run_over(self, text):
        print(f'{self.fromtitle}_{text}')
        self.setWindowTitle(f'{self.fromtitle}_{text}')

    # 出库失败提示
    def Qmessbox(self, sp_str):
        print(f'以下为程序提示 {sp_str}')
        QMessageBox.information(self, '提示', sp_str)

    def startProcess(self):
        # 开始处理函数
        try:
            # 获取勾选状态

            placeholder_text = self.lineEdit_zaiku_up_num.text()
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

            print('点击开始', checkbox_dict['出库行号'])
            PATH = r"D:\出庫UP202404161054.csv"
            no_list = ["00004", "00005"]
            self.ff = StockManager(checkbox_dict, self.config, self)
            self.ff.run_over.connect(self.run_over)
            self.ff.get_path.connect(self.get_Qoo10filepath)
            self.ff.Qmessbox.connect(self.Qmessbox)
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
    get_path = pyqtSignal(str)
    Qmessbox = pyqtSignal(str)

    def __init__(self, checkbox_dict, log_config, window, no_list=''):

        super().__init__()
        self.yujuup_path = None
        self.chuku_path = None
        self.config = log_config
        self.no_list = no_list

        self.checkbox_dict = checkbox_dict
        self.chuku_num = checkbox_dict["出库行号"]

        print(self.checkbox_dict)
        self.winown = window
        self.winown.re_path.connect(self.Q_path)

        self.running = True
        self.thread = None
        self.window_num = 0  # 设置获取窗口的数量，对比判断试用窗口是否出现
        self.time_sleep = 1  # 设置监视试用窗口时间

        self.Qoo10filepath = None
        self.path = None
        # 出库失败记录
        self.chuku_err_str = ''



    def Q_path(self, path, str_text):

        path = path.replace('/', '\\')
        print(f'主线程回写path {path}')
        if path == '':
            print('文件选择为空，程序停止！')
            self.stop()
        if '下载' in str_text:
            self.Qoo10filepath = path
        elif '上传' in str_text:
            self.path = path
        elif 'chuku' in str_text:
            self.chuku_path = path
        else:
            self.yujuup_path = path
        print('路径变量完成',path)

    def open_Stockc(self):
        from pywinauto.application import Application
        self.stop_flag = True
        if self.is_process_running('StockC.exe'):
            self.window_num = 1
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
                        self.window_num = 1
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
        print(f'开始运行选项程序,Qoopath = {self.Qoo10filepath}')
        if self.running == False:
            return
        if self.checkbox_dict["在库下载"]:
            if self.running == False:
                return

        if self.checkbox_dict["定单下载"]:
            if self.running == False:
                return
            self.chrom_ = chrome_set()
            Qoo10_file = self.chrom_.down_all_order()
            if Qoo10_file:
                self.Qoo10filepath = Qoo10_file

        if self.checkbox_dict["定单处理"]:
            if self.running == False:
                return
            if self.Qoo10filepath is None:
                self.get_path.emit('选择Qoo10定单下载文件')

                jj = 0
                while self.Qoo10filepath is None:
                    print(jj)
                    if jj >= 100:
                        return
                    time.sleep(1)
                    jj += 1
            self.set_Qoo10 = OrderDataProcessor(self.config, Qoo10data_file=self.Qoo10filepath)
            self.path,self.chuku_path,self.yujuup_path = self.set_Qoo10.generate_output_files()
            if self.path is None:
                self.Qmessbox.emit('可発貨表为空，程序中止！')
                self.stop()
                return
            print(f'定单处理完成，返回 self.path = {self.path}')
        if self.checkbox_dict["定单上传"]:
            if self.running == False:
                return
            if self.path is None:
                self.get_path.emit('选择定单上传文件')

                jj = 0
                while self.path is None:
                    print(jj)
                    if jj >= 100:
                        self.stop()
                        return
                    time.sleep(1)
                    jj += 1
            print('sdss',self.path)
            if not self.path:
                return
            self.chrom_ = chrome_set()
            self.chrom_.up_order(self.path)
            # if Qoo10_file != True:
            #     self.running = False
        if self.checkbox_dict["クリックポスト上传"]:
            if self.running == False:
                return
            if self.yujuup_path is None:
                self.get_path.emit('クリックポスト')

                jj = 0
                while self.yujuup_path is None:
                    print(jj)
                    if jj >= 100:
                        return
                    time.sleep(1)
                    jj += 1
            if not self.yujuup_path:
                return
        if self.checkbox_dict["出库上传"]:
            # 打开文件对话框选择 CSV 文件
            if self.running == False:
                return

            if self.chuku_path is None:

                self.get_path.emit('chuku')
                # print('获取文件路径完成',self.chuku_path)
                jj = 0
                while self.chuku_path is None:
                    print(jj)
                    if jj >= 100:
                        return
                    time.sleep(1)
                    jj += 1
                print(f'出库上传文件路径={self.chuku_path}')


            if self.chuku_path:
                with open(self.chuku_path, 'r', newline='', encoding='ANSI') as csvfile:
                    reader = csv.reader(csvfile)
                    next(reader)  # 跳过标题行
                    self.no_list = [row[0] for row in reader]  # 从 CSV 文件中读取数据并填充 self.no_list
            else:
                return
            self.open_Stockc()
            self.write_path(self.chuku_path)
        if self.checkbox_dict["出库"]:
            if self.running == False:
                return
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
            for i, item in enumerate(self.no_list):
                if self.chuku_num != '':
                    chuku_start_index = int(self.chuku_num) - 1  # 出库行号转换为索引
                    if i < chuku_start_index:
                        continue  # 如果当前索引小于出库行号的索引，则跳过继续下一轮循环
                try:
                    self._run(item)
                except Exception as e:
                    print(f'_run运行出错：{e}')

        self.stop()


    def stop(self):
        # print(f'以下商品出库失败 {self.chuku_err_str}')
        self.running = False
        self.run_over.emit(f'程序停止')
        try:
            self.chrom_.stop()
        except:
            pass
        try:
            self.set_Qoo10.stop()
        except:
            pass
        if self.chuku_err_str != '':
            self.Qmessbox.emit(f'以下商品在库变更失败 {self.chuku_err_str}')
        else:
            self.Qmessbox.emit('程序工作正常完成！')
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
        print(len(windows), self.window_num)
        return len(windows)

    def _run(self, set_str_text):
        self.run_over.emit(f'出库变更：{set_str_text}')
        if self.running == False:
            return
        try:
            # 激活窗口至前台
            app_title = "(試用中)在庫番頭 Professional Edition"
            hwnd = win32gui.FindWindow(None, app_title)
            if hwnd:
                # win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)  # 将窗口还原
                win32gui.SetForegroundWindow(hwnd)  # 将窗口置于前台
            else:
                print(f"窗口 '{app_title}' 未找到")
            search_text_ID = self.set_window_get_ID("(試用中)在庫番頭 Professional Edition", class_name1="TGroupBox",
                                                    index1=1, class_name2="TEdit", index2=2)
            self.set_edit_control_text(search_text_ID, set_str_text)
            time.sleep(1)

            btn_click_ID = self.set_window_get_ID("(試用中)在庫番頭 Professional Edition", class_name1="TGroupBox",
                                                  index1=1, class_name2="TBitBtn", index2=1)
            win32gui.SendMessage(btn_click_ID, win32con.BM_CLICK, None, None)  # 点击按键

            # 点击出库参照
            self.Btn_click_Cuku("(試用中)在庫番頭 Professional Edition", set_str_text)
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
    def Btn_click_Cuku(self, window_title, item):
        # 你的按钮点击函数的代码，可以直接复制过来
        if self.running == False:
            return
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
        # 3秒倒计时判断出库参照窗口是否存在
        find_win = True
        while find_win:
            for i in range(3):
                print('i 出庫参照', i)
                if self.is_window_open('出庫参照') > 0:
                    print('此处应该就打印一次，退出循环')
                    find_win = False
                    break  # 如果 Qoo10filepath 更新了，立即退出循环
                time.sleep(1)
            else:
                print('获取Qoo10path 失败，请重试！')
                self.chuku_err_str = f'{self.chuku_err_str} {item},'
                return

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
        # print('监视线程开始工作中......')
        from pywinauto.application import Application

        while self.running:
            print('监视线程开始工作中......')
            if self.is_window_open('在庫番頭 Professional Edition') > 1:
                # from pywinauto.application import Application
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
        if self.running == False:
            return
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
            if not self.running:
                return
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


# 处理定单类
class OrderDataProcessor:
    def __init__(self, config, Qoo10data_file=None, zaiku_file_path=None, output_folder=None):

        self.running = True

        self.Qoo10data_file = Qoo10data_file
        self.zaiku_file_path = config["zaiku_file_path"]
        self.output_folder = config["output_folder"]
        print('self.output_folder', self.output_folder)
        self.output_folder = self.output_folder.replace('/', '')
        # self.root = Tk()
        print(f'Orderdataprocessor Qoo10path = {self.Qoo10data_file}')

    def stop(self):
        self.running = False
    def generate_output_files(self):
        # 读取第一个表和在库表的数据
        if not self.running:
            return
        if self.zaiku_file_path is None:
            self.zaiku_file_path = r"\\LS410D8E6\tool\bazhuayu\在庫.csv"
        if self.output_folder is None:
            self.output_folder = r"D:"
        if self.Qoo10data_file is None:
            # self.select_file_dialog()
            print(f'打开选择Qoo10文件 ={self.Qoo10data_file}')
            if self.Qoo10data_file == '':
                return
            # Qdata = pd.read_csv(self.Qoo10data_file, encoding='shift-jis')
        Qdata = pd.read_csv(self.Qoo10data_file, encoding='ANSI')
        zaiku_data = pd.read_csv(self.zaiku_file_path, encoding='ANSI')

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
        # now_date = now.strftime('%Y%m%d%H%M')
        now_date = now.strftime('%Y%m%d')
        # 初始化字典
        dizhi_dict = {}
        zhuwenbanhao_dict = {}

        # 对于第一个表中的每个订单
        for index, row in Qdata.iterrows():
            if not self.running:
                return
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
            if not self.running:
                return
            all_orders_have_stock = True
            for order_number in order_numbers:
                if not self.running:
                    return
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

        # 定义新表格的列名
        new_columns = [
            "配送状態", "注文番号", "カート番号", "配送会社", "送り状番号", "発送日", "注文日", "入金日",
            "お届け希望日", "発送予定日",
            "配送完了日", "配送方法", "商品番号", "商品名", "数量", "オプション情報", "オプションコード", "おまけ", "受取人名",
            "受取人名(フリガナ)", "受取人電話番号", "受取人携帯電話番号", "住所", "郵便番号", "国家", "送料の決済",
            "決済サイト", "通貨", "購入者決済金額", "販売価格", "割引額", "注文金額の合計", "供給原価の合計",
            "購入者名", "購入者名(フリガナ)", "配送要請事項", "購入者電話番号", "購入者携帯電話番号",
            "販売者商品コード",
            "JANコード", "規格番号", "プレゼント贈り主", "外部広告", "素材"
        ]
        if not self.running:
            return
        # 创建新的空表格
        available_for_shipping_new = pd.DataFrame(columns=new_columns)

        # 遍历原始数据，将available_for_shipping中的内容填入新表格
        for col in new_columns:
            if col in available_for_shipping.columns:
                available_for_shipping_new[col] = available_for_shipping[col]
            else:
                available_for_shipping_new[col] = ""
        # 保存可出库表和在库UP表
        if not available_for_shipping_new.empty:
            available_for_shipping_new.to_csv(f"{self.output_folder}\\可発貨表{now_date}.csv", index=False, encoding='ANSI')
        else:
            # QMessageBox.information(None,'提示','可発貨表空，不保存！')
            return None,None,None
        available_for_shipping.to_csv(f"{self.output_folder}\\可発貨表_old_{now_date}.csv", index=False, encoding='ANSI')
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
        return f"{self.output_folder}\\可発貨表{now_date}.csv",f"{self.output_folder}\\出庫UP{now_date}.csv",f"{self.output_folder}\\ゆうパケット{now_date}.csv"


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
class chrome_set:

    def __init__(self):
        self.run = True
        # 切换标签
        self.tab_name_select()

        app_name = " Google Chrome"

        self.app = self.get_app('uia', app_name)

        if self.app  is None:
            print('窗口不存在，程序退出！')
            return

    def stop(self):
        self.run = False
    def get_app(self,fid, app_name):
        from pywinauto import Desktop, findwindows
        if not self.run:
            return
        try:
            # 使用Desktop对象来获取窗口
            app = Desktop(backend=fid).window(title_re=f".*{app_name}.*")
            print(f'{app_name} 连接成功')
            app.set_focus()  # 激活窗口

        except findwindows.ElementAmbiguousError as e:
            print(f"找到多个与'{app_name}'匹配的窗口")
            return None
        except findwindows.ElementNotFoundError as e:
            print(f"未找到与'{app_name}'匹配的窗口")
            return None
        except Exception as e:
            print('关联窗口失败，检查窗口')
            return None
        return app

    def But_page_ud(self,num):

        print(f'num={num}')
        for i in range(3):
            if not self.run:
                return
            pyautogui.press('pageup')
        for i in range(num):
            pyautogui.press('pagedown')

    # 点击网页目标
    def But_action(self,win_app, title='', control_type='', auto_id='', class_name=''):
        def But_bb():
            try:

                print('点击所有商品', win_app)
                edit_control = win_app.child_window(title_re=title, control_type=control_type, auto_id=auto_id,
                                                    class_name_re=class_name)
                edit_control.click_input()
                print(f'点击成功')
                return True
            except Exception as e:
                print('点击失败:', e)
                return False

        attempt = 0  # 初始化尝试计数器
        while attempt < 4:
            if not self.run:
                return
            bb_pd = But_bb()

            if bb_pd:
                # 获取今日日期
                now = datetime.datetime.now()
                # 将当前日期时间格式化为指定的格式（年月日时分）
                now_date = now.strftime('%Y%m%d_%H%M')
                # now_date = now.strftime('%Y%m%d')
                return now_date
            self.But_page_ud(attempt)
            attempt += 1  # 尝试次数加一

    def down_all_order(self):
        # 点击配送要請(詳細を見る)
        if not self.run:
            return


        for i in range(3):
            pyautogui.press('pageup')
        # 获取窗口位置
        rect = self.app.rectangle()
        print(rect)
        # 确定相对坐标
        x_relative = 564
        y_relative = 600
        # 计算绝对坐标
        x_absolute = rect.left + x_relative
        y_absolute = rect.top + y_relative
        # 点击相对坐标
        try:
            pyautogui.click(x=x_absolute, y=y_absolute)
            print("点击成功")

        except Exception as e:
            print("点击失败:", e)
            return

        # But_action(win_app, title='配送要請(詳細を見る)', control_type='Button')
        # 点击一般配送(追跡-O) 所有定单
        self.But_action(self.app, control_type='Edit', auto_id='txt_shipping_type_registered')
        # 点击全体をダウンロード
        down_time = self.But_action(self.app, title='全体をダウンロード', auto_id='btn_excel_down')

        q10_order_filename = f"DeliveryManagement_detail_{down_time}.csv"
        print(q10_order_filename)

        # 判断文件是否存在
        # 文件夹路径
        # folder_path = "C:\\Users\\user\\Downloads\\"
        folder_path = "D:\\Users\\Downloads\\"
        # 拼接文件路径
        file_path = os.path.join(folder_path, q10_order_filename)

        # 检查文件或文件夹是否存在
        for i in range(5):

            if os.path.exists(file_path):
                print(f"文件 '{q10_order_filename}' 存在于文件夹 '{folder_path}' 中。")
                return file_path
            else:
                print(f"文件 '{q10_order_filename}' 不存在于文件夹 '{folder_path}' 中。")
            time.sleep(1)

        return

    def up_order(self, up_filename):

        if not self.run:
            return
        print(self.run)
        # # 切换标签
        # self.tab_name_select()
        from pywinauto.application import Application
        # 测试点击上传发货文件
        # 点击発送予定日の入力
        self.But_action(self.app, title='発送予定日の入力', control_type='Button')
        # 点击エクセル一括発送予定日入力
        self.But_action(self.app, title='エクセル一括発送予定日入力', auto_id='btn_excel_proc_schedule')
        time.sleep(2)

        # 模拟 点击上传excel
        app_Qoo10 = self.get_app('uia', 'Qoo10 - QSM')
        app_Qoo10.set_focus()  # 激活窗口

        # 获取窗口位置
        rect = app_Qoo10.rectangle()
        print(rect)
        # 点击相对坐标
        try:
            pyautogui.click(x=rect.left + 183, y=rect.top + 151)
            print("点击成功")
        except Exception as e:
            print("点击失败:", e)
            return
        if not self.run:
            return
        time.sleep(3)
        # 上传出库文件
        # up_filename = 'asdfafsd'
        # 找到包含文件名输入框的窗口
        app_1 = Application(backend="win32").connect(title="開く", class_name="#32770")
        # 获取主窗口
        main_window = app_1.window(title="開く", class_name="#32770").child_window(
            class_name="ComboBoxEx32").child_window(class_name="ComboBox")

        main_window.child_window(class_name="Edit").set_edit_text(up_filename)
        main_window = app_1.window(title="開く", class_name="#32770").child_window(title="開く(&O)",
                                                                                  class_name="Button").click_input()
        # 点击エクセル一括発送予定日入力
        self.But_action(app_Qoo10, title='Upload File')
        return True
    # 根据关键词切换标签
    def tab_name_select(self):
        if not self.run:
            return
        from pywinauto.application import Application
        app = Application(backend='uia')
        app.connect(title_re='.*Chrome')
        dlg = app.window(title_re='.*Chrome')
        tabs = dlg.descendants(control_type='TabItem')
        tab_num = 0
        for i, tab in enumerate(tabs):
            tab_text = tab.window_text()
            print(i, tab.window_text())
            if '配送管理' in tab_text:
                tab_num = i
                break
        # 点击对应的标签页
        tabs[tab_num].click_input()
        time.sleep(1)

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
