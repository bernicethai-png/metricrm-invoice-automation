#!/bin/bash

# MetriCRM 自动发票生成 - 安装脚本

set -e  # 任何错误都会停止脚本

echo "🚀 开始安装 MetriCRM 自动发票生成..."
echo ""

# 定义路径
SCRIPT_DIR="$HOME/Claude/Projects/MetriCRM Auto Invoice"
PLIST_SOURCE="$SCRIPT_DIR/com.metricrm.invoice.generator.plist"
PLIST_DEST="$HOME/Library/LaunchAgents/com.metricrm.invoice.generator.plist"

# 1. 检查源文件是否存在
if [ ! -f "$PLIST_SOURCE" ]; then
    echo "❌ 错误：找不到plist文件"
    echo "   位置：$PLIST_SOURCE"
    exit 1
fi

echo "✓ 找到配置文件"

# 2. 创建 LaunchAgents 目录（如果不存在）
mkdir -p "$HOME/Library/LaunchAgents"
echo "✓ 确保 LaunchAgents 目录存在"

# 3. 复制plist文件
cp "$PLIST_SOURCE" "$PLIST_DEST"
echo "✓ 复制配置文件"

# 4. 加载 LaunchAgent
launchctl load "$PLIST_DEST"
echo "✓ 加载自动任务"

# 5. 验证安装
if launchctl list | grep -q "com.metricrm.invoice.generator"; then
    echo ""
    echo "✨ 安装成功！"
    echo ""
    echo "📋 任务详情："
    echo "   • 触发时间：每月第3天早上11:30"
    echo "   • 输出目录：$HOME/Desktop/Others/MetriCRM Pending payment/"
    echo "   • 日志文件："
    echo "     - 成功：$HOME/Library/Logs/metricrm_invoice.log"
    echo "     - 错误：$HOME/Library/Logs/metricrm_invoice_error.log"
    echo ""
    echo "💡 提示："
    echo "   • 卸载：launchctl unload $PLIST_DEST"
    echo "   • 手动运行：python3 $SCRIPT_DIR/auto_invoice_generator.py"
else
    echo "❌ 安装似乎失败，请检查权限"
    exit 1
fi
