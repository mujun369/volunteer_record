#!/usr/bin/env bash
# 升级 pip
pip install --upgrade pip

# 先安装基础依赖
pip install flask==2.0.1 flask-cors==3.0.10 gunicorn==20.1.0

# 安装数值计算依赖
pip install numpy==1.21.0

# 安装 pandas 和其他依赖
pip install pandas==1.3.3 xlsxwriter==3.0.2