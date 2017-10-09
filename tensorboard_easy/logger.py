import os
import socket
import struct
from time import time
from io import BytesIO
from typing import Union, Iterable

import functools
from PIL import Image
import numpy as np

from .proto.event_pb2 import Event
from .proto.summary_pb2 import Summary, HistogramProto, SummaryMetadata
from .proto.tensor_pb2 import TensorProto
from .proto.tensor_shape_pb2 import TensorShapeProto
from .proto import types_pb2 as tensor_type
from .utils import *

COLOR_SPACES = {
    1: 'L',  # grayScale
    3: 'RGB',
    4: 'RGBA',
}


class Logger:
    def __init__(self, path):
        os.makedirs(path, exist_ok=True)
        self.filename = os.path.join(path, 'events.out.tfevents.%f.%s' %
                                     (time(), socket.gethostname()))
        self.file = open(self.filename, 'wb')

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

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

    def close(self):
        self.file.close()
        self.file = None

    def make_log_scalar(self, tag: str, first_step: int = 0) -> callable(Union[int, float]):
        """
        Creates a shortcut callable, that writes to a tag and increments the step.

        Parameters
        ----------
        tag: str
        first_step: int, optional
        """
        return self._make_log(tag, first_step, self.log_scalar)

    def make_log_image(self, tag: str, first_step: int = 0) -> callable(np.array):
        """Analog to `make_log_scalar`"""
        return self._make_log(tag, first_step, self.log_image)

    def make_log_text(self, tag: str, first_step: int = 0) -> callable(Union[str, Iterable]):
        """Analog to `make_log_scalar`"""
        return self._make_log(tag, first_step, self.log_text)

    def make_log_histogram(self, tag: str, first_step: int = 0, num_bars: int = 30) \
            -> callable(np.array):
        """Analog to `make_log_scalar`"""
        method = functools.partial(self.log_histogram, num_bars=num_bars)
        return self._make_log(tag, first_step, method)

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
            raise TypeError('Cannot convert tensor of shape %s '
                            'to image' % image.shape) from None

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
        data = data.ravel()
        min_ = data.min()
        max_ = data.max()
        sum_ = data.sum()
        sum_sq = data.dot(data)
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

    def log_text(self, tag: str, tensor: Union[str, Iterable], step: int):
        """
        Adds a tensor with text to log.

        Parameters
        ----------
        tag: str
        tensor: str, iterable
            String, or iterable of type str and dimensionality <= 2
        step: int
        """
        tensor = np.asarray(tensor, dtype=bytes)

        shape = TensorShapeProto()
        for i in tensor.shape:
            shape.dim.add(size=i)
        tensor_ = TensorProto(dtype=tensor_type.DT_STRING, tensor_shape=shape,
                              string_val=tensor.ravel(), version_number=1)
        # TODO: no need to save metadata on each step
        metadata = SummaryMetadata()
        metadata.plugin_data.add(plugin_name='text', content='{}')
        self._write_event(tag, step, tensor=tensor_, metadata=metadata)
