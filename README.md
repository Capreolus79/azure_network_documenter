# Azure Network Documenter

A comprehensive tool to document and visualize Azure network infrastructure. Collects information about VNets, Subnets, Firewall Policies, NSGs, Route Tables, Private Endpoints, and generates interactive network maps.

## Features

- **Comprehensive Data Collection**: Collects VNets, Subnets, NSGs, Firewalls, Firewall Policies, Route Tables, Private Endpoints, Peerings, Load Balancers, Application Gateways, VNet Gateways, Bastion Hosts, and more
- **Interactive Visualization**: Generates an interactive D3.js-based HTML network map with:
  - Zoomable and draggable graph
  - Resource type filtering
  - Search functionality
  - Detailed resource information panels
  - Visual connectivity lines
- **Connectivity Analysis**: Analyzes what resources can connect to what based on NSG rules, firewall policies, and peerings
- **Security Issue Detection**: Identifies potential security issues like:
  - Overly permissive rules
  - Risky ports exposed to internet
  - Subnets without NSGs
- **Multiple Export Formats**:
  - Interactive HTML visualization
  - Detailed Markdown documentation
  - JSON data export

## Prerequisites

- Python 3.10+
- Azure CLI installed and logged in (`az login`)
- Appropriate Azure RBAC permissions to read network resources

## Installation

```bash
cd azure_network_documenter
# No pip install required - uses only Python standard library
```

## Usage

### Basic Usage (Live Azure Data)

```bash
# Document all network resources in current subscription
python azure_network_documenter.py

# Document specific subscription
python azure_network_documenter.py --subscription "your-subscription-id"

# Document specific resource groups
python azure_network_documenter.py --resource-groups rg-network-prod rg-network-dev

# Custom output directory
python azure_network_documenter.py --output ./my-network-docs
```

### Using Sample Data (No Azure Access Required)

```bash
# Generate sample data
python sample_data.py

# Run documenter with sample data
python azure_network_documenter.py --from-json sample_network_data.json
```

### Command Line Options

| Option | Description |
|--------|-------------|
| `--subscription`, `-s` | Azure subscription ID (uses default if not specified) |
| `--resource-groups`, `-g` | Resource groups to document (documents all if not specified) |
| `--output`, `-o` | Output directory (default: `output`) |
| `--no-firewall-rules` | Skip firewall rule collection |
| `--no-nsg-rules` | Skip NSG rule collection |
| `--from-json` | Load data from existing JSON file instead of Azure |

## Output Files

The tool generates three output files in the specified output directory:

1. **`network_map.html`** - Interactive network visualization
   - Zoomable/pannable network graph
   - Click nodes for detailed information
   - Filter by resource type
   - Search resources
   - View connectivity rules
   - Export as SVG

2. **`network_documentation.md`** - Comprehensive Markdown documentation
   - Resource inventory summary
   - Detailed VNet and subnet information
   - NSG rules tables
   - Firewall policies and rules
   - Route tables
   - Peering configurations
   - Connectivity analysis
   - Security issues

3. **`network_data.json`** - Raw JSON data
   - Complete collected data
   - Graph structure (nodes and edges)
   - Can be used for custom processing

## Architecture

```
azure_network_documenter/
├── azure_network_documenter.py  # Main application
├── collectors.py                 # Azure data collection modules
├── graph_builder.py             # Network graph and analysis
├── visualizer.py                # HTML/D3.js visualization generator
├── exporters.py                 # Markdown and JSON exporters
├── sample_data.py               # Sample data generator
└── requirements.txt             # Dependencies (standard library only)
```

## Visualization Features

The interactive HTML visualization includes:

- **Node Types**: VNets, Subnets, NSGs, Firewalls, VMs, Private Endpoints, Load Balancers, etc.
- **Edge Types**:
  - Contains (solid green) - Parent/child relationships
  - Peering (solid blue) - VNet peerings
  - Secured By (dashed orange) - NSG associations
  - Routes Via (dashed cyan) - Route table associations
  - DNS Linked (dashed green) - Private DNS zone links

- **Interactions**:
  - Drag nodes to reposition
  - Click nodes for details
  - Scroll to zoom
  - Search box to filter
  - Type filters in sidebar

## Security Analysis

The tool automatically detects common security issues:

| Severity | Issue Type |
|----------|------------|
| High | Overly permissive rules (any-to-any) |
| High | Risky ports exposed to internet (22, 3389, 445, 1433, etc.) |
| Medium | All ports open from any source |
| Medium | Subnets without NSG attached |

## Example Output

### Network Map
![Network Map Example](docs/network_map_example.png)

### Markdown Documentation
```markdown
## Summary
| Resource Type | Count |
|--------------|-------|
| Virtual Networks | 3 |
| Subnets | 9 |
| Network Security Groups | 5 |
| Azure Firewalls | 1 |
...
```

## Extending

### Adding New Resource Types

1. Add collection method in `collectors.py`
2. Add processing method in `graph_builder.py`
3. Update visualization colors/icons in `visualizer.py`
4. Add export section in `exporters.py`

### Custom Analysis

The `graph_builder.py` module exposes:
- `NetworkNode` - Node dataclass
- `NetworkEdge` - Edge dataclass
- `AccessRule` - Rule dataclass
- `get_graph_data()` - Get nodes/edges for custom processing
- `get_connectivity_matrix()` - Get analyzed connectivity

## Troubleshooting

### "Not logged into Azure CLI"
```bash
az login
az account set --subscription "your-subscription-id"
```

### "Insufficient permissions"
Ensure your account has at least `Reader` role on the target subscription/resource groups.

### Large subscriptions timeout
Use `--resource-groups` to limit scope or increase timeout in `collectors.py`.

## License

MIT License
