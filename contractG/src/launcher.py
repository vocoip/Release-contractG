#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
contractG 启动器
用于设置正确的Python路径并启动主程序
"""

import os
import sys
import importlib.util
import traceback

# 添加当前目录到Python路径，以便能够导入path_setup模块
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# 添加项目根目录到Python路径
project_root = os.path.dirname(current_dir)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# 现在使用绝对导入
from src.utils.path_setup import setup_python_path

def main():
    """主函数"""
    try:
        # 获取当前文件所在目录
        current_dir = os.path.dirname(os.path.abspath(__file__))
        
        # 获取项目根目录（src的父目录）
        project_root = os.path.dirname(current_dir)
        
        # 打印路径信息，帮助调试
        print("Python路径:")
        for p in sys.path:
            print(f"  - {p}")
        
        print(f"当前目录: {os.getcwd()}")
        print(f"当前文件: {__file__}")
        print(f"项目根目录: {project_root}")
        
        # 检查文件是否存在
        main_path = os.path.join(current_dir, 'main.py')
        if os.path.exists(main_path):
            print(f"main.py 文件存在: {main_path}")
        else:
            print(f"main.py 文件不存在: {main_path}")
        
        # 动态导入main模块
        try:
            # 尝试直接导入
            print("尝试直接导入 main 模块...")
            import main
            print("成功导入 main 模块")
            main.main()
        except ImportError as e:
            print(f"直接导入失败: {e}")
            # 如果失败，尝试动态导入
            print(f"尝试动态导入 main 模块从: {main_path}")
            if os.path.exists(main_path):
                spec = importlib.util.spec_from_file_location("main", main_path)
                main_module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(main_module)
                print("成功动态导入 main 模块")
                main_module.main()
            else:
                print(f"错误: 找不到main.py文件: {main_path}")
                sys.exit(1)
    except Exception as e:
        print(f"启动器发生错误: {e}")
        print("详细错误信息:")
        traceback.print_exc()
        
        # 创建日志目录
        log_dir = os.path.join(project_root, 'logs')
        os.makedirs(log_dir, exist_ok=True)
        
        # 写入错误日志
        import datetime
        log_file = os.path.join(log_dir, f'launcher_error_{datetime.datetime.now().strftime("%Y%m%d_%H%M%S")}.log')
        with open(log_file, 'w', encoding='utf-8') as f:
            f.write(f'Error occurred at {datetime.datetime.now()}\n')
            f.write(f'Exception: {str(e)}\n')
            f.write('Traceback:\n')
            f.write(traceback.format_exc())
            f.write('\nSystem Information:\n')
            f.write(f'Python version: {sys.version}\n')
            f.write(f'sys.path: {sys.path}\n')
            f.write(f'Current directory: {os.getcwd()}\n')
            f.write(f'Files in current directory: {os.listdir(".")}\n')
        
        print(f'详细错误信息已写入日志文件: {log_file}')
        sys.exit(1)

if __name__ == "__main__":
    main() 