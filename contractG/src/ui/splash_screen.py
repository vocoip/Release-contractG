#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
启动画面模块
"""

import os
from PyQt5.QtWidgets import QSplashScreen, QProgressBar, QLabel
from PyQt5.QtCore import Qt, QTimer, QRect, QPoint, QSize
from PyQt5.QtGui import QPixmap, QPainter, QColor, QFont, QLinearGradient, QPainterPath, QPen, QRadialGradient, QIcon

class SplashScreen(QSplashScreen):
    def __init__(self):
        """初始化启动画面"""
        # 创建一个透明背景的QPixmap
        pixmap = QPixmap(700, 400)
        pixmap.fill(Qt.transparent)
        
        # 调用父类构造函数
        super().__init__(pixmap)
        
        # 设置窗口标志
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
        
        # 加载图标
        self.app_icon = None
        icon_path = self.resource_path('icon.ico')
        if os.path.exists(icon_path):
            self.app_icon = QPixmap(icon_path)
        
        # 创建进度条
        self.progress_bar = QProgressBar(self)
        self.progress_bar.setGeometry(100, 320, 500, 8)  # 降低高度使其更现代
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: none;
                border-radius: 4px;
                background-color: rgba(255, 255, 255, 100);
                text-align: center;
            }
            QProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #4FC3F7,
                    stop:0.5 #29B6F6,
                    stop:1 #03A9F4);
                border-radius: 4px;
            }
        """)
        
        # 创建标签
        self.loading_label = QLabel("正在加载...", self)
        self.loading_label.setGeometry(100, 290, 500, 20)
        self.loading_label.setAlignment(Qt.AlignCenter)
        self.loading_label.setStyleSheet("""
            QLabel {
                color: rgba(255, 255, 255, 200);
                font-size: 12px;
                font-weight: normal;
                font-family: "Microsoft YaHei";
            }
        """)
        
        # 初始化进度
        self.progress = 0
        
        # 创建定时器更新进度
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_progress)
        self.timer.start(30)  # 每30毫秒更新一次
    
    def resource_path(self, relative_path):
        """获取资源文件的绝对路径"""
        try:
            # 检查是否在打包环境中运行
            if hasattr(sys, '_MEIPASS'):
                # 如果是打包环境，使用 _MEIPASS 作为基础路径
                base_path = sys._MEIPASS
            else:
                # 获取当前文件所在目录
                import sys
                current_dir = os.path.dirname(os.path.abspath(__file__))
                # 获取项目根目录
                base_path = os.path.dirname(os.path.dirname(current_dir))
            
            # 构建并返回资源文件的完整路径
            return os.path.join(base_path, 'resources', relative_path)
        except Exception:
            return os.path.join('resources', relative_path)
    
    def update_progress(self):
        """更新进度条"""
        self.progress += 1
        if self.progress <= 100:
            self.progress_bar.setValue(self.progress)
            if self.progress < 20:
                self.loading_label.setText("正在初始化系统...")
            elif self.progress < 40:
                self.loading_label.setText("正在加载资源文件...")
            elif self.progress < 60:
                self.loading_label.setText("正在准备数据...")
            elif self.progress < 80:
                self.loading_label.setText("正在配置界面...")
            else:
                self.loading_label.setText("即将完成...")
        else:
            self.timer.stop()
    
    def drawContents(self, painter):
        """绘制启动画面内容"""
        # 启用抗锯齿
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setRenderHint(QPainter.TextAntialiasing)
        painter.setRenderHint(QPainter.SmoothPixmapTransform)
        
        # 创建主背景渐变
        gradient = QLinearGradient(0, 0, self.width(), self.height())
        gradient.setColorAt(0, QColor(41, 121, 255))    # 深蓝色
        gradient.setColorAt(1, QColor(45, 206, 255))    # 浅蓝色
        
        # 绘制圆角矩形背景
        path = QPainterPath()
        path.addRoundedRect(0, 0, self.width(), self.height(), 15, 15)
        painter.fillPath(path, gradient)
        
        # 添加装饰性圆形
        self.draw_decorative_circles(painter)
        
        # 绘制应用图标
        if self.app_icon and not self.app_icon.isNull():
            icon_size = 80
            icon_x = (self.width() - icon_size) // 2
            icon_y = 30
            
            # 绘制图标阴影
            shadow_offset = 3
            shadow_color = QColor(0, 0, 0, 40)
            painter.setPen(Qt.NoPen)
            painter.setBrush(shadow_color)
            painter.drawEllipse(icon_x + shadow_offset, icon_y + shadow_offset, icon_size, icon_size)
            
            # 绘制图标背景圆形
            painter.setBrush(QColor(255, 255, 255, 220))
            painter.drawEllipse(icon_x, icon_y, icon_size, icon_size)
            
            # 绘制图标
            scaled_icon = self.app_icon.scaled(icon_size - 20, icon_size - 20, 
                                              Qt.KeepAspectRatio, Qt.SmoothTransformation)
            painter.drawPixmap(
                icon_x + (icon_size - scaled_icon.width()) // 2,
                icon_y + (icon_size - scaled_icon.height()) // 2,
                scaled_icon
            )
        
        # 绘制应用名称
        painter.setPen(QColor(255, 255, 255))
        font = QFont("Microsoft YaHei", 32, QFont.Bold)
        painter.setFont(font)
        
        # 添加文字阴影效果
        shadow_color = QColor(0, 0, 0, 30)
        offset = 2
        
        # 绘制阴影
        painter.setPen(shadow_color)
        painter.drawText(offset, 142 + offset, self.width(), 50, Qt.AlignCenter, "合同生成工具")
        
        # 绘制主文本
        painter.setPen(QColor(255, 255, 255))
        painter.drawText(0, 142, self.width(), 50, Qt.AlignCenter, "合同生成工具")
        
        # 绘制英文名称
        font.setPointSize(20)
        painter.setFont(font)
        # 阴影
        painter.setPen(shadow_color)
        painter.drawText(offset, 192 + offset, self.width(), 30, Qt.AlignCenter, "contractG")
        # 主文本
        painter.setPen(QColor(255, 255, 255))
        painter.drawText(0, 192, self.width(), 30, Qt.AlignCenter, "contractG")
        
        # 绘制版本号
        font.setPointSize(12)
        font.setBold(False)
        painter.setFont(font)
        painter.setPen(QColor(255, 255, 255, 180))
        painter.drawText(0, 230, self.width(), 30, Qt.AlignCenter, "Version 1.1.0")
        
        # 绘制底部版权信息
        font.setPointSize(9)
        painter.setFont(font)
        painter.setPen(QColor(255, 255, 255, 150))
        painter.drawText(0, 360, self.width(), 20, Qt.AlignCenter, "© 2024 contractG Team")
        
        # 绘制标语
        font.setPointSize(11)
        painter.setFont(font)
        painter.setPen(QColor(255, 255, 255, 200))
        painter.drawText(0, 260, self.width(), 30, Qt.AlignCenter, "让合同管理更简单、更高效！")
    
    def draw_decorative_circles(self, painter):
        """绘制装饰性圆形"""
        # 设置透明画笔
        painter.setPen(Qt.NoPen)
        
        # 绘制左上角装饰圆
        gradient1 = QRadialGradient(50, 50, 100)
        gradient1.setColorAt(0, QColor(255, 255, 255, 30))
        gradient1.setColorAt(1, QColor(255, 255, 255, 0))
        painter.setBrush(gradient1)
        painter.drawEllipse(QPoint(50, 50), 100, 100)
        
        # 绘制右下角装饰圆
        gradient2 = QRadialGradient(self.width() - 50, self.height() - 50, 80)
        gradient2.setColorAt(0, QColor(255, 255, 255, 20))
        gradient2.setColorAt(1, QColor(255, 255, 255, 0))
        painter.setBrush(gradient2)
        painter.drawEllipse(QPoint(self.width() - 50, self.height() - 50), 80, 80)
        
        # 绘制小圆点装饰
        painter.setBrush(QColor(255, 255, 255, 15))
        for pos in [(150, 30, 10), (550, 50, 15), (650, 200, 8), 
                    (50, 300, 12), (600, 350, 10), (200, 380, 8)]:
            painter.drawEllipse(QPoint(pos[0], pos[1]), pos[2], pos[2]) 