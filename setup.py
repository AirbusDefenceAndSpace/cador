from setuptools import setup, find_packages

setup(
    name='cador',
    version='0.7.7',
    packages=find_packages(),
    maintainer='Airbus Defense & Space',
    description='Geo Processing Platform Cradle for Docker Algorithm',
    install_requires=[line for line in open('requirements.txt')],
    tests_require=[line for line in open('test_requirements.txt')]
)
