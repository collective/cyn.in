from setuptools import setup, find_packages
import os

version = '1.0'

setup(name='ubify.xmlrpc',
      version=version,
      description="Provides an XMLRPC server object for consumption by client(s).",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='xmlrpc',
      author='Cynapse',
      author_email='devel@cynapse.com',
      url='http://www.cynapse.com',
      license='GPL v3 with attribution clause',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['ubify'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
