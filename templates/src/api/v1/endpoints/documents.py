"""
Document API Endpoints
"""

from fastapi import APIRouter, UploadFile, File, Depends, Query
from typing import Literal
from src.api.dependencies import get_document_service
from src.core.security.api_key import verify_api_key
from src.models.schemas.document import (
    DocumentUploadResponse,
    DocumentListResponse,
    DocumentDeleteResponse
)

router = APIRouter()


@router.post("", response_model=DocumentUploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    on_conflict: Literal["error", "replace", "skip"] = Query(
        "error",
        description="How to handle filename conflicts: error (return info), replace (overwrite), skip (ignore)"
    ),
    document_service = Depends(get_document_service),
    _: str = Depends(verify_api_key)
):
    """
    Upload and process a document with deduplication

    Args:
        file: Uploaded document file
        on_conflict: How to handle conflicts
            - error: Return conflict info (default)
            - replace: Delete existing and replace
            - skip: Skip upload if duplicate exists
        document_service: Document service instance

    Returns:
        Upload response with document ID or conflict info

    Conflicts:
        - duplicate_content: Same content already exists (different filename)
        - filename_conflict: Same filename exists but different content
    """
    # Validate file size
    content = await file.read()

    # Process the document
    result = await document_service.process_document(
        filename=file.filename,
        content=content,
        content_type=file.content_type,
        on_conflict=on_conflict
    )

    return DocumentUploadResponse(**result)


@router.get("", response_model=DocumentListResponse)
async def list_documents(
    document_service = Depends(get_document_service),
    _: str = Depends(verify_api_key)
):
    """
    List all uploaded documents

    Returns:
        List of documents with metadata
    """
    documents = await document_service.list_documents()
    return DocumentListResponse(documents=documents)


@router.delete("/{document_id}", response_model=DocumentDeleteResponse)
async def delete_document(
    document_id: str,
    document_service = Depends(get_document_service),
    _: str = Depends(verify_api_key)
):
    """
    Delete a document

    Args:
        document_id: ID of the document to delete

    Returns:
        Deletion response
    """
    success = await document_service.delete_document(document_id)
    return DocumentDeleteResponse(
        success=success,
        message="Document deleted successfully" if success else "Document not found"
    )
