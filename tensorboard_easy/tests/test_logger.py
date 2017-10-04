import unittest
from math import sin
from time import sleep

import numpy as np

from tensorboard_easy import Logger


class TestLogger(unittest.TestCase):
    def test_update(self):
        try:
            with Logger('log_path') as log:
                for i in range(100):
                    log.log_scalar('test_update', sin(i / 10) * 10, i)
                    sleep(.1)
        except BaseException:
            self.fail()

    def test_image(self):
        try:
            with Logger('log_path') as log:
                img = np.random.rand(3, 20, 20)
                log.log_image('test_image', img, 0)
        except BaseException:
            self.fail()

    def test_image_exception(self):
        with Logger('log_path') as log:
            with self.assertRaises(TypeError):
                log.log_image('test_img_ex', np.random.rand(5, 10, 10), 0)

    def test_shortcut(self):
        try:
            with Logger('log_path') as log:
                log_square = log.make_log_scalar('test_shortcut')
                for i in range(100):
                    log_square(i ** 2)
                    sleep(.1)
        except BaseException:
            self.fail()
