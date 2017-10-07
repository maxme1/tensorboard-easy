A small logger that lets you write logs readable by Tensorboard but
doesn’t require Tensorflow.

Usage
=====

Use the logger as a context manager:

.. code:: python

    from tensorboard_easy import Logger

    with Logger('/path/to/logs/folder/') as log:
        log.log_scalar('my_tag', 100, step=1)

It supports scalars, images, text and histograms.

Installation
============

It can be installed via pip:

``pip install tensorboard-easy``

The ``tensorflow`` or ``tensorflow-tensorboard`` packages are not
required, however you will need one of them to visualize your logs.