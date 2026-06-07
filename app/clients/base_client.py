"""Base client abstraction for NETCONF and SSH operations."""

from __future__ import annotations

from abc import ABC
from typing import Any, Dict, Optional

import paramiko
from decouple import config
from loguru import logger
from ncclient import manager

from app.errors import GatewayError
from app.factories.proxy_factory import ProxyFactory


class BaseNCCClient(ABC):
    def __init__(self, host: str, router_info: Dict[str, Any]) -> None:
        self.host = host
        self.router_info = router_info
        self.port = int(router_info.get("netconf_port", 830))
        self.ssh_port = int(router_info.get("ssh_port", 22))
        self.session = None
        self.ssh_client: Optional[paramiko.SSHClient] = None

    def _get_proxy(self):
        return ProxyFactory.get_proxy(self.router_info)

    @staticmethod
    def _credentials() -> Dict[str, str]:
        user = str(config("ROUTER_USERNAME"))
        passwd = str(config("ROUTER_PASSWORD"))
        return {"username": user, "password": passwd}

    @staticmethod
    def _use_relaxed_hostkey_policy() -> bool:
        return str(config("ROUTER_SSH_AUTO_ADD_HOSTKEY", default="false")).lower() in {
            "1",
            "true",
            "yes",
            "on",
        }

    def connect(self) -> None:
        if self.session is not None:
            return
        try:
            proxy = self._get_proxy()
            sock = proxy.get_channel(self.host, self.port) if proxy else None
            auth = self._credentials()
            self.session = manager.connect(
                host=self.host,
                port=self.port,
                hostkey_verify=False,
                allow_agent=False,
                look_for_keys=False,
                sock=sock,
                **auth,
            )
        except Exception as exc:
            logger.error(f"NETCONF connect failed for {self.host}: {exc}")
            raise GatewayError(f"NETCONF connect failed: {exc}")

    def close(self) -> None:
        if self.session:
            self.session.close_session()
            self.session = None

    def _connect_ssh(self) -> None:
        if self.ssh_client is not None:
            return
        try:
            self.ssh_client = paramiko.SSHClient()
            self.ssh_client.load_system_host_keys()
            if self._use_relaxed_hostkey_policy():
                self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            else:
                self.ssh_client.set_missing_host_key_policy(paramiko.RejectPolicy())
            proxy = self._get_proxy()
            sock = proxy.get_channel(self.host, self.ssh_port) if proxy else None
            auth = self._credentials()
            self.ssh_client.connect(
                hostname=self.host,
                port=self.ssh_port,
                sock=sock,
                look_for_keys=False,
                allow_agent=False,
                **auth,
            )
        except Exception as exc:
            logger.error(f"SSH connect failed for {self.host}: {exc}")
            raise GatewayError(f"SSH connect failed: {exc}")

    def close_ssh(self) -> None:
        if self.ssh_client:
            self.ssh_client.close()
            self.ssh_client = None

    def execute_ssh_command(self, command: str) -> str:
        self._connect_ssh()
        if self.ssh_client is None:
            raise GatewayError("SSH session is not available")
        _, stdout, stderr = self.ssh_client.exec_command(command)
        output = stdout.read().decode("utf-8", errors="ignore")
        err = stderr.read().decode("utf-8", errors="ignore")
        if err.strip():
            logger.warning(f"SSH stderr for {self.host}: {err.strip()}")
        return output

    def get_config(self) -> str:
        self.connect()
        reply = self.session.get_config(source="running")
        return str(reply.xml)

    def set_config(self, config_data: str) -> Dict[str, str]:
        self.connect()
        reply = self.session.edit_config(target="running", config=config_data)
        return {"status": "ok", "reply": str(reply.xml)}

    def get_operational_state(self) -> str:
        self.connect()
        reply = self.session.get()
        return str(reply.xml)

    def get_show_interface_command(self, interface_name: Optional[str] = None) -> str:
        return f"show interface {interface_name}" if interface_name else "show interfaces"

    def show_interface(self, interface_name: Optional[str] = None) -> Dict[str, str]:
        command = self.get_show_interface_command(interface_name)
        output = self.execute_ssh_command(command)
        return {"command": command, "output": output}

    def configure_interface(self, interface_name: str, config_xml: str) -> Dict[str, str]:
        _ = interface_name
        return self.set_config(config_xml)

    def get_bgp(self) -> str:
        self.connect()
        bgp_ns = str(
            self.router_info.get("bgp_namespace", "http://openconfig.net/yang/bgp")
        )
        filter_xml = f"<bgp xmlns='{bgp_ns}'/>"
        reply = self.session.get(filter=("subtree", filter_xml))
        return str(reply.xml)

    def set_bgp(self, config_xml: str) -> Dict[str, str]:
        return self.set_config(config_xml)

    def configure_firewall(self, config_xml: str) -> Dict[str, str]:
        return self.set_config(config_xml)
