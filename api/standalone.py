"""
完全独立的简化版应用
不依赖任何其他模块
"""
import os
import json
import sqlite3
from datetime import datetime
from flask import Flask, request, jsonify, send_from_directory, render_template_string

# 创建应用
app = Flask(__name__)

# 数据库路径
DB_PATH = "/tmp/volunteer_points.db"

# 简单的HTML模板
SIMPLE_HTML = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>志愿者积分记录 - 简化版</title>
    <style>
        body { font-family: Arial; margin: 20px; }
        .container { max-width: 800px; margin: 0 auto; }
        table { width: 100%; border-collapse: collapse; }
        th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
        th { background-color: #f2f2f2; }
        button { padding: 8px 16px; margin: 10px 0; cursor: pointer; }
        .error { color: red; }
        .success { color: green; }
    </style>
</head>
<body>
    <div class="container">
        <h1>志愿者积分记录 - 简化版</h1>
        
        <div id="status"></div>
        
        <h2>添加积分记录</h2>
        <form id="point-form">
            <div>
                <label>活动名称：</label>
                <input type="text" id="activity" required>
            </div>
            <div>
                <label>类别：</label>
                <input type="text" id="category" required>
            </div>
            <div>
                <label>姓名：</label>
                <input type="text" id="name" required>
            </div>
            <div>
                <label>积分：</label>
                <input type="number" id="points" required>
            </div>
            <button type="submit">提交</button>
        </form>
        
        <h2>积分汇总</h2>
        <button id="refresh-btn">刷新数据</button>
        <table>
            <thead>
                <tr>
                    <th>姓名</th>
                    <th>总积分</th>
                </tr>
            </thead>
            <tbody id="summary-table">
                <!-- 数据将通过JavaScript填充 -->
            </tbody>
        </table>
    </div>

    <script>
        // 显示状态消息
        function showStatus(message, isError = false) {
            const statusDiv = document.getElementById('status');
            statusDiv.textContent = message;
            statusDiv.className = isError ? 'error' : 'success';
            
            // 3秒后清除消息
            setTimeout(() => {
                statusDiv.textContent = '';
                statusDiv.className = '';
            }, 3000);
        }
        
        // 提交表单
        document.getElementById('point-form').addEventListener('submit', function(e) {
            e.preventDefault();
            
            const activityData = [
                document.getElementById('activity').value,
                document.getElementById('category').value,
                document.getElementById('name').value,
                document.getElementById('points').value
            ];
            
            fetch('/api/submit', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ activityData: [activityData] })
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error(`服务器返回错误 (${response.status})`);
                }
                return response.json();
            })
            .then(data => {
                showStatus(data.message || '提交成功');
                document.getElementById('point-form').reset();
                loadSummary();
            })
            .catch(error => {
                console.error('提交失败:', error);
                showStatus(`提交失败: ${error.message}`, true);
            });
        });
        
        // 加载汇总数据
        function loadSummary() {
            fetch('/api/summary')
            .then(response => {
                if (!response.ok) {
                    throw new Error(`服务器返回错误 (${response.status})`);
                }
                return response.json();
            })
            .then(data => {
                const tableBody = document.getElementById('summary-table');
                tableBody.innerHTML = '';
                
                data.forEach(item => {
                    const row = document.createElement('tr');
                    
                    const nameCell = document.createElement('td');
                    nameCell.textContent = item.name;
                    row.appendChild(nameCell);
                    
                    const pointsCell = document.createElement('td');
                    pointsCell.textContent = item.total_points;
                    row.appendChild(pointsCell);
                    
                    tableBody.appendChild(row);
                });
            })
            .catch(error => {
                console.error('加载汇总数据失败:', error);
                showStatus(`加载汇总数据失败: ${error.message}`, true);
            });
        }
        
        // 刷新按钮
        document.getElementById('refresh-btn').addEventListener('click', loadSummary);
        
        // 页面加载时获取数据
        document.addEventListener('DOMContentLoaded', loadSummary);
    </script>
</body>
</html>
"""

# 初始化数据库
def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # 创建积分表
    c.execute('''
        CREATE TABLE IF NOT EXISTS volunteer_points (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            activity_time_name TEXT,
            category TEXT,
            name TEXT,
            score INTEGER,
            timestamp TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()

# 路由：主页
@app.route('/')
def index():
    return render_template_string(SIMPLE_HTML)

# 路由：提交积分
@app.route('/api/submit', methods=['POST'])
def submit():
    try:
        data = request.get_json()
        
        if not data or 'activityData' not in data:
            return jsonify({"message": "无效的数据格式"}), 400
        
        activity_data = data['activityData']
        
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        
        for row in activity_data:
            if len(row) != 4:
                return jsonify({"message": f"数据格式错误，每行应包含4个元素，实际包含{len(row)}个"}), 400
            
            activity, category, name, score = row
            
            try:
                score = int(score)
            except ValueError:
                return jsonify({"message": f"积分必须是数字，收到的值是：{score}"}), 400
            
            c.execute('''
                INSERT INTO volunteer_points (activity_time_name, category, name, score)
                VALUES (?, ?, ?, ?)
            ''', (activity, category, name, score))
        
        conn.commit()
        conn.close()
        
        return jsonify({"message": "提交成功"}), 200
    
    except Exception as e:
        return jsonify({"message": f"提交失败: {str(e)}"}), 500

# 路由：获取汇总数据
@app.route('/api/summary')
def get_summary():
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        
        c.execute('''
            SELECT name, SUM(score) as total_points
            FROM volunteer_points
            GROUP BY name
            ORDER BY total_points DESC
        ''')
        
        rows = c.fetchall()
        result = [dict(row) for row in rows]
        
        conn.close()
        
        return jsonify(result), 200
    
    except Exception as e:
        return jsonify({"message": f"获取汇总数据失败: {str(e)}"}), 500

# 路由：健康检查
@app.route('/health')
def health():
    try:
        # 检查数据库连接
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT 1")
        conn.close()
        
        return jsonify({
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "database": "connected",
            "db_path": DB_PATH
        }), 200
    
    except Exception as e:
        return jsonify({
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500

# 初始化数据库并启动应用
init_db()

# 导出应用实例供 Vercel 使用