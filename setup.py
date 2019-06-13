# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

# import versioneer


dependencies = [
    "numpy",
    "scipy",
    "pandas",
    "tables",
    "tqdm",
    "pip",
    "rpy2",
    "tzlocal",
    "simplegeneric",
    "prefect",
    "graphviz",
    "dsu @ git+https://github.com/OpenMindInnovation/datascience_utils#egg=dsu",
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
)

setup(**setup_args)
