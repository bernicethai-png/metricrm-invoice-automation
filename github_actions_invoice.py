#!/usr/bin/env python3
"""
MetriCRM 云端自动发票生成系统 - GitHub Actions版本
自动生成发票、上传到Dropbox、发送email
"""

import os
import smtplib
import shutil
from datetime import datetime, date
from pathlib import Path
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.utils import formatdate
from email import encoders

try:
    import dropbox
except ImportError:
    print("需要安装dropbox库: pip install dropbox")
    exit(1)

# ===== 配置 =====
# 这些值应该通过GitHub Secrets设置
DROPBOX_TOKEN = os.getenv("DROPBOX_TOKEN", "")
GMAIL_USER = os.getenv("GMAIL_USER", "")
GMAIL_PASSWORD = os.getenv("GMAIL_PASSWORD", "")

# PDF路径 - 支持多个可能的位置
PDF_PATHS = [
    os.getenv("PDF_PATH", ""),  # 优先使用环境变量
    "./output/output_invoice.pdf",  # GitHub Actions生成的位置
    "output/output_invoice.pdf",
]

# 找到第一个存在的PDF文件
PDF_PATH = None
for path in PDF_PATHS:
    if path and Path(path).exists():
        PDF_PATH = path
        break

# 邮件配置 - 测试模式
SENDER_EMAIL = "bernice@webbalances.com"
RECIPIENT_EMAIL = "bernice@webbalances.com"  # 测试：发送给自己
BCC_EMAILS = []  # 测试：不发送BCC

# Dropbox保存路径
DROPBOX_FOLDER = "/Webbalances/Customer_Account/MetriCRM Auto Invoice"

# 签名
EMAIL_SIGNATURE = """Best Regards

Bernice Thai
E bernice@webbalances.com
P +6010 831 2238
W www.webbalances.com

Webbalances Solution (003096168-D)
Unit 6, Level 4 Setiawalk Mall (Block K),
Persiaran Wawasan, Pusat Bandar Puchong,
47160 Puchong Selangor."""

def get_invoice_info():
    """获取发票信息"""
    today = date.today()
    year = today.year % 100
    month = today.month
    day = today.day

    months = ['January', 'February', 'March', 'April', 'May', 'June',
              'July', 'August', 'September', 'October', 'November', 'December']

    invoice_num = f"WB_INV_{year:02d}{month:02d}{day:02d}_01"
    month_name = months[month - 1]

    return {
        "invoice_num": invoice_num,
        "month_name": month_name,
        "year": today.year,
        "month": month,
        "day": day
    }

def upload_to_dropbox(file_path, invoice_info):
    """上传文件到Dropbox"""
    try:
        dbx = dropbox.Dropbox(DROPBOX_TOKEN)

        # 获取下一个编号
        try:
            entries = dbx.files_list_folder(DROPBOX_FOLDER).entries
            max_number = 65
            for entry in entries:
                if entry.name[0].isdigit():
                    try:
                        number = int(entry.name.split('.')[0])
                        max_number = max(max_number, number)
                    except (ValueError, IndexError):
                        pass
            next_number = max_number + 1
        except:
            next_number = 66

        # 生成Dropbox文件名
        dropbox_filename = f"{next_number}.{invoice_info['invoice_num']}.pdf"
        dropbox_path = f"{DROPBOX_FOLDER}/{dropbox_filename}"

        # 读取文件并上传
        with open(file_path, 'rb') as f:
            dbx.files_upload(f.read(), dropbox_path, mode=dropbox.files.WriteMode('overwrite'))

        print(f"✅ 成功上传到Dropbox: {dropbox_path}")
        return True
    except Exception as e:
        print(f"❌ Dropbox上传失败: {e}")
        return False

def send_email(invoice_info):
    """发送email"""
    try:
        # 生成邮件内容
        subject = f"Monthly Invoice - {invoice_info['month_name']} {invoice_info['year']}"

        body = f"""Hi Invite Finance,

Herewith the MetriCRM invoice, please find your invoice attached.
Invoice Number: {invoice_info['invoice_num']}
Amount: RM320.00

Thank you for your support and it is a pleasure serving you

{EMAIL_SIGNATURE}"""

        # 创建邮件
        msg = MIMEMultipart()
        msg['From'] = SENDER_EMAIL
        msg['To'] = RECIPIENT_EMAIL
        msg['Bcc'] = ', '.join(BCC_EMAILS)
        msg['Date'] = formatdate(localtime=True)
        msg['Subject'] = subject

        # 添加邮件正文
        msg.attach(MIMEText(body, 'plain', 'utf-8'))

        # 添加附件
        if PDF_PATH and os.path.exists(PDF_PATH):
            with open(PDF_PATH, 'rb') as attachment:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(attachment.read())

            encoders.encode_base64(part)
            part.add_header('Content-Disposition', f'attachment; filename= {invoice_info["invoice_num"]}.pdf')
            msg.attach(part)

        # 发送邮件 - 使用公司邮箱SMTP (465 SSL)
        with smtplib.SMTP_SSL('smtp.webbalances.com', 465) as server:
            server.login(GMAIL_USER, GMAIL_PASSWORD)
            server.send_message(msg)

        print(f"✅ 邮件已发送到 {RECIPIENT_EMAIL}")
        print(f"   BCC: {', '.join(BCC_EMAILS)}")
        return True
    except Exception as e:
        print(f"❌ 邮件发送失败: {e}")
        return False

def main():
    """主函数"""
    print("🚀 开始云端发票生成和发送流程...")

    # 获取发票信息
    invoice_info = get_invoice_info()
    print(f"📋 发票信息:")
    print(f"   号码: {invoice_info['invoice_num']}")
    print(f"   月份: {invoice_info['month_name']} {invoice_info['year']}")

    # 检查PDF文件
    if not PDF_PATH or not os.path.exists(PDF_PATH):
        print(f"⚠️  找不到PDF文件: {PDF_PATH}")
        return False

    # 上传到Dropbox
    if not upload_to_dropbox(PDF_PATH, invoice_info):
        print("⚠️  Dropbox上传失败，继续发送邮件...")

    # 发送邮件
    if not send_email(invoice_info):
        print("❌ 邮件发送失败")
        return False

    print("✨ 发票已自动生成、保存到Dropbox并发送邮件！")
    return True

if __name__ == "__main__":
    main()
