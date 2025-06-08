"""
最小化版本的 WSGI 入口点，用于测试部署
"""
import os
import logging
import sys
from app_minimal import app, init_db

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 记录系统信息
logger.info(f"Python version: {sys.version}")
logger.info(f"Working directory: {os.getcwd()}")
logger.info(f"Directory contents: {os.listdir('.')}")

# 初始化数据库
try:
    logger.info("Initializing minimal database")
    init_db()
    logger.info("Minimal database initialization successful")
except Exception as e:
    logger.error(f"Minimal database initialization failed: {str(e)}")
    import traceback
    logger.error(traceback.format_exc())

# 应用实例
application = app

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5001))
    logger.info(f"Starting minimal application on port {port}")
    application.run(host='0.0.0.0', port=port)