#!/usr/bin/env python3
"""
MetriCRM 发票上传Dropbox和发送邮件
"""

import os
import sys
import smtplib
from datetime import date
from pathlib import Path
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.utils import formatdate
from email import encoders

print("🚀 开始云端发票生成和发送流程...")
print(f"📂 当前工作目录: {os.getcwd()}")

try:
    import dropbox
except ImportError:
    print("❌ 需要安装dropbox库")
    sys.exit(1)

# ===== 环境变量 =====
DROPBOX_TOKEN = os.getenv("DROPBOX_TOKEN", "")
GMAIL_USER = os.getenv("GMAIL_USER", "")
GMAIL_PASSWORD = os.getenv("GMAIL_PASSWORD", "")

print(f"📋 配置信息:")
print(f"   DROPBOX_TOKEN: {'✅' if DROPBOX_TOKEN else '❌'}")
print(f"   GMAIL_USER: {GMAIL_USER}")
print(f"   GMAIL_PASSWORD: {'✅' if GMAIL_PASSWORD else '❌'}")

# ===== 查找PDF文件 =====
print(f"🔍 查找PDF文件...")

PDF_CANDIDATES = [
    "./output/output_invoice.pdf",
    "output/output_invoice.pdf",
    "/home/runner/work/metricrm-invoice-automation/metricrm-invoice-automation/output/output_invoice.pdf",
]

PDF_PATH = None
for candidate in PDF_CANDIDATES:
    full_path = Path(candidate)
    print(f"   尝试: {candidate} ... ", end="")
    if full_path.exists():
        PDF_PATH = str(full_path)
        print(f"✅ 找到!")
        break
    else:
        print(f"❌")

if not PDF_PATH:
    print(f"❌ 找不到任何PDF文件!")
    sys.exit(1)

print(f"✅ 使用PDF: {PDF_PATH}")

# ===== 获取发票信息 =====
today = date.today()
invoice_num = f"WB_INV_{today.year%100:02d}{today.month:02d}{today.day:02d}_02"
months = ['January', 'February', 'March', 'April', 'May', 'June',
          'July', 'August', 'September', 'October', 'November', 'December']
month_name = months[today.month - 1]

invoice_info = {
    "invoice_num": invoice_num,
    "month_name": month_name,
    "year": today.year
}

print(f"📋 发票信息:")
print(f"   号码: {invoice_info['invoice_num']}")
print(f"   月份: {invoice_info['month_name']} {invoice_info['year']}")

# ===== 发送邮件 =====
print(f"📧 发送邮件...")

SENDER_EMAIL = "bernice@webbalances.com"
RECIPIENT_EMAIL = "bernice@webbalances.com"
BCC_EMAILS = []

EMAIL_SIGNATURE = """Best Regards

Bernice Thai
E bernice@webbalances.com
P +6010 831 2238
W www.webbalances.com

Webbalances Solution (003096168-D)
Unit 6, Level 4 Setiawalk Mall (Block K),
Persiaran Wawasan, Pusat Bandar Puchong,
47160 Puchong Selangor."""

try:
    subject = f"MetriCRM Monthly Invoice - {invoice_info['month_name']} {invoice_info['year']}"

    html_body = f"""<html>
<body style="font-family: Arial, sans-serif; font-size: 14px; line-height: 1.6; color: #333;">
    <p>Hi Invite Finance,</p>

    <p>Herewith the MetriCRM {invoice_info['month_name']} invoice, please find your invoice attached.</p>

    <p>
        <strong>Invoice Number:</strong> {invoice_info['invoice_num']}<br>
        <strong>Amount:</strong> RM320.00
    </p>

    <p>Thank you for your support and it is a pleasure serving you</p>

    <hr style="border: none; border-top: 1px solid #ddd; margin: 20px 0;">

    <p style="font-weight: bold; color: #d4a574; margin-bottom: 10px;">Bernice Thai</p>
    <p style="font-size: 14px; color: #c41e3a; margin: 5px 0;">
        Email: bernice@webbalances.com<br>
        Phone: +6010 831 2238<br>
        Website: www.webbalances.com
    </p>

    <hr style="border: none; border-top: 1px dashed #ccc; margin: 20px 0;">

    <p style="font-size: 14px; font-weight: bold;">Webbalances Solution (003096168-D)</p>
    <p style="font-size: 14px; margin: 5px 0;">
        Unit 6, Level 4 Setiawalk Mall (Block K),<br>
        Persiaran Wawasan, Pusat Bandar Puchong,<br>
        47160 Puchong Selangor.
    </p>
</body>
</html>"""

    msg = MIMEMultipart('alternative')
    msg['From'] = SENDER_EMAIL
    msg['To'] = RECIPIENT_EMAIL
    msg['Bcc'] = ', '.join(BCC_EMAILS)
    msg['Date'] = formatdate(localtime=True)
    msg['Subject'] = subject

    text_part = MIMEText(f"Hi Invite Finance,\n\nHerewith the MetriCRM {invoice_info['month_name']} invoice, please find your invoice attached.\nInvoice Number: {invoice_info['invoice_num']}\nAmount: RM320.00\n\nThank you for your support and it is a pleasure serving you", 'plain', 'utf-8')
    html_part = MIMEText(html_body, 'html', 'utf-8')

    msg.attach(text_part)
    msg.attach(html_part)

    # 添加PDF附件
    if os.path.exists(PDF_PATH):
        with open(PDF_PATH, 'rb') as attachment:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(attachment.read())
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', f'attachment; filename={invoice_info["invoice_num"]}.pdf')
            msg.attach(part)
        print(f"   ✅ 已附加PDF")
    else:
        print(f"   ⚠️  找不到PDF文件，发送不带附件的邮件")

    # 发送邮件
    print(f"   连接SMTP服务器: smtp.webbalances.com:465...")
    with smtplib.SMTP_SSL('smtp.webbalances.com', 465) as server:
        print(f"   登录: {GMAIL_USER}")
        server.login(GMAIL_USER, GMAIL_PASSWORD)
        server.send_message(msg)
        print(f"   ✅ 邮件已发送!")

except Exception as e:
    print(f"   ❌ 邮件发送失败: {e}")
    import traceback
    traceback.print_exc()

# ===== 上传到Dropbox =====
if DROPBOX_TOKEN:
    print(f"☁️  上传到Dropbox...")
    try:
        dbx = dropbox.Dropbox(DROPBOX_TOKEN)
        DROPBOX_FOLDER = "/Webbalances/Customer_Account/MetriCRM Auto Invoice"

        # 找下一个编号
        try:
            entries = dbx.files_list_folder(DROPBOX_FOLDER).entries
            max_number = 65
            for entry in entries:
                if entry.name[0].isdigit():
                    try:
                        number = int(entry.name.split('.')[0])
                        max_number = max(max_number, number)
                    except:
                        pass
            next_number = max_number + 1
        except:
            next_number = 66

        dropbox_filename = f"{next_number}.{invoice_info['invoice_num']}.pdf"
        dropbox_path = f"{DROPBOX_FOLDER}/{dropbox_filename}"

        with open(PDF_PATH, 'rb') as f:
            dbx.files_upload(f.read(), dropbox_path, mode=dropbox.files.WriteMode('overwrite'))

        print(f"   ✅ 上传成功: {dropbox_path}")

    except Exception as e:
        print(f"   ❌ Dropbox上传失败: {e}")
        import traceback
        traceback.print_exc()
else:
    print(f"⚠️  Dropbox token未设置，跳过上传")

print("✨ 完成!")
