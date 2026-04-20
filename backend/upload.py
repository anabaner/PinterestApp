import os
import uuid
from PIL import Image
from fastapi import UploadFile, HTTPException

UPLOAD_DIR = "static/uploads"
ALLOWED_TYPES = {"image/jpeg", "image/png", "image/webp", "image/gif"}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB
PIN_WIDTH = 600  # resize all pins to this width


def generate_filename(original_filename: str) -> str:
    ext = os.path.splitext(original_filename)[-1].lower()  # e.g. .jpg
    return f"{uuid.uuid4().hex}{ext}"                      # e.g. a3f9c12d....jpg


async def save_upload(file: UploadFile) -> str:
    # 1. Check file type
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"File type '{file.content_type}' not allowed. Use JPEG, PNG, WEBP or GIF."
        )

    # 2. Read file contents into memory
    contents = await file.read()

    # 3. Check file size
    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail="File too large. Maximum size is 5MB."
        )

    # 4. Generate a unique filename and build the save path
    filename = generate_filename(file.filename)
    save_path = os.path.join(UPLOAD_DIR, filename)

    # 5. Open with Pillow, resize to standard width, save
    from io import BytesIO
    image = Image.open(BytesIO(contents))
    image = image.convert("RGB")  # normalize (handles PNG transparency etc.)

    # Resize: keep aspect ratio, fix width to PIN_WIDTH
    original_width, original_height = image.size
    new_height = int((PIN_WIDTH / original_width) * original_height)
    image = image.resize((PIN_WIDTH, new_height), Image.LANCZOS)

    image.save(save_path, optimize=True, quality=85)

    # 6. Return the public URL path
    return f"/static/uploads/{filename}"