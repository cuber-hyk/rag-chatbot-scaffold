"""
Base Document Parser

Defines the interface for document parsers with LangChain integration.
"""

from abc import ABC, abstractmethod
from typing import List, Optional
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter


class BaseDocumentParser(ABC):
    """
    Base class for document parsers using LangChain loaders and splitters

    All parsers should:
    1. Use LangChain document loaders from langchain_community
    2. Support optional text splitting with RecursiveCharacterTextSplitter
    3. Return List[Document] with proper metadata
    """

    def __init__(
        self,
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
        enable_splitting: bool = False
    ):
        """
        Initialize parser with text splitting configuration

        Args:
            chunk_size: Maximum size of text chunks (default: 1000)
            chunk_overlap: Overlap between chunks (default: 200)
            enable_splitting: Whether to split documents into chunks
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.enable_splitting = enable_splitting
        self._text_splitter: Optional[RecursiveCharacterTextSplitter] = None

    @property
    def text_splitter(self) -> RecursiveCharacterTextSplitter:
        """
        Lazy initialization of text splitter

        Returns:
            RecursiveCharacterTextSplitter instance
        """
        if self._text_splitter is None:
            self._text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=self.chunk_size,
                chunk_overlap=self.chunk_overlap,
                length_function=len,
                is_separator_regex=False,
            )
        return self._text_splitter

    @abstractmethod
    def parse_from_file(self, file_path: str) -> List[Document]:
        """
        Parse document from file path using LangChain document loaders

        This is the preferred method for document parsing.

        Args:
            file_path: Path to document file

        Returns:
            List of Document objects with metadata
        """
        pass

    def _split_documents(self, documents: List[Document]) -> List[Document]:
        """
        Split documents into chunks if splitting is enabled

        Args:
            documents: List of documents to split

        Returns:
            List of split documents or original documents
        """
        if not self.enable_splitting:
            return documents

        return self.text_splitter.split_documents(documents)
