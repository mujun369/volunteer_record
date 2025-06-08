"""
最小化版本的应用，用于测试部署
"""
from flask import Flask, jsonify
import os
import sys
import logging
from datetime import datetime

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# 初始化数据库（简化版）
def init_db():
    logger.info("Minimal database initialization (no-op)")
    return True

@app.route('/')
def index():
    return "Volunteer Points Platform - Minimal Version"

@app.route('/health')
def health_check():
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "python_version": sys.version,
        "flask_version": Flask.__version__
    })

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5001))
    logger.info(f"Starting minimal application on port {port}")
    app.run(host='0.0.0.0', port=port)