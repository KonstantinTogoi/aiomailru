import os
from setuptools import setup

version = '0.0.2'

readme_filename = os.path.join(os.path.dirname(__file__), 'README.md')

with open(readme_filename, encoding='utf-8') as f:
    readme = f.read()


setup(
    name='aiomailru',
    version=version,
    author='Konstantin Togoi',
    author_email='konstantin.togoi@outlook.com',
    url='https://github.com/KonstantinTogoi/aiomailru',
    description='Platform@Mail.ru Python REST API wrapper',
    long_description=readme,
    long_description_content_type='text/markdown',
    license='BSD',
    packages=['aiomailru', 'aiomailru.objects'],
    install_requires='aiohttp>=3.0.0',
    extra_require={
        'scrapers': ['pyppeteer<=0.0.25'],
    },
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
