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
    def _prepend_unique(path: str):
        if not path:
            return
        if path in sys.path:
            sys.path.remove(path)
        sys.path.insert(0, path)

    # 获取当前文件所在目录
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 获取utils目录
    utils_dir = current_dir
    
    # 获取src目录
    src_dir = os.path.dirname(utils_dir)
    
    # 获取项目根目录（src的父目录）
    project_root = os.path.dirname(src_dir)
    
    # 将项目根目录添加到Python路径
    _prepend_unique(project_root)
    
    # 将src目录添加到Python路径
    _prepend_unique(src_dir)
    
    # 添加ui目录到Python路径
    ui_dir = os.path.join(src_dir, 'ui')
    if os.path.exists(ui_dir):
        _prepend_unique(ui_dir)
        
    # 为打包后的环境添加特殊处理
    if hasattr(sys, '_MEIPASS'):
        # 将 PyInstaller 的临时目录添加到路径
        _prepend_unique(sys._MEIPASS)
            
        # 添加src目录到Python路径
        src_path = os.path.join(sys._MEIPASS, 'src')
        if os.path.exists(src_path):
            _prepend_unique(src_path)
            
        # 添加ui目录到Python路径
        ui_path = os.path.join(sys._MEIPASS, 'src', 'ui')
        if os.path.exists(ui_path):
            _prepend_unique(ui_path)
