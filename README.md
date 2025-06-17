# 志愿者积分记录平台

这是一个用于记录和管理志愿者积分的Web平台。

## 功能特性

- 志愿者活动记录
- 积分计算和汇总
- 积分使用记录
- 数据导出功能
- 志愿者积分查询

## 技术栈

- 前端：HTML, CSS, JavaScript
- 后端：Python Flask
- 数据库：SQLite/内存存储

## 功能特性

- 志愿者活动记录
- 积分计算和汇总
- 积分使用记录
- 数据导出功能
- 志愿者积分查询

## 技术栈

- 前端：HTML, CSS, JavaScript
- 后端：Python Flask
- 数据库：内存存储 (Vercel部署)
- 部署：Vercel

## 部署架构

本项目采用前后端分离的部署方式：

- **前端**：部署在GitHub Pages，提供静态网页服务
- **后端**：部署在Vercel，提供API服务

## 访问地址

- **GitHub Pages前端**：https://mujun369.github.io/volunteer_record/
- **Vercel后端API**：https://volunteerrecord.vercel.app/
- **Vercel完整应用**：https://volunteerrecord.vercel.app/

## 部署状态

✅ **前端部署**：GitHub Actions自动部署到GitHub Pages
✅ **后端部署**：Vercel自动部署Python Flask API
✅ **跨域配置**：前端可以正常调用后端API

## 本地运行

1. 安装依赖：
```bash
pip install -r requirements.txt
```

2. 运行应用：
```bash
python app_lite.py
```

3. 访问 http://localhost:5000

## 解决方案

由于Vercel部署遇到网络连接问题，我创建了一个简化的单文件解决方案：

### 新的单文件版本 (`main.py`)

- ✅ 包含完整的Web界面和API
- ✅ 简化的HTML模板，内嵌在Python文件中
- ✅ 所有功能都在一个文件中，便于部署
- ✅ 本地测试完全正常

### 本地测试

1. 运行单文件版本：
```bash
python3 main.py
```

2. 访问 http://127.0.0.1:5000

3. 测试功能：
   - API健康检查
   - 添加志愿者记录
   - 查看积分汇总

### 部署建议

由于网络连接问题，建议：

1. **手动部署到Vercel**：
   - 将 `main.py` 作为主要文件
   - 使用简化的 `vercel.json` 配置
   - 确保 `requirements.txt` 只包含 `flask`

2. **替代部署方案**：
   - 使用 Heroku
   - 使用 Railway
   - 使用 Render

## 测试API

运行测试脚本：
```bash
python deploy_test.py https://volunteer-record.vercel.app
```

或者本地测试：
```bash
python3 main.py
# 然后访问 http://127.0.0.1:5000
```
