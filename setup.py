from distutils.core import setup

setup(
    name='tensorboard-easy',
    packages=['tensorboard_easy'],
    version='0.1.6',
    description='A tensorflow-independent tensorboard logger',
    author='maxme1',
    author_email='maxs987@gmail.com',
    license='MIT',
    url='https://github.com/maxme1/tensorboard_logger',
    download_url='https://github.com/maxme1/tensorboard_logger/archive/0.1.6.tar.gz',
    keywords=[
        'tensorboard', 'logging'
    ],
    classifiers=[],
    install_requires=[
        'Pillow>=4.3',
        'protobuf>=3.4',
        'crccheck>=0.6',
        'numpy>=1.11',
    ]
)
