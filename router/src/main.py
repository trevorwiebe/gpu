#!/usr/bin/env python3

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import logging

from routers.users.me import library
from routers.users.me import node
from routers import completion
from routers import health

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()  # Output to stdout/stderr for Docker logs
    ]
)

app = FastAPI(title="Router", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, this needs to be changed the the prod url
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(completion.router)
app.include_router(library.router)
app.include_router(node.router)
app.include_router(health.router)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)