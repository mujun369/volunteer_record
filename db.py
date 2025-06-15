import os
import logging
import sqlite3
import time
from contextlib import contextmanager

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 数据库模式：'sqlite', 'postgres', 'memory'
DB_MODE = os.environ.get('DB_MODE', 'sqlite')
logger.info(f"使用数据库模式: {DB_MODE}")

# 数据库连接信息
DATABASE_URL = os.environ.get('DATABASE_URL')
SQLITE_DB_PATH = os.environ.get('DB_PATH', 'volunteer_points.db')

# 内存数据存储
if DB_MODE == 'memory':
    volunteer_data = []
    usage_data = []

# 连接重试设置
MAX_RETRIES = 3
RETRY_DELAY = 1  # 秒

# PostgreSQL连接池
if DB_MODE == 'postgres':
    try:
        import psycopg2
        from psycopg2 import pool
        
        # 创建连接池
        connection_pool = psycopg2.pool.SimpleConnectionPool(
            1, 10, DATABASE_URL
        )
        logger.info("Database connection pool created successfully")
    except Exception as e:
        logger.error(f"Error creating connection pool: {str(e)}")
        connection_pool = None

@contextmanager
def get_db_connection():
    """获取数据库连接的上下文管理器"""
    conn = None
    retries = 0
    
    while retries < MAX_RETRIES:
        try:
            if DB_MODE == 'memory':
                # 内存模式返回字典
                yield {'volunteer_data': volunteer_data, 'usage_data': usage_data}
                return
            elif DB_MODE == 'sqlite':
                # SQLite连接
                conn = sqlite3.connect(SQLITE_DB_PATH)
                cursor = conn.cursor()
                # 初始化表（首次运行时创建）
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS volunteers (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL,
                        points INTEGER DEFAULT 0
                    )
                ''')
                conn.commit()
                yield conn
                conn.close()
                return
            elif DB_MODE == 'postgres':
                # PostgreSQL连接
                if connection_pool:
                    conn = connection_pool.getconn()
                else:
                    # 如果连接池创建失败，尝试直接连接
                    logger.warning("Using direct connection instead of connection pool")
                    conn = psycopg2.connect(DATABASE_URL)
                yield conn
                if connection_pool and conn:
                    connection_pool.putconn(conn)
                else:
                    conn.close()
                return
        except Exception as e:
            retries += 1
            logger.error(f"Database connection attempt {retries} failed: {str(e)}")
            if conn:
                try:
                    if DB_MODE == 'postgres' and connection_pool and conn:
                        connection_pool.putconn(conn)
                    else:
                        conn.close()
                except:
                    pass
            
            if retries < MAX_RETRIES:
                logger.info(f"Retrying in {RETRY_DELAY} seconds...")
                time.sleep(RETRY_DELAY)
            else:
                logger.error("Max retries reached. Could not connect to database.")
                raise

def init_db():
    """初始化数据库表"""
    try:
        with get_db_connection() as conn:
            if DB_MODE == 'memory':
                logger.info("内存数据库初始化成功")
                return True
            elif DB_MODE == 'sqlite':
                cursor = conn.cursor()
                
                # 创建志愿者积分表
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS volunteer_points (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        activity_type TEXT,
                        activity_time_name TEXT,
                        category TEXT,
                        name TEXT,
                        score TEXT
                    )
                ''')
                
                # 创建志愿者积分使用情况表
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS volunteer_usage (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        volunteer_id INTEGER NOT NULL,
                        used_points INTEGER NOT NULL,
                        course_name TEXT NOT NULL,
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (volunteer_id) REFERENCES volunteers(id)
                    )
                ''')
                conn.commit()
                logger.info("SQLite数据库初始化成功")
                return True
            elif DB_MODE == 'postgres':
                cursor = conn.cursor()
                
                # 创建志愿者积分表
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS volunteer_points (
                        id SERIAL PRIMARY KEY,
                        activity_type TEXT,
                        activity_time_name TEXT,
                        category TEXT,
                        name TEXT,
                        score TEXT
                    )
                ''')
                
                # 创建志愿者积分使用情况表
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS volunteer_usage (
                        id SERIAL PRIMARY KEY,
                        name TEXT UNIQUE,
                        total_points INTEGER DEFAULT 0,
                        used_points INTEGER DEFAULT 0,
                        course_count INTEGER DEFAULT 0
                    )
                ''')
                
                conn.commit()
                logger.info("PostgreSQL数据库初始化成功")
                return True
    except Exception as e:
        logger.error(f"数据库初始化失败: {str(e)}")
        return False

def health_check():
    """检查数据库连接健康状态"""
    try:
        with get_db_connection() as conn:
            if DB_MODE == 'memory':
                # 内存模式直接返回健康状态
                return True, "内存数据库正常"
            elif DB_MODE == 'sqlite':
                cursor = conn.cursor()
                cursor.execute("SELECT 1")
                return True, "SQLite数据库连接正常"
            elif DB_MODE == 'postgres':
                cursor = conn.cursor()
                cursor.execute("SELECT 1")
                return True, "PostgreSQL数据库连接正常"
    except Exception as e:
        return False, f"数据库连接异常: {str(e)}"
