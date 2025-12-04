"""
Sample Data Generator
Generate sample Azure network data for testing without Azure access.
"""

import json
from pathlib import Path


def generate_sample_data() -> dict:
    """Generate comprehensive sample Azure network data."""

    return {
        "metadata": {
            "collected_at": "2024-01-15T10:30:00",
            "subscription_id": "12345678-1234-1234-1234-123456789012",
            "resource_groups": ["rg-network-prod", "rg-network-dev"]
        },
        "vnets": [
            {
                "name": "vnet-hub-prod",
                "id": "/subscriptions/xxx/resourceGroups/rg-network-prod/providers/Microsoft.Network/virtualNetworks/vnet-hub-prod",
                "resourceGroup": "rg-network-prod",
                "location": "eastus",
                "addressSpace": {"addressPrefixes": ["10.0.0.0/16"]},
                "dhcpOptions": {"dnsServers": ["10.0.0.4", "10.0.0.5"]},
                "enableDdosProtection": True,
                "subnets": [
                    {"name": "AzureFirewallSubnet", "addressPrefix": "10.0.1.0/24", "id": "/subscriptions/xxx/resourceGroups/rg-network-prod/providers/Microsoft.Network/virtualNetworks/vnet-hub-prod/subnets/AzureFirewallSubnet"},
                    {"name": "GatewaySubnet", "addressPrefix": "10.0.2.0/24", "id": "/subscriptions/xxx/resourceGroups/rg-network-prod/providers/Microsoft.Network/virtualNetworks/vnet-hub-prod/subnets/GatewaySubnet"},
                    {"name": "AzureBastionSubnet", "addressPrefix": "10.0.3.0/24", "id": "/subscriptions/xxx/resourceGroups/rg-network-prod/providers/Microsoft.Network/virtualNetworks/vnet-hub-prod/subnets/AzureBastionSubnet"},
                    {"name": "snet-management", "addressPrefix": "10.0.4.0/24", "id": "/subscriptions/xxx/resourceGroups/rg-network-prod/providers/Microsoft.Network/virtualNetworks/vnet-hub-prod/subnets/snet-management",
                     "networkSecurityGroup": {"id": "/subscriptions/xxx/resourceGroups/rg-network-prod/providers/Microsoft.Network/networkSecurityGroups/nsg-management"}},
                ],
                "subnets_detail": [
                    {"name": "AzureFirewallSubnet", "addressPrefix": "10.0.1.0/24", "nsg": None, "routeTable": None, "serviceEndpoints": [], "delegations": []},
                    {"name": "GatewaySubnet", "addressPrefix": "10.0.2.0/24", "nsg": None, "routeTable": None, "serviceEndpoints": [], "delegations": []},
                    {"name": "AzureBastionSubnet", "addressPrefix": "10.0.3.0/24", "nsg": "nsg-bastion", "routeTable": None, "serviceEndpoints": [], "delegations": []},
                    {"name": "snet-management", "addressPrefix": "10.0.4.0/24", "nsg": "nsg-management", "routeTable": "rt-management", "serviceEndpoints": ["Microsoft.Storage", "Microsoft.KeyVault"], "delegations": []},
                ]
            },
            {
                "name": "vnet-spoke-prod",
                "id": "/subscriptions/xxx/resourceGroups/rg-network-prod/providers/Microsoft.Network/virtualNetworks/vnet-spoke-prod",
                "resourceGroup": "rg-network-prod",
                "location": "eastus",
                "addressSpace": {"addressPrefixes": ["10.1.0.0/16"]},
                "subnets": [
                    {"name": "snet-web", "addressPrefix": "10.1.1.0/24", "id": "/subscriptions/xxx/resourceGroups/rg-network-prod/providers/Microsoft.Network/virtualNetworks/vnet-spoke-prod/subnets/snet-web",
                     "networkSecurityGroup": {"id": "/subscriptions/xxx/resourceGroups/rg-network-prod/providers/Microsoft.Network/networkSecurityGroups/nsg-web"}},
                    {"name": "snet-app", "addressPrefix": "10.1.2.0/24", "id": "/subscriptions/xxx/resourceGroups/rg-network-prod/providers/Microsoft.Network/virtualNetworks/vnet-spoke-prod/subnets/snet-app",
                     "networkSecurityGroup": {"id": "/subscriptions/xxx/resourceGroups/rg-network-prod/providers/Microsoft.Network/networkSecurityGroups/nsg-app"}},
                    {"name": "snet-db", "addressPrefix": "10.1.3.0/24", "id": "/subscriptions/xxx/resourceGroups/rg-network-prod/providers/Microsoft.Network/virtualNetworks/vnet-spoke-prod/subnets/snet-db",
                     "networkSecurityGroup": {"id": "/subscriptions/xxx/resourceGroups/rg-network-prod/providers/Microsoft.Network/networkSecurityGroups/nsg-db"}},
                    {"name": "snet-privateendpoints", "addressPrefix": "10.1.4.0/24", "id": "/subscriptions/xxx/resourceGroups/rg-network-prod/providers/Microsoft.Network/virtualNetworks/vnet-spoke-prod/subnets/snet-privateendpoints"},
                ],
                "subnets_detail": [
                    {"name": "snet-web", "addressPrefix": "10.1.1.0/24", "nsg": "nsg-web", "routeTable": "rt-spoke", "serviceEndpoints": [], "delegations": []},
                    {"name": "snet-app", "addressPrefix": "10.1.2.0/24", "nsg": "nsg-app", "routeTable": "rt-spoke", "serviceEndpoints": ["Microsoft.Sql", "Microsoft.Storage"], "delegations": []},
                    {"name": "snet-db", "addressPrefix": "10.1.3.0/24", "nsg": "nsg-db", "routeTable": "rt-spoke", "serviceEndpoints": ["Microsoft.Sql"], "delegations": []},
                    {"name": "snet-privateendpoints", "addressPrefix": "10.1.4.0/24", "nsg": None, "routeTable": None, "serviceEndpoints": [], "delegations": []},
                ]
            },
            {
                "name": "vnet-spoke-dev",
                "id": "/subscriptions/xxx/resourceGroups/rg-network-dev/providers/Microsoft.Network/virtualNetworks/vnet-spoke-dev",
                "resourceGroup": "rg-network-dev",
                "location": "eastus",
                "addressSpace": {"addressPrefixes": ["10.2.0.0/16"]},
                "subnets": [
                    {"name": "snet-dev", "addressPrefix": "10.2.1.0/24", "id": "/subscriptions/xxx/resourceGroups/rg-network-dev/providers/Microsoft.Network/virtualNetworks/vnet-spoke-dev/subnets/snet-dev"},
                ],
                "subnets_detail": [
                    {"name": "snet-dev", "addressPrefix": "10.2.1.0/24", "nsg": None, "routeTable": None, "serviceEndpoints": [], "delegations": []},
                ]
            }
        ],
        "subnets": [
            {"name": "AzureFirewallSubnet", "vnet": "vnet-hub-prod", "resourceGroup": "rg-network-prod", "addressPrefix": "10.0.1.0/24", "id": "/subscriptions/xxx/resourceGroups/rg-network-prod/providers/Microsoft.Network/virtualNetworks/vnet-hub-prod/subnets/AzureFirewallSubnet", "nsg_id": None, "routeTable_id": None, "serviceEndpoints": [], "delegations": [], "ipConfigurations": [], "privateEndpoints": []},
            {"name": "GatewaySubnet", "vnet": "vnet-hub-prod", "resourceGroup": "rg-network-prod", "addressPrefix": "10.0.2.0/24", "id": "/subscriptions/xxx/resourceGroups/rg-network-prod/providers/Microsoft.Network/virtualNetworks/vnet-hub-prod/subnets/GatewaySubnet", "nsg_id": None, "routeTable_id": None, "serviceEndpoints": [], "delegations": [], "ipConfigurations": [], "privateEndpoints": []},
            {"name": "AzureBastionSubnet", "vnet": "vnet-hub-prod", "resourceGroup": "rg-network-prod", "addressPrefix": "10.0.3.0/24", "id": "/subscriptions/xxx/resourceGroups/rg-network-prod/providers/Microsoft.Network/virtualNetworks/vnet-hub-prod/subnets/AzureBastionSubnet", "nsg_id": "/subscriptions/xxx/resourceGroups/rg-network-prod/providers/Microsoft.Network/networkSecurityGroups/nsg-bastion", "routeTable_id": None, "serviceEndpoints": [], "delegations": [], "ipConfigurations": [], "privateEndpoints": []},
            {"name": "snet-management", "vnet": "vnet-hub-prod", "resourceGroup": "rg-network-prod", "addressPrefix": "10.0.4.0/24", "id": "/subscriptions/xxx/resourceGroups/rg-network-prod/providers/Microsoft.Network/virtualNetworks/vnet-hub-prod/subnets/snet-management", "nsg_id": "/subscriptions/xxx/resourceGroups/rg-network-prod/providers/Microsoft.Network/networkSecurityGroups/nsg-management", "routeTable_id": "/subscriptions/xxx/resourceGroups/rg-network-prod/providers/Microsoft.Network/routeTables/rt-management", "serviceEndpoints": [{"service": "Microsoft.Storage"}, {"service": "Microsoft.KeyVault"}], "delegations": [], "ipConfigurations": [{"id": "config1"}, {"id": "config2"}], "privateEndpoints": []},
            {"name": "snet-web", "vnet": "vnet-spoke-prod", "resourceGroup": "rg-network-prod", "addressPrefix": "10.1.1.0/24", "id": "/subscriptions/xxx/resourceGroups/rg-network-prod/providers/Microsoft.Network/virtualNetworks/vnet-spoke-prod/subnets/snet-web", "nsg_id": "/subscriptions/xxx/resourceGroups/rg-network-prod/providers/Microsoft.Network/networkSecurityGroups/nsg-web", "routeTable_id": "/subscriptions/xxx/resourceGroups/rg-network-prod/providers/Microsoft.Network/routeTables/rt-spoke", "serviceEndpoints": [], "delegations": [], "ipConfigurations": [{"id": "config1"}, {"id": "config2"}, {"id": "config3"}], "privateEndpoints": []},
            {"name": "snet-app", "vnet": "vnet-spoke-prod", "resourceGroup": "rg-network-prod", "addressPrefix": "10.1.2.0/24", "id": "/subscriptions/xxx/resourceGroups/rg-network-prod/providers/Microsoft.Network/virtualNetworks/vnet-spoke-prod/subnets/snet-app", "nsg_id": "/subscriptions/xxx/resourceGroups/rg-network-prod/providers/Microsoft.Network/networkSecurityGroups/nsg-app", "routeTable_id": "/subscriptions/xxx/resourceGroups/rg-network-prod/providers/Microsoft.Network/routeTables/rt-spoke", "serviceEndpoints": [{"service": "Microsoft.Sql"}, {"service": "Microsoft.Storage"}], "delegations": [], "ipConfigurations": [{"id": "config1"}], "privateEndpoints": []},
            {"name": "snet-db", "vnet": "vnet-spoke-prod", "resourceGroup": "rg-network-prod", "addressPrefix": "10.1.3.0/24", "id": "/subscriptions/xxx/resourceGroups/rg-network-prod/providers/Microsoft.Network/virtualNetworks/vnet-spoke-prod/subnets/snet-db", "nsg_id": "/subscriptions/xxx/resourceGroups/rg-network-prod/providers/Microsoft.Network/networkSecurityGroups/nsg-db", "routeTable_id": "/subscriptions/xxx/resourceGroups/rg-network-prod/providers/Microsoft.Network/routeTables/rt-spoke", "serviceEndpoints": [{"service": "Microsoft.Sql"}], "delegations": [], "ipConfigurations": [{"id": "config1"}], "privateEndpoints": []},
            {"name": "snet-privateendpoints", "vnet": "vnet-spoke-prod", "resourceGroup": "rg-network-prod", "addressPrefix": "10.1.4.0/24", "id": "/subscriptions/xxx/resourceGroups/rg-network-prod/providers/Microsoft.Network/virtualNetworks/vnet-spoke-prod/subnets/snet-privateendpoints", "nsg_id": None, "routeTable_id": None, "serviceEndpoints": [], "delegations": [], "ipConfigurations": [], "privateEndpoints": [{"id": "pe1"}, {"id": "pe2"}]},
            {"name": "snet-dev", "vnet": "vnet-spoke-dev", "resourceGroup": "rg-network-dev", "addressPrefix": "10.2.1.0/24", "id": "/subscriptions/xxx/resourceGroups/rg-network-dev/providers/Microsoft.Network/virtualNetworks/vnet-spoke-dev/subnets/snet-dev", "nsg_id": None, "routeTable_id": None, "serviceEndpoints": [], "delegations": [], "ipConfigurations": [{"id": "config1"}], "privateEndpoints": []},
        ],
        "nsgs": [
            {
                "name": "nsg-web",
                "id": "/subscriptions/xxx/resourceGroups/rg-network-prod/providers/Microsoft.Network/networkSecurityGroups/nsg-web",
                "resourceGroup": "rg-network-prod",
                "location": "eastus",
                "subnets": [{"id": "/subscriptions/xxx/resourceGroups/rg-network-prod/providers/Microsoft.Network/virtualNetworks/vnet-spoke-prod/subnets/snet-web"}],
                "networkInterfaces": [],
                "securityRules": [
                    {"name": "Allow-HTTP", "priority": 100, "direction": "Inbound", "access": "Allow", "protocol": "Tcp", "sourceAddressPrefix": "*", "sourcePortRange": "*", "destinationAddressPrefix": "*", "destinationPortRange": "80"},
                    {"name": "Allow-HTTPS", "priority": 110, "direction": "Inbound", "access": "Allow", "protocol": "Tcp", "sourceAddressPrefix": "*", "sourcePortRange": "*", "destinationAddressPrefix": "*", "destinationPortRange": "443"},
                    {"name": "Allow-AppTier", "priority": 200, "direction": "Outbound", "access": "Allow", "protocol": "Tcp", "sourceAddressPrefix": "10.1.1.0/24", "sourcePortRange": "*", "destinationAddressPrefix": "10.1.2.0/24", "destinationPortRange": "8080"},
                ],
                "customRules": [],
                "defaultSecurityRules": []
            },
            {
                "name": "nsg-app",
                "id": "/subscriptions/xxx/resourceGroups/rg-network-prod/providers/Microsoft.Network/networkSecurityGroups/nsg-app",
                "resourceGroup": "rg-network-prod",
                "location": "eastus",
                "subnets": [{"id": "/subscriptions/xxx/resourceGroups/rg-network-prod/providers/Microsoft.Network/virtualNetworks/vnet-spoke-prod/subnets/snet-app"}],
                "networkInterfaces": [],
                "securityRules": [
                    {"name": "Allow-FromWeb", "priority": 100, "direction": "Inbound", "access": "Allow", "protocol": "Tcp", "sourceAddressPrefix": "10.1.1.0/24", "sourcePortRange": "*", "destinationAddressPrefix": "*", "destinationPortRange": "8080"},
                    {"name": "Allow-ToDb", "priority": 200, "direction": "Outbound", "access": "Allow", "protocol": "Tcp", "sourceAddressPrefix": "*", "sourcePortRange": "*", "destinationAddressPrefix": "10.1.3.0/24", "destinationPortRange": "1433"},
                ],
                "customRules": [],
                "defaultSecurityRules": []
            },
            {
                "name": "nsg-db",
                "id": "/subscriptions/xxx/resourceGroups/rg-network-prod/providers/Microsoft.Network/networkSecurityGroups/nsg-db",
                "resourceGroup": "rg-network-prod",
                "location": "eastus",
                "subnets": [{"id": "/subscriptions/xxx/resourceGroups/rg-network-prod/providers/Microsoft.Network/virtualNetworks/vnet-spoke-prod/subnets/snet-db"}],
                "networkInterfaces": [],
                "securityRules": [
                    {"name": "Allow-FromApp", "priority": 100, "direction": "Inbound", "access": "Allow", "protocol": "Tcp", "sourceAddressPrefix": "10.1.2.0/24", "sourcePortRange": "*", "destinationAddressPrefix": "*", "destinationPortRange": "1433"},
                    {"name": "Deny-Internet", "priority": 4000, "direction": "Outbound", "access": "Deny", "protocol": "*", "sourceAddressPrefix": "*", "sourcePortRange": "*", "destinationAddressPrefix": "Internet", "destinationPortRange": "*"},
                ],
                "customRules": [],
                "defaultSecurityRules": []
            },
            {
                "name": "nsg-management",
                "id": "/subscriptions/xxx/resourceGroups/rg-network-prod/providers/Microsoft.Network/networkSecurityGroups/nsg-management",
                "resourceGroup": "rg-network-prod",
                "location": "eastus",
                "subnets": [{"id": "/subscriptions/xxx/resourceGroups/rg-network-prod/providers/Microsoft.Network/virtualNetworks/vnet-hub-prod/subnets/snet-management"}],
                "networkInterfaces": [],
                "securityRules": [
                    {"name": "Allow-RDP-Bastion", "priority": 100, "direction": "Inbound", "access": "Allow", "protocol": "Tcp", "sourceAddressPrefix": "10.0.3.0/24", "sourcePortRange": "*", "destinationAddressPrefix": "*", "destinationPortRange": "3389"},
                    {"name": "Allow-SSH-Bastion", "priority": 110, "direction": "Inbound", "access": "Allow", "protocol": "Tcp", "sourceAddressPrefix": "10.0.3.0/24", "sourcePortRange": "*", "destinationAddressPrefix": "*", "destinationPortRange": "22"},
                ],
                "customRules": [],
                "defaultSecurityRules": []
            },
            {
                "name": "nsg-bastion",
                "id": "/subscriptions/xxx/resourceGroups/rg-network-prod/providers/Microsoft.Network/networkSecurityGroups/nsg-bastion",
                "resourceGroup": "rg-network-prod",
                "location": "eastus",
                "subnets": [{"id": "/subscriptions/xxx/resourceGroups/rg-network-prod/providers/Microsoft.Network/virtualNetworks/vnet-hub-prod/subnets/AzureBastionSubnet"}],
                "networkInterfaces": [],
                "securityRules": [
                    {"name": "Allow-HTTPS-Inbound", "priority": 100, "direction": "Inbound", "access": "Allow", "protocol": "Tcp", "sourceAddressPrefix": "Internet", "sourcePortRange": "*", "destinationAddressPrefix": "*", "destinationPortRange": "443"},
                    {"name": "Allow-GatewayManager", "priority": 110, "direction": "Inbound", "access": "Allow", "protocol": "Tcp", "sourceAddressPrefix": "GatewayManager", "sourcePortRange": "*", "destinationAddressPrefix": "*", "destinationPortRange": "443"},
                ],
                "customRules": [],
                "defaultSecurityRules": []
            }
        ],
        "firewalls": [
            {
                "name": "afw-hub-prod",
                "id": "/subscriptions/xxx/resourceGroups/rg-network-prod/providers/Microsoft.Network/azureFirewalls/afw-hub-prod",
                "resourceGroup": "rg-network-prod",
                "location": "eastus",
                "sku": {"name": "AZFW_VNet", "tier": "Premium"},
                "threatIntelMode": "Alert",
                "firewallPolicy": {"id": "/subscriptions/xxx/resourceGroups/rg-network-prod/providers/Microsoft.Network/firewallPolicies/afwp-hub-prod"},
                "ipConfigurations": [
                    {"name": "ipconfig1", "privateIpAddress": "10.0.1.4", "publicIpAddress": {"id": "/subscriptions/xxx/resourceGroups/rg-network-prod/providers/Microsoft.Network/publicIPAddresses/pip-afw-hub"}, "subnet": {"id": "/subscriptions/xxx/resourceGroups/rg-network-prod/providers/Microsoft.Network/virtualNetworks/vnet-hub-prod/subnets/AzureFirewallSubnet"}}
                ],
                "ipConfigurations_processed": [
                    {"name": "ipconfig1", "privateIpAddress": "10.0.1.4", "publicIpAddress": "/subscriptions/xxx/resourceGroups/rg-network-prod/providers/Microsoft.Network/publicIPAddresses/pip-afw-hub", "subnet": "/subscriptions/xxx/resourceGroups/rg-network-prod/providers/Microsoft.Network/virtualNetworks/vnet-hub-prod/subnets/AzureFirewallSubnet"}
                ]
            }
        ],
        "firewall_policies": [
            {
                "name": "afwp-hub-prod",
                "id": "/subscriptions/xxx/resourceGroups/rg-network-prod/providers/Microsoft.Network/firewallPolicies/afwp-hub-prod",
                "resourceGroup": "rg-network-prod",
                "location": "eastus",
                "sku": {"tier": "Premium"},
                "threatIntelMode": "Alert",
                "ruleCollectionGroups_detail": [
                    {
                        "name": "rcg-network-rules",
                        "priority": 200,
                        "ruleCollections": [
                            {
                                "name": "rc-allow-spoke-to-spoke",
                                "priority": 100,
                                "ruleCollectionType": "FirewallPolicyFilterRuleCollection",
                                "action": "Allow",
                                "rules": [
                                    {"name": "allow-spoke-traffic", "ruleType": "NetworkRule", "sourceAddresses": ["10.1.0.0/16", "10.2.0.0/16"], "destinationAddresses": ["10.1.0.0/16", "10.2.0.0/16"], "destinationPorts": ["*"], "ipProtocols": ["Any"]}
                                ]
                            },
                            {
                                "name": "rc-allow-internet",
                                "priority": 200,
                                "ruleCollectionType": "FirewallPolicyFilterRuleCollection",
                                "action": "Allow",
                                "rules": [
                                    {"name": "allow-http-https", "ruleType": "NetworkRule", "sourceAddresses": ["10.0.0.0/8"], "destinationAddresses": ["*"], "destinationPorts": ["80", "443"], "ipProtocols": ["TCP"]}
                                ]
                            }
                        ]
                    },
                    {
                        "name": "rcg-app-rules",
                        "priority": 300,
                        "ruleCollections": [
                            {
                                "name": "rc-allow-windows-update",
                                "priority": 100,
                                "ruleCollectionType": "FirewallPolicyFilterRuleCollection",
                                "action": "Allow",
                                "rules": [
                                    {"name": "allow-windows-update", "ruleType": "ApplicationRule", "sourceAddresses": ["10.0.0.0/8"], "targetFqdns": ["*.windowsupdate.microsoft.com", "*.update.microsoft.com"], "protocols": [{"protocolType": "Https", "port": 443}]}
                                ]
                            },
                            {
                                "name": "rc-allow-azure-services",
                                "priority": 200,
                                "ruleCollectionType": "FirewallPolicyFilterRuleCollection",
                                "action": "Allow",
                                "rules": [
                                    {"name": "allow-azure-monitor", "ruleType": "ApplicationRule", "sourceAddresses": ["10.0.0.0/8"], "targetFqdns": ["*.monitor.azure.com", "*.ods.opinsights.azure.com"], "protocols": [{"protocolType": "Https", "port": 443}]}
                                ]
                            }
                        ]
                    }
                ]
            }
        ],
        "route_tables": [
            {
                "name": "rt-spoke",
                "id": "/subscriptions/xxx/resourceGroups/rg-network-prod/providers/Microsoft.Network/routeTables/rt-spoke",
                "resourceGroup": "rg-network-prod",
                "location": "eastus",
                "disableBgpRoutePropagation": True,
                "subnets": [
                    {"id": "/subscriptions/xxx/resourceGroups/rg-network-prod/providers/Microsoft.Network/virtualNetworks/vnet-spoke-prod/subnets/snet-web"},
                    {"id": "/subscriptions/xxx/resourceGroups/rg-network-prod/providers/Microsoft.Network/virtualNetworks/vnet-spoke-prod/subnets/snet-app"},
                    {"id": "/subscriptions/xxx/resourceGroups/rg-network-prod/providers/Microsoft.Network/virtualNetworks/vnet-spoke-prod/subnets/snet-db"}
                ],
                "routes": [
                    {"name": "route-to-firewall", "addressPrefix": "0.0.0.0/0", "nextHopType": "VirtualAppliance", "nextHopIpAddress": "10.0.1.4"},
                    {"name": "route-to-hub", "addressPrefix": "10.0.0.0/16", "nextHopType": "VirtualAppliance", "nextHopIpAddress": "10.0.1.4"}
                ],
                "routes_processed": [
                    {"name": "route-to-firewall", "addressPrefix": "0.0.0.0/0", "nextHopType": "VirtualAppliance", "nextHopIpAddress": "10.0.1.4"},
                    {"name": "route-to-hub", "addressPrefix": "10.0.0.0/16", "nextHopType": "VirtualAppliance", "nextHopIpAddress": "10.0.1.4"}
                ]
            },
            {
                "name": "rt-management",
                "id": "/subscriptions/xxx/resourceGroups/rg-network-prod/providers/Microsoft.Network/routeTables/rt-management",
                "resourceGroup": "rg-network-prod",
                "location": "eastus",
                "disableBgpRoutePropagation": False,
                "subnets": [
                    {"id": "/subscriptions/xxx/resourceGroups/rg-network-prod/providers/Microsoft.Network/virtualNetworks/vnet-hub-prod/subnets/snet-management"}
                ],
                "routes": [
                    {"name": "route-to-spokes", "addressPrefix": "10.1.0.0/16", "nextHopType": "VirtualAppliance", "nextHopIpAddress": "10.0.1.4"}
                ],
                "routes_processed": [
                    {"name": "route-to-spokes", "addressPrefix": "10.1.0.0/16", "nextHopType": "VirtualAppliance", "nextHopIpAddress": "10.0.1.4"}
                ]
            }
        ],
        "peerings": [
            {
                "name": "peer-hub-to-spoke-prod",
                "id": "/subscriptions/xxx/resourceGroups/rg-network-prod/providers/Microsoft.Network/virtualNetworks/vnet-hub-prod/virtualNetworkPeerings/peer-hub-to-spoke-prod",
                "sourceVnet": "vnet-hub-prod",
                "sourceResourceGroup": "rg-network-prod",
                "remoteVnetId": "/subscriptions/xxx/resourceGroups/rg-network-prod/providers/Microsoft.Network/virtualNetworks/vnet-spoke-prod",
                "peeringState": "Connected",
                "allowVirtualNetworkAccess": True,
                "allowForwardedTraffic": True,
                "allowGatewayTransit": True,
                "useRemoteGateways": False
            },
            {
                "name": "peer-spoke-prod-to-hub",
                "id": "/subscriptions/xxx/resourceGroups/rg-network-prod/providers/Microsoft.Network/virtualNetworks/vnet-spoke-prod/virtualNetworkPeerings/peer-spoke-prod-to-hub",
                "sourceVnet": "vnet-spoke-prod",
                "sourceResourceGroup": "rg-network-prod",
                "remoteVnetId": "/subscriptions/xxx/resourceGroups/rg-network-prod/providers/Microsoft.Network/virtualNetworks/vnet-hub-prod",
                "peeringState": "Connected",
                "allowVirtualNetworkAccess": True,
                "allowForwardedTraffic": True,
                "allowGatewayTransit": False,
                "useRemoteGateways": True
            },
            {
                "name": "peer-hub-to-spoke-dev",
                "id": "/subscriptions/xxx/resourceGroups/rg-network-prod/providers/Microsoft.Network/virtualNetworks/vnet-hub-prod/virtualNetworkPeerings/peer-hub-to-spoke-dev",
                "sourceVnet": "vnet-hub-prod",
                "sourceResourceGroup": "rg-network-prod",
                "remoteVnetId": "/subscriptions/xxx/resourceGroups/rg-network-dev/providers/Microsoft.Network/virtualNetworks/vnet-spoke-dev",
                "peeringState": "Connected",
                "allowVirtualNetworkAccess": True,
                "allowForwardedTraffic": True,
                "allowGatewayTransit": True,
                "useRemoteGateways": False
            }
        ],
        "private_endpoints": [
            {
                "name": "pe-storage-prod",
                "id": "/subscriptions/xxx/resourceGroups/rg-network-prod/providers/Microsoft.Network/privateEndpoints/pe-storage-prod",
                "resourceGroup": "rg-network-prod",
                "location": "eastus",
                "subnet": {"id": "/subscriptions/xxx/resourceGroups/rg-network-prod/providers/Microsoft.Network/virtualNetworks/vnet-spoke-prod/subnets/snet-privateendpoints"},
                "connections": [
                    {"name": "conn-storage", "privateLinkServiceId": "/subscriptions/xxx/resourceGroups/rg-storage/providers/Microsoft.Storage/storageAccounts/stproddata001", "groupIds": ["blob"], "status": "Approved"}
                ],
                "customDnsConfigs": [{"fqdn": "stproddata001.blob.core.windows.net", "ipAddresses": ["10.1.4.5"]}]
            },
            {
                "name": "pe-sql-prod",
                "id": "/subscriptions/xxx/resourceGroups/rg-network-prod/providers/Microsoft.Network/privateEndpoints/pe-sql-prod",
                "resourceGroup": "rg-network-prod",
                "location": "eastus",
                "subnet": {"id": "/subscriptions/xxx/resourceGroups/rg-network-prod/providers/Microsoft.Network/virtualNetworks/vnet-spoke-prod/subnets/snet-privateendpoints"},
                "connections": [
                    {"name": "conn-sql", "privateLinkServiceId": "/subscriptions/xxx/resourceGroups/rg-database/providers/Microsoft.Sql/servers/sql-prod-001", "groupIds": ["sqlServer"], "status": "Approved"}
                ],
                "customDnsConfigs": [{"fqdn": "sql-prod-001.database.windows.net", "ipAddresses": ["10.1.4.6"]}]
            },
            {
                "name": "pe-keyvault-prod",
                "id": "/subscriptions/xxx/resourceGroups/rg-network-prod/providers/Microsoft.Network/privateEndpoints/pe-keyvault-prod",
                "resourceGroup": "rg-network-prod",
                "location": "eastus",
                "subnet": {"id": "/subscriptions/xxx/resourceGroups/rg-network-prod/providers/Microsoft.Network/virtualNetworks/vnet-spoke-prod/subnets/snet-privateendpoints"},
                "connections": [
                    {"name": "conn-kv", "privateLinkServiceId": "/subscriptions/xxx/resourceGroups/rg-security/providers/Microsoft.KeyVault/vaults/kv-prod-001", "groupIds": ["vault"], "status": "Approved"}
                ],
                "customDnsConfigs": [{"fqdn": "kv-prod-001.vault.azure.net", "ipAddresses": ["10.1.4.7"]}]
            }
        ],
        "public_ips": [
            {"name": "pip-afw-hub", "id": "/subscriptions/xxx/resourceGroups/rg-network-prod/providers/Microsoft.Network/publicIPAddresses/pip-afw-hub", "resourceGroup": "rg-network-prod", "ipAddress": "20.120.50.100", "sku": {"name": "Standard"}, "publicIPAllocationMethod": "Static"},
            {"name": "pip-bastion-hub", "id": "/subscriptions/xxx/resourceGroups/rg-network-prod/providers/Microsoft.Network/publicIPAddresses/pip-bastion-hub", "resourceGroup": "rg-network-prod", "ipAddress": "20.120.50.101", "sku": {"name": "Standard"}, "publicIPAllocationMethod": "Static"},
            {"name": "pip-appgw-prod", "id": "/subscriptions/xxx/resourceGroups/rg-network-prod/providers/Microsoft.Network/publicIPAddresses/pip-appgw-prod", "resourceGroup": "rg-network-prod", "ipAddress": "20.120.50.102", "sku": {"name": "Standard"}, "publicIPAllocationMethod": "Static"}
        ],
        "private_dns_zones": [
            {
                "name": "privatelink.blob.core.windows.net",
                "id": "/subscriptions/xxx/resourceGroups/rg-network-prod/providers/Microsoft.Network/privateDnsZones/privatelink.blob.core.windows.net",
                "resourceGroup": "rg-network-prod",
                "numberOfRecordSets": 5,
                "virtualNetworkLinks": [
                    {"virtualNetwork": {"id": "/subscriptions/xxx/resourceGroups/rg-network-prod/providers/Microsoft.Network/virtualNetworks/vnet-hub-prod"}},
                    {"virtualNetwork": {"id": "/subscriptions/xxx/resourceGroups/rg-network-prod/providers/Microsoft.Network/virtualNetworks/vnet-spoke-prod"}}
                ]
            },
            {
                "name": "privatelink.database.windows.net",
                "id": "/subscriptions/xxx/resourceGroups/rg-network-prod/providers/Microsoft.Network/privateDnsZones/privatelink.database.windows.net",
                "resourceGroup": "rg-network-prod",
                "numberOfRecordSets": 3,
                "virtualNetworkLinks": [
                    {"virtualNetwork": {"id": "/subscriptions/xxx/resourceGroups/rg-network-prod/providers/Microsoft.Network/virtualNetworks/vnet-hub-prod"}},
                    {"virtualNetwork": {"id": "/subscriptions/xxx/resourceGroups/rg-network-prod/providers/Microsoft.Network/virtualNetworks/vnet-spoke-prod"}}
                ]
            }
        ],
        "application_gateways": [
            {
                "name": "appgw-prod",
                "id": "/subscriptions/xxx/resourceGroups/rg-network-prod/providers/Microsoft.Network/applicationGateways/appgw-prod",
                "resourceGroup": "rg-network-prod",
                "location": "eastus",
                "sku": {"name": "WAF_v2", "tier": "WAF_v2", "capacity": 2},
                "backendAddressPools": [{"name": "pool-web-servers"}],
                "httpListeners": [{"name": "listener-https"}, {"name": "listener-http"}]
            }
        ],
        "load_balancers": [
            {
                "name": "lb-app-internal",
                "id": "/subscriptions/xxx/resourceGroups/rg-network-prod/providers/Microsoft.Network/loadBalancers/lb-app-internal",
                "resourceGroup": "rg-network-prod",
                "location": "eastus",
                "sku": {"name": "Standard"},
                "frontendIpConfigurations": [{"name": "frontend-app"}],
                "backendAddressPools": [{"name": "pool-app-servers"}],
                "loadBalancingRules": [{"name": "rule-app-8080"}]
            }
        ],
        "virtual_network_gateways": [
            {
                "name": "vgw-hub-prod",
                "id": "/subscriptions/xxx/resourceGroups/rg-network-prod/providers/Microsoft.Network/virtualNetworkGateways/vgw-hub-prod",
                "resourceGroup": "rg-network-prod",
                "location": "eastus",
                "gatewayType": "Vpn",
                "vpnType": "RouteBased",
                "sku": {"name": "VpnGw2"},
                "activeActive": False
            }
        ],
        "bastion_hosts": [
            {
                "name": "bastion-hub-prod",
                "id": "/subscriptions/xxx/resourceGroups/rg-network-prod/providers/Microsoft.Network/bastionHosts/bastion-hub-prod",
                "resourceGroup": "rg-network-prod",
                "location": "eastus",
                "sku": {"name": "Standard"},
                "scaleUnits": 2
            }
        ],
        "nics": [
            {"name": "nic-vm-web-001", "resourceGroup": "rg-network-prod", "virtualMachine": {"id": "/subscriptions/xxx/resourceGroups/rg-compute/providers/Microsoft.Compute/virtualMachines/vm-web-001"}, "ipConfigurations": [{"privateIPAddress": "10.1.1.10", "subnet": {"id": "/subscriptions/xxx/resourceGroups/rg-network-prod/providers/Microsoft.Network/virtualNetworks/vnet-spoke-prod/subnets/snet-web"}}]},
            {"name": "nic-vm-web-002", "resourceGroup": "rg-network-prod", "virtualMachine": {"id": "/subscriptions/xxx/resourceGroups/rg-compute/providers/Microsoft.Compute/virtualMachines/vm-web-002"}, "ipConfigurations": [{"privateIPAddress": "10.1.1.11", "subnet": {"id": "/subscriptions/xxx/resourceGroups/rg-network-prod/providers/Microsoft.Network/virtualNetworks/vnet-spoke-prod/subnets/snet-web"}}]},
            {"name": "nic-vm-app-001", "resourceGroup": "rg-network-prod", "virtualMachine": {"id": "/subscriptions/xxx/resourceGroups/rg-compute/providers/Microsoft.Compute/virtualMachines/vm-app-001"}, "ipConfigurations": [{"privateIPAddress": "10.1.2.10", "subnet": {"id": "/subscriptions/xxx/resourceGroups/rg-network-prod/providers/Microsoft.Network/virtualNetworks/vnet-spoke-prod/subnets/snet-app"}}]},
            {"name": "nic-vm-mgmt-001", "resourceGroup": "rg-network-prod", "virtualMachine": {"id": "/subscriptions/xxx/resourceGroups/rg-compute/providers/Microsoft.Compute/virtualMachines/vm-mgmt-001"}, "ipConfigurations": [{"privateIPAddress": "10.0.4.10", "subnet": {"id": "/subscriptions/xxx/resourceGroups/rg-network-prod/providers/Microsoft.Network/virtualNetworks/vnet-hub-prod/subnets/snet-management"}}]},
        ]
    }


def save_sample_data(output_path: str = "sample_network_data.json"):
    """Save sample data to a JSON file."""
    data = generate_sample_data()
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)

    print(f"Sample data saved to: {output_path}")
    return output_path


if __name__ == "__main__":
    save_sample_data()
