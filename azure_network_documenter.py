"""
Azure Network Documenter
A comprehensive tool to document and visualize Azure network infrastructure.
Collects information about VNets, Subnets, Firewall Policies, NSGs, Route Tables,
Private Endpoints, and generates interactive network maps.
"""

import json
import subprocess
import sys
from dataclasses import dataclass, field
from typing import Optional
from pathlib import Path
from datetime import datetime

from collectors import AzureCollector
from graph_builder import NetworkGraphBuilder
from visualizer import NetworkVisualizer
from exporters import MarkdownExporter, JSONExporter


@dataclass
class DocumenterConfig:
    """Configuration for the Azure Network Documenter."""
    subscription_id: Optional[str] = None
    resource_groups: list[str] = field(default_factory=list)
    output_dir: str = "output"
    include_firewall_rules: bool = True
    include_nsg_rules: bool = True
    include_route_tables: bool = True
    include_private_endpoints: bool = True
    include_peerings: bool = True
    include_service_endpoints: bool = True


class AzureNetworkDocumenter:
    """Main class for documenting Azure network infrastructure."""

    def __init__(self, config: DocumenterConfig):
        self.config = config
        self.collector = AzureCollector(config)
        self.graph_builder = NetworkGraphBuilder()
        self.visualizer = NetworkVisualizer()
        self.network_data = {}

    def check_azure_cli(self) -> bool:
        """Check if Azure CLI is installed and logged in."""
        try:
            result = subprocess.run(
                ["az", "account", "show"],
                capture_output=True,
                text=True,
                shell=True
            )
            if result.returncode != 0:
                print("Error: Not logged into Azure CLI. Run 'az login' first.")
                return False
            return True
        except FileNotFoundError:
            print("Error: Azure CLI not found. Please install it first.")
            return False

    def collect_data(self) -> dict:
        """Collect all network-related data from Azure."""
        print("\n" + "=" * 60)
        print("AZURE NETWORK DOCUMENTER")
        print("=" * 60)

        if not self.check_azure_cli():
            return {}

        print("\nCollecting Azure network data...")

        # Collect all network resources
        self.network_data = {
            "metadata": {
                "collected_at": datetime.now().isoformat(),
                "subscription_id": self.config.subscription_id,
                "resource_groups": self.config.resource_groups
            },
            "vnets": self.collector.collect_vnets(),
            "subnets": self.collector.collect_subnets(),
            "nsgs": self.collector.collect_nsgs() if self.config.include_nsg_rules else [],
            "firewalls": self.collector.collect_firewalls(),
            "firewall_policies": self.collector.collect_firewall_policies() if self.config.include_firewall_rules else [],
            "route_tables": self.collector.collect_route_tables() if self.config.include_route_tables else [],
            "private_endpoints": self.collector.collect_private_endpoints() if self.config.include_private_endpoints else [],
            "peerings": self.collector.collect_peerings() if self.config.include_peerings else [],
            "public_ips": self.collector.collect_public_ips(),
            "private_dns_zones": self.collector.collect_private_dns_zones(),
            "application_gateways": self.collector.collect_app_gateways(),
            "load_balancers": self.collector.collect_load_balancers(),
            "virtual_network_gateways": self.collector.collect_vnet_gateways(),
            "bastion_hosts": self.collector.collect_bastion_hosts(),
            "nics": self.collector.collect_network_interfaces(),
        }

        return self.network_data

    def build_graph(self) -> dict:
        """Build a network graph from collected data."""
        print("\nBuilding network graph...")
        return self.graph_builder.build(self.network_data)

    def analyze_connectivity(self) -> dict:
        """Analyze what can connect to what based on rules."""
        print("\nAnalyzing connectivity...")
        return self.graph_builder.analyze_connectivity()

    def generate_visualization(self, output_path: str = None) -> str:
        """Generate interactive HTML visualization."""
        print("\nGenerating visualization...")
        if output_path is None:
            output_path = Path(self.config.output_dir) / "network_map.html"

        graph = self.graph_builder.get_graph_data()
        connectivity = self.graph_builder.get_connectivity_matrix()

        return self.visualizer.generate_html(
            graph,
            connectivity,
            str(output_path)
        )

    def export_markdown(self, output_path: str = None) -> str:
        """Export documentation as Markdown."""
        if output_path is None:
            output_path = Path(self.config.output_dir) / "network_documentation.md"

        exporter = MarkdownExporter()
        return exporter.export(
            self.network_data,
            self.graph_builder.get_connectivity_matrix(),
            str(output_path)
        )

    def export_json(self, output_path: str = None) -> str:
        """Export all data as JSON."""
        if output_path is None:
            output_path = Path(self.config.output_dir) / "network_data.json"

        exporter = JSONExporter()
        return exporter.export(
            self.network_data,
            self.graph_builder.get_graph_data(),
            str(output_path)
        )

    def run(self) -> dict:
        """Run the full documentation process."""
        # Create output directory
        Path(self.config.output_dir).mkdir(parents=True, exist_ok=True)

        # Collect data
        data = self.collect_data()
        if not data:
            return {}

        # Build graph and analyze
        self.build_graph()
        connectivity = self.analyze_connectivity()

        # Generate outputs
        html_path = self.generate_visualization()
        md_path = self.export_markdown()
        json_path = self.export_json()

        print("\n" + "=" * 60)
        print("DOCUMENTATION COMPLETE")
        print("=" * 60)
        print(f"\nOutputs generated:")
        print(f"  - Interactive Map: {html_path}")
        print(f"  - Markdown Docs:   {md_path}")
        print(f"  - JSON Data:       {json_path}")

        return {
            "data": data,
            "connectivity": connectivity,
            "outputs": {
                "html": html_path,
                "markdown": md_path,
                "json": json_path
            }
        }


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Azure Network Documenter - Visualize your Azure network infrastructure"
    )
    parser.add_argument(
        "--subscription", "-s",
        help="Azure subscription ID (uses default if not specified)"
    )
    parser.add_argument(
        "--resource-groups", "-g",
        nargs="+",
        help="Resource groups to document (documents all if not specified)"
    )
    parser.add_argument(
        "--output", "-o",
        default="output",
        help="Output directory (default: output)"
    )
    parser.add_argument(
        "--no-firewall-rules",
        action="store_true",
        help="Skip firewall rule collection"
    )
    parser.add_argument(
        "--no-nsg-rules",
        action="store_true",
        help="Skip NSG rule collection"
    )
    parser.add_argument(
        "--from-json",
        help="Load data from existing JSON file instead of Azure"
    )

    args = parser.parse_args()

    config = DocumenterConfig(
        subscription_id=args.subscription,
        resource_groups=args.resource_groups or [],
        output_dir=args.output,
        include_firewall_rules=not args.no_firewall_rules,
        include_nsg_rules=not args.no_nsg_rules
    )

    documenter = AzureNetworkDocumenter(config)

    if args.from_json:
        # Load from existing JSON
        print(f"Loading data from {args.from_json}...")
        with open(args.from_json, 'r') as f:
            documenter.network_data = json.load(f)
        documenter.build_graph()
        documenter.analyze_connectivity()
        documenter.generate_visualization()
        documenter.export_markdown()
    else:
        # Run full collection
        documenter.run()


if __name__ == "__main__":
    main()
