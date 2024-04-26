import win32gui,win32con,win32api
from pywinauto.application import Application
import time

def find_control(hwnd_parent, class_name, text, index):
    # 遍历指定父窗口的子控件
    child = None
    count = 0  # 控件计数器
    while True:
        child = win32gui.FindWindowEx(hwnd_parent, child, None, None)
        if child == 0:
            break
        # 检查控件的类名和文本
        class_name_buffer = win32gui.GetClassName(child)
        control_text = win32gui.GetWindowText(child)
        # print(class_name_buffer,control_text)
        if class_name_buffer == class_name:
            count += 1
            if count == index:
                return child
        # 如果子控件有子控件，则递归遍历子控件
        sub_child = find_control(child, class_name, text, index)
        if sub_child:
            return sub_child
    return None

def find_edit_control(hwnd_parent, index):
    # 在指定父窗口下查找第 index 个 TEdit 类
    return find_control(hwnd_parent, "TEdit", "", index)

def set_edit_control_text(hwnd_edit, text):
    win32gui.SendMessage(hwnd_edit, win32con.WM_SETTEXT, None, text)

#根据传入参数返回控件ID
def set_window_get_ID(window_title, class_name1, index1,class_name2=None,index2=None):
    hwnd = win32gui.FindWindow(None, window_title)
    if hwnd:
        hwnd_quick_search = find_control(hwnd, class_name1, None, index1)  # 获取第一个 "クイック検索" 控件
        if hwnd_quick_search:
            
            hwnd_edit = find_control(hwnd_quick_search, class_name2, None, index2)  # 获取第二个 TEdit 控件
            
            if hwnd_edit:
                return hwnd_edit
                
            else:
                print("在指定的控件下找不到编辑框")
        else:
            print("找不到指定的窗口")
    else:
        print("找不到指定的窗口")

#用绝对值坐标点击出库按键并进行出库变更
def Btn_click_Cuku(window_title):

    hwnd = win32gui.FindWindow(None, window_title)
    if hwnd:
        rect = win32gui.GetWindowRect(hwnd)
        window_width = rect[2] - rect[0]  # 窗口宽度
        window_height = rect[3] - rect[1]  # 窗口高度
        if window_width < 480 or window_height < 70:
            win32gui.MoveWindow(hwnd, rect[0], rect[1], 1024, 800, True)
            rect = win32gui.GetWindowRect(hwnd)
        x = rect[0] + 480
        y = rect[1] + 70
        win32api.SetCursorPos((x, y))
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, x, y, 0, 0)
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, x, y, 0, 0)
        time.sleep(0.5)  # 等待0.5秒以确保点击生效
        # 检查"出庫処理"窗口是否存在
        hwnd_chuku = win32gui.FindWindow(None, "出庫処理")
        if not hwnd_chuku:
            time.sleep(1)  # 如果不存在则等待1秒
            win32api.SetCursorPos((x, y))  # 再次移动鼠标到指定位置
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, x, y, 0, 0)  # 再次模拟鼠标左键按下
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, x, y, 0, 0)  # 再次模拟鼠标左键释放
    else:
        print("找不到指定的窗口")

    # 启动应用程序或连接到已经运行的应用程序
    app = Application(backend="win32").connect(title="出庫参照", class_name="TDeliveryForm") 
    
    chuku_bianheng_button = app.window(title="出庫参照", class_name="TDeliveryForm").child_window(title="出庫変更", class_name="TBitBtn")
    if not chuku_bianheng_button.is_enabled():
        xns_grid = app.window(title="出庫参照", class_name="TDeliveryForm").child_window(class_name="XnsGrid")
        xns_grid.set_focus()
        for _ in range(2):  # 尝试两次，如果第一次不成功
            win32api.keybd_event(win32con.VK_UP, 0, 0, 0)  # 模拟按键向上
            win32api.keybd_event(win32con.VK_UP, 0, win32con.KEYEVENTF_KEYUP, 0)  # 模拟释放按键
            time.sleep(0.5)  # 等待0.5秒以确保操作生效
            if chuku_bianheng_button.is_enabled():
                break  # 如果按钮可用，则跳出循环
            win32api.keybd_event(win32con.VK_DOWN, 0, 0, 0)  # 模拟按键向下
            win32api.keybd_event(win32con.VK_DOWN, 0, win32con.KEYEVENTF_KEYUP, 0)  # 模拟释放按键
            time.sleep(0.5)  # 等待0.5秒以确保操作生效
            if chuku_bianheng_button.is_enabled():
                break  # 如果按钮可用，则跳出循环
    app.window(title="出庫参照", class_name="TDeliveryForm").child_window(title="出庫変更", class_name="TBitBtn").click_input()
    app.window(title="出庫参照", class_name="TDeliveryForm").child_window(class_name="TMemo", found_index=4).click_input()

    app.window(title="出庫参照", class_name="TDeliveryForm").child_window(title="出庫変更", class_name="TBitBtn").click_input()

    time.sleep(0.5)
    #点击试用
    app_1 = Application(backend="win32").connect(title="在庫番頭 Professional Edition", class_name="#32770")
    app_1.window(title="在庫番頭 Professional Edition", class_name="#32770").child_window(title="はい(&Y)", class_name="Button").click_input()

    app.window(title="出庫参照", class_name="TDeliveryForm").child_window(title="閉じる", class_name="TBitBtn").click_input()

# 等待Application窗口出现的函数
def wait_for_window(title, class_name, timeout=30):
    start_time = time.time()
    while True:
        print(f"尝试连接窗口'{title}'...")
        try:
            app = Application(backend="win32").connect(title=title, class_name=class_name)
            break  # 如果找到了窗口，跳出循环
        except Exception as e:
            if time.time() - start_time > timeout:
                raise TimeoutError(f"等待窗口'{title}'超时: {e}")
            time.sleep(1)  # 每隔1秒尝试一次
    time.sleep(1)

#检索的文本输入框，类='TGroupBox' index=1,第二个文本框类="TEdit",index=2
#检索的按键，类='TBitBtn' index=1
window_title = "(試用中)在庫番頭 Professional Edition"
text_class_name = "TGroupBox"
tedit_class_name = "TEdit"
btn_class_name = "TBitBtn"


#打开在库程序
try:
    Application(backend="win32").connect(title="(試用中)在庫番頭 Professional Edition", class_name="TMainForm")
except:
    app = Application(backend="win32").start(cmd_line=r"C:\Program Files (x86)\zbpro\StockC.exe")
    time.sleep(1)
    # 判断app窗体出现后，激活窗体，并按键回车
    app_window = app.window(title="在庫番頭 Professional Edition", class_name="TManageForm")    
    time.sleep(1)
    win32api.keybd_event(0x0D, 0, 0, 0)  # 模拟按键回车
    win32api.keybd_event(0x0D, 0, win32con.KEYEVENTF_KEYUP, 0)  # 模拟释放按键
    time.sleep(0.5)
    app_window.child_window(title="在庫管理実行", class_name="TBitBtn").click_input()

# 调用函数等待窗口出现
wait_for_window("(試用中)在庫番頭 Professional Edition", "TMainForm")



set_str_text = "00004"
search_text_ID = set_window_get_ID(window_title, class_name1 = text_class_name, index1 = 1, class_name2 = tedit_class_name, index2 = 2)
set_edit_control_text(search_text_ID, set_str_text)
time.sleep(1)

Btn_click_ID = set_window_get_ID(window_title, class_name1 = text_class_name, index1 = 1, class_name2 = btn_class_name, index2 = 1)
win32gui.SendMessage(Btn_click_ID, win32con.BM_CLICK, None, None)  # 点击按键

#点击出库参照
Btn_click_Cuku(window_title)





