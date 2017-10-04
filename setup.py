from distutils.core import setup

setup(
    name='tensorboard-easy',
    packages=['tensorboard_easy'],
    include_package_data=True,
    version='0.1',
    description='A tensorflow-independent tensorboard logger',
    author='maxme1',
    author_email='maxs987@gmail.com',
    license='MIT',
    url='https://github.com/maxme1/tensorboard-easy',
    download_url='https://github.com/maxme1/tensorboard-easy/archive/0.1.tar.gz',
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
