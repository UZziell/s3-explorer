from domain.use_cases.bucket_use_cases import BucketUseCases
from domain.use_cases.object_use_cases import ObjectUseCases
from adapters.boto3_s3_repository import Boto3S3Repository

import shutil
import os

from fastapi import FastAPI, Path, APIRouter, File, UploadFile

repository = Boto3S3Repository()
bucket_use_cases = BucketUseCases(repository)
object_use_cases = ObjectUseCases(repository)


router = APIRouter()

@router.get("/buckets")
async def get_buckets():
    return {"buckets": bucket_use_cases.get_buckets()}

@router.get("/buckets/{bucket_name}")
async def get_objects(bucket_name: str = Path(..., min_length=1)):
    return { "bucket": f"bucket_name",
        "objects": object_use_cases.get_objects(bucket_name)}

@router.put("/buckets/{bucket_name}/upload")
async def put_object(bucket_name: str = Path(..., min_length=1), file: UploadFile = File(...)):
    contents = await file.read()
    file.file.seek(0)
    UPLOAD_DIR = "/tmp/uploads"
    os.makedirs(UPLOAD_DIR, exist_ok=True)  # Create the folder if it doesn't exist
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    return {
        "result": object_use_cases.put_object(bucket_name, file_path)}

app = FastAPI()
app.include_router(router)
