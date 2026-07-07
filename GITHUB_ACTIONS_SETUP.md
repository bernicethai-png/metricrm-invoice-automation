# GitHub Actions 云端自动化设置指南

这个指南会帮你在GitHub Actions上设置完全自动化的发票生成、Dropbox保存和email发送系统。

## 📋 概览

```
GitHub Actions (云端) 
   ↓
每月3号 11:30 (马来西亚时间)
   ↓
自动生成发票 → 上传Dropbox → 发送email
   ↓
完成！电脑不用开着
```

## 🚀 设置步骤

### 第1步：创建GitHub仓库

1. 访问 https://github.com/new
2. 创建新仓库，名称：`metricrm-invoice-automation`
3. 选择 "Public" 或 "Private"
4. 点击 "Create repository"

### 第2步：上传代码到GitHub

在你的电脑上：

```bash
# 进入项目目录
cd ~/Claude/Projects/MetriCRM\ Auto\ Invoice

# 初始化Git仓库
git init

# 添加GitHub远程
git remote add origin https://github.com/YOUR_USERNAME/metricrm-invoice-automation.git

# 添加所有文件
git add .

# 提交
git commit -m "Initial commit: MetriCRM invoice automation"

# 推送到GitHub
git branch -M main
git push -u origin main
```

### 第3步：获取必要的Token和密钥

#### A. Dropbox Token

1. 访问 https://www.dropbox.com/developers/apps
2. 点击 "Create app"
3. 选择：
   - **API** → Scoped access
   - **Type of access** → App folder
   - **App name** → MetriCRM Invoice
4. 创建后，在 "Settings" 标签下生成 "Access token"
5. **保存这个token**（稍后需要）

#### B. Gmail App Password

1. 访问 https://myaccount.google.com/security
2. 启用 "2-Step Verification"（如果还没启用）
3. 在 "App passwords" 生成一个新密码
4. 选择 "Mail" 和 "Windows Computer"
5. **保存这个密码**

### 第4步：添加Secrets到GitHub

1. 进入你的GitHub仓库
2. 点击 "Settings" → "Secrets and variables" → "Actions"
3. 点击 "New repository secret"，添加以下三个secrets：

| Name | Value |
|------|-------|
| `DROPBOX_TOKEN` | 你的Dropbox token |
| `GMAIL_USER` | bernice@webbalances.com |
| `GMAIL_PASSWORD` | Gmail app password |

### 第5步：配置工作流时间

编辑 `.github/workflows/invoice.yml`：

- **当前设置**：每月3号 03:30 UTC（马来西亚 11:30）
- **如需修改**：改 `cron` 值

Cron格式：`分 小时 日 月 星期`

例子：
- `30 3 3 * *` = 每月3号 11:30 马来西亚时间 ✓ （现在的设置）
- `0 2 3 * *` = 每月3号 10:00 马来西亚时间
- `0 8 3 * *` = 每月3号 16:00 马来西亚时间

### 第6步：测试工作流

1. 进入GitHub仓库
2. 点击 "Actions" 标签
3. 选择 "MetriCRM Monthly Invoice"
4. 点击 "Run workflow" → "Run workflow"
5. 等待执行完成（通常2-3分钟）

**检查结果：**
- ✅ 绿色勾 = 成功
- ❌ 红色叉 = 失败

如果失败，点击job查看错误日志。

## 📧 邮件配置说明

**发件人**：bernice@webbalances.com
**收件人**：finance-i@invite.my
**BCC**：
- balon.goh@webbalances.com
- janet@netregy.com
- jimmy@invite.my
- deric@netregy.com
- qi_91@hotmail.com

**邮件内容**：
- 主题：根据月份自动生成（如 "Monthly Invoice - July 2026"）
- 正文：MetriCRM invoice通知
- 附件：生成的PDF发票
- 签名：Bernice Thai 的完整签名

## 🔧 故障排除

### 邮件发送失败

**问题**：`smtplib.SMTPAuthenticationError`

**解决**：
1. 确认 Gmail app password 正确
2. 确认已启用 2-Step Verification
3. 检查GitHub Secrets中的密码没有多余空格

### Dropbox上传失败

**问题**：`Invalid access token`

**解决**：
1. 检查Dropbox token是否正确
2. 确认token还未过期
3. 在Dropbox文件夹中手动创建路径：
   `/Dropbox/Webbalances/Customer_Account/Invite&Netergy/MetriCRM/`

### 工作流没有运行

**问题**：定时任务没有触发

**解决**：
1. 确认仓库至少有一次commit到main分支
2. GitHub Actions需要仓库有activity才会激活cron
3. 如果长时间没activity，cron可能被禁用
4. 手动运行workflow来测试

## 📊 监控和日志

每次运行后都可以查看：

1. GitHub Actions → "MetriCRM Monthly Invoice"
2. 点击最新的workflow run
3. 展开 "Upload to Dropbox and Send Email" 
4. 查看控制台输出

## 🎯 完成后的行为

✅ **自动化流程：**
- 每月3号 11:30 自动执行
- 查找已生成的PDF发票
- 上传到Dropbox（自动编号：66, 67, 68...）
- 发送email到finance-i@invite.my
- BCC给5个人
- 包含完整签名
- 电脑完全不用开

## 💡 注意事项

1. **发票必须先生成**：脚本查找已生成的PDF，不会自己生成
   - 如需自动生成，需要额外配置
   
2. **Gmail限制**：Gmail每小时最多100封邮件
   - 对于月度任务足够
   
3. **时区**：Cron使用UTC，已配置为马来西亚时间11:30

4. **成本**：GitHub Actions免费用户每月有2000分钟额度
   - 这个任务每次不到1分钟
   - 足够用

## 📞 需要帮助？

如果出现问题：
1. 查看GitHub Actions日志
2. 检查所有Secrets是否正确
3. 确认Dropbox和Gmail账户可以访问
4. 尝试手动运行workflow测试

---

**设置完成！🎉** 

现在你的发票系统完全在云端运行，无需电脑开着！
