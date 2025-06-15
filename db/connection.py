"""
数据库连接管理模块
"""
import time
import logging
from contextlib import contextmanager
from config import config

logger = logging.getLogger(__name__)

# 内存数据存储
if config.DB_MODE == 'memory':
    volunteer_data = []
    usage_data = []

# PostgreSQL连接池
connection_pool = None
if config.DB_MODE == 'postgres':
    try:
        import psycopg2
        from psycopg2 import pool
        
        # 创建连接池
        connection_pool = psycopg2.pool.SimpleConnectionPool(
            config.DB_POOL_MIN, 
            config.DB_POOL_MAX, 
            config.DATABASE_URL
        )
        logger.info("PostgreSQL连接池创建成功")
    except Exception as e:
        logger.error(f"PostgreSQL连接池创建失败: {str(e)}")
        connection_pool = None

@contextmanager
def get_db_connection():
    """获取数据库连接的上下文管理器"""
    conn = None
    retries = 0
    
    while retries < config.MAX_RETRIES:
        try:
            if config.DB_MODE == 'memory':
                # 内存模式返回字典
                yield {'volunteer_data': volunteer_data, 'usage_data': usage_data}
                return
            elif config.DB_MODE == 'sqlite':
                # SQLite连接
                import sqlite3
                conn = sqlite3.connect(config.SQLITE_DB_PATH)
                conn.row_factory = sqlite3.Row  # 使结果可以通过列名访问
                yield conn
                conn.close()
                return
            elif config.DB_MODE == 'postgres':
                # PostgreSQL连接
                if connection_pool:
                    conn = connection_pool.getconn()
                else:
                    # 如果连接池创建失败，尝试直接连接
                    import psycopg2
                    logger.warning("使用直接连接而非连接池")
                    conn = psycopg2.connect(config.DATABASE_URL)
                yield conn
                if connection_pool and conn:
                    connection_pool.putconn(conn)
                else:
                    conn.close()
                return
        except Exception as e:
            retries += 1
            logger.error(f"数据库连接尝试 {retries} 失败: {str(e)}")
            if conn:
                try:
                    if config.DB_MODE == 'postgres' and connection_pool and conn:
                        connection_pool.putconn(conn)
                    else:
                        conn.close()
                except Exception as close_error:
                    logger.error(f"关闭数据库连接失败: {str(close_error)}")
            
            if retries < config.MAX_RETRIES:
                logger.info(f"{config.RETRY_DELAY} 秒后重试...")
                time.sleep(config.RETRY_DELAY)
            else:
                logger.error("达到最大重试次数。无法连接到数据库。")
                raise

def close_db_connections():
    """关闭所有数据库连接"""
    if config.DB_MODE == 'postgres' and connection_pool:
        connection_pool.closeall()
        logger.info("已关闭所有PostgreSQL连接")