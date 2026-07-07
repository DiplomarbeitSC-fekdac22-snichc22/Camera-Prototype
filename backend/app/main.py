import time
import threading

import cv2
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from ultralytics import YOLO


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

print("Loading YOLO model...")
model = YOLO("yolov8n.pt")
print("YOLO model loaded.")

camera = cv2.VideoCapture(0, cv2.CAP_V4L2)

camera.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*"MJPG"))
camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
camera.set(cv2.CAP_PROP_FPS, 15)

camera_lock = threading.Lock()


def read_camera():
    with camera_lock:
        success, frame = camera.read()

    if not success:
        return None

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

        if frame is None:
            time.sleep(0.1)
            continue

        jpeg = make_jpeg(frame)

        if jpeg is None:
            time.sleep(0.1)
            continue

        yield send_frame(jpeg)

        time.sleep(0.03)


def detection_stream():
    while True:
        frame = read_camera()

        if frame is None:
            time.sleep(0.1)
            continue

        result = model.predict(
            source=frame,
            imgsz=320,
            conf=0.35,
            verbose=False,
        )[0]

        frame_with_boxes = result.plot()

        jpeg = make_jpeg(frame_with_boxes)

        if jpeg is None:
            time.sleep(0.1)
            continue

        yield send_frame(jpeg)

        # Detection is slower than raw camera.
        time.sleep(0.3)


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
    camera.release()