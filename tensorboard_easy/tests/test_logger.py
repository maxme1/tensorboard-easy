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

    def test_histogram(self):
        try:
            with Logger('log_path') as log:
                for i in range(40):
                    log.log_histogram('normal', np.random.normal(0, i + 1, 500), i)
                    log.log_histogram('chi', np.random.chisquare(6, 500), i)
                    log.log_histogram('normal/multimodal',
                                      np.stack((np.random.normal(0, i + 1, 500),
                                                np.random.normal(100, i + 1, 500))), i)
        except BaseException:
            self.fail()

    def test_text(self):
        try:
            with Logger('log_path') as log:
                log.log_text('string', 'Test string', 0)
                log.log_text('list', ['A', 'B'], 0)
                log.log_text('2D', [['Some', 'multidimensional'], ['string', 'tensor']], 0)
        except BaseException:
            self.fail()
