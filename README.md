# PyCEF

There is no workable demo for PyCEF yet. CEF Python is still actively developed and the link is: https://github.com/cztomczak/cefpython

The PyCEF project ideas are currently being implemented as part of CEF Python. Any breaking changes are described in the Migration Guide document. You can already see implemented: update to latest Chromium, Tutorial, new API docs, better examples, python 3 support, unit tests, new tools that automate building CEF with patches etc. Most of the new features described in PyCEF draft can be implemented in CEF Python, so I decided that abandoning CEF Python at this point wasn't a good idea. I might fork CEF Python in the future and create PyCEF from it, when new features would require a major backward compatibility breaks, such as completely refactored API or Unicode support in Py2. But that's a distant future and I'm still not sure if forking is a good idea, will see.

-----

PyCEF is a CEF Python clone that is more Pythonic. It is still under
works. See below how a Hello World example will look like using the
new API. It creates a window with a browser and navigates to Google:

```python
import pycef as cef
from cef.browser import Browser

Browser(url="https://www.google.com/")
cef.run()
```

New changes coming:
* Python 3.5, 3.4 and 2.7 support
* Updated to the latest Chromium
* Unicode strings in both Python 2 and Python 3. In CEF Python byte
  strings were used in Python 2.
* API cleanup. Better package structure with submodules like app,
  browser, interfaces, etc.
* Will follow the [PEP8](https://www.python.org/dev/peps/pep-0008/)
  style guide. Function names in lower case with underscores. Transform
  enum uppercase constants to class types whenever possible.
* Better examples
* Tutorial with many topics explained
* New great API docs, easy to navigate, up-to-date and easily searchable
* New tools that fully automate building on all platforms using CMake.
  Also build automation of CEF from sources.
* Unit tests
* Lots of new CEF API exposed
* Improvements to Core - in source docs and modular code with better
  structure that will make easier to work with for contributors
* CI builds with Travis and AppVeyor

## API draft

See [API.draft](API.draft).
