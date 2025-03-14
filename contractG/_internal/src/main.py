#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
contractG
主程序入口
"""

import os
import sys
import locale
import traceback
from datetime import datetime
import pandas as pd
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

# 添加项目根目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# 添加src目录到Python路径
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# 添加ui目录到Python路径
ui_dir = os.path.join(current_dir, 'ui')
if os.path.exists(ui_dir) and ui_dir not in sys.path:
    sys.path.insert(0, ui_dir)

def setup_encoding():
    """设置系统编码"""
    try:
        # 设置默认编码为UTF-8
        if sys.stdout.encoding != 'utf-8':
            sys.stdout.reconfigure(encoding='utf-8')
        if sys.stderr.encoding != 'utf-8':
            sys.stderr.reconfigure(encoding='utf-8')
            
        # 设置区域和语言
        locale.setlocale(locale.LC_ALL, 'zh_CN.UTF-8')
    except Exception:
        try:
            # 如果无法设置中文，则使用系统默认
            locale.setlocale(locale.LC_ALL, '')
        except Exception:
            pass

def setup_python_path():
    """设置Python路径"""
    try:
        # 获取当前文件所在目录
        current_dir = os.path.dirname(os.path.abspath(__file__))
        
        # 获取项目根目录（src的父目录）
        project_root = os.path.dirname(current_dir)
        
        # 将项目根目录添加到Python路径
        if project_root not in sys.path:
            sys.path.insert(0, project_root)
        
        # 将src目录添加到Python路径
        if current_dir not in sys.path:
            sys.path.insert(0, current_dir)
            
        # 为打包后的环境添加特殊处理
        # 如果是打包后的环境，_MEIPASS 会被 PyInstaller 设置
        if hasattr(sys, '_MEIPASS'):
            # 将 PyInstaller 的临时目录添加到路径
            if sys._MEIPASS not in sys.path:
                sys.path.insert(0, sys._MEIPASS)
                
            # 如果是打包后的环境，尝试不同的导入路径
            src_path = os.path.join(sys._MEIPASS, 'src')
            if os.path.exists(src_path) and src_path not in sys.path:
                sys.path.insert(0, src_path)
                
            # 添加ui目录到Python路径
            ui_path = os.path.join(sys._MEIPASS, 'src', 'ui')
            if os.path.exists(ui_path) and ui_path not in sys.path:
                sys.path.insert(0, ui_path)
                
            # 打印路径信息，帮助调试
            print("Python路径:")
            for p in sys.path:
                print(f"  - {p}")
            print(f"当前目录: {os.getcwd()}")
            if os.path.exists(os.path.join(sys._MEIPASS, 'src', 'ui')):
                print(f"UI目录存在: {os.path.join(sys._MEIPASS, 'src', 'ui')}")
            else:
                print(f"UI目录不存在: {os.path.join(sys._MEIPASS, 'src', 'ui')}")
    except Exception as e:
        print(f"Error in setup_python_path: {str(e)}")
        raise

# 设置Python路径
setup_python_path()

# 导入UI相关模块
from PyQt5.QtWidgets import QApplication, QHBoxLayout, QPushButton
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QIcon

# 尝试使用不同的导入方式，以适应打包后的环境
try:
    # 首先尝试直接导入（开发环境）
    print("尝试导入方式1: from src.ui.main_window import MainWindow")
    from src.ui.main_window import MainWindow
    from src.ui.styles import GLOBAL_STYLE, FONT_FAMILY
    print("导入方式1成功")
except ImportError as e1:
    print(f"导入方式1失败: {e1}")
    try:
        # 如果失败，尝试相对导入（打包环境）
        print("尝试导入方式2: from ui.main_window import MainWindow")
        from ui.main_window import MainWindow
        from ui.styles import GLOBAL_STYLE, FONT_FAMILY
        print("导入方式2成功")
    except ImportError as e2:
        print(f"导入方式2失败: {e2}")
        try:
            # 如果还是失败，尝试直接导入
            print("尝试导入方式3: import main_window")
            import main_window
            import styles
            MainWindow = main_window.MainWindow
            GLOBAL_STYLE = styles.GLOBAL_STYLE
            FONT_FAMILY = styles.FONT_FAMILY
            print("导入方式3成功")
        except ImportError as e3:
            print(f"导入方式3失败: {e3}")
            # 最后的尝试，动态加载模块
            print("尝试导入方式4: 动态加载模块")
            import importlib.util
            
            # 尝试不同的路径
            possible_paths = [
                os.path.join(current_dir, 'ui', 'main_window.py'),
                os.path.join(project_root, 'src', 'ui', 'main_window.py')
            ]
            
            if hasattr(sys, '_MEIPASS'):
                possible_paths.extend([
                    os.path.join(sys._MEIPASS, 'src', 'ui', 'main_window.py'),
                    os.path.join(sys._MEIPASS, 'ui', 'main_window.py')
                ])
            
            main_window_spec = None
            styles_spec = None
            
            for path in possible_paths:
                if os.path.exists(path):
                    print(f"找到main_window.py: {path}")
                    main_window_spec = importlib.util.spec_from_file_location("main_window", path)
                    styles_path = path.replace('main_window.py', 'styles.py')
                    if os.path.exists(styles_path):
                        print(f"找到styles.py: {styles_path}")
                        styles_spec = importlib.util.spec_from_file_location("styles", styles_path)
                    break
            
            if main_window_spec and styles_spec:
                main_window_module = importlib.util.module_from_spec(main_window_spec)
                styles_module = importlib.util.module_from_spec(styles_spec)
                main_window_spec.loader.exec_module(main_window_module)
                styles_spec.loader.exec_module(styles_module)
                MainWindow = main_window_module.MainWindow
                GLOBAL_STYLE = styles_module.GLOBAL_STYLE
                FONT_FAMILY = styles_module.FONT_FAMILY
                print("导入方式4成功")
            else:
                print("所有导入方式都失败，无法找到必要的模块")
                raise ImportError("无法导入必要的模块: main_window.py 和 styles.py")

def resource_path(relative_path):
    """获取资源文件的绝对路径"""
    try:
        # 检查是否在打包环境中运行
        if hasattr(sys, '_MEIPASS'):
            # 如果是打包环境，使用 _MEIPASS 作为基础路径
            base_path = sys._MEIPASS
        else:
            # 获取当前文件所在目录
            current_dir = os.path.dirname(os.path.abspath(__file__))
            # 获取项目根目录
            base_path = os.path.dirname(current_dir)
        
        # 构建并返回资源文件的完整路径
        full_path = os.path.join(base_path, 'resources', relative_path)
        
        # 确保目录存在
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        
        return full_path
    except Exception as e:
        print(f"Error in resource_path: {str(e)}")
        return relative_path

def config_path(relative_path):
    """获取配置文件的绝对路径"""
    try:
        # 检查是否在打包环境中运行
        if hasattr(sys, '_MEIPASS'):
            # 如果是打包环境，使用 _MEIPASS 作为基础路径
            base_path = sys._MEIPASS
        else:
            # 获取当前文件所在目录
            current_dir = os.path.dirname(os.path.abspath(__file__))
            # 获取项目根目录
            base_path = os.path.dirname(current_dir)
        
        # 构建并返回配置文件的完整路径
        full_path = os.path.join(base_path, 'config', relative_path)
        
        # 确保目录存在
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        
        return full_path
    except Exception as e:
        print(f"Error in config_path: {str(e)}")
        return relative_path

def ensure_directories():
    """确保必要的目录存在"""
    directories = [
        'data',
        'output/contracts',
        'templates',  # 模板目录
        'logs',  # 日志目录
        'resources',  # 资源文件目录
        'config',  # 配置文件目录
        'src/data',  # 数据处理目录
        'src/database',  # 数据库目录
        'src/ui/dialogs',  # UI对话框目录
    ]
    for directory in directories:
        os.makedirs(directory, exist_ok=True)

def excel_to_pdf(excel_file, pdf_file):
    # 读取 Excel 文件
    df = pd.read_excel(excel_file)

    # 创建 PDF 文件
    c = canvas.Canvas(pdf_file, pagesize=A4)
    width, height = A4

    # 设置初始位置
    x_offset = 50
    y_offset = height - 50
    line_height = 20

    # 写入标题
    c.setFont("Helvetica-Bold", 12)
    c.drawString(x_offset, y_offset, "Excel to PDF Conversion")
    y_offset -= line_height

    # 写入列名
    c.setFont("Helvetica-Bold", 10)
    for col in df.columns:
        c.drawString(x_offset, y_offset, str(col))
        x_offset += 100  # 调整列间距
    y_offset -= line_height
    x_offset = 50

    # 写入数据
    c.setFont("Helvetica", 10)
    for index, row in df.iterrows():
        for col in df.columns:
            c.drawString(x_offset, y_offset, str(row[col]))
            x_offset += 100
        y_offset -= line_height
        x_offset = 50
        if y_offset < 50:  # 如果接近页面底部，添加新页面
            c.showPage()
            y_offset = height - 50

    # 保存 PDF
    c.save()

def main():
    """主函数"""
    try:
        # 设置编码
        setup_encoding()
        
        # 确保必要的目录存在
        ensure_directories()
        
        # 设置高DPI缩放
        QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
        QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)
        
        # 创建应用
        app = QApplication(sys.argv)
        
        # 设置应用样式
        app.setStyle("Fusion")  # 使用Fusion风格作为基础
        app.setStyleSheet(GLOBAL_STYLE)  # 应用全局样式表
        
        # 设置默认字体
        font = QFont(FONT_FAMILY.split(',')[0], 10)
        app.setFont(font)
        
        # 设置应用图标
        icon_path = resource_path('icon.ico')
        if os.path.exists(icon_path):
            app.setWindowIcon(QIcon(icon_path))
        else:
            print(f"Warning: Icon file not found at {icon_path}")
        
        # 创建主窗口
        window = MainWindow()
        window.show()
        
        # 运行应用
        sys.exit(app.exec_())
    except Exception as e:
        # 将错误写入日志文件
        log_dir = 'logs'
        os.makedirs(log_dir, exist_ok=True)
        
        log_file = os.path.join(log_dir, f'error_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log')
        with open(log_file, 'w', encoding='utf-8') as f:
            f.write(f'Error occurred at {datetime.now()}\n')
            f.write(f'Exception: {str(e)}\n')
            f.write('Traceback:\n')
            f.write(traceback.format_exc())
            f.write('\nSystem Information:\n')
            f.write(f'Python version: {sys.version}\n')
            f.write(f'sys.path: {sys.path}\n')
            f.write(f'Current directory: {os.getcwd()}\n')
            f.write(f'Files in current directory: {os.listdir(".")}\n')
        
        print(f'发生错误，详细信息已写入日志文件: {log_file}')
        sys.exit(1)

if __name__ == "__main__":
    main() 