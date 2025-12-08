
"""
Main entrypoint for the NETCONF API Gateway.

Initializes logging, creates the FastAPI app, and includes the root router.
"""

from fastapi import FastAPI
from app.routes import router
from app.logging import setup_logging_from_json

# Initialize logging from JSON config
setup_logging_from_json()

app = FastAPI()
app.include_router(router)
