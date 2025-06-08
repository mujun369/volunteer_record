"""
Vercel 部署入口点
"""
import os
import sys
import logging
from flask import Flask, request, jsonify, send_file, render_template
import sqlite3
from io import BytesIO
import xlsxwriter
from datetime import datetime
from flask_cors import CORS

# 添加项目根目录到 Python 路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 尝试导入应用
try:
    from app_lite import app, init_db
except ImportError:
    # 如果导入失败，创建一个最小化的应用
    app = Flask(__name__, 
                template_folder=os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'templates'))
    CORS(app)
    
    # 初始化数据库
    def init_db():
        conn = sqlite3.connect('volunteer_points.db')
        c = conn.cursor()
        
        # 创建志愿者积分表
        c.execute('''
        CREATE TABLE IF NOT EXISTS volunteer_points (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            activity_type TEXT,
            activity_time_name TEXT,
            category TEXT,
            name TEXT,
            score INTEGER
        )
        ''')
        
        # 创建志愿者积分使用情况表
        c.execute('''
        CREATE TABLE IF NOT EXISTS volunteer_usage (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            usage_description TEXT,
            score INTEGER
        )
        ''')
        
        conn.commit()
        conn.close()
    
    # 添加基本路由
    @app.route('/')
    def index():
        return render_template('volunteer_points_platform.html')
    
    @app.route('/health')
    def health():
        return jsonify({"status": "healthy"}), 200

# 初始化数据库
try:
    init_db()
except Exception as e:
    print(f"Database initialization error: {str(e)}")

# 导出应用实例供 Vercel 使用
application = app