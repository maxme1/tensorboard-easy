A small logger that lets you write logs readable by Tensorboard but
doesn’t require Tensorflow.

Usage
=====

You can use the logger as a context manager:

.. code:: python

    from tensorboard_easy import Logger
    import numpy as np

    with Logger('/path/to/logs/folder/') as log:
        log.log_scalar('my_scalar', 100, step=1)
        log.log_image('my_images', np.random.rand(3, 20, 20), step=1)

or you can close the logger explicitly:

.. code:: python

    log = Logger('/some/other/logs')
    log.log_text('my_text', "Let's throw in some text", 0)
    log.log_text('my_text', [['Some', 'tensor'], ['with', 'text!']], 1)

    log.log_histogram('my_histogram', np.random.rand(500), step=0)
    log.close()

It supports scalars, images, text and histograms.

You can also create functions, that write to a specific tag and automatically
increase the step:

.. code:: python

    with Logger('/path/to/logs/folder/') as log:
        write_loss = log.make_log_scalar('loss')
        for i in range(1, 100):
            write_loss(1 / i)


Installation
============

It can be installed via pip:

``pip install tensorboard-easy``

The ``tensorflow`` or ``tensorflow-tensorboard`` packages are not
required, however you will need one of them to visualize your logs.