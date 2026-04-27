from typing import Any
from fastapi import APIRouter, UploadFile, File, Request
from fastapi.responses import FileResponse
import shutil
import os
import uuid
from app.core.config import settings

router = APIRouter()

# Ensure upload directory exists
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)

@router.post("/upload")
def upload_file(
    request: Request,
    file: UploadFile = File(...)
) -> Any:
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
