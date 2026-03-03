"""
Plain Text Document Parser

Uses LangChain's TextLoader for plain text document loading.
"""

from typing import List
from langchain_core.documents import Document
from langchain_community.document_loaders import TextLoader
from .base import BaseDocumentParser


class TextParser(BaseDocumentParser):
    """
    Parser for plain text documents using LangChain's TextLoader

    TextLoader loads any text file with proper encoding handling.
    Supports UTF-8, UTF-16, Latin-1, and other encodings.

    Official Docs: https://python.langchain.com/docs/modules/data_connection/document_loaders/text
    """

    def __init__(self, encoding: str = "utf-8", **kwargs):
        """
        Initialize text parser

        Args:
            encoding: Text encoding (default: "utf-8")
            **kwargs: Additional arguments for BaseDocumentParser
        """
        super().__init__(**kwargs)
        self.encoding = encoding

    def parse_from_file(self, file_path: str) -> List[Document]:
        """
        Parse text file using LangChain's TextLoader

        Args:
            file_path: Path to text file

        Returns:
            List of Document objects

        Example:
            >>> parser = TextParser(chunk_size=1000, chunk_overlap=200, enable_splitting=True)
            >>> docs = parser.parse_from_file("document.txt")
            >>> print(f"Loaded {len(docs)} chunks")
        """
        # Load text using LangChain's TextLoader
        loader = TextLoader(file_path, encoding=self.encoding)
        documents = loader.load()

        # Apply text splitting if enabled
        return self._split_documents(documents)
