"""
集中配置管理模块
"""
import os
import logging
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 基础配置
class BaseConfig:
    # 应用配置
    APP_NAME = "志愿者积分记录平台"
    APP_VERSION = "1.1.0"
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev_key_please_change_in_production")
    
    # 日志配置
    LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO")
    LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # 数据库配置
    DB_MODE = os.environ.get("DB_MODE", "sqlite")  # 'sqlite', 'postgres', 'memory'
    DATABASE_URL = os.environ.get("DATABASE_URL")
    SQLITE_DB_PATH = os.environ.get("DB_PATH", "volunteer_points.db")
    
    # 连接池配置
    DB_POOL_MIN = int(os.environ.get("DB_POOL_MIN", "1"))
    DB_POOL_MAX = int(os.environ.get("DB_POOL_MAX", "10"))
    
    # 重试配置
    MAX_RETRIES = int(os.environ.get("MAX_RETRIES", "3"))
    RETRY_DELAY = int(os.environ.get("RETRY_DELAY", "1"))  # 秒
    
    # API配置
    API_PREFIX = "/api"
    CORS_ORIGINS = os.environ.get("CORS_ORIGINS", "*").split(",")

# 开发环境配置
class DevelopmentConfig(BaseConfig):
    DEBUG = True
    TESTING = False

# 测试环境配置
class TestingConfig(BaseConfig):
    DEBUG = False
    TESTING = True
    DB_MODE = "memory"

# 生产环境配置
class ProductionConfig(BaseConfig):
    DEBUG = False
    TESTING = False
    LOG_LEVEL = "ERROR"
    DB_MODE = "postgres"  # 生产环境使用PostgreSQL
    DB_POOL_MIN = 2
    DB_POOL_MAX = 5

# 根据环境变量选择配置
def get_config():
    env = os.environ.get("FLASK_ENV", "development")
    configs = {
        "development": DevelopmentConfig,
        "testing": TestingConfig,
        "production": ProductionConfig
    }
    return configs.get(env, DevelopmentConfig)

# 当前配置
config = get_config()

# 配置日志
logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL),
    format=config.LOG_FORMAT
)
logger = logging.getLogger(__name__)
logger.info(f"加载配置: {config.__class__.__name__}")
logger.info(f"数据库模式: {config.DB_MODE}")