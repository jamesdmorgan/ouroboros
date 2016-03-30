from setuptools import setup
setup(
    name="es-ouroboros",
    version="0.4",
    author="Bob Gregory",
    author_email="pathogenix@gmail.com",
    url="https://github.com/madedotcom/ouroboros/",
    keywords=["eventstore", "cli", "management"],
    description="Management CLI and library for EventStore",
    packages=["ouroboros"],
    install_requires=['click', 'requests', 'future'],
    entry_points='''
        [console_scripts]
        ouro=ouroboros.cli:main
    ''',
)
