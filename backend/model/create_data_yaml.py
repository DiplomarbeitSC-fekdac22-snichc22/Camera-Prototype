from pathlib import Path
import yaml

classes_file = Path("custom_data/classes.txt")

if not classes_file.exists():
    raise RuntimeError("custom_data/classes.txt not found")

classes = []

with open(classes_file, "r") as file:
    for line in file:
        line = line.strip()
        if line:
            classes.append(line)

data = {
    "path": str(Path("custom_data").resolve()),
    "train": "train/images",
    "val": "validation/images",
    "nc": len(classes),
    "names": classes,
}

with open("data.yaml", "w") as file:
    yaml.dump(data, file, sort_keys=False)

print("Created custom_data.yaml")
print(data)