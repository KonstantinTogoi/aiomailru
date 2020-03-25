from setuptools import find_packages, setup


setup(
    name='aiomailru',
    version='0.0.24',
    author='Konstantin Togoi',
    author_email='konstantin.togoi@protonmail.com',
    url='https://github.com/KonstantinTogoi/aiomailru',
    description='Platform@Mail.ru Python REST API wrapper',
    long_description=open('README.rst').read(),
    license='BSD',
    packages=find_packages(),
    install_requires='aiohttp>=3.0.0',
    setup_requires=['pytest-runner'],
    tests_require=['pytest-asyncio', 'pytest-dotenv', 'pytest-localserver'],
    extras_require={
        'logging': ['PyYAML'],
        'scrapers': ['pyppeteer<=0.0.25'],
    },
    keywords=['mail.ru rest api scrapers asyncio'],
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3 :: Only',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ]
)
