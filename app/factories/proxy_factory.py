"""Factory for creating proxy clients from mapping config."""

import json
import os
from typing import Any, Dict, Optional

from loguru import logger

from app.clients.proxy_client import ProxyClient
from app.errors import ProxyMappingError

def _resolve_config_path() -> str:
    configured = os.getenv(
        "PROXY_CONFIG_PATH",
        os.path.join(os.path.dirname(__file__), "../../config/proxy_config.json"),
    )
    if os.path.exists(configured):
        return configured
    return configured.replace("proxy_config.json", "proxy_config.example.json")


PROXY_CONFIG_PATH = _resolve_config_path()


class ProxyFactory:
    @staticmethod
    def get_proxy(router_info: Dict[str, Any]) -> Optional[ProxyClient]:
        try:
            if not os.path.exists(PROXY_CONFIG_PATH):
                logger.warning("Proxy config not found; using direct access")
                return None

            with open(PROXY_CONFIG_PATH, "r", encoding="utf-8") as file:
                cfg = json.load(file)

            key_columns = cfg.get("key_columns", ["owner"])
            proxy_map = cfg.get("map", {})
            key_parts = [str(router_info.get(col, "*") or "*").lower() for col in key_columns]
            key = ":".join(key_parts)

            proxy_host = proxy_map.get(key)
            if not proxy_host and len(key_parts) > 1:
                proxy_host = proxy_map.get(":".join(key_parts[:-1] + ["*"]))
            if not proxy_host:
                proxy_host = proxy_map.get(key_parts[0]) if key_parts else None
            if not proxy_host:
                proxy_host = proxy_map.get("default") or proxy_map.get("*:*")

            if not proxy_host:
                return None

            logger.info(f"Using proxy {proxy_host} for key {key}")
            return ProxyClient(proxy_host)
        except Exception as exc:
            logger.error(f"Proxy mapping failed: {exc}")
            raise ProxyMappingError(f"Proxy mapping failed: {exc}")
