import os
import shutil
from fastapi import UploadFile
from datetime import datetime
import uuid
from app.config import settings

class StorageService:
    @staticmethod
    def save_upload_file(upload_file: UploadFile) -> str:
        """
        Saves a FastAPI UploadFile to the local disk and returns the relative file URL.
        """
        # Ensure the directory exists
        os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
        
        # Generate a unique filename to prevent overwriting
        file_extension = os.path.splitext(upload_file.filename)[1]
        unique_filename = f"{uuid.uuid4().hex}{file_extension}"
        
        file_path = os.path.join(settings.UPLOAD_DIR, unique_filename)
        
        # Save the file to disk
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(upload_file.file, buffer)
            
        # Return the public URL path
        return f"/{settings.UPLOAD_DIR}/{unique_filename}"