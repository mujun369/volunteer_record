"""
WSGI 入口点文件
用于 Render 和其他 WSGI 服务器
"""
import os
import logging
from app import app, init_db

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 初始化数据库
try:
    logger.info("Initializing database from WSGI entry point")
    init_db()
    logger.info("Database initialization successful")
except Exception as e:
    logger.error(f"Database initialization failed: {str(e)}")

# 应用实例
application = app

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5001))
    logger.info(f"Starting application on port {port}")
    application.run(host='0.0.0.0', port=port)