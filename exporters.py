"""
Exporters
Export network documentation to various formats.
"""

import json
from pathlib import Path
from datetime import datetime


class MarkdownExporter:
    """Export network documentation as Markdown."""

    def export(self, network_data: dict, connectivity: dict, output_path: str) -> str:
        """Export to Markdown file."""
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)

        md = self._build_markdown(network_data, connectivity)

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(md)

        return output_path

    def _build_markdown(self, data: dict, connectivity: dict) -> str:
        """Build Markdown content."""
        lines = [
            "# Azure Network Documentation",
            "",
            f"*Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*",
            "",
            "---",
            "",
            "## Table of Contents",
            "",
            "1. [Summary](#summary)",
            "2. [Virtual Networks](#virtual-networks)",
            "3. [Subnets](#subnets)",
            "4. [Network Security Groups](#network-security-groups)",
            "5. [Azure Firewalls](#azure-firewalls)",
            "6. [Firewall Policies](#firewall-policies)",
            "7. [Route Tables](#route-tables)",
            "8. [VNet Peerings](#vnet-peerings)",
            "9. [Private Endpoints](#private-endpoints)",
            "10. [Load Balancers](#load-balancers)",
            "11. [Application Gateways](#application-gateways)",
            "12. [Connectivity Analysis](#connectivity-analysis)",
            "13. [Security Issues](#security-issues)",
            "",
            "---",
            "",
        ]

        # Summary
        lines.extend(self._build_summary(data))

        # Virtual Networks
        lines.extend(self._build_vnets_section(data.get("vnets", [])))

        # Subnets
        lines.extend(self._build_subnets_section(data.get("subnets", [])))

        # NSGs
        lines.extend(self._build_nsgs_section(data.get("nsgs", [])))

        # Firewalls
        lines.extend(self._build_firewalls_section(data.get("firewalls", [])))

        # Firewall Policies
        lines.extend(self._build_firewall_policies_section(data.get("firewall_policies", [])))

        # Route Tables
        lines.extend(self._build_route_tables_section(data.get("route_tables", [])))

        # Peerings
        lines.extend(self._build_peerings_section(data.get("peerings", [])))

        # Private Endpoints
        lines.extend(self._build_private_endpoints_section(data.get("private_endpoints", [])))

        # Load Balancers
        lines.extend(self._build_load_balancers_section(data.get("load_balancers", [])))

        # Application Gateways
        lines.extend(self._build_app_gateways_section(data.get("application_gateways", [])))

        # Connectivity Analysis
        lines.extend(self._build_connectivity_section(connectivity))

        # Security Issues
        lines.extend(self._build_issues_section(connectivity))

        return "\n".join(lines)

    def _build_summary(self, data: dict) -> list:
        """Build summary section."""
        lines = [
            "## Summary",
            "",
            "| Resource Type | Count |",
            "|--------------|-------|",
            f"| Virtual Networks | {len(data.get('vnets', []))} |",
            f"| Subnets | {len(data.get('subnets', []))} |",
            f"| Network Security Groups | {len(data.get('nsgs', []))} |",
            f"| Azure Firewalls | {len(data.get('firewalls', []))} |",
            f"| Firewall Policies | {len(data.get('firewall_policies', []))} |",
            f"| Route Tables | {len(data.get('route_tables', []))} |",
            f"| VNet Peerings | {len(data.get('peerings', []))} |",
            f"| Private Endpoints | {len(data.get('private_endpoints', []))} |",
            f"| Public IPs | {len(data.get('public_ips', []))} |",
            f"| Load Balancers | {len(data.get('load_balancers', []))} |",
            f"| Application Gateways | {len(data.get('application_gateways', []))} |",
            f"| VNet Gateways | {len(data.get('virtual_network_gateways', []))} |",
            f"| Bastion Hosts | {len(data.get('bastion_hosts', []))} |",
            "",
        ]
        return lines

    def _build_vnets_section(self, vnets: list) -> list:
        """Build VNets section."""
        lines = [
            "## Virtual Networks",
            "",
        ]

        if not vnets:
            lines.append("*No Virtual Networks found.*\n")
            return lines

        for vnet in vnets:
            lines.extend([
                f"### {vnet.get('name')}",
                "",
                f"- **Resource Group:** {vnet.get('resourceGroup')}",
                f"- **Location:** {vnet.get('location')}",
                f"- **Address Space:** {', '.join(vnet.get('addressSpace', {}).get('addressPrefixes', []))}",
            ])

            dns_servers = vnet.get('dhcpOptions', {}).get('dnsServers', []) if vnet.get('dhcpOptions') else []
            if dns_servers:
                lines.append(f"- **DNS Servers:** {', '.join(dns_servers)}")

            lines.append("")
            lines.append("#### Subnets")
            lines.append("")
            lines.append("| Subnet | Address Prefix | NSG | Route Table | Service Endpoints |")
            lines.append("|--------|----------------|-----|-------------|-------------------|")

            for subnet in vnet.get('subnets_detail', []):
                nsg = subnet.get('nsg', '-') or '-'
                rt = subnet.get('routeTable', '-') or '-'
                se = ', '.join(subnet.get('serviceEndpoints', [])) or '-'
                prefix = subnet.get('addressPrefix') or ', '.join(subnet.get('addressPrefixes', []))
                lines.append(f"| {subnet.get('name')} | {prefix} | {nsg} | {rt} | {se} |")

            lines.append("")

        return lines

    def _build_subnets_section(self, subnets: list) -> list:
        """Build detailed subnets section."""
        lines = [
            "## Subnets",
            "",
        ]

        if not subnets:
            lines.append("*No Subnets found.*\n")
            return lines

        # Group by VNet
        by_vnet = {}
        for subnet in subnets:
            vnet = subnet.get('vnet', 'Unknown')
            if vnet not in by_vnet:
                by_vnet[vnet] = []
            by_vnet[vnet].append(subnet)

        for vnet, vnet_subnets in sorted(by_vnet.items()):
            lines.append(f"### VNet: {vnet}")
            lines.append("")

            for subnet in vnet_subnets:
                lines.append(f"#### {subnet.get('name')}")
                lines.append("")
                lines.append(f"- **Address Prefix:** {subnet.get('addressPrefix')}")
                lines.append(f"- **Resource Group:** {subnet.get('resourceGroup')}")

                if subnet.get('nsg_id'):
                    lines.append(f"- **NSG:** {self._extract_name(subnet.get('nsg_id'))}")
                if subnet.get('routeTable_id'):
                    lines.append(f"- **Route Table:** {self._extract_name(subnet.get('routeTable_id'))}")

                delegations = [d.get('serviceName') for d in subnet.get('delegations', [])]
                if delegations:
                    lines.append(f"- **Delegations:** {', '.join(delegations)}")

                se = [s.get('service') for s in subnet.get('serviceEndpoints', [])]
                if se:
                    lines.append(f"- **Service Endpoints:** {', '.join(se)}")

                lines.append(f"- **IP Configurations:** {len(subnet.get('ipConfigurations', []))}")
                lines.append(f"- **Private Endpoints:** {len(subnet.get('privateEndpoints', []))}")
                lines.append("")

        return lines

    def _build_nsgs_section(self, nsgs: list) -> list:
        """Build NSGs section."""
        lines = [
            "## Network Security Groups",
            "",
        ]

        if not nsgs:
            lines.append("*No NSGs found.*\n")
            return lines

        for nsg in nsgs:
            lines.extend([
                f"### {nsg.get('name')}",
                "",
                f"- **Resource Group:** {nsg.get('resourceGroup')}",
                f"- **Location:** {nsg.get('location')}",
            ])

            associated_subnets = [self._extract_name(s.get('id')) for s in nsg.get('subnets', [])]
            if associated_subnets:
                lines.append(f"- **Associated Subnets:** {', '.join(associated_subnets)}")

            associated_nics = [self._extract_name(n.get('id')) for n in nsg.get('networkInterfaces', [])]
            if associated_nics:
                lines.append(f"- **Associated NICs:** {', '.join(associated_nics)}")

            lines.append("")
            lines.append("#### Security Rules")
            lines.append("")
            lines.append("| Priority | Name | Direction | Access | Protocol | Source | Dest | Ports |")
            lines.append("|----------|------|-----------|--------|----------|--------|------|-------|")

            all_rules = nsg.get('securityRules', []) + nsg.get('customRules', [])
            for rule in sorted(all_rules, key=lambda r: r.get('priority', 0)):
                src = rule.get('sourceAddressPrefix') or ', '.join(rule.get('sourceAddressPrefixes', []))
                dst = rule.get('destinationAddressPrefix') or ', '.join(rule.get('destinationAddressPrefixes', []))
                ports = rule.get('destinationPortRange') or ', '.join(rule.get('destinationPortRanges', []))

                lines.append(
                    f"| {rule.get('priority')} | {rule.get('name')} | {rule.get('direction')} | "
                    f"**{rule.get('access')}** | {rule.get('protocol')} | {src[:20]} | {dst[:20]} | {ports} |"
                )

            lines.append("")

        return lines

    def _build_firewalls_section(self, firewalls: list) -> list:
        """Build Azure Firewalls section."""
        lines = [
            "## Azure Firewalls",
            "",
        ]

        if not firewalls:
            lines.append("*No Azure Firewalls found.*\n")
            return lines

        for fw in firewalls:
            lines.extend([
                f"### {fw.get('name')}",
                "",
                f"- **Resource Group:** {fw.get('resourceGroup')}",
                f"- **Location:** {fw.get('location')}",
                f"- **SKU:** {fw.get('sku', {}).get('tier', 'N/A')}",
                f"- **Threat Intel Mode:** {fw.get('threatIntelMode', 'N/A')}",
            ])

            if fw.get('firewallPolicy'):
                lines.append(f"- **Firewall Policy:** {self._extract_name(fw.get('firewallPolicy', {}).get('id'))}")

            lines.append("")
            lines.append("#### IP Configurations")
            lines.append("")

            for ip_config in fw.get('ipConfigurations_processed', []):
                lines.append(f"- **{ip_config.get('name')}**")
                if ip_config.get('privateIpAddress'):
                    lines.append(f"  - Private IP: {ip_config.get('privateIpAddress')}")
                if ip_config.get('publicIpAddress'):
                    lines.append(f"  - Public IP: {self._extract_name(ip_config.get('publicIpAddress'))}")

            lines.append("")

        return lines

    def _build_firewall_policies_section(self, policies: list) -> list:
        """Build Firewall Policies section."""
        lines = [
            "## Firewall Policies",
            "",
        ]

        if not policies:
            lines.append("*No Firewall Policies found.*\n")
            return lines

        for policy in policies:
            lines.extend([
                f"### {policy.get('name')}",
                "",
                f"- **Resource Group:** {policy.get('resourceGroup')}",
                f"- **Location:** {policy.get('location')}",
                f"- **SKU:** {policy.get('sku', {}).get('tier', 'N/A')}",
                f"- **Threat Intel Mode:** {policy.get('threatIntelMode', 'N/A')}",
                "",
            ])

            for rcg in policy.get('ruleCollectionGroups_detail', []):
                lines.append(f"#### Rule Collection Group: {rcg.get('name')} (Priority: {rcg.get('priority')})")
                lines.append("")

                for rc in rcg.get('ruleCollections', []):
                    lines.append(f"##### {rc.get('name')} ({rc.get('ruleCollectionType')}) - Action: {rc.get('action')}")
                    lines.append("")
                    lines.append("| Rule | Type | Source | Destination | Ports | Protocols |")
                    lines.append("|------|------|--------|-------------|-------|-----------|")

                    for rule in rc.get('rules', []):
                        src = ', '.join(rule.get('sourceAddresses', [])[:2]) or '*'
                        dst = ', '.join(rule.get('destinationAddresses', []) + rule.get('destinationFqdns', []) + rule.get('targetFqdns', []))[:30] or '*'
                        ports = ', '.join(rule.get('destinationPorts', [])) or '*'
                        protocols = ', '.join(rule.get('protocols', []) + rule.get('ipProtocols', [])) or '*'

                        lines.append(f"| {rule.get('name')} | {rule.get('ruleType')} | {src} | {dst} | {ports} | {protocols} |")

                    lines.append("")

        return lines

    def _build_route_tables_section(self, route_tables: list) -> list:
        """Build Route Tables section."""
        lines = [
            "## Route Tables",
            "",
        ]

        if not route_tables:
            lines.append("*No Route Tables found.*\n")
            return lines

        for rt in route_tables:
            lines.extend([
                f"### {rt.get('name')}",
                "",
                f"- **Resource Group:** {rt.get('resourceGroup')}",
                f"- **Location:** {rt.get('location')}",
                f"- **Disable BGP Propagation:** {rt.get('disableBgpRoutePropagation', False)}",
            ])

            associated = [self._extract_name(s.get('id')) for s in rt.get('subnets', [])]
            if associated:
                lines.append(f"- **Associated Subnets:** {', '.join(associated)}")

            lines.append("")
            lines.append("#### Routes")
            lines.append("")
            lines.append("| Name | Address Prefix | Next Hop Type | Next Hop IP |")
            lines.append("|------|----------------|---------------|-------------|")

            for route in rt.get('routes_processed', []):
                lines.append(
                    f"| {route.get('name')} | {route.get('addressPrefix')} | "
                    f"{route.get('nextHopType')} | {route.get('nextHopIpAddress') or '-'} |"
                )

            lines.append("")

        return lines

    def _build_peerings_section(self, peerings: list) -> list:
        """Build VNet Peerings section."""
        lines = [
            "## VNet Peerings",
            "",
        ]

        if not peerings:
            lines.append("*No VNet Peerings found.*\n")
            return lines

        lines.append("| Source VNet | Peering Name | Remote VNet | State | VNet Access | Forwarded Traffic | Gateway Transit |")
        lines.append("|-------------|--------------|-------------|-------|-------------|-------------------|-----------------|")

        for peering in peerings:
            remote = self._extract_name(peering.get('remoteVnetId', ''))
            lines.append(
                f"| {peering.get('sourceVnet')} | {peering.get('name')} | {remote} | "
                f"{peering.get('peeringState')} | {peering.get('allowVirtualNetworkAccess')} | "
                f"{peering.get('allowForwardedTraffic')} | {peering.get('allowGatewayTransit')} |"
            )

        lines.append("")
        return lines

    def _build_private_endpoints_section(self, endpoints: list) -> list:
        """Build Private Endpoints section."""
        lines = [
            "## Private Endpoints",
            "",
        ]

        if not endpoints:
            lines.append("*No Private Endpoints found.*\n")
            return lines

        lines.append("| Name | Resource Group | Subnet | Target Resource | Group IDs | Status |")
        lines.append("|------|----------------|--------|-----------------|-----------|--------|")

        for ep in endpoints:
            subnet = self._extract_name(ep.get('subnet', {}).get('id', '')) if ep.get('subnet') else '-'

            for conn in ep.get('connections', []):
                target = self._extract_name(conn.get('privateLinkServiceId', ''))
                groups = ', '.join(conn.get('groupIds', []))
                status = conn.get('status', '-')

                lines.append(
                    f"| {ep.get('name')} | {ep.get('resourceGroup')} | {subnet} | "
                    f"{target} | {groups} | {status} |"
                )

        lines.append("")
        return lines

    def _build_load_balancers_section(self, lbs: list) -> list:
        """Build Load Balancers section."""
        lines = [
            "## Load Balancers",
            "",
        ]

        if not lbs:
            lines.append("*No Load Balancers found.*\n")
            return lines

        for lb in lbs:
            lines.extend([
                f"### {lb.get('name')}",
                "",
                f"- **Resource Group:** {lb.get('resourceGroup')}",
                f"- **Location:** {lb.get('location')}",
                f"- **SKU:** {lb.get('sku', {}).get('name', 'N/A')}",
                f"- **Frontend IPs:** {len(lb.get('frontendIpConfigurations', []))}",
                f"- **Backend Pools:** {len(lb.get('backendAddressPools', []))}",
                f"- **Rules:** {len(lb.get('loadBalancingRules', []))}",
                "",
            ])

        return lines

    def _build_app_gateways_section(self, gateways: list) -> list:
        """Build Application Gateways section."""
        lines = [
            "## Application Gateways",
            "",
        ]

        if not gateways:
            lines.append("*No Application Gateways found.*\n")
            return lines

        for gw in gateways:
            lines.extend([
                f"### {gw.get('name')}",
                "",
                f"- **Resource Group:** {gw.get('resourceGroup')}",
                f"- **Location:** {gw.get('location')}",
                f"- **SKU:** {gw.get('sku', {}).get('name', 'N/A')} ({gw.get('sku', {}).get('tier', 'N/A')})",
                f"- **Capacity:** {gw.get('sku', {}).get('capacity', 'N/A')}",
                f"- **Backend Pools:** {len(gw.get('backendAddressPools', []))}",
                f"- **HTTP Listeners:** {len(gw.get('httpListeners', []))}",
                "",
            ])

        return lines

    def _build_connectivity_section(self, connectivity: dict) -> list:
        """Build connectivity analysis section."""
        lines = [
            "## Connectivity Analysis",
            "",
        ]

        subnets = connectivity.get('subnets', {})
        if not subnets:
            lines.append("*No connectivity data available.*\n")
            return lines

        lines.append("### Subnet Connectivity")
        lines.append("")
        lines.append("| Subnet | VNet | Address Prefix | NSG | Internet Access |")
        lines.append("|--------|------|----------------|-----|-----------------|")

        for subnet_name, info in sorted(subnets.items()):
            lines.append(
                f"| {subnet_name} | {info.get('vnet', '-')} | {info.get('addressPrefix', '-')} | "
                f"{info.get('nsg') or 'None'} | {'Yes' if info.get('has_internet_access') else 'No'} |"
            )

        lines.append("")
        return lines

    def _build_issues_section(self, connectivity: dict) -> list:
        """Build security issues section."""
        lines = [
            "## Security Issues",
            "",
        ]

        issues = connectivity.get('potential_issues', [])
        if not issues:
            lines.append("✅ *No security issues detected.*\n")
            return lines

        lines.append(f"⚠️ **{len(issues)} potential issue(s) found:**\n")

        for issue in issues:
            severity_icon = {"High": "🔴", "Medium": "🟠", "Low": "🟡"}.get(issue.get('severity'), "⚪")
            lines.extend([
                f"### {severity_icon} {issue.get('severity')}: {issue.get('issue')}",
                "",
            ])

            if issue.get('rule_source'):
                lines.append(f"- **Source:** {issue.get('rule_source')}")
            if issue.get('recommendation'):
                lines.append(f"- **Recommendation:** {issue.get('recommendation')}")

            lines.append("")

        return lines

    def _extract_name(self, resource_id: str) -> str:
        """Extract resource name from Azure resource ID."""
        if not resource_id:
            return ""
        parts = resource_id.split("/")
        return parts[-1] if parts else ""


class JSONExporter:
    """Export network data as JSON."""

    def export(self, network_data: dict, graph_data: dict, output_path: str) -> str:
        """Export to JSON file."""
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)

        export_data = {
            "metadata": {
                "exported_at": datetime.now().isoformat(),
                "version": "1.0"
            },
            "network_data": network_data,
            "graph": graph_data
        }

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, default=str)

        return output_path
