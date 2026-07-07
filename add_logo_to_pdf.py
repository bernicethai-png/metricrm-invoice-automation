#!/usr/bin/env python3
"""
在生成的PDF中添加Webbalances Logo
"""

import os
from pathlib import Path
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from PyPDF2 import PdfMerger, PdfReader, PdfWriter
from io import BytesIO
from PIL import Image

def add_logo_to_pdf(input_pdf, logo_image, output_pdf):
    """在PDF左上角添加Logo"""

    print(f"📎 添加Logo到PDF...")

    try:
        # 1. 读取原始PDF的第一页，获取尺寸
        reader = PdfReader(input_pdf)
        first_page = reader.pages[0]
        page_width = float(first_page.mediabox.width)
        page_height = float(first_page.mediabox.height)

        print(f"   页面尺寸: {page_width}x{page_height}")

        # 2. 创建包含Logo的新PDF（透明背景）
        logo_pdf_buffer = BytesIO()
        c = canvas.Canvas(logo_pdf_buffer, pagesize=(page_width, page_height))

        # 打开Logo图片
        img = Image.open(logo_image)
        logo_width = 0.8 * inch  # Logo宽度80像素
        logo_height = (logo_width * img.height) / img.width  # 保持宽高比

        # 在左上角添加Logo（留一点margin）
        margin = 0.3 * inch
        c.drawImage(
            logo_image,
            margin,
            page_height - margin - logo_height,
            width=logo_width,
            height=logo_height,
            preserveAspectRatio=True
        )

        c.save()
        logo_pdf_buffer.seek(0)

        # 3. 读取Logo PDF
        logo_reader = PdfReader(logo_pdf_buffer)
        logo_page = logo_reader.pages[0]

        # 4. 将Logo页面合并到原始PDF的第一页
        writer = PdfWriter()

        # 处理第一页（添加Logo）
        first_page.merge_page(logo_page)
        writer.add_page(first_page)

        # 添加其余页面
        for page in reader.pages[1:]:
            writer.add_page(page)

        # 5. 保存输出PDF
        with open(output_pdf, 'wb') as out_file:
            writer.write(out_file)

        print(f"   ✅ Logo已添加: {output_pdf}")
        return True

    except Exception as e:
        print(f"   ❌ 添加Logo失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    # 配置
    OUTPUT_DIR = Path(__file__).parent / "output"
    INPUT_PDF = OUTPUT_DIR / "output_invoice.pdf"
    LOGO_IMAGE = Path(__file__).parent / "logo.png"
    OUTPUT_PDF = OUTPUT_DIR / "output_invoice_with_logo.pdf"

    if not INPUT_PDF.exists():
        print(f"❌ 输入PDF不存在: {INPUT_PDF}")
        exit(1)

    if not LOGO_IMAGE.exists():
        print(f"❌ Logo图片不存在: {LOGO_IMAGE}")
        exit(1)

    if add_logo_to_pdf(INPUT_PDF, LOGO_IMAGE, OUTPUT_PDF):
        # 用带Logo的PDF替换原始PDF
        os.replace(OUTPUT_PDF, INPUT_PDF)
        print(f"✅ PDF已更新: {INPUT_PDF}")
        exit(0)
    else:
        exit(1)
