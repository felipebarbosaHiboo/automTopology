import os
import re
import xml.etree.ElementTree as ET
import networkx as nx
from pyvis.network import Network


class CustomerTopology:
    def __init__(self, folder_path):
        self.folder_path = folder_path
        self.graph = nx.Graph()

    def parse_customer_interfaces(self, file_path):
        with open(file_path, "r") as file:
            lines = file.readlines()

        print(f"Parsing (customer only): {file_path}")

        match = re.match(r"([^/]+)(?:-re\d+)?\.txt$", os.path.basename(file_path))
        if not match:
            print(f"❌ Hostname extraction failed for: {file_path}")
            return None

        hostname = match.group(1)
        print(f"✅ Extracted Hostname: {hostname}")

        customer_interfaces = []

        for line in lines:
            match = re.match(r"(\S+)\s+(up|down)\s+(up|down)\s+(\S+)(?:\s+(\S+))?", line)
            if match:
                local_intf = match.group(1)
                admin_status = match.group(2)
                oper_status = match.group(3)
                remote_device = match.group(4)
                remote_intf = match.group(5) if match.group(5) else None

                # ✅ **Filter only "customer" interfaces**
                if "customer" not in remote_device.lower():
                    continue  # Ignore non-customer interfaces

                is_down = admin_status == "down" or oper_status == "down"

                print(f"🔗 Customer Connection: {hostname} {local_intf} → {remote_device} {remote_intf} | {'🔴 DOWN' if is_down else '🟢 UP'}")

                customer_interfaces.append((hostname, local_intf, remote_device, remote_intf, is_down))

        return customer_interfaces

    def build_topology(self):
        print(f"Checking folder: {self.folder_path}")

        for file in os.listdir(self.folder_path):
            if file.endswith(".txt"):
                file_path = os.path.join(self.folder_path, file)
                print(f"Reading file: {file_path}")

                connections = self.parse_customer_interfaces(file_path)
                if connections:
                    for src, src_intf, dst, dst_intf, is_down in connections:
                        color = "red" if is_down else "green"
                        print(f"Adding Edge: {src} ↔ {dst} ({src_intf} ↔ {dst_intf}) [{color}]")
                        self.graph.add_edge(src, dst, label=f"{src_intf} ↔ {dst_intf}", color=color)

        print("Final Nodes:", self.graph.nodes())
        print("Final Edges:", self.graph.edges(data=True))

    def visualize_customer_topology(self, output_file="customer_topology.html"):
        """Generate an interactive PyVis topology visualization for customer interfaces."""
        net = Network(height="800px", width="100%", notebook=False, bgcolor="#222222", font_color="white")

        for node in self.graph.nodes():
            net.add_node(node, label=node, title=node, color="skyblue")

        for src, dst, data in self.graph.edges(data=True):
            edge_color = data.get("color", "green")
            net.add_edge(src, dst, title=data["label"], color=edge_color)

        net.show(output_file)
        print(f"✅ Customer Interactive topology saved to {output_file}")

    def save_customer_as_drawio(self, output_file="customer_topology.drawio"):
        """Generate a structured Draw.io topology for customer interfaces."""
        root = ET.Element("mxGraphModel")
        doc = ET.SubElement(root, "root")
        ET.SubElement(doc, "mxCell", id="0")
        ET.SubElement(doc, "mxCell", id="1", parent="0")

        # 🌟 Use a Force-Directed Layout (Like PyVis)
        pos = nx.spring_layout(self.graph, k=0.6, scale=800)

        # 🟢 Store node positions for Draw.io
        drawio_nodes = {}
        node_id = 10
        for node, (x, y) in pos.items():
            node_elem = ET.SubElement(doc, "mxCell", id=str(node_id), value=node, style="shape=ellipse", vertex="1",
                                      parent="1")

            geometry_elem = ET.SubElement(node_elem, "mxGeometry")
            geometry_elem.set("x", str(int(x)))
            geometry_elem.set("y", str(int(y)))
            geometry_elem.set("width", "100")
            geometry_elem.set("height", "100")
            geometry_elem.set("as", "geometry")

            drawio_nodes[node] = node_id
            node_id += 1

        # 🔵 Add edges (connections)
        edge_id = 100
        for src, dst, data in self.graph.edges(data=True):
            label = data["label"]
            edge_color = data.get("color", "green")
            stroke_color = "#ff0000" if edge_color == "red" else "#00ff00"

            src_id, dst_id = drawio_nodes[src], drawio_nodes[dst]

            edge_elem = ET.SubElement(doc, "mxCell", id=str(edge_id), value=label, edge="1", parent="1",
                                      source=str(src_id), target=str(dst_id),
                                      style=f"edgeStyle=elbowEdgeStyle;curved=1;strokeColor={stroke_color};")

            geometry_elem = ET.SubElement(edge_elem, "mxGeometry")
            geometry_elem.set("relative", "1")
            geometry_elem.set("as", "geometry")

            edge_id += 1

        # ✍️ Save to file
        tree = ET.ElementTree(root)
        tree.write(output_file, encoding="utf-8", xml_declaration=True)
        print(f"✅ Customer Draw.io topology saved to {output_file}")


# Usage
folder_path = "./interface_files"  # Change to your directory path
customer_topology = CustomerTopology(folder_path)
customer_topology.build_topology()
customer_topology.save_customer_as_drawio()
customer_topology.visualize_customer_topology()
