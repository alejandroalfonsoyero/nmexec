import pickle
import cv2
from yolo9 import YOLO9

from .model import Model


class Yolo9Model(Model):

    def __init__(
        self,
        weights: str,
        device: str,
    ):
        self.yolo9 = YOLO9(weights, device)

    def execute(self, input_data: bytes) -> bytes:
        img = pickle.loads(input_data)
        detections = self.yolo9.detect(img)
        return pickle.dumps(detections)
