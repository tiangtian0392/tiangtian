# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'chupinwindow.ui'
#
# Created by: PyQt5 UI code generator 5.15.4
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(957, 890)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName("gridLayout")
        self.verticalLayout_4 = QtWidgets.QVBoxLayout()
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setObjectName("label")
        self.horizontalLayout.addWidget(self.label)
        self.lineEdit_url = QtWidgets.QLineEdit(self.centralwidget)
        self.lineEdit_url.setMinimumSize(QtCore.QSize(350, 0))
        self.lineEdit_url.setObjectName("lineEdit_url")
        self.horizontalLayout.addWidget(self.lineEdit_url)
        self.label_url_num = QtWidgets.QLabel(self.centralwidget)
        self.label_url_num.setMinimumSize(QtCore.QSize(90, 0))
        self.label_url_num.setObjectName("label_url_num")
        self.horizontalLayout.addWidget(self.label_url_num)
        self.checkBox_huoqu_zhuijia = QtWidgets.QCheckBox(self.centralwidget)
        self.checkBox_huoqu_zhuijia.setText("")
        self.checkBox_huoqu_zhuijia.setObjectName("checkBox_huoqu_zhuijia")
        self.horizontalLayout.addWidget(self.checkBox_huoqu_zhuijia)
        self.pushButton_huoqu = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_huoqu.setMaximumSize(QtCore.QSize(50, 16777215))
        self.pushButton_huoqu.setObjectName("pushButton_huoqu")
        self.horizontalLayout.addWidget(self.pushButton_huoqu)
        self.lineEdit_zhuandao = QtWidgets.QLineEdit(self.centralwidget)
        self.lineEdit_zhuandao.setObjectName("lineEdit_zhuandao")
        self.horizontalLayout.addWidget(self.lineEdit_zhuandao)
        self.pushButton_zhuangdao = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_zhuangdao.setMaximumSize(QtCore.QSize(50, 16777215))
        self.pushButton_zhuangdao.setObjectName("pushButton_zhuangdao")
        self.horizontalLayout.addWidget(self.pushButton_zhuangdao)
        self.pushButton_shangye = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_shangye.setMaximumSize(QtCore.QSize(50, 16777215))
        self.pushButton_shangye.setObjectName("pushButton_shangye")
        self.horizontalLayout.addWidget(self.pushButton_shangye)
        self.pushButton_xiaye = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_xiaye.setMaximumSize(QtCore.QSize(50, 16777215))
        self.pushButton_xiaye.setObjectName("pushButton_xiaye")
        self.horizontalLayout.addWidget(self.pushButton_xiaye)
        self.label_2 = QtWidgets.QLabel(self.centralwidget)
        self.label_2.setObjectName("label_2")
        self.horizontalLayout.addWidget(self.label_2)
        self.spinBox_kaishi = QtWidgets.QSpinBox(self.centralwidget)
        self.spinBox_kaishi.setProperty("value", 1)
        self.spinBox_kaishi.setObjectName("spinBox_kaishi")
        self.horizontalLayout.addWidget(self.spinBox_kaishi)
        self.label_3 = QtWidgets.QLabel(self.centralwidget)
        self.label_3.setObjectName("label_3")
        self.horizontalLayout.addWidget(self.label_3)
        self.spinBox_jiesu = QtWidgets.QSpinBox(self.centralwidget)
        self.spinBox_jiesu.setProperty("value", 1)
        self.spinBox_jiesu.setObjectName("spinBox_jiesu")
        self.horizontalLayout.addWidget(self.spinBox_jiesu)
        self.verticalLayout_4.addLayout(self.horizontalLayout)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.label_4 = QtWidgets.QLabel(self.centralwidget)
        self.label_4.setObjectName("label_4")
        self.horizontalLayout_2.addWidget(self.label_4)
        self.lineEdit_jan = QtWidgets.QLineEdit(self.centralwidget)
        self.lineEdit_jan.setMinimumSize(QtCore.QSize(113, 0))
        self.lineEdit_jan.setObjectName("lineEdit_jan")
        self.horizontalLayout_2.addWidget(self.lineEdit_jan)
        self.label_5 = QtWidgets.QLabel(self.centralwidget)
        self.label_5.setObjectName("label_5")
        self.horizontalLayout_2.addWidget(self.label_5)
        self.lineEdit_xingban = QtWidgets.QLineEdit(self.centralwidget)
        self.lineEdit_xingban.setMinimumSize(QtCore.QSize(161, 0))
        self.lineEdit_xingban.setObjectName("lineEdit_xingban")
        self.horizontalLayout_2.addWidget(self.lineEdit_xingban)
        self.label_zishu_2 = QtWidgets.QLabel(self.centralwidget)
        self.label_zishu_2.setMinimumSize(QtCore.QSize(50, 0))
        self.label_zishu_2.setObjectName("label_zishu_2")
        self.horizontalLayout_2.addWidget(self.label_zishu_2)
        self.label_paiming_riqi = QtWidgets.QLabel(self.centralwidget)
        self.label_paiming_riqi.setMinimumSize(QtCore.QSize(140, 0))
        self.label_paiming_riqi.setObjectName("label_paiming_riqi")
        self.horizontalLayout_2.addWidget(self.label_paiming_riqi)
        self.label_6 = QtWidgets.QLabel(self.centralwidget)
        self.label_6.setObjectName("label_6")
        self.horizontalLayout_2.addWidget(self.label_6)
        self.lineEdit_jiage = QtWidgets.QLineEdit(self.centralwidget)
        self.lineEdit_jiage.setMinimumSize(QtCore.QSize(80, 0))
        self.lineEdit_jiage.setMaximumSize(QtCore.QSize(80, 16777215))
        self.lineEdit_jiage.setObjectName("lineEdit_jiage")
        self.horizontalLayout_2.addWidget(self.lineEdit_jiage)
        self.label_18 = QtWidgets.QLabel(self.centralwidget)
        self.label_18.setObjectName("label_18")
        self.horizontalLayout_2.addWidget(self.label_18)
        self.spinBox_jiagequwei = QtWidgets.QSpinBox(self.centralwidget)
        self.spinBox_jiagequwei.setProperty("value", 5)
        self.spinBox_jiagequwei.setObjectName("spinBox_jiagequwei")
        self.horizontalLayout_2.addWidget(self.spinBox_jiagequwei)
        self.label_19_gong_quan = QtWidgets.QLabel(self.centralwidget)
        self.label_19_gong_quan.setMinimumSize(QtCore.QSize(54, 0))
        self.label_19_gong_quan.setObjectName("label_19_gong_quan")
        self.horizontalLayout_2.addWidget(self.label_19_gong_quan)
        self.label_15 = QtWidgets.QLabel(self.centralwidget)
        self.label_15.setObjectName("label_15")
        self.horizontalLayout_2.addWidget(self.label_15)
        self.lineEdit_jiajia = QtWidgets.QLineEdit(self.centralwidget)
        self.lineEdit_jiajia.setMaximumSize(QtCore.QSize(50, 16777215))
        self.lineEdit_jiajia.setObjectName("lineEdit_jiajia")
        self.horizontalLayout_2.addWidget(self.lineEdit_jiajia)
        self.verticalLayout_4.addLayout(self.horizontalLayout_2)
        self.horizontalLayout_9 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_9.setObjectName("horizontalLayout_9")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.label_7 = QtWidgets.QLabel(self.centralwidget)
        self.label_7.setMaximumSize(QtCore.QSize(25, 16777215))
        self.label_7.setObjectName("label_7")
        self.horizontalLayout_3.addWidget(self.label_7)
        self.lineEdit_shuliang = QtWidgets.QLineEdit(self.centralwidget)
        self.lineEdit_shuliang.setMaximumSize(QtCore.QSize(20, 16777215))
        self.lineEdit_shuliang.setObjectName("lineEdit_shuliang")
        self.horizontalLayout_3.addWidget(self.lineEdit_shuliang)
        self.label_8 = QtWidgets.QLabel(self.centralwidget)
        self.label_8.setMaximumSize(QtCore.QSize(35, 16777215))
        self.label_8.setObjectName("label_8")
        self.horizontalLayout_3.addWidget(self.label_8)
        self.lineEdit_tupianshu = QtWidgets.QLineEdit(self.centralwidget)
        self.lineEdit_tupianshu.setMaximumSize(QtCore.QSize(20, 16777215))
        self.lineEdit_tupianshu.setObjectName("lineEdit_tupianshu")
        self.horizontalLayout_3.addWidget(self.lineEdit_tupianshu)
        self.label_9 = QtWidgets.QLabel(self.centralwidget)
        self.label_9.setMaximumSize(QtCore.QSize(35, 16777215))
        self.label_9.setObjectName("label_9")
        self.horizontalLayout_3.addWidget(self.label_9)
        self.lineEdit_fasongri = QtWidgets.QLineEdit(self.centralwidget)
        self.lineEdit_fasongri.setMaximumSize(QtCore.QSize(20, 16777215))
        self.lineEdit_fasongri.setObjectName("lineEdit_fasongri")
        self.horizontalLayout_3.addWidget(self.lineEdit_fasongri)
        self.label_10 = QtWidgets.QLabel(self.centralwidget)
        self.label_10.setMaximumSize(QtCore.QSize(25, 16777215))
        self.label_10.setObjectName("label_10")
        self.horizontalLayout_3.addWidget(self.label_10)
        self.comboBox = QtWidgets.QComboBox(self.centralwidget)
        self.comboBox.setMaximumSize(QtCore.QSize(69, 16777215))
        self.comboBox.setEditable(True)
        self.comboBox.setObjectName("comboBox")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.horizontalLayout_3.addWidget(self.comboBox)
        self.label_17 = QtWidgets.QLabel(self.centralwidget)
        self.label_17.setMaximumSize(QtCore.QSize(25, 16777215))
        self.label_17.setObjectName("label_17")
        self.horizontalLayout_3.addWidget(self.label_17)
        self.lineEdit_changjia = QtWidgets.QLineEdit(self.centralwidget)
        self.lineEdit_changjia.setMaximumSize(QtCore.QSize(101, 16777215))
        self.lineEdit_changjia.setText("")
        self.lineEdit_changjia.setObjectName("lineEdit_changjia")
        self.horizontalLayout_3.addWidget(self.lineEdit_changjia)
        self.label_14 = QtWidgets.QLabel(self.centralwidget)
        self.label_14.setMaximumSize(QtCore.QSize(50, 16777215))
        self.label_14.setObjectName("label_14")
        self.horizontalLayout_3.addWidget(self.label_14)
        self.comboBox_fenlei = QtWidgets.QComboBox(self.centralwidget)
        self.comboBox_fenlei.setMinimumSize(QtCore.QSize(205, 0))
        self.comboBox_fenlei.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.comboBox_fenlei.setEditable(True)
        self.comboBox_fenlei.setObjectName("comboBox_fenlei")
        self.horizontalLayout_3.addWidget(self.comboBox_fenlei)
        self.verticalLayout.addLayout(self.horizontalLayout_3)
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.label_13 = QtWidgets.QLabel(self.centralwidget)
        self.label_13.setObjectName("label_13")
        self.horizontalLayout_4.addWidget(self.label_13)
        self.lineEdit_jiagewangURL = QtWidgets.QLineEdit(self.centralwidget)
        self.lineEdit_jiagewangURL.setText("")
        self.lineEdit_jiagewangURL.setPlaceholderText("")
        self.lineEdit_jiagewangURL.setObjectName("lineEdit_jiagewangURL")
        self.horizontalLayout_4.addWidget(self.lineEdit_jiagewangURL)
        self.comboBox_zichengxu = QtWidgets.QComboBox(self.centralwidget)
        self.comboBox_zichengxu.setMinimumSize(QtCore.QSize(181, 0))
        self.comboBox_zichengxu.setObjectName("comboBox_zichengxu")
        self.horizontalLayout_4.addWidget(self.comboBox_zichengxu)
        self.pushButton_yunxingzichongxu = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_yunxingzichongxu.setObjectName("pushButton_yunxingzichongxu")
        self.horizontalLayout_4.addWidget(self.pushButton_yunxingzichongxu)
        self.verticalLayout.addLayout(self.horizontalLayout_4)
        self.horizontalLayout_5 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.label_12 = QtWidgets.QLabel(self.centralwidget)
        self.label_12.setObjectName("label_12")
        self.horizontalLayout_5.addWidget(self.label_12)
        self.lineEdit_jiagewangbiaoti = QtWidgets.QLineEdit(self.centralwidget)
        self.lineEdit_jiagewangbiaoti.setText("")
        self.lineEdit_jiagewangbiaoti.setObjectName("lineEdit_jiagewangbiaoti")
        self.horizontalLayout_5.addWidget(self.lineEdit_jiagewangbiaoti)
        self.comboBox_shouji_zhengchang = QtWidgets.QComboBox(self.centralwidget)
        self.comboBox_shouji_zhengchang.setObjectName("comboBox_shouji_zhengchang")
        self.comboBox_shouji_zhengchang.addItem("")
        self.comboBox_shouji_zhengchang.addItem("")
        self.horizontalLayout_5.addWidget(self.comboBox_shouji_zhengchang)
        self.lineEdit_jiage_jiagewangfenlei = QtWidgets.QLineEdit(self.centralwidget)
        self.lineEdit_jiage_jiagewangfenlei.setMinimumSize(QtCore.QSize(50, 0))
        self.lineEdit_jiage_jiagewangfenlei.setMaximumSize(QtCore.QSize(120, 16777215))
        self.lineEdit_jiage_jiagewangfenlei.setObjectName("lineEdit_jiage_jiagewangfenlei")
        self.horizontalLayout_5.addWidget(self.lineEdit_jiage_jiagewangfenlei)
        self.pushButton_huoqufenlei = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_huoqufenlei.setObjectName("pushButton_huoqufenlei")
        self.horizontalLayout_5.addWidget(self.pushButton_huoqufenlei)
        self.verticalLayout.addLayout(self.horizontalLayout_5)
        self.horizontalLayout_6 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_6.setObjectName("horizontalLayout_6")
        self.label_11 = QtWidgets.QLabel(self.centralwidget)
        self.label_11.setObjectName("label_11")
        self.horizontalLayout_6.addWidget(self.label_11)
        self.lineEdit_Qoo10biaoti = QtWidgets.QLineEdit(self.centralwidget)
        self.lineEdit_Qoo10biaoti.setObjectName("lineEdit_Qoo10biaoti")
        self.horizontalLayout_6.addWidget(self.lineEdit_Qoo10biaoti)
        self.label_zishu = QtWidgets.QLabel(self.centralwidget)
        self.label_zishu.setMinimumSize(QtCore.QSize(61, 0))
        self.label_zishu.setObjectName("label_zishu")
        self.horizontalLayout_6.addWidget(self.label_zishu)
        self.verticalLayout.addLayout(self.horizontalLayout_6)
        self.horizontalLayout_7 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_7.setObjectName("horizontalLayout_7")
        self.label_16 = QtWidgets.QLabel(self.centralwidget)
        self.label_16.setObjectName("label_16")
        self.horizontalLayout_7.addWidget(self.label_16)
        self.lineEdit_gebuchuchu = QtWidgets.QLineEdit(self.centralwidget)
        self.lineEdit_gebuchuchu.setObjectName("lineEdit_gebuchuchu")
        self.horizontalLayout_7.addWidget(self.lineEdit_gebuchuchu)
        self.lineEdit = QtWidgets.QLineEdit(self.centralwidget)
        self.lineEdit.setObjectName("lineEdit")
        self.horizontalLayout_7.addWidget(self.lineEdit)
        self.checkBox_biaotiguanjianzi = QtWidgets.QCheckBox(self.centralwidget)
        self.checkBox_biaotiguanjianzi.setText("")
        self.checkBox_biaotiguanjianzi.setObjectName("checkBox_biaotiguanjianzi")
        self.horizontalLayout_7.addWidget(self.checkBox_biaotiguanjianzi)
        self.pushButton_xingbanchuli = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_xingbanchuli.setObjectName("pushButton_xingbanchuli")
        self.horizontalLayout_7.addWidget(self.pushButton_xingbanchuli)
        self.pushButton_kaishi = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_kaishi.setObjectName("pushButton_kaishi")
        self.horizontalLayout_7.addWidget(self.pushButton_kaishi)
        self.verticalLayout.addLayout(self.horizontalLayout_7)
        self.horizontalLayout_9.addLayout(self.verticalLayout)
        self.label_IMG = QtWidgets.QLabel(self.centralwidget)
        self.label_IMG.setMinimumSize(QtCore.QSize(130, 130))
        self.label_IMG.setMaximumSize(QtCore.QSize(130, 130))
        self.label_IMG.setStyleSheet("background-color: white")
        self.label_IMG.setText("")
        self.label_IMG.setScaledContents(False)
        self.label_IMG.setAlignment(QtCore.Qt.AlignCenter)
        self.label_IMG.setObjectName("label_IMG")
        self.horizontalLayout_9.addWidget(self.label_IMG)
        self.verticalLayout_4.addLayout(self.horizontalLayout_9)
        self.horizontalLayout_8 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_8.setObjectName("horizontalLayout_8")
        self.pushButton_qingchurn = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_qingchurn.setObjectName("pushButton_qingchurn")
        self.horizontalLayout_8.addWidget(self.pushButton_qingchurn)
        self.pushButton_charuhuanhang = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_charuhuanhang.setObjectName("pushButton_charuhuanhang")
        self.horizontalLayout_8.addWidget(self.pushButton_charuhuanhang)
        self.pushButton_charutupian = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_charutupian.setObjectName("pushButton_charutupian")
        self.horizontalLayout_8.addWidget(self.pushButton_charutupian)
        self.pushButton_geshihuahtml = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_geshihuahtml.setObjectName("pushButton_geshihuahtml")
        self.horizontalLayout_8.addWidget(self.pushButton_geshihuahtml)
        self.pushButton_qingkongdaima = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_qingkongdaima.setObjectName("pushButton_qingkongdaima")
        self.horizontalLayout_8.addWidget(self.pushButton_qingkongdaima)
        self.spinBox_zitidaxiao = QtWidgets.QSpinBox(self.centralwidget)
        self.spinBox_zitidaxiao.setProperty("value", 13)
        self.spinBox_zitidaxiao.setObjectName("spinBox_zitidaxiao")
        self.horizontalLayout_8.addWidget(self.spinBox_zitidaxiao)
        self.pushButton_yulang = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_yulang.setObjectName("pushButton_yulang")
        self.horizontalLayout_8.addWidget(self.pushButton_yulang)
        self.pushButton_gaolianxianshi = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_gaolianxianshi.setObjectName("pushButton_gaolianxianshi")
        self.horizontalLayout_8.addWidget(self.pushButton_gaolianxianshi)
        self.pushButton_chongzhi = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_chongzhi.setObjectName("pushButton_chongzhi")
        self.horizontalLayout_8.addWidget(self.pushButton_chongzhi)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_8.addItem(spacerItem)
        self.pushButton_shengcheng = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_shengcheng.setObjectName("pushButton_shengcheng")
        self.horizontalLayout_8.addWidget(self.pushButton_shengcheng)
        self.pushButton_zhuijia = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_zhuijia.setObjectName("pushButton_zhuijia")
        self.horizontalLayout_8.addWidget(self.pushButton_zhuijia)
        self.verticalLayout_4.addLayout(self.horizontalLayout_8)
        self.horizontalLayout_11 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_11.setObjectName("horizontalLayout_11")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout()
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.plainTextEdit = QtWidgets.QPlainTextEdit(self.centralwidget)
        self.plainTextEdit.setObjectName("plainTextEdit")
        self.verticalLayout_2.addWidget(self.plainTextEdit)
        self.textEdit = QtWidgets.QTextEdit(self.centralwidget)
        self.textEdit.setEnabled(True)
        self.textEdit.setObjectName("textEdit")
        self.verticalLayout_2.addWidget(self.textEdit)
        self.horizontalLayout_11.addLayout(self.verticalLayout_2)
        self.verticalLayout_3 = QtWidgets.QVBoxLayout()
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.tableWidget_chuping = QtWidgets.QTableWidget(self.centralwidget)
        self.tableWidget_chuping.setObjectName("tableWidget_chuping")
        self.tableWidget_chuping.setColumnCount(22)
        self.tableWidget_chuping.setRowCount(0)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget_chuping.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget_chuping.setHorizontalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget_chuping.setHorizontalHeaderItem(2, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget_chuping.setHorizontalHeaderItem(3, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget_chuping.setHorizontalHeaderItem(4, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget_chuping.setHorizontalHeaderItem(5, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget_chuping.setHorizontalHeaderItem(6, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget_chuping.setHorizontalHeaderItem(7, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget_chuping.setHorizontalHeaderItem(8, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget_chuping.setHorizontalHeaderItem(9, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget_chuping.setHorizontalHeaderItem(10, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget_chuping.setHorizontalHeaderItem(11, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget_chuping.setHorizontalHeaderItem(12, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget_chuping.setHorizontalHeaderItem(13, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget_chuping.setHorizontalHeaderItem(14, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget_chuping.setHorizontalHeaderItem(15, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget_chuping.setHorizontalHeaderItem(16, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget_chuping.setHorizontalHeaderItem(17, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget_chuping.setHorizontalHeaderItem(18, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget_chuping.setHorizontalHeaderItem(19, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget_chuping.setHorizontalHeaderItem(20, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget_chuping.setHorizontalHeaderItem(21, item)
        self.verticalLayout_3.addWidget(self.tableWidget_chuping)
        self.horizontalLayout_10 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_10.setObjectName("horizontalLayout_10")
        self.pushButton_qingkong = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_qingkong.setObjectName("pushButton_qingkong")
        self.horizontalLayout_10.addWidget(self.pushButton_qingkong)
        self.pushButton_zairu = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_zairu.setObjectName("pushButton_zairu")
        self.horizontalLayout_10.addWidget(self.pushButton_zairu)
        self.pushButton_biaogexiuzheng = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_biaogexiuzheng.setObjectName("pushButton_biaogexiuzheng")
        self.horizontalLayout_10.addWidget(self.pushButton_biaogexiuzheng)
        self.pushButton_baocun = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_baocun.setObjectName("pushButton_baocun")
        self.horizontalLayout_10.addWidget(self.pushButton_baocun)
        self.pushButton_zidong = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_zidong.setObjectName("pushButton_zidong")
        self.horizontalLayout_10.addWidget(self.pushButton_zidong)
        self.pushButton_chongxinhuoqu = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_chongxinhuoqu.setObjectName("pushButton_chongxinhuoqu")
        self.horizontalLayout_10.addWidget(self.pushButton_chongxinhuoqu)
        self.verticalLayout_3.addLayout(self.horizontalLayout_10)
        self.horizontalLayout_11.addLayout(self.verticalLayout_3)
        self.verticalLayout_4.addLayout(self.horizontalLayout_11)
        self.gridLayout.addLayout(self.verticalLayout_4, 0, 0, 1, 1)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 957, 21))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.label.setText(_translate("MainWindow", "URL"))
        self.lineEdit_url.setPlaceholderText(_translate("MainWindow", "url则获取，Qoo10data文件名则读入后修改"))
        self.label_url_num.setText(_translate("MainWindow", "共/现"))
        self.pushButton_huoqu.setText(_translate("MainWindow", "获取"))
        self.lineEdit_zhuandao.setText(_translate("MainWindow", "K000"))
        self.pushButton_zhuangdao.setText(_translate("MainWindow", "转到"))
        self.pushButton_shangye.setText(_translate("MainWindow", "↑上页"))
        self.pushButton_xiaye.setText(_translate("MainWindow", "↓下页"))
        self.label_2.setText(_translate("MainWindow", "页数"))
        self.label_3.setText(_translate("MainWindow", "--"))
        self.label_4.setText(_translate("MainWindow", "JAN"))
        self.label_5.setText(_translate("MainWindow", "型番"))
        self.label_zishu_2.setText(_translate("MainWindow", "字数：355"))
        self.label_paiming_riqi.setText(_translate("MainWindow", "排名：/日期："))
        self.label_6.setText(_translate("MainWindow", "价格"))
        self.label_18.setText(_translate("MainWindow", "价格取位"))
        self.label_19_gong_quan.setText(_translate("MainWindow", "共0/圈0"))
        self.label_15.setText(_translate("MainWindow", "加价"))
        self.lineEdit_jiajia.setText(_translate("MainWindow", "3500"))
        self.label_7.setText(_translate("MainWindow", "数量"))
        self.lineEdit_shuliang.setText(_translate("MainWindow", "1"))
        self.label_8.setText(_translate("MainWindow", "图片数"))
        self.label_9.setText(_translate("MainWindow", "发送日"))
        self.lineEdit_fasongri.setText(_translate("MainWindow", "3"))
        self.label_10.setText(_translate("MainWindow", "送料"))
        self.comboBox.setItemText(0, _translate("MainWindow", "119079"))
        self.comboBox.setItemText(1, _translate("MainWindow", "335370"))
        self.comboBox.setItemText(2, _translate("MainWindow", "646874"))
        self.label_17.setText(_translate("MainWindow", "厂家"))
        self.label_14.setText(_translate("MainWindow", "分类番号"))
        self.label_13.setText(_translate("MainWindow", "价格网URL"))
        self.pushButton_yunxingzichongxu.setText(_translate("MainWindow", "运行子程序"))
        self.label_12.setText(_translate("MainWindow", "价格网标题"))
        self.comboBox_shouji_zhengchang.setItemText(0, _translate("MainWindow", "普通"))
        self.comboBox_shouji_zhengchang.setItemText(1, _translate("MainWindow", "手机"))
        self.lineEdit_jiage_jiagewangfenlei.setPlaceholderText(_translate("MainWindow", "价格网分类"))
        self.pushButton_huoqufenlei.setText(_translate("MainWindow", "获取分类"))
        self.label_11.setText(_translate("MainWindow", "Qoo10标题"))
        self.label_zishu.setText(_translate("MainWindow", "字数："))
        self.label_16.setText(_translate("MainWindow", "各部出处"))
        self.lineEdit_gebuchuchu.setPlaceholderText(_translate("MainWindow", "JAN=出处，商品说明=出处"))
        self.lineEdit.setPlaceholderText(_translate("MainWindow", "后面勾选为自动，否则为标题关键字"))
        self.pushButton_xingbanchuli.setText(_translate("MainWindow", "型番处理"))
        self.pushButton_kaishi.setText(_translate("MainWindow", "开始"))
        self.pushButton_qingchurn.setText(_translate("MainWindow", "清除rn"))
        self.pushButton_charuhuanhang.setText(_translate("MainWindow", "插入换行"))
        self.pushButton_charutupian.setText(_translate("MainWindow", "插入图片"))
        self.pushButton_geshihuahtml.setText(_translate("MainWindow", "格式化HTML"))
        self.pushButton_qingkongdaima.setText(_translate("MainWindow", "清空代码"))
        self.pushButton_yulang.setText(_translate("MainWindow", "预览"))
        self.pushButton_gaolianxianshi.setText(_translate("MainWindow", "高亮代码"))
        self.pushButton_chongzhi.setText(_translate("MainWindow", "重置"))
        self.pushButton_shengcheng.setText(_translate("MainWindow", "生成文件"))
        self.pushButton_zhuijia.setText(_translate("MainWindow", "追加/修正"))
        item = self.tableWidget_chuping.horizontalHeaderItem(0)
        item.setText(_translate("MainWindow", "商品ID"))
        item = self.tableWidget_chuping.horizontalHeaderItem(1)
        item.setText(_translate("MainWindow", "商品名"))
        item = self.tableWidget_chuping.horizontalHeaderItem(2)
        item.setText(_translate("MainWindow", "商品説明"))
        item = self.tableWidget_chuping.horizontalHeaderItem(3)
        item.setText(_translate("MainWindow", "タイトル"))
        item = self.tableWidget_chuping.horizontalHeaderItem(4)
        item.setText(_translate("MainWindow", "予定価格"))
        item = self.tableWidget_chuping.horizontalHeaderItem(5)
        item.setText(_translate("MainWindow", "商品個数"))
        item = self.tableWidget_chuping.horizontalHeaderItem(6)
        item.setText(_translate("MainWindow", "IMAGE有無"))
        item = self.tableWidget_chuping.horizontalHeaderItem(7)
        item.setText(_translate("MainWindow", "発送日"))
        item = self.tableWidget_chuping.horizontalHeaderItem(8)
        item.setText(_translate("MainWindow", "送料"))
        item = self.tableWidget_chuping.horizontalHeaderItem(9)
        item.setText(_translate("MainWindow", "商品状態"))
        item = self.tableWidget_chuping.horizontalHeaderItem(10)
        item.setText(_translate("MainWindow", "補足"))
        item = self.tableWidget_chuping.horizontalHeaderItem(11)
        item.setText(_translate("MainWindow", "Qカテゴリ"))
        item = self.tableWidget_chuping.horizontalHeaderItem(12)
        item.setText(_translate("MainWindow", "kaakuカテゴリ"))
        item = self.tableWidget_chuping.horizontalHeaderItem(13)
        item.setText(_translate("MainWindow", "ショップ情報"))
        item = self.tableWidget_chuping.horizontalHeaderItem(14)
        item.setText(_translate("MainWindow", "単位"))
        item = self.tableWidget_chuping.horizontalHeaderItem(15)
        item.setText(_translate("MainWindow", "シリーズ"))
        item = self.tableWidget_chuping.horizontalHeaderItem(16)
        item.setText(_translate("MainWindow", "サイズ"))
        item = self.tableWidget_chuping.horizontalHeaderItem(17)
        item.setText(_translate("MainWindow", "手数料"))
        item = self.tableWidget_chuping.horizontalHeaderItem(18)
        item.setText(_translate("MainWindow", "jiajia"))
        item = self.tableWidget_chuping.horizontalHeaderItem(19)
        item.setText(_translate("MainWindow", "IMG"))
        item = self.tableWidget_chuping.horizontalHeaderItem(20)
        item.setText(_translate("MainWindow", "login_date"))
        item = self.tableWidget_chuping.horizontalHeaderItem(21)
        item.setText(_translate("MainWindow", "last scan date"))
        self.pushButton_qingkong.setText(_translate("MainWindow", "清空"))
        self.pushButton_zairu.setText(_translate("MainWindow", "载入"))
        self.pushButton_biaogexiuzheng.setText(_translate("MainWindow", "表格修正"))
        self.pushButton_baocun.setText(_translate("MainWindow", "保存"))
        self.pushButton_zidong.setText(_translate("MainWindow", "自动"))
        self.pushButton_chongxinhuoqu.setText(_translate("MainWindow", "重新获取"))
