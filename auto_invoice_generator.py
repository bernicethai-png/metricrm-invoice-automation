#!/usr/bin/env python3
"""
MetriCRM Auto Invoice Generator
自动生成发票并保存到指定位置（每月第7天）
"""

import os
import shutil
import subprocess
from datetime import datetime, date
from pathlib import Path

# 配置 - 使用实际的用户路径
HOME = Path.home()

PROJECT_DIR = HOME / "Claude/Projects/MetriCRM Auto Invoice"
DESKTOP_PATH = HOME / "Desktop/Others/Pending Payment/MetriCRM"
DROPBOX_PATH = HOME / "Dropbox/Webbalances/Customer_Account/Invite&Netergy/MetriCRM"

# 保存目标列表
SAVE_PATHS = [
    {"name": "桌面", "path": DESKTOP_PATH},
    {"name": "Dropbox", "path": DROPBOX_PATH}
]

TEMP_DIR = PROJECT_DIR / "temp_generate"

def get_invoice_info():
    """获取发票信息"""
    today = date.today()
    year = today.year % 100  # 获取年份的后两位
    month = today.month
    day = today.day

    # 生成发票号: WB_INV_YYMMDD_01
    invoice_num = f"WB_INV_{year:02d}{month:02d}{day:02d}_01"

    # 发票日期: DD-Mon-YY 格式
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
              'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    invoice_date = f"{day:02d}-{months[month-1]}-{year:02d}"

    # 计费周期: 01 Mon YYYY To DD Mon YYYY
    # 获取这个月的最后一天
    if month == 12:
        last_day = 31
    else:
        from calendar import monthrange
        last_day = monthrange(today.year, month)[1]

    billing_period = f"01 {months[month-1]} {today.year} To {last_day} {months[month-1]} {today.year}"

    return {
        "invoice_num": invoice_num,
        "invoice_date": invoice_date,
        "billing_period": billing_period,
        "year": today.year,
        "month": month,
        "day": day
    }

def should_generate_invoice():
    """检查是否应该生成发票（第7天）"""
    today = date.today()
    return today.day == 7

def copy_template():
    """复制模板文件到临时目录"""
    # 查找最近的XLSX模板
    xlsx_files = list(PROJECT_DIR.glob("**/temp_invoice.xlsx")) or \
                 list(PROJECT_DIR.glob("**/WB_INV_*.xlsx"))

    if not xlsx_files:
        # 如果没有找到，返回None
        return None

    template_file = xlsx_files[0]
    return template_file

def call_pdf_skill(invoice_info):
    """调用PDF生成技能或查找现有PDF"""
    invoice_num = invoice_info["invoice_num"]
    pdf_filename = f"{invoice_num}.pdf"

    # 1. 先查找项目目录根目录
    existing_pdf = PROJECT_DIR / pdf_filename
    if existing_pdf.exists():
        return existing_pdf

    # 2. 查找当前月份的文件夹
    month_year = datetime.now().strftime('%B %Y')
    month_dir = PROJECT_DIR / month_year
    if month_dir.exists():
        pdf_in_month = month_dir / pdf_filename
        if pdf_in_month.exists():
            return pdf_in_month

    # 3. 递归搜索子目录中的PDF
    for pdf_file in PROJECT_DIR.rglob("*.pdf"):
        if invoice_num in str(pdf_file):
            return pdf_file

    return None

def ensure_desktop_folder():
    """确保桌面路径存在"""
    os.makedirs(DESKTOP_PATH, exist_ok=True)

def get_next_dropbox_number():
    """获取Dropbox中的下一个编号"""
    try:
        if not DROPBOX_PATH.exists():
            return 66  # 默认从66开始

        # 查找Dropbox中所有的PDF文件
        max_number = 65
        for file in DROPBOX_PATH.glob("*.pdf"):
            # 尝试从文件名前面提取编号
            filename = file.name
            if filename[0].isdigit():
                try:
                    number = int(filename.split('.')[0])
                    max_number = max(max_number, number)
                except (ValueError, IndexError):
                    pass

        return max_number + 1
    except Exception as e:
        print(f"[DEBUG] 获取编号出错：{e}")
        return 66

def save_invoice_to_multiple_paths(pdf_path, invoice_info):
    """将发票复制到多个保存位置"""
    if not pdf_path or not pdf_path.exists():
        print(f"❌ 错误：找不到PDF文件 {pdf_path}")
        return False

    # 生成目标文件名：(Month)_WB_INV_YYMMDD_01.pdf
    months = ['January', 'February', 'March', 'April', 'May', 'June',
              'July', 'August', 'September', 'October', 'November', 'December']
    month_name = months[invoice_info["month"] - 1]
    desktop_filename = f"({month_name})_{invoice_info['invoice_num']}.pdf"

    # Dropbox使用编号前缀
    dropbox_number = get_next_dropbox_number()
    dropbox_filename = f"{dropbox_number}.{invoice_info['invoice_num']}.pdf"

    all_success = True

    # 保存到所有配置的路径
    for save_location in SAVE_PATHS:
        location_name = save_location["name"]

        # 根据位置选择不同的文件名
        if location_name == "Dropbox":
            filename = dropbox_filename
        else:
            filename = desktop_filename

        target_path = save_location["path"] / filename

        try:
            # 确保目录存在
            os.makedirs(target_path.parent, exist_ok=True)

            # 复制文件
            shutil.copy2(pdf_path, target_path)
            print(f"✅ 成功保存发票到{location_name}：{target_path}")
        except Exception as e:
            print(f"❌ 保存到{location_name}失败：{e}")
            all_success = False

    return all_success

def main():
    """主函数"""
    # 检查是否是第7天
    if not should_generate_invoice():
        today = date.today()
        print(f"ℹ️  今天是{today.day}号，不是每月第7天，跳过生成")
        return

    print("🚀 开始生成发票...")

    # 获取发票信息
    invoice_info = get_invoice_info()
    print(f"📋 发票号：{invoice_info['invoice_num']}")
    print(f"📅 发票日期：{invoice_info['invoice_date']}")
    print(f"⏰ 计费周期：{invoice_info['billing_period']}")

    # 获取PDF路径
    pdf_path = call_pdf_skill(invoice_info)

    if pdf_path:
        # 保存到多个位置
        if save_invoice_to_multiple_paths(pdf_path, invoice_info):
            print("✨ 发票已自动保存到所有位置！")
        else:
            print("⚠️  部分保存失败，请检查权限")
    else:
        print("⚠️  未找到现有的PDF文件，请先手动生成")

if __name__ == "__main__":
    main()
