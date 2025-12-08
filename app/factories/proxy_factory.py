

"""
Proxy Factory
--------------
Factory for creating NETCONF proxies based on configuration. All public methods are type hinted and include Google-style docstrings. Logging is included for major actions.
"""

import json
import os
from typing import Any
from app.errors import ProxyMappingError
from loguru import logger

# Config path for proxy mapping
PROXY_CONFIG_PATH = os.getenv('PROXY_CONFIG_PATH', os.path.join(os.path.dirname(__file__), '../../config/proxy_map.json'))

class ProxyFactory:
    """
    Factory for creating NETCONF proxies based on configuration.
    """
    @staticmethod
    def get_proxy(device: str) -> Any:
        """
        Get a NETCONF proxy for the specified device.

        Args:
            device (str): Device identifier.

        Returns:
            Any: NETCONF proxy instance.

        Raises:
            ProxyMappingError: If proxy mapping fails.
        """
        logger.info(f"Creating NETCONF proxy for device={device}")
        try:
            # router_info should be fetched from somewhere, e.g., a DB or config. Here, we assume a placeholder.
            router_info = {"owner": device}  # Placeholder: replace with real lookup

            if not os.path.exists(PROXY_CONFIG_PATH):
                logger.error(f"Proxy map config file not found: {PROXY_CONFIG_PATH}")
                raise ProxyMappingError(f"Proxy map config file not found: {PROXY_CONFIG_PATH}")
            with open(PROXY_CONFIG_PATH, 'r') as f:
                cfg = json.load(f)
            key_columns = cfg.get('key_columns', ['owner'])
            proxy_map = cfg.get('map', {})

            # Build key from router_info attributes
            key_parts = []
            for col in key_columns:
                val = router_info.get(col, None)
                key_parts.append((val or '*').lower())
            key = ':'.join(key_parts)

            # Try exact match, then fallback to wildcard
            proxy_host = proxy_map.get(key)
            if not proxy_host:
                # Try wildcard for last column
                if len(key_columns) > 1:
                    wildcard_key = ':'.join(key_parts[:-1] + ['*'])
                    proxy_host = proxy_map.get(wildcard_key)
                if not proxy_host:
                    # Try just first column if all else fails
                    proxy_host = proxy_map.get(key_parts[0])
            if not proxy_host:
                logger.error(f"No proxy found for key: {key}")
                raise ProxyMappingError(f"No proxy found for key: {key}")
            logger.info(f"Proxy resolved for key {key}: {proxy_host}")
            # Replace ProxyClient with actual proxy client class as needed
            return proxy_host
        except (ProxyMappingError,):
            raise
        except Exception as e:
            logger.error(f"Unexpected error in ProxyFactory.get_proxy: {e}")
            raise ProxyMappingError(f"Unexpected error in ProxyFactory: {e}")
