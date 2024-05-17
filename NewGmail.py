import os
import imaplib
import email
from email.header import decode_header
import re
from datetime import datetime, timedelta
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

# OAuth 2.0 相关信息
SCOPES = ['https://mail.google.com/']
CLIENT_SECRET_FILE = r"D:\pythonProject\Gmail\client_secret.json"  # 替换为你的client_secret.json文件路径
TOKEN_FILE = 'token.json'
# 账户信息
username = "asutbp92810@gmail.com"
password = "123456789brilliant"
keyword = "CF-FV4CDTCR"

# 获取 OAuth 2.0 凭据
def get_credentials():
    creds = None
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(TOKEN_FILE, 'w') as token:
            token.write(creds.to_json())
    return creds


# 获取 OAuth 2.0 凭据
creds = get_credentials()
auth_string = f'user={username}\1auth=Bearer {creds.token}\1\1'

# 连接到Gmail的IMAP服务器
mail = imaplib.IMAP4_SSL("imap.gmail.com")

# 登录
mail.authenticate('XOAUTH2', lambda x: auth_string)

# 选择收件箱
mail.select("inbox")

# 获取当前日期和5天前的日期
date_format = "%d-%b-%Y"
today = datetime.today()
since_date = (today - timedelta(days=2)).strftime(date_format)

# 搜索5天以内的邮件
search_criteria = f'(SINCE {since_date})'
status, messages = mail.search(None, search_criteria)


# 将邮件ID转换为列表
email_ids = messages[0].split()
print(len(email_ids),email_ids)
# 初始化一个列表来保存价格变化
price_changes = []

# 遍历每封邮件
for email_id in email_ids:
    # 获取邮件数据
    status, msg_data = mail.fetch(email_id, "(RFC822)")

    for response_part in msg_data:
        if isinstance(response_part, tuple):
            # 从消息数据中获取邮件内容
            msg = email.message_from_bytes(response_part[1])

            # 解码邮件主题
            subject, encoding = decode_header(msg["Subject"])[0]
            if isinstance(subject, bytes):
                subject = subject.decode(encoding if encoding else "utf-8")
                print('邮件主题：',subject)
            # 遍历邮件的各个部分
            # if msg.is_multipart():
            #     for part in msg.walk():
            #         # 如果邮件内容是文本或HTML
            #         if part.get_content_type() == "text/plain" or part.get_content_type() == "text/html":
            #             # 解码邮件内容
            #             body = part.get_payload(decode=True).decode(part.get_content_charset())
            #             # 检查邮件内容是否包含关键词
            #             if keyword in body:
            #                 # 使用正则表达式查找价格
            #                 prices = re.findall(r'\d+\.\d{2}', body)
            #                 # 将找到的价格添加到价格变化列表
            #                 price_changes.extend(prices)
            # else:
            #     # 如果邮件内容不是多部分
            #     body = msg.get_payload(decode=True).decode(msg.get_content_charset())
            #     if keyword in body:
            #         prices = re.findall(r'\d+\.\d{2}', body)
            #         price_changes.extend(prices)

# 打印价格变化
print("价格变化列表:")
for price in price_changes:
    print(price)

# 关闭连接
mail.logout()
