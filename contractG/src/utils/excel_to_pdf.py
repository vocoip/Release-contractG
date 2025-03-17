#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Excel转PDF工具
用于将Excel文件按照A4纸张大小进行打印预览并生成PDF
"""

import os
import sys
import logging
from pathlib import Path
import win32com.client
import pythoncom
import fitz  # PyMuPDF

# Pillow将按需导入
# from PIL import Image as PILImage

class ExcelToPdfConverter:
    """Excel转PDF转换器"""
    
    def __init__(self, log_dir='logs'):
        """初始化转换器"""
        self.logger = self._setup_logger(log_dir)
    
    def _setup_logger(self, log_dir):
        """设置日志记录器"""
        logger = logging.getLogger('ExcelToPdfConverter')
        logger.setLevel(logging.INFO)
        
        # 确保日志目录存在
        os.makedirs(log_dir, exist_ok=True)
        
        # 创建文件处理器
        log_file = os.path.join(log_dir, 'excel_to_pdf.log')
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.INFO)
        
        # 创建格式化器
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        
        # 添加处理器到记录器
        logger.addHandler(file_handler)
        
        return logger
    
    def convert_to_pdf(self, excel_file, pdf_file=None, fit_to_page=True, paper_size=9, progress_callback=None):
        """
        将Excel文件转换为PDF
        
        Args:
            excel_file (str): Excel文件路径
            pdf_file (str, optional): 输出PDF文件路径，默认为Excel文件同目录下同名PDF
            fit_to_page (bool, optional): 是否自适应页面，默认True
            paper_size (int, optional): 纸张大小，默认为9（A4）
            progress_callback (callable, optional): 进度回调函数，接收0-100的整数参数
        
        Returns:
            str: 生成的PDF文件路径
        """
        excel = None
        workbook = None
        
        try:
            if progress_callback:
                progress_callback(0)
            
            # 确保使用绝对路径
            excel_file = os.path.abspath(excel_file)
            
            # 如果未指定输出文件，使用默认路径
            if pdf_file is None:
                pdf_file = os.path.splitext(excel_file)[0] + '.pdf'
            pdf_file = os.path.abspath(pdf_file)
            
            if progress_callback:
                progress_callback(10)
            
            # 确保输出目录存在
            os.makedirs(os.path.dirname(pdf_file), exist_ok=True)
            
            # 初始化COM组件
            pythoncom.CoInitialize()
            excel = win32com.client.DispatchEx("Excel.Application")
            excel.Visible = False
            excel.DisplayAlerts = False
            
            if progress_callback:
                progress_callback(30)
            
            # 打开工作簿
            self.logger.info(f"Opening workbook: {excel_file}")
            workbook = excel.Workbooks.Open(excel_file)
            
            if progress_callback:
                progress_callback(50)
            
            try:
                # 设置打印区域和页面设置
                for sheet in workbook.Worksheets:
                    if fit_to_page:
                        sheet.PageSetup.Zoom = False
                        sheet.PageSetup.FitToPagesWide = 1
                        sheet.PageSetup.FitToPagesTall = False
                    sheet.PageSetup.PaperSize = paper_size
                
                if progress_callback:
                    progress_callback(70)
                
                # 导出为PDF
                self.logger.info(f"Exporting to PDF: {pdf_file}")
                workbook.ExportAsFixedFormat(0, pdf_file)
                
                if progress_callback:
                    progress_callback(90)
                
            finally:
                # 确保工作簿被正确关闭
                if workbook is not None:
                    try:
                        workbook.Close(False)
                    except:
                        pass
                    workbook = None
                
                # 确保Excel实例被正确退出
                if excel is not None:
                    try:
                        excel.Quit()
                    except:
                        pass
                    excel = None
                
                if progress_callback:
                    progress_callback(100)
            
            # 验证PDF文件是否成功生成
            if not os.path.exists(pdf_file):
                raise Exception("PDF文件未能成功生成")
            
            return pdf_file
            
        except Exception as e:
            self.logger.error(f"Error converting Excel to PDF: {str(e)}")
            raise Exception(f"转换Excel到PDF时出错: {str(e)}")
            
        finally:
            # 确保资源被释放
            if workbook is not None:
                try:
                    workbook.Close(False)
                except:
                    pass
            
            if excel is not None:
                try:
                    excel.Quit()
                except:
                    pass
            
            # 释放COM组件
            pythoncom.CoUninitialize()
    
    def add_image_to_pdf(self, pdf_file, image_file, position='right-bottom', output_pdf=None):
        """
        向PDF文件添加图片（如印章）
        
        参数:
            pdf_file (str): PDF文件路径
            image_file (str): 图片文件路径
            position (str): 图片位置，可选值：'right-bottom', 'right-top', 'left-bottom', 'left-top', 'center'
            output_pdf (str, optional): 输出PDF文件路径，如果为None则覆盖原文件
            
        返回:
            str: 生成的PDF文件路径
        """
        if output_pdf is None:
            output_pdf = pdf_file
        
        self.logger.info(f"开始向PDF添加图片: {pdf_file}")
        
        try:
            # 打开PDF文件
            pdf_document = fitz.open(pdf_file)
            
            # 打开图片
            img = fitz.open(image_file)
            rect = img[0].rect
            
            # 遍历所有页面
            for page_num in range(len(pdf_document)):
                page = pdf_document[page_num]
                
                # 获取页面尺寸
                page_width = page.rect.width
                page_height = page.rect.height
                
                # 计算图片位置
                if position == 'right-bottom':
                    x = page_width - rect.width - 50  # 右边距50点
                    y = page_height - rect.height - 50  # 下边距50点
                elif position == 'right-top':
                    x = page_width - rect.width - 50
                    y = 50
                elif position == 'left-bottom':
                    x = 50
                    y = page_height - rect.height - 50
                elif position == 'left-top':
                    x = 50
                    y = 50
                elif position == 'center':
                    x = (page_width - rect.width) / 2
                    y = (page_height - rect.height) / 2
                else:
                    # 默认右下角
                    x = page_width - rect.width - 50
                    y = page_height - rect.height - 50
                
                # 创建一个矩形区域来放置图片
                rect = fitz.Rect(x, y, x + rect.width, y + rect.height)
                
                # 将图片插入到页面
                page.insert_image(rect, filename=image_file)
            
            # 保存修改后的PDF
            pdf_document.save(output_pdf)
            pdf_document.close()
            
            self.logger.info(f"成功向PDF添加图片: {output_pdf}")
            return output_pdf
            
        except Exception as e:
            self.logger.error(f"向PDF添加图片时出错: {str(e)}")
            raise
    
    def convert_pdf_to_image_pdf(self, pdf_file, output_pdf=None, dpi=300):
        """
        将PDF转换为图片式PDF（每页转为图片再嵌入新PDF）
        这样可以确保印章等元素在任何PDF阅读器中都能正确显示
        
        参数:
            pdf_file (str): PDF文件路径
            output_pdf (str, optional): 输出PDF文件路径，如果为None则使用原文件名加后缀
            dpi (int): 图片分辨率，默认300
            
        返回:
            str: 生成的图片式PDF文件路径
        """
        if output_pdf is None:
            # 使用原文件名，但添加_image后缀
            output_pdf = os.path.splitext(pdf_file)[0] + '_image.pdf'
        
        self.logger.info(f"开始将PDF转换为图片式PDF: {pdf_file}")
        
        try:
            # 打开PDF文件
            pdf_document = fitz.open(pdf_file)
            
            # 创建一个新的PDF文档
            output_document = fitz.open()
            
            # 遍历所有页面
            for page_num in range(len(pdf_document)):
                page = pdf_document[page_num]
                
                # 将页面渲染为图片
                pix = page.get_pixmap(matrix=fitz.Matrix(dpi/72, dpi/72))
                
                # 创建一个新页面，大小与原页面相同
                new_page = output_document.new_page(width=page.rect.width, height=page.rect.height)
                
                # 将图片插入到新页面
                new_page.insert_image(new_page.rect, pixmap=pix)
            
            # 保存新的PDF文档
            output_document.save(output_pdf)
            output_document.close()
            pdf_document.close()
            
            self.logger.info(f"成功将PDF转换为图片式PDF: {output_pdf}")
            return output_pdf
            
        except Exception as e:
            self.logger.error(f"将PDF转换为图片式PDF时出错: {str(e)}")
            raise

# 测试代码
if __name__ == "__main__":
    converter = ExcelToPdfConverter()
    
    # 测试Excel转PDF
    excel_file = "test.xlsx"
    if os.path.exists(excel_file):
        pdf_file = converter.convert_to_pdf(excel_file)
        print(f"生成的PDF文件: {pdf_file}")
        
        # 测试添加印章
        seal_file = "seal.png"
        if os.path.exists(seal_file):
            pdf_with_seal = converter.add_image_to_pdf(pdf_file, seal_file)
            print(f"添加印章后的PDF文件: {pdf_with_seal}")
            
            # 测试转换为图片式PDF
            image_pdf = converter.convert_pdf_to_image_pdf(pdf_with_seal)
            print(f"生成的图片式PDF文件: {image_pdf}") 