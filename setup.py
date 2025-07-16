# setup.py at your repo root
from setuptools import setup, find_packages

setup(
    name="mafia-online-party-game-server",
    version="0.1",
    packages=find_packages("backend"),
    package_dir={"": "backend"},
)
