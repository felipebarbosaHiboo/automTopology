

from flask import Flask, render_template, send_file
import os
import re
import xml.etree.ElementTree as ET
import networkx as nx
from pyvis.network import Network

app = Flask(__name__)

# Define the folder where interface files are stored
FOLDER_PATH = "./interface_files"

class NetworkTopology:
    def __init__(self, folder_path):
        self.folder_path = folder_path
        self.graph = nx.Graph()

    def parse_interface_descriptions(self, file_path):
        """Parses a network interface description file."""
        with open(file_path, "r") as file:
            lines = file.readlines()

        hostname_match = re.match(r"([^/]+)(?:-re\d+)?\.txt$", os.path.basename(file_path))
        if not hostname_match:
            return None

        hostname = hostname_match.group(1)
        interfaces = []

        for line in lines:
            match = re.match(r"(\S+)\s+(up|down)\s+(up|down)\s+(\S+)(?:\s+(\S+))?", line)
            if match:
                local_intf, admin_status, oper_status, remote_device, remote_intf = (
                    match.group(1), match.group(2), match.group(3), match.group(4), match.group(5) or None
                )

                if re.match(r"^(irb|lo0|ps)\.", local_intf) or not remote_intf:
                    continue

                is_down = admin_status == "down" or oper_status == "down"
                interfaces.append((hostname, local_intf, remote_device, remote_intf, is_down))

        return interfaces

    def build_topology(self):
        """Builds a network topology from parsed data."""
        for file in os.listdir(self.folder_path):
            if file.endswith(".txt"):
                file_path = os.path.join(self.folder_path, file)
                connections = self.parse_interface_descriptions(file_path)
                if connections:
                    for src, src_intf, dst, dst_intf, is_down in connections:
                        color = "red" if is_down else "green"
                        self.graph.add_edge(src, dst, label=f"{src_intf} ↔ {dst_intf}", color=color)

    def visualize_topology_interactive(self, output_file="static/network_topology.html"):
        """Generates an interactive topology visualization."""
        net = Network(height="800px", width="100%", notebook=False, bgcolor="#222222", font_color="white")

        for node in self.graph.nodes():
            net.add_node(node, label=node, title=node, color="skyblue")

        for src, dst, data in self.graph.edges(data=True):
            edge_color = data.get("color", "green")
            net.add_edge(src, dst, title=data["label"], color=edge_color)

        net.write_html(output_file)
        return output_file


@app.route("/")
def home():
    return render_template("index.html")

@app.route("/generate_topology")
def generate_topology():
    """Generates network topology and serves the visualization."""
    topology = NetworkTopology(FOLDER_PATH)
    topology.build_topology()
    html_file = topology.visualize_topology_interactive()
    return send_file(html_file)

if __name__ == "__main__":
    app.run(debug=True)