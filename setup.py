from setuptools import setup

setup(
    name='frc449server',
    version='0.1.0',
    description='Server for referee app for Bunnybots 2021',
    url='https://github.com/blair-robot-project/Bunnybot2021Server',
    author='FRC team 449',
    packages=['frc449server'],
    install_requires=["pybluez"],
)