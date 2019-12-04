# -*- coding: utf-8 -*-

import re
from setuptools import setup, find_packages

with open('iguazu/__init__.py') as f:
    VERSION = re.search(r'^__version__\s*=\s*\'(.*)\'', f.read(), re.M).group(1)


dependencies = [
    'bokeh>=1.3,<2.0',
    'click>=7.0,<8.0',
    'colorlog>=4.0,<5.0',
    'dsu @ git+https://github.com/OpenMindInnovation/datascience_utils@v0.3.0',
    'numpy>=1.16,<1.17',
    'nolds>=0.5.2,<0.6',
    'mne>=0.19.2,<0.20',
    'pandas>=0.25.0,<0.26.0',
    'pendulum>=2.0.5,<2.1',
    'pyentrp>=0.5.0,<0.6',
    'psutil>=5.6.3,<5.7',
    'prefect>=0.6.1,<0.6.2',
    'quetzal-client>=0.5.0,<0.6',
    'scikit-learn>=0.21.2,<0.22.0',
    'scipy>=1.3,<2.0',
    'simplegeneric>=0.8.1,<0.9.0',
    'statsmodels>=0.10.1,<0.11',
    'tables>=3.5,<4.0',
    'tzlocal>=2.0,<3.0',
    # Requirements for plot-related tasks
    'Jinja2>=2.10.1,<2.11',
    'plotly>=4.1.1,<4.2',
    'matplotlib>=3.1.1,<3.2',
]
build_dependencies = dependencies + ['pytest-runner']
test_dependencies = [
    'pytest>=5.0.1,<6.0',
    'pytest-mock>=1.10.4,<2.0',
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
