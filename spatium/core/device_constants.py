"""Device-specific constants and configurations."""

# Device-specific configuration commands
DEVICE_CONFIG_COMMANDS = {
    "sonic": "show running-configuration",
    "cisco": "show running-config",
    "arista": "show running-config",
    "nokia": "show running-configuration",
    "juniper": "show configuration",
    "huawei": "display current-configuration",
    "mikrotik": "export",
    "fortinet": "show full-configuration",
    "paloalto": "show config running",
    "checkpoint": "show configuration",
    "f5": "tmsh show running-config",
    "linux": "cat /etc/network/interfaces",
    "ubuntu": "cat /etc/netplan/*.yaml",
    "debian": "cat /etc/network/interfaces",
    "redhat": "cat /etc/sysconfig/network-scripts/ifcfg-*",
    "centos": "cat /etc/sysconfig/network-scripts/ifcfg-*",
    "aruba": "show running-config",
    "cumulus": "show running-config",
    "vyos": "show configuration",
    "openwrt": "cat /etc/config/network",
    "ubiquiti": "show configuration",
    "meraki": "show running-config",
    "cisco_ios": "show running-config",
    "cisco_nxos": "show running-config",
    "cisco_xe": "show running-config",
    "cisco_iosxe": "show running-config",
    "cisco_asa": "show running-config",
}

# REST API endpoints for device configuration retrieval
DEVICE_REST_ENDPOINTS = {
    "sonic": "/api/config",
    "cisco": "/restconf/data/Cisco-IOS-XE-native:native",
    "arista": "/command-api",
    "nokia": "/api/running-config",
    "juniper": "/rpc/get-configuration",
    "huawei": "/restconf/data/huawei-configuration:configuration",
    "mikrotik": "/rest/configuration/export",
    "fortinet": "/api/v2/monitor/system/config/backup",
    "paloalto": "/api/?type=export&category=configuration",
    "checkpoint": "/web_api/show-configuration",
    "f5": "/mgmt/tm/sys/config",
    "linux": "/api/config/network",
    "ubuntu": "/api/config/netplan",
    "debian": "/api/config/network",
    "redhat": "/api/config/network-scripts",
    "centos": "/api/config/network-scripts",
    "aruba": "/v1/configuration/running-config",
    "cumulus": "/api/config/running-config",
    "vyos": "/rest/configuration",
    "openwrt": "/api/config/network",
    "ubiquiti": "/api/configuration",
    "meraki": "/api/v1/networks/{networkId}/devices/{serial}/configuration",
    "cisco_ios": "/restconf/data/Cisco-IOS-XE-native:native",
    "cisco_nxos": "/ins",
    "cisco_xe": "/restconf/data/Cisco-IOS-XE-native:native",
    "cisco_iosxe": "/restconf/data/Cisco-IOS-XE-native:native",
    "cisco_asa": "/api/config",
}

# Default device settings
DEFAULT_DEVICE_MODEL = "sonic"
DEFAULT_CONFIG_METHOD = "ssh"
DEFAULT_CONFIG_TIMEOUT = 10  # seconds
