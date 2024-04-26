import tkinter as tk
import keyboard
def select_all():
    # 判断当前全选复选框的状态
    if select_all_var.get() == 1:
        # 全选复选框被选中，勾选所有复选框
        for checkbox in checkboxes:
            checkbox.select()
    else:
        # 全选复选框未被选中，取消所有复选框的勾选
        for checkbox in checkboxes:
            checkbox.deselect()

def start(event=None):
    # 开始操作
    print('点击开始')

def stop(event=None):
    # 停止操作
    print('点击结束')

root = tk.Tk()
root.title("窗口")

checkboxes = []
select_all_var = tk.IntVar()

# 创建复选框
checkbox_texts = ["在库下载", "定单下载", "定单处理", "定单上传", "クリックポスト上传", "出库"]
for text in checkbox_texts:
    checkbox = tk.Checkbutton(root, text=text, variable=select_all_var)
    checkbox.pack(anchor=tk.W)
    checkboxes.append(checkbox)

# 全选复选框
select_all_checkbox = tk.Checkbutton(root, text="全选", command=select_all, variable=select_all_var)
select_all_checkbox.pack(anchor=tk.W)

# 开始和停止按钮
start_button = tk.Button(root, text="开始(Ct+F11)", command=start)
start_button.pack(side=tk.LEFT)
stop_button = tk.Button(root, text="停止(Ct+F12)", command=stop)
stop_button.pack(side=tk.LEFT)

# 注册全局热键
keyboard.add_hotkey('ctrl+f11', start)
keyboard.add_hotkey('ctrl+f12', stop)

root.mainloop()
