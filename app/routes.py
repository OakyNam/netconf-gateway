
"""
Root API router for the NETCONF Gateway.

This module aggregates all domain-specific routers (routers, interfaces, protocols, MPLS)
under a single FastAPI APIRouter instance for modularity and maintainability.
"""

from fastapi import APIRouter
from app.controllers.router_controller import router as router_controller
from app.controllers.interface_controller import router as interface_controller
from app.controllers.protocol_controller import router as protocol_controller
from app.controllers.mpls_controller import router as mpls_controller

router = APIRouter()
router.include_router(router_controller, prefix="/routers", tags=["Routers"])
router.include_router(interface_controller, prefix="/interfaces", tags=["Interfaces"])
router.include_router(protocol_controller, prefix="/protocols", tags=["Protocols"])
router.include_router(mpls_controller, prefix="/mpls", tags=["MPLS"])
