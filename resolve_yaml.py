#!/usr/bin/env python3

import yaml
import json
from pathlib import Path


def resolve_refs(data, base_path):
    if isinstance(data, dict):
        if "$ref" in data and len(data) == 1:
            # This is a reference, resolve it
            ref_path = data["$ref"]
            if ref_path.startswith("./") or ref_path.startswith("../"):
                # Relative file reference
                if ref_path.startswith("./"):
                    file_path = base_path / ref_path[2:]  # Remove './'
                else:
                    # Handle ../ references
                    file_path = base_path / ref_path

                # Resolve the path
                file_path = file_path.resolve()

                if file_path.exists():
                    with open(file_path, "r", encoding="utf-8") as f:
                        ref_data = yaml.safe_load(f)
                    return resolve_refs(ref_data, file_path.parent)
                else:
                    print(f"Could not find referenced file: {file_path}")
                    return data
            else:
                # Internal reference or other type, keep as is
                return data
        else:
            # Regular dict, resolve refs in values
            resolved = {}
            for key, value in data.items():
                resolved[key] = resolve_refs(value, base_path)
            return resolved
    elif isinstance(data, list):
        # List, resolve refs in items
        return [resolve_refs(item, base_path) for item in data]
    else:
        # Primitive value, return as is
        return data


def main():
    # Input and output paths
    input_file = Path(__file__).parent / "resources" / "api" / "openapi.yaml"
    output_file = Path(__file__).parent / "resources" / "api" / "openapi-resolved.yaml"

    with open(input_file, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    resolved_data = resolve_refs(data, input_file.parent)

    with open(output_file, "w", encoding="utf-8") as f:
        yaml.dump(resolved_data, f, default_flow_style=False, sort_keys=False, indent=2)

    json_output = Path(__file__).parent / "resources" / "api" / "openapi-resolved.json"
    with open(json_output, "w", encoding="utf-8") as f:
        json.dump(resolved_data, f, indent=2)

    print(f"YAML resolved: {output_file}")


if __name__ == "__main__":
    main()
