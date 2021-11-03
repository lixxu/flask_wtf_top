"""
flask_wtf_top
--------------
Simple wrapper for parsing data for flask_wtf
"""

import os.path

from setuptools import setup

folder = os.path.dirname(os.path.abspath(__file__))
version = ""
with open(os.path.join(folder, "flask_wtf_top/__init__.py")) as f:
    for line in f:
        if line.startswith("__version__ = "):
            version = line.split("=")[-1].strip().replace('"', "")
            break

setup(
    name="flask_wtf_top",
    version=version.replace("'", ""),
    url="https://github.com/lixxu/flask_wtf_top",
    license="BSD",
    author="Lix Xu",
    author_email="xuzenglin@gmail.com",
    description="Simple wrapper for parsing data for flask_wtf",
    long_description=__doc__,
    packages=["flask_wtf_top"],
    zip_safe=False,
    platforms="any",
    install_requires=["flask_wtf"],
    classifiers=[
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 3",
    ],
)
