import os
import logging
import psycopg2
from psycopg2 import pool

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 数据库连接信息
DATABASE_URL = os.environ.get('DATABASE_URL')

# 创建连接池
try:
    connection_pool = psycopg2.pool.SimpleConnectionPool(
        1, 10, DATABASE_URL
    )
    logger.info("Database connection pool created successfully")
except Exception as e:
    logger.error(f"Error creating connection pool: {str(e)}")
    connection_pool = None

def get_db_connection():
    """从连接池获取数据库连接"""
    if connection_pool:
        return connection_pool.getconn()
    else:
        # 如果连接池创建失败，尝试直接连接
        logger.warning("Using direct connection instead of connection pool")
        return psycopg2.connect(DATABASE_URL)

def release_db_connection(conn):
    """将连接归还到连接池"""
    if connection_pool and conn:
        connection_pool.putconn(conn)

def init_db():
    """初始化数据库表"""
    conn = None
    try:
        # 获取连接
        conn = get_db_connection()
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
        
        # 提交更改
        conn.commit()
        logger.info("Database tables initialized successfully")
    except Exception as e:
        logger.error(f"Database initialization failed: {str(e)}")
        if conn:
            conn.rollback()
        raise
    finally:
        if cursor:
            cursor.close()
        if conn:
            release_db_connection(conn)