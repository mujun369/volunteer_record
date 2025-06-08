"""
静态文件服务
"""
import os
from flask import Flask, send_from_directory
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# 获取项目根目录
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
template_dir = os.path.join(root_dir, 'templates')

@app.route('/<path:path>')
def serve_static(path):
    logger.info(f"Serving static file: {path}")
    return send_from_directory(template_dir, path)

@app.route('/')
def index():
    logger.info("Serving index.html")
    return send_from_directory(template_dir, 'volunteer_points_platform.html')