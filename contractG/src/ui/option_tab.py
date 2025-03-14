import os
import sys
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QFileDialog, QLabel, 
    QProgressBar, QHBoxLayout, QFrame, QGroupBox, QSplitter, 
    QSpacerItem, QSizePolicy, QApplication, QCheckBox
)
from PyQt5.QtCore import Qt, QMimeData, QTimer
from PyQt5.QtGui import QIcon, QFont, QPixmap
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
import pandas as pd
from src.utils.excel_to_pdf import ExcelToPdfConverter
from src.ui.styles import CARD_STYLE, PRIMARY_COLOR, SECONDARY_COLOR, SUCCESS_COLOR

class OptionTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.converter = ExcelToPdfConverter()  # Initialize the converter
        self.output_pdf_path = None
        
        # 启用拖放功能
        self.setAcceptDrops(True)

    def setup_ui(self):
        # 主布局
        main_layout = QVBoxLayout()
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # 标题区域
        title_layout = QHBoxLayout()
        
        title_label = QLabel("Excel 转 PDF 工具")
        title_label.setStyleSheet("""
            font-size: 18pt;
            font-weight: bold;
            color: #333333;
        """)
        
        title_layout.addWidget(title_label)
        title_layout.addStretch()
        
        # 添加到主布局
        main_layout.addLayout(title_layout)
        
        # 说明卡片
        instruction_card = QGroupBox("使用说明")
        instruction_card.setStyleSheet(CARD_STYLE)
        instruction_layout = QVBoxLayout(instruction_card)
        
        # 简化的使用说明
        instruction_text = QLabel(
            "将Excel文件直接拖放到下方虚线框内即可自动转换为PDF。\n"
            "转换后的PDF文件将保存在与Excel文件相同的目录下，文件名为\"原文件名_converted.pdf\"。\n"
            "勾选\"图片式PDF\"选项可将PDF转换为图片格式，提高兼容性。"
        )
        instruction_text.setWordWrap(True)
        instruction_text.setStyleSheet("""
            font-size: 10pt; 
            color: #555555;
            line-height: 150%;
            padding: 5px;
        """)
        instruction_layout.addWidget(instruction_text)
        
        main_layout.addWidget(instruction_card)
        
        # 文件选择卡片
        file_card = QGroupBox("文件选择")
        file_card.setStyleSheet(CARD_STYLE)
        file_layout = QVBoxLayout(file_card)
        
        # 文件信息区域
        self.file_info_frame = QFrame()
        self.file_info_frame.setFrameShape(QFrame.StyledPanel)
        self.file_info_frame.setStyleSheet("""
            background-color: #f8f9fa;
            border: 1px dashed #cccccc;
            border-radius: 5px;
            padding: 10px;
        """)
        file_info_layout = QVBoxLayout(self.file_info_frame)
        
        self.file_icon_label = QLabel()
        self.file_icon_label.setAlignment(Qt.AlignCenter)
        # 设置默认图标
        default_icon = QPixmap("resources/icons/excel.png")
        if default_icon.isNull():
            # 如果图标不存在，使用文本替代
            self.file_icon_label.setText("📄")
            self.file_icon_label.setStyleSheet("font-size: 24pt; color: #4CAF50;")
        else:
            self.file_icon_label.setPixmap(default_icon.scaled(48, 48, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        
        self.file_name_label = QLabel("未选择文件")
        self.file_name_label.setAlignment(Qt.AlignCenter)
        self.file_name_label.setStyleSheet("font-size: 12pt; font-weight: bold; color: #333333;")
        
        self.file_path_label = QLabel("")
        self.file_path_label.setAlignment(Qt.AlignCenter)
        self.file_path_label.setStyleSheet("font-size: 9pt; color: #777777;")
        self.file_path_label.setWordWrap(True)
        
        # 添加拖放提示
        self.drop_hint_label = QLabel("拖放Excel文件到此处自动转换")
        self.drop_hint_label.setAlignment(Qt.AlignCenter)
        self.drop_hint_label.setStyleSheet("font-size: 11pt; color: #999999; font-style: italic;")
        
        file_info_layout.addWidget(self.file_icon_label)
        file_info_layout.addWidget(self.file_name_label)
        file_info_layout.addWidget(self.file_path_label)
        file_info_layout.addWidget(self.drop_hint_label)
        
        file_layout.addWidget(self.file_info_frame)
        
        # 添加图片式PDF选项
        option_layout = QHBoxLayout()
        
        self.image_pdf_checkbox = QCheckBox("图片式PDF")
        self.image_pdf_checkbox.setChecked(True)
        self.image_pdf_checkbox.setToolTip("将PDF转换为图片格式，提高兼容性")
        self.image_pdf_checkbox.setStyleSheet("""
            QCheckBox {
                font-size: 10pt;
                color: #555555;
            }
            QCheckBox::indicator {
                width: 16px;
                height: 16px;
            }
            QCheckBox::indicator:unchecked {
                border: 1px solid #cccccc;
                background-color: white;
            }
            QCheckBox::indicator:checked {
                border: 1px solid #4caf50;
                background-color: #4caf50;
            }
        """)
        
        option_layout.addWidget(self.image_pdf_checkbox)
        option_layout.addStretch()
        
        file_layout.addLayout(option_layout)
        
        # 状态信息
        self.status_label = QLabel("拖放Excel文件开始自动转换")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("font-size: 11pt; color: #555555;")
        file_layout.addWidget(self.status_label)
        
        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid #E0E0E0;
                border-radius: 5px;
                text-align: center;
                background-color: #F5F5F5;
                height: 20px;
            }
            QProgressBar::chunk {
                background-color: #4CAF50;
                border-radius: 5px;
            }
        """)
        file_layout.addWidget(self.progress_bar)
        
        # 操作按钮
        action_layout = QHBoxLayout()
        
        self.open_pdf_button = QPushButton("打开PDF")
        self.open_pdf_button.setIcon(QIcon("resources/icons/pdf.png"))
        self.open_pdf_button.setToolTip("打开转换后的PDF文件")
        self.open_pdf_button.clicked.connect(self.open_pdf)
        self.open_pdf_button.setMinimumHeight(40)
        self.open_pdf_button.setEnabled(False)
        self.open_pdf_button.setStyleSheet("""
            QPushButton {
                background-color: #6c757d;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #5a6268;
            }
            QPushButton:disabled {
                background-color: #cccccc;
                color: #666666;
            }
        """)
        
        self.reset_button = QPushButton("重新选择")
        self.reset_button.setIcon(QIcon("resources/icons/reset.png"))
        self.reset_button.setToolTip("清除当前选择的文件，重新选择")
        self.reset_button.clicked.connect(self.reset_ui)
        self.reset_button.setMinimumHeight(40)
        self.reset_button.setStyleSheet("""
            QPushButton {
                background-color: #6c757d;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #5a6268;
            }
        """)
        
        action_layout.addWidget(self.open_pdf_button)
        action_layout.addWidget(self.reset_button)
        
        file_layout.addLayout(action_layout)
        
        main_layout.addWidget(file_card)
        
        # 添加弹性空间
        main_layout.addStretch()
        
        self.setLayout(main_layout)

    def convert_to_pdf(self):
        if hasattr(self, 'selected_file'):
            self.output_pdf_path = self.selected_file.replace('.xlsx', '_converted.pdf')
            
            # 更新UI状态 - 显示正在转换
            self.status_label.setText("正在转换，请稍候...")
            self.progress_bar.setVisible(True)
            self.progress_bar.setRange(0, 0)  # Indeterminate state
            
            # 更改文件区域样式，表示正在转换
            self.file_info_frame.setStyleSheet("""
                background-color: #e8f5e9;
                border: 1px dashed #4caf50;
                border-radius: 5px;
                padding: 10px;
            """)
            
            # 让UI有时间更新
            QApplication.processEvents()
            
            try:
                # 转换为PDF
                self.converter.convert_to_pdf(self.selected_file, self.output_pdf_path)
                
                # 如果勾选了图片式PDF选项，则将PDF转换为图片式PDF
                if self.image_pdf_checkbox.isChecked():
                    self.status_label.setText("正在转换为图片式PDF...")
                    QApplication.processEvents()
                    
                    # 创建临时文件路径
                    temp_pdf = self.output_pdf_path
                    final_pdf = self.output_pdf_path.replace('.pdf', '_image.pdf')
                    
                    # 转换为图片式PDF
                    self.converter.convert_pdf_to_image_pdf(temp_pdf, final_pdf)
                    
                    # 更新输出路径
                    self.output_pdf_path = final_pdf
                
                # 更新UI状态 - 显示转换成功
                self.status_label.setText(f"转换成功: {os.path.basename(self.output_pdf_path)}")
                self.open_pdf_button.setEnabled(True)
                self.open_pdf_button.setStyleSheet("""
                    QPushButton {
                        background-color: #28a745;
                        color: white;
                        border: none;
                        border-radius: 5px;
                        padding: 8px 16px;
                        font-weight: bold;
                    }
                    QPushButton:hover {
                        background-color: #218838;
                    }
                """)
                
                # 更改文件区域样式，表示转换成功
                self.file_info_frame.setStyleSheet("""
                    background-color: #e8f5e9;
                    border: 1px solid #4caf50;
                    border-radius: 5px;
                    padding: 10px;
                """)
                
            except Exception as e:
                # 更新UI状态 - 显示转换失败
                self.status_label.setText(f"转换失败: {str(e)}")
                self.output_pdf_path = None
                
                # 更改文件区域样式，表示转换失败
                self.file_info_frame.setStyleSheet("""
                    background-color: #ffebee;
                    border: 1px solid #f44336;
                    border-radius: 5px;
                    padding: 10px;
                """)
                
            finally:
                self.progress_bar.setVisible(False)
                # 重新启用按钮
                self.reset_button.setEnabled(True)
        else:
            self.status_label.setText("请先拖放Excel文件")
    
    def reset_ui(self):
        """重置UI到初始状态"""
        self.file_name_label.setText("未选择文件")
        self.file_path_label.setText("")
        self.status_label.setText("拖放Excel文件开始自动转换")
        self.drop_hint_label.setVisible(True)
        self.open_pdf_button.setEnabled(False)
        self.output_pdf_path = None
        
        # 重置图片式PDF选项
        self.image_pdf_checkbox.setChecked(True)
        
        # 恢复原来的样式
        self.file_info_frame.setStyleSheet("""
            background-color: #f8f9fa;
            border: 1px dashed #cccccc;
            border-radius: 5px;
            padding: 10px;
        """)
        
        # 恢复按钮样式
        self.open_pdf_button.setStyleSheet("""
            QPushButton {
                background-color: #6c757d;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #5a6268;
            }
            QPushButton:disabled {
                background-color: #cccccc;
                color: #666666;
            }
        """)
        
        # 确保进度条隐藏
        self.progress_bar.setVisible(False)
        
        # 确保重置按钮可用
        self.reset_button.setEnabled(True)
        
        if hasattr(self, 'selected_file'):
            delattr(self, 'selected_file')
    
    def open_pdf(self):
        if self.output_pdf_path and os.path.exists(self.output_pdf_path):
            # 打开PDF文件
            if sys.platform == 'win32':
                os.startfile(self.output_pdf_path)
            elif sys.platform == 'darwin':  # macOS
                import subprocess
                subprocess.Popen(['open', self.output_pdf_path])
            else:  # Linux
                import subprocess
                subprocess.Popen(['xdg-open', self.output_pdf_path])
        else:
            self.status_label.setText("PDF文件不存在，请先转换")
            self.open_pdf_button.setEnabled(False)

    # 添加拖放事件处理方法
    def dragEnterEvent(self, event):
        """当用户拖动文件进入窗口时触发"""
        if event.mimeData().hasUrls():
            # 检查是否是Excel文件
            for url in event.mimeData().urls():
                file_path = url.toLocalFile()
                if file_path.endswith('.xlsx'):
                    # 如果是Excel文件，接受拖放
                    self.file_info_frame.setStyleSheet("""
                        background-color: #e3f2fd;
                        border: 2px dashed #1976D2;
                        border-radius: 5px;
                        padding: 10px;
                    """)
                    event.accept()
                    return
        event.ignore()
    
    def dragLeaveEvent(self, event):
        """当用户拖动文件离开窗口时触发"""
        # 恢复原来的样式
        self.file_info_frame.setStyleSheet("""
            background-color: #f8f9fa;
            border: 1px dashed #cccccc;
            border-radius: 5px;
            padding: 10px;
        """)
        event.accept()
    
    def dropEvent(self, event):
        """当用户放下文件时触发"""
        # 恢复原来的样式 - 不需要在这里恢复，因为process_dropped_file会设置新样式
        # self.file_info_frame.setStyleSheet("""
        #     background-color: #f8f9fa;
        #     border-radius: 5px;
        #     padding: 10px;
        # """)
        
        # 处理拖放的文件
        if event.mimeData().hasUrls():
            for url in event.mimeData().urls():
                file_path = url.toLocalFile()
                if file_path.endswith('.xlsx'):
                    # 处理Excel文件
                    self.process_dropped_file(file_path)
                    break
        event.accept()
    
    def process_dropped_file(self, file_path):
        """处理拖放的Excel文件"""
        self.selected_file = file_path
        file_name = os.path.basename(file_path)
        
        # 更新UI - 显示文件已选择
        self.file_name_label.setText(file_name)
        self.file_path_label.setText(file_path)
        self.status_label.setText(f"已选择: {file_name}")
        
        # 隐藏拖放提示
        self.drop_hint_label.setVisible(False)
        
        # 重置PDF按钮状态
        self.open_pdf_button.setEnabled(False)
        self.output_pdf_path = None
        
        # 显示准备转换的状态
        self.status_label.setText("准备转换...")
        
        # 禁用重置按钮，防止转换过程中重置
        self.reset_button.setEnabled(False)
        
        # 更改文件区域样式，表示正在处理
        self.file_info_frame.setStyleSheet("""
            background-color: #fff8e1;
            border: 1px dashed #ffc107;
            border-radius: 5px;
            padding: 10px;
        """)
        
        # 让UI有时间更新
        QApplication.processEvents()
        
        # 延迟一小段时间后开始转换，让用户能看到状态变化
        QTimer.singleShot(300, self.convert_to_pdf)

    # Remove the existing excel_to_pdf method as it's no longer needed
    # def excel_to_pdf(self, excel_file, pdf_file):
    #     ... existing code ... 