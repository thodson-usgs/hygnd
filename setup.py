from setuptools import setup
from os import sep

setup(name='hygnd',
      version='0.1',
      description='HYdrologic Gauge Network Datamanager',
      url='',
      author='Timothy Hodson',
      author_email='thodson@usgs.gov',
      license='MIT',
      packages=['hygnd'],
      entry_points = {
          'console_scripts': [
              #nutrient_mon_report/__main__.py
              #'bin/hygnd-store = hygnd-store.py.__main__:main',
              #TODO add script for plotting events
              #TODO add script for updating store
          ]
      },
      zip_safe=False)
