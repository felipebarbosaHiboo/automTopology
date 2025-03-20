import pyvis
import os

print(pyvis.__file__)
pyvis_path = os.path.dirname(pyvis.__file__)
template_path = os.path.join(pyvis_path, "templates", "template.html")

if os.path.exists(template_path):
    print("✅ Pyvis templates are installed correctly.")
else:
    print("❌ Pyvis templates are MISSING! Try reinstalling Pyvis.")
