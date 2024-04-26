import sys

import pandas as pd
import datetime
from tkinter import Tk, filedialog,messagebox

def select_file_dialog():
    """弹出文件选择框选择文件"""
    root = Tk()
    root.withdraw()  # 隐藏Tk窗口
    file_path = filedialog.askopenfilename()  # 获取文件路径


    if not file_path:
        messagebox.showerror('错误', '没有选择文件，程序退出！')
        sys.exit()
    if not file_path.endswith('.csv'):
        messagebox.showerror('错误', '不是csv文件，程序退出！')
        sys.exit()
    if 'detail' not in file_path:
        messagebox.showerror('错误', '文件不是详情模式，程序退出！')
        sys.exit()

    print(file_path)
    return file_path

def generate_output_files(Qoo10data_file, zaiku_file_path, output_folder):

    # 读取第一个表和在库表的数据
    Qdata = pd.read_csv(Qoo10data_file, encoding='shift-jis')
    zaiku_data = pd.read_csv(zaiku_file_path, encoding='shift-jis')


    Qdata['JANコード'] = Qdata['JANコード'].astype(str)
    zaiku_data['商品ID'] = zaiku_data['商品ID'].astype(str).str.strip()
    # print(Qdata['入金日'])
    # print(zaiku_data)
    # print("商品ID 列的数据类型：", zaiku_data['商品ID'].dtype)
    # print("JANコード 列的数据类型：", Qdata['JANコード'].dtype)

    # 将日期数据转换为 datetime 格式
    Qdata['入金日'] = pd.to_datetime(Qdata['入金日'])
    # 根据入金日期升序对Qoo10data表进行排序
    Qdata.sort_values(by='入金日', ascending=True, inplace=True)

    # 初始化可出库表和出库UP表
    available_for_shipping = pd.DataFrame(columns=Qdata.columns)
    in_stock_UP = pd.DataFrame(columns=['品番', '注文番号', '発送予定日', '商品名', '数量', '決済サイト', '購入者決済金額', '供給原価の合計', '販売者商品コード', 'JANコード'])

    #获取今日日期
    now = datetime.datetime.now()
    # 将当前日期时间格式化为指定的格式（年月日时分）
    now_date = now.strftime('%Y%m%d%H%M')

    # 初始化字典
    dizhi_dict = {}
    zhuwenbanhao_dict = {}

    # 对于第一个表中的每个订单
    for index, row in Qdata.iterrows():
        # 在在库表中查找匹配的商品
        matching_items = zaiku_data[(zaiku_data['商品ID'] == row['JANコード']) & (zaiku_data['在庫数'] > 0)]

        # 获取地址和注文番号
        address = row['住所']
        order_number = row['注文番号']

        # 更新dizhi_dict和zhuwenbanhao_dict,无论是否有数据都向地址添加注文番号
        if address not in dizhi_dict:
            dizhi_dict[address] = [order_number]
        else:
            dizhi_dict[address].append(order_number)

        # 如果有库存，处理该订单
        if not matching_items.empty:

            if order_number not in zhuwenbanhao_dict:

                # 创建出库UP表的条目
                in_stock_up_item = {
                    '品番': zaiku_data.loc[matching_items.index[0], '品番'],
                    '注文番号': row['注文番号'],
                    '発送予定日': now_date,
                    '商品名': row['商品名'],
                    '数量': row['数量'],
                    '決済サイト': row['決済サイト'],
                    '購入者決済金額': row['購入者決済金額'],
                    '供給原価の合計': row['供給原価の合計'],
                    '販売者商品コード': row['販売者商品コード'],
                    'JANコード': row['JANコード']
                }
                zhuwenbanhao_dict[order_number] = [[row], [in_stock_up_item]]

            # 减少库存数量
            zaiku_data.loc[matching_items.index[0], '在庫数'] -= 1

    print(dizhi_dict)
    print(zhuwenbanhao_dict)
    # 遍历dizhi_dict
    for address, order_numbers in dizhi_dict.items():
        # 检查对应地址的订单是否都有对应的在库商品
        all_orders_have_stock = True
        for order_number in order_numbers:
            if order_number not in zhuwenbanhao_dict:
                all_orders_have_stock = False
                break

        # 如果都有对应的在库商品，则将内容写入可出货表和出库UP表中
        if all_orders_have_stock:
            for order_number in order_numbers:
                # 写入可出货表
                available_for_shipping = available_for_shipping.append(zhuwenbanhao_dict[order_number][0],
                                                                       ignore_index=True)

                # 写入出库UP表
                for item in zhuwenbanhao_dict[order_number][1]:
                    in_stock_UP = in_stock_UP.append(item, ignore_index=True)

    # 判断available_for_shipping是否为空
    if not available_for_shipping.empty:
        available_for_shipping.to_csv(f"{output_folder}\\可出库{now_date}.csv", index=False, encoding='shift-jis')
    else:
        messagebox.showinfo("提示", "可出库表为空，无数据需要保存。")
        sys.exit()
    in_stock_UP.to_csv(f"{output_folder}\\出庫UP{now_date}.csv", index=False, encoding='ANSI')

    #生成邮局上传文件
    # 过滤出配送会社为"ゆうパケット"的行
    yuupacket_data = available_for_shipping[available_for_shipping["配送会社"] == "ゆうパケット"]

    # 定义新表的标题行
    new_columns = ["お届け先郵便番号", "お届け先氏名", "お届け先敬称", "お届け先住所1行目", "お届け先住所2行目",
                   "お届け先住所3行目",
                   "お届け先住所4行目", "内容品"]
    new_data = pd.DataFrame(columns=new_columns)

    # 商品名关键字映射字典
    keyword_mapping = {
        "Switch": "ゲームソフト",
        "PS4": "ゲームソフト",
        "任天堂": "ゲームソフト",
        "ゲーム": "ゲームソフト",
        "Office": "PCソフト",
        "SSD": "PCパーツ(バッテリーなし)",
        "HHD": "PCパーツ(バッテリーなし)",
        "NVMe": "PCパーツ(バッテリーなし)",
        "SATA": "PCパーツ(バッテリーなし)",
        "M.2": "PCパーツ(バッテリーなし)",
        "メモリ": "PCパーツ(バッテリーなし)",
        "Keyboard": "キーボード",
        "Trackpad": "マウス"
    }

    # 遍历原始数据逐行生成新表
    for index, row in yuupacket_data.iterrows():
        # 在这里根据表1的标题行逐行处理原始数据，并生成新表的一行数据
        new_row = [
            row["郵便番号"][1:],  # お届け先郵便番号，去掉最前面的'
            row["受取人名"],  # お届け先氏名
            "様",  # お届け先敬称
            row["住所"][:20],  # お届け先住所1行目，最多20个字符
            row["住所"][20:40],  # お届け先住所2行目，最多20个字符
            row["住所"][40:60],  # お届け先住所3行目，最多20个字符
            row["受取人携帯電話番号"] if pd.notnull(row["受取人携帯電話番号"]) else row["受取人電話番号"],
            # お届け先住所4行目，如果受取人携帯電話番号为空则添入受取人電話番号
            row["商品名"]  # 数量
        ]
        # 根据关键字映射字典查找内容品
        for keyword, content in keyword_mapping.items():
            if keyword in row["商品名"]:
                new_row[-1] = content
                break
        new_data = new_data.append(pd.Series(new_row, index=new_data.columns), ignore_index=True)
    # 保存新表
    new_data.to_csv(f"{output_folder}\\ゆうパケット{now_date}.csv", index=False, encoding='ANSI')



# 获取文件路径
Qoo10data_file = select_file_dialog()
print(Qoo10data_file)
#在库文件路径
zaiku_file_path = r"\\LS410D8E6\tool\bazhuayu\在庫.csv"


# 生成输出文件
generate_output_files(Qoo10data_file, zaiku_file_path, r"D:\\")




