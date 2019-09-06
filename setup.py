from os.path import dirname, join
from setuptools import setup


readme_path = join(dirname(__file__), 'README.md')

with open(readme_path) as readme_file:
    readme = readme_file.read()


setup(
    name='aiomailru',
    version='0.0.19',
    author='Konstantin Togoi',
    author_email='konstantin.togoi@protonmail.com',
    url='https://github.com/KonstantinTogoi/aiomailru',
    description='Platform@Mail.ru Python REST API wrapper',
    long_description=readme,
    long_description_content_type='text/markdown',
    license='BSD',
    packages=['aiomailru', 'aiomailru.logging', 'aiomailru.objects'],
    package_data={'logging': ['config.yaml']},
    include_package_data=True,
    install_requires='aiohttp>=3.0.0',
    extras_require={
        'logging': ['PyYAML'],
        'scrapers': ['pyppeteer<=0.0.25'],
    },
    keywords=['mail.ru api asyncio'],
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
