"""
Network Visualizer
Generates interactive HTML visualization using D3.js for Azure network topology.
"""

import json
from pathlib import Path


class NetworkVisualizer:
    """Generates interactive HTML network visualization."""

    def __init__(self):
        self.node_colors = {
            "vnet": "#4A90D9",
            "subnet": "#7CB342",
            "nsg": "#FF7043",
            "firewall": "#E91E63",
            "firewall_policy": "#9C27B0",
            "route_table": "#00BCD4",
            "private_endpoint": "#795548",
            "public_ip": "#FFC107",
            "vm": "#607D8B",
            "application_gateway": "#3F51B5",
            "load_balancer": "#009688",
            "vnet_gateway": "#673AB7",
            "bastion": "#FF5722",
            "private_dns_zone": "#8BC34A",
        }

        self.node_icons = {
            "vnet": "🌐",
            "subnet": "📦",
            "nsg": "🛡️",
            "firewall": "🔥",
            "firewall_policy": "📋",
            "route_table": "🛤️",
            "private_endpoint": "🔒",
            "public_ip": "🌍",
            "vm": "💻",
            "application_gateway": "⚡",
            "load_balancer": "⚖️",
            "vnet_gateway": "🚪",
            "bastion": "🏰",
            "private_dns_zone": "📝",
        }

    def generate_html(self, graph_data: dict, connectivity: dict, output_path: str) -> str:
        """Generate interactive HTML visualization."""
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)

        html_content = self._build_html(graph_data, connectivity)

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)

        return output_path

    def _build_html(self, graph_data: dict, connectivity: dict) -> str:
        """Build the HTML content."""
        return f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Azure Network Map</title>
    <script src="https://d3js.org/d3.v7.min.js"></script>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            color: #fff;
            min-height: 100vh;
        }}

        .header {{
            background: rgba(0,0,0,0.3);
            padding: 15px 30px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 1px solid rgba(255,255,255,0.1);
        }}

        .header h1 {{
            font-size: 24px;
            font-weight: 600;
        }}

        .header-controls {{
            display: flex;
            gap: 15px;
            align-items: center;
        }}

        .header-controls button {{
            background: rgba(255,255,255,0.1);
            border: 1px solid rgba(255,255,255,0.2);
            color: #fff;
            padding: 8px 16px;
            border-radius: 6px;
            cursor: pointer;
            transition: all 0.2s;
        }}

        .header-controls button:hover {{
            background: rgba(255,255,255,0.2);
        }}

        .main-container {{
            display: flex;
            height: calc(100vh - 60px);
        }}

        .sidebar {{
            width: 350px;
            background: rgba(0,0,0,0.3);
            border-right: 1px solid rgba(255,255,255,0.1);
            overflow-y: auto;
            padding: 20px;
        }}

        .sidebar h2 {{
            font-size: 16px;
            margin-bottom: 15px;
            color: #aaa;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}

        .filter-section {{
            margin-bottom: 25px;
        }}

        .filter-item {{
            display: flex;
            align-items: center;
            gap: 10px;
            padding: 8px 12px;
            margin-bottom: 5px;
            background: rgba(255,255,255,0.05);
            border-radius: 6px;
            cursor: pointer;
            transition: all 0.2s;
        }}

        .filter-item:hover {{
            background: rgba(255,255,255,0.1);
        }}

        .filter-item.active {{
            background: rgba(255,255,255,0.15);
        }}

        .filter-item .color-dot {{
            width: 12px;
            height: 12px;
            border-radius: 50%;
        }}

        .filter-item .count {{
            margin-left: auto;
            background: rgba(255,255,255,0.1);
            padding: 2px 8px;
            border-radius: 10px;
            font-size: 12px;
        }}

        .graph-container {{
            flex: 1;
            position: relative;
            overflow: hidden;
        }}

        #network-graph {{
            width: 100%;
            height: 100%;
        }}

        .node {{
            cursor: pointer;
        }}

        .node circle {{
            stroke: #fff;
            stroke-width: 2px;
            transition: all 0.2s;
        }}

        .node:hover circle {{
            stroke-width: 4px;
            filter: brightness(1.2);
        }}

        .node text {{
            font-size: 11px;
            fill: #fff;
            text-anchor: middle;
            pointer-events: none;
            text-shadow: 0 1px 3px rgba(0,0,0,0.8);
        }}

        .link {{
            stroke-opacity: 0.6;
            transition: all 0.2s;
        }}

        .link.contains {{
            stroke: #4CAF50;
            stroke-dasharray: none;
        }}

        .link.peering {{
            stroke: #2196F3;
            stroke-width: 3px;
        }}

        .link.secured_by {{
            stroke: #FF9800;
            stroke-dasharray: 5,5;
        }}

        .link.routes_via {{
            stroke: #00BCD4;
            stroke-dasharray: 10,5;
        }}

        .link.dns_linked {{
            stroke: #8BC34A;
            stroke-dasharray: 3,3;
        }}

        .detail-panel {{
            position: absolute;
            right: 20px;
            top: 20px;
            width: 380px;
            background: rgba(0,0,0,0.9);
            border: 1px solid rgba(255,255,255,0.2);
            border-radius: 12px;
            padding: 20px;
            display: none;
            max-height: calc(100% - 40px);
            overflow-y: auto;
        }}

        .detail-panel.visible {{
            display: block;
        }}

        .detail-panel .close-btn {{
            position: absolute;
            right: 15px;
            top: 15px;
            background: none;
            border: none;
            color: #fff;
            font-size: 20px;
            cursor: pointer;
            opacity: 0.7;
        }}

        .detail-panel .close-btn:hover {{
            opacity: 1;
        }}

        .detail-panel h3 {{
            font-size: 18px;
            margin-bottom: 5px;
            padding-right: 30px;
        }}

        .detail-panel .resource-type {{
            color: #888;
            font-size: 12px;
            text-transform: uppercase;
            margin-bottom: 20px;
        }}

        .detail-section {{
            margin-bottom: 20px;
        }}

        .detail-section h4 {{
            font-size: 12px;
            color: #888;
            text-transform: uppercase;
            margin-bottom: 10px;
            letter-spacing: 1px;
        }}

        .detail-item {{
            display: flex;
            justify-content: space-between;
            padding: 8px 0;
            border-bottom: 1px solid rgba(255,255,255,0.1);
            font-size: 13px;
        }}

        .detail-item .label {{
            color: #888;
        }}

        .detail-item .value {{
            color: #fff;
            text-align: right;
            max-width: 200px;
            word-break: break-all;
        }}

        .rules-table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 11px;
            margin-top: 10px;
        }}

        .rules-table th {{
            text-align: left;
            padding: 8px;
            background: rgba(255,255,255,0.1);
            color: #888;
            font-weight: 500;
        }}

        .rules-table td {{
            padding: 8px;
            border-bottom: 1px solid rgba(255,255,255,0.05);
        }}

        .rules-table tr:hover {{
            background: rgba(255,255,255,0.05);
        }}

        .allow {{
            color: #4CAF50;
        }}

        .deny {{
            color: #f44336;
        }}

        .issues-panel {{
            margin-top: 20px;
            padding: 15px;
            background: rgba(255,0,0,0.1);
            border: 1px solid rgba(255,0,0,0.3);
            border-radius: 8px;
        }}

        .issues-panel h4 {{
            color: #f44336;
            margin-bottom: 10px;
        }}

        .issue-item {{
            padding: 10px;
            margin-bottom: 8px;
            background: rgba(0,0,0,0.3);
            border-radius: 6px;
            font-size: 12px;
        }}

        .issue-item .severity {{
            display: inline-block;
            padding: 2px 8px;
            border-radius: 4px;
            font-size: 10px;
            font-weight: 600;
            margin-bottom: 5px;
        }}

        .issue-item .severity.high {{
            background: #f44336;
        }}

        .issue-item .severity.medium {{
            background: #FF9800;
        }}

        .issue-item .severity.low {{
            background: #2196F3;
        }}

        .search-box {{
            width: 100%;
            padding: 10px 15px;
            background: rgba(255,255,255,0.1);
            border: 1px solid rgba(255,255,255,0.2);
            border-radius: 8px;
            color: #fff;
            font-size: 14px;
            margin-bottom: 20px;
        }}

        .search-box::placeholder {{
            color: rgba(255,255,255,0.5);
        }}

        .legend {{
            position: absolute;
            bottom: 20px;
            left: 20px;
            background: rgba(0,0,0,0.8);
            padding: 15px;
            border-radius: 8px;
            font-size: 12px;
        }}

        .legend-item {{
            display: flex;
            align-items: center;
            gap: 8px;
            margin-bottom: 5px;
        }}

        .legend-line {{
            width: 30px;
            height: 3px;
        }}

        .tabs {{
            display: flex;
            gap: 5px;
            margin-bottom: 20px;
        }}

        .tab {{
            flex: 1;
            padding: 10px;
            background: rgba(255,255,255,0.05);
            border: none;
            color: #888;
            cursor: pointer;
            border-radius: 6px;
            transition: all 0.2s;
        }}

        .tab.active {{
            background: rgba(255,255,255,0.15);
            color: #fff;
        }}

        .tab-content {{
            display: none;
        }}

        .tab-content.active {{
            display: block;
        }}

        .zoom-controls {{
            position: absolute;
            bottom: 20px;
            right: 20px;
            display: flex;
            flex-direction: column;
            gap: 5px;
        }}

        .zoom-controls button {{
            width: 40px;
            height: 40px;
            background: rgba(0,0,0,0.8);
            border: 1px solid rgba(255,255,255,0.2);
            color: #fff;
            font-size: 20px;
            cursor: pointer;
            border-radius: 8px;
        }}

        .zoom-controls button:hover {{
            background: rgba(255,255,255,0.1);
        }}

        .tooltip {{
            position: absolute;
            background: rgba(0,0,0,0.9);
            padding: 10px 15px;
            border-radius: 6px;
            font-size: 12px;
            pointer-events: none;
            z-index: 1000;
            max-width: 300px;
        }}

        .tooltip .title {{
            font-weight: 600;
            margin-bottom: 5px;
        }}

        .tooltip .type {{
            color: #888;
            font-size: 11px;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🌐 Azure Network Map</h1>
        <div class="header-controls">
            <button onclick="resetView()">Reset View</button>
            <button onclick="exportSVG()">Export SVG</button>
            <button onclick="toggleFullscreen()">Fullscreen</button>
        </div>
    </div>

    <div class="main-container">
        <div class="sidebar">
            <input type="text" class="search-box" placeholder="Search resources..." id="searchBox">

            <div class="tabs">
                <button class="tab active" onclick="showTab('filters')">Filters</button>
                <button class="tab" onclick="showTab('rules')">Rules</button>
                <button class="tab" onclick="showTab('issues')">Issues</button>
            </div>

            <div id="filters-tab" class="tab-content active">
                <div class="filter-section">
                    <h2>Resource Types</h2>
                    <div id="type-filters"></div>
                </div>
            </div>

            <div id="rules-tab" class="tab-content">
                <div class="filter-section">
                    <h2>Network Rules</h2>
                    <div id="rules-list"></div>
                </div>
            </div>

            <div id="issues-tab" class="tab-content">
                <div class="filter-section">
                    <h2>Potential Issues</h2>
                    <div id="issues-list"></div>
                </div>
            </div>
        </div>

        <div class="graph-container">
            <svg id="network-graph"></svg>

            <div class="detail-panel" id="detailPanel">
                <button class="close-btn" onclick="closeDetailPanel()">&times;</button>
                <h3 id="detailName"></h3>
                <div class="resource-type" id="detailType"></div>
                <div id="detailContent"></div>
            </div>

            <div class="legend">
                <div class="legend-item">
                    <div class="legend-line" style="background: #4CAF50;"></div>
                    <span>Contains</span>
                </div>
                <div class="legend-item">
                    <div class="legend-line" style="background: #2196F3;"></div>
                    <span>VNet Peering</span>
                </div>
                <div class="legend-item">
                    <div class="legend-line" style="background: #FF9800; border-style: dashed;"></div>
                    <span>Secured By</span>
                </div>
                <div class="legend-item">
                    <div class="legend-line" style="background: #00BCD4; border-style: dashed;"></div>
                    <span>Routes Via</span>
                </div>
            </div>

            <div class="zoom-controls">
                <button onclick="zoomIn()">+</button>
                <button onclick="zoomOut()">−</button>
            </div>
        </div>
    </div>

    <div class="tooltip" id="tooltip" style="display: none;"></div>

    <script>
        // Data
        const graphData = {json.dumps(graph_data, indent=2)};
        const connectivity = {json.dumps(connectivity, indent=2)};
        const nodeColors = {json.dumps(self.node_colors)};
        const nodeIcons = {json.dumps(self.node_icons)};

        // SVG setup
        const svg = d3.select("#network-graph");
        const width = svg.node().parentElement.clientWidth;
        const height = svg.node().parentElement.clientHeight;

        svg.attr("width", width).attr("height", height);

        // Create container for zoom
        const container = svg.append("g");

        // Zoom behavior
        const zoom = d3.zoom()
            .scaleExtent([0.1, 4])
            .on("zoom", (event) => {{
                container.attr("transform", event.transform);
            }});

        svg.call(zoom);

        // Arrow markers for directed edges
        svg.append("defs").selectAll("marker")
            .data(["arrow"])
            .enter().append("marker")
            .attr("id", d => d)
            .attr("viewBox", "0 -5 10 10")
            .attr("refX", 25)
            .attr("refY", 0)
            .attr("markerWidth", 6)
            .attr("markerHeight", 6)
            .attr("orient", "auto")
            .append("path")
            .attr("fill", "#999")
            .attr("d", "M0,-5L10,0L0,5");

        // Process data
        let nodes = graphData.nodes.map(n => ({{...n}}));
        let links = graphData.edges.map(e => ({{
            source: e.source,
            target: e.target,
            type: e.type,
            properties: e.properties
        }}));

        // Filter out links with missing nodes
        const nodeIds = new Set(nodes.map(n => n.id));
        links = links.filter(l => nodeIds.has(l.source) && nodeIds.has(l.target));

        // Count by type
        const typeCounts = {{}};
        nodes.forEach(n => {{
            typeCounts[n.type] = (typeCounts[n.type] || 0) + 1;
        }});

        // Active filters
        let activeFilters = new Set(Object.keys(typeCounts));

        // Create type filters
        const filterContainer = document.getElementById('type-filters');
        Object.entries(typeCounts).sort((a, b) => b[1] - a[1]).forEach(([type, count]) => {{
            const div = document.createElement('div');
            div.className = 'filter-item active';
            div.dataset.type = type;
            div.innerHTML = `
                <div class="color-dot" style="background: ${{nodeColors[type] || '#666'}}"></div>
                <span>${{nodeIcons[type] || ''}} ${{type.replace(/_/g, ' ')}}</span>
                <span class="count">${{count}}</span>
            `;
            div.onclick = () => toggleFilter(type, div);
            filterContainer.appendChild(div);
        }});

        // Create rules list
        const rulesContainer = document.getElementById('rules-list');
        if (graphData.rules && graphData.rules.length > 0) {{
            const table = document.createElement('table');
            table.className = 'rules-table';
            table.innerHTML = `
                <thead>
                    <tr>
                        <th>Source</th>
                        <th>Dest</th>
                        <th>Port</th>
                        <th>Action</th>
                    </tr>
                </thead>
                <tbody>
                    ${{graphData.rules.slice(0, 50).map(r => `
                        <tr>
                            <td title="${{r.source}}">${{truncate(r.source, 15)}}</td>
                            <td title="${{r.destination}}">${{truncate(r.destination, 15)}}</td>
                            <td>${{truncate(r.port, 10)}}</td>
                            <td class="${{r.action.toLowerCase()}}">${{r.action}}</td>
                        </tr>
                    `).join('')}}
                </tbody>
            `;
            rulesContainer.appendChild(table);
        }} else {{
            rulesContainer.innerHTML = '<p style="color: #888;">No rules found</p>';
        }}

        // Create issues list
        const issuesContainer = document.getElementById('issues-list');
        if (connectivity.potential_issues && connectivity.potential_issues.length > 0) {{
            connectivity.potential_issues.forEach(issue => {{
                const div = document.createElement('div');
                div.className = 'issue-item';
                div.innerHTML = `
                    <div class="severity ${{issue.severity.toLowerCase()}}">${{issue.severity}}</div>
                    <div>${{issue.issue}}</div>
                    <div style="color: #888; margin-top: 5px; font-size: 11px;">${{issue.recommendation || ''}}</div>
                `;
                issuesContainer.appendChild(div);
            }});
        }} else {{
            issuesContainer.innerHTML = '<p style="color: #4CAF50;">No issues found</p>';
        }}

        // Force simulation
        const simulation = d3.forceSimulation(nodes)
            .force("link", d3.forceLink(links).id(d => d.id).distance(120))
            .force("charge", d3.forceManyBody().strength(-400))
            .force("center", d3.forceCenter(width / 2, height / 2))
            .force("collision", d3.forceCollide().radius(50));

        // Draw links
        const link = container.append("g")
            .selectAll("line")
            .data(links)
            .enter().append("line")
            .attr("class", d => `link ${{d.type}}`)
            .attr("stroke-width", d => d.type === 'peering' ? 3 : 2);

        // Draw nodes
        const node = container.append("g")
            .selectAll("g")
            .data(nodes)
            .enter().append("g")
            .attr("class", "node")
            .call(d3.drag()
                .on("start", dragstarted)
                .on("drag", dragged)
                .on("end", dragended))
            .on("click", showNodeDetails)
            .on("mouseover", showTooltip)
            .on("mouseout", hideTooltip);

        node.append("circle")
            .attr("r", d => getNodeSize(d.type))
            .attr("fill", d => nodeColors[d.type] || "#666");

        node.append("text")
            .attr("dy", d => getNodeSize(d.type) + 15)
            .text(d => truncate(d.name, 20));

        node.append("text")
            .attr("dy", 5)
            .attr("font-size", "14px")
            .text(d => nodeIcons[d.type] || "");

        // Simulation tick
        simulation.on("tick", () => {{
            link
                .attr("x1", d => d.source.x)
                .attr("y1", d => d.source.y)
                .attr("x2", d => d.target.x)
                .attr("y2", d => d.target.y);

            node.attr("transform", d => `translate(${{d.x}},${{d.y}})`);
        }});

        // Functions
        function getNodeSize(type) {{
            const sizes = {{
                'vnet': 35,
                'subnet': 25,
                'firewall': 30,
                'vm': 20,
                'nsg': 22,
                'private_endpoint': 18,
                'public_ip': 18,
            }};
            return sizes[type] || 22;
        }}

        function truncate(str, len) {{
            if (!str) return '';
            return str.length > len ? str.substring(0, len) + '...' : str;
        }}

        function toggleFilter(type, element) {{
            if (activeFilters.has(type)) {{
                activeFilters.delete(type);
                element.classList.remove('active');
            }} else {{
                activeFilters.add(type);
                element.classList.add('active');
            }}
            updateVisibility();
        }}

        function updateVisibility() {{
            node.style("display", d => activeFilters.has(d.type) ? null : "none");
            link.style("display", d => {{
                const sourceVisible = activeFilters.has(d.source.type);
                const targetVisible = activeFilters.has(d.target.type);
                return sourceVisible && targetVisible ? null : "none";
            }});
        }}

        function showNodeDetails(event, d) {{
            const panel = document.getElementById('detailPanel');
            document.getElementById('detailName').textContent = d.name;
            document.getElementById('detailType').textContent = d.type.replace(/_/g, ' ').toUpperCase();

            let content = '<div class="detail-section"><h4>Properties</h4>';

            if (d.resourceGroup) {{
                content += `<div class="detail-item"><span class="label">Resource Group</span><span class="value">${{d.resourceGroup}}</span></div>`;
            }}

            if (d.properties) {{
                Object.entries(d.properties).forEach(([key, value]) => {{
                    if (value !== null && value !== undefined && value !== '') {{
                        let displayValue = value;
                        if (Array.isArray(value)) {{
                            displayValue = value.length > 0 ? value.join(', ') : 'None';
                        }} else if (typeof value === 'object') {{
                            displayValue = JSON.stringify(value);
                        }}
                        content += `<div class="detail-item"><span class="label">${{key}}</span><span class="value">${{displayValue}}</span></div>`;
                    }}
                }});
            }}

            content += '</div>';

            // Show connected resources
            const connectedLinks = links.filter(l =>
                (l.source.id === d.id || l.source === d.id) ||
                (l.target.id === d.id || l.target === d.id)
            );

            if (connectedLinks.length > 0) {{
                content += '<div class="detail-section"><h4>Connections</h4>';
                connectedLinks.forEach(l => {{
                    const other = (l.source.id === d.id || l.source === d.id) ? l.target : l.source;
                    const otherName = typeof other === 'object' ? other.name : nodes.find(n => n.id === other)?.name;
                    content += `<div class="detail-item"><span class="label">${{l.type}}</span><span class="value">${{otherName}}</span></div>`;
                }});
                content += '</div>';
            }}

            document.getElementById('detailContent').innerHTML = content;
            panel.classList.add('visible');
        }}

        function closeDetailPanel() {{
            document.getElementById('detailPanel').classList.remove('visible');
        }}

        function showTooltip(event, d) {{
            const tooltip = document.getElementById('tooltip');
            tooltip.innerHTML = `
                <div class="title">${{nodeIcons[d.type] || ''}} ${{d.name}}</div>
                <div class="type">${{d.type.replace(/_/g, ' ')}}</div>
            `;
            tooltip.style.display = 'block';
            tooltip.style.left = (event.pageX + 15) + 'px';
            tooltip.style.top = (event.pageY + 15) + 'px';
        }}

        function hideTooltip() {{
            document.getElementById('tooltip').style.display = 'none';
        }}

        function showTab(tabName) {{
            document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
            document.querySelectorAll('.tab-content').forEach(t => t.classList.remove('active'));
            document.querySelector(`.tab-content#${{tabName}}-tab`).classList.add('active');
            event.target.classList.add('active');
        }}

        function dragstarted(event, d) {{
            if (!event.active) simulation.alphaTarget(0.3).restart();
            d.fx = d.x;
            d.fy = d.y;
        }}

        function dragged(event, d) {{
            d.fx = event.x;
            d.fy = event.y;
        }}

        function dragended(event, d) {{
            if (!event.active) simulation.alphaTarget(0);
            d.fx = null;
            d.fy = null;
        }}

        function resetView() {{
            svg.transition().duration(750).call(
                zoom.transform,
                d3.zoomIdentity.translate(width / 2, height / 2).scale(1).translate(-width / 2, -height / 2)
            );
        }}

        function zoomIn() {{
            svg.transition().call(zoom.scaleBy, 1.5);
        }}

        function zoomOut() {{
            svg.transition().call(zoom.scaleBy, 0.67);
        }}

        function exportSVG() {{
            const svgData = svg.node().outerHTML;
            const blob = new Blob([svgData], {{type: 'image/svg+xml'}});
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'azure-network-map.svg';
            a.click();
            URL.revokeObjectURL(url);
        }}

        function toggleFullscreen() {{
            if (!document.fullscreenElement) {{
                document.documentElement.requestFullscreen();
            }} else {{
                document.exitFullscreen();
            }}
        }}

        // Search functionality
        document.getElementById('searchBox').addEventListener('input', (e) => {{
            const query = e.target.value.toLowerCase();
            node.style("opacity", d => {{
                if (!query) return 1;
                return d.name.toLowerCase().includes(query) ? 1 : 0.2;
            }});
            link.style("opacity", query ? 0.1 : 0.6);
        }});

        // Initial center
        setTimeout(() => {{
            svg.call(zoom.transform, d3.zoomIdentity.translate(0, 0).scale(0.8));
        }}, 1000);
    </script>
</body>
</html>'''
