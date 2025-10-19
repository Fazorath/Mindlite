#!/usr/bin/env python3
"""
Setup script for mindlite CLI application.
"""

from setuptools import setup, find_packages
import os

# Read the README file
def read_readme():
    with open("README.md", "r", encoding="utf-8") as fh:
        return fh.read()

# Read requirements (none for this project - uses only stdlib)
def read_requirements():
    return []

setup(
    name="mindlite",
    version="1.0.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="A minimal, fast CLI for managing ideas, todos, and issues using only Python's standard library",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/mindlite",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Topic :: Office/Business",
        "Topic :: Utilities",
    ],
    python_requires=">=3.11",
    install_requires=read_requirements(),
    entry_points={
        "console_scripts": [
            "mindlite=mindlite.cli:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
    keywords="cli todo task management productivity",
    project_urls={
        "Bug Reports": "https://github.com/yourusername/mindlite/issues",
        "Source": "https://github.com/yourusername/mindlite",
        "Documentation": "https://github.com/yourusername/mindlite#readme",
    },
)
