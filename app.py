# app.py
from flask import Flask, render_template, send_file, request, jsonify
import os

from topology import NetworkTopology
from firewall import (
    parse_firewall_config,
    check_firewall_rules_with_masks,
)
# NEW import
from backup_config import backup_configs_for_all_devices

app = Flask(__name__)

FOLDER_PATH = "./interface_files"
FIREWALL_CONFIG_FILE = "./firewall_files/firewall_10_11_0_31.txt"

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/generate_topology")
def generate_topology():
    topology = NetworkTopology(FOLDER_PATH)
    topology.build_topology()
    html_file = topology.visualize_topology_interactive()
    return send_file(html_file)

@app.route("/check_firewall", methods=["POST"])
def check_firewall():
    src_ip = request.form.get("src_ip", "")
    dst_ip = request.form.get("dst_ip", "")
    dst_port = request.form.get("dst_port", "")

    fw_data = parse_firewall_config(FIREWALL_CONFIG_FILE)

    # Single pass check
    src_equiv, dst_equiv, port_equiv, matched_policies = check_firewall_rules_with_masks(
        src_ip, dst_ip, dst_port, fw_data
    )

    # Build the response as HTML
    html = []
    # No <script> tag here anymore!

    # Always show the main summary
    html.append('<h3>Firewall Check Results (Single Pass)</h3>')
    html.append(f'<p><b>Source IP:</b> {src_ip}, '
                f'<b>Destination IP:</b> {dst_ip}, '
                f'<b>Port:</b> {dst_port}</p>')

    # Always show matched policies
    if matched_policies:
        html.append("""
        <table class="firewall-table" border="1" cellpadding="5" style="border-collapse: collapse;">
          <thead>
            <tr>
              <th>Policy Name</th>
              <th>From-Zone</th>
              <th>To-Zone</th>
              <th>Source-Addresses</th>
              <th>Destination-Addresses</th>
              <th>Applications</th>
            </tr>
          </thead>
          <tbody>
        """)
        for pol in matched_policies:
            html.append(f"""
            <tr>
              <td>{pol['policy']}</td>
              <td>{pol['from-zone']}</td>
              <td>{pol['to-zone']}</td>
              <td>{pol['src-address']}</td>
              <td>{pol['dst-address']}</td>
              <td>{pol['apps']}</td>
            </tr>
            """)
        html.append("</tbody></table>")
    else:
        html.append("<p>No matching policy found.</p>")

    # One "View More" button to show/hide expansions
    html.append("""
    <br>
    <button onclick="toggleMore()">View More</button>
    <div id="moreDetails" style="display:none; margin-top: 10px; border: 1px solid #ccc; padding: 10px;">
    """)

    # Inside this hidden div, we display expansions
    html.append("<h4>Source IP Equivalents</h4>")
    html.append(f"<p>{sorted(src_equiv)}</p>")

    html.append("<h4>Destination IP Equivalents</h4>")
    html.append(f"<p>{sorted(dst_equiv)}</p>")

    html.append("<h4>Port/Application Equivalents</h4>")
    html.append(f"<p>{sorted(port_equiv)}</p>")

    html.append("</div>")  # end of moreDetails div

    return "".join(html)

# NEW route for backup:
@app.route("/backup_configs")
def backup_configs():
    """
    Route that triggers device backup logic.
    For now, it just logs in (via napalm) and returns a snippet of config or error.
    """
    result = backup_configs_for_all_devices()
    # We'll return the result as plain text or HTML
    return f"<h3>Backup Results</h3><pre>{result}</pre>"

if __name__ == "__main__":
    app.run(debug=True)
