from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from app.ingestion.pipeline import IngestionPipeline
import os
from app.core.config import settings

router = APIRouter()

class IngestRequest(BaseModel):
    repo_url: str
    temp_dir: str = None
    sync: bool = False

@router.post("/ingest")
async def ingest_repo(request: IngestRequest, background_tasks: BackgroundTasks):
    """
    Trigger the ingestion process for a GitHub repository.
    """
    pipeline = IngestionPipeline()
    temp_dir = request.temp_dir or settings.REPO_STORAGE_PATH
    if request.sync:
        # Run synchronously for testing/debug
        result = pipeline.run(request.repo_url, temp_dir=temp_dir)
        return {"message": "Ingestion completed", "result": result}
    else:
        # Run in background to avoid blocking
        background_tasks.add_task(pipeline.run, request.repo_url, temp_dir)
        return {"message": "Ingestion started in background", "repo_url": request.repo_url, "temp_dir": temp_dir}
