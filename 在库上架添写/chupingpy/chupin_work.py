import os, re, json, time
from selenium import webdriver
import sys
from PyQt5.QtWidgets import QApplication, QWidget, QFileDialog, QMessageBox, QMainWindow, QVBoxLayout, QHBoxLayout, \
    QDialog, \
    QDialogButtonBox, QLabel, QPlainTextEdit, QLineEdit, QPushButton, QCheckBox, QScrollArea, QGridLayout
from PyQt5.QtGui import QMovie
from PyQt5.QtCore import QObject, pyqtSignal, Qt
import requests
import pandas as pd
from bs4 import BeautifulSoup
from chupin_window import Ui_MainWindow


class MyWindow(QMainWindow, Ui_MainWindow):
    re_path = pyqtSignal(str, str)

    def __init__(self):
        super().__init__()
        self.setupUi(self)

        with open("make_dict.json", "r", encoding='utf-8') as f:
            self.make_dict = json.load(f)
        with open("make_GX.json", "r", encoding='utf-8') as f:
            self.make_GX = json.load(f)
        with open("paichu.json", "r", encoding='utf-8') as f:
            self.paichu = json.load(f)

        for key, item in self.make_GX.items():
            # print(key)
            self.comboBox_zichengxu.addItem(key)

        # 读取文件时显示等待图片
        self.open_file_dialog()

        # 将QPlainTextEdit的内容变化信号连接到updateHtml槽函数
        self.plainTextEdit.textChanged.connect(self.updateHtml)
        self.lineEdit_xingban.textChanged.connect(self.linexingban)
        self.lineEdit_Qoo10biaoti.textChanged.connect(self.Qoo10biaoti)
        # JAN变化时查找是否出品过
        self.lineEdit_jan.textChanged.connect(self.lineeditJAN)

        # 改变字体大小
        self.spinBox_zitidaxiao.valueChanged.connect(self.setFontSize)

        # 设置下面窗口只读
        self.textEdit.setReadOnly(True)

        # 点击预览
        self.pushButton_yulang.clicked.connect(self.yulang)
        self.pushButton_qingchurn.clicked.connect(self.qingchurn)
        self.pushButton_charuhuanhang.clicked.connect(self.charuhuanghang)
        self.pushButton_charutupian.clicked.connect(self.charutupian)
        self.pushButton_qingkongdaima.clicked.connect(self.qingkongdaima)
        self.pushButton_chongzhi.clicked.connect(self.chongzhi)

        # 点击添加分类
        self.pushButton_huoqufenlei.clicked.connect(self.huoqufenlei)

        # 点击开始
        self.pushButton_kaishi.clicked.connect(self.kaishi)

        self.sku = ''
        self.to_dialog_dict = {}
        self.Qoo10data = ''
    # 以下三个用法用于显示等待GIF图
    def init_waiting_gif(self):
        self.waiting_gif_label = QLabel(self)
        self.waiting_gif_label.setGeometry(0, 0, self.width(), self.height())
        self.waiting_gif_label.setAlignment(Qt.AlignCenter)
        self.waiting_gif = QMovie("warte.gif")
        self.waiting_gif_label.setMovie(self.waiting_gif)
        self.waiting_gif_label.hide()

    def show_waiting_gif(self):
        self.waiting_gif_label.show()
        self.waiting_gif.start()

    def hide_waiting_gif(self):
        self.waiting_gif_label.hide()
        self.waiting_gif.stop()

    # 打开窗体时读入Qoo10data
    def open_file_dialog(self):
        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly
        file_name, _ = QFileDialog.getOpenFileName(self, "打开Qoo10下载文件", r"D:\Users\Downloads",
                                                   "Excel Files (*.xlsx);;All Files (*)",
                                                   options=options)
        if file_name:
            # 显示等待图片
            self.init_waiting_gif()
            self.show_waiting_gif()

            try:
                # 模拟长时间任务
                for i in range(1, 101):
                    time.sleep(0.02)  # 模拟文件加载过程
                self.Qoo10data = pd.read_excel(file_name, engine='openpyxl')
                self.hide_waiting_gif()

                QMessageBox.information(self, 'Success', 'File loaded successfully.')
            except Exception as e:
                self.hide_waiting_gif()
                QMessageBox.critical(self, 'Error', f'Error loading file: {str(e)}')

    # JAN变化时触发查重
    def lineeditJAN(self, jan_to_search):
        print(jan_to_search)
        if not jan_to_search.strip():  # 空输入时不进行查找
            return

        try:
            if self.Qoo10data is not None:
                if 'external_product_id' in self.Qoo10data.columns:
                    # 查找包含指定JAN的行
                    matching_rows = self.Qoo10data[
                        self.Qoo10data['external_product_id'].astype(str).str.contains(jan_to_search)]

                    if not matching_rows.empty:
                        for _, row in matching_rows.iterrows():
                            item_number = row.get('item_number', 'N/A')
                            seller_unique_item_id = row.get('seller_unique_item_id', 'N/A')
                            item_name = row.get('item_name', 'N/A')
                            JAN_PD = QMessageBox.question(self, '查重', f'JAN:{jan_to_search} found.\n'
                                                                        f'番号:{item_number}\n'
                                                                        f'型番:{seller_unique_item_id}\n'
                                                                        f'标题: {item_name}\n'
                                                                        f'以出品！,是否重新出品？',
                                                          QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
                            if JAN_PD == QMessageBox.No:
                                self.chongzhi()

        except Exception as e:
            QMessageBox.critical(self, '错误', f'JAN 查重错误: {str(e)}')

    # 获取Qoo10biaoti字符数
    def Qoo10biaoti(self):
        Qoo10biaoti = self.lineEdit_Qoo10biaoti.text()
        numstr = len(Qoo10biaoti)
        self.label_zishu.setText(f'字数：{numstr}')

    # 获取型番字符数
    def linexingban(self):
        xingban = self.lineEdit_xingban.text()
        numstr = len(xingban)
        self.label_zishu_2.setText(f'字数：{numstr}')

    def get_kakaku_url(self):
        # 获取 DevTools 协议的 JSON
        response = requests.get('http://localhost:3556/json')
        tabs = json.loads(response.text)
        url = ''
        for tab in tabs:
            if 'kakaku.com/item' in tab['url']:
                url = tab['url']
                sku = re.search(r'k\d+', url, flags=re.IGNORECASE)
                print(f'url={url},sku = {sku}')
                if sku:
                    self.sku = sku.group()
                print(tab['url'], self.sku)

        return url

    def on_error_occurred(self, error_message):
        QMessageBox.warning(self, '提醒', f'出错: {error_message}')

    def get_htmlcode(self, url):
        hd = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.51 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "Accept-Language": "ja,zh-CN;q=0.9,zh;q=0.8",

        }
        htmlcode = requests.get(url, headers=hd)
        code = htmlcode.apparent_encoding
        htmlcode.encoding = code
        htmlcode = htmlcode.text
        # print(f'Qoo10价格={htmlcode}')
        return htmlcode

    # 点击重置
    def chongzhi(self):
        # 遍历窗体上的所有控件
        for widget in self.findChildren(QWidget):
            # 找到类型为 QLineEdit 的控件
            if isinstance(widget, QLineEdit):
                # 将文本内容重置为空字符串
                widget.setText("")
        self.plainTextEdit.setPlainText('')
        self.lineEdit_fasongri.setText('3')
        self.comboBox.setCurrentIndex(0)
        self.spinBox_jiagequwei.setValue(5)
        self.lineEdit_jiajia.setText('3500')
        self.spinBox_zitidaxiao.setValue(12)

    # 点击开始
    def kaishi(self):
        # page_html = self.selenium_open_url('https://kakaku.com/item/K0001580674/')
        self.sku = ''
        to_tanchuan_dict = None
        re_getmake_dict = None
        make_url_dict = None
        url = self.get_kakaku_url()
        if url != '':
            self.lineEdit_jiagewangURL.setText(url)
            htmlcode = self.get_htmlcode(url)
            # print(htmlcode)
            # 返回商家公式字典make_GX,和商家URL的dict
            to_tanchuan_dict, make_url_dict = self.getxpath(htmlcode)
        else:
            self.on_error_occurred(f'获取url出错！获取内容={url}')
        if to_tanchuan_dict:
            re_getmake_dict = self.open_Tanchuang(to_tanchuan_dict)
            print(f're_getmake_dict={re_getmake_dict}')
        # 获取JAN，详情等
        if re_getmake_dict is not None and make_url_dict is not None:
            self.getjanxq(re_getmake_dict, make_url_dict)

    # 获取JAN 详情等
    def getjanxq(self, makedict, make_url_dict):

        for make, itmes in makedict.items():
            print(make, itmes)
            print(self.make_GX[make])

            # 获取网页源码
            page_code = self.selenium_open_url(make_url_dict[make])
            for itme in itmes:
                re_lists = self.make_GX[make][itme]
                search_str = ''
                for i, re_str in enumerate(re_lists):
                    if i == 0:
                        search_str = re.search(re_str, page_code, flags=re.IGNORECASE)
                        if search_str:
                            search_str = search_str.group()
                    else:
                        search_str = re.search(re_str, search_str, flags=re.IGNORECASE)
                        if search_str:
                            search_str = search_str.group()
                    print(search_str)

                if search_str != '':
                    if itme == 'JAN':
                        self.lineEdit_jan.setText(search_str)
                    if itme == '型号':
                        self.lineEdit_xingban.setText(search_str)
                    if itme == '详情':
                        self.plainTextEdit.setPlainText(search_str)

    def getxpath(self, htmlcode):

        soup = BeautifulSoup(htmlcode, 'html.parser')
        rows = soup.find_all('tr')
        zk = '○'
        cmaker_text = ''
        try:
            # 标题
            title = soup.find('h2', itemprop="name").text.strip()
            self.lineEdit_jiagewangbiaoti.setText(title)
            self.lineEdit_Qoo10biaoti.setText(title)
            # 厂家
            make = soup.find('li', class_='makerLabel').text.strip()
            self.lineEdit_changjia.setText(make)

            # 分类
            breadcrumb_items = soup.find_all('span', itemprop='title')
            # Extract the text from the third breadcrumb item
            cmaker_text = breadcrumb_items[1].get_text()
            self.lineEdit_jiage_jiagewangfenlei.setText(cmaker_text)
            # 图片
            urls = soup.find('div', id='imgBox').prettify()
            re_urls = re.findall(f'{self.sku}.*?\.jpg', urls)
            self.lineEdit_tupianshu.setText(str(len(re_urls)))

            if make in self.paichu:
                if self.paichu[make] == 'NO':
                    YN_PD = QMessageBox.question(self, '提示', '此厂家在排除范围，点击”Yes"不在出品！',
                                                 QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
                    if YN_PD == QMessageBox.Yes:
                        self.chongzhi()
                        return None, None
                else:
                    self.lineEdit_tupianshu.setText("NO")

        except Exception as e:
            QMessageBox.warning(self, '提示', f'获取信息出错，e={e}')
            return

        result = []
        to_dialog_dict = {}
        make_url = {}
        if '携帯電話' in cmaker_text:
            zk = "有"

        print(f'在库判断={zk}')
        price_OK = 0
        zk_num = 0

        for i, row in enumerate(rows):
            try:
                shop_location = ''
                if zk == '○':
                    # 价格
                    price = row.find('p', class_='p-PTPrice_price').text.strip()
                    print(price)
                    # 商家名 p-PTShopData_name PTShopData_name
                    shop_name = row.find('p', class_='p-PTShopData_name').find('a').text.strip()
                    print(shop_name)
                    # 在库状态
                    shop_location = row.find('p', class_='p-PTStock').text.strip()
                    print(shop_location)
                else:
                    # 价格
                    price = row.find('p', class_='fontPrice').text.strip()
                    # print(price)
                    # 商家名
                    shop_name = row.find('td', class_='shopname').find('a').text.strip()
                    # print(shop_name)
                    columns = row.find_all('td')
                    if len(columns) > 3:  # 确保有足够的列来提取信息
                        shop_location = columns[3].text.strip()
                        # print(f'在库状态: {shop_location}')
                # 判断商家是否在可出品字典中，添加给窗口选择
                shop_url = ''
                if shop_name in self.make_GX:
                    shop_links = row.find_all('a', href=lambda href: href and 'ShopCD=' in href)
                    shop_url = shop_links[0]['href']
                    # print(shop_url)
                    make_url[shop_name] = shop_url
                    to_dialog_dict[shop_name] = self.make_GX[shop_name]
                result.append({

                    'price': price,
                    'shop_name': shop_name,
                    'shop_location': shop_location

                })
                if zk == shop_location:
                    zk_num += 1
                # print(zk, shop_location, zk_num, self.spinBox_jiagequwei.value())
                if zk_num == self.spinBox_jiagequwei.value():
                    price_OK = price

            except Exception as e:
                # print(e)
                pass
        # print(result)
        if price_OK == 0:
            price_OK = result[-1]['price']
            self.lineEdit_shuliang.setText('0')
        else:
            self.lineEdit_shuliang.setText('1')
        price_OK = int(price_OK.replace('¥', '').replace(',', ''))
        print(price_OK)
        if price_OK >= 60000:
            price_OK = int((price_OK + int(self.lineEdit_jiajia.text())) / 0.983 / 0.92)
        else:
            price_OK = int((price_OK + int(self.lineEdit_jiajia.text())) / 0.92)
        self.lineEdit_jiage.setText(str(price_OK))
        print(price_OK)
        print(to_dialog_dict)
        return to_dialog_dict, make_url

    def open_Tanchuang(self, data):
        dialog = TanchuangDialog(data)
        if dialog.exec_() == QDialog.Accepted:
            data = dialog.get_selected_options()
            # print(data)
        else:
            data = None
        return data

    def selenium_open_url(self, url):
        driver = webdriver.Chrome()
        driver.get(url)

        page_source = driver.page_source
        # print(page_source)

        driver.quit()

        return page_source

    # 获取分类
    def huoqufenlei(self):
        dialog = DataInputDialog()
        if dialog.exec_() == QDialog.Accepted:
            data = dialog.getData()
            print(data)
            self.comboBox_fenlei.clear()
            for item in data:
                item = re.sub('\\s+', '_', item)

                print(item)
                self.comboBox_fenlei.addItem(item)

    # 点击预览
    def qingchurn(self):
        # 获取QPlainTextEdit的内容并清除\r\n
        plainText = self.plainTextEdit.toPlainText()
        cleanedText = plainText.replace('\r', '').replace('\n', '')
        cleanedText = re.sub(r'\s+', ' ', cleanedText)
        self.plainTextEdit.setPlainText(cleanedText)

    def charuhuanghang(self):
        # 在当前光标位置插入换行
        cursor = self.plainTextEdit.textCursor()
        cursor.insertText('<br>')
        self.plainTextEdit.setTextCursor(cursor)

    def charutupian(self):
        # 在当前光标位置插入图片标签
        cursor = self.plainTextEdit.textCursor()
        cursor.insertText('<img src="image" width="300" Height="auto">')
        self.plainTextEdit.setTextCursor(cursor)

    def qingkongdaima(self):
        # 清空代码
        clear_as = QMessageBox.question(self, '提示', '是否清空代码，不可恢复！', QMessageBox.Yes | QMessageBox.No,
                                        QMessageBox.Yes)
        if clear_as == QMessageBox.Yes:
            self.plainTextEdit.setPlainText('')

    def yulang(self):
        # 获取QPlainTextEdit的内容
        plainText = self.plainTextEdit.toPlainText()

        try:
            # 写入txt文件
            with open('D:/outhtml.html', 'w', encoding='utf-8') as file:
                file.write(plainText)
            os.startfile("D:/outhtml.html")
            # QMessageBox.information(self, 'Success', 'Content exported to D:/outhtml.txt')
        except Exception as e:
            QMessageBox.warning(self, 'Error', f'Failed to export content: {e}')

    def setFontSize(self, size):
        font = self.plainTextEdit.font()
        font.setPointSize(size)
        self.plainTextEdit.setFont(font)
        self.textEdit.setFont(font)

    def updateHtml(self):
        # 获取QPlainTextEdit的内容并将其设置为QTextEdit的HTML内容
        plainText = self.plainTextEdit.toPlainText()
        self.textEdit.setHtml(plainText)


class DataInputDialog(QDialog):
    def __init__(self):
        super().__init__()

        self.setWindowTitle('获取分类代码')
        self.setGeometry(100, 100, 400, 300)

        self.layout = QVBoxLayout()

        self.label = QLabel('添入分类代码')
        self.layout.addWidget(self.label)

        self.inputField = QPlainTextEdit(self)
        self.layout.addWidget(self.inputField)

        self.buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)
        self.layout.addWidget(self.buttonBox)

        self.setLayout(self.layout)

    def getData(self):
        # 获取输入的文本
        text = self.inputField.toPlainText()
        # 将文本按行分割成列表
        lines = text.split('\n')
        # 返回列表
        return lines


# 复选框弹窗
class TanchuangDialog(QDialog):
    def __init__(self, data_dict, width=800, title="Data Input Dialog"):
        super().__init__()

        self.data_dict = data_dict
        self.selected_options = {}
        self.currently_selected = {"JAN": None, "型号": None, "详情": None, "图片": None}

        self.init_ui()

        # 设置窗口固定宽度和标题
        self.setFixedWidth(400)
        self.setFixedHeight(800)
        self.setWindowTitle('出品商家选择')

    def init_ui(self):
        layout = QVBoxLayout()

        # 创建一个 QScrollArea
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)

        # 创建一个容器 widget，内容放在这个 widget 上
        container_widget = QWidget()
        self.grid_layout = QGridLayout(container_widget)

        # 初始化行索引
        row = 0

        for key, items in self.data_dict.items():
            group_label = QCheckBox(key)
            group_label.setTristate(False)
            group_label.setChecked(False)
            group_label.setStyleSheet("QCheckBox::indicator { width: 0px; }")
            self.grid_layout.addWidget(group_label, row, 0, 1, 4)  # 占据一行的四列

            col_positions = {"JAN": 0, "型号": 1, "详情": 2, "图片": 3}
            col_occupied = [False] * 4

            for sub_key, formulas in items.items():
                if formulas and sub_key in col_positions:
                    col = col_positions[sub_key]
                    sub_key_checkbox = QCheckBox(sub_key)
                    sub_key_checkbox.setObjectName(f"{key}_{sub_key}")
                    sub_key_checkbox.stateChanged.connect(self.check_unique_selection)

                    self.grid_layout.addWidget(sub_key_checkbox, row + 1, col)
                    col_occupied[col] = True

            # 用空标签占位
            for col, occupied in enumerate(col_occupied):
                if not occupied:
                    placeholder_label = QLabel("")
                    self.grid_layout.addWidget(placeholder_label, row + 1, col)

            row += 2  # 每组占据两行

        scroll_area.setWidget(container_widget)

        cancel_button = QPushButton('取消')
        cancel_button.clicked.connect(self.cancel_dialog)

        close_button = QPushButton('确认')
        close_button.clicked.connect(self.close_dialog)

        button_layout = QHBoxLayout()
        button_layout.addWidget(cancel_button)
        button_layout.addWidget(close_button)

        layout.addWidget(scroll_area)
        layout.addLayout(button_layout)

        self.setLayout(layout)

    def check_unique_selection(self, state):
        sender = self.sender()
        if state == 2:  # 选中
            item_type = sender.text()
            current_selection = self.currently_selected.get(item_type)
            if current_selection:
                reply = QMessageBox.question(
                    self, "替换确认",
                    f"已经选择了一个 {item_type}，是否要替换？",
                    QMessageBox.Yes | QMessageBox.No, QMessageBox.No
                )
                if reply == QMessageBox.No:
                    sender.setChecked(False)
                    return
                else:
                    current_selection.setChecked(False)

            self.currently_selected[item_type] = sender
        elif state == 0:  # 取消选中
            item_type = sender.text()
            if self.currently_selected.get(item_type) == sender:
                self.currently_selected[item_type] = None

    def cancel_dialog(self):

        self.reject()

    def close_dialog(self):
        for key, items in self.data_dict.items():
            for sub_key, formulas in items.items():
                checkbox = self.findChild(QCheckBox, f"{key}_{sub_key}")
                if checkbox and checkbox.isChecked():
                    if key not in self.selected_options:
                        self.selected_options[key] = []
                    self.selected_options[key].append(sub_key)

        self.accept()

    def get_selected_options(self):
        return self.selected_options


if __name__ == "__main__":
    app = QApplication(sys.argv)

    my_window = MyWindow()
    my_window.show()
    sys.exit(app.exec_())
