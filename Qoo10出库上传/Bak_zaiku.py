import win32gui
import win32con
import win32api
from pywinauto.application import Application
import pywinauto
import time
import threading
import psutil
import pygetwindow

class StockManager:
    def __init__(self):
        self.running = False
        self.thread = None

        if self.is_process_running('StockC.exe'):
            # result = 1/0
            app = Application(backend="uia").connect(title_re=".*在庫番頭 Professional Edition.*",
                                                     class_name="TMainForm", timeout=1)
            app_dialog = app.window(title_re=".*在庫番頭 Professional Edition.*", class_name="TMainForm")
            app_dialog.set_focus()
        else:
            print(f"程序没有启动")
            try:
                # app = Application(backend="win32").start(cmd_line=r"C:\Program Files (x86)\zbpro\StockC.exe")
                import os
                # 启动程序
                try:
                    os.popen(r'"D:\stockc.bat"')
                except Exception as e:
                    print(f'打开文件错误，{e}')
                # time.sleep(5)
                print('按键回车')
                # 判断app窗体出现后，激活窗体，并按键回车
                for i in range(50):
                    print(i,self.is_window_open('在庫番頭 Professional Edition'))
                    if self.is_window_open('在庫番頭 Professional Edition'):
                        self.monitor_trial_window()
                        break
                    time.sleep(1)

                app = Application(backend="win32").connect(title_re=".*在庫番頭 Professional Edition.*",
                                                         class_name="TMainForm", timeout=3)
                app_window = app.window(title_re=".*在庫番頭 Professional Edition.*", class_name="TManageForm")

                app_window.child_window(title="在庫管理実行", class_name="TBitBtn").click_input()
                for i in range(50):
                    print(i,self.is_window_open("(試用中)在庫番頭 Professional Edition"))
                    if self.is_window_open("(試用中)在庫番頭 Professional Edition",1):
                        break
                    time.sleep(1)

            except Exception as e:
                print(f"启动在库番頭应用程序失败: {e}")



    def start(self, no_list,path):
        #选执行上传出库
        self.write_path(path)
        self.running = True
        for item in no_list:
            t = threading.Thread(target=self._run, args=(item,))
            t.setDaemon(True)
            t.start()           
            t.join()  # 这里不需要，可以移除
            # time.sleep(6000)

    def stop(self):
        self.running = False

    #用程序名判断进程是否启动 如：StockC.exe  是在库的启动文件
    def is_process_running(self,process_name):
        for p in psutil.process_iter():
            # print(p.name())
            if p.name() == process_name:
                print(f'找到运行中程序，{p.name()}')
                return True
        return False
    #用标题查看窗体是否存在 如试用窗口：

    def is_window_open(self,window_title,num=2):
        windows = pygetwindow.getWindowsWithTitle(window_title)
        print(num)
        # print(len(windows))
        return len(windows) > num
    def _run(self, set_str_text):
        print(set_str_text)
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

        finally:
            self.running = False

    # 等待Application窗口出现的函数
    def wait_for_window(self, title, class_name, timeout=30):
        start_time = time.time()
        while self.running:
            try:
                app = Application(backend="win32").connect(title=title, class_name=class_name)
                break  # 如果找到了窗口，跳出循环
            except Exception as e:
                if time.time() - start_time > timeout:
                    raise TimeoutError(f"等待窗口'{title}'超时: {e}")
                time.sleep(1)  # 每隔1秒尝试一次
        time.sleep(1)

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

    def Btn_click_Cuku(self, window_title):
        # 你的按钮点击函数的代码，可以直接复制过来
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

        chuku_bianheng_button = app.window(title="出庫参照", class_name="TDeliveryForm").child_window(title="出庫変更",
                                                                                                      class_name="TBitBtn")
        if not chuku_bianheng_button.is_enabled():
            xns_grid = app.window(title="出庫参照", class_name="TDeliveryForm").child_window(class_name="XnsGrid")
            xns_grid.set_focus()
            for _ in range(2):  # 尝试两次，如果第一次不成功
                win32api.keybd_event(win32con.VK_UP, 0, 0, 0)  # 模拟按键向上
                win32api.keybd_event(win32con.VK_UP, 0, win32con.KEYEVENTF_KEYUP, 0)  # 模拟释放按键
                time.sleep(0.5)  # 等待0.5秒以确保操作生效
                if chuku_bianheng_button.is_enabled():
                    break  # 如果按钮可用，则跳出循环
                win32api.keybd_event(win32con.VK_DOWN, 0, 0, 0)  # 模拟按键向下
                win32api.keybd_event(win32con.VK_DOWN, 0, win32con.KEYEVENTF_KEYUP, 0)  # 模拟释放按键
                time.sleep(0.5)  # 等待0.5秒以确保操作生效
                if chuku_bianheng_button.is_enabled():
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
    #超线程监控试用弹窗
    def monitor_trial_window(self):        

        if self.is_window_open('在庫番頭 Professional Edition'):
            print('监视线程工作中......')
            app = Application(backend="win32").connect(title="在庫番頭 Professional Edition",
                                                        class_name="TLicenseForm")
            app.window(title="在庫番頭 Professional Edition", class_name="TLicenseForm").child_window(
                class_name="TButton").click()
        else:
            time.sleep(0.5)
    #模拟按键      
    def press_and_release(self,key):
        win32api.keybd_event(key, 0, 0, 0)
        time.sleep(0.1)
        win32api.keybd_event(key, 0, win32con.KEYEVENTF_KEYUP, 0)

    # 上传出库文件
    def write_path(self,path):    
        app = Application(backend="win32").connect(title="(試用中)在庫番頭 Professional Edition", class_name="TMainForm")
    # 获取应用程序的顶层窗口
        top_window = app.top_window()
        # 激活顶层窗口
        top_window.set_focus()   

        # 模拟按下 ALT + F
        self.press_and_release(win32con.VK_MENU)
        self.press_and_release(0x46)  # F 键的 ASCII 码

        # 模拟按下 A 键
        self.press_and_release(0x41)  # A 键的 ASCII 码

        # 检查“ファイルを開く”窗口是否存在
        import win32gui
        file_open_dialog = win32gui.FindWindow("#32770", "ファイルを開く")
        print(file_open_dialog)
        if not file_open_dialog:
        # 如果不存在，则重复之前的动作打开窗口
            self.press_and_release(win32con.VK_MENU)
            self.press_and_release(0x46)  # F 键的 ASCII 码
            self.press_and_release(0x41)  # A 键的 ASCII 码
            time.sleep(1)  # 等待窗口打开
        file_open_dialog = win32gui.FindWindow("#32770", "ファイルを開く")
        # 连接到应用程序
        # from pywinauto.application import Application
        app = Application(backend="win32").connect(title="ファイルを開く", class_name="#32770")

        # 获取主窗口
        main_window = app.window(title="ファイルを開く", class_name="#32770").child_window(class_name="ComboBoxEx32").child_window(class_name="ComboBox")

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
# 示例使用
PATH = r"D:\出庫UP202404161054.csv"
no_list = ["00001","00002","00003","00004"]
manager = StockManager()
monitor_thread = threading.Thread(target=manager.monitor_trial_window)
monitor_thread.setDaemon(True)
monitor_thread.start()
manager.start(no_list,PATH)  # 启动任务
# 停止任务
manager.stop()
