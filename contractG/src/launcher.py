#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
contractG 启动器
用于设置正确的Python路径并启动主程序
"""

import os
import sys
import traceback

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.utils.path_setup import setup_python_path

def main():
    """主函数"""
    try:
        setup_python_path()

        if os.environ.get("CONTRACTG_DEBUG") == "1":
            print("Python路径:")
            for p in sys.path:
                print(f"  - {p}")
            print(f"当前目录: {os.getcwd()}")
            print(f"当前文件: {__file__}")
            print(f"项目根目录: {project_root}")

        try:
            from src import main as app_main
            app_main.main()
        except Exception:
            import main as app_main
            app_main.main()
    except Exception as e:
        error_text = traceback.format_exc()

        log_dir = None
        log_file = None
        try:
            from src.utils.runtime_paths import ensure_writable_layout
            base_dir = ensure_writable_layout()
            log_dir = os.path.join(str(base_dir), 'logs')
        except Exception:
            log_dir = os.path.join(project_root, 'logs')

        os.makedirs(log_dir, exist_ok=True)

        import datetime
        log_file = os.path.join(log_dir, f'launcher_error_{datetime.datetime.now().strftime("%Y%m%d_%H%M%S")}.log')
        with open(log_file, 'w', encoding='utf-8') as f:
            f.write(f'Error occurred at {datetime.datetime.now()}\n')
            f.write(f'Exception: {str(e)}\n')
            f.write('Traceback:\n')
            f.write(error_text)
            f.write('\nSystem Information:\n')
            f.write(f'Python version: {sys.version}\n')
            f.write(f'sys.path: {sys.path}\n')
            f.write(f'Current directory: {os.getcwd()}\n')
            try:
                f.write(f'Files in current directory: {os.listdir(".")}\n')
            except Exception:
                f.write('Files in current directory: <unavailable>\n')

        if sys.platform == "win32":
            try:
                import ctypes
                message = f"contractG 启动失败：{e}\n\n错误日志：{log_file}"
                ctypes.windll.user32.MessageBoxW(0, message, "contractG", 0x10)
            except Exception:
                pass
        else:
            print(f"启动器发生错误: {e}")
            print("详细错误信息:")
            print(error_text)
            print(f'详细错误信息已写入日志文件: {log_file}')
        sys.exit(1)

if __name__ == "__main__":
    main() 
