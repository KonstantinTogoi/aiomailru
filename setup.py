import os
from setuptools import setup

version = '0.0.1'


def read(filename):
    with open(os.path.join(os.path.dirname(__file__), filename)) as f:
        return f.read()


setup(
    name='aiomailru',
    version=version,
    author='Konstantin Togoi',
    author_email='konstantin.togoi@outlook.com',
    url='https://github.com/KonstantinTogoi/aiomailru',
    description='Platform@Mail.ru Python REST API wrapper',
    long_description=read('README.rst'),
    license='BSD',
    packages=['aiomailru'],
    install_requires='aiohttp>=3.0.0',
    keywords=['mail.ru api asyncio'],
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3 :: Only',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ]
)
