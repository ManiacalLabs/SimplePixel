import os
import sys
from setuptools import setup, find_packages

INSTALLATION_ERROR = """INSTALLATION ERROR!

SimpPixel requires Python 3.4+ but
you are using version {0.major}.{0.minor}.{0.micro}
"""

if sys.version_info.major != 3:
    print(INSTALLATION_ERROR.format(sys.version_info))
    sys.exit(1)

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

def _get_version():
    from os.path import abspath, dirname, join
    filename = join(dirname(abspath(__file__)), 'SimplePixel', 'VERSION')
    return open(filename).read().strip()

with open('requirements.txt') as f:
    REQUIRED = f.read().splitlines()


setup(
    name = "SimplePixel",
    version = _get_version(),
    author = "Adam Haile",
    author_email = "adam@maniacallabs.com",
    description = "A simple python LED control framework, in the spirit of FastLED",
    license = "MIT",
    keywords = "led pixels blinky",
    url = "https://github.com/ManiacalLabs/SimplePixel",
    packages=find_packages(),
    long_description=read('README.md'),
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
    include_package_data=True,
    install_requires=REQUIRED
)
