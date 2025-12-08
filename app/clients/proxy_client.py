"""
Proxy client using paramiko for SSH tunneling.
"""

import paramiko
from decouple import config

class ProxyClient:
    def __init__(self, proxy_host):
        self.proxy_host = proxy_host
        self.proxy_port = 22
        self.ssh_client = None

    def connect(self):
        self.ssh_client = paramiko.SSHClient()
        self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.ssh_client.connect(
            hostname=self.proxy_host,
            port=self.proxy_port,
            username=config('PROXY_USERNAME'),
            password=config('PROXY_PASSWORD')
        )

    def get_channel(self, dest_host, dest_port):
        if self.ssh_client is None:
            self.connect()
        # Open a direct-tcpip channel to the destination host/port
        transport = self.ssh_client.get_transport()
        channel = transport.open_channel(
            'direct-tcpip',
            (dest_host, dest_port),
            (self.proxy_host, self.proxy_port)
        )
        return channel

    def close(self):
        if self.ssh_client:
            self.ssh_client.close()
            self.ssh_client = None
