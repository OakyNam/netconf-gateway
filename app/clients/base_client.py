"""
Abstract base class for NETCONF clients to enforce function name standardization.
"""

from abc import ABC, abstractmethod
from ncclient import manager

from app.clients.proxy_factory import ProxyFactory

from decouple import config

class BaseNCCClient(ABC):
    def __init__(self, host, owner):
        self.host = host
        self.port = 22
        self.owner = owner
        self.session = None

    def connect(self):
        proxy = ProxyFactory.get_proxy(self.owner)
        channel = proxy.get_channel(self.host, self.port)
        self.session = manager.connect(
            host=self.host,
            port=self.port,
            username=config('ROUTER_USERNAME'),
            password=config('ROUTER_PASSWORD'),
            hostkey_verify=False,
            sock=channel
        )

    def close(self):
        if self.session:
            self.session.close_session()
            self.session = None

    @abstractmethod
    def get_config(self):
        pass

    @abstractmethod
    def set_config(self, config_data):
        pass
