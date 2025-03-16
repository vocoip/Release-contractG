#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
路径设置模块
集中处理所有Python路径设置逻辑，避免在多个模块中重复设置
"""

import os
import sys

def setup_python_path():
    """设置Python路径，确保所有必要的目录都在sys.path中"""
    # 获取当前文件所在目录
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 获取utils目录
    utils_dir = current_dir
    
    # 获取src目录
    src_dir = os.path.dirname(utils_dir)
    
    # 获取项目根目录（src的父目录）
    project_root = os.path.dirname(src_dir)
    
    # 将项目根目录添加到Python路径
    if project_root not in sys.path:
        sys.path.insert(0, project_root)
    
    # 将src目录添加到Python路径
    if src_dir not in sys.path:
        sys.path.insert(0, src_dir)
    
    # 添加ui目录到Python路径
    ui_dir = os.path.join(src_dir, 'ui')
    if os.path.exists(ui_dir) and ui_dir not in sys.path:
        sys.path.insert(0, ui_dir)
        
    # 为打包后的环境添加特殊处理
    if hasattr(sys, '_MEIPASS'):
        # 将 PyInstaller 的临时目录添加到路径
        if sys._MEIPASS not in sys.path:
            sys.path.insert(0, sys._MEIPASS)
            
        # 添加src目录到Python路径
        src_path = os.path.join(sys._MEIPASS, 'src')
        if os.path.exists(src_path) and src_path not in sys.path:
            sys.path.insert(0, src_path)
            
        # 添加ui目录到Python路径
        ui_path = os.path.join(sys._MEIPASS, 'src', 'ui')
        if os.path.exists(ui_path) and ui_path not in sys.path:
            sys.path.insert(0, ui_path)
            
    # 打印路径信息，帮助调试
    print("Python路径设置完成")

# 在模块导入时自动设置路径
setup_python_path() 