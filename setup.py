__author__ = 'Jeff West @ ApigeeCorporation'

from setuptools import setup, find_packages

VERSION = '0.0.10'

setup(
        name='usergrid',
        version=VERSION,
        description='Usergrid SDK for Python',
        url='http://usergrid.apache.org',
        download_url="https://codeload.github.com/jwest-apigee/usergrid-python/zip/v" + VERSION,
        author='Jeff West',
        author_email='jwest@apigee.com',
        packages=find_packages(),
        install_requires=[
            'requests',
            'urllib3'
        ],
        entry_points={
        }
)
