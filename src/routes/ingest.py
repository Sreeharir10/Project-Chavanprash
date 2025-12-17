from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from app.ingestion.pipeline import IngestionPipeline

router = APIRouter()

class IngestRequest(BaseModel):
    repo_url: str

@router.post("/ingest")
async def ingest_repo(request: IngestRequest, background_tasks: BackgroundTasks):
    """
    Trigger the ingestion process for a GitHub repository.
    """
    pipeline = IngestionPipeline()
    
    # Run in background to avoid blocking
    background_tasks.add_task(pipeline.run, request.repo_url)
    
    return {"message": "Ingestion started in background", "repo_url": request.repo_url}
