import os, re, json, time, datetime, csv
from selenium import webdriver
import sys
from PyQt5.QtWidgets import QApplication, QWidget, QFileDialog, QMessageBox, QMainWindow, QVBoxLayout, QHBoxLayout, \
    QDialog, \
    QDialogButtonBox, QLabel, QPlainTextEdit, QLineEdit, QPushButton, QCheckBox, QScrollArea, QGridLayout, QSplashScreen
from PyQt5.QtGui import QMovie, QPixmap, QTextCursor, QTextCharFormat, QColor
from PyQt5.QtCore import QObject, pyqtSignal, Qt, QThread, QEvent
import requests
import pandas as pd
from bs4 import BeautifulSoup
from chupin_window import Ui_MainWindow
from Excelhandler import ExcelHandler
import pyperclip  # 剪贴板
from collections import OrderedDict
import jaconv  # 英文转小写，片假转平假
from functools import partial


class MyWindow(QMainWindow, Ui_MainWindow):
    re_path = pyqtSignal(str, str)

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setWindowTitle('kakaku出品 1.0')
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
        # self.open_file_dialog()

        # 将QPlainTextEdit的内容变化信号连接到updateHtml槽函数
        self.plainTextEdit.textChanged.connect(self.updateHtml)

        self.lineEdit_xingban.textChanged.connect(self.linexingban)
        self.lineEdit_Qoo10biaoti.textChanged.connect(self.Qoo10biaoti)

        self.lineEdit_jiagewangURL.installEventFilter(self)

        # JAN变化时查找是否出品过
        self.lineEdit_jan.textChanged.connect(self.lineeditJAN)

        # 改变字体大小
        self.spinBox_zitidaxiao.valueChanged.connect(self.setFontSize)
        # 判断是获取还是追加
        self.checkBox_huoqu_zhuijia.clicked.connect(self.huoqu_zhuijia)

        # 设置下面窗口只读
        # self.textEdit.setReadOnly(True)

        # 点击预览
        self.pushButton_yulang.clicked.connect(self.yulang)
        self.pushButton_qingchurn.clicked.connect(self.qingchurn)
        self.pushButton_charuhuanhang.clicked.connect(self.charuhuanghang)
        self.pushButton_charutupian.clicked.connect(self.charutupian)
        self.pushButton_qingkongdaima.clicked.connect(self.qingkongdaima)
        self.pushButton_chongzhi.clicked.connect(self.chongzhi)
        self.pushButton_yunxingzichongxu.clicked.connect(self.run_zichengxu)
        self.pushButton_shengcheng.clicked.connect(self.shengcheng)
        self.pushButton_zhuijia.clicked.connect(self.zhuijia)
        self.pushButton_geshihuahtml.clicked.connect(self.geshihuahtml)
        # self.pushButton_charubiaoge.clicked.connect(self.chuarubiaoge)
        self.pushButton_gaolianxianshi.clicked.connect(self.highlight_text)
        self.pushButton_xingbanchuli.clicked.connect(self.xingbanchuli)
        self.pushButton_huoqu.clicked.connect(self.huoqu)
        self.pushButton_zhuangdao.clicked.connect(self.zhuandao)
        self.pushButton_xiaye.clicked.connect(self.xiaye)

        # 点击添加分类
        self.pushButton_huoqufenlei.clicked.connect(self.huoqufenlei)

        # 点击开始
        self.pushButton_kaishi.clicked.connect(partial(self.kaishi, None))

        self.sku = ''
        self.to_dialog_dict = {}
        self.Qoo10data = ''
        self.csv_filename = None
        # 初始化HTML源码
        self.html_source = ""
        self.downImgUrl = ''
        self.urls_all = 0
        self.sku_list = OrderedDict()
        self.sku_list_dingwei = 0
        # 设置是获取URL还是修正xlsx
        self.huoquORxiuzheng = 'huoqu'

        self.line_dict = {
            "lineEdit_Qoo10biaoti": "Qoo10标题",
            "lineEdit_jiagewangURL": "价格网URL",
            "lineEdit_shuliang": "数量",
            "lineEdit_tupianshu": "图片数",
            "lineEdit_fasongri": "发送日",
            "lineEdit_changjia": "厂家",
            "lineEdit_gebuchuchu": "各部出处",
            # "lineEdit": "标题关键词",
            "lineEdit_jiagewangbiaoti": "价格网标题",
            "lineEdit_jiage_jiagewangfenlei": "价格网分类",
            "lineEdit_jan": "JAN",
            "lineEdit_xingban": "型番",
            "lineEdit_jiage": "价格",
            "lineEdit_jiajia": "加价"

        }

    def huoqu_zhuijia(self):
        if self.checkBox_huoqu_zhuijia.isChecked():
            self.pushButton_huoqu.setText('追加')
        else:
            self.pushButton_huoqu.setText('获取')

    def normalize_key(self, key):
        # 将英文转换为小写
        normalized_key = key.lower()
        # 将片假名转换为平假名
        normalized_key = jaconv.kata2hira(normalized_key)
        return normalized_key

    # 双击价格网URL事件
    def eventFilter(self, obj, event):
        # print('价格网URL双击事件')
        if obj == self.lineEdit_jiagewangURL and event.type() == QEvent.MouseButtonDblClick:
            url = self.lineEdit_jiagewangURL.text()
            os.system(f'start {url}')
            print(f'{url} 以打开')
        return super().eventFilter(obj, event)

    # 点击下一页
    def xiaye(self):
        if self.huoquORxiuzheng == 'huoqu':
            try:
                print(self.sku_list,self.sku_list_dingwei)
                # 迭代获取指定索引的元素
                sku = None
                for i, (key, value) in enumerate(self.sku_list.items()):
                    if i == self.sku_list_dingwei:
                        sku = key
                        break
                if sku is None:
                    QMessageBox.information(self, '提示', '没有找到 sku, 退出！')
                    return
                # sku = self.sku_list[self.sku_list_dingwei][0]
                print(f'点击下页,开始获取{sku}的数据')
                url = f'https://kakaku.com/item/{sku}'
                re_str = self.kaishi(url=url)
                if re_str == 'OK':
                    self.sku_list_dingwei += 1
                    self.label_url_num.setText(f'共{self.urls_all}/现{self.sku_list_dingwei + 1}')
            except Exception as e:
                QMessageBox.information(self, '提示', 'sku获取出错，重试！')
                return
        else:
            try:
                num_str = self.label_url_num.text()
                print(num_str)
                match = re.search(r'现(\d+)', num_str)
                if match:
                    row = int(match.group(1))
                    print(row)
                else:
                    QMessageBox.information(self, '提示', '获取行号出错，请先用转到工作正常后，在次用此功能!')
                    return
                if row < 2:
                    QMessageBox.information(self, '提示', '行号不能小于2！！！')
                    self.lineEdit_zhuandao.setText('2')
                    return
                self.sku_list_dingwei = row - 1
                self.label_url_num.setText(f'共{self.urls_all}/现{row + 1}')
                row_data = self.excel_DF.iloc[row - 1]
                print(row_data)
                self.xiuzhen_write_window(row_data)
            except Exception as e:
                QMessageBox.information(self, '提示', '下一次代码处理错误，重试')
                return

    # 点击转到，获取文本框文本，判断列表中是否存在
    def zhuandao(self):
        print('开始处理转到按键')
        if self.huoquORxiuzheng == 'huoqu':
            print('开始处理 获取 转到按键')
            if self.sku_list:
                sku = self.lineEdit_zhuandao.text()
                if 'K00' in sku:
                    # 遍历列表，找到目标 SKU 的索引
                    for i, (key, value) in enumerate(self.sku_list.items()):
                        if key == sku:
                            # self.sku_list = self.sku_list[i::]
                            self.sku_list_dingwei = i
                            self.label_url_num.setText(f'共{self.urls_all}/现{i + 1}')

                else:
                    try:
                        sku = int(sku)
                        self.sku_list_dingwei = sku - 1
                        self.label_url_num.setText(f'共{self.urls_all}/现{sku}')
                    except:
                        QMessageBox.information(self, '提示', '没有添入SKU，请重新添入！')
                    return
                print(self.sku_list)
            else:
                QMessageBox.information(self, '提示', '没有发现价格表SKU列表，退出！')
                return
        else:
            print('开始处理 修正 转到按键')
            if not self.excel_DF.empty:
                print(self.excel_DF)
                row = int(self.lineEdit_zhuandao.text())
                if row < 2:
                    QMessageBox.information(self, '提示', '行号不能小于2！！！')
                    self.lineEdit_zhuandao.setText('2')
                    return
                self.sku_list_dingwei = row - 2
                self.label_url_num.setText(f'共{self.urls_all}/现{row}')
                row_data = self.excel_DF.iloc[row - 2]
                print(row_data)
                self.xiuzhen_write_window(row_data)

    # 修正是添入窗体数据
    def xiuzhen_write_window(self, df_row):
        print('修正添入窗体数据')
        self.lineEdit_jan.setText(df_row['external_product_id'])
        self.lineEdit_xingban.setText(df_row['seller_unique_item_id'])
        self.lineEdit_jiage.setText(str(int(df_row['price_yen'])))
        self.lineEdit_Qoo10biaoti.setText(df_row['item_name'])
        self.plainTextEdit.setPlainText(df_row['item_description'])

    # 获取价格表列表数据
    def huoqu(self):
        if self.checkBox_huoqu_zhuijia.isChecked():
            print('现在处理追加')
            # self.sku_list = OrderedDict()  # 使用 OrderedDict 来去重并保持顺序
        else:
            print('现在处理获取')
            self.sku_list = OrderedDict()
        self.sku_list_dingwei = 0
        url_str = self.lineEdit_url.text()
        if 'http' in url_str:
            print('开始处理获取数据')
            self.huoquORxiuzheng = 'huoqu'

            self.urls_all = 0
            url = self.get_kakaku_url()
            print(url)

            if 'pdf_pg' in url:
                start_num = int(self.spinBox_kaishi.value())
                end_num = int(self.spinBox_jiesu.value())
                # 使用正则表达式匹配 pdf_pg= 之前的所有内容
                pattern = re.compile(r'^.*pdf_pg=')
                match = pattern.search(url)
                if match:
                    itemurl = match.group(0)
                    # print(f"匹配成功: {itemurl}")
                else:
                    print("匹配失败")
                    QMessageBox.information(self, '提示', f'网址{url}匹配失败，检查后重试！')
                print(f'开始号={start_num},结束号={end_num},url = {itemurl}')
                for current_num in range(start_num, end_num + 1):
                    geturl = f'{itemurl}{current_num}'
                    self.lineEdit_url.setText(geturl)
                    print(f'开始获取{geturl}数据')
                    html_code = self.get_htmlcode(geturl)

                    # 使用正则表达式提取 var 变量的内容
                    pattern = re.compile(r'var variationPopupData = ({.*?});', re.DOTALL)
                    match = pattern.search(html_code)
                    variation_popup_data = None
                    if match:
                        json_text = match.group(1)

                        # 将 JavaScript 对象转换为 JSON 格式（将 False 替换为 false）
                        json_text = json_text.replace('False', 'false')

                        # 解析 JSON 文本为 Python 字典
                        variation_popup_data = json.loads(json_text)

                        # 打印结果
                        print(variation_popup_data)
                    else:
                        pd_variation = QMessageBox.question(self, '提示', '没有打到匹配的JavaScript对象，退出还是继续？',
                                                            QMessageBox.Yes | QMessageBox.No)
                        if pd_variation == QMessageBox.No:
                            return
                        print("未找到匹配的 JavaScript 对象")

                    # 按排除获取行数据
                    soup = BeautifulSoup(html_code, 'html.parser')
                    td_elements = soup.find_all('td', {'class': 'sel alignC ckbtn'})

                    for td in td_elements:
                        input_element = td.find('input', {'name': 'ChkProductID'})
                        if input_element and 'value' in input_element.attrs:
                            # print(input_element['value'],'\n')
                            if 'J' in input_element['value'] and variation_popup_data is not None:
                                for item in variation_popup_data[input_element['value']]['Items']:
                                    sku = item['ChildProductID']
                                    if sku not in self.title_banhao_sku_dict:
                                        self.sku_list[item['ChildProductID']] = None
                            else:
                                sku = input_element['value']
                                if sku not in self.title_banhao_sku_dict:
                                    self.sku_list[input_element['value']] = None  # 值作为键，去重并保持顺序
                                # print(input_element['value'],'\n')
                                # print(variation_popup_data[input_element['value']],'\n')
                # self.sku_list = list(self.sku_list.items())
                print(self.sku_list, len(self.sku_list))
                self.urls_all = len(self.sku_list)
                self.label_url_num.setText(f'共{self.urls_all}/现{self.sku_list_dingwei + 1}')
            else:
                QMessageBox.information(self, '提示',
                                        f'网址 {url} 获取失败，查检网址内是否包含关键词“pdf_di”，或网址出错！')  # 型番处理
        else:
            print('开始处理修正数据')
            self.huoquORxiuzheng = 'xiuzheng'
            excel_work = ExcelHandler(url_str)
            if excel_work.workbook is None:
                QMessageBox.information(self, '提示', f'{url_str} 绑定失败，检查文件是否打开或正在被占用！')
                return
            self.sku_list = excel_work.read_ranges('Sheet1', 'A1')
            self.urls_all = len(self.sku_list)
            self.label_url_num.setText(f'共{self.urls_all}/现{1}')
            # print(excel_work_list,len(excel_work_list))
            self.excel_DF = pd.DataFrame(self.sku_list[1:], columns=self.sku_list[0])
            print(self.excel_DF)

    def xingbanchuli(self, G_str=None):
        print(f'开始处理型号: {G_str}')
        """
                处理型号字符串，从剪贴板获取数据，替换日语颜色为英文简写，并进行字符处理。
                """
        # xb = pyperclip.paste()
        if G_str:
            xb = G_str
            print(f'开始处理传入的数据转为型号: {xb}')

        else:
            # 从剪贴板获取数据
            xb = pyperclip.paste()  # 应该是 paste() 而不是 copy()
            print(f'从剪贴板获取的数据转为型号: {xb}')

        # 定义颜色字典
        color_dict = {
            "ホワイト": "WH", "ブラック": "BK", "ブルー": "BL", "レッド": "RD", "グリーン": "GR",
            "ゴールド": "GD", "シルバー": "SL", "ピンク": "PK", "スペースグレイ": "GY", "イエロー": "YL",
            "アッシュグリーン": "GN", "オレンジ": "OG", "グレイ": "GY", "ボディ": "body", "レンズキット": "LsKit",
            "ベージュ": "BG"
        }

        # 替换颜色名
        for key, value in color_dict.items():
            xb = xb.replace(key, value)

        # 使用正则表达式替换除字母数字外的所有字符为破折号
        xb = re.sub(r'[^A-Za-z0-9]+', '-', xb)

        # 移除连续的破折号
        xb = re.sub(r'-+', '-', xb).strip('-')

        # 如果长度超过20个字符，移除破折号
        if len(xb) > 20:
            xb = xb.replace("-", "")

        print(f'处理后的型号: {xb}')

        # 将结果放入剪贴板
        # pyperclip.copy(xb)
        self.lineEdit_xingban.setText(xb)

        return xb

    # 格式化html
    def geshihuahtml(self):
        html_text = self.plainTextEdit.toPlainText()
        # 使用BeautifulSoup解析HTML
        soup = BeautifulSoup(html_text, 'html.parser')

        # 格式化HTML
        formatted_html = soup.prettify()
        self.plainTextEdit.setPlainText(formatted_html)

    def shengcheng(self):
        # 生成出品文件
        current_date = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M")
        self.csv_filename = f'Z:\\YS登録\\q10\\Qoo10up_{current_date}.xlsx'

        headers = [
            "item_number",
            "seller_unique_item_id",
            "category_number",
            "brand_number",
            "item_name",
            "item_promotion_name",
            "item_status_Y/N/D",
            "end_date",
            "price_yen",
            "retail_price_yen",
            "taxrate",
            "quantity",
            "option_info",
            "additional_option_info",
            "additional_option_text",
            "image_main_url",
            "image_other_url",
            "video_url",
            "image_option_info",
            "image_additional_option_info",
            "header_html",
            "footer_html",
            "item_description",
            "Shipping_number",
            "option_number",
            "available_shipping_date",
            "desired_shipping_date",
            "search_keyword",
            "item_condition_type",
            "origin_type",
            "origin_region_id",
            "origin_country_id",
            "origin_others",
            "medication_type",
            "item_weight",
            "item_material",
            "model_name",
            "external_product_type",
            "external_product_id",
            "manufacture_date",
            "expiration_date_type",
            "expiration_date_MFD",
            "expiration_date_PAO",
            "expiration_date_EXP",
            "under18s_display_Y/N",
            "A/S_info",
            "buy_limit_type",
            "buy_limit_date",
            "buy_limit_qty"
        ]

        # 弹出选择文件对话框
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(self, "选择CSV文件", "", "CSV Files (*.csv);;All Files (*)",
                                                   options=options)
        if file_name:
            try:
                # 读取CSV文件
                df = pd.read_csv(file_name, encoding='utf-8')

                # 创建新数据框架并添加三行空行
                new_data = [headers] + [[''] * len(headers)] * 3

                for index, row in df.iterrows():
                    item_number = ''
                    seller_unique_item_id = row['商品名']
                    category_number = row['Qカテゴリ']
                    brand_number = ''
                    item_name = row['タイトル']
                    item_promotion_name = ''
                    item_status_Y_N_D = 'Y' if row['商品個数'] > 0 else 'N'
                    end_date = '2028-12-31'
                    price_yen = row['予定価格']
                    retail_price_yen = 0
                    taxrate = ''
                    quantity = row['商品個数']
                    option_info = ''
                    additional_option_info = ''
                    additional_option_text = ''
                    shopitme = row['商品説明']

                    if row['IMAGE有無'] > 0:
                        sRet = re.search(r'K\d+', row['補足'])
                        if sRet:
                            sRet = sRet.group(0)
                            sRet1 = f'<img src="https://img1.kakaku.k-img.com/images/productimage/fullscale/{sRet}.jpg" width="500" height="auto"><br><br>'
                            shopitme = f'{sRet1}{row["商品説明"]}'
                            imgURL = f'https://img1.kakaku.k-img.com/images/productimage/fullscale/{sRet}.jpg'
                            if row['IMAGE有無'] > 1:
                                more_images = [
                                    f'https://img1.kakaku.k-img.com/images/productimage/fullscale/{sRet}_000{w}.jpg' for
                                    w
                                    in range(1, row['IMAGE有無'])]
                                more_images = '$$'.join(more_images)
                            else:
                                more_images = ''
                        else:
                            shopitme = row['商品説明']
                            imgURL = row['補足']
                            more_images = ''
                    else:
                        shopitme = row['商品説明']
                        imgURL = row['補足']
                        more_images = ''

                    image_main_url = imgURL if row['IMAGE有無'] > 0 else row['補足']
                    image_other_url = more_images if row['IMAGE有無'] > 1 else ''
                    video_url = ''
                    image_option_info = ''
                    image_additional_option_info = ''
                    header_html = ''
                    footer_html = ''
                    item_description = shopitme
                    Shipping_number = row['送料']
                    option_number = '444697' if row['送料'] == 335370 else ''
                    available_shipping_date = row['発送日']
                    desired_shipping_date = ''
                    search_keyword = ''
                    item_condition_type = 1
                    origin_type = 3
                    origin_region_id = ''
                    origin_country_id = ''
                    origin_others = 'その他'
                    medication_type = ''
                    item_weight = ''
                    item_material = ''
                    model_name = row['商品名']
                    external_product_type = 'JAN'
                    external_product_id = row['商品ID']
                    manufacture_date = ''
                    expiration_date_type = ''
                    expiration_date_MFD = ''
                    expiration_date_PAO = ''
                    expiration_date_EXP = ''
                    under18s_display_Y_N = ''
                    A_S_info = ''
                    buy_limit_type = ''
                    buy_limit_date = ''
                    buy_limit_qty = ''

                    new_row = [
                        item_number, seller_unique_item_id, category_number, brand_number, item_name,
                        item_promotion_name, item_status_Y_N_D, end_date, price_yen, retail_price_yen,
                        taxrate, quantity, option_info, additional_option_info, additional_option_text,
                        image_main_url, image_other_url, video_url, image_option_info, image_additional_option_info,
                        header_html, footer_html, item_description, Shipping_number, option_number,
                        available_shipping_date, desired_shipping_date, search_keyword, item_condition_type,
                        origin_type, origin_region_id, origin_country_id, origin_others, medication_type,
                        item_weight, item_material, model_name, external_product_type, external_product_id,
                        manufacture_date, expiration_date_type, expiration_date_MFD, expiration_date_PAO,
                        expiration_date_EXP, under18s_display_Y_N, A_S_info, buy_limit_type, buy_limit_date,
                        buy_limit_qty
                    ]

                    new_data.append(new_row)

                new_df = pd.DataFrame(new_data, columns=headers)

                # 写入Excel文件
                new_df.to_excel(self.csv_filename, index=False, header=False)

                QMessageBox.information(self, "成功", f"文件已成功保存到: {self.csv_filename}")

            except Exception as e:
                print(f"处理文件时发生错误：{str(e)}")
                QMessageBox.critical(self, "错误", f"处理文件时发生错误：{str(e)}")
        else:
            QMessageBox.warning(self, "警告", "未选择任何文件")

    # 点击追加，追加出品商品到csv文件内
    def zhuijia(self):
        if self.huoquORxiuzheng == 'huoqu':
            tishi_text = '以下控件为空，是否写入：'
            # 遍历窗体上的所有控件
            for widget in self.findChildren(QWidget):
                # 找到类型为 QLineEdit 的控件
                # print(widget.objectName())
                if isinstance(widget, QLineEdit):
                    if widget.text() == '':
                        try:
                            tishi_text = tishi_text + f'\n{self.line_dict[widget.objectName()]} = 空，确认！！！'
                        except:
                            pass

            # 将文本内容重置为空字符串
            if len(tishi_text) > 15:
                pd_chuping = QMessageBox.question(self, '提示', tishi_text, QMessageBox.Yes | QMessageBox.No,
                                                  QMessageBox.Yes)
                if pd_chuping == QMessageBox.No:
                    return
            row_data = self.collect_form_data()
            excle_workbook = None
            # 写入excel

            excel_name = '在庫出力.xlsx'
            excle_workbook = ExcelHandler(excel_name)
            print(excle_workbook.workbook)
            if excle_workbook.workbook is not None:
                print(f'绑定{excel_name}成功')
            else:
                QMessageBox.warning(self, '提示', f'绑定{excel_name}失败,检查文件是否打开或被占用中！！！')
                return
            try:
                excle_workbook.write_last_row('在庫写入', row_data)
            except Exception as e:
                QMessageBox.warning(self, '提示', f'写入{excel_name},检查文件是否打开或被占用中，错误={e}')
                return
            try:
                global driver
                driver.quit()
            except:
                pass
            print('写入成功')
            self.statusbar.showMessage(f'{row_data[0]} 追加写入成功！')
        else:
            print('开始 修正 写入')
            biaoti = self.lineEdit_Qoo10biaoti.text()
            shuoming = self.bianmaozhuanhuan(self.plainTextEdit.toPlainText())

            excel_name = self.lineEdit_url.text()
            excle_workbook = ExcelHandler(excel_name)
            if excle_workbook.workbook is not None:
                print(f'绑定{excel_name}成功')
            else:
                QMessageBox.warning(self, '提示', f'绑定{excel_name}失败,检查文件是否打开或被占用中！！！')
                return

            num_str = self.label_url_num.text()
            match = re.search(r'现(\d+)', num_str)
            if match:
                row = int(match.group(1))
                print(row)
            else:
                QMessageBox.information(self, '提示', '获取行号出错，请先用转到工作正常后，在次用此功能!')
                return
            try:
                excle_workbook.write_cell('Sheet1', f'E{row}', biaoti)
                excle_workbook.write_cell('Sheet1', f'V{row}', shuoming)
                self.statusbar.showMessage(f'{biaoti} 修正写入成功！')
            except Exception as e:
                QMessageBox.information(self, '提示', '修正写入失败，查看文件是否打开或被占用！')

    # 用于生成保存时的行数据
    def collect_form_data(self):
        no_image = ''
        fenlei = ''
        tupianshu = self.lineEdit_tupianshu.text()
        if self.comboBox_fenlei.currentText():
            fenlei_list = self.comboBox_fenlei.currentText().split('_')
            fenlei = fenlei_list[0]
        if self.lineEdit_tupianshu.text() == 'no_img':
            tupianshu = 0
            no_image = 'https://gd.image-qoo10.jp/li/905/567/5162567905.jpg'
        shuoming_str = self.bianmaozhuanhuan(self.plainTextEdit.toPlainText())
        data = [
            self.lineEdit_jan.text(),
            self.lineEdit_xingban.text(),
            shuoming_str,
            self.lineEdit_Qoo10biaoti.text(),
            self.lineEdit_jiage.text(),
            self.lineEdit_shuliang.text(),
            tupianshu,
            self.lineEdit_fasongri.text(),
            self.comboBox.currentText(),
            self.lineEdit_jiagewangbiaoti.text(),
            self.lineEdit_jiagewangURL.text(),
            fenlei,
            self.lineEdit_jiage_jiagewangfenlei.text(),
            self.lineEdit_gebuchuchu.text(),
            self.lineEdit_changjia.text(),
            '',
            '',
            '',
            '',
            '',
            '',
            no_image
        ]
        return data

    # 去除商品说明内空行及\r\n等
    def bianmaozhuanhuan(self, data):
        item = [str(item).encode('ANSI', errors='ignore').decode('ANSI') for item in data]
        text = ''.join(item)
        return self.qukonghang(text)

    def qukonghang(self, text):
        # 移除前后空格
        text = text.strip()
        # 拆分成行
        lines = text.split('\n')
        # 移除空行和只包含空格的行
        cleaned_lines = [line.strip() for line in lines if line.strip()]
        # 将清理后的行合并回一个字符串
        cleaned_text = ''.join(cleaned_lines)
        return cleaned_text

    # 打开窗体时读入Qoo10data
    def open_file_dialog(self):
        read_Qoo10data = 'Qoo10data 读入出错'
        read_title = 'title和番号 读入出错'
        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly
        file_name, _ = QFileDialog.getOpenFileName(self, "打开Qoo10下载文件", r"D:\downloads",
                                                   "Excel Files (*.xlsx);;All Files (*)",
                                                   options=options)
        if file_name:

            try:

                self.Qoo10data = pd.read_excel(file_name, engine='openpyxl')
                read_Qoo10data = 'Qoo10data 读入成功'
                # QMessageBox.information(self, '提示', '文件读入完成')
            except Exception as e:
                QMessageBox.critical(self, '错误', f'Qoo10data文件读入错误: {str(e)}')
        try:
            title_banhao = ExcelHandler('title和番号.xlsm')
            title_banhao_list = title_banhao.read_column('采集 (4)', 'W')
            # print(title_banhao_list[3791::],len(title_banhao_list))
            self.title_banhao_sku_dict = set()
            for item in title_banhao_list:
                # print(item)
                try:
                    sku = re.search(r'k\d+', item, flags=re.IGNORECASE)
                    # print(f'url={url},sku = {sku}')
                    if sku:
                        sku = sku.group()
                        self.title_banhao_sku_dict.add(sku)
                except:
                    pass
            read_title = 'title和番号 读入成功'
        except Exception as e:
            QMessageBox.information(self, '提示', '读取 title和番号.xlsm 文件错误，跳过！')
        self.statusbar.showMessage(f'{read_Qoo10data},{read_title}')

    # JAN变化时触发查重
    def lineeditJAN(self, jan_to_search):
        print(jan_to_search)
        if not jan_to_search.strip() or self.huoquORxiuzheng == 'xiuzheng':  # 空输入时不进行查找
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
                            JAN_PD = QMessageBox.question(self, '查重', f'JAN:{jan_to_search} 重复！\n'
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

    # 获取当前显示窗口的URL

    def get_current_tab_url(self):
        # 获取所有标签页的信息
        response = requests.get('http://localhost:3556/json')
        tabs = json.loads(response.text)

        # 找到当前前台显示的标签页
        for tab in tabs:
            if tab.get('type') == 'page' and tab.get('url'):
                # 这里假设第一个满足条件的页面是前台显示的标签页
                return tab['url']

        return None

    def get_kakaku_url(self):
        # 获取 DevTools 协议的 JSON
        print('开始获取kakaku_URL')
        response = requests.get('http://localhost:3556/json')
        tabs = json.loads(response.text)
        # print(tabs)
        url = ''
        for tab in tabs:
            kakaku_url = re.match(r'^https://kakaku.com/', tab['url'])
            print(kakaku_url)
            if kakaku_url:
                url = tab['url']
                sku = re.search(r'k\d+', url, flags=re.IGNORECASE)
                # print(f'url={url},sku = {sku}')
                if sku:
                    self.sku = sku.group()
                # print(tab['url'], self.sku)
                return url
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

    # 正则获取tab表
    def get_tab(self, sku):
        print('正则开始获取价格网tab')

        url = f'https://kakaku.com/item/{sku}/spec/#tab'

        max_retries = 3  # 设置最大重试次数
        tab_html = ''
        for attempt in range(1, max_retries + 1):
            try:
                html = self.get_htmlcode(url)
                tab_html = re.findall(r'<div id="mainLeft">[\s\S]+?</table>', html)[0]
                break
            except:
                if attempt < max_retries:
                    pass
                else:
                    return ''

        try:
            li_html = re.findall(r'<li>[\s\S]+</li>', tab_html)[0]
        except:
            li_html = ''
        try:
            tab_all_html = re.findall(r'<table[\s\S]+', tab_html)[0]
        except:
            tab_all_html = ''
        goods_html = li_html + '\n' + tab_all_html
        # 移除所有<a>标签
        goods_html = self.yichu_html_biaoqian(goods_html)

        # 表格宽度设为1
        goods_html = re.sub(r'border="0"', ' border="1"', goods_html)

        # print(goods_html)
        return goods_html

    def yichu_html_biaoqian(self, goods_html):
        # 移除所有<a>标签
        goods_html = re.sub(r'<a[\s\S]+?>', '', goods_html)
        goods_html = re.sub(r'</a>', '', goods_html)

        # 移除所有<img>标签
        goods_html = re.sub(r'<img[\s\S]+?>', '', goods_html)

        # 移除所有URL
        goods_html = re.sub(r'https?://\S+', '', goods_html)

        return goods_html

    # 点击重置
    def chongzhi(self):
        print('开始重置窗口')

        # 遍历窗体上的所有控件
        try:
            for widget in self.findChildren(QWidget):
                # 找到类型为 QLineEdit 的控件
                # print(widget.objectName())
                if isinstance(widget, QLineEdit):
                    # 将文本内容重置为空字符串
                    # print(widget.objectName())
                    if widget.objectName() in self.line_dict:
                        widget.setText("")
            self.plainTextEdit.setPlainText('')
            self.lineEdit_fasongri.setText('3')
            # self.comboBox.setCurrentIndex(0)
            self.spinBox_jiagequwei.setValue(5)
            self.lineEdit_jiajia.setText('3500')
            self.spinBox_zitidaxiao.setValue(13)
        except Exception as e:
            print(f'重置窗口出错，e={e}')
        print('重置窗口完成')

    # 点击子程序
    def run_zichengxu(self):
        zichengxu_name = self.comboBox_zichengxu.currentText()
        zichengxu_dict = {}
        zichengxu_url = {}
        data = []
        for key, item in self.make_GX[zichengxu_name].items():
            data.append(key)
        zichengxu_dict[zichengxu_name] = data
        url = self.get_current_tab_url()
        if url is not None:
            zichengxu_url[zichengxu_name] = url
            print(zichengxu_dict, zichengxu_url)
            # 线程中运行子程序
            self.start_janxq(zichengxu_dict, zichengxu_url, 'getjanxq')

    # 点击开始
    def kaishi(self, url=None):
        self.statusbar.showMessage('')
        self.downImgUrl = ''
        self.sku = ''
        to_tanchuan_dict = None
        re_getmake_dict = None
        make_url_dict = None
        re_jan = None
        self.chongzhi()  # 重置
        print(f'url = {url}')
        if url is None:
            url = self.get_kakaku_url()
            print(url)
        try:
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
                # print(f're_getmake_dict={re_getmake_dict}')
            else:
                # print(to_tanchuan_dict,len(to_tanchuan_dict))
                QMessageBox.information(self, '提示', '没有可获取的商家，请添加或继续！')

            # 获取JAN，详情等
            if re_getmake_dict is not None and make_url_dict is not None:
                self.start_janxq(re_getmake_dict, make_url_dict, 'getjanxq')

            return 'OK'
        except Exception as e:
            QMessageBox.warning(self, '提示', f'程序发生错误，e={e}')

    def start_janxq(self, re_getmake_dict, make_url_dict, selcet):
        self.thread = WorkerThread(re_getmake_dict, make_url_dict, method=selcet)
        self.thread.re_JAN_XQ_dict.connect(self.updatajan)
        self.thread.start()
        self.show_loading_image()

    # 显示等待图片
    def show_loading_image(self):
        self.loading_label = QLabel(self)
        self.loading_movie = QMovie('warte.gif')
        self.loading_label.setMovie(self.loading_movie)
        self.loading_label.setAlignment(Qt.AlignCenter)
        self.loading_label.setGeometry(self.rect())
        # self.loading_label.setText('正在获取……')
        self.loading_label.show()
        self.loading_movie.start()

    def hide_loading_image(self):
        self.loading_label.close()

    # 添写jAN等
    def updatajan(self, jandict, gebuchuchu, downimgurl):
        try:
            self.hide_loading_image()
        except:
            pass
        try:
            self.lineEdit_xingban.setText(jandict['型号'])
        except Exception as e:
            pass
        try:
            self.plainTextEdit.setPlainText(jandict['详情'])
        except Exception as e:
            pass

        try:
            self.lineEdit_jan.setText(jandict['JAN'])
        except Exception as e:
            pass
        try:
            self.lineEdit_gebuchuchu.setText(gebuchuchu)
        except Exception as e:
            pass
        self.downImgUrl = downimgurl
        print(f'触发回写= {jandict, gebuchuchu, downimgurl, self.downImgUrl}')
        print(
            f'图片地址={self.downImgUrl}\n 图片数={self.lineEdit_tupianshu.text()}\n型番={self.lineEdit_xingban.text()}')
        if self.downImgUrl != '' and self.lineEdit_tupianshu.text() == '0' and self.lineEdit_xingban.text() != '':
            try:
                self.getdownImgUrl(self.downImgUrl)
            except Exception as e:
                QMessageBox.information(self, '提示', f'下载图片失败，错误原因：{e}')

    def getdownImgUrl(self, url):
        print('开始下载图片')
        # 保存目录
        save_dir = "D:\\Users\\Pictures\\"

        # 新的文件名
        new_file_name = f'{self.lineEdit_xingban.text()}.jpg'

        # 获取文件内容
        response = requests.get(url)
        if response.status_code == 200:
            # 构建完整的保存路径
            save_path = os.path.join(save_dir, new_file_name)

            # 写入文件
            with open(save_path, 'wb') as file:
                file.write(response.content)
            print(f"图片已保存到: {save_path}")
            # QMessageBox.information(self, '提示', f"{self.lineEdit_xingban} 图片已保存到: {save_path}")
            self.statusbar.showMessage(f"{self.lineEdit_xingban.text()} 图片已保存到: {save_path}")
        else:
            print("无法下载图片。状态码:", response.status_code)

            self.statusbar.showMessage(f"无法下载图片: {self.lineEdit_xingban.text()} URL={self.downImgUrl}")

    def getxpath(self, htmlcode):

        soup = BeautifulSoup(htmlcode, 'html.parser')
        rows = soup.find_all('tr')

        cmaker_text = ''
        xingban = ''

        gong = ''

        try:
            # 标题
            title = soup.find('h2', itemprop="name").text.strip()
            self.lineEdit_jiagewangbiaoti.setText(title)
            title_houzhui = self.lineEdit.text()
            print(f'title_houzhui= {title_houzhui}')

            if self.checkBox_biaotiguanjianzi.isChecked():
                print(self.checkBox_biaotiguanjianzi.isChecked())
                search_match = f'(?<=<p>){title_houzhui}[\\s\\S]+?(?=<span)'
                fenlei_str = re.search(search_match, htmlcode)

                if fenlei_str:
                    # 获取匹配到的描述信息数组
                    arr = fenlei_str.group(0).split()

                    # 遍历描述信息数组，拼接到标题后面
                    for item in arr:
                        # 替换掉标题和描述信息中的冒号和中文冒号
                        item = item.replace(':', ' ').replace('：', ' ')
                        item = item.replace('○', 'あり')
                        # 拼接标题和描述信息
                        new_title = f'{title} {item}'.strip()

                        # 判断拼接后的标题长度是否超过 100 个字符
                        if len(new_title) <= 100:
                            # 更新标题为拼接后的标题
                            title = new_title
                        else:
                            # 如果超过，则跳出循环
                            break

                self.lineEdit_Qoo10biaoti.setText(title)
            else:
                self.lineEdit_Qoo10biaoti.setText(title + ' ' + title_houzhui)

            xingban_match = re.search(r'\b[A-Za-z0-9()（）/-]{3,}\b', title)
            if xingban_match:
                xingban = xingban_match.group(0)
                xingban = self.xingbanchuli(xingban)
                self.lineEdit_xingban.setText(xingban)
        except Exception as e:
            QMessageBox.warning(self, '提示', f'获取标题信息出错，e={e}')

        # 厂家
        make = ''
        make_match = re.search(r"(?<=mkrname: ')[\s\S]+?(?=')", htmlcode)
        if make_match:
            make = make_match.group(0)
            make = self.normalize_key(make)  # 大写转小写，片假转平假
        else:
            QMessageBox.warning(self, '提示', f'获取厂家信息出错，e={make_match}')
        self.lineEdit_changjia.setText(make)

        try:
            # 分类
            breadcrumb_items = soup.find_all('span', itemprop='title')
            # Extract the text from the third breadcrumb item
            cmaker_text = breadcrumb_items[2].get_text()
            self.lineEdit_jiage_jiagewangfenlei.setText(cmaker_text)
        except Exception as e:
            QMessageBox.warning(self, '提示', f'获取分类信息出错，e={e}')
        try:
            # 图片
            urls = soup.find('div', id='imgBox').prettify()
            re_urls = re.findall(f'{self.sku}.*?\.jpg', urls)
            self.lineEdit_tupianshu.setText(str(len(re_urls)))
        except Exception as e:
            QMessageBox.warning(self, '提示', f'获取图片信息出错，e={e}')

        if make in self.paichu:
            if self.paichu[make] == 'paichu':
                YN_PD = QMessageBox.question(self, '提示', '此厂家在排除范围，点击”Yes"不在出品！',
                                             QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
                if YN_PD == QMessageBox.Yes:
                    self.chongzhi()
                    return None, None
            else:
                QMessageBox.warning(self, '提示', '此厂家注意图片侵权！')

                self.lineEdit_tupianshu.setText("no_img")

        result = []
        to_dialog_dict = {}
        make_url = {}
        if self.comboBox_shouji_zhengchang.currentText() == '手机':
            zk = "有"
        else:
            zk = '○'
        print(f'在库判断={zk}')
        price_OK = 0
        zk_num = 0

        for i, row in enumerate(rows):
            try:
                shop_location = ''
                if zk == '○':
                    # print('获取非手机数据')
                    # 价格
                    price = row.find('p', class_='p-PTPrice_price').text.strip()
                    # print(price)
                    # 商家名 p-PTShopData_name PTShopData_name
                    shop_name = row.find('p', class_='p-PTShopData_name').find('a').text.strip()
                    # print(shop_name)
                    # 在库状态
                    shop_location = row.find('p', class_='p-PTStock').text.strip()
                    # print(shop_location)
                else:
                    # 价格
                    # print('获取手机数据')
                    price_elem = row.find('p', class_='fontPrice')
                    price = price_elem.text.strip() if price_elem else "价格未知"
                    # print(price)
                    # 商家名
                    shop_name_elem = row.find('td', class_='shopname').find('a')
                    shop_name = shop_name_elem.text.strip() if shop_name_elem else "商家名未知"
                    # print(shop_name)
                    columns = row.find_all('td')
                    # print(len(columns))
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
        all_make = len(result)

        self.label_19_gong_quan.setText(f'共{all_make}/圈{zk_num}')
        if all_make == 0:
            return to_dialog_dict, make_url
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
        print(self.spinBox_jiagequwei.value(), type(self.spinBox_jiagequwei.value()))
        print(price_OK)
        print(to_dialog_dict)
        return to_dialog_dict, make_url

    def open_Tanchuang(self, data):
        # 传入图片数以判断是否勾选
        tupiannum = 0
        tupiannum = self.lineEdit_tupianshu.text()
        try:
            tupiannum = int(self.lineEdit_tupianshu.text())
        except:
            pass
        dialog = TanchuangDialog(data, tupiannum)
        if dialog.exec_() == QDialog.Accepted:
            data = dialog.get_selected_options()
            # print(data)
        else:
            data = None
        return data

    # def selenium_open_url(self, url):
    #     self.driver = webdriver.Chrome()
    #     self.driver.get(url)
    #
    #     page_source = self.driver.page_source
    #     # print(page_source)
    #
    #     # self.driver.quit()
    #
    #     return page_source

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

    def chuarubiaoge(self):
        # 插入kakaku表格
        kakakuurl = self.lineEdit_jiagewangURL.text()
        sku = re.search(r'k\d+', kakakuurl, flags=re.IGNORECASE)

        if not sku:
            QMessageBox.warning(self, '提醒', '价格网URL数据为空，无法获取表格！')
            return
        sku = sku.group()
        print(sku)
        cursor = self.plainTextEdit.textCursor()
        tab_html = self.get_tab(sku)
        cursor.insertText('<br>')
        cursor.insertText(tab_html)
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
        html_source = self.plainTextEdit.toPlainText()
        # 禁用信号，以避免递归调用
        self.textEdit.blockSignals(True)
        # 更新QTextEdit内容
        self.textEdit.setHtml(html_source)
        # 重新启用信号
        self.textEdit.blockSignals(False)

    # 高亮文字
    def highlight_text(self):
        print('开始处理选中文本事件')
        selected_text = self.textEdit.textCursor().selectedText()
        plain_text = self.plainTextEdit.toPlainText()
        cursor = self.plainTextEdit.textCursor()
        # print(cursor)

        # 清除之前的高亮
        cursor.setPosition(0)  # 将光标位置置于文本的开头
        cursor.movePosition(cursor.End, cursor.KeepAnchor)  # 选择整个文本
        format = cursor.charFormat()
        format.setBackground(Qt.white)
        cursor.mergeCharFormat(format)
        cursor.setPosition(0)

        if selected_text:
            print(f'选中文本={selected_text}')
            index = plain_text.find(selected_text)
            print(index)
            if index != -1:
                cursor.setPosition(index)
                cursor.movePosition(cursor.Right, cursor.KeepAnchor, len(selected_text))
                format.setBackground(Qt.yellow)
                cursor.mergeCharFormat(format)
            cursor.setPosition(index - 1)
        self.plainTextEdit.setTextCursor(cursor)


# 获取数据用
class WorkerThread(QThread):
    re_JAN_XQ_dict = pyqtSignal(dict, str, str)
    re_kakaku_data = pyqtSignal(dict)

    def __init__(self, makedict, make_url_dict, method):
        super().__init__()
        print('开始线程内获取数据')
        with open("make_GX.json", "r", encoding='utf-8') as f:
            self.make_GX = json.load(f)
        self.makedict = makedict
        self.make_url_dict = make_url_dict
        self.imgUrl = ''
        self.method = method

    def selenium_open_url(self, url):
        global driver
        driver = webdriver.Chrome()
        driver.get(url)
        page_source = driver.page_source
        # driver.quit()
        return page_source

    def yichu_html_biaoqian(self, goods_html):
        goods_html = re.sub(r'<a[\s\S]+?>', '', goods_html)
        goods_html = re.sub(r'</a>', '', goods_html)
        goods_html = re.sub(r'<img[\s\S]+?>', '', goods_html)
        goods_html = re.sub(r'https?://\S+', '', goods_html)
        return goods_html

    def getjanxq(self):
        get_jan_make = ''
        get_shuoming_make = ''
        get_xingban = ''
        get_tupian = ''
        data_dict = {}

        for make, items in self.makedict.items():
            print(self.make_GX[make])
            page_code = self.selenium_open_url(self.make_url_dict[make])
            for item in items:
                try:
                    re_lists = self.make_GX[make][item]
                    search_str = ''
                    for i, re_str in enumerate(re_lists):
                        try:
                            if i == 0:
                                search_str = re.search(re_str, page_code, flags=re.IGNORECASE)
                                if search_str:
                                    search_str = search_str.group()
                            else:
                                search_str = re.search(re_str, search_str, flags=re.IGNORECASE)
                                if search_str:
                                    search_str = search_str.group()
                        except Exception as e:
                            print(f'公式获取出错，商家={make},i={i},公式={re_str},search_str={search_str}')

                    if search_str != '':
                        if item == '型号':
                            data_dict['型号'] = search_str
                            get_xingban = make
                        if item == '详情':
                            search_str = self.yichu_html_biaoqian(search_str)
                            data_dict['详情'] = search_str
                            get_shuoming_make = make
                        if item == 'JAN':
                            data_dict['JAN'] = search_str
                            get_jan_make = make
                        if item == '图片':
                            self.imgUrl = search_str
                            get_tupian = make
                            print(f'获取到的商家可下载图片URL = {self.imgUrl}')
                except Exception as e:
                    print(f'{make}获取{item}信息出错：{e}')
                    continue
        gubuchuchu = ''
        try:
            gubuchuchu = f'JAN={get_jan_make},型番={get_xingban},说明={get_shuoming_make},图片={get_tupian}'
        except Exception as e:
            print(f'信号发射出错：{e}')
        self.re_JAN_XQ_dict.emit(data_dict, gubuchuchu, self.imgUrl)

    def getkakaku(self):
        kakaku_data = {}
        for make, url in self.make_url_dict.items():
            try:
                page_code = self.selenium_open_url(url)
                kakaku_data[make] = re.findall(r'\d+', page_code)
            except Exception as e:
                print(f'获取{kakaku_data}信息出错：{e}')
        self.re_kakaku_data.emit(kakaku_data)

    def run(self):
        if self.method == 'getjanxq':
            self.getjanxq()
        elif self.method == 'getkakaku':
            self.getkakaku()


# 用于添加商品分类
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
    def __init__(self, data_dict, tupiannum):
        super().__init__()

        self.tupiannum = tupiannum
        self.data_dict = data_dict
        self.selected_options = {}
        self.currently_selected = {"JAN": None, "型号": None, "详情": None, "图片": None}
        with open("make_dict.json", "r", encoding='utf-8') as f:
            self.make_dict = json.load(f)

        # 找出排序最前的商家
        # 找出排序最小的商家
        min_sort_value = float('inf')
        self.min_sort_key = None
        for key, values in self.data_dict.items():
            sort_value = self.make_dict[key][4]  # 第四个元素为排序值
            if sort_value < min_sort_value:
                min_sort_value = sort_value
                self.min_sort_key = key
        print(f'找出的排序最前的商家为 {self.min_sort_key}')

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
                    if key == self.min_sort_key:
                        sub_key_checkbox.setChecked(True)
                        if sub_key == "图片" and self.tupiannum != 0:
                            sub_key_checkbox.setChecked(False)

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

        # 将 "确认" 按钮设置为默认按钮
        close_button.setDefault(True)

        button_layout = QHBoxLayout()
        button_layout.addWidget(cancel_button)
        button_layout.addWidget(close_button)

        layout.addWidget(scroll_area)
        layout.addLayout(button_layout)

        self.setLayout(layout)

        # 根据商家排名顺序自动勾选复选框
        # self.auto_select_checkboxes()

    # 同一列只能选中一个，如JAN不能多选
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


if __name__ == '__main__':
    app = QApplication(sys.argv)

    driver = ''

    splash = QSplashScreen(QPixmap('images.jpg'))
    splash.showMessage('程序加载中(Qoo10data,paichu,title和番号)......', Qt.AlignHCenter | Qt.AlignBottom, Qt.black)
    splash.show()

    main_window = MyWindow()
    main_window.open_file_dialog()
    main_window.show()
    splash.finish(main_window)
    sys.exit(app.exec_())
