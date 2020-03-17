# -*- coding: utf-8 -*-

import re
from setuptools import setup, find_packages

with open('iguazu/__init__.py') as f:
    VERSION = re.search(r'^__version__\s*=\s*\'(.*)\'', f.read(), re.M).group(1)


dependencies = [
    'bokeh',
    'click',
    'colorlog',
    'dsu',
    'numpy',
    'mne',
    'nolds',
    'pandas',
    'psutil',
    'prefect',
    'quetzal-client',
    'scikit-learn',
    'scipy',
    'simplegeneric',
    'statsmodels',
    'tables',
    'tzlocal',
    'requests',
    'pyyaml',
    'marshmallow',
    # Requirements for plot-related tasks
    'Jinja2',
    'plotly',
    'matplotlib',
]
build_dependencies = dependencies + ['pytest-runner']
test_dependencies = [
    'pytest',
    'pytest-mock',
]
authors = [
    ('Raphaëlle Bretrand-Lalo', 'raphaelle@omind.me'),
    ('David Ojeda', 'david@omind.me'),
]
author_names = ', '.join(tup[0] for tup in authors)
author_emails = ', '.join(tup[1] for tup in authors)

setup_args = dict(
    name='iguazu',
    description='Offline data analysis jobs platform.',
    packages=find_packages(exclude=['docs', 'tests']),
    url='https://github.com/OpenMindInnovation/iguazu',
    author=author_names,
    author_email=author_emails,
    install_requires=dependencies,
    python_requires='>=3.7,<4.0',
    zip_safe=False,
    entry_points={
        'console_scripts': [
            'iguazu = iguazu.cli.main:cli',
        ],
    },
    version=VERSION,
    include_package_data=True,
)

setup(**setup_args)
