from setuptools import setup, find_packages

setup(
    name="atriage",
    description="A dumb afl-fuzz triage tool.",
    version="0.1.dev1",
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
