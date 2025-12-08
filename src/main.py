# backend/app/main.py

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
import time
import traceback
import logging
import inspect

# NEW: Import your logger instance
from app.core.logger import logs



app = FastAPI(
    title="Self Healer backend",
    description="This is the backend for my full-stack application.",
    version="1.0.0",
)
#Middleware to log every request
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    
    # Log the incoming request
    logs.define_logger(level=logging.INFO, request=request, message="Request received")
    
    response = await call_next(request)
    
    process_time = (time.time() - start_time) * 1000
    formatted_process_time = f'{process_time:.2f}ms'
    
    # Log the response
    logs.define_logger(
        level=logging.INFO,
        request=request,
        message=f"Request completed in {formatted_process_time} - Status: {response.status_code}",
    )
    
    return response


# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Temporarily allow all origins for debugging
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



@app.get("/")
def read_root():
    return {"status": "Healer API is running"}