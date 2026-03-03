"""
Document Parsers Module

Provides LangChain-based document parsers for various file types.
All parsers use official LangChain document loaders and text splitters.

Supported formats:
- PDF: PyPDFLoader (langchain_community)
- Markdown: TextLoader + MarkdownHeaderTextSplitter
- Word: Docx2txtLoader (langchain_community)
- Plain Text: TextLoader (langchain_community)
"""

from typing import Optional
from .base import BaseDocumentParser
from .pdf_parser import PDFParser
from .markdown_parser import MarkdownParser
from .word_parser import WordParser
from .text_parser import TextParser


class DocumentParserFactory:
    """
    Factory for creating document parsers with configurable text splitting

    All parsers support optional text splitting using LangChain's
    RecursiveCharacterTextSplitter for better RAG retrieval.
    """

    _parsers = {
        "application/pdf": PDFParser,
        "text/markdown": MarkdownParser,
        "text/plain": TextParser,
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document": WordParser,
    }

    @classmethod
    def get_parser(
        cls,
        filename: str,
        content_type: Optional[str] = None,
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
        enable_splitting: bool = True,
    ) -> Optional[BaseDocumentParser]:
        """
        Get appropriate parser for the document

        Args:
            filename: Document filename
            content_type: MIME content type
            chunk_size: Maximum size of text chunks (default: 1000)
            chunk_overlap: Overlap between chunks (default: 200)
            enable_splitting: Whether to split documents into chunks (default: True)

        Returns:
            Parser instance or None if not supported

        Example:
            >>> parser = DocumentParserFactory.get_parser(
            ...     "document.pdf",
            ...     chunk_size=1000,
            ...     chunk_overlap=200,
            ...     enable_splitting=True
            ... )
            >>> docs = parser.parse_from_file("document.pdf")
        """
        # Determine parser class
        parser_class = None

        # Try content type first
        if content_type:
            parser_class = cls._parsers.get(content_type)

        # Try filename extension
        if not parser_class and filename:
            ext = filename.lower().split('.')[-1]
            ext_map = {
                "pdf": PDFParser,
                "md": MarkdownParser,
                "markdown": MarkdownParser,
                "docx": WordParser,
                "doc": WordParser,
                "txt": TextParser,
                "text": TextParser,
            }
            parser_class = ext_map.get(ext)

        if not parser_class:
            return None

        # Create parser with text splitting configuration
        return parser_class(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            enable_splitting=enable_splitting
        )


__all__ = [
    "BaseDocumentParser",
    "PDFParser",
    "MarkdownParser",
    "WordParser",
    "TextParser",
    "DocumentParserFactory",
]
