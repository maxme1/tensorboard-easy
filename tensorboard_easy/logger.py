import os
import struct
from time import time
from io import BytesIO
from typing import Union

from PIL import Image
import numpy as np

from .proto.event_pb2 import Event, Summary
from .utils import *

COLOR_SPACES = {
    1: 'L',  # grayScale
    3: 'RGB',
    4: 'RGBA',
}


class Logger:
    def __init__(self, path):
        os.makedirs(path, exist_ok=True)
        # TODO: get machine real name instead of localhost
        self.filename = os.path.join(path, f'events.out.tfevents.{time()}.localhost')
        self.file = None

    def __enter__(self):
        self.file = open(self.filename, 'wb')
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.file.close()
        self.file = None

    def _write_event(self, summary, step):
        event = Event(wall_time=time(), summary=summary, step=step)
        event = event.SerializeToString()
        header = struct.pack('Q', len(event))
        self.file.write(header)
        self.file.write(struct.pack('I', encode(header)))
        self.file.write(event)
        self.file.write(struct.pack('I', encode(event)))
        self.file.flush()

    @staticmethod
    def _make_log(tag, first_step, method):
        step = first_step - 1

        def wrapper(value):
            nonlocal step
            step += 1
            return method(tag, value, step)

        return wrapper

    def make_log_scalar(self, tag: str, first_step: int = 0) -> callable(Union[int, float]):
        """
        Creates a shortcut callable, that writes to a tag and increments the step.

        Parameters
        ----------
        tag: str
        first_step: int, optional
        """
        return self._make_log(tag, first_step, self.log_scalar)

    def make_log_image(self, tag: str, first_step: int = 0) -> callable(Union[int, float]):
        """
        Analog to `make_log_scalar`
        """
        return self._make_log(tag, first_step, self.log_image)

    def log_scalar(self, tag: str, value: Union[int, float], step: int):
        """
        Adds a scalar to log.

        Parameters
        ----------
        tag: str
        value: int, float
        step: int
        """
        value = float(value)

        summary = Summary()
        summary.value.add(tag=tag, simple_value=value)
        self._write_event(summary, step)

    def log_image(self, tag: str, image: np.array, step: int):
        """
        Adds an image to log.

        Parameters
        ----------
        tag: str
        image: np.array
            Image to save of shape 3xMxN (RGB), 4xMxN (RGBA), MxN or 1xMxN (grayScale)
        step: int
        """
        assert image.ndim in [2, 3]

        if image.ndim == 3:
            mode = len(image)
            if mode == 1:
                image = image[0]
            else:
                image = np.transpose(image, (1, 2, 0))
        else:
            mode = 1

        try:
            image = Image.fromarray(image, COLOR_SPACES[mode])
        except KeyError:
            raise TypeError(f'Cannot convert tensor of shape {image.shape} '
                            f'to image') from None

        # convert to bytes
        with BytesIO() as output:
            image.save(output, 'BMP')
            image_string = output.getvalue()

        img = Summary.Image(height=image.height, width=image.width, colorspace=mode,
                            encoded_image_string=image_string)
        summary = Summary()
        summary.value.add(tag=tag, image=img)
        self._write_event(summary, step)
