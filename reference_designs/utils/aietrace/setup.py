# Copyright (C) 2023 Advanced Micro Devices, Inc. All rights reserved.
# SPDX-License-Identifier: MIT

from setuptools import find_packages, setup

setup(
    name="aietrace",
    version='0.1',
    package_data={
        '': ['aietrace/*.py',
             'aietrace/tests/*',
             'aietrace/tests/test_traces/*.txt'
             ],
    },
    packages=find_packages(),
    python_requires=">=3.8.*",
    install_requires=[
    ],
    entry_points={
        'console_scripts': [
                'aietrace=aietrace:main'
            ],
        },
    description="Utility for parsing trace information extracted from MLIR-AIE applications")
