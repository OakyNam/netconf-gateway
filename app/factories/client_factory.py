
"""
Client Factory
--------------
Factory for creating NETCONF clients based on configuration. All public methods are type hinted and include Google-style docstrings. Logging is included for major actions.
"""


import importlib
import json
import os

from typing import Any
from app.errors import ClientMappingError
from loguru import logger

# Config path for client mapping
CLIENT_CONFIG_PATH = os.getenv('CLIENT_CONFIG_PATH', os.path.join(os.path.dirname(__file__), '../../config/client_map.json'))

class NCCClientFactory:
    """
    Factory for creating NETCONF clients based on device configuration.
    """
    @staticmethod
    def get_client(device: str) -> Any:
        """
        Get a NETCONF client for the specified device.

        Args:
            device (str): Device identifier.

        Returns:
            Any: NETCONF client instance.

        Raises:
            ClientMappingError: If client mapping fails.
        """
        logger.info(f"Creating NETCONF client for device={device}")
        try:
            # router_info should be fetched from somewhere, e.g., a DB or config. Here, we assume a placeholder.
            # Replace this with actual device info retrieval logic as needed.
            router_info = {"vendor": device}  # Placeholder: replace with real lookup

            if not os.path.exists(CLIENT_CONFIG_PATH):
                logger.error(f"Client map config file not found: {CLIENT_CONFIG_PATH}")
                raise ClientMappingError(f"Client map config file not found: {CLIENT_CONFIG_PATH}")
            with open(CLIENT_CONFIG_PATH, 'r') as f:
                cfg = json.load(f)
            key_columns = cfg.get('key_columns', ['vendor'])
            client_map = cfg.get('map', {})

            # Build key from router_info attributes
            key_parts = []
            for col in key_columns:
                val = router_info.get(col, None)
                key_parts.append((val or '*').lower())
            key = ':'.join(key_parts)

            # Try exact match, then fallback to wildcard
            class_path = client_map.get(key)
            if not class_path:
                # Try wildcard for last column
                if len(key_columns) > 1:
                    wildcard_key = ':'.join(key_parts[:-1] + ['*'])
                    class_path = client_map.get(wildcard_key)
                if not class_path:
                    # Try just vendor if all else fails
                    class_path = client_map.get(key_parts[0])
            if not class_path:
                logger.error(f"No client mapping found for key: {key}")
                raise ClientMappingError(f"No client mapping found for key: {key}")
            logger.info(f"Client resolved for key {key}: {class_path}")
            module_name, class_name = class_path.rsplit('.', 1)
            module = importlib.import_module(module_name)
            client_class = getattr(module, class_name)
            return client_class(router_info)
        except ClientMappingError:
            raise
        except Exception as e:
            logger.error(f"Unexpected error in NCCClientFactory.get_client: {e}")
            raise ClientMappingError(f"Unexpected error in NCCClientFactory: {e}")
