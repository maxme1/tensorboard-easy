import os
import struct
from time import time
from io import BytesIO
from typing import Union

from PIL import Image
import numpy as np

from .proto.event_pb2 import Event, Summary, HistogramProto
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

    def _write_event(self, tag, step, **kwargs):
        summary = Summary()
        summary.value.add(tag=tag, **kwargs)
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
        self._write_event(tag, step, simple_value=value)

    def log_image(self, tag: str, image: np.array, step: int):
        """
        Adds an image to log.

        Parameters
        ----------
        tag: str
        image: np.array
            Image of shape 3xMxN (RGB), 4xMxN (RGBA), MxN or 1xMxN (grayScale)
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
        self._write_event(tag, step, image=img)

    def log_histogram(self, tag: str, data: np.array, step: int, num_bars: int = 30):
        """
        Adds a histogram to log.

        Parameters
        ----------
        tag: str
        data: np.array
            Array of any shape.
        step: int
        num_bars: int
            The number of bars if the resulting histogram.
        """
        data = data.flatten()
        min_ = data.min()
        max_ = data.max()
        sum_ = data.sum()
        sum_sq = data @ data
        if min_ == max_:
            num = 1
            bucket_limit = [min_]
            bucket = [len(data)]
        else:
            bucket, bucket_limit = np.histogram(data, num_bars)
            num = len(bucket_limit)
            bucket_limit = bucket_limit[1:]

        hist = HistogramProto(min=min_, max=max_, sum=sum_, sum_squares=sum_sq, num=num,
                              bucket_limit=bucket_limit, bucket=bucket)
        self._write_event(tag, step, histo=hist)
