import re

filenames = [
    "hib-dc01-rtr-core-01-mx304-re0.txt",
    "hib-dc01-rtr-edge-01-acx5448.txt",
    "hib-dc01-rtr-edge-02-acx5448.txt"
]

for filename in filenames:
    match = re.match(r"(.*)-re\d+\.txt", filename)
    if match:
        print(f"✅ Extracted Hostname: {match.group(1)} from {filename}")
    else:
        print(f"❌ Failed to extract hostname from: {filename}")