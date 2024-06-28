import datetime
import os
import sys
import time

import win32con
import win32gui
from PyQt5 import QtWidgets, QtCore
from Excelhandler import ExcelHandler
from comboboxUI import Ui_Form
from set_chrome import BrowserAutomation


class MainWindow(QtWidgets.QWidget, Ui_Form):
    def __init__(self):
        super().__init__()

        self.setupUi(self)
        # 设置窗口始终置顶 和无边框
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint | QtCore.Qt.FramelessWindowHint)
        # 设置窗口初始位置为 (1100, 100)
        self.move(10, 10)

        self.label_info.setText('用于显示提示信息！')

        # Connect functions to buttons
        self.pushButton_open.clicked.connect(self.open_file)
        self.pushButton_save.clicked.connect(self.save_file)
        self.pushButton_next.clicked.connect(self.next_action)
        self.pushButton_get_order.clicked.connect(self.get_order)
        self.pushButton_exit.clicked.connect(self.exit_app)

        # 鼠标拖动事件
        self.mousePressed = False
        self.mousePosition = None

        # 注意chrome的启动时设置端口 "C:\Program Files (x86)\Google\Chrome\Application\chrome.exe" --profile-directory="Profile 2"  --remote-debugging-port=3556 --force-renderer-accessibility
        self.chrome = BrowserAutomation("http://127.0.0.1:3556")

        now_date = datetime.datetime.now().strftime('%Y-%m-%d')
        self.csv_path = f'Z:\\bazhuayu\\caiji\\{now_date}\\'
        if os.path.exists(self.csv_path):
            print(f"路径 '{self.csv_path}' 存在.")
        else:
            folder_path = QtWidgets.QFileDialog.getExistingDirectory(self, '今日扫描文件夹不存在，重新选择！',
                                                                     'Z:\\bazhuayu\\caiji')
            print(f"路径 '{self.csv_path}' 不存在.重新设置为{folder_path}")
            self.csv_path = folder_path + '\\'

        self.xlsm_path = 'C:\\bazhuayu\\采集\\'

        self.dingdan_dict = {}
        self.paichu_dict = {}
        self.zaiku_dict = {}
        self.err_num = 0
        self.dingwei = 0
        self.csv = None
        self.xlsm = None
        self.files = self.get_files_list()
        self.get_Qoo10_web()

        self.pushButton_next.setText(f'下一个({self.dingwei + 1})')

    def get_Qoo10_web(self):
        """
       获取网页定单及取消的数据
        """
        try:
            dingdan = self.chrome.get_dingdan()
            quxiaodingdan = self.chrome.get_quxiaodingdan()
            if dingdan:
                for index, row in enumerate(dingdan[1::]):
                    if row[13] in self.dingdan_dict:
                        self.dingdan_dict[row[13]] = self.dingdan_dict[row[13]] + int(row[15])
                    else:
                        self.dingdan_dict[row[13]] = int(row[15])
            if quxiaodingdan:
                for index, row in enumerate(quxiaodingdan[1::]):
                    self.dingdan_dict[row[11]] = 'キ'
            print(self.dingdan_dict)
        except Exception as e:
            print(f'获取网页定单数据出错，e={e}')

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.mousePressed = True
            self.mousePosition = event.globalPos() - self.pos()
            event.accept()

    def mouseMoveEvent(self, event):
        if self.mousePressed:
            self.move(event.globalPos() - self.mousePosition)
            event.accept()

    def mouseReleaseEvent(self, event):
        self.mousePressed = False

    def get_files_list(self):
        print('获取改价文件夹文件')
        # 指定文件夹路径
        folder_path = r'C:\bazhuayu\采集'

        # 获取文件夹下所有的 .xlsm 文件
        files = [f for f in os.listdir(folder_path) if f.endswith('.xlsm')]

        # 定义一个函数，用来提取文件名中的数字部分
        def extract_number(filename):
            # 假设文件名的格式为 "{数字}_{其余部分}.xlsm"
            try:
                return int(filename.split('_')[0])
            except ValueError:
                return float('inf')  # 如果无法转换为整数，则返回无穷大，放到列表末尾

        # 按文件名中的数字部分进行排序
        files = sorted(files, key=extract_number)
        return files

    def qianzhichuli(self):
        print('前置判断')
        paichu_path = r"Z:\bazhuayu\paichu.xlsx"
        zaiku_path = r"Z:\bazhuayu\在庫.csv"
        testxlsx_path = r"Z:\\bazhuayu\\TEST.xlsx"
        PERSONAL_path = r"C:\Users\user\AppData\Roaming\Microsoft\Excel\XLSTART\PERSONAL.XLSB"
        paichu_work = None
        zaiku_work = None
        TEST_work = None
        PERSONAL_work = None
        try:
            paichu_work = ExcelHandler('paichu.xlsx')
            print(paichu_work.connected)
            if paichu_work.connected:
                self.err_num = 0
                print('开始处理排除文档')
                paichu_data = paichu_work.read_ranges('サイズ', 'A1')
                print(paichu_data[1::])
                if paichu_data:
                    for index, item in enumerate(paichu_data[1::]):
                        self.paichu_dict[str(int(item[0]))] = item[4]
                print(self.paichu_dict)

            else:
                print('绑定排除失败，执行打开排除！')
                os.system(f'start {paichu_path}')
                paichu_PD = self.try_num('paichu.xlsx', 10)
                if not paichu_PD and self.err_num < 3:
                    self.err_num += 1
                    return self.qianzhichuli()
                if self.err_num >= 3:
                    return
                else:
                    return self.qianzhichuli()

        except Exception as e:
            print(f'排除前置处理出错，e={e}')
        try:
            zaiku_work = ExcelHandler('在庫.csv')
            print(zaiku_work.connected)
            if zaiku_work.connected:
                self.err_num = 0

            else:
                print('绑定排除失败，退出！')
                os.system(f'start {zaiku_path}')
                zaiku_PD = self.try_num('在庫.csv', 10)
                if not zaiku_PD and self.err_num < 3:
                    self.err_num += 1
                    return self.qianzhichuli()
                # return self.qianzhichuli()
        except Exception as e:
            print(f'打开在库失败，e={e}')
        try:
            TEST_work = ExcelHandler('TEST.xlsx')
            print(TEST_work.connected)
            if TEST_work.connected:
                self.err_num = 0
            else:
                print('绑定TEST.xlsx失败，退出！')
                os.system(f'start {testxlsx_path}')
                test_PD = self.try_num('TEST.xlsx', 10)
                if not test_PD and self.err_num < 3:
                    self.err_num += 1
                    return self.qianzhichuli()
            # return self.qianzhichuli()
        except Exception as e:
            print(f'打开TEST.xlsx失败，e={e}')
        try:
            PERSONAL_work = ExcelHandler('PERSONAL.XLSB')
            print(PERSONAL_work.connected)
            if PERSONAL_work.connected:
                self.err_num = 0
            else:
                print('绑定PERSONAL.XLSB失败，退出！')
                os.system(f'start {PERSONAL_path}')
                PERSONAL_PD = self.try_num('PERSONAL.XLSB', 10)
                if not PERSONAL_PD and self.err_num < 3:
                    self.err_num += 1
                    return self.qianzhichuli()
            # return self.qianzhichuli()
        except Exception as e:
            print(f'打开TEST.xlsx失败，e={e}')
        print(f'前置程序处理成功，排除={paichu_work.connected},在库={zaiku_work.connected},TEST={TEST_work.connected},\
              PERSONAL.XLSB={PERSONAL_work.connected}')

    def compare_date(self, cell_value):
        """
        比较单元格日期和当前日期
        """
        cell_date = datetime.datetime.strptime(cell_value, '%Y-%m-%d %H:%M:%S').date()
        current_date = datetime.datetime.now().date()
        print(f'读入日期：{cell_date},当前日期：{current_date}')
        if cell_date != current_date:
            QtWidgets.QMessageBox.question(self, '提示', f'表格日期：{cell_date} 与当前日期不一致，检查表格是否更新！')

    def try_num(self, file, num):
        """
        :param file: 要绑定的excel文件路径
        :param num: 要重试的次数,每次延时1秒
        :return: True时返回，或超时返回假
        """
        for i in range(num):
            print(f'try_num,{file}重试第{i}次')
            try:
                name = ExcelHandler(file)
                if name.connected:
                    return True
                else:
                    time.sleep(1)
            except:
                time.sleep(1)
        return False

    def work_open(self):
        """
        处理打开所有excel后的具体工作
        执行宏，对比在库等
        """
        # 执行前置函数
        self.qianzhichuli()
        selected_items = self.comboBox.allItemsWithState()
        print("All items with state:", selected_items)
        filename = self.files[self.dingwei]
        # 使用 split 方法分割文件名和扩展名
        name, extension = os.path.splitext(filename)
        if name:
            os.system(f'start {self.csv_path}{name}.csv')
            csv_pd = self.try_num(f'{name}.csv', 10)
            if csv_pd:
                self.csv = ExcelHandler(f'{name}.csv')
            os.system(f'start {self.xlsm_path}{name}.xlsm')
            xlsm_PD = self.try_num(f'{name}.xlsm', 10)
            if xlsm_PD:
                self.xlsm = ExcelHandler(f'{name}.xlsm')
        else:
            print('文件名错误，退出')
            return
        self.minimize_all_excels()
        self.maximize_excel(f'{name}.xlsm')

        personal = ExcelHandler("personal.xlsb")
        self.xlsm.activate_workbook()
        self.xlsm.select_cell("Sheet1", "C1")
        self.xlsm.clear_column("Sheet1", "AC")
        k1 = self.xlsm.read_cell("Sheet1", "K1")
        print(k1)
        re_data = self.compare_date(k1)
        a_w_data = self.xlsm.read_ranges("Sheet1", "A1")
        # print(a_w_data)

        # 执行公共宏
        print(selected_items['打开宏'])
        if selected_items['打开宏']:
            print('执行打开宏')
            personal.run_macro("Shoushuliao", "personal.xlsb")
            personal.run_macro("get_CSV", "personal.xlsb")
            personal.run_macro("XieRu", "personal.xlsb")

        dingdan = ['定单数']
        for index, row in enumerate(a_w_data[1::]):
            banhao = str(int(row[0]))
            if banhao:
                if selected_items['对比定单']:
                    if banhao in self.dingdan_dict:
                        # print(self.dingdan_dict[banhao])
                        dingdan.append(self.dingdan_dict[banhao])
                    else:
                        dingdan.append(0)
                if selected_items['对比排除']:
                    if banhao in self.paichu_dict:
                        self.xlsm.write_cell("Sheet1", f'T{index + 2}', self.paichu_dict[banhao])

        self.xlsm.write_column("Sheet2", 'G1', dingdan)

        self.pushButton_next.setText(f'下一个({str(self.dingwei + 2)})')
        print('执行打开程序完成')

    def open_file(self):
        print("Open file")
        selected_items = self.comboBox.allItemsWithState()
        print("All items with state:", selected_items)

        options = QtWidgets.QFileDialog.Options()
        file_name, _ = QtWidgets.QFileDialog.getOpenFileName(self, "选择要打开的文档", "C:\\bazhuayu\\采集",
                                                             "Excel Files (*.xlsm);;All Files (*)",
                                                             options=options)
        if file_name:
            print(f'打开文件：{file_name}')
            # 使用 os.path.basename 获取文件名部分
            filename_with_extension = os.path.basename(file_name)

            # 使用 split 方法分割文件名和扩展名
            name, extension = os.path.splitext(filename_with_extension)

            # 以下划线分割文件名
            number, _ = name.split('_', 1)
            self.dingwei = int(number) - 1

            # 执行打开工作
            try:
                self.work_open()
            except Exception as e:
                print(f'执行打开文件：{self.files[self.dingwei]} 失败，e={e}')
                QtWidgets.QMessageBox.information(self, '提示', f'执行打开文件：{self.files[self.dingwei]} 失败，e={e}')
        else:
            print('没有选择打开任务文件，退出！')

    def save_file(self):
        print("Save file")
        selected_items = self.comboBox.allItemsWithState()
        print("All items with state:", selected_items)

        # 今天测试用，设置保存文件为空，手动指定保存文件
        self.xlsm = None

        if not self.xlsm:
            options = QtWidgets.QFileDialog.Options()
            file_name, _ = QtWidgets.QFileDialog.getOpenFileName(self, "选择要打开的文档", "C:\\bazhuayu\\采集",
                                                                 "Excel Files (*.xlsm);;All Files (*)",
                                                                 options=options)
            if file_name:
                print(f'打开文件：{file_name}')
                # 使用 os.path.basename 获取文件名部分
                filename_with_extension = os.path.basename(file_name)
                self.xlsm = ExcelHandler(filename_with_extension)
                if not self.xlsm.connected:
                    QtWidgets.QMessageBox.information(self, '提示', f'绑定文件：{filename_with_extension}失败，检查重试！')
                    return
            else:
                print('没有选择任何保存文件，退出！')
                return
        self.qianzhichuli()
        save_path = r'C:\\bazhuayu\\Q10up\\'

        N_list = self.xlsm.read_column("Sheet2", 'N2')
        print(N_list)
        paichu_list = self.xlsm.read_column("Sheet1", 'R2')
        # print(paichu_list)
        sh3_list = self.xlsm.read_ranges("Sheet3", "A2")
        # print(sh3_list)
        Qoo10_list = self.xlsm.read_ranges("Sheet5", "A2")
        # print(Qoo10_list)
        updata_list = []
        end_date = '2028-12-31'  # 设置贩卖终了日
        for index, item in enumerate(N_list):
            if item > 0 and item is not None:
                Qoo10_list[index][7] = end_date
                Qoo10_list[index][8] = sh3_list[index][11]
                Qoo10_list[index][10] = sh3_list[index][12]
                Qoo10_list[index][24] = sh3_list[index][28]

                updata_list.append(Qoo10_list[index])
        print(len(updata_list))
        if updata_list:
            now_date = datetime.datetime.now().strftime('%Y-%m-%d')
            filename = self.files[self.dingwei]
            # 使用 split 方法分割文件名和扩展名
            name, extension = os.path.splitext(filename)
            file_path = f'{save_path}{now_date}_{name}.xlsx'
            print(file_path)
            try:
                TEST_work = ExcelHandler('TEST.xlsx')
                TEST_work.write_range("TEST", "A5", updata_list)
                # 检查文件名是否有效
                if not os.path.basename(file_path):
                    print(f"无效的文件名：{file_path}")
                    return
                TEST_work.save_as(file_path)
                time.sleep(1)

            except Exception as e:
                print('写入TEST，保存上传文件失败，检查！')
            if selected_items['自动上传']:
                print('开始上传')
                auto_PD = self.auto_updata(path_name=file_path, name=name)
                print(auto_PD)

        else:
            print('没有要保存的文件')
        # try:
        #     self.xlsm.save()
        #     self.xlsm.close()
        #     self.csv.save()
        #     self.csv.close()
        #     TEST_work.close()
        # except Exception as e:
        #     print(f'关闭文件出错,e={e}')

    def auto_updata(self, path_name, name):
        """
        :param path_name: 全路径，用于上传添写
        :param name: 文件名，用于对比上伟是否成功
        :return:
        """
        print('开始自动上传')
        up_url = 'https://qsmupload.qoo10.jp/GMKT.INC.Gsm.Web/Product/DataExcelManagement.aspx'
        self.chrome.switch_to_tab_with_keyword(up_url)
        time.sleep(1)
        # 点击一括登録アップロード
        self.chrome.click_element('#qsm_bulk_header_tab > li:nth-child(1) > button')
        # 点击既存の商品/オプション修正
        self.chrome.click_element('#edit_upload')

        # 点击商品情報の修正
        self.chrome.click_element(
            '#qsm_bulk_content > li.selected > div:nth-child(4) > div.chkbox_wrap.modify_chkbox > div:nth-child(1) > label')
        # 点击ファイル添付
        time.sleep(1)
        self.chrome.click_element('#label_file_qoo10_upload')
        # 获取元素的坐标
        element_selector = "#label_file_qoo10_upload"
        coordinates = self.chrome.get_element_coordinates(element_selector)

        if coordinates:
            x, y = coordinates['x'], coordinates['y']
            print(f"Element coordinates: x={x}, y={y}")
            self.chrome.click_element_by_coordinates(x, y)
        else:
            print("Failed to get element coordinates.")
        time.sleep(1)
        # 上传并对比文件名是否正确
        up_name_PD = self.upload_file_win32(path_name, name)
        print('自动上传完成', up_name_PD)

        time.sleep(1)

        # 点击 一括修正ファイルのアップロード
        self.chrome.click_element('#button_file_qoo10_upload')
        time.sleep(1)
        self.chrome.click_element('#upload_progress_button')
    def upload_file_win32(self, path, name):
        print('执行上传添加文件路径操作')

        # 查找文件打开对话框的窗口
        def find_dialog(hwnd, extra):
            if win32gui.GetClassName(hwnd) == '#32770' and win32gui.GetWindowText(hwnd) == '開く':
                extra.append(hwnd)

        dialog_hwnds = []
        win32gui.EnumWindows(find_dialog, dialog_hwnds)

        if not dialog_hwnds:
            print("未找到文件打开对话框")
            return False

        dlg_hwnd = dialog_hwnds[0]

        # 查找子窗口（文件名输入框和打开按钮）
        edit_hwnd = win32gui.FindWindowEx(dlg_hwnd, 0, 'ComboBoxEx32', None)
        edit_hwnd = win32gui.FindWindowEx(edit_hwnd, 0, 'ComboBox', None)
        edit_hwnd = win32gui.FindWindowEx(edit_hwnd, 0, 'Edit', None)

        open_button_hwnd = win32gui.FindWindowEx(dlg_hwnd, 0, 'Button', '開く(&O)')

        # 输入文件路径
        win32gui.SendMessage(edit_hwnd, win32con.WM_SETTEXT, None, path)

        # 确保输入完成
        time.sleep(2)

        # 点击打开按钮
        win32gui.SendMessage(open_button_hwnd, win32con.BM_CLICK, 0, 0)

        time.sleep(2)

        # 检查文件名
        up_over_name = self.chrome.execute_js_in_tab('document.querySelector("#upload_file_name").textContent')
        print(up_over_name)
        if up_over_name:
            if up_over_name['result']['value'] != name:
                print(up_over_name['result']['value'])
                return False
            else:
                return True

        return False

    def next_action(self):
        print("Next action")
        # file_path = r"Z:\bazhuayu\auto_price\new_2024-06-28_110405.xlsx"
        # name = 'new_2024-06-28_110405.xlsx'
        # try:
        #     name = 'new_2024-06-28_110405.xlsx'
        #     auto_PD = self.auto_updata(path_name=file_path, name=name)
        #     print(auto_PD)
        # except Exception as e:
        #   print(f'打开下一个出错，e={e}')

        self.dingwei += 1
        # 执行打开工作
        try:
            self.work_open()
        except Exception as e:
            print(f'执行打开文件：{self.files[self.dingwei]} 失败，e={e}')
            QtWidgets.QMessageBox.information(self, '提示', f'执行打开文件：{self.files[self.dingwei]} 失败，e={e}')


    def get_order(self):
        print("开始获取定单")
        self.dingdan_dict = {}
        data = self.chrome.get_dingdan()
        print(data)
        if data:
            for index, item in enumerate(data[1::]):
                self.dingdan_dict[item[13]] = item[15]

        quxiao_data = self.chrome.get_quxiaodingdan()
        print(quxiao_data)
        if quxiao_data:
            for index, item in enumerate(quxiao_data[1::]):
                self.dingdan_dict[item[12]] = "キ"
        print(self.dingdan_dict)
        print('获取定单结束')

    def minimize_all_excels(self):
        try:
            # 获取所有顶级窗口的句柄
            hwnd_list = []
            win32gui.EnumWindows(lambda hwnd, param: param.append(hwnd), hwnd_list)

            # 遍历窗口句柄，找到 Excel 窗口并最小化
            for hwnd in hwnd_list:
                try:
                    class_name = win32gui.GetClassName(hwnd)
                    if class_name == "XLMAIN":
                        win32gui.ShowWindow(hwnd, win32con.SW_MINIMIZE)
                except Exception as e:
                    pass
                    # print(f"Error getting class name for hwnd {hwnd}: {e}")
        except Exception as e:
            print(f"Error enumerating windows: {e}")

    def match_windows(self, win_title):
        """
        查找指定窗口
        :param win_title: 窗口名称
        :return: 句柄列表
        """

        def callback(hwnd, hwnds):
            if win32gui.IsWindowVisible(hwnd) and win32gui.IsWindowEnabled(hwnd):
                win_text = win32gui.GetWindowText(hwnd)
                # 模糊匹配
                if win_text.find(win_title) > -1:
                    hwnds.append(hwnd)
            return True

        hwnds = []
        win32gui.EnumWindows(callback, hwnds)  # 列出所有顶级窗口，并传递它们的指针给callback函数
        return hwnds

    def maximize_excel(self, file_name):
        """
        激活指定窗口
        :param win_title: 窗口名称
        :return:
        """
        assert file_name, "win_title不能为空！"
        hwnds = self.match_windows(file_name)
        print(hwnds)
        if hwnds:
            win32gui.ShowWindow(hwnds[0], win32con.SW_SHOWMAXIMIZED)  # SW_SHOWNORMAL 默认大小，SW_SHOWMAXIMIZED 最大化显示
            win32gui.SetForegroundWindow(hwnds[0])

    def exit_app(self):
        QtWidgets.QApplication.quit()

    # 禁用按键
    def disable_buttons(self):
        # Disable all buttons
        for button in self.findChildren(QtWidgets.QPushButton):
            button.setEnabled(False)

    # 解除禁用按键
    def enable_buttons(self):
        # Enable all buttons
        for button in self.findChildren(QtWidgets.QPushButton):
            button.setEnabled(True)

    # 双击复选框动作
    def sync_checkboxes(self, clicked_checkbox):
        # Get the state of the clicked checkbox
        clicked_state = clicked_checkbox.isChecked()

        # Set all checkboxes' state to the state of the clicked checkbox
        for checkbox in self.findChildren(QtWidgets.QCheckBox):
            checkbox.setChecked(clicked_state)

    # 获取复选框的选择状态
    def get_checkbox_state(self):
        checkbox_states = {}

        # Get the state of each checkbox and store it in the dictionary
        for checkbox in self.findChildren(QtWidgets.QCheckBox):
            checkbox_states[checkbox.objectName()] = checkbox.isChecked()
        return checkbox_states


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    mainWindow = MainWindow()
    mainWindow.show()
    sys.exit(app.exec_())
