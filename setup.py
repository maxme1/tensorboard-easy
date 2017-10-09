from distutils.core import setup
from setuptools import find_packages

classifiers = '''Development Status :: 5 - Production/Stable
Programming Language :: Python :: 3.4
Programming Language :: Python :: 3.5
Programming Language :: Python :: 3.6'''

with open('README.rst') as file:
    long_description = file.read()

setup(
    name='tensorboard-easy',
    packages=find_packages(),
    include_package_data=True,
    version='0.2',
    description='A tensorflow-independent tensorboard logger',
    long_description=long_description,
    author='maxme1',
    author_email='maxs987@gmail.com',
    license='MIT',
    url='https://github.com/maxme1/tensorboard-easy',
    download_url='https://github.com/maxme1/tensorboard-easy/archive/0.2.tar.gz',
    keywords=[
        'tensorboard', 'logging'
    ],
    classifiers=classifiers.splitlines(),
    install_requires=[
        'Pillow>=4.3',
        'protobuf>=3.4',
        'crccheck>=0.6',
        'numpy>=1.11',
    ]
)
