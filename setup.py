from distutils.core import setup
from setuptools import find_packages

setup(
    name='tensorboard-easy',
    packages=find_packages(),
    include_package_data=True,
    version='0.1.10',
    description='A tensorflow-independent tensorboard logger',
    author='maxme1',
    author_email='maxs987@gmail.com',
    license='MIT',
    url='https://github.com/maxme1/tensorboard_logger',
    download_url='https://github.com/maxme1/tensorboard_logger/archive/0.1.10.tar.gz',
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