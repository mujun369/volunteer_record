#!/bin/bash
set -e

echo "Starting application..."

# 显示 Python 版本
python --version

# 显示已安装的包
pip list

# 查找 gunicorn
which gunicorn || echo "Gunicorn not found in PATH"

# 使用 Python 模块方式启动 gunicorn
python -m gunicorn app:app --bind 0.0.0.0:$PORT

echo "Application started"