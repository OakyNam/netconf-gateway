
"""
Custom error classes for the NETCONF API Gateway.

All custom exceptions inherit from GatewayError for consistent error handling and logging.
"""

class GatewayError(Exception):
    """
    Base exception for NETCONF gateway errors.
    """
    pass

class ConfigNotFoundError(GatewayError):
    """
    Raised when a required config file is missing.
    """
    pass

class DeviceNotFoundError(GatewayError):
    """
    Raised when a device is not found in the database.
    """
    pass


class ProxyNotFoundError(GatewayError):
    """
    Raised when a proxy mapping is not found.
    """
    pass

class ProxyMappingError(GatewayError):
    """
    Raised for errors in proxy mapping logic or configuration.
    """
    pass

class ClientMappingError(GatewayError):
    """
    Raised when a client mapping is not found.
    """
    pass

class DatabaseError(GatewayError):
    """
    Raised for database-related errors.
    """
    pass
