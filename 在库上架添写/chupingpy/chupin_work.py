import os, re, json
from selenium import webdriver
from chupin_window import Ui_MainWindow
import sys
from PyQt5.QtWidgets import QApplication, QWidget, QShortcut, QMessageBox, QMainWindow, QVBoxLayout, QTextEdit, QDialog, \
    QDialogButtonBox, QLabel, QPlainTextEdit
from PyQt5.QtCore import QObject, pyqtSignal, QThread, QTimer
import requests
from lxml import etree
from bs4 import BeautifulSoup


class MyWindow(QMainWindow, Ui_MainWindow):
    re_path = pyqtSignal(str, str)

    def __init__(self):
        super().__init__()
        self.setupUi(self)

        with open("make_dict.json", "r", encoding='utf-8') as f:
            make_dict = json.load(f)
        with open("make_GX.json", "r", encoding='utf-8') as f:
            make_GX = json.load(f)

        for key, item in make_GX.items():
            # print(key)
            self.comboBox_zichengxu.addItem(key)
        # 将QPlainTextEdit的内容变化信号连接到updateHtml槽函数
        self.plainTextEdit.textChanged.connect(self.updateHtml)
        self.lineEdit_xingban.textChanged.connect(self.linexingban)
        self.lineEdit_Qoo10biaoti.textChanged.connect(self.Qoo10biaoti)

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

        # 点击添加分类
        self.pushButton_huoqufenlei.clicked.connect(self.huoqufenlei)

        # 点击开始
        self.pushButton_kaishi.clicked.connect(self.kaishi)

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
                print(tab['url'])

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

    # 点击开始
    def kaishi(self):
        # page_html = self.selenium_open_url('https://kakaku.com/item/K0001580674/')
        url = self.get_kakaku_url()
        if url != '':
            htmlcode = self.get_htmlcode(url)
            # print(htmlcode)
            price = self.getxpath(htmlcode)
        else:
            self.on_error_occurred(f'获取url出错！获取内容={url}')

    def getxpath(self, htmlcode):

        soup = BeautifulSoup(htmlcode, 'html.parser')
        rows = soup.find_all('tr')

        result = []

        for row in rows:
            try:

                price = row.find('p', class_='p-PTPrice_price').text.strip()

                shop_name = row.find('p', class_='p-PTShopData_name').find('a').text.strip()
                shop_location = row.find('p', class_='p-PTStock').text.strip()


                result.append({

                    'price': price,

                    'shop_name': shop_name,
                    'shop_location': shop_location,

                })
            except Exception as e:
                print(e)
        print(result)
        

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


if __name__ == "__main__":
    app = QApplication(sys.argv)

    my_window = MyWindow()
    my_window.show()
    sys.exit(app.exec_())
