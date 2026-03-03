"""
Word Document Parser

Uses LangChain's Docx2txtLoader for Word document loading.
"""

from typing import List
from langchain_core.documents import Document
from langchain_community.document_loaders import Docx2txtLoader
from .base import BaseDocumentParser


class WordParser(BaseDocumentParser):
    """
    Parser for Word documents (.docx) using LangChain's Docx2txtLoader

    Docx2txtLoader is a lightweight Word document loader that uses
    the docx2txt library for text extraction. It's fast, has minimal
    dependencies, and works well with multi-language documents including Chinese.

    For more complex document structures, consider using UnstructuredWordDocumentLoader.

    Official Docs: https://python.langchain.com/docs/modules/data_connection/document_loaders/word

    Installation:
        pip install docx2txt
    """

    def parse_from_file(self, file_path: str) -> List[Document]:
        """
        Parse Word file using LangChain's Docx2txtLoader

        Args:
            file_path: Path to Word file (.docx)

        Returns:
            List of Document objects

        Example:
            >>> parser = WordParser(chunk_size=1000, chunk_overlap=200, enable_splitting=True)
            >>> docs = parser.parse_from_file("document.docx")
            >>> print(f"Loaded {len(docs)} chunks")
        """
        # Load Word document using LangChain's Docx2txtLoader
        loader = Docx2txtLoader(file_path)
        documents = loader.load()

        # Apply text splitting if enabled
        return self._split_documents(documents)
