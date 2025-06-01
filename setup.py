from setuptools import setup, find_packages

setup(
    name="pymagic-guyue",
    version="0.0.1",
    author="Guyue",
    author_email="guyuecw@qq.com",
    description="A utility library for Python development",
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    url="https://github.com/guyue55/pymagic",
    packages=find_packages(),
    install_requires=[
        "loguru"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6"
)
