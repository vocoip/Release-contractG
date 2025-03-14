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
from PyPDF2 import PdfReader, PdfWriter
import fitz  # PyMuPDF

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
    
    def convert_to_pdf(self, excel_file, pdf_file=None, fit_to_page=True, paper_size=9):
        """
        将Excel文件转换为PDF
        
        参数:
            excel_file (str): Excel文件路径
            pdf_file (str, optional): 输出PDF文件路径，如果为None则使用Excel文件名
            fit_to_page (bool): 是否适应页面大小，默认为True
            paper_size (int): 纸张大小，9表示A4纸张
            
        返回:
            str: 生成的PDF文件路径
        """
        if pdf_file is None:
            # 使用Excel文件名，但扩展名改为.pdf
            pdf_file = os.path.splitext(excel_file)[0] + '.pdf'
        
        self.logger.info(f"开始转换Excel文件: {excel_file} 到 PDF: {pdf_file}")
        
        try:
            # 初始化COM
            pythoncom.CoInitialize()
            
            # 创建Excel应用程序实例
            excel = win32com.client.Dispatch("Excel.Application")
            excel.Visible = False  # 不显示Excel窗口
            excel.DisplayAlerts = False  # 不显示警告
            
            # 打开工作簿
            self.logger.info(f"打开工作簿: {excel_file}")
            workbook = excel.Workbooks.Open(os.path.abspath(excel_file))
            
            # 遍历所有工作表，设置打印区域和页面设置
            for i in range(1, workbook.Worksheets.Count + 1):
                worksheet = workbook.Worksheets(i)
                
                # 设置页面设置
                worksheet.PageSetup.Zoom = False  # 禁用缩放
                if fit_to_page:
                    worksheet.PageSetup.FitToPagesWide = 1  # 宽度适应1页
                    worksheet.PageSetup.FitToPagesTall = 1  # 高度适应1页
                
                # 设置纸张大小 (9 = A4)
                worksheet.PageSetup.PaperSize = paper_size
                
                # 设置页边距（厘米）
                worksheet.PageSetup.LeftMargin = excel.CentimetersToPoints(1.5)
                worksheet.PageSetup.RightMargin = excel.CentimetersToPoints(1.5)
                worksheet.PageSetup.TopMargin = excel.CentimetersToPoints(1.5)
                worksheet.PageSetup.BottomMargin = excel.CentimetersToPoints(1.5)
                
                # 设置页眉页脚
                worksheet.PageSetup.LeftHeader = ""
                worksheet.PageSetup.CenterHeader = ""
                worksheet.PageSetup.RightHeader = ""
                worksheet.PageSetup.LeftFooter = ""
                worksheet.PageSetup.CenterFooter = ""
                worksheet.PageSetup.RightFooter = ""
                
                # 设置打印方向（1=纵向，2=横向）
                worksheet.PageSetup.Orientation = 1
            
            # 导出为PDF
            self.logger.info(f"导出为PDF: {pdf_file}")
            workbook.ExportAsFixedFormat(0, os.path.abspath(pdf_file))
            
            # 关闭工作簿
            workbook.Close(False)
            
            # 退出Excel
            excel.Quit()
            
            self.logger.info(f"Excel文件成功转换为PDF: {pdf_file}")
            return pdf_file
            
        except Exception as e:
            self.logger.error(f"转换Excel到PDF时出错: {str(e)}")
            raise
        finally:
            # 释放COM资源
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