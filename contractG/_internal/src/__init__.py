# 导入路径设置模块，确保src模块加载时路径已正确设置
import os
import sys

# 添加当前目录到Python路径，以便能够导入path_setup模块
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# 导入路径设置模块
from utils.path_setup import setup_python_path 