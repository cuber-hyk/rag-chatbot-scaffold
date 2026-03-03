"""
Document Service

Handles document upload, parsing, and indexing using LangChain parsers.
"""

import uuid
import hashlib
import tempfile
from pathlib import Path
from typing import Dict, List, Optional, Literal
from langchain_core.documents import Document as LangChainDocument
from src.repositories.vector_repository import VectorRepository
from src.parsers import DocumentParserFactory
from src.core.config.settings import get_settings


class DocumentService:
    """
    Service for document operations

    Uses LangChain-based parsers for document loading and text splitting.
    All parsers support:
    - Official LangChain document loaders
    - Optional text splitting with RecursiveCharacterTextSplitter
    - Proper metadata preservation
    """

    def __init__(self, vector_repo: VectorRepository):
        self.vector_repo = vector_repo
        self.settings = get_settings()

    async def process_document(
        self,
        filename: str,
        content: bytes,
        content_type: str,
        chunk_size: Optional[int] = None,
        chunk_overlap: Optional[int] = None,
        on_conflict: Literal["error", "replace", "skip"] = "error",
    ) -> Dict:
        """
        Process and index a document with deduplication

        Args:
            filename: Document filename
            content: Document content (bytes)
            content_type: MIME type
            chunk_size: Override default chunk size
            chunk_overlap: Override default chunk overlap
            on_conflict: How to handle filename conflicts
                - "error": Return error info (default)
                - "replace": Delete old document and replace
                - "skip": Skip upload if duplicate exists

        Returns:
            Result with document_id, chunks_added, and conflict_info if any

        Example:
            >>> result = await document_service.process_document(
            ...     "document.pdf",
            ...     file_content,
            ...     "application/pdf",
            ...     on_conflict="replace"
            ... )
        """
        # Calculate content hash for deduplication
        content_hash = hashlib.sha256(content).hexdigest()

        # Check for conflicts
        conflict_info = await self._check_conflicts(filename, content_hash)
        if conflict_info:
            # Hash same = exact duplicate content
            if conflict_info["type"] == "duplicate_content":
                return {
                    "success": False,
                    "error": "duplicate_content",
                    "message": f"文档 '{filename}' 的内容已存在（文件名: {conflict_info['existing_filename']}）",
                    "existing_document_id": conflict_info["document_id"],
                }

            # Filename exists but different content
            if conflict_info["type"] == "filename_conflict":
                if on_conflict == "error":
                    return {
                        "success": False,
                        "error": "filename_conflict",
                        "message": f"文件名 '{filename}' 已存在但内容不同。请选择：覆盖（on_conflict='replace'）或修改文件名",
                        "existing_document_id": conflict_info["document_id"],
                    }
                elif on_conflict == "skip":
                    return {
                        "success": False,
                        "error": "skipped",
                        "message": f"跳过上传：文件名 '{filename}' 已存在",
                        "existing_document_id": conflict_info["document_id"],
                    }
                elif on_conflict == "replace":
                    # Delete old document
                    await self.delete_document(conflict_info["document_id"])

        # Check file size
        size_mb = len(content) / (1024 * 1024)
        if size_mb > self.settings.max_file_size_mb:
            raise ValueError(
                f"File size exceeds maximum of {self.settings.max_file_size_mb}MB"
            )

        # Get parser with text splitting enabled
        chunk_size = chunk_size or self.settings.chunk_size
        chunk_overlap = chunk_overlap or self.settings.chunk_overlap

        parser = DocumentParserFactory.get_parser(
            filename=filename,
            content_type=content_type,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            enable_splitting=True,
        )

        if not parser:
            raise ValueError(f"Unsupported file type: {content_type}")

        # Parse document with text splitting
        # Save to temp file since LangChain loaders work with file paths
        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=Path(filename).suffix
        ) as temp_file:
            temp_file.write(content)
            temp_path = temp_file.name

        try:
            # Parse and split in one operation
            documents = parser.parse_from_file(temp_path)

            # Enhance metadata with document tracking
            document_id = str(uuid.uuid4())
            total_chunks = len(documents)

            enhanced_docs = []
            for i, doc in enumerate(documents):
                # Create enhanced metadata
                metadata = {
                    "document_id": document_id,
                    "filename": filename,
                    "chunk_index": i,
                    "chunk_count": total_chunks,
                    "content_hash": content_hash,
                }

                # Preserve original metadata from parser
                metadata.update(doc.metadata)

                enhanced_docs.append(LangChainDocument(
                    page_content=doc.page_content,
                    metadata=metadata
                ))

            # Add to vector store
            chunks_added = await self.vector_repo.add_documents(
                documents=enhanced_docs,
                collection_name=self.settings.vector_db_collection
            )

            return {
                "success": True,
                "document_id": document_id,
                "chunks_added": chunks_added,
                "filename": filename,
                "content_type": content_type,
                "message": "Document processed successfully",
            }

        finally:
            # Clean up temp file
            Path(temp_path).unlink(missing_ok=True)

    async def process_document_file(
        self,
        file_path: str,
        content_type: Optional[str] = None,
        chunk_size: Optional[int] = None,
        chunk_overlap: Optional[int] = None,
    ) -> Dict:
        """
        Process and index a document from file path

        This is the preferred method when file is already on disk.

        Args:
            file_path: Path to document file
            content_type: MIME type (auto-detected from filename if not provided)
            chunk_size: Override default chunk size
            chunk_overlap: Override default chunk overlap

        Returns:
            Result with document_id and chunks_added

        Example:
            >>> result = await document_service.process_document_file(
            ...     "/path/to/document.pdf"
            ... )
        """
        filename = Path(file_path).name

        # Get parser with text splitting enabled
        chunk_size = chunk_size or self.settings.chunk_size
        chunk_overlap = chunk_overlap or self.settings.chunk_overlap

        parser = DocumentParserFactory.get_parser(
            filename=filename,
            content_type=content_type,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            enable_splitting=True,
        )

        if not parser:
            raise ValueError(f"Unsupported file type: {filename}")

        # Parse and split in one operation
        documents = parser.parse_from_file(file_path)

        # Enhance metadata with document tracking
        document_id = str(uuid.uuid4())
        total_chunks = len(documents)

        enhanced_docs = []
        for i, doc in enumerate(documents):
            metadata = {
                "document_id": document_id,
                "filename": filename,
                "chunk_index": i,
                "chunk_count": total_chunks,
            }
            metadata.update(doc.metadata)

            enhanced_docs.append(LangChainDocument(
                page_content=doc.page_content,
                metadata=metadata
            ))

        # Add to vector store
        chunks_added = await self.vector_repo.add_documents(
            documents=enhanced_docs,
            collection_name=self.settings.vector_db_collection
        )

        return {
            "document_id": document_id,
            "chunks_added": chunks_added,
            "filename": filename,
            "file_path": file_path,
        }

    async def list_documents(self) -> List[Dict]:
        """
        List all unique documents in the vector store

        Returns:
            List of document summaries with document_id, filename, chunk_count

        Example:
            >>> docs = await document_service.list_documents()
            >>> for doc in docs:
            ...     print(f"{doc['filename']}: {doc['chunk_count']} chunks")
        """
        # Use the vector repository's list_documents method
        # This requires the repository to implement this method
        if hasattr(self.vector_repo, 'list_documents'):
            return await self.vector_repo.list_documents(
                collection_name=self.settings.vector_db_collection
            )
        return []

    async def delete_document(self, document_id: str) -> bool:
        """
        Delete a document and all its chunks

        Args:
            document_id: Document ID to delete

        Returns:
            True if deleted successfully

        Example:
            >>> success = await document_service.delete_document("uuid-123")
            >>> print(f"Deleted: {success}")
        """
        # Use the vector repository's delete_document method
        if hasattr(self.vector_repo, 'delete_document'):
            return await self.vector_repo.delete_document(
                document_id=document_id,
                collection_name=self.settings.vector_db_collection
            )
        return False

    async def get_document_chunks(self, document_id: str) -> List[LangChainDocument]:
        """
        Get all chunks for a specific document

        Args:
            document_id: Document ID

        Returns:
            List of document chunks

        Example:
            >>> chunks = await document_service.get_document_chunks("uuid-123")
            >>> print(f"Document has {len(chunks)} chunks")
        """
        if hasattr(self.vector_repo, 'get_document_chunks'):
            return await self.vector_repo.get_document_chunks(
                document_id=document_id,
                collection_name=self.settings.vector_db_collection
            )
        return []

    async def count_documents(self) -> int:
        """
        Count the number of unique documents in the collection

        Returns:
            Number of unique documents
        """
        if hasattr(self.vector_repo, 'count_documents'):
            return await self.vector_repo.count_documents(
                collection_name=self.settings.vector_db_collection
            )
        return 0

    async def count_chunks(self) -> int:
        """
        Count the total number of chunks in the collection

        Returns:
            Total number of chunks
        """
        if hasattr(self.vector_repo, 'count_chunks'):
            return await self.vector_repo.count_chunks(
                collection_name=self.settings.vector_db_collection
            )
        return 0

    async def delete_collection(self) -> bool:
        """
        Delete the entire document collection

        Returns:
            True if deleted successfully
        """
        return await self.vector_repo.delete_collection(
            self.settings.vector_db_collection
        )

    async def _check_conflicts(
        self,
        filename: str,
        content_hash: str
    ) -> Optional[Dict[str, str]]:
        """
        Check for document conflicts

        Args:
            filename: Document filename
            content_hash: SHA256 hash of content

        Returns:
            None if no conflict, otherwise dict with conflict info:
            {
                "type": "filename_conflict" | "duplicate_content",
                "document_id": "...",
                "existing_filename": "..."
            }
        """
        # Check if filename already exists
        existing_by_filename = await self.vector_repo.find_by_filename(
            filename=filename,
            collection_name=self.settings.vector_db_collection
        )

        # Check if content hash already exists
        existing_by_hash = await self.vector_repo.find_by_content_hash(
            content_hash=content_hash,
            collection_name=self.settings.vector_db_collection
        )

        # Same filename and same hash - exact duplicate
        if existing_by_filename and existing_by_hash:
            if existing_by_filename["document_id"] == existing_by_hash["document_id"]:
                return {
                    "type": "duplicate_content",
                    "document_id": existing_by_filename["document_id"],
                    "existing_filename": existing_by_filename["filename"],
                }

        # Same filename but different content
        if existing_by_filename:
            return {
                "type": "filename_conflict",
                "document_id": existing_by_filename["document_id"],
                "existing_filename": existing_by_filename["filename"],
            }

        # Different filename but same content
        if existing_by_hash:
            return {
                "type": "duplicate_content",
                "document_id": existing_by_hash["document_id"],
                "existing_filename": existing_by_hash["filename"],
            }

        return None
