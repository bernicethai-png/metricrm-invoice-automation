# 自动发票生成设置

## 功能
每个月的第3天早上11:30自动生成发票，并保存到：
`/Users/bernice_thai/Desktop/Others/MetriCRM Pending payment/`

## 安装步骤

### 1. 复制LaunchAgent配置文件
```bash
cp ~/Claude/Projects/MetriCRM\ Auto\ Invoice/com.metricrm.invoice.generator.plist ~/Library/LaunchAgents/
```

### 2. 加载任务
```bash
launchctl load ~/Library/LaunchAgents/com.metricrm.invoice.generator.plist
```

### 3. 验证安装
```bash
launchctl list | grep metricrm
```

## 使用

### 手动运行脚本
```bash
python3 ~/Claude/Projects/MetriCRM\ Auto\ Invoice/auto_invoice_generator.py
```

### 查看日志
- 成功日志：`~/Library/Logs/metricrm_invoice.log`
- 错误日志：`~/Library/Logs/metricrm_invoice_error.log`

### 卸载任务
```bash
launchctl unload ~/Library/LaunchAgents/com.metricrm.invoice.generator.plist
```

## 工作原理

1. ✅ 每月第7天早上9:00触发
2. ✅ 检查现有PDF发票
3. ✅ 自动复制到桌面指定路径
4. ✅ 日志记录所有操作

## 自定义

可以编辑 `com.metricrm.invoice.generator.plist` 修改：
- **Hour**：运行时间（小时，24小时格式）
- **Minute**：运行时间（分钟）
- **Day**：运行日期（修改为其他日期）

## 注意事项

- 该脚本依赖于现有的PDF文件生成
- 需要确保 `/Users/bernice_thai/Desktop/Others/MetriCRM Pending payment/` 目录有写入权限
- 日志文件会自动创建在 `~/Library/Logs/` 目录中
