import os
import glob
import yaml
from pathlib import Path

# Get the folder where this __init__.py is located
_current_dir = Path(__file__).parent
# Dictionary to store all loaded YAML data
prompts = {}

# Iterate over all YAML files in the directory
for yaml_path in glob.glob(os.path.join(_current_dir, "*.yaml")):
    with open(yaml_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
        name = os.path.splitext(os.path.basename(yaml_path))[0]
        prompts[name] = data
