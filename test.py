"""
简单的测试脚本
"""
import os
import sqlite3
import tempfile

# 创建临时数据库
temp_db = tempfile.NamedTemporaryFile(delete=False)
temp_db.close()

# 设置环境变量
os.environ["DB_PATH"] = temp_db.name

# 导入应用
from api.standalone import app, init_db

# 初始化数据库
init_db()

# 创建测试客户端
client = app.test_client()

# 测试健康检查
response = client.get('/health')
print(f"Health check: {response.status_code}")
print(response.json)

# 测试提交数据
test_data = {
    "activityData": [
        ["测试活动", "测试类别", "测试用户", "10"]
    ]
}
response = client.post('/api/submit', json=test_data)
print(f"Submit: {response.status_code}")
print(response.json)

# 测试获取汇总数据
response = client.get('/api/summary')
print(f"Summary: {response.status_code}")
print(response.json)

# 清理
os.unlink(temp_db.name)
print("Tests completed")