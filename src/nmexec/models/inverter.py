import cv2
import numpy as np

from .model import Model


class Inverter(Model):

    def execute(self, img: np.ndarray) -> np.ndarray:
        return cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
