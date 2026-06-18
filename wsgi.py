# -*- coding: utf-8 -*-
"""
PythonAnywhere WSGI 入口文件
用于部署抖音视频下载器 Web 应用
"""

import sys

# 确保项目目录在 Python 路径中
path = '/home/lian68/douyin-web'
if path not in sys.path:
    sys.path.insert(0, path)

# 导入 Flask 应用
from app import app as application
