# encoding: utf-8

from setuptools import setup
from pandocinject.version import VERSION

with open('README.rst', 'r', encoding='utf8') as file:
    readme_text = file.read()

setup(name='pandocinject',
      version=VERSION,
      description='build filters that select, format, and inject data (from yaml, bibtex, etc.) into pandoc documents',
      long_description=readme_text,
      url='https://github.com/msprev/pandocinject',
      author='Mark Sprevak',
      author_email='mark.sprevak@ed.ac.uk',
      license='LICENSE.txt',
      packages=['pandocinject'],
      install_requires=['pandocfilters', 'bibtexparser', 'pyyaml'],
      include_package_data=True,
      keywords=['pandoc', 'panzer'],
      classifiers=[
          'Development Status :: 4 - Beta',
          'Environment :: Console',
          'Intended Audience :: End Users/Desktop',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: BSD License',
          'Operating System :: OS Independent',
          'Programming Language :: Python :: 3',
          'Topic :: Text Processing'
        ],
      zip_safe=False)
