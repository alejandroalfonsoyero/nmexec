import cv2
import ctypes
darknet = ctypes.CDLL("libdarknet.so")
import numpy as np

# Cargar YOLO
network, class_names, class_colors = darknet.load_network(
    "cfg/yolov4.cfg",
    "cfg/coco.data",
    "yolov7-tiny.weights",
    batch_size=1
)

width, height = darknet.network_width(network), darknet.network_height(network)

# Captura de video
cap = cv2.VideoCapture(0)  # Usa 0 para webcam, o coloca la URL de la cámara

def detect(frame):
    frame_resized = cv2.resize(frame, (width, height))
    frame_rgb = cv2.cvtColor(frame_resized, cv2.COLOR_BGR2RGB)

    img_for_detect = darknet.make_image(width, height, 3)
    darknet.copy_image_from_bytes(img_for_detect, frame_rgb.tobytes())

    detections = darknet.detect_image(network, class_names, img_for_detect)
    darknet.free_image(img_for_detect)

    return detections

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    detections = detect(frame)

    # Dibujar detecciones
    for label, confidence, bbox in detections:
        x, y, w, h = map(int, bbox)
        cv2.rectangle(frame, (x - w//2, y - h//2), (x + w//2, y + h//2), (0, 255, 0), 2)
        cv2.putText(frame, f"{label} ({confidence}%)", (x, y - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

    cv2.imshow("YOLO Real-Time", frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()
