import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QTextEdit, QPlainTextEdit

class HtmlPreviewApp(QWidget):
    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):
        # 设置窗口标题和大小
        self.setWindowTitle('HTML Previewer')
        self.setGeometry(100, 100, 600, 400)

        # 创建布局
        layout = QVBoxLayout()

        # 创建QPlainTextEdit
        self.plainTextEdit = QPlainTextEdit(self)
        layout.addWidget(self.plainTextEdit)

        # 创建QTextEdit
        self.htmlTextEdit = QTextEdit(self)
        self.htmlTextEdit.setReadOnly(True)
        layout.addWidget(self.htmlTextEdit)

        # 将QPlainTextEdit的内容变化信号连接到updateHtml槽函数
        self.plainTextEdit.textChanged.connect(self.updateHtml)

        # 设置布局
        self.setLayout(layout)

    def updateHtml(self):
        # 获取QPlainTextEdit的内容并将其设置为QTextEdit的HTML内容
        plainText = self.plainTextEdit.toPlainText()
        self.htmlTextEdit.setHtml(plainText)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = HtmlPreviewApp()
    ex.show()
    sys.exit(app.exec_())
