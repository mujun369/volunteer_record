# 志愿者积分记录平台

## 部署说明

### 本地开发

1. 安装依赖：
   ```
   pip install -r requirements.txt
   ```

2. 运行应用：
   ```
   python app_lite.py
   ```

3. 访问应用：
   ```
   http://localhost:5001
   ```

### Render 部署

1. 连接 GitHub 仓库到 Render
2. 创建新的 Web Service
3. 使用以下设置：
   - Build Command: `./build.sh`
   - Start Command: `./start.sh`

## 故障排除

如果部署失败，请检查以下内容：

1. 确保 `requirements.txt` 不包含 NumPy 或 Pandas
2. 检查 Render 日志中的错误信息
3. 访问 `/health` 端点检查应用状态