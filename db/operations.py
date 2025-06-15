"""
数据库操作模块
"""
import logging
from db.connection import get_db_connection
from config import config

logger = logging.getLogger(__name__)

def init_db():
    """初始化数据库表"""
    try:
        with get_db_connection() as conn:
            if config.DB_MODE == 'memory':
                logger.info("内存数据库初始化成功")
                return True
            elif config.DB_MODE == 'sqlite':
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
                        name TEXT UNIQUE,
                        total_points INTEGER DEFAULT 0,
                        used_points INTEGER DEFAULT 0,
                        course_count INTEGER DEFAULT 0
                    )
                ''')
                
                conn.commit()
                logger.info("SQLite数据库初始化成功")
                return True
            elif config.DB_MODE == 'postgres':
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
            if config.DB_MODE == 'memory':
                # 内存模式直接返回健康状态
                return True, "内存数据库正常"
            elif config.DB_MODE == 'sqlite':
                cursor = conn.cursor()
                cursor.execute("SELECT 1")
                return True, "SQLite数据库连接正常"
            elif config.DB_MODE == 'postgres':
                cursor = conn.cursor()
                cursor.execute("SELECT 1")
                return True, "PostgreSQL数据库连接正常"
    except Exception as e:
        return False, f"数据库连接异常: {str(e)}"

def add_volunteer_points(activity_data):
    """添加志愿者积分记录"""
    try:
        with get_db_connection() as conn:
            if config.DB_MODE == 'memory':
                # 内存模式
                from db.connection import volunteer_data
                for row in activity_data:
                    if len(row) == 5:
                        volunteer_data.append(row)
                    elif len(row) == 4:
                        volunteer_data.append(['线下活动'] + row)
                return True
            elif config.DB_MODE == 'sqlite':
                cursor = conn.cursor()
                for row in activity_data:
                    if len(row) == 5:
                        cursor.execute('''
                            INSERT INTO volunteer_points (activity_type, activity_time_name, category, name, score)
                            VALUES (?,?,?,?,?)
                        ''', row)
                    elif len(row) == 4:
                        cursor.execute('''
                            INSERT INTO volunteer_points (activity_type, activity_time_name, category, name, score)
                            VALUES (?,?,?,?,?)
                        ''', ['线下活动'] + row)
                conn.commit()
                return True
            elif config.DB_MODE == 'postgres':
                cursor = conn.cursor()
                for row in activity_data:
                    if len(row) == 5:
                        cursor.execute('''
                            INSERT INTO volunteer_points (activity_type, activity_time_name, category, name, score)
                            VALUES (%s, %s, %s, %s, %s)
                        ''', row)
                    elif len(row) == 4:
                        cursor.execute('''
                            INSERT INTO volunteer_points (activity_type, activity_time_name, category, name, score)
                            VALUES (%s, %s, %s, %s, %s)
                        ''', ['线下活动'] + row)
                conn.commit()
                return True
    except Exception as e:
        logger.error(f"添加志愿者积分记录失败: {str(e)}")
        return False

def get_volunteer_summary():
    """获取志愿者积分汇总"""
    try:
        with get_db_connection() as conn:
            if config.DB_MODE == 'memory':
                # 内存模式
                from db.connection import volunteer_data
                # 按名字分组并累加积分
                summary = {}
                for row in volunteer_data:
                    name = row[3]  # 名字在第4个位置
                    score = int(row[4])  # 积分在第5个位置
                    if name in summary:
                        summary[name] += score
                    else:
                        summary[name] = score
                
                # 转换为列表格式
                return [{"name": name, "total_score": score} for name, score in summary.items()]
            elif config.DB_MODE == 'sqlite':
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT name, SUM(CAST(score AS INTEGER)) as total_score
                    FROM volunteer_points
                    GROUP BY name
                    ORDER BY name
                ''')
                data = cursor.fetchall()
                
                # 转换为字典格式
                return [dict(row) for row in data]
            elif config.DB_MODE == 'postgres':
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT name, SUM(CAST(score AS INTEGER)) as total_score
                    FROM volunteer_points
                    GROUP BY name
                    ORDER BY name
                ''')
                data = cursor.fetchall()
                
                # 转换为字典格式
                return [{"name": row[0], "total_score": row[1]} for row in data]
    except Exception as e:
        logger.error(f"获取志愿者积分汇总失败: {str(e)}")
        return []