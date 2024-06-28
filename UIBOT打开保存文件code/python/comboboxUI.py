from PyQt5 import QtCore, QtGui, QtWidgets

class CheckableComboBox(QtWidgets.QComboBox):
    def __init__(self, parent=None):
        super(CheckableComboBox, self).__init__(parent)
        self.view().pressed.connect(self.handleItemPressed)
        self.setModel(QtGui.QStandardItemModel(self))

    def handleItemPressed(self, index):
        item = self.model().itemFromIndex(index)
        if item.checkState() == QtCore.Qt.Checked:
            item.setCheckState(QtCore.Qt.Unchecked)
        else:
            item.setCheckState(QtCore.Qt.Checked)

    def checkedItems(self):
        checkedItems = []
        for index in range(self.count()):
            item = self.model().item(index)
            if item.checkState() == QtCore.Qt.Checked:
                checkedItems.append(item.text())
        return checkedItems

    def allItemsWithState(self):
        itemsWithState = {}
        for index in range(self.count()):
            item = self.model().item(index)
            itemsWithState[item.text()] = item.checkState() == QtCore.Qt.Checked
        return itemsWithState


class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(520, 80)

        # Set frameless and transparent
        Form.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        # Form.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        Form.setWindowOpacity(0.80)  # Set window opacity

        # Create CheckableComboBox instead of QComboBox
        self.comboBox = CheckableComboBox(Form)
        self.comboBox.setGeometry(QtCore.QRect(10, 20, 100, 22))
        self.comboBox.setObjectName("comboBox")

        # Add QCheckBox items to comboBox
        self.addCheckBoxItems()

        self.pushButton_open = QtWidgets.QPushButton(Form)
        self.pushButton_open.setGeometry(QtCore.QRect(120, 20, 75, 23))
        self.pushButton_open.setObjectName("pushButton_open")
        self.pushButton_save = QtWidgets.QPushButton(Form)
        self.pushButton_save.setGeometry(QtCore.QRect(200, 20, 75, 23))
        self.pushButton_save.setObjectName("pushButton_save")
        self.pushButton_next = QtWidgets.QPushButton(Form)
        self.pushButton_next.setGeometry(QtCore.QRect(280, 20, 75, 23))
        self.pushButton_next.setObjectName("pushButton_next")
        self.pushButton_get_order = QtWidgets.QPushButton(Form)
        self.pushButton_get_order.setGeometry(QtCore.QRect(360, 20, 75, 23))
        self.pushButton_get_order.setObjectName("pushButton_get_order")
        self.pushButton_exit = QtWidgets.QPushButton(Form)
        self.pushButton_exit.setGeometry(QtCore.QRect(440, 20, 75, 23))
        self.pushButton_exit.setObjectName("pushButton_exit")

        # Add a QLabel for displaying work information
        self.label_info = QtWidgets.QLabel(Form)
        self.label_info.setGeometry(QtCore.QRect(10, 50, 500, 20))  # Adjust size and position as needed
        self.label_info.setObjectName("label_info")
        self.label_info.setStyleSheet("background-color: lightgray; border: 1px solid gray;")
        self.label_info.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)


        # Example text for flowing display
        # self.flow_text = "Example flowing text..."
        # self.flow_index = 0
        # self.flow_timer = QtCore.QTimer(Form)
        # self.flow_timer.timeout.connect(self.update_flow_text)
        # self.flow_timer.start(200)  # Adjust interval as needed

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def addCheckBoxItems(self):
        items = [
            ("对比在库", "checkBox_db_zaiku"),
            ("对比定单", "checkBox_db_dingdan"),
            ("对比排除", "checkBox_db_paichu"),
            ("打开宏", "checkBox_open_hong"),
            ("自动上传", "checkBox_auto_up"),
            ("自动next", "checkBox_auto_next"),
        ]

        for text, name in items:
            item = QtGui.QStandardItem(text)
            item.setFlags(QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsEnabled)
            item.setCheckState(QtCore.Qt.Checked)
            self.comboBox.model().appendRow(item)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "打开保存文件"))
        self.pushButton_open.setText(_translate("Form", "打开"))
        self.pushButton_save.setText(_translate("Form", "保存"))
        self.pushButton_next.setText(_translate("Form", "下一个()"))
        self.pushButton_get_order.setText(_translate("Form", "获取定单"))
        self.pushButton_exit.setText(_translate("Form", "退出"))




# if __name__ == "__main__":
#     import sys
#
#     app = QtWidgets.QApplication(sys.argv)
#     Form = QtWidgets.QWidget()
#     ui = Ui_Form()
#     ui.setupUi(Form)
#     Form.show()
#     sys.exit(app.exec_())
