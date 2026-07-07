# MetriCRM 自动发票生成系统

## 📋 概述

每个月的第3天早上11:30，系统将**自动生成发票**并**保存到指定的桌面路径**：
```
/Users/bernice_thai/Desktop/Others/MetriCRM Pending payment/
```

## 🚀 快速开始

### 一键安装（推荐）

```bash
bash ~/Claude/Projects/MetriCRM\ Auto\ Invoice/install_auto_invoice.sh
```

完成！系统会：
- ✅ 配置自动任务
- ✅ 每月第3天早上11:30自动运行
- ✅ 自动复制发票到桌面指定位置

### 手动验证安装

```bash
# 查看已加载的任务
launchctl list | grep metricrm

# 查看成功日志
cat ~/Library/Logs/metricrm_invoice.log

# 查看错误日志
cat ~/Library/Logs/metricrm_invoice_error.log
```

## 📁 文件说明

| 文件 | 说明 |
|------|------|
| `auto_invoice_generator.py` | 核心脚本，负责生成和复制发票 |
| `com.metricrm.invoice.generator.plist` | macOS 任务调度配置文件 |
| `install_auto_invoice.sh` | 自动安装脚本 |
| `SETUP_AUTO_INVOICE.md` | 详细设置说明 |

## 🔧 工作原理

```
每月第3天 11:30
    ↓
系统触发 LaunchAgent
    ↓
运行 Python 脚本
    ↓
查找今天生成的PDF发票
    ↓
复制到 Desktop/Others/MetriCRM Pending payment/
    ↓
记录日志
```

## 📝 自定义设置

### 修改触发时间

编辑 `com.metricrm.invoice.generator.plist`：

```xml
<key>StartCalendarInterval</key>
<array>
  <dict>
    <key>Day</key>
    <integer>7</integer>        <!-- 修改日期 -->
    <key>Hour</key>
    <integer>9</integer>        <!-- 修改小时 (0-23) -->
    <key>Minute</key>
    <integer>0</integer>        <!-- 修改分钟 (0-59) -->
  </dict>
</array>
```

然后重新加载：
```bash
launchctl unload ~/Library/LaunchAgents/com.metricrm.invoice.generator.plist
launchctl load ~/Library/LaunchAgents/com.metricrm.invoice.generator.plist
```

### 每天运行（所有日期）

```xml
<key>StartCalendarInterval</key>
<array>
  <dict>
    <key>Hour</key>
    <integer>9</integer>
    <key>Minute</key>
    <integer>0</integer>
  </dict>
</array>
```

## 🛠️ 疑难排除

### 脚本没有运行

1. **检查任务是否已加载**
   ```bash
   launchctl list | grep metricrm
   ```
   
2. **查看错误日志**
   ```bash
   tail -f ~/Library/Logs/metricrm_invoice_error.log
   ```

3. **手动测试脚本**
   ```bash
   python3 ~/Claude/Projects/MetriCRM\ Auto\ Invoice/auto_invoice_generator.py
   ```

### 权限问题

确保以下目录有写入权限：
- `~/Desktop/Others/MetriCRM Pending payment/`
- `~/Library/Logs/`

```bash
# 检查权限
ls -ld ~/Desktop/Others/MetriCRM\ Pending\ payment/

# 如果需要，修复权限
chmod 755 ~/Desktop/Others/MetriCRM\ Pending\ payment/
```

### PDF文件找不到

脚本会自动查找：
1. 项目根目录中的 `WB_INV_YYMMDD_01.pdf`
2. 月份文件夹中的 `WB_INV_YYMMDD_01.pdf`（例：July 2026）
3. 任何子目录中的匹配文件

确保发票PDF已生成并保存在这些位置之一。

## 📧 卸载

如果需要停止自动发票生成：

```bash
launchctl unload ~/Library/LaunchAgents/com.metricrm.invoice.generator.plist
```

重新启用：

```bash
launchctl load ~/Library/LaunchAgents/com.metricrm.invoice.generator.plist
```

## 📞 支持

有任何问题，请检查：
- 日志文件：`~/Library/Logs/metricrm_invoice*`
- 手动运行脚本以测试
- 确认PDF文件已正确生成
- 检查目录权限

---

**最后更新**：2026年7月7日
