"""IOX NETCONF client implementation."""

from typing import Any, Dict

from app.clients.base_client import BaseNCCClient


class IOXNCCClient(BaseNCCClient):
    def __init__(self, host: str, router_info: Dict[str, Any]):
        super().__init__(host, router_info)
        self.port = int(router_info.get("netconf_port", 830))
