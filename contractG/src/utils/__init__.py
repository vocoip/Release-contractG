# 导入路径设置模块，确保utils模块加载时路径已正确设置
import os
import sys

# 添加当前目录到Python路径，以便能够导入path_setup模块
current_dir = os.path.dirname(os.path.abspath(__file__))
utils_dir = current_dir
src_dir = os.path.dirname(utils_dir)

# 确保utils目录在路径中
if utils_dir not in sys.path:
    sys.path.insert(0, utils_dir)

# 直接导入path_setup模块
import path_setup 