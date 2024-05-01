import re,time
import json
import requests
import win32com.client
import pandas as pd
import ThreadPool
import os
from datetime import datetime


# import flaskToWeb


def read_title():
    try:
        # 读取 Excel 文件，生成字典
        excel_path = r"Z:\bazhuayu\title和番号.xlsm"
        df_title = pd.read_excel(excel_path, sheet_name="番号=title", header=None)
        df_title.fillna('', inplace=True)
        title_dict = {}
        csv_dict = {}
        for index, row in df_title.iterrows():
            try:
                banhao_csv = int(row[1])
                if banhao_csv == 0:
                    continue
            except:
                continue
            title = str(row[2]).strip()
            if row[3] == 0:
                row[3] = ''
            try:
                title_dict[title] = banhao_csv
                data = [
                    banhao_csv,
                    '',
                    row[4],
                    row[6],
                    row[2],
                    '', '', '', '', '', row[3],
                ]
                csv_dict[str(banhao_csv)] = data
            except:
                pass

        df_JAN = pd.read_excel(excel_path, sheet_name="采集 (4)", header=None)
        df_JAN.fillna('', inplace=True)
        JAN_dict = {}
        for index, row in df_JAN.iterrows():
            try:
                banhao_str = int(row[1])
                if banhao_str == 0:
                    continue
            except:
                continue
            try:
                JAN = int(row[7])
                if JAN == 0:
                    csv_dict[str(banhao_str)][9] = ''
                else:
                    csv_dict[str(banhao_str)][9] = JAN
                    JAN_dict[str(JAN)] = banhao_str
            except:
                csv_dict[str(banhao_str)][9] = " "

    except Exception as e:
        print(f"发生异常: {e}")
        print("title和番号.xlsm绑定不成功，退出")
        exit()

    paichu_path = r"Z:\bazhuayu\paichu.xlsx"
    paichu_excel = pd.read_excel(paichu_path, sheet_name="Sheet1")
    paichu_excel.fillna('', inplace=True)
    paichu_dict = {}
    today = datetime.now().date()
    for index, row in paichu_excel.iterrows():
        try:
            banhao = int(row[0])
            if banhao == 0:
                continue
        except:
            continue

        if row[5] == '':
            paichu_dict[str(banhao)] = '有'
            continue

        paichu_date = pd.to_datetime(row[5], errors='coerce')

        if pd.isna(paichu_date):
            paichu_date = pd.to_datetime("2099-01-22 00:00:00")

        if today <= paichu_date.date():
            paichu_dict[str(banhao)] = '有'

    zaiku_path = r"Z:\bazhuayu\在庫.csv"
    zaiku_excel = pd.read_csv(zaiku_path)
    zaiku_excel.fillna('', inplace=True)
    zaiku_dict = {}
    for index, row in zaiku_excel.iterrows():

        try:
            zaiku_jan = int(row[2])
            if zaiku_jan == 0:
                continue
        except:
            continue

        try:
            zaiku_dict[JAN_dict[str(zaiku_jan)]] = '有'
        except:
            continue
    return title_dict, zaiku_dict, JAN_dict, paichu_dict, csv_dict


def read_emails(read_unread="all", mark_as_read=True, max_emails=None, sort_by_date=True):
    outlook = win32com.client.Dispatch("Outlook.Application").GetNamespace("MAPI")
    accounts = win32com.client.Dispatch("Outlook.Application").Session.Accounts;
    redata = []
    title_dict, zaiku_dict, JAN_dict, paichu_dict, csv_dict = read_title()
    unread_emails = []  # 存储所有未读邮件
    for account in accounts:
        inbox = outlook.Folders(account.DeliveryStore.DisplayName)
        folders = inbox.Folders
        for folder in folders:
            if folder.name != "收件箱":
                continue
            messages = folder.Items
            if sort_by_date:
                try:
                    messages.Sort("[ReceivedTime]", True)
                except Exception as sort_error:
                    print(f"Sort Error: {sort_error}")

            if messages:
                count = 0
                for message2 in messages:
                    try:
                        if read_unread == "all" and count >= max_emails:
                            count += 1
                            break

                        if not message2.UnRead and read_unread == "unread":
                            continue

                        unread_emails.append(message2)  # 将未读邮件添加到列表中
                        if mark_as_read:
                            message2.UnRead = False

                    except Exception as e:
                        print(f"Error: {e}")
                        pass

                    count += 1

        # 写入csv
    import csv
    nowtime = datetime.now()
    filename = nowtime.strftime('%Y-%m-%d_%H-%M') + '.csv'
    file_path = os.path.join(r'Z:\bazhuayu\Email', filename)

    # 将数据写入 CSV 文件
    with open(file_path, mode='w', newline='', encoding='utf-8-sig') as file:
        writer = csv.writer(file)

        # 处理所有未读邮件
        jishu = 1
        for message2 in unread_emails:
            print(f'当前记数={jishu},共计={len(unread_emails)}')
            jishu += 1
            try:
                title = re.findall("最安変動[↑↓]\s(.+?)\s最安変動お知らせ", message2.Subject)[0]
                print(title)
                paichu = ''
                zaiku = ''
                if title in up_set:
                    print('集合内以有，跳过')
                    continue
                else:
                    up_set.add(title)  # 将当前数据的键添加到集合中
                if title:
                    banhao = title_dict.get(title)
                    if banhao and banhao not in csv_dict:
                        paichu = paichu_dict.get(str(banhao), '')
                        zaiku = zaiku_dict.get(banhao, '')

                        paichu_zaiku = f'{paichu}/{zaiku}'
                        csv_dict[str(banhao)][1] = paichu_zaiku

                        kakaku_list = ThreadPool.get_kakaku_data(csv_dict[str(banhao)][10], '1')
                        Qoo10_jiage = int(ThreadPool.get_Qoo10_data(banhao))
                        if Qoo10_jiage != 0:
                            csv_dict[str(banhao)][6] = Qoo10_jiage

                            quan_list = [item for item in kakaku_list if '○' in item]
                            quan_num = len(quan_list)
                            csv_dict[str(banhao)][7] = quan_num

                            price = 0
                            # Calculate average price based on quan_num condition
                            if quan_num >= 6:
                                average_price = int(sum(
                                    int(float(item[5].replace('¥', '').replace(',', ''))) for item in quan_list[:6]) / 6)
                            elif 3 < quan_num < 6:
                                average_price = int(sum(int(float(item[5].replace('¥', '').replace(',', ''))) for item in
                                                    quan_list) / quan_num)
                            else:
                                average_price = 0
                            if average_price >= 60000:
                                price = int((average_price + csv_dict[str(banhao)][2]) / 0.983 / csv_dict[str(banhao)][3])
                            else:
                                price = int((average_price + csv_dict[str(banhao)][2]) / csv_dict[str(banhao)][3])

                            csv_dict[str(banhao)][8] = price
                            csv_dict[str(banhao)].insert(9,average_price)
                            zhangfu = price - Qoo10_jiage
                            csv_dict[str(banhao)][5] = zhangfu
                            print(f'Qoo10价格={Qoo10_jiage},供给原价={average_price},改后价格={price}')
                            if zhangfu > 0:
                                # banhao_URL = f'<a href="https://www.qoo10.jp/g/{banhao}" target="_blank">{banhao}'
                                banhao_URL = banhao
                                title_URL = f'<a href="{csv_dict[str(banhao)][10]}" target="_blank">{csv_dict[str(banhao)][4]}'
                                csv_dict[str(banhao)][0] = banhao_URL
                                csv_dict[str(banhao)][4] = title_URL

                                updata_list = csv_dict[str(banhao)][:-1]
                                redata.append(updata_list)

                                now = datetime.now()
                                # 将当前日期时间格式化为指定的格式（年月日时分）
                                now_date = now.strftime('%Y%m%d_%H%M')
                                updata_list.append(now_date)

                                web_updata(updata_list)

                                # 对每封邮件将数据写入CSV
                                # writer.writerow(['Column1', 'Column2', 'Column3', 'Column4', 'Column5', 'Column6'])  # 根据您的数据列数修改列名
                                writer.writerows(redata)
            except Exception as e:
                print(f"Error: {e}")
                pass

            try:
                message2.Save()
                message2.Close(0)
            except:
                pass

    print(f'数据已写入 CSV 文件: {file_path}')
    return redata


def web_updata(updata_list):
    api_url = 'http://127.0.0.1:5000/update_data'
    response = requests.post(api_url, json=updata_list)

    if response.status_code == 200:
        print('网页上传数据成功', updata_list)
    else:
        print('网页上传数据失败:', response.status_code, response.text)


def clear_list():
    api_url = 'http://127.0.0.1:5000/clear_list'
    response = requests.post(api_url)


# 调用 read_emails 函数时，设置 read_unread 参数为 "unread" 表示只读取未读邮件，设置为 "all" 表示读取所有邮件。
# 设置 sort_by_date 参数为 True 表示按最新日期排序，为 False 表示不排序。
# 设置 mark_as_read 参数为 True 表示读取邮件后将其标记为已读，为 False 表示不标记为已读。
# 设置 max_emails 参数为要读取的最大邮件数量。

# 运行前清空网站数据
clear_list()

up_set = set()  # 在函数外定义集合，用于存储已经上传过的数据的键
if __name__ == '__main__':
    print('工作开始……')
    while True:
        re_aa = read_emails(read_unread="all", mark_as_read=True, max_emails=100, sort_by_date=True)
        print('暂停60分')
        time.sleep(3600)
        print('工作中……')

