import os
import uuid
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from app.routes.deps import get_current_user
from app.models.user import User
from app.config import BASE_URL

router = APIRouter(prefix="/upload", tags=["Upload"])

ALLOWED_EXT = {"png", "jpg", "jpeg", "webp"}


@router.post("/image")
async def upload_image(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
):
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file uploaded")

    ext = file.filename.split(".")[-1].lower()

    if ext not in ALLOWED_EXT:
        raise HTTPException(status_code=400, detail="Only png/jpg/jpeg/webp allowed")

    os.makedirs("storage/tmp", exist_ok=True)

    filename = f"{uuid.uuid4().hex}.{ext}"
    out_path = os.path.join("storage", "tmp", filename)

    contents = await file.read()

    with open(out_path, "wb") as f:
        f.write(contents)

    url = f"{BASE_URL}/storage/tmp/{filename}"

    return {"status": "ok", "image_url": url}
