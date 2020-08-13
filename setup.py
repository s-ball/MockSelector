#  Copyright (c) 2020 SBA - MIT License

from setuptools import setup
import os.path
import re


name = 'mockselector'
wd = os.path.abspath(os.path.dirname(__file__))
version = '0.0.0'              # fallback value should never be used

# extract version number
try:    # first from git using setuptools_scm
    from setuptools_scm import get_version
    version = get_version(write_to=os.path.join(wd, name, 'version.py'))
except (ImportError, LookupError):
    try:  # else from a previous version.py
        with open(os.path.join(wd, name, 'version.py')) as fd:
            for line in fd:
                if line.startswith('version'):
                    version = line.split("'")[1]
    except OSError as e:
        raise RuntimeError('Need either git+setuptools-scm or'
                           ' version.py file') from e

# read long description and adjust master with version for badges or links
# only for release versions (x.y.z)
release = re.compile(r'(\d+\.){0,2}\d+')
with open(os.path.join(wd, 'README.md')) as fd:
    if version == '0.0.0' or not release.match(version):
        long_description = fd.read()
    else:
        lines = fd.readlines()
        for i, line in enumerate(lines):
            if not line.startswith('['):
                break
            lines[i] = line.replace('master', version)
        long_description = ''.join(lines)

setup(
    name=name,
    version=version,
    packages=[name],
    url='https://github.com/s-ball/MockSelector',
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 4 - Beta',

        # Indicate who your project is intended for
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Testing :: Mocking',

        # Pick your license as you wish (should match "license" above)
        'License :: OSI Approved :: MIT License',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
    python_requires='>=3.5',
    license='MIT',
    author='SBA',
    author_email='s-ball@laposte.net',
    description='Mock subclass of BaseSelector',
    long_description=long_description,
    long_description_content_type='text/markdown'

)
