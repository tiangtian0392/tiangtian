import sys
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import QClipboard, QGuiApplication
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QColor
from PyQt5.QtCore import Qt
from Top10_window import Ui_MainWindow
import chardet
import os,re,csv
import pandas as pd
import requests,time
from lxml import etree
from PyQt5.QtCore import QThreadPool

status_code = 0
stop = 1 # 停止标志
text = ''

class mywindow(QtWidgets.QMainWindow, Ui_MainWindow):
    signal_1 = QtCore.pyqtSignal(str)
    def __init__(self):
        super(mywindow, self).__init__()
        self.setupUi(self)
        self.setWindowTitle('Top10 1.0')

        #设置表格列宽
        tableWidth = [100,80,150,80,150,80,80,80,80,80]
        for i,item in enumerate(tableWidth):
            self.tableWidget.setColumnWidth(i,item)

        # 进度条前添加文本标签
        self.label = QLabel(self)
        self.statusBar().addPermanentWidget(self.label)

        # 添加进度条控件
        self.progress_bar = QProgressBar(self)
        self.statusBar().addPermanentWidget(self.progress_bar)

        #添加菜单
        self.actionaaa.triggered.connect(self.on_category_selection)

        # 启用右键
        self.tableWidget.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.tableWidget.customContextMenuRequested.connect(self.table_right_menu)

        #点击的行变色
        self.tableWidget.itemSelectionChanged.connect(self.highlight_selected_row)

        #导入按键
        self.from_top10file_pushButton.clicked.connect(self.import_top10)

        #重置键
        self.chongzhi_pushButton.clicked.connect(self.chongzhi_PUB)

        #开始按键
        self.start_pushButton.clicked.connect(self.start_PUB)

        #停止按键
        self.stop_pushButton.clicked.connect(self.stop_PUB)

        # 线程池
        self.thread_pool = QThreadPool()
        self.thread_pool.setMaxThreadCount(4)  # 设置线程池最大线程数为4
    #点击行变色
    def highlight_selected_row(self):
        selected_items = self.tableWidget.selectedItems()
        if not selected_items:
            return

        selected_row = selected_items[0].row()

        # 取消其他行的颜色
        for row in range(self.tableWidget.rowCount()):
            for column in range(self.tableWidget.columnCount()):
                item = self.tableWidget.item(row, column)
                if item:
                    item.setBackground(QColor(255, 255, 255))  # 设置背景色为白色

        # 设置选中行的颜色
        for column in range(self.tableWidget.columnCount()):
            item = self.tableWidget.item(selected_row, column)
            if item:
                item.setBackground(QColor(0, 176, 80))  # 设置背景色为绿色

        # 设置选中行的第6列和第4列的背景色
        item6 = self.tableWidget.item(selected_row, 6)
        if item6:
            item6.setBackground(QColor(237, 125, 49))

        item4 = self.tableWidget.item(selected_row, 4)
        if item4 and item4.text() != '在库：/排除：':
            item4.setBackground(QColor(237, 125, 49))

    #运行前载入前置文件，在库，排除，title等
    def zaiku_paichu_getdata(self):
        file_zaiku_path = r"Z:\bazhuayu\在庫.csv"
        file_paichu_path = r"Z:\bazhuayu\paichu.xlsx"
        title_path = r"Z:\bazhuayu\title和番号.xlsm"

        self.title_df = pd.read_excel(title_path, sheet_name=1)
        self.paichu_df = pd.read_excel(file_paichu_path, sheet_name=0)
        self.paichu_df.fillna('有',inplace=True)

        with open(file_zaiku_path, 'rb') as f:
            result = chardet.detect(f.read())
            # print("检测到的文件编码为：", result)
            zaiku_df = pd.read_csv(file_zaiku_path,encoding=result['encoding'])
            # 在构建字典时，将"商品ID"列作为字符串类型的key，"在庫数"列作为value，构建字典
            self.zaiku_dict = dict(zip(zaiku_df['商品ID'].astype(str).str.strip(), zaiku_df['在庫数']))

            # print(self.zaiku_dict)


    #任务栏前Label标签文本设置
    def Labe_one_settext(self,text):
        self.statusbar.showMessage(text)

    #处理点击分类选择
    def on_category_selection(self):
        dialog = CategorySelectionDialog(self)
        dialog.lable_text.connect(self.Labe_one_settext)
        if dialog.exec_() == QDialog.Accepted:
            # 获取 top10_list 属性
            top10_list = dialog.top10_list
            # print(top10_list)
            # 在这里进行主窗体的后期处理，使用 top10_list 数据
            if top10_list:
                self.work_thread(top10_list)
    def stop_PUB(self):
        global stop
        stop = 0
        self.from_top10file_pushButton.setEnabled(True)
        self.start_pushButton.setEnabled(True)
        QMessageBox.information(self,'程序停止','程序停止中，请等待工作中的任务结束！')

    def start_PUB(self):
        global stop
        stop = 1

        print('程序开始运行')
        row_count = self.tableWidget.rowCount()

        self.dayuzhi = int(self.dayu_lineEdit.text())
        self.zengfu = float(self.jiagezengfu_lineEdit.text())
        # print(self.dayuzhi,self.zengfu)

        self.jishu = 1
        self.rows = row_count
        self.Labe_one_settext('开始扫描，共计{}个任务。'.format(row_count))

        if self.dayuzhi < 50000:
            reply = QMessageBox.question(self,"大于值提示",'大于值小于50000，确认是否正确，没问题点击 YES。否则退出修改！',
                                         QMessageBox.Yes | QMessageBox.Cancel, QMessageBox.Cancel)

            if reply != QMessageBox.Yes:
                return
        if self.zengfu != 0.983:
            reply = QMessageBox.question(self,"大于值提示",'增幅值不等于0.983，确认是否正确，没问题点击 YES。否则退出修改！',
                                         QMessageBox.Yes | QMessageBox.Cancel, QMessageBox.Cancel)

            if reply != QMessageBox.Yes:
                return


        if row_count > 0:
            # 禁用按钮
            self.from_top10file_pushButton.setEnabled(False)
            self.start_pushButton.setEnabled(False)


            for row in range(row_count):

                if stop == 0:
                    break

                jiajia = int(round(float(self.tableWidget.item(row, 8).text())))
                shoushuliao = self.tableWidget.item(row, 7).text()
                url_item = self.tableWidget.item(row, 9)

                if url_item:
                    url = url_item.text()
                    self.process_url(url, row, jiajia, shoushuliao)

    def process_url(self, url, row, jiajia, shoushuliao):
        filename = self.tableWidget.item(row,1).text()
        if '電話' in filename:
            filenum = '6'
        else:
            filenum = '1'

        worker = Kakaku_work(url, row, jiajia, shoushuliao,self.dayuzhi,self.zengfu,filenum)
        worker.xinghao_signal.jiage.connect(self.update_jiage)
        worker.xinghao_signal.stop_pyqt.connect(self.worker_finished)
        self.thread_pool.start(worker)
    def update_jiage(self, row, K_jiage, jiage, tishi):
        print('主窗体价格回写开始',row, K_jiage, jiage, tishi)
        # 使用线程安全机制将更新操作发送到主线程执行
        paiwei = self.tableWidget.item(row, 3)
        xulei = str(re.findall('.*/',paiwei.text())[0])
        # print(xulei)

        # 创建 QTableWidgetItem 对象
        item_xulei_tishi = QTableWidgetItem(xulei + str(tishi))
        item_k_jiage = QTableWidgetItem(str(K_jiage))
        item_jiage = QTableWidgetItem(str(jiage))

        # 设置单元格的内容
        self.tableWidget.setItem(row, 3, item_xulei_tishi)
        self.tableWidget.setItem(row, 5, item_k_jiage)
        self.tableWidget.setItem(row, 6, item_jiage)


        self.label.setText('以完成{}个任务/共计{}个任务'.format(self.jishu,self.rows))
        self.jishu += 1
        print('主窗体价格回写开始结束')
        self.worker_finished()
    def worker_finished(self):
        if self.thread_pool.activeThreadCount() == 0 or self.jishu == self.rows:
            # 在工作完成且线程池为空闲时启用按钮
            self.from_top10file_pushButton.setEnabled(True)
            self.start_pushButton.setEnabled(True)

            QMessageBox.information(self,'工作结束','程序工作完成，点击关闭窗口！')
            self.label.setText('')


    def chongzhi_PUB(self):

        self.from_top10file_pushButton.setEnabled(True)
        self.start_pushButton.setEnabled(True)
        self.stop_pushButton.setEnabled(True)

        # 弹出提示框
        reply = QMessageBox.question(self, '重置确认', '重置会清除所有表格并不能恢复，确认要继续吗？',
                                     QMessageBox.Yes | QMessageBox.Cancel, QMessageBox.Cancel)

        if reply == QMessageBox.Yes:
            # 用户确认清除，执行重置操作
            self.tableWidget.clearContents()  # 清除表格内容
            self.tableWidget.setRowCount(0)  # 设置表格行数为0
            # 其他清除操作...
            self.label.setText('')
            self.progress_bar.setValue(0)
            # 弹出重置成功提示框
            QMessageBox.information(self, '提示', '重置成功')
        else:
            # 用户取消清除，不执行任何操作
            pass

    def table_right_menu(self, pos):
        selected_item_list = self.tableWidget.selectedItems()
        if len(selected_item_list) > 0:
            menu = QMenu()
            item_openurl = menu.addAction('打开网页')
            item_copy = menu.addAction('复制')
            action = menu.exec_(self.tableWidget.mapToGlobal(pos))

            if action == item_openurl:
                for item in selected_item_list:
                    index = item.row()
                    url = self.tableWidget.item(index, 9).text()
                    os.system('start ' + url)

            elif action == item_copy:
                clipboard = QApplication.clipboard()
                text = ''
                for item in selected_item_list:
                    index = item.row()
                    text += self.tableWidget.item(index, 0).text() + '\n'
                clipboard.setText(text)

    def import_top10(self):
        self.Labe_one_settext('导入开始，等待载入文件…………')

        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(None, "选择文件", "", "CSV 文件 (*.csv);;Excel 文件 (*.xlsx)")



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
            # 检测文件编码
            with open(file_path, 'rb') as f:
                result = chardet.detect(f.read())
                # print("检测到的文件编码为：", result)

            df = pd.read_csv(file_path, encoding=result['encoding'], header=None)  # 替换此行以适应实际文件读取的代码
            Top10_list = df.values.tolist()  # 将 DataFrame 转换为列表

            self.work_thread(Top10_list)

    def work_thread(self,Top10_list):

        self.text = ''

        self.progress_bar.setValue(0)

        #读取前置三个文件
        self.zaiku_paichu_getdata()
        # 禁用按钮
        self.from_top10file_pushButton.setEnabled(False)
        self.start_pushButton.setEnabled(False)

        self.progress_bar.show()  # 显示进度条

        self.work = open_path(Top10_list)
        self.work.progress_update.connect(self.sheet_uprow)
        self.work.update_ok.connect(self.updata_ok)
        self.work.lable_text.connect(self.set_progress_text)
        self.work.jindutiao_update.connect(self.jingdutiao_update)
        self.work.start()

    def set_progress_text(self,text):
        self.label.setText(text)

    # 更新进度条值
    def jingdutiao_update(self,value):
        self.progress_bar.setValue(value)


    def updata_ok(self,str):
        clipboard = QGuiApplication.clipboard()
        clipboard.setText(self.text)

        if self.text != '':
            QMessageBox.information(self, "提示", "以下标题未找到，内容已复制到剪贴板：\n" + self.text)
        else:
            QMessageBox.information(self, "提示", "导入完成")
        # 处理完成后，重新启用按钮
        self.from_top10file_pushButton.setEnabled(True)
        self.chongzhi_pushButton.setEnabled(True)
        self.start_pushButton.setEnabled(True)
        self.label.setText('')
        self.progress_bar.hide()    # 隐藏进度条
        QMessageBox.information(self, '提示', '导入完成')

    def sheet_uprow(self,title,xulei):
        print('表添加行，title={},序列={}'.format(title,xulei))
        rows = self.title_df.loc[self.title_df['增加列：kakaku标题'] == title,['Source.Name','商品番号','增加列：kakaku标题','手续料 ','商品加价','Column22','external_product_id']]
        # print(rows)

        #设置在库和排除提示
        zaiku_value = ''
        paichu_date = ''

        if rows.empty:
            self.text = self.text + title + '\n'
        else:
            # 遍历表格，检查标题是否已存在
            for row in range(self.tableWidget.rowCount()):
                table_banhao = self.tableWidget.item(row, 0).text()  # 获取表格中的商品番号
                # print('商品番号重复不在添加', table_banhao, rows['商品番号'].values[0])
                if int(table_banhao) == int(rows['商品番号'].values[0]):
                    # print('商品番号重复不在添加', table_banhao, rows['商品番号'].values[0])
                    self.Labe_one_settext('商品番号:{}重复不在添加'.format(table_banhao))
                    # 如果标题已存在于表格中，则不进行添加，直接返回
                    return

            #获取排除文档
            paichu_list = self.paichu_df.loc[self.paichu_df['商品コード'] == rows['商品番号'].values[0],['商品コード','結束日期']]
            if not paichu_list.empty:
                # print('paichu_date',paichu_list)
                paichu_value = paichu_list['結束日期'].values[0]
                if paichu_value:
                    paichu_date = paichu_list['結束日期'].values[0]
                    paichu_date = str(paichu_date)[:10]
                else:
                    paichu_date = '有'
            #获取在库
            external_product_id = str(rows['external_product_id'].values[0])
            # print(rows)

            if external_product_id in self.zaiku_dict:
                # print('zaiku_list',zaiku_list,len(zaiku_list))
                zaiku_value = self.zaiku_dict[external_product_id]
            # print("self.zaiku_df['商品ID'] == rows['external_product_id'].values[0],",
                  # rows['external_product_id'].values[0], external_product_id,zaiku_value)
            tishi = '在库：{}/排除：{}'.format(zaiku_value,paichu_date)

            teb_rows = self.tableWidget.rowCount()
            self.tableWidget.insertRow(teb_rows)

            cell = QTableWidgetItem(tishi)
            self.tableWidget.setItem(teb_rows, 4, cell)

            cell = QTableWidgetItem(str(rows['Source.Name'].values[0]))
            self.tableWidget.setItem(teb_rows, 1, cell)

            cell = QTableWidgetItem(str(int(rows['商品番号'].values[0])))
            self.tableWidget.setItem(teb_rows, 0, cell)

            cell = QTableWidgetItem(str(rows['增加列：kakaku标题'].values[0]))
            self.tableWidget.setItem(teb_rows, 2, cell)

            cell = QTableWidgetItem(str(xulei) + '/')
            self.tableWidget.setItem(teb_rows, 3, cell)

            cell = QTableWidgetItem(str(rows['手续料 '].values[0]))
            self.tableWidget.setItem(teb_rows, 7, cell)

            cell = QTableWidgetItem(str(rows['商品加价'].values[0]))
            self.tableWidget.setItem(teb_rows, 8, cell)

            cell = QTableWidgetItem(str(rows['Column22'].values[0]))
            self.tableWidget.setItem(teb_rows, 9, cell)
            self.Labe_one_settext('表格:{}行添加完成'.format(teb_rows+1))

class open_path(QtCore.QThread):
    progress_update = QtCore.pyqtSignal(str,int)
    update_ok = QtCore.pyqtSignal(str)
    lable_text = QtCore.pyqtSignal(str)
    jindutiao_update = QtCore.pyqtSignal(int)

    def __init__(self, Top10_list,parent=None):
        super(open_path, self).__init__(parent)
        self.Top10_list = Top10_list


    def run(self) -> None:

            # print(Top10_list)  # 仅用于示例，可以删除这行

            self.get_kakaku_data_thread(self.Top10_list)

    def stop(self):
        # 请求中断
        self.requestInterruption()
    #&amp;转&
    def title_del_str(self,title):
        title = title.replace('&amp;','&')
        title = title.replace('&#39;', '’')
        return title

    def get_kakaku_data_thread(self, top10_list):
        print('超线程开始')
        self.text = ''
        for i,item in enumerate(top10_list):
            self.lable_text.emit("正在执行：第{}个任务/共{}个任务".format(i+1,len(top10_list)))
            url_table = item[1]
            try:
                num_all = int(item[2])
            except:
                num_all = 10

            # 计算需要抓取的页数
            num_pages = (num_all + 39) // 40  # 向上取整
            print('共要获取页数',num_pages)

            #进度条计数
            jdt_jishu = 0

            # 调用获取数据的函数
            for page in range(1, num_pages + 1):
                if page >1:
                    num = num_all - (40 * (page - 1))  # 计算剩余行数
                else:
                    if num_all > 40:
                        num = 40
                    else:
                        num = num_all
                print(url_table)
                url = "{}{}".format(url_table,page)
                htmlcode = self.get_kakaku_data(url)
                print('现在开始获取第{}页,URL={}'.format(page,url))
                if 'smartphone' in url:
                    print('获取手机开始')
                    # 匹配标题和网址
                    pattern = r'(?<=<a href=")/keitai/smartphone/model/M\d+'
                    titles_list = re.findall(pattern, htmlcode)
                    #遍历手机排位
                    for J, item in enumerate(titles_list[:num]):
                        jdt_jishu +=1
                        try:
                            jindutiao = int(jdt_jishu/num_all*100)
                        except:
                            jindutiao = 1
                        # print(J,item)
                        self.jindutiao_update.emit(jindutiao)
                        url_googs = "https://kakaku.com" + item
                        googs_code = self.get_kakaku_data(url_googs)
                        url_pattern = r'(?<=<a href=")/item/J\d+'
                        phone_list = re.findall(url_pattern, googs_code)
                        #遍历手机分类，内存大小区分等
                        for Z ,phone in enumerate(phone_list):
                            # print(phone)
                            item_phone_url = "https://kakaku.com" + phone
                            phone_googs_code = self.get_kakaku_data(item_phone_url)
                            #获取手机颜色分类,标题
                            pattern = r'<col class="photo">[\s\S]+?</table>'
                            phone_googs_code = re.findall(pattern, phone_googs_code)[0]
                            # print(phone_googs_code)
                            pattern = r'(?<=<span>)[\s\S]+?(?=</span>)'
                            phone_titles_list = re.findall(pattern, phone_googs_code)
                            # print(phone_titles_list)
                            #遍历颜色
                            for phone_title in phone_titles_list:
                                print(phone_title)
                                phone_title = self.title_del_str(phone_title)
                                self.progress_update.emit(phone_title, J + 1)

                else:
                    print('获取非手机信息')
                    # 匹配标题和网址
                    pattern = r'<td class="ckitemLink">[\s\S]*?<td><span'
                    titles_list = re.findall(pattern, htmlcode)
                    # print(titles_list)

                    # 遍历标题处理数据
                    for J, item in enumerate(titles_list[:num]):
                        jdt_jishu += 1
                        try:
                            jindutiao = int(jdt_jishu / num_all * 100)
                        except:
                            jindutiao = 1

                        self.jindutiao_update.emit(jindutiao)
                        url_pattern = r'(?<=a href=")[\s\S]+?(?=\")'
                        url_googs = re.findall(url_pattern, item)[0]
                        # print(J, jindutiao,len(titles_list[:num]),url)
                        tltle_pattern = r''
                        if 'item/J' in url_googs:
                            googs_code = self.get_kakaku_data(url_googs)
                            tabel_pattern = r'<table>[\s\S]+?</table>'
                            title_pattern = r'<a href="([^"]+)">(.*?)</a>'
                            tabel = re.findall(tabel_pattern, googs_code)[0]
                            # print('table',tabel)
                            titles = re.findall(title_pattern, tabel)
                            for title in titles:
                                title = title[1]
                                title = self.title_del_str(title)
                                # 提取排位
                                try:
                                    rank_pattern = r'<td class="swrank2"><span class="withRankIcn fontBold">(\d+)位</span>'
                                    rank_matches = re.findall(rank_pattern, item)[0]
                                    # print(rank_matches)

                                except:
                                    rank_matches = ""
                                self.progress_update.emit(title, int(rank_matches))
                        else:
                            title_pattern = r'(?<=</span>)[\s\S]+?(?=</a>)'
                            title = re.findall(title_pattern, item)[0]
                            title = self.title_del_str(title)
                            # 提取排位
                            try:
                                rank_pattern = r'<td class="swrank2"><span class="withRankIcn fontBold">(\d+)位</span>'
                                rank_matches = re.findall(rank_pattern, item)[0]
                                print(rank_matches)

                            except:
                                rank_matches = ""
                            self.progress_update.emit(title, int(rank_matches))
                            # self.sheet_uprow(title, i + 1)
                        time.sleep(0.6)
        self.update_ok.emit('ok')


    def get_kakaku_data(self,url=None):
        # print('获取网页开始',url)
        hd = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.51 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "Accept-Language": "ja,zh-CN;q=0.9,zh;q=0.8",
        }
        # import requests
        # url = 'https://kakaku.com/camera/digital-slr-camera/itemlist.aspx?pdf_pg=1'
        htmlcode = requests.get(url, headers=hd, timeout=10)
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
        with open(tmp_html, 'w+', encoding='utf-8') as f:
            f.write(htmlcode)
            f.seek(0)
            newhtmlcode = f.read()

        # print(newhtmlcode)
        return newhtmlcode

class xinghao_pyqtsignal(QtCore.QObject):
    jiage = QtCore.pyqtSignal(int, int, int, str)
    stop_pyqt = QtCore.pyqtSignal()

#分类选择窗体
class CategorySelectionDialog(QDialog):
    lable_text = QtCore.pyqtSignal(str)
    def __init__(self, parent=None):
        super(CategorySelectionDialog, self).__init__(parent)
        self.setWindowTitle('分类选择')
        self.resize(600, 400)

        self.left_table = QTableWidget(self)
        self.left_table.setColumnCount(3)
        self.left_table.setHorizontalHeaderLabels(['分类', 'URL', '取值'])
        self.right_table = QTableWidget(self)
        self.right_table.setColumnCount(3)
        self.right_table.setHorizontalHeaderLabels(['分类', 'URL', '取值'])

        self.left_data = self.read_data_from_file('Z:\\bazhuayu\\Top10\\Top10大分類.csv')
        self.populate_left_table()

        self.right_arrow_label = QLabel('→', self)
        self.right_arrow_label.setStyleSheet("font-size: 24px;")  # 设置字体大小为24像素
        self.left_arrow_label = QLabel('←', self)
        self.left_arrow_label.setStyleSheet("font-size: 24px;")  # 设置字体大小为24像素

        self.ok_button = QPushButton('确定', self)
        self.cancel_button = QPushButton('取消', self)

        self.ok_button.clicked.connect(self.on_ok_clicked)
        self.cancel_button.clicked.connect(self.on_cancel_clicked)
        self.left_arrow_label.mousePressEvent = self.on_left_arrow_clicked
        self.right_arrow_label.mousePressEvent = self.on_right_arrow_clicked

        self.operation_label = QLabel('', self)

        main_layout = QVBoxLayout()
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.operation_label)  # Add operation_label before the buttons
        button_layout.addStretch(1)
        button_layout.addWidget(self.ok_button)
        button_layout.addWidget(self.cancel_button)

        arrow_layout = QVBoxLayout()
        arrow_layout.addWidget(self.right_arrow_label)
        arrow_layout.addWidget(self.left_arrow_label)
        arrow_layout.addStretch(1)

        tables_layout = QHBoxLayout()
        tables_layout.addWidget(self.left_table)
        tables_layout.addLayout(arrow_layout)
        tables_layout.addWidget(self.right_table)

        main_layout.addLayout(tables_layout)
        main_layout.addLayout(button_layout)
        self.setLayout(main_layout)

    def populate_left_table(self):
        self.left_table.setRowCount(len(self.left_data))
        for i, row_data in enumerate(self.left_data):
            for j, item in enumerate(row_data):
                self.left_table.setItem(i, j, QTableWidgetItem(item))

    def check_and_update_left_table_colors(self):
        for row in range(self.left_table.rowCount()):
            left_items = [self.left_table.item(row, col).text() for col in range(self.left_table.columnCount())]
            right_items = []
            for r in range(self.right_table.rowCount()):
                right_items.append(
                    [self.right_table.item(r, col).text() for col in range(self.right_table.columnCount())])
            if left_items in right_items:
                for col in range(self.left_table.columnCount()):
                    item = self.left_table.item(row, col)
                    item.setBackground(QColor(0, 176, 80))
                    item.setForeground(Qt.white)
            else:
                for col in range(self.left_table.columnCount()):
                    item = self.left_table.item(row, col)
                    item.setBackground(Qt.white)
                    item.setForeground(Qt.black)

    def on_right_arrow_clicked(self, event):
        print('添加到右侧表')
        left_rows = set()
        selected_items = self.left_table.selectedItems()

        # 获取所有选中行的行号
        for item in selected_items:
            left_rows.add(item.row())

        # 遍历左侧表的选中行
        for row in left_rows:
            left_row_data = [self.left_table.item(row, col).text() for col in range(self.left_table.columnCount())]

            # 检查是否存在相同数据的行，如果不存在，则添加到右侧表
            if not self.is_data_exist_in_right_table(left_row_data):
                self.insert_row_to_right_table(left_row_data)
                self.operation_label.setText('数据已成功添加到右侧表格')
            else:
                self.operation_label.setText('数据已存在于右侧表格，未重复添加')

    def is_data_exist_in_right_table(self, data):
        # 遍历右侧表的每一行，与要检查的数据进行比较
        for row in range(self.right_table.rowCount()):
            right_row_data = [self.right_table.item(row, col).text() for col in range(self.right_table.columnCount())]

            # 如果找到了相同的数据行，返回True
            if right_row_data == data:
                return True
        return False

    def insert_row_to_right_table(self, row_data):
        # 将一行数据添加到右侧表
        self.right_table.insertRow(self.right_table.rowCount())
        for col, data in enumerate(row_data):
            self.right_table.setItem(self.right_table.rowCount() - 1, col, QTableWidgetItem(data))
        self.check_and_update_left_table_colors()
    def on_left_arrow_clicked(self, event):
        print('从右侧表删除')
        right_items = self.right_table.selectedItems()
        if right_items:
            selected_row = right_items[0].row()
            self.right_table.removeRow(selected_row)
            self.check_and_update_left_table_colors()
            self.operation_label.setText('数据以从左侧表格删除')

    def on_ok_clicked(self):
        self.top10_list = []
        for row in range(self.right_table.rowCount()):
            row_data = [self.right_table.item(row, col).text() for col in range(3)]
            self.top10_list.append(row_data)
        print("Top10 List:", self.top10_list)
        if self.top10_list:
            self.lable_text.emit('导入开始，等待载入文件…………')
        else:
            self.lable_text.emit('没有选择导入文件')
        self.accept()

    def on_cancel_clicked(self):
        self.lable_text.emit('取消文件导入')
        self.reject()

    def read_data_from_file(self, file_path):
        data = []
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                for line in file:
                    row_data = line.strip().split(',')
                    if len(row_data) == 3:
                        data.append(row_data)
        except FileNotFoundError:
            print(f"File not found: {file_path}")
        return data

class Kakaku_work(QtCore.QRunnable):

    def __init__(self, url, index, jiajia, shoushuliao,dayuzhi,zenfu,filenumber='1'):
        super(Kakaku_work, self).__init__()
        self.url = url
        self.filenumber = filenumber
        self.index = index
        self.jiajia = jiajia
        self.shoushuliao = float(shoushuliao)
        self.xinghao_signal = xinghao_pyqtsignal()
        self.dayuzhi = dayuzhi
        self.zengfu = zenfu

    def run(self) -> None:
        print('getkakaku,self.filenumber',self.filenumber)

        global stop


        hd = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.51 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "Accept-Language": "ja,zh-CN;q=0.9,zh;q=0.8",

        }
        htmlcode = requests.get(self.url, headers=hd)
        global status_code
        if htmlcode.status_code != 200:
            status_code += 1
        code = htmlcode.apparent_encoding
        # print('code=', code)
        htmlcode.encoding = code
        htmlcode = htmlcode.text
        htmlcode = htmlcode.replace("㈱", "(株)")
        htmlcode = htmlcode.replace("デンキヤ.com	", "aabbcc")
        # writetxt(htmlcode, code)
        # ss = etree.HTML(htmlcode.encode(code))
        # ta = ss.xpath("//tr")
        ## 网页源码写入文件
        # with open(os.getcwd() + "\\htmlcode.txt", 'w', encoding='utf-8-sig') as f:
        #     f.write(htmlcode)

        # htmlcode = readtxt(path,code)
        data = []

        for i in range(0, 3):
            # print('运行次数-%i' % i)
            if stop == 0:
                self.xinghao_signal.stop_pyqt.emit()
                return
            if self.filenumber == '6':
                # print('==6')
                data, quanlist = self.getxpathphone(htmlcode, code)
            else:
                data, quanlist = self.getxpath(htmlcode, code)
            if data != '':
                break
            time.sleep(2)
        # print(quanlist)
        tishi = ''
        kakaku_jiaga = 0
        if len(quanlist) > 0:
            try:
                kakaku_jiaga = int(''.join(list(filter(str.isdigit, quanlist[2][1]))))
            except:
                kakaku_jiaga = int(''.join(list(filter(str.isdigit, quanlist[-1][1]))))
            if kakaku_jiaga > self.dayuzhi:
                jiage = (kakaku_jiaga + self.jiajia)/self.zengfu/ self.shoushuliao
            else:
                jiage = (kakaku_jiaga + self.jiajia) / self.shoushuliao
            tishi = len(quanlist)
        else:
            jiage = 0
            tishi = 0
        print('触发价格回写')
        #计算 取位价格+加价 在数组中的位置
        position = self.Paixu_jisuan(quanlist,kakaku_jiaga , self.jiajia)
        self.xinghao_signal.jiage.emit(self.index, kakaku_jiaga, int(jiage), '{}({})'.format(tishi,position))
        print('触发价格回写完成',self.index, kakaku_jiaga, int(jiage), tishi,position)
        return
    #计算 取位价格+加价 数组中第二元素也就是价格中可以排第几位
    def Paixu_jisuan(self,quanlist,jiage,jiajia):
        target_value = jiage + jiajia
        position = 0
        second_elements = [int(item[1][1:].replace(',', '')) for item in quanlist]
        for i,item in enumerate(second_elements,1):

            if item > target_value:
                break
            position = i
        return position

    def getxpath(self, html, code):
        print('getxpath')
        global stop
        if stop == 0:
            stop = 1
            return
        tablecode = "//tr"
        mytree = etree.HTML(html)
        # 有时去掉编码可以正确识别网页
        # mytree = etree.HTML(html.encode(code))
        tr_list = mytree.xpath(tablecode)
        # print('lentr',len(tr_list))
        try:
            title = mytree.xpath('//div[@id=\'titleBox\']/div[@class=\'boxL\']/h2/text()')[0]
        except:
            return ''
        try:
            date = mytree.xpath('//div[@class=\'releaseDateWrap\']/span/text()')[0].strip()

        except:
            date = ""
        try:
            pm = mytree.xpath(
                '//div[@id=\'ovBtnBox\']//span[@class=\'num\']/text()|//ul[@class=\'clearfix\']/li[1]/span[@class=\'rankNum\']/text()')[
                0]
        except:
            pm = ""
        try:
            ds = mytree.xpath('//div[@class=\'subInfoObj4\']/span[1]/a/span/text()')[0]
        except:
            ds = 0
        if int(ds) > 50:
            ds = '50'
        # print(title,date,pm,ds)
        a = [[title, date, pm, ds], [title, date, pm, ds]]
        quan_list = []
        for td in tr_list:
            try:
                # xl为序列，jg为价格，zk为在库状态，sj为商品名
                xl = td.xpath('./td[1]/span[1]//text()')
                xl = ''.join(xl)
                # print(xl)
                jg = td.xpath('./td[2]/div[1]/p[1]//text()')
                jg = ''.join(jg)
                # print(jg)
                zk = td.xpath('./td[4]/p[1]//text()')
                zk = ''.join(zk)
                # if '〜' in zk:
                #     zk = zk + '営業日'
                # print(zk)

                sj = td.xpath('./td[5]/div[1]/div[1]/div[1]/p[1]/a[1]//text()')
                sjurl = td.xpath('./td[5]/div[1]/div[2]/a[1]/@href')
                sj = ''.join(sj)
                sjurl = ''.join(sjurl)
                # print(sj,sjurl)

                if xl:
                    a.append([title, date, pm, ds, xl, jg, zk, sj])
                if zk == '○':
                    quan_list.append([xl, jg, zk, sj])
            except:
                pass

        return a,quan_list

    def getxpathphone(self,html, code):
        print('采集手机')
        tablecode = "//tr"
        mytree = etree.HTML(html)
        # mytree = etree.HTML(html.encode(code))
        tr_list = mytree.xpath(tablecode)
        # print(tr_list)
        try:
            title = mytree.xpath('//div[@id=\'titleBox\']/div[@class=\'boxL\']/h2/text()')[0]
        except:
            return '重试'
        try:
            date = mytree.xpath('//div[@class=\'releaseDateWrap\']/span/text()')[0].strip()

        except:
            date = ""
        try:
            pm = mytree.xpath(
                '//div[@id=\'ovBtnBox\']//span[@class=\'num\']/text()|//ul[@class=\'clearfix\']/li[1]/span[@class=\'rankNum\']/text()')[
                0]
        except:
            pm = ""
        try:
            ds = mytree.xpath('//*[@id="SRanking"]/a/text()')[0]
            ds = re.findall('\d+', ds)[0]
        except:
            ds = 0
        shangjiashu = ds
        # print(title, date, pm, ds)
        quan_list = []
        a = [[title, date, pm, ds]]
        for i, td in enumerate(tr_list):
            # print('i=',i)
            try:
                # xl为序列，jg为价格，zk为在库状态，sj为商品名
                xl = td.xpath('./td[1]//text()')
                xl = ''.join(xl)
                # print('xl',xl)
                jg = td.xpath('./td[2]/p[1]/a[1]//text()')
                jg = ''.join(jg)
                # print('jg',jg)
                zk = td.xpath('./td[4]//text()')
                zk = ''.join(zk)
                # print('zk',zk)
                sj = td.xpath('./td[6]//a[1]//text()')
                sj = ''.join(sj)
                # print('sj',sj)
                if xl and '位' in xl:
                    a.append([title, date, pm, ds, xl, jg, '', zk, sj])
                if zk == '有':
                    quan_list.append([xl, jg, zk, sj])
            except:
                # print('序列出错')
                pass

        return a,quan_list

if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = mywindow()

    win.show()
    sys.exit(app.exec_())
