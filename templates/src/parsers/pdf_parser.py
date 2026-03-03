"""
PDF Document Parser

Uses LangChain's PyPDFLoader for PDF document loading.
"""

from typing import List
from langchain_core.documents import Document
from langchain_community.document_loaders import PyPDFLoader
from .base import BaseDocumentParser


class PDFParser(BaseDocumentParser):
    """
    Parser for PDF documents using LangChain's PyPDFLoader

    PyPDFLoader extracts text from PDF files and creates one Document per page.
    It works with text-based PDFs (selectable text).
    For scanned PDFs, consider using OCR tools like Tesseract.

    Official Docs: https://python.langchain.com/docs/modules/data_connection/document_loaders/pdf
    """

    def parse_from_file(self, file_path: str) -> List[Document]:
        """
        Parse PDF file using LangChain's PyPDFLoader

        Args:
            file_path: Path to PDF file

        Returns:
            List of Document objects (one per page)
            Each document has metadata with 'source' and 'page' keys

        Example:
            >>> parser = PDFParser(chunk_size=1000, chunk_overlap=200, enable_splitting=True)
            >>> docs = parser.parse_from_file("document.pdf")
            >>> print(f"Loaded {len(docs)} pages")
        """
        # Load PDF using LangChain's PyPDFLoader
        loader = PyPDFLoader(file_path)
        documents = loader.load()

        # Apply text splitting if enabled
        return self._split_documents(documents)
