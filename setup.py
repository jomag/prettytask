
from os import path

# Always prefer setuptools over distutils
from setuptools import setup, find_packages
from distutils.core import setup

from prettytask import __version__

base = path.abspath(path.dirname(__file__))

# Get long description from README.md
with open(path.join(base, "README.md"), "r") as fp:
    long_description = fp.read()

setup(
    name="prettytask",
    version=__version__,
    description="Pretty task printing",
    long_description=long_description,
    url="http://github.com/jomag/prettytask",
    license="MIT",
    author="Jonatan Magnusson",
    author_email="jonatan.magnusson@gmail.com",

    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 2"
        "Programming Language :: Python :: 3"
    ],

    install_requires=["colorama"],

    keywords = "cli commandline prompt",
    py_modules=["prettytask"]
)
 

