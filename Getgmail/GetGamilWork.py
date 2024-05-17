import sys
import json
import csv
import os,shutil
from datetime import datetime, timedelta
from PyQt5 import QtCore, QtGui, QtWidgets
from GetGmailWindow import Ui_MainWindow
from PyQt5.QtWidgets import QMessageBox

# Import the Gmail reading functionality from another module
# from gmail_reader import read_gmail_and_generate_dict

# Define a function to handle the backup of make.json
def read_make_json():
    if os.path.exists('make.json'):
        with open('make.json', 'r') as f:
            make_dict = json.load(f)
        return make_dict
    else:
        return {}

def backup_make_json():
    if os.path.exists('make.json'):
        backup_folder = 'backup'
        os.makedirs(backup_folder, exist_ok=True)
        backup_file = os.path.join(backup_folder, f'make_backup_{datetime.now().strftime("%Y-%m-%d_%H%M%S")}.json')
        shutil.copy('make.json', backup_file)
        # Clean up old backup files (keep only for 3 days)
        for file in os.listdir(backup_folder):
            file_path = os.path.join(backup_folder, file)
            if os.path.isfile(file_path):
                file_time = datetime.fromtimestamp(os.path.getctime(file_path))
                if datetime.now() - file_time > timedelta(days=3):
                    os.remove(file_path)

# Define the main window class
class MainWindow(QtWidgets.QMainWindow,Ui_MainWindow):
    def __init__(self):
        super(MainWindow,self).__init__()
        self.setupUi(self)
        self.setWindowTitle("Get Gmail Data")

        # Backup make.json
        backup_make_json()
        # Read make.json and store its data in make_dict
        self.make_dict = read_make_json()

        self.pushButton_kaishi.clicked.connect(self.start_processing)
        self.pushButton_baocun.clicked.connect(self.save_to_csv)
        self.pushButton_chongzhi.clicked.connect(self.show_reset_confirmation)

    # 点击重置
    def show_reset_confirmation(self):
        # 创建确认提示框
        confirmation_box = QMessageBox()
        confirmation_box.setIcon(QMessageBox.Question)
        confirmation_box.setWindowTitle("重置")
        confirmation_box.setText("确定要清空所有字段吗？")
        confirmation_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)

        # 显示确认提示框，并等待用户响应
        response = confirmation_box.exec_()

        # 如果用户点击了“是”按钮，则清空字段
        if response == QMessageBox.Yes:
            self.clear_fields()
    def clear_fields(self):
        # Clear all QLineEdit fields
        for line_edit in self.findChildren(QtWidgets.QLineEdit):
            line_edit.clear()

        # Clear all QTextEdit fields
        for text_edit in self.findChildren(QtWidgets.QTextEdit):
            text_edit.clear()
    # 点击开始
    def start_processing(self):
        # Change button text to indicate processing
        self.pushButton_kaishi.setText("工作中")
        # Call function to read Gmail and generate dict
        # self.data_dict = read_gmail_and_generate_dict()
        # Restore button text after processing
        self.pushButton_kaishi.setText("开始")

    # 点击保存
    def save_to_csv(self):
        # Get current datetime for filename
        current_datetime = datetime.now().strftime("%Y-%m-%d_%H%M%S")
        # Create a CSV file with current datetime as filename
        csv_filename = f"{current_datetime}.csv"
        with open(csv_filename, 'w', newline='') as csvfile:
            csv_writer = csv.writer(csvfile)
            # Write data from line edits to CSV file
            # Example: csv_writer.writerow([self.lineEdit_Wuliudanhao.text(), ...])
            # You need to iterate through all line edits and get their text
            # Make sure to handle missing data appropriately
        # Backup make.json
        # backup_make_json()

# Entry point of the application
if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    win = MainWindow()

    win.show()
    sys.exit(app.exec_())
