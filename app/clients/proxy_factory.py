"""
Proxy factory to select the correct proxy based on router owner.
"""
from app.clients.proxy_client import ProxyClient


import json
import os

class ProxyFactory:
    _proxy_map = None

    @staticmethod
    def _load_proxy_map():
        if ProxyFactory._proxy_map is None:
            config_path = os.getenv('PROXY_MAP_PATH', os.path.join(os.path.dirname(__file__), '../../config/proxy_map.json'))
            with open(config_path, 'r') as f:
                ProxyFactory._proxy_map = json.load(f)
        return ProxyFactory._proxy_map

    @staticmethod
    def get_proxy(owner):
        proxy_map = ProxyFactory._load_proxy_map()
        owner_key = (owner or '').lower()
        proxy_host = proxy_map.get(owner_key, proxy_map.get('default', 'nocsup'))
        return ProxyClient(proxy_host)