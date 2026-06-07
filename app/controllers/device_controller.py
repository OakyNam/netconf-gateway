"""Unified device controller with factory-based client dispatch."""

from typing import Dict, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.errors import ClientMappingError, DeviceNotFoundError, GatewayError
from app.factories.client_factory import NCCClientFactory

router = APIRouter()


class XmlPayload(BaseModel):
    config_xml: str


@router.get("/{device}/show-interface")
def show_interface(device: str, interface_name: Optional[str] = None) -> Dict[str, str]:
    try:
        client = NCCClientFactory.get_client(device)
        return client.show_interface(interface_name=interface_name)
    except DeviceNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except ClientMappingError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except GatewayError as exc:
        raise HTTPException(status_code=502, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.get("/{device}/config")
def get_device_config(device: str) -> Dict[str, str]:
    try:
        client = NCCClientFactory.get_client(device)
        return {"config": client.get_config()}
    except DeviceNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except ClientMappingError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except GatewayError as exc:
        raise HTTPException(status_code=502, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.put("/{device}/config")
def set_device_config(device: str, payload: XmlPayload) -> Dict[str, str]:
    try:
        client = NCCClientFactory.get_client(device)
        return client.set_config(payload.config_xml)
    except DeviceNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except ClientMappingError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except GatewayError as exc:
        raise HTTPException(status_code=502, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.put("/{device}/interfaces/{interface_name}")
def configure_interface(device: str, interface_name: str, payload: XmlPayload) -> Dict[str, str]:
    try:
        client = NCCClientFactory.get_client(device)
        return client.configure_interface(interface_name, payload.config_xml)
    except DeviceNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except ClientMappingError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except GatewayError as exc:
        raise HTTPException(status_code=502, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.get("/{device}/protocols/bgp")
def get_bgp(device: str) -> Dict[str, str]:
    try:
        client = NCCClientFactory.get_client(device)
        return {"bgp": client.get_bgp()}
    except DeviceNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except ClientMappingError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except GatewayError as exc:
        raise HTTPException(status_code=502, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.put("/{device}/protocols/bgp")
def set_bgp(device: str, payload: XmlPayload) -> Dict[str, str]:
    try:
        client = NCCClientFactory.get_client(device)
        return client.set_bgp(payload.config_xml)
    except DeviceNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except ClientMappingError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except GatewayError as exc:
        raise HTTPException(status_code=502, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.post("/{device}/firewall/rules")
def apply_firewall_rule(device: str, payload: XmlPayload) -> Dict[str, str]:
    try:
        client = NCCClientFactory.get_client(device)
        return client.configure_firewall(payload.config_xml)
    except DeviceNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except ClientMappingError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except GatewayError as exc:
        raise HTTPException(status_code=502, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
