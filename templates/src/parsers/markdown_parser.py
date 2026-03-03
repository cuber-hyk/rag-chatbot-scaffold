"""
Markdown Document Parser

Uses LangChain's TextLoader and MarkdownHeaderTextSplitter for markdown processing.
"""

from typing import List
from langchain_core.documents import Document
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import MarkdownHeaderTextSplitter
from .base import BaseDocumentParser


class MarkdownParser(BaseDocumentParser):
    """
    Parser for Markdown documents using LangChain

    Uses TextLoader to load the file and MarkdownHeaderTextSplitter
    to split by headers (H1, H2, H3) for better semantic chunks.

    Official Docs: https://python.langchain.com/docs/modules/data_connection/document_transformers/text_splitters/markdown_header_text_splitter
    """

    # Headers to split on - standard markdown hierarchy
    HEADERS_TO_SPLIT_ON = [
        ("#", "Header 1"),
        ("##", "Header 2"),
        ("###", "Header 3"),
        ("####", "Header 4"),
    ]

    def parse_from_file(self, file_path: str) -> List[Document]:
        """
        Parse markdown file using LangChain's TextLoader and MarkdownHeaderTextSplitter

        Args:
            file_path: Path to markdown file

        Returns:
            List of Document objects split by markdown headers

        Example:
            >>> parser = MarkdownParser()
            >>> docs = parser.parse_from_file("README.md")
            >>> for doc in docs:
            ...     print(f"{doc.metadata.get('Header 1', 'No H1')}: {doc.page_content[:50]}...")
        """
        # Load markdown as text using LangChain's TextLoader
        loader = TextLoader(file_path, encoding="utf-8")
        documents = loader.load()

        # Split by markdown headers
        md_splitter = MarkdownHeaderTextSplitter(
            headers_to_split_on=self.HEADERS_TO_SPLIT_ON
        )

        # MarkdownHeaderTextSplitter works on raw text, not Document objects
        md_docs = md_splitter.split_text(documents[0].page_content)

        # Add source metadata
        for doc in md_docs:
            doc.metadata["source"] = file_path

        # Apply additional text splitting if enabled
        # Note: This further splits the header-based chunks
        if self.enable_splitting:
            return self._split_documents(md_docs)

        return md_docs
