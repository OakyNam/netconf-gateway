"""
IOX NETCONF client implementation.
"""

from app.clients.base_client import BaseNCCClient

class IOXNCCClient(BaseNCCClient):
    def __init__(self, device, owner=None):
        super().__init__(device, owner)
        self.port = 830

    def get_config(self):
        # Implement IOX-specific get_config logic here
        pass

    def set_config(self, config_data):
        # Implement IOX-specific set_config logic here
        pass
