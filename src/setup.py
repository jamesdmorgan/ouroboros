from setuptools import setup, find_packages
setup(
    name="ouroboros",
    version="0.1",
    packages=find_packages(),
    install_requires=['Click'],
    entry_points='''
        [console_scripts]
        ouro=ouroboros.cli:main
    ''',
)
