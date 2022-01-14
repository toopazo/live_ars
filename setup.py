import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="live_ars",    # Replace with your own username
    version="0.0.9",
    author="toopazo",
    author_email="toopazo@protonmail.com",
    description="Python package to communicate in real time with an Arduino equipped with current and rpm sensors",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/toopazo/live_ars",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
