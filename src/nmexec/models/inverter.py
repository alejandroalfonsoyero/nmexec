import pickle
import cv2

from .model import Model


class Inverter(Model):

    def execute(self, input_data: bytes) -> bytes:
        img = pickle.loads(input_data)
        return pickle.dumps(cv2.cvtColor(img, cv2.COLOR_BGR2GRAY))
