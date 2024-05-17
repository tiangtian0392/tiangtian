"""
为了在搜索邮件时限制日期范围，可以使用 IMAP 搜索命令中的日期条件。IMAP 支持使用 SINCE 和 BEFORE 关键字来过滤邮件日期。
说明
计算日期范围: 使用 datetime 模块计算当前日期和 5 天前的日期，并格式化为 dd-MMM-yyyy 格式，这是 IMAP 搜索日期的标准格式。
搜索邮件: 使用 mail.search(None, f'(SINCE {since_date})') 只搜索从指定日期以来的邮件。
检查邮件内容: 获取到符合日期范围的邮件后，逐封检查邮件内容是否包含指定关键词。

"""


import imaplib
import email
from email.header import decode_header
import re
from datetime import datetime, timedelta

# 账户信息
username = "asutbp92810@gmail.com"
password = "123456789brilliant"
keyword = "CF-FV4CDTCR"

# 获取当前日期和5天前的日期
date_format = "%d-%b-%Y"
today = datetime.today()
since_date = (today - timedelta(days=5)).strftime(date_format)

# 连接到Gmail的IMAP服务器
mail = imaplib.IMAP4_SSL("imap.gmail.com")

# 登录
mail.login(username, password)

# 选择收件箱
mail.select("inbox")

# 搜索5天以内的邮件
search_criteria = f'(SINCE {since_date})'
status, messages = mail.search(None, search_criteria)

# 将邮件ID转换为列表
email_ids = messages[0].split()

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

            # 遍历邮件的各个部分
            if msg.is_multipart():
                for part in msg.walk():
                    # 如果邮件内容是文本或HTML
                    if part.get_content_type() == "text/plain" or part.get_content_type() == "text/html":
                        # 解码邮件内容
                        body = part.get_payload(decode=True).decode(part.get_content_charset())
                        # 检查邮件内容是否包含关键词
                        if keyword in body:
                            # 使用正则表达式查找价格
                            prices = re.findall(r'\d+\.\d{2}', body)
                            # 将找到的价格添加到价格变化列表
                            price_changes.extend(prices)
            else:
                # 如果邮件内容不是多部分
                body = msg.get_payload(decode=True).decode(msg.get_content_charset())
                if keyword in body:
                    prices = re.findall(r'\d+\.\d{2}', body)
                    price_changes.extend(prices)

# 打印价格变化
print("价格变化列表:")
for price in price_changes:
    print(price)

# 关闭连接
mail.logout()
