# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

# import versioneer


dependencies = [
    "APScheduler",
    "numpy",
    "scipy",
    "pandas",
    "matplotlib",
    "tables",
    "tzlocal",
    "simplegeneric",
    "click",
    "prefect",
    "graphviz",
    "docker",
    "coloredlogs",
    'dsu @ git+https://github.com/OpenMindInnovation/datascience_utils@v0.3.0#egg=dsu',
    "quetzal-client @ git+https://github.com/quetz-al/quetzal-client.git@268b5f9#egg=quetzal-client"
 ]
build_dependencies = dependencies + ['pytest-runner']
test_dependencies = ['pytest']
authors = [
    ('Raphaëlle Bretrand-Lalo', 'raphaelle@omind.me'),
    ('David Ojeda', 'david@omind.me'),
]
author_names = ', '.join(tup[0] for tup in authors)
author_emails = ', '.join(tup[1] for tup in authors)

setup_args = dict(
    name='iguazu',
    # version=versioneer.get_version(),
    # cmdclass=versioneer.get_cmdclass(),
    description='Offline data analysis jobs platform.',
    packages=find_packages(exclude=['docs', 'tests']),
    url='https://github.com/OpenMindInnovation/iguazu',
    author=author_names,
    author_email=author_emails,
    install_requires=dependencies,
    python_requires='>=3.6',
    zip_safe=False,
    entry_points={
        'console_scripts': [
            'iguazu = iguazu.cli.main:cli',
        ],
    },
    version='0.0.4',  # TODO: use versioneer
)

setup(**setup_args)
