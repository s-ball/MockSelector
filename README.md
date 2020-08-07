# MockSelector

## Description

This is a collection of Python classes designed to help to test TCP servers
based on selectors. MockSelector provides everything needed to easily write
unittest TestCases simulating incoming connections and the associated
input data

## Installation

The current version is only available on Github. To use it, you must first
get a local copy by downloading a zipfile or cloning the repository:

    git clone https://github.com/s-ball/MockSelector.git

You can then install it in your main Python installation or in a venv with:

    python setup.py install

or on Windows with the launcher:

    py setup.py install

# Basic use

Once installed, you can easily import it in your tests.

```
from mockselector.selector import MockSocket, ListenSocket, MockSelector
```

You can find some example of use in the tests folder

# Advanced use and contribution

If you want to tailor the package, it already contains a number of tests.
You can run all of them from the top folder:

```
python setup.py install -e    # edit mode of install to use the local folder
python -m unittest discover
```
I will be glad to receive issues that would help to improve this project...

# Disclaimer: alpha quality

Even if the package has a nice test coverage, it currently only meets the
requirement to test another project of mine. It might not be usable for
your own project, or main contain Still Unidentified Bugs...

It is still a 0.x version, so the API is not guaranteed to be stable.

# License

That work is licenced under a MIT Licence. See [LICENSE.txt](https://raw.githubusercontent.com/s-ball/MockSelector/master/LICENCE.txt)
