from fastapi import FastAPI, UploadFile, File, HTTPException, Request
from fastapi.responses import FileResponse, JSONResponse
from pathlib import Path
import shutil
import os
from urllib.parse import quote_plus
import urllib.parse

app = FastAPI()

UPLOAD_DIRECTORY = "uploaded_files"
Path(UPLOAD_DIRECTORY).mkdir(parents=True, exist_ok=True)


@app.post("/files/")
async def upload_file(file: UploadFile = File(...)):
    file_path = os.path.join(UPLOAD_DIRECTORY, file.filename)
    with open(file_path, "wb") as f:
        shutil.copyfileobj(file.file, f)
    return {"filename": file.filename}


@app.api_route("/files/{file_id}", methods=['GET', 'HEAD'])
def download_file(file_id: str, request: Request):
    file_path = os.path.join(UPLOAD_DIRECTORY, file_id)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    method = request.method

    if method == 'GET':
        return FileResponse(file_path, media_type="application/octet-stream",
                            filename=file_id)

    if method == 'HEAD':
        content_disposition = f'attachment; filename="{urllib.parse.quote(file_id)}"'

        headers = {
            "Content-Length": str(os.path.getsize(file_path)),
            "Content-Disposition": content_disposition,
        }

        return JSONResponse(content={}, headers=headers)
