#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import tempfile
import unittest

from src.services.document_service import DocumentService


class _FakeExcelHandler:
    def __init__(self):
        self.calls = []
        self.output_folder = "/tmp/fake-output"
        self.convert_result_path = None

    def get_contracts_folder(self):
        self.calls.append(("get_contracts_folder",))
        return self.output_folder

    def generate_contract_only(self, contract):
        self.calls.append(("generate_contract_only", contract))
        return "contract.xlsx"

    def generate_quote_only(self, contract):
        self.calls.append(("generate_quote_only", contract))
        return "quote.xlsx"

    def convert_excel_to_pdf(self, excel_file, progress_callback=None):
        self.calls.append(("convert_excel_to_pdf", excel_file, progress_callback is not None))
        if self.convert_result_path is None:
            self.convert_result_path = os.path.splitext(excel_file)[0] + ".pdf"
        os.makedirs(os.path.dirname(self.convert_result_path), exist_ok=True)
        with open(self.convert_result_path, "w", encoding="utf-8") as fp:
            fp.write("pdf")
        return self.convert_result_path

    def ensure_a4_size_pdf(self, pdf_file):
        self.calls.append(("ensure_a4_size_pdf", pdf_file))
        return pdf_file

    def convert_pdf_to_image_pdf(self, pdf_file, output_pdf=None, dpi=150, quality=60):
        self.calls.append(("convert_pdf_to_image_pdf", pdf_file, output_pdf, dpi, quality))
        target = output_pdf or os.path.splitext(pdf_file)[0] + "_image.pdf"
        with open(target, "w", encoding="utf-8") as fp:
            fp.write("image_pdf")
        return target


class DocumentServiceTests(unittest.TestCase):
    def test_generate_document_route_contract(self):
        fake = _FakeExcelHandler()
        service = DocumentService(excel_handler=fake)
        marker = object()

        result = service.generate_document(marker, DocumentService.DOC_TYPE_CONTRACT)

        self.assertEqual(result, "contract.xlsx")
        self.assertIn(("generate_contract_only", marker), fake.calls)

    def test_generate_document_route_quote(self):
        fake = _FakeExcelHandler()
        service = DocumentService(excel_handler=fake)
        marker = object()

        result = service.generate_document(marker, DocumentService.DOC_TYPE_QUOTE)

        self.assertEqual(result, "quote.xlsx")
        self.assertIn(("generate_quote_only", marker), fake.calls)

    def test_generate_document_invalid_doc_type(self):
        service = DocumentService(excel_handler=_FakeExcelHandler())
        with self.assertRaises(ValueError):
            service.generate_document(object(), 999)

    def test_convert_excel_to_pdf_with_target_path_and_image(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            fake = _FakeExcelHandler()
            src_pdf = os.path.join(tmpdir, "source.pdf")
            fake.convert_result_path = src_pdf
            service = DocumentService(excel_handler=fake)

            excel_file = os.path.join(tmpdir, "demo.xlsx")
            with open(excel_file, "w", encoding="utf-8") as fp:
                fp.write("xlsx")

            target_pdf = os.path.join(tmpdir, "target.pdf")
            result = service.convert_excel_to_pdf(
                excel_file=excel_file,
                pdf_file=target_pdf,
                as_image_pdf=True,
                dpi=120,
                quality=70,
            )

            self.assertEqual(result, os.path.join(tmpdir, "target_image.pdf"))
            self.assertTrue(os.path.exists(target_pdf))
            self.assertTrue(os.path.exists(result))
            self.assertIn(("ensure_a4_size_pdf", target_pdf), fake.calls)
            self.assertIn(
                ("convert_pdf_to_image_pdf", target_pdf, os.path.join(tmpdir, "target_image.pdf"), 120, 70),
                fake.calls,
            )


if __name__ == "__main__":
    unittest.main()

