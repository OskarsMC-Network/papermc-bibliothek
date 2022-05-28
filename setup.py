from setuptools import setup

__version__ = '3.0.2'

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()
with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = fh.read()

setup(
    name='papermc-bibliothek',
    version=__version__,
    author='OskarZyg',
    author_email='oskar@oskarsmc.com',
    license='MIT',
    description='bibliothek API wrapper with a CLI',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/OskarsMC-Network/papermc-bibliothek',
    packages=["bibliothek"],
    install_requires=[requirements],
    python_requires='>=3.9',
    classifiers=[
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Topic :: Utilities",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.9",
        "Operating System :: OS Independent",
    ],
    entry_points={
        "console_scripts": [
            "bibliothek = bibliothek.__main__:main"
        ]
    },
    include_package_data=True
)