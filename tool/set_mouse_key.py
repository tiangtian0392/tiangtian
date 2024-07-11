import datetime
import sys
import time
from pywinauto.application import Application
import os


class set_moust_key():
    def __init__(self):
        self.app = None

    def openpath(self, wnd):
        """
        打开文件并返回app
        :param wnd: 用于连接窗口或控件 backend=win32、uia,title=title,path=path
        :return: app
        """

        os.system(f'start {wnd.get("path", "")}')

        for i in range(10):
            try:
                app = Application(backend=wnd.get("backend", "")).connect(title_re=wnd.get("title", ""))
                # 选择窗口
                self.app = app.window(title_re=wnd.get("title", ""))
                self.app.set_focus()
                print(self.app)

                time.sleep(2)
                return
            except Exception as e:
                print(f'Error: {e}')
                time.sleep(1)
        print(f'激活{wnd.get("name", "")}:窗口激活失败！')

    def find_win(self, backend, window_hierarchy, control_hierarchy, timeout=30):
        """
        查找窗口控件
        :param backend: win32 or uia
        :param window_hierarchy: 窗口层次结构
        :param control_hierarchy: 控件层次结构
        :param timeout: 等待控件出现的超时时间
        :return: 控件对象
        """
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                app = None
                window = None

                # 遍历窗口层次结构
                for index, wnd in enumerate(window_hierarchy):
                    if index == 0:
                        # 连接到应用程序
                        self.app = Application(backend=backend).connect(**wnd)
                        window = self.app
                    window = window.window(**wnd)
                # window.print_control_identifiers()
                print('窗口遍历完成，开始遍历控件')
                # 遍历控件层次结构
                control = window
                for ctrl in control_hierarchy:
                    control = control.child_window(**ctrl)

                # 设置前景窗口
                control.set_focus()
                return control
            except Exception as e:
                print(f'Error: {e}')
                if window:
                    window.print_control_identifiers()
                time.sleep(1)
        return None

    def set_mouse(self, backend, wnd, ctrl, bt_num=1, bt_lr='l', delay_before=50, delay_after=30, timeout=30):
        """
        设置鼠标操作
        :param backend: win32 or uia
        :param wnd: 用于连接窗口或控件
        :param ctrl: 控件获取参数，name,class_name，auto_id，control_type
        :param bt_num: 点击次数，1=单击，2=双击
        :param bt_lr: l=左键，r=右键
        :param delay_before: 执行前延时
        :param delay_after: 执行后延时
        :param timeout: 等待控件出现的超时时间
        :return:
        """

        bt_double = bt_num == 2  # bt_num=2 双击
        bt_lr = 'left' if bt_lr == 'l' else 'right'  # l 左键点击，否则右键
        # 延迟操作前
        time.sleep(delay_before / 1000.0)

        found_app = self.find_win(backend, wnd, ctrl, timeout)
        if not found_app:
            print("Error: 无法找到控件")
            sys.exit()
        found_app.click_input(double=bt_double, button=bt_lr)

        # 操作后延迟
        time.sleep(delay_after / 1000.0)

        return found_app

    def set_keyboot(self, backend, wnd, ctrl, text, delay_before=50, delay_after=500, timeout=30):
        """
        键盘用法，写入数据等
        :param backend: win32 or uia
        :param wnd: 用于连接窗口或控件
        :param ctrl: 控件获取参数，name,class_name，auto_id，control_type
        :param text: 写入文本内容
        :param delay_before: 执行前延时
        :param delay_after: 执行后延时
        :param timeout: 等待控件出现的超时时间
        :return:
        """
        # 延迟操作前
        time.sleep(delay_before / 1000.0)

        found_app = self.find_win(backend, wnd, ctrl, timeout)
        if not found_app:
            print("Error: 无法找到控件")
            sys.exit()
        found_app.type_keys(text)

        # 操作后延迟
        time.sleep(delay_after / 1000.0)

        return found_app


# print(datetime.datetime.now())
# name = "Access - Q10_up"
# path = r"Z:\bazhuayu\Q10_up.accdb"
# acc = set_moust_key()
#
# # 点击updata
# acc.set_mouse('uia', [{"title_re": 'Access'}, {"class_name": "NetUINativeHWNDHost", "title": "ナビゲーション ウィンドウのホスト"}],
#               [{"class_name": "NetUINavPaneGroup", "title": "フォーム"},
#                {"class_name": "NetUINavPaneItem", "title": "updata"}
#                ], bt_num=2, bt_lr='l', timeout=30)
# acc.set_mouse('uia', [{"title_re": 'Access'}, {"class_name": 'MDIClient', "found_index": 0},
#                       {"class_name": 'OForm', "title": 'updata', "found_index": 0}],
#               [{"title_re": '.*1-delete'}], bt_num=1, bt_lr='l', timeout=30)
#
# time.sleep(1)
# # 点击OK
# acc.set_mouse('win32', [{"title_re": "Microsoft Access", "class_name": "#32770"}],
#               [{"title": "OK", "class_name": "Button"}], bt_num=1, bt_lr='l', timeout=30)
#
# acc.set_mouse('uia', [{"title_re": 'Access'}, {"class_name": 'MDIClient', "found_index": 0},
#                       {"class_name": 'OForm', "title": 'updata', "found_index": 0}
#                       ], [{"title_re": '2-updata'}], bt_num=1, bt_lr='l', timeout=30)
#
# filepaht = r"D:\Users\Downloads\Qoo10_ItemInfo_20240708150340_1.xlsx"
#
# time.sleep(2)
#
# fileopen = acc.set_keyboot('win32', [{"title": "ファイルを開く"}], [{"class_name": "Edit"}], filepaht, timeout=30)
# acc.set_mouse('win32', [{"title": "ファイルを開く"}], [{"title": "開く(&O)", "class_name": "Button", "found_index": 0}], bt_num=1, bt_lr='l', timeout=30)
#
# # 点击OK
# acc.set_mouse('win32', [{"title_re": "Microsoft Access", "class_name": "#32770"}],
#               [{"title": "OK", "class_name": "Button"}], bt_num=1, bt_lr='l', timeout=3000)
# 点击保存
# acc.set_mouse('uia', [{"title_re": "Access - Q10_up"}, {"title_re": "MsoDockTop"}, {"title_re": "Ribbon","found_index": 1},
#                       ],
#               [{"title": "クイック アクセス ツール バー"}, {"title": "上書き保存"}], bt_num=1, bt_lr='l', timeout=3)
# acc.set_mouse('uia', [{"title_re": "Access - Q10_up"}, {"title_re": "MsoDockTop"}, {"title_re": "Ribbon","found_index": 1},
#                       ],
#               [{"title": "閉じる"}], bt_num=1, bt_lr='l', timeout=1)
# print(f'运行完成:{datetime.datetime.now()}')
