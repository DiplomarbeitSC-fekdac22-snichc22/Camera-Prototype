import random
import shutil
from pathlib import Path

SOURCE = Path("custom_data")
DEST = Path("custom_data")

TRAIN_PERCENT = 0.9
IMAGE_EXTENSIONS = [".jpg", ".jpeg", ".png"]

images_dir = None
labels_dir = None

for path in SOURCE.rglob("*"):
    if path.is_dir() and path.name.lower() == "images":
        images_dir = path
    if path.is_dir() and path.name.lower() == "labels":
        labels_dir = path

if images_dir is None:
    raise RuntimeError("No images folder found inside custom_data")

if labels_dir is None:
    raise RuntimeError("No labels folder found inside custom_data")

print("Images folder:", images_dir)
print("Labels folder:", labels_dir)

for folder in [
    DEST / "train" / "images",
    DEST / "train" / "labels",
    DEST / "validation" / "images",
    DEST / "validation" / "labels",
]:
    folder.mkdir(parents=True, exist_ok=True)

images = []

for ext in IMAGE_EXTENSIONS:
    images.extend(images_dir.rglob(f"*{ext}"))

images = sorted(images)
random.shuffle(images)

split_index = int(len(images) * TRAIN_PERCENT)

train_images = images[:split_index]
validation_images = images[split_index:]


def copy_files(image_list, split_name):
    for image_path in image_list:
        label_path = labels_dir / f"{image_path.stem}.txt"

        if not label_path.exists():
            print(f"Missing label for {image_path.name}")
            continue

        shutil.copy2(image_path, DEST / split_name / "images" / image_path.name)
        shutil.copy2(label_path, DEST / split_name / "labels" / label_path.name)


copy_files(train_images, "train")
copy_files(validation_images, "validation")

print("Train images:", len(train_images))
print("Validation images:", len(validation_images))
print("Done.")