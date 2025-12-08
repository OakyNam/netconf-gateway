"""
REST API endpoints for NETCONF gateway.
"""

from fastapi import APIRouter, HTTPException
from app.clients.client_factory import NCCClientFactory
router = APIRouter()

@router.get('/{device}/get-config')
def get_config(device: str):
    try:
        client = NCCClientFactory.get_client(device)
        config_data = client.get_config()
        return {"config": config_data}
    except ValueError as ve:
        raise HTTPException(status_code=404, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))