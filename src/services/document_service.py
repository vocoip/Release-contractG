#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
文档服务层
统一封装合同/报价单生成与 Excel->PDF 能力，降低 UI 与底层工具耦合。
"""

from __future__ import annotations

from typing import Optional, TYPE_CHECKING

from src.models.contract import Contract

if TYPE_CHECKING:
    from src.utils.excel_handler import ExcelHandler


class DocumentService:
    """统一文档业务服务"""

    DOC_TYPE_CONTRACT = 0
    DOC_TYPE_QUOTE = 1

    def __init__(self, excel_handler: Optional["ExcelHandler"] = None):
        if excel_handler is not None:
            self.excel_handler = excel_handler
        else:
            from src.utils.excel_handler import ExcelHandler
            self.excel_handler = ExcelHandler()

    def get_output_folder(self) -> str:
        return self.excel_handler.get_contracts_folder()

    def list_templates(self, doc_type_id: int):
        if doc_type_id == self.DOC_TYPE_CONTRACT:
            return self.excel_handler.list_template_options("contract")
        if doc_type_id == self.DOC_TYPE_QUOTE:
            return self.excel_handler.list_template_options("quote")
        return [("builtin", "内置默认")]

    def export_builtin_default_templates(self):
        return self.excel_handler.export_builtin_default_templates()

    def generate_document(self, contract: Contract, doc_type_id: int):
        """根据文档类型生成合同或报价单"""
        if doc_type_id == self.DOC_TYPE_CONTRACT:
            return self.excel_handler.generate_contract_only(contract)
        if doc_type_id == self.DOC_TYPE_QUOTE:
            return self.excel_handler.generate_quote_only(contract)
        raise ValueError(f"不支持的文档类型: {doc_type_id}")

    def convert_excel_to_pdf(
        self,
        excel_file: str,
        pdf_file: Optional[str] = None,
        progress_callback=None,
        ensure_a4: bool = True,
        as_image_pdf: bool = False,
        dpi: int = 150,
        quality: int = 60,
    ) -> str:
        """
        将 Excel 转为 PDF，并可选转为图片式 PDF。
        """
        output_pdf = pdf_file or (excel_file.rsplit(".", 1)[0] + ".pdf")
        converted_pdf = self.excel_handler.convert_excel_to_pdf(
            excel_file=excel_file,
            progress_callback=progress_callback,
        )

        # 若调用方指定了输出路径，确保最终文件名与调用方一致
        if converted_pdf != output_pdf:
            import os
            if os.path.exists(output_pdf):
                os.remove(output_pdf)
            os.replace(converted_pdf, output_pdf)
            converted_pdf = output_pdf

        if ensure_a4:
            converted_pdf = self.excel_handler.ensure_a4_size_pdf(converted_pdf)

        if as_image_pdf:
            image_pdf = output_pdf.replace(".pdf", "_image.pdf")
            converted_pdf = self.excel_handler.convert_pdf_to_image_pdf(
                pdf_file=converted_pdf,
                output_pdf=image_pdf,
                dpi=dpi,
                quality=quality,
            )

        return converted_pdf
