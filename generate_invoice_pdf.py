#!/usr/bin/env python3
"""
MetriCRM Invoice Generator - 从Excel模板自动生成PDF发票
自动修改日期、发票号、计费周期，然后转换为PDF
"""

import os
import subprocess
from datetime import datetime, date
from pathlib import Path
from openpyxl import load_workbook
from openpyxl.utils import get_column_letter

# ===== 配置 =====
TEMPLATE_PATH = Path(__file__).parent / "MetriCRM.xlsx"
OUTPUT_DIR = Path(__file__).parent / "output"
OUTPUT_EXCEL = OUTPUT_DIR / "temp_invoice.xlsx"
OUTPUT_PDF = OUTPUT_DIR / "output_invoice.pdf"

# 时区调整 (GitHub Actions使用UTC, 需要+8小时转换为Malaysia时间)
def get_malaysia_date():
    """获取马来西亚当前日期"""
    from datetime import datetime, timedelta
    utc_now = datetime.utcnow()
    malaysia_now = utc_now + timedelta(hours=8)
    return malaysia_now.date()

def get_invoice_info():
    """获取发票信息"""
    today = get_malaysia_date()
    year = today.year
    month = today.month
    day = today.day

    # 生成发票号: WB_INV_YYMMDD_02
    invoice_num = f"WB_INV_{year%100:02d}{month:02d}{day:02d}_02"

    # 发票日期: DD-Mon-YY 格式
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
              'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    invoice_date = f"{day:02d}-{months[month-1]}-{year%100:02d}"

    # 计费周期: 01 Mon YYYY To DD Mon YYYY
    from calendar import monthrange
    last_day = monthrange(year, month)[1]
    billing_period = f"01 {months[month-1]} {year} To {last_day} {months[month-1]} {year}"

    return {
        "invoice_num": invoice_num,
        "invoice_date": invoice_date,
        "billing_period": billing_period,
        "year": year,
        "month": month,
        "day": day
    }

def generate_pdf():
    """生成PDF发票"""

    # 创建输出目录
    OUTPUT_DIR.mkdir(exist_ok=True)

    print("🚀 开始生成发票...")

    # 检查模板文件
    if not TEMPLATE_PATH.exists():
        print(f"❌ 错误：找不到模板文件 {TEMPLATE_PATH}")
        return False

    # 获取发票信息
    invoice_info = get_invoice_info()
    print(f"📋 发票信息:")
    print(f"   号码: {invoice_info['invoice_num']}")
    print(f"   日期: {invoice_info['invoice_date']}")
    print(f"   周期: {invoice_info['billing_period']}")

    try:
        # 加载Excel模板
        print("📂 加载Excel模板...")
        wb = load_workbook(TEMPLATE_PATH)
        ws = wb.active

        # 修改三个关键字段
        print("✏️  修改发票字段...")

        # H10: 发票日期
        ws['H10'] = invoice_info['invoice_date']
        print(f"   H10 (DATE): {invoice_info['invoice_date']}")

        # H11: 发票号
        ws['H11'] = invoice_info['invoice_num']
        print(f"   H11 (INVOICE #): {invoice_info['invoice_num']}")

        # B21: 计费周期
        ws['B21'] = invoice_info['billing_period']
        print(f"   B21 (BILLING PERIOD): {invoice_info['billing_period']}")

        # 保存临时Excel文件
        print(f"💾 保存临时Excel文件: {OUTPUT_EXCEL}")
        wb.save(OUTPUT_EXCEL)

        # 转换Excel为PDF (使用LibreOffice)
        print("🔄 转换Excel为PDF...")
        result = subprocess.run(
            [
                'libreoffice',
                '--headless',
                '--convert-to', 'pdf',
                '--outdir', str(OUTPUT_DIR),
                str(OUTPUT_EXCEL)
            ],
            capture_output=True,
            text=True,
            timeout=30
        )

        if result.returncode != 0:
            print(f"❌ LibreOffice转换失败: {result.stderr}")
            return False

        # 重命名PDF文件为标准名称
        generated_pdf = OUTPUT_DIR / "temp_invoice.pdf"
        if generated_pdf.exists():
            generated_pdf.rename(OUTPUT_PDF)
            print(f"✅ PDF生成成功: {OUTPUT_PDF}")
        else:
            print(f"❌ 错误：PDF文件生成失败")
            return False

        # 清理临时文件
        if OUTPUT_EXCEL.exists():
            try:
                OUTPUT_EXCEL.unlink()
            except Exception:
                pass  # 忽略删除失败

        print("✨ 发票PDF已生成！")
        return True

    except Exception as e:
        print(f"❌ 生成失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = generate_pdf()
    exit(0 if success else 1)
