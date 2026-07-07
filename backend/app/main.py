import cv2
import threading
import time
from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, JSONResponse

app = FastAPI(title="Camera Prototype Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



class Camera:
    def __init__(self, camera_index: int = 0):
        self.camera_index = camera_index
        self.lock = threading.Lock()
        self.cap = None
        self.open_camera()

    def open_camera(self):
        self.cap = cv2.VideoCapture(self.camera_index)

        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        self.cap.set(cv2.CAP_PROP_FPS, 30)

        if not self.cap.isOpened():
            raise RuntimeError(f"Could not open camera with index {self.camera_index}")

    def get_frame(self):
        with self.lock:
            if self.cap is None or not self.cap.isOpened():
                self.open_camera()

            success, frame = self.cap.read()

            if not success:
                return None

            success, buffer = cv2.imencode(".jpg", frame)

            if not success:
                return None

            return buffer.tobytes()

    def release(self):
        with self.lock:
            if self.cap is not None:
                self.cap.release()
                self.cap = None


camera = Camera(camera_index=0)


@app.get("/")
def root():
    return {
        "message": "Camera backend is running",
        "stream": "/video",
        "snapshot": "/snapshot",
        "health": "/health",
    }


@app.get("/health")
def health():
    frame = camera.get_frame()

    return {
        "backend": "ok",
        "camera": "ok" if frame is not None else "not working",
    }


@app.get("/snapshot")
def snapshot():
    frame = camera.get_frame()

    if frame is None:
        return JSONResponse(
            status_code=500,
            content={"error": "Could not read frame from camera"},
        )

    return Response(content=frame, media_type="image/jpeg")


def generate_frames():
    while True:
        frame = camera.get_frame()

        if frame is None:
            time.sleep(0.1)
            continue

        yield (
            b"--frame\r\n"
            b"Content-Type: image/jpeg\r\n\r\n" + frame + b"\r\n"
        )

        time.sleep(0.03)



@app.get("/video")
def video():
    return StreamingResponse(
        generate_frames(),
        media_type="multipart/x-mixed-replace; boundary=frame",
    )


@app.on_event("shutdown")
def shutdown_event():
    camera.release()