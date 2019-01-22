# -*- coding: utf-8 -*-

"""
To upload to PyPI, PyPI test, or a local server:
python setup.py bdist_wheel upload -r <server_identifier>
"""

import setuptools

setuptools.setup(
    name="CorrectHighOrders",
    version="0.1",
    author="Andreas Mittelberger",
    author_email="Brow71189@gmail.com",
    description="A Nion Swift plug-in to calculate the lens excitations for high order aberrations",
    url="https://github.com/Brow71189/CorrectHighOrders",
    packages=["nionswift_plugin.correct_high_orders"],
    install_requires=['nionswift-instrumentation'],
    license='MIT',
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Programming Language :: Python :: 3.5",
    ],
    python_requires='~=3.5',
    zip_safe=False,
)
