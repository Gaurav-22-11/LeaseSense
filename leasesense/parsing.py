from __future__ import annotations

from pathlib import Path

import pypdfium2 as pdfium
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.document_converter import DocumentConverter, PdfFormatOption

from leasesense.config import settings
from leasesense.models import ParsedLease


def parse_pdf(path: Path) -> ParsedLease:
    docling_error: Exception | None = None
    text = ""
    try:
        text = _parse_with_docling(path)
    except Exception as exc:
        docling_error = exc
        text = _parse_with_pdfium(path)

    if not text.strip():
        message = (
            "LeaseSense could not extract text from this PDF locally. "
            "If this is a scanned lease, set ENABLE_OCR=true after installing "
            "Docling/RapidOCR model assets, or upload a text-based PDF."
        )
        if docling_error is not None:
            message = f"{message} Parser detail: {docling_error}"
        raise ValueError(message)

    return ParsedLease(text=text, source_name=path.name)


def _parse_with_docling(path: Path) -> str:
    pipeline_options = PdfPipelineOptions()
    pipeline_options.do_ocr = settings.enable_ocr
    pipeline_options.enable_remote_services = False

    converter = DocumentConverter(
        format_options={
            InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
        }
    )
    result = converter.convert(str(path))
    document = result.document

    try:
        return document.export_to_markdown()
    except AttributeError:
        return document.export_to_text()


def _parse_with_pdfium(path: Path) -> str:
    document = pdfium.PdfDocument(str(path))
    pages: list[str] = []
    for index in range(len(document)):
        page = document[index]
        textpage = page.get_textpage()
        page_text = textpage.get_text_range() or ""
        if page_text.strip():
            pages.append(f"## Page {index + 1}\n\n{page_text.strip()}")
        textpage.close()
        page.close()
    document.close()
    return "\n\n".join(pages)
