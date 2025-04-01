from abc import abstractmethod


class Model:
    def __init__(self, *args, **kwargs):
        pass

    @abstractmethod
    def execute(self, input_data: bytes) -> bytes:
        pass
