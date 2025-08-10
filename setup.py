#!/usr/bin/env python3
"""
Setup script for Research Paper Extractor
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="research-paper-extractor",
    version="1.0.0",
    author="Sreeram",
    author_email="sreeram.lagisetty@gmail.com",
    description="A Python tool that automatically downloads research papers from arXiv based on topics you specify",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Sreeram5678/Research-Paper-Extractor",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Scientific/Engineering :: Information Analysis",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "research-paper-extractor=main:cli",
        ],
    },
    keywords="arxiv research papers download pdf machine learning ai",
    project_urls={
        "Bug Reports": "https://github.com/Sreeram5678/Research-Paper-Extractor/issues",
        "Source": "https://github.com/Sreeram5678/Research-Paper-Extractor",
        "Documentation": "https://github.com/Sreeram5678/Research-Paper-Extractor#readme",
    },
)
