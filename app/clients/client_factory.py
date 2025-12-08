"""
Client factory to select the correct NETCONF client based on vendor.
"""


from app.clients.nccclient_alcatel import AlcatelNCCClient
from app.clients.nccclient_juniper import JuniperNCCClient
from app.clients.nccclient_ios import IOSNCCClient
from app.clients.nccclient_iox import IOXNCCClient
from app.clients.nccclient_adva import AdvaFSP114ProNCCClient
from app.clients.nccclient_ceina import CeinaNCCClient

from app.db.db_client import get_router_by_hostname

class NCCClientFactory:
    @staticmethod
    def get_client(hostname):
        router_info = get_router_by_hostname(hostname)
        if not router_info:
            raise ValueError(f"Router with hostname {hostname} not found")
        vendor = router_info.vendor.lower()
        if vendor == "juniper":
            return JuniperNCCClient(router_info.router, owner=router_info.owner)
        elif vendor == "alcatel":
            return AlcatelNCCClient(router_info.router, owner=router_info.owner)
        elif vendor == "ios":
            return IOSNCCClient(router_info.router, owner=router_info.owner)
        elif vendor == "iox":
            return IOXNCCClient(router_info.router, owner=router_info.owner)
        elif vendor == "adva":
            return AdvaFSP114ProNCCClient(router_info.router, owner=router_info.owner)
        elif vendor == "ceina":
            return CeinaNCCClient(router_info.router, owner=router_info.owner)
        else:
            raise ValueError(f"Unsupported vendor: {vendor}")
