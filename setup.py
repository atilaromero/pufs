from setuptools import setup, find_packages
import sys, os

version = '0.1'

setup(name='pufs',
      version=version,
      description="Parallel Union Filesystem - join multiple filesystems in one, using parallel requests to list files",
      long_description="""\
""",
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='',
      author='Atila Romero',
      author_email='atilaromero@gmail.com',
      url='',
      license='MIT',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
