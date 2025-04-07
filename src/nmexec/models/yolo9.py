from typing import Dict
import numpy as np
from yolo9 import YOLO9, CocoModels

from .model import Model


class Yolo9Model(Model):

    def __init__(
        self,
        model_name: str,
        device: str,
        dnn: bool,
        half: bool,
        iou_threshold: float,
        max_detections: int,
        classes: Dict[int, float],  # class id -> confidence threshold
    ):
        self.yolo9 = YOLO9(
            model=CocoModels(model_name),
            device=device,
            classes=classes,
            dnn=dnn,
            half=half,
            batch_size=1,
            iou_threshold=iou_threshold,
            max_det=max_detections,
        )

    def execute(self, img: np.ndarray) -> list:
        detections = self.yolo9.detect(img)
        return detections
