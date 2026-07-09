import time
import threading

import cv2
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from ultralytics import YOLO
from picamera2 import Picamera2
from libcamera import controls

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Set up Model
print("Loading YOLO model...")
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
model = YOLO(str(BASE_DIR / "best.pt"))
print("YOLO model loaded.")

# Set up Camera
print("Starting Raspberry Pi Camera Module 3...")
camera = Picamera2()

camera_config = camera.create_video_configuration(
    main={
        "size": (1280, 720),
        "format": "RGB888",
    }
)

camera.configure(camera_config)
camera.start()

# Camera autofocus.
camera.set_controls({
    "AfMode": controls.AfModeEnum.Continuous
})

time.sleep(1)

print("Pi camera started.")

camera_lock = threading.Lock()


def read_camera():
    with camera_lock:
        frame = camera.capture_array()

    return frame


def make_jpeg(frame):
    success, buffer = cv2.imencode(".jpg", frame)

    if not success:
        return None

    return buffer.tobytes()


def send_frame(jpeg):
    return (
        b"--frame\r\n"
        b"Content-Type: image/jpeg\r\n\r\n" + jpeg + b"\r\n"
    )


def raw_stream():
    while True:
        frame = read_camera()

        jpeg = make_jpeg(frame)

        if jpeg is None:
            time.sleep(0.1)
            continue

        yield send_frame(jpeg)

        time.sleep(0.03)


def detection_stream():
    while True:
        frame = read_camera()

        # configure model settings
        result = model.predict(
            source=frame,
            imgsz=320,
            conf=0.30,
            verbose=False,
        )[0]

        frame_with_boxes = result.plot()

        jpeg = make_jpeg(frame_with_boxes)

        if jpeg is None:
            time.sleep(0.1)
            continue

        yield send_frame(jpeg)

@app.get("/video")
def video():
    return StreamingResponse(
        raw_stream(),
        media_type="multipart/x-mixed-replace; boundary=frame",
    )


@app.get("/detect")
def detect():
    return StreamingResponse(
        detection_stream(),
        media_type="multipart/x-mixed-replace; boundary=frame",
    )


@app.on_event("shutdown")
def shutdown():
    camera.stop()