"""
Vercel API入口点 - 导入并重导出app.py中的功能
"""
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 导入app.py中的所有内容
from app import app as application

# 导出Flask应用实例供Vercel使用
app = application
