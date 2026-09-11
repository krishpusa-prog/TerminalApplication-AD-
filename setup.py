from setuptools import setup, find_packages

setup(
    name="cli-music-player",
    version="0.1.0",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    install_requires=[
        "pygame>=2.5.0",
        "textual>=0.80.0",
    ],
    entry_points={
        "console_scripts": [
            "music-player=player.main:main",
        ],
    },
)
