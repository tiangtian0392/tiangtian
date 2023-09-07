
import sys
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import *
from Top10_window import Ui_MainWindow
import chardet
import win32com.client,json,os,datetime,re
import pythoncom
import pandas as pd
import requests,time,threading
from lxml import etree

status_code = 0

class mywindow(QtWidgets.QMainWindow, Ui_MainWindow):
    signal_1 = QtCore.pyqtSignal(str)
    def __init__(self):
        super(mywindow, self).__init__()
        self.setupUi(self)
        self.setWindowTitle('Top10 1.0')

        self.title_path = r"Z:\bazhuayu\title和番号.xlsm"

        self.from_top10file_pushButton.clicked.connect(self.import_top10)

    def import_top10(self):
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(None, "选择文件", "", "CSV 文件 (*.csv);;Excel 文件 (*.xlsx)")

        # 检测文件编码
        with open(file_path, 'rb') as f:
            result = chardet.detect(f.read())
            print("检测到的文件编码为：", result)

        if file_path:
            # 处理文件并生成 Top10_list 数组
            # 在这里添加代码来读取文件并生成数组
            # 例如，可以使用 pandas 库来读取文件
            """
            title和番号.xlsm 的全部列名
            ['Source.Name', '商品番号', '增加列：kakaku标题', 'seller_unique_item_id',
            'item_name', 'category_number', 'brand_number', 'external_product_id',
            '手续料 ', 'Shipping_number', 'option_number', '商品加价', 'グローバル<br/>販売',
            '販売プロパティ', '大分類', '中分類', '小分類', '重量', 'マーケット', '在庫管理番号', 'Q-在庫コード',
            '登録日', 'Column22', 'Column23', 'Column24', 'Column25', 'Column26']
            
            下句示例根据标题来取得行内容，用法和字典差不多，
            filtered_df = title_df.loc[title_df['增加列：kakaku标题'] == 'Brain PW-SH7-R [レッド系]',['Source.Name','商品番号','增加列：kakaku标题','手续料 ','商品加价','Column22']]
            """

            self.title_df = pd.read_excel(self.title_path, sheet_name=1)



            df = pd.read_csv(file_path, encoding=result['encoding'],header=None)  # 替换此行以适应实际文件读取的代码
            Top10_list = df.values.tolist()  # 将 DataFrame 转换为列表
            print(Top10_list)  # 仅用于示例，可以删除这行


            # 禁用按钮
            self.from_top10file_pushButton.setEnabled(False)

            self.get_kakaku_data_thread(Top10_list)

            # # 启动多线程进行数据获取和写入
            # thread = threading.Thread(target=self.get_kakaku_data_thread, args=(Top10_list,))
            # thread.start()

    def get_kakaku_data_thread(self, top10_list):
        print('超线程开始')
        for item in top10_list:
            url = item[1]  # 假设URL存储在列表中的第1个位置
            try:
                num = item[2]
            except:
                num = 10

            # 调用获取数据的函数
            self.get_kakaku_data(url,num)


        # 处理完成后，重新启用按钮
        self.from_top10file_pushButton.setEnabled(True)

def get_kakaku_data(url=None, num=10):
    print('获取网页开始',url)
    hd = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.51 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "Accept-Language": "ja,zh-CN;q=0.9,zh;q=0.8",
    }
    import requests
    # url = 'https://kakaku.com/camera/digital-slr-camera/itemlist.aspx?pdf_pg=1'
    htmlcode = requests.get(url, headers=hd,timeout=10)
    global status_code
    if htmlcode.status_code != 200:
        status_code += 1
    code = htmlcode.apparent_encoding
    htmlcode.encoding = code
    htmlcode = htmlcode.text
    htmlcode = htmlcode.replace("㈱", "(株)")
    htmlcode = htmlcode.replace("デンキヤ.com ", "デンキヤ.com")
    # print(htmlcode)

    tmp_html = 'temp.html'
    with open(tmp_html,'w+',encoding='utf-8') as f:
        f.write(htmlcode)
        f.seek(0)
        newhtmlcode = f.read()

    # print(newhtmlcode)


    # # 使用 etree.HTML 解析 HTML
    # mytree = etree.HTML(htmlcode)
    #
    # # 获取所有 td 标签，标题行内容
    # titles_list = mytree.xpath('//td[@class="ckitemLink xh-highlight"]')
    # print(titles_list)
    #
    # # 遍历标签行，获取网址和标题
    # for i, item in enumerate(titles_list):
    #     a_element = item.xpath('./a[not(span)]')
    #     print(a_element)
    #     if a_element:
    #         # 获取 <a> 元素的 href 属性
    #         href = a_element[0].get('href')
    #         print(href)
    #
    #         # 获取 <a> 元素的文本
    #         text = a_element[0].text
    #         print(text)
    #
    #         # 判断网址后的内容是以 "K" 开头还是以 "J" 开头
    #         if href.endswith("/"):
    #             item_id = href.split("/")[-2]
    #             if item_id.startswith("K"):
    #                 print("网址后的内容以 'K' 开头")
    #             elif item_id.startswith("J"):
    #                 print("网址后的内容以 'J' 开头")

get_kakaku_data()
if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = mywindow()

    win.show()
    sys.exit(app.exec_())
