"""
Document API Endpoints
"""

from fastapi import APIRouter, UploadFile, File, Depends
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
    document_service = Depends(get_document_service),
    _: str = Depends(verify_api_key)
):
    """
    Upload and process a document

    Args:
        file: Uploaded document file
        document_service: Document service instance

    Returns:
        Upload response with document ID
    """
    # Validate file size
    content = await file.read()

    # Process the document
    result = await document_service.process_document(
        filename=file.filename,
        content=content,
        content_type=file.content_type
    )

    return DocumentUploadResponse(
        document_id=result["document_id"],
        chunks_added=result["chunks_added"],
        message="Document processed successfully"
    )


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
