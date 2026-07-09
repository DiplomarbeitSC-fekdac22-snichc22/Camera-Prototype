# Camera Prototype

Simple camera streaming and object detection prototype for the Raspberry Pi robot arm project.

The project has:

- a **FastAPI backend** for camera streaming and object detection
- a **React frontend** for viewing the camera stream
- a custom trained **YOLO model** for detecting objects like `Ball` and `Car`

---

## Project Structure

```text
Camera-Prototype/
├── backend/
│   ├── app/
│   │   └── main.py
│   ├── best.pt
│   ├── requirements.txt
│   └── model/
│       └── training files
├── frontend/
│   ├── src/
│   │   └── App.tsx
│   ├── .env
│   ├── .env.example
│   └── package.json
└── README.md
```

---

## Backend

The backend runs on the Raspberry Pi.

It provides two camera endpoints:

```text
/video   - raw camera stream
/detect  - camera stream with YOLO object detection
```

The backend uses:

- Python
- FastAPI
- Uvicorn
- Picamera2
- OpenCV
- Ultralytics YOLO

---

## Start the Backend

On the Raspberry Pi:

```bash
cd ~/dev/camera-prototype/backend
source ~/venvs/camera/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

The backend then runs at:

```text
http://RASPBERRY_PI_IP:8000
```

Example:

```text
http://192.168.74.17:8000
```

Test directly in the browser:

```text
http://192.168.74.17:8000/video
http://192.168.74.17:8000/detect
```

---

## Frontend

The frontend is a simple React app.

It shows:

- a raw camera stream button
- a detection stream button
- the current stream URL
- the live camera image

---

## Change the Raspberry Pi IP Address

The frontend uses a `.env` file.

Create or edit this file:

```text
frontend/.env
```

Example:

```env
VITE_RASPBERRY_PI_IP=192.168.74.17
```

Only change the IP address:

```env
VITE_RASPBERRY_PI_IP=NEW_RASPBERRY_PI_IP
```

Example:

```env
VITE_RASPBERRY_PI_IP=192.168.178.50
```

Important:

- the variable must start with `VITE_`
- restart the frontend after changing `.env`
- frontend `.env` values are not real secrets because they are visible in the browser

---

## Start the Frontend

On the laptop:

```bash
cd /home/fekdac/Development/htl/diplomarbeit/Code/Camera-Prototype/frontend
npm install
npm run dev -- --host 0.0.0.0
```

Open the shown URL in the browser, usually:

```text
http://localhost:5173
```

or from another device:

```text
http://LAPTOP_IP:5173
```

---

## Using the Application

1. Start the backend on the Raspberry Pi.
2. Start the frontend on the laptop.
3. Open the frontend in the browser.
4. Click **Raw Stream** to see the normal camera image.
5. Click **Detection Stream** to see YOLO object detection.

---

## Custom YOLO Model

The custom trained model is stored as:

```text
backend/best.pt
```

The backend loads this model for detection.

In `backend/app/main.py`, the model should be loaded like this:

```python
model = YOLO("best.pt")
```

or with a safe path:

```python
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
model = YOLO(str(BASE_DIR / "best.pt"))
```

---

## Training Data

Training data is not committed to GitHub.

Ignored folders/files:

```text
data/
backend/best.pt
backend/model/custom_data/
backend/model/runs/
backend/model/*.zip
backend/model/*.pt
```

The model can be trained locally on the laptop and then copied to the Raspberry Pi.

Example:

```bash
scp backend/best.pt robot@robot-arm.local:/home/robot/dev/camera-prototype/backend/best.pt
```

---

## Common Problems

### Frontend shows `undefined:8000`

The frontend cannot read the IP address.

Check:

```text
frontend/.env
```

It must contain:

```env
VITE_RASPBERRY_PI_IP=192.168.74.17
```

Then restart the frontend:

```bash
npm run dev -- --host 0.0.0.0
```

---

### Backend camera is not working

Stop old backend processes:

```bash
pkill -f uvicorn
```

Test the Raspberry Pi camera:

```bash
rpicam-hello --timeout 5000
```

If the camera test fails, reboot the Raspberry Pi or check the camera cable.

---

### Detection is weak

The model needs more real camera images.

Good training images should include:

- different lighting
- object close and far away
- object left, right, and center
- rotated objects
- empty background images
- both objects visible together

After adding more labeled data, train again and replace `backend/best.pt`.

---

## Current Prototype Status

Working:

- Raspberry Pi camera stream
- FastAPI backend
- React frontend
- raw stream endpoint
- detection stream endpoint
- custom YOLO model for `Ball` and `Car`

Still needs improvement:

- more training images
- better detection confidence
- fixed camera mounting
- stable lighting
- workspace coordinate conversion
- connection to robot kinematics
