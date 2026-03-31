from bson import ObjectId
from dotenv import load_dotenv
from fastapi import FastAPI, File, HTTPException, Path, UploadFile

from .db.collections.files import create_file_document, files_collection
from .queue.q import q
from .queue.workers import process_file
from .utils.file import save_to_disk

load_dotenv()

app = FastAPI()


@app.get("/")
def root():
    return {"status": "ok"}


@app.get("/hello")
def hello():
    return {"status": "healthy"}


@app.get("/files/{file_id}")
async def get_file_by_id(file_id: str = Path(..., description="ID of the file")):
    if not ObjectId.is_valid(file_id):
        raise HTTPException(status_code=400, detail="Invalid file ID")

    db_file = await files_collection.find_one({"_id": ObjectId(file_id)})
    if db_file is None:
        raise HTTPException(status_code=404, detail="File not found")

    return {
        "_id": str(db_file["_id"]),
        "name": db_file["name"],
        "status": db_file["status"],
        "result": db_file.get("result"),
        "error": db_file.get("error"),
    }


@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")

    db_file = await files_collection.insert_one(
        document=create_file_document(name=file.filename, status="saving")
    )

    file_path = f"/mnt/uploads/{db_file.inserted_id}_{file.filename}"
    await save_to_disk(file=await file.read(), path=file_path)

    await files_collection.update_one(
        {"_id": db_file.inserted_id},
        {"$set": {"status": "queued", "file_path": file_path}},
    )

    q.enqueue(process_file, str(db_file.inserted_id), file_path)

    file_id = str(db_file.inserted_id)
    return {
        "file_id": file_id,
        "status": "queued",
        "status_url": f"/files/{file_id}",
    }
