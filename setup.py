from setuptools import setup, find_packages

setup(
    name="atriage",
    description="A dumb afl-fuzz triage tool.",
    version="0.2",
    url="https://github.com/Ayrx/atriage",
    author="Terry Chia",
    author_email="terrycwk1994@gmail.com",
    license="Apache License, Version 2.0",
    python_requires='>=3',
    install_requires=[
        "Click",
        "tabulate",
    ],
    entry_points="""
        [console_scripts]
        atriage=atriage:cli
    """,
    packages=find_packages(exclude=["tests*"]),
)
