"""Factory for creating NETCONF/SSH clients from device metadata."""

import importlib
import json
import os
from typing import Any, Dict

from loguru import logger

from app.db.db_client import get_device_info
from app.errors import ClientMappingError, DeviceNotFoundError

def _resolve_config_path() -> str:
    configured = os.getenv(
        "CLIENT_CONFIG_PATH",
        os.path.join(os.path.dirname(__file__), "../../config/client_config.json"),
    )
    if os.path.exists(configured):
        return configured
    return configured.replace("client_config.json", "client_config.example.json")


CLIENT_CONFIG_PATH = _resolve_config_path()


class NCCClientFactory:
    @staticmethod
    def _resolve_class_path(router_info: Dict[str, Any], cfg: Dict[str, Any]) -> str:
        key_columns = cfg.get("key_columns", ["vendor"])
        client_map = cfg.get("map", {})
        key_parts = [str(router_info.get(col, "*") or "*").lower() for col in key_columns]
        key = ":".join(key_parts)

        class_path = client_map.get(key)
        if not class_path and len(key_parts) > 1:
            class_path = client_map.get(":".join(key_parts[:-1] + ["*"]))
        if not class_path and key_parts:
            class_path = client_map.get(key_parts[0])
        if not class_path:
            class_path = client_map.get("default")
        if not class_path:
            raise ClientMappingError(f"No client mapping found for key: {key}")
        return class_path

    @staticmethod
    def get_client(device: str) -> Any:
        try:
            router_info = get_device_info(device)
            if not router_info:
                raise DeviceNotFoundError(f"Device not found: {device}")

            if not os.path.exists(CLIENT_CONFIG_PATH):
                raise ClientMappingError(f"Client config file not found: {CLIENT_CONFIG_PATH}")

            with open(CLIENT_CONFIG_PATH, "r", encoding="utf-8") as file:
                cfg = json.load(file)

            class_path = NCCClientFactory._resolve_class_path(router_info, cfg)
            module_name, class_name = class_path.rsplit(".", 1)
            module = importlib.import_module(module_name)
            client_class = getattr(module, class_name)

            host = str(
                router_info.get("mgmt_ip")
                or router_info.get("ip")
                or router_info.get("host")
                or router_info.get("hostname")
                or device
            )
            logger.info(f"Resolved client {class_path} for device={device}")
            return client_class(host=host, router_info=router_info)
        except (ClientMappingError, DeviceNotFoundError):
            raise
        except Exception as exc:
            logger.error(f"Unexpected error in NCCClientFactory.get_client: {exc}")
            raise ClientMappingError(f"Unexpected error in NCCClientFactory: {exc}")
