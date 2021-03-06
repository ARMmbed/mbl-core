#!/usr/bin/env python3
# Copyright (c) 2018 Arm Limited and Contributors. All rights reserved.
#
# SPDX-License-Identifier: BSD-3-Clause

"""Mbed Linux OS Firmware Update Manager setup.py."""

import os
from setuptools import setup


def read(fname):
    """Read the content of a file."""
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
    name="mbl-firmware-update-manager",
    version="1",
    description="Mbed Linux OS Firmware Update Manager",
    long_description=read("README.md"),
    author="Arm Ltd.",
    license="BSD-3-Clause",
    packages=["mbl.firmware_update_manager"],
    zip_safe=False,
    entry_points={
        "console_scripts": [
            "mbl-firmware-update-manager = \
                mbl.firmware_update_manager.cli:_main"
        ]
    },
)
