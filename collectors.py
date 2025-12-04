"""
Azure Data Collectors
Modules to collect network-related resources from Azure using Azure CLI.
"""

import json
import subprocess
from dataclasses import dataclass
from typing import Optional


def run_az_command(command: list[str]) -> Optional[list | dict]:
    """Run an Azure CLI command and return parsed JSON output."""
    try:
        full_command = ["az"] + command + ["--output", "json"]
        result = subprocess.run(
            full_command,
            capture_output=True,
            text=True,
            shell=True
        )
        if result.returncode == 0 and result.stdout.strip():
            return json.loads(result.stdout)
        return None
    except (json.JSONDecodeError, FileNotFoundError) as e:
        print(f"  Warning: Command failed - {' '.join(command)}: {e}")
        return None


@dataclass
class AzureCollector:
    """Collector for Azure network resources."""

    def __init__(self, config):
        self.config = config
        self.subscription_filter = ""
        if config.subscription_id:
            self.subscription_filter = f"--subscription {config.subscription_id}"

    def _get_resource_group_filter(self) -> str:
        """Get resource group filter for queries."""
        if self.config.resource_groups:
            rgs = "', '".join(self.config.resource_groups)
            return f"[?resourceGroup == '{rgs}']"
        return ""

    def collect_vnets(self) -> list:
        """Collect all Virtual Networks."""
        print("  Collecting Virtual Networks...")
        cmd = ["network", "vnet", "list"]
        if self.config.subscription_id:
            cmd.extend(["--subscription", self.config.subscription_id])

        vnets = run_az_command(cmd) or []

        # Enrich with subnet details
        for vnet in vnets:
            vnet["subnets_detail"] = []
            for subnet in vnet.get("subnets", []):
                subnet_info = {
                    "name": subnet.get("name"),
                    "id": subnet.get("id"),
                    "addressPrefix": subnet.get("addressPrefix"),
                    "addressPrefixes": subnet.get("addressPrefixes", []),
                    "nsg": subnet.get("networkSecurityGroup", {}).get("id") if subnet.get("networkSecurityGroup") else None,
                    "routeTable": subnet.get("routeTable", {}).get("id") if subnet.get("routeTable") else None,
                    "serviceEndpoints": [se.get("service") for se in subnet.get("serviceEndpoints", [])],
                    "delegations": [d.get("serviceName") for d in subnet.get("delegations", [])],
                    "privateEndpointNetworkPolicies": subnet.get("privateEndpointNetworkPolicies"),
                    "natGateway": subnet.get("natGateway", {}).get("id") if subnet.get("natGateway") else None,
                }
                vnet["subnets_detail"].append(subnet_info)

        print(f"    Found {len(vnets)} VNets")
        return vnets

    def collect_subnets(self) -> list:
        """Collect all subnets with their configurations."""
        print("  Collecting Subnets...")
        subnets = []

        # Get subnets from vnets
        cmd = ["network", "vnet", "list"]
        if self.config.subscription_id:
            cmd.extend(["--subscription", self.config.subscription_id])

        vnets = run_az_command(cmd) or []

        for vnet in vnets:
            vnet_name = vnet.get("name")
            rg = vnet.get("resourceGroup")

            for subnet in vnet.get("subnets", []):
                subnet_data = {
                    "name": subnet.get("name"),
                    "id": subnet.get("id"),
                    "vnet": vnet_name,
                    "resourceGroup": rg,
                    "addressPrefix": subnet.get("addressPrefix"),
                    "addressPrefixes": subnet.get("addressPrefixes", []),
                    "nsg_id": subnet.get("networkSecurityGroup", {}).get("id") if subnet.get("networkSecurityGroup") else None,
                    "routeTable_id": subnet.get("routeTable", {}).get("id") if subnet.get("routeTable") else None,
                    "serviceEndpoints": subnet.get("serviceEndpoints", []),
                    "delegations": subnet.get("delegations", []),
                    "ipConfigurations": subnet.get("ipConfigurations", []),
                    "privateEndpoints": subnet.get("privateEndpoints", []),
                }
                subnets.append(subnet_data)

        print(f"    Found {len(subnets)} Subnets")
        return subnets

    def collect_nsgs(self) -> list:
        """Collect all Network Security Groups with rules."""
        print("  Collecting Network Security Groups...")
        cmd = ["network", "nsg", "list"]
        if self.config.subscription_id:
            cmd.extend(["--subscription", self.config.subscription_id])

        nsgs = run_az_command(cmd) or []

        # Enrich with full rule details
        for nsg in nsgs:
            nsg_name = nsg.get("name")
            rg = nsg.get("resourceGroup")

            # Get detailed rules
            rules_cmd = ["network", "nsg", "rule", "list",
                        "--nsg-name", nsg_name,
                        "--resource-group", rg]
            if self.config.subscription_id:
                rules_cmd.extend(["--subscription", self.config.subscription_id])

            rules = run_az_command(rules_cmd) or []
            nsg["customRules"] = rules

            # Parse default rules
            nsg["defaultRulesProcessed"] = []
            for rule in nsg.get("defaultSecurityRules", []):
                nsg["defaultRulesProcessed"].append({
                    "name": rule.get("name"),
                    "priority": rule.get("priority"),
                    "direction": rule.get("direction"),
                    "access": rule.get("access"),
                    "protocol": rule.get("protocol"),
                    "sourceAddressPrefix": rule.get("sourceAddressPrefix"),
                    "sourcePortRange": rule.get("sourcePortRange"),
                    "destinationAddressPrefix": rule.get("destinationAddressPrefix"),
                    "destinationPortRange": rule.get("destinationPortRange"),
                })

        print(f"    Found {len(nsgs)} NSGs")
        return nsgs

    def collect_firewalls(self) -> list:
        """Collect Azure Firewalls."""
        print("  Collecting Azure Firewalls...")
        cmd = ["network", "firewall", "list"]
        if self.config.subscription_id:
            cmd.extend(["--subscription", self.config.subscription_id])

        firewalls = run_az_command(cmd) or []

        for fw in firewalls:
            # Extract IP configurations
            fw["ipConfigurations_processed"] = []
            for ip_config in fw.get("ipConfigurations", []):
                fw["ipConfigurations_processed"].append({
                    "name": ip_config.get("name"),
                    "privateIpAddress": ip_config.get("privateIpAddress"),
                    "publicIpAddress": ip_config.get("publicIpAddress", {}).get("id") if ip_config.get("publicIpAddress") else None,
                    "subnet": ip_config.get("subnet", {}).get("id") if ip_config.get("subnet") else None,
                })

        print(f"    Found {len(firewalls)} Azure Firewalls")
        return firewalls

    def collect_firewall_policies(self) -> list:
        """Collect Firewall Policies with rule collections."""
        print("  Collecting Firewall Policies...")
        cmd = ["network", "firewall", "policy", "list"]
        if self.config.subscription_id:
            cmd.extend(["--subscription", self.config.subscription_id])

        policies = run_az_command(cmd) or []

        for policy in policies:
            policy_name = policy.get("name")
            rg = policy.get("resourceGroup")

            # Get rule collection groups
            rcg_cmd = ["network", "firewall", "policy", "rule-collection-group", "list",
                      "--policy-name", policy_name,
                      "--resource-group", rg]
            if self.config.subscription_id:
                rcg_cmd.extend(["--subscription", self.config.subscription_id])

            rcgs = run_az_command(rcg_cmd) or []
            policy["ruleCollectionGroups_detail"] = []

            for rcg in rcgs:
                rcg_data = {
                    "name": rcg.get("name"),
                    "priority": rcg.get("priority"),
                    "ruleCollections": []
                }

                for rc in rcg.get("ruleCollections", []):
                    rc_data = {
                        "name": rc.get("name"),
                        "priority": rc.get("priority"),
                        "ruleCollectionType": rc.get("ruleCollectionType"),
                        "action": rc.get("action", {}).get("type") if rc.get("action") else None,
                        "rules": []
                    }

                    for rule in rc.get("rules", []):
                        rule_data = {
                            "name": rule.get("name"),
                            "ruleType": rule.get("ruleType"),
                            "sourceAddresses": rule.get("sourceAddresses", []),
                            "sourceIpGroups": rule.get("sourceIpGroups", []),
                            "destinationAddresses": rule.get("destinationAddresses", []),
                            "destinationIpGroups": rule.get("destinationIpGroups", []),
                            "destinationFqdns": rule.get("destinationFqdns", []),
                            "destinationPorts": rule.get("destinationPorts", []),
                            "protocols": rule.get("protocols", []),
                            "targetFqdns": rule.get("targetFqdns", []),
                            "targetUrls": rule.get("targetUrls", []),
                            "ipProtocols": rule.get("ipProtocols", []),
                            "translatedAddress": rule.get("translatedAddress"),
                            "translatedPort": rule.get("translatedPort"),
                        }
                        rc_data["rules"].append(rule_data)

                    rcg_data["ruleCollections"].append(rc_data)

                policy["ruleCollectionGroups_detail"].append(rcg_data)

        print(f"    Found {len(policies)} Firewall Policies")
        return policies

    def collect_route_tables(self) -> list:
        """Collect Route Tables."""
        print("  Collecting Route Tables...")
        cmd = ["network", "route-table", "list"]
        if self.config.subscription_id:
            cmd.extend(["--subscription", self.config.subscription_id])

        route_tables = run_az_command(cmd) or []

        for rt in route_tables:
            rt["routes_processed"] = []
            for route in rt.get("routes", []):
                rt["routes_processed"].append({
                    "name": route.get("name"),
                    "addressPrefix": route.get("addressPrefix"),
                    "nextHopType": route.get("nextHopType"),
                    "nextHopIpAddress": route.get("nextHopIpAddress"),
                })

        print(f"    Found {len(route_tables)} Route Tables")
        return route_tables

    def collect_private_endpoints(self) -> list:
        """Collect Private Endpoints."""
        print("  Collecting Private Endpoints...")
        cmd = ["network", "private-endpoint", "list"]
        if self.config.subscription_id:
            cmd.extend(["--subscription", self.config.subscription_id])

        endpoints = run_az_command(cmd) or []

        for ep in endpoints:
            ep["connections"] = []
            for conn in ep.get("privateLinkServiceConnections", []) + ep.get("manualPrivateLinkServiceConnections", []):
                ep["connections"].append({
                    "name": conn.get("name"),
                    "privateLinkServiceId": conn.get("privateLinkServiceId"),
                    "groupIds": conn.get("groupIds", []),
                    "status": conn.get("privateLinkServiceConnectionState", {}).get("status"),
                })

        print(f"    Found {len(endpoints)} Private Endpoints")
        return endpoints

    def collect_peerings(self) -> list:
        """Collect VNet Peerings."""
        print("  Collecting VNet Peerings...")
        peerings = []

        cmd = ["network", "vnet", "list"]
        if self.config.subscription_id:
            cmd.extend(["--subscription", self.config.subscription_id])

        vnets = run_az_command(cmd) or []

        for vnet in vnets:
            vnet_name = vnet.get("name")
            rg = vnet.get("resourceGroup")

            peering_cmd = ["network", "vnet", "peering", "list",
                          "--vnet-name", vnet_name,
                          "--resource-group", rg]
            if self.config.subscription_id:
                peering_cmd.extend(["--subscription", self.config.subscription_id])

            vnet_peerings = run_az_command(peering_cmd) or []

            for peering in vnet_peerings:
                peerings.append({
                    "name": peering.get("name"),
                    "id": peering.get("id"),
                    "sourceVnet": vnet_name,
                    "sourceResourceGroup": rg,
                    "remoteVnetId": peering.get("remoteVirtualNetwork", {}).get("id"),
                    "peeringState": peering.get("peeringState"),
                    "allowVirtualNetworkAccess": peering.get("allowVirtualNetworkAccess"),
                    "allowForwardedTraffic": peering.get("allowForwardedTraffic"),
                    "allowGatewayTransit": peering.get("allowGatewayTransit"),
                    "useRemoteGateways": peering.get("useRemoteGateways"),
                    "peeringSyncLevel": peering.get("peeringSyncLevel"),
                })

        print(f"    Found {len(peerings)} VNet Peerings")
        return peerings

    def collect_public_ips(self) -> list:
        """Collect Public IP Addresses."""
        print("  Collecting Public IPs...")
        cmd = ["network", "public-ip", "list"]
        if self.config.subscription_id:
            cmd.extend(["--subscription", self.config.subscription_id])

        public_ips = run_az_command(cmd) or []
        print(f"    Found {len(public_ips)} Public IPs")
        return public_ips

    def collect_private_dns_zones(self) -> list:
        """Collect Private DNS Zones."""
        print("  Collecting Private DNS Zones...")
        cmd = ["network", "private-dns", "zone", "list"]
        if self.config.subscription_id:
            cmd.extend(["--subscription", self.config.subscription_id])

        zones = run_az_command(cmd) or []

        for zone in zones:
            zone_name = zone.get("name")
            rg = zone.get("resourceGroup")

            # Get virtual network links
            links_cmd = ["network", "private-dns", "link", "vnet", "list",
                        "--zone-name", zone_name,
                        "--resource-group", rg]
            if self.config.subscription_id:
                links_cmd.extend(["--subscription", self.config.subscription_id])

            links = run_az_command(links_cmd) or []
            zone["virtualNetworkLinks"] = links

        print(f"    Found {len(zones)} Private DNS Zones")
        return zones

    def collect_app_gateways(self) -> list:
        """Collect Application Gateways."""
        print("  Collecting Application Gateways...")
        cmd = ["network", "application-gateway", "list"]
        if self.config.subscription_id:
            cmd.extend(["--subscription", self.config.subscription_id])

        gateways = run_az_command(cmd) or []
        print(f"    Found {len(gateways)} Application Gateways")
        return gateways

    def collect_load_balancers(self) -> list:
        """Collect Load Balancers."""
        print("  Collecting Load Balancers...")
        cmd = ["network", "lb", "list"]
        if self.config.subscription_id:
            cmd.extend(["--subscription", self.config.subscription_id])

        lbs = run_az_command(cmd) or []
        print(f"    Found {len(lbs)} Load Balancers")
        return lbs

    def collect_vnet_gateways(self) -> list:
        """Collect Virtual Network Gateways."""
        print("  Collecting VNet Gateways...")
        cmd = ["network", "vnet-gateway", "list"]
        if self.config.subscription_id:
            cmd.extend(["--subscription", self.config.subscription_id])

        gateways = run_az_command(cmd) or []
        print(f"    Found {len(gateways)} VNet Gateways")
        return gateways

    def collect_bastion_hosts(self) -> list:
        """Collect Bastion Hosts."""
        print("  Collecting Bastion Hosts...")
        cmd = ["network", "bastion", "list"]
        if self.config.subscription_id:
            cmd.extend(["--subscription", self.config.subscription_id])

        bastions = run_az_command(cmd) or []
        print(f"    Found {len(bastions)} Bastion Hosts")
        return bastions

    def collect_network_interfaces(self) -> list:
        """Collect Network Interfaces."""
        print("  Collecting Network Interfaces...")
        cmd = ["network", "nic", "list"]
        if self.config.subscription_id:
            cmd.extend(["--subscription", self.config.subscription_id])

        nics = run_az_command(cmd) or []
        print(f"    Found {len(nics)} Network Interfaces")
        return nics
