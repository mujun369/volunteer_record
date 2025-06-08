"""
测试脚本，用于验证应用是否可以正常启动
"""
import os
import sys
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_imports():
    """测试所有必要的导入"""
    try:
        import flask
        logger.info(f"Flask version: {flask.__version__}")
        
        from flask import Flask, request, jsonify, send_file, render_template
        logger.info("Flask components imported successfully")
        
        import sqlite3
        logger.info(f"SQLite version: {sqlite3.sqlite_version}")
        
        from io import BytesIO
        logger.info("BytesIO imported successfully")
        
        import xlsxwriter
        logger.info(f"XlsxWriter version: {xlsxwriter.__version__}")
        
        from datetime import datetime
        logger.info("datetime imported successfully")
        
        from flask_cors import CORS
        logger.info("Flask-CORS imported successfully")
        
        return True
    except ImportError as e:
        logger.error(f"Import error: {str(e)}")
        return False

def test_flask_app():
    """测试创建一个简单的 Flask 应用"""
    try:
        from flask import Flask
        app = Flask(__name__)
        
        @app.route('/test')
        def test():
            return "Test successful"
        
        logger.info("Flask app created successfully")
        return True
    except Exception as e:
        logger.error(f"Flask app creation error: {str(e)}")
        return False

def test_sqlite():
    """测试 SQLite 连接"""
    try:
        import sqlite3
        conn = sqlite3.connect(':memory:')
        c = conn.cursor()
        c.execute('CREATE TABLE test (id INTEGER PRIMARY KEY, name TEXT)')
        c.execute('INSERT INTO test VALUES (1, "test")')
        c.execute('SELECT * FROM test')
        result = c.fetchone()
        conn.close()
        
        logger.info(f"SQLite test result: {result}")
        return True
    except Exception as e:
        logger.error(f"SQLite error: {str(e)}")
        return False

if __name__ == "__main__":
    logger.info(f"Python version: {sys.version}")
    logger.info(f"Working directory: {os.getcwd()}")
    
    imports_ok = test_imports()
    flask_ok = test_flask_app()
    sqlite_ok = test_sqlite()
    
    if imports_ok and flask_ok and sqlite_ok:
        logger.info("All tests passed!")
        sys.exit(0)
    else:
        logger.error("Some tests failed!")
        sys.exit(1)