from typing import Any
from fastapi import APIRouter, UploadFile, File, Request, HTTPException, status
import shutil
import os
import uuid
from app.core.config import settings

router = APIRouter()

MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB
ALLOWED_MIME_TYPES = ["image/jpeg", "image/png", "image/webp"]

# Ensure upload directory exists
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)

@router.post("/upload")
def upload_file(
    request: Request,
    file: UploadFile = File(...)
) -> Any:
    if file.content_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type {file.content_type} not allowed. Allowed types are: {', '.join(ALLOWED_MIME_TYPES)}"
        )
    
    file.file.seek(0, 2)
    file_size = file.file.tell()
    file.file.seek(0)
    
    if file_size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File size exceeds the maximum limit of 5MB."
        )
    # Generate unique filename
    extension = os.path.splitext(file.filename)[1] if file.filename else ""
    filename = f"{uuid.uuid4()}{extension}"
    file_path = os.path.join(settings.UPLOAD_DIR, filename)
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    # Construct URL
    base_url = str(request.base_url).rstrip("/")
    # Java returns: http://localhost:8081/uploads/filename
    # My python app might serve statics or I return path relative.
    # User can configure serving.
    # Assuming standard serving at /uploads
    
    url = f"{base_url}/{settings.UPLOAD_DIR}/{filename}"
    
    return {"url": url, "filename": filename}
