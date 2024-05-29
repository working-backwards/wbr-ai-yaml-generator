from distutils.core import setup

from setuptools import find_packages

print(find_packages())

setup(
    name='wbryamlgenerator',
    version='0.1',
    packages=find_packages(),
    long_description=open('README.md').read(),
    install_requires=[
        'openai==1.30.1',
        'langchain==0.1.17',
        'setuptools~=69.2.0',
        'PyYAML~=6.0.1'
    ]
)
