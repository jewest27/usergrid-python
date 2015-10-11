__author__ = 'Jeff West @ ApigeeCorporation'

from setuptools import setup, find_packages

VERSION = '0.0.1'

setup(
    name='usergrid',
    version=VERSION,
    description='Usergrid SDK for Python',
    author='Jeff West',
    author_email='jwest@apigee.com',
    url='http://usergrid.apache.org',
    packages=find_packages(),
    install_requires=[
        'requests',
    ],
    entry_points={
    }
)
