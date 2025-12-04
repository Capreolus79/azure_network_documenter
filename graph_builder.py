"""
Network Graph Builder
Builds a graph representation of the Azure network and analyzes connectivity.
"""

from dataclasses import dataclass, field
from typing import Optional
import ipaddress


@dataclass
class NetworkNode:
    """Represents a node in the network graph."""
    id: str
    name: str
    type: str  # vnet, subnet, nsg, firewall, vm, private_endpoint, etc.
    resource_group: str = ""
    properties: dict = field(default_factory=dict)
    parent_id: Optional[str] = None


@dataclass
class NetworkEdge:
    """Represents a connection/relationship between nodes."""
    source_id: str
    target_id: str
    edge_type: str  # contains, peering, routes_to, secured_by, allows, denies
    properties: dict = field(default_factory=dict)
    bidirectional: bool = False


@dataclass
class AccessRule:
    """Represents a network access rule."""
    source: str
    destination: str
    port: str
    protocol: str
    action: str  # Allow/Deny
    priority: int
    rule_source: str  # NSG name, Firewall policy, etc.
    direction: str  # Inbound/Outbound


class NetworkGraphBuilder:
    """Builds and analyzes network topology graph."""

    def __init__(self):
        self.nodes: dict[str, NetworkNode] = {}
        self.edges: list[NetworkEdge] = []
        self.access_rules: list[AccessRule] = []
        self.connectivity_matrix: dict = {}

    def build(self, network_data: dict) -> dict:
        """Build the network graph from collected data."""
        self.nodes.clear()
        self.edges.clear()
        self.access_rules.clear()

        # Process VNets
        self._process_vnets(network_data.get("vnets", []))

        # Process Subnets
        self._process_subnets(network_data.get("subnets", []))

        # Process NSGs
        self._process_nsgs(network_data.get("nsgs", []))

        # Process Firewalls
        self._process_firewalls(network_data.get("firewalls", []))

        # Process Firewall Policies
        self._process_firewall_policies(network_data.get("firewall_policies", []))

        # Process Route Tables
        self._process_route_tables(network_data.get("route_tables", []))

        # Process Private Endpoints
        self._process_private_endpoints(network_data.get("private_endpoints", []))

        # Process Peerings
        self._process_peerings(network_data.get("peerings", []))

        # Process Public IPs
        self._process_public_ips(network_data.get("public_ips", []))

        # Process Application Gateways
        self._process_app_gateways(network_data.get("application_gateways", []))

        # Process Load Balancers
        self._process_load_balancers(network_data.get("load_balancers", []))

        # Process VNet Gateways
        self._process_vnet_gateways(network_data.get("virtual_network_gateways", []))

        # Process Bastion Hosts
        self._process_bastion_hosts(network_data.get("bastion_hosts", []))

        # Process NICs to find VMs
        self._process_nics(network_data.get("nics", []))

        # Process Private DNS Zones
        self._process_dns_zones(network_data.get("private_dns_zones", []))

        return self.get_graph_data()

    def _add_node(self, node: NetworkNode):
        """Add a node to the graph."""
        self.nodes[node.id] = node

    def _add_edge(self, edge: NetworkEdge):
        """Add an edge to the graph."""
        self.edges.append(edge)

    def _extract_name_from_id(self, resource_id: str) -> str:
        """Extract resource name from Azure resource ID."""
        if not resource_id:
            return ""
        parts = resource_id.split("/")
        return parts[-1] if parts else ""

    def _process_vnets(self, vnets: list):
        """Process Virtual Networks."""
        for vnet in vnets:
            node = NetworkNode(
                id=vnet.get("id", ""),
                name=vnet.get("name", ""),
                type="vnet",
                resource_group=vnet.get("resourceGroup", ""),
                properties={
                    "addressSpace": vnet.get("addressSpace", {}).get("addressPrefixes", []),
                    "location": vnet.get("location", ""),
                    "dnsServers": vnet.get("dhcpOptions", {}).get("dnsServers", []) if vnet.get("dhcpOptions") else [],
                    "enableDdosProtection": vnet.get("enableDdosProtection", False),
                    "subnets": [s.get("name") for s in vnet.get("subnets", [])],
                }
            )
            self._add_node(node)

    def _process_subnets(self, subnets: list):
        """Process Subnets."""
        for subnet in subnets:
            vnet_name = subnet.get("vnet", "")
            subnet_id = subnet.get("id", "")

            # Find parent VNet
            parent_vnet_id = None
            for node_id, node in self.nodes.items():
                if node.type == "vnet" and node.name == vnet_name:
                    parent_vnet_id = node_id
                    break

            node = NetworkNode(
                id=subnet_id,
                name=subnet.get("name", ""),
                type="subnet",
                resource_group=subnet.get("resourceGroup", ""),
                parent_id=parent_vnet_id,
                properties={
                    "addressPrefix": subnet.get("addressPrefix", ""),
                    "addressPrefixes": subnet.get("addressPrefixes", []),
                    "vnet": vnet_name,
                    "nsg": self._extract_name_from_id(subnet.get("nsg_id")),
                    "routeTable": self._extract_name_from_id(subnet.get("routeTable_id")),
                    "serviceEndpoints": [se.get("service") for se in subnet.get("serviceEndpoints", [])],
                    "delegations": [d.get("serviceName") for d in subnet.get("delegations", [])],
                    "ipConfigCount": len(subnet.get("ipConfigurations", [])),
                    "privateEndpointCount": len(subnet.get("privateEndpoints", [])),
                }
            )
            self._add_node(node)

            # Add edge to parent VNet
            if parent_vnet_id:
                self._add_edge(NetworkEdge(
                    source_id=parent_vnet_id,
                    target_id=subnet_id,
                    edge_type="contains"
                ))

            # Add edge to NSG if exists
            if subnet.get("nsg_id"):
                self._add_edge(NetworkEdge(
                    source_id=subnet_id,
                    target_id=subnet.get("nsg_id"),
                    edge_type="secured_by"
                ))

            # Add edge to Route Table if exists
            if subnet.get("routeTable_id"):
                self._add_edge(NetworkEdge(
                    source_id=subnet_id,
                    target_id=subnet.get("routeTable_id"),
                    edge_type="routes_via"
                ))

    def _process_nsgs(self, nsgs: list):
        """Process Network Security Groups and their rules."""
        for nsg in nsgs:
            node = NetworkNode(
                id=nsg.get("id", ""),
                name=nsg.get("name", ""),
                type="nsg",
                resource_group=nsg.get("resourceGroup", ""),
                properties={
                    "location": nsg.get("location", ""),
                    "customRuleCount": len(nsg.get("customRules", [])),
                    "associatedSubnets": [self._extract_name_from_id(s.get("id")) for s in nsg.get("subnets", [])],
                    "associatedNics": [self._extract_name_from_id(n.get("id")) for n in nsg.get("networkInterfaces", [])],
                }
            )
            self._add_node(node)

            # Process security rules
            for rule in nsg.get("securityRules", []) + nsg.get("customRules", []):
                access_rule = AccessRule(
                    source=self._format_address(
                        rule.get("sourceAddressPrefix"),
                        rule.get("sourceAddressPrefixes", [])
                    ),
                    destination=self._format_address(
                        rule.get("destinationAddressPrefix"),
                        rule.get("destinationAddressPrefixes", [])
                    ),
                    port=self._format_ports(
                        rule.get("destinationPortRange"),
                        rule.get("destinationPortRanges", [])
                    ),
                    protocol=rule.get("protocol", "*"),
                    action=rule.get("access", ""),
                    priority=rule.get("priority", 0),
                    rule_source=f"NSG: {nsg.get('name')}",
                    direction=rule.get("direction", "")
                )
                self.access_rules.append(access_rule)

    def _process_firewalls(self, firewalls: list):
        """Process Azure Firewalls."""
        for fw in firewalls:
            node = NetworkNode(
                id=fw.get("id", ""),
                name=fw.get("name", ""),
                type="firewall",
                resource_group=fw.get("resourceGroup", ""),
                properties={
                    "location": fw.get("location", ""),
                    "sku": fw.get("sku", {}).get("tier", ""),
                    "threatIntelMode": fw.get("threatIntelMode", ""),
                    "firewallPolicy": self._extract_name_from_id(fw.get("firewallPolicy", {}).get("id")) if fw.get("firewallPolicy") else None,
                    "ipConfigurations": fw.get("ipConfigurations_processed", []),
                    "privateIp": next((ip.get("privateIpAddress") for ip in fw.get("ipConfigurations_processed", []) if ip.get("privateIpAddress")), None),
                }
            )
            self._add_node(node)

            # Add edges to subnets
            for ip_config in fw.get("ipConfigurations_processed", []):
                if ip_config.get("subnet"):
                    self._add_edge(NetworkEdge(
                        source_id=ip_config.get("subnet"),
                        target_id=fw.get("id"),
                        edge_type="contains"
                    ))

    def _process_firewall_policies(self, policies: list):
        """Process Firewall Policies and rules."""
        for policy in policies:
            node = NetworkNode(
                id=policy.get("id", ""),
                name=policy.get("name", ""),
                type="firewall_policy",
                resource_group=policy.get("resourceGroup", ""),
                properties={
                    "location": policy.get("location", ""),
                    "sku": policy.get("sku", {}).get("tier", ""),
                    "threatIntelMode": policy.get("threatIntelMode", ""),
                    "ruleCollectionGroupCount": len(policy.get("ruleCollectionGroups_detail", [])),
                }
            )
            self._add_node(node)

            # Process rule collections
            for rcg in policy.get("ruleCollectionGroups_detail", []):
                for rc in rcg.get("ruleCollections", []):
                    for rule in rc.get("rules", []):
                        rule_type = rule.get("ruleType", "")

                        if rule_type == "NetworkRule":
                            access_rule = AccessRule(
                                source=", ".join(rule.get("sourceAddresses", []) + rule.get("sourceIpGroups", [])),
                                destination=", ".join(rule.get("destinationAddresses", []) + rule.get("destinationFqdns", [])),
                                port=", ".join(rule.get("destinationPorts", [])),
                                protocol=", ".join(rule.get("ipProtocols", [])),
                                action=rc.get("action", ""),
                                priority=rc.get("priority", 0),
                                rule_source=f"FW Policy: {policy.get('name')} / {rcg.get('name')} / {rc.get('name')}",
                                direction="Outbound"
                            )
                            self.access_rules.append(access_rule)

                        elif rule_type == "ApplicationRule":
                            access_rule = AccessRule(
                                source=", ".join(rule.get("sourceAddresses", []) + rule.get("sourceIpGroups", [])),
                                destination=", ".join(rule.get("targetFqdns", []) + rule.get("targetUrls", [])),
                                port=", ".join([f"{p.get('port')}/{p.get('protocolType')}" for p in rule.get("protocols", [])]) if rule.get("protocols") else "*",
                                protocol="HTTP/HTTPS",
                                action=rc.get("action", ""),
                                priority=rc.get("priority", 0),
                                rule_source=f"FW Policy: {policy.get('name')} / {rcg.get('name')} / {rc.get('name')}",
                                direction="Outbound"
                            )
                            self.access_rules.append(access_rule)

                        elif rule_type == "NatRule":
                            access_rule = AccessRule(
                                source=", ".join(rule.get("sourceAddresses", []) + rule.get("sourceIpGroups", [])),
                                destination=f"{rule.get('translatedAddress')}:{rule.get('translatedPort')}",
                                port=", ".join(rule.get("destinationPorts", [])),
                                protocol=", ".join(rule.get("ipProtocols", [])),
                                action="DNAT",
                                priority=rc.get("priority", 0),
                                rule_source=f"FW Policy: {policy.get('name')} / {rcg.get('name')} / {rc.get('name')}",
                                direction="Inbound"
                            )
                            self.access_rules.append(access_rule)

    def _process_route_tables(self, route_tables: list):
        """Process Route Tables."""
        for rt in route_tables:
            node = NetworkNode(
                id=rt.get("id", ""),
                name=rt.get("name", ""),
                type="route_table",
                resource_group=rt.get("resourceGroup", ""),
                properties={
                    "location": rt.get("location", ""),
                    "routes": rt.get("routes_processed", []),
                    "disableBgpRoutePropagation": rt.get("disableBgpRoutePropagation", False),
                    "associatedSubnets": [self._extract_name_from_id(s.get("id")) for s in rt.get("subnets", [])],
                }
            )
            self._add_node(node)

    def _process_private_endpoints(self, endpoints: list):
        """Process Private Endpoints."""
        for ep in endpoints:
            node = NetworkNode(
                id=ep.get("id", ""),
                name=ep.get("name", ""),
                type="private_endpoint",
                resource_group=ep.get("resourceGroup", ""),
                properties={
                    "location": ep.get("location", ""),
                    "subnet": self._extract_name_from_id(ep.get("subnet", {}).get("id")) if ep.get("subnet") else None,
                    "connections": ep.get("connections", []),
                    "customDnsConfigs": ep.get("customDnsConfigs", []),
                }
            )
            self._add_node(node)

            # Add edge to subnet
            if ep.get("subnet", {}).get("id"):
                self._add_edge(NetworkEdge(
                    source_id=ep.get("subnet", {}).get("id"),
                    target_id=ep.get("id"),
                    edge_type="contains"
                ))

    def _process_peerings(self, peerings: list):
        """Process VNet Peerings."""
        for peering in peerings:
            # Find source VNet
            source_vnet_id = None
            for node_id, node in self.nodes.items():
                if node.type == "vnet" and node.name == peering.get("sourceVnet"):
                    source_vnet_id = node_id
                    break

            if source_vnet_id and peering.get("remoteVnetId"):
                self._add_edge(NetworkEdge(
                    source_id=source_vnet_id,
                    target_id=peering.get("remoteVnetId"),
                    edge_type="peering",
                    bidirectional=peering.get("peeringState") == "Connected",
                    properties={
                        "name": peering.get("name"),
                        "state": peering.get("peeringState"),
                        "allowVnetAccess": peering.get("allowVirtualNetworkAccess"),
                        "allowForwardedTraffic": peering.get("allowForwardedTraffic"),
                        "allowGatewayTransit": peering.get("allowGatewayTransit"),
                        "useRemoteGateways": peering.get("useRemoteGateways"),
                    }
                ))

    def _process_public_ips(self, public_ips: list):
        """Process Public IP Addresses."""
        for pip in public_ips:
            node = NetworkNode(
                id=pip.get("id", ""),
                name=pip.get("name", ""),
                type="public_ip",
                resource_group=pip.get("resourceGroup", ""),
                properties={
                    "ipAddress": pip.get("ipAddress", ""),
                    "sku": pip.get("sku", {}).get("name", ""),
                    "allocationMethod": pip.get("publicIPAllocationMethod", ""),
                    "associatedTo": self._extract_name_from_id(pip.get("ipConfiguration", {}).get("id")) if pip.get("ipConfiguration") else None,
                }
            )
            self._add_node(node)

    def _process_app_gateways(self, gateways: list):
        """Process Application Gateways."""
        for gw in gateways:
            node = NetworkNode(
                id=gw.get("id", ""),
                name=gw.get("name", ""),
                type="application_gateway",
                resource_group=gw.get("resourceGroup", ""),
                properties={
                    "location": gw.get("location", ""),
                    "sku": gw.get("sku", {}),
                    "backendPools": [p.get("name") for p in gw.get("backendAddressPools", [])],
                    "listeners": [l.get("name") for l in gw.get("httpListeners", [])],
                }
            )
            self._add_node(node)

    def _process_load_balancers(self, lbs: list):
        """Process Load Balancers."""
        for lb in lbs:
            node = NetworkNode(
                id=lb.get("id", ""),
                name=lb.get("name", ""),
                type="load_balancer",
                resource_group=lb.get("resourceGroup", ""),
                properties={
                    "location": lb.get("location", ""),
                    "sku": lb.get("sku", {}).get("name", ""),
                    "frontendIpConfigurations": [f.get("name") for f in lb.get("frontendIpConfigurations", [])],
                    "backendPools": [b.get("name") for b in lb.get("backendAddressPools", [])],
                    "rules": [r.get("name") for r in lb.get("loadBalancingRules", [])],
                }
            )
            self._add_node(node)

    def _process_vnet_gateways(self, gateways: list):
        """Process VNet Gateways."""
        for gw in gateways:
            node = NetworkNode(
                id=gw.get("id", ""),
                name=gw.get("name", ""),
                type="vnet_gateway",
                resource_group=gw.get("resourceGroup", ""),
                properties={
                    "location": gw.get("location", ""),
                    "gatewayType": gw.get("gatewayType", ""),
                    "vpnType": gw.get("vpnType", ""),
                    "sku": gw.get("sku", {}).get("name", ""),
                    "activeActive": gw.get("activeActive", False),
                }
            )
            self._add_node(node)

    def _process_bastion_hosts(self, bastions: list):
        """Process Bastion Hosts."""
        for bastion in bastions:
            node = NetworkNode(
                id=bastion.get("id", ""),
                name=bastion.get("name", ""),
                type="bastion",
                resource_group=bastion.get("resourceGroup", ""),
                properties={
                    "location": bastion.get("location", ""),
                    "sku": bastion.get("sku", {}).get("name", ""),
                    "scaleUnits": bastion.get("scaleUnits", 2),
                }
            )
            self._add_node(node)

    def _process_nics(self, nics: list):
        """Process Network Interfaces to identify VMs."""
        for nic in nics:
            # Check if attached to a VM
            vm_id = nic.get("virtualMachine", {}).get("id") if nic.get("virtualMachine") else None

            if vm_id:
                vm_name = self._extract_name_from_id(vm_id)
                if vm_id not in self.nodes:
                    node = NetworkNode(
                        id=vm_id,
                        name=vm_name,
                        type="vm",
                        resource_group=nic.get("resourceGroup", ""),
                        properties={
                            "nics": [],
                            "privateIps": [],
                            "subnets": [],
                        }
                    )
                    self._add_node(node)

                # Add NIC info to VM
                for ip_config in nic.get("ipConfigurations", []):
                    private_ip = ip_config.get("privateIPAddress")
                    subnet_id = ip_config.get("subnet", {}).get("id") if ip_config.get("subnet") else None

                    if private_ip:
                        self.nodes[vm_id].properties["privateIps"].append(private_ip)
                    if subnet_id:
                        self.nodes[vm_id].properties["subnets"].append(self._extract_name_from_id(subnet_id))

                        # Add edge to subnet
                        self._add_edge(NetworkEdge(
                            source_id=subnet_id,
                            target_id=vm_id,
                            edge_type="contains"
                        ))

    def _process_dns_zones(self, zones: list):
        """Process Private DNS Zones."""
        for zone in zones:
            node = NetworkNode(
                id=zone.get("id", ""),
                name=zone.get("name", ""),
                type="private_dns_zone",
                resource_group=zone.get("resourceGroup", ""),
                properties={
                    "recordCount": zone.get("numberOfRecordSets", 0),
                    "linkedVnets": [self._extract_name_from_id(l.get("virtualNetwork", {}).get("id"))
                                   for l in zone.get("virtualNetworkLinks", [])
                                   if l.get("virtualNetwork")],
                }
            )
            self._add_node(node)

            # Add edges to linked VNets
            for link in zone.get("virtualNetworkLinks", []):
                vnet_id = link.get("virtualNetwork", {}).get("id") if link.get("virtualNetwork") else None
                if vnet_id:
                    self._add_edge(NetworkEdge(
                        source_id=zone.get("id"),
                        target_id=vnet_id,
                        edge_type="dns_linked"
                    ))

    def _format_address(self, single: str, multiple: list) -> str:
        """Format address prefix(es) for display."""
        if multiple:
            return ", ".join(multiple)
        return single or "*"

    def _format_ports(self, single: str, multiple: list) -> str:
        """Format port range(s) for display."""
        if multiple:
            return ", ".join(multiple)
        return single or "*"

    def analyze_connectivity(self) -> dict:
        """Analyze what can connect to what based on rules."""
        self.connectivity_matrix = {
            "subnets": {},
            "rules_summary": [],
            "potential_issues": [],
        }

        # Get all subnets
        subnets = {nid: node for nid, node in self.nodes.items() if node.type == "subnet"}

        # Build connectivity between subnets
        for subnet_id, subnet in subnets.items():
            self.connectivity_matrix["subnets"][subnet.name] = {
                "vnet": subnet.properties.get("vnet"),
                "addressPrefix": subnet.properties.get("addressPrefix"),
                "can_reach": [],
                "reachable_from": [],
                "nsg": subnet.properties.get("nsg"),
                "has_internet_access": self._check_internet_access(subnet),
            }

        # Analyze peerings for inter-vnet connectivity
        for edge in self.edges:
            if edge.edge_type == "peering":
                source_vnet = self._extract_name_from_id(edge.source_id)
                target_vnet = self._extract_name_from_id(edge.target_id)

                # Find subnets in each VNet
                source_subnets = [s for s in subnets.values() if s.properties.get("vnet") == source_vnet]
                target_subnets = [s for s in subnets.values() if s.properties.get("vnet") == target_vnet]

                for src in source_subnets:
                    for tgt in target_subnets:
                        if edge.properties.get("allowVnetAccess"):
                            self.connectivity_matrix["subnets"][src.name]["can_reach"].append({
                                "subnet": tgt.name,
                                "via": "VNet Peering",
                                "vnet": target_vnet,
                            })

        # Analyze rules for access patterns
        for rule in self.access_rules:
            self.connectivity_matrix["rules_summary"].append({
                "source": rule.source,
                "destination": rule.destination,
                "port": rule.port,
                "protocol": rule.protocol,
                "action": rule.action,
                "direction": rule.direction,
                "rule_source": rule.rule_source,
            })

        # Identify potential issues
        self._identify_issues()

        return self.connectivity_matrix

    def _check_internet_access(self, subnet: NetworkNode) -> bool:
        """Check if subnet has internet access based on route tables and NSGs."""
        # Check for 0.0.0.0/0 route
        for node in self.nodes.values():
            if node.type == "route_table" and subnet.name in node.properties.get("associatedSubnets", []):
                for route in node.properties.get("routes", []):
                    if route.get("addressPrefix") == "0.0.0.0/0":
                        if route.get("nextHopType") == "Internet":
                            return True
                        elif route.get("nextHopType") in ["VirtualAppliance", "VirtualNetworkGateway"]:
                            return True  # Via NVA/Gateway

        # If no explicit route, Azure provides default internet access
        return True

    def _identify_issues(self):
        """Identify potential network security issues."""
        issues = []

        # Check for overly permissive rules
        for rule in self.access_rules:
            if rule.action.lower() == "allow":
                if rule.source == "*" and rule.destination == "*":
                    issues.append({
                        "severity": "High",
                        "issue": "Overly permissive rule allowing all traffic",
                        "rule_source": rule.rule_source,
                        "recommendation": "Restrict source and destination addresses"
                    })

                if rule.port == "*" and rule.source == "*":
                    issues.append({
                        "severity": "Medium",
                        "issue": "Rule allows all ports from any source",
                        "rule_source": rule.rule_source,
                        "recommendation": "Restrict ports and source addresses"
                    })

                # Check for risky ports open to internet
                risky_ports = ["22", "3389", "445", "1433", "3306", "5432"]
                if rule.source in ["*", "Internet", "0.0.0.0/0"]:
                    for port in risky_ports:
                        if port in rule.port or rule.port == "*":
                            issues.append({
                                "severity": "High",
                                "issue": f"Risky port {port} exposed to internet",
                                "rule_source": rule.rule_source,
                                "recommendation": f"Restrict access to port {port} from specific IPs only"
                            })
                            break

        # Check for subnets without NSGs
        for subnet_name, subnet_info in self.connectivity_matrix.get("subnets", {}).items():
            if not subnet_info.get("nsg") and "Gateway" not in subnet_name:
                issues.append({
                    "severity": "Medium",
                    "issue": f"Subnet '{subnet_name}' has no NSG attached",
                    "recommendation": "Attach an NSG to control traffic"
                })

        self.connectivity_matrix["potential_issues"] = issues

    def get_graph_data(self) -> dict:
        """Get graph data in a format suitable for visualization."""
        nodes_list = []
        for node_id, node in self.nodes.items():
            nodes_list.append({
                "id": node_id,
                "name": node.name,
                "type": node.type,
                "resourceGroup": node.resource_group,
                "properties": node.properties,
                "parentId": node.parent_id,
            })

        edges_list = []
        for edge in self.edges:
            edges_list.append({
                "source": edge.source_id,
                "target": edge.target_id,
                "type": edge.edge_type,
                "properties": edge.properties,
                "bidirectional": edge.bidirectional,
            })

        return {
            "nodes": nodes_list,
            "edges": edges_list,
            "rules": [
                {
                    "source": r.source,
                    "destination": r.destination,
                    "port": r.port,
                    "protocol": r.protocol,
                    "action": r.action,
                    "priority": r.priority,
                    "ruleSource": r.rule_source,
                    "direction": r.direction,
                }
                for r in self.access_rules
            ]
        }

    def get_connectivity_matrix(self) -> dict:
        """Get the connectivity analysis results."""
        return self.connectivity_matrix
