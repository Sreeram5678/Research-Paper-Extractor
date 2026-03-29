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
    version="2.1.0",
    author="Sreeram Lagisetty",
    author_email="sreeram.lagisetty@gmail.com",
    description=(
        "Search, download, analyse, and manage arXiv research papers. "
        "Features citation export, TF-IDF summaries, a local library, "
        "daily digests, batch downloads, and Semantic Scholar citation lookup."
    ),
    long_description=long_description,
    long_description_content_type="text/markdown",
    license="MIT",
    url="https://github.com/Sreeram5678/Research-Paper-Extractor",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Science/Research",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Topic :: Scientific/Engineering :: Information Analysis",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Utilities",
        "Environment :: Console",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "rpe=main:cli",
            "research-paper-extractor=main:cli",
        ],
    },
    keywords=(
        "arxiv research papers download pdf machine learning ai nlp "
        "citation bibtex digest library watchlist semantic scholar"
    ),
    project_urls={
        "Bug Reports": "https://github.com/Sreeram5678/Research-Paper-Extractor/issues",
        "Source": "https://github.com/Sreeram5678/Research-Paper-Extractor",
        "Documentation": "https://github.com/Sreeram5678/Research-Paper-Extractor#readme",
    },
)
